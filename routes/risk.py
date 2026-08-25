"""
TrustPay AI — Risk Routes
POST /api/risk/analyze
POST /api/payment/decision
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import (
    RiskAnalyzeRequest, RiskAnalyzeResponse, AgentResult,
    PaymentDecisionRequest, PaymentDecisionResponse,
)
from services.risk_service import run_risk_analysis
from models import Transaction, PaymentIntent, RiskAssessment, AgentLog

router = APIRouter(prefix="/api", tags=["Risk"])


@router.post("/risk/analyze", response_model=RiskAnalyzeResponse)
async def analyze_risk(request: RiskAnalyzeRequest, db: Session = Depends(get_db)):
    """Run full risk analysis pipeline on a transaction."""
    txn = db.query(Transaction).filter(Transaction.id == request.transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    intent = db.query(PaymentIntent).filter(PaymentIntent.id == txn.payment_intent_id).first()
    if not intent:
        raise HTTPException(status_code=404, detail="Payment intent not found")

    # Build proposal dict from transaction
    proposal = {
        "product_name": txn.product_name,
        "merchant_name": txn.merchant_name,
        "base_price": txn.base_price,
        "tax": txn.tax,
        "delivery_fee": txn.delivery_fee,
        "total_amount": txn.total_amount,
        "product_condition": txn.product_condition,
    }

    # Run risk analysis
    result = await run_risk_analysis(
        extracted_intent=intent.extracted_intent,
        proposal=proposal,
        context_message=txn.context_message,
    )

    decision = result["decision"]

    # Save risk assessment
    assessment = RiskAssessment(
        transaction_id=txn.id,
        intent_match_score=result["intent_verification"].get("score", 0),
        intent_violated_constraints=result["intent_verification"].get("violated_constraints", []),
        scam_probability=result["scam_detection"].get("scam_probability", 0),
        scam_detected_patterns=result["scam_detection"].get("detected_patterns", []),
        behavior_anomaly_score=result["behavior_anomaly"].get("score", 0),
        behavior_details=result["behavior_anomaly"].get("anomalies", []),
        weighted_score=decision["weighted_score"],
        final_decision=decision["decision"],
        override_applied=decision.get("override_applied"),
        decision_reasons=decision["reasons"],
    )
    db.add(assessment)

    # Save agent logs
    for log in result.get("agent_logs", []):
        agent_log = AgentLog(
            transaction_id=txn.id,
            agent_name=log["agent_name"],
            agent_step=log["agent_step"],
            input_data=log.get("input_data"),
            output_data=log.get("output_data"),
            execution_time_ms=log.get("execution_time_ms", 0),
        )
        db.add(agent_log)

    # Update transaction with decision
    txn.decision = decision["decision"]
    txn.risk_score = decision["weighted_score"]
    db.commit()

    # Build response
    agents = [
        AgentResult(
            agent_name="Intent Verification",
            agent_step="COMPLETE",
            score=result["intent_verification"].get("score", 0),
            details={
                "violated_constraints": result["intent_verification"].get("violated_constraints", []),
                "reasoning": result["intent_verification"].get("reasoning", ""),
            },
            reasons=[v["description"] for v in result["intent_verification"].get("violated_constraints", [])],
            execution_time_ms=result["intent_verification"].get("execution_time_ms", 0),
        ),
        AgentResult(
            agent_name="Scam Detection",
            agent_step="COMPLETE",
            score=result["scam_detection"].get("score", 0),
            details={
                "scam_probability": result["scam_detection"].get("scam_probability", 0),
                "detected_patterns": result["scam_detection"].get("detected_patterns", []),
                "analysis": result["scam_detection"].get("analysis", ""),
            },
            reasons=[p["description"] for p in result["scam_detection"].get("detected_patterns", [])],
            execution_time_ms=result["scam_detection"].get("execution_time_ms", 0),
        ),
        AgentResult(
            agent_name="Behavior Anomaly",
            agent_step="COMPLETE",
            score=result["behavior_anomaly"].get("score", 0),
            details={
                "anomalies": result["behavior_anomaly"].get("anomalies", []),
                "reasoning": result["behavior_anomaly"].get("reasoning", ""),
            },
            reasons=[a["description"] for a in result["behavior_anomaly"].get("anomalies", [])],
            execution_time_ms=result["behavior_anomaly"].get("execution_time_ms", 0),
        ),
    ]

    return RiskAnalyzeResponse(
        transaction_id=txn.id,
        agents=agents,
        weighted_score=decision["weighted_score"],
        final_decision=decision["decision"],
        override_applied=decision.get("override_applied"),
        decision_reasons=decision["reasons"],
        risk_level=decision["risk_level"],
    )


@router.post("/payment/decision", response_model=PaymentDecisionResponse)
async def get_decision(request: PaymentDecisionRequest, db: Session = Depends(get_db)):
    """Get the risk decision for a transaction (or run analysis if not yet done)."""
    txn = db.query(Transaction).filter(Transaction.id == request.transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # If decision hasn't been made, run analysis first
    if not txn.decision:
        # Trigger risk analysis
        from routes.risk import analyze_risk as _analyze
        await analyze_risk(RiskAnalyzeRequest(transaction_id=txn.id), db)
        db.refresh(txn)

    assessment = db.query(RiskAssessment).filter(
        RiskAssessment.transaction_id == txn.id
    ).first()

    explainability = {}
    if assessment:
        explainability = {
            "intent_match_score": assessment.intent_match_score,
            "intent_violations": assessment.intent_violated_constraints,
            "scam_probability": assessment.scam_probability,
            "scam_patterns": assessment.scam_detected_patterns,
            "behavior_anomaly_score": assessment.behavior_anomaly_score,
            "behavior_details": assessment.behavior_details,
            "override_applied": assessment.override_applied,
        }

    return PaymentDecisionResponse(
        transaction_id=txn.id,
        decision=txn.decision,
        risk_score=txn.risk_score or 0,
        reasons=assessment.decision_reasons if assessment else [],
        requires_confirmation=txn.decision == "ASK_FOR_CONFIRMATION",
        explainability=explainability,
    )
