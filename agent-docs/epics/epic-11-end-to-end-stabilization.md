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

- `backend/api/router.py` – `GET /api/projects/{id}/export` returns JSON artifact bundle (HLA Section 6: `api/router.py`)
- `backend/artifacts/renderer.py` – Markdown renderer for all three artifacts (HLA Section 6: `artifacts/renderer.py`)
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

---

### Story 11-01 — Markdown Renderer (`backend/artifacts/renderer.py`)

**User story:**
As a developer
I want a `ArtifaktRenderer` class in `backend/artifacts/renderer.py`
So that all three artifacts can be serialised to human-readable Markdown for download and export.

**Note on path:** Epic doc listed `backend/core/export.py` but HLA Section 6 already defines `backend/artifacts/renderer.py` ("JSON → Markdown (für Download, OP-19)"). Using the HLA-canonical path. No ADR required — Epic doc was misspecifying an already-defined HLA path.

**Acceptance Criteria:**

1. `backend/artifacts/renderer.py` exists and contains class `ArtifaktRenderer`.
2. `ArtifaktRenderer.render_exploration(artifact: ExplorationArtifact) -> str` produces a Markdown string containing:
   - `# Explorationsartefakt` heading
   - `Version: N` line
   - One `## <titel>` section per slot with `inhalt`, `completeness_status`, and `slot_id`
   - Empty slots rendered as `_(leer)_`
3. `ArtifaktRenderer.render_structure(artifact: StructureArtifact) -> str` produces a Markdown string containing:
   - `# Strukturartefakt` heading
   - `Version: N` line
   - `## Prozesszusammenfassung` section with content
   - One `### <reihenfolge>. <titel>` section per `Strukturschritt` with all fields: `schritt_id`, `typ`, `beschreibung`, `reihenfolge`, `nachfolger`, `completeness_status`, `algorithmus_status`; and conditionally: `bedingung` (if set, only for `typ=entscheidung`), `ausnahme_beschreibung` (if set, only for `typ=ausnahme`), `algorithmus_ref` (list of referenced algorithm section IDs), `spannungsfeld` (if set)
4. `ArtifaktRenderer.render_algorithm(artifact: AlgorithmArtifact) -> str` produces a Markdown string containing:
   - `# Algorithmusartefakt` heading
   - `Version: N` line
   - `## Prozesszusammenfassung` section with content
   - One `### <titel>` section per `Algorithmusabschnitt` with: `abschnitt_id`, `struktur_ref`, `completeness_status`, `status`
   - Within each section, one `#### <aktion_id>` sub-section per `EmmaAktion` with all fields: `aktionstyp`, `parameter` (dict), `nachfolger` (list of successor IDs), `emma_kompatibel`, and `kompatibilitaets_hinweis` (if set)
5. `ArtifaktRenderer.render_all(exploration, structure, algorithm) -> str` concatenates all three sections with `---` separator.
6. `backend/artifacts/renderer.py` does not exceed 200 lines.
7. **Tests** in `backend/tests/test_export.py`:
   - `test_render_exploration_with_slots`: renders artifact with 2 filled slots; asserts slot titles, inhalt, and completeness_status appear in output; asserts `# Explorationsartefakt` and version line appear; breaks if renderer omits a slot title.
   - `test_render_exploration_empty_slots`: slot with `inhalt=""` renders as `_(leer)_`.
   - `test_render_structure_with_steps`: renders artifact with `prozesszusammenfassung` and 2 `Strukturschritt`; asserts step titles and `schritt_id` appear; asserts `spannungsfeld` section absent when `None`.
   - `test_render_structure_spannungsfeld`: renders step with `spannungsfeld` set; asserts the spannungsfeld text appears in output.
   - `test_render_algorithm_with_actions`: renders artifact with 1 `Algorithmusabschnitt` containing 2 `EmmaAktion`; asserts `aktionstyp` values appear; asserts `emma_kompatibel` state is indicated.
   - `test_render_all_contains_all_sections`: calls `render_all`; asserts all three `# ...artefakt` headings appear; asserts `---` separator appears.

**Definition of Done:**

- [ ] `backend/artifacts/renderer.py` exists
- [ ] `ArtifaktRenderer` class with `render_exploration`, `render_structure`, `render_algorithm`, `render_all` methods
- [ ] `backend/tests/test_export.py` exists with all 6 tests
- [ ] All 6 test assertions are falsifiable (break if renderer omits required fields)
- [ ] `ruff check .` passes (from `backend/`)
- [ ] `ruff format --check .` passes
- [ ] `python -m mypy . --explicit-package-bases` passes
- [ ] `pytest --tb=short -q` passes, 0 failures

---

### Story 11-02 — Export REST Endpoint (`GET /api/projects/{id}/export`)

**User story:**
As a frontend developer
I want a `GET /api/projects/{id}/export` endpoint
So that I can retrieve both the JSON artifact bundle and the Markdown rendering in a single request for the export feature.

**Acceptance Criteria:**

