# Epic 14 — Validation Report

**Date:** 2026-03-18
**Epic:** Epic 14 – E2E Szenario-Definitionen (8 JSONs)
**Validator:** Claude (automated)
**Context:** Test harness / campaign — NOT part of the system itself. SDD/HLA traceability explicitly exempted by user. Stories must still be well-crafted with valid, complete acceptance criteria.

---

## EPIC VALIDATION REPORT

### 1. Structure Issues

**Status: 1 ISSUE**

| # | Check | Result | Detail |
|---|-------|--------|--------|
| 1.1 | Summary | PASS | Clear, concise summary describing 8 test scenario JSONs |
| 1.2 | Goal | PASS | Specific: 8 scenario JSONs in `e2e/scenarios/` covering defined behavioral categories |
| 1.3 | Testable Increment | PASS | Runnable: `npx tsx e2e/run-campaign.ts`, JSON validation against `Scenario` interface, report generation |
| 1.4 | Dependencies | PASS | Epic 12 (Framework Core) and Epic 13 (Evaluator + Reporter) correctly identified |
| 1.5 | Key Deliverables | PASS | All 8 JSON file paths listed with descriptions |
| 1.6 | Stories | PASS | 5 stories covering all 8 scenarios |
| 1.7 | Szenario-Qualitätskriterien | PASS | Epic-level quality gate with 7 mandatory criteria — good addition |
| 1.8 | Implementation Order | PASS | Explicit ordering by effort with rationale |

**Issue 1.1 — No ADR reference for `e2e/` directory:**
The `e2e/` directory is outside `hla_architecture.md` Section 6. Per AGENTS.md, new directories require an ADR. While the user has exempted SDD/HLA traceability, the `e2e-testkampagne-plan.md` effectively serves as the architectural justification. However, **no formal ADR exists** for the `e2e/` directory structure.
→ **Severity: LOW** (covered by campaign plan; recommend adding ADR reference in Epic 12 if not already present)

---

### 2. SDD Compliance Issues

**Status: EXEMPTED (with observations)**

Per user instruction, this epic is a test harness and not traceable to SDD functional requirements. The scenarios *reference* SDD concepts (FR-A-08 for German language, Moduswechsel-Logik, EMMA-Aktionstypen) but do not implement them.

**Observations (non-blocking):**
- Story 14-05 S08 correctly references FR-A-08 (Systemsprache Deutsch) in tags — good traceability for test intent
- Scenario quality criteria align with SDD behavioral expectations (phase transitions, artifact integrity, moderator behavior)
- The `intent.forbidden_concepts` pattern is a creative hallucination-guard not defined in SDD but appropriate for testing

---

### 3. Architecture Issues

**Status: 2 ISSUES**

| # | Check | Result | Detail |
|---|-------|--------|--------|
| 3.1 | File paths in `e2e/scenarios/` | PASS | All paths consistent with `e2e-testkampagne-plan.md` §Dateistruktur |
| 3.2 | Dependency on Epic 12 types | PASS | `Scenario` interface defined in campaign plan, to be implemented in Epic 12 |
| 3.3 | Reference to `backend/tests/e2e_reisekosten.py` | PASS | File exists in repository |
| 3.4 | Reference to `frontend/test-texte/dialog-reisekosten.jsonl` | **FAIL** | File does not exist |

**Issue 3.1 — Nonexistent file referenced in Story 14-02:**
Story 14-02 references `frontend/test-texte/dialog-reisekosten.jsonl` in the FR/NFR Traceability note. This file does **not exist** in the repository. The directory `frontend/test-texte/` does not exist either.
→ **Correction required:** Remove or update the reference. If the data was planned but not created, note it as aspirational or remove the traceability line.

