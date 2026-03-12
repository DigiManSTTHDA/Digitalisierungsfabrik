"""Validierungsmodus — prüft Konsistenz, Vollständigkeit und EMMA-Kompatibilität (SDD 6.6.4).

Stub-Implementierung für Epic 03. Die vollständige LLM-basierte Implementierung
folgt in Epic 10.
"""

from __future__ import annotations

from artifacts.models import Phasenstatus
from modes.base import BaseMode, ModeContext, ModeOutput


class ValidationMode(BaseMode):
    """Validierungsmodus (SDD 6.6.4).

    Ziel: Konsistenz, Vollständigkeit und EMMA-Kompatibilität beider Artefakte prüfen.

    Epic 03: Stub — gibt leere Patches und in_progress zurück.
    Epic 10: Wird durch vollständigen LLM-Aufruf ersetzt.
    """

    async def call(self, context: ModeContext) -> ModeOutput:
        return ModeOutput(
            nutzeraeusserung="[ValidationMode Stub] Kein LLM-Aufruf in diesem Epic.",
            patches=[],
            phasenstatus=Phasenstatus.in_progress,
            flags=[],
        )
