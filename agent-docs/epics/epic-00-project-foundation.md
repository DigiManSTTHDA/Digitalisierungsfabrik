# Epic 00 – Project Foundation & Dev Setup

## Summary

Stand up the complete project skeleton so that every subsequent epic has a working,
reproducible environment to build on. This covers directory layout, dependency
management, linting/formatting config, and the minimal "hello world" endpoints that
prove the stack is wired together correctly.

No business logic is written in this epic. The goal is: any developer (or AI agent) can
clone the repo, run two commands, and have a green test suite and running dev server.

## Goal

A fully reproducible, documented local development environment for both backend
(FastAPI/Python) and frontend (React/TypeScript/Vite), with a passing test baseline and
a live health-check endpoint.

## Testable Increment

- `cd backend && pytest` → all tests pass (at minimum the health-check smoke test)
- `GET /health` returns `{"status": "ok"}`
- `cd frontend && npm run dev` → Vite dev server starts, browser shows placeholder page
- Both are runnable by following only the instructions in `README.md` / `AGENTS.md`

## Dependencies

None – this is the starting epic.

## Key Deliverables

- `backend/` directory with `main.py`, `requirements.txt`, `pyproject.toml` (or
  `setup.cfg`), `.env.example`
- `backend/tests/` directory with at least one smoke test
- `frontend/` directory with Vite + React + TypeScript scaffold
- `frontend/src/` placeholder `App.tsx`
- Root-level `.gitignore`, updated `README.md` with setup instructions
- CI-ready: tests and linter pass locally with documented commands

## Stories

### Story 00-01 – Repository-Grundstruktur anlegen

**Als** Entwickler (oder AI-Agent)
**möchte ich** eine saubere Root-Level-Struktur mit `.gitignore` und einem `README.md`-Skelett,
**damit** das Repository von Beginn an keine Build-Artefakte, virtuelle Umgebungen oder
Secrets eincheckt und ein zentrales Einstiegsdokument existiert.

**Akzeptanzkriterien:**

- `/.gitignore` deckt mindestens ab: `__pycache__/`, `*.pyc`, `.venv/`, `*.egg-info/`,
  `dist/`, `.env`, `node_modules/`, `frontend/dist/`, `*.db`, `.DS_Store`
- `/README.md` enthält Platzhalter-Abschnitte: Projektbeschreibung, Voraussetzungen,
  Backend-Setup, Frontend-Setup, Konfiguration, Tests ausführen
- Die Verzeichnisse `backend/` und `frontend/` sind angelegt (dürfen noch leer sein /
  nur `.gitkeep` enthalten)
- `agent-docs/` bleibt unverändert

**Definition of Done:**

- [ ] `.gitignore` committed und funktional
- [ ] `README.md` committed (Platzhalter-Inhalte genügen)
- [ ] Keine ungewollten Dateien (z. B. `.env`) werden von git getrackt

---

### Story 00-02 – Backend-Projektskelett aufbauen

**Als** Entwickler
**möchte ich** ein vollständiges `backend/`-Verzeichnis mit allen Konfigurationsdateien,
**damit** Abhängigkeiten reproduzierbar installiert und das Backend gestartet werden kann.

**Akzeptanzkriterien:**

- `backend/requirements.txt` enthält (mit fixierten Mindestversionen):
  `fastapi>=0.111`, `uvicorn[standard]`, `pydantic>=2.6`, `pydantic-settings>=2.2`,
  `anthropic>=0.25`, `jsonpatch>=1.33`, `structlog>=24.1`, `pytest`, `pytest-asyncio`,
  `httpx` (für FastAPI-Testclient)
- `backend/pyproject.toml` konfiguriert:
  - `[tool.ruff]` mit `line-length = 88`, Lint-Rules `E, F, I`
  - `[tool.mypy]` mit `strict = true`, `python_version = "3.11"`
  - `[tool.pytest.ini_options]` mit `asyncio_mode = "auto"`, `testpaths = ["tests"]`
- `backend/.env.example` enthält alle Parameter aus HLA Section 6
  (`LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`, `OLLAMA_BASE_URL`,
  `DIALOG_HISTORY_N`, `DIALOG_HISTORY_MODERATOR_M`, `TOKEN_WARN_THRESHOLD`,
  `TOKEN_HARD_LIMIT`, `AUTOMATION_WARN_THRESHOLD`, `DATABASE_PATH`,
  `LOG_LEVEL`, `LLM_LOG_ENABLED`) mit sinnvollen Standardwerten
- `backend/config.py` liest alle Parameter aus `.env` via `pydantic-settings`
  (`BaseSettings`-Subklasse `Settings`); Singleton-Pattern via `functools.lru_cache`
