# Epic 04 Run Log – Exploration Mode & LLM Integration

**Start:** 2026-03-13
**Goal:** First end-to-end LLM turn — user message in, AI response via Anthropic Tool Use API out, ExplorationArtifact receives real content, everything persisted.

---

## STEP 0 — Epic Identified

Epic: `epic-04-exploration-llm.md`
Status: Stories not yet defined.
Dependencies: Epic 03 ✅ complete (148 tests green, all DoD checkboxes marked).

Technical debt obligations carried into this epic:
- DEBT-01: ExplorationArtifact Pflicht-Slot-Initialisierung (FR-B-00)
- DEBT-05: Orchestrator refactoring (299 lines → must split before extending)

---

## STEP 1 — Story Generation

**Date:** 2026-03-13

### Stories Generated

| ID | Title | Purpose |
|---|---|---|
| 04-01 | LLM Client Abstraction (base + AnthropicClient) | Define the `LLMClient` ABC and implement `AnthropicClient` with Anthropic Tool Use API. Establishes the provider-agnostic LLM interface all modes will use. |
| 04-02 | OllamaClient Stub + Factory | Add `OllamaClient` stub and a `create_llm_client()` factory so `LLM_PROVIDER=ollama` is config-selectable without any code change. |
| 04-03 | Orchestrator Refactoring (DEBT-05) | Extract artifact routing helpers from `orchestrator.py` (currently 299 lines) into `core/artifact_router.py` so the orchestrator stays under 300 lines after Epic 04 additions. Pure refactoring — all 148 existing tests must stay green. |
| 04-04 | ContextAssembler Upgrade | Wire `dialog_history_n` from `Settings` (fixes MUST-FIX-01 hardcoded value), add `artifact_template` to `ModeContext`, and add `prompt_context_summary()` helper for building the LLM system prompt from Working Memory fields. |
| 04-05 | OutputValidator (real implementation) | Replace the Epic 03 stub with a real validator that checks RFC 6902 syntax, required `tool_input` fields, and patch paths against the ArtifactTemplate allowlist before patches reach the Executor. |
| 04-06 | ExplorationMode (real LLM implementation) | Replace the stub in `modes/exploration.py` with a real LLM call. Initializes all 8 Pflicht-Slots on first turn (DEBT-01, FR-B-00). Creates `backend/prompts/exploration.md` (German system prompt). |
| 04-07 | Event Models for WebSocket Streaming | Define Pydantic models for all 6 WebSocket event types (`chat_token`, `chat_done`, `artifact_update`, `progress_update`, `debug_update`, `error`) in `backend/core/events.py`. No WebSocket implementation — models only, for Epic 05 readiness. |
| 04-08 | Integration Test: Full Turn Through Orchestrator | End-to-end test with mocked LLM: verifies 8 Pflicht-Slots initialized, patch applied and persisted, dialog history written, and OutputValidator blocks invalid patches. In-memory SQLite only — no live API calls. |

### Libraries Identified

| Library | Status | Usage |
|---|---|---|
| `anthropic` | Already in `requirements.txt` (≥ 0.25) | Anthropic Messages API with Tool Use in `AnthropicClient` |
| `jsonpatch` | Already in `requirements.txt` (≥ 1.33) | RFC 6902 syntax validation in `OutputValidator` |
| `pydantic` | Already in `requirements.txt` (≥ 2.6) | Event models (`events.py`), `LLMResponse` |
| `structlog` | Already in `requirements.txt` (≥ 24.1) | LLM I/O logging in `AnthropicClient` |
| `pydantic-settings` | Already in `requirements.txt` | `Settings` already has `llm_provider`, `llm_model`, `llm_api_key` |

**No new dependencies required.** All libraries needed for Epic 04 are already in `requirements.txt`.

### Escalation Points

These must be reviewed before implementation begins:

1. **ESCALATION-01 — `backend/core/events.py` placement:** HLA Section 6 does not list this file explicitly. Placed in `backend/core/` as a framework-agnostic module. Alternative: `backend/api/schemas.py`. No ADR currently required (no new directory), but placement should be confirmed before Story 04-07 starts.

2. **ESCALATION-02 — `APPLY_PATCHES_TOOL` constant location:** The JSON tool schema for the Anthropic API could live in `backend/modes/exploration.py` (mode-specific) or a shared `backend/llm/tools.py` (reusable across all future modes). The implementer must decide before Story 04-06; placement in `llm/tools.py` is recommended for reuse in later mode stories.

