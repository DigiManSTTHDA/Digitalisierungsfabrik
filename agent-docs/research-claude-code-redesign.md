# Research: Digitalisierungsfabrik — Redesign mit agentischer KI

**Datum:** 2026-03-18
**Autor:** Claude Code Research Agent
**Status:** Entwurf zur Diskussion

---

## 1. Zusammenfassung

Die **Digitalisierungsfabrik** ist ein KI-gesteuertes System, das Fachexperten durch sokratischen Dialog hilft, implizites Prozesswissen in strukturierte, automatisierbare EMMA-Algorithmen zu überführen. Das System wurde als Full-Stack-Applikation (FastAPI + React + SQLite) mit ~17.000 Zeilen Backend-Code implementiert.

Diese Analyse untersucht, ob und wie dasselbe Ziel mit modernen agentischen KI-Tools — insbesondere Claude Code und dem Claude Agent SDK — **einfacher, stabiler und wartbarer** erreicht werden könnte.

**Kernthese:** Ein Großteil der Infrastruktur (Orchestrator, Executor, Working Memory, Persistence, WebSocket-Layer, React-Frontend) wurde gebaut, um Fähigkeiten bereitzustellen, die Claude Code heute nativ mitbringt. Der fachliche Kern — die 5 kognitiven Modi mit ihren System-Prompts — könnte als Claude Code Skills/Agents direkt wiederverwendet werden.

---

## 2. Was die Digitalisierungsfabrik heute tut

### 2.1 Problemstellung
Fachexperten verstehen ihre Geschäftsprozesse intuitiv, können dieses Wissen aber nicht in automatisierbare Algorithmen überführen. Die Digitalisierungsfabrik überbrückt diese Lücke durch KI-geführte Interviews.

### 2.2 Die 4 Phasen

| Phase | Modus | Input | Output (Artefakt) |
|-------|-------|-------|-------------------|
| 1. Exploration | ExplorationMode | Dialog mit Nutzer | Explorationsartefakt (9 Pflichtslots) |
| 2. Strukturierung | StructuringMode | Explorationsartefakt | Strukturartefakt (BPMN-ähnlich) |
| 3. Spezifikation | SpecificationMode | Strukturartefakt | Algorithmusartefakt (EMMA-Aktionen) |
| 4. Validierung | ValidationMode | Alle Artefakte | Validierungsbericht |

Zusätzlich: **Moderator-Modus** für Phasenübergänge und Eskalation.

### 2.3 Aktuelle Architektur (~17.000 LoC Backend)

```
React Frontend (TypeScript/Vite)
    ↕ REST + WebSocket
FastAPI Backend (Python)
    ├── Orchestrator (11-Schritt-Zyklus)
    ├── Executor (RFC 6902 JSON Patch)
    ├── Working Memory (Laufzeitstatus)
    ├── 5 Kognitive Modi (LLM-Aufrufe mit System-Prompts)
    ├── Artifact Store (3 Artefakte, dict-keyed, versioniert)
    ├── Completeness Calculator
    └── SQLite Persistence (ACID)
```

### 2.4 Was davon ist "Infrastruktur" vs. "Fachlogik"?

| Kategorie | Komponenten | LoC (geschätzt) | Anteil |
|-----------|-------------|-----------------|--------|
| **Fachlogik** | 5 System-Prompts, Artefakt-Schemata, Completeness-Regeln, EMMA-Katalog | ~2.000 | ~12% |
| **Orchestrierung** | Orchestrator, Executor, Phase Transition, Progress Tracker, Working Memory | ~4.000 | ~23% |
| **Infrastruktur** | FastAPI, WebSocket, REST-Routes, LLM-Abstraction, Persistence, Config | ~6.000 | ~35% |
| **Frontend** | React-Komponenten, State, API-Client | ~3.000 | ~18% |
| **Tests** | Unit, Integration, E2E | ~2.000 | ~12% |

**Erkenntnis:** Nur ~12% des Codes ist domänenspezifische Fachlogik. Der Rest ist Infrastruktur, die agentische KI-Plattformen heute nativ bereitstellen.

---

## 3. Was Claude Code heute kann (März 2026)

### 3.1 Relevante Fähigkeiten im Vergleich

