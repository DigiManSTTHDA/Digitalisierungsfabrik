"""API request/response schemas — Pydantic models for all REST endpoints.

All request and response shapes are defined here so FastAPI auto-generates
a correct OpenAPI 3.x spec. Route handlers reference these models directly.

SDD references: 7.2.1 (Projektmetadaten-Felder), FR-G-01 (Projektanlage),
FR-G-02 (Projektliste), FR-B-06 (Artefaktsichtbarkeit), FR-B-07 (Download/Import),
FR-B-10 (Versionswiederherstellung), ADR-001 (OpenAPI contract).
"""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, Field

from artifacts.models import Projektphase, Projektstatus, Schweregrad

# ---------------------------------------------------------------------------
# Project management
# ---------------------------------------------------------------------------


class ProjectCreateRequest(BaseModel):
    """Request body for POST /api/projects (FR-G-01)."""

    name: str = Field(min_length=1, max_length=200, pattern=r"\S")
    beschreibung: str = ""


class ProjectResponse(BaseModel):
    """Project metadata — all SDD 7.2.1 fields."""

    projekt_id: str
    name: str
    beschreibung: str
    erstellt_am: datetime
    zuletzt_geaendert: datetime
    aktive_phase: Projektphase
    aktiver_modus: str
    projektstatus: Projektstatus


class ProjectListResponse(BaseModel):
    """Response for GET /api/projects (FR-G-02)."""

    projects: list[ProjectResponse]


class ProjectCompleteResponse(BaseModel):
    """Response for POST /api/projects/{id}/complete (FR-G-04)."""

    project: ProjectResponse


class ProjectDeleteBatchRequest(BaseModel):
    """Request body for DELETE /api/projects/batch."""

    projekt_ids: list[str] = Field(min_length=1)


class ProjectDeleteBatchResponse(BaseModel):
    """Response for DELETE /api/projects/batch."""

    deleted_count: int


# ---------------------------------------------------------------------------
# Artifacts
# ---------------------------------------------------------------------------


class ArtifactsResponse(BaseModel):
    """Response for GET /api/projects/{id}/artifacts (FR-B-06)."""

    exploration: dict  # type: ignore[type-arg]
    struktur: dict  # type: ignore[type-arg]
    algorithmus: dict  # type: ignore[type-arg]


class ArtifactVersionInfo(BaseModel):
    """Single version entry in the version history list."""

    version: int
    erstellt_am: str
    created_by: str


class ArtifactVersionsResponse(BaseModel):
    """Response for GET /api/projects/{id}/artifacts/{typ}/versions (FR-B-10)."""

    versions: list[ArtifactVersionInfo]


class ArtifactRestoreRequest(BaseModel):
    """Request body for POST /api/projects/{id}/artifacts/{typ}/restore."""

    version: int


class ArtifactRestoreResponse(BaseModel):
    """Response for POST restore and POST import."""

    artefakt: dict  # type: ignore[type-arg]


class ArtifactImportRequest(BaseModel):
    """Request body for POST /api/projects/{id}/import (FR-B-07, FR-C-04)."""

    typ: Literal["exploration", "struktur", "algorithmus"]
    artefakt: dict  # type: ignore[type-arg]


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------


class DownloadResponse(BaseModel):
    """Response for GET /api/projects/{id}/download (FR-B-07)."""

    exploration: dict  # type: ignore[type-arg]
    struktur: dict  # type: ignore[type-arg]
    algorithmus: dict  # type: ignore[type-arg]


# ---------------------------------------------------------------------------
# Export (Story 11-02, FR-B-07)
# ---------------------------------------------------------------------------


class ExportResponse(BaseModel):
    """Response for GET /api/projects/{id}/export — JSON artifacts + Markdown."""

    exploration: dict  # type: ignore[type-arg]
    struktur: dict  # type: ignore[type-arg]
    algorithmus: dict  # type: ignore[type-arg]
    markdown: str


# ---------------------------------------------------------------------------
# Error
# ---------------------------------------------------------------------------


class ErrorResponse(BaseModel):
    """Standard error response body."""

    detail: str


# ---------------------------------------------------------------------------
# Validation Report (SDD 6.6.4, FR-C-08, ADR-007)
# ---------------------------------------------------------------------------


class ValidationBefundResponse(BaseModel):
    """Single validation finding in the report."""

    befund_id: str
    schweregrad: Schweregrad
    beschreibung: str
    betroffene_slots: list[str]
    artefakttyp: str
    empfehlung: str


class ValidationReportResponse(BaseModel):
    """Full validation report (SDD 6.6.4)."""

    befunde: list[ValidationBefundResponse]
    erstellt_am: datetime
    durchlauf_nr: int
    ist_bestanden: bool


# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------


class AdvancePhaseResponse(BaseModel):
    """Response for POST /api/projects/{id}/debug/advance-phase."""

    project: ProjectResponse


# ---------------------------------------------------------------------------
# WebSocket incoming messages
# ---------------------------------------------------------------------------


class TurnMessage(BaseModel):
    """Incoming WebSocket message for a user turn (HLA 3.2)."""

    type: Literal["turn"] = "turn"
    text: str
    datei: str | None = None


class PanicMessage(BaseModel):
    """Incoming WebSocket message for the panic button (HLA 3.2)."""

    type: Literal["panic"] = "panic"


WebSocketIncoming = Annotated[
    TurnMessage | PanicMessage,
    Field(discriminator="type"),
]
