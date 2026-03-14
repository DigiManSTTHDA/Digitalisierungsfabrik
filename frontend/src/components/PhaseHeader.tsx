/**
 * PhaseHeader — shows phase name, progress, panic button, download button (HLA 3.1).
 *
 * FR-F-01: Phase + progress visible at all times.
 * SDD 2.2: Panik-Button, Download-Button, Phasenanzeige.
 * SDD 2.5: Slot-Zähler (X von Y Slots befüllt).
 */

import { useSession, useSessionDispatch } from "../store/session";
import { apiClient } from "../api/client";

export function PhaseHeader() {
  const { activeProjectId, activePhase, progress } = useSession();
  const dispatch = useSessionDispatch();

  const handleBack = () => {
    dispatch({ type: "DESELECT_PROJECT" });
  };

  const handlePanic = () => {
    // Sends panic via WebSocket — handled in websocket.ts
    // For now, dispatched as a flag; websocket.ts sendPanic() called from here
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

  const phaseLabel =
    progress.phasenstatus === "phase_complete"
      ? "Phase abgeschlossen"
      : progress.phasenstatus === "nearing_completion"
        ? "Fast fertig"
        : "In Bearbeitung";

  return (
    <header className="phase-header">
      <div className="phase-info">
        <span>
          {activePhase.charAt(0).toUpperCase() + activePhase.slice(1)}
        </span>
        <span className="slot-counter">
          {progress.befuellte_slots} von {progress.bekannte_slots} Slots befüllt
        </span>
        <span className="status-badge">{phaseLabel}</span>
      </div>
      <div className="actions">
        <button className="panic-btn" onClick={handlePanic}>
          Panik
        </button>
        <button className="download-btn" onClick={handleDownload}>
          Download
        </button>
        <button onClick={handleBack}>Zurück</button>
      </div>
    </header>
  );
}
