---
id: ADR-002
title: Flags in WorkingMemory for Observability
status: Accepted
date: 2026-03-13
---

# ADR-002: Flags in WorkingMemory for Observability

## Context

SDD 6.4.1 states explicitly that mode-switch flags are *zyklus-lokal* (cycle-local):
they are emitted by a mode as part of its output, evaluated by the Orchestrator within
the same turn, and then discarded. The SDD text reads:

> Flags werden vom Modus als Teil seines Outputs zurückgegeben, vom Orchestrator im
> selben Zyklus ausgewertet und danach verworfen. Sie werden **NICHT** im Working Memory
> geschrieben und **NICHT** persistiert.

The `WorkingMemory` Pydantic model (`backend/core/working_memory.py`) therefore should
not contain a `flags` field according to the SDD.

## Decision

We store the flags from the most recent turn in `WorkingMemory.flags: list[str]`,
overwriting the previous value on every turn. The field is persisted to the
`working_memory` table as part of the regular JSON snapshot.

## Rationale

- **Observability / debugging**: Without this field there is no way to inspect the
  current flag state of a project from the database without replaying the last turn.
  During development and production support, being able to run a single SQL query and
  see `["phase_complete"]` in the JSON snapshot is invaluable.
- **Tooling integration**: External tools (monitoring dashboards, admin scripts) can
  read the flag state directly from the SQLite snapshot without any application logic.
- **Minimal risk**: The field is overwritten at the start of every turn, so stale values
  are bounded to a single turn's duration. The Orchestrator never reads `wm.flags` for
  control flow — it reads `mode_output.flags` from the live mode call instead. There is
  therefore no risk of stale flags influencing system behaviour.
- **Explicit deviation**: The deviation is documented here and in the source-code comment
  (`# Observabilität (SDD 6.4.1: nicht persistiert als Steuerung)`) so future maintainers
  understand the intent.

## Consequences

- `WorkingMemory.flags` appears in every JSON snapshot in the `working_memory` table.
- The field contains the flags from the *last completed* turn; it may show stale values
  if inspected between turns or if the process crashes mid-turn before the next `save()`.
- No code outside the Orchestrator should use `wm.flags` for control-flow decisions.
  The authoritative flag source is always `ModeOutput.flags` from the current mode call.
- Future epics that clear or rotate flags must update this field explicitly in the
  Orchestrator's turn cycle.
