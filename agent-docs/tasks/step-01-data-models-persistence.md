# Step 01 – Data Models & Persistence

**Epic:** Epic 01 – Data Models & Persistence
**Status:** in progress
**Date:** 2026-03-12

## Goal

Implement the full data layer: Pydantic v2 models for all artifact types, WorkingMemory, and
Project, backed by a SQLite schema with ACID transactions and a `ProjectRepository`.

## TDD Approach

Each module is implemented Red → Green → Commit:

1. Write failing tests that express the requirement
2. Write minimum code to make tests pass
3. Refactor if needed, keep tests green
4. Commit

## File Mapping

| Story | Source file(s) | Test file |
|---|---|---|
| 01-01 | `backend/artifacts/models.py` (Enums only) | `backend/tests/test_models.py` |
| 01-02 | `backend/artifacts/models.py` (Artifact models) | `backend/tests/test_models.py` |
| 01-03 | `backend/core/working_memory.py`, `backend/core/models.py` | `backend/tests/test_models.py` |
| 01-04 | `backend/persistence/schema.sql`, `backend/persistence/database.py` | `backend/tests/test_persistence.py` |
| 01-05 | `backend/persistence/project_repository.py` | `backend/tests/test_persistence.py` |

## Commit Plan

```
docs(tasks): add step-01 task breakdown
test(artifacts): failing tests for Enum types (01-01 red)
feat(artifacts): implement Enum types (01-01 green)
test(artifacts): failing tests for Artifact Pydantic models (01-02 red)
feat(artifacts): implement Artifact Pydantic models (01-02 green)
test(core): failing tests for WorkingMemory and Project models (01-03 red)
feat(core): implement WorkingMemory and Project models (01-03 green)
test(persistence): failing tests for Database connection and schema (01-04 red)
feat(persistence): implement SQLite schema and Database class (01-04 green)
test(persistence): failing tests for ProjectRepository (01-05/06 red)
feat(persistence): implement ProjectRepository (01-05/06 green)
```

## Key Design Decisions

- All artifact collections use `dict[str, <SubModel>]` — never lists — for stable RFC 6902 paths
- `EmmaAktion.parameter` is `dict[str, str]` for the prototype (OP-02 open; full parameter
  definition deferred until EMMA spec is available)
- `Database` uses `isolation_level=None` (autocommit off) and manages transactions explicitly
  via the `transaction()` context manager
- In-memory SQLite (`:memory:`) for all tests — no file I/O required
- WAL mode + foreign keys enforced in `Database.__init__`
