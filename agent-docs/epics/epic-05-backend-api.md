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
- `backend/api/routes.py` – REST route definitions
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

_To be defined before this epic begins._
