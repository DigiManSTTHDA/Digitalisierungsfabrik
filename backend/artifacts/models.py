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


class EmmaAktionstyp(StrEnum):
    """EMMA-Aktionskatalog — alle 18 Aktionstypen aus SDD 8.3.

    Refs: ADR-006 (OP-02 resolution).
    """

    FIND = "FIND"
    FIND_AND_CLICK = "FIND_AND_CLICK"
    CLICK = "CLICK"
    DRAG = "DRAG"
    SCROLL = "SCROLL"
    TYPE = "TYPE"
    READ = "READ"
    READ_FORM = "READ_FORM"
    GENAI = "GENAI"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"
    FILE_OPERATION = "FILE_OPERATION"
    SEND_MAIL = "SEND_MAIL"
    COMMAND = "COMMAND"
    LOOP = "LOOP"
    DECISION = "DECISION"
    WAIT = "WAIT"
    SUCCESS = "SUCCESS"


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
    """Strukturartefakt — Kontrollfluss-Graph als dict-keyed Schritt-Map.

    SDD 5.4: Das Artefakt besteht aus zwei Teilen:
    1. Prozesszusammenfassung — Freitext, für Fachanwender lesbar
    2. Prozessstruktur — geordnete Liste von Strukturschritten
    """

    prozesszusammenfassung: str = ""  # SDD 5.4, FR-B-01 AK(3): Pflichtslot
    schritte: dict[str, Strukturschritt] = Field(default_factory=dict)
    version: int = 0


# ---------------------------------------------------------------------------
# Algorithm Artifact
# ---------------------------------------------------------------------------


class EmmaAktion(BaseModel):
    """Eine atomare EMMA-Aktion innerhalb eines Algorithmusabschnitts (SDD 5.5).

    Refs: ADR-006 (OP-02 resolution):
    - aktionstyp: EmmaAktionstyp enum (18 SDD 8.3 values)
    - parameter: dict[str, str] for prototype (full typing pending EMMA spec)
    - nachfolger: list[str] (deviates from SDD String — supports DECISION branching)
    """

    aktion_id: str
    aktionstyp: EmmaAktionstyp  # Wert aus EMMA-Aktionskatalog (SDD 8.3, ADR-006)
    parameter: dict[str, str] = Field(default_factory=dict)
    nachfolger: list[str] = Field(default_factory=list)  # ADR-006: list for branching
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
    """Algorithmusartefakt — detaillierte EMMA-Aktionen je Strukturschritt.

    SDD 5.5: Das Artefakt besteht aus zwei Teilen:
    1. Prozesszusammenfassung — Freitext, technisch angereichert, LLM-generiert
    2. Algorithmusabschnitte — geordnete Map von Abschnitten
    """

    prozesszusammenfassung: str = ""  # SDD 5.5, FR-B-02 AK(2): Pflichtslot
    abschnitte: dict[str, Algorithmusabschnitt] = Field(default_factory=dict)
    version: int = 0
