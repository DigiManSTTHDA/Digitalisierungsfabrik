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

## 2026-03-11

### Decision
- Organize implementation planning under `agent-docs/epics/`, with one folder per epic containing an `epic.md` summary and a `stories/` subfolder reserved for later breakdown.

### Rationale
- The user explicitly wants epic definitions first and story detail later.
- A folder-per-epic structure keeps summary, future stories, and eventual acceptance notes grouped together.
- This structure also makes progress easy to review incrementally without rewriting a single large roadmap document.

### Consequences
- The implementation timeline will be traceable at epic level before story planning starts.
- Future agents can add stories without restructuring the planning artifacts.
