# Implement Next Epic

You are the implementation agent.

Your task is to implement the **next unfinished Epic** in the repository
according to the project rules.

The rules in AGENTS.md are authoritative and non-negotiable.

You must read and follow:

- AGENTS.md — read in full (always relevant, manageable size)
- hla_architecture.md — read Section 6 only (file structure); read other
  sections on demand if a specific architectural question arises
- digitalisierungsfabrik_systemdefinition.md — do NOT read in full;
  read lines 6–82 (table of contents) to orient yourself, then:
  **always read Section 4 completely** (FR lines ~256–569) — it is the
  primary implementation contract for every story.
  Additionally read story-specific sections (5, 6, 7) via offset/limit.
- the Epic document — read in full

Never assume compliance — always verify.

------------------------------------------------
CORE NON-NEGOTIABLES
------------------------------------------------

Before writing any code, confirm the following:

1. AGENTS.md has been read completely.
2. Architecture in `hla_architecture.md` is binding.
3. Requirements in the SDD must be implemented fully.
4. Definition of Done rules must be followed exactly.
5. Library-First principle applies — use existing libraries before writing custom logic.
6. File size limit of 300 lines per source file must be respected.

Important reminders:

- No architecture deviations without ADR.
- No new dependencies without ADR.
- No invented directory structure.
- File paths must match the architecture exactly.
- Write an ADR for every significant design decision, not just deviations.

------------------------------------------------
STEP 1 — ESCALATION CHECK (before any code)
------------------------------------------------

Before writing a single line of code, scan every story for ambiguities.

For each story:

1. Identify the SDD section it implements.
2. Verify the SDD provides a clear, unambiguous specification.
3. Check whether the required capability can be reasonably inferred.

If any story has a genuine ambiguity that cannot be resolved by
careful reading:

**STOP. Escalate to the user.**

- Describe the ambiguity in one paragraph.
- Present 2–3 concrete implementation options with trade-offs.
- Wait for the user's decision.
- Record the decision as an ADR before proceeding.

Do NOT escalate for trivial choices. Only escalate when going in
the wrong direction would cause significant rework.

------------------------------------------------
STEP 2 — LIBRARY SEARCH (before each story)
------------------------------------------------

Before implementing any non-trivial logic, ask:

"Does a battle-tested library already solve this?"

Check:
- stdlib (collections, itertools, pathlib, functools, etc.)
- Already-listed tech stack packages (Pydantic, FastAPI, structlog, httpx, etc.)
- If a new package would eliminate significant custom code: write an ADR and propose it

Do NOT add packages to requirements.txt without an ADR.

------------------------------------------------
STEP 3 — IMPLEMENT STORIES ONE BY ONE
------------------------------------------------

For each Story in order:

1. Read the acceptance criteria completely.
2. Identify the SDD section it implements — read only that section
   (use offset/limit on the SDD file, not the full document).
3. Run the library search (Step 2) for this story's logic.
4. **Design tests before writing them (test design phase).**
   Before writing any test code, list 3–8 behaviours this story must
   guarantee. Each behaviour is one sentence starting with "It must …"
   or "When … then …". Focus on:
   - What happens on valid input (happy path with **specific** expected values)
   - What happens on invalid/missing/boundary input (error paths)
   - What state changes are observable after the operation
   - What side effects occur (DB writes, mode switches, flag emissions)

   Do NOT list:
   - "Constructor creates object" — that is language-guaranteed
   - "Enum has values" — that is definition, not behaviour
   - "Serialization round-trips" — unless the story specifically requires
     cross-system serialization

   Each behaviour becomes one test. If a test cannot be linked to a
   behaviour in this list, it should not exist.
5. Write failing tests for the behaviours listed above (TDD — red phase).
   Every test must assert on **observable outcomes** (returned values,
   DB state after reload, HTTP status + response body, emitted events).
   Never assert only on in-memory constructor state.
6. Write the minimum implementation to make tests pass (green phase).
7. Refactor if needed — keep tests green (refactor phase).
8. Check file size: if any touched file exceeds 300 lines, split it now.
9. Run all DoD commands — every command must exit 0.
10. **Run Critic review** (see STEP 3a below).
11. Fix any issues raised by the Critic.
12. Re-run DoD commands — must still pass.
13. Run Mini-Audit (see STEP 3b below).
14. Fix any issues found.
15. Mark all DoD checkboxes in the epic document.
15. Commit with a meaningful message referencing the story.

**DoD commands (run from backend/ with venv active):**

```bash
ruff check .
ruff format --check .
python -m mypy . --explicit-package-bases
pytest --tb=short -q
```

