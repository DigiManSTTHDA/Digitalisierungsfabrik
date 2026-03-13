"""WebSocket event models — Pydantic models for all streaming events (ADR-003).

These models define the typed event payloads the Orchestrator emits via WebSocket.
Used by Epic 05 (FastAPI WebSocket endpoint) without rework.

SDD references: FR-F-01 (Fortschrittsanzeige), FR-F-02 (Debug-Modus),
FR-E-04 (Fehlerbehandlung), HLA Section 3.1 (WebSocket-Events).
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from artifacts.models import Phasenstatus


class ChatTokenEvent(BaseModel):
    """LLM streaming token event — sent during response generation."""

    event: Literal["chat_token"] = "chat_token"
    token: str


class ChatDoneEvent(BaseModel):
    """Turn completed event — sent when the full response is available."""

    event: Literal["chat_done"] = "chat_done"
    message: str


class ArtifactUpdateEvent(BaseModel):
    """Artifact updated event — sent after each write operation."""

    event: Literal["artifact_update"] = "artifact_update"
    typ: str
    artefakt: dict  # type: ignore[type-arg]


class ProgressUpdateEvent(BaseModel):
    """Progress update event — sent after each write operation."""

    event: Literal["progress_update"] = "progress_update"
    phasenstatus: Phasenstatus
    befuellte_slots: int
    bekannte_slots: int


class DebugUpdateEvent(BaseModel):
    """Debug update event — sent after each orchestrator cycle."""

    event: Literal["debug_update"] = "debug_update"
    working_memory: dict  # type: ignore[type-arg]
    flags: list[str]


class ErrorEvent(BaseModel):
    """Error event — sent on LLM errors or contract violations."""

    event: Literal["error"] = "error"
    message: str
    recoverable: bool


# Discriminated union of all WebSocket event types
WebSocketEvent = (
    ChatTokenEvent
    | ChatDoneEvent
    | ArtifactUpdateEvent
    | ProgressUpdateEvent
    | DebugUpdateEvent
    | ErrorEvent
)
