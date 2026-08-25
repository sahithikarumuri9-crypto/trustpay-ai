"""
TrustPay AI — Decision Agent (Agent E)
Combines all risk agent outputs into a final decision using weighted scoring + override rules.
Outputs: ALLOW / WARN / ASK_FOR_CONFIRMATION / BLOCK with full explainability.
"""
from agents.base import BaseAgent
from config import AGENT_WEIGHTS, DECISION_THRESHOLDS, OVERRIDE_RULES, SINGLE_AGENT_FLOOR

# Severity ordering used to compare/merge decisions from different sources
# (weighted score vs. per-agent floor vs. override rules).
_SEVERITY_ORDER = ["ALLOW", "WARN", "ASK_FOR_CONFIRMATION", "BLOCK"]


def _more_severe(a: str, b: str) -> str:
    """Return whichever of two decisions is the more severe (never downgrades)."""
    return a if _SEVERITY_ORDER.index(a) >= _SEVERITY_ORDER.index(b) else b


class DecisionAgent(BaseAgent):
    """Agent E: Weighted scoring + override rules → final decision."""

    AGENT_NAME = "decision_agent"

    async def _execute(
        self,
        intent_result: dict,
        scam_result: dict,
        behavior_result: dict,
        **kwargs,
    ) -> dict:
        # Step 1: UNDERSTAND
        self._log("UNDERSTAND",
                  input_data={
                      "intent_score": intent_result.get("score", 0),
                      "scam_score": scam_result.get("score", 0),
                      "behavior_score": behavior_result.get("score", 0),
                  },
                  output_data={"action": "Combining agent scores into final risk decision"})

        # Step 2: OBSERVE — collect scores
        intent_score = intent_result.get("score", 0)
        scam_score = scam_result.get("score", 0)
        scam_probability = scam_result.get("scam_probability", 0.0)
        behavior_score = behavior_result.get("score", 0)
        budget_exceeded_pct = intent_result.get("budget_exceeded_pct", 0)

        self._log("OBSERVE", output_data={
            "intent_score": intent_score,
            "scam_score": scam_score,
            "scam_probability": scam_probability,
            "behavior_score": behavior_score,
            "weights": AGENT_WEIGHTS,
        })

        # Step 3: ANALYZE — weighted scoring
        weighted_score = (
            intent_score * AGENT_WEIGHTS["intent_verification"] +
            scam_score * AGENT_WEIGHTS["scam_detection"] +
            behavior_score * AGENT_WEIGHTS["behavior_anomaly"]
        )
        weighted_score = round(weighted_score, 1)

        self._log("ANALYZE", output_data={
            "weighted_score": weighted_score,
            "components": {
                "intent": f"{intent_score} × {AGENT_WEIGHTS['intent_verification']} = {intent_score * AGENT_WEIGHTS['intent_verification']:.1f}",
                "scam": f"{scam_score} × {AGENT_WEIGHTS['scam_detection']} = {scam_score * AGENT_WEIGHTS['scam_detection']:.1f}",
                "behavior": f"{behavior_score} × {AGENT_WEIGHTS['behavior_anomaly']} = {behavior_score * AGENT_WEIGHTS['behavior_anomaly']:.1f}",
            }
        })

        # Step 4: REASON — determine decision from thresholds
        decision = "ALLOW"
        for dec, (low, high) in DECISION_THRESHOLDS.items():
            if low <= weighted_score <= high:
                decision = dec
                break
        if weighted_score > 100:
            decision = "BLOCK"

        # Step 4b: apply the dominant-signal floor. A weighted average can
        # dilute one severely risky agent below action thresholds (e.g. a
        # critical-severity Behavior Anomaly score of 85 only contributes
        # 25.5 points at 30% weight). The floor guarantees the final
        # decision is never less severe than what the single strongest
        # agent score alone would warrant.
        strongest_agent_score = max(intent_score, scam_score, behavior_score)
        floor_decision = "ALLOW"
        for dec_name in ("BLOCK", "ASK_FOR_CONFIRMATION", "WARN"):
            if strongest_agent_score >= SINGLE_AGENT_FLOOR[dec_name]:
                floor_decision = dec_name
                break
        pre_floor_decision = decision
        decision = _more_severe(decision, floor_decision)
        floor_applied = decision != pre_floor_decision

        self._log("REASON", output_data={
            "strongest_agent_score": strongest_agent_score,
            "floor_decision": floor_decision,
            "weighted_decision": pre_floor_decision,
            "final_after_floor": decision,
        })

        # Build reasons
        reasons = []
        if intent_result.get("violated_constraints"):
            for v in intent_result["violated_constraints"]:
                reasons.append(f"Intent: {v['description']} (severity: {v['severity']})")
        if scam_result.get("detected_patterns"):
            for p in scam_result["detected_patterns"]:
                reasons.append(f"Scam: {p['description']} (severity: {p.get('severity', 'unknown')})")
        if behavior_result.get("anomalies"):
            for a in behavior_result["anomalies"]:
                reasons.append(f"Behavior: {a['description']} (severity: {a['severity']})")

        if not reasons:
            reasons.append("All checks passed — no risk indicators found.")

        if floor_applied:
            reasons.insert(0, (
                f"FLOOR: strongest single agent score ({strongest_agent_score}) "
                f"warrants at least {floor_decision} even though the weighted "
                f"average ({weighted_score}) alone only reached {pre_floor_decision}"
            ))

        # Step 5: DECIDE — apply override rules
        override_applied = None

        # Override 1: scam_probability > 0.8 → force BLOCK
        if scam_probability > OVERRIDE_RULES["scam_probability_block"]:
            if decision != "BLOCK":
                override_applied = f"OVERRIDE: scam_probability {scam_probability:.2f} > {OVERRIDE_RULES['scam_probability_block']} → forced BLOCK"
                decision = "BLOCK"
                reasons.insert(0, override_applied)

        # Override 2: budget exceeded by >20% → force at least ASK_FOR_CONFIRMATION
        if budget_exceeded_pct > OVERRIDE_RULES["budget_exceed_ask_threshold"] * 100:
            if decision in ("ALLOW", "WARN"):
                override_applied = f"OVERRIDE: budget exceeded by {budget_exceeded_pct:.1f}% > {OVERRIDE_RULES['budget_exceed_ask_threshold']*100:.0f}% → forced ASK_FOR_CONFIRMATION"
                decision = "ASK_FOR_CONFIRMATION"
                reasons.insert(0, override_applied)

        # Risk level label
        if weighted_score <= 30:
            risk_level = "LOW"
        elif weighted_score <= 60:
            risk_level = "MEDIUM"
        elif weighted_score <= 80:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"

        self._log("DECIDE", output_data={
            "final_decision": decision,
            "weighted_score": weighted_score,
            "risk_level": risk_level,
            "override_applied": override_applied,
            "reasons_count": len(reasons),
        })

        return {
            "decision": decision,
            "weighted_score": weighted_score,
            "risk_level": risk_level,
            "override_applied": override_applied,
            "reasons": reasons,
            "agent_scores": {
                "intent_verification": {
                    "score": intent_score,
                    "weight": AGENT_WEIGHTS["intent_verification"],
                    "weighted": round(intent_score * AGENT_WEIGHTS["intent_verification"], 1),
                    "reasoning": intent_result.get("reasoning", ""),
                    "violations": intent_result.get("violated_constraints", []),
                },
                "scam_detection": {
                    "score": scam_score,
                    "weight": AGENT_WEIGHTS["scam_detection"],
                    "weighted": round(scam_score * AGENT_WEIGHTS["scam_detection"], 1),
                    "scam_probability": scam_probability,
                    "reasoning": scam_result.get("reasoning", ""),
                    "patterns": scam_result.get("detected_patterns", []),
                },
                "behavior_anomaly": {
                    "score": behavior_score,
                    "weight": AGENT_WEIGHTS["behavior_anomaly"],
                    "weighted": round(behavior_score * AGENT_WEIGHTS["behavior_anomaly"], 1),
                    "reasoning": behavior_result.get("reasoning", ""),
                    "anomalies": behavior_result.get("anomalies", []),
                },
            },
            "explainability": {
                "weighted_formula": f"({intent_score} × {AGENT_WEIGHTS['intent_verification']}) + ({scam_score} × {AGENT_WEIGHTS['scam_detection']}) + ({behavior_score} × {AGENT_WEIGHTS['behavior_anomaly']}) = {weighted_score}",
                "threshold_used": f"{risk_level}: {DECISION_THRESHOLDS.get(decision, 'N/A')}",
                "override_rules_checked": [
                    f"scam_probability ({scam_probability:.2f}) > {OVERRIDE_RULES['scam_probability_block']}? {'YES → BLOCK' if scam_probability > OVERRIDE_RULES['scam_probability_block'] else 'NO'}",
                    f"budget_exceeded ({budget_exceeded_pct:.1f}%) > {OVERRIDE_RULES['budget_exceed_ask_threshold']*100:.0f}%? {'YES → ASK' if budget_exceeded_pct > OVERRIDE_RULES['budget_exceed_ask_threshold']*100 else 'NO'}",
                ],
            },
        }
