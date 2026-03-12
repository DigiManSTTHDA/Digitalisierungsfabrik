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

- AGENTS.md
- hla_architecture.md
- digitalisierungsfabrik_systemdefinition.md (SDD)

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
STEP 3 — IMPLEMENT EPIC
------------------------------------------------

Run:

/implement-next-epic

Follow TDD strictly.

Append to Epic log:

- stories implemented
- key modules created
- architecture components added

------------------------------------------------
STEP 4 — RUN TESTS
------------------------------------------------

Run:

/run-tests

Rules:

Tests must NOT be weakened.

Fix implementation instead.

Append to Epic log:

- test results
- failures encountered
- fixes applied

------------------------------------------------
STEP 5 — AUDIT IMPLEMENTATION
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
STEP 6 — FINAL VERIFICATION
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
STEP 7 — MANAGEMENT SUMMARY
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