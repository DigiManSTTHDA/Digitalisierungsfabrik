# Validate Epic and Stories

You are a strict specification validator.

Your task is to verify that an Epic and its Stories comply with:

- AGENTS.md
- hla_architecture.md
- digitalisierungsfabrik_systemdefinition.md (SDD)

You are NOT implementing code.

You are validating the Epic specification.

Assume the Epic may contain mistakes.

------------------------------------------------
PHASE 1 — DOCUMENT COLLECTION
------------------------------------------------

Read the following documents:

AGENTS.md
hla_architecture.md
digitalisierungsfabrik_systemdefinition.md

Then read the Epic document provided by the user.

Extract:

- Epic goal
- testable increment
- key deliverables
- story list
- acceptance criteria
- definition of done

------------------------------------------------
PHASE 2 — EPIC STRUCTURE VALIDATION
------------------------------------------------

Verify the Epic contains:

- Summary
- Goal
- Testable Increment
- Dependencies
- Key Deliverables
- Stories

Check:

The testable increment must be a runnable verification.

Examples:

- pytest run
- API endpoint test
- script execution

Reject vague increments.

------------------------------------------------
PHASE 3 — STORY STRUCTURE VALIDATION
------------------------------------------------

Each story must contain:

- description (As a / I want / so that)
- acceptance criteria
- definition of done

If any are missing:

report an error.

------------------------------------------------
PHASE 4 — SDD COMPLIANCE
------------------------------------------------

This is mandatory.

For every story:

identify which SDD section it implements.

Verify:

All required fields from SDD tables are listed in the story acceptance criteria.

Rules:

- No SDD field may be missing.
- No invented fields allowed.

If missing:

list them.

------------------------------------------------
PHASE 5 — ARCHITECTURE COMPLIANCE
------------------------------------------------

Verify file paths referenced in the Epic.

Rules:

Paths must match HLA Section 6 exactly.

Reject:

- invented directories
- misplaced modules
- approximate paths

Example violation:

backend/models.py

Correct path:

backend/artifacts/models.py

------------------------------------------------
PHASE 6 — TEST REQUIREMENTS
------------------------------------------------

Verify that stories introducing logic include tests.

Rules:

- backend logic requires pytest tests
- tests must correspond to acceptance criteria
- tests must cover both success and failure cases

Reject stories that introduce logic but do not define tests.

------------------------------------------------
PHASE 7 — DEFINITION OF DONE VALIDATION
------------------------------------------------

Verify DoD checklist quality.

Rules:

Each structural requirement must have its own checkbox.

Bad example:

[ ] npm run lint

Good example:

[ ] frontend/eslint.config.js exists  
[ ] npm run lint passes

Also verify:

DoD commands include required backend commands:

ruff check .
ruff format --check .
python -m mypy .
pytest

------------------------------------------------
PHASE 8 — API CONTRACT RULES
------------------------------------------------

If the Epic introduces API endpoints:

Verify the story includes:

- Pydantic schemas
- OpenAPI snapshot update
- TypeScript type regeneration

Files required:

backend/api/schemas.py  
api-contract/openapi.json  
frontend/src/generated/api.d.ts

------------------------------------------------
PHASE 9 — IMPLEMENTABILITY
------------------------------------------------

Verify the Epic can be implemented incrementally.

Rules:

Each story must produce a working system increment.

Reject stories that:

- require future components
- break earlier functionality

------------------------------------------------
OUTPUT
------------------------------------------------

Produce a report:

EPIC VALIDATION REPORT

1. Structure Issues
2. SDD Compliance Issues
3. Architecture Issues
4. Test Issues
5. DoD Issues

Then give:

EPIC VALID: YES / NO

If NO:

list required corrections.

------------------------------------------------
EPIC LOG UPDATE
------------------------------------------------

Append validation results to:

agent-docs/epic-runs/<epic-id>.md

Include:

- validation outcome
- issues found
- corrections applied