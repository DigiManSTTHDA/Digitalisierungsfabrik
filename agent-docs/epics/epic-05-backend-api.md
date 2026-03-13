# Epic 05 – Backend API (REST + WebSocket)

## Summary

Wrap the Orchestrator in a FastAPI application that exposes REST endpoints for project
management and a WebSocket endpoint for real-time conversation. After this epic the entire
backend is fully functional and can be exercised by any HTTP/WebSocket client – no frontend
required.

This epic corresponds to **Implementation Step 5** in `AGENTS.md` / `hla_architecture.md`.

## Goal

A running FastAPI server that accepts WebSocket connections for chat turns and REST calls
for project CRUD, reachable at `http://localhost:8000`, with all endpoints covered by
automated tests.

## Testable Increment

- `uvicorn backend.main:app --reload` starts without errors
- Using curl / Postman / httpx test client:
  - `POST /api/projects` → creates project, returns project ID
  - `GET /api/projects/{id}` → returns project with current artifacts
  - `GET /api/projects` → lists all projects
  - `WS /ws/session/{project_id}` → sends a user message, receives AI reply + artifact
    patch events in real time
- `pytest backend/tests/test_api.py` → all endpoint tests pass (using FastAPI TestClient
  + AsyncClient, in-memory SQLite, mocked LLM)

## Dependencies

- Epic 04 (real Exploration mode must exist to power the WebSocket handler)

## Key Deliverables

- `backend/main.py` – FastAPI application factory
- `backend/api/router.py` – REST route definitions (HLA Section 6 path)
- `backend/api/websocket.py` – WebSocket handler, streams orchestrator events
- `backend/api/schemas.py` – **required** Pydantic request/response models for every
  endpoint (drives the OpenAPI spec — no `dict` or `Any` return types on route handlers)
- `backend/tests/test_api.py` – REST + WebSocket endpoint tests
- `backend/tests/test_websocket.py` – streaming event tests

### OpenAPI Contract Deliverables (binding — see ADR-001)

This epic **must** freeze the API contract before Epic 06 begins:

1. Verify the live spec is correct: `GET http://localhost:8000/openapi.json` — all
   endpoints appear with typed request/response schemas.
2. Export the snapshot:
   ```bash
   curl http://localhost:8000/openapi.json > api-contract/openapi.json
   ```
3. Generate TypeScript types from the snapshot:
   ```bash
   cd frontend && npm run generate-api:file
   ```
4. Commit both `api-contract/openapi.json` and `frontend/src/generated/api.d.ts`.
5. Verify `tsc --noEmit` passes in the frontend after generation.

**Definition of Done addition:** Epic 05 is not complete until `api-contract/openapi.json`
is committed and `frontend/src/generated/api.d.ts` compiles without errors.

## Stories

> **Path Note:** HLA Section 6 defines `backend/api/router.py` (not `routes.py`).
> All stories use the HLA path. The Key Deliverables section has been corrected.

> **Streaming Note:** The Orchestrator's `process_turn()` returns a complete `TurnOutput`
> (not a generator). Token-level streaming (`chat_token` events) requires extending the
> Orchestrator interface and is deferred. The WebSocket handler sends `chat_done` with
> the full response after each turn. The `ChatTokenEvent` model from Epic 04 is ready
> for future streaming support.

### Story 05-01: API Request/Response Schemas

**User Story:**
As a developer,
I want all API request and response shapes defined as explicit Pydantic models in
`backend/api/schemas.py`,
so that FastAPI auto-generates a correct OpenAPI 3.x spec with typed schemas and no
route handler uses `dict` or `Any` as a return type.

**FR/NFR Traceability:** FR-G-01 (Projektanlage), FR-G-02 (Projektliste), FR-G-04
(Projektabschluss), FR-B-06 (Artefaktsichtbarkeit), FR-B-07 (Download/Export/Import),
FR-B-10 (Versionswiederherstellung), SDD 7.2.1 (Projektmetadaten-Felder),
ADR-001 (OpenAPI contract).

**Acceptance Criteria:**

