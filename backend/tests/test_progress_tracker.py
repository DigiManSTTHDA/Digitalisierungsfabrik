"""Tests für ProgressTracker (S2-T2 / B8 — Spannungsfeld-Aggregation)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from artifacts.models import (
    AlgorithmusStatus,
    CompletenessStatus,
    Phasenstatus,
    Projektphase,
    StructureArtifact,
    Strukturschritt,
    Strukturschritttyp,
)
from core.progress_tracker import update_working_memory
from core.working_memory import WorkingMemory


def _make_wm() -> WorkingMemory:
    return WorkingMemory(
        projekt_id="p1",
        aktive_phase=Projektphase.strukturierung,
        aktiver_modus="structuring",
        phasenstatus=Phasenstatus.in_progress,
        letzte_aenderung=datetime.now(tz=UTC),
    )


def _make_schritt(
    sid: str,
    reihenfolge: int = 1,
    spannungsfeld: str | None = None,
) -> Strukturschritt:
    return Strukturschritt(
        schritt_id=sid,
        titel=f"Schritt {sid}",
        typ=Strukturschritttyp.aktion,
        reihenfolge=reihenfolge,
        completeness_status=CompletenessStatus.vollstaendig,
        algorithmus_status=AlgorithmusStatus.ausstehend,
        spannungsfeld=spannungsfeld,
    )


def test_update_working_memory_no_structure_artifact() -> None:
    """Ohne structure_artifact bleibt spannungsfelder unverändert."""
    wm = _make_wm()
    wm.spannungsfelder = ["existing"]
    result = update_working_memory(wm, Phasenstatus.in_progress, 3, 9)
    assert result.spannungsfelder == ["existing"]


def test_update_working_memory_aggregates_spannungsfelder() -> None:
    """Spannungsfelder aus Strukturschritten werden in WM aggregiert."""
    wm = _make_wm()
    artifact = StructureArtifact(
        schritte={
            "s1": _make_schritt("s1", 1, "Medienbruch: ELO vs. Stempel"),
            "s2": _make_schritt("s2", 2, None),
            "s3": _make_schritt("s3", 3, "Manuelle Doppelerfassung"),
        }
    )
    result = update_working_memory(wm, Phasenstatus.in_progress, 3, 9, artifact)
    assert result.spannungsfelder == ["Medienbruch: ELO vs. Stempel", "Manuelle Doppelerfassung"]


def test_update_working_memory_empty_structure_artifact() -> None:
    """Leeres Strukturartefakt → leere spannungsfelder-Liste."""
    wm = _make_wm()
    wm.spannungsfelder = ["old"]
    result = update_working_memory(wm, Phasenstatus.in_progress, 0, 0, StructureArtifact())
    assert result.spannungsfelder == []


def test_update_working_memory_deduplicates_spannungsfelder() -> None:
    """Identische Spannungsfelder werden dedupliziert."""
    wm = _make_wm()
    artifact = StructureArtifact(
        schritte={
            "s1": _make_schritt("s1", 1, "Medienbruch"),
            "s2": _make_schritt("s2", 2, "Medienbruch"),
        }
    )
    result = update_working_memory(wm, Phasenstatus.in_progress, 2, 2, artifact)
    assert result.spannungsfelder == ["Medienbruch"]


def test_update_working_memory_skips_blank_spannungsfeld() -> None:
    """Leere oder Whitespace-only spannungsfelder werden übersprungen."""
    wm = _make_wm()
    artifact = StructureArtifact(
        schritte={
            "s1": _make_schritt("s1", 1, "  "),
            "s2": _make_schritt("s2", 2, ""),
            "s3": _make_schritt("s3", 3, "Echter Eintrag"),
        }
    )
    result = update_working_memory(wm, Phasenstatus.in_progress, 3, 3, artifact)
    assert result.spannungsfelder == ["Echter Eintrag"]


def test_update_working_memory_updates_slot_counters() -> None:
    """Befuellte und bekannte Slots werden korrekt gesetzt."""
    wm = _make_wm()
    result = update_working_memory(wm, Phasenstatus.nearing_completion, 7, 7)
    assert result.befuellte_slots == 7
    assert result.bekannte_slots == 7
    assert result.phasenstatus == Phasenstatus.nearing_completion
