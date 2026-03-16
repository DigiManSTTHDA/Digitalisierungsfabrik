# Epic 10 – Validation Mode & Correction Loop

## Summary

Implement `ValidationMode` and the correction loop it can trigger. After all three
artifacts are populated, the Moderator transitions to the Validation phase. The system
reviews the artifacts for internal consistency and completeness, presents findings to the
user, and – if issues are found – re-enters the relevant earlier mode to correct them
before returning to validation.

This epic corresponds to **Implementation Step 10** in `AGENTS.md` / `hla_architecture.md`.

## Goal

The system autonomously validates the full artifact set, surfaces any gaps or
inconsistencies in plain German, and guides the user through corrections. The correction
loop can cycle back to Exploration, Structuring, or Specification as needed and then
re-validate until all artifacts pass.

## Testable Increment

- In the browser:
  - Starting from a set of complete but deliberately flawed artifacts (seeded test data),
    the Validation phase surfaces at least one issue to the user
  - The user responds, the system enters the correction sub-loop, patches the relevant
    artifact, and re-validates
  - When all artifacts pass validation, a success message is shown
- `pytest backend/tests/test_validation_mode.py` → correction loop iterates correctly;
  clean artifacts pass in a single turn; flawed artifacts trigger at least one loop
- Open point OP-20 (retry strategy for repeated output violations) resolved via ADR

## Dependencies

- Epic 09 (all three artifact types must be producible end-to-end)

## Key Deliverables

- `backend/modes/validation_mode.py` – `ValidationMode` with completeness + consistency
  checks
- `backend/core/orchestrator.py` updated – correction loop routing logic
- `backend/core/phase_transition.py` updated – `VALIDATION_PASSED` terminal state
- `frontend/src/components/ArtifactPane.tsx` updated – highlights validated / flagged
  fields
- `frontend/src/components/ChatPane.tsx` updated – renders validation summary messages
  clearly
- `backend/tests/test_validation_mode.py` – validation pass/fail and correction-loop tests
- ADR resolving OP-20 committed to `agent-docs/decisions/`

## OpenAPI Contract Note

This epic introduces validation report data flowing to the frontend (via WebSocket events
and potentially a REST endpoint). Ensure:

- Any validation report structure is a Pydantic model in `backend/api/schemas.py` (not a
  raw `dict`), so it appears correctly in the OpenAPI spec.
- If a new REST endpoint is added to retrieve the validation report (e.g.
  `GET /api/projects/{id}/validation`), update the spec and regenerate types.

After any API change:

1. Regenerate the OpenAPI snapshot: `curl http://localhost:8000/openapi.json > api-contract/openapi.json`
2. Regenerate frontend types: `cd frontend && npm run generate-api:file`
3. Commit both `api-contract/openapi.json` and `frontend/src/generated/api.d.ts`
4. Verify `tsc --noEmit` passes

Frontend updates in this epic (`ArtifactPane.tsx` highlighting, `ChatPane.tsx` validation
summary) must use generated types for all validation-related data structures.

## Stories

### Story 10-01: ADR-007 for OP-20 + Validation Report Data Model

**User Story:**
As a developer,
I want to resolve OP-20 (repeated output contract violations) via an ADR and define
the validation report data model as a Pydantic schema,
so that the validation mode has a well-defined output structure and retry behavior.

**Acceptance Criteria:**

1. ADR-007 written and accepted in `agent-docs/decisions/ADR-007-validation-report-retry.md`:
   - Resolves OP-20: For the prototype, output violations return an error message + user retry option.
     No automatic retry. Configurable retry limit deferred to post-prototype.
   - Defines that the validation report is stored in `WorkingMemory.validierungsbericht`
     as a structured Pydantic model (not a raw dict), persisted with the project,
     and passed to the moderator as context.
2. `backend/artifacts/models.py` updated with new models:
   - `Schweregrad` StrEnum: `kritisch`, `warnung`, `hinweis` (SDD 6.6.4 Schweregradskala)
   - `Validierungsbefund` Pydantic model with fields:
     - `befund_id: str` — unique identifier
     - `schweregrad: Schweregrad` — severity classification (FR-C-08 AK(1))
     - `beschreibung: str` — human-readable German description of the finding
     - `betroffene_slots: list[str]` — list of affected slot IDs (FR-C-01 AK)
     - `artefakttyp: str` — "exploration" | "struktur" | "algorithmus"
     - `empfehlung: str` — recommended action in German
   - `Validierungsbericht` Pydantic model with fields:
     - `befunde: list[Validierungsbefund]` — all findings
     - `erstellt_am: datetime` — creation timestamp
     - `durchlauf_nr: int` — which validation pass (1-based, for correction loop tracking)
     - `ist_bestanden: bool` — True if no `kritisch` findings remain