3. **ESCALATION-03 — Implementation order is strict:** 04-03 (refactoring) must run before any feature story modifies the orchestrator. 04-04 must complete before 04-05 (the `validate()` signature change depends on `ModeContext.artifact_template`). 04-06 depends on 04-01, 04-04, 04-05. 04-08 depends on all. Recommended order: **04-01 → 04-02 → 04-03 → 04-04 → 04-05 → 04-06 → 04-07 → 04-08**.

4. **ESCALATION-04 — `backend/prompts/` directory:** HLA Section 6 lists `backend/prompts/exploration.md` so no ADR is needed. However the directory does not yet exist. Story 04-06 creates it. The implementer should create the directory and file together in the Story 04-06 commit.

### Technical Debt Addressed

| Debt ID | Description | Addressed in Story |
|---|---|---|
| DEBT-01 | ExplorationArtifact Pflicht-Slot-Initialisierung (FR-B-00) — new projects have empty `slots={}` | 04-06 (ExplorationMode) + 04-08 (integration test) |
| DEBT-05 | Orchestrator file size (299 lines, will exceed 300 with Epic 04 additions) | 04-03 (refactoring) |
| MUST-FIX-01 | `context_assembler.py` hardcodes `_DEFAULT_HISTORY_TURNS = 20` instead of reading from `Settings.dialog_history_n` | 04-04 (ContextAssembler upgrade) |

---


## STEP 2 -- Validation

**Date:** 2026-03-13
**Validator:** Strict specification validator (Claude Sonnet 4.6)
**Documents read:** AGENTS.md, SDD lines 6-82 (ToC) + Section 4 (FR lines 256-569), HLA Section 6 (file structure), epic-04-exploration-llm.md in full, SDD Section 5.3 (Exploration Artifact field table), SDD Section 6.5 (Context Engineering).

---

### EPIC VALIDATION REPORT

#### 1. Structure Issues

None. The epic contains all required sections: Summary, Goal, Testable Increment, Dependencies, Key Deliverables, Stories. The testable increment is a runnable pytest command with explicit file path and observable outcome. All 8 stories contain user story (As a / I want / So that), specific acceptance criteria, and a Definition of Done checklist.

#### 2. SDD Compliance Issues

**ISSUE-01 -- Story 04-05 incorrect FR-A-03 citation (FIXED)**
The FR/NFR Traceability section of Story 04-05 cited FR-A-03 (OutputValidator -- identification of missing/invalid information). FR-A-03 in the SDD is "Identifikation fehlender Informationen" -- the LLM identifying missing process knowledge in dialog with the user. It has nothing to do with the OutputValidator. The OutputValidator maps correctly to FR-B-09 (Schreibkontrolle via RFC 6902) and SDD 6.5.2 (Output-Kontrakt), both of which were already listed. FR-A-03 has been removed from Story 04-05 traceability.

**ISSUE-02 -- Story 04-06 incorrect FR-D-06 citation (FIXED)**
The FR/NFR Traceability section of Story 04-06 cited FR-D-06 (Orchestrator step 7: mode.process()). FR-D-06 in the SDD is "Token-Monitoring und Prozesspartitionierung" -- not the mode process call. Step 7 in the HLA data flow is modus.call(context), which is the cognitive mode execution step (SDD 6.6.1, Explorationsmodus). FR-D-06 has been removed; SDD 6.6.1 was already listed and correctly covers this story scope.

**FR-A-02 (Tool Use API):** Story 04-01 AC item 7 explicitly enforces tool_choice: {type: tool, name: apply_patches}. VALID.

**FR-A-08 (German system prompt):** Story 04-06 AC item 6 and DoD confirm backend/prompts/exploration.md must be written in German. VALID.

**FR-B-00 (8 Pflicht-Slots by name):** Story 04-06 lists all 8 slot IDs and German titles. DoD checkbox lists all 8 IDs. VALID.

**FR-D-05 (ContextAssembler step 5):** Story 04-04 correctly traces to FR-D-05. VALID.

**FR-D-07 (Orchestrator step 8 -- OutputValidator):** Stories 04-05 and 04-08 both trace to FR-D-07. VALID.

**FR-D-12 (Factory pattern verification):** Story 04-02 defines factory with tests for all three provider cases (anthropic, ollama, unknown). VALID.

**FR-E-07 (Dialog history written):** Story 04-08 test_dialog_history_written asserts both user and assistant turns are written to DB and loadable via load_dialog_history(). VALID.

**SDD 6.5.3 Context fields:** Story 04-04 covers aktive_phase, aktiver_modus, slot summaries (filled/total per artifact), and spannungsfelder in prompt_context_summary(). artifact_template added to ModeContext. Dialog history wired via dialog_history_n from Settings. VALID.

#### 3. Architecture Issues

