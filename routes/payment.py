"""
TrustPay AI — Payment Routes
POST /api/payment/propose
POST /api/payment/execute
POST /api/payment/verify
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import (
    PaymentProposeRequest, PaymentProposeResponse, PaymentProposal,
    PaymentExecuteRequest, PaymentExecuteResponse,
    PaymentVerifyRequest, PaymentVerifyResponse,
    ConfirmationRequest,
)
from services.payment_service import generate_proposal, execute_mock_payment
from services.risk_service import run_post_payment_verification
from models import PaymentIntent, Transaction

router = APIRouter(prefix="/api/payment", tags=["Payment"])


@router.post("/propose", response_model=PaymentProposeResponse)
async def propose_payment(request: PaymentProposeRequest, db: Session = Depends(get_db)):
    """Generate a simulated payment proposal based on extracted intent."""
    intent = db.query(PaymentIntent).filter(PaymentIntent.id == request.intent_id).first()
    if not intent:
        raise HTTPException(status_code=404, detail="Payment intent not found")

    # Generate proposal
    proposal = generate_proposal(intent.extracted_intent)

    # Create transaction
    txn = Transaction(
        user_id=intent.user_id,
        payment_intent_id=intent.id,
        product_name=proposal["product_name"],
        merchant_name=proposal["merchant_name"],
        base_price=proposal["base_price"],
        tax=proposal["tax"],
        delivery_fee=proposal["delivery_fee"],
        total_amount=proposal["total_amount"],
        currency=proposal.get("currency", "INR"),
        product_condition=proposal.get("product_condition", "new"),
        context_message=request.context_message,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)

    return PaymentProposeResponse(
        transaction_id=txn.id,
        intent_id=intent.id,
        proposal=PaymentProposal(**proposal),
        context_message=request.context_message,
    )


@router.post("/execute", response_model=PaymentExecuteResponse)
async def execute_payment(request: PaymentExecuteRequest, db: Session = Depends(get_db)):
    """Execute a mock payment (simulated Razorpay sandbox)."""
    txn = db.query(Transaction).filter(Transaction.id == request.transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Check if payment is allowed
    if txn.decision == "BLOCK":
        raise HTTPException(status_code=403, detail="Payment was BLOCKED by risk analysis")

    if txn.decision == "ASK_FOR_CONFIRMATION" and not txn.human_confirmed:
        raise HTTPException(status_code=403, detail="Payment requires human confirmation first")

    # Execute mock payment
    result = execute_mock_payment(
        transaction_id=txn.id,
        amount=txn.total_amount,
        merchant=txn.merchant_name,
        product=txn.product_name,
    )

    # Update transaction
    txn.payment_status = result["status"]
    txn.payment_id = result["payment_id"]
    db.commit()

    return PaymentExecuteResponse(
        transaction_id=txn.id,
        payment_id=result["payment_id"],
        payment_status=result["status"],
        amount=txn.total_amount,
        merchant=txn.merchant_name,
        product=txn.product_name,
        message=result["message"],
    )


@router.post("/verify", response_model=PaymentVerifyResponse)
async def verify_payment(request: PaymentVerifyRequest, db: Session = Depends(get_db)):
    """Post-payment verification — confirms executed payment matches approved intent."""
    txn = db.query(Transaction).filter(Transaction.id == request.transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if txn.payment_status != "executed":
        raise HTTPException(status_code=400, detail="Payment not yet executed")

    # Run post-payment verification
    approved = {
        "total_amount": txn.total_amount,
        "merchant_name": txn.merchant_name,
        "product_name": txn.product_name,
    }
    executed = {
        "total_amount": txn.total_amount,  # In simulation, these match
        "merchant_name": txn.merchant_name,
        "product_name": txn.product_name,
        "payment_status": txn.payment_status,
    }

    result = await run_post_payment_verification(approved, executed)

    # Update transaction
    txn.post_payment_status = result["verification_status"]
    txn.post_payment_details = {
        "checks": result["checks"],
        "mismatches": result["mismatches"],
    }
    db.commit()

    return PaymentVerifyResponse(
        transaction_id=txn.id,
        verification_status=result["verification_status"],
        checks=result["checks"],
        mismatches=result["mismatches"],
    )


@router.post("/confirm")
async def confirm_payment(request: ConfirmationRequest, db: Session = Depends(get_db)):
    """Human-in-the-loop confirmation for ASK_FOR_CONFIRMATION decisions."""
    txn = db.query(Transaction).filter(Transaction.id == request.transaction_id).first()
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if txn.decision != "ASK_FOR_CONFIRMATION":
        raise HTTPException(status_code=400, detail="This transaction does not require confirmation")

    txn.human_confirmed = request.confirmed
    if not request.confirmed:
        txn.payment_status = "cancelled"
    db.commit()

    return {
        "transaction_id": txn.id,
        "confirmed": request.confirmed,
        "message": "Payment confirmed by user" if request.confirmed else "Payment cancelled by user",
    }