1. `backend/api/schemas.py` exists.
2. `ProjectCreateRequest` model with fields:
   - `name: str` (required) — SDD 7.2.1
   - `beschreibung: str = ""` (optional) — SDD 7.2.1
3. `ProjectResponse` model with all SDD 7.2.1 fields:
   - `projekt_id: str`
   - `name: str`
   - `beschreibung: str`
   - `erstellt_am: datetime` (ISO 8601 serialized)
   - `zuletzt_geaendert: datetime` (ISO 8601 serialized)
   - `aktive_phase: Projektphase`
   - `aktiver_modus: str`
   - `projektstatus: Projektstatus`
4. `ProjectListResponse` model with field: `projects: list[ProjectResponse]`
5. `ArtifactsResponse` model with fields:
   - `exploration: dict` (full ExplorationArtifact serialized)
   - `struktur: dict` (full StructureArtifact serialized)
   - `algorithmus: dict` (full AlgorithmArtifact serialized)
6. `ArtifactVersionInfo` model with fields:
   - `version: int`
   - `erstellt_am: str` (ISO timestamp)
   - `created_by: str`
7. `ArtifactVersionsResponse` model with field: `versions: list[ArtifactVersionInfo]`
8. `ArtifactRestoreRequest` model with field: `version: int`
9. `ArtifactRestoreResponse` model with field: `artefakt: dict` (restored artifact)
10. `ArtifactImportRequest` model with fields:
    - `typ: Literal["exploration", "struktur", "algorithmus"]` (which artifact to import)
    - `artefakt: dict` (artifact JSON to import)
11. `DownloadResponse` model with fields:
    - `exploration: dict`
    - `struktur: dict`
    - `algorithmus: dict`
12. `ProjectCompleteResponse` model with field: `project: ProjectResponse`
13. `ErrorResponse` model with field: `detail: str`
14. `WebSocketIncoming` discriminated union for incoming WS messages:
    - `TurnMessage` with `type: Literal["turn"]`, `text: str`, `datei: str | None = None`
    - `PanicMessage` with `type: Literal["panic"]`
15. No `Any` types in public response model fields (internal `dict` for artifact
    serialization is acceptable as the artifact shape is dynamic).
16. All models importable from `backend/api/schemas.py`.

**Definition of Done:**

- [x] `backend/api/schemas.py` exists
- [x] `ProjectCreateRequest` has `name` (required) and `beschreibung` (optional)
- [x] `ProjectResponse` contains all 8 SDD 7.2.1 fields
- [x] `ProjectListResponse` wraps `list[ProjectResponse]`
- [x] `ArtifactsResponse` has `exploration`, `struktur`, `algorithmus` fields
- [x] `ArtifactVersionInfo` has `version`, `erstellt_am`, `created_by`
- [x] `ArtifactVersionsResponse` wraps `list[ArtifactVersionInfo]`
- [x] `ArtifactRestoreRequest` has `version: int`
- [x] `ArtifactRestoreResponse` has `artefakt: dict`
- [x] `ArtifactImportRequest` has `typ` and `artefakt` fields
- [x] `DownloadResponse` has all 3 artifact fields
- [x] `ProjectCompleteResponse` wraps `ProjectResponse`
- [x] `ErrorResponse` has `detail: str`
- [x] `TurnMessage` and `PanicMessage` models defined
- [x] `ruff check .` passes (exit 0)
- [x] `ruff format --check .` passes (exit 0)
- [x] `python -m mypy . --explicit-package-bases` passes (exit 0)
- [x] `pytest --tb=short -q` passes (exit 0, no regressions)

---

### Story 05-02: FastAPI App Setup + Project CRUD REST Endpoints

**User Story:**
As a developer,
I want a FastAPI application with project management REST endpoints,
so that projects can be created, listed, and loaded via HTTP without a frontend.

**FR/NFR Traceability:** FR-G-01 (Projektanlage), FR-G-02 (Projektliste/Auswahl),
FR-E-02 (Laden gespeicherter Projekte), SDD 7.2.1 (Projektmetadaten), HLA 3.2
(REST-Endpunkte).

