# Epic 06 – React Frontend (Chat + Artifact Pane)

## Summary

Build the React SPA that gives users a browser-based interface to the system. The UI
consists of three panels: the **Chat Pane** (conversation with the AI), the **Artifact Pane**
(live view of the three artifacts as they grow), and the **Debug Panel** (Working Memory
snapshot, visible during development). The frontend communicates with the backend exclusively
via the REST API and the WebSocket.

This epic corresponds to **Implementation Step 6** in `AGENTS.md` / `hla_architecture.md`.

## Goal

A running browser UI where a user can open the app, start a new project, type a message
in the chat pane, see the AI reply, and watch the Exploration Artifact update in real time
in the artifact pane.

## Testable Increment

- `cd frontend && npm run dev` → Vite dev server starts on port 5173
- User opens `http://localhost:5173` in a browser
- User can:
  1. Create a new project
  2. Type a process description in the chat input
  3. Receive an AI response in the chat pane
  4. See the Exploration Artifact populate in the artifact pane
  5. Open the Debug Panel and see the current Working Memory state
- No manual API calls required – everything driven through the UI

## Dependencies

- Epic 05 (backend API must be running and complete)

## Key Deliverables

- `frontend/src/App.tsx` – root component with three-panel layout
- `frontend/src/components/ChatPane.tsx` – message list + input box
- `frontend/src/components/ArtifactPane.tsx` – tabbed artifact viewer
- `frontend/src/components/DebugPanel.tsx` – collapsible Working Memory view
- `frontend/src/api/websocket.ts` – WebSocket client + event handling (HLA Section 6 path)
- Basic CSS / layout (functional; visual polish comes in Epic 11)

### API Client & Types (binding — see ADR-001)

**`frontend/src/types/api.ts` does not exist.** All API types come from the generated file.

| File | Description | Editable? |
|---|---|---|
| `frontend/src/generated/api.d.ts` | Auto-generated TypeScript types from `api-contract/openapi.json` | **Never** |
| `frontend/src/api/client.ts` | `openapi-fetch` client, typed with generated types | Yes |

**`frontend/src/api/client.ts`** must initialise the client as follows:

```typescript
import createClient from "openapi-fetch";
import type { paths } from "../generated/api";

export const apiClient = createClient<paths>({
  baseUrl: "http://localhost:8000",
});
```

All REST calls in components and hooks go through `apiClient`. No component may call
`fetch()` directly for REST endpoints.

**`frontend/src/types/`** may only contain app-internal types that are not part of the
API contract (e.g. local UI state shapes). It must not shadow or re-define API types.

**Before starting frontend development**, confirm that `frontend/src/generated/api.d.ts`
exists and `tsc --noEmit` passes (these are committed at the end of Epic 05).

## Stories

> **Path Note:** HLA Section 6 defines `frontend/src/api/websocket.ts` for WebSocket
> client logic. The Key Deliverables listed `hooks/useWebSocket.ts` but `hooks/` is not
> an HLA-defined directory. WebSocket logic goes in `api/websocket.ts` per HLA. React
> hook wrappers live in `store/session.ts` or inline in components.

> **State Note:** HLA Section 6 defines `frontend/src/store/session.ts` for React state.
> This epic uses React Context (built-in, no new dependency) for session state management.

> **Test Note:** AGENTS.md says "The frontend is excluded from strict TDD but should have
> smoke tests." This epic focuses on functional UI; visual polish comes in Epic 11.

### Story 06-01: Session Store + Project Selection UI

**User Story:**
As a user,
I want to see a list of my projects when I open the app and create a new project,
so that I can start or continue a process elicitation session.

**FR/NFR Traceability:** FR-G-01 (Projektanlage), FR-G-02 (Projektliste/Auswahl),
SDD 7.2.1 (Projektmetadaten), SDD 2.2 (Benutzeroberfläche).

**Acceptance Criteria:**

1. `frontend/src/store/session.ts` exists (HLA Section 6 path).
2. Session store provides:
   - `projects: ProjectResponse[]` — list of all projects
   - `activeProjectId: string | null` — currently selected project
   - `loadProjects()` — fetches project list via `apiClient.GET("/api/projects")`
   - `createProject(name, beschreibung)` — POST via `apiClient`, adds to list
   - `selectProject(id)` — sets active project
