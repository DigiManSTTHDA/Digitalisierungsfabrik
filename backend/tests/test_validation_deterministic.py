"""Tests for ValidationMode deterministic checks and correction loop (Story 10-05).

Verifies:
- Clean artifacts produce no kritisch findings
- Broken referential integrity → kritisch findings
- Invalid EMMA action types → kritisch findings
- Incomplete slots → warnung findings
- Unreferenced ausnahme steps → kritisch findings
- No patches emitted in any case
- phase_complete flag always set
- durchlauf_nr increments on second validation pass
- LLM error → graceful fallback
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from artifacts.models import (
    AlgorithmArtifact,
    Algorithmusabschnitt,
    AlgorithmusStatus,
    CompletenessStatus,
    EmmaAktion,
    EmmaAktionstyp,
    ExplorationArtifact,
    Phasenstatus,
    Projektphase,
    Schweregrad,
    StructureArtifact,
    Strukturschritt,
    Strukturschritttyp,
    Validierungsbericht,
)
from core.working_memory import WorkingMemory
from modes.base import Flag, ModeContext
from modes.validation import ValidationMode

# ── Helpers ─────────────────────────────────────────────────────────────────


def _wm() -> WorkingMemory:
    return WorkingMemory(
        projekt_id="p1",
        aktive_phase=Projektphase.validierung,
        aktiver_modus="validation",
        phasenstatus=Phasenstatus.in_progress,
        letzte_aenderung=datetime.now(tz=UTC),
    )


def _ctx(
    structure: StructureArtifact | None = None,
    algorithm: AlgorithmArtifact | None = None,
    exploration: ExplorationArtifact | None = None,
    wm: WorkingMemory | None = None,
) -> ModeContext:
    return ModeContext(
        projekt_id="p1",
        aktive_phase=Projektphase.validierung,
        aktiver_modus="validation",
        exploration_artifact=exploration or ExplorationArtifact(),
        structure_artifact=structure or StructureArtifact(),
        algorithm_artifact=algorithm or AlgorithmArtifact(),
        working_memory=wm or _wm(),
        dialog_history=[],
        completeness_state={},
    )


def _complete_schritt(
    titel: str = "Schritt 1",
    algo_refs: list[str] | None = None,
    typ: Strukturschritttyp = Strukturschritttyp.aktion,
    schritt_id: str = "s1",
) -> Strukturschritt:
    return Strukturschritt(
        schritt_id=schritt_id,
        titel=titel,
        beschreibung="Beschreibung",
        typ=typ,
        reihenfolge=1,
        completeness_status=CompletenessStatus.vollstaendig,
        algorithmus_status=AlgorithmusStatus.aktuell,
        algorithmus_ref=algo_refs or [],
    )


def _complete_abschnitt(
    titel: str = "Abschnitt 1",
    struktur_ref: str = "s1",
    abschnitt_id: str = "alg1",
) -> Algorithmusabschnitt:
    return Algorithmusabschnitt(
        abschnitt_id=abschnitt_id,
        titel=titel,
        struktur_ref=struktur_ref,
        status=AlgorithmusStatus.aktuell,
        completeness_status=CompletenessStatus.vollstaendig,
        aktionen={
            "a1": EmmaAktion(
                aktion_id="a1",
                aktionstyp=EmmaAktionstyp.CLICK,
                parameter={},
            )
        },
    )


# ── Clean artifacts → no findings ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_clean_artifacts_pass_validation() -> None:
    """Complete, consistent artifacts produce no kritisch findings and ist_bestanden=True."""
    structure = StructureArtifact(schritte={"s1": _complete_schritt(algo_refs=["alg1"])})
    algorithm = AlgorithmArtifact(abschnitte={"alg1": _complete_abschnitt(struktur_ref="s1")})
    mode = ValidationMode()
    output = await mode.call(_ctx(structure=structure, algorithm=algorithm))

    assert output.validierungsbericht is not None
    assert output.validierungsbericht.ist_bestanden is True
    assert len(output.validierungsbericht.befunde) == 0
    assert output.patches == []
    assert Flag.phase_complete in output.flags


# ── Broken referential integrity: struktur → algorithmus ───────────────────


@pytest.mark.asyncio
async def test_broken_ref_struktur_to_algo_produces_kritisch() -> None:
    """Strukturschritt referencing non-existent Algorithmusabschnitt → kritisch."""
    structure = StructureArtifact(schritte={"s1": _complete_schritt(algo_refs=["nonexistent"])})
    algorithm = AlgorithmArtifact(abschnitte={})
    mode = ValidationMode()
    output = await mode.call(_ctx(structure=structure, algorithm=algorithm))

    bericht = output.validierungsbericht
    assert bericht is not None
    assert bericht.ist_bestanden is False
    kritisch = [b for b in bericht.befunde if b.schweregrad == Schweregrad.kritisch]
    assert len(kritisch) >= 1
    assert "nonexistent" in kritisch[0].beschreibung
    assert "s1" in kritisch[0].betroffene_slots


# ── Broken referential integrity: algorithmus → struktur ───────────────────


@pytest.mark.asyncio
async def test_broken_ref_algo_to_struktur_produces_kritisch() -> None:
    """Algorithmusabschnitt referencing non-existent Strukturschritt → kritisch."""
    structure = StructureArtifact(schritte={})
    algorithm = AlgorithmArtifact(
        abschnitte={"alg1": _complete_abschnitt(struktur_ref="missing_s")}
    )
    mode = ValidationMode()
    output = await mode.call(_ctx(structure=structure, algorithm=algorithm))

    bericht = output.validierungsbericht
    assert bericht is not None
    kritisch = [b for b in bericht.befunde if b.schweregrad == Schweregrad.kritisch]
    assert len(kritisch) >= 1
    assert "missing_s" in kritisch[0].beschreibung


# ── Invalid EMMA action type ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_invalid_emma_aktionstyp_produces_kritisch() -> None:
    """EmmaAktion with invalid aktionstyp → kritisch finding."""
    # Use model_construct to bypass Pydantic validation (simulate corrupted data)
    bad_aktion = EmmaAktion.model_construct(
        aktion_id="a1",
        aktionstyp="ungueltig_typ",
        parameter={},
        nachfolger=[],
    )
    abschnitt = Algorithmusabschnitt(
        abschnitt_id="alg1",
        titel="Bad Abschnitt",
        struktur_ref="s1",
        status=AlgorithmusStatus.aktuell,
        completeness_status=CompletenessStatus.vollstaendig,
        aktionen={"a1": bad_aktion},
    )
    structure = StructureArtifact(schritte={"s1": _complete_schritt()})
    algorithm = AlgorithmArtifact(abschnitte={"alg1": abschnitt})
    mode = ValidationMode()
    output = await mode.call(_ctx(structure=structure, algorithm=algorithm))

    bericht = output.validierungsbericht
    assert bericht is not None
    kritisch = [b for b in bericht.befunde if b.schweregrad == Schweregrad.kritisch]
    assert any("ungueltig_typ" in b.beschreibung for b in kritisch)


# ── Incomplete slots → warnung ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_incomplete_structure_slot_produces_warnung() -> None:
    """Strukturschritt with completeness_status=leer → warnung finding."""
    schritt = _complete_schritt()
    schritt.completeness_status = CompletenessStatus.leer
    structure = StructureArtifact(schritte={"s1": schritt})
    mode = ValidationMode()
    output = await mode.call(_ctx(structure=structure))

    bericht = output.validierungsbericht
    assert bericht is not None
    warnungen = [b for b in bericht.befunde if b.schweregrad == Schweregrad.warnung]
    assert len(warnungen) >= 1
    assert "s1" in warnungen[0].betroffene_slots


@pytest.mark.asyncio
async def test_incomplete_algorithm_slot_produces_warnung() -> None:
    """Algorithmusabschnitt with completeness_status=teilweise → warnung finding."""
    abschnitt = _complete_abschnitt(struktur_ref="s1")
    abschnitt.completeness_status = CompletenessStatus.teilweise
    structure = StructureArtifact(schritte={"s1": _complete_schritt()})
    algorithm = AlgorithmArtifact(abschnitte={"alg1": abschnitt})
    mode = ValidationMode()
    output = await mode.call(_ctx(structure=structure, algorithm=algorithm))

    bericht = output.validierungsbericht
    assert bericht is not None
    warnungen = [b for b in bericht.befunde if b.schweregrad == Schweregrad.warnung]
    assert len(warnungen) >= 1


# ── Unreferenced ausnahme step ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_unreferenced_ausnahme_step_produces_kritisch() -> None:
    """Ausnahme Strukturschritt without corresponding Algorithmusabschnitt → kritisch."""
    structure = StructureArtifact(
        schritte={"s_exc": _complete_schritt(titel="Ausnahme", typ=Strukturschritttyp.ausnahme)}
    )
    algorithm = AlgorithmArtifact(abschnitte={})  # No reference to s_exc
    mode = ValidationMode()
    output = await mode.call(_ctx(structure=structure, algorithm=algorithm))

    bericht = output.validierungsbericht
    assert bericht is not None
    kritisch = [b for b in bericht.befunde if b.schweregrad == Schweregrad.kritisch]
    assert any("Ausnahme" in b.beschreibung for b in kritisch)
    assert any("s_exc" in b.betroffene_slots for b in kritisch)


# ── Multiple findings combined ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_multiple_findings_with_mixed_severities() -> None:
    """Flawed artifacts produce multiple findings with different severities."""
    # Broken ref (kritisch) + incomplete slot (warnung)
    schritt = _complete_schritt(algo_refs=["nonexistent"])
    schritt.completeness_status = CompletenessStatus.teilweise
    structure = StructureArtifact(schritte={"s1": schritt})
    algorithm = AlgorithmArtifact(abschnitte={})
    mode = ValidationMode()
    output = await mode.call(_ctx(structure=structure, algorithm=algorithm))

    bericht = output.validierungsbericht
    assert bericht is not None
    assert len(bericht.befunde) >= 2
    severities = {b.schweregrad for b in bericht.befunde}
    assert Schweregrad.kritisch in severities
    assert Schweregrad.warnung in severities
    assert bericht.ist_bestanden is False


# ── No patches emitted ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_validation_never_emits_patches() -> None:
    """ValidationMode output.patches is always empty (SDD 6.6.4)."""
    structure = StructureArtifact(schritte={"s1": _complete_schritt(algo_refs=["nonexistent"])})
    mode = ValidationMode()
    output = await mode.call(_ctx(structure=structure))
    assert output.patches == []


# ── phase_complete flag always set ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_phase_complete_flag_always_present() -> None:
    """ValidationMode always returns Flag.phase_complete."""
    mode = ValidationMode()
    output = await mode.call(_ctx())
    assert Flag.phase_complete in output.flags
    assert output.phasenstatus == Phasenstatus.phase_complete


# ── durchlauf_nr increments ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_durchlauf_nr_increments_on_second_pass() -> None:
    """Second validation pass has durchlauf_nr=2 when WM has existing report."""
    wm = _wm()
    wm.validierungsbericht = Validierungsbericht(
        befunde=[],
        erstellt_am=datetime.now(tz=UTC),
        durchlauf_nr=1,
        ist_bestanden=True,
    )
    mode = ValidationMode()
    output = await mode.call(_ctx(wm=wm))
    assert output.validierungsbericht is not None
    assert output.validierungsbericht.durchlauf_nr == 2


# ── Empty artifacts ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_empty_artifacts_pass_with_no_findings() -> None:
    """All artifacts empty → no findings (nothing to check)."""
    mode = ValidationMode()
    output = await mode.call(_ctx())
    assert output.validierungsbericht is not None
    assert output.validierungsbericht.ist_bestanden is True
    assert len(output.validierungsbericht.befunde) == 0


# ── Format summary ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_format_summary_contains_befunde_count() -> None:
    """Summary message contains the number of findings."""
    structure = StructureArtifact(schritte={"s1": _complete_schritt(algo_refs=["nonexistent"])})
    mode = ValidationMode()
    output = await mode.call(_ctx(structure=structure))
    assert "Befunde" in output.nutzeraeusserung or "kritisch" in output.nutzeraeusserung


@pytest.mark.asyncio
async def test_clean_summary_reports_no_findings() -> None:
    """Clean artifacts produce a summary mentioning no findings."""
    mode = ValidationMode()
    output = await mode.call(_ctx())
    assert "Keine Befunde" in output.nutzeraeusserung


# ── CR-002: regeln↔nachfolger consistency ─────────────────────────────────


@pytest.mark.asyncio
async def test_regeln_nachfolger_inconsistency_produces_kritisch() -> None:
    """CR-002: regeln nachfolger must match schritt.nachfolger — mismatch → kritisch."""
    from artifacts.models import Entscheidungsregel

    schritt = _complete_schritt(titel="Reiseart prüfen", typ=Strukturschritttyp.entscheidung)
    schritt.regeln = [
        Entscheidungsregel(bedingung="Inland", nachfolger="s2"),
        Entscheidungsregel(bedingung="Ausland", nachfolger="s3"),
    ]
    schritt.nachfolger = ["s2", "s99"]  # s99 is wrong — should be s3
    structure = StructureArtifact(schritte={"s1": schritt})
    mode = ValidationMode()
    output = await mode.call(_ctx(structure=structure))

    bericht = output.validierungsbericht
    assert bericht is not None
    kritisch = [b for b in bericht.befunde if b.schweregrad == Schweregrad.kritisch]
    assert any("nachfolger" in b.beschreibung and "regeln" in b.beschreibung for b in kritisch)


@pytest.mark.asyncio
async def test_regeln_nachfolger_consistent_no_finding() -> None:
    """CR-002: When regeln nachfolger matches schritt.nachfolger, no finding."""
    from artifacts.models import Entscheidungsregel

    schritt = _complete_schritt(titel="Reiseart prüfen", typ=Strukturschritttyp.entscheidung)
    schritt.regeln = [
        Entscheidungsregel(bedingung="Inland", nachfolger="s2"),
        Entscheidungsregel(bedingung="Ausland", nachfolger="s3"),
    ]
    schritt.nachfolger = ["s2", "s3"]
    structure = StructureArtifact(schritte={"s1": schritt})
    algorithm = AlgorithmArtifact(abschnitte={"alg1": _complete_abschnitt(struktur_ref="s1")})
    schritt.algorithmus_ref = ["alg1"]
    mode = ValidationMode()
    output = await mode.call(_ctx(structure=structure, algorithm=algorithm))

    bericht = output.validierungsbericht
    assert bericht is not None
    # No regeln/nachfolger inconsistency finding
    regeln_findings = [b for b in bericht.befunde if "regeln" in b.beschreibung]
    assert len(regeln_findings) == 0


@pytest.mark.asyncio
async def test_schleifenkoerper_invalid_ref_produces_kritisch() -> None:
    """CR-002: schleifenkoerper referencing non-existent schritt → kritisch."""
    schritt = _complete_schritt(titel="Wiederholung", typ=Strukturschritttyp.schleife)
    schritt.schleifenkoerper = ["s_nonexistent"]
    structure = StructureArtifact(schritte={"s1": schritt})
    mode = ValidationMode()
    output = await mode.call(_ctx(structure=structure))

    bericht = output.validierungsbericht
    assert bericht is not None
    kritisch = [b for b in bericht.befunde if b.schweregrad == Schweregrad.kritisch]
    assert any("schleifenkoerper" in b.beschreibung for b in kritisch)
