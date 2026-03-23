# Digitalisierungsfabrik — Prototyp

AI-geführtes System zur Prozesserhebung für Digitalisierungsprojekte.

**Status:** Epics 00–11 abgeschlossen + Change Requests CR-001 bis CR-006 verifiziert — Prototyp vollständig.

---

## Schnellstart

Voraussetzungen: Python ≥ 3.11, Node.js ≥ 18, npm ≥ 9.

```bash
# 1. Backend einrichten
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env             # .env öffnen und LLM_API_KEY eintragen

# 2. Backend starten
uvicorn main:app --reload        # Port 8000

# 3. Frontend einrichten (zweites Terminal)
cd frontend
npm install
npm run generate-api:file        # OpenAPI-Typen generieren

# 4. Frontend starten
npm run dev                      # Port 5173
```

Öffne http://localhost:5173 im Browser. Das Backend ist unter http://localhost:8000 erreichbar.
Konfiguration: alle Parameter sind in `backend/.env.example` beschrieben.

---

## Benutzerhandbuch

Das System führt durch fünf Schritte:

1. **Projekt anlegen** — Auf der Startseite "Neues Projekt" ausfüllen und "Projekt erstellen" klicken. Das Projekt erscheint in der Liste. Klick öffnet die Gesprächsansicht.

2. **Exploration** — Das System fragt nach dem Prozessauslöser, Ziel, Beschreibung, Beteiligten usw. Die Antworten werden im Explorationsartefakt (rechte Seite) gespeichert. Wenn alle Pflichtfelder gefüllt sind, schlägt der Moderator den Wechsel zur nächsten Phase vor.

3. **Strukturierung** — Beim ersten Eintritt in diese Phase führt das System im Hintergrund eine automatische Initialisierung durch (ohne sichtbaren Dialog): Es baut das Strukturartefakt vollständig aus dem Explorationsartefakt auf, validiert es deterministisch und prüft per LLM ob wesentliche Entitäten fehlen. Eventuelle Qualitätshinweise werden in den Dialog injiziert. Danach startet der interaktive Dialog: Das System präsentiert den entworfenen Prozess und nimmt Korrekturen entgegen. Nach Bestätigung erfolgt der Phasenwechsel.

4. **Spezifikation** — Analoger Ablauf: Hintergrund-Initialisierung des Algorithmusartefakts aus dem Strukturartefakt, dann interaktiver Dialog zur EMMA-Aktionssequenzierung.

5. **Validierung** — Das System prüft die Artefakte auf Konsistenz und Vollständigkeit. Bei bestandener Validierung erscheint der Status "Projekt abgeschlossen" in der Kopfzeile.

**Exportieren:** Nach Abschluss der Validierung im Artefaktbereich (rechts) auf "Exportieren" klicken. Es werden zwei Dateien heruntergeladen:
- `artifacts.json` — alle drei Artefakte als JSON-Bundle
- `artifacts.md` — lesbare Markdown-Darstellung aller Artefakte

---

## Übersicht

Das System führt Nutzer durch einen strukturierten Dialog und erzeugt dabei drei
miteinander verknüpfte Artefakte:

1. **Explorationsartefakt** — beschreibt den Ist-Prozess in Prosaform (Auslöser, Ziel, Beteiligte, Variablen, Ausnahmen usw.)
2. **Strukturartefakt** — gliedert den Prozess in nummerierte Prozessschritte mit Kontrollfluss (Entscheidungen, Schleifen, Ausnahmen)
3. **Algorithmusartefakt** — spezifiziert jeden Schritt als EMMA-Aktionssequenz (RPA-ready)

**Spezifikationen:**
- System-/Anforderungsdokumentation: `docs/digitalisierungsfabrik_systemdefinition.md`
- Architektur: `docs/hla_architecture.md`
- Agenten-Regeln: `AGENTS.md`

---

## Orchestrator & Modi

### Überblick

Der Orchestrator ist der zentrale Steuerknoten. Er verarbeitet jeden Nutzerturn in einem festen **11-Schritt-Zyklus** und ist die einzige Komponente, die Modi aktiviert, Artefakt-Patches via Executor schreibt und den Systemzustand persistiert.

