# Run E2E Epic

Commands referenced with "/" must be executed exactly.
Do not reinterpret them.

Execute the full E2E Epic lifecycle (Epics 12–14) in a controlled workflow.

This command orchestrates all other E2E commands and ensures
that progress is logged persistently.

You must write progress information to the Epic log file
after each phase.

This is NOT the production system. Use E2E-specific commands only.
Do NOT run backend/frontend commands (ruff, mypy, pytest, npm run lint).

------------------------------------------------
CRITICAL: CONTINUATION RULE
------------------------------------------------

This workflow has 9 steps (STEP 0 through STEP 8).
You MUST execute ALL steps in sequence without stopping.

After each step: log progress, then IMMEDIATELY continue
with the next step. Do NOT stop, summarize, or ask for
confirmation between steps — unless a step explicitly
says "STOP" (only STEP 2.5 may do this).

After completing EACH step, state:

"✅ Step N complete. Continuing with Step N+1..."

The epic is NOT done until you reach the FINAL RESULT
section and all conditions there are met.

------------------------------------------------
GLOBAL RULES
------------------------------------------------

Follow these documents:

- AGENTS.md — always read in full (manageable size)
- `agent-docs/e2e-testkampagne-plan.md` — the test campaign plan;
  read in full at start
- Do NOT read SDD or HLA unless a specific story references them

Never assume correctness.

Always verify by reading code and running checks.

Tests must never be weakened.

------------------------------------------------
STEP 0 — DETERMINE EPIC
------------------------------------------------

Identify the next E2E Epic (12, 13, or 14) that is not yet implemented.

Check `agent-docs/epic-runs/epic-12.md`, `epic-13.md`, `epic-14.md`
for implementation status.

Create or continue a run log:

agent-docs/epic-runs/<epic-id>.md

Initialize with:

Epic name
Start date
Goal

→ Do NOT stop here. Continue with STEP 1.

------------------------------------------------
STEP 1 — CREATE STORIES
------------------------------------------------

Run:

/create-e2e-epic-stories

After completion:

Append to the Epic log:

- generated stories
- their purpose

→ Do NOT stop here. Continue with STEP 2.

------------------------------------------------
STEP 2 — VALIDATE STORIES
------------------------------------------------

Run:

/validate-e2e-epic

If validation finds issues:

fix them.

Append validation results to the Epic log.

→ Do NOT stop here. Continue with STEP 2.5.

------------------------------------------------
STEP 2.5 — ESCALATION CHECKPOINT
------------------------------------------------

Before implementation starts, scan all stories for genuine ambiguities:

1. Is the test campaign plan clear enough to implement each story unambiguously?
2. Does any story require a design decision not covered by existing ADRs?
3. Does any story require a new npm dependency that should be discussed first?
4. Are backend API signatures (WebSocket format, REST endpoints) known
   and verified, or do they need to be checked?

If YES to any of the above:

**STOP. Present the ambiguities to the user.**

Structure the escalation clearly:
- Which story is affected
- What exactly is ambiguous
- 2–3 concrete options with trade-offs
- Your recommendation

Wait for the user's decision, then record it as an ADR before proceeding.

If all stories are clear: proceed immediately without asking.

Append escalation outcome (or "no escalations needed") to the Epic log.

→ Do NOT stop here. Continue with STEP 3.

------------------------------------------------
STEP 3 — IMPLEMENT EPIC
------------------------------------------------

Run:

/implement-e2e-epic

Follow TDD strictly where unit tests are required.

Note: /implement-e2e-epic includes per-story quality gates:
- Critic review after each story
- Mini-Audit after each story (file paths, line counts, exports, types)

Append to Epic log:

- stories implemented
- key files created
- Critic issues found and fixed per story
- Mini-Audit results per story

→ Do NOT stop here. Continue with STEP 4.

------------------------------------------
STEP 4 — VALIDATE TESTS
------------------------------------------

Run:

/validate-e2e-tests

Improve the test suite before execution.

→ Do NOT stop here. Continue with STEP 5.

---------------------------------------------
STEP 5 — RUN TESTS
---------------------------------------------

Run:

/run-e2e-tests

→ Do NOT stop here. Continue with STEP 6.

------------------------------------------------
STEP 6 — EPIC-LEVEL AUDIT
------------------------------------------------

Run:

/audit-e2e-epic

This is the comprehensive final audit across the entire epic.
The per-story Mini-Audits in /implement-e2e-epic catch issues early.
This step verifies the complete picture — all stories together.

Verify:

- test campaign plan compliance
- file structure compliance
- dependency rules
- type safety

Append audit results to Epic log.

→ Do NOT stop here. Continue with STEP 7.

------------------------------------------------
STEP 7 — FINAL VERIFICATION
------------------------------------------------

Run DoD commands again.

```bash
cd e2e && npm run typecheck
cd e2e && npx tsx --test framework/__tests__/*.test.ts
```

Verify scenario JSONs are valid (if present):

```bash
cd e2e && node -e "
  const fs = require('fs');
  const dir = 'scenarios';
  if (fs.existsSync(dir)) {
    fs.readdirSync(dir).filter(f => f.endsWith('.json')).forEach(f => {
      JSON.parse(fs.readFileSync(dir + '/' + f, 'utf-8'));
      console.log('OK:', f);
    });
  }
"
```

Append final verification results.

→ Do NOT stop here. Continue with STEP 8.

------------------------------------------------
STEP 8 — MANAGEMENT SUMMARY
------------------------------------------------

Run:

/management-summary

Use the Epic log file as input.

Create a report:

agent-docs/reports/<epic-id>-summary.md

------------------------------------------------
FINAL RESULT
------------------------------------------------

Epic is complete only if:

- typecheck passes
- unit tests pass
- plan requirements satisfied
- AGENTS.md rules satisfied
- scenario JSONs valid (if applicable)

If not:

repeat relevant steps until compliant.
