# Epic 04 – Exploration Mode & LLM Integration

## Summary

Replace the Exploration stub with a real `ExplorationMode` that calls the configured LLM
via the `LLMClient` abstraction. This epic also introduces the `ContextAssembler` (builds
the prompt from Working Memory) and `OutputValidator` (verifies the LLM's structured tool-use
output). After this epic a human can type a message and receive a genuine AI response that
begins populating the Exploration Artifact.

This epic corresponds to **Implementation Step 4** in `AGENTS.md` / `hla_architecture.md`.

## Goal

First end-to-end LLM turn: user message goes in, AI response comes back via the
Anthropic Tool Use API, the Exploration Artifact receives its first real content, and
everything is persisted.

## Testable Increment

- Running `pytest backend/tests/test_exploration_mode.py` with a live `ANTHROPIC_API_KEY`
  (or a recorded cassette / mock) → one full turn completes, artifact updated
- Alternatively: a small CLI test script (`python -m backend.scripts.test_turn`) sends a
  hard-coded user message and prints the AI reply + resulting artifact diff
- Observable without a frontend or WebSocket

## Dependencies

- Epic 03 (Orchestrator must be in place to wire the mode into the cycle)

## Key Deliverables

- `backend/llm/base.py` – `LLMClient` abstract interface + `LLMResponse` Pydantic model (HLA Section 6)
- `backend/llm/anthropic_client.py` – `AnthropicClient` implementation (HLA Section 6)
- `backend/llm/ollama_client.py` – `OllamaClient` stub (config-selectable, not required
  to be fully functional this epic) (HLA Section 6)
- `backend/llm/factory.py` – `create_llm_client()` factory (within HLA `backend/llm/` directory)
- `backend/core/context_assembler.py` – `ContextAssembler` upgrade (HLA Section 6)
- `backend/core/output_validator.py` – `OutputValidator` real implementation (HLA Section 6)
- `backend/core/artifact_router.py` – extracted artifact routing helpers (within HLA `backend/core/` directory)
- `backend/core/events.py` – WebSocket event Pydantic models (within HLA `backend/core/` directory; see ESCALATION-01)
- `backend/modes/exploration.py` – `ExplorationMode` real LLM implementation (HLA Section 6)
- `backend/prompts/exploration.md` – German system prompt for ExplorationMode (HLA Section 6)
- `backend/tests/test_exploration_mode.py` – integration test (mocked LLM, in-memory SQLite)
- `backend/.env.example` updated with `LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`

## OpenAPI Contract Note

This epic introduces no new REST API endpoints. However, the streaming event payloads
(`chat_token`, `chat_done`, `artifact_update`, `error`) that the orchestrator will emit
via WebSocket should be defined as Pydantic models in this epic (e.g. in
`backend/api/schemas.py` or a shared `backend/core/events.py`). Typed event models allow
Epic 05 to reference them directly in the WebSocket endpoint schema without rework, and
keep the generated OpenAPI spec accurate.

## Technical Debt to Resolve in This Epic

The following items from Epics 01–03 must be addressed during story design and implementation:

**DEBT-01 — ExplorationArtifact Pflicht-Slot-Initialisierung (FR-B-00)**
New projects currently have `ExplorationArtifact(slots={})` — empty. SDD FR-B-00 and Section 5.3
define 8 mandatory slots (`prozessausloeser`, `prozessziel`, `scope`, `beteiligte_systeme`,
`umgebung`, `randbedingungen`, `ausnahmen`, `prozesszusammenfassung`). `ExplorationMode` must
initialize these slots on the very first turn if they are not yet present. The story implementing
`ExplorationMode` must include acceptance criteria that verify all 8 slots exist after the first
turn, and a test for this initialization behaviour.

**DEBT-05 — Orchestrator file size (300-line limit)**
`backend/core/orchestrator.py` is at 299 lines. Any substantive addition in this epic
(dialog history integration, output validator wiring, context assembly updates) will exceed the
300-line limit defined in AGENTS.md. Before or during the story that extends the orchestrator,
extract cohesive helper methods or a sub-module. Target paths are within `backend/core/` as
defined in HLA Section 6. Create a separate refactoring commit if needed.

## Stories

> **Path Note — HLA Section 6 compliance**
>
> All stories use the exact HLA Section 6 paths. The Key Deliverables section has been
> updated (validation Step 2) to reflect these paths. No ADR is required for files added
> within existing HLA-defined directories (`backend/llm/`, `backend/core/`).
> New files within existing HLA directories: `backend/llm/factory.py`,
> `backend/core/artifact_router.py`, `backend/core/events.py` (see ESCALATION-01 for
> `events.py` placement confirmation).

---

### Story 04-01 — LLM Client Abstraction (base + AnthropicClient)

