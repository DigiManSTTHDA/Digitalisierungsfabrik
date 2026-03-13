"""Tests for Epic 03: Orchestrator, WorkingMemory, Mode Interface, and Stub Modes.

Coverage:
- Story 03-01: Flag enum, ModeContext, ModeOutput, BaseMode
- Story 03-02: Stub mode implementations (ExplorationMode, etc.)
- Story 03-04: Orchestrator 11-step cycle, mode dispatch, mode switch, persistence
"""

from __future__ import annotations

import pytest

from artifacts.models import (
    AlgorithmArtifact,
    Algorithmusabschnitt,
    AlgorithmusStatus,
    CompletenessStatus,
    ExplorationArtifact,
    ExplorationSlot,
    Phasenstatus,
    Projektphase,
    StructureArtifact,
    Strukturschritt,
    Strukturschritttyp,
)
from core.orchestrator import Orchestrator, TurnInput, TurnOutput
from core.working_memory import WorkingMemory
from modes.base import BaseMode, Flag, ModeContext, ModeOutput
from modes.exploration import ExplorationMode
from modes.moderator import Moderator
from modes.specification import SpecificationMode
from modes.structuring import StructuringMode
from modes.validation import ValidationMode
from persistence.database import Database
from persistence.project_repository import ProjectRepository

# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _make_db() -> Database:
    return Database(":memory:")


def _make_repo(db: Database) -> ProjectRepository:
    return ProjectRepository(db)


def _make_default_modes() -> dict[str, BaseMode]:
    return {
        "exploration": ExplorationMode(),
        "strukturierung": StructuringMode(),
        "spezifikation": SpecificationMode(),
        "validierung": ValidationMode(),
        "moderator": Moderator(),
    }


def _make_orchestrator(repo: ProjectRepository) -> Orchestrator:
    return Orchestrator(repository=repo, modes=_make_default_modes())


def _make_context(wm: WorkingMemory) -> ModeContext:
    """Build a minimal ModeContext for mode stub tests."""
    return ModeContext(
        projekt_id="p1",
        aktive_phase=Projektphase.exploration,
        aktiver_modus="exploration",
        exploration_artifact=ExplorationArtifact(),
        structure_artifact=StructureArtifact(),
        algorithm_artifact=AlgorithmArtifact(),
        working_memory=wm,
        dialog_history=[],
        completeness_state={},
    )


def _minimal_wm() -> WorkingMemory:
    from datetime import UTC, datetime

    return WorkingMemory(
        projekt_id="p1",
        aktive_phase=Projektphase.exploration,
        aktiver_modus="exploration",
        phasenstatus=Phasenstatus.in_progress,
        letzte_aenderung=datetime.now(tz=UTC),
    )


# ---------------------------------------------------------------------------
# Story 03-01 — WorkingMemory model fields and defaults
# ---------------------------------------------------------------------------


def test_working_memory_default_values() -> None:
    from datetime import UTC, datetime

    wm = WorkingMemory(
        projekt_id="p-test",
        aktive_phase=Projektphase.exploration,
        aktiver_modus="exploration",
        phasenstatus=Phasenstatus.in_progress,
        letzte_aenderung=datetime.now(tz=UTC),
    )
    assert wm.befuellte_slots == 0
    assert wm.bekannte_slots == 0
    assert wm.flags == []
    assert wm.letzter_dialogturn == 0
    assert wm.vorheriger_modus is None


def test_working_memory_json_round_trip() -> None:
    from datetime import UTC, datetime

    wm = WorkingMemory(
        projekt_id="p-test",
        aktive_phase=Projektphase.exploration,
        aktiver_modus="exploration",
        phasenstatus=Phasenstatus.in_progress,
        letzte_aenderung=datetime.now(tz=UTC),
        befuellte_slots=3,
        bekannte_slots=5,
    )
    json_str = wm.model_dump_json()
    wm2 = WorkingMemory.model_validate_json(json_str)
    assert wm2.befuellte_slots == 3
    assert wm2.bekannte_slots == 5
    assert wm2.projekt_id == "p-test"


# ---------------------------------------------------------------------------
# Story 03-01 — Flag enum
# ---------------------------------------------------------------------------


def test_flag_enum_has_six_values() -> None:
    assert len(Flag) == 6


