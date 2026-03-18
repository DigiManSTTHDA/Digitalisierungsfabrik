/** SessionClient — WebSocket/HTTP client for the Digitalisierungsfabrik backend. */

import WebSocket from 'ws';
import type { ArtifactSnapshots, TurnResponse, TurnState } from './types.js';

// Custom Error Types
export class ConnectionError extends Error {
  constructor(message: string) { super(message); this.name = 'ConnectionError'; }
}
export class TimeoutError extends Error {
  constructor(message: string) { super(message); this.name = 'TimeoutError'; }
}
export class BackendError extends Error {
  constructor(message: string) { super(message); this.name = 'BackendError'; }
}

// WebSocket Event Types (from backend core/events.py)
interface ChatDoneEvent { event: 'chat_done'; message: string }
interface ArtifactUpdateEvent { event: 'artifact_update'; typ: string; artefakt: Record<string, unknown> }
interface ProgressUpdateEvent { event: 'progress_update'; phasenstatus: string; befuellte_slots: number; bekannte_slots: number }
interface DebugUpdateEvent { event: 'debug_update'; working_memory: Record<string, unknown>; flags: string[] }
interface ErrorEventPayload { event: 'error'; message: string; recoverable: boolean }

type BackendEvent = ChatDoneEvent | ArtifactUpdateEvent | ProgressUpdateEvent | DebugUpdateEvent | ErrorEventPayload;
const EVENTS_PER_TURN = 6;

export class SessionClient {
  private readonly baseUrl: string;
  private readonly wsBaseUrl: string;
  private readonly timeoutMs: number;
  private ws: WebSocket | null = null;
  private eventQueue: BackendEvent[] = [];
  private eventResolve: ((event: BackendEvent) => void) | null = null;

