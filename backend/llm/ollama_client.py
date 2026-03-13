"""OllamaClient — stub LLM client for local Ollama provider.

Config-selectable via LLM_PROVIDER=ollama but not yet functional.
Raises NotImplementedError on any call — placeholder for future implementation.

SDD references: FR-D-12 (provider configurability).
"""

from __future__ import annotations

from config import Settings
from llm.base import LLMClient, LLMResponse


class OllamaClient(LLMClient):
    """Stub LLM client for Ollama — raises NotImplementedError.

    This stub ensures LLM_PROVIDER=ollama is accepted by the factory
    without code changes, fulfilling FR-D-12. Full implementation deferred.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def complete(
        self,
        system: str,
        messages: list[dict],  # type: ignore[type-arg]
        tools: list[dict] | None = None,  # type: ignore[type-arg]
        tool_choice: dict | None = None,  # type: ignore[type-arg]
    ) -> LLMResponse:
        """Not implemented — raises NotImplementedError."""
        raise NotImplementedError(
            "OllamaClient ist noch nicht vollständig implementiert. "
            "Bitte LLM_PROVIDER=anthropic setzen."
        )
