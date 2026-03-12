# Management Summary — Epic 03: Orchestrator & Working Memory

**Date:** 2026-03-12
**Report covers:** Epic 03 implementation, completed 2026-03-12
**Prepared for:** Technically literate stakeholder (non-developer audience)

---

## 1. Epic Summary

Epic 03 built the central control loop of the Digitalisierungsfabrik system — the **Orchestrator** — together with the **Working Memory** component and the full set of **cognitive mode placeholders**.

The Orchestrator is the brain of every conversation turn. When a user types a message, the Orchestrator takes that input through an eleven-step cycle: it loads the current project from the database, determines which mode (Exploration, Structuring, etc.) should handle the turn, calls that mode, applies any resulting changes to the process artifacts, recalculates how complete the artifacts are, decides whether a mode switch is needed, and saves everything back to the database — atomically, so that no partial state is ever stored.

The cognitive modes (ExplorationMode, StructuringMode, SpecificationMode, ValidationMode, Moderator) are presently placeholders. They respond with a fixed German stub message and make no artifact changes. This is intentional: it lets the full eleven-step cycle be tested and verified without requiring a real AI call, providing a solid foundation for the upcoming LLM integration in Epic 04.

**Why it matters:** Epic 03 closes the loop from user input to persisted project state. All prior components — data models (Epic 01) and the execution engine (Epic 02) — are now wired together through a single, testable pipeline. The system can receive input, process it, update state, and persist it — end-to-end — for the first time.

---

## 2. Implemented Components

### Flag Enum and BaseMode Interface
**Purpose:** Defines the shared contract that every cognitive mode must fulfill, so the Orchestrator can call any mode interchangeably.
**Files:** `backend/modes/base.py`
**Architecture fit:** The `Flag` enum (six values from SDD Section 6.4.1) carries control signals from a mode back to the Orchestrator — for example, `phase_complete` tells the Orchestrator to switch to the Moderator. `ModeContext` packages everything a mode needs as input; `ModeOutput` standardises what a mode returns. `BaseMode` is the abstract class all five modes extend.

### Five Stub Cognitive Modes
**Purpose:** Allow the Orchestrator cycle to run end-to-end without an AI call. Each stub returns a German placeholder message, no artifact patches, and no flags.
**Files:** `backend/modes/exploration.py`, `backend/modes/structuring.py`, `backend/modes/specification.py`, `backend/modes/validation.py`, `backend/modes/moderator.py`
**Architecture fit:** These files use the final production class names (ExplorationMode, StructuringMode, etc.). In later epics, the stub bodies are replaced by real AI-backed logic without renaming or restructuring any files.

### CompletenessCalculator
**Purpose:** After every turn, the Orchestrator needs to know how many artifact slots exist and how many have been filled. The CompletenessCalculator counts these numbers across all three artifacts and produces a per-slot status map.
**Files:** `backend/artifacts/completeness.py`
**Architecture fit:** Implements the slot-counting requirement from SDD Section 6.7. The counts feed directly into Working Memory fields (`befuellte_slots`, `bekannte_slots`) and drive the progress indicator visible to the user.

### Orchestrator — 11-Step Turn Cycle
**Purpose:** The single entry point for every user turn. Receives user input, coordinates all components, ensures nothing is written to the database unless the full cycle succeeds.
**Files:** `backend/core/orchestrator.py`
**Architecture fit:** Implements SDD Section 6.3 exactly. The Orchestrator is framework-agnostic — it knows nothing about HTTP or WebSocket. It accepts a `TurnInput` and returns a `TurnOutput`, both typed as Pydantic models so they can be directly referenced in the WebSocket message schema in Epic 05.

### ContextAssembler (stub)
**Purpose:** Assembles the full context object that gets handed to the active mode before each call, combining project data, artifacts, completeness state, and dialog history.
**Files:** `backend/core/context_assembler.py`
**Architecture fit:** Currently returns an empty dialog history — full dialog history loading is deferred to Epic 04. The structure is already in place; Epic 04 will fill in the loading logic.

