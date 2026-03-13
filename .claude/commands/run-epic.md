# Run Epic

Commands referenced with "/" must be executed exactly.
Do not reinterpret them.

Execute the full Epic lifecycle in a controlled workflow.

This command orchestrates all other commands and ensures
that progress is logged persistently.

You must write progress information to the Epic log file
after each phase.

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

------------------------------------------------
STEP 1 — CREATE STORIES
------------------------------------------------

Run:

/create-epic-stories

After completion:

Append to the Epic log:

- generated stories
- their purpose

------------------------------------------------
STEP 2 — VALIDATE STORIES
------------------------------------------------

Run:

/validate-epic

If validation finds issues:

fix them.

Append validation results to the Epic log.

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

------------------------------------------------
STEP 3 — IMPLEMENT EPIC
------------------------------------------------

Run:

/implement-next-epic

Follow TDD strictly.

Append to Epic log:

- stories implemented
- key modules created
- architecture components added

------------------------------------------
STEP 4 — VALIDATE TESTS
------------------------------------------

Run:

/validate-tests

Improve the test suite before execution.

---------------------------------------------
STEP 5 — RUN TESTS
---------------------------------------------

Run:

/run-tests

------------------------------------------------
STEP 6 — AUDIT IMPLEMENTATION
------------------------------------------------

Run:

/audit-epic

Verify:

- SDD compliance
- architecture compliance
- dependency rules
- API contract rules

Append audit results to Epic log.

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