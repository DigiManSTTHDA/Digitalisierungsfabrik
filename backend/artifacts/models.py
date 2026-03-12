"""Pydantic v2 data models for all three artifacts and shared enums.

Design constraints (HLA Section 3.6, OP-01):
- All addressable collections use dict[str, SubModel] with stable string keys.
  Never lists with numeric indices — RFC 6902 patch paths must remain stable
  across insert/delete operations.
- All Enums are str-based for clean JSON serialisation.
- All top-level models pass model_json_schema() without errors (required by FastAPI).
"""

from __future__ import annotations

from enum import Enum


# ---------------------------------------------------------------------------
# Shared Enums
# ---------------------------------------------------------------------------


class CompletenessStatus(str, Enum):
    """Füllstand eines Slots oder Strukturschritts."""

    leer = "leer"
    teilweise = "teilweise"
    vollstaendig = "vollstaendig"


class AlgorithmusStatus(str, Enum):
    """Bearbeitungsstatus eines Algorithmusabschnitts oder Strukturschritts."""

    ausstehend = "ausstehend"
    in_bearbeitung = "in_bearbeitung"
    abgeschlossen = "abgeschlossen"
    invalidiert = "invalidiert"


class Phasenstatus(str, Enum):
    """Fortschritt innerhalb einer Phase (Signal des aktiven Modus)."""

    in_progress = "in_progress"
    nearing_completion = "nearing_completion"
    phase_complete = "phase_complete"


class Projektphase(str, Enum):
    """Aktive Phase des Projekts."""

    exploration = "exploration"
    strukturierung = "strukturierung"
    spezifikation = "spezifikation"
    validierung = "validierung"
    abgeschlossen = "abgeschlossen"


class Projektstatus(str, Enum):
    """Gesamtstatus des Projekts."""

    aktiv = "aktiv"
    abgeschlossen = "abgeschlossen"
    archiviert = "archiviert"


# ---------------------------------------------------------------------------
# Exploration Artifact
# ---------------------------------------------------------------------------


from pydantic import BaseModel, Field  # noqa: E402


class ExplorationSlot(BaseModel):
    """Ein einzelner Informationsslot im Explorationsartefakt."""

    slot_id: str
    bezeichnung: str
    inhalt: str = ""
    completeness_status: CompletenessStatus


class ExplorationArtifact(BaseModel):
    """Explorationsartefakt — sammelt freie Prozessinformationen in benannten Slots."""

    slots: dict[str, ExplorationSlot] = Field(default_factory=dict)
    version: int = 0


# ---------------------------------------------------------------------------
# Structure Artifact
# ---------------------------------------------------------------------------


class Strukturschritt(BaseModel):
    """Ein einzelner Schritt im Strukturartefakt (Kontrollfluss-Knoten)."""

    schritt_id: str
    titel: str
    typ: str  # z.B. "ACTIVITY", "DECISION", "EVENT"
    beschreibung: str = ""
    reihenfolge: int
    nachfolger: list[str] = Field(default_factory=list)
    completeness_status: CompletenessStatus
    algorithmus_status: AlgorithmusStatus
    spannungsfeld: str | None = None


class StructureArtifact(BaseModel):
    """Strukturartefakt — Kontrollfluss-Graph als dict-keyed Schritt-Map."""

    schritte: dict[str, Strukturschritt] = Field(default_factory=dict)
    version: int = 0


# ---------------------------------------------------------------------------
# Algorithm Artifact
# ---------------------------------------------------------------------------


class EmmaAktion(BaseModel):
    """Eine atomare EMMA-Aktion innerhalb eines Algorithmusabschnitts.

    Note (OP-02): parameter ist im Prototyp dict[str, str] — vollständige
    Typisierung folgt, wenn die EMMA-Spezifikation vorliegt.
    """

    aktion_id: str
    typ: str
    parameter: dict[str, str] = Field(default_factory=dict)
    nachfolger: list[str] = Field(default_factory=list)
    emma_ok: bool = False


class Algorithmusabschnitt(BaseModel):
    """Ein Abschnitt im Algorithmusartefakt, referenziert einen Strukturschritt."""

    abschnitt_id: str
    titel: str
    struktur_ref: str  # Referenz auf Strukturschritt.schritt_id
    aktionen: dict[str, EmmaAktion] = Field(default_factory=dict)
    completeness_status: CompletenessStatus
    status: AlgorithmusStatus


class AlgorithmArtifact(BaseModel):
    """Algorithmusartefakt — detaillierte EMMA-Aktionen je Strukturschritt."""

    abschnitte: dict[str, Algorithmusabschnitt] = Field(default_factory=dict)
    version: int = 0
