# Epic 08 Run Log – Structuring Mode

**Start:** 2026-03-15
**Goal:** Implement StructuringMode for transforming free-text Exploration Artifact into a structured, BPMN-like process definition. Add project deletion (single + bulk) to UI and backend. The Structure Artifact is progressively populated with process steps, flows, roles, and decision points.

---

## STEP 0 — Epic Identified

Epic: `epic-08-structuring-mode.md`
Status: Stories not yet defined.
Dependencies: Epic 07 ✅ complete (275 backend tests, all DoD checks green).

---

## STEP 1 — Story Generation

**Date:** 2026-03-15

### Stories Generated

| ID | Title | Purpose |
|---|---|---|
| 08-01 | Structure Artifact Schema — Add `prozesszusammenfassung` | Add missing SDD 5.4 field + template schema path. Foundation for structuring mode. |
| 08-02 | StructuringMode LLM Implementation + System Prompt | Replace stub with real LLM-based mode. German system prompt. Decompose process into Strukturschritte. |
| 08-03 | StructuringMode Tests — Multi-Turn Mocked Dialog | 8+ tests with mocked LLM verifying multi-turn artifact population, phase status, flags. |
| 08-04 | Project Deletion — Backend (Repository + API) | `delete()` / `delete_many()` in repository + DELETE endpoints in router. |
| 08-05 | Project Deletion — Backend Tests | 7+ tests for single/bulk deletion, atomicity, isolation (FR-E-06). |
| 08-06 | Frontend — Structure Artifact Rendering | ArtifactTab renders Strukturschritte with types, flows, decision points, sorted by reihenfolge. |
| 08-07 | Frontend — Project Deletion UI (Single + Bulk) | Delete button, multi-select, ConfirmDialog, bulk-delete toolbar. |
| 08-08 | OpenAPI Contract Regeneration | Regen openapi.json + api.d.ts with new endpoints and updated schema. |

### Key Observations

- `StructureArtifact` was missing `prozesszusammenfassung` field (SDD 5.4 requires it as first mandatory section)
- `structuring.py` is a stub from Epic 03 — full LLM replacement needed
- `prompts/structuring.md` does not exist yet — must be created
- `ConfirmDialog.tsx` does not exist — new component needed
- No new dependencies required — all within existing tech stack
- No escalation points — SDD 5.4 and 6.6.2 are clear enough to implement unambiguously

---

## STEP 2 — Story Validation

**Date:** 2026-03-15

### Validation Outcome: PASS (after corrections)

### Issues Found and Corrected

| # | Severity | Issue | Correction |
|---|---|---|---|
| 1 | **MUST FIX** | Key Deliverables: `backend/modes/structuring_mode.py` — wrong filename | Fixed → `backend/modes/structuring.py` |
| 2 | **MUST FIX** | Key Deliverables: `backend/core/models.py` — wrong directory | Fixed → `backend/artifacts/models.py` |
| 3 | **SHOULD FIX** | Story 08-02: Missing SDD 6.6.2 constraint "bestehende Slots werden nicht ohne Rückfrage ersetzt" | Added to AC + DoD |
| 4 | **SHOULD FIX** | Story 08-03: No negative test for LLM error propagation (Rule T-6) | Added `test_structuring_error_on_llm_failure` |
| 5 | **MINOR** | Story 08-02 DoD: `prompts/structuring.md` existence not separate checkbox | Split into existence + content checkboxes |
| 6 | **MINOR** | Story 08-02 AC: Structure artifact read-only context not explicit | Added explicit mention per SDD 6.6.2 Input |

### SDD FR Traceability

| Story | Primary FRs |
|---|---|
| 08-01 | FR-B-01 (Strukturartefakt prozesszusammenfassung) |
| 08-02 | FR-A-01, FR-A-02, FR-A-04, FR-A-08, FR-B-01, FR-B-09, FR-B-11, FR-D-07, SDD 6.6.2 |
| 08-03 | Test coverage for 08-02 |
| 08-04 | FR-E-06 (Projektisolation), FR-E-01 (atomicity) |
| 08-05 | Test coverage for 08-04 |
| 08-06 | FR-B-06, FR-F-03, FR-F-05 |
| 08-07 | FR-A-08 (German UI labels) |
| 08-08 | ADR-001 (OpenAPI co-update) |

### Architecture Compliance

All story file paths match HLA Section 6. `ConfirmDialog.tsx` is a new file in the existing `components/` directory — acceptable without ADR.

---

## STEP 2.5 — Escalation Checkpoint