**Acceptance Criteria:**

1. `backend/api/router.py` exists (HLA Section 6 path).
2. `backend/main.py` imports the router from `backend/api/router.py` and mounts it.
3. CORS middleware configured on the FastAPI app allowing origin `http://localhost:5173`
   (frontend dev server), methods `*`, headers `*`.
4. `POST /api/projects` endpoint:
   - Accepts `ProjectCreateRequest` body
   - Creates project via `ProjectRepository.create(name, beschreibung)`
   - Returns `ProjectResponse` with status 201
   - FR-G-01: returned `projekt_id` is unique, project is persisted immediately
5. `GET /api/projects` endpoint:
   - Returns `ProjectListResponse` with all projects
   - FR-G-02: each entry shows `name`, `beschreibung`, `aktive_phase`,
     `zuletzt_geaendert`, `projektstatus`
6. `GET /api/projects/{projekt_id}` endpoint:
   - Returns `ProjectResponse` with full project metadata
   - Returns 404 with `ErrorResponse` when project not found
7. FastAPI dependency injection provides `ProjectRepository` instance to route handlers.
   The dependency creates a `Database` and `ProjectRepository` per-request (or uses a
   shared instance — implementation may choose either, as long as in-memory SQLite works
   for tests).
8. All route handlers have explicit typed parameters and typed return models — no `dict`
   or `Any` responses.
9. Tests in `backend/tests/test_api.py`:
   - `test_create_project` — POST returns 201, response has `projekt_id`
   - `test_create_project_without_beschreibung` — POST with only `name`
   - `test_list_projects_empty` — GET returns empty list when no projects
   - `test_list_projects` — create 2 projects, GET returns both
   - `test_get_project` — create project, GET by ID returns correct metadata
   - `test_get_project_not_found` — GET with invalid ID returns 404

**Definition of Done:**

- [x] `backend/api/router.py` exists
- [x] Router mounted in `backend/main.py`
- [x] CORS middleware allows `http://localhost:5173`
- [x] `POST /api/projects` creates project, returns 201
- [x] `GET /api/projects` returns all projects
- [x] `GET /api/projects/{projekt_id}` returns project or 404
- [x] All handlers use typed request/response models
- [x] `backend/tests/test_api.py` exists with 6 tests
- [x] `ruff check .` passes (exit 0)
- [x] `ruff format --check .` passes (exit 0)
- [x] `python -m mypy . --explicit-package-bases` passes (exit 0)
- [x] `pytest --tb=short -q` passes (exit 0, no regressions)

---

### Story 05-03: Artifact & Project Lifecycle REST Endpoints

**User Story:**
As a developer,
I want REST endpoints for viewing current artifacts, downloading project data, and
completing a project,
so that all project lifecycle operations are available via HTTP.

**FR/NFR Traceability:** FR-B-06 (Artefaktsichtbarkeit), FR-B-07 (Download/Export),
FR-G-04 (Projektabschluss), HLA 3.2 (REST-Endpunkte).

**Acceptance Criteria:**

1. `GET /api/projects/{projekt_id}/artifacts` endpoint:
   - Returns `ArtifactsResponse` with all three artifacts in their current state
   - FR-B-06: artifacts reflect the latest persisted state
   - Returns 404 if project not found
2. `GET /api/projects/{projekt_id}/download` endpoint:
   - Returns `DownloadResponse` with all three artifacts as JSON
   - FR-B-07: download available regardless of phase or completeness status
   - Returns 404 if project not found
   - Note: Markdown rendering (via `artifacts/renderer.py`) is not yet implemented;
     this endpoint returns JSON only. Markdown download will be added in a later epic.