- `backend/main.py` ist eine minimale FastAPI-App (`app = FastAPI(...)`) ohne
  Business-Logik; importiert `config.py`; enthält noch keinen `/health`-Endpunkt

**Definition of Done:**

- [ ] `cd backend && pip install -r requirements.txt` läuft fehlerfrei
- [ ] `python -c "from config import get_settings; print(get_settings())"` druckt
      Settings-Objekt ohne Fehler (`.env` nicht erforderlich, Defaults greifen)
- [ ] `ruff check .` gibt 0 Fehler aus
- [ ] `mypy main.py config.py` gibt 0 Fehler aus

---

### Story 00-03 – Health-Check-Endpunkt implementieren

**Als** Entwickler
**möchte ich** einen `GET /health`-Endpunkt,
**damit** ich mit einem einzigen HTTP-Aufruf verifizieren kann, dass der FastAPI-Server
korrekt läuft und erreichbar ist.

**Akzeptanzkriterien:**

- `GET /health` antwortet mit HTTP 200 und Body `{"status": "ok"}`
- Response-Modell ist ein Pydantic-`BaseModel` (`HealthResponse`)
- Der Endpunkt ist in `backend/main.py` registriert (kein separater Router nötig für
  diesen einzelnen Endpunkt)
- OpenAPI-Doku unter `GET /docs` listet den Endpunkt korrekt auf

**Definition of Done:**

- [ ] `uvicorn main:app --reload` startet ohne Fehler
- [ ] `curl http://localhost:8000/health` gibt `{"status":"ok"}` zurück
- [ ] Endpunkt ist in den Backend-Smoke-Tests (Story 00-04) abgedeckt

---

### Story 00-04 – Backend-Smoke-Test-Suite einrichten

**Als** Entwickler
**möchte ich** ein `backend/tests/`-Verzeichnis mit mindestens einem Smoke-Test für den
`/health`-Endpunkt,
**damit** ein grüner `pytest`-Lauf als Baseline für alle nachfolgenden Epics dient.

**Akzeptanzkriterien:**

- `backend/tests/__init__.py` (leer) ist vorhanden
- `backend/tests/test_health.py` testet den `/health`-Endpunkt via
  `httpx.AsyncClient` + FastAPI `TestClient` oder `ASGITransport`
- Testfall 1: `GET /health` → HTTP 200
- Testfall 2: `GET /health` → Response-Body enthält `{"status": "ok"}`
- `cd backend && pytest` läuft grün (0 Fehler, 0 Warnings, die Tests blocken)
- Kein LLM-Aufruf, keine DB-Verbindung erforderlich

**Definition of Done:**

- [ ] `pytest` gibt `2 passed` (oder mehr) aus
- [ ] `pytest --tb=short -q` zeigt keine Fehler
- [ ] `mypy tests/test_health.py` gibt 0 Fehler aus

---

### Story 00-05 – Linting- und Formatting-Konfiguration vervollständigen

**Als** Entwickler
**möchte ich** konfigurierte Linting- und Formatting-Tools für Backend und Frontend,
**damit** Code-Qualität und Stil von Beginn an konsistent durchgesetzt werden.

**Akzeptanzkriterien:**

**Backend (bereits in Story 00-02 angelegt – hier wird Vollständigkeit geprüft):**

- `ruff check backend/` läuft fehlerfrei auf dem gesamten `backend/`-Verzeichnis
- `ruff format --check backend/` zeigt keine Formatierungsabweichungen
- `mypy backend/` läuft fehlerfrei (strict mode)

**Frontend:**

- `frontend/.eslintrc.json` (oder `eslint.config.js`) mit Regeln für TypeScript
  (`@typescript-eslint/recommended`) und React (`plugin:react/recommended`,
  `plugin:react-hooks/recommended`)
- `frontend/.prettierrc` mit `{ "semi": true, "singleQuote": false, "tabWidth": 2 }`
- `frontend/package.json` enthält Scripts:
  `"lint": "eslint src --ext .ts,.tsx"`,
  `"format:check": "prettier --check src"`
- `npm run lint` im `frontend/`-Verzeichnis läuft fehlerfrei
- `npm run format:check` läuft fehlerfrei

**Definition of Done:**

- [ ] `ruff check backend/` → exit code 0
- [ ] `ruff format --check backend/` → exit code 0
- [ ] `mypy backend/` → exit code 0
- [ ] `cd frontend && npm run lint` → exit code 0
- [ ] `cd frontend && npm run format:check` → exit code 0

---

