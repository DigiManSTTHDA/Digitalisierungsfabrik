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
