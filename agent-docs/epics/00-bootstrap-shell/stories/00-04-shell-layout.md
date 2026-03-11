# Story 00-04: Shell Layout

## Summary
Implement the first visible application shell based on the HLA layout direction: phase header, chat pane area, artifact pane area, and debug panel placeholder.

## Value
This story turns the frontend from a blank app into a recognizable prototype surface that stakeholders can react to early.

## Scope
- Create the root layout structure for the prototype shell.
- Add placeholder regions for phase header, chat pane, artifact pane, and debug panel.
- Make the shell usable on desktop and acceptable on smaller screens.
- Keep behavior static for now; this story is about layout and affordances.

## Acceptance criteria
- The UI visibly reflects the intended product structure from the HLA.
- The shell has clear labeled regions for the major future capabilities.
- The layout does not break at common desktop and mobile widths.
- The implementation remains lightweight and does not fake product logic.

## Test notes
- Use component or UI tests where layout labels and region presence can be asserted reliably.
- Manual responsive verification is acceptable in addition to automated coverage.

## Dependencies
- Depends on `00-03-frontend-bootstrap.md`.

## User validation
- A user can open the app and recognize the intended split between chat, artifacts, progress/header, and debug areas.
