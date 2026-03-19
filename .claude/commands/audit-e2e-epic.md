# Audit E2E Epic

Run a full audit and repair after an E2E Epic implementation (Epics 12–14).

You are a strict compliance auditor for the **E2E test campaign**.

Your job is to ensure that the `e2e/` directory fully complies with:

- AGENTS.md
- `agent-docs/e2e-testkampagne-plan.md` (the test campaign plan)
- the Epic document that was just implemented

Assume the implementation may contain errors.

You must verify and repair them.

This is NOT the production system. Do NOT audit against SDD or HLA
unless a specific story references them.

------------------------------------------------
GLOBAL RULES
------------------------------------------------

You are NOT the implementer.
You are the auditor.

Never trust previous claims such as:
- "typecheck passes"
- "tests pass"
- "all interfaces implemented"

Always verify by reading code and running commands.

If something violates AGENTS.md or the test campaign plan,
you must fix it.

------------------------------------------------
PHASE 1 — CONTEXT COLLECTION
------------------------------------------------

Read in full (small, always relevant):
- AGENTS.md
- `agent-docs/e2e-testkampagne-plan.md`

Locate the epic document that was just implemented.

Extract:

- acceptance criteria
- Definition of Done checklist
- expected files and directories
- referenced plan sections

------------------------------------------------
PHASE 2 — FILE STRUCTURE COMPLIANCE
------------------------------------------------

Verify the `e2e/` directory structure matches the Epic's
Key Deliverables and the test campaign plan.

Expected structure:

```
e2e/
  package.json
  tsconfig.json
  run-campaign.ts
  framework/
    types.ts
    ws-client.ts
    scenario-runner.ts
    evaluator.ts (or assertion-evaluator.ts + behavior-evaluator.ts)
    campaign-reporter.ts
    __tests__/
      *.test.ts
  scenarios/
    s01-eingangsrechnung.json
    ...
  reports/          (generated, gitignored)
```

Rules:

1. No files outside `e2e/` for E2E epic code.
2. No files placed in incorrect directories.
3. No invented directory structure.
4. `.gitignore` includes `node_modules/` and `reports/`.

If violations exist:

Fix the structure.

------------------------------------------------
PHASE 3 — DEPENDENCY COMPLIANCE
------------------------------------------------

Verify `e2e/package.json` dependencies.

Allowed dependencies (per Epic 12):

- `ws` — WebSocket client
- `tsx` — TypeScript execution
- `typescript` — type checking
- `@types/ws` — WebSocket types
- `@types/node` — Node.js types

Rules:

- No dependencies not approved in the Epic or by the user.
- No hidden additions.
- No unnecessary libraries.

If a dependency was added without approval:

remove it.

------------------------------------------------
PHASE 4 — TEST CAMPAIGN PLAN COMPLIANCE
------------------------------------------------

This is critical.

Every implemented component must comply with `e2e-testkampagne-plan.md`.

Check:

1. **Interfaces:** Do TypeScript interfaces in `types.ts` match the plan's
   Scenario, TurnRecord, ScenarioResult, etc.?
2. **Evaluation criteria:** Do assertion checks match the plan's 7 hard
   assertions? Do behavior dimensions match the plan's 4 dimensions?
3. **Rating thresholds:** Do SEHR_GUT/GUT/BEFRIEDIGEND/MANGELHAFT
   thresholds match the epic ACs exactly?
4. **Report format:** Does Markdown output match the plan's structure
   (eckdaten, assertion table, behavior table, dialog protocol)?
5. **Scenario format:** Do JSON scenarios match the Scenario interface?

If any plan requirement is missing:

fix the implementation.

------------------------------------------------
PHASE 5 — TEST COVERAGE
------------------------------------------------

Check E2E unit tests.

Rules:

- Every evaluator method must have tests.
- Tests must correspond to acceptance criteria.
- Tests must not be trivial.
- Tests use synthetic TurnRecord data (no backend needed).

Check:

- test locations are in `e2e/framework/__tests__/`
- positive tests exist
- negative tests exist
- edge cases covered

If missing:

add tests.

------------------------------------------------
PHASE 6 — DEFINITION OF DONE
------------------------------------------------

Run the DoD commands.

```bash
cd e2e && npm run typecheck
cd e2e && npx tsx --test framework/__tests__/*.test.ts
```

If any command fails:

fix the issue.

Repeat until all commands pass.

------------------------------------------------
PHASE 7 — TYPE SAFETY
------------------------------------------------

Verify TypeScript strictness:

- `tsconfig.json` has `strict: true`
- No `any` types unless unavoidable and documented
- No type assertions (`as`) without justification
- All exported functions have explicit return types
- Interfaces match `types.ts` definitions consistently

Fix all issues.

------------------------------------------------
PHASE 8 — CODE QUALITY
------------------------------------------------

Check:

- File size limits (400 lines max per AGENTS.md, story-specific limits may be stricter)
- Missing exports
- Incorrect imports
- Unused code
- Naming inconsistencies (camelCase for TypeScript)
- Dead modules

Fix all issues.

------------------------------------------------
PHASE 9 — FINAL VERIFICATION
------------------------------------------------

Re-run all DoD commands.

Verify:

- file structure correct
- tests pass
- typecheck passes
- plan requirements satisfied
- AGENTS.md rules satisfied

------------------------------------------------
OUTPUT
------------------------------------------------

Produce a structured report:

AUDIT REPORT
- file structure issues
- plan compliance issues
- dependency issues
- test issues
- DoD issues
- type safety issues

FIXES APPLIED
- list of repairs

FINAL STATUS

E2E EPIC COMPLIANT WITH:

AGENTS.md: YES/NO
Test Campaign Plan: YES/NO
Epic ACs: YES/NO

If any item is NO, continue fixing until YES.

------------------------------------------------
EPIC LOG UPDATE
------------------------------------------------

Append audit results to:

agent-docs/epic-runs/<epic-id>.md

Include:

- file structure compliance
- plan compliance
- dependency compliance
- test results