| File Path | HLA Section 6 Verdict | Notes |
|---|---|---|
| backend/llm/base.py | VALID | Explicitly listed in HLA Section 6 |
| backend/llm/anthropic_client.py | VALID | Explicitly listed in HLA Section 6 |
| backend/llm/ollama_client.py | VALID | Explicitly listed in HLA Section 6 |
| backend/llm/factory.py | NOT IN HLA (accepted) | Within HLA-defined backend/llm/ directory; no ADR required for helper modules in existing directories |
| backend/core/context_assembler.py | VALID | Explicitly listed in HLA Section 6 |
| backend/core/output_validator.py | VALID | Explicitly listed in HLA Section 6 |
| backend/core/orchestrator.py | VALID | Explicitly listed in HLA Section 6 |
| backend/core/artifact_router.py | NOT IN HLA (accepted) | Within HLA-defined backend/core/ directory; Story 04-03 contains explicit inline note; no ADR required |
| backend/core/events.py | NOT IN HLA (escalation flagged) | Within HLA-defined backend/core/ directory; ESCALATION-01 requires user confirmation before Story 04-07 implementation |
| backend/modes/exploration.py | VALID | Explicitly listed in HLA Section 6 |
| backend/prompts/exploration.md | VALID | Explicitly listed in HLA Section 6 |
| backend/llm/client.py (former Key Deliverables) | INVALID -- FIXED | Was listed in Key Deliverables but is not an HLA path; corrected to backend/llm/base.py + backend/llm/anthropic_client.py |
| backend/modes/exploration_mode.py (former Key Deliverables) | INVALID -- FIXED | Was listed in Key Deliverables but is not an HLA path; corrected to backend/modes/exploration.py |

**ISSUE-03 -- Key Deliverables contained two non-HLA paths (FIXED)**
backend/llm/client.py and backend/modes/exploration_mode.py were listed in Key Deliverables, violating AGENTS.md Rule 5 (Key Deliverables must use exact HLA paths). The Path Note in the Stories section acknowledged this but the Key Deliverables section itself was not corrected. Key Deliverables has been rewritten to use correct HLA Section 6 paths throughout, and now explicitly lists all new files introduced by the epic.

#### 4. Test Issues

None. Every story with logic defines tests. Tests cover positive and negative cases. All test file paths mirror the source structure under backend/tests/. Story 04-08 is a dedicated integration test story testing the full pipeline with mocked LLM and in-memory SQLite.

#### 5. DoD Issues

None. All 4 required DoD commands present in every story DoD checklist:
- ruff check . (run from backend/)
- ruff format --check . (run from backend/)
- python -m mypy . --explicit-package-bases (run from backend/)
- pytest --tb=short -q (run from backend/)

All structural requirements have their own DoD checkboxes per AGENTS.md Rule 2.

---

### EPIC VALID: YES

**Corrections applied directly in epic-04-exploration-llm.md:**

1. **Key Deliverables rewritten** -- replaced two non-HLA paths (backend/llm/client.py, backend/modes/exploration_mode.py) with the correct HLA Section 6 paths and expanded the list to include all deliverables the stories actually produce.

2. **Story 04-05 FR traceability** -- removed incorrect FR-A-03 reference. FR-A-03 is "Identifikation fehlender Informationen" (dialog-level missing info detection), not the OutputValidator gate. The correct references (FR-B-09, FR-D-07, SDD 6.5.2) were already present.

3. **Story 04-06 FR traceability** -- removed incorrect FR-D-06 reference. FR-D-06 is Token-Monitoring/Prozesspartitionierung, not the cognitive mode process call. SDD 6.6.1 (Explorationsmodus) was already listed and correctly covers this story.

**Open escalation points (require user decision before implementation):**

- ESCALATION-01: backend/core/events.py placement -- confirm backend/core/ vs backend/api/schemas.py before Story 04-07 starts.
- ESCALATION-02: APPLY_PATCHES_TOOL constant location -- confirm backend/modes/exploration.py (mode-specific) vs backend/llm/tools.py (shared) before Story 04-06 starts. Recommendation: backend/llm/tools.py for reuse across future mode stories.

---

## STEP 3 — Implementation

**Date:** 2026-03-13
**Implementer:** Claude Opus 4.6

### Stories Implemented

