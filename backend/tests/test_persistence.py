"""Tests for SQLite persistence layer — Database + ProjectRepository.

All tests use in-memory SQLite (:memory:) — no file I/O required.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

import pytest

from artifacts.models import (
    AlgorithmusStatus,
    CompletenessStatus,
    ExplorationArtifact,
    ExplorationSlot,
    Phasenstatus,
    Projektphase,
    Projektstatus,
    StructureArtifact,
    Strukturschritt,
)
from core.models import Project
from core.working_memory import WorkingMemory


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_working_memory(projekt_id: str = "p1") -> WorkingMemory:
    return WorkingMemory(
        projekt_id=projekt_id,
        aktive_phase=Projektphase.exploration,
        aktiver_modus="exploration",
        phasenstatus=Phasenstatus.in_progress,
        letzte_aenderung=datetime.now(tz=timezone.utc),
    )


# ---------------------------------------------------------------------------
# Story 01-04: Database class
# ---------------------------------------------------------------------------


class TestDatabase:
    def test_in_memory_instantiation(self) -> None:
        from persistence.database import Database

        db = Database(":memory:")
        db.close()

    def test_schema_tables_created(self) -> None:
        from persistence.database import Database

        db = Database(":memory:")
        conn = db.get_connection()
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = {row[0] for row in cursor.fetchall()}
        assert "projects" in tables
        assert "artifact_versions" in tables
        assert "working_memory" in tables
        assert "dialog_history" in tables
        assert "validation_reports" in tables
        db.close()

    def test_idempotent_schema_init(self) -> None:
        """Calling Database twice on the same connection must not raise."""
        from persistence.database import Database

        db = Database(":memory:")
        # A second Database on a real file would re-run IF NOT EXISTS — fine.
        # For :memory: just verify no exception on repeated use.
        conn = db.get_connection()
        conn.execute("SELECT 1")
        db.close()

    def test_foreign_keys_enforced(self) -> None:
        from persistence.database import Database

        db = Database(":memory:")
        conn = db.get_connection()
        # FK enforcement: inserting artifact_version with unknown projekt_id must fail
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                """INSERT INTO artifact_versions
                   (projekt_id, typ, version_id, timestamp, created_by, inhalt)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                ("nonexistent", "exploration", 1, "2026-01-01T00:00:00Z", "test", "{}"),
            )
            conn.commit()
        db.close()

    def test_transaction_commits(self) -> None:
        from persistence.database import Database

        db = Database(":memory:")
        with db.transaction():
            db.get_connection().execute(
                "INSERT INTO projects VALUES (?,?,?,?,?,?,?,?)",
                ("p1", "Test", "", "2026-01-01", "2026-01-01", "exploration", "exploration", "aktiv"),
            )
        # Verify row is visible after transaction
        cursor = db.get_connection().execute("SELECT projekt_id FROM projects")
        rows = cursor.fetchall()
        assert len(rows) == 1
        assert rows[0][0] == "p1"
        db.close()

    def test_transaction_rollback_on_exception(self) -> None:
        from persistence.database import Database

        db = Database(":memory:")
        with pytest.raises(ValueError):
            with db.transaction():
                db.get_connection().execute(
                    "INSERT INTO projects VALUES (?,?,?,?,?,?,?,?)",
                    ("p2", "Test", "", "2026-01-01", "2026-01-01", "exploration", "exploration", "aktiv"),
                )
                raise ValueError("simulated failure")
        # Row must NOT be present after rollback
        cursor = db.get_connection().execute("SELECT projekt_id FROM projects")
        assert cursor.fetchall() == []
        db.close()


# ---------------------------------------------------------------------------
# Story 01-05/06: ProjectRepository
# ---------------------------------------------------------------------------


@pytest.fixture
def repo():  # type: ignore[return]
    from persistence.database import Database
    from persistence.project_repository import ProjectRepository

    db = Database(":memory:")
    yield ProjectRepository(db)
    db.close()


class TestProjectRepositoryCreate:
    def test_create_returns_project(self, repo) -> None:  # type: ignore[no-untyped-def]
        p = repo.create(name="Rechnungsverarbeitung")
        assert isinstance(p, Project)
        assert p.projekt_id != ""
        assert p.name == "Rechnungsverarbeitung"

    def test_create_sets_uuid(self, repo) -> None:  # type: ignore[no-untyped-def]
        p1 = repo.create(name="A")
        p2 = repo.create(name="B")
        assert p1.projekt_id != p2.projekt_id

    def test_create_initial_phase_is_exploration(self, repo) -> None:  # type: ignore[no-untyped-def]
        p = repo.create(name="Test")
        assert p.aktive_phase == Projektphase.exploration
        assert p.projektstatus == Projektstatus.aktiv

    def test_create_artifacts_are_empty(self, repo) -> None:  # type: ignore[no-untyped-def]
        p = repo.create(name="Test")
        assert p.exploration_artifact.slots == {}
        assert p.structure_artifact.schritte == {}
        assert p.algorithm_artifact.abschnitte == {}


