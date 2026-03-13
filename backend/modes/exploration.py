"""Explorationsmodus — erfasst implizites Prozesswissen des Nutzers (SDD 6.6.1).

Calls the LLM via LLMClient to conduct a structured interview, filling the
8 Pflicht-Slots of the ExplorationArtifact through dialog with the user.

SDD references: 6.6.1 (Explorationsmodus), FR-B-00 (Pflicht-Slots),
FR-A-02 (Tool Use API), FR-A-08 (Systemsprache Deutsch).
"""

from __future__ import annotations

from pathlib import Path

from artifacts.models import CompletenessStatus, ExplorationSlot, Phasenstatus
from core.context_assembler import prompt_context_summary
from llm.base import LLMClient
from llm.tools import APPLY_PATCHES_TOOL
from modes.base import BaseMode, ModeContext, ModeOutput

# 8 Pflicht-Slots per SDD 5.3 and FR-B-00
PFLICHT_SLOTS: dict[str, str] = {
    "prozessausloeser": "Prozessauslöser",
    "prozessziel": "Prozessziel",
    "scope": "Scope",
    "beteiligte_systeme": "Beteiligte Systeme",
    "umgebung": "Umgebung",
    "randbedingungen": "Randbedingungen",
    "ausnahmen": "Ausnahmen",
    "prozesszusammenfassung": "Prozesszusammenfassung",
}

# Path to the German system prompt
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
        if slot is None:
            lines.append(f"- {titel}: nicht initialisiert")
        else:
            status = slot.completeness_status.value
            inhalt_preview = slot.inhalt[:80] + "..." if len(slot.inhalt) > 80 else slot.inhalt
            lines.append(f"- {titel} [{status}]: {inhalt_preview or '(leer)'}")
    return "\n".join(lines)


def _translate_dialog_history(dialog_history: list[dict]) -> list[dict]:  # type: ignore[type-arg]
    """Translate internal dialog history to Anthropic messages format."""
    messages: list[dict] = []  # type: ignore[type-arg]
    for entry in dialog_history:
        role = entry.get("role", "user")
        inhalt = entry.get("inhalt", "")
        if role in ("user", "assistant") and inhalt:
            messages.append({"role": role, "content": inhalt})
    return messages


def _compute_phasenstatus(context: ModeContext) -> Phasenstatus:
    """Determine phase status based on Pflicht-Slot completeness."""
    for slot_id in PFLICHT_SLOTS:
        slot = context.exploration_artifact.slots.get(slot_id)
        if slot is None or slot.completeness_status == CompletenessStatus.leer:
            return Phasenstatus.in_progress
    return Phasenstatus.nearing_completion


class ExplorationMode(BaseMode):
    """Explorationsmodus (SDD 6.6.1) — real LLM implementation.

    Conducts a structured interview via the LLM to fill the 8 Pflicht-Slots
    of the ExplorationArtifact. On the first turn, initializes all missing
    Pflicht-Slots with empty ExplorationSlot objects.
    """

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm_client = llm_client

    async def call(self, context: ModeContext) -> ModeOutput:
        """Process one exploration turn via the LLM."""
        # Build initialization patches for missing Pflicht-Slots (DEBT-01)
        existing_ids = set(context.exploration_artifact.slots.keys())
        init_patches = _build_init_patches(existing_ids)

        # If no LLM client, return stub with init patches only
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

        # Build messages from dialog history
        messages = _translate_dialog_history(context.dialog_history)

        # Call LLM
        response = await self._llm_client.complete(
            system=system_prompt,
            messages=messages,
            tools=[APPLY_PATCHES_TOOL],
            tool_choice={"type": "tool", "name": "apply_patches"},
        )

        # Combine init patches + LLM patches
        llm_patches = response.tool_input.get("patches", [])
        all_patches = init_patches + llm_patches

        # Compute phase status
        phasenstatus = _compute_phasenstatus(context)

        return ModeOutput(
            nutzeraeusserung=response.nutzeraeusserung,
            patches=all_patches,
            phasenstatus=phasenstatus,
            flags=[],
        )
