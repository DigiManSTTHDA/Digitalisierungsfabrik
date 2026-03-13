# Management Summary — Epic 04: Exploration Mode & LLM Integration

**Date:** 2026-03-13
**Report covers:** Epic 04 implementation, completed 2026-03-13
**Prepared for:** Technically literate stakeholder (non-developer audience)

---

## 1. Epic Summary

Epic 04 replaced every remaining stub in the conversation pipeline with working, AI-backed logic. The system can now, for the first time, **receive a user message and return a genuine AI-generated response** that begins populating the Exploration Artifact with real content — no placeholder text, no hardcoded replies.

To achieve this, the epic added a provider-agnostic LLM communication layer, replaced the stub cognitive mode with a real Exploration Mode that calls the Anthropic Claude API, upgraded the context assembly component to build a fully-populated prompt from the project's current state, and replaced the no-op output validator with a real gate that rejects malformed AI responses before they can corrupt the artifact.

The epic also completed two pieces of technical debt carried over from earlier work: the Exploration Artifact now correctly initialises all eight mandatory slots on the very first turn (previously the slots were left empty), and the number of dialog history turns loaded per request is now driven by configuration rather than being hardcoded at 20.

**Why it matters:** This is the first milestone at which the Digitalisierungsfabrik system does what it was designed to do — have an AI guide a user through a structured process elicitation conversation and record the emerging knowledge into a structured artifact. All infrastructure built in Epics 01–03 is now activated. The pipeline from user message to AI response to persisted artifact state is complete and fully tested.

---

## 2. Implemented Components

### LLMClient Abstraction
**Purpose:** Defines a stable, provider-agnostic interface that every cognitive mode uses to call an AI model. Any module that calls the AI does so through this interface — it never imports a specific provider's SDK directly.
**Files:** `backend/llm/base.py`
**Architecture fit:** Implements the LLM-provider-independence requirement (FR-D-12). The interface defines a single `complete()` method that accepts a system prompt, a list of conversation messages, and tool definitions, and returns a typed `LLMResponse` containing the AI's text reply and any structured write instructions it generated.

### AnthropicClient
**Purpose:** The real, working AI connection. Calls the Anthropic Claude API using the Tool Use protocol, which forces Claude to return structured JSON patch instructions alongside its conversational reply rather than generating freeform text that would be harder to parse reliably.
**Files:** `backend/llm/anthropic_client.py`
**Architecture fit:** Enforces the key architectural decision (from HLA Section 2.5) that all LLM writes must arrive via the Tool Use API. The client logs every request and response to `structlog` when logging is enabled, supporting the observability requirement (SDD 8.1.3). API key and model name are read from the application's settings object, never hardcoded.

### OllamaClient Stub
**Purpose:** Allows the system to be configured with `LLM_PROVIDER=ollama` without a code change. In the current state the client raises a clear error when called, since a full Ollama integration is out of scope for this epic.
**Files:** `backend/llm/ollama_client.py`
**Architecture fit:** Config-selectable via the factory, satisfying the structural requirement of provider switchability (FR-D-12) while deferring the full implementation to a later decision.

### LLM Factory
**Purpose:** A single function that reads `LLM_PROVIDER` from the application configuration and returns the correct client instance. No other module in the system imports `AnthropicClient` or `OllamaClient` directly.
**Files:** `backend/llm/factory.py`
**Architecture fit:** Ensures that swapping AI providers requires only a one-line change to the `.env` configuration file — a binding constraint from SDD 8.1.1.

### APPLY_PATCHES_TOOL
**Purpose:** The JSON schema definition that is sent to the Anthropic API as the description of the `apply_patches` tool. This definition tells Claude exactly what structured output format is expected — it is the machine-readable specification of the Output Contract.
**Files:** `backend/llm/tools.py`
**Architecture fit:** Placed in the LLM layer (not inside any individual mode) so that all four cognitive modes — Exploration, Structuring, Specification, and Validation — can reuse the same tool definition (ADR-004). Changes to the tool schema propagate automatically to all modes.

