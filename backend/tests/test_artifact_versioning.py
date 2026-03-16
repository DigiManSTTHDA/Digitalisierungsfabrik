"""Tests for artifact versioning — list_artifact_versions and load_artifact_version.

Story 05-04: Artifact versioning.
"""

from __future__ import annotations

from collections.abc import Generator

import pytest

from persistence.database import Database
from persistence.project_repository import ProjectRepository


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def repo() -> Generator[ProjectRepository, None, None]:
    db = Database(":memory:")
    yield ProjectRepository(db)
    db.close()


# ---------------------------------------------------------------------------
# Story 05-04: list_artifact_versions and load_artifact_version
# ---------------------------------------------------------------------------


class TestArtifactVersioning:
    """Story 05-04: list_artifact_versions and load_artifact_version."""

    def test_list_artifact_versions(self, repo) -> None:  # type: ignore[no-untyped-def]
        """Version 0 exists after project creation."""
        p = repo.create(name="V-Test")
        versions = repo.list_artifact_versions(p.projekt_id, "exploration")
        assert len(versions) == 1
        assert versions[0]["version"] == 0
        assert "erstellt_am" in versions[0]
        assert versions[0]["created_by"] == "system"

    def test_load_artifact_version(self, repo) -> None:  # type: ignore[no-untyped-def]
        """Load specific artifact version returns valid JSON."""
        p = repo.create(name="V-Load")
        raw = repo.load_artifact_version(p.projekt_id, "exploration", 0)
        assert '"version":0' in raw.replace(" ", "").replace('"version": 0', '"version":0')
        # Parse it to verify it's valid artifact JSON
        from artifacts.models import ExplorationArtifact

        artifact = ExplorationArtifact.model_validate_json(raw)
        assert artifact.version == 0
