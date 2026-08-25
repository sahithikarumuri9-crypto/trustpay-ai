"""
TrustPay AI — Pydantic Schemas
Request/response validation for all API endpoints.
"""
from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ---------------------------------------------------------------------------
# Intent
# ---------------------------------------------------------------------------
class IntentAnalyzeRequest(BaseModel):
    user_input: str = Field(..., min_length=3, description="Natural language payment instruction")
    user_id: str = Field(default="demo_user_001")


class ExtractedIntent(BaseModel):
    product: str = ""
    purpose: str = ""
    max_amount: Optional[float] = None
    min_amount: Optional[float] = None
    condition: str = "any"  # new, refurbished, used, any
    refurbished_allowed: bool = True
    quantity: int = 1
    merchant_preference: Optional[str] = None
    urgency: str = "normal"
    raw_constraints: list[str] = []


class IntentAnalyzeResponse(BaseModel):
    intent_id: str
    raw_input: str
    extracted_intent: ExtractedIntent
    confidence: float = 0.0


# ---------------------------------------------------------------------------
# Payment Proposal
# ---------------------------------------------------------------------------
class PaymentProposeRequest(BaseModel):
    intent_id: str
    context_message: Optional[str] = None  # Optional scam-context message


class PaymentProposal(BaseModel):
    product_name: str
    merchant_name: str
    base_price: float
    tax: float
    delivery_fee: float
    total_amount: float
    currency: str = "INR"
    product_condition: str = "new"


class PaymentProposeResponse(BaseModel):
    transaction_id: str
    intent_id: str
    proposal: PaymentProposal
    context_message: Optional[str] = None


# ---------------------------------------------------------------------------
# Risk Analysis
# ---------------------------------------------------------------------------
class RiskAnalyzeRequest(BaseModel):
    transaction_id: str


class AgentResult(BaseModel):
    agent_name: str
    agent_step: str
    score: float = 0.0
    details: dict = {}
    reasons: list[str] = []
    execution_time_ms: int = 0


class RiskAnalyzeResponse(BaseModel):
    transaction_id: str
    agents: list[AgentResult] = []
    weighted_score: float = 0.0
    final_decision: str = ""
    override_applied: Optional[str] = None
    decision_reasons: list[str] = []
    risk_level: str = ""  # LOW, MEDIUM, HIGH, CRITICAL


# ---------------------------------------------------------------------------
# Decision / Confirmation
# ---------------------------------------------------------------------------
class PaymentDecisionRequest(BaseModel):
    transaction_id: str


class PaymentDecisionResponse(BaseModel):
    transaction_id: str
    decision: str
    risk_score: float
    reasons: list[str] = []
    requires_confirmation: bool = False
    explainability: dict = {}


class ConfirmationRequest(BaseModel):
    transaction_id: str
    confirmed: bool
    reason: Optional[str] = None


# ---------------------------------------------------------------------------
# Payment Execution
# ---------------------------------------------------------------------------
class PaymentExecuteRequest(BaseModel):
    transaction_id: str


class PaymentExecuteResponse(BaseModel):
    transaction_id: str
    payment_id: str
    payment_status: str
    amount: float
    merchant: str
    product: str
    message: str


# ---------------------------------------------------------------------------
# Post-Payment Verification
# ---------------------------------------------------------------------------
class PaymentVerifyRequest(BaseModel):
    transaction_id: str


class PaymentVerifyResponse(BaseModel):
    transaction_id: str
    verification_status: str  # verified, mismatch
    checks: list[dict] = []
    mismatches: list[str] = []


# ---------------------------------------------------------------------------
# Transaction History
# ---------------------------------------------------------------------------
class TransactionSummary(BaseModel):
    id: str
    product_name: Optional[str] = None
    merchant_name: Optional[str] = None
    total_amount: float = 0.0
    decision: Optional[str] = None
    risk_score: Optional[float] = None
    payment_status: str = "pending"
    created_at: Optional[datetime] = None
    raw_input: Optional[str] = None


class TransactionDetail(TransactionSummary):
    extracted_intent: Optional[dict] = None
    context_message: Optional[str] = None
    risk_assessment: Optional[dict] = None
    agent_logs: list[dict] = []
    post_payment_status: Optional[str] = None
    post_payment_details: Optional[dict] = None
    human_confirmed: bool = False


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------
class DemoScenario(BaseModel):
    id: int
    name: str
    description: str
    user_input: str
    context_message: Optional[str] = None
    expected_decision: str
    category: str  # safe, budget_violation, scam, anomaly, ambiguous


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------
class EvalMetrics(BaseModel):
    total_cases: int = 0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    accuracy: float = 0.0
    false_positive_rate: float = 0.0
    false_positive_cost_examples: list[dict] = []
    confusion_matrix: dict = {}
    misclassification_examples: list[dict] = []
    decision_distribution: dict = {}
