"""ContextAssembler — stellt den Kontext für jeden Modusaufruf zusammen (SDD 6.5).

Baut ModeContext aus den aktuellen Projektdaten und der Dialoghistorie aus der DB.

SDD-Referenz: 6.5 (Context Engineering), 6.5.3 (Kontext-Bestandteile).
"""

from __future__ import annotations

from artifacts.models import CompletenessStatus
from core.models import Project
from modes.base import ModeContext
from persistence.project_repository import ProjectRepository

# Anzahl der letzten Dialogturns, die in den Kontext geladen werden.
_DEFAULT_HISTORY_TURNS = 20


def build_context(
    project: Project,
    completeness_state: dict[str, CompletenessStatus],
    repository: ProjectRepository | None = None,
    history_turns: int = _DEFAULT_HISTORY_TURNS,
) -> ModeContext:
    """ModeContext aus aktuellem Projektzustand aufbauen (SDD 6.5.3).

    Args:
        project: Das aktive Projekt.
        completeness_state: Aktueller Vollständigkeitsstatus aller Slots.
        repository: ProjectRepository für Dialoghistorie-Lookup. Wenn None,
            wird dialog_history als leere Liste übergeben.
        history_turns: Anzahl der letzten Turns, die geladen werden.
    """
    if repository is not None:
        dialog_history: list[dict[str, str]] = repository.load_dialog_history(
            project.projekt_id, last_n=history_turns
        )
    else:
        dialog_history = []

    return ModeContext(
        projekt_id=project.projekt_id,
        aktive_phase=project.aktive_phase,
        aktiver_modus=project.aktiver_modus,
        exploration_artifact=project.exploration_artifact,
        structure_artifact=project.structure_artifact,
        algorithm_artifact=project.algorithm_artifact,
        working_memory=project.working_memory,
        dialog_history=dialog_history,
        completeness_state=completeness_state,
    )
