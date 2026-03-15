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
from modes.base import BaseMode, Flag, ModeContext, ModeOutput

# 8 Pflicht-Slots per SDD 5.3 and FR-B-00
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
    """Build a German slot status string for the system prompt.

    Always shows all 8 Pflicht-Slots. Slots not yet in the artifact are
    shown as 'leer' — they will be initialized before LLM patches are applied,
    so the LLM can safely use 'replace' on all sub-fields.
    """
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
            continue  # Zusammenfassung kommt zuletzt
        slot = context.exploration_artifact.slots.get(slot_id)
        if slot is None or not slot.inhalt or slot.completeness_status == CompletenessStatus.leer:
            return slot_id, titel
    # Check prozesszusammenfassung last
    slot = context.exploration_artifact.slots.get("prozesszusammenfassung")
    if slot is None or not slot.inhalt or slot.completeness_status == CompletenessStatus.leer:
        return "prozesszusammenfassung", "Prozesszusammenfassung"
    return None


def _merge_slot_patches(
    patches: list[dict],  # type: ignore[type-arg]
    context: ModeContext,
) -> list[dict]:  # type: ignore[type-arg]
    """Post-process LLM patches: merge new content with existing slot content.

    Instead of requiring the LLM to copy-paste existing content into replace
    values, the code handles merging. The LLM only needs to write NEW facts.
    This is critical for smaller/weaker models that can't reliably consolidate.
    """
    merged: list[dict] = []  # type: ignore[type-arg]
    for patch in patches:
        path = patch.get("path", "")
        op = patch.get("op", "")
        value = patch.get("value", "")

        # Only merge inhalt patches — let completeness_status patches through as-is
        if (
            op == "replace"
            and path.endswith("/inhalt")
            and isinstance(value, str)
            and value.strip()
        ):
            # Extract slot_id from path like /slots/prozessziel/inhalt
            parts = path.strip("/").split("/")
            if len(parts) == 3 and parts[0] == "slots":
                slot_id = parts[1]
                slot = context.exploration_artifact.slots.get(slot_id)
                existing = slot.inhalt.strip() if slot and slot.inhalt else ""

                if existing and value.strip() != existing:
                    # Check if the new value already contains the old content
                    # (LLM followed the instruction). If not, prepend it.
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


def _compute_phasenstatus_with_patches(
    context: ModeContext,
    patches: list[dict],  # type: ignore[type-arg]
) -> Phasenstatus:
    """Determine phase status accounting for patches this turn will apply.

    Builds a projected view of slot completeness: starts from the current
    artifact state, then overlays any completeness_status patches from the
    LLM. This way, if the LLM marks the last slot as 'vollstaendig' in
    this turn, we can immediately return phase_complete.
    """
    # Start with current statuses
    projected: dict[str, CompletenessStatus] = {}
    for slot_id in PFLICHT_SLOTS:
        slot = context.exploration_artifact.slots.get(slot_id)
        projected[slot_id] = slot.completeness_status if slot else CompletenessStatus.leer

    # Overlay patches that set completeness_status
    for patch in patches:
        path = patch.get("path", "")
        if path.endswith("/completeness_status") and patch.get("op") == "replace":
            parts = path.strip("/").split("/")
            if len(parts) == 3 and parts[0] == "slots" and parts[1] in PFLICHT_SLOTS:
                try:
                    projected[parts[1]] = CompletenessStatus(patch["value"])
                except ValueError:
                    pass
        # Also: if an inhalt patch exists for a slot that is currently leer,
        # promote it to at least teilweise (the LLM wrote content).
        if path.endswith("/inhalt") and patch.get("op") == "replace" and patch.get("value"):
            parts = path.strip("/").split("/")
            if len(parts) == 3 and parts[0] == "slots" and parts[1] in PFLICHT_SLOTS:
                if projected.get(parts[1]) == CompletenessStatus.leer:
                    projected[parts[1]] = CompletenessStatus.teilweise

    # Evaluate
    has_leer = any(s == CompletenessStatus.leer for s in projected.values())
    if has_leer:
        return Phasenstatus.in_progress

    all_complete = all(
        s in (CompletenessStatus.vollstaendig, CompletenessStatus.nutzervalidiert)
        for s in projected.values()
    )
    if all_complete:
        return Phasenstatus.phase_complete
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

        # Deterministic next-question hint — helps weaker models stay on track
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

        # Build messages from dialog history
        messages = _translate_dialog_history(context.dialog_history)

        # Call LLM
        response = await self._llm_client.complete(
            system=system_prompt,
            messages=messages,
            tools=[APPLY_PATCHES_TOOL],
            tool_choice={"type": "tool", "name": "apply_patches"},
        )

        # Combine init patches + LLM patches (with auto-merge of existing content)
        llm_patches = response.tool_input.get("patches", [])
        llm_patches = _merge_slot_patches(llm_patches, context)
        all_patches = init_patches + llm_patches

        # Compute phase status — must account for patches THIS turn will apply.
        # Build a projected view of slot statuses after patches are applied.
        phasenstatus = _compute_phasenstatus_with_patches(context, llm_patches)
        flags: list[Flag] = []
        if phasenstatus == Phasenstatus.phase_complete:
            flags.append(Flag.phase_complete)

        return ModeOutput(
            nutzeraeusserung=response.nutzeraeusserung,
            patches=all_patches,
            phasenstatus=phasenstatus,
            flags=flags,
        )
