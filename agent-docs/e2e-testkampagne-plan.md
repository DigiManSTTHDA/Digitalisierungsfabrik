# E2E Testkampagne — Digitalisierungsfabrik

## Vision

Ein **Testkampagnen-Framework** das beliebig viele Szenarien durch den Browser schickt, dabei bei **jedem Turn** den kompletten Systemzustand protokolliert (Dialog + Debug-Panel + Artefakte), und am Ende einen aggregierten Kampagnenbericht erzeugt. Ziel: verstehen wie sich das System ueber verschiedene Prozesse, Nutzertypen und Situationen verhaelt. Problemmuster erkennen.

## Architektur

```
Szenario-Definition (JSON)     →  Playwright Test-Runner  →  Kampagnen-Report (Markdown)
(Prozess, Nutzerverhalten,         (Browser-Automation,       (pro Szenario + aggregiert)
 Eskalationen, Widersprueche)       State-Capture)
```

### Szenario-Format

Jedes Szenario ist eine JSON-Datei mit:
- **Metadaten:** Name, Beschreibung, erwartete Schwierigkeit
- **Phasen-Eingaben:** Geordnete Nachrichten pro Phase
- **Aktionen:** Panik-Button, Nudges fuer phase_complete
- **Erwartungen (optional):** Soll-Keywords fuer Artefakte (weiche Pruefung)

```typescript
interface Scenario {
  id: string;
  name: string;
  description: string;           // Was wird getestet?
  tags: string[];                // z.B. ['happy-path', 'edge-case', 'escalation']
  phases: {
    exploration: Turn[];
    strukturierung: Turn[];
    spezifikation: Turn[];
  };
  expectations?: {               // Optional: wenn vorhanden, wird validiert
    exploration_keywords?: Record<string, string[]>;
    min_structure_steps?: number;
    min_algorithm_sections?: number;
    hallucination_keywords?: string[];
  };
}

interface Turn {
  id: string;                    // z.B. "E1-04"
  message: string;               // Nachricht an das System
  action?: 'panic';              // Panik-Button NACH der Nachricht druecken
  nudges?: string[];             // Falls phase_complete nicht kommt
  note?: string;                 // Testnotiz (warum dieser Turn interessant ist)
}
```

### Geplante Szenarien (erste Kampagne)

| # | Szenario | Tags | Was es testet |
|---|----------|------|---------------|
| S01 | Eingangsrechnung (Playbook) | baseline, escalation, contradiction | Referenz-Szenario aus dem Human Playbook. Dreistufige Freigabe, ELO-Medienbruch, 3 Eskalationen, 1 Widerspruch. |
| S02 | Reisekostenabrechnung (einfach) | happy-path, simple | Einfacher Prozess: Antrag → Genehmigung → Buchung. Keine Eskalation. Kooperativer Nutzer. Testet: normaler Durchlauf ohne Komplikationen. |
| S03 | Einstellung neuer Mitarbeiter (komplex) | complex, many-steps | Viele Schritte: Vertrag, IT-Einrichtung, Zugaenge, Einarbeitung. Entscheidungen, Schleifen. Testet: Systemverhalten bei komplexen Prozessen. |
| S04 | Ungeduldiger Nutzer | edge-case, user-behavior | Kurze Antworten, will abkuerzen, sagt "reicht das nicht?". Testet: Haelt das System den Nutzer in der Spur? Fragt es nach? |
| S05 | Widerspruchsreicher Nutzer | edge-case, contradiction | Nutzer widerspricht sich mehrfach, korrigiert eigene Aussagen. Testet: Artefakt-Integritaet bei Updates. |
| S06 | Nur Exploration (Abbruch) | edge-case, partial | Nutzer macht nur Phase 1 fertig und bricht dann ab. Testet: Ist der Zustand konsistent? Kann man spaeter weitermachen? |
| S07 | Minimaler Prozess | edge-case, minimal | "Ich drucke ein Dokument aus." Minimalst-Prozess. Testet: Kommt das System mit fast nichts klar? |
| S08 | Nutzer der auf Englisch antwortet | edge-case, language | Einige Antworten auf Englisch. Testet: Bleibt das System bei Deutsch (FR-A-08)? |

### Was pro Turn erfasst wird

Bei **jedem Turn** (Nachricht senden + Antwort empfangen) wird aufgezeichnet:

