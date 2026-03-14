/**
 * ArtifactTab — renders a single artifact's slots as a structured view (HLA 3.1).
 *
 * FR-B-06: Artifact visible at all times, reflects latest state.
 * FR-F-05: Invalidated slots visually marked.
 */

interface Slot {
  slot_id?: string;
  bezeichnung?: string;
  inhalt?: string;
  completeness_status?: string;
  // Structure artifact fields
  beschreibung?: string;
  typ?: string;
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

export function ArtifactTab({ artifact, type }: ArtifactTabProps) {
  const slots = getSlots(artifact, type);
  const entries = Object.entries(slots);
  const version = (artifact.version as number) ?? 0;

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
