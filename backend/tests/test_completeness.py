"""Tests for CompletenessCalculator (Story 03-03).

Verifies that slot counting and completeness_state mapping are correct
for all three artifact types and combined scenarios.
"""

from __future__ import annotations

import pytest

from artifacts.completeness import CompletenessCalculator
from artifacts.models import (
    AlgorithmArtifact,
    Algorithmusabschnitt,
    AlgorithmusStatus,
    CompletenessStatus,
    ExplorationArtifact,
    ExplorationSlot,
    StructureArtifact,
    Strukturschritt,
    Strukturschritttyp,
)


@pytest.fixture
def calc() -> CompletenessCalculator:
    return CompletenessCalculator()


def _make_slot(slot_id: str, status: CompletenessStatus) -> ExplorationSlot:
    return ExplorationSlot(slot_id=slot_id, titel=slot_id, completeness_status=status)


def _make_schritt(schritt_id: str, status: CompletenessStatus) -> Strukturschritt:
    return Strukturschritt(
        schritt_id=schritt_id,
        titel=schritt_id,
        typ=Strukturschritttyp.aktion,
        reihenfolge=1,
        completeness_status=status,
        algorithmus_status=AlgorithmusStatus.ausstehend,
    )


def _make_abschnitt(abschnitt_id: str, status: CompletenessStatus) -> Algorithmusabschnitt:
    return Algorithmusabschnitt(
        abschnitt_id=abschnitt_id,
        titel=abschnitt_id,
        struktur_ref="s1",
        completeness_status=status,
        status=AlgorithmusStatus.ausstehend,
    )


# ---------------------------------------------------------------------------
# Empty artifacts
# ---------------------------------------------------------------------------


def test_empty_artifacts_returns_zero_counts(calc: CompletenessCalculator) -> None:
    state, befuellte, bekannte = calc.calculate(
        ExplorationArtifact(), StructureArtifact(), AlgorithmArtifact()
    )
    assert state == {}
    assert befuellte == 0
    assert bekannte == 0


# ---------------------------------------------------------------------------
# Exploration artifact
# ---------------------------------------------------------------------------


def test_exploration_leer_not_counted(calc: CompletenessCalculator) -> None:
    exploration = ExplorationArtifact(slots={"s1": _make_slot("s1", CompletenessStatus.leer)})
    _, befuellte, bekannte = calc.calculate(exploration, StructureArtifact(), AlgorithmArtifact())
    assert bekannte == 1
    assert befuellte == 0


def test_exploration_vollstaendig_counted(calc: CompletenessCalculator) -> None:
    exploration = ExplorationArtifact(
        slots={"s1": _make_slot("s1", CompletenessStatus.vollstaendig)}
    )
    _, befuellte, bekannte = calc.calculate(exploration, StructureArtifact(), AlgorithmArtifact())
    assert bekannte == 1
    assert befuellte == 1


def test_exploration_two_slots_one_leer_one_vollstaendig(calc: CompletenessCalculator) -> None:
    exploration = ExplorationArtifact(
        slots={
            "s1": _make_slot("s1", CompletenessStatus.leer),
            "s2": _make_slot("s2", CompletenessStatus.vollstaendig),
        }
    )
    _, befuellte, bekannte = calc.calculate(exploration, StructureArtifact(), AlgorithmArtifact())
    assert bekannte == 2
    assert befuellte == 1


def test_teilweise_counted_as_befuellt(calc: CompletenessCalculator) -> None:
    exploration = ExplorationArtifact(slots={"s1": _make_slot("s1", CompletenessStatus.teilweise)})
    _, befuellte, _ = calc.calculate(exploration, StructureArtifact(), AlgorithmArtifact())
    assert befuellte == 1


def test_nutzervalidiert_counted_as_befuellt(calc: CompletenessCalculator) -> None:
    exploration = ExplorationArtifact(
        slots={"s1": _make_slot("s1", CompletenessStatus.nutzervalidiert)}
    )
    _, befuellte, _ = calc.calculate(exploration, StructureArtifact(), AlgorithmArtifact())
    assert befuellte == 1


