/**
 * AlgorithmView — renders Algorithm Artifact entries with EMMA actions (SDD 5.5).
 *
 * FR-B-06: Artifact visible at all times, reflects latest state.
 * FR-F-05: Invalidated sections visually marked.
 * Epic 09-06: Full detail rendering with parameter tables and compatibility badges.
 */

export interface EmmaAktion {
  aktion_id: string;
  aktionstyp: string;
  parameter?: Record<string, string>;
  nachfolger?: string[];
  emma_kompatibel?: boolean;
  kompatibilitaets_hinweis?: string | null;
}

export interface Algorithmusabschnitt {
  abschnitt_id: string;
  titel: string;
  struktur_ref: string;
  aktionen: Record<string, EmmaAktion>;
  completeness_status: string;
  status: string;
}

function statusLabel(status: string | undefined): string {
  switch (status) {
    case "leer":
      return "leer";
    case "teilweise":
      return "teilweise";
    case "vollstaendig":
      return "vollständig";
    case "nutzervalidiert":
      return "validiert";
    case "invalidiert":
      return "invalidiert";
    default:
      return status ?? "unbekannt";
  }
}

const ALGO_STATUS_COLORS: Record<string, string> = {
  ausstehend: "#6b7280",
  aktuell: "#059669",
  invalidiert: "#dc2626",
};

function EmmaAktionItem({ aktion }: { aktion: EmmaAktion }) {
  const params = aktion.parameter ?? {};
  const paramEntries = Object.entries(params);

  return (
    <div
      style={{
        marginLeft: "1rem",
        padding: "0.3rem 0.5rem",
        borderLeft: "2px solid #e5e7eb",
        marginTop: "0.3rem",
        fontSize: "0.8rem",
      }}
    >
      <div style={{ display: "flex", gap: "0.3rem", alignItems: "center" }}>
        <span
          style={{
            fontSize: "0.7rem",
            padding: "0.1rem 0.4rem",
            borderRadius: "3px",
            backgroundColor: "#2563eb",
            color: "#fff",
          }}
        >
          {aktion.aktionstyp}
        </span>
        <span style={{ color: "#999", fontSize: "0.7rem" }}>
          {aktion.aktion_id}
        </span>
        {aktion.emma_kompatibel === true && (
          <span style={{ color: "#059669", fontSize: "0.75rem" }}>
            EMMA-kompatibel
          </span>
        )}
        {aktion.emma_kompatibel === false && (
          <span style={{ color: "#dc2626", fontSize: "0.75rem" }}>
            nicht EMMA-kompatibel
          </span>
        )}
      </div>
      {paramEntries.length > 0 && (
        <div style={{ marginTop: "0.2rem", color: "#374151" }}>
          {paramEntries.map(([key, val]) => (
            <div key={key} style={{ fontSize: "0.75rem" }}>
              <span style={{ color: "#6b7280" }}>{key}:</span> {val}
            </div>
          ))}
        </div>
      )}
      {aktion.nachfolger && aktion.nachfolger.length > 0 && (
        <div
          style={{ fontSize: "0.7rem", color: "#6b7280", marginTop: "0.1rem" }}
        >
          → {aktion.nachfolger.join(", ")}
        </div>
      )}
      {aktion.emma_kompatibel === false && aktion.kompatibilitaets_hinweis && (
        <div
          style={{
            fontSize: "0.75rem",
            color: "#dc2626",
            backgroundColor: "#fef2f2",
            padding: "0.2rem 0.4rem",
            borderRadius: "3px",
            marginTop: "0.2rem",
          }}
        >
          {aktion.kompatibilitaets_hinweis}
        </div>
      )}
    </div>
  );
}

function AlgorithmAbschnittCard({
  id,
  abschnitt,
}: {
  id: string;
  abschnitt: Algorithmusabschnitt;
}) {
  const isInvalidiert = abschnitt.status === "invalidiert";
  const statusColor = ALGO_STATUS_COLORS[abschnitt.status] ?? "#6b7280";
  const aktionen = Object.values(abschnitt.aktionen ?? {});

  return (
    <div
      className={`slot-card ${isInvalidiert ? "invalidiert" : ""}`}
      style={isInvalidiert ? { borderLeft: "3px solid #dc2626" } : undefined}
    >
      <div className="slot-header">
        <span className="slot-name">{abschnitt.titel ?? id}</span>
        <span style={{ display: "flex", gap: "0.3rem", alignItems: "center" }}>
          <span
            style={{
              fontSize: "0.7rem",
              padding: "0.1rem 0.4rem",
              borderRadius: "3px",
              backgroundColor: statusColor,
              color: "#fff",
            }}
          >
            {abschnitt.status}
          </span>
          <span className={`slot-status ${abschnitt.completeness_status}`}>
            {statusLabel(abschnitt.completeness_status)}
          </span>
        </span>
      </div>
      <div
        style={{ fontSize: "0.75rem", color: "#6b7280", marginTop: "0.1rem" }}
      >
        Ref: {abschnitt.struktur_ref}
      </div>
      {aktionen.length > 0 && (
        <div style={{ marginTop: "0.3rem" }}>
          {aktionen.map((aktion) => (
            <EmmaAktionItem key={aktion.aktion_id} aktion={aktion} />
          ))}
        </div>
      )}
      {aktionen.length === 0 && (
        <div className="slot-empty" style={{ marginTop: "0.2rem" }}>
          (keine Aktionen)
        </div>
      )}
    </div>
  );
}

interface AlgorithmViewProps {
  artifact: Record<string, unknown>;
  version: number;
}

export function AlgorithmView({ artifact, version }: AlgorithmViewProps) {
  const zusammenfassung = (artifact.prozesszusammenfassung as string) ?? "";
  const abschnitte =
    (artifact.abschnitte as Record<string, Algorithmusabschnitt>) ?? {};
  const abschnittEntries = Object.entries(abschnitte);

  if (abschnittEntries.length === 0 && !zusammenfassung) {
    return (
      <div>
        <p className="slot-empty">Keine Einträge. Version {version}.</p>
      </div>
    );
  }

  return (
    <div className="slot-list">
      <p style={{ fontSize: "0.8rem", color: "#999", marginBottom: "0.5rem" }}>
        Version {version} — {abschnittEntries.length} Abschnitte
      </p>
      {zusammenfassung && (
        <div
          style={{
            backgroundColor: "#f0f9ff",
            padding: "0.5rem",
            borderRadius: "4px",
            marginBottom: "0.5rem",
            fontSize: "0.85rem",
          }}
        >
          <strong>Prozesszusammenfassung:</strong> {zusammenfassung}
        </div>
      )}
      {abschnittEntries.map(([id, abschnitt]) => (
        <AlgorithmAbschnittCard key={id} id={id} abschnitt={abschnitt} />
      ))}
    </div>
  );
}
