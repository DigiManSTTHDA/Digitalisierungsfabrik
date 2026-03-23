"""Tests for Epic 02 — ArtifactTemplate schema and Executor.

Stories covered:
  02-01: ArtifactTemplate / TemplatePathPattern / TEMPLATES
  02-02: Executor pipeline (RFC-6902 validation, patch application, preservation check)
  02-03: Executor invalidation logic
"""

from __future__ import annotations

import pytest

from artifacts.models import (
    AlgorithmusStatus,
    CompletenessStatus,
    ExplorationArtifact,
    ExplorationSlot,
    StructureArtifact,
    Strukturschritt,
    Strukturschritttyp,
)
from artifacts.template_schema import (
    ALGORITHM_TEMPLATE,
    EXPLORATION_TEMPLATE,
    STRUCTURE_TEMPLATE,
    TEMPLATES,
)
from core.executor import Executor

# ===========================================================================
# Story 02-01 — ArtifactTemplate tests
# ===========================================================================


class TestExplorationTemplate:
    def test_replace_titel_valid(self) -> None:
        assert EXPLORATION_TEMPLATE.is_valid_patch("replace", "/slots/slot_01/titel") is True

    def test_replace_inhalt_valid(self) -> None:
        assert EXPLORATION_TEMPLATE.is_valid_patch("replace", "/slots/slot_01/inhalt") is True

    def test_add_inhalt_invalid(self) -> None:
        """add is not allowed on /inhalt — only replace."""
        assert EXPLORATION_TEMPLATE.is_valid_patch("add", "/slots/slot_01/inhalt") is False

    def test_replace_nonexistent_field_invalid(self) -> None:
        assert EXPLORATION_TEMPLATE.is_valid_patch("replace", "/slots/slot_01/nonexistent") is False


class TestStructureTemplate:
    def test_add_whole_step_valid(self) -> None:
        assert STRUCTURE_TEMPLATE.is_valid_patch("add", "/schritte/s01") is True

    def test_copy_op_invalid(self) -> None:
        """copy is not an allowed operation."""
        assert STRUCTURE_TEMPLATE.is_valid_patch("copy", "/schritte/s01/titel") is False


class TestAlgorithmTemplate:
    def test_add_aktion_valid(self) -> None:
        assert ALGORITHM_TEMPLATE.is_valid_patch("add", "/abschnitte/a01/aktionen/ak01") is True

    def test_replace_emma_kompatibel_valid(self) -> None:
        assert (
            ALGORITHM_TEMPLATE.is_valid_patch(
                "replace", "/abschnitte/a01/aktionen/ak01/emma_kompatibel"
            )
            is True
        )


class TestTemplatesDict:
    def test_templates_has_exactly_three_keys(self) -> None:
        assert set(TEMPLATES.keys()) == {"exploration", "structure", "algorithm"}


# ===========================================================================
# F1 Bug Fix — Patch-Pfad-Validierung: numerische Keys abgelehnt
# ===========================================================================


