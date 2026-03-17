/**
 * ArtifactPane — tabbed viewer for the three process artifacts (HLA 3.1).
 *
 * FR-B-06: Artifacts visible at all times, updated in real time.
 * FR-F-03: Artifacts displayed separately from chat.
 * FR-F-05: Validation findings highlight flagged slots.
 * SDD 2.1: Artifacts not active in the current phase shown as empty but visible.
 */

import { useState } from "react";
import { useSession } from "../store/session";
import { ArtifactTab } from "./ArtifactTab";
import { ExportButton } from "./ExportButton";

const TABS = [
  { key: "exploration", label: "Exploration" },
  { key: "struktur", label: "Struktur" },
  { key: "algorithmus", label: "Algorithmus" },
] as const;

export function ArtifactPane() {
  const { artifacts, validationReport } = useSession();
  const [activeTab, setActiveTab] = useState<string>("exploration");

  // Build a map of slot_id → severity for the active artifact type
  const flaggedSlots: Record<string, string> = {};
  if (validationReport) {
    for (const b of validationReport.befunde) {
      if (b.artefakttyp === activeTab) {
        for (const slot of b.betroffene_slots) {
          // Keep the highest severity per slot
          if (!flaggedSlots[slot] || b.schweregrad === "kritisch") {
            flaggedSlots[slot] = b.schweregrad;
          }
        }
      }
    }
  }

  return (
    <div className="artifact-pane">
      <div className="artifact-tabs">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            className={activeTab === tab.key ? "active" : ""}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <ArtifactTab
        artifact={artifacts[activeTab as keyof typeof artifacts]}
        type={activeTab as "exploration" | "struktur" | "algorithmus"}
        flaggedSlots={flaggedSlots}
      />
      <ExportButton />
    </div>
  );
}
