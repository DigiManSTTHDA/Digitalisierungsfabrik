# ADR-008 — LLM Log Storage Deferred to Post-Prototype

**Status:** accepted
**Date:** 2026-03-17
**Resolves:** OP-14

## Context

OP-14 proposes a `llm_logs` table in SQLite to capture per-turn LLM usage metrics
(`timestamp`, `modus`, `turn_id`, `projekt_id`, `input_tokens`, `output_tokens`).

The prototype already has `llm_log_enabled: bool` in `config.py` and
`structlog`-based logging at the application level. Every LLM call emits
structured log lines visible in the console.

## Decision

**Defer the `llm_logs` database table to post-prototype.**

Rationale:
1. The prototype is a proof-of-concept with a single user session at a time.
   Console `structlog` output is sufficient for observability during validation.
2. Adding a `logs` table requires schema migration (DDL change in `schema.sql`),
   write calls in all three LLM client implementations (`anthropic_client.py`,
   `openai_client.py`, `ollama_client.py`), and tests — a non-trivial scope addition
   with no direct user-visible benefit in the prototype.
3. Token usage data from the Anthropic API is already available in log output;
   structured storage can be added if a cost-tracking or analytics requirement
   emerges after the prototype phase.

## Consequences

- `llm_log_enabled` in `config.py` remains as a placeholder for future use.
- Post-prototype: add `CREATE TABLE llm_logs (...)` DDL to `schema.sql`,
  inject `Database` into LLM clients, and write a row after each
  `complete()` call.
- No test coverage gap for current prototype scope.