3. `POST /api/projects/{projekt_id}/complete` endpoint:
   - Sets `projektstatus` to `abgeschlossen`, persists via `ProjectRepository.save()`
   - Returns `ProjectCompleteResponse` with updated project
   - FR-G-04: project completion persists a final snapshot
   - Note: FR-G-04 requires showing open critical findings before completion.
     Critical findings (FR-C-08) are part of Validation mode (Epic 10). For now,
     the endpoint sets the status without validation checks. The frontend (Epic 06)
     or a later epic will add pre-completion confirmation UI.
   - Returns 404 if project not found
   - Returns 409 (Conflict) if project is already `abgeschlossen`
4. All new endpoints added to `backend/api/router.py`.
5. Tests in `backend/tests/test_api.py`:
   - `test_get_artifacts` — create project, GET artifacts returns all 3
   - `test_get_artifacts_not_found` — 404 for non-existent project
   - `test_download_project` — returns JSON with all 3 artifacts
   - `test_complete_project` — POST complete sets status, returns updated project
   - `test_complete_project_already_completed` — 409 on double-complete
   - `test_complete_project_not_found` — 404

**Definition of Done:**

- [x] `GET /api/projects/{id}/artifacts` returns all 3 artifacts
- [x] `GET /api/projects/{id}/download` returns JSON download
- [x] `POST /api/projects/{id}/complete` sets `projektstatus = abgeschlossen`
- [x] 404 returned for non-existent projects on all endpoints
- [x] 409 returned when completing an already-completed project
- [x] 6 tests in `backend/tests/test_api.py`
- [x] `ruff check .` passes (exit 0)
- [x] `ruff format --check .` passes (exit 0)
- [x] `python -m mypy . --explicit-package-bases` passes (exit 0)
- [x] `pytest --tb=short -q` passes (exit 0, no regressions)

---

### Story 05-04: Artifact Versioning & Import REST Endpoints

**User Story:**
As a developer,
I want REST endpoints for artifact version history, version restore, and artifact
import,
so that users can browse artifact versions, recover from unwanted changes, and import
externally modified artifacts.

**FR/NFR Traceability:** FR-B-10 (Versionswiederherstellung), FR-B-07 (Import),
FR-C-04 (Validierung importierter Artefakte), SDD 5.2 (Versionierung), HLA 3.2
(REST-Endpunkte).

**Acceptance Criteria:**

1. `GET /api/projects/{projekt_id}/artifacts/{typ}/versions` endpoint:
   - `{typ}` path parameter accepts: `exploration`, `struktur`, `algorithmus`
   - Returns `ArtifactVersionsResponse` with list of `ArtifactVersionInfo` entries
   - FR-B-10: version history is browseable
   - Returns 404 if project not found
   - Returns 422 if `{typ}` is not one of the three valid values
2. `POST /api/projects/{projekt_id}/artifacts/{typ}/restore` endpoint:
   - Accepts `ArtifactRestoreRequest` with `version: int`
   - Loads the specified version, creates a new version with `restored_from` metadata
   - Returns `ArtifactRestoreResponse` with the restored artifact
   - FR-B-10: restoration creates a new version (history not overwritten)
   - FR-B-10 AC#4: after restoration, Completeness-State is recalculated from the
     restored artifact via the existing `CompletenessCalculator`
   - Returns 404 if project or version not found
3. `POST /api/projects/{projekt_id}/import` endpoint:
   - Accepts `ArtifactImportRequest` with `typ` (which artifact) and `artefakt` (JSON)
   - Validates the artifact against the Pydantic model for the specified `typ`
   - If valid: saves as new version, returns `ArtifactRestoreResponse`
   - If invalid: returns 422 with `ErrorResponse` describing validation errors
   - FR-C-04: imported artifacts validated for schema conformity
4. New `ProjectRepository` methods added:
   - `list_artifact_versions(projekt_id, typ)` — returns list of version metadata
   - `load_artifact_version(projekt_id, typ, version_id)` — loads a specific version
5. `{typ}` parameter mapping: `struktur` maps to DB type `structure`,
   `algorithmus` maps to `algorithm`, `exploration` maps to `exploration`.
