"""Turn Debug Logger — writes full LLM request/response per turn to JSON files.

When LLM_DEBUG_LOG=true (env var or settings), each orchestrator turn produces
a JSON file in data/debug_turns/<project_id>/ with the complete payload:

  - system_prompt: the full system prompt sent to the LLM
  - messages: the dialog history messages sent (last N turns)
  - tool_choice: the tool_choice setting used
  - response_nutzeraeusserung: the LLM's text response
  - response_patches: the RFC 6902 patches returned
  - response_phasenstatus: the LLM's phase status assessment
  - response_raw_tool_input: the full raw tool_input dict
  - token_usage: prompt/completion/total tokens for this turn
  - cumulative_tokens: running totals since project start

Files are named: turn_{turn_number:03d}_{mode}.json

SDD reference: NFR 8.1.3 (Beobachtbarkeit).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)


def write_turn_debug(
    *,
    base_dir: str,
    project_id: str,
    turn_number: int,
    mode: str,
    system_prompt: str,
    messages: list[dict],
    tool_choice: dict | None,
    response_nutzeraeusserung: str,
    response_tool_input: dict | None,
    patches_applied: list[dict] | None = None,
    patch_result: str | None = None,
    token_usage: dict | None = None,
    cumulative_tokens: dict | None = None,
) -> None:
    """Write a single turn's full LLM I/O to a JSON debug file."""
    try:
        turn_dir = Path(base_dir) / "debug_turns" / project_id
        turn_dir.mkdir(parents=True, exist_ok=True)

        tool_input = response_tool_input or {}

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "project_id": project_id,
            "turn": turn_number,
            "mode": mode,
            "request": {
                "system_prompt": system_prompt,
                "system_prompt_length": len(system_prompt),
                "messages": messages,
                "message_count": len(messages),
                "tool_choice": tool_choice,
            },
            "response": {
                "nutzeraeusserung": response_nutzeraeusserung,
                "patches": tool_input.get("patches", []),
                "phasenstatus": tool_input.get("phasenstatus", ""),
                "raw_tool_input": tool_input,
            },
            "execution": {
                "patches_applied": patches_applied,
                "patch_result": patch_result,
            },
            "token_usage": token_usage or {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            "cumulative_tokens": cumulative_tokens or {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
        }

        filename = f"turn_{turn_number:03d}_{mode}.json"
        filepath = turn_dir / filename

        filepath.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        logger.debug("turn_debug_log.written", path=str(filepath))

    except Exception:
        logger.warning("turn_debug_log.write_failed", exc_info=True)
