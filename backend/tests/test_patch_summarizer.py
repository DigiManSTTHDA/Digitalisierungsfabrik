"""Tests für PatchSummarizer (S2-T3 / B10 — Deterministischer Summarizer)."""

from __future__ import annotations

import pytest

from artifacts.models import (
    AlgorithmusStatus,
    CompletenessStatus,
    StructureArtifact,
    Strukturschritt,
    Strukturschritttyp,
)
from core.patch_summarizer import summarize_patches


def _make_artifact() -> StructureArtifact:
    schritt = Strukturschritt(
        schritt_id="s1",
        titel="Rechnungserfassung",
        typ=Strukturschritttyp.aktion,
        reihenfolge=1,
        completeness_status=CompletenessStatus.vollstaendig,
        algorithmus_status=AlgorithmusStatus.ausstehend,
    )
    return StructureArtifact(schritte={"s1": schritt})


def test_empty_patches_returns_empty_string() -> None:
    assert summarize_patches([]) == ""


def test_add_schritt_without_artifact() -> None:
    patches = [{"op": "add", "path": "/schritte/s2", "value": {"titel": "Neue Prüfung"}}]
    result = summarize_patches(patches, None)
    assert "'Neue Prüfung' hinzugefügt" in result


def test_add_schritt_uses_value_titel() -> None:
    patches = [
        {
            "op": "add",
            "path": "/schritte/s2",
            "value": {"titel": "Sachliche Prüfung", "typ": "aktion"},
        }
    ]
    result = summarize_patches(patches)
    assert "'Sachliche Prüfung' hinzugefügt" in result


def test_remove_schritt_without_artifact_falls_back_to_id() -> None:
    patches = [{"op": "remove", "path": "/schritte/s1"}]
    result = summarize_patches(patches, None)
    assert "'s1' entfernt" in result


def test_remove_schritt_with_artifact_uses_titel() -> None:
    patches = [{"op": "remove", "path": "/schritte/s1"}]
    result = summarize_patches(patches, _make_artifact())
    assert "'Rechnungserfassung' entfernt" in result


def test_replace_titel_with_artifact() -> None:
    patches = [{"op": "replace", "path": "/schritte/s1/titel", "value": "Neuer Titel"}]
    result = summarize_patches(patches, _make_artifact())
    assert "Titel von 'Rechnungserfassung' geändert" in result


def test_replace_beschreibung_with_artifact() -> None:
    patches = [{"op": "replace", "path": "/schritte/s1/beschreibung", "value": "Neue Beschreibung"}]
    result = summarize_patches(patches, _make_artifact())
    assert "Beschreibung von 'Rechnungserfassung' aktualisiert" in result


def test_replace_nachfolger() -> None:
    patches = [{"op": "replace", "path": "/schritte/s1/nachfolger", "value": ["s2"]}]
    result = summarize_patches(patches, _make_artifact())
    assert "Reihenfolge nach 'Rechnungserfassung' angepasst" in result


def test_replace_bedingung() -> None:
    patches = [{"op": "replace", "path": "/schritte/s1/bedingung", "value": "Neue Frage?"}]
    result = summarize_patches(patches, _make_artifact())
    assert "Entscheidungsfrage bei 'Rechnungserfassung' aktualisiert" in result


def test_add_spannungsfeld() -> None:
    patches = [{"op": "add", "path": "/schritte/s1/spannungsfeld", "value": "Medienbruch"}]
    result = summarize_patches(patches, _make_artifact())
    assert "Problem bei 'Rechnungserfassung' dokumentiert" in result


def test_prozesszusammenfassung_patch() -> None:
    patches = [{"op": "replace", "path": "/prozesszusammenfassung", "value": "Zusammenfassung"}]
    result = summarize_patches(patches)
    assert "Prozesszusammenfassung aktualisiert" in result


def test_multiple_patches_joined() -> None:
    patches = [
        {"op": "add", "path": "/schritte/s2", "value": {"titel": "Neuer Schritt"}},
        {"op": "remove", "path": "/schritte/s1"},
    ]
    result = summarize_patches(patches, _make_artifact())
    assert "Ich habe folgende Änderungen vorgenommen:" in result
    assert "'Neuer Schritt' hinzugefügt" in result
    assert "'Rechnungserfassung' entfernt" in result


def test_unknown_patch_returns_generic_message() -> None:
    patches = [{"op": "replace", "path": "/unknown_field", "value": "x"}]
    result = summarize_patches(patches)
    assert result == "Änderungen vorgenommen."


def test_fallback_to_id_when_schritt_not_in_artifact() -> None:
    patches = [{"op": "remove", "path": "/schritte/s99"}]
    result = summarize_patches(patches, _make_artifact())
    assert "'s99' entfernt" in result
