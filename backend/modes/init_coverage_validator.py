"""Init-Modus Coverage-Validator — prüft Coverage zwischen Quellartefakt und Zielartefakt (CR-006, §3.4).

Einmalig nach dem Init-Loop aufgerufen. Gibt ModeOutput zurück wobei
nutzeraeusserung ein JSON-String mit dem Coverage-Schema ist — kein Dialog-Text.
Der Orchestrator parst diesen JSON-String in StructuralViolation-Objekte.
"""

from __future__ import annotations

from pathlib import Path

from artifacts.models import Phasenstatus
from llm.base import LLMClient
from modes.base import BaseMode, ModeContext, ModeOutput

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "init_coverage_validator.md"

_EMPTY_COVERAGE_JSON = '{"fehlende_entitaeten": [], "coverage_vollstaendig": true}'


def _load_system_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _build_exploration_content(context: ModeContext) -> str:
    lines: list[str] = []
    for slot_id, slot in context.exploration_artifact.slots.items():
        if slot.inhalt:
            lines.append(f"### {slot.titel} ({slot_id})\n{slot.inhalt}")
    return "\n\n".join(lines) if lines else "(Explorationsartefakt ist leer)"


def _build_slot_status(context: ModeContext) -> str:
    schritte = context.structure_artifact.schritte
    if not schritte:
        return "(Noch keine Strukturschritte vorhanden)"
    lines: list[str] = []
    for sid, schritt in sorted(schritte.items(), key=lambda x: x[1].reihenfolge):
        typ = schritt.typ.value
        lines.append(f"- [{schritt.reihenfolge}] {schritt.titel} ({sid}) [{typ}]")
        if schritt.beschreibung:
            lines.append(f"  Beschreibung: {schritt.beschreibung}")
    return "\n".join(lines)


def _build_algorithm_status(context: ModeContext) -> str:
    abschnitte = context.algorithm_artifact.abschnitte
    if not abschnitte:
        return "(Noch keine Algorithmusabschnitte vorhanden)"
    lines: list[str] = []
    for aid, abschnitt in abschnitte.items():
        lines.append(f"- {abschnitt.titel} ({aid}) [ref: {abschnitt.struktur_ref}]")
        if abschnitt.kontext:
            lines.append(f"  Kontext: {abschnitt.kontext[:200]}")
    return "\n".join(lines)


class InitCoverageValidatorMode(BaseMode):
    """Coverage-Validator-Modus (CR-006, §3.4 / §3.6).

    Gibt ModeOutput zurück wobei nutzeraeusserung ein JSON-String ist.
    Der Orchestrator parst diesen String — kein menschenlesbarer Text.
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

        exploration_content = _build_exploration_content(context)
        slot_status = _build_slot_status(context)
        algorithm_status = _build_algorithm_status(context)

        system_prompt = _load_system_prompt()
        system_prompt = system_prompt.replace("{exploration_content}", exploration_content)
        system_prompt = system_prompt.replace("{slot_status}", slot_status)
        system_prompt = system_prompt.replace("{algorithm_status}", algorithm_status)

        # Coverage-Validator gibt reinen Text zurück (JSON) — kein Tool-Use
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
