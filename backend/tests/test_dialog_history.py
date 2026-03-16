"""Tests for dialog history persistence.

FR-E-07: Dialog History Persistence.
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
# FR-E-07: Dialog History Persistence
# ---------------------------------------------------------------------------


class TestDialogHistoryPersistence:
    def test_append_and_load_single_turn(self, repo) -> None:  # type: ignore[no-untyped-def]
        """append_dialog_turn() schreibt einen Turn; load_dialog_history() liest ihn zurück."""
        p = repo.create(name="Dialog Test")
        repo.append_dialog_turn(p.projekt_id, 1, "user", "Hallo")
        history = repo.load_dialog_history(p.projekt_id)
        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert history[0]["inhalt"] == "Hallo"
        assert "timestamp" in history[0]

    def test_turns_returned_in_order(self, repo) -> None:  # type: ignore[no-untyped-def]
        """Drei Turns werden chronologisch (aufsteigend nach turn_id) zurückgegeben."""
        p = repo.create(name="Order Test")
        repo.append_dialog_turn(p.projekt_id, 1, "user", "Erster")
        repo.append_dialog_turn(p.projekt_id, 1, "assistant", "Zweiter")
        repo.append_dialog_turn(p.projekt_id, 2, "user", "Dritter")

        history = repo.load_dialog_history(p.projekt_id)
        assert len(history) == 3
        assert history[0]["inhalt"] == "Erster"
        assert history[1]["inhalt"] == "Zweiter"
        assert history[2]["inhalt"] == "Dritter"

    def test_dialog_history_scoped_per_project(self, repo) -> None:  # type: ignore[no-untyped-def]
        """Dialoghistorie ist pro Projekt isoliert — kein Bleed-over zwischen Projekten."""
        p_a = repo.create(name="Projekt A")
        p_b = repo.create(name="Projekt B")

        repo.append_dialog_turn(p_a.projekt_id, 1, "user", "Nachricht von A")
        repo.append_dialog_turn(p_b.projekt_id, 1, "user", "Nachricht von B")

        history_a = repo.load_dialog_history(p_a.projekt_id)
        history_b = repo.load_dialog_history(p_b.projekt_id)

        assert len(history_a) == 1
        assert history_a[0]["inhalt"] == "Nachricht von A"
        assert len(history_b) == 1
        assert history_b[0]["inhalt"] == "Nachricht von B"

    def test_load_dialog_history_last_n_limit(self, repo) -> None:  # type: ignore[no-untyped-def]
        """last_n-Parameter begrenzt die Anzahl der zurückgegebenen Turns."""
        p = repo.create(name="Limit Test")
        for i in range(5):
            repo.append_dialog_turn(p.projekt_id, i + 1, "user", f"Turn {i + 1}")

        history = repo.load_dialog_history(p.projekt_id, last_n=3)
        assert len(history) == 3

    def test_load_dialog_history_empty_for_new_project(self, repo) -> None:  # type: ignore[no-untyped-def]
        """Neues Projekt hat leere Dialoghistorie."""
        p = repo.create(name="Leer Test")
        history = repo.load_dialog_history(p.projekt_id)
        assert history == []