3. All REST calls go through `apiClient` from `api/client.ts` (ADR-001).
4. `frontend/src/App.tsx` updated to show project selection when no project is active:
   - Lists existing projects with name, phase, status
   - "Neues Projekt" button with name input
   - Clicking a project selects it and transitions to the chat view
5. FR-G-01: Project creation captures name (required) and beschreibung (optional).
6. FR-G-02: Project list shows Projektname, Beschreibung, aktive Phase, letztes
   Änderungsdatum, Projektstatus.
7. FR-A-08: All UI labels in German (e.g. "Neues Projekt", "Projektname", "Beschreibung").

**Definition of Done:**

- [x] `frontend/src/store/session.ts` exists
- [x] Session store exports project list, active project, load/create/select functions
- [x] All REST calls use `apiClient` (no direct `fetch`)
- [x] Project list view renders in `App.tsx` when no project active
- [x] "Neues Projekt" button creates project via API
- [x] Clicking a project selects it
- [x] `npm run lint` passes (exit 0)
- [x] `npm run format:check` passes (exit 0)
- [x] `npm run typecheck` passes (exit 0)

---

### Story 06-02: App Layout + PhaseHeader

**User Story:**
As a user,
I want to see the system layout with chat on the left, artifacts on the right, and
phase information at the top,
so that I always know where I am in the process and can see all relevant information.

**FR/NFR Traceability:** FR-F-01 (Phasen- und Fortschrittsanzeige), FR-F-03
(Chat/Artefaktbereich getrennt), SDD 2.2 (UI-Elemente), SDD 2.5 (Phasenanzeige),
HLA 3.1 (Layout).

**Acceptance Criteria:**

1. `frontend/src/App.tsx` implements the HLA 3.1 split-pane layout:
   - Top: PhaseHeader bar
   - Left: ChatPane area
   - Right: ArtifactPane area
   - Bottom: DebugPanel area (collapsible)
2. `frontend/src/components/PhaseHeader.tsx` exists (HLA Section 6 path).
3. PhaseHeader displays:
   - Current phase name (e.g. "Exploration")
   - Phasenstatus badge (in_progress / nearing_completion / phase_complete)
   - Slot counter: "X von Y Slots befüllt" (FR-F-01, SDD 2.5)
   - Panik-Button (sends `{"type": "panic"}` via WebSocket; placeholder message
     until Epic 07 Moderator)
   - Download-Button (calls `GET /api/projects/{id}/download`, triggers JSON file
     download; SDD 2.2; Markdown download deferred until renderer exists)
   - Back-to-project-list button
5. FR-A-08: All UI labels in German ("Exploration", "Panik", "Download", etc.).
6. FR-F-03: Chat and artifact areas are visually separated (distinct panels).
7. Layout is responsive enough to work at 1280px width minimum.
8. CSS is in a single `frontend/src/App.css` or inline styles (no CSS framework
   dependency — keep it simple for prototype).

**Definition of Done:**

- [x] `frontend/src/components/PhaseHeader.tsx` exists
- [x] PhaseHeader shows phase name, phasenstatus, slot counter
- [x] Panik-Button visible in PhaseHeader
- [x] Download-Button triggers JSON file download (SDD 2.2)
- [x] Back button returns to project list
- [x] UI labels in German (FR-A-08)
- [x] `App.tsx` implements split-pane layout (chat left, artifacts right)
- [x] Chat and artifact areas are visually separated (FR-F-03)
- [x] `npm run lint` passes (exit 0)
- [x] `npm run format:check` passes (exit 0)
- [x] `npm run typecheck` passes (exit 0)

---

### Story 06-03: WebSocket Client + Event Handling

**User Story:**
As a developer,
I want a WebSocket client that connects to the backend, sends turn/panic messages,
and dispatches received events to the session store,
so that the UI can react to real-time updates from the Orchestrator.

**FR/NFR Traceability:** FR-A-01 (Dialogischer Interviewprozess), FR-D-03
(Panik-Button-Eskalation), FR-E-04 (Fehlerbehandlung), HLA 3.1 (WebSocket-Events),
HLA 3.2 (WebSocket Messages).

