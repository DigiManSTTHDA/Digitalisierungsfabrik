"""Moderator — steuert Phasenwechsel, Eskalationen und Nutzerdialog (SDD 6.6.5).

Aktivierung durch Flags phase_complete, escalate oder blocked, oder bei Systemstart.
Der Moderator verändert keine Artefakte direkt (SDD 6.6.5).
Er kommuniziert seine Entscheidung über Flags an den Orchestrator:
- advance_phase: Nutzer hat Phasenwechsel bestätigt
- return_to_mode: Nutzer will zum Arbeitsmodus (zurück oder erstmalig)
"""

from __future__ import annotations

from pathlib import Path

import structlog

from artifacts.models import Phasenstatus
from core.context_assembler import prompt_context_summary
from llm.base import LLMClient
from modes.base import BaseMode, Flag, ModeContext, ModeOutput

logger = structlog.get_logger()

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "moderator.md"

# Minimal tool so the LLM can signal structured intent (stay vs. hand off).
# Kept private here — only the Moderator needs this, not other modes.
_MODERATOR_TOOL: dict = {  # type: ignore[type-arg]
    "name": "moderator_antwort",
    "description": ("Moderator-Antwort mit Steuerungssignal."),
    "input_schema": {
        "type": "object",
        "properties": {
            "nutzeraeusserung": {
                "type": "string",
                "description": "Deine Antwort an den Nutzer.",
            },
            "uebergabe": {
                "type": "boolean",
                "description": (
                    "true = Nutzer hat bestätigt, Kontrolle an den Arbeitsmodus übergeben. "
                    "false = Im Moderator bleiben (Standard). "
                    "NUR true setzen wenn der Nutzer EXPLIZIT bestätigt hat."
                ),
            },
        },
        "required": ["nutzeraeusserung", "uebergabe"],
    },
}


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


def _determine_flags(uebergabe: bool, context: ModeContext) -> list[Flag]:
    """Map the LLM's handoff signal to the right flag based on context.

    Uses existing flag semantics — no new flags, no new concepts:
    - advance_phase: when phase_complete was signalled (Phasenwechsel)
    - return_to_mode: all other handoffs (system start, escalation recovery)
    """
    if not uebergabe:
        return []
    # If we're in moderator because of phase_complete, advance to next phase
    if context.working_memory.phasenstatus == Phasenstatus.phase_complete:
        return [Flag.advance_phase]
    # All other cases: return to previous mode (or phase primary if none)
    return [Flag.return_to_mode]


class Moderator(BaseMode):
    """Moderator (SDD 6.6.5).

    Ziel: Orientierung des Nutzers bei Phasenübergängen, Eskalationen und Problemen.
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

        response = await self._llm.complete(
            system=system_prompt,
            messages=messages,
            tools=[_MODERATOR_TOOL],
            tool_choice=None,
        )

        uebergabe = bool(response.tool_input.get("uebergabe", False))
        flags = _determine_flags(uebergabe, context)

        logger.info(
            "moderator.response",
            has_text=bool(response.nutzeraeusserung),
            uebergabe=uebergabe,
            flags=[f.value for f in flags],
        )

        # Preserve the phasenstatus from the previous mode. The Moderator doesn't
        # produce artifacts — it shouldn't overwrite the phase status that triggered
        # its activation. Without this, a phase_complete signal would be lost after
        # the first Moderator turn, making it impossible to advance the phase.
        return ModeOutput(
            nutzeraeusserung=response.nutzeraeusserung,
            patches=[],
            phasenstatus=context.working_memory.phasenstatus,
            flags=flags,
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