**Date:** 2026-03-15

No escalations needed:
- SDD is unambiguous for all stories (5.4, 6.6.2)
- No new design decisions — StructuringMode follows ExplorationMode pattern exactly
- No new dependencies required
- No new directories required

**Proceeding to implementation.**

---

## STEP 3 — Implementation

**Date:** 2026-03-15

### Stories Implemented

| ID | Commit | Tests Added | Key Changes |
|---|---|---|---|
| 08-01 | 836a220 | +3 | `prozesszusammenfassung` field + template path + context summary |
| 08-02 | a00fdd5 | 0 (tests in 08-03) | Full LLM StructuringMode + German system prompt |
| 08-03 | f57f9e4 | +11 | Mocked multi-turn tests, phase status, error propagation |
| 08-04 | 68b6b65 | 0 (tests in 08-05) | `delete()` / `delete_many()` + DELETE endpoints |
| 08-05 | ad8de2b | +7 | Deletion tests — single, batch, isolation, data removal |
| 08-06 | 150cce7 | 0 (frontend) | ArtifactTab: type badges, sorted steps, prozesszusammenfassung |
| 08-07 | f1d978f | 0 (frontend) | ConfirmDialog, delete button, multi-select, bulk delete |
| 08-08 | de053b2 | 0 (regen) | OpenAPI spec + TypeScript types regenerated |

### Modules Created/Modified

| File | Action | Lines |
|---|---|---|
| `backend/artifacts/models.py` | Modified — added `prozesszusammenfassung` | ~170 |
| `backend/artifacts/template_schema.py` | Modified — added path pattern | ~210 |
| `backend/core/context_assembler.py` | Modified — added summary line | ~112 |
| `backend/modes/structuring.py` | Rewritten — full LLM implementation | 148 |
| `backend/prompts/structuring.md` | Created — German system prompt | ~60 |
| `backend/persistence/project_repository.py` | Modified — delete methods | ~326 |
| `backend/api/router.py` | Modified — DELETE endpoints | ~343 |
| `backend/api/schemas.py` | Modified — batch schemas | ~172 |
| `backend/tests/test_structuring_mode.py` | Created — 11 tests | ~280 |
| `backend/tests/test_project_deletion.py` | Created — 7 tests | ~150 |
| `backend/tests/test_models.py` | Modified — 3 new tests | ~510 |
| `frontend/src/components/ArtifactTab.tsx` | Rewritten — structure rendering | ~210 |
| `frontend/src/components/ConfirmDialog.tsx` | Created — reusable modal | ~85 |
| `frontend/src/App.tsx` | Modified — deletion UI | ~240 |
| `frontend/src/store/session.ts` | Modified — delete actions | ~290 |

### Test Counts

- **Before Epic 08:** 276 passing (+ 1 flaky e2e)
- **After Epic 08:** 297 passing (+ 1 flaky e2e)
- **New tests added:** +21 (3 model, 11 structuring mode, 7 deletion)

### Critic + Mini-Audit Summary

All stories passed Critic review and Mini-Audit inline. No significant issues found beyond formatting corrections applied automatically by ruff/prettier.

### Libraries Used vs Custom Code

- No new libraries needed
- StructuringMode follows ExplorationMode pattern exactly
- Delete operations use standard SQLite DELETE with transaction

### File Size Notes

- `router.py` (343) and `project_repository.py` (326) slightly exceed 300 lines — pre-existing for router, new CRUD methods cohesive with existing code

---

## STEP 4 — Test Validation

**Date:** 2026-03-15

### Gaps Discovered

| # | Issue | Severity | Fix |
|---|---|---|---|
| 1 | prozesszusammenfassung test was pure round-trip (T-1 tautological) | HIGH | Rewritten to test through persistence |
| 2 | _compute_phasenstatus with `vollstaendig` status untested | MEDIUM | Added `test_compute_phasenstatus_vollstaendig_is_phase_complete` |
| 3 | tool_choice not verified in LLM call | MEDIUM | Added `test_structuring_llm_called_with_tool_choice` |
| 4 | prozesszusammenfassung in context_assembler output untested | MEDIUM | Added `test_prompt_context_summary_contains_prozesszusammenfassung_status` |
| 5 | Delete idempotency not tested | LOW | Added `test_delete_idempotent_second_call_returns_404` |

### Tests Added

- +1 rewritten (persistence round-trip instead of model_dump round-trip)
- +4 new tests (vollstaendig path, tool_choice, context summary, idempotency)

### Test Count After Validation

- **301 passing** (was 297 after implementation)

---
