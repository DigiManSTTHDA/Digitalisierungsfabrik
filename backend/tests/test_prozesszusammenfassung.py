"""Tests for prozesszusammenfassung field on StructureArtifact.

Story 08-01: prozesszusammenfassung + template schema.
"""

from artifacts.models import StructureArtifact
from persistence.database import Database
from persistence.project_repository import ProjectRepository

# ---------------------------------------------------------------------------
# Story 08-01: prozesszusammenfassung + template schema
# ---------------------------------------------------------------------------


class TestProzesszusammenfassung:
    """SDD 5.4: StructureArtifact must have a prozesszusammenfassung field."""

    def test_structure_artifact_prozesszusammenfassung_survives_persistence(
        self,
    ) -> None:
        """prozesszusammenfassung survives full persistence round-trip via repository."""
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