def test_flag_enum_values_match_sdd() -> None:
    assert Flag.phase_complete == "phase_complete"
    assert Flag.needs_clarification == "needs_clarification"
    assert Flag.escalate == "escalate"
    assert Flag.blocked == "blocked"
    assert Flag.artefakt_updated == "artefakt_updated"
    assert Flag.validation_failed == "validation_failed"


# ---------------------------------------------------------------------------
# Story 03-01 — ModeOutput construction
# ---------------------------------------------------------------------------


def test_mode_output_with_empty_patches_is_valid() -> None:
    output = ModeOutput(
        nutzeraeusserung="Hallo",
        patches=[],
        phasenstatus=Phasenstatus.in_progress,
        flags=[],
    )
    assert output.patches == []
    assert output.flags == []


def test_mode_output_default_fields() -> None:
    output = ModeOutput(
        nutzeraeusserung="Test",
        phasenstatus=Phasenstatus.in_progress,
    )
    assert output.patches == []
    assert output.flags == []


# ---------------------------------------------------------------------------
# Story 03-01 — BaseMode.call() raises NotImplementedError
# ---------------------------------------------------------------------------


async def test_base_mode_call_raises_not_implemented() -> None:
    base = BaseMode()
    ctx = _make_context(_minimal_wm())
    with pytest.raises(NotImplementedError):
        await base.call(ctx)


# ---------------------------------------------------------------------------
# Story 03-02 — Stub mode implementations
# ---------------------------------------------------------------------------


def test_all_stub_modes_are_base_mode_instances() -> None:
    modes: list[BaseMode] = [
        ExplorationMode(),
        StructuringMode(),
        SpecificationMode(),
        ValidationMode(),
        Moderator(),
    ]
    for mode in modes:
        assert isinstance(mode, BaseMode), f"{type(mode).__name__} is not a BaseMode instance"


async def test_exploration_mode_returns_valid_output() -> None:
    mode = ExplorationMode()
    ctx = _make_context(_minimal_wm())
    output = await mode.call(ctx)
    assert isinstance(output, ModeOutput)
    assert output.patches == []
    assert output.flags == []
    assert output.phasenstatus == Phasenstatus.in_progress
    assert len(output.nutzeraeusserung) > 0


async def test_structuring_mode_returns_valid_output() -> None:
    mode = StructuringMode()
    ctx = _make_context(_minimal_wm())
    output = await mode.call(ctx)
    assert output.patches == []
    assert output.flags == []
    assert len(output.nutzeraeusserung) > 0


async def test_specification_mode_returns_valid_output() -> None:
    mode = SpecificationMode()
    ctx = _make_context(_minimal_wm())
    output = await mode.call(ctx)
    assert output.patches == []
    assert output.flags == []
    assert len(output.nutzeraeusserung) > 0


async def test_validation_mode_returns_valid_output() -> None:
    mode = ValidationMode()
    ctx = _make_context(_minimal_wm())
    output = await mode.call(ctx)
    assert output.patches == []
    assert output.flags == []
    assert len(output.nutzeraeusserung) > 0


async def test_moderator_returns_valid_output() -> None:
    mode = Moderator()
    ctx = _make_context(_minimal_wm())
    output = await mode.call(ctx)
    assert output.patches == []
    assert output.flags == []
    assert len(output.nutzeraeusserung) > 0


# ---------------------------------------------------------------------------
# Story 03-04 — Orchestrator: basic turn
# ---------------------------------------------------------------------------


async def test_full_turn_with_stub_mode_returns_no_error() -> None:
    db = _make_db()
    repo = _make_repo(db)
    project = repo.create("Test-Projekt")
    orchestrator = _make_orchestrator(repo)

    result = await orchestrator.process_turn(project.projekt_id, TurnInput(text="Hallo"))

    assert isinstance(result, TurnOutput)
    assert result.error is None
    assert len(result.nutzeraeusserung) > 0


async def test_letzter_dialogturn_incremented_after_turn() -> None:
    db = _make_db()
    repo = _make_repo(db)
    project = repo.create("Test-Projekt")
    orchestrator = _make_orchestrator(repo)

    await orchestrator.process_turn(project.projekt_id, TurnInput(text="Hallo"))
    reloaded = repo.load(project.projekt_id)

    assert reloaded.working_memory.letzter_dialogturn == 1


