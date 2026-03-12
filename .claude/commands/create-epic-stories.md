# Create Epic Stories

Your task is to generate detailed implementation stories
for the next Epic.

The Epic exists but does not yet contain stories.

You must create them.

------------------------------------------------
MANDATORY REFERENCES
------------------------------------------------

Read and follow:

- AGENTS.md
- hla_architecture.md
- digitalisierungsfabrik_systemdefinition.md (SDD)

Stories must comply with all rules defined there.

------------------------------------------------
STEP 1 — READ THE EPIC
------------------------------------------------

Locate the next Epic that has no Stories section.

Extract:

- Epic summary
- goal
- testable increment
- key deliverables
- dependencies

------------------------------------------------
STEP 2 — MAP TO SDD
------------------------------------------------

Identify the SDD sections that the Epic implements.

For each component:

- find the SDD field tables
- identify required behaviour
- identify constraints

No SDD requirement may be omitted.

------------------------------------------------
STEP 3 — DESIGN STORY BREAKDOWN
------------------------------------------------

Split the Epic into small Stories.

Rules:

Stories must be:

- independently implementable
- testable
- architecture compliant

A story must produce a working increment.

Do not create oversized stories.

------------------------------------------------
STEP 4 — STORY STRUCTURE
------------------------------------------------

Each story must contain:

Title

User story:

As a developer  
I want ...  
So that ...

Acceptance Criteria

Definition of Done checklist

------------------------------------------------
STEP 5 — ACCEPTANCE CRITERIA
------------------------------------------------

Acceptance criteria must:

- list every SDD field if models are involved
- reference exact file paths from the architecture
- describe observable behaviour

Avoid vague criteria.

Bad:

"model implemented"

Good:

"backend/artifacts/models.py contains ExplorationArtifact
with fields slot_id, bezeichnung, inhalt..."

------------------------------------------------
STEP 6 — DEFINITION OF DONE
------------------------------------------------

Each structural requirement must have its own checkbox.

Examples:

[ ] backend/artifacts/models.py exists  
[ ] ExplorationArtifact contains all SDD fields  
[ ] ruff check backend/ passes  
[ ] pytest backend/tests/test_models.py passes  

Do not rely only on tool commands.

------------------------------------------------
STEP 7 — TEST REQUIREMENTS
------------------------------------------------

If a story introduces logic, it must define tests.

Rules:

- tests correspond to acceptance criteria
- both positive and negative cases

Test location must mirror source structure.

Example:

core/executor.py → tests/test_executor.py

------------------------------------------------
STEP 8 — ARCHITECTURE COMPLIANCE
------------------------------------------------

All file paths must match HLA architecture.

Reject invented paths.

------------------------------------------------
STEP 9 — OUTPUT
------------------------------------------------

Insert the Stories into the Epic document.

Each story must include:

- title
- user story
- acceptance criteria
- definition of done

------------------------------------------------
EPIC LOG UPDATE
------------------------------------------------

Append a short summary to:

agent-docs/epic-runs/<epic-id>.md

Include:

- generated stories
- purpose of each story

------------------------------------------------
EPIC LOG UPDATE
------------------------------------------------

Append story generation summary to:

agent-docs/epic-runs/<epic-id>.md

Include:

- generated stories
- purpose of each story