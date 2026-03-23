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
from core.patch_summarizer import summarize_patches
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
        line = f"- [{schritt.reihenfolge}] {schritt.titel} ({sid}) [{typ}] [{status}] → {nachf}"
        # CR-002: Show control flow details for entscheidung and schleife
        if schritt.regeln:
            line += f" ({len(schritt.regeln)} Regeln)"
        if schritt.schleifenkoerper:
            line += f" [Schleife: {', '.join(schritt.schleifenkoerper)}]"
        if schritt.konvergenz:
            line += f" [Konvergenz: {schritt.konvergenz}]"
        lines.append(line)

    zusammenfassung = context.structure_artifact.prozesszusammenfassung
    if zusammenfassung:
        lines.insert(0, f"Prozesszusammenfassung: {zusammenfassung}\n")

    return "\n".join(lines)


def _build_first_turn_directive(context: ModeContext) -> str:
    """Inject a strong directive when the structure artifact is still empty.

    Returns an empty string if Strukturschritte already exist, so this
    directive only fires on the very first turn of the structuring phase.
    """
    if context.structure_artifact.schritte:
        return ""
    return (
        "\n\n## SOFORT-AKTION: Strukturartefakt ist leer\n\n"
        "Das Strukturartefakt enthält noch KEINE Strukturschritte. "
        "Du befindest dich am Beginn der Strukturierungsphase.\n\n"
        "Deine PFLICHT in DIESEM Turn (nicht auf den nächsten Turn warten):\n"
        "1. Analysiere das Explorationsartefakt vollständig "
        "(prozessbeschreibung, prozessausloeser, entscheidungen_und_schleifen, variablen_und_daten).\n"
        "2. Erstelle Patches für ALLE erkennbaren Strukturschritte — "
        "mindestens die Hauptschritte des Prozessablaufs. "
        "Nutze completeness_status='teilweise', da Details noch folgen.\n"
        "3. Ordne Reihenfolge und Nachfolger bereits jetzt plausibel zu.\n"
        "4. Stelle dem Nutzer den Entwurf vor — liste alle Schritte kurz nummeriert auf:\n"
        "   '1. [Titel] — [kurze Beschreibung]\n"
        "    2. [Titel] — [kurze Beschreibung]\n"
        "    ...\n"
        "    Fehlt etwas, oder soll ich etwas anpassen?'\n\n"
        "WARTE NICHT auf weitere Eingaben — erstelle den Entwurf JETZT in diesem Turn."
    )


def _apply_guardrails(
    llm_phasenstatus: Phasenstatus,
    context: ModeContext,
    patches: list[dict],  # type: ignore[type-arg]
) -> Phasenstatus:
    """Deterministic guardrails on the LLM's phasenstatus decision.

    Evaluates the projected post-patch state to prevent a 2-turn bypass
    where the LLM sends phase_complete + add-patches in the same turn,
    causing the guardrail to block on Turn N (schritte empty) but then
    allow it on Turn N+1 because schritte were just added.
    """
    schritte = context.structure_artifact.schritte

    adding_schritte = any(
        p.get("op") == "add"
        and isinstance(p.get("path"), str)
        and p["path"].startswith("/schritte/")
        and len(p["path"].split("/")) == 3
        for p in patches
    )

    if not schritte:
        if llm_phasenstatus == Phasenstatus.phase_complete:
            # Schritte gerade erst angelegt — noch nicht durch Nutzer bestätigt
            if adding_schritte:
                return Phasenstatus.nearing_completion
            return Phasenstatus.in_progress
        return llm_phasenstatus

    has_leer = any(s.completeness_status == CompletenessStatus.leer for s in schritte.values())
    if llm_phasenstatus == Phasenstatus.phase_complete and has_leer:
        return Phasenstatus.nearing_completion

    return llm_phasenstatus


def _derive_nachfolger_from_regeln(
    patches: list[dict],  # type: ignore[type-arg]
    context: ModeContext,
) -> list[dict]:  # type: ignore[type-arg]
    """Auto-derive nachfolger from regeln when regeln is set (CR-002 guardrail).

    If a patch sets regeln on a Strukturschritt, inject an additional replace patch
    for nachfolger derived from the regeln entries. regeln is the source of truth.
    """
    extra_patches: list[dict] = []  # type: ignore[type-arg]
    for patch in patches:
        if patch.get("op") != "replace":
            continue
        path = patch.get("path", "")
        if not path.endswith("/regeln"):
            continue
        regeln_value = patch.get("value")
        if not isinstance(regeln_value, list) or not regeln_value:
            continue
        # Extract schritt path prefix: /schritte/s5/regeln → /schritte/s5
        schritt_path = path.rsplit("/", 1)[0]
        derived_nachfolger = [
            r["nachfolger"] for r in regeln_value
            if isinstance(r, dict) and "nachfolger" in r
        ]
        if derived_nachfolger:
            extra_patches.append({
                "op": "replace",
                "path": f"{schritt_path}/nachfolger",
                "value": derived_nachfolger,
            })
    return extra_patches


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
        system_prompt += _build_first_turn_directive(context)

        # Retry-Hint bei ungültigen Patch-Pfaden (S1-T1)
        if context.error_hint:
            system_prompt += f"\n\n## FEHLER-HINWEIS\n\n{context.error_hint}"

        messages = translate_dialog_history(context.dialog_history)

        response = await self._llm_client.complete(
            system=system_prompt,
            messages=messages,
            tools=[APPLY_PATCHES_TOOL],
            tool_choice={"type": "tool", "name": "apply_patches"},
        )

        patches = [p for p in (response.tool_input.get("patches") or []) if isinstance(p, dict)]

        # CR-002 guardrail: auto-derive nachfolger from regeln
        extra = _derive_nachfolger_from_regeln(patches, context)
        if extra:
            patches.extend(extra)

        # LLM decides phasenstatus, guardrails enforce hard constraints
        raw_status = response.tool_input.get("phasenstatus", "in_progress")
        try:
            llm_phasenstatus = Phasenstatus(raw_status)
        except ValueError:
            llm_phasenstatus = Phasenstatus.in_progress

        phasenstatus = _apply_guardrails(llm_phasenstatus, context, patches)

        flags: list[Flag] = []
        if phasenstatus == Phasenstatus.phase_complete:
            flags.append(Flag.phase_complete)

        # Deterministischer Summarizer: überschreibt LLM-Bestätigung bei Patches (S2-T3)
        # Verhindert halluzinierte Bestätigungen (B10).
        # Wenn keine Patches vorhanden: LLM-Text bleibt (Rückfragen, Einleitungen).
        if patches:
            nutzeraeusserung = summarize_patches(patches, context.structure_artifact)
        else:
            nutzeraeusserung = response.nutzeraeusserung

        return ModeOutput(
            nutzeraeusserung=nutzeraeusserung,
            patches=patches,
            phasenstatus=phasenstatus,
            flags=flags,
            debug_request=response.debug_request,
            usage=response.usage,
        )