async def test_letzter_dialogturn_increments_per_turn() -> None:
    db = _make_db()
    repo = _make_repo(db)
    project = repo.create("Test-Projekt")
    orchestrator = _make_orchestrator(repo)

    await orchestrator.process_turn(project.projekt_id, TurnInput(text="Turn 1"))
    await orchestrator.process_turn(project.projekt_id, TurnInput(text="Turn 2"))
    await orchestrator.process_turn(project.projekt_id, TurnInput(text="Turn 3"))
    reloaded = repo.load(project.projekt_id)

    assert reloaded.working_memory.letzter_dialogturn == 3


# ---------------------------------------------------------------------------
# Story 03-04 — Orchestrator: mode dispatch
# ---------------------------------------------------------------------------


async def test_correct_mode_called_for_exploration_modus() -> None:
    """ExplorationMode is called when aktiver_modus = 'exploration'."""
    called: list[str] = []

    class TrackedExploration(BaseMode):
        async def call(self, context: ModeContext) -> ModeOutput:
            called.append("exploration")
            return ModeOutput(
                nutzeraeusserung="ok",
                patches=[],
                phasenstatus=Phasenstatus.in_progress,
                flags=[],
            )

    db = _make_db()
    repo = _make_repo(db)
    project = repo.create("Test-Projekt")
    orchestrator = Orchestrator(
        repository=repo,
        modes={"exploration": TrackedExploration(), "moderator": Moderator()},
    )

    await orchestrator.process_turn(project.projekt_id, TurnInput(text="Hallo"))
    assert called == ["exploration"]


# ---------------------------------------------------------------------------
# Story 03-04 — Orchestrator: mode switch on flags
# ---------------------------------------------------------------------------


async def test_mode_switch_on_phase_complete_flag() -> None:
    """aktiver_modus switches to 'moderator' when phase_complete flag is set."""

    class PhaseDoneMode(BaseMode):
        async def call(self, context: ModeContext) -> ModeOutput:
            return ModeOutput(
                nutzeraeusserung="Phase abgeschlossen",
                patches=[],
                phasenstatus=Phasenstatus.phase_complete,
                flags=[Flag.phase_complete],
            )

    db = _make_db()
    repo = _make_repo(db)
    project = repo.create("Test-Projekt")
    orchestrator = Orchestrator(
        repository=repo,
        modes={
            "exploration": PhaseDoneMode(),
            "moderator": Moderator(),
        },
    )

    await orchestrator.process_turn(project.projekt_id, TurnInput(text="Fertig"))
    reloaded = repo.load(project.projekt_id)

    assert reloaded.working_memory.aktiver_modus == "moderator"
    assert reloaded.working_memory.vorheriger_modus == "exploration"


async def test_mode_switch_on_escalate_flag() -> None:
    """aktiver_modus switches to 'moderator' when escalate flag is set."""

    class EscalatingMode(BaseMode):
        async def call(self, context: ModeContext) -> ModeOutput:
            return ModeOutput(
                nutzeraeusserung="Eskalation",
                patches=[],
                phasenstatus=Phasenstatus.in_progress,
                flags=[Flag.escalate],
            )

    db = _make_db()
    repo = _make_repo(db)
    project = repo.create("Test-Projekt")
    orchestrator = Orchestrator(
        repository=repo,
        modes={"exploration": EscalatingMode(), "moderator": Moderator()},
    )

    await orchestrator.process_turn(project.projekt_id, TurnInput(text="Problem"))
    reloaded = repo.load(project.projekt_id)

    assert reloaded.working_memory.aktiver_modus == "moderator"
    assert reloaded.working_memory.vorheriger_modus == "exploration"


async def test_no_mode_switch_without_trigger_flags() -> None:
    """aktiver_modus stays 'exploration' when no trigger flag is set."""
    db = _make_db()
    repo = _make_repo(db)
    project = repo.create("Test-Projekt")
    orchestrator = _make_orchestrator(repo)

    await orchestrator.process_turn(project.projekt_id, TurnInput(text="Weiter"))
    reloaded = repo.load(project.projekt_id)

    assert reloaded.working_memory.aktiver_modus == "exploration"
    assert reloaded.working_memory.vorheriger_modus is None


# ---------------------------------------------------------------------------
# Story 03-04 — Orchestrator: persistence round-trip
# ---------------------------------------------------------------------------


