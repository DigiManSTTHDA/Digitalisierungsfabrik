# Digitalisierungsfabrik — Prototyp

AI-geführtes System zur Prozesserhebung für Digitalisierungsprojekte.

**Status:** Epics 00–11 abgeschlossen — Prototyp vollständig.

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

2. **Exploration** — Das System fragt nach dem Prozessauslöser, Ziel, Beschreibung, Beteiligten usw. Die Antworten werden im Explorationsartefakt (rechte Seite) gespeichert. Wenn alle neun Pflichtfelder gefüllt sind, schlägt der Moderator den Wechsel zur nächsten Phase vor.

3. **Strukturierung** — Das System analysiert den beschriebenen Prozess und entwirft Prozessschritte. Korrekturen und Ergänzungen sind per Chat möglich. Nach Bestätigung erfolgt der Phasenwechsel.

4. **Spezifikation** — Jeder Prozessschritt wird als EMMA-Aktionssequenz formalisiert. Das Algorithmusartefakt entsteht durch Dialog mit dem System.

5. **Validierung** — Das System prüft die Artefakte auf Konsistenz und Vollständigkeit. Bei bestandener Validierung erscheint der Status "Projekt abgeschlossen" in der Kopfzeile.

**Exportieren:** Nach Abschluss der Validierung im Artefaktbereich (rechts) auf "Exportieren" klicken. Es werden zwei Dateien heruntergeladen:
- `artifacts.json` — alle drei Artefakte als JSON-Bundle
- `artifacts.md` — lesbare Markdown-Darstellung aller Artefakte

---

## Übersicht

Das System führt Nutzer durch einen strukturierten Dialog und erzeugt dabei drei
miteinander verknüpfte Artefakte:

1. **Explorationsartefakt** — beschreibt den Ist-Prozess in Prosaform
2. **Strukturartefakt** — gliedert den Prozess in nummerierte Prozessschritte
3. **Algorithmusartefakt** — spezifiziert jeden Schritt als EMMA-Aktionssequenz

**Spezifikationen:**
- System-/Anforderungsdokumentation: `digitalisierungsfabrik_systemdefinition.md`
- Architektur: `hla_architecture.md`
- Agenten-Regeln: `AGENTS.md`

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
│   ├── artifacts/              # Pydantic-Modelle, Store, Completeness
│   ├── persistence/            # SQLite Repository
│   ├── llm/                    # LLM-Client-Abstraktion
│   ├── modes/                  # Kognitive Modi
│   ├── prompts/                # LLM-Systemprompts (Markdown)
│   └── tests/
│
├── frontend/                   # React + TypeScript + Vite
│   ├── src/
│   │   ├── api/client.ts       # openapi-fetch Client (typisiert)
│   │   ├── generated/api.d.ts  # Auto-generierte Typen (nicht manuell editieren!)
│   │   ├── components/         # React-Komponenten (ab Epic 06)
│   │   └── ...
│   ├── package.json
│   └── vite.config.ts
│
├── api-contract/
│   └── openapi.json            # Versionierter OpenAPI-Snapshot
│
└── agent-docs/
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
| `DIALOG_HISTORY_N` | `3` | Anzahl letzter Turns im Kontext |
| `DIALOG_HISTORY_MODERATOR_M` | `10` | Turns-Fenster für den Moderator |
| `TOKEN_WARN_THRESHOLD` | `80000` | Token-Warnschwelle |
| `TOKEN_HARD_LIMIT` | `100000` | Maximale Token-Anzahl |
| `AUTOMATION_WARN_THRESHOLD` | `1` | Automatisierungs-Warnschwelle (SDD 8.1.2) |
| `LOG_LEVEL` | `INFO` | Log-Level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `LLM_LOG_ENABLED` | `true` | LLM-Requests loggen |
| `LLM_DEBUG_LOG` | `false` | Vollständige LLM-Payloads pro Turn als JSON-Dateien schreiben |

### Turn Debug Log

Für Debugging und Qualitätsanalyse kann das vollständige LLM-I/O pro Turn aufgezeichnet werden.

**Aktivieren:** In `backend/.env` setzen:
```
LLM_DEBUG_LOG=true
```

**Output:** Nach jedem Turn erscheint eine JSON-Datei in `backend/data/debug_turns/<project-id>/`:
```
turn_001_moderator.json
turn_002_specification.json
turn_003_specification.json
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
| `digitalisierungsfabrik_systemdefinition.md` | Vollständige Systemanforderungen (SDD) |
| `hla_architecture.md` | High-Level-Architektur (bindend) |
| `agent-docs/decisions/` | Architecture Decision Records (ADRs) |
| `agent-docs/epics/` | Epic-Planung mit Stories und DoD-Checklisten |

---

## Implementierungsfortschritt

| Epic | Thema | Status |
|---|---|---|
| 00 | Projektfundament | ✅ abgeschlossen |
| 01 | Datenmodelle & Persistenz | ✅ abgeschlossen |
| 02 | Execution Engine | ✅ abgeschlossen |
| 03 | Orchestrator & Working Memory | ✅ abgeschlossen |
| 04 | Exploration Mode & LLM | ✅ abgeschlossen |
| 05 | Backend API | ✅ abgeschlossen |
| 06 | React Frontend | ✅ abgeschlossen |
| 07 | Moderator & Phasenwechsel | ✅ abgeschlossen |
| 08 | Strukturierungsmodus | ✅ abgeschlossen |
| 09 | Spezifikationsmodus | ✅ abgeschlossen |
| 10 | Validierung & Korrektur | ✅ abgeschlossen |
| 11 | End-to-End-Stabilisierung | ✅ abgeschlossen |
