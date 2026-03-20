"""Tests for SpecificationMode — multi-turn mocked dialog (Story 09-05).

All tests use a mocked LLMClient — no live API calls.
Tests verify: stub fallback, patch generation, guardrails, system prompt
content, tool_choice, error propagation, and validierungsbericht placeholder.
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from artifacts.models import (
    AlgorithmArtifact,
    Algorithmusabschnitt,
    AlgorithmusStatus,
    CompletenessStatus,
    EmmaAktion,
    EmmaAktionstyp,
    ExplorationArtifact,
    ExplorationSlot,
    Phasenstatus,
    Projektphase,
    StructureArtifact,
    Strukturschritt,
    Strukturschritttyp,
)
from core.working_memory import WorkingMemory
from llm.base import LLMClient, LLMResponse
from modes.base import Flag, ModeContext
from modes.specification import SpecificationMode, _apply_guardrails

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_schritt(
    sid: str,
    titel: str = "Schritt",
    typ: Strukturschritttyp = Strukturschritttyp.aktion,
    reihenfolge: int = 1,
    status: CompletenessStatus = CompletenessStatus.vollstaendig,
) -> Strukturschritt:
    return Strukturschritt(
        schritt_id=sid,
        titel=titel,
        typ=typ,
        beschreibung="Testbeschreibung",
        reihenfolge=reihenfolge,
        completeness_status=status,
        algorithmus_status=AlgorithmusStatus.ausstehend,
    )


def _make_abschnitt(
    aid: str,
    struktur_ref: str,
    completeness: CompletenessStatus = CompletenessStatus.nutzervalidiert,
) -> Algorithmusabschnitt:
    aktion = EmmaAktion(aktion_id="a1", aktionstyp=EmmaAktionstyp.READ)
    return Algorithmusabschnitt(
        abschnitt_id=aid,
        titel=f"Abschnitt {aid}",
        struktur_ref=struktur_ref,
        aktionen={"a1": aktion},
        completeness_status=completeness,
        status=AlgorithmusStatus.aktuell,
    )


def _make_context(
    schritte: dict[str, Strukturschritt] | None = None,
    abschnitte: dict[str, Algorithmusabschnitt] | None = None,
    prozesszusammenfassung: str = "",
) -> ModeContext:
    """Build a minimal ModeContext for specification tests."""
    if schritte is None:
        schritte = {"s1": _make_schritt("s1", titel="Formular öffnen")}

    wm = WorkingMemory(
        projekt_id="p1",
        aktive_phase=Projektphase.spezifikation,
        aktiver_modus="specification",
        phasenstatus=Phasenstatus.in_progress,
        letzte_aenderung=datetime.now(tz=UTC),
    )
    return ModeContext(
        projekt_id="p1",
        aktive_phase=Projektphase.spezifikation,
        aktiver_modus="specification",
        exploration_artifact=ExplorationArtifact(
            slots={
                "prozessziel": ExplorationSlot(
                    slot_id="prozessziel",
                    titel="Prozessziel",
                    inhalt="Reisekosten abrechnen",
                    completeness_status=CompletenessStatus.vollstaendig,
                ),
            }
        ),
        structure_artifact=StructureArtifact(
            schritte=schritte,
            prozesszusammenfassung=prozesszusammenfassung or "Reisekostenprozess",
        ),
        algorithm_artifact=AlgorithmArtifact(abschnitte=abschnitte or {}),
        working_memory=wm,
        dialog_history=[{"role": "user", "inhalt": "Lass uns den Prozess spezifizieren."}],
    )


def _make_mock_llm(
    nutzeraeusserung: str = "Ich spezifiziere den ersten Schritt.",
    patches: list[dict] | None = None,  # type: ignore[type-arg]
    phasenstatus: str = "in_progress",
) -> LLMClient:
    if patches is None:
        patches = []
    mock = AsyncMock(spec=LLMClient)
    mock.complete.return_value = LLMResponse(
        nutzeraeusserung=nutzeraeusserung,
        tool_input={"patches": patches, "phasenstatus": phasenstatus},
    )
    return mock


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_specification_no_llm_client_returns_stub() -> None:
    """None LLM client returns stub message."""
    mode = SpecificationMode(llm_client=None)
    ctx = _make_context()
    result = await mode.call(ctx)

    assert "Kein LLM-Client" in result.nutzeraeusserung
    assert result.patches == []
    assert result.phasenstatus == Phasenstatus.in_progress


@pytest.mark.asyncio
async def test_specification_produces_algorithm_patches() -> None:
    """LLM returns patches that add an Algorithmusabschnitt."""
    abschnitt_value = {
        "abschnitt_id": "ab1",
        "titel": "Formular öffnen",
        "struktur_ref": "s1",
        "aktionen": {
            "a1": {
                "aktion_id": "a1",
                "aktionstyp": "FIND_AND_CLICK",
                "parameter": {"element": "Reisekosten-Button"},
                "nachfolger": ["a2"],
                "emma_kompatibel": True,
            }
        },
        "completeness_status": "teilweise",
        "status": "aktuell",
    }
    patches = [{"op": "add", "path": "/abschnitte/ab1", "value": abschnitt_value}]
    mock_llm = _make_mock_llm(patches=patches)

    mode = SpecificationMode(llm_client=mock_llm)
    ctx = _make_context()
    result = await mode.call(ctx)

    assert len(result.patches) == 1
    assert result.patches[0]["op"] == "add"
    assert result.patches[0]["path"] == "/abschnitte/ab1"
    assert result.patches[0]["value"]["struktur_ref"] == "s1"


@pytest.mark.asyncio
async def test_specification_uses_tool_choice() -> None:
    """Verify tool_choice={"type": "auto"} is passed (allows pure-text responses)."""
    mock_llm = _make_mock_llm()
    mode = SpecificationMode(llm_client=mock_llm)
    ctx = _make_context()
    await mode.call(ctx)

    call_kwargs = mock_llm.complete.call_args.kwargs  # type: ignore[attr-defined]
    assert call_kwargs["tool_choice"] == {"type": "auto"}
    assert len(call_kwargs["tools"]) == 1
    assert call_kwargs["tools"][0]["name"] == "apply_patches"


@pytest.mark.asyncio
async def test_specification_system_prompt_contains_emma_catalog() -> None:
    """System prompt sent to LLM contains EMMA action type listing."""
    mock_llm = _make_mock_llm()
    mode = SpecificationMode(llm_client=mock_llm)
    ctx = _make_context()
    await mode.call(ctx)

    call_args = mock_llm.complete.call_args  # type: ignore[attr-defined]
    system_prompt = call_args.kwargs.get("system", "")
    assert "FIND_AND_CLICK" in system_prompt
    assert "SEND_MAIL" in system_prompt
    assert "DECISION" in system_prompt


@pytest.mark.asyncio
async def test_specification_system_prompt_contains_structure_content() -> None:
    """System prompt includes Structure Artifact read-only content."""
    mock_llm = _make_mock_llm()
    mode = SpecificationMode(llm_client=mock_llm)
    ctx = _make_context()
    await mode.call(ctx)

    call_args = mock_llm.complete.call_args  # type: ignore[attr-defined]
    system_prompt = call_args.kwargs.get("system", "")
    assert "Formular öffnen" in system_prompt
    assert "Reisekostenprozess" in system_prompt


@pytest.mark.asyncio
async def test_specification_system_prompt_contains_operationalisierbarkeit() -> None:
    """System prompt includes the 5 mandatory operationalisierbarkeit questions."""
    mock_llm = _make_mock_llm()
    mode = SpecificationMode(llm_client=mock_llm)
    ctx = _make_context()
    await mode.call(ctx)

    call_args = mock_llm.complete.call_args  # type: ignore[attr-defined]
    system_prompt = call_args.kwargs.get("system", "")
    assert "Welche Aktion?" in system_prompt
    assert "Wie genau?" in system_prompt
    assert "Endzustand?" in system_prompt
    assert "Timeout?" in system_prompt
    assert "Fehlerbehandlung?" in system_prompt


@pytest.mark.asyncio
async def test_specification_guardrail_blocks_no_abschnitte() -> None:
    """When no Algorithmusabschnitte exist, phase_complete is downgraded."""
    mock_llm = _make_mock_llm(phasenstatus="phase_complete")
    mode = SpecificationMode(llm_client=mock_llm)
    ctx = _make_context(abschnitte={})
    result = await mode.call(ctx)

    assert result.phasenstatus == Phasenstatus.nearing_completion
    assert Flag.phase_complete not in result.flags


@pytest.mark.asyncio
async def test_specification_guardrail_blocks_non_validated() -> None:
    """When abschnitte exist but not nutzervalidiert, phase_complete is blocked."""
    abschnitte = {
        "ab1": _make_abschnitt("ab1", "s1", CompletenessStatus.vollstaendig),
    }
    mock_llm = _make_mock_llm(phasenstatus="phase_complete")
    mode = SpecificationMode(llm_client=mock_llm)
    ctx = _make_context(abschnitte=abschnitte)
    result = await mode.call(ctx)

    assert result.phasenstatus == Phasenstatus.nearing_completion
    assert Flag.phase_complete not in result.flags


@pytest.mark.asyncio
async def test_specification_guardrail_allows_phase_complete() -> None:
    """When all Strukturschritte have nutzervalidiert abschnitte, phase_complete passes."""
    abschnitte = {
        "ab1": _make_abschnitt("ab1", "s1", CompletenessStatus.nutzervalidiert),
    }
    mock_llm = _make_mock_llm(phasenstatus="phase_complete")
    mode = SpecificationMode(llm_client=mock_llm)
    ctx = _make_context(abschnitte=abschnitte)
    result = await mode.call(ctx)

    assert result.phasenstatus == Phasenstatus.phase_complete
    assert Flag.phase_complete in result.flags


@pytest.mark.asyncio
async def test_specification_phasenstatus_in_progress() -> None:
    """Normal turn returns in_progress."""
    mock_llm = _make_mock_llm(phasenstatus="in_progress")
    mode = SpecificationMode(llm_client=mock_llm)
    ctx = _make_context()
    result = await mode.call(ctx)

    assert result.phasenstatus == Phasenstatus.in_progress
    assert Flag.phase_complete not in result.flags


@pytest.mark.asyncio
async def test_specification_prompt_has_validierungsbericht_placeholder() -> None:
    """System prompt contains validierungsbericht placeholder (Epic 10 prep)."""
    mock_llm = _make_mock_llm()
    mode = SpecificationMode(llm_client=mock_llm)
    ctx = _make_context()
    await mode.call(ctx)

    call_args = mock_llm.complete.call_args  # type: ignore[attr-defined]
    system_prompt = call_args.kwargs.get("system", "")
    # The placeholder should be in the raw template; after substitution it's empty
    # but the section header "Validierungsbericht" should still be present
    assert "Validierungsbericht" in system_prompt


@pytest.mark.asyncio
async def test_specification_error_on_llm_failure() -> None:
    """LLM error propagates correctly (Rule T-6)."""
    mock_llm = AsyncMock(spec=LLMClient)
    mock_llm.complete.side_effect = RuntimeError("LLM API timeout")

    mode = SpecificationMode(llm_client=mock_llm)
    ctx = _make_context()

    with pytest.raises(RuntimeError, match="LLM API timeout"):
        await mode.call(ctx)


# ---------------------------------------------------------------------------
# Unit tests for _apply_guardrails
# ---------------------------------------------------------------------------


def test_guardrail_blocks_phase_complete_without_abschnitte() -> None:
    """Guardrail blocks phase_complete if no Algorithmusabschnitte exist."""
    ctx = _make_context(abschnitte={})
    result = _apply_guardrails(Phasenstatus.phase_complete, ctx)
    assert result == Phasenstatus.nearing_completion


def test_guardrail_blocks_when_schritt_missing_abschnitt() -> None:
    """Guardrail blocks if a Strukturschritt has no corresponding abschnitt."""
    schritte = {
        "s1": _make_schritt("s1"),
        "s2": _make_schritt("s2", reihenfolge=2),
    }
    abschnitte = {
        "ab1": _make_abschnitt("ab1", "s1", CompletenessStatus.nutzervalidiert),
        # s2 has no abschnitt
    }
    ctx = _make_context(schritte=schritte, abschnitte=abschnitte)
    result = _apply_guardrails(Phasenstatus.phase_complete, ctx)
    assert result == Phasenstatus.nearing_completion


def test_guardrail_passes_in_progress_through() -> None:
    """Guardrail does not modify in_progress from LLM."""
    ctx = _make_context()
    result = _apply_guardrails(Phasenstatus.in_progress, ctx)
    assert result == Phasenstatus.in_progress


def test_guardrail_allows_complete_when_all_validated() -> None:
    """Guardrail allows phase_complete when all schritte have validated abschnitte."""
    schritte = {
        "s1": _make_schritt("s1"),
        "s2": _make_schritt("s2", reihenfolge=2),
    }
    abschnitte = {
        "ab1": _make_abschnitt("ab1", "s1", CompletenessStatus.nutzervalidiert),
        "ab2": _make_abschnitt("ab2", "s2", CompletenessStatus.nutzervalidiert),
    }
    ctx = _make_context(schritte=schritte, abschnitte=abschnitte)
    result = _apply_guardrails(Phasenstatus.phase_complete, ctx)
    assert result == Phasenstatus.phase_complete
