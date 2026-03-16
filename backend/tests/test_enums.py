"""Tests for Pydantic enum models.

Story 01-01: Enums — CompletenessStatus, AlgorithmusStatus, Phasenstatus,
Projektphase, Projektstatus.
"""

import pytest


# ---------------------------------------------------------------------------
# Story 01-01: Enums
# ---------------------------------------------------------------------------


class TestCompletenessStatus:
    def test_values_exist(self) -> None:
        from artifacts.models import CompletenessStatus

        assert CompletenessStatus.leer == "leer"
        assert CompletenessStatus.teilweise == "teilweise"
        assert CompletenessStatus.vollstaendig == "vollstaendig"
        assert CompletenessStatus.nutzervalidiert == "nutzervalidiert"

    def test_nutzervalidiert_accepted_in_slot(self) -> None:
        """nutzervalidiert muss als Slot-Status akzeptiert werden (FR-C-07)."""
        from artifacts.models import CompletenessStatus, ExplorationSlot

        slot = ExplorationSlot(
            slot_id="s1",
            titel="Validierter Slot",
            inhalt="Bestätigt",
            completeness_status=CompletenessStatus.nutzervalidiert,
        )
        assert slot.completeness_status == CompletenessStatus.nutzervalidiert

    def test_invalid_value_raises(self) -> None:
        from artifacts.models import CompletenessStatus

        with pytest.raises(ValueError):
            CompletenessStatus("ungueltig")


class TestAlgorithmusStatus:
    def test_values_exist(self) -> None:
        from artifacts.models import AlgorithmusStatus

        assert AlgorithmusStatus.ausstehend == "ausstehend"
        assert AlgorithmusStatus.aktuell == "aktuell"
        assert AlgorithmusStatus.invalidiert == "invalidiert"

    def test_invalid_value_raises(self) -> None:
        from artifacts.models import AlgorithmusStatus

        with pytest.raises(ValueError):
            AlgorithmusStatus("unbekannt")


class TestPhasenstatus:
    def test_values_exist(self) -> None:
        from artifacts.models import Phasenstatus

        assert Phasenstatus.in_progress == "in_progress"
        assert Phasenstatus.nearing_completion == "nearing_completion"
        assert Phasenstatus.phase_complete == "phase_complete"

    def test_invalid_value_raises(self) -> None:
        from artifacts.models import Phasenstatus

        with pytest.raises(ValueError):
            Phasenstatus("fertig")


class TestProjektphase:
    def test_values_exist(self) -> None:
        from artifacts.models import Projektphase

        assert Projektphase.exploration == "exploration"
        assert Projektphase.strukturierung == "strukturierung"
        assert Projektphase.spezifikation == "spezifikation"
        assert Projektphase.validierung == "validierung"
        assert Projektphase.abgeschlossen == "abgeschlossen"

    def test_invalid_value_raises(self) -> None:
        from artifacts.models import Projektphase

        with pytest.raises(ValueError):
            Projektphase("unbekannte_phase")


class TestProjektstatus:
    def test_values_exist(self) -> None:
        from artifacts.models import Projektstatus

        assert Projektstatus.aktiv == "aktiv"
        assert Projektstatus.pausiert == "pausiert"
        assert Projektstatus.abgeschlossen == "abgeschlossen"

    def test_invalid_value_raises(self) -> None:
        from artifacts.models import Projektstatus

        with pytest.raises(ValueError):
            Projektstatus("geloescht")
