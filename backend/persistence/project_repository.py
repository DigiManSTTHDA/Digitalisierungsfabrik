"""ProjectRepository — CRUD operations for Project aggregates.

All writes are atomic: one save() call runs inside a single SQLite transaction.
A crash or error mid-transaction leaves the database in the state before BEGIN.
This fulfils FR-E-01 (no partial state).

SQL uses parameterised queries exclusively — no string concatenation with
user-supplied data (prevents SQL injection).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from artifacts.models import (
    AlgorithmArtifact,
    ExplorationArtifact,
    Phasenstatus,
    Projektphase,
    Projektstatus,
    StructureArtifact,
)
from core.models import Project
from core.working_memory import WorkingMemory
from persistence.database import Database


class ProjectRepository:
    """Manages persistence of Project aggregates to SQLite."""

    def __init__(self, db: Database) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create(self, name: str, beschreibung: str = "") -> Project:
        """Create a new project with empty artifacts and persist it immediately."""
        now = datetime.now(tz=timezone.utc)
        projekt_id = str(uuid.uuid4())

        wm = WorkingMemory(
            projekt_id=projekt_id,
            aktive_phase=Projektphase.exploration,
            aktiver_modus="exploration",
            phasenstatus=Phasenstatus.in_progress,
            letzte_aenderung=now,
        )
        project = Project(
            projekt_id=projekt_id,
            name=name,
            beschreibung=beschreibung,
            erstellt_am=now,
            zuletzt_geaendert=now,
            aktive_phase=Projektphase.exploration,
            aktiver_modus="exploration",
            projektstatus=Projektstatus.aktiv,
            working_memory=wm,
        )
        self.save(project)
        return project

    def save(self, project: Project) -> None:
        """Persist the full project state atomically.

        Updates project.zuletzt_geaendert to the current timestamp.
        """
        now = datetime.now(tz=timezone.utc)
        project.zuletzt_geaendert = now
        project.working_memory.letzte_aenderung = now

        with self._db.transaction() as conn:
            # 1. Upsert project metadata
            conn.execute(
                """INSERT INTO projects
                       (projekt_id, name, beschreibung, erstellt_am, zuletzt_geaendert,
                        aktive_phase, aktiver_modus, projektstatus)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                   ON CONFLICT(projekt_id) DO UPDATE SET
                       name              = excluded.name,
                       beschreibung      = excluded.beschreibung,
                       zuletzt_geaendert = excluded.zuletzt_geaendert,
                       aktive_phase      = excluded.aktive_phase,
                       aktiver_modus     = excluded.aktiver_modus,
                       projektstatus     = excluded.projektstatus
                """,
                (
                    project.projekt_id,
                    project.name,
                    project.beschreibung,
                    project.erstellt_am.isoformat(),
                    now.isoformat(),
                    project.aktive_phase.value,
                    project.aktiver_modus,
                    project.projektstatus.value,
                ),
            )

            # 2. Insert new artifact versions
            ts = now.isoformat()
            for typ, artifact in (
                ("exploration", project.exploration_artifact),
                ("structure", project.structure_artifact),
                ("algorithm", project.algorithm_artifact),
            ):
                conn.execute(
                    """INSERT INTO artifact_versions
                           (projekt_id, typ, version_id, timestamp, created_by, inhalt)
                       VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        project.projekt_id,
                        typ,
                        artifact.version,
                        ts,
                        "system",
                        artifact.model_dump_json(),
                    ),
                )

            # 3. Upsert working memory
            conn.execute(
                """INSERT INTO working_memory (projekt_id, inhalt)
                   VALUES (?, ?)
                   ON CONFLICT(projekt_id) DO UPDATE SET inhalt = excluded.inhalt
                """,
                (project.projekt_id, project.working_memory.model_dump_json()),
            )

    def load(self, projekt_id: str) -> Project:
        """Load a project by ID. Raises ValueError if not found."""
        conn = self._db.get_connection()

        row = conn.execute(
            "SELECT * FROM projects WHERE projekt_id = ?", (projekt_id,)
        ).fetchone()
        if row is None:
            raise ValueError(f"Projekt '{projekt_id}' nicht gefunden")

        exploration = self._load_latest_artifact(conn, projekt_id, "exploration", ExplorationArtifact)
        structure = self._load_latest_artifact(conn, projekt_id, "structure", StructureArtifact)
        algorithm = self._load_latest_artifact(conn, projekt_id, "algorithm", AlgorithmArtifact)
        wm = self._load_working_memory(conn, projekt_id)

        return Project(
            projekt_id=row["projekt_id"],
            name=row["name"],
            beschreibung=row["beschreibung"],
            erstellt_am=datetime.fromisoformat(row["erstellt_am"]),
            zuletzt_geaendert=datetime.fromisoformat(row["zuletzt_geaendert"]),
            aktive_phase=Projektphase(row["aktive_phase"]),
            aktiver_modus=row["aktiver_modus"],
            projektstatus=Projektstatus(row["projektstatus"]),
            exploration_artifact=exploration,
            structure_artifact=structure,
            algorithm_artifact=algorithm,
            working_memory=wm,
        )

    def list_projects(self) -> list[Project]:
        """Return all projects with their latest artifact versions."""
        conn = self._db.get_connection()
        rows = conn.execute(
            "SELECT projekt_id FROM projects ORDER BY zuletzt_geaendert DESC"
        ).fetchall()
        return [self.load(row["projekt_id"]) for row in rows]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _load_latest_artifact(
        self,
        conn,  # type: ignore[no-untyped-def]
        projekt_id: str,
        typ: str,
        model_class: type,
    ) -> object:
        row = conn.execute(
            """SELECT inhalt FROM artifact_versions
               WHERE projekt_id = ? AND typ = ?
               ORDER BY version_id DESC, id DESC
               LIMIT 1
            """,
            (projekt_id, typ),
        ).fetchone()
        if row is None:
            return model_class()
        return model_class.model_validate_json(row["inhalt"])

    def _load_working_memory(self, conn, projekt_id: str) -> WorkingMemory:  # type: ignore[no-untyped-def]
        row = conn.execute(
            "SELECT inhalt FROM working_memory WHERE projekt_id = ?", (projekt_id,)
        ).fetchone()
        if row is None:
            raise ValueError(f"WorkingMemory für '{projekt_id}' nicht gefunden")
        return WorkingMemory.model_validate_json(row["inhalt"])