| Anforderung der Digitalisierungsfabrik | Aktuelle Lösung | Claude Code Äquivalent |
|----------------------------------------|-----------------|----------------------|
| Multi-Turn-Dialog mit Zustandsverwaltung | WebSocket + Working Memory + SQLite | **Native Sessions** mit `--continue`/`--resume`, Auto-Memory |
| Strukturierte Artefakte pflegen | Artifact Store + RFC 6902 Patches + Versionierung | **File-basiert** (JSON/MD) + Git-Versionierung + Edit-Tool |
| Phasensteuerung (4 Phasen sequenziell) | Orchestrator + Phase Transition Logic | **Skills** mit Phasen-Logik in CLAUDE.md oder Skill-Definitionen |
| 5 kognitive Modi (LLM mit spez. Prompts) | Python-Klassen + LLM-Abstraction + Tool Use | **Skills/Agents** (`.claude/skills/` oder `.claude/agents/`) |
| Validierung & Konsistenzprüfung | ValidationMode + deterministische Checks | **Hooks** (PostToolUse, Stop) + Validierungs-Skill |
| Completeness-Tracking | CompletenessCalculator | **Hook** oder **Skill** der JSON-Artefakte prüft |
| Export (JSON + Markdown) | Renderer + REST-Endpoint | **Skill** der Artefakte rendert (trivial) |
| Echtzeit-Updates | WebSocket-Events | Claude Code Web UI oder Agent SDK Streaming |
| Persistenz mit ACID | SQLite + Transaktionen | Git Commits (atomare Snapshots) oder Agent SDK + DB via MCP |
| LLM-Provider-Abstraktion | Factory Pattern (Anthropic/OpenAI/Ollama) | **Nativer Claude-Zugang** (kein Abstraktionslayer nötig) |

### 3.2 Schlüssel-Features für den Redesign

#### Skills (`.claude/skills/`)
- Wiederverwendbare Prompt-basierte Workflows
- Können in isolierten Subagenten laufen (`context: fork`)
- Haben Zugriff auf alle Tools (Read, Write, Edit, Bash, Grep, Glob)
- Unterstützen dynamische Kontextinjektion
- Können andere Skills laden (`skills:` Frontmatter)

#### Hooks
- `SessionStart`: Projekt-Kontext laden
- `PreToolUse` / `PostToolUse`: Validierungsregeln durchsetzen
- `Stop`: Completeness-Check vor Phasenende
- `UserPromptSubmit`: Input-Validierung

#### Agents (`.claude/agents/`)
- Spezialisierte Agenten mit eigenen Tools und Prompts
- Können als Subagenten delegiert werden
- Isolierter Kontext (schützt Hauptkonversation)

#### Claude Agent SDK
- Claude Code als Library (Python & TypeScript)
- Programmatische Steuerung von Agents
- Structured Outputs (JSON-Schema)
- Session-Management über API-Calls
- Hooks als Callbacks
- Produktionsreif für Backend-Integration

#### CLAUDE.md & Rules
- Projekt-Konventionen und Architektur-Regeln
- Automatisch geladen bei Session-Start
- Pfadspezifische Regeln möglich
- Import-Syntax für modulare Konfiguration

---

## 4. Redesign-Konzept: "Digitalisierungsfabrik v2"

### 4.1 Architektur-Vision

```
Projektverzeichnis (Git-Repository)
├── CLAUDE.md                          # Projekt-Regeln & Phasenlogik
├── .claude/
│   ├── settings.json                  # Hooks-Konfiguration
│   ├── skills/
│   │   ├── exploration/SKILL.md       # Explorations-Modus
│   │   ├── structuring/SKILL.md       # Strukturierungs-Modus
│   │   ├── specification/SKILL.md     # Spezifikations-Modus
│   │   ├── validation/SKILL.md        # Validierungs-Modus
│   │   ├── moderator/SKILL.md         # Moderator-Modus
│   │   ├── export/SKILL.md            # Export-Funktionalität
│   │   └── status/SKILL.md            # Fortschritts-Übersicht
│   ├── agents/
│   │   └── process-elicitor/AGENT.md  # Haupt-Agent für Prozesselizitierung
│   └── rules/
│       ├── artifacts.md               # Artefakt-Schemata & Regeln
│       ├── emma-catalog.md            # EMMA-Aktionskatalog
│       └── phases.md                  # Phasenübergangs-Regeln
│
├── projekte/                          # Ein Verzeichnis pro Geschäftsprozess
│   └── {prozess-name}/
│       ├── exploration.json           # Explorationsartefakt
│       ├── struktur.json              # Strukturartefakt
│       ├── algorithmus.json           # Algorithmusartefakt
│       ├── validierung.json           # Validierungsbericht
│       ├── status.json                # Working Memory / Phasenstatus
│       └── export/
│           ├── artifacts.json         # Komplett-Export
│           └── artifacts.md           # Markdown-Export
│
└── schemata/                          # JSON-Schemata für Validierung
    ├── exploration-schema.json
    ├── struktur-schema.json
    └── algorithmus-schema.json
```

