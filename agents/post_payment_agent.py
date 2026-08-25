"""
TrustPay AI — Post-Payment Verification Agent (Agent F)
After mock execution, re-checks amount/merchant/product/status against the approved payment.
Flags POST_PAYMENT_MISMATCH if anything drifted.
"""
from agents.base import BaseAgent


class PostPaymentAgent(BaseAgent):
    """Agent F: Post-payment verification — confirms executed payment matches approved intent."""

    AGENT_NAME = "post_payment_verification"

    async def _execute(self, approved_payment: dict, executed_payment: dict, **kwargs) -> dict:
        """
        Args:
            approved_payment: The payment as it was approved
            executed_payment: The payment as it was actually executed
        """

        # Step 1: UNDERSTAND
        self._log("UNDERSTAND",
                  input_data={"approved": approved_payment, "executed": executed_payment},
                  output_data={"action": "Verifying executed payment matches approved payment"})

        # Step 2: OBSERVE
        checks = []
        mismatches = []

        # Amount check
        approved_amount = approved_payment.get("total_amount", 0)
        executed_amount = executed_payment.get("total_amount", 0)
        amount_match = abs(approved_amount - executed_amount) < 0.01
        checks.append({
            "field": "amount",
            "approved": approved_amount,
            "executed": executed_amount,
            "match": amount_match,
        })
        if not amount_match:
            mismatches.append(f"Amount mismatch: approved ₹{approved_amount:,.0f} vs executed ₹{executed_amount:,.0f}")

        # Merchant check
        approved_merchant = approved_payment.get("merchant_name", "")
        executed_merchant = executed_payment.get("merchant_name", "")
        merchant_match = approved_merchant.lower() == executed_merchant.lower()
        checks.append({
            "field": "merchant",
            "approved": approved_merchant,
            "executed": executed_merchant,
            "match": merchant_match,
        })
        if not merchant_match:
            mismatches.append(f"Merchant mismatch: approved '{approved_merchant}' vs executed '{executed_merchant}'")

        # Product check
        approved_product = approved_payment.get("product_name", "")
        executed_product = executed_payment.get("product_name", "")
        product_match = approved_product.lower() == executed_product.lower()
        checks.append({
            "field": "product",
            "approved": approved_product,
            "executed": executed_product,
            "match": product_match,
        })
        if not product_match:
            mismatches.append(f"Product mismatch: approved '{approved_product}' vs executed '{executed_product}'")

        # Status check
        executed_status = executed_payment.get("payment_status", "unknown")
        status_ok = executed_status in ("executed", "success", "completed")
        checks.append({
            "field": "status",
            "approved": "expected success",
            "executed": executed_status,
            "match": status_ok,
        })
        if not status_ok:
            mismatches.append(f"Payment status issue: {executed_status}")

        self._log("OBSERVE", output_data={
            "checks_performed": len(checks),
            "mismatches_found": len(mismatches),
        })

        # Step 3: ANALYZE
        verification_status = "verified" if len(mismatches) == 0 else "mismatch"

        self._log("ANALYZE", output_data={
            "verification_status": verification_status,
            "checks": checks,
            "mismatches": mismatches,
        })

        # Step 4: REASON
        if verification_status == "verified":
            reasoning = "All post-payment checks passed. The executed payment matches the approved payment in amount, merchant, product, and status."
        else:
            reasoning = f"POST_PAYMENT_MISMATCH detected: {len(mismatches)} field(s) drifted from the approved payment. {'; '.join(mismatches)}"

        self._log("REASON", output_data={"reasoning": reasoning})

        # Step 5: DECIDE
        self._log("DECIDE", output_data={
            "verification_status": verification_status,
            "mismatches_count": len(mismatches),
        })

        return {
            "verification_status": verification_status,
            "checks": checks,
            "mismatches": mismatches,
            "reasoning": reasoning,
        }
