# Epic 05 — Management Summary: Backend API (REST + WebSocket)

**Date:** 2026-03-13
**Status:** Complete
**Tests:** 225 passing (33 new in this epic)

---

## 1. Epic Summary

Epic 05 made the entire backend accessible over the network. Until now, all the system's intelligence — the Orchestrator, the Exploration mode, the LLM integration, the artifact persistence — could only be used programmatically by calling Python functions directly. This epic wraps everything in a web API that any client (browser, mobile app, testing tool) can talk to.

Concretely, this means:

- A **REST API** for project management: creating projects, listing them, loading project details, viewing artifacts, downloading data, managing artifact versions, and importing/exporting.
- A **WebSocket endpoint** for real-time conversation: the user sends a message, the system processes it through the Orchestrator, and streams back the AI's response along with live artifact updates, progress indicators, and debug information.
- A **frozen API contract** (OpenAPI specification) that the frontend team can build against without needing the backend running.

This is the last backend-only epic. From here, the system is ready for a user interface.

---

## 2. Implemented Components

### REST API Layer (`backend/api/router.py`)
**Purpose:** Handles all HTTP requests for project management and artifact operations.
**10 endpoints** matching the architecture specification exactly:

| Endpoint | What it does |
|---|---|
| `POST /api/projects` | Create a new project |
| `GET /api/projects` | List all projects |
| `GET /api/projects/{id}` | Load project details |
| `GET /api/projects/{id}/artifacts` | View current artifacts |
| `GET /api/projects/{id}/download` | Download all artifacts as JSON |
| `POST /api/projects/{id}/complete` | Mark project as finished |
| `GET /api/projects/{id}/artifacts/{type}/versions` | Browse artifact version history |
| `POST /api/projects/{id}/artifacts/{type}/restore` | Restore an earlier artifact version |
| `POST /api/projects/{id}/import` | Import an externally modified artifact |
| `GET /health` | Server health check |

### WebSocket Handler (`backend/api/websocket.py`)
**Purpose:** Handles real-time bidirectional communication for the conversation flow.
The client connects, sends a user message, and receives a stream of events: the AI's response, updated artifacts, progress updates, and debug state. Also handles the panic button (placeholder for Epic 07's Moderator).

### API Schemas (`backend/api/schemas.py`)
**Purpose:** Defines the exact shape of every request and response. These Pydantic models drive the automatic OpenAPI specification, ensuring that the API contract is always consistent with the actual implementation.

### OpenAPI Contract (`api-contract/openapi.json` + `frontend/src/generated/api.d.ts`)
**Purpose:** The frozen API specification and auto-generated TypeScript types. The frontend team can now build type-safe API calls without running the backend.

---

## 3. SDD Progress

### Requirements fulfilled by this Epic

| SDD Requirement | Status |
|---|---|
| FR-G-01: Project creation | Fully implemented |
| FR-G-02: Project listing and selection | Fully implemented |
| FR-G-04: Project completion | Partially implemented (status change works; pre-completion validation deferred to Epic 10) |
| FR-B-06: Artifact visibility | Fully implemented (API layer; UI in Epic 06) |
| FR-B-07: Download/Export/Import | JSON download implemented; Markdown download deferred; import with validation implemented |
| FR-B-10: Version restore | Fully implemented (version history, restore, new version creation) |
| FR-C-04: Import validation | Schema validation implemented; referential integrity checks deferred to later epics |
| FR-E-02: Load saved projects | Fully implemented via REST API |
| FR-E-04: Error handling | WebSocket error events implemented |
| FR-D-03: Panic button | Placeholder — sends informational message; actual Moderator integration in Epic 07 |
| FR-F-01: Progress display | ProgressUpdateEvent sent after each turn |
| FR-F-02: Debug mode | DebugUpdateEvent sent with working memory and flags |
| SDD 7.2.1: Project metadata | All 8 fields implemented in API responses |

### What remains unimplemented

- **Frontend UI** (Epic 06) — the API exists, but there's no browser interface yet
- **Moderator & phase transitions** (Epic 07) — panic button is wired but the Moderator mode doesn't exist
- **Structuring, Specification, Validation modes** (Epics 08–10)
- **Markdown artifact rendering** for download (needs `renderer.py`)
- **Token-level streaming** — responses arrive complete, not token-by-token

---

## 4. Test Status

**225 tests passing**, all green. This includes:

