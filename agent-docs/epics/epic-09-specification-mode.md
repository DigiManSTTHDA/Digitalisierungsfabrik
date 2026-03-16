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

- `backend/modes/specification.py` – `SpecificationMode` (real LLM calls, HLA Section 6 path)
- Algorithm Artifact schema finalised in `backend/artifacts/models.py` (EMMA-compatible
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

---

### Story 09-01: ADR for OP-02 Resolution + Algorithm Artifact Schema Completion

**User Story:**
As a developer,
I want OP-02 (EMMA parameter schema) resolved via an ADR and the Algorithm Artifact schema
completed with the missing `prozesszusammenfassung` field,
so that the Specification Mode has a complete, well-defined data model to write to.

**Acceptance Criteria:**

1. `agent-docs/decisions/ADR-006-emma-parameter-schema.md` exists with status `accepted`.
   - Documents the decision: `EmmaAktion.parameter` remains `dict[str, str]` for the prototype
     because the full EMMA parameter specification is not yet available (SDD 8.3, OP-02).
   - Documents that `EmmaAktion.aktionstyp` uses a `StrEnum` `EmmaAktionstyp` with all 17
     values from SDD 8.3 (FIND, FIND_AND_CLICK, CLICK, DRAG, SCROLL, TYPE, READ, READ_FORM,
     GENAI, EXPORT, IMPORT, FILE_OPERATION, SEND_MAIL, COMMAND, LOOP, DECISION, WAIT, SUCCESS).
   - Documents that `EmmaAktion.nachfolger` remains `list[str]` (not single string) to support
     branching from DECISION actions.

2. `backend/artifacts/models.py` — `EmmaAktion.aktionstyp` field changed from `str` to
   `EmmaAktionstyp` (new StrEnum with all 17 SDD 8.3 values).

3. `backend/artifacts/models.py` — `AlgorithmArtifact` gains field
   `prozesszusammenfassung: str = ""` (SDD 5.5, FR-B-02 AK(2): "Prozesszusammenfassung —
   Freitext, technisch angereichert, LLM-generiert").

4. `backend/artifacts/template_schema.py` — `ALGORITHM_TEMPLATE` gains path pattern
   `/prozesszusammenfassung` with `allowed_ops=["replace"]`.

5. `agent-docs/open-points/open-points.md` — OP-02 status updated to `resolved` with
   reference to ADR-006.

6. All SDD 5.5 fields for `Algorithmusabschnitt` present: `abschnitt_id`, `struktur_ref`,
   `titel`, `status` (AlgorithmusStatus), `completeness_status` (CompletenessStatus),
   `aktionen` (dict[str, EmmaAktion]).

7. All SDD 5.5 fields for `EmmaAktion` present: `aktion_id`, `aktionstyp` (EmmaAktionstyp),
   `parameter` (dict[str, str]), `nachfolger` (list[str]), `emma_kompatibel` (bool),
   `kompatibilitaets_hinweis` (str | None).

**Definition of Done:**

- [ ] `agent-docs/decisions/ADR-006-emma-parameter-schema.md` exists with status `accepted`
- [ ] `EmmaAktionstyp` StrEnum in `backend/artifacts/models.py` with all 17 SDD 8.3 values
- [ ] `EmmaAktion.aktionstyp` typed as `EmmaAktionstyp` (not `str`)
- [ ] `AlgorithmArtifact.prozesszusammenfassung: str = ""` field exists
- [ ] `/prozesszusammenfassung` path in `ALGORITHM_TEMPLATE` with `allowed_ops=["replace"]`
- [ ] OP-02 marked as resolved in `agent-docs/open-points/open-points.md`
- [ ] `ruff check backend/` passes
- [ ] `ruff format --check backend/` passes
- [ ] `python -m mypy backend/ --explicit-package-bases` passes
- [ ] `pytest --tb=short -q` passes (existing tests still green)

---

### Story 09-02: Algorithm Artifact Schema Tests

**User Story:**
As a developer,
I want tests proving the Algorithm Artifact schema is complete and functional,
so that the data model is verified before building the mode on top of it.

**Acceptance Criteria:**

1. `backend/tests/test_models.py` contains tests for:
   - `EmmaAktionstyp` enum has exactly 17 members matching SDD 8.3 catalog.
   - `AlgorithmArtifact` with `prozesszusammenfassung` persists through repository
     save/load cycle (not just model_dump round-trip — test through `ProjectRepository`).
   - `Algorithmusabschnitt` with filled `aktionen` dict persists through repository
     save/load cycle with correct `aktionstyp` (EmmaAktionstyp value), `parameter`,
     `nachfolger`, `emma_kompatibel`, and `kompatibilitaets_hinweis` values.
   - Invalid `aktionstyp` value rejected by Pydantic validation (negative test, Rule T-2).
   - `AlgorithmArtifact.prozesszusammenfassung` defaults to empty string.

2. Tests are falsifiable (Rule T-1): each test would fail if the tested field were
   removed or its type changed.

**Definition of Done:**

- [ ] 5+ new tests in `backend/tests/test_models.py`
- [ ] Persistence round-trip test for `prozesszusammenfassung` via `ProjectRepository`
- [ ] Persistence round-trip test for `Algorithmusabschnitt` with `aktionen`
- [ ] Negative test: invalid `aktionstyp` rejected
- [ ] `ruff check backend/` passes
- [ ] `ruff format --check backend/` passes
- [ ] `python -m mypy backend/ --explicit-package-bases` passes
- [ ] `pytest --tb=short -q` passes

---

### Story 09-03: ContextAssembler Update for Specification Phase

**User Story:**
As a developer,
I want the ContextAssembler to include Algorithm Artifact statistics and the EMMA action
catalog in the prompt context summary for the Specification phase,
so that the SpecificationMode LLM has all necessary context.

**Acceptance Criteria:**

1. `backend/core/context_assembler.py` — `prompt_context_summary()` includes:
   - Algorithm Artifact slot counts: `Algorithmusabschnitte: {filled}/{total} befüllt`
   - Algorithm Artifact `prozesszusammenfassung` status: `befüllt` / `leer`
   - These lines appear for all phases (general context awareness).

2. A new helper function `emma_action_catalog_text() -> str` in `context_assembler.py`
   that returns a German-language listing of all 17 EMMA action types with descriptions
   (from SDD 8.3). This text is used by the specification system prompt.

3. The EMMA catalog text is derived from the `EmmaAktionstyp` enum — not hard-coded
   as a separate string. If the enum changes, the catalog text changes.

**Definition of Done:**

- [ ] `prompt_context_summary()` includes algorithm artifact slot counts
- [ ] `prompt_context_summary()` includes algorithm `prozesszusammenfassung` status
- [ ] `emma_action_catalog_text()` function exists and returns all 17 EMMA types
- [ ] EMMA catalog derived from `EmmaAktionstyp` enum members
- [ ] `ruff check backend/` passes
- [ ] `ruff format --check backend/` passes
- [ ] `python -m mypy backend/ --explicit-package-bases` passes
- [ ] `pytest --tb=short -q` passes

---

### Story 09-04: SpecificationMode LLM Implementation + System Prompt

**User Story:**
As a developer,
I want the SpecificationMode stub replaced with a full LLM-based implementation,
so that the system can convert Strukturschritte into EMMA-compatible Algorithmusabschnitte
via dialog with the user.

**Acceptance Criteria:**

1. `backend/modes/specification.py` — `SpecificationMode` class:
   - Accepts `LLMClient` via constructor (same pattern as `StructuringMode`).
   - `call()` builds system prompt from `backend/prompts/specification.md`.
   - System prompt includes: context summary, Structure Artifact content (read-only),
     current Algorithm Artifact slot status, EMMA action catalog, template schema paths.
   - Calls `llm_client.complete()` with `tools=[APPLY_PATCHES_TOOL]` and
     `tool_choice={"type": "tool", "name": "apply_patches"}` (HLA 2.5, FR-B-09).
   - Parses patches and phasenstatus from LLM response.
   - Applies deterministic guardrails: blocks `phase_complete` if any Strukturschritt
     has no corresponding Algorithmusabschnitt with `completeness_status != leer`.
   - Emits `Flag.phase_complete` when phasenstatus is `phase_complete`.

2. `backend/prompts/specification.md` — German system prompt:
   - Role: Spezifikationsmodus der Digitalisierungsfabrik.
   - Behavior: Works through Strukturschritte one by one (SDD 6.6.3), assigns EMMA
     actions, checks EMMA compatibility, marks non-compatible steps.
   - Includes placeholders: `{context_summary}`, `{structure_content}`,
     `{algorithm_status}`, `{emma_catalog}`.
   - Output contract: nutzeraeusserung + patches on algorithm artifact + phasenstatus.
   - Operationalisierbarkeit checklist (SDD 5.5): Aktion, Wie, Endzustand, Timeout,
     Fehlerbehandlung — plus context-dependent: Datenquelle, Datenziel, UI-Element, Dialoge.
   - Language: German (FR-A-08).
   - Constraint: Never overwrite existing Algorithmusabschnitte without user confirmation
     (analogous to SDD 6.6.2 constraint for structuring).

3. When called after ValidationMode: if `working_memory.validierungsbericht` is non-empty,
   it is included in the system prompt context (SDD 6.6.3: "arbeitet den Validierungsbericht
   gemeinsam mit dem Nutzer ab").

**Definition of Done:**

- [ ] `backend/modes/specification.py` replaces stub with full LLM implementation
- [ ] `SpecificationMode.__init__` accepts `LLMClient | None`
- [ ] `call()` uses `APPLY_PATCHES_TOOL` with `tool_choice`
- [ ] Guardrails block premature `phase_complete`
- [ ] `backend/prompts/specification.md` exists with German system prompt
- [ ] System prompt includes EMMA action catalog via `{emma_catalog}` placeholder
- [ ] System prompt includes operationalisierbarkeit checklist (5 mandatory + 4 contextual)
- [ ] System prompt includes output contract (patches on algorithm artifact)
- [ ] Validierungsbericht included when present in working memory
- [ ] `ruff check backend/` passes
- [ ] `ruff format --check backend/` passes
- [ ] `python -m mypy backend/ --explicit-package-bases` passes
- [ ] `pytest --tb=short -q` passes

---

### Story 09-05: SpecificationMode Tests — Multi-Turn Mocked Dialog

**User Story:**
As a developer,
I want comprehensive tests for the SpecificationMode with mocked LLM calls,
so that the mode's behavior is verified without real API calls.

**Acceptance Criteria:**

1. `backend/tests/test_specification_mode.py` contains 10+ tests:
   - `test_specification_produces_algorithm_patches` — LLM returns patches that add
     an Algorithmusabschnitt; verify patches in output.
   - `test_specification_uses_tool_choice` — verify `tool_choice={"type": "tool", "name": "apply_patches"}`
     is passed to `llm_client.complete()`.
   - `test_specification_system_prompt_contains_emma_catalog` — system prompt sent to LLM
     contains EMMA action type listing.
   - `test_specification_system_prompt_contains_structure_content` — system prompt includes
     Structure Artifact read-only content.
   - `test_specification_system_prompt_contains_operationalisierbarkeit` — system prompt
     includes the 5 mandatory operationalisierbarkeit questions.
   - `test_specification_guardrail_blocks_premature_phase_complete` — when Strukturschritte
     exist without corresponding Algorithmusabschnitte, `phase_complete` is downgraded.
   - `test_specification_guardrail_allows_phase_complete` — when all Strukturschritte have
     corresponding non-leer Algorithmusabschnitte, `phase_complete` passes through.
   - `test_specification_phasenstatus_in_progress` — normal turn returns `in_progress`.
   - `test_specification_includes_validierungsbericht` — when working_memory has
     `validierungsbericht`, it appears in system prompt.
   - `test_specification_error_on_llm_failure` — LLM error propagates correctly (Rule T-6).
   - `test_specification_no_llm_client_returns_stub` — None LLM client returns stub message.

2. All tests use mocked `LLMClient` — no real API calls.
3. Tests follow Rules T-1 through T-7.

**Definition of Done:**

- [ ] `backend/tests/test_specification_mode.py` exists with 10+ tests
- [ ] Mocked LLM — no real API calls
- [ ] Guardrail positive and negative tests
- [ ] System prompt content verification tests
- [ ] Error propagation test (Rule T-6)
- [ ] `ruff check backend/` passes
- [ ] `ruff format --check backend/` passes
- [ ] `python -m mypy backend/ --explicit-package-bases` passes
- [ ] `pytest --tb=short -q` passes

---

### Story 09-06: Frontend — Algorithm Artifact Rendering

**User Story:**
As a developer,
I want the ArtifactTab to render Algorithm Artifact entries with full detail
(EMMA actions, parameter tables, compatibility badges),
so that users can see the specification progress in the artifact pane.

**Acceptance Criteria:**

1. `frontend/src/components/ArtifactTab.tsx` — when `type === "algorithmus"`:
   - Shows `prozesszusammenfassung` if present (analogous to structure artifact rendering).
   - Each Algorithmusabschnitt rendered as a card with:
     - Title and `abschnitt_id`
     - `struktur_ref` reference displayed
     - `completeness_status` badge (same styling as exploration/structure)
     - `status` badge (aktuell/invalidiert/ausstehend) — invalidated sections visually
       marked (FR-F-05)
   - Each EMMA-Aktion within an Algorithmusabschnitt rendered as a sub-item with:
     - `aktionstyp` as a colored badge
     - `parameter` displayed as key-value pairs
     - `nachfolger` displayed
     - `emma_kompatibel` flag: green check if true, red warning if false
     - `kompatibilitaets_hinweis` shown when `emma_kompatibel === false`

2. Uses generated types from `frontend/src/generated/api.d.ts` — no hand-written
   TypeScript for EMMA action schemas.

**Definition of Done:**

- [ ] Algorithm artifact renders `prozesszusammenfassung` when present
- [ ] Algorithmusabschnitt cards show title, struktur_ref, completeness_status, status
- [ ] EMMA-Aktion sub-items show aktionstyp badge, parameters, nachfolger
- [ ] `emma_kompatibel` green/red indicator rendered
- [ ] `kompatibilitaets_hinweis` shown when incompatible
- [ ] Invalidated sections visually marked (FR-F-05)
- [ ] `npm run lint` passes
- [ ] `npm run format:check` passes
- [ ] `npm run typecheck` passes

---

### Story 09-07: OpenAPI Contract Regeneration

**User Story:**
As a developer,
I want the OpenAPI snapshot and generated TypeScript types regenerated after the
Algorithm Artifact schema changes,
so that frontend and backend stay in sync (ADR-001).

**Acceptance Criteria:**

1. `api-contract/openapi.json` updated to reflect:
   - `AlgorithmArtifact.prozesszusammenfassung` field
   - `EmmaAktionstyp` enum values in `EmmaAktion.aktionstyp`

2. `frontend/src/generated/api.d.ts` regenerated from the updated OpenAPI snapshot.

3. Both files committed together in the same commit (ADR-001 co-update rule).

4. `npm run typecheck` passes after regeneration.

**Definition of Done:**

- [ ] `api-contract/openapi.json` contains `prozesszusammenfassung` in AlgorithmArtifact
- [ ] `api-contract/openapi.json` contains `EmmaAktionstyp` enum values
- [ ] `frontend/src/generated/api.d.ts` regenerated
- [ ] Both files committed together
- [ ] `npm run lint` passes
- [ ] `npm run format:check` passes
- [ ] `npm run typecheck` passes
