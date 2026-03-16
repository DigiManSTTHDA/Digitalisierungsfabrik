# Epic 09b – Typed EMMA Parameters (OP-02 Close)

## Summary

Replace `EmmaAktion.parameter: dict[str, str]` with a per-action-type discriminated
union of typed Pydantic models. The EMMA parameter specification is now available in
`agent-docs/emma-parameter-extraction-result.md` (extracted 2026-03-16 from the
EMMA Studio 2.7 Benutzerhandbuch). This closes OP-02 as documented in ADR-006.

Additionally, the SpecificationMode system prompt is enriched with per-action-type
parameter documentation so the LLM generates structurally correct parameters.

This epic corresponds to the **OP-02 resolution** deferred in Epic 09 (ADR-006).

## Goal

The `EmmaAktion.parameter` field is validated by Pydantic against a per-action-type
schema at parse time. The SpecificationMode LLM receives a concise parameter reference
so it can generate correct parameters for all 19 EMMA action types. OP-02 is closed.

## Testable Increment

- `pytest backend/tests/` — all existing 328 tests still pass; 30+ new parameter
  model tests pass
- An `EmmaAktion` with `aktionstyp=FIND` and an invalid parameter dict (e.g. missing
  `gegenstand`) is rejected by Pydantic with a clear validation error
- An `EmmaAktion` with `aktionstyp=DECISION` and a correctly structured `regeln` list
  parses successfully through the full repository round-trip
- The SpecificationMode system prompt (`backend/prompts/specification.md`) contains
  a parameter reference table listing required/optional parameters per action type

## Dependencies

- Epic 09 complete (AlgorithmArtifact schema, SpecificationMode implementation)
- `agent-docs/emma-parameter-extraction-result.md` — parameter spec source

## Key Deliverables

- `backend/artifacts/parameter_models.py` — all 19 typed parameter model classes +
  `EmmaAktionParameter` union + `coerce_parameter` model validator
- `backend/artifacts/models.py` — `EmmaAktion.parameter` typed; `EmmaAktionstyp`
  extended with `NESTED_PROCESS`
- `backend/prompts/specification.md` — enriched with per-action parameter reference
- `backend/tests/test_parameter_models.py` — full parameter model test suite
- `agent-docs/decisions/ADR-006-emma-parameter-schema.md` — updated: OP-02 closed
- OpenAPI snapshot and frontend types regenerated

## OpenAPI Contract Note

`EmmaAktion.parameter` changes from `dict[str, str]` to a union type. This is a
breaking schema change in the OpenAPI spec. After implementing Story 09b-02:

1. Regenerate: `curl http://localhost:8000/openapi.json > api-contract/openapi.json`
2. Regenerate frontend types: `cd frontend && npm run generate-api:file`
3. Verify `tsc --noEmit` passes
4. Commit both files

---

## Stories

---

### Story 09b-01: Parameter Model Library

**User Story:**
As a developer,
I want all 19 EMMA action types to have typed Pydantic parameter models in a dedicated
module, based on the EMMA Studio 2.7 parameter specification,
so that parameter validation is available before the schema migration in 09b-02.

**Acceptance Criteria:**

1. New file `backend/artifacts/parameter_models.py` exists and contains:
   - One `BaseModel` subclass per action type, named `<Type>Parameter`:
     `FindParameter`, `FindAndClickParameter`, `ClickParameter`, `DragParameter`,
     `ScrollParameter`, `TypeParameter`, `ReadParameter`, `ReadFormParameter`,
     `GenAIParameter`, `ExportParameter`, `ImportParameter`, `FileOperationParameter`,
     `SendMailParameter`, `CommandParameter`, `LoopParameter`, `DecisionParameter`,
     `WaitParameter`, `SuccessParameter`, `NestedProcessParameter`.
   - `DecisionRule` sub-model (used by `DecisionParameter.regeln`).
   - `EmmaAktionParameter` union type (using `Union[...]` or `|` operator).
   - All required fields, optional fields with defaults, `Literal` types and
     `list` types exactly as specified in
     `agent-docs/emma-parameter-extraction-result.md`.

2. Key field correctness (spot-checks against spec):
   - `FindParameter.gegenstand: Literal["Objekt","Text","RegEx","Bild","Sprachen","Freeze"]` — required
   - `FindParameter.quelldokument: Literal["Bildschirm","Datei","Ergebnisfeld"] = "Bildschirm"` — optional with default
   - `FindParameter.minimaler_score: float = 0.9`
   - `DecisionParameter.regeln: list[DecisionRule]` — required, ≥1 element
   - `DecisionRule.nachfolger_id: str` — required
   - `LoopParameter.maximale_anzahl_loops: int` — required
   - `WaitParameter.timeout_ms: int` — required
   - `SuccessParameter` — no fields (empty model, `pass`)
   - `NestedProcessParameter.prozess_id: int` — required
   - `CommandParameter.capture_output: Literal["No","Output","Error","Both"] = "No"`

