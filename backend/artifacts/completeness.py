"""CompletenessCalculator — berechnet Completeness-State und Slot-Zähler aus den Artefakten.

Der Orchestrator ruft calculate() nach jeder Schreiboperation auf, um das Working Memory
mit den aktuellen Slot-Zählern und der Completeness-State-Map zu aktualisieren.

SDD-Referenzen: 5.6 (Completeness-State), 6.7 (Fortschrittsmodell), FR-C-01.
"""

from __future__ import annotations

from artifacts.models import (
    AlgorithmArtifact,
    CompletenessStatus,
    ExplorationArtifact,
    StructureArtifact,
)

# Statuses that count as "befüllt" (SDD 6.7)
_FILLED_STATUSES: frozenset[CompletenessStatus] = frozenset(
    {
        CompletenessStatus.teilweise,
        CompletenessStatus.vollstaendig,
        CompletenessStatus.nutzervalidiert,
    }
)


class CompletenessCalculator:
    """Berechnet Completeness-State und Slot-Zähler aus allen drei Artefakten (SDD 5.6, 6.7).

    Primärer Zustand liegt in den Artefakten. Das Working Memory ist abgeleitet —
    der Calculator leitet den Zustand deterministisch aus den Artefakten ab.
    """

    def calculate(
        self,
        exploration: ExplorationArtifact,
        structure: StructureArtifact,
        algorithm: AlgorithmArtifact,
    ) -> tuple[dict[str, CompletenessStatus], int, int]:
        """Completeness-State und Slot-Zähler aus den drei Artefakten berechnen.

        Returns:
            (completeness_state, befuellte_slots, bekannte_slots)

            completeness_state: Mapping slot_id → CompletenessStatus für alle Slots
                aller drei Artefakte. Bei überlappenden IDs überschreiben spätere
                Artefakte frühere (algorithm überschreibt structure überschreibt exploration).
            befuellte_slots: Anzahl der Slots mit Status teilweise, vollstaendig oder
                nutzervalidiert (SDD 6.7). leer zählt nicht.
            bekannte_slots: Gesamtzahl aller Slots über alle drei Artefakte.
        """
        state: dict[str, CompletenessStatus] = {}

        for slot_id, slot in exploration.slots.items():
            state[slot_id] = slot.completeness_status

        for schritt_id, schritt in structure.schritte.items():
            state[schritt_id] = schritt.completeness_status

        for abschnitt_id, abschnitt in algorithm.abschnitte.items():
            state[abschnitt_id] = abschnitt.completeness_status

        bekannte_slots = (
            len(exploration.slots) + len(structure.schritte) + len(algorithm.abschnitte)
        )
        befuellte_slots = sum(1 for s in state.values() if s in _FILLED_STATUSES)

        return state, befuellte_slots, bekannte_slots