### 4.2 Was entfällt komplett

| Komponente | Grund für Entfall |
|-----------|-------------------|
| **FastAPI Backend** (~6.000 LoC) | Claude Code IST der Server |
| **React Frontend** (~3.000 LoC) | Claude Code Web/CLI IST die UI |
| **WebSocket-Layer** | Native Streaming in Claude Code |
| **Orchestrator (11-Schritt-Zyklus)** | Claude Code's agentic loop + Skills |
| **LLM-Abstraction (Factory, Clients)** | Nativer Claude-Zugang |
| **SQLite Persistence** | Git + JSON-Dateien |
| **Working Memory (Python-Klasse)** | `status.json` + Claude's Session Memory |
| **REST-API + OpenAPI-Contract** | Nicht nötig (kein separates Frontend) |
| **Executor (RFC 6902 Patches)** | Claude's Edit-Tool (surgical file edits) |

### 4.3 Was bleibt / adaptiert wird

| Komponente | Neue Form |
|-----------|-----------|
| **5 System-Prompts** (exploration.md, etc.) | → **Skills** (`.claude/skills/`) |
| **Artefakt-Schemata** (Pydantic-Modelle) | → **JSON-Schemata** + Validierungs-Rules |
| **Completeness-Regeln** | → **Hook** oder Prüf-Skill |
| **EMMA-Aktionskatalog** | → **Rule-Datei** (`.claude/rules/emma-catalog.md`) |
| **Phasenübergangs-Logik** | → **CLAUDE.md** + Moderator-Skill |
| **Validierungs-Checks** | → **Validation-Skill** (deterministisch + LLM) |
| **Export-Rendering** | → **Export-Skill** (trivial) |

### 4.4 Beispiel: Explorations-Skill

```markdown
# .claude/skills/exploration/SKILL.md
---
name: exploration
description: Führe Phase 1 der Prozessexploration durch
allowed-tools: Read, Write, Edit, Glob, Grep
---

## Aufgabe
Du bist ein erfahrener Prozessberater. Führe ein sokratisches Interview
mit dem Nutzer, um implizites Prozesswissen zu erfassen.

## Artefakt
Lies und aktualisiere: `projekte/$ARGUMENTS/exploration.json`

## Pflichtslots (alle 9 müssen befüllt werden)
1. prozessausloeser — Was löst den Prozess aus?
2. prozessziel — Was ist das gewünschte Endergebnis?
3. prozessbeschreibung — Grobe Beschreibung des Ablaufs
4. beteiligte — Wer ist am Prozess beteiligt?
5. datenquellen — Welche Daten werden benötigt?
6. systeme — Welche IT-Systeme sind involviert?
7. ausnahmen — Welche Sonderfälle gibt es?
8. dokumentation — Gibt es bestehende Dokumentation?
9. anmerkungen — Sonstige Hinweise

## Gesprächsführung
- Stelle EINE Frage pro Turn
- Fasse Antworten zusammen und bitte um Bestätigung
- Aktualisiere das Artefakt nach jeder bestätigten Antwort
- Zeige den Fortschritt (X/9 Slots befüllt)
- Wenn alle Slots befüllt: Frage ob Phase abgeschlossen werden kann

## Schema
Das Artefakt muss diesem Schema folgen:
@schemata/exploration-schema.json
```

### 4.5 Beispiel: Phasensteuerung via CLAUDE.md