**As a** developer configuring the system,
**I want** a well-defined `LLMClient` abstract interface and a working `AnthropicClient` implementation,
**so that** all cognitive modes can call the LLM through a single stable contract without knowing the concrete provider, and swapping providers requires only a config change (FR-D-12).

#### Scope

- Create `backend/llm/base.py`: `LLMClient` abstract base class with `complete()` method
- Create `backend/llm/anthropic_client.py`: `AnthropicClient` implementing `LLMClient`
  - Uses the `anthropic` SDK (already in `requirements.txt` ≥ 0.25)
  - Calls Anthropic Messages API with Tool Use (`tool_choice: {"type": "tool", "name": "apply_patches"}`)
  - Returns a structured `LLMResponse` containing `nutzeraeusserung` (str) and `tool_input` (dict)
  - Reads `llm_api_key`, `llm_model` from `Settings` (injected, not read directly from env)
  - Logs request/response when `llm_log_enabled=True` (NFR-Observabilität, SDD 8.1.3)
- Create `backend/tests/test_llm_client.py`: unit tests with mocked `anthropic.Anthropic` client

**No `OllamaClient` in this story** — that is Story 04-02.

#### FR/NFR Traceability

- FR-A-02 (Tool Use API for LLM communication)
- FR-D-12 (LLM provider configurability — no code change to switch)
- NFR: SDD 8.1.1 (Wartbarkeit / Konfigurierbarkeit), 8.1.3 (Beobachtbarkeit)

#### Acceptance Criteria

1. `backend/llm/base.py` exists and contains `LLMClient` as an abstract base class (ABC).
2. `LLMClient` declares `async def complete(self, system: str, messages: list[dict], tools: list[dict] | None = None, tool_choice: dict | None = None) -> LLMResponse`.
3. `LLMResponse` is a Pydantic model with fields `nutzeraeusserung: str` and `tool_input: dict`.
4. `backend/llm/anthropic_client.py` exists and contains `AnthropicClient(LLMClient)`.
5. `AnthropicClient.complete()` sends a request to the Anthropic Messages API using the `anthropic` SDK.
6. `AnthropicClient.complete()` extracts the `text` block (before tool_use) as `nutzeraeusserung` and the `tool_use` block's `input` dict as `tool_input`.
7. `AnthropicClient.complete()` enforces `tool_choice: {"type": "tool", "name": "apply_patches"}` when `tool_choice` is not explicitly passed.
8. `AnthropicClient` reads `api_key` and `model` from the injected `Settings` instance — no hardcoded values.
9. When `settings.llm_log_enabled` is `True`, request system prompt, messages, and response are logged via `structlog`.
10. `backend/tests/test_llm_client.py` contains at least:
    - A positive test: mock `anthropic.Anthropic` returns a response with text block + tool_use block; `AnthropicClient.complete()` returns correct `LLMResponse`.
    - A negative test: mock returns response with no tool_use block; `AnthropicClient.complete()` raises `ValueError` (contract violation).
    - A negative test: mock raises `anthropic.APIStatusError`; `AnthropicClient.complete()` propagates the exception.
11. `backend/llm/base.py` is ≤ 300 lines.
12. `backend/llm/anthropic_client.py` is ≤ 300 lines.

#### Definition of Done

- [x] `backend/llm/base.py` exists and contains `LLMClient` as an abstract base class
- [x] `backend/llm/base.py` declares `LLMResponse` Pydantic model with fields `nutzeraeusserung: str` and `tool_input: dict`
- [x] `backend/llm/anthropic_client.py` exists and contains `AnthropicClient(LLMClient)`
- [x] `AnthropicClient.complete()` uses `tool_choice={"type": "tool", "name": "apply_patches"}` by default
- [x] `AnthropicClient.complete()` extracts `nutzeraeusserung` from the text content block and `tool_input` from the tool_use content block
- [x] `AnthropicClient` reads `api_key` and `model` exclusively from the injected `Settings` object
- [x] `backend/tests/test_llm_client.py` contains positive test, no-tool-use negative test, and API-error negative test
- [x] `ruff check .` passes (run from `backend/`)
- [x] `ruff format --check .` passes (run from `backend/`)
- [x] `python -m mypy . --explicit-package-bases` passes (run from `backend/`)
- [x] `pytest --tb=short -q` passes with 0 failures (run from `backend/`)

---

### Story 04-02 — OllamaClient Stub + Factory

**As a** developer running the system locally without internet access,
**I want** an `OllamaClient` stub registered in a factory function,
**so that** `LLM_PROVIDER=ollama` in `.env` produces a working (if limited) client without any code change (FR-D-12).

#### Scope

- Create `backend/llm/ollama_client.py`: `OllamaClient(LLMClient)` stub
  - `complete()` raises `NotImplementedError` with a clear message: "OllamaClient is not yet fully implemented. Set LLM_PROVIDER=anthropic."
  - This is intentional for the prototype — the stub is config-selectable but not functional
