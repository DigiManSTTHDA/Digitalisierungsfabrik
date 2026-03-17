/**
 * PhaseHeader — shows phase name, progress, panic button, download button (HLA 3.1).
 *
 * FR-F-01: Phase + progress visible at all times.
 * SDD 2.2: Panik-Button, Download-Button, Phasenanzeige.
 * SDD 2.5: Slot-Zähler (X von Y Slots befüllt).
 */

import { useSession, useSessionDispatch } from "../store/session";
import { apiClient } from "../api/client";

const PHASE_LABELS: Record<string, string> = {
  exploration: "Exploration",
  strukturierung: "Strukturierung",
  spezifikation: "Spezifikation",
  validierung: "Validierung",
};

export function PhaseHeader() {
  const { activeProjectId, activePhase, progress, projects } = useSession();
  const dispatch = useSessionDispatch();

  const activeProject = projects.find((p) => p.projekt_id === activeProjectId);
  const istAbgeschlossen = activeProject?.projektstatus === "abgeschlossen";

  const handleBack = () => {
    dispatch({ type: "DESELECT_PROJECT" });
  };

  const handlePanic = () => {
    // Sends panic via WebSocket — handled in websocket.ts
    import("../api/websocket").then((ws) => ws.sendPanic());
  };

  const handleDownload = async () => {
    if (!activeProjectId) return;
    const { data } = await apiClient.GET(
      "/api/projects/{projekt_id}/download",
      { params: { path: { projekt_id: activeProjectId } } },
    );
    if (data) {
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `projekt-${activeProjectId.slice(0, 8)}.json`;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const phaseLabel = istAbgeschlossen
    ? "Abgeschlossen"
    : (PHASE_LABELS[activePhase] ?? activePhase);

  const phasenstatus =
    progress.phasenstatus === "phase_complete"
      ? "Phase abgeschlossen"
      : progress.phasenstatus === "nearing_completion"
        ? "Fast fertig"
        : "In Bearbeitung";

  return (
    <header className="phase-header">
      <div className="phase-info">
        <span>{phaseLabel}</span>
        {istAbgeschlossen && (
          <span className="abgeschlossen-badge">Projekt abgeschlossen</span>
        )}
        <span className="slot-counter">
          {progress.befuellte_slots} von {progress.bekannte_slots} Slots befüllt
        </span>
        <span className="status-badge">{phasenstatus}</span>
      </div>
      <div className="actions">
        <button className="panic-btn" onClick={handlePanic}>
          Panik
        </button>
        <button className="download-btn" onClick={handleDownload}>
          Herunterladen
        </button>
        <button onClick={handleBack}>Zurück</button>
      </div>
    </header>
  );
}
