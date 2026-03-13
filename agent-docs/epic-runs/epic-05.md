# Epic 05 Run Log – Backend API (REST + WebSocket)

**Start:** 2026-03-13
**Goal:** A running FastAPI server that exposes REST endpoints for project CRUD and a WebSocket endpoint for real-time conversation, all testable without a frontend.

---

## STEP 0 — Epic Identified

Epic: `epic-05-backend-api.md`
Status: Stories not yet defined.
Dependencies: Epic 04 ✅ complete (190 tests green, all DoD checkboxes marked).

---

## STEP 1 — Story Generation

**Date:** 2026-03-13

### Stories Generated

| ID | Title | Purpose |
|---|---|---|
| 05-01 | API Request/Response Schemas | Define all Pydantic request/response models in `backend/api/schemas.py` to drive the OpenAPI spec. Covers all SDD 7.2.1 project metadata fields. No endpoint logic. |
| 05-02 | FastAPI App Setup + Project CRUD REST Endpoints | Wire `main.py` with router, add CORS, create `backend/api/router.py` with POST /api/projects, GET /api/projects, GET /api/projects/{id}. Core project management. |
| 05-03 | Artifact & Project Lifecycle REST Endpoints | Add GET /api/projects/{id}/artifacts, GET /api/projects/{id}/download, POST /api/projects/{id}/complete. Covers artifact viewing, download, and project completion. |
| 05-04 | Artifact Versioning & Import REST Endpoints | Add GET versions, POST restore, POST import endpoints. Requires new `ProjectRepository` methods for version listing and loading. |
| 05-05 | WebSocket Turn Handler | Create `backend/api/websocket.py` with WS /ws/session/{project_id}. Handles turn and panic messages, streams events via Epic 04 event models. |
| 05-06 | OpenAPI Contract Freeze + Frontend Type Generation | Export openapi.json, regenerate TypeScript types, verify frontend compiles. Freezes the API contract for Epic 06. |

### Libraries Identified

No new dependencies required. All libraries are already in `requirements.txt`:
- `fastapi` (≥ 0.111): REST endpoints, WebSocket, CORS middleware, dependency injection
- `uvicorn`: ASGI server (already in requirements)
- `pydantic` (≥ 2.6): Request/response schema models
- `httpx`: Used in tests via FastAPI's `TestClient`

### Key Decisions

1. **HLA path correction:** Epic doc listed `backend/api/routes.py` but HLA Section 6 defines `backend/api/router.py`. Fixed to use HLA path.
2. **Token streaming deferred:** `Orchestrator.process_turn()` returns complete `TurnOutput`, not a generator. The WebSocket handler sends `chat_done` (complete response) rather than `chat_token` (streaming). Token-level streaming requires Orchestrator interface changes — deferred to future epic.
3. **Markdown download deferred:** `GET /download` returns JSON only. `artifacts/renderer.py` (Markdown rendering) is not yet implemented. JSON format satisfies FR-B-07 for now.
4. **Panic button placeholder:** WebSocket panic handler returns informational message that Moderator is implemented in Epic 07. The escalation flag wiring will be added then.

### Escalation Points

1. **ESCALATION-01 — Token streaming scope:** The HLA defines `chat_token` as a WebSocket event for LLM streaming tokens. The current Orchestrator returns complete `TurnOutput` — token streaming requires either making `process_turn` an async generator or adding a callback mechanism. This is noted as deferred in the story (Streaming Note in epic doc). No user decision needed — the `ChatTokenEvent` model exists and the WebSocket handler is structured to support it when the Orchestrator evolves.

2. **ESCALATION-02 — `{typ}` path parameter naming:** HLA uses `{typ}` in the URL path. Artifact types in the database are `exploration`, `structure`, `algorithm`. SDD uses German names (Explorations-, Struktur-, Algorithmusartefakt). Story 05-04 defines a mapping: URL `struktur` → DB `structure`, URL `algorithmus` → DB `algorithm`, URL `exploration` → DB `exploration`. This maintains German naming in the API (consistent with SDD) while preserving existing DB conventions.

---

## STEP 2 — Validation

