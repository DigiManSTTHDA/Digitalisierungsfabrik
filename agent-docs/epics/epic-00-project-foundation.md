# Epic 00 – Project Foundation & Dev Setup

## Summary

Stand up the complete project skeleton so that every subsequent epic has a working,
reproducible environment to build on. This covers directory layout, dependency
management, linting/formatting config, and the minimal "hello world" endpoints that
prove the stack is wired together correctly.

No business logic is written in this epic. The goal is: any developer (or AI agent) can
clone the repo, run two commands, and have a green test suite and running dev server.

## Goal

A fully reproducible, documented local development environment for both backend
(FastAPI/Python) and frontend (React/TypeScript/Vite), with a passing test baseline and
a live health-check endpoint.

## Testable Increment

- `cd backend && pytest` → all tests pass (at minimum the health-check smoke test)
- `GET /health` returns `{"status": "ok"}`
- `cd frontend && npm run dev` → Vite dev server starts, browser shows placeholder page
- Both are runnable by following only the instructions in `README.md` / `AGENTS.md`

## Dependencies

None – this is the starting epic.

## Key Deliverables

- `backend/` directory with `main.py`, `requirements.txt`, `pyproject.toml` (or
  `setup.cfg`), `.env.example`
- `backend/tests/` directory with at least one smoke test
- `frontend/` directory with Vite + React + TypeScript scaffold
- `frontend/src/` placeholder `App.tsx`
- Root-level `.gitignore`, updated `README.md` with setup instructions
- CI-ready: tests and linter pass locally with documented commands

### OpenAPI Contract Toolchain (binding — see ADR-001)

- `frontend/package.json` includes devDependencies:
  - `openapi-typescript` ≥ 7
  - `openapi-fetch` ≥ 0.9
- `frontend/package.json` scripts:
  ```json
  {
    "generate-api": "openapi-typescript http://localhost:8000/openapi.json -o src/generated/api.d.ts",
    "generate-api:file": "openapi-typescript ../../api-contract/openapi.json -o src/generated/api.d.ts"
  }
  ```
- `frontend/src/generated/` directory created (empty `.gitkeep` placeholder until
  Epic 05 produces the real spec)
- `api-contract/` directory at the repository root with a minimal placeholder
  `openapi.json` (will be replaced by the real spec at the end of Epic 05)
- `frontend/src/api/client.ts` scaffold that initialises the `openapi-fetch` client
  (can be a stub pointing at the placeholder spec until Epic 05)

### Testable Increment (addition)

- `npm run generate-api:file` runs without error (using the placeholder spec)
- `tsc --noEmit` passes with the generated placeholder types included

## Stories

_To be defined before this epic begins._