- Add `backend/llm/factory.py`: `create_llm_client(settings: Settings) -> LLMClient`
  - Returns `AnthropicClient(settings)` when `settings.llm_provider == "anthropic"`
  - Returns `OllamaClient(settings)` when `settings.llm_provider == "ollama"`
  - Raises `ValueError` for unknown providers
- Add tests in `backend/tests/test_llm_client.py` (extend Story 04-01 test file):
  - Factory returns `AnthropicClient` for `llm_provider="anthropic"`
  - Factory returns `OllamaClient` for `llm_provider="ollama"`
  - Factory raises `ValueError` for `llm_provider="unknown"`

#### FR/NFR Traceability

- FR-D-12 (LLM provider configurability — no code change to switch)
- SDD 8.1.1 (Wartbarkeit / Konfigurierbarkeit)

#### Acceptance Criteria

1. `backend/llm/ollama_client.py` exists and contains `OllamaClient(LLMClient)`.
2. `OllamaClient.complete()` raises `NotImplementedError` with a descriptive message.
3. `backend/llm/factory.py` exists and contains `create_llm_client(settings: Settings) -> LLMClient`.
4. `create_llm_client` returns `AnthropicClient` for `llm_provider="anthropic"` and `OllamaClient` for `llm_provider="ollama"`.
5. `create_llm_client` raises `ValueError` for any unrecognised provider string.
6. No mode, orchestrator, or any other module imports `AnthropicClient` or `OllamaClient` directly — all LLM access goes through the factory or the `LLMClient` interface.

#### Definition of Done

- [x] `backend/llm/ollama_client.py` exists and contains `OllamaClient(LLMClient)` raising `NotImplementedError`
- [x] `backend/llm/factory.py` exists with `create_llm_client(settings) -> LLMClient`
- [x] Factory returns correct type for `"anthropic"` and `"ollama"`
- [x] Factory raises `ValueError` for unknown provider string
- [x] Tests for all three factory cases added to `backend/tests/test_llm_client.py`
- [x] `ruff check .` passes (run from `backend/`)
- [x] `ruff format --check .` passes (run from `backend/`)
- [x] `python -m mypy . --explicit-package-bases` passes (run from `backend/`)
- [x] `pytest --tb=short -q` passes with 0 failures (run from `backend/`)

---

### Story 04-03 — Orchestrator Refactoring (DEBT-05)

**As a** developer extending the Orchestrator in this epic,
**I want** the Orchestrator's helper logic extracted into cohesive sub-modules,
**so that** `backend/core/orchestrator.py` stays under 300 lines after the additions required by Stories 04-05 and 04-06, and the 148 existing tests remain green.

#### Scope

`backend/core/orchestrator.py` is currently at 299 lines. This refactoring extracts cohesive groups of helpers into dedicated modules within `backend/core/` (all paths defined in HLA Section 6):

- Extract artifact routing helpers (`_infer_artifact_type`, `_get_artifact`, `_set_artifact`) into `backend/core/artifact_router.py`
- Extract invalidation logic (`_apply_invalidations`) into `backend/core/invalidation.py` (or keep within `artifact_router.py` if they stay under the 300-line limit together — the implementer must measure and decide; both files are within the HLA `backend/core/` path)
- `backend/core/orchestrator.py` imports these helpers; its public API (`process_turn`, `TurnInput`, `TurnOutput`) is unchanged
- No logic changes — pure refactoring. All 148 existing `pytest` tests must remain green.
- This story produces a **separate refactoring commit** before any feature additions.

> **Note on HLA paths:** `backend/core/artifact_router.py` and `backend/core/invalidation.py` are new files within the existing `backend/core/` directory. HLA Section 6 does not list every helper module; `backend/core/` is the correct location per the architecture. No ADR is required for adding helper modules within an existing HLA-defined directory.

#### FR/NFR Traceability

- DEBT-05 (Orchestrator file size limit from AGENTS.md Rule 2)
- FR-D-01 (Orchestrator as central control node — must remain coherent)
- NFR: SDD 8.1.1 (Wartbarkeit)

#### Acceptance Criteria

1. `backend/core/orchestrator.py` is ≤ 299 lines after refactoring.
2. `backend/core/artifact_router.py` exists and contains the artifact routing helpers extracted from the orchestrator.
3. `backend/core/orchestrator.py` imports and calls the extracted helpers — no duplication.
4. All 148 existing `pytest` tests pass without modification.
5. No logic is changed — only module boundaries move.
6. `backend/core/artifact_router.py` is ≤ 300 lines.

#### Definition of Done

- [x] `backend/core/orchestrator.py` line count is ≤ 299 (verify with `wc -l`)
- [x] `backend/core/artifact_router.py` exists and contains extracted artifact routing helpers
- [x] `backend/core/orchestrator.py` imports helpers from `artifact_router` (no duplication)
- [x] `ruff check .` passes (run from `backend/`)
- [x] `ruff format --check .` passes (run from `backend/`)
- [x] `python -m mypy . --explicit-package-bases` passes (run from `backend/`)
- [x] `pytest --tb=short -q` passes with exactly 148 tests, 0 failures (run from `backend/`)

