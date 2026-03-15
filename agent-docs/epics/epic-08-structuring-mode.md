# Epic 08 – Structuring Mode

## Summary

Implement `StructuringMode`, the cognitive mode responsible for transforming the free-text
Exploration Artifact into a structured, BPMN-like process definition stored in the
Structure Artifact. The mode drives a dialogue that clarifies sequence, decision points,
roles, and sub-processes, and emits JSON Patch operations to incrementally build the
Structure Artifact.

Additionally, add project deletion capabilities (single and bulk) to the UI and backend,
so users can manage their project list by removing projects they no longer need.

This epic corresponds to **Implementation Step 8** in `AGENTS.md` / `hla_architecture.md`.

## Goal

After the Exploration phase completes and the Moderator triggers a phase transition, the
user enters a structured dialogue in the Structuring phase and the Structure Artifact is
progressively populated with process steps, flows, roles, and decision points – all visible
in real time in the artifact pane.

## Testable Increment

- In the browser: starting from a completed Exploration phase (can be seeded with test
  data), the user sees the Structuring phase dialogue begin; after a few turns the
  Structure Artifact pane shows at least:
  - A list of process steps
  - At least one decision point or flow connection
- `pytest backend/tests/test_structuring_mode.py` → a mocked multi-turn structuring
  dialogue produces a non-empty, schema-valid Structure Artifact
- Project deletion: each project card has a delete button; clicking it opens a
  confirmation dialog; after confirming, the project is removed from list and DB
- Multi-select: checkboxes on cards enable bulk selection; a toolbar allows deleting
  all selected projects at once
- `DELETE /api/projects/{id}` returns 204; `DELETE /api/projects/batch` removes multiple
- `pytest backend/tests/test_project_deletion.py` → all deletion tests pass

## Dependencies

- Epic 07 (Moderator must be able to trigger the transition into Structuring)

## Key Deliverables

- `backend/modes/structuring.py` – `StructuringMode` (real LLM calls, Tool Use output)
- Structure Artifact schema finalised in `backend/artifacts/models.py` (steps, flows, roles,
  decision points as dict-keyed slots)
- `backend/core/context_assembler.py` updated – Structuring-phase context window
- `frontend/src/components/ArtifactPane.tsx` updated – renders Structure Artifact fields
  (steps, flows, decision points) in a readable format
- `backend/tests/test_structuring_mode.py` – multi-turn structuring tests
- `backend/persistence/project_repository.py` – `delete(projekt_id)` and `delete_many(projekt_ids)` methods
- `backend/api/router.py` – `DELETE /api/projects/{id}` and `DELETE /api/projects/batch` endpoints
- `backend/api/schemas.py` – `ProjectDeleteBatchRequest` and response schemas
- `frontend/src/App.tsx` – delete button per card, multi-select checkboxes, bulk-delete toolbar
- `frontend/src/components/ConfirmDialog.tsx` – reusable confirmation dialog
- `frontend/src/store/session.ts` – delete actions and API helpers
- `backend/tests/test_project_deletion.py` – deletion tests

## OpenAPI Contract Note

This epic finalises the Structure Artifact schema in `backend/core/models.py` and adds
two new DELETE endpoints for project deletion:

- `DELETE /api/projects/{projekt_id}` – delete single project
- `DELETE /api/projects/batch` – delete multiple projects

All new endpoints must have explicit Pydantic response schemas in `backend/api/schemas.py`.

After implementation:

1. Regenerate the OpenAPI snapshot: `curl http://localhost:8000/openapi.json > api-contract/openapi.json`
2. Regenerate frontend types: `cd frontend && npm run generate-api:file`
3. Commit both `api-contract/openapi.json` and `frontend/src/generated/api.d.ts`
4. Verify `tsc --noEmit` passes

The `ArtifactPane.tsx` update that renders Structure Artifact fields must use the generated
types for all artifact-related data — do not introduce local TypeScript interfaces that
duplicate fields from the generated spec.

## Stories

---

### Story 08-01: Structure Artifact Schema — Add `prozesszusammenfassung` Field

