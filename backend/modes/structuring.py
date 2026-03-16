"""Strukturierungsmodus — überführt Prozess in Strukturartefakt (SDD 6.6.2).

Calls the LLM via LLMClient to decompose the process from the Exploration
Artifact into Strukturschritte with types, sequences, and decision points.

The LLM decides the phasenstatus. Deterministic guardrails prevent premature
phase_complete when no Strukturschritte exist yet.

SDD references: 6.6.2 (Strukturierungsmodus), FR-B-01 (Strukturartefakt),
FR-A-04 (Ausnahmen), FR-A-08 (Systemsprache Deutsch), FR-B-09 (RFC 6902).
"""

from __future__ import annotations

from pathlib import Path

from artifacts.models import CompletenessStatus, Phasenstatus
from core.context_assembler import prompt_context_summary
from llm.base import LLMClient
from llm.tools import APPLY_PATCHES_TOOL
from modes.base import BaseMode, Flag, ModeContext, ModeOutput, translate_dialog_history

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "structuring.md"


def _load_system_prompt() -> str:
    """Load the German system prompt from prompts/structuring.md."""
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _build_exploration_content(context: ModeContext) -> str:
    """Build read-only exploration artifact content for the system prompt."""
    lines: list[str] = []
    for slot_id, slot in context.exploration_artifact.slots.items():
        if slot.inhalt:
            lines.append(f"### {slot.titel} ({slot_id})\n{slot.inhalt}")
    return "\n\n".join(lines) if lines else "(Explorationsartefakt ist leer)"


def _build_slot_status(context: ModeContext) -> str:
    """Build a German status string showing current Strukturschritte."""
    schritte = context.structure_artifact.schritte
    if not schritte:
        return "(Noch keine Strukturschritte vorhanden)"

    lines: list[str] = []
    for sid, schritt in sorted(schritte.items(), key=lambda x: x[1].reihenfolge):
        status = schritt.completeness_status.value
        typ = schritt.typ.value
        nachf = ", ".join(schritt.nachfolger) if schritt.nachfolger else "—"
        lines.append(
            f"- [{schritt.reihenfolge}] {schritt.titel} ({sid}) [{typ}] [{status}] → {nachf}"
        )

    zusammenfassung = context.structure_artifact.prozesszusammenfassung
    if zusammenfassung:
        lines.insert(0, f"Prozesszusammenfassung: {zusammenfassung}\n")

    return "\n".join(lines)


def _apply_guardrails(llm_phasenstatus: Phasenstatus, context: ModeContext) -> Phasenstatus:
    """Deterministic guardrails on the LLM's phasenstatus decision.

    BLOCK phase_complete if no Strukturschritte exist or any has leer status.
    """
    schritte = context.structure_artifact.schritte
    if not schritte:
        if llm_phasenstatus == Phasenstatus.phase_complete:
            return Phasenstatus.in_progress
        return llm_phasenstatus

    has_leer = any(s.completeness_status == CompletenessStatus.leer for s in schritte.values())
    if llm_phasenstatus == Phasenstatus.phase_complete and has_leer:
        return Phasenstatus.nearing_completion

    return llm_phasenstatus


class StructuringMode(BaseMode):
    """Strukturierungsmodus (SDD 6.6.2) — real LLM implementation.

    The LLM decides the phasenstatus. Guardrails prevent premature completion.
    """

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm_client = llm_client

    async def call(self, context: ModeContext) -> ModeOutput:
        """Process one structuring turn via the LLM."""
        if self._llm_client is None:
            return ModeOutput(
                nutzeraeusserung="[StructuringMode] Kein LLM-Client konfiguriert.",
                patches=[],
                phasenstatus=Phasenstatus.in_progress,
                flags=[],
            )

        context_summary = prompt_context_summary(context)
        exploration_content = _build_exploration_content(context)
        slot_status = _build_slot_status(context)

        system_prompt = _load_system_prompt()
        system_prompt = system_prompt.replace("{context_summary}", context_summary)
        system_prompt = system_prompt.replace("{exploration_content}", exploration_content)
        system_prompt = system_prompt.replace("{slot_status}", slot_status)

        messages = translate_dialog_history(context.dialog_history)

        response = await self._llm_client.complete(
            system=system_prompt,
            messages=messages,
            tools=[APPLY_PATCHES_TOOL],
            tool_choice={"type": "tool", "name": "apply_patches"},
        )

        patches = response.tool_input.get("patches", [])

        # LLM decides phasenstatus, guardrails enforce hard constraints
        raw_status = response.tool_input.get("phasenstatus", "in_progress")
        try:
            llm_phasenstatus = Phasenstatus(raw_status)
        except ValueError:
            llm_phasenstatus = Phasenstatus.in_progress

        phasenstatus = _apply_guardrails(llm_phasenstatus, context)

        flags: list[Flag] = []
        if phasenstatus == Phasenstatus.phase_complete:
            flags.append(Flag.phase_complete)

        return ModeOutput(
            nutzeraeusserung=response.nutzeraeusserung,
            patches=patches,
            phasenstatus=phasenstatus,
            flags=flags,
        )
