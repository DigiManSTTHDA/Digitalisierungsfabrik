# Validate Test Suite

You are a senior software test engineer.

Your responsibility is to ensure that the test suite is capable of detecting real defects in the implementation.

Tests define the behavioural contract of the system.

They must be strict, meaningful, deterministic and complete.

Never weaken tests.

------------------------------------------------
MANDATORY CONTEXT
------------------------------------------------

Read in full (small, always relevant):
- AGENTS.md
- the current Epic and its acceptance criteria

Read selectively (large documents — use offset/limit):
- HLA Section 6 only (to verify test file locations mirror source structure)
- SDD: read only the sections referenced in the Epic stories

Tests must validate the behaviour defined in these documents.

------------------------------------------------
GOAL
------------------------------------------------

Ensure that the test suite:

- validates observable system behaviour
- detects incorrect implementations
- covers edge cases and boundary conditions
- prevents regressions
- reflects the SDD and acceptance criteria

------------------------------------------------
TEST COVERAGE ANALYSIS
------------------------------------------------

Inspect the entire test suite.

Verify that the following components are tested:

- public functions
- API endpoints
- repository operations
- persistence behaviour
- artifact models
- orchestration logic

Every important behaviour must have at least one test.

------------------------------------------------
BEHAVIOUR VALIDATION
------------------------------------------------

Tests must validate observable behaviour.

Avoid tests that depend on:

- private functions
- internal helper methods
- implementation details
- internal state

Tests should focus on inputs and outputs.

------------------------------------------------
EDGE CASE TESTING
------------------------------------------------

Ensure tests cover edge cases such as:

- empty inputs
- null / None values
- invalid formats
- missing fields
- duplicate entries
- malformed requests
- invalid state transitions

------------------------------------------------
BOUNDARY VALUE TESTING
------------------------------------------------

Verify boundary conditions such as:

- minimum allowed values
- maximum allowed values
- length limits
- numeric limits
- empty collections vs single item vs many items

------------------------------------------------
NEGATIVE TESTS
------------------------------------------------

Invalid inputs must produce failures.

Ensure tests verify:

- error responses
- raised exceptions
- validation failures
- rejected operations

Errors must be asserted explicitly.

------------------------------------------------
ASSERTION QUALITY
------------------------------------------------

Reject weak assertions such as:

assert result is not None  
assert len(result) > 0  

Prefer strict behavioural assertions:

assert result == expected_value  
assert response.status_code == 400  

Assertions must clearly detect incorrect behaviour.

------------------------------------------------
REGRESSION PROTECTION
------------------------------------------------

Ensure the test suite prevents behaviour regressions.

When fixing a bug:

add a regression test that fails without the fix.

------------------------------------------------
CONTRACT VALIDATION
------------------------------------------------

Verify that API behaviour matches defined schemas.

Check:

- response fields
- field types
- required vs optional fields
- error response structure

Ensure API responses comply with the OpenAPI contract.

------------------------------------------------
PROPERTY VALIDATION
------------------------------------------------

Where possible, verify system properties such as:

- idempotency
- invariants
- round-trip consistency

Examples:

save → load → same object

------------------------------------------------
TEST ISOLATION
------------------------------------------------

Tests must:

- not depend on execution order
- not depend on other tests
- not share mutable global state

Each test must set up its own data.

------------------------------------------------
DETERMINISM
------------------------------------------------

Tests must produce the same result every run.

Avoid:

- random inputs
- time-dependent behaviour
- environment-dependent behaviour

------------------------------------------------
TEST DATA QUALITY
------------------------------------------------

Use minimal and meaningful test data.

Avoid overly complex fixtures.

Each test should create only the data it needs.

------------------------------------------------
ANTI-PATTERNS — TAUTOLOGICAL TEST DETECTION
------------------------------------------------

For EVERY test, apply Rule T-1: "What code change would make this fail?"
If the answer is "nothing reasonable", the test is tautological.

Reject and **rewrite** tests that:

- only check that code runs without verifying the result
- only check types or isinstance
- assert trivial truths (enum values equal themselves, constructor defaults)
- duplicate the implementation logic (bug mirroring)
- rely on fragile internal details
- only verify serialization round-trips without domain logic
- check enum member count (`len(MyEnum) == N`)
- verify that a constructor returns the values passed to it

**Action when found:** Do NOT leave tautological tests in place. Rewrite the
assertions to test real, falsifiable behaviour. Keep the test function name
and location — replace the body with meaningful assertions.

Example — BEFORE (tautological):
```python
def test_artifact_default():
    art = ExplorationArtifact()
    assert art.slots == {}  # just tests constructor default
```

Example — AFTER (hardened):
```python
def test_artifact_empty_slots_counted_as_zero_completeness():
    art = ExplorationArtifact()
    calc = CompletenessCalculator()
    _, filled, known = calc.calculate(art, StructureArtifact(), AlgorithmArtifact())
    assert filled == 0
    assert known == 0
```

------------------------------------------------
AI TEST PITFALL: BUG MIRRORING
------------------------------------------------

Check whether tests repeat the same logic as the implementation.

If both contain the same mistake, the test may pass incorrectly.

Prefer independent verification of behaviour.

------------------------------------------------
INFRASTRUCTURE TESTS (Rule T-5)
------------------------------------------------

For every component that manages resources (DB connections, file handles,
external clients), verify:

- Resources are properly released after use
- FastAPI dependencies use generator pattern (yield + finally)
- Database connections are closed — not leaked
- Error during cleanup does not mask the original error

Example check:

```python
import inspect
from api.router import _get_repository
assert inspect.isgeneratorfunction(_get_repository)
```

------------------------------------------------
ERROR PROPAGATION TESTS (Rule T-6)
------------------------------------------------

For every component that can fail, verify:

- DB errors (connection closed, disk full) propagate or return meaningful errors
- LLM errors produce user-facing error messages, not silent swallows
- Error messages are non-empty and contain actionable information
- Bare `except Exception` blocks are flagged and each catch path is tested

Every `except` block in production code MUST have a corresponding test
that triggers it.

------------------------------------------------
BOUNDARY VALUE TESTS (Rule T-7)
------------------------------------------------

For every validated input, test:

- Exact boundary: max_length=200 → test 200 (pass) AND 201 (fail)
- Empty input where non-empty required
- Whitespace-only where content required
- Large inputs (100+ items in collections)
- Zero/null/None where positive required

------------------------------------------------
TEST HARDENING
------------------------------------------------

If gaps exist:

create additional tests.

Examples:

- invalid artifact schema
- executor patch failure
- persistence rollback
- API validation errors
- invalid orchestration steps
- resource cleanup after errors
- error message content verification

------------------------------------------------
STRICT PROHIBITIONS
------------------------------------------------

Never weaken existing tests. Never delete tests to make the suite green.

Do NOT:

- delete tests to suppress failures
- mark tests as skipped
- weaken assertions (e.g. `== 5` → `>= 0`)
- remove negative test cases
- reduce coverage

You MUST however **harden** tautological tests (Rule T-1 violations).
Rewriting a trivial assertion into a stricter, falsifiable one is not
"weakening" — it is fixing a defective test. The test function stays,
the body gets stronger assertions that test real behaviour.

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