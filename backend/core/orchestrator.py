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
from artifacts.models import (
    AlgorithmArtifact,
    ExplorationArtifact,
    Phasenstatus,
    StructureArtifact,
)
from core.context_assembler import build_context
from core.executor import ArtifactType, Executor
from core.models import Project
from core.output_validator import validate
from core.progress_tracker import update_working_memory
from core.working_memory import WorkingMemory
from modes.base import BaseMode, Flag
from persistence.project_repository import ProjectRepository

logger = structlog.get_logger(__name__)

# Modes that trigger a switch to the Moderator (SDD 6.3 Moduswechsel-Logik)
_MODERATOR_TRIGGER_FLAGS = {Flag.phase_complete, Flag.escalate, Flag.blocked}

# Map patch path prefixes to artifact types
_PATH_PREFIX_TO_ARTIFACT_TYPE: dict[str, ArtifactType] = {
    "/slots/": "exploration",
    "/schritte/": "structure",
    "/abschnitte/": "algorithm",
}


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
    ) -> None:
        self._repository = repository
        self._modes = modes
        self._executor = Executor()
        self._calculator = CompletenessCalculator()

    async def process_turn(self, project_id: str, input: TurnInput) -> TurnOutput:
        """Nutzerturn verarbeiten — 11-Schritt-Zyklus (SDD 6.3).

        Args:
            project_id: ID des aktiven Projekts.
            input: Nutzereingabe (Text + optionale Datei).

        Returns:
            TurnOutput mit Antwort, aktualisiertem Working Memory und ggf. Fehlermeldung.

        Raises:
            ValueError: Wenn das Projekt nicht gefunden wird.
        """
        repo: ProjectRepository = self._repository

        # ------------------------------------------------------------------
        # Schritt 1: Projekt laden
        # ------------------------------------------------------------------
        project: Project = repo.load(project_id)
        wm: WorkingMemory = project.working_memory

        log = logger.bind(project_id=project_id, turn=wm.letzter_dialogturn + 1)
        log.info("orchestrator.process_turn.start")

        # ------------------------------------------------------------------
        # Schritt 2: Working Memory aktualisieren
        # ------------------------------------------------------------------
        wm.letzter_dialogturn += 1

        # ------------------------------------------------------------------
        # Schritt 3: Flags aus letztem Turn auswerten (Observabilität)
        # Hinweis: Der Moduswechsel wurde bereits am Ende des letzten Turns
        # in wm.aktiver_modus gespeichert — hier nur Logging.
        # ------------------------------------------------------------------
        if wm.flags:
            log.info("orchestrator.previous_turn_flags", flags=wm.flags)

        # ------------------------------------------------------------------
        # Schritt 4: Aktiven Modus bestimmen
        # ------------------------------------------------------------------
        mode_key = wm.aktiver_modus
        mode = self._modes.get(mode_key)
        if mode is None:
            mode = self._modes.get("exploration")
        if mode is None:
            return self._error_output(
                wm, f"Kein Modus '{mode_key}' registriert und kein Fallback 'exploration'"
            )

        # ------------------------------------------------------------------
        # Schritt 5: Kontext zusammenstellen
        # ------------------------------------------------------------------
        completeness_state, befuellte, bekannte = self._calculator.calculate(
            project.exploration_artifact,
            project.structure_artifact,
            project.algorithm_artifact,
        )
        context = build_context(project, completeness_state, repository=repo)

        # ------------------------------------------------------------------
        # Schritt 6: Modus aufrufen
        # ------------------------------------------------------------------
        mode_output = await mode.call(context)

        # OutputValidator (Stub in Epic 03 — immer True)
        if not validate(mode_output):
            return self._error_output(wm, "Output-Kontrakt-Verletzung: ModeOutput ungültig")

        # ------------------------------------------------------------------
        # Schritt 7: Patches anwenden (wenn vorhanden)
        # ------------------------------------------------------------------
        if mode_output.patches:
            artifact_type = self._infer_artifact_type(mode_output.patches)
            if artifact_type is None:
                return self._error_output(
                    wm,
                    "Patch-Pfade konnten keinem Artefakttyp zugeordnet werden",
                )

            artifact = self._get_artifact(project, artifact_type)
            result = self._executor.apply_patches(artifact_type, artifact, mode_output.patches)

            if not result.success:
                log.warning("orchestrator.executor_failure", error=result.error)
                return self._error_output(wm, f"Executor-Fehler: {result.error}")

            assert result.artifact is not None
            self._set_artifact(project, artifact_type, result.artifact)

            # ------------------------------------------------------------------
            # Schritt 8: Invalidierungen auslösen (SDD 6.3 Schritt 8, FR-B-04)
            # ------------------------------------------------------------------
            if result.invalidated_abschnitt_ids:
                self._apply_invalidations(project, result.invalidated_abschnitt_ids)

        # ------------------------------------------------------------------
        # Schritt 9: Completeness-State aktualisieren
        # ------------------------------------------------------------------
        completeness_state, befuellte, bekannte = self._calculator.calculate(
            project.exploration_artifact,
            project.structure_artifact,
            project.algorithm_artifact,
        )
        wm.completeness_state = completeness_state

        # ------------------------------------------------------------------
        # Schritt 10: Fortschritt bewerten + Moduswechsel prüfen
        # ------------------------------------------------------------------
        wm = update_working_memory(wm, mode_output.phasenstatus, befuellte, bekannte)

        flag_strings = [f.value for f in mode_output.flags]
        wm.flags = flag_strings  # Observabilität (SDD 6.4.1: nicht persistiert als Steuerung)

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

        project.working_memory = wm
        project.aktiver_modus = wm.aktiver_modus
        project.aktive_phase = wm.aktive_phase

        # ------------------------------------------------------------------
        # Schritt 11: Zustand persistieren
        # ------------------------------------------------------------------
        repo.save(project)

        # Dialogturns persistieren (FR-E-07): Nutzereingabe + Modus-Antwort
        repo.append_dialog_turn(project.projekt_id, wm.letzter_dialogturn, "user", input.text)
        repo.append_dialog_turn(
            project.projekt_id,
            wm.letzter_dialogturn,
            "assistant",
            mode_output.nutzeraeusserung,
        )

        log.info("orchestrator.process_turn.done", phasenstatus=wm.phasenstatus.value)

        return TurnOutput(
            nutzeraeusserung=mode_output.nutzeraeusserung,
            phasenstatus=wm.phasenstatus,
            flags=flag_strings,
            working_memory=wm,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _infer_artifact_type(self, patches: list[dict]) -> ArtifactType | None:  # type: ignore[type-arg]
        """Artefakttyp anhand des ersten Patch-Pfad-Präfixes bestimmen."""
        if not patches:
            return None
        first_patch = patches[0]
        if not isinstance(first_patch, dict):
            return None
        path: str = first_patch.get("path", "") if isinstance(first_patch.get("path"), str) else ""
        for prefix, artifact_type in _PATH_PREFIX_TO_ARTIFACT_TYPE.items():
            if path.startswith(prefix):
                return artifact_type
        return None

    def _get_artifact(
        self, project: Project, artifact_type: ArtifactType
    ) -> ExplorationArtifact | StructureArtifact | AlgorithmArtifact:
        if artifact_type == "exploration":
            return project.exploration_artifact
        if artifact_type == "structure":
            return project.structure_artifact
        return project.algorithm_artifact

    def _set_artifact(
        self,
        project: Project,
        artifact_type: ArtifactType,
        artifact: ExplorationArtifact | StructureArtifact | AlgorithmArtifact,
    ) -> None:
        if artifact_type == "exploration":
            if not isinstance(artifact, ExplorationArtifact):
                raise TypeError("Erwartete ExplorationArtifact")
            project.exploration_artifact = artifact
        elif artifact_type == "structure":
            if not isinstance(artifact, StructureArtifact):
                raise TypeError("Erwartete StructureArtifact")
            project.structure_artifact = artifact
        else:
            if not isinstance(artifact, AlgorithmArtifact):
                raise TypeError("Erwartete AlgorithmArtifact")
            project.algorithm_artifact = artifact

    def _apply_invalidations(self, project: Project, abschnitt_ids: list[str]) -> None:
        """Referenzierte Algorithmusabschnitte auf 'invalidiert' setzen (SDD FR-B-04, 6.3 Schritt 8)."""
        inv_patches = [
            {"op": "replace", "path": f"/abschnitte/{aid}/status", "value": "invalidiert"}
            for aid in abschnitt_ids
            if aid in project.algorithm_artifact.abschnitte
        ]
        if not inv_patches:
            return

        result = self._executor.apply_patches("algorithm", project.algorithm_artifact, inv_patches)
        if result.success and result.artifact is not None:
            assert isinstance(result.artifact, AlgorithmArtifact)
            project.algorithm_artifact = result.artifact
            logger.info(
                "orchestrator.invalidation_applied",
                abschnitt_ids=abschnitt_ids,
            )
        else:
            logger.warning(
                "orchestrator.invalidation_failed",
                abschnitt_ids=abschnitt_ids,
                error=result.error,
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