3. `backend/core/working_memory.py` updated:
   - New field `validierungsbericht: Validierungsbericht | None = None` added to `WorkingMemory`
4. `backend/api/schemas.py` updated:
   - `ValidationReportResponse` schema added with the same structure for the API
5. `agent-docs/open-points/open-points.md` updated: OP-20 status changed to `resolved`

**Definition of Done:**

- [ ] `agent-docs/decisions/ADR-007-validation-report-retry.md` exists with status `accepted`
- [ ] `Schweregrad` StrEnum with 3 values in `backend/artifacts/models.py`
- [ ] `Validierungsbefund` model with all 6 fields in `backend/artifacts/models.py`
- [ ] `Validierungsbericht` model with all 4 fields in `backend/artifacts/models.py`
- [ ] `WorkingMemory.validierungsbericht` field exists
- [ ] `ValidationReportResponse` in `backend/api/schemas.py`
- [ ] OP-20 marked resolved in `agent-docs/open-points/open-points.md`
- [ ] `ruff check .` passes
- [ ] `ruff format --check .` passes
- [ ] `python -m mypy . --explicit-package-bases` passes
- [ ] `pytest --tb=short -q` passes with 0 failures

---

### Story 10-02: Validation Report Schema Tests

**User Story:**
As a developer,
I want thorough tests for the validation report data model,
so that serialization, persistence round-trips, and severity classification work correctly.

**Acceptance Criteria:**

1. `backend/tests/test_validation_mode.py` created with tests for:
   - `Schweregrad` enum: all 3 values exist and are strings
   - `Validierungsbefund` construction with all fields
   - `Validierungsbefund` rejects empty `beschreibung`
   - `Validierungsbericht.ist_bestanden` is `True` when no `kritisch` findings
   - `Validierungsbericht.ist_bestanden` is `False` when any `kritisch` finding present
   - Persistence round-trip: project with `validierungsbericht` in working memory survives
     save/load cycle with all fields intact
   - `Validierungsbericht` with empty `befunde` list → `ist_bestanden` is True
   - `durchlauf_nr` increments correctly across validation passes

**Definition of Done:**

- [ ] `backend/tests/test_validation_mode.py` exists with ≥8 tests
- [ ] All tests cover both positive and negative cases (Rule T-2)
- [ ] Persistence round-trip tests assert on reloaded data, not in-memory data (Rule T-3)
- [ ] `ruff check .` passes
- [ ] `ruff format --check .` passes
- [ ] `python -m mypy . --explicit-package-bases` passes
- [ ] `pytest --tb=short -q` passes with 0 failures

---

### Story 10-03: ValidationMode LLM Implementation + System Prompt

**User Story:**
As a developer,
I want to replace the ValidationMode stub with a full LLM-based implementation
that checks artifact consistency, completeness, and EMMA compatibility,
so that the system produces a structured validation report (SDD 6.6.4).

**Acceptance Criteria:**

1. `backend/modes/validation.py` updated — stub replaced with full LLM implementation:
   - Receives all three artifacts via `ModeContext` (read-only)
   - Uses the LLM via `self._llm.complete()` with Tool Use to produce structured findings
   - Tool schema: `produce_validation_report` with parameters matching `Validierungsbericht`
   - Checks performed (SDD 6.6.4):
     - Referenzielle Integrität: every `Strukturschritt.algorithmus_ref` points to existing
       `Algorithmusabschnitt`; every `Algorithmusabschnitt.struktur_ref` points to existing
       `Strukturschritt` (FR-C-01, FR-B-03)
     - EMMA-Kompatibilität: all `EmmaAktion.aktionstyp` values are valid `EmmaAktionstyp`
       members (FR-C-03)
     - Completeness: no mandatory slots have status `leer` or `teilweise` (SDD 5.6)
     - Consistency: no contradictions within artifact fields
   - Returns `ModeOutput` with:
     - `nutzeraeusserung`: formatted German summary of the validation report
     - `patches`: empty list (validation mode has NO write operations — SDD 6.6.4)
     - `phasenstatus`: `phase_complete` (always — validation runs once then hands off)
     - `flags`: `[Flag.phase_complete]`
   - Stores the `Validierungsbericht` in the mode output (via a mechanism accessible
     to the orchestrator — see Story 10-04)
