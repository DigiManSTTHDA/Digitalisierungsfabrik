# ADR-007: Validation Report Storage & Output Violation Retry Strategy

**Status:** accepted
**Date:** 2026-03-16

## Context

Epic 10 requires:
1. OP-20 resolution: How to handle repeated LLM output contract violations during validation.
2. A structured data model for the validation report (SDD 6.6.4).
3. A mechanism to pass the report from ValidationMode through the Orchestrator to the Moderator.

Additionally, SDD has an internal inconsistency: FR-C-08 AK(1) names the second
severity level `wichtig`, while SDD 6.6.4 Schweregradskala defines it as `warnung`.

## Decision

### OP-20: Retry Strategy
For the prototype, output contract violations during validation return an error
message to the user with a retry option. No automatic retry. A configurable
retry limit with moderator escalation is deferred to post-prototype.

### Severity Naming
Follow SDD 6.6.4 Schweregradskala (`warnung`) as the more specific, contextual
definition. FR-C-08's `wichtig` is treated as a synonym in the requirements —
the implementation uses `warnung` consistently.

### Validation Report Storage
The validation report (`Validierungsbericht`) is:
- A Pydantic model in `backend/artifacts/models.py` (not a raw dict)
- Stored in `WorkingMemory.validierungsbericht` (optional, None when no validation has run)
- Passed through `ModeOutput.validierungsbericht` from ValidationMode to the Orchestrator
- Persisted with the project via standard WorkingMemory JSON serialization
- Available to the Moderator and SpecificationMode as context

## Reason

**OP-20:** Automatic retry adds complexity for edge cases that rarely occur in
practice. The prototype prioritizes correctness over resilience — a manual retry
gives the user control and avoids silent loops.

**Severity naming:** SDD 6.6.4 provides the authoritative table with descriptions.
Using `warnung` ensures the codebase matches the Schweregradskala exactly.

**Storage in WorkingMemory:** The report must persist across turns (Moderator reads
it after the validation turn). Storing it in WorkingMemory (which is already
JSON-serialized and persisted per turn) is the simplest approach — no new DB table,
no new persistence mechanism.

## Consequences

- `Schweregrad` StrEnum uses `warnung` (not `wichtig`)
- `ModeOutput` gets an optional `validierungsbericht` field
- `WorkingMemory` gets an optional `validierungsbericht` field
- No automatic retry logic needed in the prototype
- Post-prototype: add configurable `MAX_OUTPUT_RETRIES` with moderator escalation

## SDD/HLA Reference

- SDD 6.6.4 (Validierungsmodus, Schweregradskala)
- SDD 6.1.3 (Validierungs-Korrekturschleife)
- FR-C-08 (Schweregradklassifikation)
- FR-C-09 (Validierungs-Korrekturschleife)
- OP-20 (Retry strategy for repeated output violations)
