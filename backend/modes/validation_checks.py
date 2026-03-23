"""Deterministic validation checks and prompt content builders (SDD 6.6.4).

Extracted from validation.py to respect the 300-line file limit.
Contains pure functions with no LLM dependency.

SDD references: FR-C-01 (Inkonsistenz), FR-C-03 (EMMA), FR-C-08 (Schweregrad).
"""

from __future__ import annotations

from artifacts.models import (
    CompletenessStatus,
    EmmaAktionstyp,
    Schweregrad,
    Strukturschritttyp,
    Validierungsbefund,
)
from modes.base import ModeContext


def deterministic_checks(ctx: ModeContext) -> list[Validierungsbefund]:
    """Run deterministic checks that don't need the LLM (FR-C-01, FR-C-03, SDD 5.6)."""
    befunde: list[Validierungsbefund] = []
    bid = 0
    structure, algorithm = ctx.structure_artifact, ctx.algorithm_artifact

    # 1. Referential integrity: struktur → algorithmus (FR-B-03)
    for sid, schritt in structure.schritte.items():
        for aref in schritt.algorithmus_ref:
            if aref not in algorithm.abschnitte:
                bid += 1
                befunde.append(
                    Validierungsbefund(
                        befund_id=f"det-{bid}",
                        schweregrad=Schweregrad.kritisch,
                        beschreibung=f"Strukturschritt '{schritt.titel}' referenziert "
                        f"Algorithmusabschnitt '{aref}', der nicht existiert.",
                        betroffene_slots=[sid],
                        artefakttyp="struktur",
                        empfehlung="Fehlenden Algorithmusabschnitt erstellen oder Referenz korrigieren.",
                    )
                )

    # 2. Referential integrity: algorithmus → struktur (FR-B-03)
    for aid, abschnitt in algorithm.abschnitte.items():
        if abschnitt.struktur_ref not in structure.schritte:
            bid += 1
            befunde.append(
                Validierungsbefund(
                    befund_id=f"det-{bid}",
                    schweregrad=Schweregrad.kritisch,
                    beschreibung=f"Algorithmusabschnitt '{abschnitt.titel}' referenziert "
                    f"Strukturschritt '{abschnitt.struktur_ref}', der nicht existiert.",
                    betroffene_slots=[aid],
                    artefakttyp="algorithmus",
                    empfehlung="Referenz auf existierenden Strukturschritt korrigieren.",
                )
            )

    # 3. EMMA compatibility: all aktionstyp values valid (FR-C-03)
    valid_types = set(EmmaAktionstyp)
    for aid, abschnitt in algorithm.abschnitte.items():
        for aktion_id, aktion in abschnitt.aktionen.items():
            if aktion.aktionstyp not in valid_types:
                bid += 1
                befunde.append(
                    Validierungsbefund(
                        befund_id=f"det-{bid}",
                        schweregrad=Schweregrad.kritisch,
                        beschreibung=f"EMMA-Aktion '{aktion_id}' in Abschnitt '{abschnitt.titel}' "
                        f"hat ungültigen Aktionstyp '{aktion.aktionstyp}'.",
                        betroffene_slots=[aid],
                        artefakttyp="algorithmus",
                        empfehlung="Aktionstyp aus dem EMMA-Katalog wählen.",
                    )
                )

    # 4. Completeness: no mandatory slots with status leer/teilweise (SDD 5.6)
    incomplete = (CompletenessStatus.leer, CompletenessStatus.teilweise)
    for sid, schritt in structure.schritte.items():
        if schritt.completeness_status in incomplete:
            bid += 1
            befunde.append(
                Validierungsbefund(
                    befund_id=f"det-{bid}",
                    schweregrad=Schweregrad.warnung,
                    beschreibung=f"Strukturschritt '{schritt.titel}' hat Status "
                    f"'{schritt.completeness_status.value}' — nicht vollständig.",
                    betroffene_slots=[sid],
                    artefakttyp="struktur",
                    empfehlung="Fehlende Informationen ergänzen.",
                )
            )
    for aid, abschnitt in algorithm.abschnitte.items():
        if abschnitt.completeness_status in incomplete:
            bid += 1
            befunde.append(
                Validierungsbefund(
                    befund_id=f"det-{bid}",
                    schweregrad=Schweregrad.warnung,
                    beschreibung=f"Algorithmusabschnitt '{abschnitt.titel}' hat Status "
                    f"'{abschnitt.completeness_status.value}' — nicht vollständig.",
                    betroffene_slots=[aid],
                    artefakttyp="algorithmus",
                    empfehlung="Fehlende Aktionen spezifizieren.",
                )
            )

    # 5. Exception handling: ausnahme Strukturschritte referenced (SDD 6.6.4 bullet 4)
    ausnahme_ids = {
        sid for sid, s in structure.schritte.items() if s.typ == Strukturschritttyp.ausnahme
    }
    referenced = {a.struktur_ref for a in algorithm.abschnitte.values()}
    for sid in ausnahme_ids - referenced:
        bid += 1
        befunde.append(
            Validierungsbefund(
                befund_id=f"det-{bid}",
                schweregrad=Schweregrad.kritisch,
                beschreibung=f"Ausnahme-Schritt '{structure.schritte[sid].titel}' "
                f"hat keinen zugehörigen Algorithmusabschnitt.",
                betroffene_slots=[sid],
                artefakttyp="struktur",
                empfehlung="Algorithmusabschnitt für die Ausnahmebehandlung erstellen.",
            )
        )
    # 6. CR-002: regeln↔nachfolger consistency
    for sid, schritt in structure.schritte.items():
        if not schritt.regeln:
            continue
        expected_nachfolger = [r.nachfolger for r in schritt.regeln]
        if set(schritt.nachfolger) != set(expected_nachfolger):
            bid += 1
            befunde.append(
                Validierungsbefund(
                    befund_id=f"det-{bid}",
                    schweregrad=Schweregrad.kritisch,
                    beschreibung=f"Strukturschritt '{schritt.titel}': nachfolger {schritt.nachfolger} "
                    f"stimmt nicht mit regeln-Nachfolgern {expected_nachfolger} überein.",
                    betroffene_slots=[sid],
                    artefakttyp="struktur",
                    empfehlung="regeln ist die Quelle der Wahrheit — nachfolger muss daraus abgeleitet werden.",
                )
            )

    # 7. CR-002: schleifenkoerper references valid Strukturschritte
    all_schritt_ids = set(structure.schritte.keys())
    for sid, schritt in structure.schritte.items():
        for ref in schritt.schleifenkoerper:
            if ref not in all_schritt_ids:
                bid += 1
                befunde.append(
                    Validierungsbefund(
                        befund_id=f"det-{bid}",
                        schweregrad=Schweregrad.kritisch,
                        beschreibung=f"Strukturschritt '{schritt.titel}': schleifenkoerper "
                        f"referenziert '{ref}', der nicht existiert.",
                        betroffene_slots=[sid],
                        artefakttyp="struktur",
                        empfehlung="Referenz auf existierenden Strukturschritt korrigieren.",
                    )
                )

    return befunde