class TestStructureTemplateKeyFormat:
    """Tests for F1 fix: schritte paths must use string IDs (s1, s2, ...) not numeric indices."""

    def test_schema_rejects_numeric_key_for_whole_step(self) -> None:
        """Numeric index like /schritte/0 must be rejected — schritte is a dict, not an array."""
        assert STRUCTURE_TEMPLATE.is_valid_patch("add", "/schritte/0") is False

    def test_schema_rejects_numeric_key_for_titel(self) -> None:
        assert STRUCTURE_TEMPLATE.is_valid_patch("replace", "/schritte/0/titel") is False

    def test_schema_rejects_numeric_key_for_beschreibung(self) -> None:
        assert STRUCTURE_TEMPLATE.is_valid_patch("replace", "/schritte/0/beschreibung") is False

    def test_schema_rejects_numeric_key_for_typ(self) -> None:
        assert STRUCTURE_TEMPLATE.is_valid_patch("replace", "/schritte/0/typ") is False

    def test_schema_accepts_string_key_s1(self) -> None:
        """String key s1 must be accepted."""
        assert STRUCTURE_TEMPLATE.is_valid_patch("add", "/schritte/s1") is True

    def test_schema_accepts_string_key_s2(self) -> None:
        assert STRUCTURE_TEMPLATE.is_valid_patch("replace", "/schritte/s2/titel") is True

    def test_schema_accepts_string_key_s99(self) -> None:
        assert STRUCTURE_TEMPLATE.is_valid_patch("replace", "/schritte/s99/beschreibung") is True

    def test_schema_accepts_string_key_s01(self) -> None:
        """Multi-digit padded keys like s01 are also valid."""
        assert STRUCTURE_TEMPLATE.is_valid_patch("add", "/schritte/s01") is True

    def test_schema_accepts_string_key_s10_titel(self) -> None:
        assert STRUCTURE_TEMPLATE.is_valid_patch("replace", "/schritte/s10/titel") is True

    def test_schema_accepts_bare_text_key_with_s_prefix(self) -> None:
        """CR-002 bugfix: 'schritt_1' starts with 's' and is valid under s[^/]+ regex."""
        assert STRUCTURE_TEMPLATE.is_valid_patch("add", "/schritte/schritt_1") is True

    def test_schema_rejects_key_starting_with_digit(self) -> None:
        """Key starting with a digit (no 's' prefix) must be rejected."""
        assert STRUCTURE_TEMPLATE.is_valid_patch("add", "/schritte/1s") is False

    # CR-002: Extended string ID format tests (s[^/]+ regex)
    def test_schema_accepts_key_s2a(self) -> None:
        """CR-002 bugfix: s2a is valid — regex must be s[^/]+, not s\\d+."""
        assert STRUCTURE_TEMPLATE.is_valid_patch("add", "/schritte/s2a") is True

    def test_schema_accepts_key_s_gutschrift(self) -> None:
        """CR-002 bugfix: s_gutschrift is valid — regex must be s[^/]+, not s\\d+."""
        assert STRUCTURE_TEMPLATE.is_valid_patch("add", "/schritte/s_gutschrift") is True


# ===========================================================================
# F1b Integration — Executor produces helpful message for invalid key
# ===========================================================================


class TestExecutorNumericKeyMessage:
    """Integration test: applying a patch with a numeric key produces a useful error message."""

    def test_numeric_key_whole_step_rejected_by_template(
        self, executor: Executor, structure_artifact_with_refs: StructureArtifact
    ) -> None:
        """Numeric path /schritte/0/titel is caught at template-schema step (Step 2)."""
        patches = [{"op": "replace", "path": "/schritte/0/titel", "value": "Hallo"}]
        result = executor.apply_patches("structure", structure_artifact_with_refs, patches)
        assert result.success is False
        assert result.artifact is None
        assert result.error is not None
        # Error should mention the path/op combination — not a raw Python traceback
        assert "/schritte/0/titel" in result.error or "Template" in result.error


# ===========================================================================
# Fixtures
# ===========================================================================


@pytest.fixture
def executor() -> Executor:
    return Executor()


@pytest.fixture
def exploration_artifact() -> ExplorationArtifact:
    slot = ExplorationSlot(
        slot_id="s01",
        titel="Test",
        inhalt="alt",
        completeness_status=CompletenessStatus.leer,
    )
    return ExplorationArtifact(slots={"s01": slot}, version=0)


@pytest.fixture
def structure_artifact_with_refs() -> StructureArtifact:
    s01 = Strukturschritt(
        schritt_id="s01",
        titel="Schritt 1",
        typ=Strukturschritttyp.aktion,
        beschreibung="alt",
        reihenfolge=1,
        algorithmus_ref=["a01", "a02"],
        completeness_status=CompletenessStatus.leer,
        algorithmus_status=AlgorithmusStatus.ausstehend,
    )
    s02 = Strukturschritt(
        schritt_id="s02",
        titel="Schritt 2",
        typ=Strukturschritttyp.entscheidung,
        beschreibung="entscheidung",
        reihenfolge=2,
        algorithmus_ref=["a03"],
        completeness_status=CompletenessStatus.leer,
        algorithmus_status=AlgorithmusStatus.ausstehend,
    )
    return StructureArtifact(schritte={"s01": s01, "s02": s02}, version=0)


# ===========================================================================
# Story 02-02 — Executor core pipeline
# ===========================================================================


