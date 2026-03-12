-- Digitalisierungsfabrik — SQLite Schema
-- Alle Tabellen mit IF NOT EXISTS (idempotent, safe to re-run on startup).
-- Foreign Keys werden via PRAGMA foreign_keys=ON erzwungen (in database.py).

CREATE TABLE IF NOT EXISTS projects (
    projekt_id        TEXT PRIMARY KEY,
    name              TEXT NOT NULL,
    beschreibung      TEXT NOT NULL DEFAULT '',
    erstellt_am       TEXT NOT NULL,
    zuletzt_geaendert TEXT NOT NULL,
    aktive_phase      TEXT NOT NULL,
    aktiver_modus     TEXT NOT NULL,
    projektstatus     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS artifact_versions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    projekt_id     TEXT    NOT NULL,
    typ            TEXT    NOT NULL,   -- 'exploration' | 'structure' | 'algorithm'
    version_id     INTEGER NOT NULL,
    timestamp      TEXT    NOT NULL,
    created_by     TEXT    NOT NULL,
    slot_id        TEXT,
    change_summary TEXT,
    inhalt         TEXT    NOT NULL,   -- vollständiges Artefakt als JSON-String
    FOREIGN KEY (projekt_id) REFERENCES projects(projekt_id)
);

CREATE TABLE IF NOT EXISTS working_memory (
    projekt_id TEXT PRIMARY KEY,
    inhalt     TEXT NOT NULL,          -- WorkingMemory als JSON-String
    FOREIGN KEY (projekt_id) REFERENCES projects(projekt_id)
);

CREATE TABLE IF NOT EXISTS dialog_history (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    projekt_id TEXT    NOT NULL,
    turn_id    INTEGER NOT NULL,
    role       TEXT    NOT NULL,       -- 'user' | 'assistant'
    inhalt     TEXT    NOT NULL,
    timestamp  TEXT    NOT NULL,
    FOREIGN KEY (projekt_id) REFERENCES projects(projekt_id)
);

CREATE TABLE IF NOT EXISTS validation_reports (
    projekt_id TEXT PRIMARY KEY,
    inhalt     TEXT NOT NULL,          -- JSON
    timestamp  TEXT NOT NULL,
    FOREIGN KEY (projekt_id) REFERENCES projects(projekt_id)
);