async def test_persistence_round_trip() -> None:
    """After a turn, reloaded project WM matches the turn output WM."""
    db = _make_db()
    repo = _make_repo(db)
    project = repo.create("Test-Projekt")
    orchestrator = _make_orchestrator(repo)

    result = await orchestrator.process_turn(project.projekt_id, TurnInput(text="Hallo"))
    reloaded = repo.load(project.projekt_id)

    assert reloaded.working_memory.letzter_dialogturn == result.working_memory.letzter_dialogturn
    assert reloaded.working_memory.phasenstatus == result.working_memory.phasenstatus


# ---------------------------------------------------------------------------
# Story 03-04 — Orchestrator: completeness update
# ---------------------------------------------------------------------------


async def test_completeness_updated_after_turn() -> None:
    """Working Memory completeness fields reflect artifact state after turn."""
    db = _make_db()
    repo = _make_repo(db)
    project = repo.create("Test-Projekt")

    # Pre-populate project with one exploration slot.
    # version=1 ensures save() does not skip the write (version 0 is already stored by create()).
    slot = ExplorationSlot(
        slot_id="s1",
        titel="Prozessname",
        inhalt="Kreditorenbuchhaltung",
        completeness_status=CompletenessStatus.vollstaendig,
    )
    project.exploration_artifact = ExplorationArtifact(slots={"s1": slot}, version=1)
    repo.save(project)

    orchestrator = _make_orchestrator(repo)
    result = await orchestrator.process_turn(project.projekt_id, TurnInput(text="Hallo"))

    assert result.working_memory.bekannte_slots == 1
    assert result.working_memory.befuellte_slots == 1

    # Verify persisted
    reloaded = repo.load(project.projekt_id)
    assert reloaded.working_memory.bekannte_slots == 1
    assert reloaded.working_memory.befuellte_slots == 1


# ---------------------------------------------------------------------------
# Story 03-04 — Orchestrator: unknown project raises ValueError
# ---------------------------------------------------------------------------


async def test_unknown_project_id_raises_value_error() -> None:
    db = _make_db()
    repo = _make_repo(db)
    orchestrator = _make_orchestrator(repo)

    with pytest.raises(ValueError):
        await orchestrator.process_turn("nonexistent-id", TurnInput(text="Hallo"))


# ---------------------------------------------------------------------------
# Story 03-04 — Orchestrator: Executor error path
# ---------------------------------------------------------------------------


async def test_executor_error_returns_error_output_without_save() -> None:
    """Invalid patches → TurnOutput.error set, artifact version unchanged."""

    class InvalidPatchMode(BaseMode):
        async def call(self, context: ModeContext) -> ModeOutput:
            return ModeOutput(
                nutzeraeusserung="patch attempt",
                patches=[{"op": "replace", "path": "/invalid_path", "value": "x"}],
                phasenstatus=Phasenstatus.in_progress,
                flags=[],
            )

    db = _make_db()
    repo = _make_repo(db)
    project = repo.create("Test-Projekt")
    initial_version = project.exploration_artifact.version

    orchestrator = Orchestrator(
        repository=repo,
        modes={"exploration": InvalidPatchMode(), "moderator": Moderator()},
    )

    result = await orchestrator.process_turn(project.projekt_id, TurnInput(text="Hallo"))

    assert result.error is not None
    assert len(result.error) > 0

    # Artifact version unchanged — project was NOT saved after the error
    reloaded = repo.load(project.projekt_id)
    assert reloaded.exploration_artifact.version == initial_version
    # letzter_dialogturn also NOT incremented in the persisted state
    assert reloaded.working_memory.letzter_dialogturn == 0


# ---------------------------------------------------------------------------
# Story 03-04 — Orchestrator: invalidation write applied
# ---------------------------------------------------------------------------


async def test_mode_switch_on_blocked_flag() -> None:
    """aktiver_modus switches to 'moderator' when blocked flag is set."""

    class BlockedMode(BaseMode):
        async def call(self, context: ModeContext) -> ModeOutput:
            return ModeOutput(
                nutzeraeusserung="Blockiert",
                patches=[],
                phasenstatus=Phasenstatus.in_progress,
                flags=[Flag.blocked],
            )

    db = _make_db()
    repo = _make_repo(db)
    project = repo.create("Test-Projekt")
    orchestrator = Orchestrator(
        repository=repo,
        modes={"exploration": BlockedMode(), "moderator": Moderator()},
    )

    await orchestrator.process_turn(project.projekt_id, TurnInput(text="Problem"))
    reloaded = repo.load(project.projekt_id)

    assert reloaded.working_memory.aktiver_modus == "moderator"
    assert reloaded.working_memory.vorheriger_modus == "exploration"


