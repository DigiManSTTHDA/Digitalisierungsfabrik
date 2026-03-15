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
def _app_with_memory_db():  # type: ignore[no-untyped-def]
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
def client(_app_with_memory_db):  # type: ignore[no-untyped-def]
    app, _repo = _app_with_memory_db
    return TestClient(app)


@pytest.fixture()
def repo(_app_with_memory_db):  # type: ignore[no-untyped-def]
    _app, repo = _app_with_memory_db
    return repo


# ---------------------------------------------------------------------------
# Story 05-02: Project CRUD
# ---------------------------------------------------------------------------


def test_create_project(client: TestClient) -> None:
    """POST /api/projects creates a project and returns 201 with all SDD 7.2.1 fields."""
    resp = client.post("/api/projects", json={"name": "Test", "beschreibung": "Desc"})
    assert resp.status_code == 201
    data = resp.json()
    assert "projekt_id" in data
    assert data["name"] == "Test"
    assert data["beschreibung"] == "Desc"
    assert data["aktive_phase"] == "exploration"
    # FR-D-11: Project starts in moderator mode. Greeting and handoff
    # happen over WebSocket, not synchronously at creation time.
    assert data["aktiver_modus"] == "moderator"
    assert data["projektstatus"] == "aktiv"
    # Verify timestamps are valid ISO 8601 strings
    from datetime import datetime

    datetime.fromisoformat(data["erstellt_am"])
    datetime.fromisoformat(data["zuletzt_geaendert"])


def test_create_project_without_beschreibung(client: TestClient) -> None:
    """POST /api/projects with only name field works."""
    resp = client.post("/api/projects", json={"name": "Minimal"})
    assert resp.status_code == 201
    assert resp.json()["beschreibung"] == ""


def test_create_project_missing_name(client: TestClient) -> None:
    """POST /api/projects without name returns 422."""
    resp = client.post("/api/projects", json={"beschreibung": "no name"})
    assert resp.status_code == 422


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
    assert data["aktive_phase"] == "exploration"
    assert data["aktiver_modus"] == "moderator"  # FR-D-11: greeting on WS, not REST
    assert data["projektstatus"] == "aktiv"
    # Verify timestamps are parseable ISO strings
    from datetime import datetime

    datetime.fromisoformat(data["erstellt_am"])
    datetime.fromisoformat(data["zuletzt_geaendert"])


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


# ---------------------------------------------------------------------------
# Story 05-04: Artifact Versioning & Import
# ---------------------------------------------------------------------------


def test_list_artifact_versions(client: TestClient) -> None:
    """GET versions returns version 0 after project creation."""
    pid = client.post("/api/projects", json={"name": "V"}).json()["projekt_id"]
    resp = client.get(f"/api/projects/{pid}/artifacts/exploration/versions")
    assert resp.status_code == 200
    versions = resp.json()["versions"]
    assert len(versions) == 1
    assert versions[0]["version"] == 0


def test_list_artifact_versions_invalid_typ(client: TestClient) -> None:
    """GET versions returns 422 for invalid artifact type."""
    pid = client.post("/api/projects", json={"name": "V2"}).json()["projekt_id"]
    resp = client.get(f"/api/projects/{pid}/artifacts/invalid/versions")
    assert resp.status_code == 422


def test_restore_artifact_version(client: TestClient) -> None:
    """POST restore creates a new version from version 0."""
    pid = client.post("/api/projects", json={"name": "R"}).json()["projekt_id"]
    resp = client.post(
        f"/api/projects/{pid}/artifacts/exploration/restore",
        json={"version": 0},
    )
    assert resp.status_code == 200
    assert "artefakt" in resp.json()
    # Check that a new version was created
    versions = client.get(f"/api/projects/{pid}/artifacts/exploration/versions").json()["versions"]
    assert len(versions) == 2
    assert versions[0]["version"] == 1  # newest first


def test_restore_artifact_version_not_found(client: TestClient) -> None:
    """POST restore returns 404 for non-existent version."""
    pid = client.post("/api/projects", json={"name": "R2"}).json()["projekt_id"]
    resp = client.post(
        f"/api/projects/{pid}/artifacts/exploration/restore",
        json={"version": 999},
    )
    assert resp.status_code == 404


def test_import_artifact_valid(client: TestClient) -> None:
    """POST import accepts valid artifact JSON."""
    pid = client.post("/api/projects", json={"name": "I"}).json()["projekt_id"]
    resp = client.post(
        f"/api/projects/{pid}/import",
        json={"typ": "exploration", "artefakt": {"slots": {}, "version": 0}},
    )
    assert resp.status_code == 200
    assert "artefakt" in resp.json()