**Date:** 2026-03-13
**Validator:** Claude Opus 4.6 (strict specification validator)
**Documents read:** AGENTS.md (full), SDD lines 6–82 (ToC) + Section 4 (FR lines 256–569) + Section 7.2 (Projektmodell lines 1381–1430), HLA Section 6 (Projektstruktur lines 532–640) + HLA Section 3.1–3.2 (Frontend + Backend-API lines 145–210), epic-05-backend-api.md (full).

### EPIC VALIDATION REPORT

#### 1. Structure Issues

None. All required sections present. Testable increment is runnable. All 6 stories have user story, acceptance criteria, and DoD.

#### 2. SDD Compliance Issues

**ISSUE-01 — `ArtifactImportRequest` missing `typ` field (FIXED)**
Import endpoint needed to know which artifact type to validate against. Added `typ: Literal["exploration", "struktur", "algorithmus"]` field.

**ISSUE-02 — FR-B-10 AC#4 Completeness-State reconstruction missing (FIXED)**
Added explicit AC requiring `CompletenessCalculator` invocation after version restore.

**ISSUE-03 — FR-G-04 scope limitation noted (FIXED)**
Pre-completion validation checks deferred (Validation mode is Epic 10). Documented in story.

All FR references verified: FR-G-01, FR-G-02, FR-G-04, FR-B-06, FR-B-07, FR-B-10, FR-C-04, FR-E-02, FR-E-04, FR-D-01, FR-D-03, FR-F-01, FR-F-02. SDD 7.2.1 field coverage complete (all 8 fields).

#### 3. Architecture Issues

All file paths within HLA-defined directories. `backend/api/schemas.py` mandated by AGENTS.md. No invented directories. PASS.

#### 4. Test Issues

Every logic-introducing story (05-02 through 05-05) defines tests with positive and negative cases. Stories 05-01 and 05-06 are non-logic. PASS.

#### 5. DoD Issues

All 4 backend DoD commands present in every story. Structural checkboxes present. Story 05-06 includes frontend `npm run typecheck`. PASS.

### EPIC VALID: YES

**Corrections applied:** (1) `ArtifactImportRequest` `typ` field, (2) FR-B-10 Completeness-State reconstruction, (3) FR-G-04 scope limitation documented. No open escalation points.

---

## STEP 2.5 — Escalation Checkpoint

**Date:** 2026-03-13

All stories scanned for genuine ambiguities:

1. **SDD clear enough?** YES — all stories map to specific HLA 3.2 endpoints and FR requirements.
2. **Design decisions needing ADRs?** NO — `schemas.py` mandated by AGENTS.md, `{typ}` mapping is internal detail.
3. **New dependencies?** NO — all libraries already in `requirements.txt`.

**No escalations needed. Proceeding to implementation.**

---

## STEP 3 — Implementation

**Date:** 2026-03-13
**Implementer:** Claude Opus 4.6

### Stories Implemented

| ID | Title | Commit | Tests Added |
|---|---|---|---|
| 05-01 | API Request/Response Schemas | 3c3fca3 | 0 (declarative models, no logic) |
| 05-02 | FastAPI App Setup + Project CRUD REST | 6c14ff1 | 6 (test_api.py) |
| 05-03 | Artifact & Project Lifecycle REST | 77594d8 | 6 (test_api.py) |
| 05-04 | Artifact Versioning & Import REST | 7f25f0d | 8 (6 API + 2 repo) |
| 05-05 | WebSocket Turn Handler | 02c567f | 6 (test_websocket.py) |
| 05-06 | OpenAPI Contract Freeze | a9fe4ef | 0 (build artifact) |

**Total: 218 tests passing (192 existing + 26 new)**

### Modules Created

| File | Purpose |
|---|---|
| `backend/api/schemas.py` | All Pydantic request/response models for REST endpoints |
| `backend/api/router.py` | All 9 REST endpoints (HLA Section 6 path) |
| `backend/api/websocket.py` | WebSocket handler for turn processing and event streaming |
| `backend/tests/test_api.py` | REST endpoint tests (18 tests) |
| `backend/tests/test_websocket.py` | WebSocket endpoint tests (6 tests) |

### Modules Modified

| File | Changes |
|---|---|
| `backend/main.py` | Added CORS middleware, router mount, WebSocket route registration |
| `backend/persistence/project_repository.py` | Added `list_artifact_versions()` and `load_artifact_version()` methods |
| `backend/tests/test_persistence.py` | Added 2 tests for new repository methods |
| `api-contract/openapi.json` | Updated with real OpenAPI spec (10 endpoints) |
| `frontend/src/generated/api.d.ts` | Regenerated TypeScript types |

