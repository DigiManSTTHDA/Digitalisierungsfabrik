"""REST API endpoint tests — FastAPI TestClient with in-memory SQLite.

Tests use dependency override to inject an in-memory Database so no
on-disk state leaks between tests.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import create_app
from persistence.database import Database
from persistence.project_repository import ProjectRepository


@pytest.fixture()
def _app_with_memory_db():
    """Create a fresh app + in-memory DB for each test."""
    app = create_app()
    db = Database(":memory:")
    repo = ProjectRepository(db)

    def _override_repo() -> ProjectRepository:
        return repo

    from api.router import _get_repository

    app.dependency_overrides[_get_repository] = _override_repo
    yield app, repo
    db.close()
    app.dependency_overrides.clear()


@pytest.fixture()
def client(_app_with_memory_db):
    app, _repo = _app_with_memory_db
    return TestClient(app)


@pytest.fixture()
def repo(_app_with_memory_db):
    _app, repo = _app_with_memory_db
    return repo


# ---------------------------------------------------------------------------
# Story 05-02: Project CRUD
# ---------------------------------------------------------------------------


def test_create_project(client: TestClient) -> None:
    """POST /api/projects creates a project and returns 201."""
    resp = client.post("/api/projects", json={"name": "Test", "beschreibung": "Desc"})
    assert resp.status_code == 201
    data = resp.json()
    assert "projekt_id" in data
    assert data["name"] == "Test"
    assert data["beschreibung"] == "Desc"
    assert data["aktive_phase"] == "exploration"
    assert data["projektstatus"] == "aktiv"


def test_create_project_without_beschreibung(client: TestClient) -> None:
    """POST /api/projects with only name field works."""
    resp = client.post("/api/projects", json={"name": "Minimal"})
    assert resp.status_code == 201
    assert resp.json()["beschreibung"] == ""


def test_list_projects_empty(client: TestClient) -> None:
    """GET /api/projects returns empty list when no projects exist."""
    resp = client.get("/api/projects")
    assert resp.status_code == 200
    assert resp.json()["projects"] == []


def test_list_projects(client: TestClient) -> None:
    """GET /api/projects returns all created projects."""
    client.post("/api/projects", json={"name": "A"})
    client.post("/api/projects", json={"name": "B"})
    resp = client.get("/api/projects")
    assert resp.status_code == 200
    projects = resp.json()["projects"]
    assert len(projects) == 2
    names = {p["name"] for p in projects}
    assert names == {"A", "B"}


def test_get_project(client: TestClient) -> None:
    """GET /api/projects/{id} returns correct project metadata."""
    create_resp = client.post("/api/projects", json={"name": "Proj", "beschreibung": "D"})
    pid = create_resp.json()["projekt_id"]
    resp = client.get(f"/api/projects/{pid}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["projekt_id"] == pid
    assert data["name"] == "Proj"
    assert data["beschreibung"] == "D"
    assert "erstellt_am" in data
    assert "zuletzt_geaendert" in data


def test_get_project_not_found(client: TestClient) -> None:
    """GET /api/projects/{id} returns 404 for unknown ID."""
    resp = client.get("/api/projects/nonexistent-id")
    assert resp.status_code == 404
    assert "nicht gefunden" in resp.json()["detail"]


# ---------------------------------------------------------------------------
# Story 05-03: Artifact & Project Lifecycle
# ---------------------------------------------------------------------------


def test_get_artifacts(client: TestClient) -> None:
    """GET /api/projects/{id}/artifacts returns all 3 artifacts."""
    pid = client.post("/api/projects", json={"name": "A"}).json()["projekt_id"]
    resp = client.get(f"/api/projects/{pid}/artifacts")
    assert resp.status_code == 200
    data = resp.json()
    assert "exploration" in data
    assert "struktur" in data
    assert "algorithmus" in data
    # Empty artifacts should have version 0 and empty slots
    assert data["exploration"]["version"] == 0
    assert data["struktur"]["version"] == 0
    assert data["algorithmus"]["version"] == 0


def test_get_artifacts_not_found(client: TestClient) -> None:
    """GET /api/projects/{id}/artifacts returns 404 for non-existent project."""
    resp = client.get("/api/projects/no-such-id/artifacts")
    assert resp.status_code == 404


def test_download_project(client: TestClient) -> None:
    """GET /api/projects/{id}/download returns JSON with all 3 artifacts."""
    pid = client.post("/api/projects", json={"name": "DL"}).json()["projekt_id"]
    resp = client.get(f"/api/projects/{pid}/download")
    assert resp.status_code == 200
    data = resp.json()
    assert "exploration" in data
    assert "struktur" in data
    assert "algorithmus" in data


def test_complete_project(client: TestClient) -> None:
    """POST /api/projects/{id}/complete sets projektstatus to abgeschlossen."""
    pid = client.post("/api/projects", json={"name": "C"}).json()["projekt_id"]
    resp = client.post(f"/api/projects/{pid}/complete")
    assert resp.status_code == 200
    assert resp.json()["project"]["projektstatus"] == "abgeschlossen"
    # Verify persistence — reload the project
    get_resp = client.get(f"/api/projects/{pid}")
    assert get_resp.json()["projektstatus"] == "abgeschlossen"


def test_complete_project_already_completed(client: TestClient) -> None:
    """POST /api/projects/{id}/complete returns 409 if already completed."""
    pid = client.post("/api/projects", json={"name": "C2"}).json()["projekt_id"]
    client.post(f"/api/projects/{pid}/complete")
    resp = client.post(f"/api/projects/{pid}/complete")
    assert resp.status_code == 409
    assert "bereits abgeschlossen" in resp.json()["detail"]


def test_complete_project_not_found(client: TestClient) -> None:
    """POST /api/projects/{id}/complete returns 404 for non-existent project."""
    resp = client.post("/api/projects/no-such-id/complete")
    assert resp.status_code == 404