6. Tests in `backend/tests/test_api.py`:
   - `test_list_artifact_versions` — version 0 exists after project creation
   - `test_list_artifact_versions_invalid_typ` — 422 for bad typ
   - `test_restore_artifact_version` — restore version 0, new version created
   - `test_restore_artifact_version_not_found` — 404 for non-existent version
   - `test_import_artifact_valid` — valid JSON accepted
   - `test_import_artifact_invalid` — invalid JSON returns 422 with error detail
7. Repository method tests in `backend/tests/test_persistence.py`:
   - `test_list_artifact_versions` — returns correct version metadata
   - `test_load_artifact_version` — returns specific version content

**Definition of Done:**

- [x] `GET /api/projects/{id}/artifacts/{typ}/versions` returns version list
- [x] `POST /api/projects/{id}/artifacts/{typ}/restore` restores a version
- [x] `POST /api/projects/{id}/import` validates and imports artifact
- [x] `{typ}` parameter validates: `exploration`, `struktur`, `algorithmus`
- [x] `ProjectRepository.list_artifact_versions()` method added
- [x] `ProjectRepository.load_artifact_version()` method added
- [x] Repository method tests in `test_persistence.py`
- [x] API endpoint tests in `test_api.py`
- [x] `ruff check .` passes (exit 0)
- [x] `ruff format --check .` passes (exit 0)
- [x] `python -m mypy . --explicit-package-bases` passes (exit 0)
- [x] `pytest --tb=short -q` passes (exit 0, no regressions)

---

### Story 05-05: WebSocket Turn Handler

**User Story:**
As a developer,
I want a WebSocket endpoint that handles conversation turns and streams events in
real time,
so that a client can interact with the Orchestrator without REST polling.

**FR/NFR Traceability:** FR-A-01 (Dialogischer Interviewprozess), FR-D-01
(Orchestrator als zentraler Steuerknoten), FR-D-03 (Panik-Button-Eskalation),
FR-E-04 (Fehlerbehandlung bei LLM-Fehlern), FR-F-01 (Fortschrittsanzeige),
FR-F-02 (Debug-Modus), HLA 3.2 (WebSocket-Endpunkt), HLA 3.1 (WebSocket-Events).

**Acceptance Criteria:**

1. `backend/api/websocket.py` exists (HLA Section 6 path).
2. `WS /ws/session/{project_id}` endpoint accepts WebSocket upgrade.
3. WebSocket handler registered in `backend/main.py` (or via router include).
4. Receives JSON messages. Two message types:
   - `{"type": "turn", "text": "...", "datei": null}` — user turn
   - `{"type": "panic"}` — panic button activation
5. On `turn` message:
   - Constructs `TurnInput(text=..., datei=...)` from the message
   - Calls `Orchestrator.process_turn(project_id, turn_input)`
   - After `process_turn` completes, sends the following events (from `core/events.py`):
     - `ChatDoneEvent` with `message = turn_output.nutzeraeusserung`
     - `ArtifactUpdateEvent` for each artifact type (exploration, structure, algorithm)
       with the current artifact state loaded from the repository
     - `ProgressUpdateEvent` with phasenstatus and slot counts from
       `turn_output.working_memory`
     - `DebugUpdateEvent` with working memory dict and flags
   - If `turn_output.error` is set: sends `ErrorEvent` with `recoverable=True`
6. On `panic` message:
   - Sends an `ErrorEvent` with message "Panik-Button: Moderator wird in Epic 07
     implementiert" and `recoverable=True` (Moderator is not yet available; panic
     handling is wired in Epic 07)
7. On invalid JSON or unknown message type: sends `ErrorEvent` with descriptive
   message and `recoverable=True`.
8. On unexpected exception during `process_turn`: sends `ErrorEvent` with
   `recoverable=True` and logs the error.
9. WebSocket connection stays open for multiple turns until the client disconnects.
10. The handler creates an `Orchestrator` instance with proper dependencies
    (`ProjectRepository`, mode instances, `Settings`).
