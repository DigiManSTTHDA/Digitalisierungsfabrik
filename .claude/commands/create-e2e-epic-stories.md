# Create E2E Epic Stories

Your task is to generate detailed implementation stories
for the next E2E Epic (Epics 12–14).

The Epic exists but does not yet contain stories.

You must create them.

This is NOT the production system. Stories describe **test harness**
components (TypeScript, WebSocket client, evaluator, reporter, scenarios).
Different rules apply than for backend/frontend stories.

------------------------------------------------
MANDATORY REFERENCES
------------------------------------------------

Read in full (small, always relevant):
- AGENTS.md
- `agent-docs/e2e-testkampagne-plan.md` — the test campaign plan
  (architecture, scenario format, TurnRecord format, evaluation criteria)

Do NOT read the SDD or HLA upfront. Only read specific SDD sections
if the Epic references them (e.g. for EMMA action types, flag names).

------------------------------------------------
STEP 1 — READ THE EPIC
------------------------------------------------

Locate the next E2E Epic that has no Stories section.

Extract:

- Epic summary
- goal
- testable increment
- key deliverables
- dependencies

------------------------------------------------
STEP 2 — MAP TO TEST CAMPAIGN PLAN
------------------------------------------------

1. Read `agent-docs/e2e-testkampagne-plan.md` in full.
2. Identify which sections of the plan this Epic implements:
   - Epic 12: WebSocket client, scenario runner, types, CLI
   - Epic 13: Evaluator (assertions + behavior), reporter, campaign runner
   - Epic 14: Scenario JSON definitions (8 scenarios)
3. For each relevant plan section:
   - find the required interfaces, evaluation criteria, report formats
   - identify required behaviour
   - identify constraints (thresholds, rating scales, pattern detection)

No plan requirement from the relevant sections may be omitted.

------------------------------------------------
STEP 3 — DESIGN STORY BREAKDOWN
------------------------------------------------

Split the Epic into small Stories.

Rules:

Stories must be:

- independently implementable
- testable (at least via `npm run typecheck`)
- file-path compliant with the Epic's Key Deliverables

A story must produce a working increment.

Do not create oversized stories.

**Story size guidance:**
- A story should be implementable in one focused session.
- If a story would produce a source file over 300 lines, split the story.
  Exception: some stories allow up to 400 lines per AGENTS.md.
- If a story bundles multiple distinct responsibilities, split it.

**Dependency awareness:**
- Check what exists from prior epics before designing stories.
- Epic 13 stories should extend/use Epic 12 deliverables.
- Epic 14 stories should use the Scenario interface from Epic 12.

------------------------------------------------
STEP 4 — STORY STRUCTURE
------------------------------------------------

Each story must contain:

Title

User story:

As a QA engineer
I want ...
So that ...

Acceptance Criteria

Definition of Done checklist

------------------------------------------------
STEP 5 — ACCEPTANCE CRITERIA
------------------------------------------------

Acceptance criteria must:

- reference exact file paths under `e2e/`
- describe observable behaviour (what the code does, not just that it exists)
- include TypeScript interface compliance where applicable
- specify line count limits per file
- for evaluator stories: list exact thresholds and rating logic
- for scenario stories: list required fields (turns, intent, BehaviorProbes, etc.)

Avoid vague criteria.

Bad:

"evaluator implemented"

Good:

"`e2e/framework/evaluator.ts` exports `AssertionEvaluator` class
with method `checkModeTransitions(records: TurnRecord[]): AssertionResult`
that returns FAIL if mode changes without phase_complete/escalate/blocked flag"

------------------------------------------------
STEP 6 — DEFINITION OF DONE
------------------------------------------------

Each structural requirement must have its own checkbox.

Examples:

[ ] `e2e/framework/evaluator.ts` exists
[ ] `AssertionEvaluator` exports all 7 check methods
[ ] `npm run typecheck` passes (exit 0)
[ ] `npx tsx --test e2e/framework/__tests__/evaluator.test.ts` passes
[ ] File ≤400 lines

Do not rely only on tool commands.

------------------------------------------------
STEP 7 — TEST REQUIREMENTS
------------------------------------------------

If a story introduces evaluator or reporter logic, it must define tests.

Rules:

- Tests use `node:test` (import { describe, it } from 'node:test')
- Tests use `node:assert/strict` for assertions
- Tests use synthetic TurnRecord arrays (no backend needed)
- Both positive and negative cases
- Test location: `e2e/framework/__tests__/<module>.test.ts`

Stories that only define TypeScript interfaces or JSON scenarios
do not require unit tests, but must pass `npm run typecheck`.

------------------------------------------------
STEP 8 — FILE PATH COMPLIANCE
------------------------------------------------

All file paths must be under `e2e/` and match the Epic's
Key Deliverables exactly.

Reject invented paths.

------------------------------------------------
STEP 9 — OUTPUT
------------------------------------------------

Insert the Stories into the Epic document.

Each story must include:

- title
- user story
- acceptance criteria
- definition of done

------------------------------------------------
EPIC LOG UPDATE
------------------------------------------------

Append story generation summary to:

agent-docs/epic-runs/<epic-id>.md

Include:

- generated stories
- purpose of each story
- dependencies between stories
- any escalation points flagged (plan ambiguities requiring user decision)
