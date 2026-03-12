"""Pydantic v2 data models for all three artifacts and shared enums.

Design constraints (HLA Section 3.6, OP-01):
- All addressable collections use dict[str, SubModel] with stable string keys.
  Never lists with numeric indices — RFC 6902 patch paths must remain stable
  across insert/delete operations.
- All Enums are str-based for clean JSON serialisation.
- All top-level models pass model_json_schema() without errors (required by FastAPI).
"""

from __future__ import annotations

from enum import StrEnum

# ---------------------------------------------------------------------------
# Shared Enums
# ---------------------------------------------------------------------------


class CompletenessStatus(StrEnum):
    """Füllstand eines Slots oder Strukturschritts (SDD 5.6)."""

    leer = "leer"
    teilweise = "teilweise"
    vollstaendig = "vollstaendig"
    nutzervalidiert = "nutzervalidiert"  # Explizit durch Nutzer bestätigt (FR-C-07)


class AlgorithmusStatus(StrEnum):
    """Bearbeitungsstatus eines Algorithmusabschnitts oder Strukturschritts (SDD 5.4, 5.5)."""

    ausstehend = "ausstehend"
    aktuell = "aktuell"  # Abschnitt ist aktuell / up-to-date
    invalidiert = "invalidiert"  # Durch Strukturänderung ungültig geworden (FR-B-04)


class Phasenstatus(StrEnum):
    """Fortschritt innerhalb einer Phase (Signal des aktiven Modus)."""

    in_progress = "in_progress"
    nearing_completion = "nearing_completion"
    phase_complete = "phase_complete"


class Projektphase(StrEnum):
    """Aktive Phase des Projekts."""

    exploration = "exploration"
    strukturierung = "strukturierung"
    spezifikation = "spezifikation"
    validierung = "validierung"
    abgeschlossen = "abgeschlossen"


class Projektstatus(StrEnum):
    """Gesamtstatus des Projekts (SDD 8.4, 6.4)."""

    aktiv = "aktiv"
    pausiert = "pausiert"
    abgeschlossen = "abgeschlossen"


class Strukturschritttyp(StrEnum):
    """Typ eines Strukturschritts im Kontrollflussgraph (SDD 5.4)."""

    aktion = "aktion"
    entscheidung = "entscheidung"
    schleife = "schleife"
    ausnahme = "ausnahme"


# ---------------------------------------------------------------------------
# Exploration Artifact
# ---------------------------------------------------------------------------


from pydantic import BaseModel, Field  # noqa: E402


class ExplorationSlot(BaseModel):
    """Ein einzelner Informationsslot im Explorationsartefakt."""

    slot_id: str
    titel: str  # SDD 5.3: Thema des Slots
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
    """Ein einzelner Schritt im Strukturartefakt (Kontrollfluss-Knoten, SDD 5.4)."""

    schritt_id: str
    titel: str
    typ: Strukturschritttyp  # aktion / entscheidung / schleife / ausnahme
    beschreibung: str = ""
    reihenfolge: int
    nachfolger: list[str] = Field(default_factory=list)
    bedingung: str | None = None  # Nur bei typ=entscheidung (SDD 5.4)
    ausnahme_beschreibung: str | None = None  # Nur bei typ=ausnahme (SDD 5.4)
    algorithmus_ref: list[str] = Field(
        default_factory=list
    )  # → Algorithmusabschnitt.abschnitt_id (FR-B-03)
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
    """Eine atomare EMMA-Aktion innerhalb eines Algorithmusabschnitts (SDD 5.5).

    Note (OP-02): aktionstyp ist im Prototyp str — vollständige Enum-Typisierung
    folgt wenn der EMMA-Aktionskatalog finalisiert ist.
    Note (OP-02): parameter ist im Prototyp dict[str, str] — vollständige
    Typisierung folgt wenn die EMMA-Spezifikation vorliegt.
    """

    aktion_id: str
    aktionstyp: str  # Wert aus EMMA-Aktionskatalog (SDD 8.3)
    parameter: dict[str, str] = Field(default_factory=dict)
    nachfolger: list[str] = Field(default_factory=list)
    emma_kompatibel: bool = False  # Ergebnis der EMMA-Kompatibilitätsprüfung
    kompatibilitaets_hinweis: str | None = None  # Begründung bei emma_kompatibel=False


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
