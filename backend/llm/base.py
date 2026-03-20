"""LLMClient abstract base class and LLMResponse model.

Defines the contract for all LLM provider implementations. Modes interact
with the LLM exclusively through this interface — never through a concrete
provider client directly.

SDD references: FR-D-12 (provider configurability), FR-A-02 (Tool Use API).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel


class LLMResponse(BaseModel):
    """Structured response from an LLM call.

    Fields:
        nutzeraeusserung: The text portion of the LLM response (chat message for the user).
        tool_input: The parsed input dict from the tool_use block (contains 'patches' list).
        debug_request: Full request payload (only set when llm_debug_log=True).
    """

    nutzeraeusserung: str
    tool_input: dict  # type: ignore[type-arg]
    debug_request: dict | None = None  # type: ignore[type-arg]
    usage: dict | None = None  # type: ignore[type-arg]  # Token usage from API response


class LLMClient(ABC):
    """Abstract base class for LLM provider clients (SDD FR-D-12).

    All cognitive modes receive an LLMClient instance and call complete()
    to communicate with the LLM. The concrete provider is selected at
    startup via Settings.llm_provider and the factory function.
    """

    @abstractmethod
    async def complete(
        self,
        system: str,
        messages: list[dict],  # type: ignore[type-arg]
        tools: list[dict] | None = None,  # type: ignore[type-arg]
        tool_choice: dict | None = None,  # type: ignore[type-arg]
    ) -> LLMResponse:
        """Send a request to the LLM and return a structured response.

        Args:
            system: System prompt text.
            messages: Conversation history in [{role, content}] format.
            tools: Tool definitions for the LLM (Anthropic tool schema format).
            tool_choice: Tool choice configuration. Defaults to forcing apply_patches.

        Returns:
            LLMResponse with extracted nutzeraeusserung and tool_input.

        Raises:
            ValueError: If the LLM response violates the expected contract.
            RuntimeError: If the LLM API call fails.
        """
        ...
