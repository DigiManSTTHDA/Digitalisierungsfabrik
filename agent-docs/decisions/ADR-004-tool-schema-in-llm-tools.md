---
id: ADR-004
title: Anthropic Tool Schema in backend/llm/tools.py
status: Accepted
date: 2026-03-13
---

# ADR-004: Anthropic Tool Schema in backend/llm/tools.py

## Context

The `apply_patches` tool schema (JSON description sent to the Anthropic API for
Tool Use) must be defined somewhere. Two options were considered:

- `backend/modes/exploration.py` — local to ExplorationMode only
- `backend/llm/tools.py` — shared across all LLM-calling modes

All four cognitive modes (Exploration, Strukturierung, Spezifikation, Validierung)
will use the same `apply_patches` tool. HLA Section 6 defines `backend/llm/` as
the home for LLM infrastructure.

## Decision

Define the `apply_patches` tool schema in `backend/llm/tools.py`.

## Rationale

The tool schema is an LLM-layer concern, not a mode-layer concern. Defining it
once in `backend/llm/tools.py` avoids duplication across four mode implementations.
All future modes import the shared constant. Changes to the tool schema (e.g.,
adding a field) propagate automatically.

## Consequences

- `backend/llm/tools.py` is added (within the defined `backend/llm/` directory)
- All cognitive modes import `APPLY_PATCHES_TOOL` from `backend/llm/tools`
- Single source of truth for the Anthropic tool definition
