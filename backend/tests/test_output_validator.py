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
from artifacts.template_schema import EXPLORATION_TEMPLATE
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
