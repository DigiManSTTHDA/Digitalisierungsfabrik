# Run Epic

Commands referenced with "/" must be executed exactly.
Do not reinterpret them.

Execute the full Epic lifecycle in a controlled workflow.

This command orchestrates all other commands and ensures
that progress is logged persistently.

You must write progress information to the Epic log file
after each phase.

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
- hla_architecture.md — read Section 6 on demand, not upfront
- digitalisierungsfabrik_systemdefinition.md — never read in full;
  each sub-command reads only its relevant sections

Never assume correctness.

Always verify by reading code and running checks.

Tests must never be weakened.

------------------------------------------------
STEP 0 — DETERMINE EPIC
------------------------------------------------

Identify the next Epic that is not yet implemented.

Create a run log:

agent-docs/epic-runs/<epic-id>.md

If the file already exists, continue appending to it.

Initialize with:

Epic name
Start date
Goal

→ Do NOT stop here. Continue with STEP 1.

------------------------------------------------
STEP 1 — CREATE STORIES
------------------------------------------------

Run:

/create-epic-stories

After completion:

Append to the Epic log:

- generated stories
- their purpose

→ Do NOT stop here. Continue with STEP 2.

------------------------------------------------
STEP 2 — VALIDATE STORIES
------------------------------------------------

Run:

/validate-epic

If validation finds issues:

fix them.

Append validation results to the Epic log.

→ Do NOT stop here. Continue with STEP 2.5.

------------------------------------------------
STEP 2.5 — ESCALATION CHECKPOINT
------------------------------------------------

Before implementation starts, scan all stories for genuine ambiguities:

1. Is the SDD clear enough to implement each story unambiguously?
2. Does any story require a significant design decision not covered by existing ADRs?
3. Does any story require a new dependency that should be discussed first?

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

/implement-next-epic

Follow TDD strictly.

Note: /implement-next-epic now includes per-story quality gates:
- Critic review after each story (active search for missed edge cases,
  weak assertions, SDD mismatches, overly complex solutions)
- Mini-Audit after each story (file paths, line counts, FR coverage,
  type hints, test count vs. previous story)

Append to Epic log:

- stories implemented
- key modules created
- architecture components added
- Critic issues found and fixed per story
- Mini-Audit results per story

→ Do NOT stop here. Continue with STEP 4.

------------------------------------------
STEP 4 — VALIDATE TESTS
------------------------------------------

Run:

/validate-tests

Improve the test suite before execution.

→ Do NOT stop here. Continue with STEP 5.

---------------------------------------------
STEP 5 — RUN TESTS
---------------------------------------------

Run:

/run-tests

→ Do NOT stop here. Continue with STEP 6.

------------------------------------------------
STEP 6 — EPIC-LEVEL AUDIT
------------------------------------------------

Run:

/audit-epic

This is the comprehensive final audit across the entire epic.
The per-story Mini-Audits in /implement-next-epic catch issues early.
This step verifies the complete picture — all stories together.

Verify:

- SDD compliance (full Section 4 check)
- architecture compliance (all files, all paths)
- dependency rules
- API contract rules

Append audit results to Epic log.

→ Do NOT stop here. Continue with STEP 7.

------------------------------------------------
STEP 7 — FINAL VERIFICATION
------------------------------------------------

Run DoD commands again.

Ensure:

ruff check .
ruff format --check .
mypy
pytest
frontend checks

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

- tests pass
- DoD checks pass
- SDD requirements satisfied
- architecture rules satisfied

If not:

repeat relevant steps until compliant.