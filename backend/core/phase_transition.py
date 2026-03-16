"""Phase transition logic — advances the system through its 4 phases (SDD 6.1).

PHASE_ORDER defines the sequence: exploration → strukturierung → spezifikation → validierung.
PHASE_TO_MODE maps each phase to its primary cognitive mode.
"""

from __future__ import annotations

import structlog

from artifacts.models import Phasenstatus, Projektphase, Projektstatus
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
    When called in the validierung phase (terminal), sets projektstatus to
    abgeschlossen (FR-G-04) instead of trying to advance further.
    Returns False if already at the last phase with no action taken.
    """
    new_phase = next_phase(wm.aktive_phase)
    if new_phase is None:
        # Terminal phase: validierung → project complete (FR-G-04, SDD 6.1.3)
        if (
            wm.aktive_phase == Projektphase.validierung
            and project.projektstatus != Projektstatus.abgeschlossen
        ):
            project.projektstatus = Projektstatus.abgeschlossen
            wm.phasenstatus = Phasenstatus.phase_complete
            logger.info("phase_transition.terminal", phase="validierung", status="abgeschlossen")
            return True
        return False

    primary_mode = PHASE_TO_MODE[new_phase]

    logger.info(
        "phase_transition.advance",
        from_phase=wm.aktive_phase.value,
        to_phase=new_phase.value,
        new_mode="moderator",
    )

    # After phase advance, the Moderator provides the phase intro (SDD 6.1.2).
    # vorheriger_modus carries the primary working mode so return_to_mode
    # hands off to it once the user confirms.
    wm.aktive_phase = new_phase
    wm.aktiver_modus = "moderator"
    wm.vorheriger_modus = primary_mode
    wm.phasenstatus = Phasenstatus.in_progress

    project.aktive_phase = new_phase
    project.aktiver_modus = "moderator"

    return True
