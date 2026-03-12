"""Explorationsmodus — erfasst implizites Prozesswissen des Nutzers (SDD 6.6.1).

Stub-Implementierung für Epic 03. Die vollständige LLM-basierte Implementierung
mit ContextAssembler, Systemprompt und Anthropic-Client folgt in Epic 04.
"""

from __future__ import annotations

from artifacts.models import Phasenstatus
from modes.base import BaseMode, ModeContext, ModeOutput


class ExplorationMode(BaseMode):
    """Explorationsmodus (SDD 6.6.1).

    Ziel: Implizites Prozesswissen des Nutzers erfassen und ein ausreichend
    klares Prozessverständnis herstellen.

    Epic 03: Stub — gibt leere Patches und in_progress zurück.
    Epic 04: Wird durch vollständigen LLM-Aufruf ersetzt.
    """

    async def call(self, context: ModeContext) -> ModeOutput:
        return ModeOutput(
            nutzeraeusserung="[ExplorationMode Stub] Kein LLM-Aufruf in diesem Epic.",
            patches=[],
            phasenstatus=Phasenstatus.in_progress,
            flags=[],
        )
