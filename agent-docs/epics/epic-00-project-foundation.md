# Epic 00 – Project Foundation & Dev Setup

## Summary

Stand up the complete project skeleton so that every subsequent epic has a working,
reproducible environment to build on. This covers directory layout, dependency
management, linting/formatting config, and the minimal "hello world" endpoints that
prove the stack is wired together correctly.

No business logic is written in this epic. The goal is: any developer (or AI agent) can
clone the repo, run two commands, and have a green test suite and running dev server.

## Goal

A fully reproducible, documented local development environment for both backend
(FastAPI/Python) and frontend (React/TypeScript/Vite), with a passing test baseline and
a live health-check endpoint.

## Testable Increment

- `cd backend && pytest` → all tests pass (at minimum the health-check smoke test)
- `GET /health` returns `{"status": "ok"}`
- `cd frontend && npm run dev` → Vite dev server starts, browser shows placeholder page
- Both are runnable by following only the instructions in `README.md` / `AGENTS.md`

## Dependencies

None – this is the starting epic.

## Key Deliverables

- `backend/` directory with `main.py`, `requirements.txt`, `pyproject.toml` (or
  `setup.cfg`), `.env.example`
- `backend/tests/` directory with at least one smoke test
- `frontend/` directory with Vite + React + TypeScript scaffold
- `frontend/src/` placeholder `App.tsx`
- Root-level `.gitignore`, updated `README.md` with setup instructions
- CI-ready: tests and linter pass locally with documented commands

## Stories

_To be defined before this epic begins._
