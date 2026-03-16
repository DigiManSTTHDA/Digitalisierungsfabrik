"""Tests for Pydantic data models — artifacts, WorkingMemory, Project.

TDD: tests are written before (or alongside) implementation.
Each describe-block focuses on one model or concept.
"""

from datetime import UTC

import pytest
from pydantic import ValidationError

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


# ---------------------------------------------------------------------------
# Story 01-02: Artifact Pydantic models
# ---------------------------------------------------------------------------


class TestExplorationArtifact:
    def test_default_instantiation(self) -> None:
        from artifacts.models import ExplorationArtifact

        art = ExplorationArtifact()
        assert art.slots == {}
        assert art.version == 0

    def test_with_slot(self) -> None:
        from artifacts.models import CompletenessStatus, ExplorationArtifact, ExplorationSlot

        slot = ExplorationSlot(
            slot_id="s1",
            titel="Prozessname",
            completeness_status=CompletenessStatus.leer,
        )
        art = ExplorationArtifact(slots={"s1": slot})
        assert art.slots["s1"].slot_id == "s1"
        assert art.slots["s1"].inhalt == ""

    def test_json_schema_contains_slots(self) -> None:
        from artifacts.models import ExplorationArtifact

        schema = ExplorationArtifact.model_json_schema()
        assert "slots" in schema["properties"]

    def test_invalid_completeness_status_raises(self) -> None:
        from artifacts.models import ExplorationSlot

        with pytest.raises(ValidationError):
            ExplorationSlot(
                slot_id="s1",
                titel="X",
                completeness_status="ungueltig",  # type: ignore[arg-type]
            )

    def test_roundtrip_via_model_dump(self) -> None:
        from artifacts.models import CompletenessStatus, ExplorationArtifact, ExplorationSlot

        slot = ExplorationSlot(
            slot_id="s1",
            titel="Name",
            inhalt="Rechnungsverarbeitung",
            completeness_status=CompletenessStatus.vollstaendig,
        )
        art = ExplorationArtifact(slots={"s1": slot}, version=3)
        data = art.model_dump()
        art2 = ExplorationArtifact.model_validate(data)
        assert art2.slots["s1"].inhalt == "Rechnungsverarbeitung"
        assert art2.version == 3


