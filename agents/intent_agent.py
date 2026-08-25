"""
TrustPay AI — Intent Agent (Agent A)
Extracts structured constraints from natural language using LLM.
"""
import time
from agents.base import BaseAgent
from llm.factory import get_llm


class IntentAgent(BaseAgent):
    """Agent A: Converts natural language payment instructions into structured intent."""

    AGENT_NAME = "intent_agent"

    async def _execute(self, user_input: str, **kwargs) -> dict:
        llm = get_llm()

        # Step 1: UNDERSTAND
        self._log("UNDERSTAND", input_data={"user_input": user_input},
                  output_data={"action": "Parsing user's natural language payment instruction"})

        # Step 2: OBSERVE
        self._log("OBSERVE", input_data={"raw_text": user_input},
                  output_data={"observation": f"Input is {len(user_input)} characters, contains payment-related language"})

        # Step 3: ANALYZE — use LLM
        start = time.time()
        extracted = await llm.extract_intent(user_input)
        llm_time = int((time.time() - start) * 1000)

        self._log("ANALYZE", input_data={"user_input": user_input},
                  output_data={"extracted_intent": extracted, "llm_provider": llm.provider_name},
                  execution_time_ms=llm_time)

        # Step 4: REASON
        confidence = self._compute_confidence(extracted)
        self._log("REASON",
                  input_data={"extracted_intent": extracted},
                  output_data={"confidence": confidence,
                               "reasoning": f"Extracted {len(extracted.get('raw_constraints', []))} constraints with {confidence:.0%} confidence"})

        # Step 5: DECIDE
        self._log("DECIDE",
                  output_data={"decision": "Intent extraction complete", "confidence": confidence})

        return {
            "extracted_intent": extracted,
            "confidence": confidence,
            "llm_provider": llm.provider_name,
        }

    def _compute_confidence(self, intent: dict) -> float:
        """Heuristic confidence based on how many fields were extracted."""
        score = 0.3  # base
        if intent.get("product") and intent["product"] != "General Purchase":
            score += 0.2
        if intent.get("max_amount") is not None:
            score += 0.2
        if intent.get("condition") != "any":
            score += 0.1
        if intent.get("purpose") != "general":
            score += 0.1
        if intent.get("raw_constraints"):
            score += 0.1
        return min(score, 1.0)