### OutputValidator (stub)
**Purpose:** After a mode returns its output, the OutputValidator checks that the output meets the required contract before the Orchestrator acts on it.
**Files:** `backend/core/output_validator.py`
**Architecture fit:** Currently always returns valid — stub modes cannot produce invalid output. Full contract enforcement (for real LLM outputs that may be malformed) is implemented in Epic 04.

### ProgressTracker
**Purpose:** Writes the updated phase status and slot counts from each turn back into Working Memory.
**Files:** `backend/core/progress_tracker.py`
**Architecture fit:** A small, focused component that separates the concern of Working Memory updates from the Orchestrator's control logic. Fully functional (not a stub).

---

## 3. SDD Progress

| SDD Section | Topic | Status |
|---|---|---|
| 1.1–1.3 | System purpose, users, German language | Implemented (architecture compliant; language not yet exercised end-to-end) |
| 2.x | UI, chat pane, artifact pane, debug panel | Not yet implemented (Epics 05–06) |
| 4 / FR-B-09 | RFC 6902 JSON Patch write control via Executor | Fully implemented (Epic 02, now wired in Orchestrator) |
| 4 / FR-B-03, FR-B-04 | Referential integrity and invalidation logic | Implemented: Executor returns affected IDs; Orchestrator applies invalidation writes (step 8 of cycle) |
| 4 / FR-D-01 | Orchestrator as sole controller of mode switches and artifact writes | Fully implemented |
| 4 / FR-D-02 | Moderator mode available | Stub implemented; full logic in Epic 07 |
| 4 / FR-D-04 | Context handover on mode switch | Structural scaffolding in place; dialog history loading deferred to Epic 04 |
| 5.x | Artifact schemas (all three), enums, completeness states | Fully implemented (Epic 01, no changes needed in Epic 03) |
| 6.3 | 11-step Orchestrator cycle | Fully implemented |
| 6.4 | Working Memory fields | Fully implemented |
| 6.4.1 | Flag enum (six values) | Fully implemented |
| 6.6 | ACID persistence of project state | Fully implemented (via ProjectRepository) |
| 6.7 | Slot count and completeness state calculation | Fully implemented (CompletenessCalculator) |
| 6.5 / FR-D-05 | Context engineering, dialog history window | Partial — ContextAssembler stub; full implementation in Epic 04 |
| 6.5.2 | OutputValidator / output contract enforcement | Partial — always-true stub; full implementation in Epic 04 |
| 8.x | LLM client abstraction, Anthropic / Ollama | Not yet implemented (Epic 04) |
| API layer, WebSocket | REST endpoints, real-time streaming | Not yet implemented (Epic 05) |
| React frontend | Browser UI | Not yet implemented (Epic 06) |

---

## 4. Test Status

**Total tests: 135 — all passing.**

37 new tests were added in Epic 03 (17 for CompletenessCalculator, 20 for the Orchestrator, Working Memory, and modes). No tests from earlier epics were deleted or weakened.

| Test file | Tests | What is covered |
|---|---|---|
| `test_models.py` (Epic 01) | 22 | Pydantic model validation, schema correctness, enum values |
| `test_persistence.py` (Epic 01) | 37 | SQLite round-trips, ACID transactions, load/save/list |
| `test_executor.py` (Epic 02) | 39 | RFC 6902 patch application, rollback, invalidation detection |
| `test_completeness.py` (Epic 03) | 17 | Slot counting, completeness state map, edge cases |
| `test_orchestrator.py` (Epic 03) | 20 | Full turn cycle, mode dispatch, mode switches on flags, error path, persistence round-trip |

All four quality-gate commands pass with exit code 0:
- `ruff check .` — no linting errors
- `ruff format --check .` — no formatting deviations
- `python -m mypy . --explicit-package-bases` — no type errors (34 files checked)
- `pytest --tb=short -q` — 135 passed in 1.72 seconds

