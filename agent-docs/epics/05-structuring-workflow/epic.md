# Epic 05: Structuring Workflow

## Summary
Implement moderator-controlled phase progression into structuring mode and generate the process structure artifact from the exploration results, including invalidation behavior where needed.

## Why this exists
Once exploration becomes useful, the next visible value is turning raw findings into a structured process model. This epic introduces the first real cross-artifact dependency.

## Target outcome
- Moderator logic can recommend or trigger phase movement.
- Structuring mode creates and updates the structure artifact.
- Cross-artifact consistency rules begin to matter in implementation.
- Invalidations are surfaced to the user when upstream changes affect downstream state.

## Visible user-testable increment
A user can drive the prototype from exploration into a structured process view and see how the system organizes steps, relationships, and status changes.

## HLA alignment
- Maps to HLA steps 7 and 8.
- Extends the orchestration model with visible phase control.

## Story placeholder
- Add detailed stories in `stories/`.
