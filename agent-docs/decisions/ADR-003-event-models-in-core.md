---
id: ADR-003
title: WebSocket Event Models in backend/core/events.py
status: Accepted
date: 2026-03-13
---

# ADR-003: WebSocket Event Models in backend/core/events.py

## Context

Epic 04 defines 6 typed WebSocket event payloads (chat_token, chat_done,
artifact_update, progress_update, debug_update, error). These must be placed
in a module. Two options were considered:

- `backend/core/events.py` — framework-agnostic, in the Core layer
- `backend/api/schemas.py` — API layer, alongside REST schemas

HLA Section 6 does not list `events.py` explicitly but does define `backend/core/`
as the home of framework-agnostic infrastructure.

## Decision

Place event models in `backend/core/events.py`.

## Rationale

Events are core data structures emitted by the Orchestrator — they are not
API contracts. Placing them in `backend/api/` would create an upward dependency
(Core → API), violating the layering principle. Epic 05 WebSocket handlers will
import from `backend/core/events.py`, which is the correct direction (API depends
on Core, not the reverse).

## Consequences

- `backend/core/events.py` is added to the architecture (within the defined `backend/core/` directory — no new directory created)
- Epic 05 imports event models from `backend/core/events.py`
- `backend/api/schemas.py` remains for REST request/response schemas only
