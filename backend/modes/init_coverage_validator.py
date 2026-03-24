"""Init-Modus Coverage-Validator — prüft Qualität der Artefakt-Transformation (CR-006, CR-009).

Einmalig nach dem Init-Call aufgerufen. Gibt ModeOutput zurück wobei
nutzeraeusserung ein JSON-String mit dem Coverage-Schema ist — kein Dialog-Text.
Der Orchestrator parst diesen JSON-String in StructuralViolation-Objekte.

CR-009: Phasenspezifischer Kontext, aufgewertete Prüfkriterien,
darf jetzt auch "kritisch" melden.
"""

from __future__ import annotations

import json
from pathlib import Path

from artifacts.models import Phasenstatus, Projektphase
from llm.base import LLMClient
from modes.base import BaseMode, ModeContext, ModeOutput

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "init_coverage_validator.md"

_EMPTY_COVERAGE_JSON = '{"fehlende_entitaeten": [], "coverage_vollstaendig": true}'

_OUTPUT_SCHEMA_JSON = """{
  "fehlende_entitaeten": [
    {
      "typ": "prozessabschnitt | entscheidung | system | akteur | variable | detail | feldvollstaendigkeit | kontrollfluss",
      "bezeichnung": "Beschreibung des Befunds",
      "quelle_slot": "Slot/Feld im Quellartefakt mit der Information",
      "zitat": "Wörtliches Zitat aus dem Quellartefakt",
      "schweregrad": "kritisch | warnung"
    }
  ],
  "coverage_vollstaendig": true
}"""


def _load_system_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _build_exploration_content(context: ModeContext) -> str:
    lines: list[str] = []
    for slot_id, slot in context.exploration_artifact.slots.items():
        if slot.inhalt:
            lines.append(f"### {slot.titel} ({slot_id})\n{slot.inhalt}")
    return "\n\n".join(lines) if lines else "(Explorationsartefakt ist leer)"


def _build_structure_content(context: ModeContext) -> str:
    """Build full structure artifact content for coverage validation."""
    schritte = context.structure_artifact.schritte
    if not schritte:
        return "(Noch keine Strukturschritte vorhanden)"
    lines: list[str] = []
    zusammenfassung = context.structure_artifact.prozesszusammenfassung
    if zusammenfassung:
        lines.append(f"Prozesszusammenfassung: {zusammenfassung}\n")
    for sid, schritt in sorted(schritte.items(), key=lambda x: x[1].reihenfolge):
        typ = schritt.typ.value
        lines.append(f"### {schritt.titel} ({sid}) [{typ}]")
        if schritt.beschreibung:
            lines.append(f"Beschreibung: {schritt.beschreibung}")
        if schritt.bedingung:
            lines.append(f"Bedingung: {schritt.bedingung}")
        if schritt.regeln:
            for r in schritt.regeln:
                lines.append(f"  Regel: {r.bedingung} → {r.nachfolger} ({r.bezeichnung})")
        if schritt.schleifenkoerper:
            lines.append(f"Schleifenkörper: {schritt.schleifenkoerper}")
        if schritt.abbruchbedingung:
            lines.append(f"Abbruchbedingung: {schritt.abbruchbedingung}")
        if schritt.nachfolger:
            lines.append(f"Nachfolger: {schritt.nachfolger}")
        if schritt.spannungsfeld:
            lines.append(f"Spannungsfeld: {schritt.spannungsfeld}")
        if schritt.ausnahme_beschreibung:
            lines.append(f"Ausnahme: {schritt.ausnahme_beschreibung}")
        lines.append("")
    return "\n".join(lines)


def _build_algorithm_content(context: ModeContext) -> str:
    """Build full algorithm artifact content for coverage validation."""
    abschnitte = context.algorithm_artifact.abschnitte
    if not abschnitte:
        return "(Noch keine Algorithmusabschnitte vorhanden)"
    lines: list[str] = []
    zusammenfassung = context.algorithm_artifact.prozesszusammenfassung
    if zusammenfassung:
        lines.append(f"Prozesszusammenfassung: {zusammenfassung}\n")
    for aid, abschnitt in abschnitte.items():
        lines.append(f"### {abschnitt.titel} ({aid}) [ref: {abschnitt.struktur_ref}]")
        if abschnitt.kontext:
            lines.append(f"Kontext: {abschnitt.kontext}")
        n_aktionen = len(abschnitt.aktionen)
        if n_aktionen > 0:
            lines.append(f"Aktionen: {n_aktionen}")
            for aktion_id, aktion in abschnitt.aktionen.items():
                compat = "kompatibel" if aktion.emma_kompatibel else "NICHT kompatibel"
                lines.append(f"  - {aktion_id}: {aktion.aktionstyp} [{compat}]")
        lines.append("")
    return "\n".join(lines)


class InitCoverageValidatorMode(BaseMode):
    """Coverage-Validator-Modus (CR-006, CR-009).

    Gibt ModeOutput zurück wobei nutzeraeusserung ein JSON-String ist.
    Der Orchestrator parst diesen String — kein menschenlesbarer Text.

    CR-009: Phasenspezifischer Kontext, darf "kritisch" melden.
    """

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm_client = llm_client

    async def call(self, context: ModeContext) -> ModeOutput:
        if self._llm_client is None:
            return ModeOutput(
                nutzeraeusserung=_EMPTY_COVERAGE_JSON,
                patches=[],
                phasenstatus=Phasenstatus.in_progress,
                flags=[],
            )

        system_prompt = _load_system_prompt()

        # CR-009: Phasenspezifischen Kontext bestimmen
        if context.aktive_phase == Projektphase.strukturierung:
            transition_desc = (
                "Du prüfst den Übergang **Exploration → Struktur**.\n\n"
                "Quellartefakt: Explorationsartefakt (7 Slots mit Freitext).\n"
                "Zielartefakt: Strukturartefakt (Strukturschritte mit Kontrollfluss).\n\n"
                "Hauptfrage: Wurde jede substanzielle Information aus den 7 Exploration-Slots "
                "in mindestens einem Strukturschritt repräsentiert?"
            )
            source_artifact = _build_exploration_content(context)
            target_artifact = _build_structure_content(context)
        else:
            transition_desc = (
                "Du prüfst den Übergang **Struktur → Algorithmus**.\n\n"
                "Quellartefakt: Strukturartefakt (Strukturschritte mit Kontrollfluss).\n"
                "Zielartefakt: Algorithmusartefakt (Algorithmusabschnitte mit EMMA-Aktionen).\n\n"
                "Hauptfrage: Hat jeder Strukturschritt einen korrespondierenden "
                "Algorithmusabschnitt mit vollständigem Kontext?"
            )
            source_artifact = _build_structure_content(context)
            target_artifact = _build_algorithm_content(context)

        system_prompt = system_prompt.replace("{transition_type_description}", transition_desc)
        system_prompt = system_prompt.replace("{source_artifact}", source_artifact)
        system_prompt = system_prompt.replace("{target_artifact}", target_artifact)
        system_prompt = system_prompt.replace("{output_schema}", _OUTPUT_SCHEMA_JSON)

        response = await self._llm_client.complete(
            system=system_prompt,
            messages=[{"role": "user", "content": "[Coverage-Prüfung starten]"}],
            tools=None,
            tool_choice=None,
        )

        return ModeOutput(
            nutzeraeusserung=response.nutzeraeusserung or _EMPTY_COVERAGE_JSON,
            patches=[],
            phasenstatus=Phasenstatus.in_progress,
            flags=[],
            debug_request=response.debug_request,
            usage=response.usage,
        )
