# AGENTS.md — Digitalisierungsfabrik

This file governs how AI agents work in this repository.

---

## Goal

Build a **working prototype** of the Digitalisierungsfabrik system as specified in
`digitalisierungsfabrik_systemdefinition.md` and architected in `hla_architecture.md`.

The prototype validates whether the AI-guided process elicitation approach yields valuable
results. It will serve as inspiration for a dev team building the actual product.

**Scope:** Working prototype — not production-grade, but well-structured enough to inspire
a production implementation. Correctness and clarity over optimization.

---

## Architecture

The canonical architecture is defined in `hla_architecture.md`. Follow it.

**Tech stack (binding):**

| Layer | Technology |
|---|---|
| Backend | Python ≥ 3.11, FastAPI ≥ 0.111 |
| Data models | Pydantic v2 |
| LLM client | anthropic SDK ≥ 0.25 |
| Persistence | SQLite (stdlib `sqlite3`) |
| Frontend | React ≥ 18, TypeScript ≥ 5, Vite ≥ 5 |
| API contract | OpenAPI 3.x (FastAPI auto-generated) |
| API type generation | `openapi-typescript` ≥ 7 (devDependency) |
| API client (frontend) | `openapi-fetch` ≥ 0.9 |
| Logging | structlog |

**Project structure** follows `hla_architecture.md` Section 6 exactly, with the following
binding addition: `frontend/src/types/api.ts` (referenced in HLA Section 6) does **not**
exist. It is replaced by the generated file `frontend/src/generated/api.d.ts` per ADR-001.

**New directories or structural changes** (files placed outside the paths defined in HLA
Section 6) require an ADR **before** any implementation work begins. No new directory
may be created speculatively.

**New dependencies** (Python packages or npm packages not listed in the Tech Stack above)
may not be added without an ADR. This applies to transitive additions too — do not quietly
expand `requirements.txt` or `package.json` with unlisted libraries.

### Deviations from Architecture

Any deviation from `hla_architecture.md` **must** be documented in an ADR **before**
implementation starts. Implementation must stop until the ADR is written and its status
is set to `accepted`. Reference the ADR in commit messages and inline comments where the
deviation occurs.

---

## Documentation

All decisions, open points, and architectural rationale go into `agent-docs/`.

### Folder structure

```
agent-docs/
  decisions/          # Architecture Decision Records (ADRs)
    ADR-001-*.md
    ADR-002-*.md
    ...
  tasks/              # Per-implementation-step task breakdowns
    step-01-*.md
    step-02-*.md
    ...
  open-points/        # Tracking of open points from hla_architecture.md Section 9
    open-points.md
```

### ADR Template (`agent-docs/decisions/ADR-NNN-title.md`)

```markdown
# ADR-NNN: Title

**Status:** proposed | accepted | superseded
**Date:** YYYY-MM-DD

## Context
What situation prompted this decision?

## Decision
What was decided?

## Reason
Why? What alternatives were considered?

## Consequences
What changes in the codebase? What risks does this introduce?

## SDD/HLA Reference
Which section does this affect?
```

---

## Definition of Done — NON-NEGOTIABLE

**Every story and every epic has a Definition of Done (DoD) checklist in its epic document.**

The following rules are absolute. No exceptions. No commits without compliance.

### Rule 1 — Run every DoD command, verify exit code 0

Before committing any story as done, **every single DoD command listed in the epic doc MUST be
executed and return exit code 0**. "It should work" is not sufficient. Run it. Check the output.

### Rule 2 — Every acceptance criterion needs a DoD checkbox

**Every acceptance criterion that mentions a specific file, directory, configuration value,
or structural requirement MUST have its own DoD checkbox** — not just the tool command that
runs on top of it.

Examples of what needs its own checkbox:
- `frontend/eslint.config.js` existiert → `- [ ] frontend/eslint.config.js existiert`
- `pyproject.toml` konfiguriert `[tool.mypy]` → `- [ ] pyproject.toml enthält [tool.mypy] strict=true`
- `src/components/` Verzeichnis existiert → `- [ ] frontend/src/components/ existiert`

A passing `npm run lint` does NOT implicitly verify that `eslint.config.js` has correct
content. Structural requirements must be checked explicitly.

