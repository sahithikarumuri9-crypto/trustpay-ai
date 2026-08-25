"""
TrustPay AI — Configuration
Central configuration for risk thresholds, agent weights, and LLM settings.
"""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # App
    APP_NAME: str = "TrustPay AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite:///./trustpay.db"

    # LLM
    GEMINI_API_KEY: str = ""
    LLM_PROVIDER: str = "auto"  # "auto", "gemini", "mock"

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()


# ---------------------------------------------------------------------------
# Risk Agent Weights (configurable — 40/30/30 as per spec)
# ---------------------------------------------------------------------------
AGENT_WEIGHTS = {
    "intent_verification": 0.40,
    "scam_detection": 0.30,
    "behavior_anomaly": 0.30,
}

# ---------------------------------------------------------------------------
# Decision Thresholds
# ---------------------------------------------------------------------------
DECISION_THRESHOLDS = {
    "ALLOW": (0, 30),
    "WARN": (31, 60),
    "ASK_FOR_CONFIRMATION": (61, 80),
    "BLOCK": (81, 100),
}

# ---------------------------------------------------------------------------
# Override Rules (fire regardless of weighted score)
# ---------------------------------------------------------------------------
OVERRIDE_RULES = {
    "scam_probability_block": 0.8,        # scam_probability > 0.8 → force BLOCK
    "budget_exceed_ask_threshold": 0.20,   # budget exceeded by >20% → force ASK_FOR_CONFIRMATION
}

# ---------------------------------------------------------------------------
# Dominant-Signal Floor
# ---------------------------------------------------------------------------
# A weighted average of 3 agents means a single "critical" agent (score 100)
# can only ever contribute score*weight (max 40) to the final total — never
# enough on its own to cross the ASK_FOR_CONFIRMATION (61) or BLOCK (81)
# thresholds. That silently downgrades genuinely severe single-signal cases
# (e.g. a 67x-average purchase, or a scam message with one strong pattern)
# into WARN. This floor says: whatever the weighted average lands on, the
# final decision is never *lower* than what the single strongest agent score
# alone would justify. Tune these independently of DECISION_THRESHOLDS.
SINGLE_AGENT_FLOOR = {
    "BLOCK": 80,                  # any one agent >= 80 -> floor is BLOCK
    "ASK_FOR_CONFIRMATION": 60,   # any one agent >= 60 -> floor is at least ASK
    "WARN": 40,                   # any one agent >= 40 -> floor is at least WARN
}

# ---------------------------------------------------------------------------
# Synthetic User Behavior Profile (for Behavior Anomaly Agent)
# ---------------------------------------------------------------------------
SYNTHETIC_USER_PROFILE = {
    "user_id": "demo_user_001",
    "name": "Demo User",
    "avg_transaction_amount": 4500,
    "typical_range_min": 400,
    "typical_range_max": 15000,
    "typical_merchants": [
        "Amazon", "Flipkart", "BigBasket", "Swiggy", "Myntra",
        "Croma", "Reliance Digital"
    ],
    "transaction_count": 147,
    "account_age_days": 730,
}