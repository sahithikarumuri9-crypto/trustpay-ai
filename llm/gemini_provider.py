"""
TrustPay AI — Gemini LLM Provider
Uses Google Gemini API for intent extraction and scam analysis.
Falls back to mock if API fails.
"""
import json
import re
from llm.base import BaseLLMProvider

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class GeminiLLMProvider(BaseLLMProvider):
    """Google Gemini API provider."""

    def __init__(self, api_key: str):
        if not GENAI_AVAILABLE:
            raise ImportError("google-generativeai package not installed")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def extract_intent(self, user_input: str) -> dict:
        prompt = f"""You are a payment intent extraction system. Extract structured payment intent from the user's natural language input.

User input: "{user_input}"

Return ONLY valid JSON (no markdown, no explanation) with these fields:
{{
    "product": "string - the product or service being purchased",
    "purpose": "string - the purpose/use case (e.g., college, office, gift, general)",
    "max_amount": number or null - maximum budget if specified,
    "min_amount": number or null - minimum budget if specified,
    "condition": "string - new/refurbished/used/any",
    "refurbished_allowed": boolean,
    "quantity": number (default 1),
    "merchant_preference": "string or null",
    "urgency": "string - normal/medium/high",
    "raw_constraints": ["list of human-readable constraint strings"]
}}"""

        try:
            response = await self._generate(prompt)
            # Parse JSON from response
            json_str = self._extract_json(response)
            data = json.loads(json_str)
            # Ensure all required fields
            return {
                "product": data.get("product", "General Purchase"),
                "purpose": data.get("purpose", "general"),
                "max_amount": data.get("max_amount"),
                "min_amount": data.get("min_amount"),
                "condition": data.get("condition", "any"),
                "refurbished_allowed": data.get("refurbished_allowed", True),
                "quantity": data.get("quantity", 1),
                "merchant_preference": data.get("merchant_preference"),
                "urgency": data.get("urgency", "normal"),
                "raw_constraints": data.get("raw_constraints", []),
            }
        except Exception as e:
            # Fallback to mock
            from llm.mock_provider import MockLLMProvider
            mock = MockLLMProvider()
            return await mock.extract_intent(user_input)

    async def analyze_scam_context(self, context_message: str, transaction_details: dict) -> dict:
        prompt = f"""You are a scam/fraud detection system. Analyze the following payment context message for scam indicators.

Context message: "{context_message}"
Transaction details: {json.dumps(transaction_details)}

Analyze for: urgency tactics, threats, impersonation, unusual payment requests, too-good-to-be-true offers.

Return ONLY valid JSON:
{{
    "scam_probability": float between 0.0 and 1.0,
    "detected_patterns": [
        {{
            "type": "string (urgency/threat/impersonation/unusual_payment_method/too_good_to_be_true)",
            "description": "string describing the pattern",
            "severity": "string (low/medium/high/critical)"
        }}
    ],
    "analysis": "string - brief analysis summary"
}}"""

        try:
            response = await self._generate(prompt)
            json_str = self._extract_json(response)
            data = json.loads(json_str)
            return {
                "scam_probability": min(max(float(data.get("scam_probability", 0)), 0.0), 1.0),
                "detected_patterns": data.get("detected_patterns", []),
                "analysis": data.get("analysis", "Analysis complete."),
            }
        except Exception:
            from llm.mock_provider import MockLLMProvider
            mock = MockLLMProvider()
            return await mock.analyze_scam_context(context_message, transaction_details)

    async def generate_text(self, prompt: str) -> str:
        try:
            return await self._generate(prompt)
        except Exception:
            return f"[Gemini Error] Could not generate response."

    async def _generate(self, prompt: str) -> str:
        """Synchronous call wrapped for async interface."""
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None, lambda: self.model.generate_content(prompt)
        )
        return response.text

    def _extract_json(self, text: str) -> str:
        """Extract JSON from a response that might contain markdown fencing."""
        # Try to find JSON block in markdown
        match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Try to find raw JSON
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group(0)
        return text
