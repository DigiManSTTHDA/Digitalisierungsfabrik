"""Tests für den deterministischen Init-Validator (CR-006, AC #12).

Prüft alle 6 Validierungsregeln:
- R-1: Referenzielle Integrität (nachfolger, regeln, schleifenkoerper, konvergenz)
- R-2: Feldvollständigkeit (titel, beschreibung, bedingung, ausnahme_beschreibung)
- R-3: Graph-Konsistenz (genau 1 Startschritt, mindestens 1 Endschritt)
- R-4: Variablen-Crosscheck (variablen_und_daten → beschreibung)
- R-5: Abschnitt-Mapping vollständig (jeder Strukturschritt hat Algorithmusabschnitt)
- R-6: ANALOG-Konsistenz (ANALOG:-Schritt hat emma_kompatibel=false Aktion)
"""

from __future__ import annotations

import pytest

from artifacts.init_validator import StructuralViolation, validate_algorithm_artifact, validate_structure_artifact
from artifacts.models import (
    AlgorithmArtifact,
    Algorithmusabschnitt,
    AlgorithmusStatus,
    CompletenessStatus,
    EmmaAktion,
    EmmaAktionstyp,
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


def _make_exploration_with_variable(var_name: str) -> ExplorationArtifact:
    return ExplorationArtifact(
        slots={
            "variablen_und_daten": ExplorationSlot(
                slot_id="variablen_und_daten",
                titel="Variablen und Daten",
                inhalt=f"{var_name} — Eine Testvariable",
                completeness_status=CompletenessStatus.teilweise,
            )
        }
    )


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


# ---------------------------------------------------------------------------
# R-2: Feldvollständigkeit
# ---------------------------------------------------------------------------


class TestR2Feldvollstaendigkeit:
    def test_titel_leer(self) -> None:
        structure = StructureArtifact(
            schritte={"s1": _make_schritt("s1", 1, titel="")}
        )
        violations = validate_structure_artifact(_make_empty_exploration(), structure)
        assert any("titel leer" in v.message and v.severity == "kritisch" for v in violations)

    def test_beschreibung_leer(self) -> None:
        structure = StructureArtifact(
            schritte={"s1": _make_schritt("s1", 1, beschreibung="")}
        )
        violations = validate_structure_artifact(_make_empty_exploration(), structure)
        assert any("beschreibung leer" in v.message and v.severity == "warnung" for v in violations)

    def test_entscheidung_ohne_bedingung(self) -> None:
        structure = StructureArtifact(
            schritte={
                "s1": _make_schritt(
                    "s1", 1, typ=Strukturschritttyp.entscheidung, bedingung=None
                )
            }
        )
        violations = validate_structure_artifact(_make_empty_exploration(), structure)
        assert any("entscheidung ohne bedingung" in v.message and v.severity == "warnung" for v in violations)

    def test_ausnahme_ohne_beschreibung(self) -> None:
        structure = StructureArtifact(
            schritte={
                "s1": _make_schritt(
                    "s1", 99, typ=Strukturschritttyp.ausnahme, ausnahme_beschreibung=None
                )
            }
        )
        violations = validate_structure_artifact(_make_empty_exploration(), structure)
        assert any(
            "ausnahme ohne ausnahme_beschreibung" in v.message and v.severity == "warnung"
            for v in violations
        )


# ---------------------------------------------------------------------------
# R-3: Graph-Konsistenz
# ---------------------------------------------------------------------------


class TestR3GraphKonsistenz:
    def test_kein_startschritt(self) -> None:
        """Wenn alle Schritte referenziert sind, gibt es keinen Startschritt."""
        structure = StructureArtifact(
            schritte={
                "s1": _make_schritt("s1", 1, nachfolger=["s2"]),
                "s2": _make_schritt("s2", 2, nachfolger=["s1"]),  # Zyklus — beide referenziert
            }
        )
        violations = validate_structure_artifact(_make_empty_exploration(), structure)
        assert any("Startschritt" in v.message and v.severity == "warnung" for v in violations)

    def test_mehrere_startkandidaten(self) -> None:
        structure = StructureArtifact(
            schritte={
                "s1": _make_schritt("s1", 1, nachfolger=[]),
                "s2": _make_schritt("s2", 2, nachfolger=[]),
            }
        )
        violations = validate_structure_artifact(_make_empty_exploration(), structure)
        assert any("Startschritt" in v.message and v.severity == "warnung" for v in violations)

    def test_kein_endschritt(self) -> None:
        """Kein Schritt hat nachfolger: [] (abgesehen von Ausnahmen)."""
        structure = StructureArtifact(
            schritte={
                "s1": _make_schritt("s1", 1, nachfolger=["s2"]),
                "s2": _make_schritt("s2", 2, nachfolger=["s1"]),
            }
        )
        violations = validate_structure_artifact(_make_empty_exploration(), structure)
        assert any("Endschritt" in v.message and v.severity == "warnung" for v in violations)

    def test_valid_graph(self) -> None:
        structure = _make_valid_structure()
        violations = validate_structure_artifact(_make_empty_exploration(), structure)
        graph_violations = [
            v for v in violations
            if "Startschritt" in v.message or "Endschritt" in v.message
        ]
        assert not graph_violations


# ---------------------------------------------------------------------------
# R-4: Variablen-Crosscheck
# ---------------------------------------------------------------------------


class TestR4VariablenCrosscheck:
    def test_variable_nicht_in_beschreibung(self) -> None:
        exploration = _make_exploration_with_variable("rechnungsnummer")
        structure = StructureArtifact(
            schritte={
                "s1": _make_schritt("s1", 1, beschreibung="Keine Variable hier"),
            }
        )
        violations = validate_structure_artifact(exploration, structure)
        assert any(
            "rechnungsnummer" in v.message and v.severity == "warnung" for v in violations
        )

    def test_variable_in_beschreibung_vorhanden(self) -> None:
        exploration = _make_exploration_with_variable("rechnungsnummer")
        structure = StructureArtifact(
            schritte={
                "s1": _make_schritt("s1", 1, beschreibung="Die rechnungsnummer wird geprüft"),
            }
        )
        violations = validate_structure_artifact(exploration, structure)
        variable_violations = [v for v in violations if "rechnungsnummer" in v.message]
        assert not variable_violations

    def test_empty_exploration_no_violations(self) -> None:
        structure = _make_valid_structure()
        violations = validate_structure_artifact(_make_empty_exploration(), structure)
        variable_violations = [v for v in violations if "Variable" in v.message]
        assert not variable_violations


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


# ---------------------------------------------------------------------------
# R-6: ANALOG-Konsistenz
# ---------------------------------------------------------------------------


class TestR6AnalogKonsistenz:
    def test_analog_schritt_ohne_inkompatible_aktion(self) -> None:
        structure = StructureArtifact(
            schritte={
                "s1": _make_schritt(
                    "s1", 1, spannungsfeld="ANALOG: Physische Unterschrift erforderlich"
                )
            }
        )
        algorithm = AlgorithmArtifact(
            abschnitte={
                "ab1": Algorithmusabschnitt(
                    abschnitt_id="ab1",
                    titel="Schritt 1",
                    struktur_ref="s1",
                    aktionen={
                        "a1": EmmaAktion(
                            aktion_id="a1",
                            aktionstyp=EmmaAktionstyp.FIND,
                            emma_kompatibel=True,  # Alle kompatibel — Warnung erwartet
                        )
                    },
                    completeness_status=CompletenessStatus.leer,
                    status=AlgorithmusStatus.ausstehend,
                )
            }
        )
        violations = validate_algorithm_artifact(structure, algorithm)
        assert any(
            "ANALOG-Schritt" in v.message and v.severity == "warnung" for v in violations
        )

    def test_analog_schritt_mit_inkompatible_aktion(self) -> None:
        structure = StructureArtifact(
            schritte={
                "s1": _make_schritt(
                    "s1", 1, spannungsfeld="ANALOG: Physische Unterschrift"
                )
            }
        )
        algorithm = AlgorithmArtifact(
            abschnitte={
                "ab1": Algorithmusabschnitt(
                    abschnitt_id="ab1",
                    titel="Schritt 1",
                    struktur_ref="s1",
                    aktionen={
                        "a1": EmmaAktion(
                            aktion_id="a1",
                            aktionstyp=EmmaAktionstyp.WAIT,
                            emma_kompatibel=False,  # Inkompatibel — kein Fehler
                        )
                    },
                    completeness_status=CompletenessStatus.leer,
                    status=AlgorithmusStatus.ausstehend,
                )
            }
        )
        violations = validate_algorithm_artifact(structure, algorithm)
        analog_violations = [v for v in violations if "ANALOG-Schritt" in v.message]
        assert not analog_violations

    def test_nicht_analog_kein_spannungsfeld(self) -> None:
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
        analog_violations = [v for v in violations if "ANALOG-Schritt" in v.message]
        assert not analog_violations
