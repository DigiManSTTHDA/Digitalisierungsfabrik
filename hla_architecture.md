# HIGH-LEVEL ARCHITECTURE — Digitalisierungsfabrik
**Version:** 0.2
**Status:** Entwurf
**Bezug:** SDD `digitalisierungsfabrik_systemdefinition.md`
**Changelog:**
- v0.2: Chainlit ersetzt durch FastAPI + React; SQLite statt JSON-Files; Dict-Keyed Artefakt-Slots; Structured-Output-Strategie (Option A) definiert

---

## Inhaltsverzeichnis

1. [Zweck dieses Dokuments](#1-zweck)
2. [Tech Stack](#2-tech-stack)
3. [Komponentenübersicht](#3-komponentenübersicht)
4. [Komponentendiagramm](#4-komponentendiagramm)
5. [Datenfluss: Orchestrator-Zyklus](#5-datenfluss-orchestrator-zyklus)
6. [Projektstruktur](#6-projektstruktur)
7. [Schließung kritischer Open Points](#7-schließung-kritischer-open-points)
8. [Implementierungsreihenfolge](#8-implementierungsreihenfolge)
9. [Offene Punkte (HLA-Ebene)](#9-offene-punkte-hla-ebene)

---

## 1. Zweck

Dieses Dokument beschreibt die High-Level-Architektur (HLA) des Digitalisierungsfabrik-Prototyps.

Es beantwortet drei Fragen:
- **Was** wird gebaut? (Komponenten und ihre Verantwortlichkeiten)
- **Womit** wird gebaut? (Tech Stack mit Begründungen)
- **Wie** ist es strukturiert? (Projektlayout, Interfaces, Datenfluss)

Es ist kein Implementierungsdesign — Prompt-Engineering, Slot-Schemas und Modus-interne Logik werden in einem separaten Implementierungsdesign-Dokument behandelt.

Die Entscheidungen in diesem Dokument sind **bindend für die Implementierung**, soweit nicht explizit als offen markiert.

---

## 2. Tech Stack

### 2.1 Übersicht

| Schicht | Komponente | Version |
|---|---|---|
| Backend-Framework | **FastAPI** | ≥ 0.111 |
| Backend-Sprache | **Python** | ≥ 3.11 |
| Datenmodelle | **Pydantic v2** | ≥ 2.6 |
| LLM-Client (Cloud) | **anthropic SDK** | ≥ 0.25 |
| JSON Patch | **jsonpatch** | ≥ 1.33 |
| Konfiguration | **pydantic-settings** | ≥ 2.2 |
| Logging | **structlog** | ≥ 24.1 |
| Persistenz | **SQLite** (stdlib `sqlite3`) | — |
| Frontend-Framework | **React** | ≥ 18 |
| Frontend-Build | **Vite** | ≥ 5 |
| Frontend-Sprache | **TypeScript** | ≥ 5 |

### 2.2 Frontend-Backend-Trennung

Das System besteht aus zwei eigenständigen Prozessen:

```
Backend  (Python / FastAPI)     →  Port 8000
Frontend (React / Vite SPA)     →  Port 5173 (dev) / statische Files (prod)
```

Die Kommunikation erfolgt über zwei Kanäle:

| Kanal | Verwendung |
|---|---|
| **REST** (`/api/...`) | Projektverwaltung, Artefakt-Download, Stateless-Operationen |
| **WebSocket** (`/ws/session/{project_id}`) | Turn-Verarbeitung, Streaming, Live-Updates |

Das Frontend hat keinen direkten Zugriff auf LLMs, Datenbank oder Systemlogik. Das Backend hat keine UI-Logik. Der Schnitt ist prozessseitig, nicht nur konventionell. Dies erfüllt die SDD-Anforderung "Frontend-Backend-Trennung" direkt (SDD 8.2).

### 2.3 Begründungen

#### FastAPI (Backend)

FastAPI ist der Standard für Python-REST-APIs mit async-Support. Relevante Eigenschaften:
- Native WebSocket-Unterstützung (für Streaming-Antworten und Live-Artefakt-Updates)
- Pydantic-Integration (Request/Response-Modelle sind dieselben Pydantic-Klassen wie im Orchestrator)
- Deterministisch testbar — jeder Endpunkt ist eine pure Funktion
- Kein UI-Coupling, keine Session-Magie

#### React + Vite (Frontend)

React gibt vollständige Layout-Kontrolle für das Split-Pane-Design des SDD (Chat links, Artefakt-Panel rechts, Debug-Panel). Die Chat-UI-Komponente ist in React ~150 Zeilen Code oder kann aus einer Bibliothek bezogen werden (`@chatscope/chat-ui-kit-react`). Streaming wird nativ via WebSocket-Events gehandhabt.

Vite liefert schnelle Hot-Module-Replacement-Entwicklungszyklen. Der Build-Output sind statische HTML/CSS/JS-Files, die vom FastAPI-Backend mitausgeliefert oder separat deployed werden können.

#### SQLite (Persistenz)

SQLite ist in Python's Stdlib (`sqlite3`), braucht keine externe Abhängigkeit und keine Serverinstallation. Entscheidend: SQLite-Transaktionen sind ACID — ein `BEGIN / COMMIT` über mehrere Tabellen-Writes ist atomar. Ein Crash mid-Transaction hinterlässt den Zustand vor dem `BEGIN`. Das erfüllt FR-E-01 direkt.

Die Alternative (JSON-Dateien) erlaubt keine atomaren Multi-File-Writes. Ein Projektzustand umfasst mehrere Dateien — `os.replace()` ist per-Datei atomar, aber nicht cross-file. JSON-Files scheiden daher aus.

#### Pydantic v2 (Datenmodelle)

Pydantic v2 ist die natürliche Implementierung der im SDD definierten Slot-Schemas mit Pflichtfeldern, Enums und Konsistenzregeln. Die Serialisierung zu JSON (für DB-Speicherung) und das Schema für die LLM-Kontextinjektion werden direkt aus den Modellen abgeleitet.

#### jsonpatch (RFC 6902)

Das SDD schreibt RFC 6902 JSON Patch für alle Artefakt-Schreiboperationen vor (SDD 5.7). Die Bibliothek `jsonpatch` ist die Standard-Python-Implementierung und wird ausschließlich intern im Executor verwendet.

#### structlog (Logging)

Das SDD fordert vollständiges Logging aller LLM-Aufrufe, Orchestrator-Entscheidungen und Schreiboperationen (SDD 8.1.3). `structlog` ermöglicht strukturiertes JSON-Logging, das direkt als Analyse-Input genutzt werden kann.

### 2.4 LLM-Flexibilität

Das SDD fordert, dass das verwendete Modell ohne Code-Änderung austauschbar ist (lokal ↔ Cloud, SDD 8.1.1). Dies wird durch ein abstraktes `LLMClient`-Interface erreicht:

```
LLMClient (abstrakt)
├── AnthropicClient    → Anthropic API (Claude)
└── OllamaClient       → Ollama (lokale Modelle)
```

Die Auswahl erfolgt ausschließlich über die Konfiguration. Kein Modus kennt den konkreten Client.

### 2.5 Structured Output Strategie (MVP)

Das LLM wird über Tool-Use zur strukturierten Ausgabe gezwungen. Jeder Modus definiert ein Tool apply_patches mit dem RFC 6902 Patch-Array als Input-Schema. Der Aufruf wird via tool_choice: {"type": "tool", "name": "apply_patches"} erzwungen.
Der OutputValidator prüft das zurückgegebene Tool-Input-Dict gegen das Patch-Schema. Da das LLM kein Freitext-JSON mehr produziert, entfällt das Parsing. Kontrakt-Verletzungen reduzieren sich auf semantische Fehler (ungültige Pfade, falsche Typen) — diese werden weiterhin vom Executor abgefangen.
Der nutzeraeusserung-Text (Chat-Antwort an den Nutzer) kommt als separates text-Block vor dem Tool-Use-Block — das Anthropic SDK liefert beides im content-Array.

---

## 3. Komponentenübersicht

Das System besteht aus acht Komponenten-Gruppen:

| Komponente | Verantwortlichkeit | SDD-Referenz |
|---|---|---|
| **Frontend (React SPA)** | Nutzerinteraktion, Darstellung, Events | Abschnitt 2 |
| **Backend-API (FastAPI)** | REST-Endpunkte, WebSocket-Session | SDD 8.2 |
| **Orchestrator** | Zentraler Steuerknoten, Zyklus-Koordination | Abschnitt 6.2, 6.3 |
| **Executor** (intern im Orchestrator) | RFC 6902 Patch-Validierung und -Ausführung | Abschnitt 5.7 |
| **Working Memory** | Operativer Zustandsspeicher | Abschnitt 6.4 |
| **Kognitive Modi** | LLM-Aufrufe, Modus-spezifische Logik | Abschnitt 6.6 |
| **Artefakt-Store** | Artefakt-Verwaltung, Versionierung, Completeness | Abschnitt 5.1–5.6 |
| **Persistenz-Schicht (SQLite)** | Projekt-Speicherung und -Wiederherstellung | Abschnitt 7.2, 7.3 |
| **LLM-Client** | Abstrakte LLM-Schnittstelle | Abschnitt 8.1.1 |

### 3.1 Frontend (React SPA)

Das Frontend ist eine React-Single-Page-Application. Es kommuniziert ausschließlich über die definierten API-Endpunkte mit dem Backend.

**Layout:**
```
┌─────────────────────────────────────────────────────┐
│  Phasen-Header: [Phase] [Fortschritt] [Buttons]      │
├─────────────────────────┬───────────────────────────┤
│  Chat-Pane              │  Artefakt-Pane             │
│  (Nachrichten-Stream,   │  (3 Tabs: Exploration /    │
│   Eingabe, Datei-Upload)│   Struktur / Algorithmus,  │
│                         │   live-updatend)            │
├─────────────────────────┴───────────────────────────┤
│  Debug-Panel (collapsible)                           │
└─────────────────────────────────────────────────────┘
```

**Komponenten:**
- `ChatPane` — Nachrichten-Liste, Streaming-Anzeige, Text-/Datei-Eingabe
- `ArtifactPane` — Tab-Ansicht der drei Artefakte, Invalidierungsmarkierungen
- `DebugPanel` — Working Memory, aktiver Modus, Flags, letzte Schreiboperation
- `PhaseHeader` — aktive Phase, Slot-Zähler, Panik-Button, Download-Button

**WebSocket-Events (Backend → Frontend):**

| Event | Payload | Auslöser |
|---|---|---|
| `chat_token` | `{token: str}` | LLM-Streaming-Token |
| `chat_done` | `{message: str}` | Turn abgeschlossen |
| `artifact_update` | `{typ, artefakt}` | Nach jeder Schreiboperation |
| `progress_update` | `{phasenstatus, befuellte_slots, bekannte_slots}` | Nach jeder Schreiboperation |
| `debug_update` | `{working_memory, flags}` | Nach jedem Zyklus |
| `error` | `{message, recoverable}` | LLM-Fehler, Kontrakt-Verletzung |

### 3.2 Backend-API (FastAPI)

**REST-Endpunkte:**

| Method | Path | Beschreibung |
|---|---|---|
| `GET` | `/api/projects` | Projektliste |
| `POST` | `/api/projects` | Neues Projekt anlegen |
| `GET` | `/api/projects/{id}` | Projektdetails laden |
| `GET` | `/api/projects/{id}/artifacts` | Alle drei Artefakte (aktuell) |
| `GET` | `/api/projects/{id}/artifacts/{typ}/versions` | Versionshistorie |
| `POST` | `/api/projects/{id}/artifacts/{typ}/restore` | Version wiederherstellen |
| `GET` | `/api/projects/{id}/download` | Download (JSON + Markdown) |
| `POST` | `/api/projects/{id}/import` | Artefakt importieren |
| `POST` | `/api/projects/{id}/complete` | Projekt abschließen |

**WebSocket:**

| Path | Beschreibung |
|---|---|
| `/ws/session/{project_id}` | Bidirektionaler Kanal für Turn-Verarbeitung |

WebSocket-Messages vom Frontend:

| Event | Payload |
|---|---|
| `turn` | `{text: str, file?: base64}` |
| `panic` | `{}` |

### 3.3 Orchestrator

**Typ:** Reiner Python-Code, kein LLM-Aufruf.

**Verantwortlichkeiten** (gemäß SDD 6.3 — 11-Schritt-Zyklus):
- Empfang des Nutzer-Inputs
- Auswertung von Steuerungsflags aus dem vorherigen Turn
- Entscheidung über den aktiven Modus
- Context-Assembly für den LLM-Aufruf
- Aufruf des aktiven Modus
- Validierung des LLM-Outputs (OutputValidator)
- Beauftragung des Executors mit Schreiboperationen
- Auslösung von Invalidierungen
- Aktualisierung von Working Memory und Completeness-State
- Persistierung nach jedem abgeschlossenen Zyklus

**Schnittstelle:**
```python
async def process_turn(project_id: str, input: TurnInput) -> TurnOutput
```

Der Orchestrator kennt weder FastAPI noch WebSocket-Details. Die Backend-API-Schicht ist verantwortlich für das Mapping zwischen WebSocket-Events und `process_turn`-Aufrufen, sowie für das Streamen der Rückgabe an den Client.

### 3.4 Executor (intern)

Internes Modul des Orchestrators. Nach außen nicht sichtbar (SDD 5.7).

**Pipeline (sequenziell, bei Fehler → Rollback auf Snapshot):**

| Schritt | Aktion |
|---|---|
| 1 | Formale RFC 6902 Validierung |
| 2 | Pfad-Prüfung gegen Template-Schema |
| 3 | Atomarer Snapshot (aktueller Artefaktzustand) |
| 4 | Patch-Anwendung via `jsonpatch` |
| 5 | Preservation-Check (nur adressierte Pfade geändert) |
| 6 | Invalidierungs-Check (Strukturschritt geändert → alle `algorithmus_ref` → `invalidiert`) |
| 7 | Versionserzeugung im Artefakt-Store |

### 3.5 Kognitive Modi

Jeder Modus erbt von einer gemeinsamen Basisklasse.

```python
class BaseMode:
    async def call(self, context: ModeContext) -> ModeOutput: ...

@dataclass
class ModeOutput:
    nutzeraeusserung: str
    patches: list[dict]          # RFC 6902, kann leer sein
    phasenstatus: Phasenstatus   # in_progress / nearing_completion / phase_complete
    flags: list[Flag]            # s. SDD 6.4.1
```

| Modus | Klasse | Artefakt (Patches auf) |
|---|---|---|
| Exploration | `ExplorationMode` | Explorationsartefakt |
| Strukturierung | `StructuringMode` | Strukturartefakt |
| Spezifikation | `SpecificationMode` | Algorithmusartefakt |
| Validierung | `ValidationMode` | keines (gibt Validierungsbericht aus) |
| Moderator | `Moderator` | keines |

Kein Modus schreibt direkt in Artefakte oder Working Memory.

### 3.6 Artefakt-Store

**Artefakt-Slot-Modell: Dict-Keyed (nicht Listen)**

Alle Collections innerhalb der Artefakte sind als ID-keyede Dicts implementiert:

```python
class Strukturartefakt(BaseModel):
    schritte: dict[str, Strukturschritt]   # key = schritt_id

class Algorithmusartefakt(BaseModel):
    abschnitte: dict[str, Algorithmusabschnitt]  # key = abschnitt_id
```

Dies ist eine fundamentale Designentscheidung: RFC 6902 Patch-Pfade auf Dict-Elemente sind stabil (`/schritte/step_003/beschreibung`). Pfade auf Listen-Elemente wären numerische Indizes (`/schritte/2`), die bei Einfüge- und Löschoperationen instabil werden und silente Schreibfehler auf falsche Slots ermöglichen. Die Reihenfolge der Schritte wird durch das `reihenfolge`-Feld im Strukturschritt codiert, nicht durch die Collection-Reihenfolge.

**Verantwortlichkeiten:**
- Verwaltung aller drei Artefakte in ihrer aktuellen Version
- Versionierung: jede Schreiboperation → neue Version in SQLite
- Completeness-Berechnung: aggregierte Map `slot_id → Status`
- Markdown-Rendering: JSON-Artefakt → menschenlesbare Darstellung (für Download)

### 3.7 Persistenz-Schicht (SQLite)

**Schema (vereinfacht):**

```sql
CREATE TABLE projects (
    projekt_id   TEXT PRIMARY KEY,
    name         TEXT NOT NULL,
    beschreibung TEXT,
    erstellt_am  TEXT NOT NULL,
    zuletzt_geaendert TEXT NOT NULL,
    aktive_phase TEXT NOT NULL,
    aktiver_modus TEXT NOT NULL,
    projektstatus TEXT NOT NULL
);

CREATE TABLE artifact_versions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    projekt_id   TEXT NOT NULL,
    typ          TEXT NOT NULL,   -- 'exploration' | 'structure' | 'algorithm'
    version_id   INTEGER NOT NULL,
    timestamp    TEXT NOT NULL,
    created_by   TEXT NOT NULL,
    slot_id      TEXT,
    change_summary TEXT,
    inhalt       TEXT NOT NULL,   -- vollständiges Artefakt als JSON
    FOREIGN KEY (projekt_id) REFERENCES projects(projekt_id)
);

CREATE TABLE working_memory (
    projekt_id   TEXT PRIMARY KEY,
    inhalt       TEXT NOT NULL    -- JSON
);

CREATE TABLE dialog_history (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    projekt_id   TEXT NOT NULL,
    turn_id      INTEGER NOT NULL,
    role         TEXT NOT NULL,   -- 'user' | 'assistant'
    inhalt       TEXT NOT NULL,
    timestamp    TEXT NOT NULL
);

CREATE TABLE validation_reports (
    projekt_id   TEXT PRIMARY KEY,
    inhalt       TEXT NOT NULL,   -- JSON
    timestamp    TEXT NOT NULL
);
```

**Atomarität:** Jeder Projektzustand-Write läuft in einer einzigen SQLite-Transaktion:

```python
with db.transaction():
    db.update_project_metadata(...)
    db.insert_artifact_version(...)
    db.update_working_memory(...)
    db.append_dialog_history(...)
```

Ein Crash mid-Transaction hinterlässt exakt den Zustand vor dem `BEGIN`. Kein partieller Zustand möglich (FR-E-01).

### 3.8 LLM-Client

```python
class LLMClient(ABC):
    async def complete(
        self,
        system: str,
        messages: list[Message],
        **kwargs
    ) -> str: ...

    async def stream(
        self,
        system: str,
        messages: list[Message],
        **kwargs
    ) -> AsyncIterator[str]: ...

    async def complete(
        self,
        system: str,
        messages: list[Message],
        tools: list[dict] | None = None,
        tool_choice: dict | None = None,
        **kwargs
    ) -> str: ...
```

Implementierungen: `AnthropicClient`, `OllamaClient`. Auswahl über Konfiguration.

---

## 4. Komponentendiagramm

```
┌──────────────────────────────────────────────────────────────────────┐
│  FRONTEND (React SPA)                            Port 5173 / static  │
│                                                                       │
│  ┌────────────┐  ┌──────────────┐  ┌───────────┐  ┌──────────────┐  │
│  │  ChatPane   │  │ ArtifactPane │  │ DebugPanel│  │  PhaseHeader │  │
│  │  (Stream,   │  │ (3 Tabs,     │  │ (WM, Flags│  │  (Phase,     │  │
│  │   Upload)   │  │  live update)│  │  Ops)     │  │   Slots,     │  │
│  │             │  │              │  │           │  │   Panic, DL) │  │
│  └──────┬──────┘  └──────┬───────┘  └─────┬────┘  └──────┬───────┘  │
└─────────┼────────────────┼────────────────┼───────────────┼──────────┘
          │ WebSocket /ws/session/{id}       │               │ REST /api
          │ ←─────────────────────────────────────────────── │
          ▼                                                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│  BACKEND (FastAPI)                                       Port 8000   │
│                                                                       │
│  ┌─────────────────────────┐   ┌───────────────────────────────────┐ │
│  │ WebSocketHandler         │   │ REST Router                       │ │
│  │ - empfängt turn/panic    │   │ /api/projects, /artifacts, ...    │ │
│  │ - streamt Events zurück  │   └───────────────────────────────────┘ │
│  └───────────┬─────────────┘                                         │
└──────────────┼───────────────────────────────────────────────────────┘
               │ orchestrator.process_turn(input)
               ▼
┌──────────────────────────────────────────────────────────────────────┐
│  ORCHESTRATOR                                                         │
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌────────────────────┐  │
│  │ ZyklusKoordinator│  │ ContextAssembler  │  │ OutputValidator    │  │
│  │ (11 Schritte)    │  │ (SDD 6.5)         │  │ (Output-Kontrakt)  │  │
│  └────────┬─────────┘  └──────────────────┘  └────────────────────┘  │
│           │                                                            │
│  ┌────────▼──────────────────────────────────────────────────────┐    │
│  │ EXECUTOR (intern)                                              │    │
│  │  Validate → Snapshot → Apply → PreservationCheck →            │    │
│  │  Invalidation → Versioning          (SDD 5.7)                 │    │
│  └────────────────────────────────────────────────────────────────┘   │
└──────────┬─────────────────────────────────────────────────────────────┘
           │ mode.call(context)
           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  KOGNITIVE MODI                                                       │
│                                                                       │
│  ExplorationMode │ StructuringMode │ SpecificationMode │ Moderator   │
│  ValidationMode                                                       │
│                                                                       │
│  call(context: ModeContext) → ModeOutput(text, patches, flags)       │
└──────────────────────────────┬───────────────────────────────────────┘
                               │ LLMClient.complete(system, messages)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│  LLM-CLIENT                                                          │
│  AnthropicClient  │  OllamaClient                                    │
└─────────────────────────────────────────────────────────────────────┘

   Orchestrator liest/schreibt:
   ┌────────────────┐   ┌──────────────────┐   ┌──────────────────────┐
   │ Working Memory │   │  Artefakt-Store   │   │  SQLite              │
   │ (Laufzeit-     │   │  (3 Artefakte,    │   │  (ACID-Transaktionen,│
   │  Zustand)      │   │   dict-keyed,     │   │   vollständiger      │
   │                │   │   Versionen,      │   │   Projektzustand)    │
   │                │   │   Completeness)   │   │                      │
   └────────────────┘   └──────────────────┘   └──────────────────────┘
```

---

## 5. Datenfluss: Orchestrator-Zyklus

Ein vollständiger Turn, entsprechend SDD Abschnitt 6.3:

```
WebSocket-Event 'turn' vom Frontend
    │
    ▼
WebSocketHandler.handle_turn(project_id, input)
    │
    ▼
[1] Orchestrator.process_turn(input)
    │
    ▼
[2] WorkingMemory.update(input)
    │
    ▼
[3] Flags aus letztem Turn auswerten
    ├── phase_complete → Moderator aktivieren (nach Turn)
    ├── escalate / blocked → Moderator aktivieren
    └── → Modus bleibt aktiv
    │
    ▼
[4] Aktiven Modus bestimmen (Moduswechsel-Logik)
    │
    ▼
[5] ContextAssembler.build(modus, artefakte, working_memory, history)
    → Systemprompt + Template-Schema + Artefakte (RO) + Completeness +
      Working-Memory-Auszug + Dialoghistorie (N Turns) +
      ggf. Moderator-Kontext / Validierungsbericht / EMMA-Katalog
    │
    ▼
[6] modus.call(context)
    └── LLMClient.complete(system, messages) → LLM-Antwort
        └── Jedes streaming token → WebSocket Event 'chat_token' an Frontend
    │
    ▼
[7] OutputValidator.validate(llm_output)
    ├── OK → weiter
    └── Verletzung → WebSocket Event 'error' an Frontend,
                     Turn abgebrochen, kein Zustandsänderung
    │
    ▼
[8] Executor.apply_patches(patches)  [wenn patches nicht leer]
    ├── RFC 6902 syntaktisch valide? Pfade im Schema?
    ├── Snapshot des aktuellen Artefakts
    ├── jsonpatch.apply_patch(artefakt, patches)
    ├── Preservation-Check
    ├── Invalidierungs-Check (Strukturschritt geändert → referenzierte Algo-Abschnitte → invalidiert)
    ├── Neue Artefaktversion erzeugen
    └── WebSocket Event 'artifact_update' an Frontend
    │
    ▼
[9] CompletenessCalculator.recalculate(artefakte)
    → WorkingMemory.completeness_state aktualisieren
    │
    ▼
[10] ProgressTracker.update(phasenstatus, slot_counts)
     → WorkingMemory.phasenstatus, befuellte_slots, bekannte_slots
     └── WebSocket Event 'progress_update' an Frontend
    │
    ▼
[11] ProjectRepository.save(projekt)  [SQLite-Transaktion, atomar]
    │
    ▼
WebSocket Event 'chat_done' + 'debug_update' an Frontend
```

---

## 6. Projektstruktur

```
digitalisierungsfabrik/
│
├── backend/
│   ├── main.py                         # FastAPI-App, Startup
│   ├── config.py                       # Konfiguration (pydantic-settings)
│   ├── .env.example
│   ├── requirements.txt
│   │
│   ├── api/
│   │   ├── router.py                   # REST-Endpunkte
│   │   └── websocket.py                # WebSocket-Handler
│   │
│   ├── core/
│   │   ├── orchestrator.py             # Orchestrator-Zyklus (SDD 6.3)
│   │   ├── context_assembler.py        # Kontext-Zusammenstellung (SDD 6.5)
│   │   ├── output_validator.py         # Output-Kontrakt-Prüfung (SDD 6.5.2)
│   │   ├── executor.py                 # RFC 6902 Executor (SDD 5.7)
│   │   ├── working_memory.py           # Working-Memory-Datenmodell (SDD 6.4)
│   │   └── progress_tracker.py        # Phasenstatus + Slot-Zähler (SDD 6.7)
│   │
│   ├── modes/
│   │   ├── base.py                     # Abstrakte Basis + ModeContext/ModeOutput
│   │   ├── exploration.py              # Explorationsmodus (SDD 6.6.1)
│   │   ├── structuring.py              # Strukturierungsmodus (SDD 6.6.2)
│   │   ├── specification.py            # Spezifikationsmodus (SDD 6.6.3)
│   │   ├── validation.py               # Validierungsmodus (SDD 6.6.4)
│   │   └── moderator.py                # Moderator (SDD 6.6.5)
│   │
│   ├── artifacts/
│   │   ├── models.py                   # Pydantic-Modelle (dict-keyed Collections)
│   │   ├── store.py                    # Artefakt-Store + Versionierung
│   │   ├── template_schema.py          # Template-Schema (aus models.py abgeleitet)
│   │   ├── completeness.py             # Completeness-State-Berechnung (SDD 5.6)
│   │   └── renderer.py                 # JSON → Markdown (für Download, OP-19)
│   │
│   ├── persistence/
│   │   ├── database.py                 # SQLite-Verbindung + Transaktions-Helper
│   │   ├── project_repository.py       # Projekt CRUD (atomar via Transaktion)
│   │   └── schema.sql                  # DDL (CREATE TABLE statements)
│   │
│   ├── llm/
│   │   ├── base.py                     # Abstraktes LLMClient-Interface
│   │   ├── anthropic_client.py         # Anthropic Claude
│   │   └── ollama_client.py            # Ollama
│   │
│   ├── prompts/                        # Systemprompts der Modi (Markdown)
│   │   ├── exploration.md
│   │   ├── structuring.md
│   │   ├── specification.md
│   │   ├── validation.md
│   │   └── moderator.md
│   │
│   ├── static/
│   │   └── emma_catalog.json           # EMMA-Aktionskatalog (SDD 8.3)
│   │
│   └── tests/
│       ├── test_executor.py
│       ├── test_artifacts.py
│       ├── test_orchestrator.py
│       ├── test_completeness.py
│       └── test_persistence.py
│
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    │
    └── src/
        ├── main.tsx                    # React-Einstiegspunkt
        ├── App.tsx                     # Root-Layout (Split-Pane)
        ├── api/
        │   ├── rest.ts                 # REST-Client (fetch-Wrapper)
        │   └── websocket.ts            # WebSocket-Client + Event-Handling
        ├── components/
        │   ├── ChatPane.tsx
        │   ├── ArtifactPane.tsx
        │   ├── ArtifactTab.tsx         # Einzelne Artefakt-Ansicht
        │   ├── DebugPanel.tsx
        │   └── PhaseHeader.tsx
        ├── store/
        │   └── session.ts              # React-State (Zustand/Context)
        └── types/
            └── api.ts                  # TypeScript-Typen (gespiegelt von Pydantic)
```

### Konfiguration (`.env`)

Alle systemrelevanten Parameter sind konfigurierbar (SDD 8.1.1):

| Parameter | Beschreibung | Standard |
|---|---|---|
| `LLM_PROVIDER` | `anthropic` / `ollama` | `anthropic` |
| `LLM_MODEL` | Modell-ID | `claude-opus-4-6` |
| `LLM_API_KEY` | API-Key (nie im Frontend) | — |
| `OLLAMA_BASE_URL` | URL für Ollama | `http://localhost:11434` |
| `DIALOG_HISTORY_N` | Turns für Modi | `3` |
| `DIALOG_HISTORY_MODERATOR_M` | Turns für Moderator (M > N) | `10` |
| `TOKEN_WARN_THRESHOLD` | Token-Warnschwelle | `80000` |
| `TOKEN_HARD_LIMIT` | Hartes Tokenlimit | `100000` |
| `AUTOMATION_WARN_THRESHOLD` | Schwelle nicht-automatisierbarer Schritte | `1` |
| `DATABASE_PATH` | Pfad zur SQLite-Datei | `./data/digitalisierungsfabrik.db` |
| `LOG_LEVEL` | Log-Level | `INFO` |
| `LLM_LOG_ENABLED` | LLM I/O-Logging | `true` |

---

## 7. Schließung kritischer Open Points

### OP-01: JSON-Schema Artefakte

Die formale Schemadefinition aller drei Artefakte wird durch **Pydantic-v2-Modelle** in `artifacts/models.py` implementiert. Collections sind durchgängig als Dicts mit stabiler ID als Key modelliert.

**RFC 6902 Pfad-Konventionen (dict-keyed):**
```
# Exploration
/slots/{slot_id}/inhalt
/slots/{slot_id}/completeness_status

# Struktur (dict-keyed by schritt_id)
/schritte/{schritt_id}/beschreibung
/schritte/{schritt_id}/completeness_status
/schritte/{schritt_id}/algorithmus_status

# Algorithmus (dict-keyed by abschnitt_id)
/abschnitte/{abschnitt_id}/aktionen
/abschnitte/{abschnitt_id}/completeness_status
/abschnitte/{abschnitt_id}/status
```

Alle Pfade sind stabil durch Einfüge- und Löschoperationen. Numerische Indizes werden nirgendwo als Pfadsegmente verwendet.

### OP-10: Persistenztechnologie

**Entscheidung:** SQLite mit ACID-Transaktionen.

Begründung: ein Projektzustand umfasst mehrere logische Einheiten (Metadaten, Working Memory, Artefaktversion, Dialoghistorie). SQLite-Transaktionen garantieren atomare Multi-Entity-Writes. FR-E-01 ist direkt erfüllt.

### OP-19: Markdown-Renderlogik

Renderer in `artifacts/renderer.py`:

**Strukturartefakt → Markdown:**
```
## {reihenfolge}. {titel}  [TYP: {typ}] [{completeness_status}]
{beschreibung}
Nachfolger: {nachfolger_liste}
⚠️ INVALIDIERT       ← wenn algorithmus_status = invalidiert
🔴 Spannungsfeld: … ← wenn gesetzt
```

**Algorithmusartefakt → Markdown:**
```
## {titel}  [{status}] [{completeness_status}]
Bezug: Strukturschritt {struktur_ref}

| Aktion-ID | Typ | Parameter | Nachfolger | EMMA-OK |
...
```

### OP-16: Erfolgs-/Fehlerkanten im Kontrollflussgraph

Für den Prototyp: Fehlerbehandlung als explizite `DECISION`-Knoten modelliert. Kein neues Schema-Feld nötig. Post-Prototyp: optionale `success_edge`/`error_edge`-Felder als rückwärtskompatible Erweiterung.

---

## 8. Implementierungsreihenfolge

Jeder Schritt ist ein eigenständig testbares Inkrement.

| Schritt | Inhalt | Testbar wenn |
|---|---|---|
| 1 | Pydantic-Modelle + SQLite-Schema + ProjectRepository | Projekt anlegen, speichern, laden |
| 2 | Executor + Template-Schema | Patch anwenden, Fehler → Rollback |
| 3 | Orchestrator-Skeleton + Working Memory (stub-Modi) | Zyklus läuft, WM aktualisiert, Persistenz |
| 4 | LLM-Client + Explorationsmodus + ContextAssembler + OutputValidator | Erster LLM-Turn vollständig |
| 5 | FastAPI-Backend (REST + WebSocket) | API-Endpunkte testbar ohne Frontend |
| 6 | React-Frontend | Vollständiger Nutzerdialog im Browser |
| 7 | Moderator + Phasenwechsel | Phasenwechsel-Zyklus vollständig |
| 8 | Strukturierungsmodus | |
| 9 | Spezifikationsmodus | |
| 10 | Validierungsmodus + Korrekturschleife | |
| 11 | End-to-End-Durchlauf + Stabilisierung | Vollständiger Prozess Exploration → Validierung |

---

## 9. Offene Punkte (HLA-Ebene)

| ID | Thema | Auswirkung |
|---|---|---|
| OP-02 | EMMA-Parameterdefinition | `EmmaAktion.parameter: dict[str, Any]` im Prototyp — vollständige Definition wenn EMMA-Spezifikation vorliegt |
| OP-03 | Versionshistorie im UI | Liste oder Diff-Ansicht? Im Frontend-Design (Schritt 6) klären |
| OP-04 | Maximale Versionszahl | Prototyp: unbegrenzt. Ggf. konfigurierbares Limit post-Prototyp |
| OP-05 | Token-Schwellenwerte | Konfigurierbare Platzhalter. Nach erstem Testlauf kalibrieren |
| OP-06 | nearing_completion-Kriterien | Pro Modus im Implementierungsdesign |
| OP-07 | Steuerungsflags vollständig | Basis-Flags definiert (SDD 6.4.1), Vervollständigung im Implementierungsdesign |
| OP-11 | Dialoghistorie-Umfang | Prototyp: vollständig in SQLite. Größe nach Testläufen abschätzen |
| OP-12 | Projektliste im UI | Frontend-Komponente in Schritt 6 |
| OP-14 | LLM-Log-Format | `logs`-Tabelle in SQLite: `timestamp, modus, turn_id, input_tokens, output_tokens, input_json, output_json` |
| OP-17 | Eventlog-Format | Prototyp: Upload als Freitext, kein strukturiertes Parsing |
| OP-20 | Wiederholte Output-Kontrakt-Verletzung | Prototyp: Fehlermeldung + Retry durch Nutzer. Post-Prototyp: konfigurierbares Retry-Limit + Moderator-Eskalation |

---

*Dokument-Ende. Nächstes Dokument: Implementierungsdesign Schritt 1 — Datenmodelle & SQLite-Schema.*