2. `backend/prompts/validation.md` created — German system prompt:
   - Describes the validation task in German
   - Lists all check categories (integrity, EMMA, completeness, consistency)
   - Instructs the LLM to classify each finding by `Schweregrad`
   - Instructs that no artifact modifications are allowed
   - Provides the EMMA action catalog as reference
3. `ValidationMode.__init__` accepts `llm: LLMClient` parameter (same pattern as other modes)

**Definition of Done:**

- [ ] `backend/modes/validation.py` contains full LLM-based `ValidationMode`
- [ ] `backend/prompts/validation.md` exists with German system prompt
- [ ] Validation mode produces `Validierungsbericht` with `Schweregrad`-classified findings
- [ ] Validation mode emits NO patches (SDD 6.6.4: keine Schreibrechte)
- [ ] Validation mode always sets `phase_complete` flag
- [ ] LLM tool schema `produce_validation_report` defined
- [ ] `ruff check .` passes
- [ ] `ruff format --check .` passes
- [ ] `python -m mypy . --explicit-package-bases` passes
- [ ] `pytest --tb=short -q` passes with 0 failures

---

### Story 10-04: Orchestrator Correction Loop + Validation Report Persistence

**User Story:**
As a developer,
I want the Orchestrator to support the validation-correction loop (SDD 6.1.3),
persisting the validation report and routing between validation ↔ specification
via the moderator,
so that the user can iteratively fix issues found by validation.

**Acceptance Criteria:**

1. `backend/core/orchestrator.py` updated:
   - After `ValidationMode` returns, the orchestrator extracts the `Validierungsbericht`
     from the mode output and stores it in `WorkingMemory.validierungsbericht`
   - The moderator receives the validation report as part of its context
   - When moderator signals `return_to_mode` with `vorheriger_modus = "specification"`,
     the specification mode receives the validation report as context for targeted fixes
   - When moderator signals `advance_phase` after validation passes, the project
     transitions to `abgeschlossen` status (FR-G-04)
2. `backend/modes/base.py` updated:
   - `ModeOutput` gets an optional field: `validierungsbericht: Validierungsbericht | None = None`
3. `backend/core/phase_transition.py` updated:
   - Handle terminal state: when `advance_phase` is called in `validierung` phase,
     instead of trying to advance to a non-existent next phase, set
     `project.projektstatus = Projektstatus.abgeschlossen`
