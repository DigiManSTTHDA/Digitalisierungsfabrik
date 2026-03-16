"""Validierungsmodus — prüft Konsistenz, Vollständigkeit und EMMA-Kompatibilität (SDD 6.6.4).

Performs deterministic pre-checks (referential integrity, EMMA compatibility,
completeness) and delegates consistency/content checks to the LLM.

SDD references: 6.6.4 (Validierungsmodus), FR-C-01 (Inkonsistenz), FR-C-03 (EMMA),
FR-C-08 (Schweregrad), FR-C-09 (Korrekturschleife), ADR-007.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from artifacts.models import (
    Phasenstatus,
    Schweregrad,
    Validierungsbefund,
    Validierungsbericht,
)
from core.context_assembler import emma_action_catalog_text, prompt_context_summary
from llm.base import LLMClient
from modes.base import BaseMode, Flag, ModeContext, ModeOutput, translate_dialog_history
from modes.validation_checks import (
    build_algorithm_content,
    build_exploration_content,
    build_structure_content,
    deterministic_checks,
)

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "validation.md"

# Tool schema for structured validation report (ADR-007)
_BEFUND_PROPS: dict = {  # type: ignore[type-arg]
    "befund_id": {"type": "string"},
    "schweregrad": {"type": "string", "enum": ["kritisch", "warnung", "hinweis"]},
    "beschreibung": {"type": "string"},
    "betroffene_slots": {"type": "array", "items": {"type": "string"}},
    "artefakttyp": {"type": "string", "enum": ["exploration", "struktur", "algorithmus"]},
    "empfehlung": {"type": "string"},
}
PRODUCE_VALIDATION_REPORT_TOOL: dict = {  # type: ignore[type-arg]
    "name": "produce_validation_report",
    "description": "Erstellt einen strukturierten Validierungsbericht mit Befunden und Schweregrad.",
    "input_schema": {
        "type": "object",
        "properties": {
            "nutzeraeusserung": {
                "type": "string",
                "description": "Deutsche Zusammenfassung der Validierungsergebnisse.",
            },
            "befunde": {
                "type": "array",
                "description": "Liste der Validierungsbefunde",
                "items": {
                    "type": "object",
                    "properties": _BEFUND_PROPS,
                    "required": list(_BEFUND_PROPS.keys()),
                },
            },
        },
        "required": ["nutzeraeusserung", "befunde"],
    },
}


def _load_system_prompt() -> str:
    return _PROMPT_PATH.read_text(encoding="utf-8")


class ValidationMode(BaseMode):
    """Validierungsmodus (SDD 6.6.4) — deterministic + LLM validation."""

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm_client = llm_client

    async def call(self, context: ModeContext) -> ModeOutput:
        """Run validation and produce a Validierungsbericht."""
        det_befunde = deterministic_checks(context)
        llm_befunde: list[Validierungsbefund] = []
        nutzeraeusserung = ""

        if self._llm_client is not None:
            try:
                llm_befunde, nutzeraeusserung = await self._llm_validation(context)
            except (ValueError, RuntimeError):
                nutzeraeusserung = (
                    "Fehler bei der LLM-basierten Validierung. "
                    "Deterministische Prüfungen wurden durchgeführt."
                )

        all_befunde = det_befunde + llm_befunde
        has_kritisch = any(b.schweregrad == Schweregrad.kritisch for b in all_befunde)
        prev = context.working_memory.validierungsbericht
        durchlauf_nr = (prev.durchlauf_nr + 1) if prev else 1

        bericht = Validierungsbericht(
            befunde=all_befunde,
            erstellt_am=datetime.now(tz=UTC),
            durchlauf_nr=durchlauf_nr,
            ist_bestanden=not has_kritisch,
        )
        if not nutzeraeusserung:
            nutzeraeusserung = self._format_summary(bericht)

        return ModeOutput(
            nutzeraeusserung=nutzeraeusserung,
            patches=[],  # SDD 6.6.4: keine Schreibrechte
            phasenstatus=Phasenstatus.phase_complete,
            flags=[Flag.phase_complete],
            validierungsbericht=bericht,
        )

    async def _llm_validation(self, context: ModeContext) -> tuple[list[Validierungsbefund], str]:
        """Run LLM-based validation checks."""
        assert self._llm_client is not None
        system_prompt = _load_system_prompt()
        system_prompt = system_prompt.replace("{context_summary}", prompt_context_summary(context))
        system_prompt = system_prompt.replace("{emma_catalog}", emma_action_catalog_text())
        system_prompt = system_prompt.replace(
            "{exploration_content}", build_exploration_content(context)
        )
        system_prompt = system_prompt.replace(
            "{structure_content}", build_structure_content(context)
        )
        system_prompt = system_prompt.replace(
            "{algorithm_content}", build_algorithm_content(context)
        )

        messages = translate_dialog_history(context.dialog_history)
        if not messages:
            messages = [{"role": "user", "content": "Bitte validiere die Artefakte."}]

        response = await self._llm_client.complete(
            system=system_prompt,
            messages=messages,
            tools=[PRODUCE_VALIDATION_REPORT_TOOL],
            tool_choice={"type": "tool", "name": "produce_validation_report"},
        )

        befunde: list[Validierungsbefund] = []
        for rb in response.tool_input.get("befunde", []):
            if isinstance(rb, dict):
                try:
                    befunde.append(Validierungsbefund(**rb))
                except (ValueError, TypeError):
                    pass  # Skip malformed findings
        return befunde, response.nutzeraeusserung

    def _format_summary(self, bericht: Validierungsbericht) -> str:
        """Format a German summary of the validation report."""
        if not bericht.befunde:
            return (
                "Validierung abgeschlossen. Keine Befunde — alle Artefakte "
                "sind konsistent und vollständig."
            )
        kritisch = sum(1 for b in bericht.befunde if b.schweregrad == Schweregrad.kritisch)
        warnung = sum(1 for b in bericht.befunde if b.schweregrad == Schweregrad.warnung)
        hinweis = sum(1 for b in bericht.befunde if b.schweregrad == Schweregrad.hinweis)
        lines = [
            f"Validierung abgeschlossen (Durchlauf {bericht.durchlauf_nr}).",
            f"Ergebnis: {len(bericht.befunde)} Befunde gefunden.",
        ]
        if kritisch:
            lines.append(f"  - {kritisch} kritisch")
        if warnung:
            lines.append(f"  - {warnung} Warnungen")
        if hinweis:
            lines.append(f"  - {hinweis} Hinweise")
        if bericht.ist_bestanden:
            lines.append("Status: Bestanden — keine kritischen Befunde.")
        else:
            lines.append("Status: Nicht bestanden — kritische Befunde müssen behoben werden.")
        return "\n".join(lines)
