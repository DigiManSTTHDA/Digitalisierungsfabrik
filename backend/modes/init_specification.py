"""Init-Modus Spezifikation — Background-Initialisierung des Algorithmusartefakts (CR-006, CR-009).

Transformiert das Strukturartefakt vollständig in Algorithmusabschnitte,
bevor der Nutzer mit dem Dialog beginnt. Kein Dialog, keine Nutzeransprache.

CR-009: Single-Call statt Multi-Turn-Loop. Kein init_status mehr.
Validator-Feedback wird als Template-Variable {validator_feedback} injiziert.
"""

from __future__ import annotations

from pathlib import Path

from artifacts.models import Phasenstatus
from llm.base import LLMClient
from llm.tools import INIT_APPLY_PATCHES_TOOL
from modes.base import BaseMode, ModeContext, ModeOutput

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "init_specification.md"


def _load_system_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _build_slot_status(context: ModeContext) -> str:
    """Build structure artifact content for the system prompt."""
    schritte = context.structure_artifact.schritte
    if not schritte:
        return "(Strukturartefakt ist leer)"
    lines: list[str] = []
    zusammenfassung = context.structure_artifact.prozesszusammenfassung
    if zusammenfassung:
        lines.append(f"Prozesszusammenfassung: {zusammenfassung}\n")
    for sid, schritt in sorted(schritte.items(), key=lambda x: x[1].reihenfolge):
        typ = schritt.typ.value
        lines.append(f"- [{schritt.reihenfolge}] {schritt.titel} ({sid}) [{typ}]")
        if schritt.beschreibung:
            lines.append(f"  Beschreibung: {schritt.beschreibung}")
        if schritt.spannungsfeld:
            lines.append(f"  Spannungsfeld: {schritt.spannungsfeld}")
        if schritt.bedingung:
            lines.append(f"  Bedingung: {schritt.bedingung}")
        if schritt.regeln:
            regeln_text = "; ".join(
                f"{r.bedingung} → {r.nachfolger}" for r in schritt.regeln
            )
            lines.append(f"  Regeln: {regeln_text}")
        if schritt.schleifenkoerper:
            lines.append(f"  Schleifenkörper: {schritt.schleifenkoerper}")
        if schritt.abbruchbedingung:
            lines.append(f"  Abbruchbedingung: {schritt.abbruchbedingung}")
        if schritt.nachfolger:
            lines.append(f"  Nachfolger: {schritt.nachfolger}")
    return "\n".join(lines)


def _build_algorithm_status(context: ModeContext) -> str:
    """Build current algorithm artifact status for the system prompt."""
    abschnitte = context.algorithm_artifact.abschnitte
    if not abschnitte:
        return "(Noch keine Algorithmusabschnitte vorhanden)"
    lines: list[str] = []
    for aid, abschnitt in abschnitte.items():
        status = abschnitt.completeness_status.value
        n_aktionen = len(abschnitt.aktionen)
        lines.append(
            f"- {abschnitt.titel} ({aid}) [ref: {abschnitt.struktur_ref}] "
            f"[{status}] — {n_aktionen} Aktionen"
        )
    return "\n".join(lines)


class InitSpecificationMode(BaseMode):
    """Init-Modus für Spezifikation (CR-006, CR-009).

    Erbt von BaseMode, gibt ModeOutput zurück.
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
            )

        slot_status = _build_slot_status(context)
        algorithm_status = _build_algorithm_status(context)

        system_prompt = _load_system_prompt()
        system_prompt = system_prompt.replace("{slot_status}", slot_status)
        system_prompt = system_prompt.replace("{algorithm_status}", algorithm_status)

        # CR-009: Validator-Feedback injizieren
        feedback = context.validator_feedback or ""
        system_prompt = system_prompt.replace("{validator_feedback}", feedback)

        response = await self._llm_client.complete(
            system=system_prompt,
            messages=[{"role": "user", "content": "[Initialisierung starten]"}],
            tools=[INIT_APPLY_PATCHES_TOOL],
            tool_choice={"type": "tool", "name": "apply_patches"},
        )

        tool_input = response.tool_input or {}
        patches = [p for p in (tool_input.get("patches") or []) if isinstance(p, dict)]

        return ModeOutput(
            nutzeraeusserung="",
            patches=patches,
            phasenstatus=Phasenstatus.in_progress,
            flags=[],
            debug_request=response.debug_request,
            usage=response.usage,
        )