### Rule 3 — Mark the checklist in the epic document

After verifying each DoD item:
- Mark it `- [x]` (green) if the command passes or file exists as specified
- Mark it `- [~] FAILED: <error summary>` (red) if it fails — then fix it before committing

**A story is only done when all its checkboxes are `[x]`.**

### Rule 4 — Never mark an epic done unless all its stories are done

An epic is complete when every story in it has all DoD checkboxes checked `[x]`.
Update the epic's **Status** section with date, test count, and commit references.

### Rule 5 — Key Deliverables must use exact HLA paths

Every **Key Deliverables** section in an epic document MUST reference the exact file paths
defined in `hla_architecture.md` Section 6. Invented or approximate paths are not allowed.

If an implementation deviates from HLA Section 6 paths, an ADR is required **before** writing
the epic document. The Key Deliverables section then references both the ADR and the actual path.

### Rule 6 — Pydantic model fields must be complete against the SDD field tables

When an epic story specifies Pydantic models, the acceptance criteria **must list every field**
from the corresponding SDD field table — not a subset.

Before writing or reviewing a story that defines a data model:
1. Locate the SDD field table for that model (e.g. SDD Section 5.3 for `Strukturschritt`).
2. Copy every row from that table into the story's acceptance criteria field list.
3. Cross-check: no SDD field may be absent from the story AC without explicit justification
   (e.g. "deferred to Epic N because it requires the Executor").

A passing `mypy` or `pytest` does NOT verify field completeness. Field coverage must be
checked manually against the SDD before marking a model story as done.

### Rule 7 — Backend stories that change logic must include tests

Any backend story that introduces or modifies logic **must** include or extend tests for
that logic. A story that changes backend code but adds no tests is **incomplete** —
regardless of whether existing tests still pass.

### The full DoD checklist for backend stories

These commands apply to **every backend story**. Run them from `backend/` with the venv activated:

```bash
ruff check .                               # exit 0
ruff format --check .                      # exit 0
python -m mypy . --explicit-package-bases  # exit 0
pytest --tb=short -q                       # exit 0, 0 failures
```

### The full DoD checklist for frontend stories

Run these from `frontend/`:

```bash
npm run lint          # exit 0
npm run format:check  # exit 0
npm run typecheck     # exit 0
```

---

## Development Workflow

### Implementation Order

Follow `hla_architecture.md` Section 8 strictly:

| Step | Content | Definition of Done |
|---|---|---|
| 1 | Pydantic models + SQLite schema + ProjectRepository | Project can be created, saved, loaded |
| 2 | Executor + Template schema | Patch applied; error triggers rollback |
| 3 | Orchestrator skeleton + Working Memory (stub modes) | Cycle runs, WM updated, persistence works |
| 4 | LLM client + ExplorationMode + ContextAssembler + OutputValidator | First LLM turn completes end-to-end |
| 5 | FastAPI backend (REST + WebSocket) | API endpoints testable without frontend |
| 6 | React frontend | Full user dialog in browser |
| 7 | Moderator + phase transition | Phase transition cycle complete |
| 8 | StructuringMode | |
| 9 | SpecificationMode | |
| 10 | ValidationMode + correction loop | |
| 11 | End-to-end run + stabilization | Full Exploration → Validation flow works |

Each step is a self-contained, testable increment. Do not start step N+1 before step N
passes its tests.

**Story isolation:** A story may only modify files that belong to its defined scope.
Unrelated changes — including "opportunistic" refactors, comment cleanup, or dependency
updates — are not allowed within a story commit. If an unrelated change is necessary,
it goes in a separate commit with its own justification.

Document each step in `agent-docs/tasks/step-NN-*.md` before starting.

### Commits

**See "Definition of Done — NON-NEGOTIABLE" above. All DoD commands must pass before any commit.**

Commit **frequently** — after every logical unit of work:

- After each green test batch
- After completing a module or class
- After each implementation step
- After each ADR is written

Commit message format:
```
<type>(<scope>): <short summary>

<body if needed>

Refs: ADR-NNN (if deviating from architecture)
```

Types: `feat`, `test`, `fix`, `docs`, `refactor`, `chore`

