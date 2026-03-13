# Create Epic Stories

Your task is to generate detailed implementation stories
for the next Epic.

The Epic exists but does not yet contain stories.

You must create them.

------------------------------------------------
MANDATORY REFERENCES
------------------------------------------------

Read in full (small, always relevant):
- AGENTS.md
- HLA Section 6 only (file structure, ~150 lines) — use offset/limit

Do NOT read full SDD or full HLA upfront. Both are large (SDD ~1600 lines,
HLA ~740 lines). Load sections on demand as described below.

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

1. Read the SDD table of contents: docs/digitalisierungsfabrik_systemdefinition.md
   lines 6–82. It lists every section with its exact line number.
2. **Always read Section 4 completely** (FR lines ~256–569).
   Section 4 is the primary requirements contract — every story must
   trace back to at least one FR or NFR. Know all FRs before designing stories.
3. Identify which additional sections (5, 6, 7) are relevant to this Epic
   and read those sections via offset/limit.
2. Read only those specific SDD sections using offset/limit.
   Do not read sections unrelated to this Epic.

For each relevant section:

- find the SDD field tables
- identify required behaviour
- identify constraints

No SDD requirement from the relevant sections may be omitted.

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

**Story size guidance:**
- A story should be implementable in one focused session.
- If a story would produce a source file over 300 lines, split the story.
- If a story bundles multiple distinct responsibilities, split it.

**Library awareness:**
- Before designing a story that requires non-trivial logic, check whether
  a library in the tech stack already provides it.
- If yes: reference the library in the story's acceptance criteria.
- If a new library is needed: the story must include an ADR as a prerequisite.

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

Append story generation summary to:

agent-docs/epic-runs/<epic-id>.md

Include:

- generated stories
- purpose of each story
- libraries identified for use
- any escalation points flagged (SDD ambiguities requiring user decision)