**User story:**
As a developer
I want the StructureArtifact to include a `prozesszusammenfassung` field per SDD 5.4
So that the Structuring Mode can populate it and the artifact matches the SDD specification.

**Acceptance Criteria:**

- `backend/artifacts/models.py`: `StructureArtifact` gains a field `prozesszusammenfassung: str = ""` (SDD 5.4: "Freitext, für Fachanwender lesbar, LLM-generiert")
- `backend/artifacts/template_schema.py`: `STRUCTURE_TEMPLATE` gains a path pattern `/prozesszusammenfassung` with allowed ops `["replace"]`
- `backend/artifacts/completeness.py`: if the completeness calculator references structure artifact slots, `prozesszusammenfassung` is included in the count
- `backend/core/context_assembler.py`: `prompt_context_summary()` includes `prozesszusammenfassung` status in its output (empty/filled)
- Existing tests continue to pass — the new field has a default so no existing code breaks
- One test in `backend/tests/test_artifacts.py` verifies `StructureArtifact` serialization round-trip includes `prozesszusammenfassung`
- One test in `backend/tests/test_artifacts.py` verifies `STRUCTURE_TEMPLATE.is_valid_patch("replace", "/prozesszusammenfassung")` returns True
- One test verifies `is_valid_patch("add", "/prozesszusammenfassung")` returns False (only replace allowed)

**Definition of Done:**

- [x] `backend/artifacts/models.py` — `StructureArtifact` has `prozesszusammenfassung: str = ""`
- [x] `backend/artifacts/template_schema.py` — `/prozesszusammenfassung` path pattern added
- [x] `backend/artifacts/completeness.py` — no update needed (counts schritte only, prozesszusammenfassung is a top-level field)
- [x] `backend/core/context_assembler.py` — `prompt_context_summary()` includes prozesszusammenfassung
- [x] `backend/tests/test_models.py` — 3 new tests (round-trip, valid patch, invalid patch)
- [x] `ruff check backend/` passes
- [x] `ruff format --check backend/` passes
- [x] `python -m mypy backend/ --explicit-package-bases` passes (no new errors)
- [x] `pytest backend/ --tb=short -q` passes — 280 passed

---

### Story 08-02: StructuringMode LLM Implementation + System Prompt

**User story:**
As a developer
I want the StructuringMode stub to be replaced with a real LLM-based implementation
So that the Structuring phase can conduct a dialog to decompose the process into Strukturschritte.

**Acceptance Criteria:**

- `backend/modes/structuring.py`: `StructuringMode` accepts an `LLMClient` in its constructor (same pattern as `ExplorationMode`)
- `StructuringMode.call(context)` builds a system prompt from `backend/prompts/structuring.md`, injects context summary, current structure artifact state, and exploration artifact as read-only context
- LLM is called with `tools=[APPLY_PATCHES_TOOL]` and `tool_choice={"type": "tool", "name": "apply_patches"}` (SDD 6.5.2)
- The mode translates dialog history into Anthropic message format (reuse `_translate_dialog_history` pattern from exploration)
- Patches target the structure artifact paths: `/schritte/{id}` (add), `/schritte/{id}/beschreibung` (replace), etc. per template schema
- Phase status is computed based on structure artifact completeness:
  - `in_progress` if any Pflichtfelder are `leer`
  - `nearing_completion` if all have content but not all `nutzervalidiert`
  - `phase_complete` if all `vollstaendig` or `nutzervalidiert`
- When `phase_complete`, flag `Flag.phase_complete` is emitted
- If no LLM client is configured, returns a stub response (same pattern as ExplorationMode)
- `backend/prompts/structuring.md` exists with a German system prompt that:
  - Describes the Structuring role (SDD 6.6.2)
  - Lists all Strukturschritt fields from SDD 5.4
  - Instructs the LLM to decompose the process from the Exploration Artifact
  - Instructs the LLM to ask clarifying questions about sequence, decisions, loops, exceptions
  - Contains `{context_summary}` and `{slot_status}` placeholders
  - Enforces Output-Kontrakt (SDD 6.5.2)
  - Instructs the LLM not to overwrite existing Strukturschritte without asking (SDD 6.6.2: "bestehende Slots werden nicht ohne Rückfrage ersetzt")
  - References FR-A-04 (exceptions), FR-A-08 (German language)
