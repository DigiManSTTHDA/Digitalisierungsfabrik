# Implement Next Epic

You are the implementation agent.

Your task is to implement the **next unfinished Epic** in the repository
according to the project rules.

The rules in AGENTS.md are authoritative and non-negotiable.

You must read and follow:

- AGENTS.md
- hla_architecture.md
- digitalisierungsfabrik_systemdefinition.md (SDD)
- the Epic document to implement

Never assume compliance — always verify.

------------------------------------------------
CORE NON-NEGOTIABLES
------------------------------------------------

Before writing any code, confirm the following:

1. AGENTS.md has been read completely.
2. Architecture in `hla_architecture.md` is binding.
3. Requirements in the SDD must be implemented fully.
4. Definition of Done rules must be followed exactly.

Important reminders:

- No architecture deviations without ADR.
- No new dependencies without ADR.
- No invented directory structure.
- File paths must match the architecture exactly.

------------------------------------------------
IMPLEMENTATION PROCESS
------------------------------------------------

Follow the workflow defined in AGENTS.md.

1. Identify the next unfinished Epic.
2. Read the Epic document.
3. Implement its Stories **one by one**.

For each Story:

1. Read acceptance criteria.
2. Identify the corresponding SDD

------------------------------------------------
EPIC LOG UPDATE
------------------------------------------------

Append implementation summary to:

agent-docs/epic-runs/<epic-id>.md

Include:

- stories implemented
- modules created
- architecture components added