The test run confirmed on 2026-03-12: `135 passed in 1.72s`.

---

## 5. Problems Encountered

Six issues arose during Epic 03. All were resolved before committing.

**1. stubs.py not in the HLA architecture (Critical)**
The initial epic plan proposed a single `stubs.py` file for all five mode stubs. This file path does not appear in the architecture specification (HLA Section 6), which would have violated a non-negotiable rule. The fix was to place each stub in its own HLA-defined file under the final production class name.

**2. test_working_memory.py not in the HLA test mapping (Major)**
The initial plan referenced a separate test file for Working Memory tests. This file is not in the approved test location mapping. Working Memory tests were merged into `test_orchestrator.py`, which is the correct location per the project rules.

**3. DoD command format correction (Minor)**
Draft Definition-of-Done commands used `ruff check backend/` instead of the canonical format `ruff check .` run from inside the `backend/` directory. All commands were corrected to match the project standard exactly.

**4. pytest-asyncio not installed**
The async testing framework `pytest-asyncio` was listed in `requirements.txt` but was not installed in the virtual environment. This caused async tests to fail on first run. Fixed by installing it from the existing requirements file — no new dependency was introduced.

**5. Two test failures due to SQLite version-skip behavior at version 0**
The repository's `save()` method skips writing artifact data if the version has already been stored (to avoid duplicates). Two tests manually pre-populated artifacts at version 0, which is also the version created by `create()`. The pre-populated data was silently skipped. Fixed by setting `version=1` on manually created test artifacts in those tests, matching the contract that pre-existing version 0 belongs to the empty initial state.

**6. Incorrect type hint on Orchestrator constructor**
The Orchestrator's constructor had `repository: object` as a type annotation with a comment claiming it was to avoid a circular import. No circular import actually exists. The type was replaced with the proper `ProjectRepository` type, using a standard module-level import. This was discovered during the post-implementation audit.

---

## 6. Remaining Issues

The following limitations are known and by design for this epic. They will be addressed in later epics.

- **All five cognitive modes are stubs.** They return fixed placeholder text and never call an AI model. Real AI integration begins in Epic 04.
- **ContextAssembler returns empty dialog history.** The dialog history loading mechanism is not implemented yet. The Orchestrator hands modes an empty conversation history on every turn. This will be filled in during Epic 04.
- **OutputValidator always returns True.** Real AI responses can be malformed or contract-violating. The validator will enforce the full output contract in Epic 04, once real LLM outputs are in play.
- **No WebSocket or API layer.** The Orchestrator can only be called programmatically from tests. There is no HTTP endpoint and no browser connection yet. This is implemented in Epic 05.

---

## 7. System Integration

The full turn cycle, as it stands after Epic 03, flows as follows:

**User input → Orchestrator.process\_turn**
1. Load project from SQLite via `ProjectRepository`
2. Increment `letzter_dialogturn` (turn counter) in Working Memory
3. Read flags from the previous turn (stored in Working Memory for observability)
4. Determine the active mode from Working Memory (`aktiver_modus`); default to `"exploration"` if not set
5. Build mode context via `ContextAssembler` (currently: empty dialog history)
6. Call the active mode: `await mode.call(context)` → returns `ModeOutput`
7. If the mode returned patches: apply them via `Executor.apply_patches()` to the relevant artifact; if the Executor fails, return a `TurnOutput` with an error and do NOT save
8. If the Executor returned invalidated algorithm section IDs: apply a second Executor call to mark those sections as `invalidiert` (SDD FR-B-04)
9. Recalculate completeness via `CompletenessCalculator`; update Working Memory slot counts and completeness map
10. Update `phasenstatus` in Working Memory from the mode output; evaluate mode-switch flags (`phase_complete`, `escalate`, `blocked`) — if any are set, switch `aktiver_modus` to `"moderator"` and store the prior mode in `vorheriger_modus`
11. Save the complete updated project to SQLite atomically via `repository.save()`
12. Return `TurnOutput` to the caller (which will eventually be the WebSocket handler in Epic 05)

