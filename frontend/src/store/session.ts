/**
 * Session store — React Context for global session state (HLA Section 6).
 *
 * Manages project list, active project, chat messages, artifact state,
 * progress, debug state, and WebSocket lifecycle.
 *
 * All REST calls go through apiClient (ADR-001).
 */

import {
  createElement,
  createContext,
  useContext,
  useReducer,
  type Dispatch,
  type ReactNode,
} from "react";
import { apiClient } from "../api/client";
import type { components } from "../generated/api";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type ProjectResponse = components["schemas"]["ProjectResponse"];
type ValidationReportResponse =
  components["schemas"]["ValidationReportResponse"];

export interface ChatMessage {
  role: "user" | "assistant" | "error";
  text: string;
}

export interface SessionState {
  projects: ProjectResponse[];
  activeProjectId: string | null;
  activePhase: string;
  chatMessages: ChatMessage[];
  artifacts: {
    exploration: Record<string, unknown>;
    struktur: Record<string, unknown>;
    algorithmus: Record<string, unknown>;
  };
  progress: {
    phasenstatus: string;
    befuellte_slots: number;
    bekannte_slots: number;
  };
  debugState: {
    working_memory: Record<string, unknown>;
    flags: string[];
  };
  validationReport: ValidationReportResponse | null;
  error: string | null;
  isProcessing: boolean;
  initProgress: { status: string; message: string } | null;
}

// ---------------------------------------------------------------------------
// Actions
// ---------------------------------------------------------------------------

export type SessionAction =
  | { type: "SET_PROJECTS"; projects: ProjectResponse[] }
  | { type: "ADD_PROJECT"; project: ProjectResponse }
  | { type: "SELECT_PROJECT"; id: string; phase: string }
  | { type: "DESELECT_PROJECT" }
  | { type: "ADD_CHAT_MESSAGE"; message: ChatMessage }
  | { type: "SET_PROCESSING"; value: boolean }
  | {
      type: "UPDATE_ARTIFACT";
      typ: string;
      artefakt: Record<string, unknown>;
    }
  | {
      type: "UPDATE_PROGRESS";
      phasenstatus: string;
      befuellte_slots: number;
      bekannte_slots: number;
    }
  | {
      type: "UPDATE_DEBUG";
      working_memory: Record<string, unknown>;
      flags: string[];
    }
  | { type: "SET_VALIDATION_REPORT"; report: ValidationReportResponse | null }
  | { type: "SET_ERROR"; error: string | null }
  | { type: "SET_INIT_PROGRESS"; status: string; message: string };

// ---------------------------------------------------------------------------
// Initial state
// ---------------------------------------------------------------------------

export const initialState: SessionState = {
  projects: [],
  activeProjectId: null,
  activePhase: "exploration",
  chatMessages: [],
  artifacts: {
    exploration: {},
    struktur: {},
    algorithmus: {},
  },
  progress: {
    phasenstatus: "in_progress",
    befuellte_slots: 0,
    bekannte_slots: 0,
  },
  debugState: {
    working_memory: {},
    flags: [],
  },
  validationReport: null,
  error: null,
  isProcessing: false,
  initProgress: null,
};

// ---------------------------------------------------------------------------
// Reducer
// ---------------------------------------------------------------------------

