"""
TrustPay AI — Transaction Routes
GET /api/transactions
GET /api/transactions/{id}
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Transaction, PaymentIntent, RiskAssessment, AgentLog

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.get("")
async def list_transactions(db: Session = Depends(get_db)):
    """List all transactions with summary data."""
    txns = db.query(Transaction).order_by(Transaction.created_at.desc()).all()

    results = []
    for txn in txns:
        intent = db.query(PaymentIntent).filter(PaymentIntent.id == txn.payment_intent_id).first()
        results.append({
            "id": txn.id,
            "product_name": txn.product_name,
            "merchant_name": txn.merchant_name,
            "total_amount": txn.total_amount,
            "decision": txn.decision,
            "risk_score": txn.risk_score,
            "payment_status": txn.payment_status,
            "created_at": txn.created_at.isoformat() if txn.created_at else None,
            "raw_input": intent.raw_input if intent else None,
        })

    return results


@router.get("/{transaction_id}")
async def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    """Get detailed transaction info including risk assessment and agent logs."""
    txn = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    intent = db.query(PaymentIntent).filter(PaymentIntent.id == txn.payment_intent_id).first()
    assessment = db.query(RiskAssessment).filter(RiskAssessment.transaction_id == txn.id).first()
    logs = db.query(AgentLog).filter(AgentLog.transaction_id == txn.id).order_by(AgentLog.created_at).all()

    return {
        "id": txn.id,
        "product_name": txn.product_name,
        "merchant_name": txn.merchant_name,
        "base_price": txn.base_price,
        "tax": txn.tax,
        "delivery_fee": txn.delivery_fee,
        "total_amount": txn.total_amount,
        "currency": txn.currency,
        "product_condition": txn.product_condition,
        "context_message": txn.context_message,
        "decision": txn.decision,
        "risk_score": txn.risk_score,
        "payment_status": txn.payment_status,
        "payment_id": txn.payment_id,
        "human_confirmed": txn.human_confirmed,
        "post_payment_status": txn.post_payment_status,
        "post_payment_details": txn.post_payment_details,
        "created_at": txn.created_at.isoformat() if txn.created_at else None,
        "raw_input": intent.raw_input if intent else None,
        "extracted_intent": intent.extracted_intent if intent else None,
        "risk_assessment": {
            "intent_match_score": assessment.intent_match_score,
            "intent_violated_constraints": assessment.intent_violated_constraints,
            "scam_probability": assessment.scam_probability,
            "scam_detected_patterns": assessment.scam_detected_patterns,
            "behavior_anomaly_score": assessment.behavior_anomaly_score,
            "behavior_details": assessment.behavior_details,
            "weighted_score": assessment.weighted_score,
            "final_decision": assessment.final_decision,
            "override_applied": assessment.override_applied,
            "decision_reasons": assessment.decision_reasons,
        } if assessment else None,
        "agent_logs": [
            {
                "agent_name": log.agent_name,
                "agent_step": log.agent_step,
                "input_data": log.input_data,
                "output_data": log.output_data,
                "execution_time_ms": log.execution_time_ms,
            }
            for log in logs
        ],
    }
