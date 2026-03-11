# Epic 00: Bootstrap Shell

## Summary
Establish the runnable application skeleton for the prototype: backend, frontend, shared development conventions, and a minimal UI shell that proves the chosen architecture is wired correctly.

## Why this exists
This epic creates the first executable baseline for the project. It turns the repository from documentation-only into a running system that later epics can extend without reworking the foundation.

## Target outcome
- FastAPI backend boots with basic configuration and health endpoints.
- React + Vite frontend boots and can talk to the backend.
- The initial UI shell reflects the intended layout direction from the HLA.
- Local development and test commands are documented and repeatable.

## Visible user-testable increment
A user can start the system locally, open the application in the browser, see the prototype shell, and verify that frontend and backend connectivity works.

## HLA alignment
- Maps to the HLA project structure and frontend-backend separation.
- Creates the baseline needed before implementing persistence, orchestration, or modes.

## Story placeholder
- Story breakdown is defined in `stories/README.md`.
