# Epic 03 – Orchestrator & Working Memory: Run Log

**Start date:** 2026-03-12
**Goal:** Build the Orchestrator (11-step turn cycle) and wire it to Working Memory,
stub cognitive modes, the Executor, and SQLite persistence — all without LLM or HTTP.

---

## Step 1 — Story Generation (2026-03-12)

Stories generated and inserted into
`agent-docs/epics/epic-03-orchestrator-working-memory.md`.

### Generated Stories

| Story | Title | Purpose |
|---|---|---|
| 03-01 | Flag Enum, ModeContext, ModeOutput, BaseMode | Defines the abstract mode interface. `Flag` StrEnum (SDD 6.4.1), `ModeContext` (all inputs a mode needs), `ModeOutput` (what every mode returns), `BaseMode` abstract class. Enables all other Epic 03 stories. |
| 03-02 | Stub Mode Implementations | Five concrete mode stubs (Exploration, Structuring, Specification, Validation, Moderator) that return no-op patches. Allows the Orchestrator to drive a full turn cycle without any LLM call. |
| 03-03 | CompletenessCalculator | Derives `completeness_state`, `befuellte_slots`, `bekannte_slots` from all three artifacts. Implements Orchestrator step 9 (SDD 6.7 slot-count update). |
| 03-04 | Orchestrator with 11-Step Turn Cycle | Central control loop (`process_turn`). Loads project, calls mode, applies patches via Executor, handles invalidations, updates Working Memory, persists atomically. Also creates `context_assembler.py` (stub), `output_validator.py` (stub), `progress_tracker.py` (functional). |

### Test Files Produced

| File | Covers |
|---|---|
| `backend/tests/test_orchestrator.py` | WorkingMemory fields/defaults, Flag enum, ModeOutput, BaseMode, all 5 mode stubs, full turn cycle, mode dispatch, mode switch on flags, Executor error path, persistence round-trip |
| `backend/tests/test_completeness.py` | CompletenessCalculator: slot counting, completeness_state map |

---

## Step 2 — Validation (2026-03-12)

### Issues Found

| # | Severity | Issue | Fix Applied |
|---|---|---|---|
| 1 | **Critical** | `backend/modes/stubs.py` listed as Key Deliverable but is NOT in HLA Section 6. AGENTS.md Rule 5 requires exact HLA paths. | Removed `stubs.py`. Stub classes now live in HLA-defined files: `exploration.py`, `structuring.py`, `specification.py`, `validation.py`, `moderator.py` under final production class names. |
| 2 | **Major** | `backend/tests/test_working_memory.py` not in HLA Section 6 or AGENTS.md test mapping. Working Memory tests belong in `test_orchestrator.py`. | All `test_working_memory.py` references replaced with `test_orchestrator.py`. |
| 3 | **Minor** | DoD commands used `ruff check backend/` instead of canonical AGENTS.md format `ruff check .` (run from inside backend/). | Updated all DoD commands to match AGENTS.md format exactly. |

### Validation Outcome

**EPIC VALID: YES** (after corrections applied)

- Structure: ✓ Summary, Goal, Testable Increment, Dependencies, Key Deliverables, Stories all present
- SDD Compliance: ✓ All 6 Flag values from SDD 6.4.1 present; 11-step cycle matches SDD 6.3; slot counting per SDD 6.7
- Architecture: ✓ After fix — all file paths match HLA Section 6 exactly
- Tests: ✓ All logic-introducing stories have test requirements; `pytest-asyncio` confirmed in requirements.txt
- DoD: ✓ After fix — commands match AGENTS.md canonical format; each structural requirement has its own checkbox
- API Contract: N/A — Epic 03 has no API surface; TurnInput/TurnOutput are internal types

---

## Step 3 — Implementation (2026-03-12)

**Commit:** ba08dc0

### Stories Implemented

| Story | Status | Key notes |
|---|---|---|
| 03-01 | ✓ Done | `Flag` (6 values, SDD 6.4.1), `ModeContext`, `ModeOutput`, `BaseMode` all in `modes/base.py` |
| 03-02 | ✓ Done | 5 mode stubs in HLA-defined files with final class names (ExplorationMode, StructuringMode, SpecificationMode, ValidationMode, Moderator) |
| 03-03 | ✓ Done | `CompletenessCalculator.calculate()` returns (completeness_state, befuellte, bekannte) |
| 03-04 | ✓ Done | Full 11-step Orchestrator cycle; ContextAssembler stub; OutputValidator stub; ProgressTracker |

### Architecture Components Added

