# Epic 07: Validation And Closure

## Summary
Implement validation mode, finding severity handling, correction loops, completion signals, download/export, and explicit user-controlled project closure.

## Why this exists
The prototype is not complete until it can critique its own outputs, guide correction, and allow the user to finish with transparent tradeoffs.

## Target outcome
- Validation mode produces structured findings against the artifacts.
- The system supports correction loops back into earlier phases.
- Completion state and phase status are visible and coherent.
- Export and completion flows reflect the current project state and warnings.

## Visible user-testable increment
A user can run validation, review findings, iterate on corrections, and explicitly finish a project with a downloadable result bundle and clear warnings if issues remain.

## HLA alignment
- Maps directly to HLA step 10 and the SDD completion model.
- Completes the intended end-to-end process from exploration to validation.

## Story placeholder
- Add detailed stories in `stories/`.
