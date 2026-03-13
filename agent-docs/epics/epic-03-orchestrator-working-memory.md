# Epic 03 – Orchestrator & Working Memory

## Summary

Build the `Orchestrator` – the central control loop that drives every conversation turn –
and the `WorkingMemory` component that holds the operational state for a session. In this
epic the cognitive modes (Exploration, Structuring, etc.) are replaced with lightweight
stubs that return hard-coded responses, so the full 11-step orchestrator cycle can be
exercised and persisted without any LLM calls.

This epic corresponds to **Implementation Step 3** in `AGENTS.md` / `hla_architecture.md`.

## Goal

A fully wired orchestrator cycle: receive user input → determine active mode → call mode
(stub) → collect patch operations → apply via Executor → update Working Memory → persist
state. All without LLM or HTTP.

## Testable Increment

- `pytest backend/tests/test_orchestrator.py` → all tests pass, including:
  - A full turn executes without error
  - Working Memory is updated after each turn
  - State is persisted to (in-memory) SQLite and can be restored
  - Mode stub is called with correct inputs
- Observable via test assertions; no UI required

## Dependencies

- Epic 01 (models and persistence)
- Epic 02 (Executor for patch application)

## Key Deliverables

- `backend/core/orchestrator.py` – `Orchestrator` class with 11-step cycle + `TurnInput`/`TurnOutput`
- `backend/core/context_assembler.py` – stub ContextAssembler for Epic 03
- `backend/core/output_validator.py` – stub OutputValidator for Epic 03
- `backend/core/progress_tracker.py` – ProgressTracker (updates WM phasenstatus + slot counts)
- `backend/core/working_memory.py` – `WorkingMemory` class (already exists; no changes needed)
- `backend/modes/base.py` – abstract `BaseMode` interface + `Flag`, `ModeContext`, `ModeOutput`
- `backend/modes/exploration.py` – `ExplorationMode` stub (returns no-op patches)
- `backend/modes/structuring.py` – `StructuringMode` stub (returns no-op patches)
- `backend/modes/specification.py` – `SpecificationMode` stub (returns no-op patches)
- `backend/modes/validation.py` – `ValidationMode` stub (returns no-op patches)
- `backend/modes/moderator.py` – `Moderator` stub (returns no-op patches)
- `backend/artifacts/completeness.py` – `CompletenessCalculator`
- `backend/tests/test_orchestrator.py` – full-cycle integration tests + WM unit tests
- `backend/tests/test_completeness.py` – CompletenessCalculator tests

**Note:** No `stubs.py` file is created. Stub implementations live in the HLA-defined mode files
(`exploration.py`, `structuring.py`, etc.) under their final class names. Later epics replace
the stub bodies with real LLM-backed implementations.

## OpenAPI Contract Note

The `Orchestrator` and `WorkingMemory` are internal components with no direct API surface.
However, the `TurnInput` and `TurnOutput` types that `process_turn` accepts and returns
will become the payload types of the WebSocket messages in Epic 05. Define these as
Pydantic models (not plain dataclasses) so they can be exported as JSON schemas and
included in the OpenAPI spec without rework.

## Stories

---

### Story 03-01 — Mode Interface: Flag, ModeContext, ModeOutput, BaseMode

**User story:**

As a developer
I want a well-typed interface for all cognitive modes
So that the Orchestrator can call any mode interchangeably without knowing its implementation

**Acceptance Criteria:**

1. `backend/modes/base.py` exists and contains:

   - `Flag` StrEnum with exactly 6 values matching SDD 6.4.1:
     `phase_complete`, `needs_clarification`, `escalate`, `blocked`,
     `artefakt_updated`, `validation_failed`

   - `ModeContext` Pydantic model with fields:
     - `projekt_id: str`
     - `aktive_phase: Projektphase`
     - `aktiver_modus: str`
     - `exploration_artifact: ExplorationArtifact`
     - `structure_artifact: StructureArtifact`
     - `algorithm_artifact: AlgorithmArtifact`
     - `working_memory: WorkingMemory`
     - `dialog_history: list[dict]` — last N turns; `{role: str, inhalt: str, timestamp: str}`
     - `completeness_state: dict[str, CompletenessStatus]`

   - `ModeOutput` Pydantic model with fields:
     - `nutzeraeusserung: str`
     - `patches: list[dict]` — RFC 6902 patch operations, may be empty
     - `phasenstatus: Phasenstatus`
     - `flags: list[Flag]` — zyklus-lokale Steuerungsflags (SDD 6.4.1)

   - `BaseMode` abstract class:
     - `async def call(self, context: ModeContext) -> ModeOutput`
     - Raises `NotImplementedError` when called directly