### ArtifactRouter
**Purpose:** Helper functions that determine which artifact to read or write based on the current project phase, and route accordingly.
**Files:** `backend/core/artifact_router.py`
**Architecture fit:** Extracted from the Orchestrator as a pure refactoring step (resolving DEBT-05 from Epic 03). The Orchestrator file had reached the 300-line project limit and needed to be split before new logic could be added. All 148 tests from Epics 01–03 remained green after the extraction.

### ContextAssembler (upgrade)
**Purpose:** Builds the complete context object that gets handed to a cognitive mode before it calls the AI. The upgraded version now: (1) loads the correct number of dialog history turns from configuration rather than a hardcoded value, (2) attaches the active artifact's template schema so the mode knows which JSON patch paths are valid, and (3) generates a German-language summary of Working Memory state (active phase, active mode, slot fill counts, active tension fields) for injection into the AI system prompt.
**Files:** `backend/core/context_assembler.py`
**Architecture fit:** Implements the context management requirements from SDD Section 6.5.3. The `prompt_context_summary()` helper function is also used directly by ExplorationMode to build the system prompt.

### OutputValidator (real implementation)
**Purpose:** The gate between the AI's response and the Executor. Before any patch is applied to an artifact, the OutputValidator checks that the AI actually used the `apply_patches` tool, that each patch has a valid RFC 6902 operation code, that each patch targets a path that the active artifact's template allows, and that `add` or `replace` patches include the required value field.
**Files:** `backend/core/output_validator.py`
**Architecture fit:** Implements FR-B-09 (write control) and SDD Section 6.5.2 (Output Contract). Replaces the Epic 03 stub that always returned "valid". An empty patch list (AI responds without writing anything) is explicitly permitted — the AI may choose to ask a clarifying question without updating the artifact.

### ExplorationMode (real LLM implementation)
**Purpose:** The first fully-operational cognitive mode. On every turn it builds a German system prompt from the current context, translates the dialog history into the format the Anthropic API expects, calls the AI, and packages the response (conversational reply + patch instructions) as a typed output for the Orchestrator to act on.
**Files:** `backend/modes/exploration.py`, `backend/prompts/exploration.md`
**Architecture fit:** Implements SDD Section 6.6.1. On the first turn of a new project it generates `add` patches for all eight mandatory Exploration slots (FR-B-00, DEBT-01), ensuring the artifact is never left in the undefined empty state that prior epics allowed. The German system prompt is loaded from a Markdown file, keeping prompts out of Python code and easy to edit without touching logic.

### Event Models
**Purpose:** Six typed data structures for every kind of real-time update the system will emit to the browser once the WebSocket layer is built in Epic 05: a streaming token event, a turn-complete event, an artifact update event, a progress update event, a debug state event, and an error event.
**Files:** `backend/core/events.py`
**Architecture fit:** Placed in the Core layer rather than the API layer (ADR-003), because these events are emitted by the Orchestrator — a framework-agnostic component — and must not create a dependency pointing upward toward FastAPI. Epic 05 imports these models without any rework.

### Integration Tests (full turn through Orchestrator)
**Purpose:** End-to-end tests that verify the complete pipeline — from `Orchestrator.process_turn()` call through ContextAssembler, ExplorationMode (with a mock AI), OutputValidator, Executor, and Repository — using an in-memory SQLite database and no live API calls.
**Files:** `backend/tests/test_exploration_mode.py`
**Architecture fit:** Four scenarios are covered: first turn initialises all eight mandatory slots; a patch from the AI is applied and survives a reload from the database; user and assistant turns are written to dialog history; and the OutputValidator correctly blocks a patch targeting a non-existent field and leaves the artifact unchanged.

---

## 3. SDD Progress

### Implemented in Epic 04

