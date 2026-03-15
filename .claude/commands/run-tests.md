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
STEP 4 — INFRASTRUCTURE CHECKS
------------------------------------------------

After all tests pass, verify infrastructure correctness:

1. Check that ALL FastAPI dependencies that create resources
   (Database, file handles) use generator pattern:
   ```python
   import inspect
   from api.router import _get_repository
   assert inspect.isgeneratorfunction(_get_repository)
   ```

2. Check that no `except Exception` in production code lacks
   a corresponding test that triggers it.

3. Verify error messages in error responses are non-empty.

------------------------------------------------
STEP 5 — TAUTOLOGICAL TEST CHECK (Rule T-1)
------------------------------------------------

After all tests pass, scan every test added or modified in this Epic.

For each test, ask: "What production code change would make this fail?"

If the answer is "nothing reasonable", the test is tautological.

Common tautological patterns:
- Asserting enum values equal themselves
- Asserting constructor returns passed values / defaults
- Asserting isinstance on freshly constructed objects
- Asserting serialization round-trips without domain logic
- Asserting len(SomeEnum) == N

Action: Rewrite the test body to assert on real, observable behaviour.
This is not "weakening" — it is hardening a defective test.

------------------------------------------------
FINAL VERIFICATION
------------------------------------------------

Verify:

- no tests were deleted to suppress failures
- no tests were skipped
- no assertions were weakened
- all checks pass
- resource cleanup is tested (Rule T-5)
- no tautological tests remain (Rule T-1)

------------------------------------------------
EPIC LOG UPDATE
------------------------------------------------

Append test results to:

agent-docs/epic-runs/<epic-id>.md

Include:

- number of tests
- failing tests
- fixes applied