```
Nutzerturn
    │
    ▼
[1] Projekt laden
[2] Turn-Zähler erhöhen
[3] Flags aus letztem Turn auswerten
[4] Aktiven Modus bestimmen
[5] Nutzerturn vorab persistieren + Kontext zusammenstellen
[6] Modus aufrufen  →  LLM-Call (oder deterministischer Code)
[7] Patches anwenden (RFC 6902) — mit Retry-Logik bei ungültigen Pfaden
[8] Invalidierungen auslösen (Struktur → Algorithmus)
[9] Completeness-State neu berechnen
[10] Working Memory aktualisieren + Moduswechsel prüfen
[10b] Background-Init ausführen (nur beim Erstbetreten von Structuring/Specification)
[11] Zustand persistieren
```

### Kognitive Modi

Das System kennt acht Modi, von denen immer genau einer aktiv ist. Modi schreiben nie direkt in Artefakte oder Working Memory — sie liefern ausschließlich `(nutzeraeusserung, patches, phasenstatus, flags)` zurück.

#### Dialog-Modi (sichtbar für den Nutzer)

| Modus | Klasse | Artefakt | Wann aktiv |
|---|---|---|---|
| **Exploration** | `ExplorationMode` | Explorationsartefakt | Standardmodus der Explorationsphase |
| **Structuring** | `StructuringMode` | Strukturartefakt | Nach erfolgreicher Background-Init in der Strukturierungsphase |
| **Specification** | `SpecificationMode` | Algorithmusartefakt | Nach erfolgreicher Background-Init in der Spezifikationsphase |
| **Validation** | `ValidationMode` | — (gibt Validierungsbericht aus) | Validierungsphase |
| **Moderator** | `Moderator` | — | Bei `phase_complete`, `escalate` oder `blocked`-Flag; führt Phasenwechsel durch |

#### Moduswechsel-Logik

```
phase_complete ─┐
escalate        ├──▶  Moderator aktivieren
blocked         ┘

Moderator → advance_phase ──▶  Phase erhöhen + return_to_mode
Moderator → return_to_mode ──▶  Primärmodus der neuen Phase aktivieren
                                 ↓ (falls Artefakt leer)
                                 Background-Init vor Modus-Aktivierung
```

#### Background-Init-Modi (unsichtbar, kein Nutzer-Dialog)

Diese Modi werden ausschließlich vom Orchestrator intern aufgerufen — nie direkt vom Nutzer. Ihre `nutzeraeusserung` wird nicht an den Client gesendet.

| Modus | Klasse | Zweck |
|---|---|---|
| **Init-Structuring** | `InitStructuringMode` | Transformiert Explorationsartefakt vollständig in Strukturartefakt (Prozessschritte, Kontrollfluss, Variablen-Lineage, ANALOG-Kennzeichnung) |
| **Init-Specification** | `InitSpecificationMode` | Transformiert Strukturartefakt vollständig in Algorithmusartefakt (EMMA-Skelett, WAIT-Aktionen für ANALOG-Schritte) |
| **Init-Coverage-Validator** | `InitCoverageValidatorMode` | Prüft einmalig ob Entitäten aus dem Explorationsartefakt (Variablen, Beteiligte, Ausnahmen) in den nachgelagerten Artefakten abgebildet sind; gibt ausschließlich Warnungen zurück (nie kritische Befunde) |

### Background-Initialisierung (Detail)

Beim erstmaligen Betreten der Strukturierungs- oder Spezifikationsphase (erkennbar daran, dass das Zielartefakt leer ist) führt der Orchestrator vor dem Dialog-Einstieg folgenden 5-stufigen Prozess aus:

