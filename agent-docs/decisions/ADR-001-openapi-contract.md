# ADR-001: OpenAPI Contract for Frontend–Backend Integration

**Status:** accepted
**Date:** 2026-03-11

## Context

The HLA (Section 2.2, 3.2) defines REST endpoints for frontend–backend communication but
does not specify how TypeScript types and the API client are maintained. The original plan
in `hla_architecture.md` Section 6 was to hand-write TypeScript interfaces in
`frontend/src/types/api.ts` to mirror the backend's Pydantic models.

Hand-written mirroring creates two problems:

1. **Silent drift** — any change to a Pydantic model that is not reflected in the
   TypeScript types compiles and deploys without error, but breaks at runtime.
2. **Maintenance overhead** — every new field, endpoint, or schema change must be applied
   in two separate files in two different languages.

FastAPI already generates a machine-readable OpenAPI 3.x specification for free (at
`/openapi.json`). Not leveraging this for type generation is leaving a proven contract
mechanism unused.

## Decision

Adopt an **OpenAPI-first contract** for all REST communication between frontend and backend:

1. FastAPI exposes the live OpenAPI 3.x spec at `GET /openapi.json` (default FastAPI
   behaviour — no additional code required).
2. All request and response body shapes are explicitly defined as Pydantic models in
   `backend/api/schemas.py`. Route handler parameter and return type annotations drive the
   spec; no implicit or anonymous response shapes.
3. The TypeScript frontend uses **generated** types derived from that spec — not
   hand-written types. The generated file lives at `frontend/src/generated/api.d.ts`.
4. The REST API client in the frontend uses `openapi-fetch`, which wraps native `fetch`
   with full type-safety based on the generated types. No hand-written fetch wrappers
   exist for REST calls.
5. A contract snapshot is committed to the repository at `api-contract/openapi.json`
   before Epic 06 begins, so frontend development can proceed without a running backend.

### Toolchain

| Tool | Role | Location |
|---|---|---|
| FastAPI (existing) | Generates live OpenAPI spec | `GET /openapi.json` |
| `openapi-typescript` ≥ 7 | Generates TypeScript types from spec | `npm run generate-api` |
| `openapi-fetch` ≥ 0.9 | Type-safe REST client using generated types | `frontend/src/api/client.ts` |

### Generated file

```
frontend/src/generated/api.d.ts   ← auto-generated; never edit by hand
```

This file is committed to the repository so the frontend can be built without a running
backend (e.g. in CI). It must be regenerated after any API change.

### npm scripts (frontend/package.json)

```json
{
  "scripts": {
    "generate-api": "openapi-typescript http://localhost:8000/openapi.json -o src/generated/api.d.ts",
    "generate-api:file": "openapi-typescript ../../api-contract/openapi.json -o src/generated/api.d.ts"
  }
}
```

`generate-api` fetches from the running backend; `generate-api:file` uses the committed
snapshot (for CI and offline development).

## Reason

- Eliminates hand-written TypeScript types that can silently drift from backend Pydantic models.
- `openapi-typescript` is zero-runtime — it generates only types, no runtime code.
- `openapi-fetch` wraps native `fetch` without introducing a heavyweight HTTP client
  dependency; bundle impact is minimal.
- Regeneration is a single command and fails fast on spec changes (compile errors in
  TypeScript immediately surface any incompatibility).
- FastAPI already produces the spec at zero cost; we use the output it already generates.
- Alternative tools evaluated: `openapi-generator-cli` (heavier, class-based output,
  more configuration), `hey-api` (good but less widely adopted). `openapi-typescript` +
  `openapi-fetch` is the most lightweight combination for a Vite/React project.

## Consequences

### Backend

- `backend/api/schemas.py` is now **required** (not optional). Every endpoint must declare
  its request body and response model explicitly via Pydantic models in this file.
- No implicit response types (e.g. `dict`, `Any`) on route handlers — these produce
  incomplete OpenAPI specs.
- Any new endpoint introduced in any epic must be accompanied by its Pydantic schema
  in `backend/api/schemas.py`.

### Frontend

- `frontend/src/types/api.ts` does not exist. The HLA Section 6 reference to this file
  is superseded by `frontend/src/generated/api.d.ts`.
- `frontend/src/api/rest.ts` (HLA Section 6) is replaced by `frontend/src/api/client.ts`,
  which initialises and exports the `openapi-fetch` client.
- All frontend components and hooks must import API types from `../generated/api` (or
  through the client), never define them locally.
- `frontend/src/generated/api.d.ts` must never be edited by hand. A lint rule (or CI
  check) should enforce this.

### Repository

- New directory `api-contract/` holds the versioned OpenAPI snapshots committed to git.
- `api-contract/openapi.json` is updated (regenerated + committed) at the end of Epic 05
  and whenever API schemas change in subsequent epics.

### Workflow

Every epic that introduces a new endpoint or changes an existing schema must:

1. Update `backend/api/schemas.py`
2. Start the backend and run `npm run generate-api` in `frontend/`
3. Commit both `api-contract/openapi.json` and `frontend/src/generated/api.d.ts`
4. Verify TypeScript compilation succeeds (`npm run build` or `tsc --noEmit`)

## SDD/HLA Reference

- HLA Section 2.2 — Frontend–Backend communication channels
- HLA Section 3.2 — REST endpoint table
- HLA Section 6 — Project structure (`frontend/src/types/api.ts` superseded by this ADR)
