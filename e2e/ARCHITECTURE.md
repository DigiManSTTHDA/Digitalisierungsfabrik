# E2E-Testarchitektur

Dokumentation der End-to-End-Testinfrastruktur der Digitalisierungsfabrik.

## Überblick

Die E2E-Tests prüfen die kognitiven Modi der Digitalisierungsfabrik (Exploration, Strukturierung, Spezifikation) durch simulierte Nutzer-Gespräche über WebSocket. Es gibt zwei Test-Modi:

1. **Scripted Scenarios** — Vorgeskriptete Nutzer-Antworten in JSON-Dateien
2. **Live-Persona** — Ein LLM spielt die Nutzer-Persona dynamisch, basierend auf einem Playbook

## Architektur

```
                    ┌──────────────────────┐
                    │     Playbook (.md)   │
                    │  Persona + Prozess-  │
                    │  wissen + Ziel-      │
                    │  artefakt            │
                    └──────────┬───────────┘
                               │
                               ▼
┌─────────────┐    ┌──────────────────────┐    ┌──────────────────┐
│  Persona    │◄───│  Live-Persona-Runner │───►│  Backend         │
│  LLM        │    │  (run-live-persona)  │    │  (WebSocket)     │
│  (GPT-4.1-  │    │                      │    │                  │
│   mini)     │    │  1. Empfängt Frage   │    │  Explorer-Modus  │
│             │    │  2. Persona antwortet│    │  (GPT-5.4)       │
│  Spielt die │    │  3. Sendet Antwort   │    │                  │
│  Persona    │    │  4. Empfängt nächste │    │  Stellt Fragen,  │
│             │    │     Frage            │    │  füllt Artefakt  │
└─────────────┘    │  5. Wiederholt bis   │    │                  │
                    │     phase_complete   │    │                  │
                    └──────────────────────┘    └──────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Report (.md)        │
                    │  - Dialog            │
                    │  - Soll/Ist-Vgl.     │
                    │  - Gap-Analyse       │
                    └──────────────────────┘
```

### Scripted Scenarios (legacy)

```
Szenario (.json)  ──►  ScenarioRunner  ──►  Backend (WebSocket)
                        Sendet vorgeskriptete         │
                        Turns sequentiell              │
                                                       ▼
                        AssertionEvaluator  ◄──  Turn-Ergebnisse
                        BehaviorEvaluator
                        CampaignReporter
```

## Verzeichnisstruktur

```
e2e/
├── framework/                    # Kern-Infrastruktur
│   ├── ws-client.ts             # WebSocket/HTTP-Client (SessionClient)
│   ├── scenario-runner.ts       # Scripted-Scenario-Ausführung
│   ├── assertion-evaluator.ts   # 7 deterministische Prüfregeln
│   ├── behavior-evaluator.ts    # Verhaltensbewertung
│   ├── campaign-reporter.ts     # Markdown-Reportgenerator
│   └── types.ts                 # TypeScript-Interfaces
├── scenarios/                    # Scripted-Szenario-Definitionen (JSON)
│   ├── s01-eingangsrechnung.json
│   ├── ...
│   ├── s09-eingangsrechnung-bueroware.json
│   └── s10-angebotsanfragen.json
├── reports/                      # Generierte Reports (gitignored)
├── run-campaign.ts              # CLI: Scripted-Szenarien ausführen
├── run-live-persona.ts          # CLI: Live-Persona-Test ausführen
├── package.json
└── tsconfig.json

agent-docs/
├── e2e-human-playbook.md               # Playbook: Frau Meier (Rechnungen)
├── e2e-playbook-angebotsanfragen.md    # Playbook: Herr Krause (Angebote)
└── e2e-playbook-reklamationen.md       # Playbook: Frau Hartmann (Reklamationen)
```

## Playbook-Format

Jedes Playbook enthält:

### Teil A: Persona & Prozesswissen
- **Persona-Briefing**: Rolle, Unternehmen, Charakter, typische Formulierungen
- **Prozesswissen**: Vollständige Ground Truth des Prozesses auf RPA-Niveau
  - Systeme (Name, Zugang, Funktion)
  - Schritt-für-Schritt-Ablauf
  - Entscheidungen mit Bedingungen
  - Ausnahmen/Sonderfälle
  - Variablen & Daten

### Teil B: Ziel-Artefakte
- Pro Slot: Soll-Inhalt als Blockquote
- `**Muss enthalten:**` — Pflichtbegriffe für automatischen Keyword-Check
- `**Status:**` — erwarteter completeness_status