| ID | Title | Commit | Tests Added |
|---|---|---|---|
| 04-01 | LLM Client Abstraction | f120df2 | 6 (test_llm_client.py) |
| 04-02 | OllamaClient Stub + Factory | f1e2f5a | 4 (test_llm_client.py) |
| 04-03 | Orchestrator Refactoring (DEBT-05) | 04f5f38 | 0 (refactoring — all 148 existing tests stay green) |
| 04-04 | ContextAssembler Upgrade | d11e092 | 8 (test_context_assembler.py) |
| 04-05 | OutputValidator | 6830050 | 7 (test_output_validator.py) |
| 04-06 | ExplorationMode (real LLM) | 9b4c40f | 0 (behavior tested via 04-08 integration tests) |
| 04-07 | Event Models | 400a242 | 6 (test_events.py) |
| 04-08 | Integration Test | 0406417 | 4 (test_exploration_mode.py) |

**Total: 183 tests passing (148 existing + 35 new)**

### Modules Created

| File | Purpose |
|---|---|
| `backend/llm/base.py` | LLMClient ABC + LLMResponse Pydantic model |
| `backend/llm/anthropic_client.py` | AnthropicClient — Anthropic Messages API with Tool Use |
| `backend/llm/ollama_client.py` | OllamaClient stub (NotImplementedError) |
| `backend/llm/factory.py` | create_llm_client() factory function |
| `backend/llm/tools.py` | APPLY_PATCHES_TOOL constant (Anthropic tool schema) |
| `backend/core/artifact_router.py` | Extracted artifact routing helpers from orchestrator |
| `backend/core/events.py` | 6 WebSocket event Pydantic models + union type |
| `backend/prompts/exploration.md` | German system prompt for ExplorationMode |
| `backend/tests/test_llm_client.py` | Tests for LLM client + factory |
| `backend/tests/test_context_assembler.py` | Tests for ContextAssembler upgrade |
| `backend/tests/test_output_validator.py` | Tests for OutputValidator |
| `backend/tests/test_events.py` | Tests for event models |
| `backend/tests/test_exploration_mode.py` | Integration tests for full LLM turn |

### Modules Modified

| File | Changes |
|---|---|
| `backend/core/orchestrator.py` | Extracted helpers to artifact_router.py (194 lines, down from 299). Updated validate() call to pass artifact_template. |
| `backend/core/context_assembler.py` | Added settings parameter for dialog_history_n, artifact_template population, prompt_context_summary() function. |
| `backend/core/output_validator.py` | Replaced stub with real RFC 6902 + template validation. |
| `backend/modes/base.py` | Added artifact_template field to ModeContext. |
| `backend/modes/exploration.py` | Replaced stub with real LLM-backed implementation. |
| `backend/pyproject.toml` | Added mypy override for anthropic module. |
| `backend/tests/test_orchestrator.py` | Updated tests to accommodate new ExplorationMode behavior (Pflicht-Slot init patches). |

### ADRs Referenced

- ADR-003: WebSocket event models placed in `backend/core/events.py` (ESCALATION-01 resolved: placed in core/ as framework-agnostic models)
- ADR-004: APPLY_PATCHES_TOOL placed in `backend/llm/tools.py` (ESCALATION-02 resolved: shared module for reuse across modes)
- ADR-002: Flags in WorkingMemory for observability (existing, referenced in modes/base.py)

### Libraries Used

All libraries were already in `requirements.txt` — no new dependencies added:
- `anthropic` (≥ 0.25): Anthropic Messages API in AnthropicClient
- `jsonpatch` (≥ 1.33): RFC 6902 validation concept (actual validation uses regex matching via ArtifactTemplate)
- `structlog` (≥ 24.1): LLM I/O logging
- `pydantic` (≥ 2.6): LLMResponse, event models
- `pydantic-settings` (≥ 2.2): Settings.dialog_history_n

### Decisions Made During Implementation

1. **APPLY_PATCHES_TOOL in `llm/tools.py`** — placed in shared module (not mode-specific) to enable reuse by StructuringMode, SpecificationMode etc. in future epics.

2. **ExplorationMode accepts optional LLMClient** — constructor signature is `__init__(self, llm_client: LLMClient | None = None)` to maintain backward compatibility with Epic 03 tests that construct ExplorationMode() without arguments. When llm_client is None, the mode returns only init patches (stub behavior).

3. **OutputValidator signature** — `validate(output, artifact_template=None)` where artifact_template is optional. When None (e.g., during `abgeschlossen` phase), only RFC 6902 syntax is checked without template path validation. This avoids errors when no template maps to the current phase.

4. **Orchestrator test update** — `test_invalidation_write_applied_after_structure_patch` needed phase set to `strukturierung` since the OutputValidator now validates patch paths against the phase-specific template. Previously (stub validator returning True), the test worked with the default exploration phase despite sending structure patches.

---

## STEP 4 — Test Validation

**Date:** 2026-03-13
**Validator:** Claude Sonnet 4.6

### Test Validation Report

#### `test_llm_client.py`