class TestExecutorHappyPath:
    def test_replace_inhalt(
        self, executor: Executor, exploration_artifact: ExplorationArtifact
    ) -> None:
        patches = [{"op": "replace", "path": "/slots/s01/inhalt", "value": "neu"}]
        result = executor.apply_patches("exploration", exploration_artifact, patches)
        assert result.success is True
        assert result.artifact is not None
        assert result.artifact.slots["s01"].inhalt == "neu"  # type: ignore[union-attr]
        assert result.artifact.version == 1

    def test_add_new_slot(
        self, executor: Executor, exploration_artifact: ExplorationArtifact
    ) -> None:
        new_slot = {
            "slot_id": "s02",
            "titel": "Neu",
            "inhalt": "",
            "completeness_status": "leer",
        }
        patches = [{"op": "add", "path": "/slots/s02", "value": new_slot}]
        result = executor.apply_patches("exploration", exploration_artifact, patches)
        assert result.success is True
        assert result.artifact is not None
        assert "s02" in result.artifact.slots  # type: ignore[union-attr]
        assert result.artifact.version == 1

    def test_remove_slot(
        self, executor: Executor, exploration_artifact: ExplorationArtifact
    ) -> None:
        patches = [{"op": "remove", "path": "/slots/s01"}]
        result = executor.apply_patches("exploration", exploration_artifact, patches)
        assert result.success is True
        assert result.artifact is not None
        assert "s01" not in result.artifact.slots  # type: ignore[union-attr]
        assert result.artifact.version == 1

    def test_empty_patches_no_version_bump(
        self, executor: Executor, exploration_artifact: ExplorationArtifact
    ) -> None:
        result = executor.apply_patches("exploration", exploration_artifact, [])
        assert result.success is True
        assert result.artifact is not None
        assert result.artifact.version == 0  # no bump


class TestExecutorRFC6902Syntax:
    def test_copy_op_rejected(
        self, executor: Executor, exploration_artifact: ExplorationArtifact
    ) -> None:
        patches = [{"op": "copy", "path": "/slots/s01/inhalt"}]
        result = executor.apply_patches("exploration", exploration_artifact, patches)
        assert result.success is False
        assert result.artifact is None
        assert result.error is not None
        assert exploration_artifact.version == 0  # unchanged

    def test_empty_path_rejected(
        self, executor: Executor, exploration_artifact: ExplorationArtifact
    ) -> None:
        patches = [{"op": "replace", "path": "", "value": "x"}]
        result = executor.apply_patches("exploration", exploration_artifact, patches)
        assert result.success is False
        assert result.artifact is None
        assert result.error is not None

    def test_missing_op_key_rejected(
        self, executor: Executor, exploration_artifact: ExplorationArtifact
    ) -> None:
        patches = [{"path": "/slots/s01/inhalt", "value": "x"}]
        result = executor.apply_patches("exploration", exploration_artifact, patches)
        assert result.success is False
        assert result.artifact is None
        assert result.error is not None

    def test_missing_path_key_rejected(
        self, executor: Executor, exploration_artifact: ExplorationArtifact
    ) -> None:
        patches = [{"op": "replace", "value": "x"}]
        result = executor.apply_patches("exploration", exploration_artifact, patches)
        assert result.success is False
        assert result.artifact is None
        assert result.error is not None


class TestExecutorTemplateViolation:
    def test_unlisted_path_rejected(
        self, executor: Executor, exploration_artifact: ExplorationArtifact
    ) -> None:
        patches = [{"op": "replace", "path": "/slots/s01/nonexistent", "value": "x"}]
        result = executor.apply_patches("exploration", exploration_artifact, patches)
        assert result.success is False
        assert result.artifact is None
        assert exploration_artifact.version == 0

    def test_forbidden_op_on_valid_path_rejected(
        self, executor: Executor, exploration_artifact: ExplorationArtifact
    ) -> None:
        """add is not allowed on /inhalt."""
        patches = [{"op": "add", "path": "/slots/s01/inhalt", "value": "x"}]
        result = executor.apply_patches("exploration", exploration_artifact, patches)
        assert result.success is False
        assert result.artifact is None


class TestExecutorPatchFailure:
    def test_nonexistent_slot_replace_fails(
        self, executor: Executor, exploration_artifact: ExplorationArtifact
    ) -> None:
        patches = [{"op": "replace", "path": "/slots/s99/inhalt", "value": "x"}]
        result = executor.apply_patches("exploration", exploration_artifact, patches)
        assert result.success is False
        assert result.artifact is None
        assert exploration_artifact.version == 0

    def test_partial_patch_rolls_back(
        self, executor: Executor, exploration_artifact: ExplorationArtifact
    ) -> None:
        """First patch is valid, second patch references nonexistent path — full rollback."""
        patches = [
            {"op": "replace", "path": "/slots/s01/inhalt", "value": "neu"},
            {"op": "replace", "path": "/slots/s99/inhalt", "value": "also_neu"},
        ]
        result = executor.apply_patches("exploration", exploration_artifact, patches)
        assert result.success is False
        assert result.artifact is None
        assert exploration_artifact.version == 0


