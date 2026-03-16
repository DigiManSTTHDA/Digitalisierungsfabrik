# Open Points Tracker

Tracks open points from `hla_architecture.md` Section 9.

| ID | Topic | Status | Resolution |
|---|---|---|---|
| OP-02 | EMMA parameter definition | resolved | ADR-006: `EmmaAktionstyp` StrEnum (18 values), `parameter: dict[str, str]` for prototype, `nachfolger: list[str]` for branching |
| OP-03 | Version history in UI | open | Resolve in frontend Step 6 |
| OP-04 | Max version count | open | Prototype: unlimited. Configurable limit post-prototype |
| OP-05 | Token thresholds | open | Placeholder values; calibrate after first test run |
| OP-06 | nearing_completion criteria | open | Define per mode during Step 8–9 |
| OP-07 | Control flags complete list | open | Base flags defined (SDD 6.4.1); complete during Step 7 |
| OP-11 | Dialog history scope | open | Prototype: full history in SQLite; estimate size after test runs |
| OP-12 | Project list in UI | open | Frontend component in Step 6 |
| OP-14 | LLM log format | open | `logs` table in SQLite: `timestamp, modus, turn_id, input_tokens, output_tokens, input_json, output_json` |
| OP-17 | Event log format | open | Prototype: free-text upload, no structured parsing |
| OP-20 | Repeated output contract violations | open | Prototype: error message + user retry. Post-prototype: configurable retry limit + moderator escalation |

## Already resolved (in current HLA v0.2)

The adversarial review (`hla_adversarial_review.md`) identified the following issues.
All were resolved in `hla_architecture.md` v0.2 before implementation started:

| Issue | Resolution |
|---|---|
| List-indexed artifact slots → RFC 6902 path instability | Dict-keyed slots throughout (HLA 3.6) |
| JSON files → multi-file atomicity problem | SQLite with ACID transactions (HLA 3.7) |
| Structured output not addressed | Tool Use strategy defined (HLA 2.5) |
| Chainlit coupling | FastAPI + React from the start (HLA 2.2) |
