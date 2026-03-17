/**
 * ExportButton — downloads artifacts as JSON and Markdown (Story 11-03, FR-B-07).
 *
 * Calls GET /api/projects/{id}/export via the typed openapi-fetch client.
 * Triggers two file downloads on success:
 *   - artifacts.json  (exploration + struktur + algorithmus)
 *   - artifacts.md    (Markdown rendering of all three artifacts)
 */

import { useState } from "react";
import { apiClient } from "../api/client";
import type { components } from "../generated/api";
import { useSession } from "../store/session";

type ExportResponse = components["schemas"]["ExportResponse"];

function triggerDownload(
  content: string,
  filename: string,
  mimeType: string,
): void {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}

export function ExportButton() {
  const { activeProjectId } = useSession();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!activeProjectId) return null;

  async function handleExport() {
    setLoading(true);
    setError(null);

    const { data, error: fetchError } = await apiClient.GET(
      "/api/projects/{projekt_id}/export",
      { params: { path: { projekt_id: activeProjectId! } } },
    );

    setLoading(false);

    if (fetchError || !data) {
      setError("Export fehlgeschlagen");
      return;
    }

    const response = data as ExportResponse;

    const jsonPayload = JSON.stringify(
      {
        exploration: response.exploration,
        struktur: response.struktur,
        algorithmus: response.algorithmus,
      },
      null,
      2,
    );

    triggerDownload(jsonPayload, "artifacts.json", "application/json");
    triggerDownload(response.markdown, "artifacts.md", "text/markdown");
  }

  return (
    <div className="export-button-area">
      <button
        className="export-button"
        onClick={handleExport}
        disabled={loading}
      >
        {loading ? "Exportiere..." : "Exportieren"}
      </button>
      {error && <span className="export-error">{error}</span>}
    </div>
  );
}