```typescript
interface TurnRecord {
  turn_nr: number;
  timestamp: string;
  scenario_id: string;
  phase: string;                      // exploration | strukturierung | spezifikation
  step_id: string;                    // E1-04, E2-03, etc.

  // Eingabe
  user_message: string;
  action?: string;                    // 'panic' wenn Panik-Button gedrueckt

  // System-Antwort
  assistant_response: string;
  response_time_ms: number;           // Wie lange hat der Turn gedauert?

  // Debug-Panel Snapshot (aus dem UI gelesen)
  debug: {
    aktiver_modus: string;            // moderator | exploration | structuring | specification
    phasenstatus: string;             // in_progress | nearing_completion | phase_complete
    befuellte_slots: number;
    bekannte_slots: number;
    flags: string[];                  // artefakt_updated, phase_complete, escalate, etc.
    working_memory_json: string;      // Kompletter WM-Dump
  };

  // UI-State
  ui: {
    phase_label: string;              // "Exploration", "Strukturierung", etc.
    status_badge: string;             // "In Bearbeitung", "Fast fertig", etc.
    slot_counter: string;             // "3 von 9 Slots befuellt"
    message_count: number;            // Anzahl Nachrichten im Chat
    has_error_banner: boolean;
  };

  // Artefakte (via REST API)
  artifacts_snapshot?: {
    exploration_slot_count: number;
    structure_step_count: number;
    algorithm_section_count: number;
  };
}
```

### Kampagnen-Report

Am Ende aller Szenarien wird ein Markdown-Report erzeugt:

```markdown
# E2E Testkampagne — Ergebnisse
Datum: 2026-03-17
Szenarien: 8 | Turns gesamt: 234 | Laufzeit: 3h 12m

## Zusammenfassung
| Szenario | Turns | Dauer | Phasen erreicht | Auffaelligkeiten |
|----------|-------|-------|-----------------|------------------|
| S01 Eingangsrechnung | 41 | 42m | exp→str→spec | Widerspruch korrekt eingearbeitet |
| S02 Reisekosten | 28 | 31m | exp→str→spec | Sauber durchgelaufen |
| S04 Ungeduldiger Nutzer | 22 | 25m | exp→str | System hat in Str. aufgegeben |
| ... | | | | |

## Problemmuster
1. **Phase-Complete Verzoegerung:** In 5/8 Szenarien brauchte es Nudges
2. **Englische Begriffe:** System nutzt in Phase 3 trotz Eskalation weiter EMMA-Jargon
3. **Antwortlaenge:** Nach Eskalation nur in 3/5 Faellen kuerzer
4. ...

## Detail: S01 Eingangsrechnung
### Dialog-Protokoll
| # | Modus | Nachricht (gekuerzt) | Antwort (gekuerzt) | Slots | Flags |
|---|-------|---------------------|---------------------|-------|-------|
| 1 | moderator | "Moment, bevor wir..." | "Gerne erklaere..." | 0/9 | - |
| 2 | moderator | "Ok der Prozess..." | "Verstanden. Sollen..." | 0/9 | - |
| 3 | exploration | "Ja, legen wir los" | "Wunderbar! Lassen..." | 0/9 | - |
| ... | | | | | |

### Artefakt-Zustand nach Phase 1
(Slot-Inhalte + Keywords-Match)

### Artefakt-Zustand nach Phase 2
(Schritte + Typen + Nachfolger)

### Artefakt-Zustand nach Phase 3
(Abschnitte + EMMA-Typen + Widerspruch-Check)
```

## Implementierungsschritte

### Schritt 1: Playwright Setup

**`frontend/package.json`** — Dependencies + Scripts:
```json
{
  "devDependencies": {
    "@playwright/test": "^1.50.0"
  },
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:headed": "playwright test --headed",
    "test:e2e:report": "playwright show-report",
    "test:e2e:scenario": "playwright test --grep"
  }
}
```

**`frontend/playwright.config.ts`** — NEU:
- `baseURL: 'http://localhost:5173'`
- `timeout: 180_000` (3 Min pro Turn max, wegen LLM)
- `globalTimeout: 3_600_000` (1 Stunde pro Szenario)
- Reporter: `html` mit `screenshot: 'on'`, `trace: 'on-first-retry'`
- Video: `off` (Nutzer will Dialoge, nicht Video)
- Retries: 0
- Workers: 1 (seriell, weil LLM-Backend shared)

### Schritt 2: Szenario-Runner (Kern-Framework)

**`frontend/e2e/framework/scenario-runner.ts`** — NEU:
Das Herzstück: Nimmt ein Szenario und fuehrt es im Browser durch.

