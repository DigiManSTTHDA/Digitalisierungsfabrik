"""Tests for WebSocket event models (Story 04-07).

Coverage: one round-trip serialisation test per event model (6 total).
"""

from __future__ import annotations

import pytest

from artifacts.models import Phasenstatus
from core.events import (
    ArtifactUpdateEvent,
    ChatDoneEvent,
    ChatTokenEvent,
    DebugUpdateEvent,
    ErrorEvent,
    ProgressUpdateEvent,
    WebSocketEvent,
)


def test_chat_token_event_round_trip() -> None:
    event = ChatTokenEvent(token="Hallo")
    data = event.model_dump_json()
    restored = ChatTokenEvent.model_validate_json(data)
    assert restored.event == "chat_token"
    assert restored.token == "Hallo"


def test_chat_done_event_round_trip() -> None:
    event = ChatDoneEvent(message="Antwort komplett")
    data = event.model_dump_json()
    restored = ChatDoneEvent.model_validate_json(data)
    assert restored.event == "chat_done"
    assert restored.message == "Antwort komplett"


def test_artifact_update_event_round_trip() -> None:
    event = ArtifactUpdateEvent(typ="exploration", artefakt={"slots": {}})
    data = event.model_dump_json()
    restored = ArtifactUpdateEvent.model_validate_json(data)
    assert restored.event == "artifact_update"
    assert restored.typ == "exploration"
    assert restored.artefakt == {"slots": {}}


def test_progress_update_event_round_trip() -> None:
    event = ProgressUpdateEvent(
        phasenstatus=Phasenstatus.in_progress,
        befuellte_slots=3,
        bekannte_slots=8,
    )
    data = event.model_dump_json()
    restored = ProgressUpdateEvent.model_validate_json(data)
    assert restored.event == "progress_update"
    assert restored.phasenstatus == Phasenstatus.in_progress
    assert restored.befuellte_slots == 3
    assert restored.bekannte_slots == 8


def test_debug_update_event_round_trip() -> None:
    event = DebugUpdateEvent(
        working_memory={"aktive_phase": "exploration"},
        flags=["phase_complete"],
    )
    data = event.model_dump_json()
    restored = DebugUpdateEvent.model_validate_json(data)
    assert restored.event == "debug_update"
    assert restored.working_memory == {"aktive_phase": "exploration"}
    assert restored.flags == ["phase_complete"]


def test_error_event_round_trip() -> None:
    event = ErrorEvent(message="LLM Timeout", recoverable=True)
    data = event.model_dump_json()
    restored = ErrorEvent.model_validate_json(data)
    assert restored.event == "error"
    assert restored.message == "LLM Timeout"
    assert restored.recoverable is True


# ---------------------------------------------------------------------------
# WebSocketEvent discriminated union rejects unknown event type
# ---------------------------------------------------------------------------


def test_websocket_event_union_rejects_unknown_type() -> None:
    """WebSocketEvent union must raise ValidationError for an unknown event discriminator."""
    from pydantic import TypeAdapter, ValidationError

    ta: TypeAdapter[WebSocketEvent] = TypeAdapter(WebSocketEvent)
    with pytest.raises(ValidationError):
        ta.validate_python({"event": "totally_unknown_type", "token": "x"})
