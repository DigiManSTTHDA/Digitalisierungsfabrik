"""REST-Endpunkte — all REST API endpoints (HLA Section 6, api/router.py)."""

from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError

from api.schemas import (
    AdvancePhaseResponse,
    ArtifactImportRequest,
    ArtifactRestoreRequest,
    ArtifactRestoreResponse,
    ArtifactsResponse,
    ArtifactVersionInfo,
    ArtifactVersionsResponse,
    DownloadResponse,
    ErrorResponse,
    ProjectCompleteResponse,
    ProjectCreateRequest,
    ProjectDeleteBatchRequest,
    ProjectDeleteBatchResponse,
    ProjectListResponse,
    ProjectResponse,
    ValidationBefundResponse,
    ValidationReportResponse,
)
from artifacts.completeness import CompletenessCalculator
from artifacts.models import (
    AlgorithmArtifact,
    ExplorationArtifact,
    Projektstatus,
    StructureArtifact,
)
from core.models import Project
from persistence.database import Database
from persistence.project_repository import ProjectRepository

logger = structlog.get_logger()

router = APIRouter(prefix="/api", tags=["projects"])


def _get_repository() -> Generator[ProjectRepository, None, None]:
    """Provide a ProjectRepository backed by the configured database.

    Uses a generator so FastAPI calls close() after the request completes.
    Without this, every REST request would leak a SQLite connection.
    """
    from config import get_settings

    settings = get_settings()
    db = Database(settings.database_path)
    try:
        yield ProjectRepository(db)
    finally:
        db.close()


RepoDep = Annotated[ProjectRepository, Depends(_get_repository)]


def _project_to_response(p: Project) -> ProjectResponse:
    return ProjectResponse.model_validate(p, from_attributes=True)


def _load_or_404(repo: ProjectRepository, projekt_id: str) -> Project:
    try:
        return repo.load(projekt_id)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Projekt '{projekt_id}' nicht gefunden")


@router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    responses={422: {"model": ErrorResponse}},
)
async def create_project(
    body: ProjectCreateRequest,
    repo: RepoDep,
) -> ProjectResponse:
    """Neues Projekt anlegen (FR-G-01).

    Per SDD 6.1.0: Neue Projekte starten im Moderator-Modus.
    Die Begrüßung erfolgt über den WebSocket bei Verbindungsaufbau (FR-D-11),
    NICHT synchron hier — damit der Moderator im Modus bleibt und der
    Nutzer mit ihm interagieren kann, bevor die Exploration beginnt.
    """
    project = repo.create(name=body.name, beschreibung=body.beschreibung)
    logger.info("project_created", projekt_id=project.projekt_id)
    return _project_to_response(project)


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(repo: RepoDep) -> ProjectListResponse:
    """Alle Projekte auflisten (FR-G-02)."""
    projects = repo.list_projects()
    return ProjectListResponse(
        projects=[_project_to_response(p) for p in projects],
    )