---

### Story 04-04 — ContextAssembler Upgrade

**As a** cognitive mode receiving its context from the Orchestrator,
**I want** the `ModeContext` to carry all mandatory context fields defined in SDD 6.5.3,
**so that** the LLM system prompt is built from a fully-populated context and the existing dialog-history integration (FR-E-07, MUST-FIX-01) is verified to work correctly.

#### Scope

The existing `backend/core/context_assembler.py` already builds a `ModeContext` with dialog history from the DB. This story upgrades it to ensure **all** SDD 6.5.3 mandatory fields are wired:

1. **Verify dialog history integration (MUST-FIX-01):** confirm `dialog_history` is correctly populated from `ProjectRepository.load_dialog_history()` with `settings.dialog_history_n` turns (currently hardcoded to 20 — must read from `Settings`).
2. **Wire `working_memory` fields into context:** `ModeContext.working_memory` is already present. Add a `prompt_context_summary` helper function in `context_assembler.py` that formats the Working Memory summary for injection into the system prompt — covering `aktive_phase`, `aktiver_modus`, artifact slot summaries (count of filled/total slots per artifact), and `spannungsfelder`.
3. **Wire template schema into context:** `ModeContext` must carry the `ArtifactTemplate` for the active artifact. Add field `artifact_template: ArtifactTemplate` to `ModeContext` in `backend/modes/base.py`.
4. Update `build_context()` in `context_assembler.py` to populate `artifact_template` from `TEMPLATES[artifact_type]` based on `project.aktive_phase`.
5. Update `backend/tests/test_orchestrator.py` or add `backend/tests/test_context_assembler.py` to verify:
   - Dialog history is loaded with `dialog_history_n` turns (not the hardcoded 20)
   - `ModeContext.artifact_template` is correctly populated for each phase
   - `prompt_context_summary()` returns a non-empty string containing the active phase

#### FR/NFR Traceability

- FR-D-05 (Aktives Kontextmanagement — Orchestrator step 6: ContextAssembler)
- FR-E-07 (Dialog history — already implemented, verify correct N)
- SDD 6.5.3 (Kontext-Bestandteile — all mandatory fields)
- NFR: SDD 8.1.1 (Konfigurierbarkeit — N must be config-driven)

#### Acceptance Criteria

1. `build_context()` reads `dialog_history_n` from the `Settings` object (passed as parameter), not from a hardcoded constant.
2. `ModeContext` has a field `artifact_template: ArtifactTemplate` populated from `TEMPLATES` based on the active phase.
3. `context_assembler.py` exports a `prompt_context_summary(context: ModeContext) -> str` function that returns a German-language string covering: aktive Phase, aktiver Modus, slot-Zähler (befüllt/gesamt), aktive Spannungsfelder.
4. `prompt_context_summary()` returns a non-empty string for a minimal `ModeContext` (no slots filled).
5. Tests verify `dialog_history_n` is respected (not the old hardcoded value of 20).
6. Tests verify `artifact_template` is set to the exploration template during the exploration phase.
7. `backend/core/context_assembler.py` remains ≤ 300 lines.
8. `backend/modes/base.py` remains ≤ 300 lines after adding the `artifact_template` field.

#### Definition of Done

- [x] `build_context()` accepts a `settings: Settings` parameter and uses `settings.dialog_history_n`
- [x] `ModeContext` in `backend/modes/base.py` has field `artifact_template: ArtifactTemplate`
- [x] `context_assembler.py` exports `prompt_context_summary(context: ModeContext) -> str`
- [x] `prompt_context_summary()` output contains aktive Phase, aktiver Modus, and slot counts
- [x] Tests confirm `dialog_history_n` is respected (not hardcoded 20)
- [x] Tests confirm `artifact_template` matches phase
- [x] `backend/core/context_assembler.py` is ≤ 300 lines
- [x] `ruff check .` passes (run from `backend/`)
- [x] `ruff format --check .` passes (run from `backend/`)
- [x] `python -m mypy . --explicit-package-bases` passes (run from `backend/`)
- [x] `pytest --tb=short -q` passes with 0 failures (run from `backend/`)

---

### Story 04-05 — OutputValidator (real implementation)

**As a** developer operating the Orchestrator,
**I want** the `OutputValidator` to fully verify the LLM's tool-use response against the Output-Kontrakt,
**so that** invalid or hallucinated LLM outputs are caught before they reach the Executor, preventing corrupt artifact state (FR-B-09, FR-D-07, SDD 6.5.2).

#### Scope

Replace the Epic 03 stub in `backend/core/output_validator.py` with a real validator:

1. **Tool name check:** the response must have used the `apply_patches` tool (tool_input must be present and non-empty).
2. **Required fields check:** `tool_input` must contain a `patches` key with a list value.
3. **RFC 6902 syntax check:** each patch object in `patches` must have `op` (one of `add`, `replace`, `remove`, `move`, `copy`, `test`), `path` (string starting with `/`), and — for `add`/`replace` — a `value` key. Use `jsonpatch` library (already in `requirements.txt`) to validate syntax.
4. **Template schema check:** each patch's `(op, path)` must be valid per `ArtifactTemplate.is_valid_patch()`. The validator receives the active `ArtifactTemplate` as a parameter.
5. `validate()` signature changes to: `validate(output: ModeOutput, artifact_template: ArtifactTemplate) -> bool`.
6. Update the call site in `backend/core/orchestrator.py` to pass `context.artifact_template`.
7. Add `backend/tests/test_output_validator.py` with:
   - Positive: valid patch list with correct tool name and valid paths → returns `True`
   - Negative: empty `tool_input` (no tool used) → returns `False`
   - Negative: patch with invalid `op` → returns `False`
   - Negative: patch with path not in template → returns `False`
   - Negative: `add`/`replace` patch missing `value` field → returns `False`
   - Edge case: empty patches list (no writes this turn) → returns `True` (valid — mode may respond without writing)

#### FR/NFR Traceability

- FR-B-09 (Schreibkontrolle via RFC 6902 — validator is the gate before Executor)
- FR-D-07 (Orchestrator step 8: OutputValidator)
- SDD 6.5.2 (Output-Kontrakt)

#### Acceptance Criteria

1. `backend/core/output_validator.py` contains a real implementation (not the stub returning `True`).
2. `validate(output, artifact_template)` returns `False` when `output.patches` contains a patch with an invalid RFC 6902 `op`.
3. `validate(output, artifact_template)` returns `False` when a patch `path` is not accepted by `artifact_template.is_valid_patch()`.
4. `validate(output, artifact_template)` returns `False` when an `add` or `replace` patch is missing the `value` field.
5. `validate(output, artifact_template)` returns `True` when `output.patches` is an empty list (no writes this turn is valid).
6. `validate(output, artifact_template)` returns `True` for a well-formed patch with a valid path and correct `op`.
7. `backend/core/orchestrator.py` passes `context.artifact_template` to `validate()`.
8. `backend/core/output_validator.py` is ≤ 300 lines.
9. `backend/tests/test_output_validator.py` covers all 6 cases listed in Scope.

#### Definition of Done

- [x] `backend/core/output_validator.py` is a real implementation (stub comment removed)
- [x] `validate()` signature is `validate(output: ModeOutput, artifact_template: ArtifactTemplate) -> bool`
- [x] `validate()` returns `False` for invalid RFC 6902 op values
- [x] `validate()` returns `False` for paths not in the artifact template
- [x] `validate()` returns `False` for add/replace patches missing `value`
- [x] `validate()` returns `True` for empty patches list
- [x] `backend/core/orchestrator.py` passes `context.artifact_template` to `validate()`
- [x] `backend/tests/test_output_validator.py` exists with all 6 test cases
- [x] `backend/core/output_validator.py` is ≤ 300 lines
- [x] `ruff check .` passes (run from `backend/`)
- [x] `ruff format --check .` passes (run from `backend/`)
- [x] `python -m mypy . --explicit-package-bases` passes (run from `backend/`)
- [x] `pytest --tb=short -q` passes with 0 failures (run from `backend/`)

---

### Story 04-06 — ExplorationMode (real LLM implementation)

**As a** user starting a new project,
**I want** the ExplorationMode to call the real LLM via the Anthropic Tool Use API and initialize all 8 Pflicht-Slots on the first turn,
**so that** I receive a genuine AI-guided interview that begins populating the Exploration Artifact (FR-B-00, FR-A-02, SDD 6.6.1).

#### Scope

Replace the stub in `backend/modes/exploration.py` with the real implementation:

1. **Constructor:** `ExplorationMode(llm_client: LLMClient)` — injects the client (no direct import of `AnthropicClient`).
2. **Pflicht-Slot initialization (DEBT-01, FR-B-00):** on the first turn (when `context.exploration_artifact.slots` is empty or missing any of the 8 Pflicht-Slot IDs), generate an `add` patch for each missing slot with `completeness_status: "leer"` and the correct `titel` per SDD 5.3. The 8 slot IDs and titles are:
   - `prozessausloeser` → "Prozessauslöser"
   - `prozessziel` → "Prozessziel"
   - `scope` → "Scope"
   - `beteiligte_systeme` → "Beteiligte Systeme"
   - `umgebung` → "Umgebung"
   - `randbedingungen` → "Randbedingungen"
   - `ausnahmen` → "Ausnahmen"
   - `prozesszusammenfassung` → "Prozesszusammenfassung"
