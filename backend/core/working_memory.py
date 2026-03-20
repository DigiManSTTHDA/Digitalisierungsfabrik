"""WorkingMemory — operativer Laufzeit-Zustand eines Projekts (SDD 6.4).

Wird nach jedem Orchestrator-Zyklus aktualisiert und in SQLite persistiert.
Enthält keine Artefakte — nur Steuerungsfelder und abgeleitete Metriken.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from artifacts.models import (
    CompletenessStatus,
    Phasenstatus,
    Projektphase,
    Projektstatus,
    Validierungsbericht,
)


class WorkingMemory(BaseModel):
    """Operativer Zustandsspeicher des Orchestrators für ein Projekt (SDD 6.4)."""

    projekt_id: str
    aktive_phase: Projektphase
    aktiver_modus: str  # z.B. "exploration", "structuring", "moderator"
    vorheriger_modus: str | None = None  # Für Rückgabe nach Moderator-Unterbrechung
    phasenstatus: Phasenstatus
    befuellte_slots: int = 0
    bekannte_slots: int = 0
    explorationsartefakt_ref: str | None = None  # Referenz auf aktuelle Artefakt-Version
    strukturartefakt_ref: str | None = None
    algorithmusartefakt_ref: str | None = None
    completeness_state: dict[str, CompletenessStatus] = Field(default_factory=dict)
    spannungsfelder: list[str] = Field(default_factory=list)  # Dokumentierte Spannungsfelder
    aktiver_abschnitt: str | None = None  # Aktuell bearbeiteter Algorithmusabschnitt (z.B. "ab2")
    letzter_dialogturn: int = 0  # Index des letzten verarbeiteten Dialogturns
    projektstatus: Projektstatus = Projektstatus.aktiv
    flags: list[str] = Field(default_factory=list)  # Aktive Steuerungsflags (SDD 6.4.1)
    validierungsbericht: Validierungsbericht | None = None  # ADR-007: structured report
    cumulative_prompt_tokens: int = 0  # Kumulative Prompt-Tokens seit Projektbeginn
    cumulative_completion_tokens: int = 0  # Kumulative Completion-Tokens seit Projektbeginn
    cumulative_total_tokens: int = 0  # Kumulative Gesamttokens seit Projektbeginn
    letzte_aenderung: datetime
