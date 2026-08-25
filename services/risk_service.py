"""
TrustPay AI — Risk Service
Orchestrates the full risk analysis pipeline: Intent Verification → Scam Detection → Behavior Anomaly → Decision.
"""
from agents.intent_agent import IntentAgent
from agents.intent_verification_agent import IntentVerificationAgent
from agents.scam_detection_agent import ScamDetectionAgent
from agents.behavior_anomaly_agent import BehaviorAnomalyAgent
from agents.decision_agent import DecisionAgent
from agents.post_payment_agent import PostPaymentAgent


async def run_risk_analysis(
    extracted_intent: dict,
    proposal: dict,
    context_message: str = None,
    user_profile: dict = None,
) -> dict:
    """
    Run the full risk analysis pipeline.

    Returns:
        Complete risk analysis including all agent results and final decision.
    """
    all_logs = []

    # Agent B: Intent Verification
    intent_verifier = IntentVerificationAgent()
    intent_result = await intent_verifier.run(
        extracted_intent=extracted_intent,
        proposal=proposal,
    )
    all_logs.extend(intent_verifier.get_logs())

    # Agent C: Scam Detection
    scam_detector = ScamDetectionAgent()
    scam_result = await scam_detector.run(
        context_message=context_message,
        transaction_details={
            "product": proposal.get("product_name"),
            "merchant": proposal.get("merchant_name"),
            "amount": proposal.get("total_amount"),
        },
    )
    all_logs.extend(scam_detector.get_logs())

    # Agent D: Behavior Anomaly
    behavior_analyzer = BehaviorAnomalyAgent()
    behavior_result = await behavior_analyzer.run(
        proposal=proposal,
        user_profile=user_profile,
    )
    all_logs.extend(behavior_analyzer.get_logs())

    # Agent E: Decision
    decision_agent = DecisionAgent()
    decision_result = await decision_agent.run(
        intent_result=intent_result,
        scam_result=scam_result,
        behavior_result=behavior_result,
    )
    all_logs.extend(decision_agent.get_logs())

    return {
        "intent_verification": intent_result,
        "scam_detection": scam_result,
        "behavior_anomaly": behavior_result,
        "decision": decision_result,
        "agent_logs": all_logs,
    }


async def run_post_payment_verification(approved_payment: dict, executed_payment: dict) -> dict:
    """Run post-payment verification."""
    verifier = PostPaymentAgent()
    result = await verifier.run(
        approved_payment=approved_payment,
        executed_payment=executed_payment,
    )
    result["agent_logs"] = verifier.get_logs()
    return result
