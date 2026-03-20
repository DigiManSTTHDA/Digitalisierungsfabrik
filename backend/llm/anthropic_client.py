"""AnthropicClient — LLMClient implementation using the Anthropic Messages API.

Uses the anthropic SDK (≥ 0.25) with Tool Use support. Enforces
tool_choice=apply_patches by default so the LLM always returns structured
patches alongside its text response.

SDD references: FR-A-02 (Tool Use API), FR-D-12 (provider configurability),
NFR 8.1.3 (Beobachtbarkeit — optional LLM I/O logging).
"""

from __future__ import annotations

import anthropic
import structlog

from config import Settings
from llm.base import LLMClient, LLMResponse

logger = structlog.get_logger(__name__)

# Default tool_choice: force the LLM to use apply_patches (SDD 6.5.2 Output-Kontrakt)
_DEFAULT_TOOL_CHOICE: dict[str, str] = {"type": "tool", "name": "apply_patches"}


class AnthropicClient(LLMClient):
    """LLM client implementation for the Anthropic Messages API.

    Reads api_key and model from the injected Settings instance — no hardcoded values.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = anthropic.AsyncAnthropic(api_key=settings.llm_api_key)

    async def complete(
        self,
        system: str,
        messages: list[dict],  # type: ignore[type-arg]
        tools: list[dict] | None = None,  # type: ignore[type-arg]
        tool_choice: dict | None = None,  # type: ignore[type-arg]
    ) -> LLMResponse:
        """Call Anthropic Messages API with Tool Use and return structured response.

        Extracts the text block as nutzeraeusserung and the tool_use block's
        input dict as tool_input. Raises ValueError if no tool_use block is found.
        """
        effective_tool_choice = tool_choice if tool_choice is not None else _DEFAULT_TOOL_CHOICE

        if self._settings.llm_log_enabled:
            logger.info(
                "anthropic_client.request",
                model=self._settings.llm_model,
                system_prompt_length=len(system),
                message_count=len(messages),
            )

        kwargs: dict = {  # type: ignore[type-arg]
            "model": self._settings.llm_model,
            "max_tokens": 4096,
            "system": system,
            "messages": messages,
            "tool_choice": effective_tool_choice,
        }
        if tools is not None:
            kwargs["tools"] = tools

        response = await self._client.messages.create(**kwargs)

        # Parse response: extract tool_use block (nutzeraeusserung is inside tool_input)
        tool_input: dict | None = None  # type: ignore[type-arg]

        for block in response.content:
            if block.type == "tool_use":
                tool_input = block.input

        if tool_input is None:
            raise ValueError(
                "Anthropic-Antwort enthält keinen tool_use-Block — "
                "Output-Kontrakt-Verletzung (SDD 6.5.2)"
            )

        nutzeraeusserung = str(tool_input.get("nutzeraeusserung", ""))

        if self._settings.llm_log_enabled:
            logger.info(
                "anthropic_client.response",
                nutzeraeusserung_length=len(nutzeraeusserung),
                has_tool_use=True,
            )

        # Extract token usage from API response
        usage = None
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            }

        # Capture full request for debug logging when enabled
        debug_request = None
        if self._settings.llm_debug_log:
            debug_request = {
                "system_prompt": system,
                "messages": messages,
                "tool_choice": effective_tool_choice,
                "model": self._settings.llm_model,
            }

        return LLMResponse(
            nutzeraeusserung=nutzeraeusserung,
            tool_input=tool_input,
            debug_request=debug_request,
            usage=usage,
        )