- **31 new API/WebSocket tests** added in this epic
- **2 new repository method tests** for version operations
- **192 pre-existing tests** from Epics 01–04 — all still passing (no regressions)

Every endpoint is tested with both success and failure scenarios. The test validation phase discovered and closed 9 coverage gaps, including missing negative tests and weak assertions.

The tests guarantee:
- Projects can be created, listed, loaded, and completed correctly
- Artifacts are returned in their current state and can be versioned/restored/imported
- Invalid inputs are rejected with appropriate error codes
- The WebSocket correctly routes messages through the Orchestrator
- Error conditions are handled gracefully without corrupting system state

---

## 4a. Key Decisions (ADRs)

No new ADRs were written during Epic 05. All decisions in this epic fell within the scope of existing architecture decisions:

- **ADR-001 (OpenAPI Contract):** Established the API contract workflow in Epic 01. Epic 05 is the first epic to fully exercise it — exporting the spec, generating TypeScript types, and committing both together.
- **ADR-003 (Event Models in core/):** The WebSocket event models created in Epic 04 were used directly by the WebSocket handler without modification.
- **ADR-004 (Tool Schema in llm/tools.py):** The LLM tool configuration remained stable through Epic 05.

**Key implementation decisions (not requiring ADRs):**
1. **Token streaming deferred:** The Orchestrator returns complete responses. Token-by-token streaming would require significant architectural changes. The infrastructure is ready (ChatTokenEvent model exists) but not wired yet.
2. **German API parameter names:** URL parameters use German names (`struktur`, `algorithmus`) consistent with the SDD, mapped internally to English DB column names.

---

## 5. Problems Encountered

1. **File size limit pressure:** Two files (`router.py` at 336 lines, `project_repository.py` at 327 lines) exceeded the 300-line limit after adding versioning endpoints. Resolved by compacting docstrings, removing decorative comments, and using lookup dictionaries instead of if-chains.

2. **DateTime serialization in WebSocket:** The `WorkingMemory` model contains `datetime` fields which aren't JSON-serializable by default. The WebSocket handler needed to use Pydantic's `model_dump(mode="json")` instead of `model_dump()` to produce serializable output.

3. **mypy type strictness:** 11 new mypy issues required fixes — `Any` return types from SQLite row access, dict variance with mode types, and stale type-ignore comments. All resolved during the test-run phase.

4. **Frontend formatting drift:** Pre-existing frontend files had accumulated Prettier formatting differences. Resolved by running Prettier across all frontend source files.

---

## 6. Remaining Issues

1. **Pre-existing mypy errors:** 7 mypy errors exist in `scripts/interactive_explorer.py` and `tests/test_exploration_mode.py` from earlier epics. These are not regressions from Epic 05 but should be cleaned up.

2. **Markdown download not available:** The `GET /download` endpoint returns JSON only. The Markdown renderer (`artifacts/renderer.py`) doesn't exist yet. This is a known limitation documented in the epic.

3. **No token-level streaming:** AI responses arrive as a single complete message. For a smooth user experience, responses should stream token-by-token. This requires extending the Orchestrator interface.

