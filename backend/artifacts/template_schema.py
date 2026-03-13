"""ArtifactTemplate schema — defines allowed RFC 6902 patch paths per artifact type.

Each template holds a list of TemplatePathPattern entries. Patterns use Python regex
syntax where {id} in the documentation corresponds to [^/]+ (any dict key segment).
The Executor uses TEMPLATES[artifact_type].is_valid_patch(op, path) before applying
any patch to ensure only whitelisted paths and operations are accepted.
"""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel


class TemplatePathPattern(BaseModel):
    """A single allowed path pattern with its permitted operations."""

    pattern: str  # Python regex; {id} segments are stored as [^/]+
    allowed_ops: list[Literal["add", "replace", "remove"]]
    description: str  # Human/LLM-readable description of this path (OpenAPI prep)


class ArtifactTemplate(BaseModel):
    """Template schema for one artifact type — defines the patch allowlist."""

    artifact_type: Literal["exploration", "structure", "algorithm"]
    path_patterns: list[TemplatePathPattern]

    def is_valid_patch(self, op: str, path: str) -> bool:
        """Return True iff op is allowed and path matches a registered pattern.

        Uses re.fullmatch — prefix paths like /slots are not accepted.
        """
        for pp in self.path_patterns:
            if re.fullmatch(pp.pattern, path):
                return op in pp.allowed_ops
        return False


# ---------------------------------------------------------------------------
# Static template instances
# ---------------------------------------------------------------------------

EXPLORATION_TEMPLATE = ArtifactTemplate(
    artifact_type="exploration",
    path_patterns=[
        TemplatePathPattern(
            pattern=r"/slots/[^/]+",
            allowed_ops=["add", "remove"],
            description="Gesamten Slot hinzufügen oder entfernen",
        ),
        TemplatePathPattern(
            pattern=r"/slots/[^/]+/titel",
            allowed_ops=["replace"],
            description="Titel/Thema eines Slots aktualisieren (SDD 5.3: Pflichtfeld)",
        ),
        TemplatePathPattern(
            pattern=r"/slots/[^/]+/inhalt",
            allowed_ops=["replace"],
            description="Freitextinhalt eines Slots aktualisieren",
        ),
        TemplatePathPattern(
            pattern=r"/slots/[^/]+/completeness_status",
            allowed_ops=["add", "replace"],
            description="Completeness-Status eines Slots setzen (add und replace erlaubt — RFC 6902 §4.1)",
        ),
    ],
)

STRUCTURE_TEMPLATE = ArtifactTemplate(
    artifact_type="structure",
    path_patterns=[
        TemplatePathPattern(
            pattern=r"/schritte/[^/]+",
            allowed_ops=["add", "remove"],
            description="Gesamten Strukturschritt hinzufügen oder entfernen",
        ),
        TemplatePathPattern(
            pattern=r"/schritte/[^/]+/titel",
            allowed_ops=["replace"],
            description="Titel eines Strukturschritts setzen",
        ),
        TemplatePathPattern(
            pattern=r"/schritte/[^/]+/typ",
            allowed_ops=["replace"],
            description="Typ eines Strukturschritts setzen (aktion/entscheidung/schleife/ausnahme)",
        ),
        TemplatePathPattern(
            pattern=r"/schritte/[^/]+/beschreibung",
            allowed_ops=["replace"],
            description="Beschreibung eines Strukturschritts setzen — löst Invalidierung aus",
        ),
        TemplatePathPattern(
            pattern=r"/schritte/[^/]+/reihenfolge",
            allowed_ops=["replace"],
            description="Reihenfolge eines Strukturschritts setzen",
        ),
        TemplatePathPattern(
            pattern=r"/schritte/[^/]+/nachfolger",
            allowed_ops=["replace"],
            description="Nachfolger-IDs eines Strukturschritts setzen",
        ),
        TemplatePathPattern(
            pattern=r"/schritte/[^/]+/bedingung",
            allowed_ops=["replace"],
            description="Bedingungstext setzen (nur bei typ=entscheidung) — löst Invalidierung aus",
        ),
        TemplatePathPattern(
            pattern=r"/schritte/[^/]+/ausnahme_beschreibung",
            allowed_ops=["replace"],
            description="Ausnahmebeschreibung setzen (nur bei typ=ausnahme) — löst Invalidierung aus",
        ),
        TemplatePathPattern(
            pattern=r"/schritte/[^/]+/algorithmus_ref",
            allowed_ops=["replace"],
            description="Algorithmus-Referenz-IDs eines Strukturschritts setzen",
        ),
        TemplatePathPattern(
            pattern=r"/schritte/[^/]+/completeness_status",
            allowed_ops=["replace"],
            description="Completeness-Status eines Strukturschritts setzen",
        ),
        TemplatePathPattern(
            pattern=r"/schritte/[^/]+/algorithmus_status",
            allowed_ops=["replace"],
            description="Algorithmus-Status eines Strukturschritts setzen (z.B. invalidiert)",
        ),
        TemplatePathPattern(
            pattern=r"/schritte/[^/]+/spannungsfeld",
            allowed_ops=["replace"],
            description="Spannungsfeld-Hinweis eines Strukturschritts setzen",
        ),
    ],
)