### Architecture Components

- **REST layer:** 9 endpoints matching HLA 3.2 exactly
- **WebSocket layer:** WS /ws/session/{project_id} with event streaming
- **CORS:** localhost:5173 allowed for frontend dev server
- **Dependency injection:** FastAPI Depends() for ProjectRepository
- **OpenAPI contract:** Frozen and committed per ADR-001

### Libraries Used

No new dependencies. All from existing tech stack:
- `fastapi` (CORSMiddleware, APIRouter, WebSocket, Depends, HTTPException)
- `pydantic` (BaseModel for all schemas)
- `structlog` (logging in router and websocket)
- `openapi-typescript` (devDependency, for frontend type generation)

### Critic Issues Found and Fixed Per Story

All stories: **No issues found.** Each Critic review confirmed correct implementation.

### Mini-Audit Results Per Story

| Story | File Paths | Line Counts | FR Coverage | Type Hints | Tests |
|---|---|---|---|---|---|
| 05-01 | OK | 150 lines | OK | OK | 192 |
| 05-02 | OK | router 183, main 63 | OK | OK | 198 |
| 05-03 | OK | router 183 | OK | OK | 204 |
| 05-04 | OK | router 294, repo 290 | OK | OK | 212 |
| 05-05 | OK | websocket ~140 | OK | OK | 218 |
| 05-06 | N/A | N/A | N/A | N/A | 218 |

### File Size Decisions

- `router.py`: Reached 336 lines after Story 05-04. Compacted by removing section headers, compressing docstrings, and using `_ARTIFACT_ATTR` dict for `_get_current_version`/`_set_artifact`. Final: 294 lines.
- `project_repository.py`: Reached 327 lines. Compacted docstrings. Final: 290 lines.

---

## STEP 4 — Test Validation

**Date:** 2026-03-13
**Validator:** Claude Opus 4.6

### Gaps Discovered

| # | File | Gap | Severity |
|---|---|---|---|
| 1 | test_api.py | `test_create_project` didn't verify `aktiver_modus` or timestamp validity | Medium |
| 2 | test_api.py | No test for POST /api/projects without `name` (422 negative case) | High |
| 3 | test_api.py | `test_get_project` used weak `"erstellt_am" in data` assertions (key presence only) | Medium |
| 4 | test_api.py | No test for `download` 404 | Medium |
| 5 | test_api.py | Version metadata fields (`erstellt_am`, `created_by`) not verified in version list | Low |
| 6 | test_api.py | No test for `struktur` type mapping — all versioning tests used `exploration` only | High |
| 7 | test_api.py | `test_import_artifact_valid` didn't verify persistence of imported artifact | High |
| 8 | test_websocket.py | No test for valid JSON with unknown `type` field | Medium |
| 9 | test_websocket.py | No test for `TurnOutput.error` code path (ErrorEvent instead of normal events) | High |

### Tests Added

| # | File | Test Name | Gap Fixed |
|---|---|---|---|
| 1 | test_api.py | Strengthened `test_create_project` | Added `aktiver_modus` assertion + ISO timestamp parsing |
| 2 | test_api.py | `test_create_project_missing_name` | Missing name → 422 |
| 3 | test_api.py | Strengthened `test_get_project` | All SDD 7.2.1 fields + timestamp parsing |
| 4 | test_api.py | `test_download_not_found` | Download 404 |
| 5 | test_api.py | `test_list_versions_version_metadata_complete` | All ArtifactVersionInfo fields |
| 6 | test_api.py | `test_restore_struktur_artifact_type_mapping` | `struktur` → DB `structure` mapping |
| 7 | test_api.py | `test_import_artifact_persisted` | Verifies import persisted via reload |
| 8 | test_websocket.py | `test_websocket_unknown_message_type` | Unknown type → error event |
| 9 | test_websocket.py | `test_websocket_turn_output_error_field` | TurnOutput.error → ErrorEvent |

### Summary

- **Tests before validation:** 218
- **Tests after validation:** 225 (+7 new)
- **Existing tests strengthened:** 2 (tighter assertions in create/get project)
- **Critical gaps closed:** Missing name 422, `struktur` type mapping, import persistence, TurnOutput.error path

---
