"""Tests for OutputValidator real implementation (Story 04-05).

Coverage:
- Valid patch passes validation
- Empty patches list → valid (no writes this turn)
- Missing tool_input / empty patches key → invalid
- Invalid RFC 6902 op → invalid
- Path outside template allowlist → invalid
- add/replace missing value → invalid
"""

from __future__ import annotations

from artifacts.models import Phasenstatus
from artifacts.template_schema import (
    ALGORITHM_TEMPLATE,
    EXPLORATION_TEMPLATE,
    STRUCTURE_TEMPLATE,
)
from core.output_validator import validate
from modes.base import ModeOutput


def _make_output(patches: list[dict]) -> ModeOutput:  # type: ignore[type-arg]
    return ModeOutput(
        nutzeraeusserung="Test",
        patches=patches,
        phasenstatus=Phasenstatus.in_progress,
        flags=[],
    )


# ---------------------------------------------------------------------------
# Positive: valid patch passes
# ---------------------------------------------------------------------------


def test_valid_patch_passes_validation() -> None:
    output = _make_output(
        [{"op": "replace", "path": "/slots/prozessziel/inhalt", "value": "Ziel des Prozesses"}]
    )
    assert validate(output, EXPLORATION_TEMPLATE) is True


# ---------------------------------------------------------------------------
# Edge case: empty patches list → valid
# ---------------------------------------------------------------------------


def test_empty_patches_list_is_valid() -> None:
    output = _make_output([])
    assert validate(output, EXPLORATION_TEMPLATE) is True


# ---------------------------------------------------------------------------
# Negative: invalid RFC 6902 op
# ---------------------------------------------------------------------------


def test_invalid_op_fails_validation() -> None:
    output = _make_output([{"op": "move", "path": "/slots/prozessziel/inhalt", "value": "test"}])
    assert validate(output, EXPLORATION_TEMPLATE) is False


# ---------------------------------------------------------------------------
# Negative: path not in template
# ---------------------------------------------------------------------------


def test_path_outside_template_fails_validation() -> None:
    output = _make_output(
        [{"op": "replace", "path": "/slots/prozessziel/nonexistent_field", "value": "test"}]
    )
    assert validate(output, EXPLORATION_TEMPLATE) is False


# ---------------------------------------------------------------------------
# Negative: add/replace missing value
# ---------------------------------------------------------------------------


def test_add_patch_missing_value_fails_validation() -> None:
    output = _make_output([{"op": "add", "path": "/slots/new_slot"}])
    assert validate(output, EXPLORATION_TEMPLATE) is False


def test_replace_patch_missing_value_fails_validation() -> None:
    output = _make_output([{"op": "replace", "path": "/slots/prozessziel/inhalt"}])
    assert validate(output, EXPLORATION_TEMPLATE) is False


# ---------------------------------------------------------------------------
# Negative: remove without value is valid (remove doesn't need value)
# ---------------------------------------------------------------------------


def test_remove_patch_without_value_is_valid() -> None:
    output = _make_output([{"op": "remove", "path": "/slots/prozessziel"}])
    assert validate(output, EXPLORATION_TEMPLATE) is True


# ---------------------------------------------------------------------------
# Positive: add patch for a new (not-yet-existing) slot ID is accepted
# (verifies template uses regex [^/]+ for slot IDs — any string is valid)
# ---------------------------------------------------------------------------


def test_valid_add_patch_for_new_slot_id_passes() -> None:
    """An add patch for an arbitrary new slot path is accepted by the template."""
    output = _make_output(
        [
            {
                "op": "add",
                "path": "/slots/new_custom_slot",
                "value": {
                    "slot_id": "new_custom_slot",
                    "titel": "Neuer Slot",
                    "inhalt": "",
                    "completeness_status": "leer",
                },
            }
        ]
    )
    assert validate(output, EXPLORATION_TEMPLATE) is True


# ---------------------------------------------------------------------------
# Negative: patch targeting a completely unknown path segment is rejected
# (not just a wrong field under a valid slot, but a wrong top-level key)
# ---------------------------------------------------------------------------


def test_patch_with_unknown_top_level_path_fails_validation() -> None:
    """A patch with an unknown top-level path (not /slots/) is rejected by the template."""
    output = _make_output(
        [{"op": "replace", "path": "/unknown_key/prozessziel/inhalt", "value": "test"}]
    )
    assert validate(output, EXPLORATION_TEMPLATE) is False


