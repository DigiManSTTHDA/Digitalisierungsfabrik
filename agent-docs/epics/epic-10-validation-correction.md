# Epic 10 – Validation Mode & Correction Loop

## Summary

Implement `ValidationMode` and the correction loop it can trigger. After all three
artifacts are populated, the Moderator transitions to the Validation phase. The system
reviews the artifacts for internal consistency and completeness, presents findings to the
user, and – if issues are found – re-enters the relevant earlier mode to correct them
before returning to validation.

This epic corresponds to **Implementation Step 10** in `AGENTS.md` / `hla_architecture.md`.

## Goal

The system autonomously validates the full artifact set, surfaces any gaps or
inconsistencies in plain German, and guides the user through corrections. The correction
loop can cycle back to Exploration, Structuring, or Specification as needed and then
re-validate until all artifacts pass.

## Testable Increment

- In the browser:
  - Starting from a set of complete but deliberately flawed artifacts (seeded test data),
    the Validation phase surfaces at least one issue to the user
  - The user responds, the system enters the correction sub-loop, patches the relevant
    artifact, and re-validates
  - When all artifacts pass validation, a success message is shown
- `pytest backend/tests/test_validation_mode.py` → correction loop iterates correctly;
  clean artifacts pass in a single turn; flawed artifacts trigger at least one loop
- Open point OP-20 (retry strategy for repeated output violations) resolved via ADR

## Dependencies

- Epic 09 (all three artifact types must be producible end-to-end)

## Key Deliverables

- `backend/modes/validation_mode.py` – `ValidationMode` with completeness + consistency
  checks
- `backend/core/orchestrator.py` updated – correction loop routing logic
- `backend/core/phase_transition.py` updated – `VALIDATION_PASSED` terminal state
- `frontend/src/components/ArtifactPane.tsx` updated – highlights validated / flagged
  fields
- `frontend/src/components/ChatPane.tsx` updated – renders validation summary messages
  clearly
- `backend/tests/test_validation_mode.py` – validation pass/fail and correction-loop tests
- ADR resolving OP-20 committed to `agent-docs/decisions/`

## Stories

_To be defined before this epic begins._
