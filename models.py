"""
TrustPay AI — Database Models
5 tables: users, payment_intents, transactions, risk_assessments, agent_logs
"""
import datetime
import uuid
from sqlalchemy import (
    Column, String, Integer, Float, Text, DateTime, Boolean, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from database import Base


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False, default="Demo User")
    email = Column(String(200), nullable=True)
    avg_transaction_amount = Column(Float, default=2500.0)
    typical_range_min = Column(Float, default=500.0)
    typical_range_max = Column(Float, default=5000.0)
    typical_merchants = Column(JSON, default=list)
    transaction_count = Column(Integer, default=147)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    payment_intents = relationship("PaymentIntent", back_populates="user")
    transactions = relationship("Transaction", back_populates="user")


class PaymentIntent(Base):
    __tablename__ = "payment_intents"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    raw_input = Column(Text, nullable=False)
    extracted_intent = Column(JSON, nullable=True)  # Structured JSON from Intent Agent
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="payment_intents")
    transactions = relationship("Transaction", back_populates="payment_intent")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    payment_intent_id = Column(String, ForeignKey("payment_intents.id"), nullable=False)

    # Proposed payment details (from simulated commerce agent)
    product_name = Column(String(300), nullable=True)
    merchant_name = Column(String(300), nullable=True)
    base_price = Column(Float, default=0.0)
    tax = Column(Float, default=0.0)
    delivery_fee = Column(Float, default=0.0)
    total_amount = Column(Float, default=0.0)
    currency = Column(String(10), default="INR")
    product_condition = Column(String(50), default="new")  # new, refurbished, used

    # Context message (for scam detection)
    context_message = Column(Text, nullable=True)

    # Decision
    decision = Column(String(30), nullable=True)  # ALLOW, WARN, ASK_FOR_CONFIRMATION, BLOCK
    risk_score = Column(Float, nullable=True)  # 0-100
    human_confirmed = Column(Boolean, default=False)

    # Payment execution
    payment_status = Column(String(30), default="pending")  # pending, executed, failed, cancelled
    payment_id = Column(String(100), nullable=True)  # Mock Razorpay payment ID

    # Post-payment verification
    post_payment_status = Column(String(30), nullable=True)  # verified, mismatch
    post_payment_details = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="transactions")
    payment_intent = relationship("PaymentIntent", back_populates="transactions")
    risk_assessments = relationship("RiskAssessment", back_populates="transaction")
    agent_logs = relationship("AgentLog", back_populates="transaction")


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(String, primary_key=True, default=generate_uuid)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)

    # Agent scores
    intent_match_score = Column(Float, nullable=True)  # 0-100 from Intent Verification
    intent_violated_constraints = Column(JSON, nullable=True)
    scam_probability = Column(Float, nullable=True)  # 0-1 from Scam Detection
    scam_detected_patterns = Column(JSON, nullable=True)
    behavior_anomaly_score = Column(Float, nullable=True)  # 0-100 from Behavior Anomaly
    behavior_details = Column(JSON, nullable=True)

    # Final decision
    weighted_score = Column(Float, nullable=True)
    final_decision = Column(String(30), nullable=True)
    override_applied = Column(String(100), nullable=True)
    decision_reasons = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    transaction = relationship("Transaction", back_populates="risk_assessments")


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    agent_step = Column(String(50), nullable=True)  # UNDERSTAND, OBSERVE, ANALYZE, REASON, DECIDE, ACT, MONITOR
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    transaction = relationship("Transaction", back_populates="agent_logs")