| File | Description |
|---|---|
| `backend/modes/base.py` | Flag enum, ModeContext, ModeOutput, BaseMode |
| `backend/modes/exploration.py` | ExplorationMode (stub) |
| `backend/modes/structuring.py` | StructuringMode (stub) |
| `backend/modes/specification.py` | SpecificationMode (stub) |
| `backend/modes/validation.py` | ValidationMode (stub) |
| `backend/modes/moderator.py` | Moderator (stub) |
| `backend/artifacts/completeness.py` | CompletenessCalculator |
| `backend/core/context_assembler.py` | build_context() stub |
| `backend/core/output_validator.py` | validate() stub |
| `backend/core/progress_tracker.py` | update_working_memory() |
| `backend/core/orchestrator.py` | TurnInput, TurnOutput, Orchestrator |
| `backend/tests/test_completeness.py` | 17 tests for CompletenessCalculator |
| `backend/tests/test_orchestrator.py` | 20 tests for Orchestrator, WM, modes |

### Issues Encountered and Fixed

1. **pytest-asyncio not installed**: `asyncio_mode = "auto"` in pyproject.toml requires
   pytest-asyncio installed. Installed from existing requirements.txt entry.

2. **Artifact version-skip in test setup**: `repo.save()` skips artifact writes for
   already-stored version numbers. Two tests that manually pre-populated artifacts
   at version 0 had their data silently dropped (version 0 was already stored by
   `create()`). Fixed by setting `version=1` on manually created test artifacts.

### DoD Final State

```
ruff check .                              → exit 0 ✓
ruff format --check .                     → exit 0 ✓
python -m mypy . --explicit-package-bases → exit 0, 34 files ✓
pytest --tb=short -q                      → 135 passed ✓
```

---

## Step 4 — Test Run (2026-03-12)

### Backend

| Check | Result |
|---|---|
| `ruff check .` | ✓ exit 0 |
| `ruff format --check .` | ✓ exit 0 |
| `python -m mypy . --explicit-package-bases` | ✓ exit 0, 34 files |
| `pytest --tb=short -q` | ✓ **135 passed** |

No failures. No tests deleted, skipped, or weakened.

### Frontend

| Check | Result |
|---|---|
| `npm run lint` | ✓ exit 0 |
| `npm run format:check` | ✓ exit 0 |
| `npm run typecheck` | ✓ exit 0 |

### Test breakdown

| File | Tests |
|---|---|
| `test_models.py` (Epic 01) | 22 |
| `test_persistence.py` (Epic 01) | 37 |
| `test_executor.py` (Epic 02) | 39 |
| `test_completeness.py` (Epic 03) | 17 |
| `test_orchestrator.py` (Epic 03) | 20 |
| `test_health.py` | — |
| **Total** | **135** |

---

## Step 5 — Audit (2026-03-12)

### AUDIT REPORT

#### Architecture Issues

| # | Finding | Verdict |
|---|---|---|
| 1 | `repository: object` type hint in `Orchestrator.__init__` (comment said "avoid circular import", but no circular dependency exists) | Fixed |
| 2 | All other file paths match HLA Section 6 exactly | ✓ Compliant |

#### SDD Compliance

| Component | SDD Ref | Status |
|---|---|---|
| `Flag` StrEnum (6 values: phase_complete, needs_clarification, escalate, blocked, artefakt_updated, validation_failed) | SDD 6.4.1 | ✓ |
| 11-step Orchestrator cycle (`process_turn`) | SDD 6.3 | ✓ |
| Working Memory fields (phasenstatus, befuellte_slots, bekannte_slots, completeness_state, aktiver_modus, vorheriger_modus, letzter_dialogturn, flags) | SDD 6.4 | ✓ |
| Mode switch on phase_complete / escalate / blocked → Moderator | SDD 6.3 Moduswechsel-Logik | ✓ |
| CompletenessCalculator: slot counting across all three artifacts | SDD 6.7 | ✓ |
| Invalidation write (algorithmus_status=invalidiert) on structure patch | SDD FR-B-04, 6.3 Schritt 8 | ✓ |
| ACID persistence via `repo.save()` single transaction | SDD 6.6 | ✓ |

#### Dependency Issues

No new dependencies added. All packages already in `requirements.txt`. ✓

#### Test Issues

No issues. 17 completeness tests + 20 orchestrator tests covering all acceptance criteria. ✓

#### DoD Issues

All commands pass after fix:

```
ruff check .                              → exit 0 ✓
ruff format --check .                     → exit 0 ✓
python -m mypy . --explicit-package-bases → exit 0, 34 files ✓
pytest --tb=short -q                      → 135 passed ✓
npm run lint                              → exit 0 ✓
npm run format:check                      → exit 0 ✓
npm run typecheck                         → exit 0 ✓
```

### Fixes Applied

1. **`backend/core/orchestrator.py`**: Replaced `repository: object` with `repository: ProjectRepository`, added static import of `ProjectRepository` at module level, removed deferred local import and `# type: ignore[assignment]`.

### Final Status

AGENTS.md: **YES**
HLA architecture: **YES**
SDD requirements: **YES**

---