| FR Group | Requirement | Status |
|---|---|---|
| FR-A-02 | Tool Use API for LLM communication | Implemented — enforced in AnthropicClient and ExplorationMode |
| FR-A-08 | System language German | Implemented — `prompts/exploration.md` is in German; mode instructs AI to respond in German |
| FR-B-00 | Exploration Artifact mandatory slots initialised | Implemented — 8 slots created on first turn |
| FR-B-09 | Write control via RFC 6902 OutputValidator | Implemented — real validator replaces stub |
| FR-D-05 | Active context management (ContextAssembler) | Implemented — dialog history N from config, artifact template, WM summary |
| FR-D-07 | OutputValidator as Orchestrator gate | Implemented — invalid patches blocked before Executor |
| FR-D-12 | LLM provider configurability | Implemented — factory reads config, no hardcoding |
| FR-E-07 | Dialog history persisted and loaded per turn | Implemented — both directions verified by integration test |

### Partially Implemented

| FR Group | Requirement | What is partial |
|---|---|---|
| FR-D-02 / FR-D-08 / FR-D-09 | Moderator, phase transitions, phase sequence | ExplorationMode reports `in_progress` / `nearing_completion` but `phase_complete` and the Moderator handoff are deferred to Epic 07 |
| FR-D-06 | Token monitoring | Not yet — requires Epic 05+ infrastructure |
| FR-F-01 / FR-F-02 | Progress and debug display in UI | Event models are ready; actual WebSocket delivery deferred to Epic 05 |

### Remaining (not yet started)

| FR Group | Requirement |
|---|---|
| FR-A-01 / FR-A-03 | Contextual follow-up questions, identification of missing information (depends on real mode behaviour across multiple turns) |
| FR-A-05 | External raw data (EMMA Recorder event logs, documents, images) |
| FR-A-06 / FR-A-07 | Automatability assessment and warnings |
| FR-B-01 / FR-B-02 | Structuring and Algorithm artifacts |
| FR-B-03 / FR-B-04 / FR-B-05 | Cross-artifact referential integrity and invalidation |
| FR-B-06 / FR-B-07 / FR-B-10 | Artifact visibility, download/export/import, version restore |
| FR-C-xx | Validation and consistency (9 requirements) |
| FR-D-02 / FR-D-03 | Moderator mode, Panic Button |
| FR-F-xx | UI and Observability in browser (5 requirements) |
| FR-G-xx | Project management in UI (4 requirements) |

---

## 4. Test Status

**Total tests: 190 — all passing.**

| Test file | Tests | What is guaranteed |
|---|---|---|
| `test_llm_client.py` | 10 | AnthropicClient extracts conversational reply and patch input correctly; raises on missing tool use; propagates real Anthropic SDK errors; logs request and response when enabled; factory returns the correct client type for each provider string |
| `test_output_validator.py` | 9 | Valid patches pass; invalid RFC 6902 operation codes are rejected; patch paths not in the artifact template are rejected; `add`/`replace` patches missing a value are rejected; empty patch list is accepted; new slot IDs are accepted; unknown top-level paths are rejected |
| `test_context_assembler.py` | 8 | `dialog_history_n` from settings is respected (not the old hardcoded 20); the last N turns are returned, not the first N; `artifact_template` matches the active phase; `prompt_context_summary()` contains the required fields |
| `test_exploration_mode.py` | 6 | First turn initialises all 8 mandatory slots with correct IDs and German titles; second turn does not re-add existing slots; patched artifact value survives a reload from the database; both user and assistant turns are written to dialog history; invalid patch paths cause `TurnOutput.error` to be set and leave the artifact unchanged; `nearing_completion` status is set when all slots are filled |
| `test_events.py` | 7 | All 6 event models serialise and deserialise correctly; the union type rejects unknown event discriminator values |
| Earlier epics (01–03) | 148 | Data models, persistence, execution engine, orchestrator cycle — all still green |

These tests together guarantee that: no AI response can write to an artifact without passing through the OutputValidator; the dialog history loads in the correct chronological order; all mandatory exploration slots exist after the first turn; and the full turn cycle produces a persistent, reloadable project state.

