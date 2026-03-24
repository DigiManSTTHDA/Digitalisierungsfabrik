"""Mode interface — Flag enum, ModeContext, ModeOutput, BaseMode.

All cognitive modes extend BaseMode. The Orchestrator calls mode.call(context)
and processes the returned ModeOutput. No mode writes directly to artifacts or
Working Memory — all writes go through the Orchestrator / Executor.

SDD references: 6.4.1 (Flags), 6.5.2 (Output-Kontrakt), 6.5.3 (Kontext-Bestandteile),
HLA Section 3.5 (BaseMode interface).
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field

from artifacts.models import (
    AlgorithmArtifact,
    CompletenessStatus,
    ExplorationArtifact,
    Phasenstatus,
    Projektphase,
    StructureArtifact,
    Validierungsbericht,
)
from artifacts.template_schema import ArtifactTemplate
from core.working_memory import WorkingMemory


class Flag(StrEnum):
    """Zyklus-lokale Steuerungsflags des kognitiven Modus (SDD 6.4.1).

    Flags werden vom Modus als Teil seines Outputs zurückgegeben,
    vom Orchestrator im selben Zyklus ausgewertet und danach verworfen.
    Sie werden NICHT ins Working Memory geschrieben und NICHT persistiert (SDD 6.4.1).
    """

    phase_complete = "phase_complete"
    needs_clarification = "needs_clarification"
    escalate = "escalate"
    blocked = "blocked"
    artefakt_updated = "artefakt_updated"
    validation_failed = "validation_failed"
    advance_phase = "advance_phase"
    return_to_mode = "return_to_mode"


class ModeContext(BaseModel):
    """Kontext für den Modus-Aufruf durch den Orchestrator (SDD 6.5.3)."""

    projekt_id: str
    aktive_phase: Projektphase
    aktiver_modus: str
    exploration_artifact: ExplorationArtifact
    structure_artifact: StructureArtifact
    algorithm_artifact: AlgorithmArtifact
    working_memory: WorkingMemory
    dialog_history: list[dict]  # type: ignore[type-arg]  # [{role, inhalt, timestamp}]
    completeness_state: dict[str, CompletenessStatus] = Field(default_factory=dict)
    artifact_template: ArtifactTemplate | None = None
    error_hint: str | None = None  # Retry-Hint bei ungültigen Patches (S1-T1)
    validator_feedback: str | None = None  # CR-009: Validator-Befunde für Korrektur-Call

    def with_error_hint(self, hint: str) -> "ModeContext":
        """Kopie des Kontexts mit gesetztem error_hint zurückgeben (S1-T1)."""
        return self.model_copy(update={"error_hint": hint})

    def with_validator_feedback(self, feedback: str) -> "ModeContext":
        """Kopie des Kontexts mit Validator-Feedback zurückgeben (CR-009)."""
        return self.model_copy(update={"validator_feedback": feedback})


class ModeOutput(BaseModel):
    """Output jedes kognitiven Modus (SDD 6.5.2, 6.6).

    Enthält ausschließlich die drei SDD-definierten Bestandteile:
    - nutzeraeusserung: Freitext für den Chatbereich
    - patches: RFC 6902 Schreiboperationen (kann leer sein)
    - phasenstatus + flags: Steuerungsoutput
    """

    nutzeraeusserung: str
    patches: list[dict] = Field(default_factory=list)  # type: ignore[type-arg]
    phasenstatus: Phasenstatus
    flags: list[Flag] = Field(default_factory=list)
    validierungsbericht: Validierungsbericht | None = None
    summarizer_active: bool = False  # CR-010: True wenn nutzeraeusserung durch Summarizer ersetzt
    debug_request: dict | None = Field(default=None, exclude=True)  # type: ignore[type-arg]
    usage: dict | None = Field(default=None, exclude=True)  # type: ignore[type-arg]  # Token usage


def translate_dialog_history(dialog_history: list[dict]) -> list[dict]:  # type: ignore[type-arg]
    """Translate internal dialog history to LLM messages format.

    Converts [{role, inhalt, ...}] entries to [{role, content}] for LLM APIs.
    """
    messages: list[dict] = []  # type: ignore[type-arg]
    for entry in dialog_history:
        role = entry.get("role", "user")
        inhalt = entry.get("inhalt", "")
        if role in ("user", "assistant") and inhalt:
            messages.append({"role": role, "content": inhalt})
    return messages


class BaseMode:
    """Abstrakte Basisklasse für alle kognitiven Modi (HLA Section 3.5).

    Alle konkreten Modi erben von dieser Klasse und implementieren call().
    Kein Modus schreibt direkt in Artefakte oder Working Memory.
    """

    async def call(self, context: ModeContext) -> ModeOutput:
        """Modus mit dem gegebenen Kontext aufrufen und ModeOutput zurückgeben."""
        raise NotImplementedError(f"{type(self).__name__}.call() ist nicht implementiert")
