"""Artifact routing helpers — extracted from orchestrator.py (DEBT-05).

Maps patch paths to artifact types and provides get/set accessors for
artifacts on a Project. Used by the Orchestrator to determine which
artifact to pass to the Executor based on patch path prefixes.

SDD references: 6.3 (Orchestrator-Zyklus), FR-B-04 (Invalidierungslogik).
"""

from __future__ import annotations

import structlog

from artifacts.models import (
    AlgorithmArtifact,
    ExplorationArtifact,
    StructureArtifact,
)
from core.executor import ArtifactType, Executor
from core.models import Project

logger = structlog.get_logger(__name__)

# Map patch path prefixes to artifact types
_PATH_PREFIX_TO_ARTIFACT_TYPE: dict[str, ArtifactType] = {
    "/slots/": "exploration",
    "/schritte/": "structure",
    "/abschnitte/": "algorithm",
}


def infer_artifact_type(patches: list[dict]) -> ArtifactType | None:  # type: ignore[type-arg]
    """Artefakttyp anhand der Patch-Pfad-Präfixe bestimmen.

    Prüft ALLE Patches (nicht nur den ersten). Verwendet den ersten
    eindeutigen Treffer. /prozesszusammenfassung allein ist mehrdeutig
    (existiert auf Structure- und Algorithm-Artefakt) und wird ignoriert.
    """
    if not patches:
        return None

    for patch in patches:
        if not isinstance(patch, dict):
            continue
        path: str = patch.get("path", "") if isinstance(patch.get("path"), str) else ""
        for prefix, artifact_type in _PATH_PREFIX_TO_ARTIFACT_TYPE.items():
            if path.startswith(prefix):
                return artifact_type

    return None


def get_artifact(
    project: Project, artifact_type: ArtifactType
) -> ExplorationArtifact | StructureArtifact | AlgorithmArtifact:
    """Return the artifact from the project matching the given type."""
    if artifact_type == "exploration":
        return project.exploration_artifact
    if artifact_type == "structure":
        return project.structure_artifact
    return project.algorithm_artifact


def set_artifact(
    project: Project,
    artifact_type: ArtifactType,
    artifact: ExplorationArtifact | StructureArtifact | AlgorithmArtifact,
) -> None:
    """Set the artifact on the project matching the given type."""
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


def apply_invalidations(project: Project, abschnitt_ids: list[str], executor: Executor) -> None:
    """Referenzierte Algorithmusabschnitte auf 'invalidiert' setzen (FR-B-04, 6.3 Schritt 8)."""
    inv_patches = [
        {"op": "replace", "path": f"/abschnitte/{aid}/status", "value": "invalidiert"}
        for aid in abschnitt_ids
        if aid in project.algorithm_artifact.abschnitte
    ]
    if not inv_patches:
        return

    result = executor.apply_patches("algorithm", project.algorithm_artifact, inv_patches)
    if result.success and result.artifact is not None:
        assert isinstance(result.artifact, AlgorithmArtifact)
        project.algorithm_artifact = result.artifact
        logger.info(
            "artifact_router.invalidation_applied",
            abschnitt_ids=abschnitt_ids,
        )
    else:
        logger.warning(
            "artifact_router.invalidation_failed",
            abschnitt_ids=abschnitt_ids,
            error=result.error,
        )