### Story 00-06 – Frontend-Projektskelett aufbauen

**Als** Entwickler
**möchte ich** ein vollständiges `frontend/`-Verzeichnis mit Vite + React + TypeScript,
**damit** die Frontend-Entwicklung in nachfolgenden Epics auf einer sauberen Basis starten kann.

**Akzeptanzkriterien:**

- `frontend/` enthält die Standard-Vite-Scaffolding-Dateien:
  `package.json`, `vite.config.ts`, `tsconfig.json`, `tsconfig.node.json`, `index.html`
- `frontend/package.json` enthält:
  - Dependencies: `react>=18`, `react-dom>=18`
  - DevDependencies: `typescript>=5`, `vite>=5`, `@types/react`, `@types/react-dom`,
    `@vitejs/plugin-react`, `eslint`, `@typescript-eslint/eslint-plugin`,
    `@typescript-eslint/parser`, `eslint-plugin-react`, `eslint-plugin-react-hooks`,
    `prettier`
  - Scripts: `"dev"`, `"build"`, `"preview"`, `"lint"`, `"format:check"`
- `frontend/src/main.tsx` ist der React-Einstiegspunkt (rendert `<App />` in `#root`)
- `frontend/src/App.tsx` zeigt eine Platzhalter-Seite (mindestens `<h1>Digitalisierungsfabrik</h1>`)
- `frontend/src/` enthält leere (mit `// TODO`-Kommentar) Verzeichnisse/Dateien für
  die spätere Struktur gemäß HLA Section 6: `api/`, `components/`, `store/`, `types/`
  (jeweils mit `.gitkeep` oder Platzhalter-`.ts`-Dateien)
- `vite.config.ts` konfiguriert den Dev-Server-Proxy:
  `/api` und `/ws` werden auf `http://localhost:8000` weitergeleitet

**Definition of Done:**

- [ ] `cd frontend && npm install` läuft fehlerfrei
- [ ] `cd frontend && npm run dev` startet den Vite-Dev-Server auf Port 5173
- [ ] Browser unter `http://localhost:5173` zeigt die Platzhalter-Seite
- [ ] `npm run build` produziert ein `dist/`-Verzeichnis ohne Fehler
- [ ] `npm run lint` gibt 0 Fehler aus

---

### Story 00-07 – README vervollständigen und Entwickler-Dokumentation schreiben

**Als** neuer Entwickler (oder AI-Agent)
**möchte ich** ein vollständiges `README.md` mit schrittweisen Setup-Anweisungen für
Backend und Frontend,
**damit** ich das Projekt aus einem frischen Clone heraus ohne weitere Nachfragen zum
Laufen bringen kann.

**Akzeptanzkriterien:**

- `README.md` im Root-Verzeichnis enthält folgende Abschnitte:
  1. **Projektbeschreibung** – 2–3 Sätze zum Zweck des Systems (DE + EN akzeptabel)
  2. **Voraussetzungen** – Python ≥ 3.11, Node.js ≥ 20, Git
  3. **Backend-Setup** – exakte Kommandos:
     ```bash
     cd backend
     python -m venv .venv
     source .venv/bin/activate   # Windows: .venv\Scripts\activate
     pip install -r requirements.txt
     cp .env.example .env
     # .env befüllen (mindestens LLM_API_KEY)
     uvicorn main:app --reload
     ```
  4. **Frontend-Setup** – exakte Kommandos:
     ```bash
     cd frontend
     npm install
     npm run dev
     ```
  5. **Tests ausführen** – `cd backend && pytest`
  6. **Linting** – `ruff check backend/` und `cd frontend && npm run lint`
  7. **Konfigurationsreferenz** – Tabelle aller `.env`-Parameter (aus HLA Section 6)
  8. **Projektstruktur** – kompakte Übersicht der Verzeichnisse
  9. **Weiterführende Dokumentation** – Links zu `AGENTS.md`,
     `digitalisierungsfabrik_systemdefinition.md`, `hla_architecture.md`

- Alle Kommandos sind copy-paste-fähig und auf einem frischen Ubuntu 22.04 / macOS 14
  mit den genannten Voraussetzungen ausführbar
- `AGENTS.md` muss **nicht** verändert werden (es ist bereits vollständig)

**Definition of Done:**

- [ ] `README.md` enthält alle 9 Abschnitte
- [ ] Sämtliche Code-Blöcke im README sind syntaktisch korrekt
- [ ] Ein frischer `git clone` + Befolgen des READMEs führt zu grünem `pytest` und
      laufendem Vite-Dev-Server (manuell geprüft oder per Review bestätigt)
