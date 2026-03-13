# Management Summary

Produce a management-level summary after completing an Epic.

Audience: technically literate stakeholder who is not a software developer.

The summary must explain clearly:

- what has been implemented
- how this contributes to the overall system goal
- what SDD requirements are now fulfilled
- what risks remain

------------------------------------------------
INPUT SOURCES
------------------------------------------------

Read in full (small, always relevant):
- AGENTS.md
- the Epic document

Read selectively (large documents — use offset/limit):
- HLA: read section headings and Section 6 only
- SDD: read lines 6–80 (table of contents) — sufficient for Section 10
  (SDD Coverage overview); read content only for sections referenced
  in this Epic

Also inspect:

- the Epic document that was just implemented
- relevant commits
- implemented code modules
- test results
- agent-docs/epic-runs/<epic-id>.md
- agent-docs/decisions/ (ADRs written during or before this Epic)

------------------------------------------------
SECTION 1 — EPIC SUMMARY
------------------------------------------------

Explain in simple terms:

- what this Epic implemented
- which system capability it adds
- why this capability matters for the Digitalisierungsfabrik prototype

Keep explanations understandable for non-developers.

------------------------------------------------
SECTION 2 — IMPLEMENTED COMPONENTS
------------------------------------------------

List the main components implemented in this Epic.

For each component explain:

- its purpose
- which files/modules implement it
- how it fits into the system architecture

Example structure:

Component  
Purpose  
How it interacts with other parts of the system

------------------------------------------------
SECTION 3 — SDD PROGRESS
------------------------------------------------

Identify which SDD sections are now implemented.

Explain:

- which SDD requirements are fulfilled
- which are partially implemented
- which remain unimplemented

Provide a short progress estimate.

Example:

Exploration phase components → implemented  
Executor patch mechanism → implemented  
Validation mode → not implemented yet

------------------------------------------------
SECTION 4 — TEST STATUS
------------------------------------------------

Summarize the testing situation.

Include:

- number of tests
- whether the test suite passes
- what types of behaviour are covered

Explain what the tests guarantee about system correctness.

------------------------------------------------
SECTION 4a — KEY DECISIONS (ADRs)
------------------------------------------------

List every Architecture Decision Record written during or before this Epic.

For each ADR:

- What decision was made
- Why (the key trade-off that made this non-trivial)
- What the alternative(s) were
- What risk or consequence the decision carries

This section surfaces the intellectual work behind the implementation —
the choices that shaped how the system was built and why it looks the way it does.

If no ADRs were written: state "No new decisions recorded in this Epic."

------------------------------------------------
SECTION 5 — PROBLEMS ENCOUNTERED
------------------------------------------------

Describe any problems that occurred during implementation.

Examples:

- architecture issues
- failing tests
- SDD ambiguities
- dependency issues

Explain briefly how they were resolved.

------------------------------------------------
SECTION 6 — REMAINING ISSUES
------------------------------------------------

List any known limitations or incomplete areas.

Examples:

- partial implementation
- missing modes
- technical debt
- performance concerns

------------------------------------------------
SECTION 7 — SYSTEM INTEGRATION
------------------------------------------------

Explain how the implemented components interact.

Describe the flow at a high level.

Example:

User input  
→ Orchestrator  
→ Mode  
→ Executor  
→ Artifact update  
→ Persistence

This section should help understand the system as a whole.

------------------------------------------------
SECTION 8 — PROJECT PROGRESS
------------------------------------------------

Estimate progress toward the prototype goal.

Explain:

- what capabilities are already working
- what still needs to be built
- how close the system is to a full end-to-end run

------------------------------------------------
SECTION 9 — PROJECT STATUS OVERVIEW
------------------------------------------------

Provide a high-level overview of the entire project.

Analyze:

- which Epics exist
- which Epics are already implemented
- which Epics remain
- which core system components exist in the repository

Sources:

- Epic documents
- agent-docs/epic-runs/
- repository structure

Produce a short overview:

Completed Epics
List Epics that are fully implemented.

Current Epic
Identify the Epic that was just completed.

Remaining Epics
List Epics that are not yet implemented.

------------------------------------------------
SECTION 10 — SDD COVERAGE
------------------------------------------------

Evaluate overall SDD implementation progress.

Identify:

- which SDD sections are implemented
- which are partially implemented
- which are not yet implemented

Provide an approximate progress estimate for the prototype.


------------------------------------------------
SECTION 11 — MAJOR RISKS
------------------------------------------------

Identify major technical or project risks.

Examples:

- architecture complexity
- unclear SDD areas
- components not yet implemented
- integration risks

Explain potential impact.

------------------------------------------------
SECTION 12 — NEXT STEPS
------------------------------------------------

Explain what the next Epic will implement
and how it moves the system closer to the final goal.

------------------------------------------------
OUTPUT
------------------------------------------------

Write the report to:

agent-docs/reports/<epic-id>-summary.md

The output must be a Markdown document.

Do not print the report only to the terminal.

------------------------------------------------
OUTPUT STYLE
------------------------------------------------

Use clear language.

Avoid unnecessary code details.

Focus on understanding and progress.