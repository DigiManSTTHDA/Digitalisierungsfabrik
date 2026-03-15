"""Tests for Moderator mode (Story 07-01).

Verifies the Moderator:
- Without LLM: returns deterministic summary
- With mock LLM: calls complete() with correct prompt
- Never produces patches (SDD 6.6.5)
- Receives full context (FR-D-02)
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from artifacts.models import (
    AlgorithmArtifact,
    ExplorationArtifact,
    Phasenstatus,
    Projektphase,
    StructureArtifact,
)
from core.working_memory import WorkingMemory
from llm.base import LLMResponse
from modes.base import ModeContext
from modes.moderator import Moderator


def _make_context(
    phase: Projektphase = Projektphase.exploration,
    vorheriger_modus: str | None = "exploration",
) -> ModeContext:
    wm = WorkingMemory(
        projekt_id="test-id",
        aktive_phase=phase,
        aktiver_modus="moderator",
        vorheriger_modus=vorheriger_modus,
        phasenstatus=Phasenstatus.in_progress,
        befuellte_slots=5,
        bekannte_slots=9,
        letzte_aenderung=datetime.now(tz=UTC),
    )
    return ModeContext(
        projekt_id="test-id",
        aktive_phase=phase,
        aktiver_modus="moderator",
        exploration_artifact=ExplorationArtifact(),
        structure_artifact=StructureArtifact(),
        algorithm_artifact=AlgorithmArtifact(),
        working_memory=wm,
        dialog_history=[
            {"role": "user", "inhalt": "Hallo", "timestamp": "2026-01-01"},
        ],
    )


@pytest.mark.asyncio
async def test_moderator_without_llm_returns_summary() -> None:
    """Moderator without LLM returns a deterministic summary."""
    mod = Moderator(llm_client=None)
    ctx = _make_context()
    output = await mod.call(ctx)
    assert len(output.nutzeraeusserung) > 0
    assert "5/9" in output.nutzeraeusserung
    assert "exploration" in output.nutzeraeusserung


@pytest.mark.asyncio
async def test_moderator_produces_no_patches() -> None:
    """Moderator never produces patches (SDD 6.6.5)."""
    mod = Moderator(llm_client=None)
    ctx = _make_context()
    output = await mod.call(ctx)
    assert output.patches == []


@pytest.mark.asyncio
async def test_moderator_with_mock_llm_calls_complete() -> None:
    """Moderator calls LLM with system prompt containing context."""
    mock_llm = AsyncMock()
    mock_llm.complete = AsyncMock(
        return_value=LLMResponse(
            nutzeraeusserung="Zusammenfassung der Explorationsphase.",
            tool_input={},
        )
    )
    mod = Moderator(llm_client=mock_llm)
    ctx = _make_context()
    output = await mod.call(ctx)

    mock_llm.complete.assert_called_once()
    call_kwargs = mock_llm.complete.call_args
    system_prompt = call_kwargs.kwargs.get("system") or call_kwargs.args[0]
    assert "Moderator" in system_prompt
    assert "exploration" in system_prompt
    assert output.nutzeraeusserung == "Zusammenfassung der Explorationsphase."
    assert output.patches == []


@pytest.mark.asyncio
async def test_moderator_receives_full_context() -> None:
    """Moderator context includes all required fields (FR-D-02)."""
    ctx = _make_context()
    # Verify context has all required fields per FR-D-02 with specific checks
    assert isinstance(ctx.exploration_artifact, ExplorationArtifact)
    assert isinstance(ctx.structure_artifact, StructureArtifact)
    assert isinstance(ctx.algorithm_artifact, AlgorithmArtifact)
    assert ctx.working_memory.projekt_id == "test-id"
    assert ctx.working_memory.befuellte_slots == 5
    assert ctx.working_memory.bekannte_slots == 9
    assert len(ctx.dialog_history) == 1
    assert ctx.dialog_history[0]["role"] == "user"
    assert ctx.dialog_history[0]["inhalt"] == "Hallo"
    # completeness_state defaults to empty dict for ModeContext without completeness calc
    assert ctx.completeness_state == {}
    assert ctx.aktive_phase == Projektphase.exploration
    assert ctx.aktiver_modus == "moderator"


@pytest.mark.asyncio
async def test_moderator_stub_includes_vorheriger_modus() -> None:
    """Stub response mentions the previous mode."""
    mod = Moderator(llm_client=None)
    ctx = _make_context(vorheriger_modus="exploration")
    output = await mod.call(ctx)
    assert "exploration" in output.nutzeraeusserung