**Acceptance Criteria:**

1. `frontend/src/api/websocket.ts` exists (HLA Section 6 path).
2. Exports functions:
   - `connectWebSocket(projectId)` — opens `ws://host/ws/session/{projectId}`
   - `sendTurn(text, datei?)` — sends `{"type": "turn", "text": ..., "datei": ...}`
   - `sendPanic()` — sends `{"type": "panic"}`
   - `disconnectWebSocket()` — closes the connection
3. Receives and parses all 6 event types from HLA 3.1:
   - `chat_token` → appended to streaming message buffer (future use)
   - `chat_done` → adds assistant message to chat history
   - `artifact_update` → updates artifact in session store
   - `progress_update` → updates phase/slot counters in session store
   - `debug_update` → updates working memory in session store
   - `error` → displays error message to user
4. Session store (`store/session.ts`) extended with:
   - `chatMessages: Array<{role: "user" | "assistant", text: string}>`
   - `artifacts: {exploration: object, struktur: object, algorithmus: object}`
   - `progress: {phasenstatus: string, befuellte_slots: number, bekannte_slots: number}`
   - `debugState: {working_memory: object, flags: string[]}`
   - `error: string | null`
   - `isProcessing: boolean` (true while waiting for turn response)
5. Connection automatically established when a project is selected.
6. Connection closed when returning to project list.

**Definition of Done:**

- [x] `frontend/src/api/websocket.ts` exists
- [x] `connectWebSocket`, `sendTurn`, `sendPanic`, `disconnectWebSocket` exported
- [x] All 6 event types handled (chat_done, artifact_update, progress_update,
      debug_update, error, chat_token)
- [x] Session store extended with chat, artifacts, progress, debug, error state
- [x] `isProcessing` flag set during turn processing
- [x] WebSocket connects on project select, disconnects on back
- [x] `npm run lint` passes (exit 0)
- [x] `npm run format:check` passes (exit 0)
- [x] `npm run typecheck` passes (exit 0)

---

### Story 06-04: ChatPane Component

**User Story:**
As a user,
I want to type messages in the chat pane and see the AI's responses appear in
real time,
so that I can have a natural conversation about my business process.

**FR/NFR Traceability:** FR-A-01 (Dialogischer Interviewprozess), FR-A-02
(Anleitungskompetenz), FR-A-08 (Systemsprache Deutsch), FR-F-03 (Chat/Artefakt
getrennt), FR-F-04 (Eingabetypen — text only for now), SDD 2.1 (Kerninteraktion).

**Acceptance Criteria:**

1. `frontend/src/components/ChatPane.tsx` exists (HLA Section 6 path).
2. Displays a scrollable list of chat messages from `session.chatMessages`.
3. User messages styled differently from assistant messages (e.g. alignment/color).
4. Text input field at the bottom with a send button.
5. Pressing Enter or clicking Send:
   - Adds the user message to `chatMessages` immediately
   - Calls `sendTurn(text)` via WebSocket
   - Clears the input field
   - Sets `isProcessing = true` (disables input until response)
6. When `chat_done` event arrives:
   - Assistant message appears in the chat list
   - `isProcessing = false` (re-enables input)
7. When `error` event arrives:
   - Error message displayed in the chat (styled as error)
   - `isProcessing = false`
8. FR-F-03: No artifact data shown in the chat pane.
9. FR-A-08: UI labels in German ("Nachricht eingeben...", "Senden").
10. Auto-scrolls to the bottom when new messages arrive.

**Definition of Done:**

- [x] `frontend/src/components/ChatPane.tsx` exists
- [x] Message list renders user and assistant messages
- [x] Text input with send button
- [x] Enter key sends message
- [x] Input disabled while `isProcessing`
- [x] Error events displayed in chat
- [x] Auto-scroll on new messages
- [x] UI labels in German
- [x] `npm run lint` passes (exit 0)
- [x] `npm run format:check` passes (exit 0)
- [x] `npm run typecheck` passes (exit 0)

---

### Story 06-05: ArtifactPane + ArtifactTab