# ---------------------------------------------------------------------------
# Structure artifact
# ---------------------------------------------------------------------------


def test_structure_three_steps_mixed(calc: CompletenessCalculator) -> None:
    structure = StructureArtifact(
        schritte={
            "s1": _make_schritt("s1", CompletenessStatus.leer),
            "s2": _make_schritt("s2", CompletenessStatus.teilweise),
            "s3": _make_schritt("s3", CompletenessStatus.nutzervalidiert),
        }
    )
    _, befuellte, bekannte = calc.calculate(ExplorationArtifact(), structure, AlgorithmArtifact())
    assert bekannte == 3
    assert befuellte == 2


# ---------------------------------------------------------------------------
# Algorithm artifact
# ---------------------------------------------------------------------------


def test_algorithm_one_vollstaendig(calc: CompletenessCalculator) -> None:
    algorithm = AlgorithmArtifact(
        abschnitte={"a1": _make_abschnitt("a1", CompletenessStatus.vollstaendig)}
    )
    _, befuellte, bekannte = calc.calculate(ExplorationArtifact(), StructureArtifact(), algorithm)
    assert bekannte == 1
    assert befuellte == 1


# ---------------------------------------------------------------------------
# Combined artifacts
# ---------------------------------------------------------------------------


def test_combined_artifacts_correct_totals(calc: CompletenessCalculator) -> None:
    exploration = ExplorationArtifact(
        slots={
            "e1": _make_slot("e1", CompletenessStatus.vollstaendig),
            "e2": _make_slot("e2", CompletenessStatus.leer),
        }
    )
    structure = StructureArtifact(
        schritte={
            "s1": _make_schritt("s1", CompletenessStatus.teilweise),
        }
    )
    algorithm = AlgorithmArtifact(
        abschnitte={
            "a1": _make_abschnitt("a1", CompletenessStatus.nutzervalidiert),
            "a2": _make_abschnitt("a2", CompletenessStatus.leer),
        }
    )
    _, befuellte, bekannte = calc.calculate(exploration, structure, algorithm)
    assert bekannte == 5  # 2 + 1 + 2
    assert befuellte == 3  # e1(v) + s1(t) + a1(n)


# ---------------------------------------------------------------------------
# completeness_state map
# ---------------------------------------------------------------------------


def test_completeness_state_contains_all_slot_ids(calc: CompletenessCalculator) -> None:
    exploration = ExplorationArtifact(
        slots={"e1": _make_slot("e1", CompletenessStatus.vollstaendig)}
    )
    structure = StructureArtifact(schritte={"s1": _make_schritt("s1", CompletenessStatus.leer)})
    algorithm = AlgorithmArtifact(
        abschnitte={"a1": _make_abschnitt("a1", CompletenessStatus.teilweise)}
    )
    state, _, _ = calc.calculate(exploration, structure, algorithm)
    assert "e1" in state
    assert "s1" in state
    assert "a1" in state
    assert len(state) == 3


def test_completeness_state_maps_leer_correctly(calc: CompletenessCalculator) -> None:
    exploration = ExplorationArtifact(slots={"s1": _make_slot("s1", CompletenessStatus.leer)})
    state, _, _ = calc.calculate(exploration, StructureArtifact(), AlgorithmArtifact())
    assert state["s1"] == CompletenessStatus.leer


def test_completeness_state_maps_vollstaendig_correctly(calc: CompletenessCalculator) -> None:
    exploration = ExplorationArtifact(
        slots={"s1": _make_slot("s1", CompletenessStatus.vollstaendig)}
    )
    state, _, _ = calc.calculate(exploration, StructureArtifact(), AlgorithmArtifact())
    assert state["s1"] == CompletenessStatus.vollstaendig


def test_completeness_state_maps_teilweise_correctly(calc: CompletenessCalculator) -> None:
    exploration = ExplorationArtifact(slots={"s1": _make_slot("s1", CompletenessStatus.teilweise)})
    state, _, _ = calc.calculate(exploration, StructureArtifact(), AlgorithmArtifact())
    assert state["s1"] == CompletenessStatus.teilweise


