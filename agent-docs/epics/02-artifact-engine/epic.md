# Epic 02: Artifact Engine

## Summary
Implement artifact models, template schema derivation, version handling, and the RFC 6902 patch execution pipeline with validation and rollback behavior.

## Why this exists
The artifact system is the core external memory of the prototype. Before conversational intelligence is added, the system must be able to change artifact state safely and predictably.

## Target outcome
- Pydantic models define the artifact schemas.
- Template schema generation is available for downstream use.
- Executor validates and applies JSON Patch operations.
- Failed patch application rolls back safely.
- Artifact version snapshots are stored and recoverable.

## Visible user-testable increment
A user can trigger or inspect artifact changes through the API or a simple debug flow, see version history, and restore a previous artifact state after a change.

## HLA alignment
- Maps directly to HLA implementation step 2.
- Preserves the HLA requirement for RFC 6902-based artifact writes.

## Story placeholder
- Add detailed stories in `stories/`.