2. All imports use package-relative paths consistent with existing code style
   (`from artifacts.models import ...`, `from core.working_memory import ...`)

3. No new dependencies introduced

**Definition of Done:**

- [x] `backend/modes/base.py` exists
- [x] `Flag` StrEnum has exactly 6 values as listed in SDD 6.4.1
- [x] `ModeContext` Pydantic model has all 9 fields with correct types
- [x] `ModeOutput` Pydantic model has `nutzeraeusserung`, `patches`, `phasenstatus`, `flags`
- [x] `BaseMode.call()` raises `NotImplementedError`
- [x] `backend/tests/test_orchestrator.py` covers: WorkingMemory field defaults,
      serialisation round-trip, Flag enum values, ModeOutput construction
- [x] `ruff check .` → exit 0
- [x] `ruff format --check .` → exit 0
- [x] `python -m mypy . --explicit-package-bases` → exit 0
- [x] `pytest --tb=short -q` → all tests pass

**Tests (added to `backend/tests/test_orchestrator.py`):**

- WorkingMemory default values: `befuellte_slots=0`, `bekannte_slots=0`, `flags=[]`
- WorkingMemory serialises to JSON and deserialises back without loss
- All 6 `Flag` enum values exist and have correct string values
- `ModeOutput` with `patches=[]` and `flags=[]` is valid
- `BaseMode.call()` raises `NotImplementedError` when called directly

---

### Story 03-02 — Stub Mode Implementations

**User story:**

As a developer
I want stub implementations of all five cognitive modes in the HLA-defined mode files
So that the Orchestrator can complete a full turn cycle without an LLM in this epic

**Acceptance Criteria:**

1. The following files exist in `backend/modes/`, each containing a stub class extending
   `BaseMode`. The class names are the final production names — later epics replace the
   stub body with real LLM-backed logic:

   | File | Class |
   |---|---|
   | `backend/modes/exploration.py` | `ExplorationMode` |
   | `backend/modes/structuring.py` | `StructuringMode` |
   | `backend/modes/specification.py` | `SpecificationMode` |
   | `backend/modes/validation.py` | `ValidationMode` |
   | `backend/modes/moderator.py` | `Moderator` |

2. Every stub's `async call(self, context: ModeContext) -> ModeOutput` returns:
   - `nutzeraeusserung`: a non-empty German placeholder string, e.g.
     `"[ExplorationMode Stub] Kein LLM-Aufruf in diesem Epic."`
   - `patches`: `[]` (empty — no artifact changes)
   - `phasenstatus`: `Phasenstatus.in_progress`
   - `flags`: `[]` (no control signals)

3. All 5 mode classes are importable from their respective files.

4. No `stubs.py` file is created (not in HLA Section 6).

**Definition of Done:**

- [x] `backend/modes/exploration.py` exists with `ExplorationMode(BaseMode)`
- [x] `backend/modes/structuring.py` exists with `StructuringMode(BaseMode)`
- [x] `backend/modes/specification.py` exists with `SpecificationMode(BaseMode)`
- [x] `backend/modes/validation.py` exists with `ValidationMode(BaseMode)`
- [x] `backend/modes/moderator.py` exists with `Moderator(BaseMode)`
- [x] Each class implements `async call()` returning valid `ModeOutput`
- [x] All stubs return `patches=[]`, `flags=[]`, `phasenstatus=in_progress`
- [x] `nutzeraeusserung` is non-empty
- [x] Tests verify each mode can be called and returns expected ModeOutput shape
- [x] `ruff check .` → exit 0
- [x] `ruff format --check .` → exit 0
- [x] `python -m mypy . --explicit-package-bases` → exit 0
- [x] `pytest --tb=short -q` → all tests pass

**Tests (added to `backend/tests/test_orchestrator.py`):**

- `ExplorationMode().call(context)` returns `ModeOutput` with `patches=[]`, `flags=[]`
- `Moderator().call(context)` returns `ModeOutput` with `patches=[]`, `flags=[]`
- All 5 mode classes are instances of `BaseMode`
- All modes return non-empty `nutzeraeusserung`

---

