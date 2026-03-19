# Validate E2E Epic and Stories

You are a strict specification validator for the **E2E test campaign**.

Your task is to verify that an E2E Epic (Epics 12–14) and its Stories
comply with:

- AGENTS.md
- `agent-docs/e2e-testkampagne-plan.md` (the test campaign plan)
- the Epic document itself

You are NOT implementing code.

You are validating the Epic specification.

Assume the Epic may contain mistakes.

This is NOT the production system. Do NOT validate against
digitalisierungsfabrik_systemdefinition.md (SDD) or hla_architecture.md (HLA)
unless a story explicitly references SDD sections (e.g. for flag names
or EMMA action types).

------------------------------------------------
PHASE 1 — DOCUMENT COLLECTION
------------------------------------------------

Read in full (small, always relevant):
- AGENTS.md
- `agent-docs/e2e-testkampagne-plan.md`

Read selectively:
- The Epic document provided by the user (in full)
- `agent-docs/epics/` — check dependency epics if referenced

Then extract:

- Epic goal
- testable increment
- key deliverables
- story list
- acceptance criteria
- definition of done

------------------------------------------------
PHASE 2 — EPIC STRUCTURE VALIDATION
------------------------------------------------

Verify the Epic contains:

- Summary
- Goal
- Testable Increment
- Dependencies
- Key Deliverables
- Stories

Check:

The testable increment must be a runnable verification.

Examples:

- `npm run typecheck` exit 0
- `npx tsx --test e2e/framework/__tests__/*.test.ts` exit 0
- `npx tsx e2e/run-campaign.ts --scenario S02` generates report

Reject vague increments.

------------------------------------------------
PHASE 3 — STORY STRUCTURE VALIDATION
------------------------------------------------

Each story must contain:

- description (As a / I want / so that)
- acceptance criteria
- definition of done

If any are missing:

report an error.

------------------------------------------------
PHASE 4 — TEST CAMPAIGN PLAN COMPLIANCE
------------------------------------------------

This is mandatory.

For every story:

identify which section of `e2e-testkampagne-plan.md` it implements.

Verify:

- Evaluation criteria (assertions, behavior dimensions) from the plan
  are correctly reflected in story ACs
- Scenario format (Scenario interface, TurnRecord, etc.) matches the plan
- Architecture (WebSocket client, scenario runner, evaluator, reporter)
  matches the plan

Rules:

- No required component from the plan may be omitted.
- No invented components that contradict the plan.

If missing:

list them.

------------------------------------------------
PHASE 5 — FILE PATH COMPLIANCE
------------------------------------------------

Verify file paths referenced in the Epic.

Rules:

All E2E code lives under `e2e/` at the repository root.

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
    evaluator.ts (or split into assertion-evaluator.ts + behavior-evaluator.ts)
    campaign-reporter.ts
    __tests__/
      *.test.ts
  scenarios/
    s01-eingangsrechnung.json
    s02-reisekosten.json
    ...
  reports/          (generated, gitignored)
```

Reject:

- files placed outside `e2e/`
- invented directory structures
- paths that don't match the plan or epic deliverables

------------------------------------------------
PHASE 6 — TEST REQUIREMENTS
------------------------------------------------

Verify that stories introducing logic include tests.

Rules:

- Evaluator logic requires unit tests (using `node:test`)
- Tests must correspond to acceptance criteria
- Tests must cover both success and failure cases
- Tests run without a backend (synthetic TurnRecord data)

Reject stories that introduce evaluator/reporter logic but do not
define tests.

------------------------------------------------
PHASE 7 — DEFINITION OF DONE VALIDATION
------------------------------------------------

Verify DoD checklist quality.

Rules:

Each structural requirement must have its own checkbox.

Bad example:

[ ] npm run typecheck

Good example:

[ ] `e2e/framework/evaluator.ts` exists
[ ] `npm run typecheck` passes (exit 0)
[ ] `npx tsx --test e2e/framework/__tests__/evaluator.test.ts` passes

Also verify:

DoD commands include required E2E commands:

```
cd e2e && npm run typecheck
cd e2e && npx tsx --test framework/__tests__/*.test.ts   (if tests exist)
```

------------------------------------------------
PHASE 8 — DEPENDENCY VALIDATION
------------------------------------------------

If the Epic introduces npm dependencies:

Verify:

- Only dependencies listed in the epic's story ACs (ws, tsx, typescript, @types/ws, @types/node)
- No unnecessary dependencies
- Any new dependency requires user approval

If the Epic depends on other epics:

Verify:

- Epic 12 depends on: backend WebSocket endpoint (Epic 05)
- Epic 13 depends on: Epic 12 (framework core)
- Epic 14 depends on: Epic 12 + 13

------------------------------------------------
PHASE 9 — IMPLEMENTABILITY
------------------------------------------------

Verify the Epic can be implemented incrementally.

Rules:

Each story must produce a working system increment.

Reject stories that:

- require future components from a later story
- break earlier functionality
- exceed the 400-line file limit (AGENTS.md)

Verify story-specific line limits match epic ACs
(e.g. types.ts ≤300 lines, ws-client.ts ≤300 lines).

------------------------------------------------
OUTPUT
------------------------------------------------

Produce a report:

E2E EPIC VALIDATION REPORT

1. Structure Issues
2. Test Campaign Plan Compliance Issues
3. File Path Issues
4. Test Issues
5. DoD Issues
6. Dependency Issues

Then give:

EPIC VALID: YES / NO

If NO:

list required corrections.

------------------------------------------------
EPIC LOG UPDATE
------------------------------------------------

Append validation results to:

agent-docs/epic-runs/<epic-id>.md

Include:

- validation outcome
- issues found
- corrections applied
