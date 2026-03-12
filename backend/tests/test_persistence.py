"""Tests for SQLite persistence layer — Database + ProjectRepository.

All tests use in-memory SQLite (:memory:) — no file I/O required.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Generator
from datetime import UTC, datetime

import pytest

from artifacts.models import (
    AlgorithmArtifact,
    Algorithmusabschnitt,
    AlgorithmusStatus,
    CompletenessStatus,
    EmmaAktion,
    ExplorationArtifact,
    ExplorationSlot,
    Phasenstatus,
    Projektphase,
    Projektstatus,
    StructureArtifact,
    Strukturschritt,
    Strukturschritttyp,
)
from core.models import Project
from core.working_memory import WorkingMemory
from persistence.database import Database
from persistence.project_repository import ProjectRepository

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_working_memory(projekt_id: str = "p1") -> WorkingMemory:
    return WorkingMemory(
        projekt_id=projekt_id,
        aktive_phase=Projektphase.exploration,
        aktiver_modus="exploration",
        phasenstatus=Phasenstatus.in_progress,
        letzte_aenderung=datetime.now(tz=UTC),
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
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = {row[0] for row in cursor.fetchall()}
        assert "projects" in tables
        assert "artifact_versions" in tables
        assert "working_memory" in tables
        assert "dialog_history" in tables
        assert "validation_reports" in tables
        db.close()

    def test_idempotent_schema_init(self, tmp_path) -> None:  # type: ignore[no-untyped-def]
        """CREATE TABLE IF NOT EXISTS — zweites Database auf derselben Datei darf nicht schmeißen."""
        from persistence.database import Database

        db_file = str(tmp_path / "test.db")
        db1 = Database(db_file)
        db1.close()
        # If IF NOT EXISTS were missing, this second init would raise "table already exists"
        db2 = Database(db_file)
        conn = db2.get_connection()
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        assert "projects" in tables
        db2.close()

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
                (
                    "p1",
                    "Test",
                    "",
                    "2026-01-01",
                    "2026-01-01",
                    "exploration",
                    "exploration",
                    "aktiv",
                ),
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
                    (
                        "p2",
                        "Test",
                        "",
                        "2026-01-01",
                        "2026-01-01",
                        "exploration",
                        "exploration",
                        "aktiv",
                    ),
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
def repo() -> Generator[ProjectRepository, None, None]:
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

    def test_save_and_load_algorithm_artifact(self, repo) -> None:  # type: ignore[no-untyped-def]
        p = repo.create(name="Test")
        aktion = EmmaAktion(
            aktion_id="a1",
            aktionstyp="SEND_EMAIL",
            parameter={"empfaenger": "archiv@firma.de"},
            emma_kompatibel=True,
        )
        abschnitt = Algorithmusabschnitt(
            abschnitt_id="ab1",
            titel="Benachrichtigung versenden",
            struktur_ref="step_001",
            aktionen={"a1": aktion},
            completeness_status=CompletenessStatus.vollstaendig,
            status=AlgorithmusStatus.aktuell,
        )
        p.algorithm_artifact = AlgorithmArtifact(abschnitte={"ab1": abschnitt}, version=1)
        repo.save(p)

        loaded = repo.load(p.projekt_id)
        assert loaded.algorithm_artifact.abschnitte["ab1"].titel == "Benachrichtigung versenden"
        assert loaded.algorithm_artifact.abschnitte["ab1"].aktionen["a1"].emma_kompatibel is True
        assert loaded.algorithm_artifact.version == 1

    def test_save_and_load_structure_artifact(self, repo) -> None:  # type: ignore[no-untyped-def]
        p = repo.create(name="Test")
        schritt = Strukturschritt(
            schritt_id="step_001",
            titel="Eingang prüfen",
            typ=Strukturschritttyp.aktion,
            reihenfolge=1,
            completeness_status=CompletenessStatus.teilweise,
            algorithmus_status=AlgorithmusStatus.ausstehend,
        )
        p.structure_artifact = StructureArtifact(schritte={"step_001": schritt}, version=1)
        repo.save(p)

        loaded = repo.load(p.projekt_id)
        assert loaded.structure_artifact.schritte["step_001"].titel == "Eingang prüfen"
        assert loaded.structure_artifact.schritte["step_001"].schritt_id == "step_001"

    def test_only_changed_artifacts_create_new_version_rows(self, repo) -> None:  # type: ignore[no-untyped-def]
        """save() schreibt nur dann eine neue Zeile, wenn sich die version des Artefakts
        erhöht hat. Unveränderte Artefakte erzeugen keine Duplikat-Zeilen."""

        p = repo.create(name="Test")
        db: Database = repo._db

        def count_rows() -> int:
            return int(
                db.get_connection()
                .execute(
                    "SELECT COUNT(*) FROM artifact_versions WHERE projekt_id=?",
                    (p.projekt_id,),
                )
                .fetchone()[0]
            )

        # create() speichert version=0 für alle 3 Artefakte → 3 Zeilen
        assert count_rows() == 3

        # save() ohne Änderung → keine neuen Zeilen
        repo.save(p)
        assert count_rows() == 3

        # Nur Explorationsartefakt wird gepatcht (version 0 → 1)
        p.exploration_artifact = ExplorationArtifact(
            slots={
                "s1": ExplorationSlot(
                    slot_id="s1",
                    bezeichnung="Name",
                    inhalt="Inhalt",
                    completeness_status=CompletenessStatus.teilweise,
                )
            },
            version=1,
        )
        repo.save(p)
        # Nur exploration bekommt eine neue Zeile → 4 Zeilen total
        assert count_rows() == 4

        # Struktur- und Algorithmusartefakt noch unverändert → erneutes save → immer noch 4
        repo.save(p)
        assert count_rows() == 4

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

    def test_save_updates_zuletzt_geaendert_in_db(self, repo) -> None:  # type: ignore[no-untyped-def]
        """zuletzt_geaendert muss nach save() in der Datenbank tatsächlich neuer sein."""
        import time

        p = repo.create(name="Test")
        original_ts = p.zuletzt_geaendert
        time.sleep(0.02)
        repo.save(p)

        loaded = repo.load(p.projekt_id)
        assert loaded.zuletzt_geaendert > original_ts

    def test_save_is_atomic_partial_failure_rolls_back(self, repo, monkeypatch) -> None:  # type: ignore[no-untyped-def]
        """FR-E-01: Bei einem Fehler mitten in save() darf kein Partial State geschrieben werden.

        Strategie: Wir patchen working_memory.model_dump_json() so, dass es nach dem
        Artifact-INSERT wirft. Danach darf die neue Artifact-Version NICHT in der DB stehen.
        """
        p = repo.create(name="Atomic Test")

        # Modify artifact so save() would write a new artifact_versions row
        slot = ExplorationSlot(
            slot_id="s1",
            bezeichnung="Test",
            inhalt="Neuer Inhalt",
            completeness_status=CompletenessStatus.teilweise,
        )
        p.exploration_artifact = ExplorationArtifact(slots={"s1": slot}, version=1)

        # Force failure when working_memory is serialized (last step in save()).
        # Pydantic v2 blocks instance-level attribute patching, so we patch the class.
        def fail(self: object) -> str:
            raise RuntimeError("simulated DB write failure")

        monkeypatch.setattr(WorkingMemory, "model_dump_json", fail)

        with pytest.raises(RuntimeError, match="simulated DB write failure"):
            repo.save(p)

        # Artifact version 1 must NOT be in the DB — transaction was rolled back
        conn = repo._db.get_connection()
        count = conn.execute(
            "SELECT COUNT(*) FROM artifact_versions WHERE projekt_id=? AND version_id=1",
            (p.projekt_id,),
        ).fetchone()[0]
        assert count == 0, "Partial write committed — atomicity (FR-E-01) violated"

    def test_phase_change_persists(self, repo) -> None:  # type: ignore[no-untyped-def]
        """aktive_phase-Änderung muss nach save()/load() erhalten bleiben."""
        p = repo.create(name="Test")
        assert p.aktive_phase == Projektphase.exploration

        p.aktive_phase = Projektphase.strukturierung
        p.aktiver_modus = "structuring"
        p.working_memory.aktive_phase = Projektphase.strukturierung
        repo.save(p)

        loaded = repo.load(p.projekt_id)
        assert loaded.aktive_phase == Projektphase.strukturierung
        assert loaded.aktiver_modus == "structuring"
        assert loaded.working_memory.aktive_phase == Projektphase.strukturierung
