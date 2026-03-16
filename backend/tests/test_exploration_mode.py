"""Integration tests for full turn through Orchestrator with ExplorationMode (Story 04-08).

All tests use in-memory SQLite and a mocked LLMClient — no live API calls.
Tests verify: Pflicht-Slot initialization, patch application + persistence,
dialog history, and OutputValidator rejection of invalid paths.
"""

from __future__ import annotations

from datetime import UTC
from unittest.mock import AsyncMock

from core.orchestrator import Orchestrator, TurnInput
from llm.base import LLMClient, LLMResponse
from modes.base import BaseMode
from modes.exploration import ExplorationMode
from modes.moderator import Moderator
from persistence.database import Database
from persistence.project_repository import ProjectRepository

# ---------------------------------------------------------------------------
# Mock LLM Client
# ---------------------------------------------------------------------------


def _make_mock_llm(
    nutzeraeusserung: str = "Willkommen! Was ist der Auslöser Ihres Prozesses?",
    patches: list[dict] | None = None,  # type: ignore[type-arg]
) -> LLMClient:
    """Create a mock LLMClient that returns a valid apply_patches response."""
    if patches is None:
        patches = [
            {
                "op": "replace",
                "path": "/slots/prozessausloeser/inhalt",
                "value": "Nutzer öffnet Anwendung",
            }
        ]

    mock = AsyncMock(spec=LLMClient)
    mock.complete.return_value = LLMResponse(
        nutzeraeusserung=nutzeraeusserung,
        tool_input={"patches": patches},
    )
    return mock


def _make_invalid_path_llm() -> LLMClient:
    """Create a mock LLMClient that returns a patch with an invalid path."""
    mock = AsyncMock(spec=LLMClient)
    mock.complete.return_value = LLMResponse(
        nutzeraeusserung="Ungültig",
        tool_input={
            "patches": [
                {
                    "op": "replace",
                    "path": "/slots/prozessausloeser/nonexistent_field",
                    "value": "test",
                }
            ]
        },
    )
    return mock


def _make_orchestrator(repo: ProjectRepository, llm_client: LLMClient) -> Orchestrator:
    modes: dict[str, BaseMode] = {
        "exploration": ExplorationMode(llm_client=llm_client),
        "moderator": Moderator(),
    }
    return Orchestrator(repository=repo, modes=modes)


def _set_exploration_mode(repo: ProjectRepository, project) -> None:  # type: ignore[type-arg]
    """Force a freshly-created project into exploration mode (FR-D-11 changed default to moderator)."""
    project.aktiver_modus = "exploration"
    project.working_memory.aktiver_modus = "exploration"
    repo.save(project)


# ---------------------------------------------------------------------------
# Test: first turn initializes 9 Pflicht-Slots
# ---------------------------------------------------------------------------


async def test_first_turn_initializes_pflicht_slots() -> None:
    """After the first turn, all 9 Pflicht-Slot IDs must be present."""
    db = Database(":memory:")
    repo = ProjectRepository(db)
    project = repo.create("Test")
    _set_exploration_mode(repo, project)
    llm = _make_mock_llm()
    orchestrator = _make_orchestrator(repo, llm)

    result = await orchestrator.process_turn(project.projekt_id, TurnInput(text="Hallo"))
    assert result.error is None

    reloaded = repo.load(project.projekt_id)
    slot_ids = set(reloaded.exploration_artifact.slots.keys())

    expected_ids = {
        "prozessausloeser",
        "prozessziel",
        "prozessbeschreibung",
        "scope",
        "beteiligte_systeme",
        "umgebung",
        "randbedingungen",
        "ausnahmen",
        "prozesszusammenfassung",
    }
    assert slot_ids == expected_ids
    db.close()


# ---------------------------------------------------------------------------
# Test: patch applied and persisted
# ---------------------------------------------------------------------------