### Story 03-03 — CompletenessCalculator

**User story:**

As a developer
I want a CompletenessCalculator that derives slot counts and a completeness map from the three
artifacts
So that the Orchestrator can update Working Memory after every turn (SDD 6.7)

**Acceptance Criteria:**

1. `backend/artifacts/completeness.py` exists and contains `CompletenessCalculator` with:

   ```python
   def calculate(
       self,
       exploration: ExplorationArtifact,
       structure: StructureArtifact,
       algorithm: AlgorithmArtifact,
   ) -> tuple[dict[str, CompletenessStatus], int, int]:
       ...
   ```

   Returns `(completeness_state, befuellte_slots, bekannte_slots)`.

2. `completeness_state` maps every slot ID across all three artifacts to its
   `CompletenessStatus`. Key uniqueness: slot IDs within each artifact are unique by
   construction (dict-keyed). IDs from different artifacts may overlap — the map merges
   them; later artifacts overwrite earlier ones for duplicate keys.

3. `bekannte_slots`: total count of all slots across all three artifacts
   (sum of len(exploration.slots), len(structure.schritte), len(algorithm.abschnitte))

4. `befuellte_slots`: count of slots whose status is `teilweise`, `vollstaendig`, or
   `nutzervalidiert` (SDD 6.7). `leer` does not count.

5. All-empty artifacts: returns `({}, 0, 0)`

**Definition of Done:**

- [x] `backend/artifacts/completeness.py` exists with `CompletenessCalculator`
- [x] `calculate()` accepts all three artifact types and returns `(dict, int, int)`
- [x] `leer` status does NOT increment `befuellte_slots`
- [x] `teilweise`, `vollstaendig`, `nutzervalidiert` each increment `befuellte_slots`
- [x] `bekannte_slots` = sum of slot counts across all three artifacts
- [x] `completeness_state` contains one entry per slot across all three artifacts
- [x] `ruff check .` → exit 0
- [x] `ruff format --check .` → exit 0
- [x] `python -m mypy . --explicit-package-bases` → exit 0
- [x] `pytest --tb=short -q` → all tests pass

**Tests (`backend/tests/test_completeness.py`):**

- Empty artifacts: `({}, 0, 0)`
- Exploration: 2 slots (`leer`, `vollstaendig`) → `bekannte=2`, `befuellte=1`
- Structure: 3 steps (`leer`, `teilweise`, `nutzervalidiert`) → `bekannte=3`, `befuellte=2`
- Algorithm: 1 section (`vollstaendig`) → `bekannte=1`, `befuellte=1`
- All three artifacts populated: correct aggregated totals
- `completeness_state` contains all slot IDs from all three artifacts
- Slot with `leer` in completeness_state maps to `CompletenessStatus.leer`

---

### Story 03-04 — Orchestrator with 11-Step Turn Cycle

**User story:**

As a developer
I want an Orchestrator that implements the complete 11-step turn cycle from SDD 6.3
So that user input flows through mode call → executor → completeness update → persistence
in a single atomic operation

**Acceptance Criteria:**

1. `backend/core/orchestrator.py` exists and contains:

   - `TurnInput` Pydantic model:
     - `text: str`
     - `datei: str | None = None` — optional base64 file attachment

   - `TurnOutput` Pydantic model:
     - `nutzeraeusserung: str`
     - `phasenstatus: Phasenstatus`
     - `flags: list[str]` — flags from the mode output (for debug/observability only)
     - `working_memory: WorkingMemory` — updated state after this turn
     - `error: str | None = None` — set if a fatal error occurred; artifact unchanged

   - `Orchestrator` class:
     - `__init__(self, repository: ProjectRepository, modes: dict[str, BaseMode])`
     - `async def process_turn(self, project_id: str, input: TurnInput) -> TurnOutput`

