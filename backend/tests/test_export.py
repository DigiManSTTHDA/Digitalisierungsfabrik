"""Tests for ArtifaktRenderer — Story 11-01.

Behaviour contract:
1. render_exploration produces heading, version, slot titles, inhalt, completeness_status.
2. Empty-inhalt slots render as _(leer)_.
3. render_structure produces heading, version, prozesszusammenfassung, all Strukturschritt fields.
4. Optional Strukturschritt fields (bedingung, ausnahme_beschreibung, spannungsfeld) appear only when set.
5. algorithmus_ref list is always rendered in structure output.
6. render_algorithm produces heading, version, prozesszusammenfassung, all Algorithmusabschnitt/EmmaAktion fields.
7. EmmaAktion nachfolger list is rendered.
8. render_all concatenates all three sections with --- separator.
"""

from __future__ import annotations

import pytest

from artifacts.models import (
    AlgorithmArtifact,
    Algorithmusabschnitt,
    AlgorithmusStatus,
    CompletenessStatus,
    EmmaAktion,
    EmmaAktionstyp,
    ExplorationArtifact,
    ExplorationSlot,
    StructureArtifact,
    Strukturschritt,
    Strukturschritttyp,
)
from artifacts.renderer import ArtifaktRenderer


@pytest.fixture()
def renderer() -> ArtifaktRenderer:
    return ArtifaktRenderer()


# ---------------------------------------------------------------------------
# Exploration rendering
# ---------------------------------------------------------------------------


def test_render_exploration_with_slots(renderer: ArtifaktRenderer) -> None:
    """Slot titles, inhalt, slot_id, and completeness_status all appear in output."""
    art = ExplorationArtifact(
        version=3,
        slots={
            "s1": ExplorationSlot(
                slot_id="s1",
                titel="Prozessname",
                inhalt="Rechnungsbearbeitung",
                completeness_status=CompletenessStatus.nutzervalidiert,
            ),
            "s2": ExplorationSlot(
                slot_id="s2",
                titel="Beteiligte",
                inhalt="Buchhaltung",
                completeness_status=CompletenessStatus.vollstaendig,
            ),
        },
    )
    result = renderer.render_exploration(art)

    assert "# Explorationsartefakt" in result
    assert "Version: 3" in result
    # Both slot titles must appear as headings
    assert "Prozessname" in result
    assert "Beteiligte" in result
    # Inhalt values
    assert "Rechnungsbearbeitung" in result
    assert "Buchhaltung" in result
    # slot_ids
    assert "s1" in result
    assert "s2" in result
    # completeness_status
    assert "nutzervalidiert" in result
    assert "vollstaendig" in result


def test_render_exploration_empty_slot_shows_leer(renderer: ArtifaktRenderer) -> None:
    """Empty inhalt renders as _(leer)_, not as an empty string."""
    art = ExplorationArtifact(
        version=1,
        slots={
            "s1": ExplorationSlot(
                slot_id="s1",
                titel="Prozessname",
                inhalt="",
                completeness_status=CompletenessStatus.leer,
            ),
        },
    )
    result = renderer.render_exploration(art)

    assert "_(leer)_" in result
    # Must NOT render a blank content line instead
    # (verified by presence of the placeholder text)


def test_render_exploration_empty_artifact(renderer: ArtifaktRenderer) -> None:
    """An artifact with no slots still renders the heading and version."""
    art = ExplorationArtifact(version=0, slots={})
    result = renderer.render_exploration(art)

    assert "# Explorationsartefakt" in result
    assert "Version: 0" in result


# ---------------------------------------------------------------------------
# Structure rendering
# ---------------------------------------------------------------------------


def test_render_structure_with_steps(renderer: ArtifaktRenderer) -> None:
    """All mandatory Strukturschritt fields appear; spannungsfeld absent when None."""
    art = StructureArtifact(
        version=2,
        prozesszusammenfassung="Rechnungsbearbeitung per E-Mail",
        schritte={
            "s1": Strukturschritt(
                schritt_id="s1",
                titel="Rechnung empfangen",
                typ=Strukturschritttyp.aktion,
                beschreibung="Eingehende Rechnung per E-Mail",
                reihenfolge=1,
                nachfolger=["s2"],
                algorithmus_ref=["a1"],
                completeness_status=CompletenessStatus.nutzervalidiert,
                algorithmus_status=AlgorithmusStatus.aktuell,
                spannungsfeld=None,
            ),
            "s2": Strukturschritt(
                schritt_id="s2",
                titel="Prüfen",
                typ=Strukturschritttyp.entscheidung,
                beschreibung="Rechnung prüfen",
                reihenfolge=2,
                nachfolger=[],
                algorithmus_ref=["a2", "a3"],
                completeness_status=CompletenessStatus.vollstaendig,
                algorithmus_status=AlgorithmusStatus.ausstehend,
                spannungsfeld=None,
            ),
        },
    )
    result = renderer.render_structure(art)

    assert "# Strukturartefakt" in result
    assert "Version: 2" in result
    assert "Prozesszusammenfassung" in result
    assert "Rechnungsbearbeitung per E-Mail" in result
    # Step titles and IDs
    assert "Rechnung empfangen" in result
    assert "s1" in result
    assert "Prüfen" in result
    assert "s2" in result
    # Types
    assert "aktion" in result
    assert "entscheidung" in result
    # Reihenfolge shown
    assert "1" in result
    assert "2" in result
    # algorithmus_ref
    assert "a1" in result
    assert "a2" in result
    # completeness / algorithmus_status
    assert "nutzervalidiert" in result
    assert "aktuell" in result
    # spannungsfeld must NOT appear at all when None — OR logic was a tautology
    assert "Spannungsfeld" not in result


