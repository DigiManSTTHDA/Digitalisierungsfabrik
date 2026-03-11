# Epic 09 – Specification Mode

## Summary

Implement `SpecificationMode`, the cognitive mode that converts the structured process
definition from the Structure Artifact into a technically precise Algorithm Artifact –
the EMMA RPA-ready specification. This mode produces the most detailed and technical
artifact: it spells out every input/output parameter, system interaction, decision logic,
and exception path required by an RPA tool to execute the process without human
interpretation.

This epic corresponds to **Implementation Step 9** in `AGENTS.md` / `hla_architecture.md`.

## Goal

After the Structuring phase completes, the user enters the Specification phase and the
Algorithm Artifact is incrementally populated with EMMA-compatible technical detail,
visible in the artifact pane as it grows. The user only needs to answer clarifying
questions; no technical knowledge is required from them.

## Testable Increment

- In the browser: starting from a completed Structure Artifact (can be seeded with test
  data), a few Specification-phase turns produce an Algorithm Artifact with at least:
  - One fully specified process step (inputs, outputs, system, action)
  - At least one exception / error path
- `pytest backend/tests/test_specification_mode.py` → a mocked multi-turn specification
  dialogue produces a non-empty, schema-valid Algorithm Artifact
- Open point OP-02 (EMMA parameter schema) must be resolved before this epic starts

## Dependencies

- Epic 08 (Structuring Mode must produce a complete Structure Artifact to work from)

## Key Deliverables

- `backend/modes/specification_mode.py` – `SpecificationMode` (real LLM calls)
- Algorithm Artifact schema finalised in `backend/core/models.py` (EMMA-compatible
  slots as dict-keyed entries)
- `backend/core/context_assembler.py` updated – Specification-phase context window
  (includes Structure Artifact as reference)
- `frontend/src/components/ArtifactPane.tsx` updated – renders Algorithm Artifact fields
  (steps with full parameter tables) in a readable format
- `backend/tests/test_specification_mode.py` – multi-turn specification tests
- ADR resolving OP-02 committed to `agent-docs/decisions/`

## OpenAPI Contract Note

This epic finalises the Algorithm Artifact schema in `backend/core/models.py`, including
the resolution of OP-02 (EMMA parameter schema). The finalised schema directly affects the
OpenAPI spec because the Algorithm Artifact is returned in `GET /api/projects/{id}/artifacts`.

After schema finalisation:

1. Regenerate the OpenAPI snapshot: `curl http://localhost:8000/openapi.json > api-contract/openapi.json`
2. Regenerate frontend types: `cd frontend && npm run generate-api:file`
3. Commit both `api-contract/openapi.json` and `frontend/src/generated/api.d.ts`
4. Verify `tsc --noEmit` passes

The `ArtifactPane.tsx` update that renders Algorithm Artifact fields (parameter tables,
EMMA actions) must use the generated types — no hand-written TypeScript for EMMA action
schemas.

## Stories

_To be defined before this epic begins._