async def test_patch_applied_and_persisted() -> None:
    """Mock LLM patch is applied and persisted — reload confirms the value."""
    db = Database(":memory:")
    repo = ProjectRepository(db)
    project = repo.create("Test")
    _set_exploration_mode(repo, project)
    llm = _make_mock_llm()
    orchestrator = _make_orchestrator(repo, llm)

    result = await orchestrator.process_turn(
        project.projekt_id, TurnInput(text="Der Prozess startet wenn...")
    )
    assert result.error is None

    reloaded = repo.load(project.projekt_id)
    slot = reloaded.exploration_artifact.slots["prozessausloeser"]
    assert slot.inhalt == "Nutzer öffnet Anwendung"
    db.close()


# ---------------------------------------------------------------------------
# Test: dialog history written
# ---------------------------------------------------------------------------


async def test_dialog_history_written() -> None:
    """Both user and assistant dialog turns are written to the DB."""
    db = Database(":memory:")
    repo = ProjectRepository(db)
    project = repo.create("Test")
    _set_exploration_mode(repo, project)
    llm = _make_mock_llm(nutzeraeusserung="Erzählen Sie mir mehr.")
    orchestrator = _make_orchestrator(repo, llm)

    await orchestrator.process_turn(project.projekt_id, TurnInput(text="Test-Eingabe"))

    history = repo.load_dialog_history(project.projekt_id, last_n=10)
    user_turns = [h for h in history if h["role"] == "user"]
    assistant_turns = [h for h in history if h["role"] == "assistant"]

    assert len(user_turns) == 1
    assert user_turns[0]["inhalt"] == "Test-Eingabe"
    assert len(assistant_turns) == 1
    assert assistant_turns[0]["inhalt"] == "Erzählen Sie mir mehr."
    db.close()


