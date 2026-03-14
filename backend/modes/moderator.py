"""Moderator — steuert Phasenwechsel, Eskalationen und Nutzerdialog (SDD 6.6.5).

Aktivierung durch Flags phase_complete, escalate oder blocked.
Der Moderator verändert keine Artefakte direkt (SDD 6.6.5).
Er kommuniziert seine Entscheidung über Flags an den Orchestrator:
- advance_phase: Nutzer hat Phasenwechsel bestätigt
- return_to_mode: Nutzer will beim aktuellen Modus bleiben
"""

from __future__ import annotations

from pathlib import Path

import structlog

from artifacts.models import Phasenstatus
from core.context_assembler import prompt_context_summary
from llm.base import LLMClient
from modes.base import BaseMode, ModeContext, ModeOutput

logger = structlog.get_logger()

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "moderator.md"


def _load_system_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _build_moderator_prompt(context: ModeContext) -> str:
    """Build the system prompt with injected context values."""
    template = _load_system_prompt()
    summary = prompt_context_summary(context)

    wm = context.working_memory
    return (
        template.replace("{context_summary}", summary)
        .replace("{aktive_phase}", context.aktive_phase.value)
        .replace("{vorheriger_modus}", wm.vorheriger_modus or "–")
        .replace("{befuellte_slots}", str(wm.befuellte_slots))
        .replace("{bekannte_slots}", str(wm.bekannte_slots))
        .replace("{phasenstatus}", wm.phasenstatus.value)
    )


class Moderator(BaseMode):
    """Moderator (SDD 6.6.5).

    Ziel: Orientierung des Nutzers bei Phasenübergängen, Eskalationen und Problemen.
    Aktivierung durch Flags phase_complete, escalate oder blocked.

    Produziert KEINE Patches — nur eine Nutzeräußerung und Steuerungsflags.
    """

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm = llm_client

    async def call(self, context: ModeContext) -> ModeOutput:
        if self._llm is None:
            return self._stub_response(context)

        system_prompt = _build_moderator_prompt(context)
        messages = [
            {"role": entry["role"], "content": entry["inhalt"]} for entry in context.dialog_history
        ]

        # Moderator does NOT use tools — no patches, only text response
        response = await self._llm.complete(
            system=system_prompt,
            messages=messages,
            tools=None,
            tool_choice=None,
        )

        logger.info(
            "moderator.response",
            has_text=bool(response.nutzeraeusserung),
        )

        # Moderator NEVER produces patches (SDD 6.6.5)
        return ModeOutput(
            nutzeraeusserung=response.nutzeraeusserung,
            patches=[],
            phasenstatus=Phasenstatus.in_progress,
            flags=[],
        )

    def _stub_response(self, context: ModeContext) -> ModeOutput:
        """Deterministic response when no LLM is available (for testing)."""
        wm = context.working_memory
        phase = context.aktive_phase.value
        filled = wm.befuellte_slots
        total = wm.bekannte_slots

        text = (
            f"Moderator: Phase '{phase}' — {filled}/{total} Slots befüllt. "
            f"Vorheriger Modus: {wm.vorheriger_modus or 'keiner'}."
        )
        return ModeOutput(
            nutzeraeusserung=text,
            patches=[],
            phasenstatus=Phasenstatus.in_progress,
            flags=[],
        )
