"""APPLY_PATCHES_TOOL — Anthropic tool schema for the apply_patches tool.

Defines the JSON schema sent to the Anthropic Messages API so the LLM
can return structured RFC 6902 patch operations. Used by all cognitive modes.

SDD references: FR-B-09 (Schreibkontrolle via RFC 6902), SDD 6.5.2 (Output-Kontrakt).
"""

from __future__ import annotations

# Anthropic tool definition for apply_patches (ADR-004 reference)
APPLY_PATCHES_TOOL: dict = {  # type: ignore[type-arg]
    "name": "apply_patches",
    "description": (
        "Wendet RFC 6902 JSON Patch Operationen auf das aktive Artefakt an. "
        "Jeder Patch muss 'op' (add/replace/remove), 'path' (RFC 6902 Pfad) "
        "und bei add/replace einen 'value' enthalten."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "nutzeraeusserung": {
                "type": "string",
                "description": (
                    "Deine Antwort an den Nutzer — wird im Chatbereich angezeigt. "
                    "Muss eine gezielte Folgefrage enthalten. "
                    "KEINE Zusammenfassung, KEINE Paraphrase des Gesagten. "
                    "Pflichtfeld, darf nicht leer sein."
                ),
            },
            "patches": {
                "type": "array",
                "description": "Liste von RFC 6902 JSON Patch Operationen auf das aktive Artefakt",
                "items": {
                    "type": "object",
                    "properties": {
                        "op": {
                            "type": "string",
                            "enum": ["add", "replace", "remove"],
                            "description": "RFC 6902 Operation",
                        },
                        "path": {
                            "type": "string",
                            "description": "RFC 6902 JSON Pointer Pfad (z.B. /slots/prozessziel/inhalt)",
                        },
                        "value": {
                            "description": "Neuer Wert (erforderlich bei add/replace)",
                        },
                    },
                    "required": ["op", "path"],
                },
            },
        },
        "required": ["nutzeraeusserung", "patches"],
    },
}