2. `process_turn` implements the 11-step SDD 6.3 cycle:

   | Step | Implementation |
   |---|---|
   | 1. Load project | `repository.load(project_id)` — raises `ValueError` if not found |
   | 2. Update WM | Increment `working_memory.letzter_dialogturn` by 1 |
   | 3. Evaluate flags | Read flags from previous turn (stored in WM.flags for observability); determine if mode switch is needed |
   | 4. Determine mode | Look up `working_memory.aktiver_modus` in `self.modes`; fall back to `"exploration"` if not found |
   | 5. Build context | `ContextAssembler.build_context(project, completeness_state)` |
   | 6. Call mode | `await mode.call(context)` → `ModeOutput` |
   | 7. Apply patches | If `mode_output.patches` non-empty: call `Executor.apply_patches(artifact, patches)` for the relevant artifact; on failure: return `TurnOutput(error=..., working_memory=wm, nutzeraeusserung="", phasenstatus=phasenstatus.in_progress, flags=[])` without saving |
   | 8. Invalidations | If executor returned `invalidated_abschnitt_ids`: apply a second Executor call to set `algorithmus_status=invalidiert` on those algorithm sections (per SDD FR-B-04) |
   | 9. Completeness | `CompletenessCalculator().calculate(...)` → update `wm.completeness_state`, `wm.befuellte_slots`, `wm.bekannte_slots` |
   | 10. Progress | Update `wm.phasenstatus` from `mode_output.phasenstatus`; evaluate mode-switch flags (`phase_complete`, `escalate`, `blocked`) → update `wm.aktiver_modus` and `wm.vorheriger_modus` |
   | 11. Persist | `repository.save(project)` atomically |

3. Mode-switch logic (applied in step 10):
   - If `Flag.phase_complete` in `mode_output.flags` AND current mode is not `"moderator"`:
     set `wm.vorheriger_modus = wm.aktiver_modus`, `wm.aktiver_modus = "moderator"`
   - If `Flag.escalate` or `Flag.blocked` in `mode_output.flags`:
     same switch to moderator
   - Otherwise: `aktiver_modus` unchanged
   - Flags for the current turn are stored in `wm.flags` for observability
     (note: per SDD 6.4.1 flags are zyklus-lokal; the WM field serves debug purposes only)

4. `backend/core/context_assembler.py` exists with:
   - `build_context(project: Project, completeness_state: dict[str, CompletenessStatus]) -> ModeContext`
   - For Epic 03: builds `ModeContext` with `dialog_history=[]`
   - Will be extended with real dialog history lookup in Epic 04

5. `backend/core/output_validator.py` exists with:
   - `validate(output: ModeOutput) -> bool`
   - For Epic 03: always returns `True` (stubs always produce valid output)
   - Will enforce the full output contract in Epic 04

6. `backend/core/progress_tracker.py` exists with:
   - `update_working_memory(wm: WorkingMemory, phasenstatus: Phasenstatus, befuellte: int, bekannte: int) -> WorkingMemory`
   - Writes `phasenstatus`, `befuellte_slots`, `bekannte_slots` into WM and returns it

**Definition of Done:**

- [x] `backend/core/orchestrator.py` with `TurnInput`, `TurnOutput`, `Orchestrator`
- [x] `backend/core/context_assembler.py` (stub, builds ModeContext with empty history)
- [x] `backend/core/output_validator.py` (stub, always returns `True`)
- [x] `backend/core/progress_tracker.py` (functional, updates WM fields)
- [x] `process_turn()` executes all 11 steps in order
- [x] Executor called for non-empty patches; result applied to correct artifact in `project`
- [x] Invalidation writes applied when `invalidated_abschnitt_ids` is non-empty
- [x] Mode switch: `phase_complete` / `escalate` / `blocked` → `aktiver_modus = "moderator"`
- [x] On Executor failure: `TurnOutput.error` set, project NOT saved, artifact unchanged
- [x] After turn: `letzter_dialogturn` incremented in persisted WM
- [x] `ruff check .` → exit 0
- [x] `ruff format --check .` → exit 0
- [x] `python -m mypy . --explicit-package-bases` → exit 0
- [x] `pytest --tb=short -q` → all tests pass

**Tests (`backend/tests/test_orchestrator.py`):**

- Full turn with stub mode and no patches: returns `TurnOutput` with no error; project saved
- `letzter_dialogturn` incremented by 1 per turn after processing
- Correct stub mode is called based on `working_memory.aktiver_modus`
- Project reloaded after turn: `working_memory.letzter_dialogturn` matches expected value
- Completeness update: after turn, `wm.befuellte_slots` and `wm.bekannte_slots` reflect artifact state
- Mode switch on `phase_complete` flag: `aktiver_modus` changes to `"moderator"`,
  `vorheriger_modus` stores prior mode
- Mode switch on `escalate` flag: same moderator switch
- Unknown project ID: raises `ValueError`
- Executor error path: if patches are invalid, `TurnOutput.error` is set and artifact version
  is unchanged
