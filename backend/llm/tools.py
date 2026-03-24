"""APPLY_PATCHES_TOOL — Anthropic tool schema for the apply_patches tool.

Defines the JSON schema sent to the Anthropic Messages API so the LLM
can return structured RFC 6902 patch operations. Used by all cognitive modes.

The LLM also reports its assessment of the phase status (SDD 6.4.1, 6.6.x):
- in_progress: still working, more turns needed
- nearing_completion: almost done, wrapping up
- phase_complete: phase goal reached, ready for Moderator handoff

INIT_APPLY_PATCHES_TOOL (CR-006): Variant for Init-Modi — includes init_status field.

SDD references: FR-B-09 (Schreibkontrolle via RFC 6902), SDD 6.5.2 (Output-Kontrakt).
"""

from __future__ import annotations

# Anthropic tool definition for apply_patches (ADR-004 reference)
APPLY_PATCHES_TOOL: dict = {  # type: ignore[type-arg]
    "name": "apply_patches",
    "description": (
        "Wendet RFC 6902 JSON Patch Operationen auf das aktive Artefakt an "
        "und meldet den Phasenstatus."
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
            "phasenstatus": {
                "type": "string",
                "enum": ["in_progress", "nearing_completion", "phase_complete"],
                "description": (
                    "Deine Einschätzung des Phasenstatus: "
                    "'in_progress' = es fehlen noch wesentliche Informationen. "
                    "'nearing_completion' = fast fertig, nur noch Feinschliff. "
                    "'phase_complete' = alle Ziele der Phase sind erreicht, "
                    "der Nutzer hat den Stand bestätigt, Übergabe an den Moderator."
                ),
            },
        },
        "required": ["nutzeraeusserung", "patches", "phasenstatus"],
    },
}

# CR-009: Tool-Schema für Init-Modi — vereinfacht (kein init_status mehr)
INIT_APPLY_PATCHES_TOOL: dict = {  # type: ignore[type-arg]
    "name": "apply_patches",
    "description": (
        "Wendet RFC 6902 JSON Patch Operationen auf das aktive Artefakt an."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "nutzeraeusserung": {
                "type": "string",
                "description": "Immer leer lassen: ''",
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
                            "description": "RFC 6902 JSON Pointer Pfad",
                        },
                        "value": {
                            "description": "Neuer Wert (erforderlich bei add/replace)",
                        },
                    },
                    "required": ["op", "path"],
                },
            },
            "phasenstatus": {
                "type": "string",
                "enum": ["in_progress"],
                "description": "Immer 'in_progress' — Init-Modi setzen keinen phase_complete.",
            },
        },
        "required": ["nutzeraeusserung", "patches", "phasenstatus"],
    },
}
