"""Explorationsmodus — erfasst implizites Prozesswissen des Nutzers (SDD 6.6.1).

Calls the LLM via LLMClient to conduct a structured interview, filling the
6 Pflicht-Slots of the ExplorationArtifact through dialog with the user.

The LLM decides the phasenstatus directly — no deterministic guardrails.

SDD references: 6.6.1 (Explorationsmodus), FR-B-00 (Pflicht-Slots),
FR-A-02 (Tool Use API), FR-A-08 (Systemsprache Deutsch).
"""

from __future__ import annotations

from pathlib import Path

from artifacts.models import CompletenessStatus, ExplorationSlot, Phasenstatus
from core.context_assembler import prompt_context_summary
from llm.base import LLMClient
from llm.tools import APPLY_PATCHES_TOOL
from modes.base import BaseMode, Flag, ModeContext, ModeOutput, translate_dialog_history

# 6 Pflicht-Slots per SDD 5.3 and FR-B-00 (ADR CR-003: consolidated from 9)
# prozesszusammenfassung removed — redundant cognitive load, LLM wasted turns on it
PFLICHT_SLOTS: dict[str, str] = {
    "prozessausloeser": "Prozessauslöser",
    "prozessziel": "Prozessziel",
    "prozessbeschreibung": "Prozessbeschreibung",
    "entscheidungen_und_schleifen": "Entscheidungen und Schleifen",
    "beteiligte_systeme": "Beteiligte Systeme",
    "variablen_und_daten": "Variablen und Daten",
}

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "exploration.md"


def _load_system_prompt() -> str:
    """Load the German system prompt from prompts/exploration.md."""
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _build_init_patches(existing_slot_ids: set[str]) -> list[dict]:  # type: ignore[type-arg]
    """Build add patches for all missing Pflicht-Slots (DEBT-01, FR-B-00)."""
    patches: list[dict] = []  # type: ignore[type-arg]
    for slot_id, titel in PFLICHT_SLOTS.items():
        if slot_id not in existing_slot_ids:
            slot = ExplorationSlot(
                slot_id=slot_id,
                titel=titel,
                inhalt="",
                completeness_status=CompletenessStatus.leer,
            )
            patches.append(
                {
                    "op": "add",
                    "path": f"/slots/{slot_id}",
                    "value": slot.model_dump(),
                }
            )
    return patches


def _build_slot_status(context: ModeContext) -> str:
    """Build a German slot status string for the system prompt."""
    lines: list[str] = []
    for slot_id, titel in PFLICHT_SLOTS.items():
        slot = context.exploration_artifact.slots.get(slot_id)
        if slot is None or not slot.inhalt:
            lines.append(f"- {titel} ({slot_id}) [leer]")
        else:
            status = slot.completeness_status.value
            lines.append(f"- {titel} ({slot_id}) [{status}]: {slot.inhalt}")
    return "\n".join(lines)




class ExplorationMode(BaseMode):
    """Explorationsmodus (SDD 6.6.1) — real LLM implementation.

    The LLM decides the phasenstatus directly without guardrails.
    """

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm_client = llm_client

    async def call(self, context: ModeContext) -> ModeOutput:
        """Process one exploration turn via the LLM."""
        existing_ids = set(context.exploration_artifact.slots.keys())
        init_patches = _build_init_patches(existing_ids)

        if self._llm_client is None:
            return ModeOutput(
                nutzeraeusserung="[ExplorationMode] Kein LLM-Client konfiguriert.",
                patches=init_patches,
                phasenstatus=Phasenstatus.in_progress,
                flags=[],
            )

        # Build system prompt
        context_summary = prompt_context_summary(context)
        slot_status = _build_slot_status(context)
        system_prompt = _load_system_prompt()
        system_prompt = system_prompt.replace("{context_summary}", context_summary)
        system_prompt = system_prompt.replace("{slot_status}", slot_status)


        messages = translate_dialog_history(context.dialog_history)

        response = await self._llm_client.complete(
            system=system_prompt,
            messages=messages,
            tools=[APPLY_PATCHES_TOOL],
            tool_choice={"type": "tool", "name": "apply_patches"},
        )

        llm_patches = [p for p in (response.tool_input.get("patches") or []) if isinstance(p, dict)]
        all_patches = init_patches + llm_patches

        # LLM decides phasenstatus directly — no guardrails
        raw_status = response.tool_input.get("phasenstatus", "in_progress")
        try:
            llm_phasenstatus = Phasenstatus(raw_status)
        except ValueError:
            llm_phasenstatus = Phasenstatus.in_progress

        phasenstatus = llm_phasenstatus

        flags: list[Flag] = []
        if phasenstatus == Phasenstatus.phase_complete:
            flags.append(Flag.phase_complete)

        return ModeOutput(
            nutzeraeusserung=response.nutzeraeusserung,
            patches=all_patches,
            phasenstatus=phasenstatus,
            flags=flags,
            debug_request=response.debug_request,
            usage=response.usage,
        )