class TestExecutorPreservationCheck:
    def test_preservation_check_catches_unadressed_change(
        self,
        executor: Executor,
        exploration_artifact: ExplorationArtifact,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Simulate a patch that modifies an extra field not in the patch list.

        We monkeypatch jsonpatch.apply_patch to return a dict where an extra field
        was modified, so the preservation check fires.
        """
        import jsonpatch as jp

        original_apply = jp.apply_patch

        def patched_apply(doc, patch, in_place=False):  # type: ignore[no-untyped-def]
            result = original_apply(doc, patch, in_place=False)
            # Inject an extra top-level change to simulate side effect
            result["version"] = 999  # version is skipped in check, use a real field instead
            # Actually add a field that would be noticed — we need a real collection field
            # Simulate side-effect: adding something to slots that wasn't addressed by patches
            # The patches only address /slots/s01/inhalt, but we also change slots["s_extra"]
            result["slots"]["s_extra"] = {
                "slot_id": "s_extra",
                "titel": "injected",
                "inhalt": "",
                "completeness_status": "leer",
            }
            return result

        monkeypatch.setattr(jp, "apply_patch", patched_apply)

        patches = [{"op": "replace", "path": "/slots/s01/inhalt", "value": "neu"}]
        result = executor.apply_patches("exploration", exploration_artifact, patches)
        assert result.success is False
        assert result.artifact is None
        assert result.error is not None


# ===========================================================================
# Story 02-03 — Invalidation logic
# ===========================================================================


class TestInvalidationTriggered:
    def test_replace_beschreibung_returns_refs(
        self, executor: Executor, structure_artifact_with_refs: StructureArtifact
    ) -> None:
        patches = [{"op": "replace", "path": "/schritte/s01/beschreibung", "value": "neu"}]
        result = executor.apply_patches("structure", structure_artifact_with_refs, patches)
        assert result.success is True
        assert set(result.invalidated_abschnitt_ids) == {"a01", "a02"}

    def test_replace_typ_returns_refs(
        self, executor: Executor, structure_artifact_with_refs: StructureArtifact
    ) -> None:
        patches = [{"op": "replace", "path": "/schritte/s01/typ", "value": "entscheidung"}]
        result = executor.apply_patches("structure", structure_artifact_with_refs, patches)
        assert result.success is True
        assert set(result.invalidated_abschnitt_ids) == {"a01", "a02"}

    def test_replace_bedingung_returns_refs(
        self, executor: Executor, structure_artifact_with_refs: StructureArtifact
    ) -> None:
        patches = [{"op": "replace", "path": "/schritte/s02/bedingung", "value": "wenn X"}]
        result = executor.apply_patches("structure", structure_artifact_with_refs, patches)
        assert result.success is True
        assert set(result.invalidated_abschnitt_ids) == {"a03"}

    def test_replace_ausnahme_beschreibung_returns_refs(
        self, executor: Executor, structure_artifact_with_refs: StructureArtifact
    ) -> None:
        patches = [
            {"op": "replace", "path": "/schritte/s02/ausnahme_beschreibung", "value": "Fehler"}
        ]
        result = executor.apply_patches("structure", structure_artifact_with_refs, patches)
        assert result.success is True
        assert set(result.invalidated_abschnitt_ids) == {"a03"}

    def test_batch_patch_deduplicates_refs(
        self, executor: Executor, structure_artifact_with_refs: StructureArtifact
    ) -> None:
        patches = [
            {"op": "replace", "path": "/schritte/s01/beschreibung", "value": "neu1"},
            {"op": "replace", "path": "/schritte/s02/beschreibung", "value": "neu2"},
        ]
        result = executor.apply_patches("structure", structure_artifact_with_refs, patches)
        assert result.success is True
        assert set(result.invalidated_abschnitt_ids) == {"a01", "a02", "a03"}

    def test_remove_whole_step_returns_refs(
        self, executor: Executor, structure_artifact_with_refs: StructureArtifact
    ) -> None:
        patches = [{"op": "remove", "path": "/schritte/s01"}]
        result = executor.apply_patches("structure", structure_artifact_with_refs, patches)
        assert result.success is True
        assert "a01" in result.invalidated_abschnitt_ids
        assert "a02" in result.invalidated_abschnitt_ids


class TestInvalidationNotTriggered:
    def test_replace_titel_no_invalidation(
        self, executor: Executor, structure_artifact_with_refs: StructureArtifact
    ) -> None:
        patches = [{"op": "replace", "path": "/schritte/s01/titel", "value": "Neuer Titel"}]
        result = executor.apply_patches("structure", structure_artifact_with_refs, patches)
        assert result.success is True
        assert result.invalidated_abschnitt_ids == []

    def test_replace_reihenfolge_no_invalidation(
        self, executor: Executor, structure_artifact_with_refs: StructureArtifact
    ) -> None:
        patches = [{"op": "replace", "path": "/schritte/s01/reihenfolge", "value": 99}]
        result = executor.apply_patches("structure", structure_artifact_with_refs, patches)
        assert result.success is True
        assert result.invalidated_abschnitt_ids == []

    def test_replace_nachfolger_no_invalidation(
        self, executor: Executor, structure_artifact_with_refs: StructureArtifact
    ) -> None:
        patches = [{"op": "replace", "path": "/schritte/s01/nachfolger", "value": ["s02"]}]
        result = executor.apply_patches("structure", structure_artifact_with_refs, patches)
        assert result.success is True
        assert result.invalidated_abschnitt_ids == []

    def test_replace_algorithmus_ref_no_invalidation(
        self, executor: Executor, structure_artifact_with_refs: StructureArtifact
    ) -> None:
        patches = [{"op": "replace", "path": "/schritte/s01/algorithmus_ref", "value": ["a99"]}]
        result = executor.apply_patches("structure", structure_artifact_with_refs, patches)
        assert result.success is True
        assert result.invalidated_abschnitt_ids == []

    def test_replace_spannungsfeld_no_invalidation(
        self, executor: Executor, structure_artifact_with_refs: StructureArtifact
    ) -> None:
        patches = [{"op": "replace", "path": "/schritte/s01/spannungsfeld", "value": "Konfikt"}]
        result = executor.apply_patches("structure", structure_artifact_with_refs, patches)
        assert result.success is True
        assert result.invalidated_abschnitt_ids == []

    def test_replace_completeness_status_no_invalidation(
        self, executor: Executor, structure_artifact_with_refs: StructureArtifact
    ) -> None:
        patches = [
            {"op": "replace", "path": "/schritte/s01/completeness_status", "value": "teilweise"}
        ]
        result = executor.apply_patches("structure", structure_artifact_with_refs, patches)
        assert result.success is True
        assert result.invalidated_abschnitt_ids == []

    def test_replace_algorithmus_status_no_invalidation(
        self, executor: Executor, structure_artifact_with_refs: StructureArtifact
    ) -> None:
        patches = [
            {"op": "replace", "path": "/schritte/s01/algorithmus_status", "value": "invalidiert"}
        ]
        result = executor.apply_patches("structure", structure_artifact_with_refs, patches)
        assert result.success is True
        assert result.invalidated_abschnitt_ids == []

    def test_replace_konvergenz_no_invalidation(
        self, executor: Executor, structure_artifact_with_refs: StructureArtifact
    ) -> None:
        """CR-002: konvergenz is NOT in _INVALIDATING_FIELDS."""
        patches = [{"op": "replace", "path": "/schritte/s01/konvergenz", "value": "s99"}]
        result = executor.apply_patches("structure", structure_artifact_with_refs, patches)
        assert result.success is True
        assert result.invalidated_abschnitt_ids == []

    def test_replace_abbruchbedingung_no_invalidation(
        self, executor: Executor, structure_artifact_with_refs: StructureArtifact
    ) -> None:
        """CR-002: abbruchbedingung is NOT in _INVALIDATING_FIELDS."""
        patches = [
            {"op": "replace", "path": "/schritte/s01/abbruchbedingung", "value": "Alle geprüft"}
        ]
        result = executor.apply_patches("structure", structure_artifact_with_refs, patches)
        assert result.success is True
        assert result.invalidated_abschnitt_ids == []


class TestInvalidationCR002:
    """CR-002: regeln and schleifenkoerper trigger invalidation."""

    def test_replace_regeln_triggers_invalidation(
        self, executor: Executor, structure_artifact_with_refs: StructureArtifact
    ) -> None:
        regeln_value = [
            {"bedingung": "Betrag > 500€", "nachfolger": "s01", "bezeichnung": ""},
        ]
        patches = [{"op": "replace", "path": "/schritte/s02/regeln", "value": regeln_value}]
        result = executor.apply_patches("structure", structure_artifact_with_refs, patches)
        assert result.success is True
        assert set(result.invalidated_abschnitt_ids) == {"a03"}

    def test_replace_schleifenkoerper_triggers_invalidation(
        self, executor: Executor, structure_artifact_with_refs: StructureArtifact
    ) -> None:
        patches = [
            {"op": "replace", "path": "/schritte/s01/schleifenkoerper", "value": ["s02"]}
        ]
        result = executor.apply_patches("structure", structure_artifact_with_refs, patches)
        assert result.success is True
        assert set(result.invalidated_abschnitt_ids) == {"a01", "a02"}


class TestCR002PatchPaths:
    """CR-002: Template accepts new patch paths for control flow fields."""

    def test_replace_regeln_accepted(self) -> None:
        assert STRUCTURE_TEMPLATE.is_valid_patch("replace", "/schritte/s1/regeln") is True

    def test_replace_schleifenkoerper_accepted(self) -> None:
        assert STRUCTURE_TEMPLATE.is_valid_patch("replace", "/schritte/s1/schleifenkoerper") is True

    def test_add_abbruchbedingung_accepted(self) -> None:
        assert STRUCTURE_TEMPLATE.is_valid_patch("add", "/schritte/s1/abbruchbedingung") is True

    def test_replace_abbruchbedingung_accepted(self) -> None:
        assert STRUCTURE_TEMPLATE.is_valid_patch("replace", "/schritte/s1/abbruchbedingung") is True

    def test_add_konvergenz_accepted(self) -> None:
        assert STRUCTURE_TEMPLATE.is_valid_patch("add", "/schritte/s1/konvergenz") is True

    def test_replace_konvergenz_accepted(self) -> None:
        assert STRUCTURE_TEMPLATE.is_valid_patch("replace", "/schritte/s1/konvergenz") is True


class TestInvalidationEdgeCases:
    def test_step_without_algorithmus_ref_empty_list(self, executor: Executor) -> None:
        s = Strukturschritt(
            schritt_id="s01",
            titel="T",
            typ=Strukturschritttyp.aktion,
            beschreibung="old",
            reihenfolge=1,
            algorithmus_ref=[],
            completeness_status=CompletenessStatus.leer,
            algorithmus_status=AlgorithmusStatus.ausstehend,
        )
        art = StructureArtifact(schritte={"s01": s}, version=0)
        patches = [{"op": "replace", "path": "/schritte/s01/beschreibung", "value": "neu"}]
        result = executor.apply_patches("structure", art, patches)
        assert result.success is True
        assert result.invalidated_abschnitt_ids == []

    def test_add_new_step_without_refs_empty_list(
        self, executor: Executor, structure_artifact_with_refs: StructureArtifact
    ) -> None:
        new_step = {
            "schritt_id": "s99",
            "titel": "Neu",
            "typ": "aktion",
            "beschreibung": "",
            "reihenfolge": 99,
            "nachfolger": [],
            "bedingung": None,
            "ausnahme_beschreibung": None,
            "algorithmus_ref": [],
            "completeness_status": "leer",
            "algorithmus_status": "ausstehend",
            "spannungsfeld": None,
        }
        patches = [{"op": "add", "path": "/schritte/s99", "value": new_step}]
        result = executor.apply_patches("structure", structure_artifact_with_refs, patches)
        assert result.success is True
        assert result.invalidated_abschnitt_ids == []

    def test_failing_patch_returns_empty_invalidated_ids(
        self, executor: Executor, structure_artifact_with_refs: StructureArtifact
    ) -> None:
        """A patch that fails in step 4 must return empty invalidated_abschnitt_ids."""
        patches = [{"op": "replace", "path": "/schritte/nonexistent/beschreibung", "value": "x"}]
        result = executor.apply_patches("structure", structure_artifact_with_refs, patches)
        assert result.success is False
        assert result.invalidated_abschnitt_ids == []

    def test_exploration_artifact_no_invalidation(
        self, executor: Executor, exploration_artifact: ExplorationArtifact
    ) -> None:
        patches = [{"op": "replace", "path": "/slots/s01/inhalt", "value": "x"}]
        result = executor.apply_patches("exploration", exploration_artifact, patches)
        assert result.success is True
        assert result.invalidated_abschnitt_ids == []