Examples:
```
feat(artifacts): implement Pydantic models with dict-keyed slots
test(executor): add RFC 6902 patch application and rollback tests
docs(adr): ADR-001 SQLite over JSON files
fix(orchestrator): correct mode transition on phase_complete flag
```

---

## Test-Driven Development

The entire backend is subject to TDD. Any backend story that introduces or modifies logic
requires tests. "I'll add tests later" is not acceptable — a story without tests for its
new logic is not done, regardless of whether the DoD tool commands pass.

The frontend is excluded from strict TDD but should have smoke tests.

### TDD Cycle

1. **Write a failing test** that captures the requirement from the SDD
2. **Write the minimum code** to make the test pass
3. **Refactor** if needed, keeping tests green
4. **Commit**

### Test locations

All backend tests live in `backend/tests/`. Mirror the source structure:

| Source | Test file |
|---|---|
| `core/executor.py` | `tests/test_executor.py` |
| `artifacts/models.py` + `artifacts/store.py` | `tests/test_artifacts.py` |
| `core/orchestrator.py` | `tests/test_orchestrator.py` |
| `artifacts/completeness.py` | `tests/test_completeness.py` |
| `persistence/project_repository.py` | `tests/test_persistence.py` |

### What to test

| Component | Key test scenarios |
|---|---|
| Executor | Valid patch applied; invalid path rejected; crash mid-patch → rollback to snapshot; preservation check; invalidation propagation |
| Artifacts | Dict-keyed slot access; completeness state calculation; Markdown rendering |
| Orchestrator | Mode selection from flags; 11-step cycle runs; WM updated after turn; persistence called |
| Persistence | Atomic transaction: all writes committed or none; project load after save returns identical state |
| LLM client | Mock-based: `complete()` called with correct args; streaming tokens yielded |

Use `pytest`. Use `pytest-asyncio` for async tests. Use in-memory SQLite (`:memory:`) for
persistence tests.

### Test quality rules — non-negotiable

These rules exist to prevent tests that pass trivially without proving anything.

**Rule T-1 — Every test must be falsifiable.**
Before committing a test, ask: "What code change would make this test fail?" If the answer
is "nothing reasonable", the test is not a test — it is noise. Replace it or delete it.

Tautological tests that must never be written:
- Tests that verify a property guaranteed by the language or framework (e.g. that a `StrEnum`
  member is a `str`, that Pydantic rejects a wrong type)
- Tests that call a function and only assert it does not raise, without checking the result
- Tests whose docstring describes behaviour X but whose assertions do not actually verify X

**Rule T-2 — Test the contract in both directions.**
Every component that accepts or rejects input needs both a happy-path test and a negative
test. A validator without an invalid-input test, a range check without an out-of-range test,
or a required field without a missing-field test, leaves half the contract untested.

**Rule T-3 — Assertions must be as tight as the requirement.**
Weak assertions hide bugs:
- Use `==` not `in` when the exact value is known
- Use `>` not `>=` when the requirement is "strictly after"
- When testing persistence, assert on data retrieved from the store — not on the in-memory
  object that was just written, which may reflect the write regardless of whether it persisted

**Rule T-4 — Coverage must match the acceptance criteria.**
If a story's AC lists N fields, scenarios, or cases, the tests must cover all N. A passing
test suite that covers only a subset of the AC is an incomplete test suite. Cross-check
the AC line by line before marking a story done.

**Rule T-5 — Test infrastructure, not just logic.**
Resource lifecycle bugs (connection leaks, unclosed files, missing cleanup) are not caught
by logic tests. Every story that introduces a resource (DB connection, file handle, external
client) must include a test verifying the resource is properly released. For FastAPI
dependencies, verify that generator-based cleanup (`yield` + `finally`) is used.

**Rule T-6 — Test error propagation, not just success.**
Every component that can fail (DB operations, LLM calls, network I/O) needs a test that
verifies error propagation. Bare `except Exception` that swallows errors is a bug.
Test that:
- Errors from lower layers propagate or are translated to meaningful error responses
- Error messages are non-empty and contain actionable information
- `recoverable` flags accurately reflect whether the user can retry

**Rule T-7 — Test boundary values.**
For every validated input (string lengths, numeric ranges, collection sizes), test:
- The exact boundary value (e.g. `max_length=200` → test with 200 AND 201)
- Empty input where non-empty is required
- The zero/null case