```markdown
# CLAUDE.md (Auszug)

## Digitalisierungsfabrik — Phasenregeln

Dieses Projekt dient der KI-gestützten Prozesselizitierung.
Jeder Geschäftsprozess hat sein eigenes Verzeichnis unter `projekte/`.

### Phasenreihenfolge (strikt sequentiell)
1. `/exploration` → Explorationsartefakt befüllen
2. `/structuring` → Strukturartefakt aus Exploration ableiten
3. `/specification` → EMMA-Algorithmus aus Struktur ableiten
4. `/validation` → Alle Artefakte auf Konsistenz prüfen

### Phasenübergang
- Eine Phase darf erst gestartet werden, wenn die vorherige als
  `phase_complete` in `status.json` markiert ist
- Prüfe IMMER `status.json` bevor du einen Phasen-Skill startest
- Der `/moderator`-Skill entscheidet über Phasenübergänge

### Artefakt-Regeln
- Artefakte liegen als JSON unter `projekte/{name}/`
- Schemata unter `schemata/` sind bindend
- Nach jeder Artefakt-Änderung: Git-Commit mit Beschreibung
```

---

## 5. Vergleich: Alt vs. Neu

### 5.1 Quantitativer Vergleich

| Metrik | Digitalisierungsfabrik v1 | Redesign v2 (Claude Code) |
|--------|--------------------------|--------------------------|
| **Backend LoC** | ~17.000 (Python) | ~0 (kein Custom-Backend) |
| **Frontend LoC** | ~3.000 (TypeScript/React) | ~0 (Claude Code UI) |
| **Konfiguration/Prompts** | ~2.000 (Prompts + Schemata) | ~2.000 (Skills + Rules + Schemata) |
| **Infrastruktur-Code** | ~12.000 | ~0 |
| **Abhängigkeiten** | 14 Python-Packages + npm | Claude Code CLI oder Agent SDK |
| **Deployment** | FastAPI + Vite + SQLite | Git-Repository + Claude Code |
| **Wartung** | Python + TypeScript + SQL | Markdown-Prompts + JSON-Schemata |

### 5.2 Qualitativer Vergleich

| Aspekt | v1 (Custom App) | v2 (Claude Code) |
|--------|-----------------|-------------------|
| **Entwicklungsaufwand** | Wochen/Monate | Tage |
| **Änderbarkeit der Fachlogik** | Python-Code ändern + testen | Markdown-Prompts editieren |
| **LLM-Qualität** | Identisch (Claude) | Identisch (Claude), aber immer aktuellstes Modell |
| **Artefakt-Konsistenz** | ACID-Transaktionen (stark) | Git-Commits (gut, aber nicht ACID) |
| **Versionierung** | SQLite artifact_versions | Git-History (mächtiger) |
| **UI/UX** | Custom React (poliert) | Claude Code CLI/Web (funktional, aber generisch) |
| **Multi-User** | Möglich (mit Aufwand) | Nicht nativ (jeder hat eigene Session) |
| **Offline-Fähigkeit** | Mit Ollama (teilweise) | Mit lokalen LLMs (experimentell) |
| **Erweiterbarkeit** | Python-Code schreiben | Skills/Agents/Hooks hinzufügen |
| **Debugging/Observability** | structlog + Debug-Panel | Claude Code native Logging |

---

## 6. Drei Umsetzungsoptionen

### Option A: "Pure Claude Code" (minimal)

**Ansatz:** Alles als Skills + CLAUDE.md + JSON-Dateien in einem Git-Repo.

**Vorteile:**
- Keinerlei Custom-Code
- Sofort einsetzbar
- Fachlogik = Prompts (leicht änderbar)
- Versionierung über Git

**Nachteile:**
- Keine Custom-UI (CLI oder Claude Code Web)
- Keine ACID-Garantien
- Kein Multi-User
- Abhängig von Claude Code als Plattform

**Aufwand:** 2-5 Tage

**Empfohlen wenn:** Prototyping, Einzelnutzer, schnelle Iteration

---

### Option B: "Agent SDK Backend" (hybrid)

**Ansatz:** Schlankes Backend (FastAPI oder Express) das den Claude Agent SDK nutzt. Minimales Frontend optional.

```
Leichtgewichtiges Frontend (optional)
    ↕ REST/WebSocket
Schlankes Backend (~500 LoC)
    ├── Session-Management
    ├── Claude Agent SDK Aufrufe
    ├── Structured Outputs (JSON-Schema)
    └── Datei-basierte Persistenz (oder SQLite)
```

**Vorteile:**
- Kontrollierte API für externe Integration
- Custom-UI möglich
- Structured Outputs garantieren Artefakt-Konformität
- Claude übernimmt die gesamte Fachlogik
- Multi-User über Session-Management

