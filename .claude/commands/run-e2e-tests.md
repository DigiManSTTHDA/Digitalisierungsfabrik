# Run E2E Tests and Fix Implementation

Run all E2E project checks and fix failures.

IMPORTANT: Tests define the contract of the E2E test harness.

If tests fail, assume the implementation is wrong.

Never weaken tests to make them pass.

This applies to the `e2e/` directory — a standalone TypeScript project.
Do NOT run backend (ruff, mypy, pytest) or frontend checks here.

------------------------------------------------
ABSOLUTE PROHIBITIONS
------------------------------------------------

You must NOT:

- delete failing tests
- mark tests as skipped
- weaken assertions
- replace strict comparisons with weaker ones
- remove negative tests
- add `any` types to bypass type errors

Examples of forbidden changes:

```typescript
assert.strictEqual(x, 5) → assert.ok(x >= 0)
assert.deepStrictEqual(result, expected) → assert.ok(result !== null)
```

Tests may only be modified if they contradict the Epic acceptance
criteria or the test campaign plan.

------------------------------------------------
STEP 1 — RUN TYPECHECK
------------------------------------------------

```bash
cd e2e && npm run typecheck
```

This runs `tsc --noEmit` with strict mode.

------------------------------------------------
STEP 2 — RUN UNIT TESTS
------------------------------------------------

```bash
cd e2e && npx tsx --test framework/__tests__/*.test.ts
```

These tests use `node:test` and run without a backend.

------------------------------------------------
STEP 3 — FIX FAILURES
------------------------------------------------

If any command fails:

1. identify the failing test or type error
2. determine the root cause
3. fix the implementation (NOT the test)
4. re-run the checks

Repeat until all commands pass.

------------------------------------------------
STEP 4 — TYPE SAFETY CHECKS
------------------------------------------------

After all tests pass, verify type safety:

1. Check that `tsconfig.json` has `strict: true`
2. Check for `any` types — each must be justified
3. Check that exported functions have explicit return types
4. Check that interfaces match `types.ts` definitions

------------------------------------------------
STEP 5 — TAUTOLOGICAL TEST CHECK (Rule T-1)
------------------------------------------------

After all tests pass, scan every test added or modified in this Epic.

For each test, ask: "What code change would make this fail?"

If the answer is "nothing reasonable", the test is tautological.

Common tautological patterns:
- Asserting interface properties equal themselves
- Asserting constructor returns passed values
- Asserting typeof on freshly constructed objects
- Asserting array length without checking content

Action: Rewrite the test body to assert on real, observable behaviour.
This is not "weakening" — it is hardening a defective test.

------------------------------------------------
STEP 6 — SCENARIO JSON VALIDATION (Epic 14)
------------------------------------------------

If scenario JSON files exist, validate each one:

1. Parse as JSON (must be valid)
2. Check required fields match the `Scenario` interface from `types.ts`
3. Check that `user_inputs` are non-empty arrays per phase
4. Check that `intent.key_concepts` and `intent.forbidden_concepts` are present
5. Check that `behavior_probes` exist (≥2 per scenario)
6. Check that turn expectations reference valid fields

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

------------------------------------------------
FINAL VERIFICATION
------------------------------------------------

Verify:

- no tests were deleted to suppress failures
- no tests were skipped
- no assertions were weakened
- all checks pass (typecheck + unit tests)
- no `any` types without justification
- no tautological tests remain (Rule T-1)
- scenario JSONs are valid (if present)

------------------------------------------------
EPIC LOG UPDATE
------------------------------------------------

Append test results to:

agent-docs/epic-runs/<epic-id>.md

Include:

- number of tests
- failing tests
- fixes applied
- scenario validation results (if applicable)
