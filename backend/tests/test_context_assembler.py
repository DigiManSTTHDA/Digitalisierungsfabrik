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


def test_prompt_context_summary_contains_prozesszusammenfassung_status() -> None:
    """prompt_context_summary shows Prozesszusammenfassung as leer or befüllt."""
    from artifacts.models import StructureArtifact

    # Empty summary → shows leer
    project = _make_project()
    context = build_context(project, completeness_state={})
    summary = prompt_context_summary(context)
    assert "Prozesszusammenfassung (Struktur): leer" in summary

    # Filled summary → shows befüllt
    project2 = _make_project()
    project2.structure_artifact = StructureArtifact(
        prozesszusammenfassung="Zusammenfassung des Reisekostenprozesses"
    )
    context2 = build_context(project2, completeness_state={})
    summary2 = prompt_context_summary(context2)
    assert "Prozesszusammenfassung (Struktur): befüllt" in summary2


def test_prompt_context_summary_nonempty_for_minimal_context() -> None:
    project = _make_project()
    context = build_context(project, completeness_state={})
    summary = prompt_context_summary(context)
    assert "exploration" in summary  # contains the phase name
    assert "0/0 befüllt" in summary  # contains slot counter


# ---------------------------------------------------------------------------
# dialog_history_n returns the LAST N turns, not any N turns
# ---------------------------------------------------------------------------


def test_build_context_dialog_history_n_returns_last_n_turns() -> None:
    """build_context with dialog_history_n=3 returns specifically the last 3 turns."""
    db = Database(":memory:")
    repo = ProjectRepository(db)
    project = repo.create("Test")

    # Write 5 dialog turns with distinguishable content
    for i in range(1, 6):
        repo.append_dialog_turn(project.projekt_id, i, "user", f"Turn {i}")

    settings = Settings(
        llm_provider="anthropic",
        llm_api_key="",
        llm_model="test",
        dialog_history_n=3,
    )

    context = build_context(project, completeness_state={}, repository=repo, settings=settings)

    # Exactly 3 turns returned
    assert len(context.dialog_history) == 3

    # They must be the LAST 3 turns: Turn 3, Turn 4, Turn 5
    contents = [entry["inhalt"] for entry in context.dialog_history]
    assert "Turn 3" in contents
    assert "Turn 4" in contents
    assert "Turn 5" in contents

    # The first two turns must NOT appear
    assert "Turn 1" not in contents
    assert "Turn 2" not in contents
    db.close()


# ---------------------------------------------------------------------------
# Story 09-03: Algorithm artifact counts + EMMA catalog
# ---------------------------------------------------------------------------


def test_prompt_context_summary_contains_algorithm_counts() -> None:
    """Algorithm artifact slot counts appear in summary output."""
    from artifacts.models import (
        AlgorithmArtifact,
        Algorithmusabschnitt,
        AlgorithmusStatus,
        EmmaAktion,
        EmmaAktionstyp,
    )

    project = _make_project()
    aktion = EmmaAktion(aktion_id="a1", aktionstyp=EmmaAktionstyp.READ)
    abschnitt = Algorithmusabschnitt(
        abschnitt_id="ab1",
        titel="Lesen",
        struktur_ref="step_001",
        aktionen={"a1": aktion},
        completeness_status=CompletenessStatus.teilweise,
        status=AlgorithmusStatus.aktuell,
    )
    project.algorithm_artifact = AlgorithmArtifact(abschnitte={"ab1": abschnitt})
    context = build_context(project, completeness_state={})
    summary = prompt_context_summary(context)
    assert "Algorithmusabschnitte: 1/1 befüllt" in summary


def test_prompt_context_summary_contains_algorithm_zusammenfassung_status() -> None:
    """Algorithm prozesszusammenfassung status appears in summary output."""
    from artifacts.models import AlgorithmArtifact

    # Empty
    project = _make_project()
    context = build_context(project, completeness_state={})
    summary = prompt_context_summary(context)
    assert "Prozesszusammenfassung (Algorithmus): leer" in summary

    # Filled
    project2 = _make_project()
    project2.algorithm_artifact = AlgorithmArtifact(
        prozesszusammenfassung="Technische Spezifikation"
    )
    context2 = build_context(project2, completeness_state={})
    summary2 = prompt_context_summary(context2)
    assert "Prozesszusammenfassung (Algorithmus): befüllt" in summary2


def test_emma_action_catalog_text_contains_all_types() -> None:
    """All 18 EMMA action types appear in the catalog text."""
    from artifacts.models import EmmaAktionstyp
    from core.context_assembler import emma_action_catalog_text

    text = emma_action_catalog_text()
    for member in EmmaAktionstyp:
        assert member.value in text, f"{member.value} not found in catalog text"


def test_emma_action_catalog_text_contains_descriptions() -> None:
    """Descriptions are non-empty for each EMMA action type."""
    from core.context_assembler import emma_action_catalog_text

    text = emma_action_catalog_text()
    lines = [line for line in text.strip().split("\n") if line.startswith("- ")]
    assert len(lines) == 18
    for line in lines:
        # Each line has format "- TYPE: Description"
        parts = line.split(": ", 1)
        assert len(parts) == 2, f"Unexpected format: {line}"
        assert len(parts[1]) > 5, f"Description too short: {line}"
