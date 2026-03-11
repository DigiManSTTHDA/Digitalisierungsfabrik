# Epic 04: Exploration Workflow

## Summary
Implement the first real LLM-backed workflow: context assembly, output validation, exploration mode, file input handling, and live population of the exploration artifact.

## Why this exists
This is the first epic where the prototype should produce core product value. It enables structured knowledge extraction from user dialogue and uploaded source material.

## Target outcome
- LLM client abstraction is operational with at least one provider.
- Context assembly and output contract validation are in place.
- Exploration mode writes to the exploration artifact through the executor.
- File uploads can be ingested in the prototype-supported formats.
- Chat responses stream while artifact changes remain structured.

## Visible user-testable increment
A user can upload or paste process information, converse with the system, and see the exploration artifact grow with structured extracted knowledge.

## HLA alignment
- Maps directly to HLA implementation step 4 and completes the first meaningful product loop.
- Establishes the mode pattern used by later cognitive modes.

## Story placeholder
- Add detailed stories in `stories/`.