**Issue 3.2 — `e2e/` directory does not exist yet:**
The `e2e/` directory, `e2e/framework/types.ts`, and `e2e/run-campaign.ts` referenced in the testable increment do not exist. These are dependencies from Epic 12 and Epic 13. This is correct by design (Epic 14 depends on Epic 12+13), but the epic should explicitly note that **implementation cannot start before Epic 12 delivers the Scenario interface**.
→ **Severity: LOW** — Dependencies section covers this, but an explicit note would improve clarity.

---

### 4. Test Issues

**Status: 1 ISSUE**

This epic defines test data (JSON scenarios), not backend logic. No pytest tests are required per AGENTS.md Rule 7 ("backend stories that change logic must include tests"). The JSON files are validated by `npm run typecheck` which verifies the loading and type-checking of scenario data.

| # | Check | Result | Detail |
|---|-------|--------|--------|
| 4.1 | Logic requiring tests? | N/A | No backend/frontend logic introduced — only JSON data files |
| 4.2 | TypeCheck coverage | PASS | All stories include `npm run typecheck` in DoD |
| 4.3 | JSON validity check | **WARN** | No explicit JSON schema validation step beyond TypeScript type checking |

**Issue 4.1 — No explicit JSON validation step:**
The DoD relies solely on `npm run typecheck` to validate JSON files. TypeScript type checking verifies the *loading code* but does not directly validate that each JSON file conforms to the `Scenario` interface at the field level (TypeScript doesn't validate JSON at compile time). A runtime validation step (e.g., `npx tsx -e "import s from './e2e/scenarios/s01-eingangsrechnung.json'; ..."`) would provide stronger guarantees.
→ **Recommendation:** Add a DoD checkbox like: `- [ ] JSON validates against Scenario interface (runtime check or schema validation)`

---

### 5. DoD Issues

**Status: 4 ISSUES**

#### 5.1 — Missing phase coverage in Stories 14-03, 14-05 (S07, S08)

The `Scenario` interface requires `phases.spezifikation: Turn[]` as a **non-optional** field. Several stories define acceptance criteria for only some phases:

| Story | Scenario | Phases in AC | Missing from AC |
|-------|----------|-------------|-----------------|
| 14-03 | S03 | exploration, strukturierung | **spezifikation** |
| 14-05 | S07 | exploration | **strukturierung, spezifikation** |
| 14-05 | S08 | exploration | **strukturierung, spezifikation** |

For S06 (Abbruch), this is explicitly handled: AC states `strukturierung`, `spezifikation`, `validierung` are empty arrays `[]`. The other scenarios do not make this explicit.

→ **Correction required:** For each scenario, either:
  - (a) Define AC for all required phases (even if minimal), or
  - (b) Explicitly state which phases use empty arrays `[]` and why

#### 5.2 — Epic-level quality criteria not reflected in story DoDs

The epic defines 7 "Szenario-Qualitätskriterien" (lines 42-55), but several are not checkboxed in individual story DoDs:

| Quality Criterion | Covered in Story DoDs? |
|---|---|
| 1. Valides Scenario-Interface | YES (via typecheck) |
| 2. Realistische Nutzer-Messages | **NO** — no DoD checkbox |
| 3. Intent-Definition | YES (most stories) |
| 4. BehaviorProbes (≥2) | YES (all stories) |
| 5. TurnExpectations an kritischen Turns | PARTIAL — only in 14-01, 14-04, 14-05/S08 |
| 6. Nudges für letzten Turn einer Phase | PARTIAL — only in 14-01, 14-02 |
| 7. Notes an kritischen Turns | **NO** — no DoD checkbox in any story |

→ **Correction required:** Add DoD checkboxes for criteria 2 (realistic messages) and 7 (notes on critical turns) to each story, or remove them from the epic-level criteria.
→ **Correction required:** Ensure criteria 5 (TurnExpectations) and 6 (Nudges) are consistently addressed in all story DoDs.

#### 5.3 — Missing `tags` validation in DoDs

All stories define expected `tags` in their acceptance criteria, but **no story DoD includes a checkbox** verifying that the `tags` field is correctly set in the JSON. Tags are important for campaign filtering.

→ **Correction required:** Add `- [ ] tags field set correctly` to each story DoD.

#### 5.4 — DoD commands incomplete for e2e/ context

The DoD command is `npm run typecheck` in `e2e/`. This is appropriate for a TypeScript project, but the DoD does not specify:
- Which directory to run from (should be `e2e/`)
- Whether `npm install` must succeed first (prerequisite)
- No lint check included

Per AGENTS.md, frontend stories require `npm run lint`, `npm run format:check`, `npm run typecheck`. While this is not a frontend story per se, the `e2e/` project is TypeScript. If `e2e/package.json` defines lint/format scripts (set up in Epic 12), they should be included.

→ **Recommendation:** Verify what scripts `e2e/package.json` (from Epic 12) provides and align DoD commands accordingly.

---

### 6. API Contract Issues

**Status: N/A**

No API endpoints are introduced by this epic. The scenarios use existing WebSocket endpoints defined in earlier epics.

---

### 7. Implementability Issues

**Status: PASS (with 1 observation)**

| # | Check | Result | Detail |
|---|-------|--------|--------|
| 7.1 | Independent stories | PASS | All stories produce independent JSON files — no cross-dependencies |
| 7.2 | Incremental delivery | PASS | Each story delivers usable scenario files; campaign can run with partial set |
| 7.3 | No future dependencies | PASS | Stories only depend on Epic 12/13 (declared in Dependencies) |
| 7.4 | Story bundling | PASS | Stories 14-04 (2 scenarios) and 14-05 (3 scenarios) bundle related scenarios — acceptable for JSON-only work |

**Observation:** Story 14-02 extends an existing file (`s02-reisekosten.json` from Epic 12-05). If Epic 12 has not yet been implemented, this story cannot start. The dependency is correctly declared at epic level but could be made more explicit in Story 14-02 itself.

---

## Summary

| Phase | Result |
|-------|--------|
| 1. Structure | PASS (1 low-severity observation) |
| 2. SDD Compliance | EXEMPTED |
| 3. Architecture | 1 ISSUE (nonexistent file reference) |
| 4. Tests | 1 RECOMMENDATION |
| 5. DoD | 4 ISSUES (missing phases in AC, quality criteria gaps, missing tags, incomplete commands) |
| 6. API Contract | N/A |
| 7. Implementability | PASS |

---

## EPIC VALID: NO

### Required Corrections

1. **[Story 14-02]** Remove or correct reference to nonexistent `frontend/test-texte/dialog-reisekosten.jsonl`.

2. **[Stories 14-03, 14-05]** Explicitly define all required `phases` for scenarios S03, S07, S08 — either with turns or as empty arrays `[]` with justification. The `Scenario` interface requires `spezifikation: Turn[]` as non-optional.

3. **[All Stories]** Add DoD checkboxes for epic-level quality criteria currently missing:
   - `- [ ] Nutzer-Messages sind realistisch und domänenspezifisch (keine Platzhalter)`
   - `- [ ] Kritische Turns mit note annotiert`
   - `- [ ] tags field korrekt gesetzt`

4. **[Stories 14-03, 14-05/S07, 14-05/S08]** Add DoD checkboxes for TurnExpectations and Nudges (epic quality criteria 5+6), or explicitly state why they are not applicable for that scenario.

### Recommendations (non-blocking)

5. Add a runtime JSON validation step to DoDs (beyond TypeScript type checking).
6. Verify `e2e/package.json` lint/format scripts from Epic 12 and align DoD commands.
7. Consider adding an ADR reference for the `e2e/` directory if not covered by Epic 12.

---

## Validation Log

- **2026-03-18:** Initial validation performed. Result: **NOT VALID** — 4 required corrections identified. Primarily DoD completeness gaps and missing phase definitions in acceptance criteria. No structural or implementability blockers.
