# Epic 12 — E2E Framework Core — Run Log

## Validation — 2026-03-18

**Outcome:** INVALID (corrections required)

**Context:** Epic 12 is a test harness, not a system component. SDD/HLA traceability waived per user instruction. Validation focused on story craftsmanship, AC completeness, internal consistency, and implementability.

### Issues Found

| # | Severity | Category | Issue |
|---|----------|----------|-------|
| C1 | ERROR | Consistency | Testable Increment references `ws-client.test.ts` but no story creates this file |
| C2 | ERROR | Consistency | `TurnResponse` type referenced in Story 12-03 AC8 but missing from Story 12-02's interface list |
| D1 | ERROR | DoD | File size limits (ACs in 12-02/03/04/05) have no corresponding DoD checkboxes |
| A1 | WARN | Architecture | No ADR for new `e2e/` root directory (AGENTS.md requires ADR for new directories) |
| C3 | WARN | Consistency | False positive — `AssertionResult` is correctly spelled |
| D2 | WARN | DoD | Story 12-02 DoD collapses 17 interfaces into 2 checkboxes — too coarse per AGENTS.md Rule 2 |
| D3 | WARN | DoD | Story 12-03 DoD missing constructor/baseUrl verification |
| T1 | WARN | Tests | No unit tests defined for framework logic (ws-client, scenario-runner) — accepted for test harness |
| C5 | INFO | Consistency | Story 12-03 AC4 should list `error` event as possible WebSocket response |

### Corrections Applied (2026-03-18)

| # | Fix |
|---|-----|
| C1 | Removed orphan `ws-client.test.ts` reference from Testable Increment |
| C2 | Added `TurnResponse` as AC18 in Story 12-02 (now 18 interfaces) |
| D1 | Added file size limit checkboxes to DoD of Stories 12-02, 12-03, 12-04, 12-05 |
| A1 | Added ADR-009 prerequisite note to Key Deliverables "Hinweis" block |
| C3 | No fix needed — false positive |
| D2 | Expanded Story 12-02 DoD from 2 checkboxes to per-group checkboxes (7 groups) |
| D3 | Added constructor/baseUrl checkbox + expanded error types in Story 12-03 DoD |
| C5 | Added `error` event reference to Story 12-03 AC4 |

**Post-correction outcome:** VALID (pending ADR-009 creation before implementation)

---

## Implementation — 2026-03-18

### Stories Implemented

| Story | Summary | Commit |
|-------|---------|--------|
| ADR-009 | E2E directory at repository root | `af3139c` |
| 12-01 | TypeScript project setup in `e2e/` | `a4085c9` |
| 12-02 | `types.ts` — All 18 interfaces | `6000b3f` |
| 12-03 | `ws-client.ts` — SessionClient | `5761c58` |
| 12-04 | `scenario-runner.ts` — ScenarioRunner | `06857bd` |
| 12-05 | S02 scenario + `run-campaign.ts` CLI | `05fe291` |

### Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `agent-docs/decisions/ADR-009-e2e-test-directory.md` | 53 | ADR for `e2e/` root directory |
| `e2e/package.json` | 18 | npm project config |
| `e2e/tsconfig.json` | 14 | TypeScript strict config |
| `e2e/.gitignore` | 2 | node_modules/ + reports/ |
| `e2e/framework/types.ts` | 170 | All 18 interfaces (limit: 300) |
| `e2e/framework/ws-client.ts` | 259 | SessionClient with WS + REST (limit: 300) |
| `e2e/framework/scenario-runner.ts` | 286 | Turn-loop, nudge, expectations (limit: 300) |
| `e2e/scenarios/s02-reisekosten.json` | 107 | S02 Happy Path (12 exploration turns) |
| `e2e/run-campaign.ts` | 143 | CLI entry point (limit: 150) |

### ADRs Written

- ADR-009: E2E Test Directory at Repository Root

### Critic Issues Found and Fixed

| Story | Issues | Details |
|-------|--------|---------|
| 12-01 | 0 | — |
| 12-02 | 0 | — |
| 12-03 | 1 | Initial implementation was 320 lines (limit 300); compressed event type definitions to 259 lines |
| 12-04 | 1 | TypeScript type error in nudge logProgress call; fixed by extracting nudgeTurn variable |
| 12-05 | 1 | Unused `client` variable in main(); removed |

### Mini-Audit Results

| Story | Paths | Lines | Exports | Types | Typecheck |
|-------|-------|-------|---------|-------|-----------|
| 12-01 | OK | OK | n/a | n/a | OK |
| 12-02 | OK | OK (170/300) | OK (18) | OK | OK |
| 12-03 | OK | OK (259/300) | OK (4) | OK | OK |
| 12-04 | OK | OK (286/300) | OK (1) | OK | OK |
| 12-05 | OK | OK (143/150) | n/a | OK | OK |

### Open Items

- **Smoke test pending manual verification:** Story 12-05 DoD checkbox for
  `npx tsx e2e/run-campaign.ts --scenario S02` is unchecked — requires a
  running backend to verify. All other checkboxes are `[x]`.
