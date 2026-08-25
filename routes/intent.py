"""
TrustPay AI — Intent Routes
POST /api/intent/analyze
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import IntentAnalyzeRequest, IntentAnalyzeResponse, ExtractedIntent
from agents.intent_agent import IntentAgent
from models import PaymentIntent, User

router = APIRouter(prefix="/api/intent", tags=["Intent"])


@router.post("/analyze", response_model=IntentAnalyzeResponse)
async def analyze_intent(request: IntentAnalyzeRequest, db: Session = Depends(get_db)):
    """Extract structured payment intent from natural language input."""
    # Ensure user exists
    user = db.query(User).filter(User.id == request.user_id).first()
    if not user:
        user = User(id=request.user_id, name="Demo User")
        db.add(user)
        db.commit()

    # Run Intent Agent
    agent = IntentAgent()
    result = await agent.run(user_input=request.user_input)

    extracted = result["extracted_intent"]

    # Save to database
    intent = PaymentIntent(
        user_id=request.user_id,
        raw_input=request.user_input,
        extracted_intent=extracted,
    )
    db.add(intent)
    db.commit()
    db.refresh(intent)

    return IntentAnalyzeResponse(
        intent_id=intent.id,
        raw_input=request.user_input,
        extracted_intent=ExtractedIntent(**extracted),
        confidence=result["confidence"],
    )
