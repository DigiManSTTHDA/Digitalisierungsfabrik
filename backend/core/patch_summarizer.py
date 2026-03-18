"""Deterministischer Patch-Summarizer für nutzeraeusserung (SDD 6.5.x).

Übersetzt ein Patch-Array in einen lesbaren deutschen Satz.
Kein LLM — reine Logik. Verhindert halluzinierte Bestätigungen.
Schritt-IDs werden anhand des Artefakts in Titel übersetzt.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from artifacts.models import StructureArtifact


def _get_titel(sid: str, structure_artifact: "StructureArtifact | None") -> str:
    """Schritt-ID → Titel aus Artefakt, Fallback auf ID."""
    if structure_artifact is None:
        return sid
    schritt = structure_artifact.schritte.get(sid)
    return schritt.titel if schritt else sid


def summarize_patches(
    patches: list[dict],  # type: ignore[type-arg]
    structure_artifact: "StructureArtifact | None" = None,
) -> str:
    """Patches → lesbare deutsche Bestätigung."""
    if not patches:
        return ""

    parts: list[str] = []
    for patch in patches:
        op = patch.get("op")
        path = patch.get("path", "")
        value = patch.get("value")
        segments = path.strip("/").split("/")

        if segments[0] == "schritte" and len(segments) >= 2:
            sid = segments[1]
            field = segments[2] if len(segments) > 2 else None

            if op == "add" and not field:
                titel = value.get("titel", sid) if isinstance(value, dict) else sid
                parts.append(f"'{titel}' hinzugefügt")
            elif op == "remove" and not field:
                titel = _get_titel(sid, structure_artifact)
                parts.append(f"'{titel}' entfernt")
            elif op == "replace":
                titel = _get_titel(sid, structure_artifact)
                if field == "titel":
                    parts.append(f"Titel von '{titel}' geändert")
                elif field == "beschreibung":
                    parts.append(f"Beschreibung von '{titel}' aktualisiert")
                elif field == "nachfolger":
                    parts.append(f"Reihenfolge nach '{titel}' angepasst")
                elif field == "bedingung":
                    parts.append(f"Entscheidungsfrage bei '{titel}' aktualisiert")
                elif field == "typ":
                    parts.append(f"Typ von '{titel}' geändert")
            elif op == "add" and field == "spannungsfeld":
                titel = _get_titel(sid, structure_artifact)
                parts.append(f"Problem bei '{titel}' dokumentiert")

        elif segments[0] == "prozesszusammenfassung":
            parts.append("Prozesszusammenfassung aktualisiert")

    if not parts:
        return "Änderungen vorgenommen."

    return "Ich habe folgende Änderungen vorgenommen: " + ", ".join(parts) + "."
