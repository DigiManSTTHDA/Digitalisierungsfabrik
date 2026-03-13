# Audit Epic

Run a full repository audit and repair after an Epic implementation.

You are a strict architecture and compliance auditor.

Your job is to ensure that the repository fully complies with:

- AGENTS.md
- hla_architecture.md
- digitalisierungsfabrik_systemdefinition.md (SDD)
- the Epic document that was just implemented

Assume the implementation may contain errors.

You must verify and repair them.

------------------------------------------------
GLOBAL RULES
------------------------------------------------

You are NOT the implementer.
You are the auditor.

Never trust previous claims such as:
- "tests pass"
- "architecture followed"
- "DoD completed"

Always verify by reading code and running commands.

If something violates AGENTS.md or the SDD,
you must fix it.

------------------------------------------------
PHASE 1 — CONTEXT COLLECTION
------------------------------------------------

Read in full (small, always relevant):
- AGENTS.md

Read selectively (large documents — use offset/limit):
- HLA Section 6 only (file structure and module paths)
- SDD: read lines 6–82 (table of contents), then **always read Section 4
  in full** (FR lines ~256–569) — it is the primary compliance reference.
  Additionally read sections referenced in the Epic document.

Locate the epic document that was just implemented.

Extract:

- acceptance criteria
- Definition of Done checklist
- expected files and directories
- referenced SDD sections (these determine which SDD sections to read)

------------------------------------------------
PHASE 2 — ARCHITECTURE COMPLIANCE
------------------------------------------------

Verify the repository structure against HLA Section 6.

Check:

- backend/ structure
- frontend/ structure
- artifacts modules
- persistence modules
- llm modules
- api modules

Rules:

1. No directories outside the defined architecture.
2. No files placed in incorrect modules.
3. No invented module structure.

If violations exist:

Fix the structure.

------------------------------------------------
PHASE 3 — DEPENDENCY COMPLIANCE
------------------------------------------------

Verify dependencies against AGENTS.md Tech Stack.

Check:

backend/requirements.txt  
frontend/package.json  

Rules:

- No dependencies not listed in AGENTS.md.
- No hidden additions.
- No unnecessary libraries.

If a dependency was added without ADR:

remove it.

------------------------------------------------
PHASE 4 — SDD REQUIREMENTS COMPLIANCE
------------------------------------------------

This is critical.

Every implemented component must comply with the SDD.

Check:

1. Data models
2. Artifact schemas
3. executor logic
4. orchestrator logic
5. persistence behaviour
6. API endpoints

Verify that:

- every field defined in SDD tables exists in the models
- JSON Patch usage matches SDD
- artifact slot structure matches SDD
- persistence rules match SDD
- orchestration cycle matches SDD

If any SDD requirement is missing:

fix the implementation.

------------------------------------------------
PHASE 5 — TEST COVERAGE
------------------------------------------------

Check backend tests.

Rules:

- Every backend logic change must have tests.
- Tests must correspond to acceptance criteria.
- Tests must not be trivial.

Check:

- test locations mirror source structure
- positive tests exist
- negative tests exist

If missing:

add tests.

------------------------------------------------
PHASE 6 — DEFINITION OF DONE
------------------------------------------------

Run the DoD commands.

Backend:

cd backend

ruff check .
ruff format --check .
python -m mypy . --explicit-package-bases
pytest --tb=short -q

Frontend:

cd frontend

npm run lint
npm run format:check
npm run typecheck

If any command fails:

fix the issue.

Repeat until all commands pass.

------------------------------------------------
PHASE 7 — API CONTRACT COMPLIANCE
------------------------------------------------

If API endpoints changed:

Verify:

backend/api/schemas.py updated  
api-contract/openapi.json updated  
frontend/src/generated/api.d.ts regenerated  

Rules:

OpenAPI snapshot and generated types must be updated together.

If not:

regenerate them.

------------------------------------------------
PHASE 8 — CODE QUALITY
------------------------------------------------

Check:

- missing type hints
- incorrect imports
- unused code
- naming inconsistencies
- dead modules

Fix all issues.

------------------------------------------------
PHASE 9 — FINAL VERIFICATION
------------------------------------------------

Re-run all DoD commands.

Verify:

- architecture correct
- tests pass
- SDD requirements satisfied
- AGENTS.md rules satisfied

------------------------------------------------
OUTPUT
------------------------------------------------

Produce a structured report:

AUDIT REPORT
- architecture issues
- SDD compliance issues
- dependency issues
- test issues
- DoD issues

FIXES APPLIED
- list of repairs

FINAL STATUS

EPIC COMPLIANT WITH:

AGENTS.md: YES/NO  
HLA architecture: YES/NO  
SDD requirements: YES/NO  

If any item is NO, continue fixing until YES.

------------------------------------------------
EPIC LOG UPDATE
------------------------------------------------

Append audit results to:

agent-docs/epic-runs/<epic-id>.md

Include:

- architecture compliance
- SDD compliance
- dependency compliance