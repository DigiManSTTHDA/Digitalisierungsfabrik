"""Deterministische Strukturvalidierung für Background-Initialisierung (CR-006, CR-009).

Prüft nach dem Init-Call referenzielle Integrität (R-1) und Abschnitt-Mapping (R-5).
Semantische Prüfungen (Feldvollständigkeit, Graph-Konsistenz, Variablen, ANALOG)
werden vom LLM-Coverage-Validator übernommen (CR-009, §3.6).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from artifacts.models import (
    AlgorithmArtifact,
    ExplorationArtifact,
    StructureArtifact,
)


@dataclass
class StructuralViolation:
    """Ein einzelner Befund der deterministischen Strukturprüfung."""

    severity: Literal["kritisch", "warnung"]
    message: str
    element_id: str | None = field(default=None)


def validate_structure_artifact(
    exploration: ExplorationArtifact,
    structure: StructureArtifact,
) -> list[StructuralViolation]:
    """Struktur-Artefakt validieren — nur R-1: Referenzielle Integrität."""
    violations: list[StructuralViolation] = []

    # R-1: Referenzielle Integrität
    alle_ids = set(structure.schritte.keys())
    for sid, schritt in structure.schritte.items():
        for nf in schritt.nachfolger:
            if nf not in alle_ids:
                violations.append(StructuralViolation(
                    "kritisch", f"nachfolger '{nf}' existiert nicht", sid))
        for regel in schritt.regeln:
            if regel.nachfolger not in alle_ids:
                violations.append(StructuralViolation(
                    "kritisch", f"regeln.nachfolger '{regel.nachfolger}' existiert nicht", sid))
        for kid in schritt.schleifenkoerper:
            if kid not in alle_ids:
                violations.append(StructuralViolation(
                    "kritisch", f"schleifenkoerper '{kid}' existiert nicht", sid))
        if schritt.konvergenz and schritt.konvergenz not in alle_ids:
            violations.append(StructuralViolation(
                "kritisch", f"konvergenz '{schritt.konvergenz}' existiert nicht", sid))
        for vg in schritt.vorgaenger:
            if vg not in alle_ids:
                violations.append(StructuralViolation(
                    "kritisch", f"vorgaenger '{vg}' existiert nicht", sid))

    # R-2: Bidirektionale Konsistenz nachfolger↔vorgaenger (CR-012)
    # Berechne erwartete vorgaenger aus nachfolger-Referenzen
    expected_vorgaenger: dict[str, set[str]] = {sid: set() for sid in alle_ids}
    for sid, schritt in structure.schritte.items():
        for nf in schritt.nachfolger:
            if nf in expected_vorgaenger:
                expected_vorgaenger[nf].add(sid)
    for sid, schritt in structure.schritte.items():
        actual = set(schritt.vorgaenger)
        expected = expected_vorgaenger[sid]
        if actual != expected:
            violations.append(StructuralViolation(
                "kritisch",
                f"vorgaenger-Inkonsistenz: ist {sorted(actual)}, erwartet {sorted(expected)} (aus nachfolger abgeleitet)",
                sid,
            ))

    return violations


def validate_algorithm_artifact(
    structure: StructureArtifact,
    algorithm: AlgorithmArtifact,
) -> list[StructuralViolation]:
    """Algorithmus-Artefakt validieren — nur R-5: Abschnitt-Mapping vollständig."""
    violations: list[StructuralViolation] = []

    # R-5: Abschnitt-Mapping vollständig
    for sid in structure.schritte:
        refs = [ab for ab in algorithm.abschnitte.values() if ab.struktur_ref == sid]
        if not refs:
            violations.append(StructuralViolation(
                "kritisch", f"Kein Algorithmusabschnitt für Strukturschritt '{sid}'", sid))

    return violations