3. **System prompt:** load from `backend/prompts/exploration.md` (create the file). The prompt must be in German (FR-A-08) and must include:
   - Role description (Explorationsmodus)
   - The tool `apply_patches` schema (RFC 6902 patch list for the ExplorationArtifact)
   - The working memory summary (via `prompt_context_summary()` from Story 04-04)
   - The completeness state of all slots
   - A reminder that only `apply_patches` tool calls are accepted and `nutzeraeusserung` is the chat response
4. **Messages:** translate `context.dialog_history` into the Anthropic messages format (`[{"role": "user"|"assistant", "content": str}]`), appending the current user input as the final user message.
5. **LLM call:** call `self._llm_client.complete(system, messages, tools=[APPLY_PATCHES_TOOL], tool_choice={"type": "tool", "name": "apply_patches"})`. `APPLY_PATCHES_TOOL` is a constant in `exploration.py` (or a shared module) defining the JSON schema for the `apply_patches` tool.
6. **Output:** return `ModeOutput(nutzeraeusserung=response.nutzeraeusserung, patches=response.tool_input.get("patches", []), phasenstatus=..., flags=[])`.
7. **Phasenstatus logic:** if all 8 Pflicht-Slots have `completeness_status` other than `leer` → `nearing_completion`; else → `in_progress`. `phase_complete` is reserved for a future story.
8. `backend/modes/exploration.py` must remain ≤ 300 lines.
9. Create `backend/prompts/exploration.md` with the German system prompt.

#### FR/NFR Traceability

- FR-B-00 (Pflicht-Slots initialization on first turn — DEBT-01)
- FR-A-02 (Tool Use API for LLM communication)
- FR-A-08 (System language German — all prompts in German)
- SDD 6.6.1 (Explorationsmodus — cognitive mode definition)
- SDD 6.5.2 (Output-Kontrakt)

#### Acceptance Criteria

1. `backend/modes/exploration.py` no longer contains the stub comment.
2. `ExplorationMode.__init__` accepts `llm_client: LLMClient` — no direct import of `AnthropicClient`.
3. On the first turn (empty `slots` dict), `call()` returns patches that add all 8 Pflicht-Slots with correct `slot_id`, `titel`, `inhalt: ""`, and `completeness_status: "leer"`.
4. On subsequent turns (slots already initialized), `call()` does not re-add existing slots.
5. `call()` invokes `self._llm_client.complete()` with `tool_choice={"type": "tool", "name": "apply_patches"}`.
6. `backend/prompts/exploration.md` exists and is written in German.
7. `call()` returns `ModeOutput` with `phasenstatus=in_progress` when any slot has `completeness_status=leer`.
8. `call()` returns `ModeOutput` with `phasenstatus=nearing_completion` when all 8 Pflicht-Slots have `completeness_status` other than `leer`.
9. `backend/modes/exploration.py` is ≤ 300 lines.
10. Dialog history from `context.dialog_history` is correctly translated into Anthropic messages format.

#### Definition of Done

- [x] `backend/modes/exploration.py` stub comment removed; real implementation in place
- [x] `ExplorationMode.__init__` accepts `llm_client: LLMClient`
- [x] On first turn with empty slots, patches add all 8 Pflicht-Slots (slot_ids: `prozessausloeser`, `prozessziel`, `scope`, `beteiligte_systeme`, `umgebung`, `randbedingungen`, `ausnahmen`, `prozesszusammenfassung`)
- [x] All 8 Pflicht-Slot `add` patches use `completeness_status: "leer"` and the correct German `titel`
- [x] On subsequent turns, no `add` patches for already-existing slots
- [x] `backend/prompts/exploration.md` exists and is written in German
- [x] `phasenstatus=in_progress` when any Pflicht-Slot is `leer`
- [x] `phasenstatus=nearing_completion` when all Pflicht-Slots are non-`leer`
- [x] `backend/modes/exploration.py` is ≤ 300 lines
- [x] `ruff check .` passes (run from `backend/`)
- [x] `ruff format --check .` passes (run from `backend/`)
- [x] `python -m mypy . --explicit-package-bases` passes (run from `backend/`)
- [x] `pytest --tb=short -q` passes with 0 failures (run from `backend/`)

---

### Story 04-07 — Event Models for WebSocket Streaming

**As a** developer implementing the WebSocket endpoint in Epic 05,
**I want** typed Pydantic models for all streaming events the Orchestrator will emit,
**so that** Epic 05 can reference them directly in the WebSocket schema without rework, and the OpenAPI spec stays accurate (OpenAPI Contract Note in this epic).

#### Scope

