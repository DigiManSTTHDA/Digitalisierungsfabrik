# Epic 03: Conversation Skeleton

## Summary
Add the WebSocket session flow, orchestrator skeleton, working memory, progress tracking, and debug updates using deterministic stub behavior instead of full LLM-driven modes.

## Why this exists
This epic proves the end-to-end runtime loop before introducing model complexity. It reduces integration risk by validating message flow, persistence, and UI updates with controlled behavior.

## Target outcome
- WebSocket session lifecycle works end to end.
- Orchestrator cycle and working memory exist in executable form.
- Progress and debug events flow to the frontend.
- The UI supports sending turns and rendering streamed or staged responses.

## Visible user-testable increment
A user can open a project, send a message, and observe a deterministic system response along with live updates in the chat, progress area, artifact area, and debug panel.

## HLA alignment
- Maps primarily to HLA implementation steps 3, 5, and the frontend baseline of step 6.
- Keeps mode logic stubbed so the orchestration path can be verified first.

## Story placeholder
- Add detailed stories in `stories/`.