def test_render_structure_spannungsfeld_shown(renderer: ArtifaktRenderer) -> None:
    """spannungsfeld text appears when set."""
    art = StructureArtifact(
        version=1,
        schritte={
            "s1": Strukturschritt(
                schritt_id="s1",
                titel="Freigabe",
                typ=Strukturschritttyp.aktion,
                reihenfolge=1,
                completeness_status=CompletenessStatus.vollstaendig,
                algorithmus_status=AlgorithmusStatus.aktuell,
                spannungsfeld="Freigabe kann mehrere Tage dauern",
            ),
        },
    )
    result = renderer.render_structure(art)

    assert "Freigabe kann mehrere Tage dauern" in result


def test_render_structure_bedingung_shown(renderer: ArtifaktRenderer) -> None:
    """bedingung appears when set (typ=entscheidung)."""
    art = StructureArtifact(
        version=1,
        schritte={
            "s1": Strukturschritt(
                schritt_id="s1",
                titel="Betrag prüfen",
                typ=Strukturschritttyp.entscheidung,
                reihenfolge=1,
                completeness_status=CompletenessStatus.vollstaendig,
                algorithmus_status=AlgorithmusStatus.aktuell,
                bedingung="Betrag > 1000 EUR",
            ),
        },
    )
    result = renderer.render_structure(art)

    assert "Betrag > 1000 EUR" in result


def test_render_structure_ausnahme_beschreibung_shown(renderer: ArtifaktRenderer) -> None:
    """ausnahme_beschreibung appears when set (typ=ausnahme)."""
    art = StructureArtifact(
        version=1,
        schritte={
            "s1": Strukturschritt(
                schritt_id="s1",
                titel="Fehlerfall",
                typ=Strukturschritttyp.ausnahme,
                reihenfolge=1,
                completeness_status=CompletenessStatus.vollstaendig,
                algorithmus_status=AlgorithmusStatus.aktuell,
                ausnahme_beschreibung="Rechnung unleserlich",
            ),
        },
    )
    result = renderer.render_structure(art)

    assert "Rechnung unleserlich" in result


# ---------------------------------------------------------------------------
# Algorithm rendering
# ---------------------------------------------------------------------------


def test_render_algorithm_with_actions(renderer: ArtifaktRenderer) -> None:
    """All EmmaAktion fields including nachfolger appear in output."""
    art = AlgorithmArtifact(
        version=1,
        prozesszusammenfassung="Technische Beschreibung",
        abschnitte={
            "a1": Algorithmusabschnitt(
                abschnitt_id="a1",
                titel="E-Mail öffnen",
                struktur_ref="s1",
                completeness_status=CompletenessStatus.vollstaendig,
                status=AlgorithmusStatus.aktuell,
                aktionen={
                    "act1": EmmaAktion(
                        aktion_id="act1",
                        aktionstyp=EmmaAktionstyp.FIND,
                        parameter={"selector": "email_app"},
                        nachfolger=["act2"],
                        emma_kompatibel=True,
                    ),
                    "act2": EmmaAktion(
                        aktion_id="act2",
                        aktionstyp=EmmaAktionstyp.READ,
                        parameter={},
                        nachfolger=[],
                        emma_kompatibel=False,
                        kompatibilitaets_hinweis="Dynamischer Inhalt",
                    ),
                },
            ),
        },
    )
    result = renderer.render_algorithm(art)

    assert "# Algorithmusartefakt" in result
    assert "Version: 1" in result
    assert "Technische Beschreibung" in result
    assert "E-Mail öffnen" in result
    assert "a1" in result
    assert "s1" in result  # struktur_ref
    # EmmaAktion fields
    assert "FIND" in result
    assert "READ" in result
    assert "act2" in result  # nachfolger of act1
    assert "email_app" in result  # parameter value
    # emma_kompatibel must show the actual boolean value — loose OR was a tautology
    # ("kompatibel" always appears as a field label so the last branch never fails)
    assert "True" in result  # act1 is emma_kompatibel=True
    # kompatibilitaets_hinweis
    assert "Dynamischer Inhalt" in result


