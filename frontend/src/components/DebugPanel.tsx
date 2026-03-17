/**
 * DebugPanel — collapsible panel showing Working Memory + flags (HLA 3.1).
 *
 * FR-F-02: Debug area shows active mode, flags, progress, WM contents.
 * SDD 2.3: Visible by default in prototype, can be hidden later.
 */

import { useState } from "react";
import { useSession } from "../store/session";

export function DebugPanel() {
  const { debugState, progress } = useSession();
  const [expanded, setExpanded] = useState(true);

  const wm = debugState.working_memory;
  const aktiverModus = (wm.aktiver_modus as string) ?? "–";
  const flags =
    debugState.flags.length > 0 ? debugState.flags.join(", ") : "keine";

  return (
    <div className="debug-panel">
      <div className="debug-toggle" onClick={() => setExpanded(!expanded)}>
        {expanded ? "▼" : "▶"} Diagnose
      </div>
      {expanded && (
        <div className="debug-content">
          <p>
            <strong>Modus:</strong> {aktiverModus} |{" "}
            <strong>Phasenstatus:</strong> {progress.phasenstatus} |{" "}
            <strong>Slots:</strong> {progress.befuellte_slots}/
            {progress.bekannte_slots} | <strong>Flags:</strong> {flags}
          </p>
          <pre>{JSON.stringify(wm, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