- Create `backend/core/events.py` with Pydantic models for all WebSocket event types defined in HLA Section 3.1:

  | Model | Fields | Trigger |
  |---|---|---|
  | `ChatTokenEvent` | `event: Literal["chat_token"]`, `token: str` | LLM streaming token |
  | `ChatDoneEvent` | `event: Literal["chat_done"]`, `message: str` | Turn completed |
  | `ArtifactUpdateEvent` | `event: Literal["artifact_update"]`, `typ: str`, `artefakt: dict` | After each write operation |
  | `ProgressUpdateEvent` | `event: Literal["progress_update"]`, `phasenstatus: Phasenstatus`, `befuellte_slots: int`, `bekannte_slots: int` | After each write operation |
  | `DebugUpdateEvent` | `event: Literal["debug_update"]`, `working_memory: dict`, `flags: list[str]` | After each cycle |
  | `ErrorEvent` | `event: Literal["error"]`, `message: str`, `recoverable: bool` | LLM error, contract violation |

- Add a `WebSocketEvent` union type: `WebSocketEvent = ChatTokenEvent | ChatDoneEvent | ArtifactUpdateEvent | ProgressUpdateEvent | DebugUpdateEvent | ErrorEvent`
- No actual WebSocket implementation in this story — models only.
- Add `backend/tests/test_events.py` with serialisation round-trip tests for each event model.

#### FR/NFR Traceability

- FR-F-02 (Debug-Modus — debug_update event)
- FR-F-01 (Phasen- und Fortschrittsanzeige — progress_update event)
- FR-E-04 (Fehlerbehandlung bei LLM-Fehlern — error event)
- HLA Section 3.1 (WebSocket-Events Backend → Frontend)
- OpenAPI Contract Note (this epic)

#### Acceptance Criteria

1. `backend/core/events.py` exists.
2. `ChatTokenEvent`, `ChatDoneEvent`, `ArtifactUpdateEvent`, `ProgressUpdateEvent`, `DebugUpdateEvent`, `ErrorEvent` are all defined as Pydantic models.
3. Each model has a `event: Literal[...]` discriminator field.
4. `WebSocketEvent` union type is defined and exported.
5. Each model serialises to JSON correctly (verified by round-trip tests).
6. `backend/tests/test_events.py` has one round-trip test per event model (6 tests total).
7. `backend/core/events.py` is ≤ 300 lines.

#### Definition of Done

- [x] `backend/core/events.py` exists
- [x] All 6 event models defined: `ChatTokenEvent`, `ChatDoneEvent`, `ArtifactUpdateEvent`, `ProgressUpdateEvent`, `DebugUpdateEvent`, `ErrorEvent`
- [x] Each model has `event: Literal[...]` discriminator
- [x] `WebSocketEvent` union type exported from `backend/core/events.py`
- [x] `backend/tests/test_events.py` has 6 round-trip serialisation tests (one per model)
- [x] `backend/core/events.py` is ≤ 300 lines
- [x] `ruff check .` passes (run from `backend/`)
- [x] `ruff format --check .` passes (run from `backend/`)
- [x] `python -m mypy . --explicit-package-bases` passes (run from `backend/`)
- [x] `pytest --tb=short -q` passes with 0 failures (run from `backend/`)

---

### Story 04-08 — Integration Test: Full Turn Through Orchestrator

**As a** developer verifying the end-to-end LLM integration,
**I want** an integration test that sends a user message through the full Orchestrator cycle with a mocked LLM and asserts that all 8 Pflicht-Slots are initialized, a patch is applied, dialog history is written, and state is persisted,
**so that** I can confirm the complete Story 04 pipeline works correctly without needing a live Anthropic API key (FR-B-00, FR-E-07, FR-D-07).

#### Scope

Create `backend/tests/test_exploration_mode.py`:

1. **Test fixture:** in-memory SQLite project, `ExplorationMode` wired with a mock `LLMClient`.
2. **Mock LLM response:** the mock `LLMClient.complete()` returns an `LLMResponse` with:
   - `nutzeraeusserung`: a German assistant message
   - `tool_input`: `{"patches": [{"op": "replace", "path": "/slots/prozessausloeser/inhalt", "value": "Nutzer öffnet Anwendung"}]}`
3. **Test: first turn initializes 8 Pflicht-Slots** (`test_first_turn_initializes_pflicht_slots`):
   - Call `orchestrator.process_turn(project_id, TurnInput(text="Hallo"))`
   - Assert `project.exploration_artifact.slots` has exactly 8 keys
   - Assert all 8 Pflicht-Slot IDs are present
   - Assert `prozessausloeser` slot has `completeness_status="leer"` before the mock patch updates it (patch updates `inhalt`, not `completeness_status`)
4. **Test: patch applied and persisted** (`test_patch_applied_and_persisted`):
   - Call `orchestrator.process_turn(project_id, TurnInput(text="Der Prozess startet wenn..."))`
   - After the turn, reload the project from the repository
   - Assert `project.exploration_artifact.slots["prozessausloeser"].inhalt == "Nutzer öffnet Anwendung"`
