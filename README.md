# Digitalisierungsfabrik — Prototyp

AI-geführtes System zur Prozesserhebung für Digitalisierungsprojekte.

**Status:** Epics 00–11 abgeschlossen + Change Requests CR-001 bis CR-009 verifiziert — Prototyp vollständig.

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
| **Init-Coverage-Validator** | `InitCoverageValidatorMode` | Prüft einmalig Informationsvollständigkeit, Kontrollfluss-Abbildung und Feldvollständigkeit der Artefakt-Transformation; darf "kritisch" und "warnung" melden (CR-009) |

### Background-Initialisierung (Detail)

Beim erstmaligen Betreten der Strukturierungs- oder Spezifikationsphase (erkennbar daran, dass das Zielartefakt leer ist) führt der Orchestrator vor dem Dialog-Einstieg folgenden Prozess aus (CR-009, ADR-009):

```
Phase 1 — Single Init-Call
    InitStructuringMode oder InitSpecificationMode einmalig aufrufen
    Patches anwenden (vollständige Artefakt-Transformation in einem Call)

Phase 2 — Python-Validator (deterministisch, kein LLM)
    2 Regeln werden geprüft:
    R-1  Referenzielle Integrität  — alle nachfolger/regeln/schleifenkoerper/konvergenz-Referenzen gültig
    R-5  Abschnitt-Mapping         — jeder Strukturschritt hat einen Algorithmusabschnitt

Phase 3 — LLM Coverage-Validator (einmalig)
    InitCoverageValidatorMode prüft Informationsvollständigkeit, Kontrollfluss, Feldvollständigkeit
    Gibt reines JSON zurück (fehlende_entitaeten, coverage_vollstaendig)
    Darf "kritisch" und "warnung" melden

Phase 4 — Korrektur-Call (optional, nur bei kritischen Befunden)
    Init-Modus erneut aufrufen mit validator_feedback (Violation-Liste)
    Maximal EIN Korrektur-Call

Phase 5 — Warnungen speichern
    Alle Warnungen → wm.init_hinweise (list[str])
    Werden beim ersten Dialog-Turn in den System-Prompt des Structurer/Specifier injiziert
```

Maximal 3 LLM-Calls (Init + Coverage + Korrektur), normalerweise 2 (Init + Coverage).

Der gesamte Prozess läuft transparent im Hintergrund. Der Nutzer sieht nichts davon — er erhält direkt das bereits befüllte Artefakt zur Überprüfung und Korrektur.

### Bekannte Beschränkungen

- **Prozessgröße**: Die Background-Initialisierung ist für Prozesse mit bis zu ~15 Strukturschritten optimiert. Bei größeren Prozessen kann der Init-Call unvollständige Artefakte erzeugen. Der Dialog-Modus kann fehlende Schritte im Gespräch ergänzen.

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
│   │   ├── init_validator.py   # Deterministischer Validator R-1 + R-5 (CR-009)
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
    ├── change-requests/        # Change Requests (CR-001 bis CR-009)
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
| `LLM_PROVIDER` | `openai` | LLM-Anbieter: `openai`, `anthropic` oder `ollama` |
| `LLM_MODEL` | `gpt-5.4` | Modellname (siehe Hinweis zur Modellwahl unten) |
| `LLM_API_KEY` | *(leer)* | API-Key |
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

### Modellwahl (wichtig!)

Die Modellwahl hat massiven Einfluss auf die Qualität der Prozesserhebung. Das System stellt hohe Anforderungen an Instruction Following, strukturierte Extraktion und gewissenhaftes Arbeiten mit JSON-Patches.

Das System verlangt zuverlässiges **Multi-Turn Instruction Following** und **strukturierte Extraktion** via JSON-Patches. Nicht jedes Modell kann das — der relevante Benchmark ist MultiChallenge (Scale Labs), nicht MMLU oder Chatbot Arena.

**Empfohlene Modelle (OpenAI API):**

| Modell | Empfehlung | Anmerkung |
|--------|-----------|-----------|
| `gpt-5.4` | **Empfohlen** | Bestes Instruction Following, gewissenhafte Extraktion |
| `gpt-5.4-mini` | Gut | Günstiger, für die meisten Fälle ausreichend |
| `o4-mini` | Für schwierige Fälle | Reasoning-Modell mit Selbstprüfung, teurer und langsamer |
| `gpt-4.1` | Minimum | Akzeptables Instruction Following |
| `gpt-4o` | **Nicht verwenden** | Überspringt Patches, markiert Slots vorzeitig als fertig, paraphrasiert statt zu extrahieren, stellt Wiederholungsfragen. Bekanntes OpenAI-Problem (MultiChallenge: 27.8%). |

**Empfohlene Modelle (Self-Hosting via Ollama):**

Open-Source-Modelle haben bei Instruction Following aufgeholt und übertreffen GPT-4o teilweise deutlich. Für Self-Hosting über `LLM_PROVIDER=ollama`:

| Modell | MultiChallenge | IFEval | Anmerkung |
|--------|---------------|--------|-----------|
| **Qwen 3.5** (397B MoE, ~35B aktiv) | **67.6%** | **92.6%** | Bestes OS-Modell für diesen Use Case. Benötigt ~48 GB VRAM. |
| Nemotron 3 Super (120B MoE) | 55.2% | 89.5% | Effiziente MoE-Architektur, gut für Agentic Workflows. |
| DeepSeek V3.1 | 46.1% | ~83% | Starkes Function Calling (94.7% BFCL), native JSON-Schema-Validierung. |
| Qwen3 235B (22B aktiv) | 41.2% | 87.8% | Guter Kompromiss aus Qualität und Ressourcenbedarf. |
| **Llama 3.3 70B** | — | **92.1%** | Bestes IFEval-Ergebnis unter 100B. Läuft auf Consumer-GPUs (Q4: ~40 GB). |
| GPT-4o (Referenz) | 27.8% | ~81% | Alle oben genannten OS-Modelle sind besser. |

**Wichtig:** Nicht jedes "gute" Modell eignet sich. Allgemeine Benchmarks (MMLU, Chatbot Arena) sagen wenig über die Eignung für strukturierte Extraktion aus. Ein Modell kann brillant konversieren und trotzdem bei JSON-Patch-Extraktion versagen. Die entscheidenden Benchmarks sind:
- **MultiChallenge** (Scale Labs) — Multi-Turn Instruction Following. Minimum ~40%, empfohlen >55%.
- **IFEval** — Single-Turn Instruction Following. Minimum ~85%.
- **BFCL** (Berkeley Function Calling) — Tool Use / Function Calling Zuverlässigkeit.

**Technische Hinweise:**
- Modelle ab GPT-5.x und o-Serie benötigen `max_completion_tokens` statt `max_tokens` — der OpenAI-Client erkennt das automatisch anhand des Modellnamens.
- Temperature ist auf 0.3 gesetzt (optimiert für strukturierte Extraktion).
- Das Tool-Schema ist so geordnet, dass `patches` vor `nutzeraeusserung` generiert wird (Extraktion vor Konversation).
- Bei Ollama: Function Calling muss vom Modell nativ unterstützt werden. Qwen3, DeepSeek V3 und Llama 3.x unterstützen das.

**Background-Init** (CR-009, ADR-009): Die Initialisierung verwendet einen Single-Call-Ansatz — kein Loop, keine konfigurierbaren Turn-Limits. Maximal 3 LLM-Calls pro Init (Init + Coverage-Validator + optionaler Korrektur-Call).

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

## E2E-Tests

Die Explorationsphase wird durch End-to-End-Tests validiert. Ein LLM spielt eine Sachbearbeiter-Persona und führt ein natürliches Gespräch mit dem Explorer — genau wie ein echter Nutzer.

**Verfügbare Playbooks (Testszenarien):**

| Playbook | Persona | Prozess | Systeme | Komplexität |
|----------|---------|---------|---------|-------------|
| `e2e-human-playbook.md` | Frau Meier | Eingangsrechnungen verbuchen | Outlook, BüroWare, Acrobat | Mittel |
| `e2e-playbook-angebotsanfragen.md` | Herr Krause | Angebotsanfragen beantworten | Outlook, ProSales, WAWI | Mittel |
| `e2e-playbook-reklamationen.md` | Frau Hartmann | Kundenreklamationen | Outlook, ServiceDesk, proALPHA, Excel | Hoch |

**Test ausführen:**

```bash
# API-Key laden
source backend/.env
export OPENAI_API_KEY=$LLM_API_KEY

# Live-Persona-Test starten (erzeugt Report in e2e/reports/)
npx tsx e2e/run-live-persona.ts --playbook agent-docs/e2e-playbook-reklamationen.md
```

Der Report enthält: vollständigen Dialog, Soll/Ist-Artefaktvergleich pro Slot und eine LLM-generierte qualitative Analyse.

Architektur, Komponenten und Konfiguration: siehe [`e2e/ARCHITECTURE.md`](e2e/ARCHITECTURE.md).

---

## Weiterführende Dokumentation

| Dokument | Inhalt |
|---|---|
| `AGENTS.md` | Regeln für AI-Agenten: Workflow, DoD, TDD, Designconstraints |
| `docs/digitalisierungsfabrik_systemdefinition.md` | Vollständige Systemanforderungen (SDD) |
| `docs/hla_architecture.md` | High-Level-Architektur (bindend) |
| `agent-docs/decisions/` | Architecture Decision Records (ADRs) |
| `agent-docs/epics/` | Epic-Planung mit Stories und DoD-Checklisten |
| `agent-docs/change-requests/` | Change Requests CR-001–CR-009 mit Reviews und Verifikationen |
| `e2e/ARCHITECTURE.md` | E2E-Testarchitektur, Runner, Playbook-Format |

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
| CR-007 | Init-Progress-Feedback | Entwurf |
| CR-008 | Phasenende-Validator | Entwurf |
| CR-009 | Init-Rewrite: Single-Call + aufgewerteter Coverage-Validator | ✅ verifiziert |
