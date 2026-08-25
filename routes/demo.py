"""
TrustPay AI — Demo Routes
GET /api/demo/scenarios
POST /api/demo/run/{scenario_id}
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import DemoScenario
from models import PaymentIntent, Transaction, User
from agents.intent_agent import IntentAgent
from services.payment_service import generate_proposal
from services.risk_service import run_risk_analysis

router = APIRouter(prefix="/api/demo", tags=["Demo"])

# The 5 demo scenarios from the spec
DEMO_SCENARIOS = [
    {
        "id": 1,
        "name": "Safe Payment",
        "description": "A normal, safe purchase within budget — should be ALLOWED",
        "user_input": "Buy headphones under ₹5,000",
        "context_message": None,
        "expected_decision": "ALLOW",
        "category": "safe",
        "proposal_override": {
            "product_name": "boAt Rockerz 450",
            "merchant_name": "SoundBazaar",
            "base_price": 1499,
            "tax": 244,
            "delivery_fee": 49,
            "total_amount": 1792,
            "product_condition": "new",
        },
    },
    {
        "id": 2,
        "name": "Budget Violation",
        "description": "Laptop purchase where total exceeds user's ₹60,000 budget — should BLOCK or ASK_FOR_CONFIRMATION",
        "user_input": "Buy a laptop for college under ₹60,000. It must be new, not refurbished.",
        "context_message": None,
        "expected_decision": "ASK_FOR_CONFIRMATION",
        "category": "budget_violation",
        "proposal_override": {
            "product_name": "Dell Inspiron 15",
            "merchant_name": "ABC Electronics",
            "base_price": 54999,
            "tax": 8999,
            "delivery_fee": 499,
            "total_amount": 64497,
            "product_condition": "new",
        },
    },
    {
        "id": 3,
        "name": "Scam Context",
        "description": "Electricity disconnection threat — classic scam pattern, should BLOCK on context risk alone",
        "user_input": "Pay electricity bill",
        "context_message": "Your electricity will be disconnected today unless you pay ₹4,500 now. This is your final notice from the electricity board. Service will be suspended immediately.",
        "expected_decision": "BLOCK",
        "category": "scam",
        "proposal_override": {
            "product_name": "Electricity Bill Payment",
            "merchant_name": "State Electricity Board",
            "base_price": 4500,
            "tax": 0,
            "delivery_fee": 0,
            "total_amount": 4500,
            "product_condition": "new",
        },
    },
    {
        "id": 4,
        "name": "Unusual Behavior",
        "description": "₹45,000 purchase when user's typical range is ₹500-₹5,000 — should ASK_FOR_CONFIRMATION",
        "user_input": "Buy a premium smartphone",
        "context_message": None,
        "expected_decision": "ASK_FOR_CONFIRMATION",
        "category": "anomaly",
        "proposal_override": {
            "product_name": "Samsung Galaxy S24 Ultra",
            "merchant_name": "Mobile Hub",
            "base_price": 35000,
            "tax": 5688,
            "delivery_fee": 0,
            "total_amount": 40688,
            "product_condition": "new",
        },
    },
    {
        "id": 5,
        "name": "Ambiguous Edge Case",
        "description": "Hospital emergency — legitimate urgency that may trigger false-positive scam detection",
        "user_input": "Pay hospital bill immediately",
        "context_message": "Emergency admission. Patient needs immediate treatment. Please pay ₹45,000 hospital deposit urgently.",
        "expected_decision": "ASK_FOR_CONFIRMATION",
        "category": "ambiguous",
        "proposal_override": {
            "product_name": "Hospital Emergency Deposit",
            "merchant_name": "Apollo Hospital",
            "base_price": 45000,
            "tax": 0,
            "delivery_fee": 0,
            "total_amount": 45000,
            "product_condition": "new",
        },
    },
]


@router.get("/scenarios")
async def get_scenarios():
    """Return the 5 demo scenarios."""
    return [
        {
            "id": s["id"],
            "name": s["name"],
            "description": s["description"],
            "user_input": s["user_input"],
            "context_message": s["context_message"],
            "expected_decision": s["expected_decision"],
            "category": s["category"],
        }
        for s in DEMO_SCENARIOS
    ]


@router.post("/run/{scenario_id}")
async def run_scenario(scenario_id: int, db: Session = Depends(get_db)):
    """Run a demo scenario end-to-end and return complete results."""
    scenario = next((s for s in DEMO_SCENARIOS if s["id"] == scenario_id), None)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")

    user_id = "demo_user_001"

    # Ensure demo user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(
            id=user_id, name="Demo User",
            avg_transaction_amount=2500,
            typical_range_min=500, typical_range_max=5000,
            typical_merchants=["Amazon", "Flipkart", "BigBasket", "Swiggy", "Myntra"],
            transaction_count=147,
        )
        db.add(user)
        db.commit()

    # Step 1: Intent extraction
    intent_agent = IntentAgent()
    intent_result = await intent_agent.run(user_input=scenario["user_input"])
    extracted_intent = intent_result["extracted_intent"]

    # Save intent
    intent = PaymentIntent(
        user_id=user_id,
        raw_input=scenario["user_input"],
        extracted_intent=extracted_intent,
    )
    db.add(intent)
    db.commit()
    db.refresh(intent)

    # Step 2: Payment proposal (use override for consistent demos)
    proposal = scenario["proposal_override"]

    # Save transaction
    txn = Transaction(
        user_id=user_id,
        payment_intent_id=intent.id,
        product_name=proposal["product_name"],
        merchant_name=proposal["merchant_name"],
        base_price=proposal["base_price"],
        tax=proposal["tax"],
        delivery_fee=proposal["delivery_fee"],
        total_amount=proposal["total_amount"],
        product_condition=proposal.get("product_condition", "new"),
        context_message=scenario.get("context_message"),
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)

    # Step 3: Risk analysis
    risk_result = await run_risk_analysis(
        extracted_intent=extracted_intent,
        proposal=proposal,
        context_message=scenario.get("context_message"),
    )

    decision = risk_result["decision"]

    # Update transaction
    txn.decision = decision["decision"]
    txn.risk_score = decision["weighted_score"]
    db.commit()

    # Step 4: Save risk assessment and agent logs
    from models import RiskAssessment, AgentLog
    assessment = RiskAssessment(
        transaction_id=txn.id,
        intent_match_score=risk_result["intent_verification"].get("score", 0),
        intent_violated_constraints=risk_result["intent_verification"].get("violated_constraints", []),
        scam_probability=risk_result["scam_detection"].get("scam_probability", 0),
        scam_detected_patterns=risk_result["scam_detection"].get("detected_patterns", []),
        behavior_anomaly_score=risk_result["behavior_anomaly"].get("score", 0),
        behavior_details=risk_result["behavior_anomaly"].get("anomalies", []),
        weighted_score=decision["weighted_score"],
        final_decision=decision["decision"],
        override_applied=decision.get("override_applied"),
        decision_reasons=decision["reasons"],
    )
    db.add(assessment)

    for log in risk_result.get("agent_logs", []):
        agent_log = AgentLog(
            transaction_id=txn.id,
            agent_name=log["agent_name"],
            agent_step=log["agent_step"],
            input_data=log.get("input_data"),
            output_data=log.get("output_data"),
            execution_time_ms=log.get("execution_time_ms", 0),
        )
        db.add(agent_log)

    db.commit()

    return {
        "scenario": {
            "id": scenario["id"],
            "name": scenario["name"],
            "description": scenario["description"],
            "expected_decision": scenario["expected_decision"],
        },
        "intent": {
            "raw_input": scenario["user_input"],
            "extracted": extracted_intent,
            "confidence": intent_result["confidence"],
        },
        "proposal": proposal,
        "risk_analysis": {
            "intent_verification": {
                "score": risk_result["intent_verification"].get("score", 0),
                "violated_constraints": risk_result["intent_verification"].get("violated_constraints", []),
                "reasoning": risk_result["intent_verification"].get("reasoning", ""),
            },
            "scam_detection": {
                "score": risk_result["scam_detection"].get("score", 0),
                "scam_probability": risk_result["scam_detection"].get("scam_probability", 0),
                "detected_patterns": risk_result["scam_detection"].get("detected_patterns", []),
                "analysis": risk_result["scam_detection"].get("analysis", ""),
            },
            "behavior_anomaly": {
                "score": risk_result["behavior_anomaly"].get("score", 0),
                "anomalies": risk_result["behavior_anomaly"].get("anomalies", []),
                "reasoning": risk_result["behavior_anomaly"].get("reasoning", ""),
            },
        },
        "decision": {
            "final_decision": decision["decision"],
            "weighted_score": decision["weighted_score"],
            "risk_level": decision["risk_level"],
            "override_applied": decision.get("override_applied"),
            "reasons": decision["reasons"],
            "agent_scores": decision.get("agent_scores", {}),
            "explainability": decision.get("explainability", {}),
        },
        "transaction_id": txn.id,
    }
