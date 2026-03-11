# Step 00 – Project Foundation & Dev Setup

**Epic:** `agent-docs/epics/epic-00-project-foundation.md`
**Status:** in progress
**Date:** 2026-03-11

## Scope

Stand up the complete project skeleton. No business logic. After this step:
- `cd backend && pytest` → green
- `GET /health` → `{"status": "ok"}`
- `cd frontend && npm run dev` → Vite starts, placeholder page
- `npm run generate-api:file` → generates `src/generated/api.d.ts` from placeholder spec
- `tsc --noEmit` → passes

## Task Breakdown

### Backend

| # | Task | Test first? |
|---|---|---|
| B-01 | Create `backend/` directory structure | — |
| B-02 | Write `requirements.txt` | — |
| B-03 | Write `pyproject.toml` (pytest config + ruff linter) | — |
| B-04 | Write `backend/.env.example` | — |
| B-05 | Write `backend/config.py` (pydantic-settings) | — |
| B-06 | **[TDD]** Write failing `tests/test_health.py` | Yes — test first |
| B-07 | Write `backend/main.py` (FastAPI app + `/health` endpoint) | makes B-06 pass |
| B-08 | Run `pytest` → confirm green | — |

### Frontend

| # | Task | Notes |
|---|---|---|
| F-01 | Create `frontend/` directory structure | |
| F-02 | Write `frontend/package.json` with all deps incl. openapi-typescript + openapi-fetch | |
| F-03 | Write `frontend/vite.config.ts` | |
| F-04 | Write `frontend/tsconfig.json` | |
| F-05 | Write `frontend/index.html` | |
| F-06 | Write `frontend/src/main.tsx` | |
| F-07 | Write `frontend/src/App.tsx` (placeholder) | |
| F-08 | Write `frontend/src/api/client.ts` (openapi-fetch stub) | |
| F-09 | Write `frontend/src/generated/.gitkeep` | |

### OpenAPI Contract Toolchain

| # | Task | Notes |
|---|---|---|
| O-01 | Create `api-contract/openapi.json` (minimal placeholder with /health) | |
| O-02 | Run `npm run generate-api:file` → generates `src/generated/api.d.ts` | |
| O-03 | Run `tsc --noEmit` → must pass | |

### Root Files

| # | Task | Notes |
|---|---|---|
| R-01 | Write `.gitignore` | covers Python, Node, .env |
| R-02 | Write `README.md` | setup instructions |

## Definition of Done

- [ ] `cd backend && pytest` → all tests pass
- [ ] `GET /health` → `{"status": "ok"}`
- [ ] `cd frontend && npm run dev` → starts without error
- [ ] `cd frontend && npm run generate-api:file` → runs without error
- [ ] `cd frontend && npx tsc --noEmit` → passes
- [ ] All files committed with conventional commit messages
