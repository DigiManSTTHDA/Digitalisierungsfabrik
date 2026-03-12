# Run Tests and Fix Implementation

Run all project checks and fix failures.

IMPORTANT: Tests define the contract of the system.

If tests fail, assume the implementation is wrong.

Never weaken tests to make them pass.

------------------------------------------------
ABSOLUTE PROHIBITIONS
------------------------------------------------

You must NOT:

- delete failing tests
- mark tests as skipped
- weaken assertions
- replace strict comparisons with weaker ones
- remove negative tests

Examples of forbidden changes:

assert x == 5 → assert x >= 0  
assert result == expected → assert result is not None

Tests may only be modified if they contradict the SDD
or Epic acceptance criteria.

------------------------------------------------
STEP 1 — RUN BACKEND CHECKS
------------------------------------------------

cd backend

ruff check .
ruff format --check .
python -m mypy . --explicit-package-bases
pytest --tb=short -q

------------------------------------------------
STEP 2 — RUN FRONTEND CHECKS
------------------------------------------------

cd frontend

npm run lint
npm run format:check
npm run typecheck

------------------------------------------------
STEP 3 — FIX FAILURES
------------------------------------------------

If any command fails:

1. identify the failing test or error
2. determine the root cause
3. fix the implementation
4. re-run the checks

Repeat until all commands pass.

------------------------------------------------
FINAL VERIFICATION
------------------------------------------------

Verify:

- no tests were deleted
- no tests were skipped
- no assertions were weakened
- all checks pass

------------------------------------------------
EPIC LOG UPDATE
------------------------------------------------

Append test results to:

agent-docs/epic-runs/<epic-id>.md

Include:

- number of tests
- failing tests
- fixes applied