class TestStructureArtifact:
    def test_default_instantiation(self) -> None:
        from artifacts.models import StructureArtifact

        art = StructureArtifact()
        assert art.schritte == {}
        assert art.version == 0

    def test_with_schritt(self) -> None:
        from artifacts.models import (
            AlgorithmusStatus,
            CompletenessStatus,
            StructureArtifact,
            Strukturschritt,
            Strukturschritttyp,
        )

        schritt = Strukturschritt(
            schritt_id="step_001",
            titel="Eingang prüfen",
            typ=Strukturschritttyp.aktion,
            reihenfolge=1,
            completeness_status=CompletenessStatus.leer,
            algorithmus_status=AlgorithmusStatus.ausstehend,
        )
        art = StructureArtifact(schritte={"step_001": schritt})
        assert art.schritte["step_001"].titel == "Eingang prüfen"

    def test_model_dump_contains_schritte(self) -> None:
        from artifacts.models import StructureArtifact

        data = StructureArtifact().model_dump()
        assert "schritte" in data

    def test_roundtrip_via_model_dump(self) -> None:
        from artifacts.models import (
            AlgorithmusStatus,
            CompletenessStatus,
            StructureArtifact,
            Strukturschritt,
            Strukturschritttyp,
        )

        schritt = Strukturschritt(
            schritt_id="step_001",
            titel="Validierung",
            typ=Strukturschritttyp.entscheidung,
            reihenfolge=2,
            nachfolger=["step_002"],
            completeness_status=CompletenessStatus.teilweise,
            algorithmus_status=AlgorithmusStatus.ausstehend,
            spannungsfeld="Zeitdruck vs. Qualität",
        )
        art = StructureArtifact(schritte={"step_001": schritt}, version=1)
        art2 = StructureArtifact.model_validate(art.model_dump())
        assert art2.schritte["step_001"].spannungsfeld == "Zeitdruck vs. Qualität"
        assert art2.schritte["step_001"].nachfolger == ["step_002"]

    def test_algorithmus_ref_roundtrip(self) -> None:
        """Strukturschritt.algorithmus_ref verknüpft auf Algorithmusabschnitt (FR-B-03)."""
        from artifacts.models import (
            AlgorithmusStatus,
            CompletenessStatus,
            StructureArtifact,
            Strukturschritt,
            Strukturschritttyp,
        )

        schritt = Strukturschritt(
            schritt_id="step_001",
            titel="Eingang prüfen",
            typ=Strukturschritttyp.aktion,
            reihenfolge=1,
            algorithmus_ref=["ab1", "ab2"],
            completeness_status=CompletenessStatus.leer,
            algorithmus_status=AlgorithmusStatus.ausstehend,
        )
        art = StructureArtifact(schritte={"step_001": schritt})
        art2 = StructureArtifact.model_validate(art.model_dump())
        assert art2.schritte["step_001"].algorithmus_ref == ["ab1", "ab2"]

    def test_algorithmus_ref_defaults_to_empty_list(self) -> None:
        from artifacts.models import (
            AlgorithmusStatus,
            CompletenessStatus,
            Strukturschritt,
            Strukturschritttyp,
        )

        schritt = Strukturschritt(
            schritt_id="step_001",
            titel="Eingang prüfen",
            typ=Strukturschritttyp.aktion,
            reihenfolge=1,
            completeness_status=CompletenessStatus.leer,
            algorithmus_status=AlgorithmusStatus.ausstehend,
        )
        assert schritt.algorithmus_ref == []


class TestAlgorithmArtifact:
    def test_default_instantiation(self) -> None:
        from artifacts.models import AlgorithmArtifact

        art = AlgorithmArtifact()
        assert art.abschnitte == {}
        assert art.version == 0

    def test_with_abschnitt_and_aktion(self) -> None:
        from artifacts.models import (
            AlgorithmArtifact,
            Algorithmusabschnitt,
            AlgorithmusStatus,
            CompletenessStatus,
            EmmaAktion,
            EmmaAktionstyp,
        )

        aktion = EmmaAktion(aktion_id="a1", aktionstyp=EmmaAktionstyp.READ)
        abschnitt = Algorithmusabschnitt(
            abschnitt_id="ab1",
            titel="Daten lesen",
            struktur_ref="step_001",
            aktionen={"a1": aktion},
            completeness_status=CompletenessStatus.leer,
            status=AlgorithmusStatus.ausstehend,
        )
        art = AlgorithmArtifact(abschnitte={"ab1": abschnitt})
        assert art.abschnitte["ab1"].aktionen["a1"].aktionstyp == "READ"

    def test_roundtrip_via_model_dump(self) -> None:
        from artifacts.models import (
            AlgorithmArtifact,
            Algorithmusabschnitt,
            AlgorithmusStatus,
            CompletenessStatus,
            EmmaAktion,
            EmmaAktionstyp,
        )

        aktion = EmmaAktion(
            aktion_id="a1",
            aktionstyp=EmmaAktionstyp.SEND_MAIL,
            parameter={"empfaenger": "archiv@firma.de"},
            emma_kompatibel=True,
        )
        abschnitt = Algorithmusabschnitt(
            abschnitt_id="ab1",
            titel="Benachrichtigung",
            struktur_ref="step_002",
            aktionen={"a1": aktion},
            completeness_status=CompletenessStatus.vollstaendig,
            status=AlgorithmusStatus.aktuell,
        )
        art = AlgorithmArtifact(abschnitte={"ab1": abschnitt}, version=2)
        art2 = AlgorithmArtifact.model_validate(art.model_dump())
        assert art2.abschnitte["ab1"].aktionen["a1"].emma_kompatibel is True
        assert art2.version == 2

    def test_json_schema_valid(self) -> None:
        from artifacts.models import AlgorithmArtifact

        schema = AlgorithmArtifact.model_json_schema()
        assert "abschnitte" in schema["properties"]


