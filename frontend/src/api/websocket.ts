/**
 * WebSocket client — connects to backend, sends turns/panic, dispatches events.
 *
 * HLA 3.1: All 6 event types handled.
 * HLA 3.2: turn and panic messages sent.
 */

import type { Dispatch } from "react";
import type { SessionAction } from "../store/session";

let ws: WebSocket | null = null;
let dispatch: Dispatch<SessionAction> | null = null;

export function connectWebSocket(
  projectId: string,
  sessionDispatch: Dispatch<SessionAction>,
): void {
  disconnect();
  dispatch = sessionDispatch;

  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const host = window.location.host;
  ws = new WebSocket(`${protocol}//${host}/ws/session/${projectId}`);

  ws.onmessage = (event: MessageEvent) => {
    if (!dispatch) return;
    try {
      const data = JSON.parse(event.data as string) as Record<string, unknown>;
      handleEvent(data, dispatch);
    } catch {
      console.error("WebSocket: failed to parse message", event.data);
    }
  };

  ws.onerror = () => {
    if (dispatch) {
      dispatch({
        type: "SET_ERROR",
        error: "WebSocket-Verbindungsfehler",
      });
    }
  };

  ws.onclose = () => {
    ws = null;
  };
}

function handleEvent(
  data: Record<string, unknown>,
  d: Dispatch<SessionAction>,
): void {
  const eventType = data.event as string;

  switch (eventType) {
    case "chat_token":
      // Token streaming — future use; for now, ignored (complete response via chat_done)
      break;

    case "chat_done":
      d({
        type: "ADD_CHAT_MESSAGE",
        message: { role: "assistant", text: data.message as string },
      });
      d({ type: "SET_PROCESSING", value: false });
      break;

    case "artifact_update":
      d({
        type: "UPDATE_ARTIFACT",
        typ: data.typ as string,
        artefakt: data.artefakt as Record<string, unknown>,
      });
      break;

    case "progress_update":
      d({
        type: "UPDATE_PROGRESS",
        phasenstatus: data.phasenstatus as string,
        befuellte_slots: data.befuellte_slots as number,
        bekannte_slots: data.bekannte_slots as number,
      });
      break;

    case "debug_update":
      d({
        type: "UPDATE_DEBUG",
        working_memory: data.working_memory as Record<string, unknown>,
        flags: data.flags as string[],
      });
      break;

    case "error":
      d({
        type: "ADD_CHAT_MESSAGE",
        message: { role: "error", text: data.message as string },
      });
      d({ type: "SET_PROCESSING", value: false });
      break;

    default:
      console.warn("WebSocket: unknown event type", eventType);
  }
}

export function sendTurn(text: string, datei?: string): void {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    console.error("WebSocket not connected");
    return;
  }
  ws.send(JSON.stringify({ type: "turn", text, datei: datei ?? null }));
}

export function sendPanic(): void {
  if (!ws || ws.readyState !== WebSocket.OPEN) {
    console.error("WebSocket not connected");
    return;
  }
  ws.send(JSON.stringify({ type: "panic" }));
}

export function disconnect(): void {
  if (ws) {
    ws.close();
    ws = null;
  }
  dispatch = null;
}
