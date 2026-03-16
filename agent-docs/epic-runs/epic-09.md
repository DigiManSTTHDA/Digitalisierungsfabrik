# Epic 09 Run Log – Specification Mode

**Start:** 2026-03-16
**Goal:** Implement SpecificationMode for converting the structured process definition (Structure Artifact) into a technically precise Algorithm Artifact (EMMA RPA-ready specification). Resolve OP-02 (EMMA parameter schema). Render Algorithm Artifact in frontend.

---

## STEP 0 — Epic Identified

Epic: `epic-09-specification-mode.md`
Status: Stories not yet defined.
Dependencies: Epic 08 ✅ complete (302 backend tests, all DoD checks green).
Prerequisite: OP-02 (EMMA parameter schema) must be resolved via ADR.

---

## STEP 1 — Story Generation

**Date:** 2026-03-16

### Stories Generated

| ID | Title | Purpose |
|---|---|---|
| 09-01 | ADR for OP-02 Resolution + Algorithm Artifact Schema Completion | Resolve OP-02 via ADR-006, add `EmmaAktionstyp` enum, add `prozesszusammenfassung` to AlgorithmArtifact, update template schema. |
| 09-02 | Algorithm Artifact Schema Tests | Persistence round-trip tests, enum validation, negative tests for schema changes. |
| 09-03 | ContextAssembler Update for Specification Phase | Add algorithm artifact stats + EMMA catalog text helper to context assembler. |
| 09-04 | SpecificationMode LLM Implementation + System Prompt | Replace stub with full LLM-based mode + German system prompt with operationalisierbarkeit checklist. |
| 09-05 | SpecificationMode Tests — Multi-Turn Mocked Dialog | 10+ tests with mocked LLM verifying multi-turn artifact population, guardrails, error propagation. |
| 09-06 | Frontend — Algorithm Artifact Rendering | ArtifactTab renders Algorithmusabschnitte with EMMA actions, parameter tables, compatibility badges. |
| 09-07 | OpenAPI Contract Regeneration | Regen openapi.json + api.d.ts with updated AlgorithmArtifact schema. |

### Key Observations

- `AlgorithmArtifact` was missing `prozesszusammenfassung` field (SDD 5.5, FR-B-02 AK(2))
- `EmmaAktion.aktionstyp` was `str` — upgraded to `EmmaAktionstyp` StrEnum with 18 SDD 8.3 values
- `specification.py` is a stub from Epic 03 — full LLM replacement needed
- `prompts/specification.md` does not exist yet — must be created
- Epic doc had wrong path `specification_mode.py` — corrected to `specification.py` (HLA Section 6)
- Epic doc had wrong path `backend/core/models.py` — corrected to `backend/artifacts/models.py`
- No new dependencies required — all within existing tech stack
- OP-02 resolved as ADR-006: `dict[str, str]` parameters for prototype, `EmmaAktionstyp` enum for action types
- `EmmaAktion.nachfolger` kept as `list[str]` to support branching from DECISION actions

### Escalation Points Flagged

- None — SDD 5.5, 6.6.3, and 8.3 are clear enough to implement unambiguously

---

## STEP 2 — Story Validation

**Date:** 2026-03-16

### Validation Outcome: PASS (after corrections)

### Issues Found and Corrected

| # | Severity | Issue | Correction |
|---|---|---|---|
| 1 | **MUST FIX** | EMMA action type count was 17, SDD 8.3 has 18 types | Fixed → 18 throughout all stories (09-01, 09-02, 09-03) |
| 2 | **MUST FIX** | Guardrail condition `completeness_status != leer` too weak — SDD 6.6.3 requires `nutzervalidiert` | Fixed → guardrail checks for `nutzervalidiert` in 09-04, 09-05 |
| 3 | **SHOULD FIX** | ADR-006 didn't explicitly call out `nachfolger` SDD deviation (SDD 5.5 says String, model uses list[str]) | Fixed → ADR AC explicitly documents SDD deviation |
| 4 | **SHOULD FIX** | Story 09-04 referenced `working_memory.validierungsbericht` which doesn't exist | Fixed → clarified as placeholder for Epic 10, not testable yet |
| 5 | **SHOULD FIX** | Story 09-03 had no test requirements despite introducing logic (AGENTS.md Rule 7) | Fixed → added 4 tests for context assembler + EMMA catalog |
| 6 | **MINOR** | OpenAPI Contract Note had wrong path `backend/core/models.py` | Fixed → `backend/artifacts/models.py` |

### SDD FR Traceability

| Story | Primary FRs |
|---|---|
| 09-01 | FR-B-02 (Algorithmusartefakt), FR-C-03 (EMMA-Kompatibilitätsprüfung), OP-02 |
| 09-02 | Test coverage for 09-01 |
| 09-03 | FR-D-05 (Aktives Kontextmanagement), FR-D-07 (Fortschrittsmodell), SDD 6.5.3 |
| 09-04 | FR-A-01, FR-A-02, FR-A-03, FR-A-08, FR-B-02, FR-B-09, FR-B-11, FR-C-03, FR-C-06, FR-D-07, SDD 6.6.3 |
| 09-05 | Test coverage for 09-04 |
| 09-06 | FR-B-06, FR-F-03, FR-F-05 |
| 09-07 | ADR-001 (OpenAPI co-update) |

### Architecture Compliance

All story file paths match HLA Section 6. No new directories. `prompts/specification.md` is a new file in existing `prompts/` directory — acceptable without ADR.