**Nachteile:**
- Etwas Custom-Code nötig (~500-1000 LoC vs. 17.000)
- Abhängigkeit vom Agent SDK

**Aufwand:** 1-2 Wochen

**Empfohlen wenn:** Produktions-Einsatz mit mehreren Nutzern, API-Integration nötig

---

### Option C: "Prompt-Optimiertes v1" (evolutionär)

**Ansatz:** Bestehende Architektur beibehalten, aber massiv vereinfachen durch Entfernung von Infrastruktur-Schichten, die Claude Code nativ liefern kann.

**Konkret entfernen/vereinfachen:**
- LLM-Abstraction → Direkt Anthropic SDK
- Executor (RFC 6902) → Claude's native Edit-Fähigkeit nutzen (Structured Output mit JSON)
- Working Memory → Vereinfachte Datei-basierte Lösung
- Orchestrator → Vereinfachter Dispatcher

**Vorteile:**
- Erhalt der Custom-UI
- Schrittweise Migration möglich
- Weniger Risiko

**Nachteile:**
- Immer noch viel Infrastruktur-Code
- Halbherzige Lösung

**Aufwand:** 1-2 Wochen

**Empfohlen wenn:** UI-Qualität kritisch, schrittweise Migration bevorzugt

---

## 7. Empfehlung

### Für Prototyp/Validierung: **Option A** (Pure Claude Code)

Die Digitalisierungsfabrik wurde konzipiert, um ein spezifisches fachliches Problem zu lösen. Die aktuelle Implementierung investiert ~88% des Codes in Infrastruktur, die Claude Code heute nativ bereitstellt.

**Option A** erlaubt es, den fachlichen Kern (die 5 System-Prompts + Artefakt-Schemata) innerhalb weniger Tage als Claude Code Skills zu deployen und sofort zu testen, ob das Grundkonzept funktioniert.

### Für Produktion: **Option B** (Agent SDK)

Sobald validiert ist, dass die Skills die gewünschte Qualität liefern, kann mit dem Claude Agent SDK ein schlankes Backend gebaut werden, das:
- Multi-User-Support bietet
- Eine Custom-UI anbinden kann
- Structured Outputs für Artefakt-Konformität erzwingt
- Session-Persistenz über API-Calls managed

### Migrationspfad

```
Jetzt           → Option A (2-5 Tage)
                  Skills + CLAUDE.md + JSON-Dateien
                  Validierung des Konzepts

Danach          → Option B (1-2 Wochen)
                  Agent SDK Backend
                  Schlankes Frontend (falls nötig)
                  Produktions-Deployment

Von v1 nutzen   → System-Prompts (fast 1:1 als Skills)
                  Artefakt-Schemata (als JSON-Schemata)
                  EMMA-Katalog (als Rule-Datei)
                  Phasenlogik (als CLAUDE.md Regeln)

Nicht mitnehmen → Orchestrator, Executor, Working Memory,
                  FastAPI, React, SQLite, WebSocket,
                  LLM-Abstraction, Completeness Calculator
```

---

## 8. Offene Fragen & Risiken

### 8.1 Offene Fragen
1. **UI-Anforderungen:** Reicht Claude Code Web/CLI als Interface, oder brauchen Fachexperten eine dedizierte UI?
2. **ACID-Garantien:** Ist Git-basierte Versionierung ausreichend, oder werden DB-Transaktionen benötigt?
3. **Multi-User:** Wie viele parallele Nutzer sind realistisch?
4. **EMMA-Kompatibilität:** Können Structured Outputs die EMMA-Konformität genauso streng durchsetzen wie der RFC 6902 Executor?
5. **Kosten:** Wie verhält sich der Token-Verbrauch bei Skills vs. Custom-Backend mit optimiertem Context?

### 8.2 Risiken
1. **Plattformabhängigkeit:** Vollständige Abhängigkeit von Claude Code / Anthropic
2. **Kontrollverlust:** Weniger Kontrolle über LLM-Verhalten als bei Custom-Orchestrator
3. **Context-Window:** Bei großen Artefakten könnte das Context-Window limitierend sein
4. **Determinismus:** Skills sind weniger deterministisch als ein 11-Schritt-Orchestrator
5. **Regression:** Modell-Updates könnten Verhalten ändern (kein Pin auf spezifische Version in Claude Code)

