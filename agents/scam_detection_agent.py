"""
TrustPay AI — Context/Scam Detection Agent (Agent C)
Analyzes payment context for urgency, threats, impersonation, scam patterns.
Outputs scam_probability (0-1) and detected_patterns.
"""
import time
from agents.base import BaseAgent
from llm.factory import get_llm


class ScamDetectionAgent(BaseAgent):
    """Agent C: Detects scam/social-engineering patterns in payment context."""

    AGENT_NAME = "scam_detection"

    async def _execute(self, context_message: str = None, transaction_details: dict = None, **kwargs) -> dict:
        llm = get_llm()

        # Step 1: UNDERSTAND
        has_context = bool(context_message and context_message.strip())
        self._log("UNDERSTAND",
                  input_data={"has_context_message": has_context},
                  output_data={"action": "Analyzing payment context for scam indicators"})

        if not has_context:
            self._log("OBSERVE", output_data={"observation": "No context message — skipping scam analysis"})
            self._log("DECIDE", output_data={"decision": "No context to analyze, scam probability = 0"})
            return {
                "score": 0,
                "scam_probability": 0.0,
                "detected_patterns": [],
                "analysis": "No context message provided — no scam indicators.",
                "reasoning": "Without a context message, there is no text to analyze for scam patterns.",
            }

        # Step 2: OBSERVE
        self._log("OBSERVE",
                  input_data={"context_message": context_message},
                  output_data={"observation": f"Context message is {len(context_message)} characters",
                               "preview": context_message[:200]})

        # Step 3: ANALYZE — use LLM
        start = time.time()
        result = await llm.analyze_scam_context(
            context_message,
            transaction_details or {}
        )
        llm_time = int((time.time() - start) * 1000)

        scam_probability = result.get("scam_probability", 0.0)
        detected_patterns = result.get("detected_patterns", [])
        analysis = result.get("analysis", "")

        self._log("ANALYZE",
                  input_data={"context_message": context_message[:200]},
                  output_data={
                      "scam_probability": scam_probability,
                      "patterns_found": len(detected_patterns),
                      "llm_provider": llm.provider_name,
                  },
                  execution_time_ms=llm_time)

        # Step 4: REASON
        # Convert scam_probability (0-1) to a 0-100 score for the decision agent
        score_0_100 = int(scam_probability * 100)

        if scam_probability > 0.7:
            reasoning = f"HIGH SCAM RISK ({scam_probability:.0%}): {len(detected_patterns)} scam patterns detected. This payment context shows strong indicators of social engineering or fraud."
        elif scam_probability > 0.4:
            reasoning = f"MODERATE SCAM RISK ({scam_probability:.0%}): {len(detected_patterns)} concerning patterns found. The context warrants caution."
        elif scam_probability > 0.1:
            reasoning = f"LOW SCAM RISK ({scam_probability:.0%}): Minor indicators present but likely benign."
        else:
            reasoning = f"MINIMAL SCAM RISK ({scam_probability:.0%}): No significant scam patterns detected."

        self._log("REASON", output_data={"reasoning": reasoning, "score_0_100": score_0_100})

        # Step 5: DECIDE
        self._log("DECIDE", output_data={
            "scam_probability": scam_probability,
            "score": score_0_100,
            "patterns_count": len(detected_patterns),
        })

        return {
            "score": score_0_100,
            "scam_probability": scam_probability,
            "detected_patterns": detected_patterns,
            "analysis": analysis,
            "reasoning": reasoning,
        }