4. `backend/persistence/project_repository.py` updated:
   - `validierungsbericht` field in `WorkingMemory` is serialized/deserialized correctly
     (it's a Pydantic model within WM, which is already JSON-serialized — verify round-trip)
5. Correction loop flow (SDD 6.1.3):
   - Validation → `phase_complete` → Moderator presents report → User says "fix" →
     Moderator returns `return_to_mode` → Specification mode with report context →
     Specification `phase_complete` → Validation re-runs → repeat until pass or user accepts

**Definition of Done:**

- [ ] `ModeOutput.validierungsbericht` optional field exists in `backend/modes/base.py`
- [ ] Orchestrator stores validation report in `WorkingMemory` after validation turn
- [ ] `advance_phase` in validierung sets `projektstatus = abgeschlossen` (terminal state)
- [ ] Validation report persists through save/load cycle
- [ ] Correction loop routing logic implemented in orchestrator
- [ ] `ruff check .` passes
- [ ] `ruff format --check .` passes
- [ ] `python -m mypy . --explicit-package-bases` passes
- [ ] `pytest --tb=short -q` passes with 0 failures

---

### Story 10-05: ValidationMode Tests — Mocked LLM + Correction Loop

**User Story:**
As a developer,
I want comprehensive tests for the ValidationMode and correction loop,
so that validation behavior is verified for clean artifacts, flawed artifacts,
and the iterative correction cycle.

**Acceptance Criteria:**

1. `backend/tests/test_validation_mode.py` extended with ≥12 additional tests:
   - **Clean artifacts:** all three artifacts complete → report with 0 `kritisch` findings,
     `ist_bestanden = True`
   - **Missing referential integrity:** `Strukturschritt.algorithmus_ref` points to
     non-existent `Algorithmusabschnitt` → `kritisch` finding with correct `betroffene_slots`
   - **Invalid EMMA action type:** `EmmaAktion.aktionstyp` is an invalid string →
     `kritisch` finding
   - **Incomplete slots:** slots with `completeness_status = leer` → `warnung` or `kritisch`
     finding
   - **Multiple findings:** flawed artifacts produce multiple findings with correct severities
   - **Severity classification:** each severity level (`kritisch`, `warnung`, `hinweis`)
     appears in at least one test
   - **No patches emitted:** verify `mode_output.patches == []` in all cases
   - **phase_complete flag:** verify `Flag.phase_complete` in all outputs
   - **Correction loop integration:** 2-turn test with mocked orchestrator:
     Turn 1: validation finds issues → moderator activates
     Turn 2: after fix, validation re-runs → report is clean
   - **Error propagation:** LLM error during validation → meaningful error, no state corruption
   - **Empty artifacts:** all artifacts empty → findings for all missing content
   - **durchlauf_nr increment:** second validation pass has `durchlauf_nr = 2`
2. All tests use mocked LLM (no real API calls)
3. Tests use `pytest-asyncio` for async test functions

**Definition of Done:**

- [ ] ≥12 new tests in `backend/tests/test_validation_mode.py`
- [ ] Both positive (clean) and negative (flawed) test cases (Rule T-2)
- [ ] Correction loop tested end-to-end with mocked components
- [ ] All assertions test actual behavior, not tautologies (Rule T-1)
- [ ] `ruff check .` passes
- [ ] `ruff format --check .` passes
- [ ] `python -m mypy . --explicit-package-bases` passes
- [ ] `pytest --tb=short -q` passes with 0 failures

---

### Story 10-06: Frontend — Validation Report Rendering + Artifact Highlighting

**User Story:**
As a developer,
I want the frontend to display validation findings clearly and highlight
flagged slots in the artifact pane,
so that the user can see which parts of the artifacts need attention (FR-C-08 AK(2), FR-F-05).

**Acceptance Criteria:**

1. `frontend/src/components/ChatPane.tsx` updated:
   - Validation report messages (from the moderator after validation) are rendered
     with visual severity indicators:
     - `kritisch`: red badge/icon
     - `warnung`: yellow/orange badge/icon
     - `hinweis`: blue/gray badge/icon
   - Findings are displayed as a structured list, not raw text
2. `frontend/src/components/ArtifactPane.tsx` updated:
   - Slots referenced in `betroffene_slots` of `kritisch` findings are highlighted
     with a red border or background
   - Slots referenced in `warnung` findings are highlighted with a yellow indicator
   - Highlighting updates reactively when validation report changes (FR-F-05 AK(2))
3. `frontend/src/components/ArtifactTab.tsx` updated:
   - Each slot card shows a validation status badge when findings exist for that slot
   - User can click the badge to see the full finding description
4. All new types use generated TypeScript types from `frontend/src/generated/api.d.ts`

**Definition of Done:**

- [ ] Validation findings render with severity-colored badges in `ChatPane.tsx`
- [ ] `ArtifactPane.tsx` highlights flagged slots by severity
- [ ] `ArtifactTab.tsx` shows validation badges on affected slots
- [ ] Generated types used (no hand-written API types)
- [ ] `npm run lint` passes
- [ ] `npm run format:check` passes
- [ ] `npm run typecheck` passes

---

### Story 10-07: OpenAPI Contract Regeneration

**User Story:**
As a developer,
I want the OpenAPI contract and generated TypeScript types updated to include
the validation report schemas,
so that the frontend and backend share a consistent API contract (ADR-001).

**Acceptance Criteria:**

1. `backend/api/schemas.py` has `ValidationReportResponse` and related schemas
   (already added in Story 10-01)
2. If a new REST endpoint is added (e.g. `GET /api/projects/{id}/validation`),
   it is registered in `backend/api/router.py`
3. `api-contract/openapi.json` regenerated from running backend
4. `frontend/src/generated/api.d.ts` regenerated via `npm run generate-api:file`
5. Both files committed together (ADR-001 co-update rule)
6. `npm run typecheck` passes with regenerated types

**Definition of Done:**

- [ ] `api-contract/openapi.json` updated with validation schemas
- [ ] `frontend/src/generated/api.d.ts` regenerated
- [ ] Both committed in same commit (ADR-001 co-update rule)
- [ ] `npm run typecheck` passes
- [ ] `npm run lint` passes
- [ ] `npm run format:check` passes