3. `EmmaAktionParameter` is defined as a type alias covering all 19 parameter
   models (not a discriminated union — discrimination is handled by `EmmaAktion`'s
   model validator in Story 09b-02).

4. Module has `from __future__ import annotations` and full type hints.
   `ruff check` and `mypy` pass on the new file.

5. `backend/tests/test_parameter_models.py` exists and contains ≥ 30 tests:
   - For every action type: at least one valid instantiation test.
   - For types with required fields: at least one rejection test (missing required
     field raises `ValidationError`).
   - `FindParameter` — `gegenstand="Objekt"` without `objektnummer` is valid
     (objektnummer is optional; business-level constraint is documented, not enforced
     by Pydantic to avoid over-constraining the LLM).
   - `DecisionParameter` — empty `regeln=[]` is rejected (min length 1 if enforced,
     or documented as must-have; use `Field(min_length=1)` if Pydantic v2 supports it
     on lists, otherwise document in constraints only).
   - `SuccessParameter` — instantiates with no arguments.
   - `LoopParameter(maximale_anzahl_loops=5)` — valid.
   - `WaitParameter(gegenstand="Zeit", timeout_ms=3000)` — valid.
   - `CommandParameter` — `capture_output` defaults to `"No"`.
   - `GenAIParameter(skill="inv_ext")` — valid with empty `skill_inputs`.

**Definition of Done:**

- [ ] `backend/artifacts/parameter_models.py` exists
- [ ] All 19 parameter model classes present with correct field names and types
- [ ] `DecisionRule` sub-model present
- [ ] `EmmaAktionParameter` union type present
- [ ] `backend/tests/test_parameter_models.py` exists with ≥ 30 tests
- [ ] All new tests pass
- [ ] `ruff check backend/` passes
- [ ] `ruff format --check backend/` passes
- [ ] `python -m mypy backend/ --explicit-package-bases` passes
- [ ] `pytest --tb=short -q` passes (all existing + new tests green)

---

### Story 09b-02: EmmaAktion Schema Migration

**User Story:**
As a developer,
I want `EmmaAktion.parameter` to use the typed union from 09b-01 instead of
`dict[str, str]`, with automatic type coercion via a model validator keyed on
`aktionstyp`, so that Pydantic validates parameters at parse time and OP-02 is closed.

**Acceptance Criteria:**

