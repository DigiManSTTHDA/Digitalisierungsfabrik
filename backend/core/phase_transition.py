"""Phase transition logic — advances the system through its 4 phases (SDD 6.1).

PHASE_ORDER defines the sequence: exploration → strukturierung → spezifikation → validierung.
PHASE_TO_MODE maps each phase to its primary cognitive mode.
"""

from __future__ import annotations

import structlog

from artifacts.models import Phasenstatus, Projektphase
from core.models import Project
from core.working_memory import WorkingMemory

logger = structlog.get_logger()

# SDD 6.1.1 — exact phase sequence
PHASE_ORDER: list[Projektphase] = [
    Projektphase.exploration,
    Projektphase.strukturierung,
    Projektphase.spezifikation,
    Projektphase.validierung,
]

# Mapping from phase to primary mode name (SDD 6.1.1)
PHASE_TO_MODE: dict[Projektphase, str] = {
    Projektphase.exploration: "exploration",
    Projektphase.strukturierung: "structuring",
    Projektphase.spezifikation: "specification",
    Projektphase.validierung: "validation",
}


def next_phase(current: Projektphase) -> Projektphase | None:
    """Return the next phase in the sequence, or None if at end."""
    try:
        idx = PHASE_ORDER.index(current)
    except ValueError:
        return None
    if idx + 1 >= len(PHASE_ORDER):
        return None
    return PHASE_ORDER[idx + 1]


def advance_phase(project: Project, wm: WorkingMemory) -> bool:
    """Advance the project to the next phase. Returns True if successful.

    Updates both the project metadata and the working memory.
    Returns False if already at the last phase.
    """
    new_phase = next_phase(wm.aktive_phase)
    if new_phase is None:
        return False

    new_mode = PHASE_TO_MODE[new_phase]

    logger.info(
        "phase_transition.advance",
        from_phase=wm.aktive_phase.value,
        to_phase=new_phase.value,
        new_mode=new_mode,
    )

    wm.aktive_phase = new_phase
    wm.aktiver_modus = new_mode
    wm.vorheriger_modus = None
    wm.phasenstatus = Phasenstatus.in_progress

    project.aktive_phase = new_phase
    project.aktiver_modus = new_mode

    return True
