"""Spezifikationsmodus — präzisiert Strukturschritte mit EMMA-Aktionen (SDD 6.6.3).

Stub-Implementierung für Epic 03. Die vollständige LLM-basierte Implementierung
folgt in Epic 09.
"""

from __future__ import annotations

from artifacts.models import Phasenstatus
from modes.base import BaseMode, ModeContext, ModeOutput


class SpecificationMode(BaseMode):
    """Spezifikationsmodus (SDD 6.6.3).

    Ziel: Jeden Strukturschritt mit konkreten EMMA-Aktionen präzisieren.

    Epic 03: Stub — gibt leere Patches und in_progress zurück.
    Epic 09: Wird durch vollständigen LLM-Aufruf ersetzt.
    """

    async def call(self, context: ModeContext) -> ModeOutput:
        return ModeOutput(
            nutzeraeusserung="[SpecificationMode Stub] Kein LLM-Aufruf in diesem Epic.",
            patches=[],
            phasenstatus=Phasenstatus.in_progress,
            flags=[],
        )
