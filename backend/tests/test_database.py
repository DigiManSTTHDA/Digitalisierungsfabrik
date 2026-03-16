"""Tests for the Database class (SQLite persistence layer).

Story 01-04: Database class.
"""

from __future__ import annotations

import sqlite3

import pytest

from persistence.database import Database


# ---------------------------------------------------------------------------
# Story 01-04: Database class
# ---------------------------------------------------------------------------


class TestDatabase:
    def test_in_memory_instantiation(self) -> None:
        db = Database(":memory:")
        db.close()

    def test_schema_tables_created(self) -> None:
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