ALGORITHM_TEMPLATE = ArtifactTemplate(
    artifact_type="algorithm",
    path_patterns=[
        TemplatePathPattern(
            pattern=r"/abschnitte/[^/]+",
            allowed_ops=["add", "remove"],
            description="Gesamten Algorithmusabschnitt hinzufügen oder entfernen",
        ),
        TemplatePathPattern(
            pattern=r"/abschnitte/[^/]+/titel",
            allowed_ops=["replace"],
            description="Titel eines Algorithmusabschnitts setzen",
        ),
        TemplatePathPattern(
            pattern=r"/abschnitte/[^/]+/struktur_ref",
            allowed_ops=["replace"],
            description="Referenz auf Strukturschritt setzen",
        ),
        TemplatePathPattern(
            pattern=r"/abschnitte/[^/]+/completeness_status",
            allowed_ops=["replace"],
            description="Completeness-Status eines Algorithmusabschnitts setzen",
        ),
        TemplatePathPattern(
            pattern=r"/abschnitte/[^/]+/status",
            allowed_ops=["replace"],
            description="Status eines Algorithmusabschnitts setzen (ausstehend/aktuell/invalidiert)",
        ),
        TemplatePathPattern(
            pattern=r"/abschnitte/[^/]+/aktionen/[^/]+",
            allowed_ops=["add", "remove"],
            description="Einzelne EMMA-Aktion hinzufügen oder entfernen",
        ),
        TemplatePathPattern(
            pattern=r"/abschnitte/[^/]+/aktionen/[^/]+/aktionstyp",
            allowed_ops=["replace"],
            description="Aktionstyp einer EMMA-Aktion setzen",
        ),
        TemplatePathPattern(
            pattern=r"/abschnitte/[^/]+/aktionen/[^/]+/parameter",
            allowed_ops=["replace"],
            description="Parameter einer EMMA-Aktion setzen",
        ),
        TemplatePathPattern(
            pattern=r"/abschnitte/[^/]+/aktionen/[^/]+/nachfolger",
            allowed_ops=["replace"],
            description="Nachfolger einer EMMA-Aktion setzen",
        ),
        TemplatePathPattern(
            pattern=r"/abschnitte/[^/]+/aktionen/[^/]+/emma_kompatibel",
            allowed_ops=["replace"],
            description="EMMA-Kompatibilitätsflag einer Aktion setzen",
        ),
        TemplatePathPattern(
            pattern=r"/abschnitte/[^/]+/aktionen/[^/]+/kompatibilitaets_hinweis",
            allowed_ops=["replace"],
            description="Kompatibilitätshinweis einer EMMA-Aktion setzen",
        ),
    ],
)

# Lookup map for Executor: artifact_type → template
TEMPLATES: dict[str, ArtifactTemplate] = {
    "exploration": EXPLORATION_TEMPLATE,
    "structure": STRUCTURE_TEMPLATE,
    "algorithm": ALGORITHM_TEMPLATE,
}
