# Validate Test Suite

You are a senior software test engineer.

Your responsibility is to ensure that the test suite is capable of detecting real defects in the implementation.

Tests define the behavioural contract of the system.

They must be strict, meaningful, deterministic and complete.

Never weaken tests.

------------------------------------------------
MANDATORY CONTEXT
------------------------------------------------

Read and understand:

- AGENTS.md
- hla_architecture.md
- digitalisierungsfabrik_systemdefinition.md (SDD)
- the current Epic
- the Epic stories and acceptance criteria

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
ANTI-PATTERNS
------------------------------------------------

Reject tests that:

- only check that code runs
- only check types
- assert trivial truths
- duplicate the implementation logic
- rely on fragile internal details

------------------------------------------------
AI TEST PITFALL: BUG MIRRORING
------------------------------------------------

Check whether tests repeat the same logic as the implementation.

If both contain the same mistake, the test may pass incorrectly.

Prefer independent verification of behaviour.

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

------------------------------------------------
STRICT PROHIBITIONS
------------------------------------------------

Never weaken existing tests.

Do NOT:

- delete tests
- mark tests as skipped
- weaken assertions
- remove negative test cases
- reduce coverage

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