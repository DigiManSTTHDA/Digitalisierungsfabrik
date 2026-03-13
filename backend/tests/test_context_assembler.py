"""Tests for ContextAssembler upgrade (Story 04-04).

Coverage:
- dialog_history_n is read from Settings (not hardcoded 20)
- ModeContext has artifact_template field populated per phase
- prompt_context_summary returns expected content
"""

from __future__ import annotations

from datetime import UTC, datetime

from artifacts.models import (
    CompletenessStatus,
    ExplorationArtifact,
    ExplorationSlot,
    Phasenstatus,
    Projektphase,
    Projektstatus,
)
from artifacts.template_schema import EXPLORATION_TEMPLATE, STRUCTURE_TEMPLATE
from config import Settings
from core.context_assembler import build_context, prompt_context_summary
from core.models import Project
from core.working_memory import WorkingMemory
from persistence.database import Database
from persistence.project_repository import ProjectRepository


def _make_project(phase: Projektphase = Projektphase.exploration) -> Project:
    now = datetime.now(tz=UTC)
    wm = WorkingMemory(
        projekt_id="p1",
        aktive_phase=phase,
        aktiver_modus="exploration",
        phasenstatus=Phasenstatus.in_progress,
        letzte_aenderung=now,
    )
    return Project(
        projekt_id="p1",
        name="Test",
        erstellt_am=now,
        zuletzt_geaendert=now,
        aktive_phase=phase,
        aktiver_modus="exploration",
        projektstatus=Projektstatus.aktiv,
        working_memory=wm,
    )


# ---------------------------------------------------------------------------
# dialog_history_n is respected (not hardcoded 20)
# ---------------------------------------------------------------------------


def test_build_context_uses_settings_dialog_history_n() -> None:
    """build_context reads dialog_history_n from Settings, not the old default of 20."""
    db = Database(":memory:")
    repo = ProjectRepository(db)
    project = repo.create("Test")

    # Write 5 dialog turns
    for i in range(5):
        repo.append_dialog_turn(project.projekt_id, i + 1, "user", f"Turn {i + 1}")

    settings = Settings(
        llm_provider="anthropic",
        llm_api_key="",
        llm_model="test",
        dialog_history_n=3,
    )

    context = build_context(project, completeness_state={}, repository=repo, settings=settings)
    # With dialog_history_n=3, only 3 turns should be loaded
    assert len(context.dialog_history) == 3
    db.close()


def test_build_context_default_without_settings_loads_20() -> None:
    """Without settings, fallback to 20 for backward compatibility."""
    db = Database(":memory:")
    repo = ProjectRepository(db)
    project = repo.create("Test")

    # Write 25 dialog turns
    for i in range(25):
        repo.append_dialog_turn(project.projekt_id, i + 1, "user", f"Turn {i + 1}")

    context = build_context(project, completeness_state={}, repository=repo)
    # Default is 20
    assert len(context.dialog_history) == 20
    db.close()


# ---------------------------------------------------------------------------
# ModeContext has artifact_template populated per phase
# ---------------------------------------------------------------------------


def test_artifact_template_set_for_exploration_phase() -> None:
    project = _make_project(Projektphase.exploration)
    context = build_context(project, completeness_state={})
    assert context.artifact_template is not None
    assert context.artifact_template.artifact_type == "exploration"
    assert context.artifact_template == EXPLORATION_TEMPLATE


def test_artifact_template_set_for_strukturierung_phase() -> None:
    project = _make_project(Projektphase.strukturierung)
    context = build_context(project, completeness_state={})
    assert context.artifact_template is not None
    assert context.artifact_template.artifact_type == "structure"
    assert context.artifact_template == STRUCTURE_TEMPLATE


def test_artifact_template_none_for_abgeschlossen() -> None:
    project = _make_project(Projektphase.abgeschlossen)
    context = build_context(project, completeness_state={})
    assert context.artifact_template is None


# ---------------------------------------------------------------------------
# prompt_context_summary
# ---------------------------------------------------------------------------


def test_prompt_context_summary_contains_phase_and_modus() -> None:
    project = _make_project()
    context = build_context(project, completeness_state={})
    summary = prompt_context_summary(context)
    assert "exploration" in summary
    assert "Aktive Phase" in summary
    assert "Aktiver Modus" in summary


def test_prompt_context_summary_contains_slot_counts() -> None:
    project = _make_project()
    # Add one filled slot
    project.exploration_artifact = ExplorationArtifact(
        slots={
            "s1": ExplorationSlot(
                slot_id="s1",
                titel="Test",
                inhalt="Inhalt",
                completeness_status=CompletenessStatus.teilweise,
            ),
            "s2": ExplorationSlot(
                slot_id="s2",
                titel="Test2",
                inhalt="",
                completeness_status=CompletenessStatus.leer,
            ),
        }
    )
    context = build_context(project, completeness_state={})
    summary = prompt_context_summary(context)
    assert "1/2 befüllt" in summary


def test_prompt_context_summary_nonempty_for_minimal_context() -> None:
    project = _make_project()
    context = build_context(project, completeness_state={})
    summary = prompt_context_summary(context)
    assert len(summary) > 0
    assert "0/0 befüllt" in summary
