# Implementation Timeline – Epics

Each epic delivers a **visible, user-testable increment**. No epic ends in an invisible or
untestable state. Epics must be completed in order; each one builds on the previous.

Stories (detailed tasks) are tracked inside each epic file and will be added before work
on that epic begins.

---

## Epic Overview

| ID | Title | Testable Increment |
|----|-------|--------------------|
| [00](epic-00-project-foundation.md) | Project Foundation & Dev Setup | `pytest` passes, health endpoint responds, `npm run dev` starts |
| [01](epic-01-data-models-persistence.md) | Data Models & Persistence | Project can be created, saved, and reloaded from SQLite |
| [02](epic-02-execution-engine.md) | Execution Engine (Executor + JSON Patch) | Patches apply to artifacts; invalid patches roll back cleanly |
| [03](epic-03-orchestrator-working-memory.md) | Orchestrator & Working Memory | Full orchestrator cycle runs with stub modes; state is persisted |
| [04](epic-04-exploration-llm.md) | Exploration Mode & LLM Integration | User message → AI response in Exploration phase via API call |
| [05](epic-05-backend-api.md) | Backend API (REST + WebSocket) | Entire backend is testable via Postman / curl / automated tests |
| [06](epic-06-react-frontend.md) | React Frontend (Chat + Artifact pane) | User opens browser, starts a session, chats with the AI |
| [07](epic-07-moderator-phase-transitions.md) | Moderator & Phase Transitions | System automatically advances from Exploration → Structuring |
| [08](epic-08-structuring-mode.md) | Structuring Mode | User reaches Structuring phase and sees structured process artifact |
| [09](epic-09-specification-mode.md) | Specification Mode | User receives a complete EMMA RPA-ready algorithm artifact |
| [10](epic-10-validation-correction.md) | Validation & Correction Loop | User validates artifacts and can correct inconsistencies |
| [11](epic-11-end-to-end-stabilization.md) | End-to-End Stabilization & Export | Full flow works; user downloads all artifacts as JSON + Markdown |

---

## Sequencing Rules

- Epics **0 → 11** must be completed in order.
- Each epic has a clear **Definition of Done** before the next may begin.
- Stories are added to an epic file **before** work on that epic starts.
- Any architectural deviation from `hla_architecture.md` requires an ADR in
  `agent-docs/decisions/` before implementation.
