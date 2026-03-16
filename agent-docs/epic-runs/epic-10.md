# Epic 10 Run Log – Validation Mode & Correction Loop

**Start:** 2026-03-16
**Goal:** Implement ValidationMode and the correction loop for reviewing artifacts for internal consistency and completeness, surfacing findings in plain German, and guiding the user through corrections by re-entering earlier modes as needed.

---

## STEP 0 — Epic Identified

Epic: `epic-10-validation-correction.md`
Status: Stories not yet defined.
Dependencies: Epic 09 ✅ complete (328 backend tests, all DoD checks green after fixing 3 pre-existing phase transition test mismatches).

---

## STEP 1 — Story Generation

**Date:** 2026-03-16

### Stories Generated

| ID | Title | Purpose |
|---|---|---|
| 10-01 | ADR-007 for OP-20 + Validation Report Data Model | Resolve OP-20, define `Schweregrad` enum, `Validierungsbefund`, `Validierungsbericht` models, add to WorkingMemory |
| 10-02 | Validation Report Schema Tests | Persistence round-trip, severity classification, model construction tests |
| 10-03 | ValidationMode LLM Implementation + System Prompt | Replace stub with full LLM validation, German system prompt, Tool Use schema |
| 10-04 | Orchestrator Correction Loop + Validation Report Persistence | Correction loop routing, terminal state for project completion, report storage in WM |
| 10-05 | ValidationMode Tests — Mocked LLM + Correction Loop | 12+ mocked tests for clean/flawed artifacts, loop iteration, error propagation |
| 10-06 | Frontend — Validation Report Rendering + Artifact Highlighting | Severity badges, slot highlighting, ChatPane validation display |
| 10-07 | OpenAPI Contract Regeneration | Regen openapi.json + api.d.ts with validation schemas |

### Key Observations

- `ValidationMode` in `backend/modes/validation.py` is a stub from Epic 03
- No `backend/prompts/validation.md` exists yet
- SDD 6.6.4 severity scale uses `kritisch`, `warnung`, `hinweis` (not `wichtig` as in epic doc)
- Validation mode has NO write operations and does NOT interact with user directly
- Validation report is an "eigenständiges Ausgabedokument, kein Slot-Modell" (SDD 6.6.4)
- Correction loop (SDD 6.1.3): validation → moderator → specification → validation
- OP-20 resolved as ADR-007: prototype uses error message + user retry, no auto-retry
- `ModeOutput` needs optional `validierungsbericht` field for orchestrator extraction
- Terminal state: `advance_phase` in validierung → `projektstatus = abgeschlossen`
- No new dependencies required — all within existing tech stack

### Escalation Points Flagged

- None — SDD 6.6.4, 6.1.3, and FR-C-08/FR-C-09 are clear enough to implement unambiguously

---

## STEP 2 — Validation

**Date:** 2026-03-16

### Issues Found and Fixed

| # | Issue | Severity | Fix Applied |
|---|---|---|---|
| 1 | Key Deliverables: `validation_mode.py` → `validation.py` | Path error | Fixed in epic header |
| 2 | FR-C-08/6.6.4 `warnung` vs `wichtig` SDD inconsistency | Documentation | Added to ADR-007 scope in 10-01 |
| 3 | Missing "Ausnahmebehandlung" check in validation checks | SDD gap | Added to 10-03 AC |
| 4 | Tautological Schweregrad enum test | Test quality | Reworded 10-02 AC |
| 5 | Missing DoD checkbox for `llm: LLMClient` | DoD completeness | Added to 10-03 DoD |
| 6 | Missing DoD checkboxes for phase_transition + persistence | DoD completeness | Added to 10-04 DoD |

### Validation Outcome

All 6 issues corrected. Epic is now valid.

---

## STEP 2.5 — Escalation Checkpoint

No escalations needed:
1. SDD is clear enough for all stories (6.6.4, 6.1.3, FR-C-08/FR-C-09)
2. OP-20 resolution already planned as Story 10-01 (ADR-007)
3. No new dependencies required

---

## STEP 3 — Implementation

**Date:** 2026-03-16

### Stories Implemented

| Story | Commit | Key Changes |
|---|---|---|
| 10-01 | c3f2225 | ADR-007, Schweregrad/Validierungsbefund/Validierungsbericht models, WM field, API schema |
| 10-02 | 6d9d6ea | 9 tests: severity logic, persistence round-trip, durchlauf_nr |
| 10-03 | 3a286b2 | Full ValidationMode (5 deterministic checks + LLM), system prompt, validation_checks.py split |
| 10-04 | b52af56 | Orchestrator stores report in WM, terminal phase → abgeschlossen |
| 10-05 | a1fb237 | 14 deterministic validation tests (clean/flawed/mixed/edge cases) |
| 10-06+07 | 94d451e | Frontend severity badges, slot highlighting, GET /validation endpoint, OpenAPI + TS types |

### Test Results

- 351 backend tests passing (was 337 before Epic 10)
- Frontend: lint, typecheck, format all pass