5. **Test: dialog history written** (`test_dialog_history_written`):
   - Call `orchestrator.process_turn(project_id, TurnInput(text="Test"))`
   - Load `repository.load_dialog_history(project_id, last_n=10)`
   - Assert the list contains a `user` entry with `inhalt="Test"` and an `assistant` entry with the mock `nutzeraeusserung`
6. **Test: OutputValidator blocks invalid patch** (`test_output_validator_rejects_invalid_path`):
   - Mock LLM returns a patch with an invalid path (e.g. `"/slots/prozessausloeser/nonexistent_field"`)
   - Call `orchestrator.process_turn(...)`
   - Assert `TurnOutput.error` is not `None`
   - Assert the artifact is unchanged after the turn
7. All tests use in-memory SQLite (`:memory:`). No live API calls.

#### FR/NFR Traceability

- FR-B-00 (Pflicht-Slots initialization — DEBT-01)
- FR-D-07 (Orchestrator step 8: OutputValidator rejects invalid output)
- FR-E-07 (Dialog history persisted and loadable)
- FR-E-01 (Atomic persistence — reload from repo proves it)
- HLA Section 3.8 (Integration test for full LLM turn)

#### Acceptance Criteria

1. `backend/tests/test_exploration_mode.py` exists.
2. `test_first_turn_initializes_pflicht_slots`: asserts exactly 8 slots exist with the correct IDs.
3. `test_patch_applied_and_persisted`: reloads from repository and asserts the patched field matches the mock value.
4. `test_dialog_history_written`: asserts `user` and `assistant` turns are written to the DB.
5. `test_output_validator_rejects_invalid_path`: asserts `TurnOutput.error` is set and artifact is unchanged.
6. All tests use in-memory SQLite — no live API dependency.
7. Tests are independently runnable: `pytest backend/tests/test_exploration_mode.py`.

#### Definition of Done

- [x] `backend/tests/test_exploration_mode.py` exists
- [x] `test_first_turn_initializes_pflicht_slots` asserts all 8 Pflicht-Slot IDs are present
- [x] `test_patch_applied_and_persisted` reloads from repository and asserts patched `inhalt` value
- [x] `test_dialog_history_written` asserts both user and assistant dialog turns are in DB
- [x] `test_output_validator_rejects_invalid_path` asserts `TurnOutput.error` is set and artifact unchanged
- [x] All 4 tests use in-memory SQLite (`:memory:`)
- [x] No live API calls in any test in this file
- [x] `ruff check .` passes (run from `backend/`)
- [x] `ruff format --check .` passes (run from `backend/`)
- [x] `python -m mypy . --explicit-package-bases` passes (run from `backend/`)
- [x] `pytest --tb=short -q` passes with 0 failures (run from `backend/`)

---

## Epic Status

**Status:** Complete — all 8 stories implemented. 183 tests passing. Date: 2026-03-13.

**Escalation Points (review before implementation):**

1. **ESCALATION-01 — `backend/core/events.py` path:** HLA Section 6 does not list `backend/core/events.py` explicitly. It is placed in `backend/core/` (an HLA-defined directory) because events are framework-agnostic Pydantic models consumed by the Orchestrator layer, not API-layer schemas. If the user prefers `backend/api/schemas.py`, Story 04-07 must be updated accordingly. No ADR is currently required (no new directory), but the placement choice should be confirmed before implementation.

2. **ESCALATION-02 — `APPLY_PATCHES_TOOL` location:** Story 04-06 defines an `APPLY_PATCHES_TOOL` constant (the JSON tool schema sent to the Anthropic API). Its natural home is either in `backend/modes/exploration.py` (mode-specific) or a shared `backend/llm/tools.py` (reused by all modes). The choice has architectural impact on Stories 04+. The implementer must decide and document inline; an ADR is not required for an intra-`llm/` module.

3. **ESCALATION-03 — Story ordering dependency:** Story 04-05 (OutputValidator) changes the `validate()` signature to include `artifact_template`. This requires Story 04-04 (ContextAssembler upgrade adding `artifact_template` to `ModeContext`) to complete first. Story 04-06 (ExplorationMode) depends on Stories 04-01, 04-04, and 04-05. Story 04-08 (integration test) depends on all previous stories. The implementation order must be: **04-01 → 04-02 → 04-03 → 04-04 → 04-05 → 04-06 → 04-07 → 04-08** (04-07 can be done in parallel with 04-05/04-06).

4. **ESCALATION-04 — `backend/prompts/exploration.md` path:** HLA Section 6 lists `backend/prompts/exploration.md` explicitly. The existing `backend/` directory does not have a `prompts/` subdirectory. Creating it requires an HLA-aligned path check — the path IS in HLA Section 6, so no ADR is required. However, the implementer must verify the directory does not already exist before creating it.