async def test_wm_flags_stored_after_turn_with_flags() -> None:
    """wm.flags reflects the flags emitted by the mode — persisted for observability (SDD 6.4.1)."""

    class FlagEmittingMode(BaseMode):
        async def call(self, context: ModeContext) -> ModeOutput:
            return ModeOutput(
                nutzeraeusserung="Fertig",
                patches=[],
                phasenstatus=Phasenstatus.phase_complete,
                flags=[Flag.phase_complete],
            )

    db = _make_db()
    repo = _make_repo(db)
    project = repo.create("Test-Projekt")
    orchestrator = Orchestrator(
        repository=repo,
        modes={"exploration": FlagEmittingMode(), "moderator": Moderator()},
    )

    await orchestrator.process_turn(project.projekt_id, TurnInput(text="Fertig"))
    reloaded = repo.load(project.projekt_id)

    assert reloaded.working_memory.flags == ["phase_complete"]


async def test_mode_fallback_to_exploration_when_modus_unknown() -> None:
    """Falls aktiver_modus nicht in modes registriert, wird 'exploration' als Fallback verwendet."""
    called: list[str] = []

    class TrackedFallback(BaseMode):
        async def call(self, context: ModeContext) -> ModeOutput:
            called.append("exploration")
            return ModeOutput(
                nutzeraeusserung="Fallback",
                patches=[],
                phasenstatus=Phasenstatus.in_progress,
                flags=[],
            )

    db = _make_db()
    repo = _make_repo(db)
    project = repo.create("Test-Projekt")

    # Force an unregistered mode key into the persisted working memory
    project.working_memory.aktiver_modus = "nonexistent_mode"
    repo.save(project)

    orchestrator = Orchestrator(
        repository=repo,
        modes={"exploration": TrackedFallback(), "moderator": Moderator()},
    )

    result = await orchestrator.process_turn(project.projekt_id, TurnInput(text="Hallo"))

    assert result.error is None
    assert called == ["exploration"]


async def test_invalidation_write_applied_after_structure_patch() -> None:
    """When executor returns invalidated_abschnitt_ids, algorithm status is set to invalidiert."""

    db = _make_db()
    repo = _make_repo(db)
    project = repo.create("Test-Projekt")

    # Set up: one structure step referencing one algorithm section
    schritt = Strukturschritt(
        schritt_id="s1",
        titel="Schritt 1",
        typ=Strukturschritttyp.aktion,
        beschreibung="alte beschreibung",
        reihenfolge=1,
        completeness_status=CompletenessStatus.teilweise,
        algorithmus_status=AlgorithmusStatus.aktuell,
        algorithmus_ref=["a1"],
    )
    abschnitt = Algorithmusabschnitt(
        abschnitt_id="a1",
        titel="Abschnitt 1",
        struktur_ref="s1",
        completeness_status=CompletenessStatus.vollstaendig,
        status=AlgorithmusStatus.aktuell,
    )
    # version=1 ensures save() does not skip the write (version 0 was stored by create()).
    project.structure_artifact = StructureArtifact(schritte={"s1": schritt}, version=1)
    project.algorithm_artifact = AlgorithmArtifact(abschnitte={"a1": abschnitt}, version=1)
    repo.save(project)

    class StructurePatchMode(BaseMode):
        async def call(self, context: ModeContext) -> ModeOutput:
            return ModeOutput(
                nutzeraeusserung="Beschreibung geändert",
                patches=[
                    {
                        "op": "replace",
                        "path": "/schritte/s1/beschreibung",
                        "value": "neue beschreibung",
                    }
                ],
                phasenstatus=Phasenstatus.in_progress,
                flags=[],
            )

    orchestrator = Orchestrator(
        repository=repo,
        modes={"exploration": StructurePatchMode(), "moderator": Moderator()},
    )

    result = await orchestrator.process_turn(project.projekt_id, TurnInput(text="Ändere Schritt"))
    assert result.error is None

    reloaded = repo.load(project.projekt_id)
    assert reloaded.algorithm_artifact.abschnitte["a1"].status == AlgorithmusStatus.invalidiert
