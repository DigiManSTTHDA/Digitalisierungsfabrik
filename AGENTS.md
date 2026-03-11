# AGENTS.md — Digitalisierungsfabrik

This file governs how AI agents work in this repository.

---

## Goal

Build a **working prototype** of the Digitalisierungsfabrik system as specified in
`digitalisierungsfabrik_systemdefinition.md` and architected in `hla_architecture.md`.

The prototype validates whether the AI-guided process elicitation approach yields valuable
results. It will serve as inspiration for a dev team building the actual product.

**Scope:** Working prototype — not production-grade, but well-structured enough to inspire
a production implementation. Correctness and clarity over optimization.

---

## Architecture

The canonical architecture is defined in `hla_architecture.md`. Follow it.

**Tech stack (binding):**

| Layer | Technology |
|---|---|
| Backend | Python ≥ 3.11, FastAPI ≥ 0.111 |
| Data models | Pydantic v2 |
| LLM client | anthropic SDK ≥ 0.25 |
| Persistence | SQLite (stdlib `sqlite3`) |
| Frontend | React ≥ 18, TypeScript ≥ 5, Vite ≥ 5 |
| API contract | OpenAPI 3.x (FastAPI auto-generated) |
| API type generation | `openapi-typescript` ≥ 7 (devDependency) |
| API client (frontend) | `openapi-fetch` ≥ 0.9 |
| Logging | structlog |

**Project structure** follows `hla_architecture.md` Section 6 exactly, with the following
binding addition: `frontend/src/types/api.ts` (referenced in HLA Section 6) does **not**
exist. It is replaced by the generated file `frontend/src/generated/api.d.ts` per ADR-001.

### Deviations from Architecture

Any deviation from `hla_architecture.md` **must** be documented before implementation in
`agent-docs/decisions/` using the ADR template (see below). Reference the ADR in commit
messages and inline comments where the deviation occurs.

---

## Documentation

All decisions, open points, and architectural rationale go into `agent-docs/`.

### Folder structure

```
agent-docs/
  decisions/          # Architecture Decision Records (ADRs)
    ADR-001-*.md
    ADR-002-*.md
    ...
  tasks/              # Per-implementation-step task breakdowns
    step-01-*.md
    step-02-*.md
    ...
  open-points/        # Tracking of open points from hla_architecture.md Section 9
    open-points.md
```

### ADR Template (`agent-docs/decisions/ADR-NNN-title.md`)

```markdown
# ADR-NNN: Title

**Status:** proposed | accepted | superseded
**Date:** YYYY-MM-DD

## Context
What situation prompted this decision?

## Decision
What was decided?

## Reason
Why? What alternatives were considered?

## Consequences
What changes in the codebase? What risks does this introduce?

## SDD/HLA Reference
Which section does this affect?
```

---

## Development Workflow

### Implementation Order

Follow `hla_architecture.md` Section 8 strictly:

| Step | Content | Definition of Done |
|---|---|---|
| 1 | Pydantic models + SQLite schema + ProjectRepository | Project can be created, saved, loaded |
| 2 | Executor + Template schema | Patch applied; error triggers rollback |
| 3 | Orchestrator skeleton + Working Memory (stub modes) | Cycle runs, WM updated, persistence works |
| 4 | LLM client + ExplorationMode + ContextAssembler + OutputValidator | First LLM turn completes end-to-end |
| 5 | FastAPI backend (REST + WebSocket) | API endpoints testable without frontend |
| 6 | React frontend | Full user dialog in browser |
| 7 | Moderator + phase transition | Phase transition cycle complete |
| 8 | StructuringMode | |
| 9 | SpecificationMode | |
| 10 | ValidationMode + correction loop | |
| 11 | End-to-end run + stabilization | Full Exploration → Validation flow works |

Each step is a self-contained, testable increment. Do not start step N+1 before step N
passes its tests.

Document each step in `agent-docs/tasks/step-NN-*.md` before starting.

### Commits

Commit **frequently** — after every logical unit of work:

- After each green test batch
- After completing a module or class
- After each implementation step
- After each ADR is written

Commit message format:
```
<type>(<scope>): <short summary>

<body if needed>

Refs: ADR-NNN (if deviating from architecture)
```

Types: `feat`, `test`, `fix`, `docs`, `refactor`, `chore`

Examples:
```
feat(artifacts): implement Pydantic models with dict-keyed slots
test(executor): add RFC 6902 patch application and rollback tests
docs(adr): ADR-001 SQLite over JSON files
fix(orchestrator): correct mode transition on phase_complete flag
```

---

## Test-Driven Development

Apply TDD wherever the component has deterministic, testable behavior. This covers
the entire backend. The frontend is excluded from strict TDD but should have smoke tests.

### TDD Cycle

1. **Write a failing test** that captures the requirement from the SDD
2. **Write the minimum code** to make the test pass
3. **Refactor** if needed, keeping tests green
4. **Commit**

### Test locations

All backend tests live in `backend/tests/`. Mirror the source structure:

| Source | Test file |
|---|---|
| `core/executor.py` | `tests/test_executor.py` |
| `artifacts/models.py` + `artifacts/store.py` | `tests/test_artifacts.py` |
| `core/orchestrator.py` | `tests/test_orchestrator.py` |
| `artifacts/completeness.py` | `tests/test_completeness.py` |
| `persistence/project_repository.py` | `tests/test_persistence.py` |

### What to test

| Component | Key test scenarios |
|---|---|
| Executor | Valid patch applied; invalid path rejected; crash mid-patch → rollback to snapshot; preservation check; invalidation propagation |
| Artifacts | Dict-keyed slot access; completeness state calculation; Markdown rendering |
| Orchestrator | Mode selection from flags; 11-step cycle runs; WM updated after turn; persistence called |
| Persistence | Atomic transaction: all writes committed or none; project load after save returns identical state |
| LLM client | Mock-based: `complete()` called with correct args; streaming tokens yielded |

Use `pytest`. Use `pytest-asyncio` for async tests. Use in-memory SQLite (`:memory:`) for
persistence tests.

---

## Key Design Constraints

These are **non-negotiable** — they come directly from the SDD and HLA:

1. **RFC 6902 JSON Patch** for all artifact write operations (SDD 5.7)
2. **Dict-keyed artifact slots** — never lists — for stable RFC 6902 paths (HLA Section 3.6)
3. **SQLite ACID transactions** for all project state writes — no partial state (FR-E-01)
4. **Structured output via Tool Use** — `tool_choice: {"type": "tool", "name": "apply_patches"}` — not prompt-only format instructions (HLA Section 2.5)
5. **Orchestrator is framework-agnostic** — it knows nothing about FastAPI or WebSocket
6. **No mode writes directly to artifacts or Working Memory** — all writes go through Executor
7. **LLM provider is config-only** — `LLM_PROVIDER=anthropic|ollama` in `.env`, no code change needed
8. **System language is German** — all dialogs and artifacts in German (SDD 1.3)

---

## API Contract (OpenAPI)

The REST interface between frontend and backend is governed by a machine-readable
OpenAPI 3.x contract. **This section is binding.** See `agent-docs/decisions/ADR-001-openapi-contract.md`
for the full rationale.

### Rules

1. **Backend exposes the live spec** at `GET /openapi.json` (FastAPI default — no extra code).
2. **All request and response shapes** are explicit Pydantic models in `backend/api/schemas.py`.
   Route handlers must declare typed parameters and return types; no `dict` or `Any` responses.
3. **Frontend types are generated**, never hand-written. The generated file is
   `frontend/src/generated/api.d.ts`. It must never be edited manually.
4. **Frontend API client** uses `openapi-fetch` initialised in `frontend/src/api/client.ts`.
   All REST calls go through this client; no hand-written `fetch` wrappers for API endpoints.
5. **Contract snapshot** lives at `api-contract/openapi.json` (committed to the repository).
   It is the source of truth for frontend development when the backend is not running.
6. **Regeneration command** (run from `frontend/`):
   ```bash
   npm run generate-api          # from running backend (http://localhost:8000/openapi.json)
   npm run generate-api:file     # from committed snapshot (api-contract/openapi.json)
   ```
7. **Every new endpoint** introduced in any epic must:
   - Add or update its Pydantic schema in `backend/api/schemas.py`
   - Export an updated snapshot: `GET http://localhost:8000/openapi.json > api-contract/openapi.json`
   - Regenerate types: `npm run generate-api:file` in `frontend/`
   - Commit `api-contract/openapi.json` and `frontend/src/generated/api.d.ts` together

### File locations

| File | Role | Editable? |
|---|---|---|
| `backend/api/schemas.py` | Pydantic request/response models | Yes — source of truth |
| `api-contract/openapi.json` | Committed OpenAPI snapshot | Only via regeneration |
| `frontend/src/generated/api.d.ts` | Generated TypeScript types | **Never** — auto-generated |
| `frontend/src/api/client.ts` | `openapi-fetch` client init | Yes |

---

## Environment Setup

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest

# Run backend
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run generate-api:file   # generate TypeScript types from committed OpenAPI snapshot
npm run dev
```

Configuration via `backend/.env` (copy from `backend/.env.example`):

```
LLM_PROVIDER=anthropic
LLM_MODEL=claude-opus-4-6
LLM_API_KEY=sk-ant-...
DATABASE_PATH=./data/digitalisierungsfabrik.db
```

---

## References

- `digitalisierungsfabrik_systemdefinition.md` — Full system requirements (SDD)
- `hla_architecture.md` — High-level architecture (binding)
- `hla_adversarial_review.md` — Critical review of earlier architecture draft; key issues
  already resolved in current HLA (SQLite, dict-keyed slots, Tool Use strategy)
- `agent-docs/decisions/` — ADRs for any deviations from HLA
- `agent-docs/decisions/ADR-001-openapi-contract.md` — OpenAPI contract for frontend–backend integration
- `agent-docs/open-points/open-points.md` — Tracking of HLA Section 9 open points
- `api-contract/openapi.json` — Committed OpenAPI 3.x snapshot (source of truth for frontend type generation)