# ---------------------------------------------------------------------------
# Story 01-03: WorkingMemory + Project models
# ---------------------------------------------------------------------------


class TestWorkingMemory:
    def test_instantiation(self) -> None:
        from datetime import datetime

        from artifacts.models import Phasenstatus, Projektphase
        from core.working_memory import WorkingMemory

        wm = WorkingMemory(
            projekt_id="p1",
            aktive_phase=Projektphase.exploration,
            aktiver_modus="exploration",
            phasenstatus=Phasenstatus.in_progress,
            letzte_aenderung=datetime.now(tz=UTC),
        )
        assert wm.befuellte_slots == 0
        assert wm.bekannte_slots == 0
        assert wm.completeness_state == {}
        assert wm.flags == []

    def test_roundtrip_via_model_dump(self) -> None:
        from datetime import datetime

        from artifacts.models import CompletenessStatus, Phasenstatus, Projektphase
        from core.working_memory import WorkingMemory

        wm = WorkingMemory(
            projekt_id="p1",
            aktive_phase=Projektphase.strukturierung,
            aktiver_modus="structuring",
            phasenstatus=Phasenstatus.nearing_completion,
            befuellte_slots=3,
            bekannte_slots=5,
            completeness_state={"s1": CompletenessStatus.vollstaendig},
            flags=["phase_complete"],
            letzte_aenderung=datetime.now(tz=UTC),
        )
        data = wm.model_dump()
        wm2 = WorkingMemory.model_validate(data)
        assert wm2.completeness_state["s1"] == CompletenessStatus.vollstaendig
        assert "phase_complete" in wm2.flags

    def test_vorheriger_modus_roundtrip(self) -> None:
        """vorheriger_modus wird für Rückkehr nach Moderator-Unterbrechung gebraucht."""
        from datetime import datetime

        from artifacts.models import Phasenstatus, Projektphase
        from core.working_memory import WorkingMemory

        wm = WorkingMemory(
            projekt_id="p1",
            aktive_phase=Projektphase.exploration,
            aktiver_modus="moderator",
            vorheriger_modus="exploration",
            phasenstatus=Phasenstatus.in_progress,
            letzte_aenderung=datetime.now(tz=UTC),
        )
        wm2 = WorkingMemory.model_validate(wm.model_dump())
        assert wm2.vorheriger_modus == "exploration"
        assert wm2.aktiver_modus == "moderator"

    def test_spannungsfelder_and_letzter_dialogturn(self) -> None:
        """spannungsfelder und letzter_dialogturn müssen erhalten bleiben."""
        from datetime import datetime

        from artifacts.models import Phasenstatus, Projektphase
        from core.working_memory import WorkingMemory

        wm = WorkingMemory(
            projekt_id="p1",
            aktive_phase=Projektphase.exploration,
            aktiver_modus="exploration",
            phasenstatus=Phasenstatus.in_progress,
            spannungsfelder=["Zeitdruck vs. Qualität", "Kosten vs. Vollständigkeit"],
            letzter_dialogturn=7,
            letzte_aenderung=datetime.now(tz=UTC),
        )
        wm2 = WorkingMemory.model_validate(wm.model_dump())
        assert wm2.spannungsfelder == ["Zeitdruck vs. Qualität", "Kosten vs. Vollständigkeit"]
        assert wm2.letzter_dialogturn == 7


