"""Tests for WorkingMemory and Project core models.

Story 01-03: WorkingMemory + Project models.
"""

import json
from datetime import UTC, datetime

from artifacts.models import (
    CompletenessStatus,
    Phasenstatus,
    Projektphase,
    Projektstatus,
)
from core.models import Project
from core.working_memory import WorkingMemory

# ---------------------------------------------------------------------------
# Story 01-03: WorkingMemory + Project models
# ---------------------------------------------------------------------------


class TestWorkingMemory:
    def test_instantiation(self) -> None:
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
        schema = Project.model_json_schema()
        assert "projekt_id" in schema["properties"]
        assert "exploration_artifact" in schema["properties"]

    def test_default_artifacts_are_empty(self) -> None:
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