1. New Pydantic model `ExportResponse` in `backend/api/schemas.py`:
   - `exploration: dict` — raw JSON of `ExplorationArtifact`
   - `struktur: dict` — raw JSON of `StructureArtifact`
   - `algorithmus: dict` — raw JSON of `AlgorithmArtifact`
   - `markdown: str` — full Markdown string from `ArtifaktRenderer.render_all()`
2. New endpoint `GET /api/projects/{projekt_id}/export` in `backend/api/router.py`:
   - Returns `ExportResponse`
   - Returns HTTP 404 with `ErrorResponse` if project not found
   - Uses `ArtifaktRenderer.render_all()` from `backend/artifacts/renderer.py`
   - FR-B-07: downloadable at any phase, regardless of completeness state
3. After adding the endpoint, the OpenAPI snapshot is updated:
   - `curl http://localhost:8000/openapi.json > api-contract/openapi.json`
   - `cd frontend && npm run generate-api:file`
   - Both `api-contract/openapi.json` and `frontend/src/generated/api.d.ts` committed together
4. **Tests** added to `backend/tests/test_api.py`:
   - `test_export_returns_json_and_markdown`: creates project, calls `GET /api/projects/{id}/export`, asserts response has `exploration`, `struktur`, `algorithmus`, `markdown` keys; asserts `markdown` contains `# Explorationsartefakt`; breaks if `ExportResponse` schema changes.
   - `test_export_404_for_unknown_project`: `GET /api/projects/nonexistent/export` → 404.
   - `test_export_includes_markdown_for_all_phases`: creates project with some slots filled, asserts all three artifact section headings appear in `markdown`.

**Definition of Done:**

- [ ] `ExportResponse` model in `backend/api/schemas.py` with `exploration`, `struktur`, `algorithmus`, `markdown` fields
- [ ] `GET /api/projects/{projekt_id}/export` endpoint in `backend/api/router.py`
- [ ] `ArtifaktRenderer.render_all()` called inside the endpoint handler
- [ ] HTTP 404 returned for unknown project
- [ ] 3 new tests in `backend/tests/test_api.py`
- [ ] `api-contract/openapi.json` regenerated and committed
- [ ] `frontend/src/generated/api.d.ts` regenerated and committed in same commit
- [ ] `ExportResponse` visible in `/openapi.json` with all 4 fields typed (no `{}`)
- [ ] `ruff check .` passes
- [ ] `ruff format --check .` passes
- [ ] `python -m mypy . --explicit-package-bases` passes
- [ ] `pytest --tb=short -q` passes, 0 failures

---

### Story 11-03 — Frontend ExportButton

**User story:**
As a non-technical user
I want an "Exportieren" button in the UI
So that I can download my finished artifacts as `artifacts.json` and `artifacts.md` without developer assistance.

**Acceptance Criteria:**

1. `frontend/src/components/ExportButton.tsx` exists.
2. `ExportButton` renders a button labelled `Exportieren` (German, FR-A-08).
3. On click, the component calls `GET /api/projects/{id}/export` using the `openapi-fetch` client from `frontend/src/api/client.ts`.
4. Uses the generated type `components["schemas"]["ExportResponse"]` from `frontend/src/generated/api.d.ts` — no hand-written response type.
5. On success, two file downloads are triggered:
   - `artifacts.json`: a JSON blob containing `{ exploration, struktur, algorithmus }` from the response
   - `artifacts.md`: a text blob containing the `markdown` string from the response
6. If the request fails, a German error message is displayed in the button area (e.g. "Export fehlgeschlagen").
7. During download, the button shows a loading state (disabled + label `Exportiere...`).
8. `ExportButton` is integrated into the active project view in `App.tsx` or `ArtifactPane.tsx` — visible when a project is active.
9. `npm run lint` passes.
10. `npm run typecheck` passes — no implicit-any from API types.
11. `npm run build` produces a successful production build with no TypeScript errors.

**Definition of Done:**

- [ ] `frontend/src/components/ExportButton.tsx` exists
- [ ] Button labelled `Exportieren` in German
- [ ] Uses `openapi-fetch` client (no hand-written fetch)
- [ ] Uses generated `ExportResponse` type — not hand-written
- [ ] Downloads `artifacts.json` on success
- [ ] Downloads `artifacts.md` on success
- [ ] Loading state while request in progress
- [ ] German error message on failure
- [ ] `ExportButton` visible in active project view
- [ ] `npm run lint` passes
- [ ] `npm run format:check` passes
- [ ] `npm run typecheck` passes
- [ ] `npm run build` passes with 0 errors

---

### Story 11-04 — Open Points Resolution

**User story:**
As a developer
I want all remaining open points formally resolved or deferred with ADRs
So that the prototype is fully documented with no dangling design questions.

**Acceptance Criteria:**

For each open point, either mark as `resolved` in `agent-docs/open-points/open-points.md` with a resolution note, or write an ADR (`agent-docs/decisions/ADR-00N-*.md`) documenting the deferral decision. Every open point must reach a final status of `resolved` or `deferred`. The following open points must be addressed:

| OP | Resolution required |
|---|---|
| OP-03 | Version history in UI — ArtifactPane tab already shows artifact content; mark resolved or add minimal version-count display if absent |
| OP-04 | Max version count — Prototype: unlimited; mark resolved with note |
| OP-05 | Token thresholds — Placeholder values in `config.py`; calibrate values or document as deferred-post-prototype |
| OP-06 | nearing_completion criteria — Each mode has implemented criteria (Epics 8–9); document the final criteria per mode and mark resolved |
| OP-07 | Control flags complete list — All flags defined through Epics 7–10; document the final flag set and mark resolved |
| OP-11 | Dialog history scope — Full history in SQLite (FR-E-07); mark resolved |
| OP-12 | Project list in UI — Implemented in `App.tsx`; mark resolved |
| OP-14 | LLM log format — Defined in open-points as `logs` table; implement minimal `logs` table DDL in `backend/persistence/schema.sql` and a write call in the LLM client, or write ADR deferring to post-prototype |
| OP-17 | Event log format — "Prototype: free-text upload, no structured parsing"; mark resolved |

For OP-14: if implementing the `logs` table, it requires:
- `schema.sql` DDL: `CREATE TABLE IF NOT EXISTS llm_logs (id INTEGER PRIMARY KEY, timestamp TEXT, modus TEXT, turn_id TEXT, projekt_id TEXT, input_tokens INTEGER, output_tokens INTEGER)`
- A write call from `backend/llm/anthropic_client.py`, `backend/llm/openai_client.py`, and `backend/llm/ollama_client.py` after each LLM completion
- Tests verifying the write

**Definition of Done:**

- [ ] `agent-docs/open-points/open-points.md` updated — every open point has `resolved` or `deferred` status
- [ ] OP-03 resolved or deferred with note
- [ ] OP-04 marked resolved
- [ ] OP-05 resolved or deferred
- [ ] OP-06 documented and marked resolved
- [ ] OP-07 documented and marked resolved
- [ ] OP-11 marked resolved
- [ ] OP-12 marked resolved
- [ ] OP-14 resolved (implementation) or deferred (ADR written with `accepted` status)
- [ ] OP-17 marked resolved
- [ ] All new ADRs have status `accepted`
- [ ] `ruff check .` passes (if any Python changed)
- [ ] `python -m mypy . --explicit-package-bases` passes (if any Python changed)
- [ ] `pytest --tb=short -q` passes, 0 failures (if any Python changed)

---

### Story 11-05 — UI Polish, Production Build & README

**User story:**
As a non-technical user
I want the prototype UI to be polished and readable in German
So that I can follow the entire process independently without developer guidance.

**Acceptance Criteria:**

**UI Polish (FR-A-08, FR-F-01, FR-F-03):**
1. All visible labels, buttons, status messages, headings, placeholder text, and error messages in the frontend are in German. Any English UI text (excluding code identifiers and generated content) must be replaced.
2. The `PhaseHeader` shows the active phase name in German (`Exploration`, `Strukturierung`, `Spezifikation`, `Validierung`, `Abgeschlossen`).
3. The artifact tabs in `ArtifactPane` are labelled in German (`Exploration`, `Struktur`, `Algorithmus` — already German; verify no regressions).
4. The `DebugPanel` heading is in German; field labels readable.
5. Artifact slot content is displayed with readable line breaks (multi-line `inhalt` renders across lines, not as a single overflowing string).
6. When `projektstatus === "abgeschlossen"`, the UI shows a visible "Projekt abgeschlossen" indicator (badge or banner) in the phase header area.
7. The layout is readable at 1280×800 viewport — chat and artifact panes not overflowing without scrollbars.

**Production build:**
8. `npm run build` completes successfully (exit 0) with the final `frontend/src/generated/api.d.ts`.
9. No TypeScript errors and no implicit-any warnings from API types.

**README:**
10. `README.md` (root) contains a "Schnellstart" (Quick Start) section with the exact commands to install, configure, and run both backend and frontend.
11. `README.md` contains a "Benutzerhandbuch" (User Guide) section describing the five steps: Projekt anlegen → Exploration → Strukturierung → Spezifikation → Validierung → Exportieren.
12. `README.md` references `.env.example` for configuration.

**Definition of Done:**

- [ ] All visible UI strings in German (no English labels in rendered output)
- [ ] Phase names in German in `PhaseHeader`
- [ ] "Projekt abgeschlossen" indicator visible when `projektstatus === "abgeschlossen"`
- [ ] Multi-line slot content renders without horizontal overflow
- [ ] `npm run lint` passes
- [ ] `npm run format:check` passes
- [ ] `npm run typecheck` passes
- [ ] `npm run build` passes (exit 0) — production build succeeds
- [ ] `README.md` has "Schnellstart" section with install + run commands
- [ ] `README.md` has "Benutzerhandbuch" section with 5-step walkthrough
- [ ] `README.md` references `backend/.env.example`