export function sessionReducer(
  state: SessionState,
  action: SessionAction,
): SessionState {
  switch (action.type) {
    case "SET_PROJECTS":
      return { ...state, projects: action.projects };
    case "ADD_PROJECT":
      return { ...state, projects: [action.project, ...state.projects] };
    case "SELECT_PROJECT":
      return {
        ...state,
        activeProjectId: action.id,
        activePhase: action.phase,
        chatMessages: [],
        error: null,
      };
    case "DESELECT_PROJECT":
      return { ...initialState, projects: state.projects };
    case "ADD_CHAT_MESSAGE":
      return {
        ...state,
        chatMessages: [...state.chatMessages, action.message],
      };
    case "SET_PROCESSING":
      return { ...state, isProcessing: action.value };
    case "UPDATE_ARTIFACT": {
      const key = action.typ as keyof SessionState["artifacts"];
      if (!(key in state.artifacts)) return state;
      return {
        ...state,
        artifacts: { ...state.artifacts, [key]: action.artefakt },
      };
    }
    case "UPDATE_PROGRESS":
      return {
        ...state,
        progress: {
          phasenstatus: action.phasenstatus,
          befuellte_slots: action.befuellte_slots,
          bekannte_slots: action.bekannte_slots,
        },
      };
    case "UPDATE_DEBUG":
      return {
        ...state,
        debugState: {
          working_memory: action.working_memory,
          flags: action.flags,
        },
      };
    case "SET_VALIDATION_REPORT":
      return { ...state, validationReport: action.report };
    case "SET_ERROR":
      return { ...state, error: action.error };
    case "SET_INIT_PROGRESS":
      return {
        ...state,
        initProgress:
          action.status === "completed"
            ? null
            : { status: action.status, message: action.message },
      };
    default:
      return state;
  }
}

// ---------------------------------------------------------------------------
// Context
// ---------------------------------------------------------------------------

export const SessionContext = createContext<SessionState>(initialState);
export const SessionDispatchContext = createContext<Dispatch<SessionAction>>(
  () => {},
);

export function useSession(): SessionState {
  return useContext(SessionContext);
}

export function useSessionDispatch(): Dispatch<SessionAction> {
  return useContext(SessionDispatchContext);
}

// ---------------------------------------------------------------------------
// API helpers (all go through apiClient per ADR-001)
// ---------------------------------------------------------------------------

export async function loadProjects(
  dispatch: Dispatch<SessionAction>,
): Promise<void> {
  const { data } = await apiClient.GET("/api/projects");
  if (data) {
    dispatch({ type: "SET_PROJECTS", projects: data.projects });
  }
}

export async function createProject(
  dispatch: Dispatch<SessionAction>,
  name: string,
  beschreibung: string,
): Promise<void> {
  const { data, error } = await apiClient.POST("/api/projects", {
    body: { name, beschreibung },
  });
  if (data) {
    dispatch({ type: "ADD_PROJECT", project: data });
  } else if (error) {
    dispatch({
      type: "SET_ERROR",
      error: "Projekt konnte nicht erstellt werden",
    });
  }
}

export async function loadProjectState(
  dispatch: Dispatch<SessionAction>,
  projektId: string,
): Promise<void> {
  const { data } = await apiClient.GET("/api/projects/{projekt_id}/artifacts", {
    params: { path: { projekt_id: projektId } },
  });
  if (data) {
    dispatch({
      type: "UPDATE_ARTIFACT",
      typ: "exploration",
      artefakt: data.exploration as Record<string, unknown>,
    });
    dispatch({
      type: "UPDATE_ARTIFACT",
      typ: "struktur",
      artefakt: data.struktur as Record<string, unknown>,
    });
    dispatch({
      type: "UPDATE_ARTIFACT",
      typ: "algorithmus",
      artefakt: data.algorithmus as Record<string, unknown>,
    });
  }
}

export async function deleteProject(
  dispatch: Dispatch<SessionAction>,
  projektId: string,
): Promise<void> {
  const resp = await fetch(`/api/projects/${projektId}`, { method: "DELETE" });
  if (resp.ok) {
    await loadProjects(dispatch);
  } else {
    dispatch({
      type: "SET_ERROR",
      error: "Projekt konnte nicht gelöscht werden",
    });
  }
}

export async function deleteProjects(
  dispatch: Dispatch<SessionAction>,
  projektIds: string[],
): Promise<void> {
  const resp = await fetch("/api/projects/batch", {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ projekt_ids: projektIds }),
  });
  if (resp.ok) {
    await loadProjects(dispatch);
  } else {
    dispatch({
      type: "SET_ERROR",
      error: "Projekte konnten nicht gelöscht werden",
    });
  }
}

// ---------------------------------------------------------------------------
// Provider component
// ---------------------------------------------------------------------------

export function SessionProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(sessionReducer, initialState);
  return createElement(
    SessionContext.Provider,
    { value: state },
    createElement(
      SessionDispatchContext.Provider,
      { value: dispatch },
      children,
    ),
  );
}