```
Phase 1 — Init-Loop (max. 8 LLM-Turns)
    InitStructuringMode oder InitSpecificationMode aufrufen
    Patches anwenden bis init_status = "init_complete" oder Limit erreicht

Phase 2 — Python-Validator (deterministisch, kein LLM)
    6 Regeln werden geprüft:
    R-1  Referenzielle Integrität  — alle nachfolger/regeln/schleifenkoerper/konvergenz-Referenzen gültig
    R-2  Feldvollständigkeit       — titel/beschreibung/bedingung/ausnahme_beschreibung nicht leer
    R-3  Graph-Konsistenz          — genau 1 Startschritt, mindestens 1 Endschritt
    R-4  Variablen-Crosscheck      — alle Variablen aus Exploration tauchen in Strukturbeschreibungen auf
    R-5  Abschnitt-Mapping         — jeder Strukturschritt hat einen Algorithmusabschnitt
    R-6  ANALOG-Konsistenz         — ANALOG-Schritte haben emma_kompatibel=false-Aktion

Phase 3 — LLM Coverage-Validator (einmalig)
    InitCoverageValidatorMode prüft ob Entitäten aus Exploration fehlen
    Gibt reines JSON zurück (fehlende_entitaeten, coverage_vollstaendig)
    Severity: immer "warnung", nie "kritisch"

Phase 4 — Korrektur-Turns (max. 2, nur bei kritischen Befunden aus Phase 2)
    Init-Modus erneut aufrufen mit error_hint (Violation-Liste)
    Nach jedem Korrektur-Turn re-validieren

Phase 5 — Warnungen speichern
    Alle Warnungen → wm.init_hinweise (list[str])
    Werden beim ersten Dialog-Turn in den System-Prompt des Structurer/Specifier injiziert
```

Der gesamte Prozess läuft transparent im Hintergrund. Der Nutzer sieht nichts davon — er erhält direkt das bereits befüllte Artefakt zur Überprüfung und Korrektur.

### Steuerungsflags

Modi setzen Flags in ihrem Output. Der Orchestrator wertet diese nach jedem Turn aus:

| Flag | Gesetzt von | Bedeutung |
|---|---|---|
| `phase_complete` | Dialog-Modus | Phase abgeschlossen — Moderator übernimmt |
| `escalate` | beliebiger Modus | Systemfehler — Moderator übernimmt |
| `blocked` | Dialog-Modus | Nutzer feststeckend — Moderator übernimmt |
| `advance_phase` | Moderator | Phase erhöhen (Exploration→Structuring→…) |
| `return_to_mode` | Moderator | Zurück zum Primärmodus (ggf. mit Background-Init) |
| `artefakt_updated` | Dialog-Modus | Artefakt wurde modifiziert |
| `validation_failed` | Validierung | Validierung nicht bestanden |
| `needs_clarification` | Dialog-Modus | Nutzerinput fehlt |

---

## Voraussetzungen

| Tool | Version |
|---|---|
| Python | ≥ 3.11 |
| Node.js | ≥ 18 |
| npm | ≥ 9 |

---

## Setup & Start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Konfiguration
cp .env.example .env
# .env bearbeiten: LLM_API_KEY setzen

# Tests ausführen
pytest

# Server starten (Port 8000)
uvicorn main:app --reload
```

Läuft der Server, ist die API-Dokumentation unter http://localhost:8000/docs erreichbar.

### Frontend

```bash
cd frontend
npm install

# TypeScript-Typen aus der OpenAPI-Spezifikation generieren
# (verwendet api-contract/openapi.json — kein laufendes Backend nötig)
npm run generate-api:file

# Dev-Server starten (Port 5173)
npm run dev
```

> **Hinweis:** Sobald das Backend unter Port 8000 läuft, können die Typen auch direkt
> vom Backend generiert werden: `npm run generate-api`

### Linter & Typen prüfen

```bash
# Backend
cd backend
.venv/bin/ruff check .
.venv/bin/ruff format --check .