---

## 5. Problems Encountered

Two bugs were found and fixed during the implementation and audit phases of this epic.

### Bug 1 — Dialog History Returned Wrong Turns (ORDER BY defect)
The SQL query that loads the last N dialog turns from the database was using `ORDER BY turn_id ASC LIMIT N`, which returns the **first** N turns ever recorded for the project rather than the **most recent** N. In a fresh project with few turns this difference is invisible, but in a longer conversation the AI would have received outdated context instead of the current conversation.

The bug was discovered by a test specifically designed to detect it: five turns were written to the database, the last three were requested, and the test asserted that the returned entries were turns 3–5 (not turns 1–3).

**Fix:** The query was rewritten using a descending subquery to select the last N rows, with an outer query re-sorting them into ascending chronological order for consumption by the mode.

### Bug 2 — Settings Not Passed to ContextAssembler (hardcoded history length)
The Story 04-04 tests verified that `build_context()` correctly reads `dialog_history_n` from a `Settings` object when called directly. However, the Orchestrator was calling `build_context()` without passing the `settings` parameter, so the function silently fell back to the hardcoded default of 20 in all production code paths, ignoring whatever value was set in `.env`.

**Fix:** The `Orchestrator` constructor was extended to accept a `settings: Settings | None = None` parameter, and this settings object is forwarded to every `build_context()` call. Existing tests that construct an Orchestrator without settings continue to work and receive the hardcoded default — backward-compatible. Epic 05 must inject settings when wiring the Orchestrator to the FastAPI application to make the configuration effective end-to-end.

---

## 6. Remaining Issues / Technical Debt

### OllamaClient Is a Non-Functional Stub
The `OllamaClient` is registered in the factory and is config-selectable, but calling it raises `NotImplementedError`. Setting `LLM_PROVIDER=ollama` in the environment will cause the system to fail on the first turn. This is intentional for the prototype at this stage — a full Ollama integration requires decisions about the local model's Tool Use capability that have not yet been made.

### No Live API Test Exists
All 190 tests use a mocked AI client. There is no automated test that makes a real call to the Anthropic API. This means it is theoretically possible for an incompatibility between the test mock and the real API behaviour to go undetected until the system is run manually. A small integration smoke test against the live API (skipped unless an `ANTHROPIC_API_KEY` is present in the environment) would close this gap in a future epic.

### Settings Must Be Injected in Epic 05
As noted in Bug 2 above, the `dialog_history_n` configuration value is only effective if the FastAPI application injects its `Settings` object into the `Orchestrator` constructor. Epic 05 must include this wiring — otherwise the system always uses 20 turns regardless of configuration.

### Four Cognitive Modes Not Yet Implemented
The modes for Structuring (Epic 08), Specification (Epic 09), Validation (Epic 10), and the Moderator (Epic 07) are still stubs. The full AI-guided process flow requires all four modes. These are the largest remaining implementation effort.

---

## 7. System Integration

The end-to-end flow for a single conversation turn in the current state of the system is:

