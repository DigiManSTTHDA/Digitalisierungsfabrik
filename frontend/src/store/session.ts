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

export interface ChatMessage {
  role: "user" | "assistant" | "error";
  text: string;
}

export interface SessionState {
  projects: ProjectResponse[];
  activeProjectId: string | null;
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
  error: string | null;
  isProcessing: boolean;
}

// ---------------------------------------------------------------------------
// Actions
// ---------------------------------------------------------------------------

export type SessionAction =
  | { type: "SET_PROJECTS"; projects: ProjectResponse[] }
  | { type: "ADD_PROJECT"; project: ProjectResponse }
  | { type: "SELECT_PROJECT"; id: string }
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
  | { type: "SET_ERROR"; error: string | null };

// ---------------------------------------------------------------------------
// Initial state
// ---------------------------------------------------------------------------

export const initialState: SessionState = {
  projects: [],
  activeProjectId: null,
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
  error: null,
  isProcessing: false,
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
    case "SET_ERROR":
      return { ...state, error: action.error };
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
  const { data } = await apiClient.POST("/api/projects", {
    body: { name, beschreibung },
  });
  if (data) {
    dispatch({ type: "ADD_PROJECT", project: data });
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
