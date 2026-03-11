# Epic 08 – Structuring Mode

## Summary

Implement `StructuringMode`, the cognitive mode responsible for transforming the free-text
Exploration Artifact into a structured, BPMN-like process definition stored in the
Structure Artifact. The mode drives a dialogue that clarifies sequence, decision points,
roles, and sub-processes, and emits JSON Patch operations to incrementally build the
Structure Artifact.

This epic corresponds to **Implementation Step 8** in `AGENTS.md` / `hla_architecture.md`.

## Goal

After the Exploration phase completes and the Moderator triggers a phase transition, the
user enters a structured dialogue in the Structuring phase and the Structure Artifact is
progressively populated with process steps, flows, roles, and decision points – all visible
in real time in the artifact pane.

## Testable Increment

- In the browser: starting from a completed Exploration phase (can be seeded with test
  data), the user sees the Structuring phase dialogue begin; after a few turns the
  Structure Artifact pane shows at least:
  - A list of process steps
  - At least one decision point or flow connection
- `pytest backend/tests/test_structuring_mode.py` → a mocked multi-turn structuring
  dialogue produces a non-empty, schema-valid Structure Artifact

## Dependencies

- Epic 07 (Moderator must be able to trigger the transition into Structuring)

## Key Deliverables

- `backend/modes/structuring_mode.py` – `StructuringMode` (real LLM calls, Tool Use output)
- Structure Artifact schema finalised in `backend/core/models.py` (steps, flows, roles,
  decision points as dict-keyed slots)
- `backend/core/context_assembler.py` updated – Structuring-phase context window
- `frontend/src/components/ArtifactPane.tsx` updated – renders Structure Artifact fields
  (steps, flows, decision points) in a readable format
- `backend/tests/test_structuring_mode.py` – multi-turn structuring tests

## OpenAPI Contract Note

This epic finalises the Structure Artifact schema in `backend/core/models.py`. Any new
field added to the Structure Artifact's Pydantic model will automatically appear in the
OpenAPI spec the next time it is regenerated.

After schema finalisation:

1. Regenerate the OpenAPI snapshot: `curl http://localhost:8000/openapi.json > api-contract/openapi.json`
2. Regenerate frontend types: `cd frontend && npm run generate-api:file`
3. Commit both `api-contract/openapi.json` and `frontend/src/generated/api.d.ts`
4. Verify `tsc --noEmit` passes

The `ArtifactPane.tsx` update that renders Structure Artifact fields must use the generated
types for all artifact-related data — do not introduce local TypeScript interfaces that
duplicate fields from the generated spec.

## Stories

_To be defined before this epic begins._
