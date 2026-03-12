"""Moderator — steuert Phasenwechsel, Eskalationen und Nutzerdialog (SDD 6.6.5).

Stub-Implementierung für Epic 03. Die vollständige LLM-basierte Implementierung
folgt in Epic 07.
"""

from __future__ import annotations

from artifacts.models import Phasenstatus
from modes.base import BaseMode, ModeContext, ModeOutput


class Moderator(BaseMode):
    """Moderator (SDD 6.6.5).

    Ziel: Orientierung des Nutzers bei Phasenübergängen, Eskalationen und Problemen.
    Aktivierung durch Flags phase_complete, escalate oder blocked.

    Epic 03: Stub — gibt leere Patches und in_progress zurück.
    Epic 07: Wird durch vollständigen LLM-Aufruf ersetzt.
    """

    async def call(self, context: ModeContext) -> ModeOutput:
        return ModeOutput(
            nutzeraeusserung="[Moderator Stub] Kein LLM-Aufruf in diesem Epic.",
            patches=[],
            phasenstatus=Phasenstatus.in_progress,
            flags=[],
        )
