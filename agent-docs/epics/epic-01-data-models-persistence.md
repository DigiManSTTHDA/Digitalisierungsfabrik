# Epic 01 – Data Models & Persistence

## Summary

Define every Pydantic v2 model that the system will use (artifacts, working memory, project
state) and implement the SQLite persistence layer via `ProjectRepository`. This gives all
future components a stable, typed data contract and a reliable way to save and restore state.

This epic corresponds to **Implementation Step 1** in `AGENTS.md` / `hla_architecture.md`.

## Goal

A fully-typed data layer: Pydantic models for all three artifact types and for working memory,
backed by a SQLite schema with ACID transactions and a `ProjectRepository` that can create,
save, load, and list projects.

## Testable Increment

- A Python test (or short script) can:
  1. Create a new project via `ProjectRepository`
  2. Save it to SQLite
  3. Reload it from SQLite
  4. Assert that all fields round-trip correctly (including nested artifact schemas)
- `pytest backend/tests/test_repository.py` → all tests pass
- No LLM calls or HTTP server required

## Dependencies

- Epic 00 (project skeleton with working test runner)

## Key Deliverables

- `backend/core/models.py` – Pydantic v2 models for:
  - `ExplorationArtifact`
  - `StructureArtifact`
  - `AlgorithmArtifact`
  - `WorkingMemory`
  - `Project`
- `backend/core/schema.sql` (or inline in repository) – SQLite DDL
- `backend/core/repository.py` – `ProjectRepository` with create / save / load / list
- `backend/tests/test_models.py` – model validation tests
- `backend/tests/test_repository.py` – persistence round-trip tests (in-memory SQLite)

## OpenAPI Contract Note

The Pydantic models defined in this epic (`ExplorationArtifact`, `StructureArtifact`,
`AlgorithmArtifact`, `WorkingMemory`, `Project`) form the **domain model** that the API
layer (Epic 05) will reference. Design them for clean JSON serialisation:

- Use explicit field types (no `Any`, no bare `dict` without type parameters where avoidable).
- All models must pass `model.model_json_schema()` without errors — FastAPI uses this to
  build the OpenAPI spec.
- These models are **not** the API schemas (those live in `backend/api/schemas.py`); they
  are the internal domain types. The API schemas in Epic 05 will compose or reference them.

## Stories

_To be defined before this epic begins._
