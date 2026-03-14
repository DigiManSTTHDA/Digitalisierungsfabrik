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
- `backend/api/router.py` updated – debug endpoint `advance-phase` (HLA Section 6 path)
- `frontend/src/components/ChatPane.tsx` updated – renders system/phase-change messages
  differently from AI messages
- `backend/tests/test_moderator.py` – transition condition tests
- `backend/tests/test_phase_transition.py` – full phase-advance integration test

## OpenAPI Contract Note

This epic adds one new REST endpoint:

- `POST /api/projects/{id}/debug/advance-phase`

This endpoint must have an explicit Pydantic response schema in `backend/api/schemas.py`.
After implementing it:

1. Regenerate the OpenAPI snapshot: `curl http://localhost:8000/openapi.json > api-contract/openapi.json`
2. Regenerate frontend types: `cd frontend && npm run generate-api:file`
3. Commit both `api-contract/openapi.json` and `frontend/src/generated/api.d.ts`
4. Verify `tsc --noEmit` passes

Frontend changes in this epic (`ChatPane.tsx` update for phase-change messages) must use
the generated types from `frontend/src/generated/api.d.ts`, not locally-defined interfaces.

## Stories

> **Scope Note:** StructuringMode (Epic 08) is still a stub. The Moderator can
> transition to it, but it will respond with a placeholder. This is consistent
> with the stub pattern from Epic 03.

> **Path Note:** `backend/core/phase_transition.py` is not explicitly listed in
> HLA Section 6 but is within the HLA-defined `backend/core/` directory (same
> pattern as `artifact_router.py` and `events.py` from earlier epics).

### Story 07-01: Moderator LLM Implementation + System Prompt

**User Story:**
As a developer,
I want the Moderator stub replaced with a real LLM-based implementation that
analyzes the current system state and guides the user through phase transitions,
so that the system can intelligently decide when to advance phases.

**FR/NFR Traceability:** FR-D-02 (Moderator-Modus), FR-D-09 (Phasenwechsel-Protokoll),
FR-D-11 (Systemstart-Verhalten), SDD 6.6.5 (Moderator), SDD 6.1.2 (Phasenwechsel).

**Acceptance Criteria:**

1. `backend/modes/moderator.py` replaces the stub with a real implementation.
2. `backend/prompts/moderator.md` exists (HLA Section 6 path) — German system prompt.
3. Moderator receives `ModeContext` with all artifacts, WM, dialog history, and
   `completeness_state` (FR-D-02).
