# Validate E2E Test Suite

You are a senior software test engineer.

Your responsibility is to ensure that the E2E test suite is capable of
detecting real defects in the test harness implementation.

Tests define the behavioural contract of the E2E framework.

They must be strict, meaningful, deterministic and complete.

Never weaken tests.

This applies to tests under `e2e/framework/__tests__/` — TypeScript
tests using `node:test` and `node:assert/strict`.

Do NOT validate backend tests (pytest) or frontend tests here.

------------------------------------------------
MANDATORY CONTEXT
------------------------------------------------

Read in full (small, always relevant):
- AGENTS.md
- `agent-docs/e2e-testkampagne-plan.md`
- the current Epic and its acceptance criteria

Tests must validate the behaviour defined in these documents.

------------------------------------------------
GOAL
------------------------------------------------

Ensure that the test suite:

- validates observable framework behaviour
- detects incorrect evaluator logic
- covers edge cases and boundary conditions
- prevents regressions
- reflects the test campaign plan and acceptance criteria

------------------------------------------------
TEST COVERAGE ANALYSIS
------------------------------------------------

Inspect the entire E2E test suite under `e2e/framework/__tests__/`.

Verify that the following components are tested:

- AssertionEvaluator (all 7 check methods)
- BehaviorEvaluator (all 4 dimensions)
- CampaignReporter (report generation, pattern detection)
- Threshold/rating logic (boundary between ratings)

Every evaluator method must have at least one test.

------------------------------------------------
BEHAVIOUR VALIDATION
------------------------------------------------

Tests must validate observable behaviour.

Good: "Given TurnRecords where mode changes without phase_complete flag,
AssertionEvaluator.checkModeTransitions returns FAIL"

Bad: "AssertionEvaluator has a checkModeTransitions method"

Tests should focus on inputs (synthetic TurnRecords) and outputs
(AssertionResult, BehaviorScore).

------------------------------------------------
EDGE CASE TESTING
------------------------------------------------

Ensure tests cover edge cases such as:

- Empty TurnRecord arrays
- Single-turn scenarios
- TurnRecords with missing optional fields
- Scenarios with no escalations
- Scenarios where all assertions pass
- Scenarios where all assertions fail
- Boundary values for behavior ratings
  (e.g. exactly 0.7 slot_efficiency for SEHR_GUT threshold)

------------------------------------------------
BOUNDARY VALUE TESTING
------------------------------------------------

For evaluator rating thresholds, verify exact boundaries:

AssertionEvaluator:
- Mode transition with/without proper flags
- Moderator turn with/without artifact changes
- Language check at German/English boundary

BehaviorEvaluator:
- slot_efficiency at exact threshold: 0.7 (SEHR_GUT), 0.5 (GUT), 0.3 (BEFRIEDIGEND)
- p95 response time at: 20s (SEHR_GUT), 30s (GUT), 45s (BEFRIEDIGEND)
- nudge_count at: 1, 2, boundaries
- escalation_resolved ratio at: 1.0, partial, 0.0

Each threshold needs a test at the boundary AND one step below.

------------------------------------------------
NEGATIVE TESTS
------------------------------------------------

Invalid inputs must produce expected results.

Ensure tests verify:

- Evaluator correctly returns FAIL for invalid TurnRecords
- BehaviorEvaluator returns MANGELHAFT for worst-case data
- Reporter handles empty scenario results gracefully
- Pattern detection with no patterns to detect

Errors must be asserted explicitly.

------------------------------------------------
ASSERTION QUALITY
------------------------------------------------

Reject weak assertions such as:

```typescript
assert.ok(result)
assert.ok(result.length > 0)
```

Prefer strict behavioural assertions:

```typescript
assert.strictEqual(result.status, 'FAIL')
assert.strictEqual(result.rating, 'SEHR_GUT')
assert.deepStrictEqual(result.failed_turns, [3, 7])
```

Assertions must clearly detect incorrect behaviour.

------------------------------------------------
SYNTHETIC TEST DATA QUALITY
------------------------------------------------

Tests must use realistic synthetic TurnRecord data.

Rules:

- TurnRecords must have all required fields from `types.ts`
- State fields (aktiver_modus, aktive_phase, flags) must be consistent
- response_time_ms must be realistic (not 0 or negative)
- Each test should create only the data it needs
- Use factory functions or helpers for common TurnRecord creation

Avoid overly complex fixtures. Prefer inline test data that makes
the test's intent obvious.

------------------------------------------------
ANTI-PATTERNS — TAUTOLOGICAL TEST DETECTION
------------------------------------------------

For EVERY test, apply Rule T-1: "What code change would make this fail?"
If the answer is "nothing reasonable", the test is tautological.

Reject and **rewrite** tests that:

- only check that code runs without verifying the result
- only check types or instanceof
- assert trivial truths (enum values equal themselves)
- duplicate the evaluator logic (bug mirroring)
- check array length without checking content

**Action when found:** Do NOT leave tautological tests in place. Rewrite
the assertions to test real, falsifiable behaviour. Keep the test function
name and location — replace the body with meaningful assertions.

Example — BEFORE (tautological):
```typescript
it('should create evaluator', () => {
  const evaluator = new AssertionEvaluator();
  assert.ok(evaluator);
});
```

Example — AFTER (hardened):
```typescript
it('should detect mode change without flag', () => {
  const records = [
    makeTurnRecord({ mode: 'exploration', flags: [] }),
    makeTurnRecord({ mode: 'moderator', flags: [] }), // no escalate flag!
  ];
  const result = new AssertionEvaluator().checkModeTransitions(records);
  assert.strictEqual(result.status, 'FAIL');
  assert.strictEqual(result.failed_turns.length, 1);
});
```

------------------------------------------------
TEST ISOLATION
------------------------------------------------

Tests must:

- not depend on execution order
- not depend on other tests
- not share mutable state
- not require a running backend (use synthetic data)

Each test must set up its own data.

------------------------------------------------
DETERMINISM
------------------------------------------------

Tests must produce the same result every run.

Avoid:

- random inputs
- time-dependent behaviour
- file system state dependencies

------------------------------------------------
PATTERN DETECTION TESTS (Epic 13)
------------------------------------------------

If pattern detection logic exists, verify tests for:

- "dimension weak" pattern (≥50% scenarios BEFRIEDIGEND or worse)
- "assertion fails" pattern (≥3 scenarios with same assertion fail)
- "phase-complete weakness" pattern (median nudge_total >2)
- No patterns detected (clean run)

Each pattern needs its own test with crafted input data.

------------------------------------------------
STRICT PROHIBITIONS
------------------------------------------------

Never weaken existing tests. Never delete tests to make the suite green.

Do NOT:

- delete tests to suppress failures
- mark tests as skipped (`.skip`)
- weaken assertions (e.g. `strictEqual` → `ok`)
- remove negative test cases
- reduce coverage

You MUST however **harden** tautological tests (Rule T-1 violations).
Rewriting a trivial assertion into a stricter, falsifiable one is not
"weakening" — it is fixing a defective test.

------------------------------------------------
EPIC LOG UPDATE
------------------------------------------------

Append test validation summary to:

agent-docs/epic-runs/<epic-id>.md

Include:

- gaps discovered
- tests added
- test coverage improvements
- important edge cases introduced