def test_completeness_state_maps_nutzervalidiert_correctly(calc: CompletenessCalculator) -> None:
    exploration = ExplorationArtifact(
        slots={"s1": _make_slot("s1", CompletenessStatus.nutzervalidiert)}
    )
    state, _, _ = calc.calculate(exploration, StructureArtifact(), AlgorithmArtifact())
    assert state["s1"] == CompletenessStatus.nutzervalidiert


# ---------------------------------------------------------------------------
# Overlapping slot IDs across artifacts
# ---------------------------------------------------------------------------


def test_overlapping_id_later_artifact_overwrites_earlier(calc: CompletenessCalculator) -> None:
    """When exploration and structure share a slot ID, structure's status wins in the state map.

    bekannte_slots counts raw slot totals (2), while completeness_state deduplicates to 1 key.
    befuellte_slots is derived from completeness_state values — so the overwritten status
    (structure = vollstaendig) is what determines whether the slot counts as filled.
    """
    exploration = ExplorationArtifact(slots={"x": _make_slot("x", CompletenessStatus.leer)})
    structure = StructureArtifact(
        schritte={"x": _make_schritt("x", CompletenessStatus.vollstaendig)}
    )
    state, befuellte, bekannte = calc.calculate(exploration, structure, AlgorithmArtifact())

    # completeness_state has one entry — structure's value wins
    assert len(state) == 1
    assert state["x"] == CompletenessStatus.vollstaendig

    # bekannte_slots sums raw lengths including the duplicate
    assert bekannte == 2

    # befuellte_slots is based on state values (1 entry = vollstaendig → counts)
    assert befuellte == 1


# ---------------------------------------------------------------------------
# QA Review: Boundary + Edge Case Tests
# ---------------------------------------------------------------------------


class TestBoundaryCases:
    """Edge cases for CompletenessCalculator identified in QA review."""

    def test_all_empty_artifacts(self, calc: CompletenessCalculator) -> None:
        """Three empty artifacts produce zero slots."""
        state, befuellte, bekannte = calc.calculate(
            ExplorationArtifact(), StructureArtifact(), AlgorithmArtifact()
        )
        assert state == {}
        assert befuellte == 0
        assert bekannte == 0

    def test_many_slots_performance(self, calc: CompletenessCalculator) -> None:
        """Calculator handles 100+ slots without error."""
        slots = {f"s{i}": _make_slot(f"s{i}", CompletenessStatus.teilweise) for i in range(100)}
        exploration = ExplorationArtifact(slots=slots)
        state, befuellte, bekannte = calc.calculate(
            exploration, StructureArtifact(), AlgorithmArtifact()
        )
        assert bekannte == 100
        assert befuellte == 100  # teilweise counts as filled per _FILLED_STATUSES

    def test_mixed_statuses_across_artifacts(self, calc: CompletenessCalculator) -> None:
        """Correct counting with mixed statuses across all three artifact types."""
        exploration = ExplorationArtifact(
            slots={
                "e1": _make_slot("e1", CompletenessStatus.vollstaendig),
                "e2": _make_slot("e2", CompletenessStatus.leer),
            }
        )
        structure = StructureArtifact(
            schritte={
                "s1": _make_schritt("s1", CompletenessStatus.nutzervalidiert),
            }
        )
        algorithm = AlgorithmArtifact(
            abschnitte={
                "a1": _make_abschnitt("a1", CompletenessStatus.teilweise),
            }
        )
        state, befuellte, bekannte = calc.calculate(exploration, structure, algorithm)
        assert bekannte == 4
        # teilweise + vollstaendig + nutzervalidiert = 3 filled (only leer is unfilled)
        assert befuellte == 3
        assert state["e1"] == CompletenessStatus.vollstaendig
        assert state["e2"] == CompletenessStatus.leer
        assert state["s1"] == CompletenessStatus.nutzervalidiert
        assert state["a1"] == CompletenessStatus.teilweise