```typescript
class ScenarioRunner {
  constructor(page: Page, scenario: Scenario) {}

  async run(): Promise<ScenarioResult> {
    // 1. Projekt erstellen
    // 2. Fuer jede Phase:
    //    a. Jede Nachricht senden + Antwort abwarten
    //    b. Debug-Panel lesen nach jedem Turn
    //    c. Artefakte via API lesen (periodisch, nicht jeden Turn)
    //    d. Panik-Button druecken wenn action === 'panic'
    //    e. Nudges senden wenn phase_complete nicht kommt
    //    f. Turn-Record speichern
    // 3. Artefakte final validieren (wenn expectations vorhanden)
    // 4. Alle TurnRecords + Ergebnis zurueckgeben
  }
}
```

**`frontend/e2e/framework/state-capture.ts`** — NEU:
Liest den kompletten UI-State nach jedem Turn:

```typescript
async function captureState(page: Page, projectId: string): Promise<TurnState> {
  // 1. Debug-Panel: Modus, Phasenstatus, Slots, Flags, Working Memory
  //    Selektoren: '.debug-content p' (zusammenfassung), '.debug-content pre' (JSON)
  // 2. Phase Header: Phase, Slot-Counter, Status-Badge
  //    Selektoren: '.phase-info span', '.slot-counter', '.status-badge'
  // 3. Chat: Letzte Nachricht, Gesamtzahl
  //    Selektoren: '.message.assistant:last-child', '.message'
  // 4. Error Banner: vorhanden?
  //    Selektor: '.error-banner'
  // 5. Artefakte via REST API (periodisch):
  //    GET /api/projects/{id}/artifacts
}
```

### Schritt 3: Page Objects

**`frontend/e2e/pages/project-selection.page.ts`** — NEU:
- `createProject(name)` → Name eingeben, klicken, warten
- `getProjectId()` → ID aus DOM oder API extrahieren

**`frontend/e2e/pages/session.page.ts`** — NEU:
- `sendMessage(text)` → `.chat-input input` fuellen, Button klicken
- `waitForResponse(timeout)` → Warten bis Button nicht mehr "..." zeigt
- `getLastResponse()` → `.message.assistant:last-child` Text
- `clickPanic()` → `.panic-btn` klicken
- `getDebugState()` → Debug-Panel parsen
- `getPhaseInfo()` → Phase-Header parsen
- `isProcessing()` → Button-Text pruefen

### Schritt 4: Kampagnen-Reporter

**`frontend/e2e/framework/campaign-reporter.ts`** — NEU:
Aggregiert alle Szenario-Ergebnisse in einen Kampagnenbericht.

```typescript
class CampaignReporter {
  addScenarioResult(result: ScenarioResult): void;

  // Analysiert Muster ueber alle Szenarien:
  analyzePatterns(): PatternReport;
  // - Phase-Complete-Verhalten (wie oft Nudges noetig?)
  // - Antwortlaengen (vor/nach Eskalation)
  // - Modus-Wechsel-Korrektheit
  // - Artefakt-Wachstum pro Turn
  // - Response-Zeiten
  // - Flags-Verteilung

  writeReport(outputDir: string): void;
  // Schreibt:
  //   campaign-summary.md     — Uebersicht + Problemmuster
  //   scenario-S01.md         — Detail pro Szenario
  //   scenario-S02.md
  //   ...
  //   raw-data.json           — Alle TurnRecords als JSON (maschinenlesbar)
}
```

### Schritt 5: Szenarien definieren

**`frontend/e2e/scenarios/s01-eingangsrechnung.json`** — NEU:
Das Referenz-Szenario aus dem Human Playbook (41 Turns, 3 Eskalationen).

**`frontend/e2e/scenarios/s02-reisekosten.json`** — NEU:
Einfacher Prozess, kooperativer Nutzer, keine Eskalationen.

**`frontend/e2e/scenarios/s03-mitarbeiter-einstellung.json`** — NEU:
Komplexer Prozess mit vielen Schritten, Entscheidungen, Schleifen.

**`frontend/e2e/scenarios/s04-ungeduldiger-nutzer.json`** — NEU:
Kurze Antworten, Ungeduld, "reicht das?", "koennen wir weitermachen?".

**`frontend/e2e/scenarios/s05-widersprueche.json`** — NEU:
Nutzer korrigiert sich mehrfach. Testet Artefakt-Integritaet.

**`frontend/e2e/scenarios/s06-abbruch-nach-phase1.json`** — NEU:
Nur Exploration, dann Abbruch. Konsistenz-Check.

**`frontend/e2e/scenarios/s07-minimaler-prozess.json`** — NEU:
"Ich drucke ein Dokument aus." Minimal-Eingabe.

**`frontend/e2e/scenarios/s08-englisch-antworten.json`** — NEU:
Mischung Deutsch/Englisch. Testet Sprachverhalten.

### Schritt 6: Test-Dateien

**`frontend/e2e/tests/campaign.spec.ts`** — NEU:
Laedt alle Szenarien und fuehrt sie nacheinander aus:

```typescript
import { test } from '@playwright/test';
import { ScenarioRunner } from '../framework/scenario-runner';
import { CampaignReporter } from '../framework/campaign-reporter';

const scenarios = loadAllScenarios('e2e/scenarios/');
const reporter = new CampaignReporter();

for (const scenario of scenarios) {
  test(`Szenario: ${scenario.name}`, async ({ page }) => {
    const runner = new ScenarioRunner(page, scenario);
    const result = await runner.run();
    reporter.addScenarioResult(result);
  });
}

test.afterAll(async () => {
  reporter.writeReport('e2e/reports/');
});
```

Einzelnes Szenario ausfuehren:
```bash
npm run test:e2e:scenario -- "S01"
```

### Schritt 7: Artefakt-Validierung

**`frontend/e2e/framework/artifact-validator.ts`** — NEU:
Weiche Validierung (Keyword-Matching, nicht exakt):

```typescript
function validateArtifacts(artifacts, expectations): ValidationResult {
  // Exploration: Keywords pro Slot pruefen
  // Struktur: Mindest-Schritte, Typ-Vielfalt, Nachfolger-Integritaet
  // Algorithmus: Mindest-Abschnitte, EMMA-Typen, struktur_refs
  // Halluzinations-Check: Verbotene Keywords
}
```

## Dateistruktur

```
frontend/
  playwright.config.ts
  e2e/
    framework/                        # Wiederverwendbares Framework
      scenario-runner.ts              # Kern: Szenario durch Browser fuehren
      state-capture.ts                # UI-State lesen (Debug, Phase, Chat)
      campaign-reporter.ts            # Kampagnen-Report erzeugen
      artifact-validator.ts           # Keyword-basierte Artefakt-Pruefung
      types.ts                        # Scenario, Turn, TurnRecord, etc.
    pages/                            # Page Objects
      project-selection.page.ts
      session.page.ts
    scenarios/                        # Szenario-Definitionen (JSON)
      s01-eingangsrechnung.json       # Playbook-Referenz
      s02-reisekosten.json            # Happy Path, einfach
      s03-mitarbeiter-einstellung.json # Komplex
      s04-ungeduldiger-nutzer.json    # Edge: Ungeduld
      s05-widersprueche.json          # Edge: Korrekturen
      s06-abbruch-phase1.json         # Edge: Abbruch
      s07-minimaler-prozess.json      # Edge: Minimal
      s08-englisch-antworten.json     # Edge: Sprache
    tests/
      campaign.spec.ts                # Kampagnen-Runner
    reports/                          # Generiert (.gitignore'd)
      campaign-summary.md
      scenario-S01.md
      scenario-S02.md
      ...
      raw-data.json
```

## Aenderungen an bestehenden Dateien

- `frontend/package.json` — `@playwright/test` + Scripts
- `frontend/.gitignore` — `e2e/reports/`, `test-results/`, `playwright-report/`

## Ausfuehrung

```bash
# Setup (einmalig)
cd frontend && npm install && npx playwright install chromium

# Backend + Frontend muessen laufen:
# Terminal 1: cd backend && source .venv/bin/activate && uvicorn main:app --reload
# Terminal 2: cd frontend && npm run dev

# Komplette Kampagne (alle Szenarien, ~3-4h):
npm run test:e2e

# Einzelnes Szenario (~30-60min):
npm run test:e2e:scenario -- "S01"

# Headed (Browser sichtbar):
npm run test:e2e:headed

# Reports anschauen:
cat e2e/reports/campaign-summary.md      # Kampagnen-Ueberblick
cat e2e/reports/scenario-S01.md          # Detail-Protokoll
npm run test:e2e:report                  # Playwright HTML-Report
```

## Was der Report zeigt

**Pro Szenario:**
- Vollstaendiger Dialog (User + System, Schritt fuer Schritt)
- Debug-State bei jedem Turn (Modus, Phase, Slots, Flags, Working Memory)
- Artefakt-Zustand nach jeder Phase
- Response-Zeiten
- Auffaelligkeiten (Eskalation, Modus-Fehler, Nudges noetig)

**Aggregiert ueber alle Szenarien:**
- Muster: Wo braucht es Nudges? Wo haengt das System?
- Modus-Wechsel: Korrekt in X% der Faelle?
- Eskalationsverhalten: Moderator verhaelt sich korrekt?
- Sprachverhalten: Antwortet auf Deutsch? Erklaert EMMA-Begriffe?
- Artefakt-Qualitaet: Keywords-Abdeckung ueber alle Szenarien
- Performance: Durchschnittliche Response-Zeiten pro Phase