---

## 8. Project Progress

**What works end-to-end today:**

The backend pipeline from data models through to orchestration is complete and fully tested. A developer can programmatically create a project, send it through one or more turns, and retrieve the updated project state from the SQLite database. All artifact writes go through the validated RFC 6902 patch pipeline. Invalidation propagation between the Structure Artifact and Algorithm Artifact works correctly. The Orchestrator enforces mode-switch rules from the SDD.

**What still needs to be built:**

- **LLM integration** (Epic 04): Replace the five mode stubs with real AI calls via the Anthropic API. Implement the ContextAssembler's dialog history loading and the OutputValidator's contract enforcement.
- **Dialog history persistence** (Epic 04): The `dialog_history` table exists in SQLite but is not yet written to or read from.
- **REST API and WebSocket layer** (Epic 05): Wrap the Orchestrator in FastAPI endpoints so it can be reached from a browser.
- **React frontend** (Epic 06): Build the chat pane, artifact pane, and debug panel.
- **Moderator and phase transitions** (Epic 07): Implement the Moderator's heuristic logic for deciding when to advance between phases.
- **Structuring, Specification, Validation modes** (Epics 08–10): Replace remaining stubs with real AI logic.
- **End-to-end stabilization and export** (Epic 11): Final integration, edge-case fixes, and artifact download feature.

---

## 9. Project Status Overview

| Epic | Title | Status |
|---|---|---|
| Epic 00 | Project Foundation & Dev Setup | Completed |
| Epic 01 | Data Models & Persistence | Completed — 51 tests |
| Epic 02 | Execution Engine (Executor + JSON Patch) | Completed — 98 tests cumulative |
| **Epic 03** | **Orchestrator & Working Memory** | **Completed — 135 tests** |
| Epic 04 | Exploration Mode & LLM Integration | Not started |
| Epic 05 | Backend API (REST + WebSocket) | Not started |
| Epic 06 | React Frontend (Chat + Artifact Pane) | Not started |
| Epic 07 | Moderator & Phase Transitions | Not started |
| Epic 08 | Structuring Mode | Not started |
| Epic 09 | Specification Mode | Not started |
| Epic 10 | Validation Mode & Correction Loop | Not started |
| Epic 11 | End-to-End Stabilization & Artifact Export | Not started |

Three of eleven epics are complete. The project is on track against the planned implementation sequence.

---

## 10. SDD Coverage

| SDD Section | Topic | Coverage |
|---|---|---|
| Section 1 — System Overview | Purpose, target users, German language | Partial — architecture compliant; language not exercised without LLM |
| Section 2 — UI & Interaction | Chat pane, artifact pane, debug panel, Panik-Button, phase display | Not implemented |
| Section 4 / Group A — Knowledge Extraction | Dialogic interview, follow-up questions, missing-info detection | Not implemented (requires LLM, Epics 04–09) |
| Section 4 / Group B — Artifact Management (FR-B-09, FR-B-03, FR-B-04) | Write control via Executor, referential integrity, invalidation | Fully implemented |
| Section 4 / Group B — other B requirements | Download/export, version restore, continuous visibility | Not implemented (Epics 05–06, 11) |
| Section 4 / Group C — Validation & Consistency | EMMA compatibility, inconsistency detection, correction loop | Not implemented (Epics 08–10) |
| Section 4 / Group D — Orchestration (FR-D-01, FR-D-04) | Orchestrator as sole controller, context handover | Fully implemented |
| Section 4 / Group D — FR-D-02, FR-D-03 | Moderator mode, Panik-Button | Stub implemented; full logic in Epics 05–07 |
| Section 4 / Group E — Persistence (FR-E-01) | ACID transactions | Fully implemented |
| Section 5 — Artifact Schemas | All three artifact types, enums, completeness states | Fully implemented |
| Section 6.3 — Orchestrator 11-step cycle | Turn cycle | Fully implemented |
| Section 6.4 — Working Memory | All WM fields | Fully implemented |
| Section 6.4.1 — Flag enum | Six control flags | Fully implemented |
| Section 6.5 — Context Engineering | Dialog history window, context assembly | Partial (stub) |
| Section 6.5.2 — Output contract / OutputValidator | Validation of LLM output | Partial (stub — always true) |
| Section 6.6 — Cognitive Modes | LLM-backed mode logic | Stubs only |
| Section 6.7 — Completeness / Slot counting | Slot counts and completeness map | Fully implemented |
| Section 7 — Persistence layer / SQLite | Schema, transactions, repository | Fully implemented |
| Section 8.1 — LLM client abstraction | Anthropic / Ollama provider switching | Not implemented |
| Section 8.2 — Frontend–backend separation | API contract, OpenAPI | Not implemented |

