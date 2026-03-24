"""Tests for turn_debug_log — CR-010: lückenloses Debug-Logging."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.turn_debug_log import write_turn_debug


@pytest.fixture()
def debug_dir(tmp_path: Path) -> str:
    """Return a temporary base directory for debug output."""
    return str(tmp_path)


class TestWriteTurnDebug:
    """Tests for write_turn_debug() with CR-010 extended parameters."""

    def test_basic_write_creates_json_file(self, debug_dir: str) -> None:
        """A basic call creates a correctly named JSON file."""
        write_turn_debug(
            base_dir=debug_dir,
            project_id="proj_1",
            turn_number=1,
            mode="exploration",
            system_prompt="You are a helper.",
            messages=[{"role": "user", "content": "hello"}],
            tool_choice=None,
            response_nutzeraeusserung="Hi!",
            response_tool_input={"nutzeraeusserung": "Hi!", "patches": []},
        )
        path = Path(debug_dir) / "debug_turns" / "proj_1" / "turn_001_exploration.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["turn"] == 1
        assert data["mode"] == "exploration"
        assert data["request"]["system_prompt"] == "You are a helper."
        assert data["response"]["nutzeraeusserung"] == "Hi!"

    def test_llm_raw_section_present(self, debug_dir: str) -> None:
        """CR-010: llm_raw section with raw/final nutzeraeusserung and summarizer flag."""
        write_turn_debug(
            base_dir=debug_dir,
            project_id="proj_2",
            turn_number=5,
            mode="structuring",
            system_prompt="sys",
            messages=[],
            tool_choice=None,
            response_nutzeraeusserung="summarized text",
            response_tool_input={"patches": [{"op": "add", "path": "/schritte/s1"}]},
            raw_llm_nutzeraeusserung="original LLM text",
            raw_llm_tool_input={"patches": [{"op": "add", "path": "/schritte/s1"}], "nutzeraeusserung": "original LLM text"},
            final_nutzeraeusserung="summarized text",
            summarizer_active=True,
        )
        path = Path(debug_dir) / "debug_turns" / "proj_2" / "turn_005_structuring.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["llm_raw"]["raw_nutzeraeusserung"] == "original LLM text"
        assert data["llm_raw"]["final_nutzeraeusserung"] == "summarized text"
        assert data["llm_raw"]["summarizer_active"] is True
        assert data["llm_raw"]["raw_tool_input"]["patches"][0]["op"] == "add"

    def test_artifacts_section_with_before_after(self, debug_dir: str) -> None:
        """CR-010: artifacts section contains before/after snapshots."""
        before = {"schritte": {}}
        after = {"schritte": {"s1": {"titel": "Schritt 1"}}}
        write_turn_debug(
            base_dir=debug_dir,
            project_id="proj_3",
            turn_number=7,
            mode="structuring",
            system_prompt="sys",
            messages=[],
            tool_choice=None,
            response_nutzeraeusserung="done",
            response_tool_input={},
            artifact_before=before,
            artifact_after=after,
        )
        path = Path(debug_dir) / "debug_turns" / "proj_3" / "turn_007_structuring.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["artifacts"]["before"] == before
        assert data["artifacts"]["after"] == after

    def test_artifacts_null_when_no_patches(self, debug_dir: str) -> None:
        """CR-010: artifacts before/after are null when no patches applied."""
        write_turn_debug(
            base_dir=debug_dir,
            project_id="proj_4",
            turn_number=3,
            mode="exploration",
            system_prompt="sys",
            messages=[],
            tool_choice=None,
            response_nutzeraeusserung="text",
            response_tool_input={},
        )
        path = Path(debug_dir) / "debug_turns" / "proj_4" / "turn_003_exploration.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["artifacts"]["before"] is None
        assert data["artifacts"]["after"] is None

    def test_flags_section(self, debug_dir: str) -> None:
        """CR-010: flags list is included in payload."""
        write_turn_debug(
            base_dir=debug_dir,
            project_id="proj_5",
            turn_number=2,
            mode="structuring",
            system_prompt="sys",
            messages=[],
            tool_choice=None,
            response_nutzeraeusserung="text",
            response_tool_input={},
            flags=["phase_complete", "artefakt_updated"],
        )
        path = Path(debug_dir) / "debug_turns" / "proj_5" / "turn_002_structuring.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["flags"] == ["phase_complete", "artefakt_updated"]

    def test_execution_section_with_patches(self, debug_dir: str) -> None:
        """CR-010: execution section records patches_applied and patch_result."""
        patches = [{"op": "add", "path": "/schritte/s1", "value": {}}]
        write_turn_debug(
            base_dir=debug_dir,
            project_id="proj_6",
            turn_number=4,
            mode="structuring",
            system_prompt="sys",
            messages=[],
            tool_choice=None,
            response_nutzeraeusserung="text",
            response_tool_input={},
            patches_applied=patches,
            patch_result="success",
        )
        path = Path(debug_dir) / "debug_turns" / "proj_6" / "turn_004_structuring.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["execution"]["patches_applied"] == patches
        assert data["execution"]["patch_result"] == "success"

    def test_init_mode_filename(self, debug_dir: str) -> None:
        """CR-010: init turns use mode name like 'init_structuring' for unique filenames."""
        write_turn_debug(
            base_dir=debug_dir,
            project_id="proj_7",
            turn_number=19,
            mode="init_structuring",
            system_prompt="sys",
            messages=[],
            tool_choice=None,
            response_nutzeraeusserung="init done",
            response_tool_input={},
        )
        path = Path(debug_dir) / "debug_turns" / "proj_7" / "turn_019_init_structuring.json"
        assert path.exists()

    def test_defaults_produce_valid_json(self, debug_dir: str) -> None:
        """All new CR-010 params default to safe values — no crash on minimal call."""
        write_turn_debug(
            base_dir=debug_dir,
            project_id="proj_8",
            turn_number=1,
            mode="moderator",
            system_prompt="sys",
            messages=[],
            tool_choice=None,
            response_nutzeraeusserung="hello",
            response_tool_input=None,
        )
        path = Path(debug_dir) / "debug_turns" / "proj_8" / "turn_001_moderator.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["llm_raw"]["summarizer_active"] is False
        assert data["llm_raw"]["raw_nutzeraeusserung"] == ""
        assert data["artifacts"]["before"] is None
        assert data["flags"] is None
