# Epic 01 – Data Models & Persistence

## Summary

Define every Pydantic v2 model that the system will use (artifacts, working memory, project
state) and implement the SQLite persistence layer via `ProjectRepository`. This gives all
future components a stable, typed data contract and a reliable way to save and restore state.

This epic corresponds to **Implementation Step 1** in `AGENTS.md` / `hla_architecture.md`.

## Goal

A fully-typed data layer: Pydantic models for all three artifact types and for working memory,
backed by a SQLite schema with ACID transactions and a `ProjectRepository` that can create,
save, load, and list projects.

## Testable Increment

- A Python test (or short script) can:
  1. Create a new project via `ProjectRepository`
  2. Save it to SQLite
  3. Reload it from SQLite
  4. Assert that all fields round-trip correctly (including nested artifact schemas)
- `pytest backend/tests/test_repository.py` → all tests pass
- No LLM calls or HTTP server required

## Dependencies

- Epic 00 (project skeleton with working test runner)

## Key Deliverables

- `backend/core/models.py` – Pydantic v2 models for:
  - `ExplorationArtifact`
  - `StructureArtifact`
  - `AlgorithmArtifact`
  - `WorkingMemory`
  - `Project`
- `backend/core/schema.sql` (or inline in repository) – SQLite DDL
- `backend/core/repository.py` – `ProjectRepository` with create / save / load / list
- `backend/tests/test_models.py` – model validation tests
- `backend/tests/test_repository.py` – persistence round-trip tests (in-memory SQLite)

## OpenAPI Contract Note

The Pydantic models defined in this epic (`ExplorationArtifact`, `StructureArtifact`,
`AlgorithmArtifact`, `WorkingMemory`, `Project`) form the **domain model** that the API
layer (Epic 05) will reference. Design them for clean JSON serialisation:

- Use explicit field types (no `Any`, no bare `dict` without type parameters where avoidable).
- All models must pass `model.model_json_schema()` without errors — FastAPI uses this to
  build the OpenAPI spec.
- These models are **not** the API schemas (those live in `backend/api/schemas.py`); they
  are the internal domain types. The API schemas in Epic 05 will compose or reference them.

## Status

**Implementiert** — 2026-03-12 · 49/49 Tests grün · 5 Commits

| Story | Status | Commit |
|---|---|---|
| 01-01 Enums | ✅ done | `9247328` |
| 01-02 Artifact models | ✅ done | `9247328` |
| 01-03 WorkingMemory + Project | ✅ done | `e8f8a1e` |
| 01-04 SQLite schema + Database | ✅ done | `09edf8a` |
| 01-05 ProjectRepository | ✅ done | `16981ba` |
| 01-06 Tests | ✅ done | `16981ba` |

## Stories

### Story 01-01 – Gemeinsame Enums und Basis-Typen definieren

**Als** Entwickler (oder AI-Agent)
**möchte ich** alle gemeinsam genutzten Enums und einfachen Hilfstypen in einer zentralen Datei,
**damit** Artefakt-Modelle, Working-Memory und Repository auf denselben Typen aufbauen und
Inkonsistenzen durch doppelte Definitionen ausgeschlossen sind.

**Akzeptanzkriterien:**

- `backend/artifacts/models.py` wird angelegt und enthält mindestens folgende Enums:
  - `CompletenessStatus` — Werte: `leer`, `teilweise`, `vollstaendig`
  - `AlgorithmusStatus` — Werte: `ausstehend`, `in_bearbeitung`, `abgeschlossen`, `invalidiert`
  - `Phasenstatus` — Werte: `in_progress`, `nearing_completion`, `phase_complete`
  - `Projektphase` — Werte: `exploration`, `strukturierung`, `spezifikation`, `validierung`, `abgeschlossen`
  - `Projektstatus` — Werte: `aktiv`, `abgeschlossen`, `archiviert`
- Alle Enums sind `str`-basiert (`class Foo(str, Enum)`) für saubere JSON-Serialisierung
- `python -c "from artifacts.models import CompletenessStatus; print(CompletenessStatus.vollstaendig)"` läuft fehlerfrei
- `mypy backend/artifacts/models.py` → 0 Fehler (strict mode)
- `ruff check backend/artifacts/models.py` → 0 Fehler

**Definition of Done:**

- [ ] `backend/artifacts/__init__.py` (leer) ist vorhanden
- [ ] `backend/artifacts/models.py` enthält alle oben gelisteten Enums
- [ ] Enums sind mit `model_json_schema`-kompatiblen Typen annotiert
- [ ] `mypy` und `ruff` laufen grün

---

