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
} from "./store/session";
import "./App.css";

function ProjectSelection() {
  const { projects } = useSession();
  const dispatch = useSessionDispatch();
  const [name, setName] = useState("");
  const [beschreibung, setBeschreibung] = useState("");

  useEffect(() => {
    loadProjects(dispatch);
  }, [dispatch]);

  const handleCreate = async () => {
    if (!name.trim()) return;
    await createProject(dispatch, name.trim(), beschreibung.trim());
    setName("");
    setBeschreibung("");
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
        {projects.length === 0 && (
          <p className="empty">Keine Projekte vorhanden.</p>
        )}
        {projects.map((p) => (
          <div
            key={p.projekt_id}
            className="project-card"
            onClick={() =>
              dispatch({ type: "SELECT_PROJECT", id: p.projekt_id })
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
        ))}
      </div>
    </div>
  );
}

function SessionView() {
  const { activeProjectId } = useSession();
  const dispatch = useSessionDispatch();

  return (
    <div className="session-layout">
      <header className="phase-header">
        <span>Projekt: {activeProjectId?.slice(0, 8)}...</span>
        <button onClick={() => dispatch({ type: "DESELECT_PROJECT" })}>
          Zurück
        </button>
      </header>
      <div className="main-content">
        <div className="chat-pane">
          <p>ChatPane — wird in Story 06-04 implementiert</p>
        </div>
        <div className="artifact-pane">
          <p>ArtifactPane — wird in Story 06-05 implementiert</p>
        </div>
      </div>
      <div className="debug-panel">
        <p>DebugPanel — wird in Story 06-06 implementiert</p>
      </div>
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