4. **Panic button is a placeholder:** The WebSocket accepts panic messages but responds with an informational message instead of activating the Moderator (which doesn't exist yet — Epic 07).

---

## 7. System Integration

The system now has a complete data flow from HTTP client to persisted artifacts:

```
Browser / HTTP Client
        |
   [REST API]  ←→  ProjectRepository  ←→  SQLite
        |
   [WebSocket]
        |
        ↓
  Orchestrator (11-step cycle)
        |
        ↓
  ExplorationMode  →  LLM (Anthropic Claude)
        |
        ↓
  OutputValidator  →  Executor  →  Artifacts
        |
        ↓
  Persistence (atomic SQLite transaction)
        |
        ↓
  WebSocket Events → Client
  (chat_done, artifact_update, progress_update, debug_update)
```

The API layer is a thin wrapper. It does not contain business logic — it translates HTTP/WebSocket requests into Orchestrator calls and formats the responses. The Orchestrator remains completely framework-agnostic and knows nothing about FastAPI or WebSocket.

---

## 8. Project Progress

### Working capabilities
- Create and manage multiple projects
- Conduct AI-guided exploration conversations via API
- View and version artifacts
- Download project data
- All operations persisted atomically to SQLite

### Still needed for a complete prototype
- **Browser UI** (Epic 06) — the next immediate step
- **Phase transitions** via Moderator (Epic 07)
- **Three additional cognitive modes:** Structuring, Specification, Validation (Epics 08–10)
- **End-to-end stabilization** (Epic 11)

### Progress estimate
The backend is now **functionally complete for the Exploration phase**. A developer can exercise the full flow via curl or Postman. The next step adds a user-facing interface.

---

## 9. Project Status Overview

### Completed Epics

| Epic | Title | Tests |
|---|---|---|
| 00 | Project Foundation | — |
| 01 | Data Models & Persistence | — |
| 02 | Execution Engine | (included in 148 base) |
| 03 | Orchestrator & Working Memory | 148 |
| 04 | Exploration Mode & LLM Integration | 192 |
| **05** | **Backend API (REST + WebSocket)** | **225** |

### Current Epic
**Epic 05 — Backend API** is now complete.

### Remaining Epics

| Epic | Title | What it adds |
|---|---|---|
| 06 | React Frontend | Browser-based user interface |
| 07 | Moderator & Phase Transitions | Phase switching, panic button handling |
| 08 | Structuring Mode | BPMN-level process structuring |
| 09 | Specification Mode | Detailed algorithm specification |
| 10 | Validation & Correction | Quality checks and correction loop |
| 11 | End-to-End Stabilization | Full flow from Exploration to Validation |

---

## 10. SDD Coverage

| SDD Section | Coverage | Notes |
|---|---|---|
| 1. Systemübersicht | Implemented | System architecture established |
| 2. Benutzerinteraktion & UI | Partially | API layer ready; UI in Epic 06 |
| 4. Gruppe A (Dialog) | FR-A-01, FR-A-08 | Exploration dialog works via API |
| 4. Gruppe B (Artefakte) | FR-B-00, B-06, B-07, B-09, B-10, B-11 | Core artifact management complete |
| 4. Gruppe C (Validierung) | FR-C-04 (basic) | Schema validation for import; full validation in Epic 10 |
| 4. Gruppe D (Orchestrierung) | FR-D-01, D-03 (partial), D-05, D-07 | Orchestrator + Exploration mode; Moderator in Epic 07 |
| 4. Gruppe E (Persistenz) | FR-E-01, E-02, E-04, E-07 | Atomic persistence, loading, error handling, dialog history |
| 4. Gruppe F (UI/Observability) | FR-F-01, F-02 (events only) | Events defined; UI display in Epic 06 |
| 4. Gruppe G (Projektverwaltung) | FR-G-01, G-02, G-04 (partial) | Project CRUD via REST API |
| 5. Prozessartefakte | Implemented | Models, slots, versioning, completeness |
| 6. Systemsteuerung | Partially | Orchestrator + Exploration; phases 2–4 pending |
| 7. Persistenz | Implemented | SQLite ACID, project model, dialog history |
| 8. Qualitätsanforderungen | Partially | Maintainability, reliability; performance/scaling not yet relevant |

**Approximate SDD coverage: ~50%** of functional requirements are now implemented or have the infrastructure in place. The remaining 50% centers on the additional cognitive modes (Structuring, Specification, Validation), the Moderator for phase transitions, and the user interface.

---

## 11. Major Risks

1. **Frontend complexity:** Epic 06 introduces React, TypeScript, WebSocket handling, and a split-pane UI layout. This is a significant technology shift from the Python backend work done so far.

2. **Token streaming gap:** The current response model sends complete messages. Users may perceive delays waiting for the full LLM response. Implementing streaming requires changes across LLM client, Orchestrator, and WebSocket handler.

3. **Mode integration:** Epics 07–10 each add a new cognitive mode. These modes must integrate with the existing Orchestrator without breaking prior modes. The risk grows as more modes are added.

4. **SDD completeness in later phases:** The Structuring and Specification phases reference detailed BPMN-level concepts and EMMA RPA compatibility. These are more complex than the Exploration phase and may surface SDD ambiguities.

---

## 12. Next Steps

**Epic 06 — React Frontend** will build the browser-based user interface. After this epic, a user can:

1. Open the app in a browser
2. Create a new project
3. Have a conversation with the AI in a chat pane
4. Watch the Exploration Artifact grow in real time in the artifact pane
5. Inspect the system's internal state in the debug panel

This transforms the system from a developer-testable API into a user-facing application — the first time a non-technical user can interact with the Digitalisierungsfabrik prototype.
