"""Markdown renderer for all three process artifacts (HLA Section 6, FR-B-07, OP-19).

ArtifaktRenderer converts ExplorationArtifact, StructureArtifact, and
AlgorithmArtifact to human-readable German Markdown suitable for download.
"""

from __future__ import annotations

from artifacts.models import AlgorithmArtifact, ExplorationArtifact, StructureArtifact


class ArtifaktRenderer:
    """Renders Digitalisierungsfabrik artifacts as Markdown (FR-B-07, OP-19)."""

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def render_exploration(self, artifact: ExplorationArtifact) -> str:
        """Render ExplorationArtifact as Markdown."""
        lines: list[str] = [
            "# Explorationsartefakt",
            f"Version: {artifact.version}",
            "",
        ]
        if not artifact.slots:
            lines.append("_Keine Slots vorhanden._")
            return "\n".join(lines)

        for slot in artifact.slots.values():
            lines.append(f"## {slot.titel}")
            lines.append(f"- **Slot-ID:** {slot.slot_id}")
            lines.append(f"- **Status:** {slot.completeness_status}")
            inhalt = slot.inhalt if slot.inhalt else "_(leer)_"
            lines.append(f"- **Inhalt:** {inhalt}")
            lines.append("")

        return "\n".join(lines)

    def render_structure(self, artifact: StructureArtifact) -> str:
        """Render StructureArtifact as Markdown."""
        lines: list[str] = [
            "# Strukturartefakt",
            f"Version: {artifact.version}",
            "",
            "## Prozesszusammenfassung",
            artifact.prozesszusammenfassung if artifact.prozesszusammenfassung else "_(leer)_",
            "",
        ]

        if not artifact.schritte:
            lines.append("_Keine Schritte vorhanden._")
            return "\n".join(lines)

        sorted_schritte = sorted(artifact.schritte.values(), key=lambda s: s.reihenfolge)
        for schritt in sorted_schritte:
            lines.append(f"### {schritt.reihenfolge}. {schritt.titel}")
            lines.append(f"- **Schritt-ID:** {schritt.schritt_id}")
            lines.append(f"- **Typ:** {schritt.typ}")
            if schritt.beschreibung:
                lines.append(f"- **Beschreibung:** {schritt.beschreibung}")
            lines.append(f"- **Reihenfolge:** {schritt.reihenfolge}")
            lines.append(
                f"- **Nachfolger:** {', '.join(schritt.nachfolger) if schritt.nachfolger else '–'}"
            )
            lines.append(
                f"- **Algorithmus-Ref:** {', '.join(schritt.algorithmus_ref) if schritt.algorithmus_ref else '–'}"
            )
            lines.append(f"- **Vollständigkeit:** {schritt.completeness_status}")
            lines.append(f"- **Algorithmus-Status:** {schritt.algorithmus_status}")
            if schritt.bedingung is not None:
                lines.append(f"- **Bedingung:** {schritt.bedingung}")
            if schritt.ausnahme_beschreibung is not None:
                lines.append(f"- **Ausnahme:** {schritt.ausnahme_beschreibung}")
            if schritt.spannungsfeld is not None:
                lines.append(f"- **Spannungsfeld:** {schritt.spannungsfeld}")
            lines.append("")

        return "\n".join(lines)

    def render_algorithm(self, artifact: AlgorithmArtifact) -> str:
        """Render AlgorithmArtifact as Markdown."""
        lines: list[str] = [
            "# Algorithmusartefakt",
            f"Version: {artifact.version}",
            "",
            "## Prozesszusammenfassung",
            artifact.prozesszusammenfassung if artifact.prozesszusammenfassung else "_(leer)_",
            "",
        ]

        if not artifact.abschnitte:
            lines.append("_Keine Abschnitte vorhanden._")
            return "\n".join(lines)

        for abschnitt in artifact.abschnitte.values():
            lines.append(f"### {abschnitt.titel}")
            lines.append(f"- **Abschnitt-ID:** {abschnitt.abschnitt_id}")
            lines.append(f"- **Struktur-Ref:** {abschnitt.struktur_ref}")
            lines.append(f"- **Vollständigkeit:** {abschnitt.completeness_status}")
            lines.append(f"- **Status:** {abschnitt.status}")
            lines.append("")

            for aktion in abschnitt.aktionen.values():
                lines.append(f"#### {aktion.aktion_id}")
                lines.append(f"- **Aktionstyp:** {aktion.aktionstyp}")
                if aktion.parameter:
                    param_str = ", ".join(f"{k}={v}" for k, v in aktion.parameter.items())
                    lines.append(f"- **Parameter:** {param_str}")
                else:
                    lines.append("- **Parameter:** –")
                lines.append(
                    f"- **Nachfolger:** {', '.join(aktion.nachfolger) if aktion.nachfolger else '–'}"
                )
                lines.append(f"- **EMMA-kompatibel:** {aktion.emma_kompatibel}")
                if aktion.kompatibilitaets_hinweis is not None:
                    lines.append(f"- **Hinweis:** {aktion.kompatibilitaets_hinweis}")
                lines.append("")

        return "\n".join(lines)

    def render_all(
        self,
        exploration: ExplorationArtifact,
        structure: StructureArtifact,
        algorithm: AlgorithmArtifact,
    ) -> str:
        """Render all three artifacts as a single Markdown document."""
        return "\n\n---\n\n".join(
            [
                self.render_exploration(exploration),
                self.render_structure(structure),
                self.render_algorithm(algorithm),
            ]
        )
