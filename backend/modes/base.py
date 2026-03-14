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


class BaseMode:
    """Abstrakte Basisklasse für alle kognitiven Modi (HLA Section 3.5).

    Alle konkreten Modi erben von dieser Klasse und implementieren call().
    Kein Modus schreibt direkt in Artefakte oder Working Memory.
    """

    async def call(self, context: ModeContext) -> ModeOutput:
        """Modus mit dem gegebenen Kontext aufrufen und ModeOutput zurückgeben."""
        raise NotImplementedError(f"{type(self).__name__}.call() ist nicht implementiert")
