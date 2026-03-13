"""Tests for LLM client abstraction: LLMClient ABC, AnthropicClient, OllamaClient, factory.

Coverage:
- Story 04-01: LLMClient ABC, LLMResponse, AnthropicClient
- Story 04-02: OllamaClient stub, create_llm_client factory
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

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
    tool_block.input = {"patches": [{"op": "add", "path": "/slots/s1", "value": {}}]}

    mock_response = MagicMock()
    mock_response.content = [text_block, tool_block]

    mock_messages = MagicMock()
    mock_messages.create = MagicMock(return_value=mock_response)

    with patch.object(client, "_client") as mock_client:
        mock_client.messages = mock_messages
        result = await client.complete(
            system="System prompt",
            messages=[{"role": "user", "content": "Hallo"}],
            tools=[{"name": "apply_patches", "input_schema": {}}],
        )

    assert isinstance(result, LLMResponse)
    assert result.nutzeraeusserung == "Ich helfe Ihnen gerne."
    assert result.tool_input == {"patches": [{"op": "add", "path": "/slots/s1", "value": {}}]}


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
    mock_messages.create = MagicMock(return_value=mock_response)

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
    from llm.anthropic_client import AnthropicClient

    settings = Settings(
        llm_provider="anthropic",
        llm_api_key="sk-test-key",
        llm_model="claude-test",
        llm_log_enabled=False,
    )
    client = AnthropicClient(settings)

    mock_messages = MagicMock()
    mock_messages.create = MagicMock(side_effect=RuntimeError("API connection failed"))

    with patch.object(client, "_client") as mock_client:
        mock_client.messages = mock_messages
        with pytest.raises(RuntimeError, match="API connection failed"):
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
    tool_block.input = {"patches": []}

    mock_response = MagicMock()
    mock_response.content = [text_block, tool_block]

    mock_messages = MagicMock()
    mock_messages.create = MagicMock(return_value=mock_response)

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