---

## Library-First Principle

Before implementing any non-trivial logic, check whether a battle-tested library already solves the problem.

**Rules:**

1. Prefer stdlib and already-listed tech stack dependencies over writing custom code.
2. If a library outside the tech stack would eliminate a meaningful chunk of custom code, write an ADR proposing it — do not add it silently.
3. Minimize lines of code written from scratch. More code = more bugs = more maintenance.

**Examples:**
- JSON merge logic: use `jsonpatch` (via ADR) rather than implementing RFC 6902 manually
- Async HTTP: use `httpx` rather than a hand-rolled client
- Token counting: use the Anthropic SDK's built-in utilities, not manual estimators
- Date/time handling: use `datetime` stdlib, not custom wrappers

A story that re-implements something a library does is a design defect, not a feature.

---

## Escalation Protocol

Autonomous execution is the goal — but not at the cost of building in the wrong direction.

**Escalate to the user before starting implementation when:**

1. The SDD is ambiguous or internally contradictory on a requirement the Epic must implement.
2. Two equally valid approaches exist and the choice has long-term architectural impact.
3. A required capability is not defined in the SDD and cannot be reasonably inferred.
4. An Epic would require a new dependency or directory structure that seems significant but no ADR exists.

**How to escalate:**
- Stop before implementing the affected story.
- Describe the ambiguity in one paragraph.
- Present 2–3 concrete options with trade-offs.
- Ask the user to choose.
- Once answered, record the decision as an ADR before proceeding.

**Do NOT escalate for:**
- Trivial choices (variable names, minor internal structure)
- Issues already resolved by existing ADRs
- Questions answerable by reading the SDD carefully

---

## File Size and Modularity

Keep files focused and readable. A human engineer would refactor proactively — so should an AI agent.

**Rules:**

1. **No source file should exceed 300 lines** (tests and generated files excluded).
2. If a file approaches 300 lines during implementation, split it:
   - Extract cohesive classes or functions into separate modules.
   - Use existing HLA Section 6 paths. If none fit, write an ADR first.
3. **One class = one responsibility.** Do not merge unrelated concerns into a single class.
4. Test files may be longer than source files, but each individual test function must be short and self-contained.
5. Refactoring commits must be **separate** from feature commits.

**Proactive refactoring is required when:**
- A file has grown beyond its original scope during an Epic.
- Multiple unrelated concerns share a module.
- Copy-paste patterns appear that signal a missing abstraction.

---

## Architecture Decision Records (ADRs) — When to Write One

ADRs are required for **all** of the following — not just architecture deviations:

| Trigger | Example |
|---|---|
| Deviation from `hla_architecture.md` | New directory, moved module |
| New dependency | Adding a Python package not in requirements.txt |
| Significant implementation design choice | Choice of algorithm, data structure, or pattern with long-term impact |
| SDD ambiguity resolved by interpretation | "The SDD says X but we interpreted it as Y because Z" |
| Explicit user decision (escalation outcome) | Any decision made after an escalation |

ADR status must be `accepted` before the implementation it governs begins. Reference the ADR number in commit messages and inline comments where the deviation or decision is visible.

---

## Key Design Constraints

These are **non-negotiable** — they come directly from the SDD and HLA:

1. **RFC 6902 JSON Patch** for all artifact write operations (SDD 5.7)
2. **Dict-keyed artifact slots** — never lists — for stable RFC 6902 paths (HLA Section 3.6)
3. **SQLite ACID transactions** for all project state writes — no partial state (FR-E-01)
4. **Structured output via Tool Use** — `tool_choice: {"type": "tool", "name": "apply_patches"}` — not prompt-only format instructions (HLA Section 2.5)
5. **Orchestrator is framework-agnostic** — it knows nothing about FastAPI or WebSocket
6. **No mode writes directly to artifacts or Working Memory** — all writes go through Executor
7. **LLM provider is config-only** — `LLM_PROVIDER=anthropic|ollama` in `.env`, no code change needed
8. **System language is German** — all dialogs and artifacts in German (SDD 1.3)

---

## API Contract (OpenAPI)

