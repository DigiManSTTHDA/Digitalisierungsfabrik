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
- `backend/api/schemas.py` – request/response Pydantic models for the API layer
- `backend/tests/test_api.py` – REST + WebSocket endpoint tests
- `backend/tests/test_websocket.py` – streaming event tests

## Stories

_To be defined before this epic begins._
