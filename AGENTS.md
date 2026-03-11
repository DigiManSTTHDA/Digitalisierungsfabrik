# Digitalisierungsfabrik Agent Guide

## Mission
- Build a working prototype that fulfills the requirements in `digitalisierungsfabrik_systemdefinition.md`.
- Treat the prototype as a value-validation vehicle and a reference implementation for a later product team, not as the final production system.
- Follow `hla_architecture.md` as the default implementation baseline. Any intentional deviation must be documented in `agent-docs/architecture-deviations.md` before or during implementation.

## Source Of Truth
1. `AGENTS.md`
2. `digitalisierungsfabrik_systemdefinition.md`
3. `hla_architecture.md`
4. `hla_adversarial_review.md` for risk awareness and challenge material

If documents conflict, prefer the higher entry and document the conflict in `agent-docs/decision-log.md`.

## Scope Guardrails
- Scope target: working prototype.
- Optimize for clarity, traceability, and learning value.
- Preserve the architecture constraints from `hla_architecture.md` unless a documented deviation is justified.
- Keep frontend and backend separated as defined in the HLA.
- Keep the system single-user, German-language, and within the explicit prototype limits from the SDD.
- Do not quietly expand scope into production-hardening work unless it is required to satisfy the prototype requirements.

## Required Documentation
Everything must be documented in `agent-docs/`. At minimum, update these files as part of every non-trivial task:

- `agent-docs/task-log.md`
  - Record the task goal, status, touched areas, tests, and resulting commits.
- `agent-docs/decision-log.md`
  - Record meaningful implementation decisions, tradeoffs, assumptions, and document conflicts.
- `agent-docs/architecture-deviations.md`
  - Record every deviation from `hla_architecture.md`, with rationale, impact, and follow-up implications.
- `agent-docs/session-notes.md`
  - Keep a concise running journal of current work so another agent can resume without rereading the full repo.

Documentation expectations:
- Update `session-notes.md` when starting a task, when the plan materially changes, and before ending work.
- Update `task-log.md` when a task starts and when it completes.
- Update `decision-log.md` whenever a decision is non-obvious, affects later work, or constrains the design.
- If no architecture deviation was made, do not invent one.
- If TDD is not applicable for a task, state why in `task-log.md`.

## Delivery Workflow
1. Read the relevant sections of the SDD and HLA before changing code.
2. Document the task in `agent-docs/session-notes.md` and `agent-docs/task-log.md`.
3. Prefer TDD where applicable:
   - write or update a failing test first
   - implement the smallest change to make it pass
   - refactor while keeping tests green
4. Run the relevant tests and record what was executed in `agent-docs/task-log.md`.
5. Commit frequently in small, coherent increments.
6. If a task introduces a design change, document the decision and any HLA deviation before concluding the task.

## TDD Rules
- TDD is the default for code changes where behavior can be exercised through automated tests.
- Start at the most relevant layer for the change:
  - unit tests for pure models, validation, executor, progress tracking, context assembly
  - integration tests for repository/database behavior and FastAPI endpoints
  - frontend component or UI-flow tests where frontend behavior changes materially
- For bug fixes, add or adjust a test that reproduces the bug before changing the implementation.
- For exploratory spikes, documentation-only tasks, or scaffolding where tests are not yet meaningful, document why TDD was not applicable.

## Commit Rules
- Commit frequently. Default expectation: commit after each coherent green increment.
- Do not let unrelated changes accumulate in one commit.
- Each commit should leave the repo in a usable state or clearly scoped partial state with matching documentation.
- Reference documentation updates in the same commit as the code they describe whenever practical.
- Suggested commit style:
  - `docs(agent-docs): define operating workflow`
  - `feat(backend): add project repository skeleton`
  - `test(executor): cover invalid patch rollback`

## Architecture Compliance
- Implement in the order described in `hla_architecture.md` unless there is a strong reason not to.
- Preserve the core stack unless a documented deviation is required:
  - backend: Python, FastAPI, Pydantic v2, SQLite, jsonpatch, structlog
  - frontend: React, Vite, TypeScript
- Respect the defined responsibilities of:
  - Orchestrator
  - Executor
  - Working Memory
  - Modes
  - Artifact Store
  - Persistence Layer
  - LLM Client
- Keep RFC 6902 JSON Patch semantics for artifact write operations.

## Documentation-Driven Decisions
- When a requirement is ambiguous, prefer the interpretation that best supports prototype learning value and architectural clarity.
- Document open questions and temporary assumptions in `agent-docs/decision-log.md`.
- If the implementation must contradict the SDD or HLA, record:
  - what is changing
  - why the original approach is insufficient
  - prototype impact
  - what a production team should revisit later

## Handoff Standard
Before ending a work session:
- update `agent-docs/session-notes.md` with current status and next steps
- ensure `agent-docs/task-log.md` reflects the latest task state
- ensure decisions and deviations are documented
- leave the repo with passing relevant tests, or explicitly document what is failing and why