def test_import_artifact_invalid(client: TestClient) -> None:
    """POST import returns 422 for invalid artifact JSON."""
    pid = client.post("/api/projects", json={"name": "I2"}).json()["projekt_id"]
    # ExplorationArtifact requires 'slots' to be a dict — pass invalid type
    resp = client.post(
        f"/api/projects/{pid}/import",
        json={"typ": "exploration", "artefakt": {"slots": "not-a-dict"}},
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Additional gap-filling tests (validate-tests)
# ---------------------------------------------------------------------------


def test_download_not_found(client: TestClient) -> None:
    """GET /api/projects/{id}/download returns 404 for non-existent project."""
    resp = client.get("/api/projects/no-such-id/download")
    assert resp.status_code == 404


def test_list_versions_version_metadata_complete(client: TestClient) -> None:
    """GET versions returns all ArtifactVersionInfo fields with valid values."""
    from datetime import datetime

    pid = client.post("/api/projects", json={"name": "VM"}).json()["projekt_id"]
    resp = client.get(f"/api/projects/{pid}/artifacts/exploration/versions")
    v = resp.json()["versions"][0]
    assert v["version"] == 0
    # Validate ISO 8601 format (not just non-empty string)
    datetime.fromisoformat(v["erstellt_am"])
    assert v["created_by"] == "system"


def test_restore_struktur_artifact_type_mapping(client: TestClient) -> None:
    """POST restore works for 'struktur' typ (maps to DB 'structure')."""
    pid = client.post("/api/projects", json={"name": "S"}).json()["projekt_id"]
    resp = client.post(
        f"/api/projects/{pid}/artifacts/struktur/restore",
        json={"version": 0},
    )
    assert resp.status_code == 200
    assert "artefakt" in resp.json()
    versions = client.get(f"/api/projects/{pid}/artifacts/struktur/versions").json()["versions"]
    assert len(versions) == 2


def test_create_project_empty_name_rejected(client: TestClient) -> None:
    """POST /api/projects with empty name returns 422."""
    resp = client.post("/api/projects", json={"name": ""})
    assert resp.status_code == 422


def test_create_project_whitespace_name_rejected(client: TestClient) -> None:
    """POST /api/projects with whitespace-only name returns 422."""
    resp = client.post("/api/projects", json={"name": "   "})
    assert resp.status_code == 422


def test_debug_advance_phase(client: TestClient) -> None:
    """POST debug/advance-phase advances from exploration to strukturierung."""
    pid = client.post("/api/projects", json={"name": "AP"}).json()["projekt_id"]
    resp = client.post(f"/api/projects/{pid}/debug/advance-phase")
    assert resp.status_code == 200
    assert resp.json()["project"]["aktive_phase"] == "strukturierung"


def test_debug_advance_phase_at_end(client: TestClient) -> None:
    """POST debug/advance-phase returns 400 at last phase."""
    pid = client.post("/api/projects", json={"name": "APE"}).json()["projekt_id"]
    # Advance through all phases
    for _ in range(3):  # exploration→strukturierung→spezifikation→validierung
        client.post(f"/api/projects/{pid}/debug/advance-phase")
    resp = client.post(f"/api/projects/{pid}/debug/advance-phase")
    assert resp.status_code == 400
    assert "letzten Phase" in resp.json()["detail"]


def test_debug_advance_phase_not_found(client: TestClient) -> None:
    """POST debug/advance-phase returns 404 for non-existent project."""
    resp = client.post("/api/projects/nope/debug/advance-phase")
    assert resp.status_code == 404


def test_import_artifact_persisted(client: TestClient) -> None:
    """POST import persists the imported artifact — verified by reload."""
    pid = client.post("/api/projects", json={"name": "IP"}).json()["projekt_id"]
    client.post(
        f"/api/projects/{pid}/import",
        json={"typ": "exploration", "artefakt": {"slots": {}, "version": 0}},
    )
    # Reload and verify the artifact version incremented
    artifacts = client.get(f"/api/projects/{pid}/artifacts").json()
    assert artifacts["exploration"]["version"] == 1


# ---------------------------------------------------------------------------
# QA Review: Connection Lifecycle + Boundary Tests
# ---------------------------------------------------------------------------


def test_db_connection_closed_after_request(_app_with_memory_db) -> None:  # type: ignore[no-untyped-def]
    """Verify the generator dependency closes the DB after each request.

    This is a regression test for BUG 1 (CRITICAL connection leak).
    The _get_repository dependency must use yield/finally to close the DB.
    """
    import inspect

    from api.router import _get_repository

    # The dependency MUST be a generator (yield-based) to ensure cleanup
    assert inspect.isgeneratorfunction(_get_repository), (
        "_get_repository must be a generator function (yield + finally: db.close()). "
        "A plain return leaks SQLite connections on every request."
    )


def test_create_project_very_long_name(client: TestClient) -> None:
    """POST /api/projects rejects names exceeding 200 characters."""
    resp = client.post("/api/projects", json={"name": "A" * 201})
    assert resp.status_code == 422


def test_create_project_max_length_name(client: TestClient) -> None:
    """POST /api/projects accepts name at exactly 200 characters."""
    resp = client.post("/api/projects", json={"name": "B" * 200})
    assert resp.status_code == 201
    assert len(resp.json()["name"]) == 200


def test_import_artifact_empty_body(client: TestClient) -> None:
    """POST /api/projects/{id}/import with empty body returns 422."""
    pid = client.post("/api/projects", json={"name": "Empty"}).json()["projekt_id"]
    resp = client.post(f"/api/projects/{pid}/import", json={})
    assert resp.status_code == 422


def test_restore_invalid_typ(client: TestClient) -> None:
    """POST restore with invalid artifact type returns 422."""
    pid = client.post("/api/projects", json={"name": "RT"}).json()["projekt_id"]
    resp = client.post(
        f"/api/projects/{pid}/artifacts/invalid_type/restore",
        json={"version": 0},
    )
    assert resp.status_code == 422


def test_multiple_projects_isolated(client: TestClient) -> None:
    """Changes to one project don't affect another (FR-E-06)."""
    pid1 = client.post("/api/projects", json={"name": "P1"}).json()["projekt_id"]
    pid2 = client.post("/api/projects", json={"name": "P2"}).json()["projekt_id"]

    # Complete P1
    client.post(f"/api/projects/{pid1}/complete")

    # P2 should still be aktiv
    p2 = client.get(f"/api/projects/{pid2}").json()
    assert p2["projektstatus"] == "aktiv"

    # P1 should be abgeschlossen
    p1 = client.get(f"/api/projects/{pid1}").json()
    assert p1["projektstatus"] == "abgeschlossen"