  constructor(baseUrl: string = 'http://localhost:8000', timeoutMs: number = 60_000) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
    this.wsBaseUrl = this.baseUrl.replace(/^http/, 'ws');
    this.timeoutMs = timeoutMs;
  }

  /** Create a new project via POST /api/projects. Returns projekt_id. */
  async createProject(name: string): Promise<string> {
    const url = `${this.baseUrl}/api/projects`;
    let response: Response;
    try {
      response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, beschreibung: '' }),
      });
    } catch {
      throw new ConnectionError(
        `Backend nicht erreichbar unter ${this.baseUrl}. Bitte Backend starten.`
      );
    }
    if (!response.ok) {
      const text = await response.text();
      throw new BackendError(`Project creation failed (${response.status}): ${text}`);
    }
    const data = (await response.json()) as { projekt_id: string };
    return data.projekt_id;
  }

  /**
   * Connect to the WebSocket for a project. Consumes the initial
   * greeting/replay events automatically.
   */
  async connect(projectId: string): Promise<TurnResponse> {
    const wsUrl = `${this.wsBaseUrl}/ws/session/${projectId}`;
    this.eventQueue = [];
    this.eventResolve = null;

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(wsUrl);
      } catch {
        reject(new ConnectionError(`WebSocket-Verbindung fehlgeschlagen: ${wsUrl}`));
        return;
      }

      const timeout = setTimeout(() => {
        reject(new TimeoutError(`Timeout beim Verbinden mit ${wsUrl}`));
      }, this.timeoutMs);

      this.ws.on('error', (err) => {
        clearTimeout(timeout);
        reject(new ConnectionError(`WebSocket-Fehler: ${err.message}`));
      });

      this.ws.on('open', () => {
        clearTimeout(timeout);
        // Consume greeting/replay events
        this.collectTurnResponse(Date.now()).then(resolve).catch(reject);
      });

      this.ws.on('message', (data) => {
        let event: BackendEvent;
        try {
          event = JSON.parse(data.toString()) as BackendEvent;
        } catch {
          return;
        }
        if (this.eventResolve) {
          const fn = this.eventResolve;
          this.eventResolve = null;
          fn(event);
        } else {
          this.eventQueue.push(event);
        }
      });

      this.ws.on('close', () => {
        this.ws = null;
      });
    });
  }

  /** Disconnect the WebSocket. */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /** Send a user message and collect the turn response. */
  async sendMessage(projectId: string, message: string): Promise<TurnResponse> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      await this.connect(projectId);
    }
    const startTime = Date.now();
    this.ws!.send(JSON.stringify({ type: 'turn', text: message, datei: null }));
    return this.collectTurnResponse(startTime);
  }

  /** Press a button (e.g. panic) via WebSocket. */
  async pressButton(projectId: string, button: 'panic'): Promise<TurnResponse> {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      await this.connect(projectId);
    }
    const startTime = Date.now();
    this.ws!.send(JSON.stringify({ type: button }));
    return this.collectTurnResponse(startTime);
  }

  /** Retrieve artifacts via GET /api/projects/{id}/artifacts. */
  async getArtifacts(projectId: string): Promise<ArtifactSnapshots> {
    const url = `${this.baseUrl}/api/projects/${projectId}/artifacts`;
    let response: Response;
    try {
      response = await fetch(url);
    } catch {
      throw new ConnectionError(
        `Backend nicht erreichbar unter ${this.baseUrl}. Bitte Backend starten.`
      );
    }
    if (!response.ok) {
      const text = await response.text();
      throw new BackendError(`Artifact fetch failed (${response.status}): ${text}`);
    }
    return (await response.json()) as ArtifactSnapshots;
  }

  private nextEvent(): Promise<BackendEvent> {
    if (this.eventQueue.length > 0) {
      return Promise.resolve(this.eventQueue.shift()!);
    }
    return new Promise((resolve) => {
      this.eventResolve = resolve;
    });
  }

  private async collectTurnResponse(startTime: number): Promise<TurnResponse> {
    let chatMessage = '';
    let artifactsUpdated = false;
    const state: TurnState = {
      aktiver_modus: '',
      aktive_phase: '',
      phasenstatus: '',
      befuellte_slots: 0,
      bekannte_slots: 0,
      flags: [],
      working_memory: {},
    };

    for (let i = 0; i < EVENTS_PER_TURN; i++) {
      const event = await Promise.race([
        this.nextEvent(),
        this.timeoutPromise<BackendEvent>(),
      ]);

      if (event.event === 'error') {
        throw new BackendError((event as ErrorEventPayload).message);
      }

      this.applyEvent(event, state, (msg) => { chatMessage = msg; },
        () => { artifactsUpdated = true; });
    }

    // If phase_complete triggered auto-moderator, collect that batch too
    if (state.flags.includes('phase_complete') && state.aktiver_modus === 'moderator') {
      for (let i = 0; i < EVENTS_PER_TURN; i++) {
        const event = await Promise.race([
          this.nextEvent(),
          this.timeoutPromise<BackendEvent>(),
        ]);
        if (event.event === 'error') {
          throw new BackendError((event as ErrorEventPayload).message);
        }
        this.applyEvent(event, state, (msg) => { chatMessage = msg; },
          () => { artifactsUpdated = true; });
      }
    }

    return {
      message: chatMessage,
      state,
      artifacts_updated: artifactsUpdated,
      response_time_ms: Date.now() - startTime,
    };
  }

  private applyEvent(
    event: BackendEvent,
    state: TurnState,
    setMessage: (msg: string) => void,
    setArtifactsUpdated: () => void,
  ): void {
    switch (event.event) {
      case 'chat_done':
        setMessage(event.message);
        break;
      case 'artifact_update':
        setArtifactsUpdated();
        break;
      case 'progress_update':
        state.phasenstatus = event.phasenstatus as string;
        state.befuellte_slots = event.befuellte_slots;
        state.bekannte_slots = event.bekannte_slots;
        break;
      case 'debug_update':
        state.flags = event.flags;
        state.working_memory = event.working_memory;
        if (event.working_memory) {
          state.aktiver_modus = (event.working_memory['aktiver_modus'] as string) ?? '';
          state.aktive_phase = (event.working_memory['aktive_phase'] as string) ?? '';
        }
        break;
    }
  }

  private timeoutPromise<T>(): Promise<T> {
    return new Promise((_, reject) => {
      setTimeout(() => reject(new TimeoutError(
        `Timeout nach ${this.timeoutMs}ms — keine Antwort vom Backend`
      )), this.timeoutMs);
    });
  }
}