### Story 01-02 – Pydantic-Modelle für alle drei Artefakte implementieren

**Als** Entwickler (oder AI-Agent)
**möchte ich** vollständig typisierte Pydantic-v2-Modelle für `ExplorationArtifact`,
`StructureArtifact` und `AlgorithmArtifact`,
**damit** alle späteren Komponenten (Executor, Modi, API) gegen einen stabilen, validierten
Datenvertrag arbeiten.

**Akzeptanzkriterien:**

- In `backend/artifacts/models.py` sind folgende Modelle definiert:

  **`ExplorationSlot`** (Untermodell):
  - `slot_id: str`
  - `bezeichnung: str`
  - `inhalt: str` (Standardwert `""`)
  - `completeness_status: CompletenessStatus`

  **`ExplorationArtifact`**:
  - `slots: dict[str, ExplorationSlot]` — Key = `slot_id`
  - `version: int` (Standardwert `0`)

  **`Strukturschritt`** (Untermodell):
  - `schritt_id: str`
  - `titel: str`
  - `typ: str` — z. B. `"ACTIVITY"`, `"DECISION"`, `"EVENT"`
  - `beschreibung: str` (Standardwert `""`)
  - `reihenfolge: int`
  - `nachfolger: list[str]` (Standardwert `[]`)
  - `completeness_status: CompletenessStatus`
  - `algorithmus_status: AlgorithmusStatus`
  - `spannungsfeld: str | None` (Standardwert `None`)

  **`StructureArtifact`**:
  - `schritte: dict[str, Strukturschritt]` — Key = `schritt_id`
  - `version: int` (Standardwert `0`)

  **`EmmaAktion`** (Untermodell):
  - `aktion_id: str`
  - `typ: str`
  - `parameter: dict[str, str]` (Standardwert `{}`)
  - `nachfolger: list[str]` (Standardwert `[]`)
  - `emma_ok: bool` (Standardwert `False`)

  **`Algorithmusabschnitt`** (Untermodell):
  - `abschnitt_id: str`
  - `titel: str`
  - `struktur_ref: str` — Referenz auf `schritt_id`
  - `aktionen: dict[str, EmmaAktion]` — Key = `aktion_id`
  - `completeness_status: CompletenessStatus`
  - `status: AlgorithmusStatus`

  **`AlgorithmArtifact`**:
  - `abschnitte: dict[str, Algorithmusabschnitt]` — Key = `abschnitt_id`
  - `version: int` (Standardwert `0`)

- Alle Collections sind als `dict[str, <Untermodell>]` mit stabilen String-Keys modelliert
  (keine numerisch-indexierten Listen für addressierbare Elemente — siehe HLA OP-01)
- Jedes Modell besteht `model.model_json_schema()` ohne Fehler
- `ExplorationArtifact()`, `StructureArtifact()`, `AlgorithmArtifact()` sind mit reinen
  Defaultwerten instanziierbar (leere Artefakte für neue Projekte)

**Definition of Done:**

- [ ] Alle drei Artefakt-Modelle + Untermodelle in `backend/artifacts/models.py`
- [ ] `model_json_schema()` für alle drei Hauptmodelle liefert valides JSON-Schema
- [ ] `mypy backend/artifacts/models.py` → 0 Fehler
- [ ] `ruff check backend/artifacts/models.py` → 0 Fehler

---

### Story 01-03 – Pydantic-Modelle für WorkingMemory und Project definieren

**Als** Entwickler (oder AI-Agent)
**möchte ich** typisierte Modelle für `WorkingMemory` und `Project`,
**damit** der Orchestrator einen klar strukturierten Laufzeit-Zustand hat und der
`ProjectRepository` einen vollständigen Projekt-Graphen speichern und laden kann.

**Akzeptanzkriterien:**

- `backend/core/working_memory.py` enthält das Modell **`WorkingMemory`**:
  - `projekt_id: str`
  - `aktive_phase: Projektphase`
  - `aktiver_modus: str` — z. B. `"exploration"`, `"moderator"`
  - `phasenstatus: Phasenstatus`
  - `befuellte_slots: int` (Standardwert `0`)
  - `bekannte_slots: int` (Standardwert `0`)
  - `completeness_state: dict[str, CompletenessStatus]` (Standardwert `{}`) —
    Map `slot_id → status`
  - `flags: list[str]` (Standardwert `[]`) — aktive Steuerungsflags
  - `letzte_aenderung: datetime`

