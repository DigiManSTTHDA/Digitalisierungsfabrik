# Open Points Tracker

Tracks open points from `hla_architecture.md` Section 9.

| ID | Topic | Status | Resolution |
|---|---|---|---|
| OP-02 | EMMA parameter definition | resolved | ADR-006: `EmmaAktionstyp` StrEnum (18 values), `parameter: dict[str, str]` for prototype, `nachfolger: list[str]` for branching |
| OP-03 | Version history in UI | resolved | REST endpoint `GET /api/projects/{id}/artifacts/{typ}/versions` implemented (FR-B-10). ArtifactPane shows current artifact content per FR-B-06. Version count display not required for prototype. |
| OP-04 | Max version count | resolved | Prototype: unlimited. No max enforced. Configurable limit deferred to post-prototype production system. |
| OP-05 | Token thresholds | deferred | Placeholder values (`token_warn_threshold=80_000`, `token_hard_limit=100_000`) in `config.py`. Calibration requires production usage data. Deferred to post-prototype. |
| OP-06 | nearing_completion criteria | resolved | Implemented per mode: ExplorationMode — all 9 Pflicht-Slots non-leer; StructuringMode — no Strukturschritte with `completeness_status=leer`; SpecificationMode — all Algorithmusabschnitte `vollstaendig`; ValidationMode — `ist_bestanden=True`. Guardrails enforce in each mode's `_apply_guardrails()`. |
| OP-07 | Control flags complete list | resolved | Final flag set: `Flag.phase_complete` (signals Moderator to propose phase transition). All flags defined in `modes/base.py`. Additional flags (panic, escalate) not required for prototype. |
| OP-11 | Dialog history scope | resolved | Full dialog history stored in SQLite `dialog_history` table (FR-E-07). `load_dialog_history(last_n)` retrieves the N most recent turns per project. No size limit enforced in prototype. |
| OP-12 | Project list in UI | resolved | Project list implemented in `App.tsx` — fetches from `GET /api/projects`, renders project cards with create/delete/select actions. |
| OP-14 | LLM log format | deferred | ADR-008: `llm_logs` database table deferred to post-prototype. Console structlog output sufficient for prototype observability. `llm_log_enabled` flag reserved in `config.py`. |
| OP-17 | Event log format | resolved | Prototype: free-text upload, no structured event log parsing. Structured event log format deferred to production system. |
| OP-20 | Repeated output contract violations | resolved | ADR-007: Prototype uses error message + user retry. No auto-retry. Configurable retry limit deferred to post-prototype. |

## Already resolved (in current HLA v0.2)

The adversarial review (`hla_adversarial_review.md`) identified the following issues.
All were resolved in `hla_architecture.md` v0.2 before implementation started:

| Issue | Resolution |
|---|---|
| List-indexed artifact slots → RFC 6902 path instability | Dict-keyed slots throughout (HLA 3.6) |
| JSON files → multi-file atomicity problem | SQLite with ACID transactions (HLA 3.7) |
| Structured output not addressed | Tool Use strategy defined (HLA 2.5) |
| Chainlit coupling | FastAPI + React from the start (HLA 2.2) |