# ---------------------------------------------------------------------------
# Structure template tests (QA fix: was untested — only exploration covered)
# ---------------------------------------------------------------------------


def test_structure_template_valid_add_schritt() -> None:
    """Adding a new Strukturschritt is valid for STRUCTURE_TEMPLATE."""
    output = _make_output([{"op": "add", "path": "/schritte/s01", "value": {"titel": "Schritt 1"}}])
    assert validate(output, STRUCTURE_TEMPLATE) is True


def test_structure_template_replace_beschreibung() -> None:
    """Replacing a Strukturschritt beschreibung is valid."""
    output = _make_output([{"op": "replace", "path": "/schritte/s01/beschreibung", "value": "Neu"}])
    assert validate(output, STRUCTURE_TEMPLATE) is True


def test_structure_template_invalid_path_rejected() -> None:
    """Invalid path in structure template is rejected."""
    output = _make_output([{"op": "replace", "path": "/slots/s01/inhalt", "value": "wrong"}])
    assert validate(output, STRUCTURE_TEMPLATE) is False


# ---------------------------------------------------------------------------
# Algorithm template tests (QA fix: was untested)
# ---------------------------------------------------------------------------


def test_algorithm_template_valid_add_abschnitt() -> None:
    """Adding a new Algorithmusabschnitt is valid."""
    output = _make_output(
        [{"op": "add", "path": "/abschnitte/a01", "value": {"aktionstyp": "click"}}]
    )
    assert validate(output, ALGORITHM_TEMPLATE) is True


def test_algorithm_template_replace_aktion_aktionstyp() -> None:
    """Replacing aktionstyp of an EMMA-Aktion within an Abschnitt is valid."""
    output = _make_output(
        [{"op": "replace", "path": "/abschnitte/a01/aktionen/ak1/aktionstyp", "value": "click"}]
    )
    assert validate(output, ALGORITHM_TEMPLATE) is True


def test_algorithm_template_invalid_path_rejected() -> None:
    """Path from exploration template is rejected by algorithm template."""
    output = _make_output([{"op": "replace", "path": "/slots/s01/inhalt", "value": "wrong"}])
    assert validate(output, ALGORITHM_TEMPLATE) is False


# ---------------------------------------------------------------------------
# Gap: patch is not a dict → rejected (covers output_validator.py lines 43-45)
# ---------------------------------------------------------------------------


def test_non_dict_patch_fails_validation() -> None:
    """A patch that is not a dict (e.g. a string) is rejected by the validator."""
    output = _make_output([])
    # Bypass Pydantic to inject a non-dict patch (simulates corrupted LLM output)
    object.__setattr__(output, "patches", ["not a dict"])
    assert validate(output, EXPLORATION_TEMPLATE) is False


# ---------------------------------------------------------------------------
# Gap: patch without path key / non-string path → rejected (lines 60-62)
# ---------------------------------------------------------------------------


def test_patch_missing_path_key_fails_validation() -> None:
    """A patch dict without a 'path' key is rejected."""
    output = _make_output([{"op": "add", "value": "test"}])
    assert validate(output, EXPLORATION_TEMPLATE) is False


def test_patch_with_non_string_path_fails_validation() -> None:
    """A patch dict with a non-string path is rejected."""
    output = _make_output([{"op": "add", "path": 123, "value": "test"}])
    assert validate(output, EXPLORATION_TEMPLATE) is False


def test_patch_with_path_not_starting_with_slash_fails() -> None:
    """A path not starting with '/' is rejected."""
    output = _make_output([{"op": "add", "path": "slots/s1/inhalt", "value": "test"}])
    assert validate(output, EXPLORATION_TEMPLATE) is False


# ---------------------------------------------------------------------------
# Gap: validation without template (None) — only RFC 6902 syntax checked
# ---------------------------------------------------------------------------


def test_validation_without_template_accepts_any_valid_path() -> None:
    """Without a template, any syntactically valid RFC 6902 patch passes."""
    output = _make_output([{"op": "replace", "path": "/any/arbitrary/path", "value": "test"}])
    assert validate(output, artifact_template=None) is True


def test_validation_without_template_still_rejects_invalid_op() -> None:
    """Without a template, invalid ops are still rejected."""
    output = _make_output([{"op": "copy", "path": "/any/path", "value": "test"}])
    assert validate(output, artifact_template=None) is False