**Approximate SDD coverage after Epic 03:** roughly 35–40% of all SDD requirements have at least partial implementation. The infrastructure layer (data models, persistence, execution engine, orchestration skeleton) is complete. The intelligence layer (LLM modes), the API layer, and the frontend remain.

---

## 11. Major Risks

**Technical risks:**

- **LLM output quality and reliability (High):** The biggest unknown is how consistently real AI responses will conform to the RFC 6902 patch contract. The OutputValidator stub currently accepts everything. Once real LLM calls are introduced in Epic 04, there may be a significant volume of malformed outputs requiring retries, error handling, or prompt redesign.

- **Context window management (Medium):** The SDD requires that dialog history be limited to the last N turns, and that artifact content always be included in context. As artifacts grow over a long session, the combined context may approach the LLM's token limit. The context engineering logic (Epic 04) must handle this gracefully without losing artifact data.

- **EMMA action catalog dependency (Medium):** The Algorithm Artifact's action type field is currently an open string because the EMMA RPA action catalog schema has not been finalized (SDD open point OP-02). Epic 09 (Specification Mode) cannot be completed until this is resolved. If the resolution comes late, it may delay Epics 09–11.

- **SQLite concurrency (Low for prototype):** The current architecture uses SQLite with WAL mode. For the intended prototype use case (one user, one session at a time), this is sufficient. Multi-user or multi-session scenarios would require a different persistence strategy, but this is out of scope for the prototype.

**Project risks:**

- **Stub-to-real gap for modes (Medium):** Five cognitive modes are stubs. Converting them to production-quality AI modes requires prompt engineering, testing with real LLM responses, and iterative refinement. The effort per mode is difficult to estimate until the first real mode (ExplorationMode in Epic 04) is implemented and measured.

- **Frontend complexity (Low):** The React frontend (Epic 06) is a standard split-pane chat UI. The main complexity is the WebSocket event stream and the artifact pane's real-time update behavior, both of which have well-understood implementation patterns.

---

## 12. Next Steps

**Epic 04 — Exploration Mode & LLM Integration**

Epic 04 replaces the ExplorationMode stub with a real AI-backed implementation that calls the Anthropic API via the Tool Use mechanism. This is the first time the system will produce genuine AI responses and actually populate the Exploration Artifact with content.

Key deliverables for Epic 04:
- `LLMClient` abstraction with `AnthropicClient` implementation (and an Ollama stub for future local-model support)
- Full `ContextAssembler` that loads and trims dialog history from the database
- Full `OutputValidator` that enforces the RFC 6902 patch contract on real LLM outputs
- `ExplorationMode` with real Anthropic Tool Use calls
- Integration tests (with mocked or live API key)

After Epic 04, the system will be capable of conducting a real AI-guided conversation and updating a process artifact — the first true end-to-end user experience, though still only accessible via test scripts rather than a browser.
