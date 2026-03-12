"""ProgressTracker — aktualisiert Phasenstatus und Slot-Zähler im Working Memory (SDD 6.7).

Orchestrator-Schritt 10: nach jeder Runde werden Phasenstatus und Slot-Zähler
aus dem Modus-Output ins Working Memory geschrieben.

SDD-Referenz: 6.7 (Fortschrittsmodell).
"""

from __future__ import annotations

from artifacts.models import Phasenstatus
from core.working_memory import WorkingMemory


def update_working_memory(
    wm: WorkingMemory,
    phasenstatus: Phasenstatus,
    befuellte_slots: int,
    bekannte_slots: int,
) -> WorkingMemory:
    """Phasenstatus und Slot-Zähler im Working Memory aktualisieren (SDD 6.7).

    Args:
        wm: Aktuelles Working Memory (wird in-place modifiziert und zurückgegeben).
        phasenstatus: Vom aktiven Modus gemeldeter Fortschrittsstatus.
        befuellte_slots: Anzahl befüllter Slots (teilweise/vollstaendig/nutzervalidiert).
        bekannte_slots: Gesamtzahl aller bekannten Slots.

    Returns:
        Das aktualisierte WorkingMemory-Objekt.
    """
    wm.phasenstatus = phasenstatus
    wm.befuellte_slots = befuellte_slots
    wm.bekannte_slots = bekannte_slots
    return wm