def test_render_algorithm_empty_artifact(renderer: ArtifaktRenderer) -> None:
    """Empty algorithm artifact still renders heading and version."""
    art = AlgorithmArtifact(version=0)
    result = renderer.render_algorithm(art)

    assert "# Algorithmusartefakt" in result
    assert "Version: 0" in result


# ---------------------------------------------------------------------------
# render_all
# ---------------------------------------------------------------------------


def test_render_all_contains_all_sections(renderer: ArtifaktRenderer) -> None:
    """render_all produces all three headings and --- separator between sections."""
    exploration = ExplorationArtifact(version=1)
    structure = StructureArtifact(version=1)
    algorithm = AlgorithmArtifact(version=1)

    result = renderer.render_all(exploration, structure, algorithm)

    assert "# Explorationsartefakt" in result
    assert "# Strukturartefakt" in result
    assert "# Algorithmusartefakt" in result
    assert "---" in result
    # All three sections appear in correct order
    pos_exp = result.index("# Explorationsartefakt")
    pos_str = result.index("# Strukturartefakt")
    pos_alg = result.index("# Algorithmusartefakt")
    assert pos_exp < pos_str < pos_alg


def test_render_all_separator_count(renderer: ArtifaktRenderer) -> None:
    """render_all joins exactly 3 sections with exactly 2 '---' separators.

    T-7 boundary: a renderer that emits extra or missing separators would break
    the Markdown structure seen by the user. Checking count is falsifiable
    (adding a fourth section or omitting the second separator both fail).
    """
    result = renderer.render_all(
        ExplorationArtifact(version=0),
        StructureArtifact(version=0),
        AlgorithmArtifact(version=0),
    )
    # The separator string used by render_all is "\n\n---\n\n"
    assert result.count("\n---\n") == 2


def test_render_exploration_single_slot(renderer: ArtifaktRenderer) -> None:
    """T-7 boundary: exactly one slot renders correctly (no off-by-one in loop).

    A renderer that accidentally skips the first or last slot when count == 1
    would produce output without the slot title, breaking this assertion.
    """
    art = ExplorationArtifact(
        version=1,
        slots={
            "only": ExplorationSlot(
                slot_id="only",
                titel="Einziger Slot",
                inhalt="Einziger Inhalt",
                completeness_status=CompletenessStatus.vollstaendig,
            ),
        },
    )
    result = renderer.render_exploration(art)

    assert "Einziger Slot" in result
    assert "Einziger Inhalt" in result
    assert "only" in result  # slot_id
    assert "vollstaendig" in result


def test_render_exploration_slot_with_empty_inhalt_no_blank_line(
    renderer: ArtifaktRenderer,
) -> None:
    """T-7: empty inhalt must NOT render a blank content value — only _(leer)_.

    This is stronger than just asserting _(leer)_ is present: we also verify
    that the raw empty string is not written as the Inhalt value, which would
    produce a misleading 'Inhalt: ' line in the Markdown.
    """
    art = ExplorationArtifact(
        version=1,
        slots={
            "s1": ExplorationSlot(
                slot_id="s1",
                titel="Leerer Slot",
                inhalt="",
                completeness_status=CompletenessStatus.leer,
            ),
        },
    )
    result = renderer.render_exploration(art)

    assert "_(leer)_" in result
    # The Inhalt line must not end with ': ' (empty value after the colon)
    assert "**Inhalt:** \n" not in result
    assert "**Inhalt:**\n" not in result


def test_render_algorithm_emma_kompatibel_false_shown(renderer: ArtifaktRenderer) -> None:
    """T-7: emma_kompatibel=False must be rendered explicitly, not omitted.

    A renderer that only renders True values would silently hide incompatible
    actions. This test verifies False appears in the output for act2.
    """
    art = AlgorithmArtifact(
        version=1,
        abschnitte={
            "a1": Algorithmusabschnitt(
                abschnitt_id="a1",
                titel="Abschnitt",
                struktur_ref="s1",
                completeness_status=CompletenessStatus.vollstaendig,
                status=AlgorithmusStatus.aktuell,
                aktionen={
                    "act1": EmmaAktion(
                        aktion_id="act1",
                        aktionstyp=EmmaAktionstyp.READ,
                        parameter={},
                        nachfolger=[],
                        emma_kompatibel=False,
                    ),
                },
            ),
        },
    )
    result = renderer.render_algorithm(art)

    assert "False" in result  # emma_kompatibel=False must appear explicitly