- The mode passes the current structure artifact as read-only context alongside the exploration artifact (SDD 6.6.2 Input)

**Definition of Done:**

- [ ] `backend/modes/structuring.py` — full LLM implementation (no stub response when LLM client present)
- [ ] `backend/prompts/structuring.md` exists
- [ ] `backend/prompts/structuring.md` — German system prompt with Strukturierungsmodus role description
- [ ] System prompt contains `{context_summary}` and `{slot_status}` placeholders
- [ ] System prompt instructs LLM not to overwrite existing slots without asking
- [ ] LLM called with `tool_choice: apply_patches`
- [ ] Phase status computed from structure artifact completeness
- [ ] `Flag.phase_complete` emitted when phase is complete
- [ ] Stub fallback when no LLM client
- [ ] `ruff check backend/` passes
- [ ] `ruff format --check backend/` passes
- [ ] `python -m mypy backend/ --explicit-package-bases` passes
- [ ] `pytest backend/ --tb=short -q` passes with 0 failures

---

### Story 08-03: StructuringMode Tests — Multi-Turn Mocked Dialog

**User story:**
As a developer
I want comprehensive tests for StructuringMode with mocked LLM responses
So that I can verify the mode correctly populates the Structure Artifact across multiple turns.

**Acceptance Criteria:**

- `backend/tests/test_structuring_mode.py` exists with the following tests:
  - **test_structuring_stub_without_llm**: Without LLM client, returns stub message, empty patches, `in_progress`
  - **test_structuring_single_turn_adds_schritt**: Mock LLM returns a single `add` patch for `/schritte/s1`, verify ModeOutput contains the patch with all Pflichtfelder
  - **test_structuring_multi_turn_builds_artifact**: Simulate 3 turns — turn 1 adds 2 steps, turn 2 adds a decision point, turn 3 adds connections. Verify final patches contain steps with correct types
  - **test_structuring_decision_has_bedingung**: When LLM adds a step with `typ=entscheidung`, verify `bedingung` is present in the patch value
  - **test_structuring_phase_complete_when_all_validated**: When all Strukturschritte have `completeness_status=nutzervalidiert`, mode returns `phase_complete` status and `Flag.phase_complete`
  - **test_structuring_in_progress_when_slots_empty**: When structure artifact has no schritte, returns `in_progress`
  - **test_structuring_exploration_artifact_in_context**: Verify the system prompt passed to LLM contains exploration artifact content (read-only reference)
  - **test_structuring_prozesszusammenfassung_patch**: LLM can emit a `replace` patch on `/prozesszusammenfassung` (the top-level summary field)
  - **test_structuring_error_on_llm_failure**: When LLM client raises an error, the mode propagates it (no silent swallowing). Verify error message is non-empty (Rule T-6).
- All tests use mock LLM responses (no real API calls)
- Both positive and negative path coverage

**Definition of Done:**

- [ ] `backend/tests/test_structuring_mode.py` exists
- [ ] At least 9 test functions covering the scenarios above (including error propagation)
- [ ] All tests use mocked LLM client
- [ ] Tests verify patches, phasenstatus, and flags
- [ ] `ruff check backend/` passes
- [ ] `ruff format --check backend/` passes
- [ ] `python -m mypy backend/ --explicit-package-bases` passes
- [ ] `pytest backend/tests/test_structuring_mode.py --tb=short -q` passes with 0 failures

---

### Story 08-04: Project Deletion — Backend (Repository + API Endpoints)

**User story:**
As a developer
I want DELETE endpoints for single and bulk project deletion
So that users can remove projects they no longer need.

**Acceptance Criteria:**

- `backend/persistence/project_repository.py`:
  - `delete(projekt_id: str) -> bool` — deletes project and all related data (artifacts, versions, dialog history, working memory). Returns True if found and deleted, False if not found. Uses a single atomic transaction.
  - `delete_many(projekt_ids: list[str]) -> int` — deletes multiple projects atomically. Returns count of actually deleted projects.