- **Coverage of acceptance criteria:** GAPS (see below)
- **Negative test coverage:** GAPS — the existing API-error negative test used `RuntimeError` instead of the `anthropic.APIStatusError` specified by AC10 Story 04-01. Mock did not reflect the real Anthropic SDK exception contract.
- **Assertion quality:** WEAK in one area — logging not tested at all (AC9 Story 04-01).
- **Mock quality:** ISSUES — RuntimeError is too broad; the real contract specifies `anthropic.APIStatusError`.

Gaps found and fixed:
1. `test_anthropic_client_api_error_propagated` — replaced `RuntimeError` mock with a real `anthropic.APIStatusError` constructed with `httpx.Request` + `httpx.Response`. Now verifies the specific exception type required by AC10.
2. `test_anthropic_client_logs_when_enabled` (new) — verifies AC9: when `llm_log_enabled=True`, structlog `info()` is called for both request and response, with correct fields (`model`, `has_tool_use`).

#### `test_output_validator.py`

- **Coverage of acceptance criteria:** GAPS
- **Negative test coverage:** COMPLETE for the 5 failure modes listed in scope.
- **Assertion quality:** STRONG — all assertions use `is True` / `is False` exact boolean equality.
- **Mock quality:** GOOD

Gaps found and fixed:
1. `test_valid_add_patch_for_new_slot_id_passes` (new) — explicitly verifies that an `add` patch to an arbitrary new slot path (e.g. `/slots/new_custom_slot`) is accepted, confirming the template uses `[^/]+` regex (any slot ID is valid).
2. `test_patch_with_unknown_top_level_path_fails_validation` (new) — verifies that a patch targeting a non-`/slots/` top-level key (e.g. `/unknown_key/...`) is rejected by the template.

#### `test_exploration_mode.py`

- **Coverage of acceptance criteria:** GAPS
- **Negative test coverage:** COMPLETE for what was tested.
- **Assertion quality:** STRONG for existing tests (exact set comparison for slot IDs, exact string equality for inhalt).
- **Mock quality:** GOOD — uses `AsyncMock(spec=LLMClient)`.

Gaps found and fixed:
1. `test_second_turn_does_not_reinitialize_slots` (new) — AC#4 Story 04-06: runs two orchestrator turns and asserts that exactly 8 slots exist after both (not 16), verifying the idempotency of Pflicht-Slot initialization.
2. `test_nearing_completion_phasenstatus_when_all_slots_filled` (new) — AC#8 Story 04-06: constructs a context where all 8 Pflicht-Slots have `completeness_status=vollstaendig` and asserts `output.phasenstatus == Phasenstatus.nearing_completion`.

#### `test_events.py`

- **Coverage of acceptance criteria:** GAPS
- **Negative test coverage:** GAPS — no test verified that the `WebSocketEvent` union type rejects unknown discriminator values.
- **Assertion quality:** STRONG for the 6 round-trip tests.
- **Mock quality:** N/A (no mocks needed — pure Pydantic model tests).

Gaps found and fixed:
1. `test_websocket_event_union_rejects_unknown_type` (new) — uses `pydantic.TypeAdapter(WebSocketEvent)` to verify that `{"event": "totally_unknown_type", ...}` raises `ValidationError`.

#### `test_context_assembler.py`

- **Coverage of acceptance criteria:** GAPS
- **Negative test coverage:** N/A for this component.
- **Assertion quality:** WEAK — `test_build_context_uses_settings_dialog_history_n` verified `len(context.dialog_history) == 3` but not that those 3 entries are the *last* 3 (chronologically most recent), not the *first* 3.
- **Mock quality:** GOOD.

Gaps found and fixed:
1. `test_build_context_dialog_history_n_returns_last_n_turns` (new) — writes 5 turns (Turn 1–5), requests `dialog_history_n=3`, and asserts the returned entries contain Turn 3, Turn 4, Turn 5 — and that Turn 1 and Turn 2 are NOT present.

**Bug discovered:** This new test revealed a real bug in `ProjectRepository.load_dialog_history()`. The SQL query used `ORDER BY turn_id ASC LIMIT ?` which returns the **first** N turns, not the last N. The docstring says "Die letzten N Dialogturns" (the last N turns). Fixed by using a DESC subquery to select the last N rows and an outer query to restore chronological order:
```sql
SELECT role, inhalt, timestamp FROM (
    SELECT role, inhalt, timestamp, turn_id, id
    FROM dialog_history
    WHERE projekt_id = ?
    ORDER BY turn_id DESC, id DESC
    LIMIT ?
) ORDER BY turn_id ASC, id ASC
```

### Summary

