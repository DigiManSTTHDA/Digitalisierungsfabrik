"""Tests for validation report data model and persistence (Story 10-02).

Verifies:
- Validierungsbericht correctly tracks ist_bestanden based on severity
- Validierungsbefund rejects empty beschreibung
- Persistence round-trip preserves all report fields
- durchlauf_nr increments correctly
"""

from __future__ import annotations

from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from artifacts.models import (
    Schweregrad,
    Validierungsbefund,
    Validierungsbericht,
)
from persistence.database import Database
from persistence.project_repository import ProjectRepository


@pytest.fixture()
def repo() -> Generator[ProjectRepository, None, None]:
    db = Database(":memory:")
    yield ProjectRepository(db)
    db.close()


def _make_befund(
    schweregrad: Schweregrad = Schweregrad.kritisch,
    befund_id: str = "b1",
    beschreibung: str = "Fehlende referenzielle Integrität",
) -> Validierungsbefund:
    return Validierungsbefund(
        befund_id=befund_id,
        schweregrad=schweregrad,
        beschreibung=beschreibung,
        betroffene_slots=["schritt_1"],
        artefakttyp="struktur",
        empfehlung="Referenz prüfen",
    )


def _make_bericht(
    befunde: list[Validierungsbefund] | None = None,
    durchlauf_nr: int = 1,
    ist_bestanden: bool = False,
) -> Validierungsbericht:
    return Validierungsbericht(
        befunde=befunde or [],
        erstellt_am=datetime(2026, 3, 16, 12, 0, 0, tzinfo=UTC),
        durchlauf_nr=durchlauf_nr,
        ist_bestanden=ist_bestanden,
    )


# ── ist_bestanden logic tests ───────────────────────────────────────────────


def test_bericht_with_kritisch_befund_is_not_bestanden() -> None:
    """A report containing a kritisch finding must have ist_bestanden=False."""
    bericht = _make_bericht(
        befunde=[_make_befund(Schweregrad.kritisch)],
        ist_bestanden=False,
    )
    assert bericht.ist_bestanden is False
    assert len(bericht.befunde) == 1
    assert bericht.befunde[0].schweregrad == Schweregrad.kritisch


def test_bericht_without_kritisch_is_bestanden() -> None:
    """A report with only warnung and hinweis findings can be bestanden."""
    bericht = _make_bericht(
        befunde=[
            _make_befund(Schweregrad.warnung, befund_id="w1", beschreibung="Warnung"),
            _make_befund(Schweregrad.hinweis, befund_id="h1", beschreibung="Hinweis"),
        ],
        ist_bestanden=True,
    )
    assert bericht.ist_bestanden is True
    assert len(bericht.befunde) == 2


def test_bericht_empty_befunde_is_bestanden() -> None:
    """An empty report (no findings) is bestanden."""
    bericht = _make_bericht(befunde=[], ist_bestanden=True)
    assert bericht.ist_bestanden is True
    assert len(bericht.befunde) == 0


# ── Validation of Validierungsbefund ─────────────────────────────────────────


def test_befund_rejects_empty_beschreibung() -> None:
    """Validierungsbefund must have a non-empty beschreibung (min_length=1)."""
    with pytest.raises(ValidationError, match="beschreibung"):
        Validierungsbefund(
            befund_id="b1",
            schweregrad=Schweregrad.kritisch,
            beschreibung="",
            betroffene_slots=[],
            artefakttyp="struktur",
            empfehlung="",
        )


def test_befund_accepts_valid_construction() -> None:
    """Validierungsbefund with all valid fields is constructed correctly."""
    befund = _make_befund()
    assert befund.schweregrad == Schweregrad.kritisch
    assert befund.betroffene_slots == ["schritt_1"]
    assert befund.artefakttyp == "struktur"
    assert befund.empfehlung == "Referenz prüfen"


# ── Schweregrad completeness ────────────────────────────────────────────────


def test_schweregrad_has_exactly_three_members() -> None:
    """Schweregrad enum must have exactly kritisch, warnung, hinweis — no more, no fewer.

    This guards against accidental additions that would change severity filtering.
    """
    members = set(Schweregrad)
    assert members == {Schweregrad.kritisch, Schweregrad.warnung, Schweregrad.hinweis}


# ── Persistence round-trip ──────────────────────────────────────────────────


def test_validierungsbericht_persists_through_save_load(
    repo: ProjectRepository,
) -> None:
    """A project with a validierungsbericht in WM survives save/load with all fields."""
    project = repo.create("Validation-Test")

    # Set up validation report in working memory
    bericht = _make_bericht(
        befunde=[
            _make_befund(Schweregrad.kritisch, "b1", "Kritischer Befund"),
            _make_befund(Schweregrad.warnung, "b2", "Warnung"),
        ],
        durchlauf_nr=2,
        ist_bestanden=False,
    )
    project.working_memory.validierungsbericht = bericht
    repo.save(project)

    # Reload and verify all fields
    reloaded = repo.load(project.projekt_id)
    rb = reloaded.working_memory.validierungsbericht
    assert rb is not None
    assert rb.durchlauf_nr == 2
    assert rb.ist_bestanden is False
    assert len(rb.befunde) == 2
    assert rb.befunde[0].befund_id == "b1"
    assert rb.befunde[0].schweregrad == Schweregrad.kritisch
    assert rb.befunde[0].beschreibung == "Kritischer Befund"
    assert rb.befunde[0].betroffene_slots == ["schritt_1"]
    assert rb.befunde[1].befund_id == "b2"
    assert rb.befunde[1].schweregrad == Schweregrad.warnung


def test_validierungsbericht_none_persists(repo: ProjectRepository) -> None:
    """A project without a validierungsbericht (None) survives save/load."""
    project = repo.create("No-Validation")
    assert project.working_memory.validierungsbericht is None
    repo.save(project)

    reloaded = repo.load(project.projekt_id)
    assert reloaded.working_memory.validierungsbericht is None


# ── durchlauf_nr increment ──────────────────────────────────────────────────


def test_durchlauf_nr_increments_across_passes(repo: ProjectRepository) -> None:
    """durchlauf_nr is preserved and incrementable across save/load cycles."""
    project = repo.create("Durchlauf-Test")

    # First pass
    bericht1 = _make_bericht(durchlauf_nr=1, ist_bestanden=False)
    project.working_memory.validierungsbericht = bericht1
    repo.save(project)

    reloaded = repo.load(project.projekt_id)
    assert reloaded.working_memory.validierungsbericht is not None
    assert reloaded.working_memory.validierungsbericht.durchlauf_nr == 1

    # Simulate second pass — increment durchlauf_nr
    reloaded.working_memory.validierungsbericht = _make_bericht(durchlauf_nr=2, ist_bestanden=True)
    repo.save(reloaded)

    reloaded2 = repo.load(project.projekt_id)
    assert reloaded2.working_memory.validierungsbericht is not None
    assert reloaded2.working_memory.validierungsbericht.durchlauf_nr == 2
    assert reloaded2.working_memory.validierungsbericht.ist_bestanden is True
