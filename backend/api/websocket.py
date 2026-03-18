"""WebSocket-Handler — bidirectional channel for turn processing (HLA 3.2).

Receives turn/panic messages from the frontend, routes them through the
Orchestrator, and streams back event responses using the event models
defined in core/events.py (Epic 04, ADR-003).
"""

from __future__ import annotations

import asyncio
import json

import structlog
from fastapi import WebSocket, WebSocketDisconnect

from config import Settings, get_settings
from core.events import (
    ArtifactUpdateEvent,
    ChatDoneEvent,
    DebugUpdateEvent,
    ErrorEvent,
    ProgressUpdateEvent,
)
from core.orchestrator import Orchestrator, TurnInput, TurnOutput
from modes.exploration import ExplorationMode
from modes.specification import SpecificationMode
from modes.structuring import StructuringMode
from modes.validation import ValidationMode
from persistence.database import Database
from persistence.project_repository import ProjectRepository

logger = structlog.get_logger()

# Guard against React 18 StrictMode double-mount triggering duplicate greetings.
# Tracks project IDs with an in-flight greeting to prevent concurrent LLM calls.
_greeting_in_progress: set[str] = set()


def _build_orchestrator(repo: ProjectRepository, settings: Settings) -> Orchestrator:
    """Build an Orchestrator with real mode instances."""
    from llm.factory import create_llm_client
    from modes.base import BaseMode
    from modes.moderator import Moderator

    llm = create_llm_client(settings)
    modes: dict[str, BaseMode] = {
        "exploration": ExplorationMode(llm_client=llm),
        "structuring": StructuringMode(llm_client=llm),
        "specification": SpecificationMode(llm_client=llm),
        "validation": ValidationMode(llm_client=llm),
        "moderator": Moderator(llm_client=llm),
    }
    return Orchestrator(repository=repo, modes=modes, settings=settings)


async def _send_event(ws: WebSocket, event: object) -> None:
    """Send a Pydantic model as JSON over the WebSocket."""
    if hasattr(event, "model_dump"):
        await ws.send_json(event.model_dump(mode="json"))
    else:
        await ws.send_json(event)


async def _send_turn_events(
    ws: WebSocket,
    output: TurnOutput,
    repo: ProjectRepository,
    project_id: str,
) -> None:
    """Send all post-turn events to the client."""
    if output.error:
        await _send_event(ws, ErrorEvent(message=output.error, recoverable=True))
        return

    await _send_event(ws, ChatDoneEvent(message=output.nutzeraeusserung))

    # Reload project for current artifact state
    project = repo.load(project_id)
    for typ, artifact in [
        ("exploration", project.exploration_artifact),
        ("struktur", project.structure_artifact),
        ("algorithmus", project.algorithm_artifact),
    ]:
        await _send_event(ws, ArtifactUpdateEvent(typ=typ, artefakt=artifact.model_dump()))

    wm = output.working_memory
    await _send_event(
        ws,
        ProgressUpdateEvent(
            phasenstatus=output.phasenstatus,
            befuellte_slots=wm.befuellte_slots,
            bekannte_slots=wm.bekannte_slots,
        ),
    )
    await _send_event(
        ws,
        DebugUpdateEvent(
            working_memory=wm.model_dump(mode="json"),
            flags=output.flags,
        ),
    )


async def _replay_last_assistant_message(
    ws: WebSocket,
    repo: ProjectRepository,
    project_id: str,
) -> None:
    """Replay the most recent assistant message from dialog history."""
    history = repo.load_dialog_history(project_id, last_n=1)
    if history and history[0].get("role") == "assistant":
        msg = history[0].get("inhalt", "")
        if msg:
            await _send_event(ws, ChatDoneEvent(message=msg))


async def _handle_greeting(
    ws: WebSocket,
    orchestrator: Orchestrator,
    repo: ProjectRepository,
    project_id: str,
    log: structlog.stdlib.BoundLogger,
) -> None:
    """Handle moderator greeting for fresh projects (FR-D-11).

    Guards against React 18 StrictMode double-mount:
    - First connection runs the greeting via LLM and sends events.
    - Second connection (if first is still in-flight) waits for completion
      then replays from dialog history.
    """
    if project_id not in _greeting_in_progress:
        # First connection — run the greeting turn
        _greeting_in_progress.add(project_id)
        try:
            output = await orchestrator.process_turn(project_id, TurnInput(text="[Systemstart]"))
            await _send_turn_events(ws, output, repo, project_id)
        except Exception:
            log.exception("websocket.greeting_error")
        finally:
            _greeting_in_progress.discard(project_id)
    else:
        # Another connection is already handling the greeting (StrictMode).
        # Wait for it to complete, then replay from dialog history.
        for _ in range(50):  # up to 10 seconds
            await asyncio.sleep(0.2)
            if project_id not in _greeting_in_progress:
                break
        await _replay_last_assistant_message(ws, repo, project_id)


