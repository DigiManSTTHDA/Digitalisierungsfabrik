# Story 00-05: Connectivity Check

## Summary
Connect the frontend shell to the backend with a simple visible status check so the epic ends with a proven frontend-backend integration point.

## Value
This closes Epic 00 with a user-testable signal that the architecture boundary works in practice, not just in isolated runtimes.

## Scope
- Add a minimal frontend API client path to the backend.
- Surface backend connectivity status in the UI.
- Handle the success and failure states in a simple, visible way.
- Add coverage for the integration contract at the boundary where practical.

## Acceptance criteria
- The frontend can call the backend successfully in local development.
- The UI shows a clear connectivity state derived from the backend response.
- Connection failure is visible and does not crash the shell.
- The epic increment can be demonstrated without hidden setup beyond documented local startup.

## Test notes
- Prefer TDD for the API client behavior and UI state transitions if practical.
- Cover the happy path at minimum, and ideally a failure path for unavailable backend state.

## Dependencies
- Depends on `00-02-backend-bootstrap.md`.
- Depends on `00-04-shell-layout.md`.

## User validation
- A user can start frontend and backend, open the app, and see a visible “connected” state that proves the shell talks to the backend.
