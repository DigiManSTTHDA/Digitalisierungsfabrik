"""REST-Endpunkte — FastAPI router for all REST API endpoints (HLA Section 6).

All route handlers use explicit Pydantic request/response models from
api.schemas — no dict or Any responses (AGENTS.md API Contract rules).

SDD references: FR-G-01 (Projektanlage), FR-G-02 (Projektliste),
FR-G-04 (Projektabschluss), FR-B-06 (Artefaktsichtbarkeit),
FR-B-07 (Download/Export/Import), FR-B-10 (Versionswiederherstellung).
"""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from api.schemas import (
    ArtifactsResponse,
    DownloadResponse,
    ErrorResponse,
    ProjectCompleteResponse,
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectResponse,
)
from artifacts.models import Projektstatus
from core.models import Project
from persistence.database import Database
from persistence.project_repository import ProjectRepository

logger = structlog.get_logger()

router = APIRouter(prefix="/api", tags=["projects"])


# ---------------------------------------------------------------------------
# Dependency injection
# ---------------------------------------------------------------------------


def _get_repository() -> ProjectRepository:
    """Provide a ProjectRepository backed by the configured database."""
    from config import get_settings

    settings = get_settings()
    db = Database(settings.database_path)
    return ProjectRepository(db)


RepoDep = Annotated[ProjectRepository, Depends(_get_repository)]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Project CRUD (Story 05-02)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Artifact endpoints (Story 05-03)
# ---------------------------------------------------------------------------


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