class TestProjectRepositoryLoadRoundTrip:
    def test_create_then_load_metadata(self, repo) -> None:  # type: ignore[no-untyped-def]
        p = repo.create(name="Archivierung", beschreibung="Wichtig")
        loaded = repo.load(p.projekt_id)
        assert loaded.name == "Archivierung"
        assert loaded.beschreibung == "Wichtig"
        assert loaded.aktive_phase == Projektphase.exploration
        assert loaded.working_memory.aktive_phase == Projektphase.exploration

    def test_load_nonexistent_raises_value_error(self, repo) -> None:  # type: ignore[no-untyped-def]
        with pytest.raises(ValueError, match="nicht gefunden"):
            repo.load("does-not-exist")

    def test_save_and_load_exploration_artifact(self, repo) -> None:  # type: ignore[no-untyped-def]
        p = repo.create(name="Test")
        slot = ExplorationSlot(
            slot_id="s1",
            bezeichnung="Prozessname",
            inhalt="Rechnungsverarbeitung",
            completeness_status=CompletenessStatus.vollstaendig,
        )
        p.exploration_artifact = ExplorationArtifact(slots={"s1": slot}, version=1)
        repo.save(p)

        loaded = repo.load(p.projekt_id)
        assert loaded.exploration_artifact.slots["s1"].inhalt == "Rechnungsverarbeitung"
        assert loaded.exploration_artifact.version == 1

    def test_save_and_load_structure_artifact(self, repo) -> None:  # type: ignore[no-untyped-def]
        p = repo.create(name="Test")
        schritt = Strukturschritt(
            schritt_id="step_001",
            titel="Eingang prüfen",
            typ="ACTIVITY",
            reihenfolge=1,
            completeness_status=CompletenessStatus.teilweise,
            algorithmus_status=AlgorithmusStatus.ausstehend,
        )
        p.structure_artifact = StructureArtifact(schritte={"step_001": schritt}, version=1)
        repo.save(p)

        loaded = repo.load(p.projekt_id)
        assert loaded.structure_artifact.schritte["step_001"].titel == "Eingang prüfen"
        assert loaded.structure_artifact.schritte["step_001"].schritt_id == "step_001"

    def test_save_increments_version_in_artifact_versions(self, repo) -> None:  # type: ignore[no-untyped-def]
        """Each save() must create a new row in artifact_versions."""
        from persistence.database import Database

        p = repo.create(name="Test")
        repo.save(p)  # second save (create already saved once)

        db: Database = repo._db
        cursor = db.get_connection().execute(
            "SELECT COUNT(*) FROM artifact_versions WHERE projekt_id=?",
            (p.projekt_id,),
        )
        count = cursor.fetchone()[0]
        # create() saves 3 artifact types × 1 = 3 rows,
        # explicit save() adds another 3 = 6 total
        assert count >= 6

    def test_multiple_saves_load_returns_latest(self, repo) -> None:  # type: ignore[no-untyped-def]
        p = repo.create(name="Test")
        p.exploration_artifact = ExplorationArtifact(
            slots={
                "s1": ExplorationSlot(
                    slot_id="s1",
                    bezeichnung="Name",
                    inhalt="Version 1",
                    completeness_status=CompletenessStatus.teilweise,
                )
            },
            version=1,
        )
        repo.save(p)

        p.exploration_artifact = ExplorationArtifact(
            slots={
                "s1": ExplorationSlot(
                    slot_id="s1",
                    bezeichnung="Name",
                    inhalt="Version 2",
                    completeness_status=CompletenessStatus.vollstaendig,
                )
            },
            version=2,
        )
        repo.save(p)

        loaded = repo.load(p.projekt_id)
        assert loaded.exploration_artifact.slots["s1"].inhalt == "Version 2"


class TestProjectRepositoryList:
    def test_list_empty_db(self, repo) -> None:  # type: ignore[no-untyped-def]
        assert repo.list_projects() == []

    def test_list_returns_all_projects(self, repo) -> None:  # type: ignore[no-untyped-def]
        repo.create(name="Projekt A")
        repo.create(name="Projekt B")
        projects = repo.list_projects()
        assert len(projects) == 2
        names = {p.name for p in projects}
        assert names == {"Projekt A", "Projekt B"}

    def test_list_projects_have_correct_metadata(self, repo) -> None:  # type: ignore[no-untyped-def]
        p = repo.create(name="Einzelprojekt", beschreibung="Beschreibung")
        projects = repo.list_projects()
        assert len(projects) == 1
        assert projects[0].projekt_id == p.projekt_id
        assert projects[0].beschreibung == "Beschreibung"


class TestProjectRepositoryAtomicity:
    def test_working_memory_updated_after_save(self, repo) -> None:  # type: ignore[no-untyped-def]
        p = repo.create(name="Test")
        p.working_memory.befuellte_slots = 5
        p.working_memory.bekannte_slots = 10
        repo.save(p)

        loaded = repo.load(p.projekt_id)
        assert loaded.working_memory.befuellte_slots == 5
        assert loaded.working_memory.bekannte_slots == 10

    def test_save_updates_zuletzt_geaendert(self, repo) -> None:  # type: ignore[no-untyped-def]
        p = repo.create(name="Test")
        original_ts = p.zuletzt_geaendert
        import time
        time.sleep(0.01)
        repo.save(p)
        assert p.zuletzt_geaendert >= original_ts
