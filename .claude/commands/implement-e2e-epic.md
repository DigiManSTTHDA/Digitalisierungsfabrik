# Implement E2E Epic

You are the implementation agent for the **E2E test campaign**.

Your task is to implement the next unfinished E2E Epic (Epics 12–14)
in the `e2e/` directory — a standalone TypeScript project that tests
the Digitalisierungsfabrik system via WebSocket.

This is NOT production system code. It is a **test harness**.
Different rules apply than for the backend/frontend.

You must read:

- AGENTS.md — for general project rules (commit format, ADR discipline)
- `agent-docs/e2e-testkampagne-plan.md` — the test campaign plan
  (architecture, scenario format, TurnRecord format, evaluation criteria)
- the Epic document — read in full
- the epic run log in `agent-docs/epic-runs/` — check validation status
  and any corrections that were applied

Do NOT read the SDD or HLA unless a specific story references them
(e.g. for EMMA action types or flag names). The E2E epics are not
traceable to SDD/HLA.

------------------------------------------------
CONTEXT — WHAT THIS IS
------------------------------------------------

The E2E framework lives in `e2e/` at the repository root. It is:

- A standalone TypeScript project (separate `package.json`, `tsconfig.json`)
- NOT part of the backend (Python) or frontend (React)
- Tests run against a live backend via WebSocket + REST API
- Unit tests for evaluator logic run without a backend

Tech stack for `e2e/`:

| Concern        | Tool                        |
|----------------|-----------------------------|
| Runtime        | Node.js + `tsx`             |
| Language       | TypeScript (strict mode)    |
| WebSocket      | `ws` package                |
| Test runner    | `tsx --test` (node:test)    |
| Package mgmt   | npm                         |

------------------------------------------------
CORE RULES
------------------------------------------------

1. **File size limit: 400 lines** per source file (AGENTS.md general rule).
   Epic-specific limits may be stricter (check story ACs).
2. **No new npm dependencies** without asking the user first.
3. **All code in TypeScript with strict mode** — no `any` unless unavoidable.
4. **File paths must match the epic document** exactly.
5. **ADR-009 must exist** before creating `e2e/` directory (Epic 12 prerequisite).

------------------------------------------------
STEP 1 — IDENTIFY THE NEXT EPIC
------------------------------------------------

Check which E2E epic to implement:

1. Read `agent-docs/epic-runs/epic-12.md`, `epic-13.md`, `epic-14.md`
2. Find the first epic whose run log does NOT contain an implementation
   summary (only validation results = not yet implemented)
3. Read that epic's full document from `agent-docs/epics/`

If all E2E epics are implemented, inform the user.

------------------------------------------------
STEP 2 — PRE-FLIGHT CHECK
------------------------------------------------

Before writing code:

1. **ADR check (Epic 12 only):** Verify ADR-009 exists for `e2e/` directory.
   If not, create it first.
2. **Dependency check:** Verify epic dependencies are met:
   - Epic 12: backend WebSocket endpoint must exist (check `backend/api/websocket.py`)
   - Epic 13: Epic 12 must be implemented (check `e2e/framework/types.ts` exists)
   - Epic 14: Epic 12 must be implemented (check `e2e/framework/types.ts` exists)
3. **Scan for blockers:** Read each story's ACs. If anything references
   backend behavior you're unsure about, check the actual backend code
   (e.g. WebSocket message format, REST endpoints, flag names).

------------------------------------------------
STEP 3 — IMPLEMENT STORIES ONE BY ONE
------------------------------------------------

For each Story in the epic's implementation order:

1. **Read ACs and DoD completely.**
2. **Check what exists:** If this story modifies an existing file,
   read it first.
3. **Implement the code:**
   - Write clean, typed TypeScript
   - Follow the interfaces defined in `e2e/framework/types.ts`
   - Keep files within the size limit specified in the story AC/DoD
4. **Write tests (when the story requires them):**
   - Use `node:test` (import { describe, it } from 'node:test')
   - Use `node:assert/strict` for assertions
   - Tests for evaluator logic use synthetic data (no backend needed)
   - Tests for WebSocket client need a running backend (mark as integration)
5. **Run DoD commands:**
   ```bash
   cd e2e && npm run typecheck    # tsc --noEmit, exit 0
   ```
   For stories with tests:
   ```bash
   cd e2e && npx tsx --test framework/__tests__/*.test.ts
   ```
6. **Critic review (brief):**
   - Are all AC points addressed?
   - Are there obvious type errors or missing error handling?
   - Does the file exceed its size limit?
   - For evaluator logic: are thresholds and conditions correct per AC?
7. **Mark DoD checkboxes** as `[x]` in the epic document.
8. **Commit** with message format: `feat(e2e): <story summary>`

------------------------------------------------
STEP 3a — CRITIC REVIEW (after each story)
------------------------------------------------

After implementing a story, review your own code:

- Are all AC points covered? Cross-check line by line.
- Are TypeScript types correct (no `any`, no type assertions without reason)?
- Does error handling match what the AC specifies?
- For evaluator stories: are the threshold values exactly as specified?
- For reporter stories: does the Markdown output match the plan format?
- Is the file within its size limit?

Produce:

```
CRITIC REPORT — Story <id>
Issues found: <n>
- [issue 1]
...
```

Fix issues before proceeding.

------------------------------------------------
STEP 3b — MINI-AUDIT (after each story)
------------------------------------------------

Quick checks:

1. **File paths:** Match the epic's Key Deliverables exactly?
2. **Line counts:** Within limits specified in story AC?
3. **Exports:** Are all required classes/functions exported?
4. **Type consistency:** Do interfaces match `types.ts` definitions?
5. **No regressions:** Does `npm run typecheck` still pass?

Produce:

```
MINI-AUDIT — Story <id>
File paths: OK / VIOLATION
Line counts: OK / VIOLATION (<file>: <n> lines, limit: <m>)
Exports: OK / MISSING (<name>)
Types: OK / MISMATCH (<detail>)
Typecheck: OK / FAIL
```

------------------------------------------------
STEP 4 — VERIFY AGAINST BACKEND (when applicable)
------------------------------------------------

For stories that interact with the backend (WebSocket client, REST calls):

1. Check actual backend endpoint signatures:
   - `POST /api/projects` — request/response schemas
   - `GET /api/projects/{id}/artifacts` — response schema
   - `ws://host/ws/session/{id}` — message format
2. Check actual WebSocket event types in `backend/core/events.py`:
   - `ChatDoneEvent`, `ArtifactUpdateEvent`, `ProgressUpdateEvent`,
     `DebugUpdateEvent`, `ErrorEvent`
3. Check actual flag names in `backend/modes/base.py`:
   - `Flag` enum values (phase_complete, artefakt_updated, etc.)

Do NOT guess these — read the backend source.

------------------------------------------------
STEP 5 — INTEGRATION SMOKE TEST (Epic 12-05, Epic 13-05)
------------------------------------------------

For stories that require a running backend:

1. Inform the user that the smoke test needs a running backend.
2. Provide the exact command to run.
3. Do NOT mark the smoke test DoD checkbox — the user must verify manually.

------------------------------------------------
EPIC LOG UPDATE
------------------------------------------------

After all stories are implemented, append to:

`agent-docs/epic-runs/<epic-id>.md`

Include:

- implementation date
- stories implemented (with commit hashes)
- files created/modified
- ADRs written (if any)
- Critic issues found and fixed (per story)
- Mini-Audit results (per story)
- open items (e.g. smoke test pending manual verification)
