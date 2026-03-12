"""WorkingMemory — operativer Laufzeit-Zustand eines Projekts.

Wird nach jedem Orchestrator-Zyklus aktualisiert und in SQLite persistiert.
Enthält keine Artefakte — nur Steuerungsfelder und abgeleitete Metriken.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from artifacts.models import CompletenessStatus, Phasenstatus, Projektphase


class WorkingMemory(BaseModel):
    """Operativer Zustandsspeicher des Orchestrators für ein Projekt."""

    projekt_id: str
    aktive_phase: Projektphase
    aktiver_modus: str  # z.B. "exploration", "structuring", "moderator"
    phasenstatus: Phasenstatus
    befuellte_slots: int = 0
    bekannte_slots: int = 0
    completeness_state: dict[str, CompletenessStatus] = Field(default_factory=dict)
    flags: list[str] = Field(default_factory=list)  # aktive Steuerungsflags (SDD 6.4.1)
    letzte_aenderung: datetime
