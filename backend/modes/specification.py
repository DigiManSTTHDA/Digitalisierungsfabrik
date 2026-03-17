"""Spezifikationsmodus — präzisiert Strukturschritte mit EMMA-Aktionen (SDD 6.6.3).

Calls the LLM via LLMClient to assign EMMA actions to each Strukturschritt,
building the Algorithm Artifact incrementally through dialog with the user.

The LLM decides the phasenstatus. Deterministic guardrails prevent premature
phase_complete when Algorithmusabschnitte are missing or not yet nutzervalidiert.

SDD references: 6.6.3 (Spezifikationsmodus), FR-B-02 (Algorithmusartefakt),
FR-A-04 (Ausnahmen), FR-A-08 (Systemsprache Deutsch), FR-B-09 (RFC 6902).
"""

from __future__ import annotations

from pathlib import Path

from artifacts.models import CompletenessStatus, Phasenstatus
from core.context_assembler import emma_action_catalog_text, prompt_context_summary
from llm.base import LLMClient
from llm.tools import APPLY_PATCHES_TOOL
from modes.base import BaseMode, Flag, ModeContext, ModeOutput, translate_dialog_history

_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "specification.md"


def _load_system_prompt() -> str:
    """Load the German system prompt from prompts/specification.md."""
    return _PROMPT_PATH.read_text(encoding="utf-8")


def _build_structure_content(context: ModeContext) -> str:
    """Build read-only structure artifact content for the system prompt."""
    schritte = context.structure_artifact.schritte
    if not schritte:
        return "(Strukturartefakt ist leer)"

    lines: list[str] = []
    zusammenfassung = context.structure_artifact.prozesszusammenfassung
    if zusammenfassung:
        lines.append(f"Prozesszusammenfassung: {zusammenfassung}\n")

    for sid, schritt in sorted(schritte.items(), key=lambda x: x[1].reihenfolge):
        typ = schritt.typ.value
        nachf = ", ".join(schritt.nachfolger) if schritt.nachfolger else "—"
        lines.append(f"- [{schritt.reihenfolge}] {schritt.titel} ({sid}) [{typ}] → {nachf}")
        if schritt.beschreibung:
            lines.append(f"  Beschreibung: {schritt.beschreibung}")

    return "\n".join(lines)


def _build_algorithm_status(context: ModeContext) -> str:
    """Build current Algorithm Artifact status for the system prompt."""
    abschnitte = context.algorithm_artifact.abschnitte
    if not abschnitte:
        return "(Noch keine Algorithmusabschnitte vorhanden)"

    lines: list[str] = []
    zusammenfassung = context.algorithm_artifact.prozesszusammenfassung
    if zusammenfassung:
        lines.append(f"Prozesszusammenfassung: {zusammenfassung}\n")

    for aid, abschnitt in abschnitte.items():
        status = abschnitt.completeness_status.value
        algo_status = abschnitt.status.value
        n_aktionen = len(abschnitt.aktionen)
        lines.append(
            f"- {abschnitt.titel} ({aid}) [ref: {abschnitt.struktur_ref}] "
            f"[{status}] [{algo_status}] — {n_aktionen} Aktionen"
        )

    return "\n".join(lines)


