"""
TrustPay AI — Intent Verification Agent (Agent B)
Compares the proposed payment against the original intent.
Outputs intent-match score (0-100) and violated constraints.
This is the most novel/differentiated piece — invest the most care here.
"""
from agents.base import BaseAgent


class IntentVerificationAgent(BaseAgent):
    """Agent B: Compares payment proposal vs. user's original intent."""

    AGENT_NAME = "intent_verification"

    async def _execute(self, extracted_intent: dict, proposal: dict, **kwargs) -> dict:
        """
        Args:
            extracted_intent: Structured intent from Intent Agent
            proposal: Payment proposal from commerce agent
        Returns:
            score (0-100, where 0=perfect match, 100=total mismatch),
            violated_constraints
        """
        violations = []
        mismatch_score = 0

        # Step 1: UNDERSTAND
        self._log("UNDERSTAND",
                  input_data={"intent": extracted_intent, "proposal": proposal},
                  output_data={"action": "Comparing payment proposal against user intent"})

        # Step 2: OBSERVE
        self._log("OBSERVE",
                  input_data={"intent_product": extracted_intent.get("product"),
                              "proposal_product": proposal.get("product_name"),
                              "intent_max": extracted_intent.get("max_amount"),
                              "proposal_total": proposal.get("total_amount")})

        # ---- Budget Check ----
        max_amount = extracted_intent.get("max_amount")
        total_amount = proposal.get("total_amount", 0)
        if max_amount and total_amount > max_amount:
            excess = total_amount - max_amount
            excess_pct = (excess / max_amount) * 100
            severity = "critical" if excess_pct > 20 else "high" if excess_pct > 10 else "medium"
            violations.append({
                "type": "budget_exceeded",
                "description": f"Payment ₹{total_amount:,.0f} exceeds budget ₹{max_amount:,.0f} by ₹{excess:,.0f} ({excess_pct:.1f}%)",
                "severity": severity,
                "excess_amount": excess,
                "excess_percentage": excess_pct,
            })
            # Score: proportional to how much over budget
            mismatch_score += min(excess_pct * 2, 50)

        # ---- Product Match ----
        intent_product = (extracted_intent.get("product") or "").lower()
        proposal_product = (proposal.get("product_name") or "").lower()
        if intent_product and proposal_product:
            if intent_product not in proposal_product and proposal_product not in intent_product:
                # Check partial match
                intent_words = set(intent_product.split())
                proposal_words = set(proposal_product.split())
                overlap = intent_words & proposal_words
                if not overlap:
                    violations.append({
                        "type": "product_mismatch",
                        "description": f"Requested '{extracted_intent.get('product')}' but proposed '{proposal.get('product_name')}'",
                        "severity": "high",
                    })
                    mismatch_score += 25

        # ---- Condition Check ----
        intent_condition = (extracted_intent.get("condition") or "any").lower()
        proposal_condition = (proposal.get("product_condition") or "new").lower()
        refurbished_allowed = extracted_intent.get("refurbished_allowed", True)

        if intent_condition != "any":
            if intent_condition != proposal_condition:
                violations.append({
                    "type": "condition_mismatch",
                    "description": f"Requested '{intent_condition}' but proposed '{proposal_condition}'",
                    "severity": "medium",
                })
                mismatch_score += 15

        if not refurbished_allowed and proposal_condition == "refurbished":
            violations.append({
                "type": "refurbished_not_allowed",
                "description": "User explicitly prohibited refurbished products",
                "severity": "high",
            })
            mismatch_score += 20

        # ---- Quantity Check ----
        intent_qty = extracted_intent.get("quantity", 1)
        proposal_qty = proposal.get("quantity", 1)
        if intent_qty != proposal_qty:
            violations.append({
                "type": "quantity_mismatch",
                "description": f"Requested {intent_qty} but proposed {proposal_qty}",
                "severity": "medium",
            })
            mismatch_score += 10

        # ---- Merchant Preference ----
        merchant_pref = extracted_intent.get("merchant_preference")
        proposal_merchant = proposal.get("merchant_name", "")
        if merchant_pref and merchant_pref.lower() not in proposal_merchant.lower():
            violations.append({
                "type": "merchant_preference_mismatch",
                "description": f"Preferred merchant '{merchant_pref}' but proposed '{proposal_merchant}'",
                "severity": "low",
            })
            mismatch_score += 5

        # Cap at 100
        mismatch_score = min(int(mismatch_score), 100)

        # Step 3: ANALYZE
        self._log("ANALYZE",
                  output_data={"violations_found": len(violations),
                               "raw_mismatch_score": mismatch_score,
                               "violations": violations})

        # Step 4: REASON
        if mismatch_score == 0:
            reasoning = "Payment proposal fully matches the user's stated intent. No violations found."
        elif mismatch_score < 30:
            reasoning = f"Minor deviations found ({len(violations)} issues). Payment is mostly aligned with intent."
        elif mismatch_score < 60:
            reasoning = f"Moderate mismatches found ({len(violations)} issues). User should review before proceeding."
        else:
            reasoning = f"Significant intent violations detected ({len(violations)} issues). Payment deviates substantially from user's original request."

        self._log("REASON", output_data={"reasoning": reasoning, "score": mismatch_score})

        # Step 5: DECIDE
        self._log("DECIDE", output_data={
            "intent_match_score": mismatch_score,
            "violated_constraints": [v["type"] for v in violations],
            "decision": "Intent verification complete"
        })

        return {
            "score": mismatch_score,
            "violated_constraints": violations,
            "reasoning": reasoning,
            "budget_exceeded_pct": violations[0].get("excess_percentage", 0) if violations and violations[0]["type"] == "budget_exceeded" else 0,
        }
