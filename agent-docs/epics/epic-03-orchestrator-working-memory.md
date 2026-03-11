# Epic 03 – Orchestrator & Working Memory

## Summary

Build the `Orchestrator` – the central control loop that drives every conversation turn –
and the `WorkingMemory` component that holds the operational state for a session. In this
epic the cognitive modes (Exploration, Structuring, etc.) are replaced with lightweight
stubs that return hard-coded responses, so the full 11-step orchestrator cycle can be
exercised and persisted without any LLM calls.

This epic corresponds to **Implementation Step 3** in `AGENTS.md` / `hla_architecture.md`.

## Goal

A fully wired orchestrator cycle: receive user input → determine active mode → call mode
(stub) → collect patch operations → apply via Executor → update Working Memory → persist
state. All without LLM or HTTP.

## Testable Increment

- `pytest backend/tests/test_orchestrator.py` → all tests pass, including:
  - A full turn executes without error
  - Working Memory is updated after each turn
  - State is persisted to (in-memory) SQLite and can be restored
  - Mode stub is called with correct inputs
- Observable via test assertions; no UI required

## Dependencies

- Epic 01 (models and persistence)
- Epic 02 (Executor for patch application)

## Key Deliverables

- `backend/core/orchestrator.py` – `Orchestrator` class with 11-step cycle
- `backend/core/working_memory.py` – `WorkingMemory` class
- `backend/modes/base.py` – abstract `BaseMode` interface
- `backend/modes/stubs.py` – stub implementations of all modes (return no-op patches)
- `backend/tests/test_orchestrator.py` – full-cycle integration tests
- `backend/tests/test_working_memory.py` – Working Memory unit tests

## OpenAPI Contract Note

The `Orchestrator` and `WorkingMemory` are internal components with no direct API surface.
However, the `TurnInput` and `TurnOutput` types that `process_turn` accepts and returns
will become the payload types of the WebSocket messages in Epic 05. Define these as
Pydantic models (not plain dataclasses) so they can be exported as JSON schemas and
included in the OpenAPI spec without rework.

## Stories

_To be defined before this epic begins._
