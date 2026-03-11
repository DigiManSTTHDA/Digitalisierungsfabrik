# Epic 07 – Moderator & Phase Transitions

## Summary

Implement the `Moderator` mode and the phase-transition logic. The Moderator runs after
every turn and decides whether the current phase (Exploration, Structuring, Specification,
Validation) is sufficiently complete to advance. When it decides to transition, it updates
the active phase in Working Memory and the Orchestrator routes the next turn to the new mode.

This epic corresponds to **Implementation Step 7** in `AGENTS.md` / `hla_architecture.md`.

## Goal

The system autonomously moves from the Exploration phase to the Structuring phase at the
right moment, without the user having to explicitly request it. The transition is visible
in the UI: the artifact pane switches focus to the Structure Artifact and a system message
appears in the chat.

## Testable Increment

- In the browser: after enough exploration dialogue (or a forced trigger via a test flag),
  the chat pane shows a system message like _"Wir haben genug Informationen gesammelt.
  Ich beginne jetzt mit der Strukturierung."_ and the artifact pane switches to the
  Structure Artifact tab
- `pytest backend/tests/test_moderator.py` → transition fires at the correct turn,
  correct mode is activated in Working Memory
- Phase can also be triggered manually via a test endpoint
  (`POST /api/projects/{id}/debug/advance-phase`) for easier QA

## Dependencies

- Epic 06 (frontend must exist to make the transition visible to the user)

## Key Deliverables

- `backend/modes/moderator.py` – `Moderator` mode with completeness heuristics
- `backend/core/phase_transition.py` – transition logic, phase enum, control flags
- `backend/api/routes.py` updated – debug endpoint `advance-phase`
- `frontend/src/components/ChatPane.tsx` updated – renders system/phase-change messages
  differently from AI messages
- `backend/tests/test_moderator.py` – transition condition tests
- `backend/tests/test_phase_transition.py` – full phase-advance integration test

## Stories

_To be defined before this epic begins._