- `backend/core/models.py` enthält das Modell **`Project`**:
  - `projekt_id: str`
  - `name: str`
  - `beschreibung: str` (Standardwert `""`)
  - `erstellt_am: datetime`
  - `zuletzt_geaendert: datetime`
  - `aktive_phase: Projektphase`
  - `aktiver_modus: str`
  - `projektstatus: Projektstatus`
  - `exploration_artifact: ExplorationArtifact` (Standardwert = leeres Artefakt)
  - `structure_artifact: StructureArtifact` (Standardwert = leeres Artefakt)
  - `algorithm_artifact: AlgorithmArtifact` (Standardwert = leeres Artefakt)
  - `working_memory: WorkingMemory`

- `backend/core/__init__.py` (leer) ist vorhanden
- `Project.model_json_schema()` liefert valides JSON-Schema (keine Fehler)
- `Project` ist mit Minimal-Parametern (`projekt_id`, `name`, `working_memory`) instanziierbar —
  alle anderen Felder haben Defaults

**Definition of Done:**

- [ ] `backend/core/working_memory.py` mit `WorkingMemory`-Modell
- [ ] `backend/core/models.py` mit `Project`-Modell
- [ ] Beide Module bestehen `mypy` und `ruff` ohne Fehler
- [ ] `Project(projekt_id="x", name="Test", working_memory=...).model_dump()` serialisiert
      vollständig zu einem JSON-kompatiblen Dict

---

### Story 01-04 – SQLite-Schema und Datenbankverbindung implementieren

**Als** Entwickler (oder AI-Agent)
**möchte ich** ein deklaratives SQL-Schema und einen Datenbank-Verbindungs-Helper mit
Transaktions-Unterstützung,
**damit** der `ProjectRepository` auf ACID-gesicherten SQLite-Transaktionen aufbauen kann.

**Akzeptanzkriterien:**

- `backend/persistence/__init__.py` (leer) ist vorhanden
- `backend/persistence/schema.sql` enthält `CREATE TABLE IF NOT EXISTS`-Statements für
  alle fünf Tabellen (exakt wie in HLA Section 3.7 spezifiziert):
  - `projects` — Projektmetadaten
  - `artifact_versions` — versionierte Artefakt-Snapshots als JSON
  - `working_memory` — aktueller WM-Zustand als JSON
  - `dialog_history` — Turn-Einträge
  - `validation_reports` — Validierungsergebnisse als JSON
- Alle `FOREIGN KEY`-Constraints sind vorhanden und korrekt
- `backend/persistence/database.py` enthält die Klasse `Database`:
  - `__init__(self, db_path: str)` — öffnet/erstellt die SQLite-Datei,
    führt `schema.sql` aus (idempotent via `IF NOT EXISTS`)
  - `get_connection(self) -> sqlite3.Connection`
  - Kontextmanager `transaction(self)` — führt `BEGIN / COMMIT` durch,
    bei Exception `ROLLBACK`; stellt sicher, dass kein partieller Zustand möglich ist
  - `close(self) -> None`
- `Database(":memory:")` ist mit In-Memory-SQLite verwendbar (für Tests)
- WAL-Modus ist aktiviert (`PRAGMA journal_mode=WAL`)
- Foreign-Key-Enforcement ist aktiviert (`PRAGMA foreign_keys=ON`)

**Definition of Done:**

- [ ] `backend/persistence/schema.sql` mit allen 5 Tabellen
- [ ] `backend/persistence/database.py` mit `Database`-Klasse + `transaction()`-Kontextmanager
- [ ] `Database(":memory:")` instanziierbar ohne Fehler
- [ ] `mypy backend/persistence/database.py` → 0 Fehler
- [ ] `ruff check backend/persistence/` → 0 Fehler

---

### Story 01-05 – ProjectRepository implementieren

**Als** Entwickler (oder AI-Agent)
**möchte ich** einen `ProjectRepository` mit den Operationen `create`, `save`, `load` und `list`,
**damit** der Orchestrator Projekte vollständig und atomar in SQLite speichern und
wiederherstellen kann.

**Akzeptanzkriterien:**

