"""Init-Modus Strukturierung — Background-Initialisierung des Strukturartefakts (CR-006, §3.6).

Transformiert das Explorationsartefakt vollständig in Strukturschritte,
bevor der Nutzer mit dem Dialog beginnt. Kein Dialog, keine Nutzeransprache.

Gibt ModeOutput zurück mit init_status gesetzt. nutzeraeusserung ist immer "".
"""

from __future__ import annotations

from pathlib import Path

from artifacts.models import InitStatus, Phasenstatus
from llm.base import LLMClient
from llm.tools import INIT_APPLY_PATCHES_TOOL
from modes.base import BaseMode, ModeContext, ModeOutput

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "init_structuring.md"


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
        status = schritt.completeness_status.value
        typ = schritt.typ.value
        lines.append(f"- [{schritt.reihenfolge}] {schritt.titel} ({sid}) [{typ}] [{status}]")
    return "\n".join(lines)


class InitStructuringMode(BaseMode):
    """Init-Modus für Strukturierung (CR-006, §3.6).

    Erbt von BaseMode, gibt ModeOutput zurück mit init_status gesetzt.
    Kein Dialog — nutzeraeusserung ist immer "".
    """

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm_client = llm_client

    async def call(self, context: ModeContext) -> ModeOutput:
        if self._llm_client is None:
            return ModeOutput(
                nutzeraeusserung="",
                patches=[],
                phasenstatus=Phasenstatus.in_progress,
                flags=[],
                init_status=InitStatus.init_complete,
            )

        exploration_content = _build_exploration_content(context)
        slot_status = _build_slot_status(context)

        system_prompt = _load_system_prompt()
        system_prompt = system_prompt.replace("{exploration_content}", exploration_content)
        system_prompt = system_prompt.replace("{slot_status}", slot_status)

        # Init-Modi benötigen keinen Dialog-Verlauf — einmaliger LLM-Call ohne History
        response = await self._llm_client.complete(
            system=system_prompt,
            messages=[{"role": "user", "content": "[Initialisierung starten]"}],
            tools=[INIT_APPLY_PATCHES_TOOL],
            tool_choice={"type": "tool", "name": "apply_patches"},
        )

        tool_input = response.tool_input or {}
        patches = [p for p in (tool_input.get("patches") or []) if isinstance(p, dict)]

        raw_init_status = tool_input.get("init_status", "init_in_progress")
        try:
            init_status = InitStatus(raw_init_status)
        except ValueError:
            init_status = InitStatus.init_in_progress

        return ModeOutput(
            nutzeraeusserung="",
            patches=patches,
            phasenstatus=Phasenstatus.in_progress,
            flags=[],
            init_status=init_status,
            debug_request=response.debug_request,
            usage=response.usage,
        )
