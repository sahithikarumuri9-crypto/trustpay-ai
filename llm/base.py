"""
TrustPay AI — Base LLM Provider
Abstract interface for swappable LLM providers.
"""
from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """Abstract LLM provider — implement for each backend (mock, Gemini, etc.)."""

    @abstractmethod
    async def extract_intent(self, user_input: str) -> dict:
        """Extract structured payment intent from natural language."""
        ...

    @abstractmethod
    async def analyze_scam_context(self, context_message: str, transaction_details: dict) -> dict:
        """Analyze a message/context for scam patterns."""
        ...

    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        """General-purpose text generation."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        ...
