"""Tests für den deterministischen Init-Validator (CR-006, CR-009).

Prüft die 2 verbleibenden Validierungsregeln:
- R-1: Referenzielle Integrität (nachfolger, regeln, schleifenkoerper, konvergenz)
- R-5: Abschnitt-Mapping vollständig (jeder Strukturschritt hat Algorithmusabschnitt)

CR-009: R-2 (Feldvollständigkeit), R-3 (Graph-Konsistenz), R-4 (Variablen-Crosscheck),
R-6 (ANALOG-Konsistenz) wurden in den LLM-Coverage-Validator verlagert.
"""

from __future__ import annotations

import pytest

from artifacts.init_validator import StructuralViolation, validate_algorithm_artifact, validate_structure_artifact
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
    Entscheidungsregel,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_schritt(
    schritt_id: str,
    reihenfolge: int,
    titel: str = "Schritt",
    beschreibung: str = "Beschreibung",
    typ: Strukturschritttyp = Strukturschritttyp.aktion,
    nachfolger: list[str] | None = None,
    bedingung: str | None = None,
    ausnahme_beschreibung: str | None = None,
    regeln: list[Entscheidungsregel] | None = None,
    schleifenkoerper: list[str] | None = None,
    konvergenz: str | None = None,
    spannungsfeld: str | None = None,
) -> Strukturschritt:
    return Strukturschritt(
        schritt_id=schritt_id,
        titel=titel,
        typ=typ,
        beschreibung=beschreibung,
        reihenfolge=reihenfolge,
        nachfolger=nachfolger or [],
        bedingung=bedingung,
        ausnahme_beschreibung=ausnahme_beschreibung,
        regeln=regeln or [],
        schleifenkoerper=schleifenkoerper or [],
        konvergenz=konvergenz,
        spannungsfeld=spannungsfeld,
        completeness_status=CompletenessStatus.teilweise,
        algorithmus_status=AlgorithmusStatus.ausstehend,
    )


def _make_valid_structure() -> StructureArtifact:
    """Minimales valides Strukturartefakt: s1 → s2 (Endschritt)."""
    return StructureArtifact(
        schritte={
            "s1": _make_schritt("s1", 1, nachfolger=["s2"]),
            "s2": _make_schritt("s2", 2, nachfolger=[]),
        }
    )


def _make_empty_exploration() -> ExplorationArtifact:
    return ExplorationArtifact(slots={})


# ---------------------------------------------------------------------------
# R-1: Referenzielle Integrität
# ---------------------------------------------------------------------------


class TestR1ReferenzielleIntegritaet:
    def test_valid_no_violations(self) -> None:
        structure = _make_valid_structure()
        violations = validate_structure_artifact(_make_empty_exploration(), structure)
        referenz_violations = [v for v in violations if "existiert nicht" in v.message]
        assert not referenz_violations

    def test_nachfolger_ungueltig(self) -> None:
        structure = StructureArtifact(
            schritte={"s1": _make_schritt("s1", 1, nachfolger=["s_nicht_vorhanden"])}
        )
        violations = validate_structure_artifact(_make_empty_exploration(), structure)
        assert any("nachfolger" in v.message and v.severity == "kritisch" for v in violations)

    def test_regeln_nachfolger_ungueltig(self) -> None:
        regeln = [Entscheidungsregel(bedingung="Ja", nachfolger="s_ghost")]
        structure = StructureArtifact(
            schritte={
                "s1": _make_schritt(
                    "s1", 1,
                    typ=Strukturschritttyp.entscheidung,
                    regeln=regeln,
                    bedingung="Test?",
                    nachfolger=[],
                )
            }
        )
        violations = validate_structure_artifact(_make_empty_exploration(), structure)
        assert any("regeln.nachfolger" in v.message and v.severity == "kritisch" for v in violations)

    def test_schleifenkoerper_ungueltig(self) -> None:
        structure = StructureArtifact(
            schritte={"s1": _make_schritt("s1", 1, schleifenkoerper=["s_ghost"])}
        )
        violations = validate_structure_artifact(_make_empty_exploration(), structure)
        assert any("schleifenkoerper" in v.message and v.severity == "kritisch" for v in violations)

    def test_konvergenz_ungueltig(self) -> None:
        structure = StructureArtifact(
            schritte={"s1": _make_schritt("s1", 1, konvergenz="s_ghost")}
        )
        violations = validate_structure_artifact(_make_empty_exploration(), structure)
        assert any("konvergenz" in v.message and v.severity == "kritisch" for v in violations)

    def test_vorgaenger_ungueltig(self) -> None:
        """R-1: vorgaenger referencing non-existent step is kritisch (CR-012)."""
        s1 = _make_schritt("s1", 1, nachfolger=["s2"])
        s1.vorgaenger = ["s_ghost"]
        structure = StructureArtifact(schritte={"s1": s1, "s2": _make_schritt("s2", 2)})
        violations = validate_structure_artifact(_make_empty_exploration(), structure)
        assert any("vorgaenger" in v.message and "existiert nicht" in v.message for v in violations)


