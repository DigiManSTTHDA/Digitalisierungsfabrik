"""Deterministische Strukturvalidierung für Background-Initialisierung (CR-006, §3.3).

Prüft nach jedem Init-Turn und nach Abschluss referenzielle Integrität,
Feldvollständigkeit, Graph-Konsistenz, Variablen-Crosscheck, Abschnitt-Mapping
und ANALOG-Konsistenz.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from artifacts.models import (
    AlgorithmArtifact,
    ExplorationArtifact,
    StructureArtifact,
    Strukturschritttyp,
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
    """Struktur-Artefakt gegen 4 Prüfregeln validieren (R-1 bis R-4)."""
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

    # R-2: Feldvollständigkeit
    for sid, schritt in structure.schritte.items():
        if not schritt.titel:
            violations.append(StructuralViolation("kritisch", "titel leer", sid))
        if not schritt.beschreibung:
            violations.append(StructuralViolation("warnung", "beschreibung leer", sid))
        if schritt.typ == Strukturschritttyp.entscheidung and not schritt.bedingung:
            violations.append(StructuralViolation("warnung", "entscheidung ohne bedingung", sid))
        if schritt.typ == Strukturschritttyp.ausnahme and not schritt.ausnahme_beschreibung:
            violations.append(StructuralViolation(
                "warnung", "ausnahme ohne ausnahme_beschreibung", sid))

    # R-3: Graph-Konsistenz
    referenziert = {nf for s in structure.schritte.values() for nf in s.nachfolger}
    start_kandidaten = [sid for sid in alle_ids if sid not in referenziert]
    if len(start_kandidaten) != 1:
        violations.append(StructuralViolation(
            "warnung", f"Genau 1 Startschritt erwartet, gefunden: {start_kandidaten}"))
    end_kandidaten = [sid for sid, s in structure.schritte.items() if not s.nachfolger
                      and s.typ != Strukturschritttyp.ausnahme]
    if not end_kandidaten:
        violations.append(StructuralViolation("warnung", "Kein Endschritt (nachfolger: []) gefunden"))

    # R-4: Variablen-Crosscheck
    var_slot = exploration.slots.get("variablen_und_daten")
    if var_slot and var_slot.inhalt:
        # Einfache Heuristik: Prüfe ob Eintrags-Namen (bis " —") in irgendeiner beschreibung auftauchen
        for zeile in var_slot.inhalt.splitlines():
            var_name = zeile.split("—")[0].strip().split(" ")[0].lower()
            if var_name and not any(
                var_name in s.beschreibung.lower()
                for s in structure.schritte.values()
            ):
                violations.append(StructuralViolation(
                    "warnung",
                    f"Variable '{var_name}' aus variablen_und_daten nicht in beschreibung gefunden"))

    return violations


def validate_algorithm_artifact(
    structure: StructureArtifact,
    algorithm: AlgorithmArtifact,
) -> list[StructuralViolation]:
    """Algorithmus-Artefakt gegen 2 Prüfregeln validieren (R-5 bis R-6)."""
    violations: list[StructuralViolation] = []

    # R-5: Abschnitt-Mapping vollständig
    for sid in structure.schritte:
        refs = [ab for ab in algorithm.abschnitte.values() if ab.struktur_ref == sid]
        if not refs:
            violations.append(StructuralViolation(
                "kritisch", f"Kein Algorithmusabschnitt für Strukturschritt '{sid}'", sid))

    # R-6: ANALOG-Konsistenz
    for sid, schritt in structure.schritte.items():
        if schritt.spannungsfeld and schritt.spannungsfeld.startswith("ANALOG:"):
            ab = next((a for a in algorithm.abschnitte.values() if a.struktur_ref == sid), None)
            if ab:
                hat_inkompatible_aktion = any(
                    not a.emma_kompatibel for a in ab.aktionen.values()
                )
                if not hat_inkompatible_aktion:
                    violations.append(StructuralViolation(
                        "warnung",
                        f"ANALOG-Schritt '{sid}' hat keine emma_kompatibel=false Aktion", sid))

    return violations
