"""
TrustPay AI — Behavior Anomaly Agent (Agent D)
Compares the transaction against synthetic historical user data.
Flags deviation from typical spending patterns.
"""
from agents.base import BaseAgent
from config import SYNTHETIC_USER_PROFILE


class BehaviorAnomalyAgent(BaseAgent):
    """Agent D: Detects behavioral anomalies by comparing against user history."""

    AGENT_NAME = "behavior_anomaly"

    async def _execute(self, proposal: dict, user_profile: dict = None, **kwargs) -> dict:
        profile = user_profile or SYNTHETIC_USER_PROFILE
        total_amount = proposal.get("total_amount", 0)
        merchant = proposal.get("merchant_name", "")

        # Step 1: UNDERSTAND
        self._log("UNDERSTAND",
                  input_data={"transaction_amount": total_amount, "merchant": merchant},
                  output_data={"action": "Comparing transaction against user's historical behavior"})

        # Step 2: OBSERVE
        self._log("OBSERVE",
                  input_data={"user_profile": {
                      "avg_amount": profile["avg_transaction_amount"],
                      "typical_range": f"₹{profile['typical_range_min']:,.0f} - ₹{profile['typical_range_max']:,.0f}",
                      "typical_merchants": profile["typical_merchants"],
                      "transaction_count": profile["transaction_count"],
                  }},
                  output_data={"current_amount": total_amount, "current_merchant": merchant})

        # Step 3: ANALYZE
        anomalies = []
        anomaly_score = 0

        # --- Amount deviation ---
        avg = profile["avg_transaction_amount"]
        range_min = profile["typical_range_min"]
        range_max = profile["typical_range_max"]

        if total_amount > range_max:
            deviation_ratio = total_amount / avg if avg > 0 else 999
            excess_over_max = total_amount / range_max if range_max > 0 else 999

            if deviation_ratio > 10:
                severity = "critical"
                amount_score = 60
            elif deviation_ratio > 5:
                severity = "high"
                amount_score = 45
            elif deviation_ratio > 2:
                severity = "medium"
                amount_score = 30
            else:
                severity = "low"
                amount_score = 15

            anomalies.append({
                "type": "amount_deviation",
                "description": f"Amount ₹{total_amount:,.0f} is {deviation_ratio:.1f}x the average (₹{avg:,.0f}) and {excess_over_max:.1f}x above typical max (₹{range_max:,.0f})",
                "severity": severity,
                "deviation_ratio": round(deviation_ratio, 2),
            })
            anomaly_score += amount_score

        elif total_amount < range_min and range_min > 0:
            # Unusually low — could be a probe/test transaction
            ratio = range_min / total_amount if total_amount > 0 else 999
            if ratio > 10:
                anomalies.append({
                    "type": "unusually_low_amount",
                    "description": f"Amount ₹{total_amount:,.0f} is unusually low (typical min ₹{range_min:,.0f})",
                    "severity": "low",
                    "deviation_ratio": round(ratio, 2),
                })
                anomaly_score += 10

        # --- Merchant familiarity ---
        typical_merchants = [m.lower() for m in profile.get("typical_merchants", [])]
        if merchant and merchant.lower() not in typical_merchants:
            anomalies.append({
                "type": "unfamiliar_merchant",
                "description": f"Merchant '{merchant}' is not in user's typical merchant list",
                "severity": "low",
            })
            anomaly_score += 10

        # --- High-value + unfamiliar merchant combo ---
        if total_amount > range_max * 2 and merchant.lower() not in typical_merchants:
            anomalies.append({
                "type": "high_value_unfamiliar",
                "description": f"High-value transaction (₹{total_amount:,.0f}) with unfamiliar merchant '{merchant}' — compound risk",
                "severity": "high",
            })
            anomaly_score += 15

        anomaly_score = min(int(anomaly_score), 100)

        self._log("ANALYZE",
                  output_data={"anomalies_found": len(anomalies),
                               "raw_anomaly_score": anomaly_score,
                               "anomalies": anomalies})

        # Step 4: REASON
        if anomaly_score == 0:
            reasoning = "Transaction is consistent with user's historical behavior. No anomalies detected."
        elif anomaly_score < 30:
            reasoning = f"Minor behavioral deviations detected ({len(anomalies)} anomalies). Transaction is somewhat unusual but not alarming."
        elif anomaly_score < 60:
            reasoning = f"Moderate behavioral anomalies ({len(anomalies)} found). Transaction deviates notably from typical patterns."
        else:
            reasoning = f"Significant behavioral anomaly ({len(anomalies)} found). Transaction is highly unusual compared to user's history."

        self._log("REASON", output_data={"reasoning": reasoning, "score": anomaly_score})

        # Step 5: DECIDE
        self._log("DECIDE", output_data={
            "anomaly_score": anomaly_score,
            "anomalies_count": len(anomalies),
        })

        return {
            "score": anomaly_score,
            "anomalies": anomalies,
            "reasoning": reasoning,
            "user_avg_amount": avg,
            "deviation_ratio": anomalies[0].get("deviation_ratio", 1.0) if anomalies else 1.0,
        }