| Test file | Tests before | Tests added | Total |
|---|---|---|---|
| `test_llm_client.py` | 8 | 2 | 10 |
| `test_output_validator.py` | 7 | 2 | 9 |
| `test_exploration_mode.py` | 4 | 2 | 6 |
| `test_events.py` | 6 | 1 | 7 |
| `test_context_assembler.py` | 7 | 1 | 8 |
| **Total** | **183** | **7** | **190** |

### Bug Fixed

`backend/persistence/project_repository.py` — `load_dialog_history()` was returning the FIRST N turns instead of the LAST N turns. Fixed with a DESC subquery + outer ASC re-sort. The fix is covered by the new `test_build_context_dialog_history_n_returns_last_n_turns` test.

### VALID: YES

All 7 new tests added. Bug in `load_dialog_history` fixed. All 190 tests pass. All DoD commands pass (ruff check, ruff format --check, mypy --explicit-package-bases, pytest).

**Commit:** `4eeeebd` — `test(epic-04): strengthen test suite per validate-tests`

---

## STEP 6 — Audit

**Date:** 2026-03-13
**Auditor:** Claude Sonnet 4.6 (strict architecture and compliance auditor)
**Documents read:** AGENTS.md (full), SDD lines 6–82 (ToC) + Section 4 FR lines 256–569, HLA Section 6 (Projektstruktur, lines 532–640), epic-04-exploration-llm.md (full), all Epic 04 source and test files, all 4 ADRs.

---

### AUDIT REPORT

#### Architecture Compliance (Phase 2)

All file paths checked against HLA Section 6:

| File | HLA Status | Notes |
|---|---|---|
| `backend/llm/base.py` | VALID | Explicitly listed in HLA Section 6 |
| `backend/llm/anthropic_client.py` | VALID | Explicitly listed in HLA Section 6 |
| `backend/llm/ollama_client.py` | VALID | Explicitly listed in HLA Section 6 |
| `backend/llm/factory.py` | ACCEPTED | Not listed explicitly; within HLA-defined `backend/llm/` — no new directory |
| `backend/llm/tools.py` | ACCEPTED | ADR-004 governs; within HLA-defined `backend/llm/` |
| `backend/core/artifact_router.py` | ACCEPTED | Not listed explicitly; within HLA-defined `backend/core/` — no new directory |
| `backend/core/context_assembler.py` | VALID | Explicitly listed in HLA Section 6 |
| `backend/core/output_validator.py` | VALID | Explicitly listed in HLA Section 6 |
| `backend/core/orchestrator.py` | VALID | Explicitly listed in HLA Section 6 |
| `backend/core/events.py` | ACCEPTED | ADR-003 governs; within HLA-defined `backend/core/` |
| `backend/modes/base.py` | VALID | Explicitly listed in HLA Section 6 |
| `backend/modes/exploration.py` | VALID | Explicitly listed in HLA Section 6 |
| `backend/prompts/exploration.md` | VALID | Explicitly listed in HLA Section 6 |
| `backend/config.py` | VALID | Explicitly listed in HLA Section 6 |
| `backend/requirements.txt` | VALID | Explicitly listed in HLA Section 6 |

**Line counts (all within 300-line limit):**

| File | Lines |
|---|---|
| `backend/llm/base.py` | 60 |
| `backend/llm/anthropic_client.py` | 95 |
| `backend/llm/ollama_client.py` | 36 |
| `backend/llm/factory.py` | 39 |
| `backend/llm/tools.py` | 47 |
| `backend/core/artifact_router.py` | 100 |
| `backend/core/orchestrator.py` | 197 |
| `backend/core/context_assembler.py` | 107 |
| `backend/core/output_validator.py` | 83 |
| `backend/core/events.py` | 74 |
| `backend/modes/exploration.py` | 152 |
| `backend/modes/base.py` | 84 |
| `backend/config.py` | 47 |

No invented directories. No files exceed 300 lines. Architecture compliance: PASS.

**API directory:** `backend/api/` contains only `__init__.py` — last modified in the initial scaffold commit. No changes in Epic 04. PASS.

---

#### Dependency Compliance (Phase 3)

`requirements.txt` contains: `fastapi`, `uvicorn`, `pydantic`, `pydantic-settings`, `anthropic`, `jsonpatch`, `structlog`, `pytest`, `pytest-asyncio`, `httpx`, `ruff`, `mypy`. No new packages added. All packages are in the original tech stack. The `anthropic` package (≥ 0.25) is used correctly via `anthropic.Anthropic(api_key=...)` and `client.messages.create()` with `tool_choice` and content block parsing. Dependency compliance: PASS.

---

