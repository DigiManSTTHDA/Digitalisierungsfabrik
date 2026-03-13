"""OutputValidator — prüft den ModeOutput gegen den Output-Kontrakt (SDD 6.5.2).

Validates:
1. RFC 6902 syntax: each patch has valid op, path starting with /
2. add/replace patches must have a 'value' field
3. Template schema: each (op, path) must be accepted by the ArtifactTemplate
4. Only allowed ops: add, replace, remove

SDD-Referenz: 6.5.2 (Output-Kontrakt), FR-B-09 (Schreibkontrolle).
"""

from __future__ import annotations

import structlog

from artifacts.template_schema import ArtifactTemplate
from modes.base import ModeOutput

logger = structlog.get_logger(__name__)

# Allowed RFC 6902 operations (restricted set for this system)
_ALLOWED_OPS = {"add", "replace", "remove"}


def validate(output: ModeOutput, artifact_template: ArtifactTemplate | None = None) -> bool:
    """ModeOutput gegen den Output-Kontrakt prüfen.

    Args:
        output: The mode's output containing patches and nutzeraeusserung.
        artifact_template: Template to validate patch paths against.
            If None, only RFC 6902 syntax is checked.

    Returns:
        True if all patches are valid, False otherwise.
    """
    patches = output.patches

    # Empty patches list is valid — mode may respond without writing
    if not patches:
        return True

    for patch in patches:
        if not isinstance(patch, dict):
            logger.warning("output_validator.invalid_patch", reason="Patch ist kein dict")
            return False

        op = patch.get("op")
        path = patch.get("path")

        # Check op is valid
        if op not in _ALLOWED_OPS:
            logger.warning(
                "output_validator.invalid_op",
                op=op,
                allowed=list(_ALLOWED_OPS),
            )
            return False

        # Check path is a string starting with /
        if not isinstance(path, str) or not path.startswith("/"):
            logger.warning("output_validator.invalid_path", path=path)
            return False

        # Check add/replace have value field
        if op in ("add", "replace") and "value" not in patch:
            logger.warning(
                "output_validator.missing_value",
                op=op,
                path=path,
            )
            return False

        # Check path against template if provided
        if artifact_template is not None:
            if not artifact_template.is_valid_patch(op, path):
                logger.warning(
                    "output_validator.path_not_in_template",
                    op=op,
                    path=path,
                )
                return False

    return True
