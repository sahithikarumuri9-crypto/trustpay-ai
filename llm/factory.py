"""
TrustPay AI — LLM Factory
Selects the appropriate LLM provider based on environment config.
"""
from config import settings
from llm.base import BaseLLMProvider
from llm.mock_provider import MockLLMProvider


def get_llm_provider() -> BaseLLMProvider:
    """Return the configured LLM provider instance."""
    provider_choice = settings.LLM_PROVIDER.lower()

    if provider_choice == "gemini":
        return _try_gemini()
    elif provider_choice == "mock":
        return MockLLMProvider()
    else:
        # "auto" — try Gemini first, fall back to mock
        if settings.GEMINI_API_KEY:
            return _try_gemini()
        return MockLLMProvider()


def _try_gemini() -> BaseLLMProvider:
    """Attempt to create a Gemini provider; fall back to mock."""
    try:
        from llm.gemini_provider import GeminiLLMProvider
        if not settings.GEMINI_API_KEY:
            print("[LLM] No GEMINI_API_KEY found — using mock provider")
            return MockLLMProvider()
        provider = GeminiLLMProvider(api_key=settings.GEMINI_API_KEY)
        print(f"[LLM] Using Gemini provider")
        return provider
    except Exception as e:
        print(f"[LLM] Gemini init failed ({e}) — falling back to mock provider")
        return MockLLMProvider()


# Singleton
_provider_instance: BaseLLMProvider | None = None


def get_llm() -> BaseLLMProvider:
    """Get or create the singleton LLM provider."""
    global _provider_instance
    if _provider_instance is None:
        _provider_instance = get_llm_provider()
        print(f"[LLM] Initialized provider: {_provider_instance.provider_name}")
    return _provider_instance