### 8.3 Mitigationen
- **Plattformabhängigkeit:** Agent SDK als Abstraktion; Prompts sind portabel
- **Kontrollverlust:** Hooks + Rules für deterministische Guardrails
- **Context-Window:** Artefakte in separaten Dateien; Subagenten für Isolation
- **Determinismus:** Stop-Hooks für Validierung; JSON-Schema Enforcement
- **Regression:** Versionierte Skills + E2E-Tests als Regressions-Checks

---

## 9. Nächste Schritte

1. **Proof of Concept (Option A):** Explorations-Skill implementieren und mit echtem Prozess testen
2. **Skills migrieren:** Die 5 System-Prompts aus `backend/prompts/` als Skills adaptieren
3. **Schemata portieren:** Pydantic-Modelle → JSON-Schemata
4. **Hooks definieren:** Validierungs- und Phasenübergangs-Hooks
5. **E2E-Test:** Einen kompletten 4-Phasen-Durchlauf mit Claude Code Skills durchführen
6. **Evaluierung:** Qualität der Artefakte vergleichen (v1 vs. v2)

---

## Anhang A: Agentic AI Landschaft (März 2026)

### Relevante Frameworks

| Framework | Anbieter | Stärke | Relevanz für Digitalisierungsfabrik |
|-----------|---------|--------|--------------------------------------|
| **Claude Code + Agent SDK** | Anthropic | Native LLM-Integration, Skills, Hooks, Agents | ★★★★★ Höchste Relevanz |
| **LangGraph** | LangChain | Graph-basierte Workflows, State Management | ★★★☆☆ Alternative für komplexe Flows |
| **CrewAI** | CrewAI | Multi-Agent Kollaboration, Rollen-basiert | ★★☆☆☆ Overkill für diesen Use Case |
| **Google ADK** | Google | Gemini-optimiert, MCP-Support, Multi-Agent | ★★☆☆☆ Vendor Lock-in (Google) |
| **AWS Strands Agents** | Amazon | Bedrock-Integration, Enterprise-ready | ★★☆☆☆ Vendor Lock-in (AWS) |
| **AutoGen** | Microsoft | Multi-Agent Conversations | ★★☆☆☆ Zu generisch |

### Warum Claude Code/Agent SDK die beste Wahl ist

1. **Gleicher LLM-Provider:** Die Digitalisierungsfabrik nutzt bereits Claude — kein Provider-Wechsel nötig
2. **Skills = direkte Prompt-Migration:** Die 5 System-Prompts können fast 1:1 übernommen werden
3. **Built-in Tools:** Read, Write, Edit, Glob, Grep — alles was für Artefakt-Management nötig ist
4. **Hooks für Guardrails:** Deterministische Validierung ohne Custom-Code
5. **Agent SDK für Produktion:** Programmatische Steuerung wenn Custom-Backend nötig
6. **Geringster Migrationsaufwand:** Prompt-zentrische Architektur passt perfekt

---

## Anhang B: Komponentenmapping (v1 → v2)

| v1 Komponente | Datei(en) | v2 Äquivalent |
|---------------|-----------|---------------|
| `modes/exploration.py` + `prompts/exploration.md` | `.claude/skills/exploration/SKILL.md` |
| `modes/structuring.py` + `prompts/structuring.md` | `.claude/skills/structuring/SKILL.md` |
| `modes/specification.py` + `prompts/specification.md` | `.claude/skills/specification/SKILL.md` |
| `modes/validation.py` + `prompts/validation.md` | `.claude/skills/validation/SKILL.md` |
| `modes/moderator.py` + `prompts/moderator.md` | `.claude/skills/moderator/SKILL.md` |
| `core/orchestrator.py` | CLAUDE.md Phasenregeln + Moderator-Skill |
| `core/executor.py` | Claude Code's Edit-Tool + Structured Outputs |
| `core/working_memory.py` | `projekte/{name}/status.json` |
| `artifacts/models.py` | `schemata/*.json` (JSON-Schema) |
| `artifacts/completeness.py` | Hook oder Prüf-Logik im Skill |
| `artifacts/renderer.py` | Export-Skill |
| `persistence/` | Git + JSON-Dateien |
| `api/router.py` + `api/websocket.py` | Nicht nötig (Claude Code = Interface) |
| `llm/` | Nicht nötig (nativer Claude-Zugang) |
| `config.py` | `.claude/settings.json` |
