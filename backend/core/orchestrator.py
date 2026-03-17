"""Orchestrator — zentraler Steuerknoten des Systems (SDD 6.2, 6.3).

Implementiert den 11-Schritt-Zyklus für jeden Nutzerturn. Ist die einzige
Komponente, die Modi aktiviert/deaktiviert, Schreiboperationen via Executor
ausführt und den Systemzustand persistiert.

Der Orchestrator kennt weder FastAPI noch WebSocket-Details (HLA Section 3.3).

SDD-Referenzen: 6.2 (Orchestrator), 6.3 (11-Schritt-Zyklus), 6.4 (Working Memory).
"""

from __future__ import annotations

import structlog
from pydantic import BaseModel, Field

from artifacts.completeness import CompletenessCalculator
from artifacts.models import Phasenstatus
from config import Settings
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

# Modes that trigger a switch to the Moderator (SDD 6.3 Moduswechsel-Logik)
_MODERATOR_TRIGGER_FLAGS = {Flag.phase_complete, Flag.escalate, Flag.blocked}


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
    ) -> None:
        self._repository = repository
        self._modes = modes
        self._settings = settings
        self._executor = Executor()
        self._calculator = CompletenessCalculator()

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
                wm, f"Kein Modus '{mode_key}' registriert und kein Fallback 'exploration'"
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
            return self._error_output(wm, "Output-Kontrakt-Verletzung: ModeOutput ungültig")

        # Schritt 7: Patches anwenden (wenn vorhanden)
        if mode_output.patches:
            artifact_type = infer_artifact_type(mode_output.patches)
            if artifact_type is None:
                return self._error_output(
                    wm, "Patch-Pfade konnten keinem Artefakttyp zugeordnet werden"
                )

            artifact = get_artifact(project, artifact_type)
            result = self._executor.apply_patches(artifact_type, artifact, mode_output.patches)

            if not result.success:
                log.warning("orchestrator.executor_failure", error=result.error)
                return self._error_output(wm, f"Executor-Fehler: {result.error}")

            assert result.artifact is not None
            set_artifact(project, artifact_type, result.artifact)

            # Schritt 8: Invalidierungen auslösen (SDD 6.3 Schritt 8, FR-B-04)
            if result.invalidated_abschnitt_ids:
                apply_invalidations(project, result.invalidated_abschnitt_ids, self._executor)

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
        wm = update_working_memory(wm, mode_output.phasenstatus, befuellte, bekannte)

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

        # Moderator signals: return to previous mode (FR-D-09 AC#4)
        # Also handles system start: if no vorheriger_modus, switch to
        # the current phase's primary mode (FR-D-11).
        if Flag.return_to_mode in active_flags:
            if wm.vorheriger_modus:
                wm.aktiver_modus = wm.vorheriger_modus
                wm.vorheriger_modus = None
            else:
                # System start or no previous mode: switch to phase primary mode
                from core.phase_transition import PHASE_TO_MODE

                wm.aktiver_modus = PHASE_TO_MODE.get(wm.aktive_phase, "exploration")
            project.aktiver_modus = wm.aktiver_modus
            log.info("orchestrator.return_to_mode", mode=wm.aktiver_modus)

        project.working_memory = wm
        project.aktiver_modus = wm.aktiver_modus
        project.aktive_phase = wm.aktive_phase

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

    def _error_output(self, wm: WorkingMemory, error: str) -> TurnOutput:
        """Fehler-TurnOutput ohne Zustandsänderung zurückgeben."""
        return TurnOutput(
            nutzeraeusserung="",
            phasenstatus=wm.phasenstatus,
            flags=[],
            working_memory=wm,
            error=error,
        )