class TestProject:
    def test_json_schema_valid(self) -> None:
        from core.models import Project

        schema = Project.model_json_schema()
        assert "projekt_id" in schema["properties"]
        assert "exploration_artifact" in schema["properties"]

    def test_default_artifacts_are_empty(self) -> None:
        from datetime import datetime

        from artifacts.models import Phasenstatus, Projektphase, Projektstatus
        from core.models import Project
        from core.working_memory import WorkingMemory

        wm = WorkingMemory(
            projekt_id="p1",
            aktive_phase=Projektphase.exploration,
            aktiver_modus="exploration",
            phasenstatus=Phasenstatus.in_progress,
            letzte_aenderung=datetime.now(tz=UTC),
        )
        p = Project(
            projekt_id="p1",
            name="Testprojekt",
            erstellt_am=datetime.now(tz=UTC),
            zuletzt_geaendert=datetime.now(tz=UTC),
            aktive_phase=Projektphase.exploration,
            aktiver_modus="exploration",
            projektstatus=Projektstatus.aktiv,
            working_memory=wm,
        )
        assert p.exploration_artifact.slots == {}
        assert p.structure_artifact.schritte == {}
        assert p.algorithm_artifact.abschnitte == {}

    def test_model_dump_is_json_serialisable(self) -> None:
        import json
        from datetime import datetime

        from artifacts.models import Phasenstatus, Projektphase, Projektstatus
        from core.models import Project
        from core.working_memory import WorkingMemory

        wm = WorkingMemory(
            projekt_id="p1",
            aktive_phase=Projektphase.exploration,
            aktiver_modus="exploration",
            phasenstatus=Phasenstatus.in_progress,
            letzte_aenderung=datetime.now(tz=UTC),
        )
        p = Project(
            projekt_id="p1",
            name="JSON-Test",
            erstellt_am=datetime.now(tz=UTC),
            zuletzt_geaendert=datetime.now(tz=UTC),
            aktive_phase=Projektphase.exploration,
            aktiver_modus="exploration",
            projektstatus=Projektstatus.aktiv,
            working_memory=wm,
        )
        # model_dump(mode="json") produces JSON-safe types
        json_str = json.dumps(p.model_dump(mode="json"))
        assert "p1" in json_str


# ---------------------------------------------------------------------------
# Story 08-01: prozesszusammenfassung + template schema
# ---------------------------------------------------------------------------


class TestProzesszusammenfassung:
    """SDD 5.4: StructureArtifact must have a prozesszusammenfassung field."""

    def test_structure_artifact_prozesszusammenfassung_survives_persistence(
        self,
    ) -> None:
        """prozesszusammenfassung survives full persistence round-trip via repository."""
        from artifacts.models import StructureArtifact
        from persistence.database import Database
        from persistence.project_repository import ProjectRepository

        db = Database(":memory:")
        repo = ProjectRepository(db)
        project = repo.create("Test")
        project.structure_artifact = StructureArtifact(
            prozesszusammenfassung="Reisekostenprozess in 5 Schritten", version=1
        )
        repo.save(project)
        reloaded = repo.load(project.projekt_id)
        assert (
            reloaded.structure_artifact.prozesszusammenfassung
            == "Reisekostenprozess in 5 Schritten"
        )
        assert reloaded.structure_artifact.version == 1
        db.close()

    def test_template_allows_replace_on_prozesszusammenfassung(self) -> None:
        """STRUCTURE_TEMPLATE must accept replace on /prozesszusammenfassung."""
        from artifacts.template_schema import STRUCTURE_TEMPLATE

        assert STRUCTURE_TEMPLATE.is_valid_patch("replace", "/prozesszusammenfassung") is True

    def test_template_rejects_add_on_prozesszusammenfassung(self) -> None:
        """Only replace is allowed — add must be rejected."""
        from artifacts.template_schema import STRUCTURE_TEMPLATE

        assert STRUCTURE_TEMPLATE.is_valid_patch("add", "/prozesszusammenfassung") is False
