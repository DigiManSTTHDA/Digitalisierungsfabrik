# ADR-009: E2E Test Directory at Repository Root

**Status:** accepted
**Date:** 2026-03-18

## Context

The E2E test campaign (Epics 12–14) requires a standalone TypeScript project
that tests the Digitalisierungsfabrik system via WebSocket. This project is
neither backend (Python) nor frontend (React) code — it is an independent
test harness with its own `package.json`, `tsconfig.json`, and dependencies.

AGENTS.md requires an ADR for any new directory outside the paths defined in
HLA Section 6.

## Decision

Create `e2e/` at the repository root level, analogous to `api-contract/` and
`agent-docs/`. The directory contains a standalone TypeScript project with:

- `e2e/package.json` — project configuration (`tsx`, `ws`, `typescript`)
- `e2e/tsconfig.json` — strict TypeScript configuration
- `e2e/framework/` — test framework code (types, WebSocket client, runner, evaluator)
- `e2e/scenarios/` — scenario JSON files
- `e2e/reports/` — generated reports (gitignored)
- `e2e/run-campaign.ts` — CLI entry point

## Reason

1. The E2E framework has its own runtime (Node.js + tsx), dependencies, and
   TypeScript configuration — it cannot be a subdirectory of `backend/` or
   `frontend/`.
2. Placing it at root level makes the separation clear and avoids polluting
   either project's dependency tree.
3. `api-contract/` already establishes the precedent for root-level directories
   that serve cross-cutting concerns.

Alternatives considered:
- `backend/tests/e2e/` — rejected because it would require Node.js in the
  Python test environment and create confusing dependency mixing.
- `frontend/e2e/` — rejected because the tests don't use the browser/UI at all.

## Consequences

- `e2e/` is a standalone npm project; `npm install` must be run separately.
- `e2e/node_modules/` and `e2e/reports/` are gitignored.
- The framework tests the backend via WebSocket/REST — it requires a running
  backend but no frontend.

## SDD/HLA Reference

Not directly traceable to SDD/HLA — this is test infrastructure for the
E2E test campaign defined in `agent-docs/e2e-testkampagne-plan.md`.
