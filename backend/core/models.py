"""Domain root model — Project aggregates all sub-models.

Project is the persistence unit: one save() call writes all of its
fields atomically to SQLite via ProjectRepository.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from artifacts.models import (
    AlgorithmArtifact,
    ExplorationArtifact,
    Projektphase,
    Projektstatus,
    StructureArtifact,
)
from core.working_memory import WorkingMemory


class Project(BaseModel):
    """Root-Aggregat — repräsentiert ein vollständiges Digitalisierungsprojekt."""

    projekt_id: str
    name: str
    beschreibung: str = ""
    erstellt_am: datetime
    zuletzt_geaendert: datetime
    aktive_phase: Projektphase
    aktiver_modus: str
    projektstatus: Projektstatus
    exploration_artifact: ExplorationArtifact = Field(default_factory=ExplorationArtifact)
    structure_artifact: StructureArtifact = Field(default_factory=StructureArtifact)
    algorithm_artifact: AlgorithmArtifact = Field(default_factory=AlgorithmArtifact)
    working_memory: WorkingMemory