def _build_first_turn_directive(context: ModeContext) -> str:
    """Inject a strong directive when the algorithm artifact is still empty.

    Returns an empty string if Algorithmusabschnitte already exist, so this
    directive only fires on the very first turn of the specification phase.
    Lists the Strukturschritte so the LLM has concrete targets with correct IDs.
    """
    if context.algorithm_artifact.abschnitte:
        return ""

    schritte = context.structure_artifact.schritte
    if not schritte:
        return (
            "\n\n## SOFORT-AKTION: Algorithmusartefakt ist leer\n\n"
            "Das Strukturartefakt ist ebenfalls leer. Bitte den Nutzer, "
            "zuerst die Strukturierungsphase abzuschließen."
        )

    schritt_liste = "\n".join(
        f"  - {schritt.titel} ({sid})"
        for sid, schritt in sorted(schritte.items(), key=lambda x: x[1].reihenfolge)
    )

    return (
        "\n\n## SOFORT-AKTION: Algorithmusartefakt ist leer\n\n"
        "Das Algorithmusartefakt enthält noch KEINE Abschnitte. "
        "Du befindest dich am Beginn der Spezifikationsphase.\n\n"
        f"Folgende Strukturschritte warten auf Algorithmusabschnitte:\n{schritt_liste}\n\n"
        "Deine PFLICHT in DIESEM Turn:\n"
        "1. Lege für JEDEN Strukturschritt einen Skelett-Abschnitt an "
        "(completeness_status='leer', status='ausstehend', aktionen={}).\n"
        "2. Beginne dann mit dem ersten Schritt: stelle die erste Operationalisierungsfrage.\n"
        "3. Warte NICHT — lege alle Skelett-Abschnitte JETZT an."
    )


def _apply_guardrails(llm_phasenstatus: Phasenstatus, context: ModeContext) -> Phasenstatus:
    """Deterministic guardrails on the LLM's phasenstatus decision (SDD 6.6.3).

    BLOCK phase_complete if:
    - No Algorithmusabschnitte exist yet
    - Any Strukturschritt has no corresponding Algorithmusabschnitt with
      completeness_status == nutzervalidiert
    """
    if llm_phasenstatus != Phasenstatus.phase_complete:
        return llm_phasenstatus

    abschnitte = context.algorithm_artifact.abschnitte
    if not abschnitte:
        return Phasenstatus.nearing_completion

    # Build set of struktur_refs that have nutzervalidiert Algorithmusabschnitte
    validated_refs: set[str] = set()
    for abschnitt in abschnitte.values():
        if abschnitt.completeness_status == CompletenessStatus.nutzervalidiert:
            validated_refs.add(abschnitt.struktur_ref)

    # Every Strukturschritt must have a validated Algorithmusabschnitt
    for schritt_id in context.structure_artifact.schritte:
        if schritt_id not in validated_refs:
            return Phasenstatus.nearing_completion

    return Phasenstatus.phase_complete


class SpecificationMode(BaseMode):
    """Spezifikationsmodus (SDD 6.6.3) — real LLM implementation.

    The LLM decides the phasenstatus. Guardrails prevent premature completion.
    """

    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self._llm_client = llm_client

    async def call(self, context: ModeContext) -> ModeOutput:
        """Process one specification turn via the LLM."""
        if self._llm_client is None:
            return ModeOutput(
                nutzeraeusserung="[SpecificationMode] Kein LLM-Client konfiguriert.",
                patches=[],
                phasenstatus=Phasenstatus.in_progress,
                flags=[],
            )

        context_summary = prompt_context_summary(context)
        structure_content = _build_structure_content(context)
        algorithm_status = _build_algorithm_status(context)
        emma_catalog = emma_action_catalog_text()

        system_prompt = _load_system_prompt()
        system_prompt = system_prompt.replace("{context_summary}", context_summary)
        system_prompt = system_prompt.replace("{structure_content}", structure_content)
        system_prompt = system_prompt.replace("{algorithm_status}", algorithm_status)
        system_prompt = system_prompt.replace("{emma_catalog}", emma_catalog)
        system_prompt = system_prompt.replace("{validierungsbericht}", "")
        system_prompt += _build_first_turn_directive(context)

        messages = translate_dialog_history(context.dialog_history)

        response = await self._llm_client.complete(
            system=system_prompt,
            messages=messages,
            tools=[APPLY_PATCHES_TOOL],
            tool_choice={"type": "tool", "name": "apply_patches"},
        )

        patches = [p for p in (response.tool_input.get("patches") or []) if isinstance(p, dict)]

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