def build_exploration_content(ctx: ModeContext) -> str:
    """Build exploration artifact summary for the prompt."""
    if not ctx.exploration_artifact.slots:
        return "(Explorationsartefakt ist leer)"
    lines: list[str] = []
    for sid, slot in ctx.exploration_artifact.slots.items():
        inhalt = slot.inhalt[:100] + "..." if len(slot.inhalt) > 100 else slot.inhalt
        lines.append(f"- {slot.titel} ({sid}) [{slot.completeness_status.value}]: {inhalt}")
    return "\n".join(lines)


def build_structure_content(ctx: ModeContext) -> str:
    """Build structure artifact summary for the prompt."""
    if not ctx.structure_artifact.schritte:
        return "(Strukturartefakt ist leer)"
    lines: list[str] = []
    for sid, s in sorted(ctx.structure_artifact.schritte.items(), key=lambda x: x[1].reihenfolge):
        refs = ", ".join(s.algorithmus_ref) if s.algorithmus_ref else "—"
        lines.append(
            f"- [{s.reihenfolge}] {s.titel} ({sid}) [{s.typ.value}] "
            f"[{s.completeness_status.value}] → algo: {refs}"
        )
    return "\n".join(lines)


def build_algorithm_content(ctx: ModeContext) -> str:
    """Build algorithm artifact summary for the prompt."""
    if not ctx.algorithm_artifact.abschnitte:
        return "(Algorithmusartefakt ist leer)"
    lines: list[str] = []
    for aid, a in ctx.algorithm_artifact.abschnitte.items():
        lines.append(
            f"- {a.titel} ({aid}) [ref: {a.struktur_ref}] "
            f"[{a.completeness_status.value}] — {len(a.aktionen)} Aktionen"
        )
    return "\n".join(lines)
