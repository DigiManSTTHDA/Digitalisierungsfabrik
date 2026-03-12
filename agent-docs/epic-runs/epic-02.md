# Epic 02 – Execution Engine: Run Log

**Date:** 2026-03-12
**Status:** Completed
**Commit:** 65aaf39

## Goal

Implement the Executor — the only component allowed to write to artifacts — with full
RFC 6902 JSON Patch validation, rollback on failure, and invalidation detection.

## Stories Implemented

### Story 02-01 — ArtifactTemplate Schema

**Module created:** `backend/artifacts/template_schema.py`

- `TemplatePathPattern`: `pattern` (Python regex), `allowed_ops`, `description`
- `ArtifactTemplate`: `artifact_type`, `path_patterns`, `is_valid_patch()` via `re.fullmatch`
- Static instances: `EXPLORATION_TEMPLATE` (4 path patterns), `STRUCTURE_TEMPLATE` (12 path patterns), `ALGORITHM_TEMPLATE` (11 path patterns)
- `TEMPLATES` dict for Executor lookup

### Story 02-02 — Executor Core Pipeline

**Module created:** `backend/core/executor.py`

- `ExecutorResult` dataclass: `success`, `artifact`, `invalidated_abschnitt_ids`, `error`
- `Executor.apply_patches()` 7-step pipeline:
  1. RFC-6902 formal validation (op/path syntax)
  2. Template-schema allowlist check
  3. Atomic snapshot via `model_dump()`
  4. Patch application via `jsonpatch`
  5. Preservation check (second-level entity comparison)
  6. Invalidation detection (structure only — story 02-03)
  7. Version bump
- `structlog` logging at INFO (success) and WARNING (failure)

### Story 02-03 — Invalidation Logic

Implemented inside `apply_patches()` (step 6):

- Triggers on: `beschreibung`, `typ`, `bedingung`, `ausnahme_beschreibung` changes, and whole-step `add`/`remove`
- Does NOT trigger on: `titel`, `reihenfolge`, `nachfolger`, `algorithmus_ref`, `spannungsfeld`, `completeness_status`, `algorithmus_status`
- Returns deduplicated `algorithmus_ref` IDs from affected steps
- Responsibility split: Executor returns IDs; Orchestrator (Epic 03) sets `algorithmus_status = invalidiert`

## Test File Created

`backend/tests/test_executor.py` — 39 tests:

| Category | Count |
|---|---|
| Template validation | 9 |
| Happy path | 4 |
| RFC-6902 syntax errors | 4 |
| Template violations | 2 |
| Patch failure / rollback | 2 |
| Preservation check | 1 |
| Invalidation triggered | 6 |
| No invalidation | 7 |
| Edge cases | 4 |

## Architecture Components Added

- `backend/artifacts/template_schema.py` — patch allowlist schema
- `backend/core/executor.py` — atomic patch engine
- `backend/tests/test_executor.py` — full test suite
- `backend/pyproject.toml` — added `jsonpatch` mypy override (`ignore_missing_imports`)

## DoD Verification

```
ruff check .                              → exit 0 ✓
ruff format --check .                     → exit 0 ✓
python -m mypy . --explicit-package-bases → exit 0 ✓
pytest --tb=short -q                      → 98 passed ✓
```
