# Digitalisierungsfabrik — Prototyp

AI-geführtes System zur Prozesserhebung für Digitalisierungsprojekte.

**Status:** Implementierung läuft — Epic 00 + 01 abgeschlossen.

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
| 02 | Execution Engine | ⏳ ausstehend |
| 03 | Orchestrator & Working Memory | ⏳ ausstehend |
| 04 | Exploration Mode & LLM | ⏳ ausstehend |
| 05 | Backend API | ⏳ ausstehend |
| 06 | React Frontend | ⏳ ausstehend |
| 07 | Moderator & Phasenwechsel | ⏳ ausstehend |
| 08 | Strukturierungsmodus | ⏳ ausstehend |
| 09 | Spezifikationsmodus | ⏳ ausstehend |
| 10 | Validierung & Korrektur | ⏳ ausstehend |
| 11 | End-to-End-Stabilisierung | ⏳ ausstehend |
