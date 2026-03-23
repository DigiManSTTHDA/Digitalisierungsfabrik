"""Tests for Pydantic artifact models — ExplorationArtifact, StructureArtifact,
and the non-persistence parts of AlgorithmArtifact.

Story 01-02: Artifact Pydantic models.
"""

import pytest
from pydantic import ValidationError

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

    # --- CR-002: Kontrollfluss-Felder ---

    def test_entscheidungsregel_model(self) -> None:
        """Entscheidungsregel model stores bedingung, nachfolger, bezeichnung."""
        from artifacts.models import Entscheidungsregel

        regel = Entscheidungsregel(bedingung="Betrag > 500€", nachfolger="s3")
        assert regel.bedingung == "Betrag > 500€"
        assert regel.nachfolger == "s3"
        assert regel.bezeichnung == ""

    def test_entscheidungsregel_with_bezeichnung(self) -> None:
        from artifacts.models import Entscheidungsregel

        regel = Entscheidungsregel(bedingung="Intern", nachfolger="s4", bezeichnung="Interne Reise")
        assert regel.bezeichnung == "Interne Reise"

    def test_new_fields_default_empty(self) -> None:
        """CR-002 fields default to empty — backward compatible."""
        from artifacts.models import (
            AlgorithmusStatus,
            CompletenessStatus,
            Strukturschritt,
            Strukturschritttyp,
        )

        schritt = Strukturschritt(
            schritt_id="s1",
            titel="Test",
            typ=Strukturschritttyp.aktion,
            reihenfolge=1,
            completeness_status=CompletenessStatus.leer,
            algorithmus_status=AlgorithmusStatus.ausstehend,
        )
        assert schritt.regeln == []
        assert schritt.schleifenkoerper == []
        assert schritt.abbruchbedingung is None
        assert schritt.konvergenz is None

    def test_roundtrip_with_regeln(self) -> None:
        """Strukturschritt with regeln survives model_dump → model_validate."""
        from artifacts.models import (
            AlgorithmusStatus,
            CompletenessStatus,
            Entscheidungsregel,
            StructureArtifact,
            Strukturschritt,
            Strukturschritttyp,
        )

        schritt = Strukturschritt(
            schritt_id="s5",
            titel="Entscheidung",
            typ=Strukturschritttyp.entscheidung,
            reihenfolge=5,
            regeln=[
                Entscheidungsregel(bedingung="Betrag > 500€", nachfolger="s6"),
                Entscheidungsregel(bedingung="Betrag <= 500€", nachfolger="s7"),
            ],
            konvergenz="s8",
            completeness_status=CompletenessStatus.teilweise,
            algorithmus_status=AlgorithmusStatus.ausstehend,
        )
        art = StructureArtifact(schritte={"s5": schritt})
        art2 = StructureArtifact.model_validate(art.model_dump())
        assert len(art2.schritte["s5"].regeln) == 2
        assert art2.schritte["s5"].regeln[0].nachfolger == "s6"
        assert art2.schritte["s5"].konvergenz == "s8"

    def test_roundtrip_with_schleifenkoerper(self) -> None:
        """Strukturschritt with schleifenkoerper survives roundtrip."""
        from artifacts.models import (
            AlgorithmusStatus,
            CompletenessStatus,
            StructureArtifact,
            Strukturschritt,
            Strukturschritttyp,
        )

        schritt = Strukturschritt(
            schritt_id="s3",
            titel="Wiederholung",
            typ=Strukturschritttyp.schleife,
            reihenfolge=3,
            schleifenkoerper=["s4", "s5"],
            abbruchbedingung="Alle Belege geprüft",
            completeness_status=CompletenessStatus.teilweise,
            algorithmus_status=AlgorithmusStatus.ausstehend,
        )
        art = StructureArtifact(schritte={"s3": schritt})
        art2 = StructureArtifact.model_validate(art.model_dump())
        assert art2.schritte["s3"].schleifenkoerper == ["s4", "s5"]
        assert art2.schritte["s3"].abbruchbedingung == "Alle Belege geprüft"


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

    # --- Story 09-02: Algorithm Artifact Schema Tests ---

    def test_invalid_aktionstyp_rejected(self) -> None:
        """Invalid aktionstyp string must be rejected by Pydantic (Rule T-2)."""
        from artifacts.models import EmmaAktion

        with pytest.raises(ValidationError, match="aktionstyp"):
            EmmaAktion(
                aktion_id="a1",
                aktionstyp="INVALID_ACTION",  # type: ignore[arg-type]
            )

    def test_emma_aktionstyp_has_exactly_18_members(self) -> None:
        """EmmaAktionstyp must have exactly 18 members matching SDD 8.3."""
        from artifacts.models import EmmaAktionstyp

        expected = {
            "FIND",
            "FIND_AND_CLICK",
            "CLICK",
            "DRAG",
            "SCROLL",
            "TYPE",
            "READ",
            "READ_FORM",
            "GENAI",
            "EXPORT",
            "IMPORT",
            "FILE_OPERATION",
            "SEND_MAIL",
            "COMMAND",
            "LOOP",
            "DECISION",
            "WAIT",
            "SUCCESS",
        }
        actual = {m.value for m in EmmaAktionstyp}
        assert actual == expected, f"Mismatch: {actual.symmetric_difference(expected)}"

    def test_algorithm_template_prozesszusammenfassung_replace(self) -> None:
        """ALGORITHM_TEMPLATE must accept replace on /prozesszusammenfassung."""
        from artifacts.template_schema import ALGORITHM_TEMPLATE

        assert ALGORITHM_TEMPLATE.is_valid_patch("replace", "/prozesszusammenfassung") is True
        assert ALGORITHM_TEMPLATE.is_valid_patch("add", "/prozesszusammenfassung") is False
