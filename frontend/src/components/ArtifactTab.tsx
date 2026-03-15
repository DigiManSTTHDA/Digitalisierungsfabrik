/**
 * ArtifactTab — renders a single artifact's slots as a structured view (HLA 3.1).
 *
 * FR-B-06: Artifact visible at all times, reflects latest state.
 * FR-F-05: Invalidated slots visually marked.
 * Epic 08-06: Structure artifact renders steps sorted by reihenfolge with
 *   type badges, decision conditions, successor links, and spannungsfeld warnings.
 */

interface Slot {
  slot_id?: string;
  bezeichnung?: string;
  inhalt?: string;
  completeness_status?: string;
  // Structure artifact fields (SDD 5.4)
  titel?: string;
  beschreibung?: string;
  typ?: string;
  reihenfolge?: number;
  nachfolger?: string[];
  bedingung?: string;
  ausnahme_beschreibung?: string;
  algorithmus_status?: string;
  spannungsfeld?: string;
  // Algorithm artifact fields
  aktionstyp?: string;
  status?: string;
}

interface ArtifactTabProps {
  artifact: Record<string, unknown>;
  type: "exploration" | "struktur" | "algorithmus";
}

function getSlots(
  artifact: Record<string, unknown>,
  type: string,
): Record<string, Slot> {
  if (type === "exploration") {
    return (artifact.slots as Record<string, Slot>) ?? {};
  }
  if (type === "struktur") {
    return (artifact.schritte as Record<string, Slot>) ?? {};
  }
  return (artifact.abschnitte as Record<string, Slot>) ?? {};
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

const TYPE_LABELS: Record<string, { label: string; color: string }> = {
  aktion: { label: "Aktion", color: "#2563eb" },
  entscheidung: { label: "Entscheidung", color: "#d97706" },
  schleife: { label: "Schleife", color: "#7c3aed" },
  ausnahme: { label: "Ausnahme", color: "#dc2626" },
};

function StructureSlotCard({ id, slot }: { id: string; slot: Slot }) {
  const status = slot.completeness_status ?? "leer";
  const algoStatus = slot.algorithmus_status ?? "ausstehend";
  const isInvalidiert = algoStatus === "invalidiert";
  const typeInfo = TYPE_LABELS[slot.typ ?? ""] ?? {
    label: slot.typ ?? "?",
    color: "#6b7280",
  };

  return (
    <div
      className={`slot-card ${isInvalidiert ? "invalidiert" : ""}`}
      style={isInvalidiert ? { borderLeft: "3px solid #dc2626" } : undefined}
    >
      <div className="slot-header">
        <span className="slot-name">
          <span style={{ color: "#999", marginRight: "0.3rem" }}>
            {slot.reihenfolge ?? "?"}.
          </span>
          {slot.titel ?? id}
        </span>
        <span style={{ display: "flex", gap: "0.3rem", alignItems: "center" }}>
          <span
            style={{
              fontSize: "0.7rem",
              padding: "0.1rem 0.4rem",
              borderRadius: "3px",
              backgroundColor: typeInfo.color,
              color: "#fff",
            }}
          >
            {typeInfo.label}
          </span>
          <span className={`slot-status ${status}`}>{statusLabel(status)}</span>
        </span>
      </div>
      {slot.beschreibung ? (
        <div className="slot-content">{slot.beschreibung}</div>
      ) : (
        <div className="slot-empty">(keine Beschreibung)</div>
      )}
      {slot.bedingung && (
        <div
          style={{ fontSize: "0.8rem", color: "#d97706", marginTop: "0.3rem" }}
        >
          Bedingung: {slot.bedingung}
        </div>
      )}
      {slot.ausnahme_beschreibung && (
        <div
          style={{ fontSize: "0.8rem", color: "#dc2626", marginTop: "0.3rem" }}
        >
          Ausnahme: {slot.ausnahme_beschreibung}
        </div>
      )}
      {slot.nachfolger && slot.nachfolger.length > 0 && (
        <div
          style={{ fontSize: "0.75rem", color: "#6b7280", marginTop: "0.3rem" }}
        >
          → {slot.nachfolger.join(", ")}
        </div>
      )}
      {slot.spannungsfeld && (
        <div
          style={{
            fontSize: "0.8rem",
            color: "#b45309",
            backgroundColor: "#fef3c7",
            padding: "0.2rem 0.4rem",
            borderRadius: "3px",
            marginTop: "0.3rem",
          }}
        >
          Spannungsfeld: {slot.spannungsfeld}
        </div>
      )}
      {isInvalidiert && (
        <div
          style={{ fontSize: "0.75rem", color: "#dc2626", marginTop: "0.2rem" }}
        >
          Algorithmus-Status: invalidiert
        </div>
      )}
    </div>
  );
}

export function ArtifactTab({ artifact, type }: ArtifactTabProps) {
  const slots = getSlots(artifact, type);
  const version = (artifact.version as number) ?? 0;

  // For structure artifacts: show prozesszusammenfassung and sort by reihenfolge
  if (type === "struktur") {
    const zusammenfassung = (artifact.prozesszusammenfassung as string) ?? "";
    const sortedEntries = Object.entries(slots).sort(
      ([, a], [, b]) => (a.reihenfolge ?? 0) - (b.reihenfolge ?? 0),
    );

    if (sortedEntries.length === 0 && !zusammenfassung) {
      return (
        <div>
          <p className="slot-empty">Keine Einträge. Version {version}.</p>
        </div>
      );
    }

    return (
      <div className="slot-list">
        <p
          style={{ fontSize: "0.8rem", color: "#999", marginBottom: "0.5rem" }}
        >
          Version {version} — {sortedEntries.length} Schritte
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
        {sortedEntries.map(([id, slot]) => (
          <StructureSlotCard key={id} id={id} slot={slot} />
        ))}
      </div>
    );
  }

  // Default rendering for exploration and algorithm artifacts
  const entries = Object.entries(slots);

  if (entries.length === 0) {
    return (
      <div>
        <p className="slot-empty">Keine Einträge. Version {version}.</p>
      </div>
    );
  }

  return (
    <div className="slot-list">
      <p style={{ fontSize: "0.8rem", color: "#999", marginBottom: "0.5rem" }}>
        Version {version} — {entries.length} Einträge
      </p>
      {entries.map(([id, slot]) => {
        const status = slot.completeness_status ?? slot.status ?? "leer";
        const isInvalidiert = status === "invalidiert";
        const content =
          slot.inhalt ?? slot.beschreibung ?? slot.aktionstyp ?? "";

        return (
          <div
            key={id}
            className={`slot-card ${isInvalidiert ? "invalidiert" : ""}`}
          >
            <div className="slot-header">
              <span className="slot-name">
                {slot.bezeichnung ?? slot.slot_id ?? id}
              </span>
              <span className={`slot-status ${status}`}>
                {statusLabel(status)}
              </span>
            </div>
            {content ? (
              <div className="slot-content">{content}</div>
            ) : (
              <div className="slot-empty">(leer)</div>
            )}
          </div>
        );
      })}
    </div>
  );
}
