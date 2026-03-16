"""Explorationsmodus — erfasst implizites Prozesswissen des Nutzers (SDD 6.6.1).

Calls the LLM via LLMClient to conduct a structured interview, filling the
9 Pflicht-Slots of the ExplorationArtifact through dialog with the user.

The LLM decides the phasenstatus (in_progress / nearing_completion / phase_complete).
Deterministic guardrails prevent premature phase_complete when slots are still empty.

SDD references: 6.6.1 (Explorationsmodus), FR-B-00 (Pflicht-Slots),
FR-A-02 (Tool Use API), FR-A-08 (Systemsprache Deutsch).
"""

from __future__ import annotations

from pathlib import Path

from artifacts.models import CompletenessStatus, ExplorationSlot, Phasenstatus
from core.context_assembler import prompt_context_summary
from llm.base import LLMClient
from llm.tools import APPLY_PATCHES_TOOL
from modes.base import BaseMode, Flag, ModeContext, ModeOutput

# 9 Pflicht-Slots per SDD 5.3 and FR-B-00
PFLICHT_SLOTS: dict[str, str] = {
    "prozessausloeser": "Prozessauslöser",
    "prozessziel": "Prozessziel",
    "prozessbeschreibung": "Prozessbeschreibung",
    "scope": "Scope",
    "beteiligte_systeme": "Beteiligte Systeme",
    "umgebung": "Umgebung",
    "randbedingungen": "Randbedingungen",
    "ausnahmen": "Ausnahmen",
    "prozesszusammenfassung": "Prozesszusammenfassung",
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
            lines.append(f"- {titel} ({slot_id}) [LEER — braucht Informationen]")
        else:
            status = slot.completeness_status.value
            lines.append(f"- {titel} ({slot_id}) [{status}]: {slot.inhalt}")
    return "\n".join(lines)


def _next_empty_slot(context: ModeContext) -> tuple[str, str] | None:
    """Return (slot_id, titel) of the first empty/partial Pflicht-Slot, or None."""
    for slot_id, titel in PFLICHT_SLOTS.items():
        if slot_id == "prozesszusammenfassung":
            continue
        slot = context.exploration_artifact.slots.get(slot_id)
        if slot is None or not slot.inhalt or slot.completeness_status == CompletenessStatus.leer:
            return slot_id, titel
    slot = context.exploration_artifact.slots.get("prozesszusammenfassung")
    if slot is None or not slot.inhalt or slot.completeness_status == CompletenessStatus.leer:
        return "prozesszusammenfassung", "Prozesszusammenfassung"
    return None


def _merge_slot_patches(
    patches: list[dict],  # type: ignore[type-arg]
    context: ModeContext,
) -> list[dict]:  # type: ignore[type-arg]
    """Post-process LLM patches: merge new content with existing slot content."""
    merged: list[dict] = []  # type: ignore[type-arg]
    for patch in patches:
        path = patch.get("path", "")
        op = patch.get("op", "")
        value = patch.get("value", "")

        if (
            op == "replace"
            and path.endswith("/inhalt")
            and isinstance(value, str)
            and value.strip()
        ):
            parts = path.strip("/").split("/")
            if len(parts) == 3 and parts[0] == "slots":
                slot_id = parts[1]
                slot = context.exploration_artifact.slots.get(slot_id)
                existing = slot.inhalt.strip() if slot and slot.inhalt else ""

                if existing and value.strip() != existing:
                    if existing[:50] not in value:
                        merged_value = existing + " " + value.strip()
                        merged.append({"op": "replace", "path": path, "value": merged_value})
                        continue

        merged.append(patch)
    return merged


def _translate_dialog_history(dialog_history: list[dict]) -> list[dict]:  # type: ignore[type-arg]
    """Translate internal dialog history to Anthropic messages format."""
    messages: list[dict] = []  # type: ignore[type-arg]
    for entry in dialog_history:
        role = entry.get("role", "user")
        inhalt = entry.get("inhalt", "")
        if role in ("user", "assistant") and inhalt:
            messages.append({"role": role, "content": inhalt})
    return messages


def _apply_guardrails(
    llm_phasenstatus: Phasenstatus,
    context: ModeContext,
    patches: list[dict],  # type: ignore[type-arg]
) -> Phasenstatus:
    """Deterministic guardrails on top of the LLM's phasenstatus decision.

    The LLM decides the phasenstatus, but we enforce two hard constraints:

    1. BLOCK phase_complete if any Pflicht-Slot is still leer (no content).
       The LLM might be overconfident. Can't complete with empty slots.

    2. PROMOTE to phase_complete if the LLM says nearing_completion but all
       slots have content and no new content was written this turn. This catches
       LLMs that are too conservative and never say phase_complete even when
       the user is clearly done.
    """
    # Build projected slot states (current + patches about to be applied)
    projected: dict[str, CompletenessStatus] = {}
    for slot_id in PFLICHT_SLOTS:
        slot = context.exploration_artifact.slots.get(slot_id)
        projected[slot_id] = slot.completeness_status if slot else CompletenessStatus.leer

    for patch in patches:
        path = patch.get("path", "")
        if path.endswith("/completeness_status") and patch.get("op") == "replace":
            parts = path.strip("/").split("/")
            if len(parts) == 3 and parts[0] == "slots" and parts[1] in PFLICHT_SLOTS:
                try:
                    projected[parts[1]] = CompletenessStatus(patch["value"])
                except ValueError:
                    pass
        if path.endswith("/inhalt") and patch.get("op") == "replace" and patch.get("value"):
            parts = path.strip("/").split("/")
            if len(parts) == 3 and parts[0] == "slots" and parts[1] in PFLICHT_SLOTS:
                if projected.get(parts[1]) == CompletenessStatus.leer:
                    projected[parts[1]] = CompletenessStatus.teilweise

    has_leer = any(s == CompletenessStatus.leer for s in projected.values())

    # Guardrail 1: BLOCK — can't complete with empty or incomplete slots.
    # All slots must be at least vollstaendig for phase_complete.
    all_at_least_complete = all(
        s in (CompletenessStatus.vollstaendig, CompletenessStatus.nutzervalidiert)
        for s in projected.values()
    )
    if llm_phasenstatus == Phasenstatus.phase_complete and not all_at_least_complete:
        if has_leer:
            return Phasenstatus.in_progress
        return Phasenstatus.nearing_completion

    # Guardrail 2: PROMOTE — LLM says nearing but all slots are nutzervalidiert
    # (FR-C-07: user must explicitly confirm each slot). If all are validated
    # and no new content was written, the conservative LLM just won't say phase_complete.
    all_validated = all(s == CompletenessStatus.nutzervalidiert for s in projected.values())
    if llm_phasenstatus == Phasenstatus.nearing_completion and all_validated:
        content_patches = [
            p for p in patches if p.get("path", "").endswith("/inhalt") and p.get("value")
        ]
        if not content_patches:
            return Phasenstatus.phase_complete

    return llm_phasenstatus


class ExplorationMode(BaseMode):
    """Explorationsmodus (SDD 6.6.1) — real LLM implementation.

    The LLM decides the phasenstatus. Deterministic guardrails prevent
    premature completion (empty slots) and help conservative LLMs that
    never signal phase_complete on their own.
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

        next_slot = _next_empty_slot(context)
        if next_slot:
            hint = (
                f"\n\n## Nächste Frage\n"
                f"Stelle eine Frage zum Slot **{next_slot[1]}** ({next_slot[0]}) — "
                f"dieser ist noch leer oder unvollständig.\n\n"
                f"WICHTIG: Auch wenn du eine Frage zu einem bestimmten Slot stellst, "
                f"extrahiere trotzdem ALLE neuen Informationen aus der Nutzernachricht "
                f"und schreibe Patches für ALLE betroffenen Slots."
            )
        else:
            hint = (
                "\n\n## Nächste Frage\n"
                "Alle Pflicht-Slots sind befüllt. Frage den Nutzer gezielt nach Details "
                "die noch fehlen könnten oder ob er Ergänzungen hat.\n\n"
                "WICHTIG: Auch wenn alle Slots befüllt sind — extrahiere WEITERHIN alle "
                "neuen Informationen aus jeder Nutzernachricht und schreibe Patches. "
                "Der Nutzer liefert oft wichtige Details in Nebensätzen. "
                "Jede neue Information muss in den passenden Slot geschrieben werden."
            )
        system_prompt += hint

        messages = _translate_dialog_history(context.dialog_history)

        response = await self._llm_client.complete(
            system=system_prompt,
            messages=messages,
            tools=[APPLY_PATCHES_TOOL],
            tool_choice={"type": "tool", "name": "apply_patches"},
        )

        llm_patches = response.tool_input.get("patches", [])
        llm_patches = _merge_slot_patches(llm_patches, context)
        all_patches = init_patches + llm_patches

        # LLM decides phasenstatus, guardrails enforce hard constraints
        raw_status = response.tool_input.get("phasenstatus", "in_progress")
        try:
            llm_phasenstatus = Phasenstatus(raw_status)
        except ValueError:
            llm_phasenstatus = Phasenstatus.in_progress

        phasenstatus = _apply_guardrails(llm_phasenstatus, context, llm_patches)

        flags: list[Flag] = []
        if phasenstatus == Phasenstatus.phase_complete:
            flags.append(Flag.phase_complete)

        return ModeOutput(
            nutzeraeusserung=response.nutzeraeusserung,
            patches=all_patches,
            phasenstatus=phasenstatus,
            flags=flags,
        )
