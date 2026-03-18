"""ProgressTracker — aktualisiert Phasenstatus und Slot-Zähler im Working Memory (SDD 6.7).

Orchestrator-Schritt 10: nach jeder Runde werden Phasenstatus und Slot-Zähler
aus dem Modus-Output ins Working Memory geschrieben.

SDD-Referenz: 6.7 (Fortschrittsmodell).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from artifacts.models import Phasenstatus
from core.working_memory import WorkingMemory

if TYPE_CHECKING:
    from artifacts.models import StructureArtifact


def update_working_memory(
    wm: WorkingMemory,
    phasenstatus: Phasenstatus,
    befuellte_slots: int,
    bekannte_slots: int,
    structure_artifact: "StructureArtifact | None" = None,
) -> WorkingMemory:
    """Phasenstatus, Slot-Zähler und Spannungsfelder im Working Memory aktualisieren (SDD 6.7).

    Args:
        wm: Aktuelles Working Memory (wird in-place modifiziert und zurückgegeben).
        phasenstatus: Vom aktiven Modus gemeldeter Fortschrittsstatus.
        befuellte_slots: Anzahl befüllter Slots (teilweise/vollstaendig/nutzervalidiert).
        bekannte_slots: Gesamtzahl aller bekannten Slots.
        structure_artifact: Aktuelles Strukturartefakt für Spannungsfeld-Aggregation (S2-T2).

    Returns:
        Das aktualisierte WorkingMemory-Objekt.
    """
    wm.phasenstatus = phasenstatus
    wm.befuellte_slots = befuellte_slots
    wm.bekannte_slots = bekannte_slots

    # Spannungsfelder aus allen Strukturschritten aggregieren (S2-T2)
    if structure_artifact is not None:
        spannungsfelder: list[str] = []
        for schritt in structure_artifact.schritte.values():
            if schritt.spannungsfeld and schritt.spannungsfeld.strip():
                if schritt.spannungsfeld not in spannungsfelder:
                    spannungsfelder.append(schritt.spannungsfeld)
        wm.spannungsfelder = spannungsfelder

    return wm
