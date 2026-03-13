"""LLM client factory — creates the correct LLMClient based on settings.

All code that needs an LLM client should call create_llm_client(settings)
rather than importing a concrete client directly.

SDD references: FR-D-12 (provider configurability — no code change to switch).
"""

from __future__ import annotations

from config import Settings
from llm.base import LLMClient


def create_llm_client(settings: Settings) -> LLMClient:
    """Create and return the LLMClient matching settings.llm_provider.

    Args:
        settings: Application settings with llm_provider field.

    Returns:
        LLMClient instance for the configured provider.

    Raises:
        ValueError: If llm_provider is not a recognised provider string.
    """
    if settings.llm_provider == "anthropic":
        from llm.anthropic_client import AnthropicClient

        return AnthropicClient(settings)

    if settings.llm_provider == "openai":
        from llm.openai_client import OpenAIClient

        return OpenAIClient(settings)

    if settings.llm_provider == "ollama":
        from llm.ollama_client import OllamaClient

        return OllamaClient(settings)

    raise ValueError(
        f"Unbekannter LLM-Provider '{settings.llm_provider}'. Erlaubt: 'anthropic', 'openai', 'ollama'."
    )
