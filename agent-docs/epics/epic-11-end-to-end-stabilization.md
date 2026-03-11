# Epic 11 – End-to-End Stabilization & Artifact Export

## Summary

Complete the full Exploration → Structuring → Specification → Validation → Export flow
without any manual intervention or test seeds. Fix edge-case bugs discovered in the
earlier epics, resolve remaining open points, and add the artifact export feature so
users can download their finished artifacts as JSON and Markdown files. Apply final UX
polish to make the interface usable by a non-technical business user.

This epic corresponds to **Implementation Step 11** in `AGENTS.md` / `hla_architecture.md`.

## Goal

A real, non-technical user can sit down at the running prototype, describe a business
process from scratch, follow the AI-guided dialogue through all four phases, and walk
away with downloadable JSON and Markdown artifacts – without any developer assistance.

## Testable Increment

- **Full end-to-end user test** (no seeds, no debug flags):
  1. Open `http://localhost:5173`
  2. Create a new project
  3. Describe a simple process (e.g. "Ich bearbeite eingehende Rechnungen per E-Mail")
  4. Follow all AI prompts through Exploration → Structuring → Specification → Validation
  5. Receive a validation-passed message
  6. Click "Exportieren" and download `artifacts.json` and `artifacts.md`
  7. Open both files – content is correct and complete
- `pytest backend/tests/` → full test suite passes with no skips
- `npm run build` in `frontend/` → production build succeeds with no warnings

## Dependencies

- Epic 10 (entire core pipeline must work before stabilisation)

## Key Deliverables

- `backend/api/routes.py` – `GET /api/projects/{id}/export` returns JSON artifact bundle
- `backend/core/export.py` – Markdown renderer for all three artifacts
- `frontend/src/components/ExportButton.tsx` – triggers download of JSON + Markdown
- All remaining open points resolved or explicitly deferred with ADRs
- UI polish: German labels throughout, readable artifact formatting, clear phase
  indicators in the chat pane, responsive layout
- `backend/tests/test_export.py` – export format and content tests
- Updated `README.md` with full usage walkthrough

## OpenAPI Contract Note

This epic adds the export endpoint:

- `GET /api/projects/{id}/export`

This must have an explicit Pydantic response schema in `backend/api/schemas.py`. Before
this epic closes, perform a **final contract audit**:

1. Verify `GET http://localhost:8000/openapi.json` shows all endpoints with fully typed
   request/response schemas (no `{}` or missing models).
2. Export the final snapshot: `curl http://localhost:8000/openapi.json > api-contract/openapi.json`
3. Regenerate frontend types: `cd frontend && npm run generate-api:file`
4. Commit both `api-contract/openapi.json` and `frontend/src/generated/api.d.ts`
5. Run `npm run build` — TypeScript compilation must succeed with zero errors and zero
   implicit-any warnings related to API types.

The `ExportButton.tsx` component that triggers the JSON + Markdown download must use the
generated type for the export response body.

**Definition of Done addition (Epic 11):** The production build (`npm run build`) passes
with the final `frontend/src/generated/api.d.ts` committed in the repository.

## Stories

_To be defined before this epic begins._
