"""WebSocket endpoint tests — FastAPI TestClient with mocked LLM.

All tests use in-memory SQLite and mock the LLM client to avoid
real API calls. The Orchestrator runs the real 11-step cycle.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from artifacts.models import Phasenstatus
from core.orchestrator import TurnOutput
from core.working_memory import WorkingMemory
from main import create_app
from persistence.database import Database
from persistence.project_repository import ProjectRepository


def _make_test_app():  # type: ignore[no-untyped-def]
    """Create a fresh app + in-memory DB for WebSocket tests."""
    app = create_app()
    db = Database(":memory:")
    repo = ProjectRepository(db)
    return app, db, repo


def _make_mock_output(project_id: str) -> TurnOutput:
    """Create a minimal TurnOutput for mocked orchestrator."""
    wm = WorkingMemory(
        projekt_id=project_id,
        aktive_phase="exploration",  # type: ignore[arg-type]
        aktiver_modus="exploration",
        phasenstatus=Phasenstatus.in_progress,
        letzte_aenderung=datetime.now(tz=UTC),
    )
    return TurnOutput(
        nutzeraeusserung="Testantwort vom LLM",
        phasenstatus=Phasenstatus.in_progress,
        flags=[],
        working_memory=wm,
    )


@pytest.fixture()
def ws_setup():  # type: ignore[no-untyped-def]
    """Provide app, db, repo, project_id for WebSocket tests."""
    app, db, repo = _make_test_app()  # type: ignore[no-untyped-call]
    project = repo.create(name="WS-Test")
    yield app, db, repo, project.projekt_id
    db.close()


def test_websocket_turn_success(ws_setup) -> None:  # type: ignore[no-untyped-def]
    """Send a turn message, receive chat_done + artifact_update + progress + debug events."""
    app, db, repo, pid = ws_setup
    mock_output = _make_mock_output(pid)

    with patch("api.websocket._build_orchestrator") as mock_build:
        mock_orch = AsyncMock()
        mock_orch.process_turn.return_value = mock_output
        mock_build.return_value = mock_orch

        with patch("api.websocket.Database", return_value=db):
            with patch("api.websocket.ProjectRepository", return_value=repo):
                client = TestClient(app)
                with client.websocket_connect(f"/ws/session/{pid}") as ws:
                    ws.send_text(json.dumps({"type": "turn", "text": "Hallo"}))
                    events = []
                    # Expect: chat_done, 3x artifact_update, progress_update, debug_update = 6 events
                    for _ in range(6):
                        events.append(ws.receive_json())
    event_types = [e["event"] for e in events]
    assert "chat_done" in event_types
    assert event_types.count("artifact_update") == 3
    assert "progress_update" in event_types
    assert "debug_update" in event_types
    chat_done = next(e for e in events if e["event"] == "chat_done")
    assert chat_done["message"] == "Testantwort vom LLM"


def test_websocket_turn_error(ws_setup) -> None:  # type: ignore[no-untyped-def]
    """Orchestrator exception sends an error event."""
    app, db, repo, pid = ws_setup

    with patch("api.websocket._build_orchestrator") as mock_build:
        mock_orch = AsyncMock()
        mock_orch.process_turn.side_effect = RuntimeError("LLM kaputt")
        mock_build.return_value = mock_orch

        with patch("api.websocket.Database", return_value=db):
            with patch("api.websocket.ProjectRepository", return_value=repo):
                client = TestClient(app)
                with client.websocket_connect(f"/ws/session/{pid}") as ws:
                    ws.send_text(json.dumps({"type": "turn", "text": "Boom"}))
                    event = ws.receive_json()
    assert event["event"] == "error"
    assert event["recoverable"] is True
    # Error message must be non-empty and contain actionable info (Rule T-6)
    assert isinstance(event["message"], str)
    assert len(event["message"]) >= 5, "Error message must be descriptive, not just a word"
    assert "Fehler" in event["message"] or "Interner" in event["message"]


def test_websocket_panic_triggers_moderator(ws_setup) -> None:  # type: ignore[no-untyped-def]
    """Panic message activates Moderator and returns chat_done event."""
    app, db, repo, pid = ws_setup
    mock_output = _make_mock_output(pid)
    mock_output.nutzeraeusserung = "Moderator: Ich analysiere die Situation."

    with patch("api.websocket._build_orchestrator") as mock_build:
        mock_orch = AsyncMock()
        mock_orch.process_turn.return_value = mock_output
        mock_build.return_value = mock_orch

        with patch("api.websocket.Database", return_value=db):
            with patch("api.websocket.ProjectRepository", return_value=repo):
                client = TestClient(app)
                with client.websocket_connect(f"/ws/session/{pid}") as ws:
                    ws.send_text(json.dumps({"type": "panic"}))
                    events = [ws.receive_json() for _ in range(6)]
    event_types = [e["event"] for e in events]
    assert "chat_done" in event_types
    chat = next(e for e in events if e["event"] == "chat_done")
    assert "Moderator" in chat["message"]


def test_websocket_invalid_message(ws_setup) -> None:  # type: ignore[no-untyped-def]
    """Invalid JSON sends an error event."""
    app, db, repo, pid = ws_setup

    with patch("api.websocket.Database", return_value=db):
        with patch("api.websocket.ProjectRepository", return_value=repo):
            with patch("api.websocket._build_orchestrator"):
                client = TestClient(app)
                with client.websocket_connect(f"/ws/session/{pid}") as ws:
                    ws.send_text("not valid json {{{")
                    event = ws.receive_json()
    assert event["event"] == "error"
    assert "JSON" in event["message"]


def test_websocket_project_not_found(ws_setup) -> None:  # type: ignore[no-untyped-def]
    """WebSocket for non-existent project sends error and closes connection."""
    app, db, repo, _pid = ws_setup

    with patch("api.websocket.Database", return_value=db):
        with patch("api.websocket.ProjectRepository", return_value=repo):
            with patch("api.websocket._build_orchestrator"):
                client = TestClient(app)
                with client.websocket_connect("/ws/session/nonexistent") as ws:
                    # Server validates project on connect and sends error before closing
                    event = ws.receive_json()
    assert event["event"] == "error"
    assert "nicht gefunden" in event["message"]
    assert event["recoverable"] is False


def test_websocket_multiple_turns(ws_setup) -> None:  # type: ignore[no-untyped-def]
    """Two consecutive turns both succeed."""
    app, db, repo, pid = ws_setup
    mock_output = _make_mock_output(pid)

    with patch("api.websocket._build_orchestrator") as mock_build:
        mock_orch = AsyncMock()
        mock_orch.process_turn.return_value = mock_output
        mock_build.return_value = mock_orch

        with patch("api.websocket.Database", return_value=db):
            with patch("api.websocket.ProjectRepository", return_value=repo):
                client = TestClient(app)
                with client.websocket_connect(f"/ws/session/{pid}") as ws:
                    # Turn 1
                    ws.send_text(json.dumps({"type": "turn", "text": "Turn 1"}))
                    events_1 = [ws.receive_json() for _ in range(6)]
                    # Turn 2
                    ws.send_text(json.dumps({"type": "turn", "text": "Turn 2"}))
                    events_2 = [ws.receive_json() for _ in range(6)]
    assert any(e["event"] == "chat_done" for e in events_1)
    assert any(e["event"] == "chat_done" for e in events_2)
    assert mock_orch.process_turn.call_count == 2


def test_websocket_unknown_message_type(ws_setup) -> None:  # type: ignore[no-untyped-def]
    """Valid JSON with unknown 'type' sends error event with descriptive message."""
    app, db, repo, pid = ws_setup

    with patch("api.websocket.Database", return_value=db):
        with patch("api.websocket.ProjectRepository", return_value=repo):
            with patch("api.websocket._build_orchestrator"):
                client = TestClient(app)
                with client.websocket_connect(f"/ws/session/{pid}") as ws:
                    ws.send_text(json.dumps({"type": "unknown_type"}))
                    event = ws.receive_json()
    assert event["event"] == "error"
    assert "unknown_type" in event["message"]
    assert event["recoverable"] is True


def test_websocket_turn_empty_text(ws_setup) -> None:  # type: ignore[no-untyped-def]
    """Turn message with empty text returns error event."""
    app, db, repo, pid = ws_setup

    with patch("api.websocket.Database", return_value=db):
        with patch("api.websocket.ProjectRepository", return_value=repo):
            with patch("api.websocket._build_orchestrator"):
                client = TestClient(app)
                with client.websocket_connect(f"/ws/session/{pid}") as ws:
                    ws.send_text(json.dumps({"type": "turn", "text": ""}))
                    event = ws.receive_json()
    assert event["event"] == "error"
    assert "text" in event["message"].lower()


def test_websocket_turn_missing_text(ws_setup) -> None:  # type: ignore[no-untyped-def]
    """Turn message without text field returns error event."""
    app, db, repo, pid = ws_setup

    with patch("api.websocket.Database", return_value=db):
        with patch("api.websocket.ProjectRepository", return_value=repo):
            with patch("api.websocket._build_orchestrator"):
                client = TestClient(app)
                with client.websocket_connect(f"/ws/session/{pid}") as ws:
                    ws.send_text(json.dumps({"type": "turn"}))
                    event = ws.receive_json()
    assert event["event"] == "error"
    assert "text" in event["message"].lower()


def test_websocket_turn_output_error_field(ws_setup) -> None:  # type: ignore[no-untyped-def]
    """When TurnOutput.error is set, an ErrorEvent is sent instead of normal events."""
    app, db, repo, pid = ws_setup
    wm = WorkingMemory(
        projekt_id=pid,
        aktive_phase="exploration",  # type: ignore[arg-type]
        aktiver_modus="exploration",
        phasenstatus=Phasenstatus.in_progress,
        letzte_aenderung=datetime.now(tz=UTC),
    )
    error_output = TurnOutput(
        nutzeraeusserung="",
        phasenstatus=Phasenstatus.in_progress,
        flags=[],
        working_memory=wm,
        error="LLM Output-Kontrakt-Verletzung",
    )

    with patch("api.websocket._build_orchestrator") as mock_build:
        mock_orch = AsyncMock()
        mock_orch.process_turn.return_value = error_output
        mock_build.return_value = mock_orch

        with patch("api.websocket.Database", return_value=db):
            with patch("api.websocket.ProjectRepository", return_value=repo):
                client = TestClient(app)
                with client.websocket_connect(f"/ws/session/{pid}") as ws:
                    ws.send_text(json.dumps({"type": "turn", "text": "Hallo"}))
                    event = ws.receive_json()
    assert event["event"] == "error"
    assert event["message"] == "LLM Output-Kontrakt-Verletzung"
    assert event["recoverable"] is True