The REST interface between frontend and backend is governed by a machine-readable
OpenAPI 3.x contract. **This section is binding.** See `agent-docs/decisions/ADR-001-openapi-contract.md`
for the full rationale.

### Rules

1. **Backend exposes the live spec** at `GET /openapi.json` (FastAPI default — no extra code).
2. **All request and response shapes** are explicit Pydantic models in `backend/api/schemas.py`.
   Route handlers must declare typed parameters and return types; no `dict` or `Any` responses.
3. **Frontend types are generated**, never hand-written. The generated file is
   `frontend/src/generated/api.d.ts`. It must never be edited manually.
4. **Frontend API client** uses `openapi-fetch` initialised in `frontend/src/api/client.ts`.
   All REST calls go through this client; no hand-written `fetch` wrappers for API endpoints.
5. **Contract snapshot** lives at `api-contract/openapi.json` (committed to the repository).
   It is the source of truth for frontend development when the backend is not running.
6. **Regeneration command** (run from `frontend/`):
   ```bash
   npm run generate-api          # from running backend (http://localhost:8000/openapi.json)
   npm run generate-api:file     # from committed snapshot (api-contract/openapi.json)
   ```
7. **Every new endpoint** introduced in any epic must:
   - Add or update its Pydantic schema in `backend/api/schemas.py`
   - Export an updated snapshot: `GET http://localhost:8000/openapi.json > api-contract/openapi.json`
   - Regenerate types: `npm run generate-api:file` in `frontend/`
   - Commit `api-contract/openapi.json` and `frontend/src/generated/api.d.ts` together

8. **Co-update rule (non-negotiable):** Whenever `api-contract/openapi.json` changes,
   `frontend/src/generated/api.d.ts` **must** be regenerated and committed in the same
   commit. A commit that updates the spec without regenerating the types is invalid.
   A commit that updates the generated types without updating the spec is invalid.

### File locations

| File | Role | Editable? |
|---|---|---|
| `backend/api/schemas.py` | Pydantic request/response models | Yes — source of truth |
| `api-contract/openapi.json` | Committed OpenAPI snapshot | Only via regeneration |
| `frontend/src/generated/api.d.ts` | Generated TypeScript types | **Never** — auto-generated |
| `frontend/src/api/client.ts` | `openapi-fetch` client init | Yes |

---

## Environment Setup

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run tests
pytest

# Run backend
uvicorn main:app --reload

# Frontend
cd frontend
npm install
npm run generate-api:file   # generate TypeScript types from committed OpenAPI snapshot
npm run dev
```

Configuration via `backend/.env` (copy from `backend/.env.example`):

```
LLM_PROVIDER=anthropic
LLM_MODEL=claude-opus-4-6
LLM_API_KEY=sk-ant-...
DATABASE_PATH=./data/digitalisierungsfabrik.db
```

---

## Reading Large Documents

The SDD (~1600 lines) and HLA (~740 lines) are large. Never load them fully into
context unless there is a specific reason. Follow this protocol:

| Document | How to read |
|---|---|
| AGENTS.md | Always read in full — it is the rule set |
| `hla_architecture.md` | Read Section 6 (file structure) by default; read other sections on demand |
| `digitalisierungsfabrik_systemdefinition.md` | Read lines 6–82 (table of contents). Then: **always read Section 4 in full** (Funktionale Anforderungen, lines ~256–569) — it is the primary implementation contract. Additionally read the specific Sections referenced by the current story using `offset`/`limit`. |

Use `offset` and `limit` parameters when reading files to fetch specific line ranges.

---

## References

- `digitalisierungsfabrik_systemdefinition.md` — Full system requirements (SDD)
- `hla_architecture.md` — High-level architecture (binding)
- `hla_adversarial_review.md` — Critical review of earlier architecture draft; key issues
  already resolved in current HLA (SQLite, dict-keyed slots, Tool Use strategy)
- `agent-docs/decisions/` — ADRs for any deviations from HLA
- `agent-docs/decisions/ADR-001-openapi-contract.md` — OpenAPI contract for frontend–backend integration
- `agent-docs/open-points/open-points.md` — Tracking of HLA Section 9 open points
- `api-contract/openapi.json` — Committed OpenAPI 3.x snapshot (source of truth for frontend type generation)
