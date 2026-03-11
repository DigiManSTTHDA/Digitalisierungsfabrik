# Epic 01: Project Persistence

## Summary
Implement the project model, SQLite persistence layer, and the ability to create, load, and inspect empty prototype projects with their initial artifact state.

## Why this exists
The prototype needs stable project storage before any orchestration or LLM-driven work can be trusted. This epic turns the shell into a stateful system.

## Target outcome
- SQLite schema exists for projects and core state.
- Project repository supports create, load, list, and save operations.
- Empty artifacts and working memory can be persisted and restored.
- Basic REST endpoints expose project creation and retrieval.

## Visible user-testable increment
A user can create a project, reload the page or restart the backend, and still see the same project and initial artifact state.

## HLA alignment
- Maps directly to HLA implementation step 1.
- Establishes the persistence constraints required for later atomic saves.

## Story placeholder
- Add detailed stories in `stories/`.