- `backend/persistence/project_repository.py` enthält die Klasse `ProjectRepository`:

  **`create(self, name: str, beschreibung: str = "") -> Project`**
  - Erstellt ein neues `Project`-Objekt mit generierter `projekt_id` (UUID4), initialen
    leeren Artefakten und einer neuen `WorkingMemory`
  - Speichert das Projekt sofort in SQLite (erste `save`-Operation)
  - Gibt das gespeicherte `Project`-Objekt zurück

  **`save(self, project: Project) -> None`**
  - Schreibt den vollständigen Projektzustand in einer einzigen SQLite-Transaktion:
    1. `projects`-Zeile anlegen oder aktualisieren (Metadaten)
    2. Neue Zeile in `artifact_versions` für jedes geänderte Artefakt
       (Typ, Version, Timestamp, Inhalt als JSON-String)
    3. `working_memory`-Zeile anlegen oder ersetzen
  - Bei Fehler: vollständiger `ROLLBACK`, `Project`-Objekt bleibt unverändert
  - Aktualisiert `project.zuletzt_geaendert` auf den Zeitpunkt des Saves

  **`load(self, projekt_id: str) -> Project`**
  - Liest Metadaten aus `projects`, aktuellste Artefakt-Version je Typ aus
    `artifact_versions` (höchste `version_id` je `typ`), Working Memory aus
    `working_memory`
  - Deserialisiert JSON-Strings zurück in die entsprechenden Pydantic-Modelle
    (`model_validate_json` / `model_validate`)
  - Wirft `ValueError` wenn `projekt_id` nicht existiert

  **`list_projects(self) -> list[Project]`**
  - Gibt alle Projekte als Liste zurück (Metadaten + aktuellste Artefakte)
  - Leere Liste wenn keine Projekte vorhanden

- Alle vier Methoden laufen in `Database.transaction()` (atomar)
- `mypy backend/persistence/project_repository.py` → 0 Fehler
- `ruff check backend/persistence/project_repository.py` → 0 Fehler

**Definition of Done:**

- [ ] `ProjectRepository.create()`, `save()`, `load()`, `list_projects()` implementiert
- [ ] Keine direkte SQL-String-Konkatenation mit User-Input (SQL-Injection-sicher via
      parametrisierte Queries mit `?`-Platzhaltern)
- [ ] `mypy` und `ruff` laufen grün
- [ ] Wird von den Tests in Story 01-06 vollständig abgedeckt

---

### Story 01-06 – Modell-Validierungs- und Persistenz-Tests implementieren

**Als** Entwickler (oder AI-Agent)
**möchte ich** eine vollständige Test-Suite für Modelle und Repository,
**damit** der Datenvertrag und die SQLite-Persistenz dauerhaft verifiziert sind und
Regressionen sofort auffallen.

**Akzeptanzkriterien:**

**`backend/tests/test_models.py` — Modell-Validierungstests:**

- Test: `ExplorationArtifact()`, `StructureArtifact()`, `AlgorithmArtifact()` sind mit
  leeren Defaults instanziierbar
- Test: Ungültiger `CompletenessStatus`-Wert (`"ungueltig"`) wirft `ValidationError`
- Test: `ExplorationArtifact.model_json_schema()` enthält den Key `"slots"`
- Test: `StructureArtifact` mit einem `Strukturschritt` ist korrekt serialisierbar
  (`model_dump()` enthält `"schritte"`)
- Test: `AlgorithmArtifact` mit einem `Algorithmusabschnitt` und einer `EmmaAktion`
  round-tripped korrekt via `model_dump()` → `model_validate()`
- Test: `Project.model_json_schema()` liefert valides Schema (kein Exception)

**`backend/tests/test_repository.py` — Persistenz-Tests (In-Memory-SQLite):**

- Fixture: `repo` — `ProjectRepository` mit `Database(":memory:")`
- Test: `create()` gibt ein `Project`-Objekt mit gesetzter `projekt_id` zurück
- Test: `create()` → `load()` — alle Felder stimmen überein (Metadaten, leere Artefakte,
  `working_memory.aktive_phase`)
- Test: `save()` nach Modifikation eines Artefakt-Slots → `load()` enthält die Änderung
  (vollständiger Round-Trip mit befülltem `ExplorationSlot`)
- Test: `save()` mit modifiziertem `StructureArtifact` (ein `Strukturschritt`) → `load()`
  liefert denselben Schritt mit identischem `schritt_id` und `beschreibung`
- Test: `list_projects()` auf leerer DB → `[]`
- Test: Zwei `create()`-Aufrufe → `list_projects()` gibt Liste mit Länge 2 zurück
- Test: `load()` mit unbekannter `projekt_id` → wirft `ValueError`

- `cd backend && pytest tests/test_models.py tests/test_repository.py` → alle Tests grün
- Kein LLM-Aufruf, kein HTTP-Server, keine Datei-I/O nötig

**Definition of Done:**

- [ ] `backend/tests/test_models.py` mit ≥ 6 Testfällen, alle grün
- [ ] `backend/tests/test_repository.py` mit ≥ 8 Testfällen, alle grün
- [ ] `pytest --tb=short -q` zeigt 0 Fehler, 0 blockierende Warnings
- [ ] `mypy tests/test_models.py tests/test_repository.py` → 0 Fehler