- `backend/api/schemas.py`:
  - `ProjectDeleteBatchRequest` with field `projekt_ids: list[str]` (min 1 item)
  - `ProjectDeleteBatchResponse` with field `deleted_count: int`
- `backend/api/router.py`:
  - `DELETE /api/projects/{projekt_id}` — returns 204 No Content on success, 404 if not found
  - `DELETE /api/projects/batch` — accepts `ProjectDeleteBatchRequest`, returns `ProjectDeleteBatchResponse`
- Both endpoints log deletion via structlog
- FR-E-06: Deletion of one project does not affect other projects

**Definition of Done:**

- [ ] `backend/persistence/project_repository.py` — `delete()` and `delete_many()` methods exist
- [ ] `backend/api/schemas.py` — `ProjectDeleteBatchRequest` and `ProjectDeleteBatchResponse` exist
- [ ] `backend/api/router.py` — `DELETE /api/projects/{projekt_id}` endpoint returns 204/404
- [ ] `backend/api/router.py` — `DELETE /api/projects/batch` endpoint returns `ProjectDeleteBatchResponse`
- [ ] Deletion is atomic (single transaction)
- [ ] `ruff check backend/` passes
- [ ] `ruff format --check backend/` passes
- [ ] `python -m mypy backend/ --explicit-package-bases` passes
- [ ] `pytest backend/ --tb=short -q` passes with 0 failures

---

### Story 08-05: Project Deletion — Backend Tests

**User story:**
As a developer
I want tests for project deletion (single and bulk)
So that deletion logic and API endpoints are verified.

**Acceptance Criteria:**

- `backend/tests/test_project_deletion.py` exists with:
  - **test_delete_existing_project**: Create project, delete it, verify 204 and project gone from list
  - **test_delete_nonexistent_project**: DELETE with random UUID returns 404
  - **test_delete_removes_all_data**: After deletion, loading project raises/returns None; dialog history is gone; artifact versions are gone
  - **test_delete_does_not_affect_other_projects**: Create 2 projects, delete 1, verify the other is intact (FR-E-06)
  - **test_batch_delete_multiple**: Create 3 projects, batch-delete 2, verify 2 deleted and 1 remains
  - **test_batch_delete_partial_ids**: Batch with mix of existing and non-existing IDs — deletes what exists, returns correct count
  - **test_batch_delete_empty_list_rejected**: Empty `projekt_ids` list returns 422 (Pydantic validation)
  - **test_delete_atomicity**: If deletion of one project in a batch fails mid-transaction, none are deleted (or graceful handling)

**Definition of Done:**

- [ ] `backend/tests/test_project_deletion.py` exists
- [ ] At least 7 test functions covering scenarios above
- [ ] Tests use real SQLite (`:memory:`) — not mocks
- [ ] Both happy-path and negative tests included
- [ ] `ruff check backend/` passes
- [ ] `ruff format --check backend/` passes
- [ ] `python -m mypy backend/ --explicit-package-bases` passes
- [ ] `pytest backend/tests/test_project_deletion.py --tb=short -q` passes with 0 failures

---

### Story 08-06: Frontend — Structure Artifact Rendering in ArtifactPane

**User story:**
As a developer
I want the ArtifactPane to render Structure Artifact fields in a readable, structured format
So that users can see process steps, decision points, and flow connections in real time.

**Acceptance Criteria:**

- `frontend/src/components/ArtifactTab.tsx` updated:
  - For `type === "struktur"`: renders each Strukturschritt with:
    - `titel` as header
    - `typ` shown as a badge/label (aktion/entscheidung/schleife/ausnahme) with distinct styling per type
    - `beschreibung` as body text
    - `reihenfolge` shown as step number
    - `nachfolger` shown as arrows/links to successor step IDs
    - `bedingung` shown when present (decision steps)
    - `completeness_status` and `algorithmus_status` as status badges
    - `spannungsfeld` shown as a warning note when present
  - Steps are sorted by `reihenfolge`
  - `prozesszusammenfassung` (top-level field) rendered above the step list as a summary block
