/**
 * Root layout component — split-pane layout per HLA 3.1.
 *
 * When no project is active: shows project selection (FR-G-01, FR-G-02).
 * When a project is active: shows PhaseHeader + ChatPane + ArtifactPane + DebugPanel.
 */

import { useEffect, useState } from "react";
import {
  SessionProvider,
  useSession,
  useSessionDispatch,
  loadProjects,
  createProject,
  loadProjectState,
  deleteProject,
  deleteProjects,
} from "./store/session";
import { connectWebSocket, disconnect } from "./api/websocket";
import { PhaseHeader } from "./components/PhaseHeader";
import { ChatPane } from "./components/ChatPane";
import { ArtifactPane } from "./components/ArtifactPane";
import { DebugPanel } from "./components/DebugPanel";
import { ConfirmDialog } from "./components/ConfirmDialog";
import "./App.css";

function ProjectSelection() {
  const { projects } = useSession();
  const dispatch = useSessionDispatch();
  const [name, setName] = useState("");
  const [beschreibung, setBeschreibung] = useState("");
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [confirmDelete, setConfirmDelete] = useState<{
    type: "single" | "bulk";
    id?: string;
  } | null>(null);

  useEffect(() => {
    loadProjects(dispatch);
  }, [dispatch]);

  const handleCreate = async () => {
    if (!name.trim()) return;
    await createProject(dispatch, name.trim(), beschreibung.trim());
    setName("");
    setBeschreibung("");
  };

  const toggleSelect = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleConfirmDelete = async () => {
    if (!confirmDelete) return;
    if (confirmDelete.type === "single" && confirmDelete.id) {
      await deleteProject(dispatch, confirmDelete.id);
      selected.delete(confirmDelete.id);
      setSelected(new Set(selected));
    } else if (confirmDelete.type === "bulk") {
      await deleteProjects(dispatch, Array.from(selected));
      setSelected(new Set());
    }
    setConfirmDelete(null);
  };

  return (
    <div className="project-selection">
      <h1>Digitalisierungsfabrik</h1>
      <p className="subtitle">KI-gestützte Prozesserhebung</p>

      <div className="create-project">
        <h2>Neues Projekt</h2>
        <input
          type="text"
          placeholder="Projektname *"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleCreate()}
        />
        <input
          type="text"
          placeholder="Beschreibung (optional)"
          value={beschreibung}
          onChange={(e) => setBeschreibung(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleCreate()}
        />
        <button onClick={handleCreate} disabled={!name.trim()}>
          Projekt erstellen
        </button>
      </div>

      <div className="project-list">
        <h2>Vorhandene Projekte</h2>
        {selected.size > 0 && (
          <div
            style={{
              display: "flex",
              gap: "0.5rem",
              alignItems: "center",
              marginBottom: "0.5rem",
              padding: "0.4rem 0.6rem",
              background: "#fef2f2",
              borderRadius: "4px",
            }}
          >
            <span style={{ fontSize: "0.85rem" }}>
              {selected.size} ausgewählt
            </span>
            <button
              onClick={() => setConfirmDelete({ type: "bulk" })}
              style={{
                padding: "0.3rem 0.8rem",
                background: "#dc2626",
                color: "#fff",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
                fontSize: "0.8rem",
              }}
            >
              Ausgewählte löschen ({selected.size})
            </button>
          </div>
        )}
        {projects.length === 0 && (
          <p className="empty">Keine Projekte vorhanden.</p>
        )}
        {projects.map((p) => (
          <div
            key={p.projekt_id}
            className="project-card"
            style={{ display: "flex", alignItems: "flex-start", gap: "0.5rem" }}
          >
            <input
              type="checkbox"
              checked={selected.has(p.projekt_id)}
              onChange={() => toggleSelect(p.projekt_id)}
              onClick={(e) => e.stopPropagation()}
              style={{ marginTop: "0.3rem" }}
            />
            <div
              style={{ flex: 1, cursor: "pointer" }}
              onClick={() =>
                dispatch({
                  type: "SELECT_PROJECT",
                  id: p.projekt_id,
                  phase: p.aktive_phase,
                })
              }
            >
              <div className="project-name">{p.name}</div>
              {p.beschreibung && (
                <div className="project-desc">{p.beschreibung}</div>
              )}
              <div className="project-meta">
                <span className="phase-badge">{p.aktive_phase}</span>
                <span className="status-badge">{p.projektstatus}</span>
                <span className="date">
                  {new Date(p.zuletzt_geaendert).toLocaleDateString("de-DE")}
                </span>
              </div>
            </div>
            <button
              onClick={(e) => {
                e.stopPropagation();
                setConfirmDelete({ type: "single", id: p.projekt_id });
              }}
              style={{
                padding: "0.2rem 0.5rem",
                background: "none",
                border: "1px solid #e5e7eb",
                borderRadius: "4px",
                cursor: "pointer",
                color: "#dc2626",
                fontSize: "0.8rem",
              }}
              title="Projekt löschen"
            >
              Löschen
            </button>
          </div>
        ))}
      </div>

      <ConfirmDialog
        open={confirmDelete !== null}
        title="Projekt löschen"
        message={
          confirmDelete?.type === "bulk"
            ? `${selected.size} Projekt(e) unwiderruflich löschen?`
            : "Dieses Projekt unwiderruflich löschen?"
        }
        onConfirm={handleConfirmDelete}
        onCancel={() => setConfirmDelete(null)}
      />
    </div>
  );
}

function ErrorBanner() {
  const { error } = useSession();
  const dispatch = useSessionDispatch();
  if (!error) return null;
  return (
    <div
      className="error-banner"
      style={{
        background: "#fef2f2",
        color: "#991b1b",
        padding: "0.5rem 1rem",
        borderBottom: "1px solid #fecaca",
        display: "flex",
        justifyContent: "space-between",
      }}
    >
      <span>{error}</span>
      <button
        onClick={() => dispatch({ type: "SET_ERROR", error: null })}
        style={{ background: "none", border: "none", cursor: "pointer" }}
      >
        ✕
      </button>
    </div>
  );
}

function SessionView() {
  const { activeProjectId } = useSession();
  const dispatch = useSessionDispatch();

  // Connect WebSocket + load existing project state.
  // setTimeout(0) defers the connect to the next tick, which skips
  // React 18 StrictMode's first mount (unmount fires before the tick).
  // This prevents a double WS connection that causes ECONNABORTED errors
  // when the backend sends the greeting through the already-dead first socket.
  useEffect(() => {
    if (activeProjectId) {
      const timer = setTimeout(() => {
        connectWebSocket(activeProjectId, dispatch);
        loadProjectState(dispatch, activeProjectId);
      }, 0);
      return () => {
        clearTimeout(timer);
        disconnect();
      };
    }
  }, [activeProjectId, dispatch]);

  return (
    <div className="session-layout">
      <PhaseHeader />
      <ErrorBanner />
      <div className="main-content">
        <ChatPane />
        <ArtifactPane />
      </div>
      <DebugPanel />
    </div>
  );
}

function AppContent() {
  const { activeProjectId } = useSession();

  if (!activeProjectId) {
    return <ProjectSelection />;
  }
  return <SessionView />;
}

function App() {
  return (
    <SessionProvider>
      <AppContent />
    </SessionProvider>
  );
}

export default App;