**User Story:**
As a user,
I want to see the three process artifacts in a tabbed view that updates in real time,
so that I can observe the exploration artifact being populated as I describe my process.

**FR/NFR Traceability:** FR-B-06 (Artefaktsichtbarkeit), FR-F-03 (Chat/Artefakt
getrennt), FR-F-05 (Visuelle Markierung invalidierter Slots), SDD 2.1
(Artefaktbereich), HLA 3.1 (ArtifactPane, ArtifactTab).

**Acceptance Criteria:**

1. `frontend/src/components/ArtifactPane.tsx` exists (HLA Section 6 path).
2. `frontend/src/components/ArtifactTab.tsx` exists (HLA Section 6 path).
3. ArtifactPane renders three tabs: "Exploration", "Struktur", "Algorithmus".
4. Active tab shows the corresponding artifact via ArtifactTab.
5. ArtifactTab renders the artifact JSON as a structured view:
   - For ExplorationArtifact: list each slot with `bezeichnung`, `inhalt`,
     `completeness_status` badge
   - Empty slots shown with "(leer)" placeholder
   - FR-F-05: Slots with status `invalidiert` have a visual warning marker
6. Artifact data comes from `session.artifacts` (updated by `artifact_update` events).
7. FR-B-06: Artifacts update without user action when `artifact_update` events arrive.
8. SDD 2.1: Artifacts not active in the current phase shown as empty but visible.
9. FR-A-08: Tab labels and status badges in German ("Exploration", "Struktur",
   "Algorithmus", "leer", "teilweise", "vollständig", "invalidiert").

**Definition of Done:**

- [x] `frontend/src/components/ArtifactPane.tsx` exists
- [x] `frontend/src/components/ArtifactTab.tsx` exists
- [x] Three tabs rendered: Exploration, Struktur, Algorithmus
- [x] Active tab shows artifact slots with bezeichnung, inhalt, status
- [x] Empty slots show "(leer)" placeholder
- [x] Invalidated slots visually marked (FR-F-05)
- [x] Artifacts update in real time from WebSocket events
- [x] `npm run lint` passes (exit 0)
- [x] `npm run format:check` passes (exit 0)
- [x] `npm run typecheck` passes (exit 0)

---

### Story 06-06: DebugPanel

**User Story:**
As a developer,
I want a collapsible debug panel showing the Working Memory, active mode, flags,
and progress metrics,
so that I can inspect the system's internal state during development.

**FR/NFR Traceability:** FR-F-02 (Debug-Modus), SDD 2.3 (Debug-Bereich).

**Acceptance Criteria:**

1. `frontend/src/components/DebugPanel.tsx` exists (HLA Section 6 path).
2. Panel is collapsible (toggle button to show/hide).
3. FR-F-02: Displays when expanded:
   - Aktiver kognitiver Modus
   - Gesetzte Steuerungsflags
   - Fortschrittsmetriken (phasenstatus, befuellte/bekannte slots)
   - Working-Memory-Inhalte (formatted JSON)
4. Data comes from `session.debugState` (updated by `debug_update` events).
5. SDD 2.3: Debug panel is visible by default in the prototype.
6. Panel positioned at the bottom of the layout per HLA 3.1.

**Definition of Done:**

- [x] `frontend/src/components/DebugPanel.tsx` exists
- [x] Panel collapsible with toggle button
- [x] Shows aktiver Modus, Flags, Fortschritt, Working Memory
- [x] Data from `debug_update` WebSocket events
- [x] Visible by default
- [x] `npm run lint` passes (exit 0)
- [x] `npm run format:check` passes (exit 0)
- [x] `npm run typecheck` passes (exit 0)

---

### Implementation Order

Stories must be implemented in this order:

1. **06-01** (session store + project selection) — foundation for all other stories
2. **06-02** (app layout + phase header) — depends on 06-01 for active project state
3. **06-03** (WebSocket client) — depends on 06-01 for store, 06-02 for layout
4. **06-04** (ChatPane) — depends on 06-03 for WebSocket send/receive
5. **06-05** (ArtifactPane) — depends on 06-03 for artifact_update events
6. **06-06** (DebugPanel) — depends on 06-03 for debug_update events
