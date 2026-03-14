"""Tests for phase transition logic (Story 07-02).

Verifies:
- Phase ordering matches SDD 6.1.1
- next_phase returns correct successor
- advance_phase updates WM and project
"""

from __future__ import annotations

from datetime import UTC, datetime

from artifacts.models import Phasenstatus, Projektphase
from core.models import Project
from core.phase_transition import PHASE_ORDER, PHASE_TO_MODE, advance_phase, next_phase
from core.working_memory import WorkingMemory


def _make_wm(phase: Projektphase = Projektphase.exploration) -> WorkingMemory:
    return WorkingMemory(
        projekt_id="test",
        aktive_phase=phase,
        aktiver_modus="exploration",
        phasenstatus=Phasenstatus.in_progress,
        letzte_aenderung=datetime.now(tz=UTC),
    )


def _make_project(phase: Projektphase = Projektphase.exploration) -> Project:
    wm = _make_wm(phase)
    return Project(
        projekt_id="test",
        name="Test",
        erstellt_am=datetime.now(tz=UTC),
        zuletzt_geaendert=datetime.now(tz=UTC),
        aktive_phase=phase,
        aktiver_modus=PHASE_TO_MODE[phase],
        projektstatus="aktiv",  # type: ignore[arg-type]
        working_memory=wm,
    )


def test_phase_order_matches_sdd() -> None:
    """Phase order is exactly: exploration → strukturierung → spezifikation → validierung."""
    assert PHASE_ORDER == [
        Projektphase.exploration,
        Projektphase.strukturierung,
        Projektphase.spezifikation,
        Projektphase.validierung,
    ]


def test_next_phase_from_exploration() -> None:
    """Next phase after exploration is strukturierung."""
    assert next_phase(Projektphase.exploration) == Projektphase.strukturierung


def test_next_phase_from_strukturierung() -> None:
    """Next phase after strukturierung is spezifikation."""
    assert next_phase(Projektphase.strukturierung) == Projektphase.spezifikation


def test_next_phase_from_spezifikation() -> None:
    """Next phase after spezifikation is validierung."""
    assert next_phase(Projektphase.spezifikation) == Projektphase.validierung


def test_next_phase_from_validierung() -> None:
    """No next phase after validierung (end of sequence)."""
    assert next_phase(Projektphase.validierung) is None


def test_advance_phase_updates_wm_and_project() -> None:
    """advance_phase updates both WM and project to the next phase."""
    project = _make_project(Projektphase.exploration)
    wm = project.working_memory
    result = advance_phase(project, wm)
    assert result is True
    assert wm.aktive_phase == Projektphase.strukturierung
    assert wm.aktiver_modus == "structuring"
    assert wm.phasenstatus == Phasenstatus.in_progress
    assert project.aktive_phase == Projektphase.strukturierung
    assert project.aktiver_modus == "structuring"


def test_advance_phase_at_end_returns_false() -> None:
    """advance_phase returns False when already at last phase."""
    project = _make_project(Projektphase.validierung)
    wm = project.working_memory
    wm.aktive_phase = Projektphase.validierung
    result = advance_phase(project, wm)
    assert result is False
    assert wm.aktive_phase == Projektphase.validierung  # unchanged


def test_phase_to_mode_covers_all_phases() -> None:
    """Every phase in PHASE_ORDER has a mode mapping."""
    for phase in PHASE_ORDER:
        assert phase in PHASE_TO_MODE