4. Moderator uses `LLMClient.complete()` with the moderator system prompt.
5. Moderator does NOT produce patches (SDD 6.6.5: "keine Schreiboperationen auf
   Artefakt-Slots").
6. Moderator's output includes:
   - `nutzeraeusserung`: summary of current state + phase transition proposal
   - `patches`: always empty list
   - `phasenstatus`: `in_progress` (Moderator itself does not advance phases)
   - `flags`: may include a new `mode_switch` flag to signal the target mode
7. When activated due to `phase_complete`:
   - Summarizes what was achieved in the current phase
   - Proposes the next phase to the user
   - Waits for user confirmation before the Orchestrator switches
8. When activated due to `escalate` (panic button):
   - Analyzes the situation from dialog history
   - Proposes a solution strategy
9. Moderator accepts optional `LLMClient` parameter (same pattern as ExplorationMode).
   When `None`, returns a deterministic response for testing.
10. Tests in `backend/tests/test_moderator.py`:
    - `test_moderator_without_llm_returns_summary` — stub mode returns non-empty response
    - `test_moderator_with_mock_llm_calls_complete` — LLM called with correct system prompt
    - `test_moderator_produces_no_patches` — patches always empty
    - `test_moderator_receives_full_context` — context includes all required fields

**Definition of Done:**

- [x] `backend/modes/moderator.py` replaced with real implementation
- [x] `backend/prompts/moderator.md` exists (German)
- [x] Moderator uses LLMClient for generation
- [x] Moderator produces no patches (SDD 6.6.5)
- [x] System prompt is in German (FR-A-08)
- [x] Tests in `backend/tests/test_moderator.py` (4+ tests)
- [x] `ruff check .` passes (exit 0)
- [x] `ruff format --check .` passes (exit 0)
- [x] `python -m mypy . --explicit-package-bases` passes (exit 0)
- [x] `pytest --tb=short -q` passes (exit 0, no regressions)

---

### Story 07-02: Phase Transition Logic in Orchestrator

**User Story:**
As a developer,
I want the Orchestrator to execute phase transitions when the Moderator signals
user confirmation,
so that the system advances from Exploration to Structuring (and later phases)
at the right moment.

**FR/NFR Traceability:** FR-D-08 (Systemphasen-Sequenz), FR-D-09 (Phasenwechsel-
Protokoll), FR-D-04 (Kontextübergabe), SDD 6.1.2 (Phasenwechsel), SDD 6.1.1
(Phasendefinitionen).

**Acceptance Criteria:**

1. New file `backend/core/phase_transition.py` with:
   - `PHASE_ORDER`: ordered list of phases (exploration → strukturierung →
     spezifikation → validierung)
   - `PHASE_TO_MODE`: mapping from phase to primary mode name
   - `next_phase(current)`: returns the next phase or None if at end
   - `advance_phase(project, wm)`: advances to next phase, updates WM and project
2. Moderator output can include a special flag `advance_phase` to signal that the
   user confirmed the phase transition.
3. Orchestrator processes `advance_phase` flag:
   - Calls `advance_phase()` from phase_transition.py
   - Sets `aktiver_modus` to the primary mode of the new phase
   - Sets `aktive_phase` to the new phase
   - Logs the transition
4. Orchestrator processes Moderator's `return_to_mode` flag:
   - Restores `aktiver_modus` to `vorheriger_modus`
   - Resets `phase_complete` flag
   - FR-D-09 AC#4: user can request to stay in current mode
5. FR-D-08: Phase sequence is Exploration → Strukturierung → Spezifikation → Validierung.
6. FR-D-09: No phase transition without Moderator involvement + user confirmation.
7. Tests in `backend/tests/test_phase_transition.py`:
   - `test_next_phase_from_exploration` → returns strukturierung
   - `test_next_phase_from_validierung` → returns None (end)
   - `test_advance_phase_updates_wm_and_project`
   - `test_phase_order_matches_sdd` — all 4 phases in correct order
8. Tests in `backend/tests/test_orchestrator.py` (extended):
   - `test_advance_phase_flag_triggers_transition`
   - `test_return_to_mode_flag_restores_previous_mode`

**Definition of Done:**

- [x] `backend/core/phase_transition.py` exists
- [x] `PHASE_ORDER`, `PHASE_TO_MODE`, `next_phase`, `advance_phase` implemented
- [x] Orchestrator handles `advance_phase` flag from Moderator
- [x] Orchestrator handles `return_to_mode` flag from Moderator
- [x] Phase sequence matches SDD 6.1.1
- [x] Tests in `test_phase_transition.py` (4+ tests)
- [x] Extended tests in `test_orchestrator.py` (2+ tests)
- [x] `ruff check .` passes (exit 0)
- [x] `ruff format --check .` passes (exit 0)
- [x] `python -m mypy . --explicit-package-bases` passes (exit 0)
- [x] `pytest --tb=short -q` passes (exit 0, no regressions)

---

### Story 07-03: Panic Button WebSocket Integration

**User Story:**
As a user,
I want the panic button to immediately activate the Moderator so I can get help
when the conversation is stuck,
so that I always have a way to escalate issues.

**FR/NFR Traceability:** FR-D-03 (Panik-Button-Eskalation), SDD 2.4 (Panik-Button).

**Acceptance Criteria:**

1. `backend/api/websocket.py` updated: when `type: "panic"` message received,
   instead of the current placeholder:
   - Loads the project and sets `wm.aktiver_modus = "moderator"` + saves
     (the Orchestrator will then route the next turn to the Moderator)
   - Triggers `orchestrator.process_turn()` with a synthetic turn like
     "[Panik-Button aktiviert]"
   - Returns the Moderator's response as normal WebSocket events
   - Note: flags are ephemeral per SDD 6.4.1 — the `escalate` intent is
     communicated by switching to Moderator mode, not by persisting a flag
2. Frontend `api/websocket.ts` already sends `{"type": "panic"}` — no frontend
   changes needed.
3. The Moderator receives the escalation context and responds appropriately
   (handled by Story 07-01's system prompt).
4. FR-D-03 AC#4: The `escalate` flag is visible in the debug panel.
5. Tests in `backend/tests/test_websocket.py` (extended):
   - `test_websocket_panic_triggers_moderator` — panic sends a turn that activates
     the Moderator, receives chat_done event with Moderator response

**Definition of Done:**

- [x] WebSocket panic handler triggers real Orchestrator turn with escalate flag
- [x] Moderator responds to escalation (not a placeholder anymore)
- [x] `escalate` flag visible in debug_update event
- [x] Test in `test_websocket.py` for panic→Moderator flow
- [x] `ruff check .` passes (exit 0)
- [x] `ruff format --check .` passes (exit 0)
- [x] `python -m mypy . --explicit-package-bases` passes (exit 0)
- [x] `pytest --tb=short -q` passes (exit 0, no regressions)

---

### Story 07-04: Debug Endpoint for Manual Phase Advance

**User Story:**
As a developer/QA,
I want a debug REST endpoint to manually advance the project phase,
so that I can test phase transitions without going through the full exploration dialog.

**FR/NFR Traceability:** Epic 07 Testable Increment (debug endpoint for QA).

**Acceptance Criteria:**

1. `POST /api/projects/{projekt_id}/debug/advance-phase` endpoint added to
   `backend/api/router.py`.
2. Endpoint calls `advance_phase()` from `phase_transition.py`.
3. Returns updated `ProjectResponse` with the new phase.
4. Returns 400 if already at the last phase (validierung).
5. Returns 404 if project not found.
6. Pydantic schema `AdvancePhaseResponse` added to `backend/api/schemas.py`.
7. OpenAPI contract updated: `api-contract/openapi.json` regenerated.
8. Frontend types regenerated: `frontend/src/generated/api.d.ts`.
9. Tests in `backend/tests/test_api.py`:
   - `test_debug_advance_phase` — advances from exploration to strukturierung
   - `test_debug_advance_phase_at_end` — returns 400 at validierung
   - `test_debug_advance_phase_not_found` — 404

**Definition of Done:**

- [x] `POST /api/projects/{id}/debug/advance-phase` endpoint exists
- [x] Uses `advance_phase()` from phase_transition.py
- [x] Returns updated ProjectResponse
- [x] 400 at last phase, 404 for missing project
- [x] `AdvancePhaseResponse` schema in schemas.py
- [x] `api-contract/openapi.json` updated
- [x] `frontend/src/generated/api.d.ts` regenerated
- [x] Tests in `test_api.py` (3 tests)
- [x] `ruff check .` passes (exit 0)
- [x] `ruff format --check .` passes (exit 0)
- [x] `python -m mypy . --explicit-package-bases` passes (exit 0)
- [x] `pytest --tb=short -q` passes (exit 0, no regressions)
- [x] `npm run typecheck` passes in frontend (exit 0)

---

### Story 07-05: Integration Test — Full Phase Transition Cycle

**User Story:**
As a developer,
I want an integration test that exercises the complete phase transition flow
(ExplorationMode → Moderator → phase advance → StructuringMode),
so that I can verify the entire lifecycle works end-to-end.

**FR/NFR Traceability:** FR-D-08 (Systemphasen-Sequenz), FR-D-09 (Phasenwechsel-Protokoll).

**Acceptance Criteria:**

1. Integration test in `backend/tests/test_orchestrator.py` (extended):
   - Sets up a project with exploration artifacts
   - ExplorationMode returns `phase_complete` flag
   - Orchestrator activates Moderator
   - Moderator (mocked) returns `advance_phase` flag
   - Orchestrator transitions to `strukturierung` phase
   - Next turn goes to StructuringMode (stub)
   - Verifies: phase changed, mode changed, WM updated, persisted
2. Test for panic button flow:
   - ExplorationMode is active
   - User triggers panic (escalate flag set externally)
   - Moderator is activated
   - Moderator returns `return_to_mode` flag
   - Previous mode (exploration) is restored
3. All tests use in-memory SQLite and mocked LLM.

**Definition of Done:**

- [x] Integration test for full phase transition cycle
- [x] Integration test for panic→Moderator→return flow
- [x] All tests use mocked LLM + in-memory SQLite
- [x] `ruff check .` passes (exit 0)
- [x] `ruff format --check .` passes (exit 0)
- [x] `python -m mypy . --explicit-package-bases` passes (exit 0)
- [x] `pytest --tb=short -q` passes (exit 0, no regressions)

---

### Implementation Order

Stories must be implemented in this order:

1. **07-01** (Moderator LLM) — foundation: replaces stub with real mode
2. **07-02** (Phase transition logic) — depends on 07-01 for Moderator flags
3. **07-03** (Panic button wiring) — depends on 07-01 for real Moderator
4. **07-04** (Debug endpoint) — depends on 07-02 for advance_phase()
5. **07-05** (Integration tests) — depends on all prior stories