1. **User input** arrives as a text string (in tests: passed directly to `Orchestrator.process_turn()`; in future epics: received via WebSocket).
2. **Orchestrator** loads the project from SQLite, determines that the active mode is `ExplorationMode`, and hands off to `ContextAssembler`.
3. **ContextAssembler** loads the last N dialog turns from the database (N from `Settings.dialog_history_n`), retrieves the active artifact's template schema, calculates a Working Memory summary, and returns a typed `ModeContext` object.
4. **ExplorationMode** receives the context, builds a German system prompt (loaded from `backend/prompts/exploration.md` and populated with the Working Memory summary and slot completeness state), translates the dialog history into the Anthropic messages format, appends the user's message, and calls `AnthropicClient.complete()`.
5. **AnthropicClient** sends the system prompt, messages, and the `apply_patches` tool schema to the Anthropic Claude API with `tool_choice` enforced to `apply_patches`. It extracts the text reply as `nutzeraeusserung` and the tool input dict (containing the patch list) as `tool_input`, and returns a typed `LLMResponse`.
6. **ExplorationMode** packages the response into a `ModeOutput` and returns it to the Orchestrator.
7. **OutputValidator** checks the patches: RFC 6902 syntax, required fields, and that every patch path is permitted by the artifact template. If any check fails, the Orchestrator sets an error in `TurnOutput` and stops — the artifact is not touched.
8. **Executor** (from Epic 02) applies each valid patch to the artifact using RFC 6902, with snapshot-and-rollback protection.
9. **ProjectRepository** saves the updated project state — artifacts, Working Memory, versioning, and dialog history — to SQLite in a single atomic transaction.
10. **Dialog history** entries for the user turn and the AI reply are written to the `dialog_history` table.
11. **TurnOutput** is returned to the caller, carrying the AI's conversational reply, the updated artifact state, and any error information.

---

## 8. Project Progress

The system has completed its most critical capability milestone: a real, AI-guided conversation that writes structured content to an artifact. The backend core is now functionally complete for the Exploration phase.

**What works today:**
- A new project can be created, saved, and reloaded.
- Sending a message triggers a real AI call (when `LLM_PROVIDER=anthropic` is configured) that returns a German-language conversational reply and structured JSON patch instructions.
- The mandatory Exploration slots are initialised automatically on the first turn.
- The AI cannot write to an artifact path that is not in the template schema.
- Every turn is persisted atomically to SQLite; restarting the application restores the full project state including dialog history.

**What still needs to be built:**
- The HTTP and WebSocket API layer to expose this logic to a browser (Epic 05).
- A React frontend so a user can actually open the system in a browser (Epic 06).
- The Moderator mode and phase transition protocol (Epic 07).
- The remaining three cognitive modes: Structuring (Epic 08), Specification (Epic 09), Validation (Epic 10).
- End-to-end stabilisation and artifact export (Epic 11).

Estimated overall progress toward the complete prototype: **approximately 35%** of the total implementation work is done. The foundational and backend-core work (Epics 00–04) accounts for roughly this fraction of the epic plan. The remaining work is substantial — particularly the four mode implementations and the frontend — but the architecture is sound and each remaining epic builds on a verified foundation.

---

## 9. Project Status Overview

| Epic | Title | Status |
|---|---|---|
| 00 | Project Foundation & Dev Setup | Completed |
| 01 | Data Models & Persistence | Completed |
| 02 | Execution Engine (Executor + JSON Patch) | Completed |
| 03 | Orchestrator & Working Memory | Completed |
| **04** | **Exploration Mode & LLM Integration** | **Completed** |
| 05 | Backend API (REST + WebSocket) | Remaining |
| 06 | React Frontend (Chat + Artifact pane) | Remaining |
| 07 | Moderator & Phase Transitions | Remaining |
| 08 | Structuring Mode | Remaining |
| 09 | Specification Mode | Remaining |
| 10 | Validation & Correction Loop | Remaining |
| 11 | End-to-End Stabilisation & Export | Remaining |

---

## 10. SDD Coverage

### Implemented (fully or substantially)

| SDD Area | Coverage |
|---|---|
| Section 5.3 — Exploration Artifact (8 mandatory slots) | Full — slots defined, initialised on first turn, template schema enforced |
| Section 5.7 — RFC 6902 Executor Pipeline | Full — from Epic 02; OutputValidator gate now active |
| Section 5.8 — Template Schema | Full — used by OutputValidator to validate every patch path |
| Section 6.3 — Orchestrator 11-Step Cycle | Full — all steps operational; mode stub for Moderator/Structuring/Specification/Validation still in place |
| Section 6.4 — Working Memory | Full — all fields maintained, updated after every turn |
| Section 6.5 — Context Engineering | Substantially implemented — dialog history N from config, artifact template, WM summary injected into system prompt |
| Section 6.5.2 — Output Contract | Full — OutputValidator enforces tool name, RFC 6902 syntax, and template path allowlist |
| Section 6.6.1 — Exploration Mode | Full — real LLM-backed implementation with German system prompt |
| Section 7.3 — Persistence Model (ACID) | Full — atomic writes across artifacts, WM, versioning, dialog history |