#### SDD Requirements Compliance (Phase 4)

**FR-A-02 (Tool Use API):** `AnthropicClient.complete()` passes `tool_choice={"type": "tool", "name": "apply_patches"}` by default (line 22, `_DEFAULT_TOOL_CHOICE`). The `tools` parameter is sent when provided. `ExplorationMode.call()` explicitly passes `tools=[APPLY_PATCHES_TOOL]` and `tool_choice={"type": "tool", "name": "apply_patches"}` (lines 136–137). PASS.

**FR-A-04 (ContextAssembler builds prompt from WM fields):** `prompt_context_summary()` in `context_assembler.py` formats `aktive_phase`, `aktiver_modus`, slot counts, and `spannungsfelder` from the Working Memory. `ExplorationMode.call()` injects this summary into the system prompt via `{context_summary}` placeholder replacement. PASS.

**FR-A-08 (German language):** `backend/prompts/exploration.md` is written entirely in German. The file instructs the mode to communicate "ausschließlich auf Deutsch" and all headings, bullet points, and instructions are in German. PASS.

**FR-B-00 (8 Pflicht-Slots initialized on first turn):** `PFLICHT_SLOTS` dict in `exploration.py` contains all 8 required IDs: `prozessausloeser`, `prozessziel`, `scope`, `beteiligte_systeme`, `umgebung`, `randbedingungen`, `ausnahmen`, `prozesszusammenfassung` with correct German titles. `_build_init_patches()` generates `add` patches for all missing slots with `completeness_status="leer"`. `test_first_turn_initializes_pflicht_slots` asserts all 8 are present after the first turn. PASS.

**FR-D-05 (Orchestrator step 5 calls ContextAssembler):** `orchestrator.py` line 108 (post-fix: lines 111–113): `context = build_context(project, completeness_state, repository=repo, settings=self._settings)`. Called at "Schritt 5: Kontext zusammenstellen" before mode.call(). PASS.

**FR-D-07 (Orchestrator step 7 calls OutputValidator):** `orchestrator.py` lines 118–120 (Schritt 6/7 area): `if not validate(mode_output, context.artifact_template)`. OutputValidator is called before patches are applied to the artifact. PASS.

**FR-D-12 (LLM provider switchable via config):** `create_llm_client(settings)` in `factory.py` reads `settings.llm_provider` and returns the correct client. `Settings.llm_provider` is a `Literal["anthropic", "ollama"]` field loaded from `.env`. No hardcoded provider anywhere in orchestrator or modes. PASS.

**FR-E-07 (Dialog history written after each turn):** `orchestrator.py` lines 172–175: `repo.append_dialog_turn(project.projekt_id, wm.letzter_dialogturn, "user", input.text)` and `repo.append_dialog_turn(..., "assistant", mode_output.nutzeraeusserung)` are called at Schritt 11 after persistence. `test_dialog_history_written` asserts both turns appear in DB. PASS.

SDD requirements compliance: PASS on all checked FRs.

---

#### Test Coverage (Phase 5)

**Test file locations mirror source structure:** PASS (all in `backend/tests/`).

**Test count:** 190 tests total (148 from Epics 01–03 + 42 new from Epic 04). Epic status document says 183 after implementation; Step 4 validation added 7 more = 190. Current run confirms: 190 passed.

**Test files for Epic 04:**

| Source | Test file | Tests |
|---|---|---|
| `llm/base.py` + `llm/anthropic_client.py` + `llm/factory.py` | `test_llm_client.py` | 10 |
| `core/output_validator.py` | `test_output_validator.py` | 8 |
| `modes/exploration.py` + orchestrator integration | `test_exploration_mode.py` | 6 |
| `core/events.py` | `test_events.py` | 7 |
| `core/context_assembler.py` | `test_context_assembler.py` | 8 |

Total Epic 04 new tests: 39 (slight discrepancy with the 35 listed in STEP 3 + 7 in STEP 4 = 42; the actual count from passing suite is what matters: 190 total).

**Test quality spot-check:**
- `test_llm_client.py`: positive, negative (no tool_use), API-error, logging, default tool_choice, factory cases, unknown provider. All falsifiable. PASS.
- `test_output_validator.py`: 8 cases covering valid, invalid op, invalid path, missing value for add/replace, remove without value, new slot ID, unknown top-level key. PASS.
- `test_exploration_mode.py`: Pflicht-Slot initialization, patch persistence, dialog history, invalid path rejection, second turn idempotency, nearing_completion status. PASS.
- `test_events.py`: 6 round-trip tests + union discriminator rejection. PASS.
- `test_context_assembler.py`: dialog_history_n respects settings, last-N ordering, artifact_template per phase, prompt_context_summary content. PASS.

