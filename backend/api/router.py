"""REST-Endpunkte — all REST API endpoints (HLA Section 6, api/router.py)."""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError

from api.schemas import (
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
    ProjectListResponse,
    ProjectResponse,
)
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


def _get_repository() -> ProjectRepository:
    """Provide a ProjectRepository backed by the configured database."""
    from config import get_settings

    settings = get_settings()
    db = Database(settings.database_path)
    return ProjectRepository(db)


RepoDep = Annotated[ProjectRepository, Depends(_get_repository)]


def _project_to_response(project: Project) -> ProjectResponse:
    return ProjectResponse(
        projekt_id=project.projekt_id,
        name=project.name,
        beschreibung=project.beschreibung,
        erstellt_am=project.erstellt_am,
        zuletzt_geaendert=project.zuletzt_geaendert,
        aktive_phase=project.aktive_phase,
        aktiver_modus=project.aktiver_modus,
        projektstatus=project.projektstatus,
    )


def _load_or_404(repo: ProjectRepository, projekt_id: str) -> Project:
    """Load a project or raise 404."""
    try:
        return repo.load(projekt_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Projekt '{projekt_id}' nicht gefunden",
        )


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
    """Neues Projekt anlegen (FR-G-01)."""
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


_TYP_TO_DB: dict[str, str] = {
    "exploration": "exploration",
    "struktur": "structure",
    "algorithmus": "algorithm",
}

_TYP_TO_MODEL: dict[str, type[ExplorationArtifact | StructureArtifact | AlgorithmArtifact]] = {
    "exploration": ExplorationArtifact,
    "struktur": StructureArtifact,
    "algorithmus": AlgorithmArtifact,
}


def _validate_typ(typ: str) -> str:
    """Validate and map the artifact type path parameter."""
    if typ not in _TYP_TO_DB:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Ungültiger Artefakttyp: '{typ}'. Erlaubt: exploration, struktur, algorithmus",
        )
    return _TYP_TO_DB[typ]


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
    db_typ = _validate_typ(typ)
    _load_or_404(repo, projekt_id)  # ensure project exists
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
    db_typ = _validate_typ(typ)
    project = _load_or_404(repo, projekt_id)
    try:
        raw_json = repo.load_artifact_version(projekt_id, db_typ, body.version)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {body.version} nicht gefunden",
        )
    model_class = _TYP_TO_MODEL[typ]
    restored = model_class.model_validate_json(raw_json)
    # Increment version to create a new entry (FR-B-10: history not overwritten)
    restored.version = _get_current_version(project, typ) + 1
    _set_artifact(project, typ, restored)
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
    _validate_typ(body.typ)
    project = _load_or_404(repo, projekt_id)
    model_class = _TYP_TO_MODEL[body.typ]
    try:
        imported = model_class.model_validate(body.artefakt)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        )
    imported.version = _get_current_version(project, body.typ) + 1
    _set_artifact(project, body.typ, imported)
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
