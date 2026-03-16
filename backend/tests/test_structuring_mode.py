"""Tests for StructuringMode — multi-turn mocked dialog (Story 08-03).

All tests use a mocked LLMClient — no live API calls.
Tests verify: stub fallback, patch generation, phase status computation,
exploration context injection, prozesszusammenfassung, and error propagation.
"""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from artifacts.models import (
    AlgorithmArtifact,
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
from core.working_memory import WorkingMemory
from llm.base import LLMClient, LLMResponse
from modes.base import Flag, ModeContext
from modes.structuring import StructuringMode, _apply_guardrails

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_context(
    schritte: dict[str, Strukturschritt] | None = None,
    exploration_slots: dict[str, ExplorationSlot] | None = None,
    prozesszusammenfassung: str = "",
) -> ModeContext:
    """Build a minimal ModeContext for structuring tests."""
    if exploration_slots is None:
        exploration_slots = {
            "prozessziel": ExplorationSlot(
                slot_id="prozessziel",
                titel="Prozessziel",
                inhalt="Reisekosten abrechnen",
                completeness_status=CompletenessStatus.vollstaendig,
            ),
        }
    wm = WorkingMemory(
        projekt_id="p1",
        aktive_phase=Projektphase.strukturierung,
        aktiver_modus="structuring",
        phasenstatus=Phasenstatus.in_progress,
        letzte_aenderung=datetime.now(tz=UTC),
    )
    return ModeContext(
        projekt_id="p1",
        aktive_phase=Projektphase.strukturierung,
        aktiver_modus="structuring",
        exploration_artifact=ExplorationArtifact(slots=exploration_slots or {}),
        structure_artifact=StructureArtifact(
            schritte=schritte or {},
            prozesszusammenfassung=prozesszusammenfassung,
        ),
        algorithm_artifact=AlgorithmArtifact(),
        working_memory=wm,
        dialog_history=[{"role": "user", "inhalt": "Lass uns den Prozess strukturieren."}],
    )


def _make_schritt(
    sid: str,
    titel: str = "Schritt",
    typ: Strukturschritttyp = Strukturschritttyp.aktion,
    reihenfolge: int = 1,
    status: CompletenessStatus = CompletenessStatus.leer,
) -> Strukturschritt:
    return Strukturschritt(
        schritt_id=sid,
        titel=titel,
        typ=typ,
        beschreibung="Test",
        reihenfolge=reihenfolge,
        completeness_status=status,
        algorithmus_status=AlgorithmusStatus.ausstehend,
    )


def _make_mock_llm(
    nutzeraeusserung: str = "Ich habe den ersten Schritt identifiziert.",
    patches: list[dict] | None = None,  # type: ignore[type-arg]
    phasenstatus: str = "in_progress",
) -> LLMClient:
    """Create a mock LLMClient returning a valid apply_patches response."""
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
async def test_structuring_stub_without_llm() -> None:
    """Without LLM client, returns stub message, empty patches, in_progress."""
    mode = StructuringMode(llm_client=None)
    ctx = _make_context()
    result = await mode.call(ctx)

    assert "Kein LLM-Client" in result.nutzeraeusserung
    assert result.patches == []
    assert result.phasenstatus == Phasenstatus.in_progress


@pytest.mark.asyncio
async def test_structuring_single_turn_adds_schritt() -> None:
    """Mock LLM returns a single add patch for /schritte/s1 — verify ModeOutput."""
    schritt_value = {
        "schritt_id": "s1",
        "titel": "Formular öffnen",
        "typ": "aktion",
        "beschreibung": "Nutzer öffnet das Reisekostenformular",
        "reihenfolge": 1,
        "nachfolger": ["s2"],
        "algorithmus_ref": [],
        "completeness_status": "teilweise",
        "algorithmus_status": "ausstehend",
    }
    patches = [{"op": "add", "path": "/schritte/s1", "value": schritt_value}]
    mock_llm = _make_mock_llm(patches=patches)

    mode = StructuringMode(llm_client=mock_llm)
    ctx = _make_context()
    result = await mode.call(ctx)

    assert len(result.patches) == 1
    assert result.patches[0]["op"] == "add"
    assert result.patches[0]["path"] == "/schritte/s1"
    assert result.patches[0]["value"]["titel"] == "Formular öffnen"
    assert result.patches[0]["value"]["typ"] == "aktion"


@pytest.mark.asyncio
async def test_structuring_multi_turn_builds_artifact() -> None:
    """Simulate 3 turns — verify patches contain steps with correct types."""
    # Turn 1: add two aktion steps
    patches_t1 = [
        {
            "op": "add",
            "path": "/schritte/s1",
            "value": {
                "schritt_id": "s1",
                "titel": "Antrag erstellen",
                "typ": "aktion",
                "beschreibung": "Erstelle Reisekostenantrag",
                "reihenfolge": 1,
                "nachfolger": ["s2"],
                "algorithmus_ref": [],
                "completeness_status": "teilweise",
                "algorithmus_status": "ausstehend",
            },
        },
        {
            "op": "add",
            "path": "/schritte/s2",
            "value": {
                "schritt_id": "s2",
                "titel": "Belege prüfen",
                "typ": "aktion",
                "beschreibung": "Prüfung der eingereichten Belege",
                "reihenfolge": 2,
                "nachfolger": ["s3"],
                "algorithmus_ref": [],
                "completeness_status": "teilweise",
                "algorithmus_status": "ausstehend",
            },
        },
    ]
    mock_llm = _make_mock_llm(patches=patches_t1)
    mode = StructuringMode(llm_client=mock_llm)
    ctx = _make_context()
    result = await mode.call(ctx)

    assert len(result.patches) == 2
    assert result.patches[0]["value"]["typ"] == "aktion"
    assert result.patches[1]["value"]["typ"] == "aktion"

    # Turn 2: add a decision point
    patches_t2 = [
        {
            "op": "add",
            "path": "/schritte/s3",
            "value": {
                "schritt_id": "s3",
                "titel": "Betrag prüfen",
                "typ": "entscheidung",
                "beschreibung": "Ist der Betrag über 500€?",
                "reihenfolge": 3,
                "nachfolger": ["s4", "s5"],
                "bedingung": "Betrag > 500€",
                "algorithmus_ref": [],
                "completeness_status": "teilweise",
                "algorithmus_status": "ausstehend",
            },
        },
    ]
    mock_llm2 = _make_mock_llm(patches=patches_t2)
    mode2 = StructuringMode(llm_client=mock_llm2)
    result2 = await mode2.call(ctx)

    assert result2.patches[0]["value"]["typ"] == "entscheidung"
    assert result2.patches[0]["value"]["bedingung"] == "Betrag > 500€"


@pytest.mark.asyncio
async def test_structuring_decision_has_bedingung() -> None:
    """When LLM adds a step with typ=entscheidung, bedingung must be present."""
    patches = [
        {
            "op": "add",
            "path": "/schritte/d1",
            "value": {
                "schritt_id": "d1",
                "titel": "Genehmigung erforderlich?",
                "typ": "entscheidung",
                "beschreibung": "Entscheide ob Genehmigung nötig",
                "reihenfolge": 1,
                "nachfolger": ["s2", "s3"],
                "bedingung": "Betrag > 100€",
                "algorithmus_ref": [],
                "completeness_status": "teilweise",
                "algorithmus_status": "ausstehend",
            },
        },
    ]
    mock_llm = _make_mock_llm(patches=patches)
    mode = StructuringMode(llm_client=mock_llm)
    ctx = _make_context()
    result = await mode.call(ctx)

    value = result.patches[0]["value"]
    assert value["typ"] == "entscheidung"
    assert value["bedingung"] == "Betrag > 100€"
    assert len(value["nachfolger"]) == 2


@pytest.mark.asyncio
async def test_structuring_phase_complete_when_llm_signals() -> None:
    """When LLM says phase_complete and schritte exist, mode emits Flag.phase_complete."""
    schritte = {
        "s1": _make_schritt("s1", status=CompletenessStatus.nutzervalidiert),
        "s2": _make_schritt("s2", reihenfolge=2, status=CompletenessStatus.nutzervalidiert),
    }
    mock_llm = _make_mock_llm(phasenstatus="phase_complete")
    mode = StructuringMode(llm_client=mock_llm)
    ctx = _make_context(schritte=schritte)
    result = await mode.call(ctx)

    assert result.phasenstatus == Phasenstatus.phase_complete
    assert Flag.phase_complete in result.flags


@pytest.mark.asyncio
async def test_structuring_in_progress_when_no_schritte() -> None:
    """When structure artifact has no schritte, returns in_progress."""
    mock_llm = _make_mock_llm()
    mode = StructuringMode(llm_client=mock_llm)
    ctx = _make_context(schritte={})
    result = await mode.call(ctx)

    assert result.phasenstatus == Phasenstatus.in_progress
    assert Flag.phase_complete not in result.flags


@pytest.mark.asyncio
async def test_structuring_exploration_artifact_in_context() -> None:
    """Verify the system prompt passed to LLM contains exploration artifact content."""
    mock_llm = _make_mock_llm()
    mode = StructuringMode(llm_client=mock_llm)
    ctx = _make_context()
    await mode.call(ctx)

    # Check that complete() was called and the system prompt contains exploration content
    call_args = mock_llm.complete.call_args  # type: ignore[attr-defined]
    system_prompt = call_args.kwargs.get("system") or call_args.args[0]
    assert "Reisekosten abrechnen" in system_prompt
    assert "Prozessziel" in system_prompt


@pytest.mark.asyncio
async def test_structuring_prozesszusammenfassung_patch() -> None:
    """LLM can emit a replace patch on /prozesszusammenfassung."""
    patches = [
        {
            "op": "replace",
            "path": "/prozesszusammenfassung",
            "value": "Dieser Prozess beschreibt die Reisekostenabrechnung.",
        },
    ]
    mock_llm = _make_mock_llm(patches=patches)
    mode = StructuringMode(llm_client=mock_llm)
    ctx = _make_context()
    result = await mode.call(ctx)

    assert len(result.patches) == 1
    assert result.patches[0]["path"] == "/prozesszusammenfassung"
    assert "Reisekostenabrechnung" in result.patches[0]["value"]


@pytest.mark.asyncio
async def test_structuring_llm_called_with_tool_choice() -> None:
    """Verify the LLM is called with tool_choice forcing apply_patches (SDD 6.5.2)."""
    mock_llm = _make_mock_llm()
    mode = StructuringMode(llm_client=mock_llm)
    ctx = _make_context()
    await mode.call(ctx)

    call_kwargs = mock_llm.complete.call_args.kwargs  # type: ignore[attr-defined]
    assert call_kwargs["tool_choice"] == {"type": "tool", "name": "apply_patches"}
    assert len(call_kwargs["tools"]) == 1
    assert call_kwargs["tools"][0]["name"] == "apply_patches"


@pytest.mark.asyncio
async def test_structuring_error_on_llm_failure() -> None:
    """When LLM client raises an error, the mode propagates it (Rule T-6)."""
    mock_llm = AsyncMock(spec=LLMClient)
    mock_llm.complete.side_effect = RuntimeError("LLM API timeout nach 30s")

    mode = StructuringMode(llm_client=mock_llm)
    ctx = _make_context()

    with pytest.raises(RuntimeError, match="LLM API timeout"):
        await mode.call(ctx)


# ---------------------------------------------------------------------------
# Unit tests for _compute_phasenstatus
# ---------------------------------------------------------------------------


def test_guardrail_blocks_phase_complete_without_schritte() -> None:
    """Guardrail blocks phase_complete if no Strukturschritte exist."""
    ctx = _make_context(schritte={})
    assert _apply_guardrails(Phasenstatus.phase_complete, ctx) == Phasenstatus.in_progress


def test_guardrail_blocks_phase_complete_with_leer_schritte() -> None:
    """Guardrail downgrades phase_complete to nearing_completion if any schritt is leer."""
    schritte = {
        "s1": _make_schritt("s1", status=CompletenessStatus.vollstaendig),
        "s2": _make_schritt("s2", reihenfolge=2, status=CompletenessStatus.leer),
    }
    ctx = _make_context(schritte=schritte)
    assert _apply_guardrails(Phasenstatus.phase_complete, ctx) == Phasenstatus.nearing_completion


def test_guardrail_allows_phase_complete_when_schritte_filled() -> None:
    """Guardrail passes through phase_complete when schritte exist and none are leer."""
    schritte = {
        "s1": _make_schritt("s1", status=CompletenessStatus.teilweise),
        "s2": _make_schritt("s2", reihenfolge=2, status=CompletenessStatus.vollstaendig),
    }
    ctx = _make_context(schritte=schritte)
    assert _apply_guardrails(Phasenstatus.phase_complete, ctx) == Phasenstatus.phase_complete


def test_guardrail_passes_through_in_progress() -> None:
    """Guardrail does not modify in_progress from LLM."""
    schritte = {
        "s1": _make_schritt("s1", status=CompletenessStatus.teilweise),
    }
    ctx = _make_context(schritte=schritte)
    assert _apply_guardrails(Phasenstatus.in_progress, ctx) == Phasenstatus.in_progress