1. `backend/artifacts/models.py` — `EmmaAktion`:
   - `parameter` field type changed from `dict[str, str]` to `EmmaAktionParameter`
     (imported from `backend.artifacts.parameter_models`).
   - A `@model_validator(mode="before")` (or equivalent Pydantic v2 mechanism)
     maps each `EmmaAktionstyp` value to its `*Parameter` class and calls
     `model_cls.model_validate(raw)` if `parameter` is a plain dict.
   - The validator mapping covers all 19 action types including `NESTED_PROCESS`.
   - If `parameter` is already an instance of the correct model class, it passes
     through unchanged (idempotent).
   - If `aktionstyp` is not in the mapping, `parameter` is left as-is (forward
     compatibility: unknown types don't hard-fail at this layer).

2. `EmmaAktionstyp` enum in `backend/artifacts/models.py` gains:
   `NESTED_PROCESS = "NESTED_PROCESS"` (total: 19 members).

3. All existing tests in `backend/tests/` that construct `EmmaAktion` objects
   with raw dict parameters are migrated to use typed parameter dicts
   (i.e., dicts that pass validation for their respective model). Tests that
   intentionally test schema rejection are updated to use correctly typed dicts
   or `NestedProcessParameter`-style raw dicts. No test is weakened.

4. Repository round-trip: an `EmmaAktion` with `aktionstyp=DECISION` and a
   `DecisionParameter` (including `regeln` list) survives
   `ProjectRepository.save()` → `ProjectRepository.load()` with all fields intact.
   JSON serialisation uses `model_dump()` / `model_validate()` correctly for
   nested models.

5. `backend/artifacts/template_schema.py` — no path pattern changes required
   (the `parameter` field path `/abschnitte/{id}/aktionen/{id}/parameter` with
   `allowed_ops=["replace"]` remains valid; the entire parameter object is always
   replaced as a unit).

6. `agent-docs/decisions/ADR-006-emma-parameter-schema.md` — updated:
   - Status remains `accepted`.
   - Add a new `## Update (Epic 09b)` section noting OP-02 is now fully closed:
     `parameter` is no longer `dict[str, str]` but a typed discriminated union,
     migration completed, `NESTED_PROCESS` added to enum.
   - Reference `agent-docs/emma-parameter-extraction-result.md` as the spec source.

7. `agent-docs/open-points/open-points.md` — OP-02 status updated to `resolved
   (Epic 09b)` if the file exists; otherwise skip.

**Definition of Done:**

- [ ] `EmmaAktion.parameter` type is `EmmaAktionParameter` (not `dict[str, str]`)
- [ ] Model validator present and covers all 19 action types
- [ ] `EmmaAktionstyp` has 19 members including `NESTED_PROCESS`
- [ ] All existing tests migrated (no test weakened)
- [ ] Repository round-trip test for `DECISION` with `regeln` passes
- [ ] ADR-006 updated with Epic 09b closure note
- [ ] `ruff check backend/` passes
- [ ] `ruff format --check backend/` passes
- [ ] `python -m mypy backend/ --explicit-package-bases` passes
- [ ] `pytest --tb=short -q` passes (all 328+ tests green)

---

### Story 09b-03: SpecificationMode Prompt Enrichment

**User Story:**
As a developer,
I want the SpecificationMode system prompt to include a concise per-action-type
parameter reference, so that the LLM generates structurally correct `parameter`
objects without needing to infer valid field names.

**Acceptance Criteria:**

1. `backend/prompts/specification.md` gains a new section
   **"EMMA Aktionskatalog — Parameter-Referenz"** containing a compact table or
   list that for each of the 19 action types names:
   - The action type (Aktionstyp enum value)
   - Required parameters (name + allowed values / type)
   - Key optional parameters (name + default)
   - At least one minimal valid example (JSON object for `parameter`)

   The section is generated from `agent-docs/emma-parameter-extraction-result.md`
   (manual transcription of the essential subset — do not inject the full 1800-line
   document; aim for ≤ 120 lines of reference text).

2. `backend/core/context_assembler.py` — `emma_action_catalog_text()` function
   updated (or a new companion function `emma_parameter_reference_text()` added)
   that returns the parameter reference for injection into the prompt. The function
   must not hard-code strings but reference the parameter model classes from
   `backend.artifacts.parameter_models` to enumerate required vs. optional fields
   programmatically.

3. If `emma_parameter_reference_text()` is added as a new function, it is covered
   by a test in `backend/tests/test_context_assembler.py`:
   - `test_emma_parameter_reference_text_contains_all_types` — all 19 action types
     appear in the output.
   - `test_emma_parameter_reference_text_contains_required_fields` — for at least
     FIND, DECISION, LOOP: their required fields appear by name in the output.

4. The prompt change is purely additive — no existing system-prompt behaviour is
   removed or altered.

**Definition of Done:**

- [ ] `backend/prompts/specification.md` contains parameter reference section
- [ ] Reference section covers all 19 action types
- [ ] Reference section is ≤ 120 lines (concise, not a full dump)
- [ ] At least one minimal JSON example per action type in the prompt
- [ ] `emma_action_catalog_text()` or companion function covers parameter info
- [ ] 2+ new tests for the catalog/reference function
- [ ] `ruff check backend/` passes
- [ ] `ruff format --check backend/` passes
- [ ] `python -m mypy backend/ --explicit-package-bases` passes
- [ ] `pytest --tb=short -q` passes

---

### Story 09b-04: OpenAPI Contract Regeneration

**User Story:**
As a developer,
I want the OpenAPI contract and generated frontend TypeScript types updated to reflect
the new `EmmaAktion.parameter` schema, so that the frontend type-checks against the
new union type and the API contract is current.

**Acceptance Criteria:**

1. `api-contract/openapi.json` regenerated and committed. The schema for
   `EmmaAktion.parameter` in the spec no longer shows `additionalProperties: {type: string}`
   (old dict) but the union of typed parameter schemas.

2. `frontend/src/generated/api.d.ts` regenerated via
   `cd frontend && npm run generate-api:file` and committed.

3. `tsc --noEmit` in the frontend passes with the new types.

4. No frontend component changes required in this story — if the frontend currently
   renders `parameter` as a generic key-value table (which it does: AlgorithmArtifact
   rendering from Epic 09-06), that rendering remains valid for the union type since
   `model_dump()` still produces a dict. Verify this at the TypeScript level.

5. If `tsc --noEmit` fails because a frontend component accesses `parameter` in a
   way that breaks with the new union type, fix the component in this story.

**Definition of Done:**

- [ ] `api-contract/openapi.json` regenerated and committed
- [ ] `frontend/src/generated/api.d.ts` regenerated and committed
- [ ] `tsc --noEmit` passes
- [ ] `ruff check backend/` passes
- [ ] `pytest --tb=short -q` passes
- [ ] No frontend rendering regressions (manual smoke-test or existing frontend
      tests green)
