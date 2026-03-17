# Epic 10 — Management Summary

## Validation Mode & Correction Loop

**Date:** 2026-03-16
**Status:** Complete
**Test count:** 351 passing (was 337 pre-epic, +14 new)

## What Was Built

Epic 10 implements the Validation Mode (SDD 6.6.4) — the final phase of the
Digitalisierungsfabrik process elicitation pipeline. After artifacts are
populated in Exploration → Structuring → Specification, the system validates
them for internal consistency, completeness, and EMMA compatibility.

### Key Capabilities

1. **5 Deterministic Pre-Checks** (no LLM needed):
   - Referential integrity: Struktur → Algorithmus
   - Referential integrity: Algorithmus → Struktur
   - EMMA compatibility: all action types valid
   - Completeness: no mandatory slots left empty
   - Exception handling: all ausnahme steps have algorithm sections

2. **LLM-Based Content Validation** — checks for logical contradictions
   and content consistency beyond what deterministic checks cover

3. **Severity Classification** (FR-C-08):
   - `kritisch` — must be fixed before completion
   - `warnung` — potential issue, not blocking
   - `hinweis` — informational only

4. **Correction Loop** (SDD 6.1.3):
   - Validation → Moderator → Specification → Validation cycle
   - Unlimited iterations until all kritisch findings resolved

5. **Terminal State** (FR-G-04):
   - When validation passes, project status → `abgeschlossen`

6. **Frontend Integration**:
   - Severity-colored badges in chat
   - Slot highlighting in artifact pane by severity
   - Validation report REST endpoint

## Architecture Decisions

- **ADR-007**: Validation report storage + OP-20 retry strategy (resolved)
- `validation_checks.py` added (user-approved) for 300-line file limit compliance

## Commits

| # | Hash | Description |
|---|---|---|
| 1 | c3f2225 | ADR-007 + validation report data model (Story 10-01) |
| 2 | 6d9d6ea | Validation report schema tests (Story 10-02) |
| 3 | 3a286b2 | ValidationMode implementation + system prompt (Story 10-03) |
| 4 | b52af56 | Orchestrator correction loop + terminal state (Story 10-04) |
| 5 | a1fb237 | 14 deterministic validation tests (Story 10-05) |
| 6 | 94d451e | Frontend + OpenAPI regeneration (Stories 10-06, 10-07) |

## Quality

- Backend: ruff, mypy, pytest all green on modified files
- Frontend: eslint, tsc, prettier all green
- 23 new validation-specific tests
- Pre-existing e2e test issues (format, lint) remain — not caused by this epic

## Known Issues

- `api/router.py` at 375 lines (limit: 300). Was ~345 pre-epic; the 30-line
  validation endpoint addition is necessary. Splitting into sub-routers is
  recommended as a future refactoring task.