**A story is only done when all its checkboxes are [x].**

------------------------------------------------
STEP 3a — CRITIC REVIEW (after each story)
------------------------------------------------

After implementing a story, switch to the role of a Critic.

**Apply to ALL stories:**

Read the implementation you just wrote and actively look for:

- Missing edge cases not covered by tests
- Incorrect interpretation of the acceptance criteria
- SDD fields or requirements that were overlooked
- Overly complex solutions where simpler ones exist
- Tests that only assert `is not None` or `len > 0` (too weak)
- Missing negative test cases
- **Tautological tests (Rule T-1):** For each test, ask: "What code change
  would make this fail?" If the answer is "nothing reasonable", the test
  MUST be rewritten. Common offenders:
  - Asserting enum values equal themselves (`assert Flag.x == "x"`)
  - Asserting constructor defaults (`assert obj.field == default`)
  - Asserting serialization round-trips without domain logic
  - Asserting `isinstance` on freshly constructed objects
  - Asserting `len(SomeEnum) == N`
  Rewrite each into a test that exercises real behaviour and would break
  if the corresponding production code had a bug.

Produce a short Critic Report:

```
CRITIC REPORT — Story <id>
Issues found: <n>
- [issue 1]
- [issue 2]
...
```

If issues exist: fix them before proceeding to the Mini-Audit.
If no issues: write "CRITIC REPORT — Story <id>: No issues found."

**Apply full Critic depth when the story:**

- introduces more than ~100 lines of new logic
- implements a new abstraction or module
- interprets an ambiguous SDD requirement
- touches the Orchestrator cycle

For simple stories (config changes, pure refactors, test additions):
a brief Critic pass is sufficient.

------------------------------------------------
STEP 3b — MINI-AUDIT (after each story)
------------------------------------------------

After the Critic review and fixes, run a targeted mini-audit.

Check ONLY what this story touched:

1. **File paths**: do all new/modified files match HLA Section 6 exactly?
   Reject invented paths. Flag any file not in the HLA-defined structure.

2. **Line counts**: does any new/modified file exceed 300 lines?

3. **FR coverage**: for the FRs this story implements —
   are all required SDD fields present in the implementation?
   (Do not re-read the full SDD — use what you already know from Step 3.)

4. **Type completeness**: do all new functions have full type hints?

5. **No regressions**: does `pytest --tb=short -q` still show the same
   or more passing tests vs. the previous story?

Produce a Mini-Audit Result:

```
MINI-AUDIT — Story <id>
File paths: OK / VIOLATION (<details>)
Line counts: OK / VIOLATION (<file>: <n> lines)
FR coverage: OK / GAP (<FR-id>: <missing field>)
Type hints: OK / MISSING (<function>)
Tests: <n> passing (was <n-prev>)
```

If any item is VIOLATION or GAP: fix before committing.

------------------------------------------------
STEP 4 — ADR DISCIPLINE
------------------------------------------------

Write an ADR for every significant design decision:

- Any non-obvious implementation choice
- Any interpretation of an ambiguous SDD requirement
- Any dependency added (even if minor)
- Any file structure that required judgment

ADR file: `agent-docs/decisions/ADR-NNN-short-title.md`

Reference the ADR in the commit message: `Refs: ADR-NNN`

------------------------------------------------
STEP 5 — FILE SIZE AND MODULARITY CHECK
------------------------------------------------

After each story is implemented, verify:

- No source file exceeds 300 lines
- Each class has a single clear responsibility
- No unrelated concerns are merged in one module

If a file approaches the limit:

1. Identify cohesive groups to extract.
2. Verify target paths exist in HLA Section 6.
3. Create a separate refactoring commit.

------------------------------------------------
STEP 6 — FRONTEND (if applicable)
------------------------------------------------

For stories that add or modify API endpoints:

1. Update Pydantic schemas in `backend/api/schemas.py`.
2. Export updated OpenAPI snapshot: `GET /openapi.json > api-contract/openapi.json`
3. Regenerate TypeScript types: `npm run generate-api:file` (from `frontend/`)
4. Commit snapshot and generated types together.

Frontend DoD commands (run from frontend/):

```bash
npm run lint
npm run format:check
npm run typecheck
```

------------------------------------------------
EPIC LOG UPDATE
------------------------------------------------

Append implementation summary to:

agent-docs/epic-runs/<epic-id>.md

Include:

- stories implemented
- modules created
- architecture components added
- ADRs written
- libraries used vs. custom code written
- escalations made (if any)
- Critic issues found and fixed (per story)
- Mini-Audit results (per story)
- file size / modularity decisions
