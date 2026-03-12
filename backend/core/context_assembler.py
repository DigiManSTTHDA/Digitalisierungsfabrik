"""ContextAssembler — stellt den Kontext für jeden Modusaufruf zusammen (SDD 6.5).

Epic 03 Stub: baut ModeContext aus den aktuellen Projektdaten ohne Dialoghistorie.
Epic 04 erweitert dies um echte Dialoghistorie aus der Datenbank und Systemprompts.

SDD-Referenz: 6.5 (Context Engineering), 6.5.3 (Kontext-Bestandteile).
"""

from __future__ import annotations

from artifacts.models import CompletenessStatus
from core.models import Project
from modes.base import ModeContext


def build_context(
    project: Project,
    completeness_state: dict[str, CompletenessStatus],
) -> ModeContext:
    """ModeContext aus aktuellem Projektzustand aufbauen (SDD 6.5.3).

    Epic 03: dialog_history ist leer — Dialoghistorie-Lookup aus SQLite folgt in Epic 04.
    """
    return ModeContext(
        projekt_id=project.projekt_id,
        aktive_phase=project.aktive_phase,
        aktiver_modus=project.aktiver_modus,
        exploration_artifact=project.exploration_artifact,
        structure_artifact=project.structure_artifact,
        algorithm_artifact=project.algorithm_artifact,
        working_memory=project.working_memory,
        dialog_history=[],  # Epic 04: aus dialog_history-Tabelle laden
        completeness_state=completeness_state,
    )