# Frontend
cd frontend
npm run typecheck
```

---

## Projektstruktur

```
digitalisierungsfabrik/
├── backend/                    # FastAPI + Python
│   ├── main.py                 # App-Factory, /health-Endpunkt
│   ├── config.py               # Konfiguration (pydantic-settings)
│   ├── requirements.txt
│   ├── pyproject.toml          # pytest + ruff Konfiguration
│   ├── .env.example
│   ├── api/                    # REST-Endpunkte + WebSocket
│   ├── core/                   # Orchestrator, Executor, Working Memory
│   ├── artifacts/
│   │   ├── models.py           # Pydantic-Modelle (alle drei Artefakte)
│   │   ├── init_validator.py   # Deterministischer Validator R-1 bis R-6 (CR-006)
│   │   └── ...
│   ├── persistence/            # SQLite Repository
│   ├── llm/                    # LLM-Client-Abstraktion
│   ├── modes/
│   │   ├── exploration.py      # Dialog-Modus: Explorationsphase
│   │   ├── structuring.py      # Dialog-Modus: Strukturierungsphase
│   │   ├── specification.py    # Dialog-Modus: Spezifikationsphase
│   │   ├── validation.py       # Dialog-Modus: Validierungsphase
│   │   ├── moderator.py        # Moduswechsel & Phasenwechsel
│   │   ├── init_structuring.py      # Background-Init: Exploration → Struktur
│   │   ├── init_specification.py    # Background-Init: Struktur → Algorithmus
│   │   └── init_coverage_validator.py  # Background-Init: Coverage-Prüfung
│   ├── prompts/
│   │   ├── exploration.md
│   │   ├── structuring.md
│   │   ├── specification.md
│   │   ├── validation.md
│   │   ├── moderator.md
│   │   ├── init_structuring.md      # Prompt für Background-Init Structurer
│   │   ├── init_specification.md    # Prompt für Background-Init Specifier
│   │   └── init_coverage_validator.md  # Prompt für Coverage-Validator
│   └── tests/
│
├── frontend/                   # React + TypeScript + Vite
│   ├── src/
│   │   ├── api/client.ts       # openapi-fetch Client (typisiert)
│   │   ├── generated/api.d.ts  # Auto-generierte Typen (nicht manuell editieren!)
│   │   ├── components/         # React-Komponenten
│   │   └── ...
│   ├── package.json
│   └── vite.config.ts
│
├── docs/
│   ├── digitalisierungsfabrik_systemdefinition.md  # SDD (Systemanforderungen)
│   └── hla_architecture.md                          # High-Level-Architektur
│
├── api-contract/
│   └── openapi.json            # Versionierter OpenAPI-Snapshot
│
└── agent-docs/
    ├── change-requests/        # Change Requests (CR-001 bis CR-006)
    ├── cr-runs/                # Run-Logs der Change-Request-Workflows
    ├── decisions/              # Architecture Decision Records (ADRs)
    ├── epics/                  # Epic-Planung (Epic 00–11)
    └── tasks/                  # Schritt-für-Schritt-Aufgabenlisten
```

---

## Konfigurationsreferenz

Alle Parameter werden aus `backend/.env` gelesen (Vorlage: `backend/.env.example`):

| Parameter | Standardwert | Beschreibung |
|---|---|---|
| `LLM_PROVIDER` | `anthropic` | LLM-Anbieter: `anthropic` oder `ollama` |
| `LLM_MODEL` | `claude-opus-4-6` | Modellname |
| `LLM_API_KEY` | *(leer)* | API-Key (Anthropic) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama-Endpoint (nur bei `ollama`) |
| `DATABASE_PATH` | `./data/digitalisierungsfabrik.db` | SQLite-Datenbankpfad |
| `DIALOG_HISTORY_N` | `3` | Anzahl letzter Turns im Kontext (Dialog-Modi) |
| `DIALOG_HISTORY_MODERATOR_M` | `10` | Turns-Fenster für den Moderator |
| `TOKEN_WARN_THRESHOLD` | `80000` | Token-Warnschwelle |
| `TOKEN_HARD_LIMIT` | `100000` | Maximale Token-Anzahl |
| `AUTOMATION_WARN_THRESHOLD` | `1` | Automatisierungs-Warnschwelle (SDD 8.1.2) |
| `LOG_LEVEL` | `INFO` | Log-Level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `LLM_LOG_ENABLED` | `true` | LLM-Requests loggen |
| `LLM_DEBUG_LOG` | `false` | Vollständige LLM-Payloads pro Turn als JSON-Dateien schreiben |

**Background-Init-Limits** (direkt im Code konfigurierbar, `backend/core/orchestrator.py`):

| Konstante | Wert | Beschreibung |
|---|---|---|
| `_MAX_INIT_TURNS` | `8` | Maximale LLM-Turns im Init-Loop |
| `_MAX_CORRECTION_TURNS` | `2` | Maximale Korrektur-Turns bei kritischen Validator-Befunden |

### Turn Debug Log

Für Debugging und Qualitätsanalyse kann das vollständige LLM-I/O pro Turn aufgezeichnet werden.

**Aktivieren:** In `backend/.env` setzen:
```
LLM_DEBUG_LOG=true
```

**Output:** Nach jedem Turn erscheint eine JSON-Datei in `backend/data/debug_turns/<project-id>/`:
```
turn_001_moderator.json
turn_002_structuring.json
turn_003_structuring.json
...
```

**Jede Datei enthält:**
- `request.system_prompt` — der komplette System-Prompt, der an das LLM gesendet wird
- `request.messages` — die Dialog-History (letzte N Turns) mit den tatsächlichen Inhalten
- `request.message_count` — Anzahl der Messages
- `request.tool_choice` — ob `auto` oder `required`
- `response.nutzeraeusserung` — was das LLM dem Nutzer antwortet
- `response.patches` — die RFC 6902 JSON-Patches
- `response.phasenstatus` — die Statuseinschätzung des LLM
- `token_usage.prompt_tokens` — gesendete Tokens in diesem Turn
- `token_usage.completion_tokens` — empfangene Tokens in diesem Turn
- `token_usage.total_tokens` — Gesamttokens dieses Turns
- `cumulative_tokens.prompt_tokens` — kumulative gesendete Tokens seit Projektbeginn
- `cumulative_tokens.completion_tokens` — kumulative empfangene Tokens seit Projektbeginn
- `cumulative_tokens.total_tokens` — kumulative Gesamttokens seit Projektbeginn

**Hinweis:** Debug-Logs können große Dateien erzeugen (System-Prompt + Dialog pro Turn). Nur für Analyse-Sessions aktivieren.

---

## OpenAPI-Vertrag (ADR-001)

Die REST-Schnittstelle zwischen Backend und Frontend wird durch einen
maschinenlesbaren OpenAPI 3.x Vertrag definiert.

- **Snapshot:** `api-contract/openapi.json` (im Repository versioniert)
- **Generierte Typen:** `frontend/src/generated/api.d.ts` (nie manuell editieren)
- **Client:** `frontend/src/api/client.ts` (verwendet `openapi-fetch`)

Nach jeder API-Änderung im Backend:

```bash
# Snapshot exportieren (Backend muss laufen)
curl http://localhost:8000/openapi.json > api-contract/openapi.json

