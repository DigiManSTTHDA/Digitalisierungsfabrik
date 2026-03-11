# Decision Log

## 2026-03-11

### Decision
- Use `agent-docs/` as the mandatory operational memory for agents, with fixed files for session notes, task tracking, decisions, and architecture deviations.

### Rationale
- The user explicitly wants all tasks and decisions documented in `agent-docs`.
- A fixed structure reduces ambiguity and makes future agent handoffs predictable.
- The repository currently contains only high-level documentation, so workflow scaffolding is needed before implementation begins.

### Consequences
- Every non-trivial task now carries a documentation obligation.
- Agents must maintain `agent-docs` alongside code and tests.