No tests weakened compared to prior epics. Test coverage: PASS.

---

#### DoD Verification (Phase 6)

Commands run from `backend/` with venv activated:

| Command | Result |
|---|---|
| `ruff check .` | All checks passed (exit 0) |
| `ruff format --check .` | 46 files already formatted (exit 0) |
| `python -m mypy . --explicit-package-bases` | Success: no issues found in 46 source files (exit 0) |
| `pytest --tb=short -q` | 190 passed in 2.28s (exit 0) |

DoD verification: PASS.

---

#### API Contract (Phase 7)

`backend/api/` was NOT modified during Epic 04 — only `__init__.py` exists (from initial scaffold). No new REST endpoints were introduced. `backend/core/events.py` uses Pydantic correctly: each model inherits `BaseModel`, each has a `Literal[...]` discriminator field with a default value, `WebSocketEvent` is a union type alias. All 6 models serialize and deserialize correctly (verified by round-trip tests in `test_events.py`). API contract: PASS.

---

#### Code Quality (Phase 8)

All functions in Epic 04 files have parameter type hints and return type annotations. Imports are used (verified by `ruff check .` — no unused import warnings). Naming is consistent snake_case throughout. No dead code found. No copy-paste patterns requiring abstraction. `ExplorationMode.__init__` accepts `llm_client: LLMClient | None = None` (optional for backward compatibility with existing tests) — this is a deliberate decision documented in STEP 3. Code quality: PASS.

---

#### ADR Coverage (Phase 9)

ADRs present in `agent-docs/decisions/`:

| ADR | Title | Status | Required? |
|---|---|---|---|
| ADR-001 | OpenAPI Contract | Accepted | Pre-existing (Epic 01) |
| ADR-002 | Flags in WorkingMemory | Accepted | Yes — covers WorkingMemory.flags field deviation from SDD 6.4.1 |
| ADR-003 | WebSocket Event Models in backend/core/events.py | Accepted | Yes — covers events.py placement (ESCALATION-01) |
| ADR-004 | Anthropic Tool Schema in backend/llm/tools.py | Accepted | Yes — covers tools.py placement (ESCALATION-02) |

All three Epic 04 decisions requiring ADRs are covered (ADR-002, ADR-003, ADR-004). ADR-002 and ADR-003 and ADR-004 are all dated 2026-03-13 (Accepted before implementation). PASS.

---

### FIXES APPLIED

**FIX-01 — Orchestrator not passing `settings` to `build_context`** (critical compliance defect):

The `Orchestrator.process_turn()` was calling `build_context(project, completeness_state, repository=repo)` without `settings`. This caused `build_context()` to fall back to the hardcoded default of 20 for `dialog_history_n` in all production code paths, regardless of the `DIALOG_HISTORY_N` environment variable configured in `.env`. The Story 04-04 tests (`test_build_context_uses_settings_dialog_history_n`) exercised `build_context` directly but never through the orchestrator, so the defect was invisible to the test suite.

**Changes made:**

1. `backend/core/orchestrator.py`: Added `from config import Settings` import.
2. `backend/core/orchestrator.py`: Added `settings: Settings | None = None` parameter to `Orchestrator.__init__()` and `self._settings = settings`.
3. `backend/core/orchestrator.py`: Updated `build_context(...)` call to pass `settings=self._settings`.
4. `ruff format .` applied (reformatted the `build_context(...)` call to multi-line).

The `settings` parameter is optional (`None` by default) so existing orchestrator test fixtures that do not inject settings continue to work — they fall back to the hardcoded 20, which matches the backward-compatibility contract already in `build_context`. Epic 05 must inject `settings` when constructing `Orchestrator` to make `dialog_history_n` configurable end-to-end.

**Verification after fix:**

```
ruff check .             → All checks passed
ruff format --check .    → 46 files already formatted
mypy . --explicit-package-bases → Success: no issues in 46 source files
pytest --tb=short -q     → 190 passed in 2.28s
```

---

### FINAL STATUS

| Criterion | Status |
|---|---|
| AGENTS.md compliance | YES |
| HLA architecture compliance | YES |
| SDD requirements compliance | YES |
| Dependency compliance | YES |
| Test coverage (190 tests, all passing) | YES |
| DoD commands (all 4 exit 0) | YES |
| API contract (no unintended changes) | YES |
| ADR coverage (ADR-002, ADR-003, ADR-004) | YES |
| Code quality (type hints, naming, no dead code) | YES |

**All checks: YES. Epic 04 audit complete.**

**Fix commit required:** The `settings` injection fix in `orchestrator.py` must be committed.