- FR-F-05: Invalidated steps (`algorithmus_status === "invalidiert"`) have distinct visual styling
- Uses generated types from `frontend/src/generated/api.d.ts` — no duplicate local interfaces for artifact fields

**Definition of Done:**

- [ ] `frontend/src/components/ArtifactTab.tsx` renders Strukturschritt fields
- [ ] Steps sorted by `reihenfolge`
- [ ] Type badge per step (aktion/entscheidung/schleife/ausnahme)
- [ ] `prozesszusammenfassung` rendered above step list
- [ ] `spannungsfeld` shown as warning when present
- [ ] Invalidated steps visually distinct (FR-F-05)
- [ ] `npm run lint` passes
- [ ] `npm run format:check` passes
- [ ] `npm run typecheck` passes

---

### Story 08-07: Frontend — Project Deletion UI (Single + Bulk)

**User story:**
As a developer
I want each project card to have a delete button and a multi-select mode for bulk deletion
So that users can manage their project list by removing unwanted projects.

**Acceptance Criteria:**

- `frontend/src/components/ConfirmDialog.tsx`: Reusable confirmation dialog component:
  - Props: `open: boolean`, `title: string`, `message: string`, `onConfirm: () => void`, `onCancel: () => void`
  - Renders a modal overlay with title, message, confirm button ("Löschen"), cancel button ("Abbrechen")
  - Confirm button has destructive styling (red)
- `frontend/src/App.tsx` — `ProjectSelection` component updated:
  - Each project card has a delete button (trash icon or "Löschen" text)
  - Clicking delete opens `ConfirmDialog` — after confirm, calls `DELETE /api/projects/{id}`
  - Each project card has a checkbox for multi-select
  - When ≥1 checkbox selected, a toolbar appears with "Ausgewählte löschen ({n})" button
  - Clicking bulk delete opens `ConfirmDialog` — after confirm, calls `DELETE /api/projects/batch`
  - After successful deletion, project list is refreshed
- `frontend/src/store/session.ts`:
  - `deleteProject(dispatch, projektId)` action — calls DELETE endpoint, dispatches list refresh
  - `deleteProjects(dispatch, projektIds)` action — calls batch DELETE endpoint, dispatches list refresh

**Definition of Done:**

- [ ] `frontend/src/components/ConfirmDialog.tsx` exists and is a reusable modal
- [ ] `frontend/src/App.tsx` — delete button per project card
- [ ] `frontend/src/App.tsx` — multi-select checkboxes on project cards
- [ ] `frontend/src/App.tsx` — bulk delete toolbar appears when items selected
- [ ] `frontend/src/store/session.ts` — `deleteProject()` and `deleteProjects()` actions exist
- [ ] Confirmation dialog shown before any deletion
- [ ] Project list refreshed after deletion
- [ ] `npm run lint` passes
- [ ] `npm run format:check` passes
- [ ] `npm run typecheck` passes

---

### Story 08-08: OpenAPI Contract Regeneration + Integration Verification

**User story:**
As a developer
I want the OpenAPI contract and generated types updated to reflect the new deletion endpoints and updated Structure Artifact schema
So that frontend and backend stay in sync per ADR-001.

**Acceptance Criteria:**

- `api-contract/openapi.json` regenerated from running backend — includes:
  - `DELETE /api/projects/{projekt_id}` with 204 response
  - `DELETE /api/projects/batch` with `ProjectDeleteBatchRequest`/`ProjectDeleteBatchResponse`
  - Updated `StructureArtifact` schema with `prozesszusammenfassung` field
- `frontend/src/generated/api.d.ts` regenerated via `npm run generate-api:file`
- Both files committed together in the same commit (ADR-001 co-update rule)
- `npm run typecheck` passes — verifying frontend code compiles against new types

**Definition of Done:**

- [ ] `api-contract/openapi.json` updated with new endpoints and schema
- [ ] `frontend/src/generated/api.d.ts` regenerated
- [ ] Both files committed together
- [ ] `npm run typecheck` passes
- [ ] Backend DoD passes: `ruff check`, `ruff format --check`, `mypy`, `pytest`
- [ ] Frontend DoD passes: `npm run lint`, `npm run format:check`, `npm run typecheck`
