"""OpenAIClient — LLMClient implementation using the OpenAI Chat Completions API.

Uses OpenAI Function Calling (tool_choice="required") to enforce structured
patch output. Translates between Anthropic tool schema format (used internally)
and OpenAI function schema format transparently.

SDD references: FR-D-12 (provider configurability), ADR-005.
"""

from __future__ import annotations

import json

import structlog
from openai import AsyncOpenAI

from config import Settings
from llm.base import LLMClient, LLMResponse

logger = structlog.get_logger(__name__)


def _anthropic_tool_to_openai(tool: dict) -> dict:  # type: ignore[type-arg]
    """Translate an Anthropic tool definition to OpenAI function schema.

    Anthropic uses `input_schema`; OpenAI uses `parameters` inside `function`.
    """
    return {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool.get("description", ""),
            "parameters": tool.get("input_schema", {}),
        },
    }


class OpenAIClient(LLMClient):
    """LLM client implementation for the OpenAI Chat Completions API.

    Reads api_key and model from the injected Settings instance.
    Supports any OpenAI model with function calling (gpt-4o, gpt-4-turbo, etc.).
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = AsyncOpenAI(api_key=settings.llm_api_key)

    async def complete(
        self,
        system: str,
        messages: list[dict],  # type: ignore[type-arg]
        tools: list[dict] | None = None,  # type: ignore[type-arg]
        tool_choice: dict | None = None,  # type: ignore[type-arg]
    ) -> LLMResponse:
        """Call OpenAI Chat Completions API with function calling.

        Translates Anthropic tool schema to OpenAI format, sends the request,
        and maps the response back to LLMResponse.

        Raises:
            ValueError: If the model did not call a function (tool_use missing).
        """
        openai_messages = [{"role": "system", "content": system}] + list(messages)

        openai_tools = [_anthropic_tool_to_openai(t) for t in tools] if tools else None

        if self._settings.llm_log_enabled:
            logger.info(
                "openai_client.request",
                model=self._settings.llm_model,
                system_prompt_length=len(system),
                message_count=len(messages),
            )

        kwargs: dict = {  # type: ignore[type-arg]
            "model": self._settings.llm_model,
            "max_tokens": 4096,
            "messages": openai_messages,
        }
        if openai_tools:
            kwargs["tools"] = openai_tools
            # Translate Anthropic tool_choice format to OpenAI format.
            # "auto" allows the LLM to respond without a tool call (e.g. pure questions),
            # "required" forces a tool call every turn.
            if tool_choice and tool_choice.get("type") == "auto":
                kwargs["tool_choice"] = "auto"
            else:
                kwargs["tool_choice"] = "required"

        response = await self._client.chat.completions.create(**kwargs)

        choice = response.choices[0]
        message = choice.message

        tool_input: dict | None = None  # type: ignore[type-arg]

        if message.tool_calls:
            call = message.tool_calls[0]
            tool_input = json.loads(call.function.arguments)

        # When tools were requested, nutzeraeusserung is inside tool_input.
        # When no tools (e.g. Moderator), nutzeraeusserung is message.content.
        if tool_input is not None:
            nutzeraeusserung = str(tool_input.get("nutzeraeusserung", ""))
        elif message.content:
            nutzeraeusserung = message.content
            tool_input = {}  # Moderator: no patches, just text
        else:
            raise ValueError(
                "OpenAI-Antwort enthält weder function_call noch text — "
                "Output-Kontrakt-Verletzung (SDD 6.5.2)"
            )

        if self._settings.llm_log_enabled:
            logger.info(
                "openai_client.response",
                nutzeraeusserung_length=len(nutzeraeusserung),
                has_tool_use=bool(message.tool_calls),
            )

        # Extract token usage from API response
        usage = None
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        # Capture full request + response for debug logging when enabled (CR-010)
        debug_request = None
        if self._settings.llm_debug_log:
            debug_request = {
                "system_prompt": system,
                "messages": messages,
                "tool_choice": kwargs.get("tool_choice"),
                "model": self._settings.llm_model,
                "raw_tool_input": tool_input,
                "raw_nutzeraeusserung": nutzeraeusserung,
            }

        return LLMResponse(
            nutzeraeusserung=nutzeraeusserung,
            tool_input=tool_input,
            debug_request=debug_request,
            usage=usage,
        )