# Typen neu generieren
cd frontend && npm run generate-api:file

# TypeScript-Kompilierung prüfen
npm run typecheck
```

Vollständige Begründung: `agent-docs/decisions/ADR-001-openapi-contract.md`

---

## Weiterführende Dokumentation

| Dokument | Inhalt |
|---|---|
| `AGENTS.md` | Regeln für AI-Agenten: Workflow, DoD, TDD, Designconstraints |
| `docs/digitalisierungsfabrik_systemdefinition.md` | Vollständige Systemanforderungen (SDD) |
| `docs/hla_architecture.md` | High-Level-Architektur (bindend) |
| `agent-docs/decisions/` | Architecture Decision Records (ADRs) |
| `agent-docs/epics/` | Epic-Planung mit Stories und DoD-Checklisten |
| `agent-docs/change-requests/` | Change Requests CR-001–CR-006 mit Reviews und Verifikationen |

---

## Implementierungsfortschritt

| Epic / CR | Thema | Status |
|---|---|---|
| Epic 00 | Projektfundament | ✅ abgeschlossen |
| Epic 01 | Datenmodelle & Persistenz | ✅ abgeschlossen |
| Epic 02 | Execution Engine | ✅ abgeschlossen |
| Epic 03 | Orchestrator & Working Memory | ✅ abgeschlossen |
| Epic 04 | Exploration Mode & LLM | ✅ abgeschlossen |
| Epic 05 | Backend API | ✅ abgeschlossen |
| Epic 06 | React Frontend | ✅ abgeschlossen |
| Epic 07 | Moderator & Phasenwechsel | ✅ abgeschlossen |
| Epic 08 | Strukturierungsmodus | ✅ abgeschlossen |
| Epic 09 | Spezifikationsmodus | ✅ abgeschlossen |
| Epic 10 | Validierung & Korrektur | ✅ abgeschlossen |
| Epic 11 | End-to-End-Stabilisierung | ✅ abgeschlossen |
| CR-001 | Exploration-Slot-Schema-Validierung | ✅ verifiziert |
| CR-002 | Kontrollfluss-Modellierung (Entscheidungen, Schleifen) | ✅ verifiziert |
| CR-003 | Explorer-Konsolidierung (7 Slots, Variablen) | ✅ verifiziert |
| CR-004 | Structurer-Prompt-Überarbeitung | ✅ verifiziert |
| CR-005 | Phasenkette-Integrität | ✅ überholt (durch CR-006 ersetzt) |
| CR-006 | Background-Initialisierung mit Validierung | ✅ verifiziert |