# ---------------------------------------------------------------------------
# Test: OutputValidator rejects invalid path
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Test: second turn does not re-initialize slots (AC #4, Story 04-06)
# ---------------------------------------------------------------------------


async def test_second_turn_does_not_reinitialize_slots() -> None:
    """On the second turn, no add patches are emitted for already-existing slots."""
    db = Database(":memory:")
    repo = ProjectRepository(db)
    project = repo.create("Test")
    _set_exploration_mode(repo, project)
    llm = _make_mock_llm()
    orchestrator = _make_orchestrator(repo, llm)

    # First turn: initializes 9 slots
    result1 = await orchestrator.process_turn(project.projekt_id, TurnInput(text="Erster Turn"))
    assert result1.error is None

    reloaded_after_first = repo.load(project.projekt_id)
    assert len(reloaded_after_first.exploration_artifact.slots) == 9

    # Second turn: LLM returns an empty patches list (no new slot writes)
    llm2 = _make_mock_llm(patches=[])
    orchestrator2 = _make_orchestrator(repo, llm2)

    result2 = await orchestrator2.process_turn(project.projekt_id, TurnInput(text="Zweiter Turn"))
    assert result2.error is None

    reloaded_after_second = repo.load(project.projekt_id)
    # Still exactly 9 slots — no duplicate add patches
    assert len(reloaded_after_second.exploration_artifact.slots) == 9

    # The 9 slot IDs must be unchanged (no new slots added, none removed)
    expected_ids = {
        "prozessausloeser",
        "prozessziel",
        "prozessbeschreibung",
        "scope",
        "beteiligte_systeme",
        "umgebung",
        "randbedingungen",
        "ausnahmen",
        "prozesszusammenfassung",
    }
    assert set(reloaded_after_second.exploration_artifact.slots.keys()) == expected_ids
    db.close()


# ---------------------------------------------------------------------------
# Test: phasenstatus=nearing_completion when all 9 Pflicht-Slots are non-leer
# (AC #8, Story 04-06)
# ---------------------------------------------------------------------------


async def test_nearing_completion_phasenstatus_when_all_slots_filled() -> None:
    """phasenstatus is nearing_completion when all 9 Pflicht-Slots are non-leer."""
    from datetime import UTC, datetime

    from artifacts.models import (
        AlgorithmArtifact,
        CompletenessStatus,
        ExplorationArtifact,
        ExplorationSlot,
        Phasenstatus,
        Projektphase,
        StructureArtifact,
    )
    from artifacts.template_schema import EXPLORATION_TEMPLATE
    from core.working_memory import WorkingMemory
    from modes.base import ModeContext
    from modes.exploration import PFLICHT_SLOTS, ExplorationMode

    # Build a context where all 9 Pflicht-Slots exist and are non-leer
    slots = {
        slot_id: ExplorationSlot(
            slot_id=slot_id,
            titel=titel,
            inhalt="Etwas Inhalt",
            completeness_status=CompletenessStatus.vollstaendig,
        )
        for slot_id, titel in PFLICHT_SLOTS.items()
    }

    llm_mock = _make_mock_llm(patches=[])
    mode = ExplorationMode(llm_client=llm_mock)

    now = datetime.now(tz=UTC)
    wm = WorkingMemory(
        projekt_id="p-fill",
        aktive_phase=Projektphase.exploration,
        aktiver_modus="exploration",
        phasenstatus=Phasenstatus.in_progress,
        letzte_aenderung=now,
    )
    context = ModeContext(
        projekt_id="p-fill",
        aktive_phase=Projektphase.exploration,
        aktiver_modus="exploration",
        exploration_artifact=ExplorationArtifact(slots=slots),
        structure_artifact=StructureArtifact(),
        algorithm_artifact=AlgorithmArtifact(),
        working_memory=wm,
        dialog_history=[],
        artifact_template=EXPLORATION_TEMPLATE,
    )

    output = await mode.call(context)

    # All 9 Pflicht-Slots are vollstaendig → phase_complete (triggers Moderator)
    assert output.phasenstatus == Phasenstatus.phase_complete


# ---------------------------------------------------------------------------
# Test: current user message is included in messages sent to LLM (regression)
# ---------------------------------------------------------------------------


async def test_current_user_message_passed_to_llm_on_first_turn() -> None:
    """On the first turn, the user's message must be included in the messages
    passed to LLMClient.complete(). Previously the user turn was appended to
    the dialog history *after* the mode call, so the LLM received an empty
    messages list and generated no content patches.
    """
    db = Database(":memory:")
    repo = ProjectRepository(db)
    project = repo.create("Test")
    _set_exploration_mode(repo, project)
    llm = _make_mock_llm(patches=[])
    orchestrator = _make_orchestrator(repo, llm)

    await orchestrator.process_turn(project.projekt_id, TurnInput(text="Meine Eingabe"))

    call_args = llm.complete.call_args  # type: ignore[attr-defined]
    messages: list[dict[str, str]] = call_args.kwargs.get("messages") or call_args.args[1]
    user_messages = [m for m in messages if m.get("role") == "user"]

    assert len(user_messages) >= 1, (
        "LLM must receive at least one user message — "
        "the current user input must be in messages before the mode is called"
    )
    assert any("Meine Eingabe" in str(m.get("content", "")) for m in user_messages), (
        "Current user text must appear in messages passed to LLM"
    )
    db.close()


# ---------------------------------------------------------------------------
# Test: _build_slot_status shows 'leer' for uninitialized slots (regression)
# ---------------------------------------------------------------------------


def test_build_slot_status_shows_leer_for_uninitialized_slots() -> None:
    """Pflicht-Slots not yet present in the artifact must appear as '[leer]' in
    the slot status string — not as 'nicht initialisiert' or similar. This
    ensures the LLM does not see a contradiction when the prompt says
    'use replace on all sub-fields' but slots appear non-existent.
    """
    from datetime import datetime

    from artifacts.models import (
        AlgorithmArtifact,
        ExplorationArtifact,
        Phasenstatus,
        Projektphase,
        StructureArtifact,
    )
    from artifacts.template_schema import EXPLORATION_TEMPLATE
    from core.working_memory import WorkingMemory
    from modes.base import ModeContext
    from modes.exploration import _build_slot_status

    wm = WorkingMemory(
        projekt_id="test",
        aktive_phase=Projektphase.exploration,
        aktiver_modus="exploration",
        phasenstatus=Phasenstatus.in_progress,
        letzte_aenderung=datetime.now(tz=UTC),
    )
    context = ModeContext(
        projekt_id="test",
        aktive_phase=Projektphase.exploration,
        aktiver_modus="exploration",
        exploration_artifact=ExplorationArtifact(),  # empty — no slots yet
        structure_artifact=StructureArtifact(),
        algorithm_artifact=AlgorithmArtifact(),
        working_memory=wm,
        dialog_history=[],
        artifact_template=EXPLORATION_TEMPLATE,
    )
    status = _build_slot_status(context)

    assert "nicht initialisiert" not in status, (
        "_build_slot_status must not use 'nicht initialisiert' — use 'leer' instead"
    )
    assert "LEER" in status or "leer" in status, (
        "Uninitialized Pflicht-Slots must appear as 'leer'/'LEER' in the slot status string"
    )
    # All 9 Pflicht-Slots must be listed by their German title
    for titel in (
        "Prozessauslöser",
        "Prozessziel",
        "Prozessbeschreibung",
        "Scope",
        "Beteiligte Systeme",
        "Umgebung",
        "Randbedingungen",
        "Ausnahmen",
        "Prozesszusammenfassung",
    ):
        assert titel in status, f"Pflicht-Slot '{titel}' missing from slot status"
    # Verify count: 9 lines expected
    lines = [line for line in status.splitlines() if line.strip()]
    assert len(lines) == 9, f"Expected 9 slot lines, got {len(lines)}"


async def test_output_validator_rejects_invalid_path() -> None:
    """Mock LLM returns patch with invalid path → TurnOutput.error is set."""
    db = Database(":memory:")
    repo = ProjectRepository(db)
    project = repo.create("Test")
    _set_exploration_mode(repo, project)
    llm = _make_invalid_path_llm()
    orchestrator = _make_orchestrator(repo, llm)

    result = await orchestrator.process_turn(project.projekt_id, TurnInput(text="Hallo"))

    # The init patches (9 Pflicht-Slots) are combined with the invalid LLM patch.
    # The validator should reject the combined patches because of the invalid path.
    assert result.error is not None
    assert "Kontrakt" in result.error or "ungültig" in result.error.lower()

    # Artifact should be unchanged (no patches applied)
    reloaded = repo.load(project.projekt_id)
    assert reloaded.exploration_artifact.slots == {}
    db.close()


# ---------------------------------------------------------------------------
# Test: nearing_completion promotes to phase_complete when LLM has no new content
# ---------------------------------------------------------------------------


async def test_nearing_completion_escalates_to_phase_complete() -> None:
    """When all slots are teilweise and LLM returns no content patches,
    phase_complete should be emitted so the Moderator can propose transition."""
    from artifacts.models import CompletenessStatus, ExplorationSlot
    from modes.exploration import PFLICHT_SLOTS

    db = Database(":memory:")
    repo = ProjectRepository(db)
    project = repo.create("Test")
    _set_exploration_mode(repo, project)

    # Pre-fill all 9 slots with teilweise status (simulating LLM that never
    # sets vollstaendig). Bump version so save() actually writes the new state.
    for slot_id, titel in PFLICHT_SLOTS.items():
        project.exploration_artifact.slots[slot_id] = ExplorationSlot(
            slot_id=slot_id,
            titel=titel,
            inhalt=f"Inhalt für {titel}",
            completeness_status=CompletenessStatus.teilweise,
        )
    project.exploration_artifact.version += 1
    repo.save(project)

    # LLM returns no content patches (user said "I'm done")
    llm = _make_mock_llm(
        nutzeraeusserung="Alles klar, wir können weitermachen.",
        patches=[],
    )
    orchestrator = _make_orchestrator(repo, llm)
    result = await orchestrator.process_turn(
        project.projekt_id, TurnInput(text="Mir fällt nichts mehr ein")
    )

    # Should escalate to moderator via phase_complete
    assert result.error is None
    reloaded = repo.load(project.projekt_id)
    assert reloaded.aktiver_modus == "moderator"
    assert "phase_complete" in result.flags
    db.close()