async def websocket_session(ws: WebSocket, project_id: str) -> None:
    """Handle a WebSocket session for a project (HLA 3.2)."""
    await ws.accept()
    settings = get_settings()
    db = Database(settings.database_path)
    repo = ProjectRepository(db)
    log = logger.bind(project_id=project_id)

    # Validate project exists before allocating resources
    try:
        project = repo.load(project_id)
    except ValueError:
        await _send_event(
            ws,
            ErrorEvent(message=f"Projekt '{project_id}' nicht gefunden", recoverable=False),
        )
        db.close()
        await ws.close()
        return

    orchestrator = _build_orchestrator(repo, settings)

    # FR-D-11: Handle greeting for fresh projects.
    # If the project is in moderator mode and has no dialog history yet,
    # run the greeting turn. The moderator STAYS in moderator mode (no auto-handoff).
    greeting_needed = (
        project.working_memory.aktiver_modus == "moderator"
        and project.working_memory.letzter_dialogturn == 0
    )

    if greeting_needed:
        await _handle_greeting(ws, orchestrator, repo, project_id, log)
    elif project.working_memory.letzter_dialogturn > 0:
        # Existing project or project with history: replay last assistant message
        await _replay_last_assistant_message(ws, repo, project_id)

    try:
        while True:
            raw = await ws.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await _send_event(ws, ErrorEvent(message="Ungültiges JSON", recoverable=True))
                continue

            msg_type = data.get("type")

            if msg_type == "turn":
                text = data.get("text")
                if not isinstance(text, str) or not text.strip():
                    await _send_event(
                        ws,
                        ErrorEvent(message="Feld 'text' fehlt oder ist leer", recoverable=True),
                    )
                    continue
                datei = data.get("datei")
                turn_input = TurnInput(text=text, datei=datei)
                try:
                    output = await orchestrator.process_turn(project_id, turn_input)
                except ValueError as exc:
                    log.warning("websocket.project_error", error=str(exc))
                    await _send_event(
                        ws,
                        ErrorEvent(message=str(exc), recoverable=False),
                    )
                    continue
                except Exception:
                    log.exception("websocket.process_turn_error")
                    await _send_event(
                        ws,
                        ErrorEvent(
                            message="Interner Fehler bei der Turn-Verarbeitung",
                            recoverable=True,
                        ),
                    )
                    continue
                try:
                    await _send_turn_events(ws, output, repo, project_id)
                except Exception:
                    log.exception("websocket.send_events_error")
                    await _send_event(
                        ws,
                        ErrorEvent(
                            message="Turn verarbeitet, aber Ereignisse konnten nicht gesendet werden",
                            recoverable=True,
                        ),
                    )

            elif msg_type == "panic":
                # FR-D-03: Panic button activates Moderator
                try:
                    project = repo.load(project_id)
                    project.working_memory.vorheriger_modus = project.working_memory.aktiver_modus
                    project.working_memory.aktiver_modus = "moderator"
                    project.aktiver_modus = "moderator"
                    repo.save(project)
                    turn_input = TurnInput(text="[Panik-Button aktiviert]")
                    output = await orchestrator.process_turn(project_id, turn_input)
                    await _send_turn_events(ws, output, repo, project_id)
                except Exception:
                    log.exception("websocket.panic_error")
                    await _send_event(
                        ws,
                        ErrorEvent(
                            message="Fehler bei Panik-Verarbeitung",
                            recoverable=True,
                        ),
                    )

            else:
                await _send_event(
                    ws,
                    ErrorEvent(
                        message=f"Unbekannter Nachrichtentyp: {msg_type}",
                        recoverable=True,
                    ),
                )

    except WebSocketDisconnect:
        log.info("websocket.disconnected")
    finally:
        db.close()
