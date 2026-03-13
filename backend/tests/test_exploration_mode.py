"""Integration tests for full turn through Orchestrator with ExplorationMode (Story 04-08).

All tests use in-memory SQLite and a mocked LLMClient — no live API calls.
Tests verify: Pflicht-Slot initialization, patch application + persistence,
dialog history, and OutputValidator rejection of invalid paths.
"""

from __future__ import annotations

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


# ---------------------------------------------------------------------------
# Test: first turn initializes 8 Pflicht-Slots
# ---------------------------------------------------------------------------


async def test_first_turn_initializes_pflicht_slots() -> None:
    """After the first turn, all 8 Pflicht-Slot IDs must be present."""
    db = Database(":memory:")
    repo = ProjectRepository(db)
    project = repo.create("Test")
    llm = _make_mock_llm()
    orchestrator = _make_orchestrator(repo, llm)

    result = await orchestrator.process_turn(project.projekt_id, TurnInput(text="Hallo"))
    assert result.error is None

    reloaded = repo.load(project.projekt_id)
    slot_ids = set(reloaded.exploration_artifact.slots.keys())

    expected_ids = {
        "prozessausloeser",
        "prozessziel",
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


async def test_output_validator_rejects_invalid_path() -> None:
    """Mock LLM returns patch with invalid path → TurnOutput.error is set."""
    db = Database(":memory:")
    repo = ProjectRepository(db)
    project = repo.create("Test")
    llm = _make_invalid_path_llm()
    orchestrator = _make_orchestrator(repo, llm)

    result = await orchestrator.process_turn(project.projekt_id, TurnInput(text="Hallo"))

    # The init patches (8 Pflicht-Slots) are combined with the invalid LLM patch.
    # The validator should reject the combined patches because of the invalid path.
    assert result.error is not None
    assert "Kontrakt" in result.error or "ungültig" in result.error.lower()

    # Artifact should be unchanged (no patches applied)
    reloaded = repo.load(project.projekt_id)
    assert reloaded.exploration_artifact.slots == {}
    db.close()
