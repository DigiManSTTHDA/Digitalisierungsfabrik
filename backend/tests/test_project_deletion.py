"""Tests for project deletion — single and batch (Story 08-05).

Uses FastAPI TestClient with in-memory SQLite. Covers:
- Single delete (204/404)
- Batch delete (existing, partial, empty)
- Data removal (artifacts, dialog history, working memory)
- Project isolation (FR-E-06)
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from main import create_app
from persistence.database import Database
from persistence.project_repository import ProjectRepository


@pytest.fixture()
def _app_with_memory_db():  # type: ignore[no-untyped-def]
    """Fresh app + in-memory DB for each test."""
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


def _create_project(client: TestClient, name: str = "Test") -> str:
    """Helper: create a project and return its projekt_id."""
    resp = client.post("/api/projects", json={"name": name})
    assert resp.status_code == 201
    return resp.json()["projekt_id"]


# ---------------------------------------------------------------------------
# Single deletion
# ---------------------------------------------------------------------------


def test_delete_existing_project(client: TestClient) -> None:
    """Create project, delete it, verify 204 and project gone from list."""
    pid = _create_project(client)

    resp = client.delete(f"/api/projects/{pid}")
    assert resp.status_code == 204

    # Verify project is gone from list
    list_resp = client.get("/api/projects")
    assert list_resp.status_code == 200
    project_ids = [p["projekt_id"] for p in list_resp.json()["projects"]]
    assert pid not in project_ids


def test_delete_nonexistent_project(client: TestClient) -> None:
    """DELETE with random UUID returns 404."""
    resp = client.delete("/api/projects/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404
    assert "nicht gefunden" in resp.json()["detail"]


def test_delete_removes_all_data(client: TestClient, repo: ProjectRepository) -> None:
    """After deletion, loading project raises; dialog history and versions gone."""
    pid = _create_project(client)

    # Add some dialog history
    repo.append_dialog_turn(pid, 1, "user", "Hallo")
    repo.append_dialog_turn(pid, 2, "assistant", "Willkommen")

    # Verify data exists before deletion
    history = repo.load_dialog_history(pid)
    assert len(history) == 2

    # Delete
    resp = client.delete(f"/api/projects/{pid}")
    assert resp.status_code == 204

    # Verify project is gone
    with pytest.raises(ValueError, match="nicht gefunden"):
        repo.load(pid)

    # Verify dialog history is gone
    history_after = repo.load_dialog_history(pid)
    assert len(history_after) == 0

    # Verify artifact versions are gone
    conn = repo._db.get_connection()
    rows = conn.execute(
        "SELECT COUNT(*) as cnt FROM artifact_versions WHERE projekt_id = ?", (pid,)
    ).fetchone()
    assert rows["cnt"] == 0


def test_delete_does_not_affect_other_projects(client: TestClient, repo: ProjectRepository) -> None:
    """Create 2 projects, delete 1, verify the other is intact (FR-E-06)."""
    pid1 = _create_project(client, "Projekt A")
    pid2 = _create_project(client, "Projekt B")

    resp = client.delete(f"/api/projects/{pid1}")
    assert resp.status_code == 204

    # Projekt B must still be loadable with correct data
    project_b = repo.load(pid2)
    assert project_b.name == "Projekt B"
    assert project_b.projekt_id == pid2


# ---------------------------------------------------------------------------
# Batch deletion
# ---------------------------------------------------------------------------


def test_batch_delete_multiple(client: TestClient) -> None:
    """Create 3 projects, batch-delete 2, verify 2 deleted and 1 remains."""
    pid1 = _create_project(client, "A")
    pid2 = _create_project(client, "B")
    pid3 = _create_project(client, "C")

    resp = client.request(
        "DELETE",
        "/api/projects/batch",
        json={"projekt_ids": [pid1, pid2]},
    )
    assert resp.status_code == 200
    assert resp.json()["deleted_count"] == 2

    # Verify only pid3 remains
    list_resp = client.get("/api/projects")
    project_ids = [p["projekt_id"] for p in list_resp.json()["projects"]]
    assert pid1 not in project_ids
    assert pid2 not in project_ids
    assert pid3 in project_ids


def test_batch_delete_partial_ids(client: TestClient) -> None:
    """Batch with mix of existing and non-existing IDs — deletes what exists."""
    pid1 = _create_project(client, "Exists")
    fake_id = "00000000-0000-0000-0000-000000000000"

    resp = client.request(
        "DELETE",
        "/api/projects/batch",
        json={"projekt_ids": [pid1, fake_id]},
    )
    assert resp.status_code == 200
    assert resp.json()["deleted_count"] == 1


def test_batch_delete_empty_list_rejected(client: TestClient) -> None:
    """Empty projekt_ids list returns 422 (Pydantic validation)."""
    resp = client.request(
        "DELETE",
        "/api/projects/batch",
        json={"projekt_ids": []},
    )
    assert resp.status_code == 422
