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
- `frontend/src/hooks/useWebSocket.ts` – WebSocket connection + message handling
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

_To be defined before this epic begins._