# ---------------------------------------------------------------------------
# R-2: Bidirektionale Konsistenz nachfolger↔vorgaenger (CR-012)
# ---------------------------------------------------------------------------


class TestR2BidirektionaleKonsistenz:
    def test_konsistent_keine_violation(self) -> None:
        """Correct vorgaenger matching nachfolger → no violation."""
        s1 = _make_schritt("s1", 1, nachfolger=["s2"])
        s1.vorgaenger = []
        s2 = _make_schritt("s2", 2, nachfolger=[])
        s2.vorgaenger = ["s1"]
        structure = StructureArtifact(schritte={"s1": s1, "s2": s2})
        violations = validate_structure_artifact(_make_empty_exploration(), structure)
        konsistenz_violations = [v for v in violations if "vorgaenger-Inkonsistenz" in v.message]
        assert not konsistenz_violations

    def test_inkonsistent_fehlender_vorgaenger(self) -> None:
        """s1.nachfolger=["s2"] but s2.vorgaenger=[] → kritisch."""
        s1 = _make_schritt("s1", 1, nachfolger=["s2"])
        s1.vorgaenger = []
        s2 = _make_schritt("s2", 2, nachfolger=[])
        s2.vorgaenger = []  # Should be ["s1"]
        structure = StructureArtifact(schritte={"s1": s1, "s2": s2})
        violations = validate_structure_artifact(_make_empty_exploration(), structure)
        konsistenz_violations = [v for v in violations if "vorgaenger-Inkonsistenz" in v.message]
        assert len(konsistenz_violations) == 1
        assert konsistenz_violations[0].element_id == "s2"
        assert konsistenz_violations[0].severity == "kritisch"

    def test_inkonsistent_falscher_vorgaenger(self) -> None:
        """s2.vorgaenger=["s3"] but s3 doesn't have s2 in nachfolger → kritisch."""
        s1 = _make_schritt("s1", 1, nachfolger=["s2"])
        s2 = _make_schritt("s2", 2, nachfolger=[])
        s2.vorgaenger = ["s1", "s3"]  # s3 doesn't point to s2
        s3 = _make_schritt("s3", 3, nachfolger=[])
        structure = StructureArtifact(schritte={"s1": s1, "s2": s2, "s3": s3})
        violations = validate_structure_artifact(_make_empty_exploration(), structure)
        konsistenz_violations = [v for v in violations if "vorgaenger-Inkonsistenz" in v.message]
        assert len(konsistenz_violations) >= 1

    def test_default_empty_vorgaenger_triggers_if_nachfolger_exists(self) -> None:
        """Default [] vorgaenger with existing nachfolger references → violation."""
        structure = _make_valid_structure()  # s1→s2, both have vorgaenger=[]
        violations = validate_structure_artifact(_make_empty_exploration(), structure)
        konsistenz_violations = [v for v in violations if "vorgaenger-Inkonsistenz" in v.message]
        # s2 should have vorgaenger=["s1"] but has []
        assert len(konsistenz_violations) == 1
        assert konsistenz_violations[0].element_id == "s2"


# ---------------------------------------------------------------------------
# R-5: Abschnitt-Mapping
# ---------------------------------------------------------------------------


class TestR5AbschnittMapping:
    def test_fehlender_abschnitt(self) -> None:
        structure = _make_valid_structure()
        algorithm = AlgorithmArtifact(abschnitte={})
        violations = validate_algorithm_artifact(structure, algorithm)
        assert any(v.severity == "kritisch" for v in violations)
        assert len([v for v in violations if v.severity == "kritisch"]) == 2  # s1 und s2

    def test_abschnitt_vorhanden(self) -> None:
        structure = _make_valid_structure()
        algorithm = AlgorithmArtifact(
            abschnitte={
                "ab1": Algorithmusabschnitt(
                    abschnitt_id="ab1",
                    titel="Schritt 1",
                    struktur_ref="s1",
                    completeness_status=CompletenessStatus.leer,
                    status=AlgorithmusStatus.ausstehend,
                ),
                "ab2": Algorithmusabschnitt(
                    abschnitt_id="ab2",
                    titel="Schritt 2",
                    struktur_ref="s2",
                    completeness_status=CompletenessStatus.leer,
                    status=AlgorithmusStatus.ausstehend,
                ),
            }
        )
        violations = validate_algorithm_artifact(structure, algorithm)
        r5_violations = [v for v in violations if "Kein Algorithmusabschnitt" in v.message]
        assert not r5_violations
