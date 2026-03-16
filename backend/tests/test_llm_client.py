"""Tests for LLM client abstraction: LLMClient ABC, AnthropicClient, OllamaClient, factory.

Coverage:
- Story 04-01: LLMClient ABC, LLMResponse, AnthropicClient
- Story 04-02: OllamaClient stub, create_llm_client factory
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from config import Settings
from llm.base import LLMResponse

# ---------------------------------------------------------------------------
# Story 04-01 — LLMClient is abstract, LLMResponse is a Pydantic model
# ---------------------------------------------------------------------------


def test_llm_response_has_required_fields() -> None:
    resp = LLMResponse(nutzeraeusserung="Hallo", tool_input={"patches": []})
    assert resp.nutzeraeusserung == "Hallo"
    assert resp.tool_input == {"patches": []}


def test_llm_response_json_round_trip() -> None:
    resp = LLMResponse(nutzeraeusserung="Test", tool_input={"patches": [{"op": "add"}]})
    json_str = resp.model_dump_json()
    resp2 = LLMResponse.model_validate_json(json_str)
    assert resp2.nutzeraeusserung == "Test"
    assert resp2.tool_input == {"patches": [{"op": "add"}]}


# ---------------------------------------------------------------------------
# Story 04-01 — AnthropicClient: positive test (text + tool_use response)
# ---------------------------------------------------------------------------


async def test_anthropic_client_positive_text_and_tool_use() -> None:
    """Mock anthropic SDK returns text + tool_use blocks → correct LLMResponse."""
    from llm.anthropic_client import AnthropicClient

    settings = Settings(
        llm_provider="anthropic",
        llm_api_key="sk-test-key",
        llm_model="claude-test",
        llm_log_enabled=False,
    )
    client = AnthropicClient(settings)

    # Build a mock response matching Anthropic Messages API structure
    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = "Ich helfe Ihnen gerne."

    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.name = "apply_patches"
    tool_block.input = {
        "nutzeraeusserung": "Ich helfe Ihnen gerne.",
        "patches": [{"op": "add", "path": "/slots/s1", "value": {}}],
    }

    mock_response = MagicMock()
    mock_response.content = [text_block, tool_block]

    mock_messages = MagicMock()
    mock_messages.create = AsyncMock(return_value=mock_response)

    with patch.object(client, "_client") as mock_client:
        mock_client.messages = mock_messages
        result = await client.complete(
            system="System prompt",
            messages=[{"role": "user", "content": "Hallo"}],
            tools=[{"name": "apply_patches", "input_schema": {}}],
        )

    assert isinstance(result, LLMResponse)
    assert result.nutzeraeusserung == "Ich helfe Ihnen gerne."
    assert "patches" in result.tool_input


# ---------------------------------------------------------------------------
# Story 04-01 — AnthropicClient: negative test (no tool_use → ValueError)
# ---------------------------------------------------------------------------


async def test_anthropic_client_no_tool_use_raises_value_error() -> None:
    """Response without tool_use block → AnthropicClient raises ValueError."""
    from llm.anthropic_client import AnthropicClient

    settings = Settings(
        llm_provider="anthropic",
        llm_api_key="sk-test-key",
        llm_model="claude-test",
        llm_log_enabled=False,
    )
    client = AnthropicClient(settings)

    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = "Keine Tool-Nutzung."

    mock_response = MagicMock()
    mock_response.content = [text_block]

    mock_messages = MagicMock()
    mock_messages.create = AsyncMock(return_value=mock_response)

    with patch.object(client, "_client") as mock_client:
        mock_client.messages = mock_messages
        with pytest.raises(ValueError, match="tool_use"):
            await client.complete(
                system="System prompt",
                messages=[{"role": "user", "content": "Hallo"}],
            )


# ---------------------------------------------------------------------------
# Story 04-01 — AnthropicClient: API error propagated
# ---------------------------------------------------------------------------


async def test_anthropic_client_api_error_propagated() -> None:
    """anthropic.APIStatusError is propagated from AnthropicClient.complete()."""
    import anthropic
    import httpx

    from llm.anthropic_client import AnthropicClient

    settings = Settings(
        llm_provider="anthropic",
        llm_api_key="sk-test-key",
        llm_model="claude-test",
        llm_log_enabled=False,
    )
    client = AnthropicClient(settings)

    # Construct a real anthropic.APIStatusError matching the AC requirement
    req = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    resp = httpx.Response(status_code=500, request=req)
    api_error = anthropic.APIStatusError("Internal Server Error", response=resp, body=None)

    mock_messages = MagicMock()
    mock_messages.create = AsyncMock(side_effect=api_error)

    with patch.object(client, "_client") as mock_client:
        mock_client.messages = mock_messages
        with pytest.raises(anthropic.APIStatusError):
            await client.complete(
                system="System prompt",
                messages=[{"role": "user", "content": "Hallo"}],
            )


# ---------------------------------------------------------------------------
# Story 04-01 — AnthropicClient: default tool_choice
# ---------------------------------------------------------------------------


async def test_anthropic_client_default_tool_choice() -> None:
    """When tool_choice is not passed, apply_patches is used by default."""
    from llm.anthropic_client import AnthropicClient

    settings = Settings(
        llm_provider="anthropic",
        llm_api_key="sk-test-key",
        llm_model="claude-test",
        llm_log_enabled=False,
    )
    client = AnthropicClient(settings)

    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = "Ok"

    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.name = "apply_patches"
    tool_block.input = {"nutzeraeusserung": "Ok", "patches": []}

    mock_response = MagicMock()
    mock_response.content = [text_block, tool_block]

    mock_messages = MagicMock()
    mock_messages.create = AsyncMock(return_value=mock_response)

    with patch.object(client, "_client") as mock_client:
        mock_client.messages = mock_messages
        await client.complete(
            system="System prompt",
            messages=[{"role": "user", "content": "Hallo"}],
            tools=[{"name": "apply_patches", "input_schema": {}}],
        )

    # Verify tool_choice was passed in the create() call
    call_kwargs = mock_messages.create.call_args
    assert call_kwargs.kwargs["tool_choice"] == {"type": "tool", "name": "apply_patches"}


# ---------------------------------------------------------------------------
# Story 04-02 — OllamaClient stub raises NotImplementedError
# ---------------------------------------------------------------------------


async def test_ollama_client_raises_not_implemented() -> None:
    from llm.ollama_client import OllamaClient

    settings = Settings(llm_provider="ollama", llm_api_key="", llm_model="llama3")
    client = OllamaClient(settings)

    with pytest.raises(NotImplementedError, match="OllamaClient"):
        await client.complete(system="test", messages=[])


# ---------------------------------------------------------------------------
# Story 04-02 — Factory: create_llm_client
# ---------------------------------------------------------------------------


def test_factory_returns_anthropic_client() -> None:
    from llm.anthropic_client import AnthropicClient
    from llm.factory import create_llm_client

    settings = Settings(llm_provider="anthropic", llm_api_key="sk-test", llm_model="claude-test")
    client = create_llm_client(settings)
    assert isinstance(client, AnthropicClient)


def test_factory_returns_ollama_client() -> None:
    from llm.factory import create_llm_client
    from llm.ollama_client import OllamaClient

    settings = Settings(llm_provider="ollama", llm_api_key="", llm_model="llama3")
    client = create_llm_client(settings)
    assert isinstance(client, OllamaClient)


# ---------------------------------------------------------------------------
# Story 04-01 — AnthropicClient: logging when llm_log_enabled=True (AC9)
# ---------------------------------------------------------------------------


async def test_anthropic_client_logs_when_enabled() -> None:
    """When llm_log_enabled=True, structlog is called with request and response info."""
    from llm.anthropic_client import AnthropicClient

    settings = Settings(
        llm_provider="anthropic",
        llm_api_key="sk-test-key",
        llm_model="claude-log-test",
        llm_log_enabled=True,
    )
    client = AnthropicClient(settings)

    text_block = MagicMock()
    text_block.type = "text"
    text_block.text = "Log-Test-Antwort"

    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.name = "apply_patches"
    tool_block.input = {"nutzeraeusserung": "Ok", "patches": []}

    mock_response = MagicMock()
    mock_response.content = [text_block, tool_block]

    mock_messages = MagicMock()
    mock_messages.create = AsyncMock(return_value=mock_response)

    log_calls: list[tuple[str, dict[str, object]]] = []

    class CapturingLogger:
        def info(self, event: str, **kwargs: object) -> None:
            log_calls.append((event, kwargs))

    with (
        patch.object(client, "_client") as mock_client,
        patch("llm.anthropic_client.logger", CapturingLogger()),
    ):
        mock_client.messages = mock_messages
        await client.complete(
            system="System prompt",
            messages=[{"role": "user", "content": "Hallo"}],
        )

    # Two log calls must have been made: one for request, one for response
    assert len(log_calls) == 2
    request_events = [ev for ev, _ in log_calls if "request" in ev]
    response_events = [ev for ev, _ in log_calls if "response" in ev]
    assert len(request_events) == 1, "Expected one request log event"
    assert len(response_events) == 1, "Expected one response log event"

    # Request log must include model and message_count
    _, req_kwargs = next((ev, kw) for ev, kw in log_calls if "request" in ev)
    assert req_kwargs.get("model") == "claude-log-test"

    # Response log must include has_tool_use=True
    _, resp_kwargs = next((ev, kw) for ev, kw in log_calls if "response" in ev)
    assert resp_kwargs.get("has_tool_use") is True


def test_factory_raises_for_unknown_provider() -> None:
    from llm.factory import create_llm_client

    # pydantic-settings validates the Literal["anthropic", "ollama"] field,
    # so we construct Settings and override after creation
    settings = Settings(llm_provider="anthropic", llm_api_key="", llm_model="test")
    # Bypass pydantic validation to set an invalid provider for testing
    object.__setattr__(settings, "llm_provider", "unknown")
    with pytest.raises(ValueError, match="Unbekannter LLM-Provider"):
        create_llm_client(settings)