### Dinge die NICHT im Artefakt stehen dürfen
- Liste von Halluzinations-Begriffen (OCR, SAP, API, etc.)

## Komponenten

### SessionClient (`ws-client.ts`)

WebSocket-Client für die Backend-Kommunikation.

- `createProject(name)` — POST /api/projects
- `connect(projectId)` — WebSocket /ws/session/{projectId}
- `sendMessage(projectId, message)` — Sendet Turn, sammelt Events
- `getArtifacts(projectId)` — GET /api/projects/{id}/artifacts
- Sammelt 6 Events pro Turn (chat_done, artifact_update, progress_update, debug_update, etc.)
- Erkennt Auto-Moderator-Batch nach phase_complete und preserviert Flags

### Live-Persona-Runner (`run-live-persona.ts`)

Dynamischer E2E-Test mit LLM-generierter Persona.

**Ablauf:**
1. Playbook laden, Persona-Name extrahieren
2. Projekt erstellen, WebSocket verbinden
3. Begrüßung empfangen
4. Loop: Explorer-Frage → Persona-LLM generiert Antwort → Antwort ans Backend
5. Bis `phase_complete` oder max-turns erreicht
6. Artefakte abrufen, Report generieren

**Report-Inhalte:**
- Zusammenfassung mit Ergebnis (BESTANDEN / BESTANDEN MIT LÜCKEN / LÜCKENHAFT / HALLUZINATION)
- Pflichtbegriff-Check pro Slot
- Halluzinations-Check
- Vollständiger Dialog (Explorer-Frage + Persona-Antwort pro Turn)
- Soll/Ist-Vergleich pro Slot
- Artefakt-Rohdaten als JSON

**Verwendung:**
```bash
# API-Key setzen (aus Backend .env)
source backend/.env
export OPENAI_API_KEY=$LLM_API_KEY

# Test starten
npx tsx e2e/run-live-persona.ts --playbook agent-docs/e2e-playbook-reklamationen.md

# Optionen
--max-turns 15        # Max. Turns (default: 20)
--model gpt-4.1       # Persona-Model (default: gpt-4.1-mini)
--output ./reports    # Report-Verzeichnis
```

### ScenarioRunner (`scenario-runner.ts`)

Führt vorgeskriptete Szenarien aus JSON-Dateien aus.

- Sendet Turns sequentiell
- Unterstützt Nudges (Nachfrage-Prompts wenn phase_complete ausbleibt)
- Evaluiert Turn-Expectations und BehaviorProbes
- Erkennt phase_complete über Flags UND phasenstatus

**Verwendung:**
```bash
BACKEND_URL=http://127.0.0.1:8000 npx tsx e2e/run-campaign.ts --scenario S09 --verbose
```

### AssertionEvaluator (`assertion-evaluator.ts`)

7 deterministische Prüfregeln:
1. Moduswechsel nur bei Flags
2. Phasenwechsel via Moderator
3. Moderator schreibt keine Artefakte
4. Systemsprache Deutsch
5. Output-Kontrakt (kein JSON-Dump im Chat)
6. Artefakt-Integrität
7. EMMA-Kompatibilität

## Konfiguration

| Variable | Default | Beschreibung |
|----------|---------|-------------|
| `BACKEND_URL` | `http://127.0.0.1:8000` | Backend-URL |
| `OPENAI_API_KEY` / `LLM_API_KEY` | — | API-Key für Persona-LLM |
| `PERSONA_MODEL` | `gpt-4.1-mini` | Modell für Persona-Antworten |

## Voraussetzungen

- Node.js ≥ 18
- Laufendes Backend (`python -m uvicorn api.main:app`)
- OpenAI API-Key (für Live-Persona)
- `npm install` in `e2e/`

## Scripted vs. Live-Persona

| Aspekt | Scripted | Live-Persona |
|--------|----------|--------------|
| Antworten | Vorgeskriptet in JSON | Dynamisch vom LLM generiert |
| Realismus | Niedrig (reagiert nicht auf Fragen) | Hoch (natürliches Gespräch) |
| Reproduzierbarkeit | Exakt | Variiert (LLM-abhängig) |
| Wiederholungsprobleme | Häufig (Frage-Antwort-Mismatch) | Selten |
| Assertions | 7 deterministische Regeln | Keyword-basierter Soll/Ist-Vergleich |
| Kosten pro Run | Nur Backend-LLM | Backend-LLM + Persona-LLM |
| Empfohlen für | Regressionstests, CI/CD | Qualitätstests, Prompt-Kalibrierung |
