"""Orchestrator — zentraler Steuerknoten des Systems (SDD 6.2, 6.3).

Implementiert den 11-Schritt-Zyklus für jeden Nutzerturn. Ist die einzige
Komponente, die Modi aktiviert/deaktiviert, Schreiboperationen via Executor
ausführt und den Systemzustand persistiert.

Der Orchestrator kennt weder FastAPI noch WebSocket-Details (HLA Section 3.3).

SDD-Referenzen: 6.2 (Orchestrator), 6.3 (11-Schritt-Zyklus), 6.4 (Working Memory).
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypedDict

import structlog
from pydantic import BaseModel, Field

from artifacts.completeness import CompletenessCalculator
from artifacts.init_validator import (
    StructuralViolation,
    validate_algorithm_artifact,
    validate_structure_artifact,
)
from artifacts.models import Phasenstatus
from config import Settings
from core.turn_debug_log import write_turn_debug
from core.artifact_router import (
    apply_invalidations,
    get_artifact,
    infer_artifact_type,
    set_artifact,
)
from core.context_assembler import build_context
from core.executor import Executor
from core.models import Project
from core.output_validator import validate
from core.phase_transition import advance_phase as do_advance_phase
from core.progress_tracker import update_working_memory
from core.working_memory import WorkingMemory
from modes.base import BaseMode, Flag
from persistence.project_repository import ProjectRepository

logger = structlog.get_logger(__name__)


class InitProgressInfo(TypedDict):
    """Callback data for init progress events (CR-007)."""

    phase: str
    status: str
    turn: int
    max_turns: int
    message: str


# Max init turns: 1 init-call + 1 optional correction-call (CR-009 single-call architecture)
_MAX_INIT_TURNS = 2

# Modes that trigger a switch to the Moderator (SDD 6.3 Moduswechsel-Logik)
_MODERATOR_TRIGGER_FLAGS = {Flag.phase_complete, Flag.escalate, Flag.blocked}


def _patch_retry_hint(aktive_phase: str) -> str:
    """Phasenabhängiger Retry-Hint für ungültige Patch-Pfade."""
    base = (
        "ACHTUNG: Der letzte Aufruf produzierte Patches mit ungültigen Pfaden. "
        "Verwende AUSSCHLIESSLICH Pfade mit diesen Präfixen: "
    )
    if aktive_phase == "spezifikation":
        return base + (
            "/abschnitte/{aid}/..., /abschnitte/{aid}/aktionen/{aktion_id}/... "
            "Ergänze /prozesszusammenfassung NUR zusammen mit mindestens einem /abschnitte/-Patch. "
            "Numerische Indizes wie /abschnitte/0/ sind ungültig."
        )
    return base + (
        "/schritte/{sid}/..., /slots/{slot_id}/..., /abschnitte/{aid}/... "
        "Ergänze /prozesszusammenfassung NUR zusammen mit mindestens einem "
        "/schritte/- oder /abschnitte/-Patch. "
        "Numerische Indizes wie /schritte/0/ sind ungültig."
    )


class TurnInput(BaseModel):
    """Nutzereingabe für einen Orchestrator-Turn (HLA Section 3.3, Epic 05 WebSocket-Payload)."""

    text: str
    datei: str | None = None  # base64-kodierter Dateiinhalt (optional)


class TurnOutput(BaseModel):
    """Ergebnis eines Orchestrator-Turns (HLA Section 3.3, Epic 05 WebSocket-Payload)."""

    nutzeraeusserung: str
    phasenstatus: Phasenstatus
    flags: list[str] = Field(default_factory=list)  # Flag-Werte als Strings (Observabilität)
    working_memory: WorkingMemory
    error: str | None = None  # gesetzt bei fatalen Fehlern; kein Zustandsänderung


class Orchestrator:
    """Zentraler Steuerknoten — implementiert den 11-Schritt-Zyklus (SDD 6.3).

    Kennt weder FastAPI noch WebSocket. Die API-Schicht (Epic 05) ist verantwortlich
    für das Mapping zwischen WebSocket-Events und process_turn-Aufrufen.
    """

    def __init__(
        self,
        repository: ProjectRepository,
        modes: dict[str, BaseMode],
        settings: Settings | None = None,
        on_init_progress: Callable[[InitProgressInfo], Awaitable[None]] | None = None,
    ) -> None:
        self._repository = repository
        self._modes = modes
        self._settings = settings
        self._on_init_progress = on_init_progress
        self._executor = Executor()
        self._calculator = CompletenessCalculator()

    async def _emit_init_progress(self, info: InitProgressInfo) -> None:
        """Emit init progress via callback (CR-007). Errors are logged, never raised."""
        if self._on_init_progress is not None:
            try:
                await self._on_init_progress(info)
            except Exception:
                logger.warning("orchestrator.init_progress_callback_error", info=info)

    async def process_turn(self, project_id: str, input: TurnInput) -> TurnOutput:
        """Nutzerturn verarbeiten — 11-Schritt-Zyklus (SDD 6.3)."""
        repo: ProjectRepository = self._repository

        # Schritt 1: Projekt laden
        project: Project = repo.load(project_id)
        wm: WorkingMemory = project.working_memory

        log = logger.bind(project_id=project_id, turn=wm.letzter_dialogturn + 1)
        log.info("orchestrator.process_turn.start")

        # Schritt 2: Working Memory aktualisieren
        wm.letzter_dialogturn += 1

        # Schritt 3: Flags aus letztem Turn auswerten (Observabilität)
        if wm.flags:
            log.info("orchestrator.previous_turn_flags", flags=wm.flags)

        # Schritt 4: Aktiven Modus bestimmen
        mode_key = wm.aktiver_modus
        mode = self._modes.get(mode_key)
        if mode is None:
            mode = self._modes.get("exploration")
        if mode is None:
            return self._error_output(
                wm,
                "Ein interner Fehler ist aufgetreten.",
                internal=f"Kein Modus '{mode_key}' registriert und kein Fallback 'exploration'",
            )

        # Schritt 5: Nutzerturn vorab persistieren (FR-E-07) — damit die aktuelle
        # Nutzereingabe im Dialogverlauf sichtbar ist, bevor der Modus aufgerufen wird.
        repo.append_dialog_turn(project.projekt_id, wm.letzter_dialogturn, "user", input.text)

        # Schritt 5b: Kontext zusammenstellen
        completeness_state, befuellte, bekannte = self._calculator.calculate(
            project.exploration_artifact,
            project.structure_artifact,
            project.algorithm_artifact,
        )
        context = build_context(
            project, completeness_state, repository=repo, settings=self._settings
        )

        # Schritt 6: Modus aufrufen
        mode_output = await mode.call(context)

        # OutputValidator (SDD 6.5.2 — prüft RFC 6902 Syntax + Template-Pfade)
        if not validate(mode_output, context.artifact_template):
            return self._error_output(
                wm,
                "Die Systemantwort war fehlerhaft. Bitte erneut versuchen.",
                internal="Output-Kontrakt-Verletzung: ModeOutput ungültig",
                repo=repo,
                project=project,
            )

        # Schritt 7: Patches anwenden (wenn vorhanden) — mit Retry-Logik (S1-T1)
        _MAX_PATCH_RETRIES = 2

        if mode_output.patches:
            artifact_type = infer_artifact_type(mode_output.patches)

            if artifact_type is None:
                for attempt in range(_MAX_PATCH_RETRIES):
                    log.warning("orchestrator.patch_retry", attempt=attempt + 1)
                    retry_context = context.with_error_hint(
                        f"Versuch {attempt + 1}: {_patch_retry_hint(wm.aktive_phase.value)}"
                    )
                    mode_output = await mode.call(retry_context)
                    if not validate(mode_output, context.artifact_template):
                        continue
                    # Empty patches on retry: LLM corrected itself — proceed without patching
                    if not mode_output.patches:
                        artifact_type = "none"  # type: ignore[assignment]
                        break
                    artifact_type = infer_artifact_type(mode_output.patches)
                    if artifact_type is not None:
                        break

            if artifact_type is None:
                return self._error_output(
                    wm,
                    "Ein interner Fehler ist aufgetreten. Bitte erneut versuchen.",
                    internal="Patch-Pfade konnten keinem Artefakttyp zugeordnet werden (nach Retries)",
                    repo=repo,
                    project=project,
                )

            # Skip patch application if LLM corrected to empty patches on retry
            if not mode_output.patches:
                artifact_type = None  # reset so the block below is skipped cleanly

        if mode_output.patches and artifact_type is not None:
            artifact = get_artifact(project, artifact_type)
            result = self._executor.apply_patches(artifact_type, artifact, mode_output.patches)

            if not result.success:
                log.warning("orchestrator.executor_failure", error=result.error)
                return self._error_output(
                    wm,
                    "Ein interner Fehler ist aufgetreten. Bitte erneut versuchen.",
                    internal=result.error,
                    repo=repo,
                    project=project,
                )

            assert result.artifact is not None
            set_artifact(project, artifact_type, result.artifact)

            # Schritt 8: Invalidierungen auslösen (SDD 6.3 Schritt 8, FR-B-04)
            if result.invalidated_abschnitt_ids:
                apply_invalidations(project, result.invalidated_abschnitt_ids, self._executor)

            # Track aktiver_abschnitt from patches targeting /abschnitte/{aid}/...
            if artifact_type == "algorithm":
                for patch in mode_output.patches:
                    path = patch.get("path", "")
                    parts = path.strip("/").split("/")
                    if len(parts) >= 2 and parts[0] == "abschnitte":
                        wm.aktiver_abschnitt = parts[1]

        # Store validation report in WorkingMemory (SDD 6.6.4, Story 10-04)
        if mode_output.validierungsbericht is not None:
            wm.validierungsbericht = mode_output.validierungsbericht

        # Schritt 9: Completeness-State aktualisieren
        completeness_state, befuellte, bekannte = self._calculator.calculate(
            project.exploration_artifact,
            project.structure_artifact,
            project.algorithm_artifact,
        )
        wm.completeness_state = completeness_state

        # Schritt 10: Fortschritt bewerten + Moduswechsel prüfen
        wm = update_working_memory(
            wm, mode_output.phasenstatus, befuellte, bekannte, project.structure_artifact
        )

        flag_strings = [f.value for f in mode_output.flags]
        wm.flags = flag_strings

        active_flags = set(mode_output.flags)
        if _MODERATOR_TRIGGER_FLAGS & active_flags and wm.aktiver_modus != "moderator":
            wm.vorheriger_modus = wm.aktiver_modus
            wm.aktiver_modus = "moderator"
            log.info(
                "orchestrator.mode_switch",
                from_mode=wm.vorheriger_modus,
                to_mode="moderator",
                trigger_flags=flag_strings,
            )

        # Moderator signals: advance to next phase (FR-D-09)
        if Flag.advance_phase in active_flags:
            success = do_advance_phase(project, wm)
            if success:
                log.info("orchestrator.phase_advanced", new_phase=wm.aktive_phase.value)
                active_flags.add(Flag.return_to_mode)  # skip extra moderator turn

        # Moderator signals: return to previous mode (FR-D-09 AC#4)
        # Also handles system start: if no vorheriger_modus, switch to
        # the current phase's primary mode (FR-D-11).
        if Flag.return_to_mode in active_flags:
            from core.phase_transition import PHASE_TO_MODE

            if wm.vorheriger_modus:
                target_mode = wm.vorheriger_modus
                wm.vorheriger_modus = None
            else:
                # System start or no previous mode: switch to phase primary mode
                target_mode = PHASE_TO_MODE.get(wm.aktive_phase, "exploration")

            # CR-006 Schritt 10b: Background-Init für Structurer/Specifier wenn Artefakt leer
            if self._init_required(target_mode, project):
                log.info("orchestrator.background_init.start", target_mode=target_mode)
                await self._run_background_init(project, wm, target_mode)
                log.info("orchestrator.background_init.complete", target_mode=target_mode)

            wm.aktiver_modus = target_mode
            project.aktiver_modus = wm.aktiver_modus
            log.info("orchestrator.return_to_mode", mode=wm.aktiver_modus)

        project.working_memory = wm
        project.aktiver_modus = wm.aktiver_modus
        project.aktive_phase = wm.aktive_phase

        # Update cumulative token counters in Working Memory
        turn_usage = mode_output.usage
        if turn_usage:
            wm.cumulative_prompt_tokens += turn_usage.get("prompt_tokens", 0)
            wm.cumulative_completion_tokens += turn_usage.get("completion_tokens", 0)
            wm.cumulative_total_tokens += turn_usage.get("total_tokens", 0)

        # Turn Debug Log: write full LLM I/O to JSON file
        if self._settings and self._settings.llm_debug_log and mode_output.debug_request:
            write_turn_debug(
                base_dir=self._settings.database_path.rsplit("/", 1)[0] or "./data",
                project_id=project_id,
                turn_number=wm.letzter_dialogturn,
                mode=mode_key,
                system_prompt=mode_output.debug_request.get("system_prompt", ""),
                messages=mode_output.debug_request.get("messages", []),
                tool_choice=mode_output.debug_request.get("tool_choice"),
                response_nutzeraeusserung=mode_output.nutzeraeusserung,
                response_tool_input=mode_output.debug_request
                if not mode_output.patches
                else {
                    "nutzeraeusserung": mode_output.nutzeraeusserung,
                    "patches": mode_output.patches,
                    "phasenstatus": wm.phasenstatus.value,
                },
                token_usage=turn_usage,
                cumulative_tokens={
                    "prompt_tokens": wm.cumulative_prompt_tokens,
                    "completion_tokens": wm.cumulative_completion_tokens,
                    "total_tokens": wm.cumulative_total_tokens,
                },
            )

        # Schritt 11: Zustand persistieren
        repo.save(project)

        # Assistenten-Antwortturn persistieren (FR-E-07)
        repo.append_dialog_turn(
            project.projekt_id, wm.letzter_dialogturn, "assistant", mode_output.nutzeraeusserung
        )

        log.info("orchestrator.process_turn.done", phasenstatus=wm.phasenstatus.value)

        return TurnOutput(
            nutzeraeusserung=mode_output.nutzeraeusserung,
            phasenstatus=wm.phasenstatus,
            flags=flag_strings,
            working_memory=wm,
        )

    # ---------------------------------------------------------------------------
    # CR-006 / CR-009: Background-Initialisierung (Single-Call, ADR-009)
    # ---------------------------------------------------------------------------

    def _init_required(self, target_mode: str, project: "Project") -> bool:  # noqa: F821
        """Prüfen ob Background-Init erforderlich ist (Artefakt leer?)."""
        if target_mode == "structuring":
            return len(project.structure_artifact.schritte) == 0
        if target_mode == "specification":
            return len(project.algorithm_artifact.abschnitte) == 0
        return False

    async def _run_background_init(
        self,
        project: "Project",  # noqa: F821
        wm: WorkingMemory,
        target_mode: str,
    ) -> None:
        """Background-Init: Single-Call + Validator + optionaler Korrektur-Call (CR-009, ADR-009)."""
        init_mode_key = f"init_{target_mode}"
        init_mode = self._modes.get(init_mode_key)
        if init_mode is None:
            logger.warning("orchestrator.background_init.no_init_mode", key=init_mode_key)
            return

        source_type = "structure" if target_mode == "structuring" else "algorithm"
        artefakt_label = "Strukturartefakt" if target_mode == "structuring" else "Algorithmusartefakt"

        try:
            # CR-007: started
            await self._emit_init_progress(InitProgressInfo(
                phase=target_mode, status="started", turn=0,
                max_turns=_MAX_INIT_TURNS,
                message=f"Das System bereitet das {artefakt_label} vor...",
            ))

            # Phase 1: Single Init-Call
            context = build_context(project, {}, repository=self._repository, settings=self._settings)
            output = await init_mode.call(context)

            if output.patches:
                artifact = get_artifact(project, source_type)
                result = self._executor.apply_patches(source_type, artifact, output.patches)
                if result.success and result.artifact is not None:
                    set_artifact(project, source_type, result.artifact)
                    if result.invalidated_abschnitt_ids:
                        apply_invalidations(project, result.invalidated_abschnitt_ids, self._executor)

            # CR-007: in_progress after init call
            await self._emit_init_progress(InitProgressInfo(
                phase=target_mode, status="in_progress", turn=1,
                max_turns=_MAX_INIT_TURNS,
                message=f"Verarbeitung läuft (Turn 1/{_MAX_INIT_TURNS})...",
            ))

            # CR-007: validating before validators
            await self._emit_init_progress(InitProgressInfo(
                phase=target_mode, status="validating", turn=0,
                max_turns=_MAX_INIT_TURNS,
                message="Qualitätsprüfung läuft...",
            ))

            # Phase 2: Python-Validator (nur R-1 + R-5)
            py_violations = self._run_structural_validator(project, target_mode)

            # Phase 3: LLM-Coverage-Validator (einmalig)
            coverage_violations = await self._run_coverage_validator(project, wm)
            all_violations = py_violations + coverage_violations

            # Phase 4: Bei kritischen Befunden → EIN Korrektur-Call
            kritische = [v for v in all_violations if v.severity == "kritisch"]
            if kritische:
                feedback = self._format_validator_feedback(all_violations)
                context = build_context(project, {}, repository=self._repository, settings=self._settings)
                context = context.with_validator_feedback(feedback)
                output = await init_mode.call(context)

                if output.patches:
                    artifact = get_artifact(project, source_type)
                    result = self._executor.apply_patches(source_type, artifact, output.patches)
                    if result.success and result.artifact is not None:
                        set_artifact(project, source_type, result.artifact)

                # CR-007: in_progress after correction call
                await self._emit_init_progress(InitProgressInfo(
                    phase=target_mode, status="in_progress", turn=2,
                    max_turns=_MAX_INIT_TURNS,
                    message=f"Verarbeitung läuft (Turn 2/{_MAX_INIT_TURNS})...",
                ))

            # Phase 5: Warnungen als init_hinweise im WorkingMemory speichern
            warnungen = [v for v in all_violations if v.severity == "warnung"]
            if warnungen:
                wm.init_hinweise = [v.message for v in warnungen]

            # CR-007: completed
            await self._emit_init_progress(InitProgressInfo(
                phase=target_mode, status="completed", turn=0,
                max_turns=_MAX_INIT_TURNS,
                message=f"Initialisierung abgeschlossen. Das {artefakt_label} ist bereit.",
            ))

        except Exception:
            logger.exception("orchestrator.background_init.error", target_mode=target_mode)
            # Dialog-Modus startet auch bei Init-Fehler — mit unvollständigem Artefakt

    def _run_structural_validator(
        self,
        project: "Project",  # noqa: F821
        target_mode: str,
    ) -> list[StructuralViolation]:
        """Deterministischen Python-Validator ausführen (CR-009: nur R-1 + R-5)."""
        if target_mode == "structuring":
            return validate_structure_artifact(
                project.exploration_artifact,
                project.structure_artifact,
            )
        if target_mode == "specification":
            return validate_algorithm_artifact(
                project.structure_artifact,
                project.algorithm_artifact,
            )
        return []

    async def _run_coverage_validator(
        self,
        project: "Project",  # noqa: F821
        wm: WorkingMemory,
    ) -> list[StructuralViolation]:
        """Coverage-Validator als registrierten Modus aufrufen (CR-009: aufgewertet)."""
        import json

        coverage_mode = self._modes.get("init_coverage_validator")
        if coverage_mode is None:
            logger.warning("orchestrator.background_init.no_coverage_mode")
            return []
        context = build_context(project, {}, repository=self._repository, settings=self._settings)
        output = await coverage_mode.call(context)
        try:
            data = json.loads(output.nutzeraeusserung)
            return [
                StructuralViolation(
                    severity=e.get("schweregrad", "warnung"),
                    message=f"{e['typ']}: {e['bezeichnung']} (aus {e['quelle_slot']})",
                )
                for e in data.get("fehlende_entitaeten", [])
            ]
        except (json.JSONDecodeError, KeyError):
            logger.warning("orchestrator.coverage_validator.parse_error")
            return []

    def _format_validator_feedback(self, violations: list[StructuralViolation]) -> str:
        """Violations in lesbares Prompt-Feedback für Korrektur-Call formatieren (CR-009)."""
        lines = ["## Validator-Befunde\n"]
        lines.append("Das Artefakt wurde geprüft. Folgende Probleme wurden gefunden:\n")
        for v in violations:
            severity_label = "KRITISCH" if v.severity == "kritisch" else "Warnung"
            element = f" ({v.element_id})" if v.element_id else ""
            lines.append(f"- [{severity_label}]{element}: {v.message}")
        lines.append(
            "\nKorrigiere die kritischen Befunde. Überarbeite das bestehende Artefakt gezielt — "
            "lege KEINE neuen Schritte/Abschnitte an, die bereits existieren."
        )
        return "\n".join(lines)

    # ---------------------------------------------------------------------------

    def _error_output(
        self,
        wm: WorkingMemory,
        user_msg: str,
        *,
        internal: str | None = None,
        repo: ProjectRepository | None = None,
        project: Project | None = None,
    ) -> TurnOutput:
        """Fehler-TurnOutput zurückgeben.

        Falls repo und project übergeben werden, wird der aktuelle WM-Zustand
        persistiert (inkl. letzter_dialogturn), damit kein Drift zwischen
        dialog_history und working_memory entsteht.

        user_msg wird dem Nutzer angezeigt (generische Formulierung).
        internal wird nur ins Log geschrieben (technisches Detail).
        """
        logger.warning("orchestrator.error", detail=internal or user_msg)
        if repo is not None and project is not None:
            project.working_memory = wm
            repo.save(project)
        return TurnOutput(
            nutzeraeusserung="",
            phasenstatus=wm.phasenstatus,
            flags=[],
            working_memory=wm,
            error=user_msg,
        )
