"""
TrustPay AI — Mock LLM Provider
Pattern-matching mock that works fully offline without any API key.
Handles intent extraction and scam analysis using deterministic rules.
"""
import re
import json
from llm.base import BaseLLMProvider


class MockLLMProvider(BaseLLMProvider):
    """Deterministic mock LLM provider — no API key required."""

    @property
    def provider_name(self) -> str:
        return "mock"

    async def extract_intent(self, user_input: str) -> dict:
        """Extract structured intent using pattern matching."""
        text = user_input.lower()

        # Extract product
        product = self._extract_product(text)

        # Extract purpose
        purpose = self._extract_purpose(text)

        # Extract amount constraints
        max_amount = self._extract_max_amount(text)
        min_amount = self._extract_min_amount(text)

        # Extract condition
        condition, refurbished_allowed = self._extract_condition(text)

        # Extract quantity
        quantity = self._extract_quantity(text)

        # Extract merchant preference
        merchant_preference = self._extract_merchant(text)

        # Extract urgency
        urgency = self._extract_urgency(text)

        # Build raw constraints
        raw_constraints = []
        if max_amount:
            raw_constraints.append(f"Maximum budget: ₹{max_amount:,.0f}")
        if min_amount:
            raw_constraints.append(f"Minimum budget: ₹{min_amount:,.0f}")
        if condition != "any":
            raw_constraints.append(f"Condition: {condition}")
        if not refurbished_allowed:
            raw_constraints.append("Refurbished NOT allowed")
        if merchant_preference:
            raw_constraints.append(f"Preferred merchant: {merchant_preference}")
        if quantity > 1:
            raw_constraints.append(f"Quantity: {quantity}")

        return {
            "product": product,
            "purpose": purpose,
            "max_amount": max_amount,
            "min_amount": min_amount,
            "condition": condition,
            "refurbished_allowed": refurbished_allowed,
            "quantity": quantity,
            "merchant_preference": merchant_preference,
            "urgency": urgency,
            "raw_constraints": raw_constraints,
        }

    async def analyze_scam_context(self, context_message: str, transaction_details: dict) -> dict:
        """Analyze context for scam patterns using keyword detection."""
        if not context_message:
            return {
                "scam_probability": 0.0,
                "detected_patterns": [],
                "analysis": "No context message provided.",
            }

        text = context_message.lower()
        patterns = []
        scam_score = 0.0

        # Urgency patterns
        urgency_keywords = [
            "immediately", "urgent", "right now", "today", "within hours",
            "last chance", "expires today", "act now", "hurry", "deadline",
            "time is running out", "don't delay", "asap"
        ]
        urgency_hits = [kw for kw in urgency_keywords if kw in text]
        if urgency_hits:
            patterns.append({
                "type": "urgency",
                "description": f"Urgency language detected: {', '.join(urgency_hits)}",
                "severity": "high"
            })
            scam_score += 0.25 * min(len(urgency_hits), 3)

        # Threat patterns
        threat_keywords = [
            "disconnected", "suspended", "blocked", "terminated", "legal action",
            "arrest", "police", "lawsuit", "penalty", "fine", "shut down",
            "account will be", "service will be", "access will be"
        ]
        threat_hits = [kw for kw in threat_keywords if kw in text]
        if threat_hits:
            patterns.append({
                "type": "threat",
                "description": f"Threatening language detected: {', '.join(threat_hits)}",
                "severity": "critical"
            })
            scam_score += 0.3 * min(len(threat_hits), 3)

        # Impersonation patterns
        impersonation_keywords = [
            "government", "official", "authority", "police", "bank officer",
            "customer support", "tech support", "microsoft", "apple support",
            "irs", "tax department", "electricity board", "we are from"
        ]
        impersonation_hits = [kw for kw in impersonation_keywords if kw in text]
        if impersonation_hits:
            patterns.append({
                "type": "impersonation",
                "description": f"Possible impersonation: {', '.join(impersonation_hits)}",
                "severity": "critical"
            })
            scam_score += 0.3

        # Unusual payment method requests
        payment_keywords = [
            "gift card", "bitcoin", "crypto", "wire transfer", "western union",
            "upi to personal", "personal account", "don't tell anyone"
        ]
        payment_hits = [kw for kw in payment_keywords if kw in text]
        if payment_hits:
            patterns.append({
                "type": "unusual_payment_method",
                "description": f"Unusual payment method requested: {', '.join(payment_hits)}",
                "severity": "high"
            })
            scam_score += 0.25

        # Too-good-to-be-true patterns
        tgtbt_keywords = [
            "lottery", "winner", "won", "prize", "congratulations",
            "free", "guaranteed returns", "double your money", "investment opportunity",
            "limited offer", "limited time offer", "cashback reward", "claim your",
            "processing fee", "act now"
        ]
        tgtbt_hits = [kw for kw in tgtbt_keywords if kw in text]
        if tgtbt_hits:
            patterns.append({
                "type": "too_good_to_be_true",
                "description": f"Suspicious offer language: {', '.join(tgtbt_hits)}",
                "severity": "high"
            })
            scam_score += 0.25

        scam_probability = min(scam_score, 1.0)

        analysis = "No significant scam indicators found."
        if scam_probability > 0.7:
            analysis = "HIGH RISK: Multiple scam patterns detected. This context shows strong indicators of a social engineering attack."
        elif scam_probability > 0.4:
            analysis = "MODERATE RISK: Some concerning patterns found in the context. Proceed with caution."
        elif scam_probability > 0.1:
            analysis = "LOW RISK: Minor indicators found but likely benign."

        return {
            "scam_probability": round(scam_probability, 3),
            "detected_patterns": patterns,
            "analysis": analysis,
        }

    async def generate_text(self, prompt: str) -> str:
        return f"[Mock LLM Response] Processed prompt with {len(prompt)} characters."

    # -----------------------------------------------------------------------
    # Private helpers
    # -----------------------------------------------------------------------

    def _extract_product(self, text: str) -> str:
        products = {
            "laptop": "Laptop", "phone": "Smartphone", "mobile": "Smartphone",
            "smartphone": "Smartphone", "headphone": "Headphones", "headphones": "Headphones",
            "earphone": "Earphones", "earbuds": "Earbuds", "tablet": "Tablet",
            "watch": "Smartwatch", "smartwatch": "Smartwatch", "camera": "Camera",
            "television": "Television", "tv": "Television", "monitor": "Monitor",
            "keyboard": "Keyboard", "mouse": "Mouse", "speaker": "Speaker",
            "printer": "Printer", "router": "Router", "charger": "Charger",
            "shoes": "Shoes", "shirt": "Shirt", "book": "Book", "books": "Books",
            "electricity": "Electricity Bill Payment", "bill": "Bill Payment",
            "recharge": "Mobile Recharge", "groceries": "Groceries",
            "subscription": "Subscription", "software": "Software",
        }
        for keyword, product_name in products.items():
            if keyword in text:
                return product_name
        # Fallback: try to find a noun after "buy" or "purchase" or "order"
        match = re.search(r'(?:buy|purchase|order|get)\s+(?:a\s+|an\s+)?(\w+)', text)
        if match:
            return match.group(1).capitalize()
        return "General Purchase"

    def _extract_purpose(self, text: str) -> str:
        purposes = {
            "college": "college", "school": "school", "office": "office",
            "work": "work", "gaming": "gaming", "travel": "travel",
            "gift": "gift", "home": "home", "personal": "personal",
            "business": "business", "study": "study", "fitness": "fitness",
        }
        for keyword, purpose in purposes.items():
            if keyword in text:
                return purpose
        return "general"

    def _extract_max_amount(self, text: str) -> float | None:
        # "under ₹60,000" / "under 60000" / "below ₹60,000" / "max ₹60000" / "budget 60000"
        patterns = [
            r'(?:under|below|less than|max(?:imum)?|budget(?:\s+of)?|up\s+to|within|not\s+(?:more|above|exceeding)\s+(?:than\s+)?)[₹rs.\s]*([0-9,]+(?:\.\d+)?)',
            r'[₹rs.\s]*([0-9,]+(?:\.\d+)?)\s*(?:max|maximum|budget|or\s+less|or\s+below|or\s+under)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return float(match.group(1).replace(",", ""))
        return None

    def _extract_min_amount(self, text: str) -> float | None:
        patterns = [
            r'(?:above|over|more than|min(?:imum)?|at\s+least|starting\s+from)[₹rs.\s]*([0-9,]+(?:\.\d+)?)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return float(match.group(1).replace(",", ""))
        return None

    def _extract_condition(self, text: str) -> tuple[str, bool]:
        if "not refurbished" in text or "no refurbished" in text or "brand new" in text:
            return "new", False
        if "refurbished" in text or "renewed" in text:
            return "refurbished", True
        if "used" in text or "second hand" in text or "pre-owned" in text:
            return "used", True
        if "new" in text:
            return "new", False
        return "any", True

    def _extract_quantity(self, text: str) -> int:
        match = re.search(r'(\d+)\s*(?:pieces?|units?|items?|nos?|quantity)', text)
        if match:
            return int(match.group(1))
        # Check word numbers
        word_numbers = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
        for word, num in word_numbers.items():
            if word in text:
                return num
        return 1

    def _extract_merchant(self, text: str) -> str | None:
        merchants = [
            "amazon", "flipkart", "myntra", "snapdeal", "croma",
            "reliance digital", "vijay sales", "bigbasket", "swiggy",
            "zomato", "meesho", "ajio"
        ]
        for m in merchants:
            if m in text:
                return m.title()
        return None

    def _extract_urgency(self, text: str) -> str:
        if any(w in text for w in ["urgent", "asap", "immediately", "right now", "today"]):
            return "high"
        if any(w in text for w in ["soon", "this week", "quickly"]):
            return "medium"
        return "normal"
