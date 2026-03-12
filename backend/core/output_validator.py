"""OutputValidator — prüft den ModeOutput gegen den Output-Kontrakt (SDD 6.5.2).

Epic 03 Stub: gibt immer True zurück — Stubs erzeugen immer validen Output.
Epic 04 implementiert die vollständige Kontrakt-Prüfung (RFC 6902 Syntax,
Phasenstatus-Pflicht, Patch-Pfad-Validierung).

SDD-Referenz: 6.5.2 (Output-Kontrakt).
"""

from __future__ import annotations

from modes.base import ModeOutput


def validate(output: ModeOutput) -> bool:
    """ModeOutput gegen den Output-Kontrakt prüfen.

    Epic 03: Stub — gibt immer True zurück.
    Epic 04: Vollständige Implementierung mit RFC 6902 Syntax-Check,
    Phasenstatus-Pflicht und Patch-Pfad-Validierung.
    """
    return True