11. Tests in `backend/tests/test_websocket.py`:
    - `test_websocket_turn_success` — send turn, receive `chat_done` + `artifact_update`
      + `progress_update` + `debug_update` events
    - `test_websocket_turn_error` — mock orchestrator to raise, receive `error` event
    - `test_websocket_panic` — send panic message, receive error event about Epic 07
    - `test_websocket_invalid_message` — send garbage, receive `error` event
    - `test_websocket_project_not_found` — turn for non-existent project returns error
    - `test_websocket_multiple_turns` — two consecutive turns succeed
    - All tests use `TestClient.websocket_connect()` with mocked LLM and in-memory
      SQLite

**Definition of Done:**

- [x] `backend/api/websocket.py` exists
- [x] `WS /ws/session/{project_id}` accepts WebSocket connections
- [x] WebSocket handler registered in `backend/main.py`
- [x] Turn messages trigger `orchestrator.process_turn()`
- [x] `chat_done`, `artifact_update`, `progress_update`, `debug_update` events sent
- [x] Error events sent on orchestrator failure
- [x] Panic message handled with informational error
- [x] Invalid messages handled gracefully
- [x] Connection supports multiple consecutive turns
- [x] `backend/tests/test_websocket.py` exists with 6 tests
- [x] `ruff check .` passes (exit 0)
- [x] `ruff format --check .` passes (exit 0)
- [x] `python -m mypy . --explicit-package-bases` passes (exit 0)
- [x] `pytest --tb=short -q` passes (exit 0, no regressions)

---

### Story 05-06: OpenAPI Contract Freeze + Frontend Type Generation

**User Story:**
As a developer,
I want the OpenAPI spec exported and TypeScript types generated from it,
so that Epic 06 (React frontend) can build against a stable, typed API contract.

**FR/NFR Traceability:** ADR-001 (OpenAPI contract), AGENTS.md API Contract rules
(co-update rule).

**Acceptance Criteria:**

1. `api-contract/openapi.json` is updated with the real spec from the running backend.
2. The spec contains all REST endpoints defined in HLA 3.2:
   - `GET /api/projects`
   - `POST /api/projects`
   - `GET /api/projects/{projekt_id}`
   - `GET /api/projects/{projekt_id}/artifacts`
   - `GET /api/projects/{projekt_id}/artifacts/{typ}/versions`
   - `POST /api/projects/{projekt_id}/artifacts/{typ}/restore`
   - `GET /api/projects/{projekt_id}/download`
   - `POST /api/projects/{projekt_id}/import`
   - `POST /api/projects/{projekt_id}/complete`
   - `GET /health`
3. All endpoints have typed request/response schemas in the spec (no `{}` schemas).
4. `frontend/src/generated/api.d.ts` is regenerated via `npm run generate-api:file`.
5. `npm run typecheck` passes in `frontend/` after regeneration.
6. Both `api-contract/openapi.json` and `frontend/src/generated/api.d.ts` are committed
   together in the same commit (co-update rule per AGENTS.md).
7. The committed spec matches the running backend exactly — verified by diffing the
   live output of `GET /openapi.json` against the committed file.

**Definition of Done:**

- [x] `api-contract/openapi.json` contains all 10 endpoints
- [x] All endpoints have typed schemas in the spec
- [x] `frontend/src/generated/api.d.ts` regenerated from committed spec
- [x] `npm run typecheck` passes in `frontend/` (exit 0)
- [x] Both files committed together
- [x] Backend DoD commands still pass:
  - [x] `ruff check .` passes (exit 0)
  - [x] `ruff format --check .` passes (exit 0)
  - [x] `python -m mypy . --explicit-package-bases` passes (exit 0)
  - [x] `pytest --tb=short -q` passes (exit 0, no regressions)

---

### Implementation Order

Stories must be implemented in this order:

1. **05-01** (schemas) — no dependencies, defines types for all other stories
2. **05-02** (project CRUD) — depends on 05-01
3. **05-03** (artifact/lifecycle endpoints) — depends on 05-02
4. **05-04** (versioning/import) — depends on 05-02, adds new repo methods
5. **05-05** (WebSocket handler) — depends on 05-02 (needs app setup)
6. **05-06** (OpenAPI freeze) — depends on all prior stories being complete
