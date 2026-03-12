"""Strukturierungsmodus — überführt Prozess in Strukturartefakt (SDD 6.6.2).

Stub-Implementierung für Epic 03. Die vollständige LLM-basierte Implementierung
folgt in Epic 08.
"""

from __future__ import annotations

from artifacts.models import Phasenstatus
from modes.base import BaseMode, ModeContext, ModeOutput


class StructuringMode(BaseMode):
    """Strukturierungsmodus (SDD 6.6.2).

    Ziel: Prozess in ein vollständiges Strukturartefakt überführen.

    Epic 03: Stub — gibt leere Patches und in_progress zurück.
    Epic 08: Wird durch vollständigen LLM-Aufruf ersetzt.
    """

    async def call(self, context: ModeContext) -> ModeOutput:
        return ModeOutput(
            nutzeraeusserung="[StructuringMode Stub] Kein LLM-Aufruf in diesem Epic.",
            patches=[],
            phasenstatus=Phasenstatus.in_progress,
            flags=[],
        )