@router.get(
    "/projects/{projekt_id}",
    response_model=ProjectResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_project(
    projekt_id: str,
    repo: RepoDep,
) -> ProjectResponse:
    """Projektdetails laden (FR-E-02)."""
    project = _load_or_404(repo, projekt_id)
    return _project_to_response(project)


@router.get(
    "/projects/{projekt_id}/artifacts",
    response_model=ArtifactsResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_artifacts(
    projekt_id: str,
    repo: RepoDep,
) -> ArtifactsResponse:
    """Alle drei Artefakte eines Projekts laden (FR-B-06)."""
    project = _load_or_404(repo, projekt_id)
    return ArtifactsResponse(
        exploration=project.exploration_artifact.model_dump(),
        struktur=project.structure_artifact.model_dump(),
        algorithmus=project.algorithm_artifact.model_dump(),
    )


@router.get(
    "/projects/{projekt_id}/download",
    response_model=DownloadResponse,
    responses={404: {"model": ErrorResponse}},
)
async def download_project(
    projekt_id: str,
    repo: RepoDep,
) -> DownloadResponse:
    """Alle drei Artefakte als JSON herunterladen (FR-B-07)."""
    project = _load_or_404(repo, projekt_id)
    return DownloadResponse(
        exploration=project.exploration_artifact.model_dump(),
        struktur=project.structure_artifact.model_dump(),
        algorithmus=project.algorithm_artifact.model_dump(),
    )


@router.delete(
    "/projects/batch",
    response_model=ProjectDeleteBatchResponse,
    responses={422: {"model": ErrorResponse}},
)
async def delete_projects_batch(
    body: ProjectDeleteBatchRequest,
    repo: RepoDep,
) -> ProjectDeleteBatchResponse:
    """Mehrere Projekte gleichzeitig löschen."""
    deleted = repo.delete_many(body.projekt_ids)
    logger.info("projects_batch_deleted", count=deleted, requested=len(body.projekt_ids))
    return ProjectDeleteBatchResponse(deleted_count=deleted)


@router.delete(
    "/projects/{projekt_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"model": ErrorResponse}},
)
async def delete_project(
    projekt_id: str,
    repo: RepoDep,
) -> None:
    """Einzelnes Projekt löschen (FR-E-06: isoliert)."""
    found = repo.delete(projekt_id)
    if not found:
        raise HTTPException(status_code=404, detail=f"Projekt '{projekt_id}' nicht gefunden")
    logger.info("project_deleted", projekt_id=projekt_id)


@router.post(
    "/projects/{projekt_id}/complete",
    response_model=ProjectCompleteResponse,
    responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
)
async def complete_project(
    projekt_id: str,
    repo: RepoDep,
) -> ProjectCompleteResponse:
    """Projekt als abgeschlossen markieren (FR-G-04)."""
    project = _load_or_404(repo, projekt_id)
    if project.projektstatus == Projektstatus.abgeschlossen:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Projekt ist bereits abgeschlossen",
        )
    project.projektstatus = Projektstatus.abgeschlossen
    repo.save(project)
    logger.info("project_completed", projekt_id=projekt_id)
    return ProjectCompleteResponse(project=_project_to_response(project))


_TYP_MAP: dict[
    str, tuple[str, type[ExplorationArtifact | StructureArtifact | AlgorithmArtifact]]
] = {
    "exploration": ("exploration", ExplorationArtifact),
    "struktur": ("structure", StructureArtifact),
    "algorithmus": ("algorithm", AlgorithmArtifact),
}


def _validate_typ(
    typ: str,
) -> tuple[str, type[ExplorationArtifact | StructureArtifact | AlgorithmArtifact]]:
    if typ not in _TYP_MAP:
        raise HTTPException(status_code=422, detail=f"Ungültiger Artefakttyp: '{typ}'")
    return _TYP_MAP[typ]


@router.get(
    "/projects/{projekt_id}/artifacts/{typ}/versions",
    response_model=ArtifactVersionsResponse,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
async def list_artifact_versions(
    projekt_id: str,
    typ: str,
    repo: RepoDep,
) -> ArtifactVersionsResponse:
    """Versionshistorie eines Artefakts (FR-B-10)."""
    db_typ, _ = _validate_typ(typ)
    _load_or_404(repo, projekt_id)
    versions_raw = repo.list_artifact_versions(projekt_id, db_typ)
    versions = [
        ArtifactVersionInfo(
            version=v["version"],  # type: ignore[arg-type]
            erstellt_am=str(v["erstellt_am"]),
            created_by=str(v["created_by"]),
        )
        for v in versions_raw
    ]
    return ArtifactVersionsResponse(versions=versions)


@router.post(
    "/projects/{projekt_id}/artifacts/{typ}/restore",
    response_model=ArtifactRestoreResponse,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
async def restore_artifact_version(
    projekt_id: str,
    typ: str,
    body: ArtifactRestoreRequest,
    repo: RepoDep,
) -> ArtifactRestoreResponse:
    """Version wiederherstellen — erzeugt neue Version (FR-B-10)."""
    db_typ, model_class = _validate_typ(typ)
    project = _load_or_404(repo, projekt_id)
    try:
        raw_json = repo.load_artifact_version(projekt_id, db_typ, body.version)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Version {body.version} nicht gefunden")
    restored = model_class.model_validate_json(raw_json)
    # Increment version to create a new entry (FR-B-10: history not overwritten)
    restored.version = _get_current_version(project, typ) + 1
    _set_artifact(project, typ, restored)
    # FR-B-10 AC#4: recalculate completeness from restored artifact
    _recalculate_completeness(project)
    repo.save(project)
    return ArtifactRestoreResponse(artefakt=restored.model_dump())


@router.post(
    "/projects/{projekt_id}/import",
    response_model=ArtifactRestoreResponse,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
async def import_artifact(
    projekt_id: str,
    body: ArtifactImportRequest,
    repo: RepoDep,
) -> ArtifactRestoreResponse:
    """Artefakt importieren und validieren (FR-B-07, FR-C-04)."""
    _, model_class = _validate_typ(body.typ)
    project = _load_or_404(repo, projekt_id)
    try:
        imported = model_class.model_validate(body.artefakt)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        )
    imported.version = _get_current_version(project, body.typ) + 1
    _set_artifact(project, body.typ, imported)
    # FR-C-04 / FR-B-10 AC#4: recalculate completeness after import
    _recalculate_completeness(project)
    repo.save(project)
    return ArtifactRestoreResponse(artefakt=imported.model_dump())


_ARTIFACT_ATTR = {
    "exploration": "exploration_artifact",
    "struktur": "structure_artifact",
    "algorithmus": "algorithm_artifact",
}


def _get_current_version(project: Project, typ: str) -> int:
    return int(getattr(project, _ARTIFACT_ATTR[typ]).version)


def _set_artifact(
    project: Project,
    typ: str,
    artifact: ExplorationArtifact | StructureArtifact | AlgorithmArtifact,
) -> None:
    setattr(project, _ARTIFACT_ATTR[typ], artifact)


@router.post("/projects/{projekt_id}/debug/advance-phase", response_model=AdvancePhaseResponse)
async def debug_advance_phase(projekt_id: str, repo: RepoDep) -> AdvancePhaseResponse:
    from core.phase_transition import advance_phase as do_advance

    project = _load_or_404(repo, projekt_id)
    if not do_advance(project, project.working_memory):
        raise HTTPException(status_code=400, detail="Bereits in der letzten Phase")
    repo.save(project)
    return AdvancePhaseResponse(project=_project_to_response(project))


@router.get(
    "/projects/{projekt_id}/validation",
    response_model=ValidationReportResponse,
    responses={404: {"model": ErrorResponse}},
    tags=["projects"],
)
async def get_validation_report(projekt_id: str, repo: RepoDep) -> ValidationReportResponse:
    """Aktuellen Validierungsbericht abrufen (SDD 6.6.4, FR-C-08)."""
    project = _load_or_404(repo, projekt_id)
    bericht = project.working_memory.validierungsbericht
    if bericht is None:
        raise HTTPException(status_code=404, detail="Kein Validierungsbericht vorhanden")
    return ValidationReportResponse(
        befunde=[
            ValidationBefundResponse(
                befund_id=b.befund_id,
                schweregrad=b.schweregrad,
                beschreibung=b.beschreibung,
                betroffene_slots=b.betroffene_slots,
                artefakttyp=b.artefakttyp,
                empfehlung=b.empfehlung,
            )
            for b in bericht.befunde
        ],
        erstellt_am=bericht.erstellt_am,
        durchlauf_nr=bericht.durchlauf_nr,
        ist_bestanden=bericht.ist_bestanden,
    )


def _recalculate_completeness(project: Project) -> None:
    """Recalculate completeness from artifacts (FR-B-10 AC#4, FR-E-05)."""
    state, filled, total = CompletenessCalculator().calculate(
        project.exploration_artifact, project.structure_artifact, project.algorithm_artifact
    )
    wm = project.working_memory
    wm.completeness_state, wm.befuellte_slots, wm.bekannte_slots = state, filled, total
