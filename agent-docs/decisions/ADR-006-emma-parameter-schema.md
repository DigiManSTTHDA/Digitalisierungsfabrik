# ADR-006: EMMA Parameter Schema Resolution (OP-02)

**Status:** accepted
**Date:** 2026-03-16

## Context

SDD 8.3 defines the EMMA action catalog with 18 action types but notes that
"Parameter pro Aktion sind aktuell nicht vollständig spezifiziert [OFFEN: OP-02]".
Epic 09 (Specification Mode) requires the Algorithm Artifact schema to be finalized
before the SpecificationMode can write EMMA actions to it.

Three aspects of `EmmaAktion` needed decisions:

1. **`aktionstyp`**: Was `str` — should it become a typed enum?
2. **`parameter`**: The SDD says "Key-Value" but doesn't define per-action parameter schemas.
3. **`nachfolger`**: SDD 5.5 says type `String` (singular), but DECISION actions need
   multiple successors for branching.

## Decision

1. **`aktionstyp`** → `EmmaAktionstyp` StrEnum with all 18 values from SDD 8.3:
   FIND, FIND_AND_CLICK, CLICK, DRAG, SCROLL, TYPE, READ, READ_FORM, GENAI,
   EXPORT, IMPORT, FILE_OPERATION, SEND_MAIL, COMMAND, LOOP, DECISION, WAIT, SUCCESS.

2. **`parameter`** → remains `dict[str, str]` for the prototype. The full EMMA parameter
   specification is not yet available. A flat string-keyed dict is flexible enough for
   the LLM to populate during specification and can be tightened later when EMMA provides
   typed parameter schemas per action type.

3. **`nachfolger`** → remains `list[str]` (deviation from SDD 5.5 which specifies `String`).
   This is required to support branching from DECISION actions where multiple successors
   are needed (e.g., true-branch and false-branch aktion_ids). A single string cannot
   represent this. The `END` sentinel is placed as a single-element list `["END"]`.

## Reason

- The enum provides compile-time safety and prevents hallucinated action types from the LLM.
- `dict[str, str]` is the minimal viable type — it allows the LLM to express parameters
  without constraining them to a schema that doesn't exist yet.
- `list[str]` for `nachfolger` is the minimum change needed to support control flow branching,
  which is core to the Algorithm Artifact's purpose as a control flow graph.

## Consequences

- `EmmaAktion.aktionstyp` now validates against the enum — invalid values are rejected
  by Pydantic. Existing tests that use arbitrary string values need updating.
- Adding a new EMMA action type requires adding it to the `EmmaAktionstyp` enum.
- When EMMA provides typed parameter schemas, `dict[str, str]` will be replaced with
  per-action-type parameter models (likely a union type or discriminated union).
- `nachfolger` as `list[str]` is a deliberate deviation from SDD 5.5's `String` type.

## SDD/HLA Reference

- SDD 5.5 (Algorithmusartefakt, EMMA-Aktion Felder)
- SDD 8.3 (EMMA-Aktionskatalog)
- OP-02 (EMMA parameter definition)
