"""Strukturierungsmodus — überführt Prozess in Strukturartefakt (SDD 6.6.2).

Calls the LLM via LLMClient to decompose the process from the Exploration
Artifact into Strukturschritte with types, sequences, and decision points.

SDD references: 6.6.2 (Strukturierungsmodus), FR-B-01 (Strukturartefakt),
FR-A-04 (Ausnahmen), FR-A-08 (Systemsprache Deutsch), FR-B-09 (RFC 6902).
"""

from __future__ import annotations

from pathlib import Path

from artifacts.models import CompletenessStatus, Phasenstatus
from core.context_assembler import prompt_context_summary
from llm.base import LLMClient
from llm.tools import APPLY_PATCHES_TOOL
from modes.base import BaseMode, Flag, ModeContext, ModeOutput

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
    """Determine phase status from structure artifact completeness (SDD 6.6.2).

    - in_progress: no schritte yet, or any schritt is leer
    - nearing_completion: all schritte have content but not all nutzervalidiert
    - phase_complete: all schritte are vollstaendig or nutzervalidiert
    """
    schritte = context.structure_artifact.schritte
    if not schritte:
        return Phasenstatus.in_progress

    statuses = [s.completeness_status for s in schritte.values()]

    if any(s == CompletenessStatus.leer for s in statuses):
        return Phasenstatus.in_progress

    if all(
        s in (CompletenessStatus.vollstaendig, CompletenessStatus.nutzervalidiert) for s in statuses
    ):
        return Phasenstatus.phase_complete

    return Phasenstatus.nearing_completion


class StructuringMode(BaseMode):
    """Strukturierungsmodus (SDD 6.6.2) — real LLM implementation.

    Decomposes the process from the Exploration Artifact into Strukturschritte
    with types, sequences, decision points, loops, and exceptions.
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

        # Build system prompt with context
        context_summary = prompt_context_summary(context)
        exploration_content = _build_exploration_content(context)
        slot_status = _build_slot_status(context)

        system_prompt = _load_system_prompt()
        system_prompt = system_prompt.replace("{context_summary}", context_summary)
        system_prompt = system_prompt.replace("{exploration_content}", exploration_content)
        system_prompt = system_prompt.replace("{slot_status}", slot_status)

        # Build messages from dialog history
        messages = _translate_dialog_history(context.dialog_history)

        # Call LLM with Tool Use (SDD 6.5.2)
        response = await self._llm_client.complete(
            system=system_prompt,
            messages=messages,
            tools=[APPLY_PATCHES_TOOL],
            tool_choice={"type": "tool", "name": "apply_patches"},
        )

        patches = response.tool_input.get("patches", [])

        # Compute phase status from current artifact state
        phasenstatus = _compute_phasenstatus(context)
        flags: list[Flag] = []
        if phasenstatus == Phasenstatus.phase_complete:
            flags.append(Flag.phase_complete)

        return ModeOutput(
            nutzeraeusserung=response.nutzeraeusserung,
            patches=patches,
            phasenstatus=phasenstatus,
            flags=flags,
        )
