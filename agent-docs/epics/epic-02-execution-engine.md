# Epic 02 – Execution Engine (Executor + JSON Patch)

## Summary

Implement the `Executor` – the only component allowed to write to artifacts. All artifact
mutations go through the Executor as RFC 6902 JSON Patch operations. Invalid or failing
patches must trigger a full rollback, leaving artifacts in their previous valid state.

This is a critical correctness boundary: no other component ever writes directly to an
artifact. This epic also defines the `ArtifactTemplate` schema that patches must conform to.

This epic corresponds to **Implementation Step 2** in `AGENTS.md` / `hla_architecture.md`.

## Goal

A battle-tested Executor that applies JSON Patch operations to artifacts atomically, validates
patches against the artifact schema, and rolls back cleanly on any failure.

## Testable Increment

- `pytest backend/tests/test_executor.py` → all tests pass, including:
  - Valid patch applied → artifact updated correctly
  - Invalid patch (bad path) → artifact unchanged, error returned
  - Partially valid patch sequence → rollback to pre-patch state
- No HTTP server or LLM required; pure unit tests

## Dependencies

- Epic 01 (Pydantic models must exist for the Executor to operate on)

## Key Deliverables

- `backend/core/executor.py` – `Executor` class
  - `apply_patch(artifact, patch_ops) → Result`
  - RFC 6902 validation before application
  - Rollback on failure
- `backend/core/templates.py` – `ArtifactTemplate` schema definitions (allowed patch paths
  per artifact type)
- `backend/tests/test_executor.py` – comprehensive patch apply / rollback tests

## OpenAPI Contract Note

The `Executor` is an internal component — it has no API surface of its own. However, the
patch-operation schema it validates against will be referenced in the WebSocket message
contract defined in Epic 05. When defining `ArtifactTemplate` in this epic, ensure patch
path structures are documented with Python docstrings/comments so they can be accurately
described in the OpenAPI spec's WebSocket message schemas later.

## Stories

_To be defined before this epic begins._
