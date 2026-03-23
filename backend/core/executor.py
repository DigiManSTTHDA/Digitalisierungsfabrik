"""Executor — the only component allowed to write to artifacts.

All artifact mutations go through apply_patches() as RFC 6902 JSON Patch operations.
Invalid or failing patches trigger a full rollback, leaving artifacts unchanged.

Pipeline (per apply_patches call):
  1. RFC-6902 formal validation (op/path syntax)
  2. Template-schema check (allowlist per artifact_type)
  3. Atomic snapshot (deep-copy via model_dump)
  4. Patch application (jsonpatch)
  5. Preservation check (only addressed fields changed)
  6. Invalidation detection (structure artifact only)
  7. Version bump
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Literal

import jsonpatch
import structlog

from artifacts.models import (
    AlgorithmArtifact,
    ExplorationArtifact,
    StructureArtifact,
)
from artifacts.template_schema import TEMPLATES

logger = structlog.get_logger(__name__)

ArtifactType = Literal["exploration", "structure", "algorithm"]
AnyArtifact = ExplorationArtifact | StructureArtifact | AlgorithmArtifact

# Fields on a Strukturschritt that trigger algorithm invalidation when changed
_INVALIDATING_FIELDS = {"beschreibung", "typ", "bedingung", "ausnahme_beschreibung", "regeln", "schleifenkoerper"}

# Regex to extract schritt_id and optional field from a /schritte/... path
_SCHRITTE_PATH_RE = re.compile(r"^/schritte/([^/]+)(?:/([^/]+))?$")


@dataclass
class ExecutorResult:
    """Result of an apply_patches call."""

    success: bool
    artifact: AnyArtifact | None
    invalidated_abschnitt_ids: list[str] = field(default_factory=list)
    error: str | None = None


class Executor:
    """Applies RFC 6902 JSON Patch operations to artifacts atomically."""

    def apply_patches(
        self,
        artifact_type: ArtifactType,
        artifact: AnyArtifact,
        patches: list[dict],  # type: ignore[type-arg]
    ) -> ExecutorResult:
        """Apply patches to artifact through the full validation pipeline.

        Returns ExecutorResult with success=True and updated artifact on success,
        or success=False with error description and original artifact=None on failure.
        """
        # Identity operation — return unchanged artifact without version bump
        if not patches:
            logger.info(
                "executor.apply_patches",
                artifact_type=artifact_type,
                patch_count=0,
                success=True,
                version=artifact.version,
            )
            return ExecutorResult(success=True, artifact=artifact)

        # ------------------------------------------------------------------
        # Step 1: RFC-6902 formal validation
        # ------------------------------------------------------------------
        for op_dict in patches:
            if not isinstance(op_dict, dict):
                return self._fail(artifact_type, "Patch-Element ist kein dict")
            if "op" not in op_dict:
                return self._fail(artifact_type, "Patch-Element fehlt 'op'-Key")
            if "path" not in op_dict:
                return self._fail(artifact_type, "Patch-Element fehlt 'path'-Key")
            op = op_dict["op"]
            path = op_dict["path"]
            if op not in {"add", "replace", "remove"}:
                return self._fail(
                    artifact_type,
                    f"Ungültige RFC-6902-Operation '{op}' — nur add/replace/remove erlaubt",
                )
            if not isinstance(path, str) or not path.startswith("/"):
                return self._fail(
                    artifact_type,
                    f"Ungültiger RFC-6902-Pfad '{path}' — muss mit '/' beginnen",
                )

        # ------------------------------------------------------------------
        # Step 2: Template-schema check
        # ------------------------------------------------------------------
        template = TEMPLATES[artifact_type]
        for op_dict in patches:
            op = op_dict["op"]
            path = op_dict["path"]
            if not template.is_valid_patch(op, path):
                return self._fail(
                    artifact_type,
                    f"Pfad/Op-Kombination nicht im Template: {op} {path}",
                )

        # ------------------------------------------------------------------
        # Step 3: Atomic snapshot
        # ------------------------------------------------------------------
        snapshot = artifact.model_dump()

        # ------------------------------------------------------------------
        # Step 4: Patch application
        # ------------------------------------------------------------------
        data = artifact.model_dump()
        try:
            patched_data = jsonpatch.apply_patch(data, patches, in_place=False)
        except Exception as exc:
            msg = str(exc)
            if "not found" in msg and "member" in msg:
                msg = f"Patch-Pfad ungültig — Key existiert nicht im Artefakt: {exc}"
            else:
                msg = f"Patch-Anwendung fehlgeschlagen: {exc}"
            return self._fail(artifact_type, msg)

        # Deserialize back into Pydantic model
        artifact_class = type(artifact)
        try:
            patched_artifact = artifact_class.model_validate(patched_data)
        except Exception as exc:
            return self._fail(
                artifact_type, f"Pydantic-Validierung nach Patch fehlgeschlagen: {exc}"
            )

        # ------------------------------------------------------------------
        # Step 5: Preservation check
        # ------------------------------------------------------------------
        # Build the set of addressed (collection, entity_id) pairs from patch paths.
        # For /slots/s01/inhalt → ("slots", "s01"); for /slots/s02 → ("slots", "s02")
        addressed_items = self._addressed_items(patches)
        preservation_error = self._check_preservation(snapshot, patched_data, addressed_items)
        if preservation_error:
            return self._fail(artifact_type, preservation_error)

        # ------------------------------------------------------------------
        # Step 6: Invalidation detection (structure only)
        # ------------------------------------------------------------------
        invalidated_ids: list[str] = []
        if artifact_type == "structure" and isinstance(patched_artifact, StructureArtifact):
            invalidated_ids = self._collect_invalidated_ids(patches, snapshot, patched_artifact)

        # ------------------------------------------------------------------
        # Step 7: Version bump
        # ------------------------------------------------------------------
        patched_artifact.version = artifact.version + 1

        logger.info(
            "executor.apply_patches",
            artifact_type=artifact_type,
            patch_count=len(patches),
            success=True,
            version=patched_artifact.version,
        )
        return ExecutorResult(
            success=True,
            artifact=patched_artifact,
            invalidated_abschnitt_ids=invalidated_ids,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _fail(self, artifact_type: ArtifactType, error: str) -> ExecutorResult:
        logger.warning(
            "executor.apply_patches", artifact_type=artifact_type, error=error, success=False
        )
        return ExecutorResult(success=False, artifact=None, error=error)

    def _addressed_items(self, patches: list[dict]) -> set[tuple[str, str]]:  # type: ignore[type-arg]
        """Return (collection_key, entity_id) pairs addressed by patch paths.

        Example: /slots/s01/inhalt        → ("slots", "s01")
                 /schritte/s01            → ("schritte", "s01")
                 /prozesszusammenfassung  → ("prozesszusammenfassung", "")
        """
        items: set[tuple[str, str]] = set()
        for op_dict in patches:
            path: str = op_dict["path"]
            parts = path.lstrip("/").split("/")
            if len(parts) >= 2:
                items.add((parts[0], parts[1]))
            elif len(parts) == 1 and parts[0]:
                # Top-level scalar field like /prozesszusammenfassung
                items.add((parts[0], ""))
        return items

    def _check_preservation(
        self,
        snapshot: dict,  # type: ignore[type-arg]
        patched_data: dict,  # type: ignore[type-arg]
        addressed_items: set[tuple[str, str]],
    ) -> str | None:
        """Return error message if any unaddressed collection entry was changed, else None."""
        for key in patched_data:
            if key == "version":
                continue
            snap_val = snapshot.get(key)
            patch_val = patched_data.get(key)
            if snap_val == patch_val:
                continue
            # This top-level field changed — check at entity level if it's a dict collection
            if isinstance(patch_val, dict) and isinstance(snap_val, dict):
                all_entity_keys = set(snap_val.keys()) | set(patch_val.keys())
                for entity_id in all_entity_keys:
                    if snap_val.get(entity_id) != patch_val.get(entity_id):
                        if (key, entity_id) not in addressed_items:
                            return (
                                f"Preservation-Check: nicht adressiertes Element "
                                f"'{key}/{entity_id}' wurde geändert"
                            )
            else:
                # Scalar top-level field changed and not in addressed items
                if not any(k == key for k, _ in addressed_items):
                    return f"Preservation-Check: nicht adressiertes Feld '{key}' wurde geändert"
        return None

    def _collect_invalidated_ids(
        self,
        patches: list[dict],  # type: ignore[type-arg]
        snapshot: dict,  # type: ignore[type-arg]
        patched_artifact: StructureArtifact,
    ) -> list[str]:
        """Collect algorithm abschnitt IDs that need invalidation after structure patches."""
        schritte_snapshot: dict = snapshot.get("schritte", {})  # type: ignore[type-arg]
        invalidated: set[str] = set()

        for op_dict in patches:
            path = op_dict["path"]
            m = _SCHRITTE_PATH_RE.match(path)
            if not m:
                continue
            schritt_id = m.group(1)
            field_name = m.group(2)  # None for whole-step add/remove

            triggers = False
            if field_name is None:
                # add/remove of whole step — triggers invalidation
                triggers = True
            elif field_name in _INVALIDATING_FIELDS:
                triggers = True

            if not triggers:
                continue

            # Collect algorithmus_ref from snapshot (for remove/replace) or patched (for add)
            refs: list[str] = []
            if schritt_id in schritte_snapshot:
                refs = schritte_snapshot[schritt_id].get("algorithmus_ref", [])
            elif schritt_id in patched_artifact.schritte:
                refs = patched_artifact.schritte[schritt_id].algorithmus_ref

            invalidated.update(refs)

        return list(invalidated)