### Partially Implemented

| SDD Area | What is partial |
|---|---|
| Section 6.1 — System Phases | Phase sequence defined; `phase_complete` flag and Moderator handoff not yet active |
| Section 6.5.3 — Context components | All fields wired except raw data file injection (FR-A-05, deferred) |
| Section 6.7 — Progress Model | `in_progress` / `nearing_completion` working; `phase_complete` and Moderator connection deferred to Epic 07 |

### Not Yet Started

| SDD Area | Epic |
|---|---|
| Section 6.6.2 — Structuring Mode | 08 |
| Section 6.6.3 — Specification Mode | 09 |
| Section 6.6.4 — Validation Mode | 10 |
| Section 6.6.5 — Moderator | 07 |
| Section 6.1.2 / 6.1.3 — Phase transition and correction loop | 07 / 10 |
| Section 2.x / Section 3.x — UI and user interaction | 06 |
| Section 7.1 — Raw data integration | Deferred |

---

## 11. Major Risks

### Architecture Complexity
The system has a layered architecture with strict separation between the AI layer, the orchestration layer, the execution layer, and the persistence layer. Every turn passes through six or more components. This separation is deliberate and correct, but it means that bugs at any layer interface can be difficult to trace without good test coverage at each layer. The current test suite mitigates this well, but the risk increases as the remaining four mode implementations are added.

### Remaining Mode Implementations
Three of the four remaining cognitive modes (Structuring, Specification, Validation) each require their own system prompts, their own artifact templates, and their own phase-completion logic. Each is comparable in scope to the ExplorationMode work in this epic. The Moderator mode additionally requires phase transition protocols and user confirmation flows. These four epics represent the bulk of the remaining backend work.

### OllamaClient Not Functional
If the project sponsor or a stakeholder wishes to run the prototype without an internet connection or without an Anthropic API key, the system will fail at the first AI call. Completing the Ollama integration would require a separate assessment of whether the chosen local model supports the Tool Use protocol in a way compatible with the current architecture.

### API Cost During Development and Testing
All end-to-end tests use mocked AI clients and incur no cost. However, manual testing and any live demonstration of the system consumes Anthropic API credits. The model configured in `.env` (`claude-opus-4-6` by default) is among the most capable and most expensive Anthropic models. Switching to a smaller model for development testing is possible via configuration and is recommended.

### No Automated Live API Smoke Test
As noted in Section 6, there is currently no automated test that validates behaviour against the real Anthropic API. A prompt change or API version update could break the system without triggering any test failure.

---

## 12. Next Steps

**Epic 05 — Backend API (REST + WebSocket)** wraps the Orchestrator in a FastAPI application and exposes it to external callers. The key deliverables are:

- REST endpoints for project creation, retrieval, and listing (`POST /api/projects`, `GET /api/projects`, `GET /api/projects/{id}`)
- A WebSocket endpoint (`WS /ws/session/{project_id}`) that accepts user messages and streams back the AI reply as real-time token events, followed by artifact update events, a progress update, and a turn-complete event — using the typed event models already defined in Epic 04
- Settings injection into the Orchestrator constructor, activating the `dialog_history_n` configuration that Bug 2 in this epic exposed as previously inert
- Automated API tests using FastAPI's test client with an in-memory SQLite database and a mocked LLM

After Epic 05, the system's backend will be fully functional and demonstrable without a frontend — any HTTP/WebSocket client (curl, Postman, a Python test script) can drive a complete Exploration phase conversation and receive AI-generated artifact updates in real time. This makes Epic 05 a significant verification milestone before the React frontend is built in Epic 06.
