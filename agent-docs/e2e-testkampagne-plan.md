# E2E Testkampagne — Digitalisierungsfabrik

## Intentio

Das System hat einen klaren Auftrag (SDD 1.1): Implizites Prozesswissen eines Fachanwenders schrittweise in einen EMMA-kompatiblen Algorithmus ueberfuehren. Der Weg geht ueber vier Phasen — Exploration, Strukturierung, Spezifikation, Validierung — gesteuert von einem deterministischen Orchestrator, vermittelt durch einen Moderator.

Die E2E-Tests bewerten, **wie gut das System diesen Auftrag erfuellt**. Das ist keine reine Assertion-Aufgabe. Es ist eine **Verhaltensbeurteilung** — wie ein Business Process Analyst, der beobachtet ob der Dialog sein Ziel erreicht, wo er hakt, wo die UX holprig ist, und wo die Artefaktqualitaet nicht stimmt.

## Zwei Bewertungsebenen

### Ebene 1: Deterministische Assertions (hart)

Dinge die das System laut SDD **immer korrekt tun muss** — regelbasiert, deterministisch, pruefbar:

| Was | SDD-Referenz | Assertion |
|-----|-------------|-----------|
| Orchestrator wechselt Modus nur bei definierten Flags | 6.3 Moduswechsel-Logik | `aktiver_modus` aendert sich nur nach `phase_complete`, `escalate`, `blocked` |
| Phasenwechsel nur nach Nutzerbestaetigung via Moderator | 6.1.2 | Zwischen `phase_complete`-Flag und neuem Modus liegt mindestens ein Moderator-Turn mit Nutzerbestaetigung |
| Artefakte wachsen monoton (keine unbegruendeten Loeschungen) | 5.2, FR-B-04 | `befuellte_slots` sinkt nie ohne expliziten Nutzereingriff |
| Moderator veraendert keine Artefakte | 6.6.5 | Waehrend `aktiver_modus === moderator` bleibt `artefakt_updated`-Flag immer aus |
| Systemsprache bleibt Deutsch | 1.3, FR-A-08 | Systemantworten sind auf Deutsch (Pruefung via Sprachdetektions-Heuristik) |
| Debug-Panel spiegelt Working Memory korrekt | FR-F-01 | UI-Phasenlabel === Working-Memory-Phase, Slot-Zaehler === berechneter Wert |
| Output-Kontrakt wird eingehalten | 6.5.2 | Keine Artefakt-Dumps im Chat, strukturierter Output mit Flags |

### Ebene 2: Verhaltensbeurteilung (weich)

Qualitaeten die nicht mit `assert()` pruefbar sind, aber ueber Erfolg oder Scheitern des Systems entscheiden:

#### A. Dialogfuehrung — "Fuehrt das System den Nutzer oder verliert es ihn?"

| Kriterium | Was beobachtet wird | Bewertungslogik |
|-----------|---------------------|-----------------|
| **Gezielte Fragen** | Stellt der Explorationsmodus praezise Fragen die Slots fuellen? Oder stellt er generische Fragen? | Turn-Analyse: Ratio von Turns mit `artefakt_updated` zu Turns ohne. Niedrige Ratio = System fragt ins Leere. |
| **Keine Wiederholungen** | Fragt das System nochmal nach etwas das schon beantwortet wurde? | Semantischer Vergleich aufeinanderfolgender Fragen — Wiederholungsmuster erkennen. |
| **Umgang mit Ungeduld** | Wenn der Nutzer abkuerzen will — haelt das System den Kurs oder gibt es auf? | Szenario S04: Wird `phase_complete` gesetzt obwohl Slots fehlen? Verliert das System den Nutzer? |
| **Umgang mit Widerspruechen** | Erkennt das System Widersprueche? Loest es sie auf? | Szenario S05: Wird nach Korrektur das Artefakt korrekt aktualisiert? Bleibt alter Zustand stehen? |
| **Antwortlaenge** | Sind die Antworten angemessen lang? Oder ueberfordern sie den Fachanwender? | Zeichenzahl pro Antwort. Nach Eskalation ("zu lang!"): wird sie kuerzer? |

#### B. Moderatorverhalten — "Vermittelt der Moderator oder nervt er?"

| Kriterium | Was beobachtet wird | Bewertungslogik |
|-----------|---------------------|-----------------|
| **Orientierung geben** | Erklaert der Moderator dem Nutzer wo er steht, was erreicht wurde, was kommt? | Phasenwechsel-Turns pruefen: Enthaelt die Antwort eine Zusammenfassung + Vorschlag? |
| **Nicht bevormundend** | Gibt der Moderator Kontrolle zurueck wenn der Nutzer bestaetigt? Oder haelt er unnoetig fest? | Laenge der Moderator-Phase: Wie viele Turns bis Rueckgabe? Mehr als 3 = auffaellig. |
| **Panik-Button Reaktion** | Reagiert der Moderator angemessen auf Eskalation? Analysiert er die Situation? | S01 Eskalationen: Erkennt der Moderator das Problem? Schlaegt er eine Loesung vor? |
| **Ruecksprung-Qualitaet** | Wenn ein Ruecksprung noetig ist — erklaert der Moderator die Konsequenzen? | Werden Artefakt-Konsequenzen (6.1.4) kommuniziert? |

#### C. Artefaktqualitaet — "Ist das Ergebnis brauchbar?"

| Kriterium | Was beobachtet wird | Bewertungslogik |
|-----------|---------------------|-----------------|
| **Slot-Vollstaendigkeit** | Sind am Phasenende alle Pflichtslots gefuellt? | Completeness-State nach `phase_complete`: Ratio `nutzervalidiert` / `pflicht-gesamt` |
| **Inhaltliche Praezision** | Steht in den Slots das was der Nutzer gesagt hat — oder hat das LLM halluziniert? | Keyword-Abgleich: Nutzernachrichten vs. Slot-Inhalte. Keywords die der Nutzer verwendet hat muessen im Artefakt auftauchen. |
| **Keine Halluzination** | Hat das System Prozessschritte erfunden die der Nutzer nie erwaehnt hat? | Verbotene Keywords: Begriffe die im Szenario nie fallen, aber im Artefakt auftauchen. |
| **Strukturelle Integritaet** | Stimmen die Nachfolger-Referenzen? Gibt es Waisen? | Deterministisch pruefbar: Jeder `nachfolger_id` muss auf existierenden Schritt zeigen. Jeder Schritt ausser Ende muss Nachfolger haben. |
| **EMMA-Kompatibilitaet** | Verwendet das Algorithmusartefakt gueltige EMMA-Aktionstypen? | Deterministisch: Alle `emma_aktion.typ`-Werte gegen Katalog (SDD 8.3) pruefen. |
| **Artefakt-Wachstumskurve** | Waechst das Artefakt stetig oder in Spruengen? | Befuellte Slots pro Turn plotten. Lange Plateaus = System stagniert. |

#### D. UX-Bewertung — "Ist der Ablauf fluessig oder holprig?"

| Kriterium | Was beobachtet wird | Bewertungslogik |
|-----------|---------------------|-----------------|
| **Nudge-Bedarf** | Wie oft muss der Nutzer nachhelfen damit `phase_complete` kommt? | Zaehler: Nudge-Messages pro Szenario. Mehr als 2 = Phase-Complete-Erkennung hat Schwaeche. |
| **Response-Zeiten** | Wie lange wartet der Nutzer? Gibt es Ausreisser? | Median + P95 pro Phase. Deutlich > 30s = UX-Problem. |
| **Modus-Ping-Pong** | Wechselt der Modus hin und her ohne Fortschritt? | Pattern: Gleicher Modus → Moderator → gleicher Modus ohne Slot-Aenderung dazwischen. |
| **Error-Recovery** | Wenn ein Fehler auftritt — kann der Nutzer weitermachen? | Error-Banner-Haeufigkeit. System muss nach Fehler weiterarbeiten koennen. |

## Architektur

```
Szenario (JSON)  →  WebSocket-Client  →  Backend/Orchestrator  →  LLM (echte API-Calls)
     |                    |                      |                        |
     |                    ↓                      ↓                        ↓
     |              Turn-Protokoll          State-Capture            echte Antworten
     |              (Dialog-Log)        (WM, Artefakte, Flags)    (nicht-deterministisch)
     |                    |                      |
     ↓                    ↓                      ↓
Bewertungsmatrix  ←  Kampagnen-Reporter  ←  Rohdaten (JSON)
(Assertions +          (Aggregation +         (alle TurnRecords,
 Verhaltensbewertung)   Musteranalyse)         Artefakt-Snapshots)
```

**Kein Browser.** Die Tests laufen direkt gegen die WebSocket-API des Backends. Der Orchestrator, die LLM-Calls, die Artefakt-Persistenz — alles echt. Nur die Browser-Schicht wird umgangen. Das ist kein UI-Test, sondern ein **Systemverhaltenstest**.

### Szenario-Format

```typescript
interface Scenario {
  id: string;
  name: string;
  description: string;
  tags: string[];
  // Intentio: Was soll am Ende rauskommen? Dient als Bewertungsmassstab.
  intent: {
    process_description: string;     // "Dreistufige Rechnungsfreigabe mit ELO-Medienbruch"
    expected_structure_steps: number; // Grobe Erwartung: ~12 Schritte
    expected_complexity: 'minimal' | 'einfach' | 'mittel' | 'komplex';
    key_concepts: string[];          // Begriffe die im Artefakt auftauchen MUESSEN
    forbidden_concepts: string[];    // Begriffe die NICHT auftauchen duerfen (Halluzinations-Check)
  };
  phases: {
    exploration: Turn[];
    strukturierung: Turn[];
    spezifikation: Turn[];
    validierung?: Turn[];            // Optional — Validierung laeuft oft automatisch
  };
  behavior_probes: BehaviorProbe[];  // Gezielte Verhaltenspruefungen (s. unten)
}

interface Turn {
  id: string;                        // z.B. "E1-04"
  message: string;                   // Nachricht an das System
  action?: 'panic';                  // Panik-Button NACH der Nachricht druecken
  nudges?: string[];                 // Falls phase_complete nicht kommt
  note?: string;                     // Testnotiz: warum ist dieser Turn interessant?
  expect?: TurnExpectation;          // Optionale Erwartung fuer diesen spezifischen Turn
}

// Gezielte Erwartung an einen einzelnen Turn
interface TurnExpectation {
  mode_should_be?: string;           // "exploration", "moderator", etc.
  flag_should_include?: string[];    // ["artefakt_updated"]
  flag_should_not_include?: string[];// ["phase_complete"] — z.B. wenn noch Slots fehlen
  slots_should_increase?: boolean;   // Erwarte dass mindestens 1 neuer Slot gefuellt wird
  response_should_contain?: string[];// Keywords in der Antwort
  response_should_not_contain?: string[];
}

// Verhaltenspruefung die NACH einem bestimmten Turn ausgewertet wird
interface BehaviorProbe {
  after_turn: string;                // Turn-ID, z.B. "E1-12"
  name: string;                      // z.B. "Widerspruch erkannt?"
  type: 'artifact_check' | 'dialog_check' | 'state_check';
  check: {
    // artifact_check: Ist ein bestimmter Inhalt im Artefakt?
    slot_path?: string;              // z.B. "exploration.slots.beteiligte_systeme"
    should_contain?: string[];
    should_not_contain?: string[];
    // dialog_check: Hat das System etwas bestimmtes gesagt/gefragt?
    response_pattern?: string;       // Regex auf die letzte Systemantwort
    // state_check: Ist der Systemzustand korrekt?
    expected_phase?: string;
    expected_mode?: string;
    min_filled_slots?: number;
  };
}
```

### Was pro Turn erfasst wird

```typescript
interface TurnRecord {
  turn_nr: number;
  timestamp: string;
  scenario_id: string;
  phase: string;
  step_id: string;

  // Eingabe
  user_message: string;
  action?: string;

  // System-Antwort
  assistant_response: string;
  response_time_ms: number;

  // Systemzustand (via API / WebSocket-Response)
  state: {
    aktiver_modus: string;
    aktive_phase: string;
    phasenstatus: string;
    befuellte_slots: number;
    bekannte_slots: number;
    flags: string[];
    working_memory: object;
  };

  // Artefakt-Snapshot (periodisch, nicht jeden Turn)
  artifacts?: {
    exploration: object;             // Vollstaendiger Artefakt-Inhalt
    struktur: object;
    algorithmus: object;
  };

  // Bewertung (wird nach dem Turn berechnet)
  evaluation: {
    assertions_passed: string[];     // Welche harten Assertions bestanden
    assertions_failed: string[];     // Welche harten Assertions fehlgeschlagen
    behavior_probes: {               // Ergebnisse der Verhaltenspruefungen
      name: string;
      passed: boolean;
      detail: string;
    }[];
    metrics: {
      response_length: number;       // Zeichenzahl der Antwort
      slots_delta: number;           // Wie viele Slots seit letztem Turn dazugekommen?
      mode_changed: boolean;         // Hat sich der Modus geaendert?
      nudge_used: boolean;           // Musste ein Nudge gesendet werden?
    };
  };
}
```

## Geplante Szenarien (erste Kampagne)

Jedes Szenario hat eine klare **Testabsicht** — nicht einfach "durchlaufen lassen", sondern gezielt Verhalten provozieren und bewerten.

| # | Szenario | Testabsicht | Verhaltensfokus |
|---|----------|-------------|-----------------|
| S01 | Eingangsrechnung (Referenz) | Vollstaendiger Durchlauf mit Eskalationen. Baseline fuer alle Bewertungsdimensionen. | Moderatorverhalten bei 3 Eskalationen, Widerspruchsaufloesung, Artefaktqualitaet ueber alle Phasen |
| S02 | Reisekostenabrechnung | Happy Path. Kooperativer Nutzer, keine Komplikationen. | Wie effizient ist das System wenn nichts schiefgeht? Wie viele Turns braucht es? Slot-Effizienz. |
| S03 | Mitarbeiter-Einstellung | Komplexer Prozess mit vielen Schritten. | Skaliert das System? Bleibt die Artefaktqualitaet bei >15 Strukturschritten? Nachfolger-Integritaet? |
| S04 | Ungeduldiger Nutzer | Nutzer will abkuerzen: kurze Antworten, "reicht das?", "weiter!". | Haelt das System den Kurs? Setzt es `phase_complete` obwohl Slots fehlen? Oder fragt es richtig nach? |
| S05 | Widersprueche | Nutzer korrigiert sich 3x. | Wird das Artefakt korrekt aktualisiert? Oder bleiben Altlasten stehen? Erkennt das System den Widerspruch explizit? |
| S06 | Abbruch nach Phase 1 | Nur Exploration, dann Stop. | Ist der Zustand konsistent? Koennte man spaeter weitermachen? Kein Zombie-State? |
| S07 | Minimaler Prozess | "Ich drucke ein Dokument aus." | Kommt das System mit fast nichts klar? Erzeugt es trotzdem gueltige Artefakte? Oder halluziniert es Komplexitaet? |
| S08 | Englisch-Antworten | Nutzer antwortet teilweise auf Englisch. | Bleibt das System bei Deutsch (FR-A-08)? Wandelt es englische Begriffe korrekt um? |

## Kampagnen-Report

Der Report hat zwei Teile: **Befundliste** (was ist passiert) und **Bewertungsmatrix** (wie gut war es).

### Teil 1: Befundliste (pro Szenario)

```markdown
# Szenario S01 — Eingangsrechnung

## Eckdaten
- Turns: 41 | Dauer: 42m | Phasen erreicht: exp → str → spec → val
- Nudges benoetig: 2 (Phase 1 Turn 18, Phase 2 Turn 29)
- Eskalationen: 3 (Turn 8, 22, 35) — alle vom Moderator aufgeloest

## Assertion-Ergebnisse
| Assertion | Status | Detail |
|-----------|--------|--------|
| Moduswechsel nur bei Flags | PASS | 6/6 Wechsel korrekt |
| Phasenwechsel via Moderator | PASS | 3/3 Phasenwechsel korrekt |
| Moderator schreibt keine Artefakte | PASS | 0 artefakt_updated waehrend Moderator |
| Systemsprache Deutsch | WARN | Turn 31: "Next, we need to..." (1 Satz Englisch) |
| Output-Kontrakt | PASS | Kein Artefakt-Dump im Chat |

## Verhaltensbewertung
| Dimension | Bewertung | Begruendung |
|-----------|-----------|-------------|
| Dialogfuehrung | GUT | 78% der Turns mit artefakt_updated. 2 unnoetige Wiederholungsfragen (Turn 6, 14). |
| Moderatorverhalten | SEHR GUT | Alle 3 Eskalationen sauber aufgeloest. Phasenwechsel mit Zusammenfassung. |
| Artefaktqualitaet | GUT | 9/9 Pflichtslots gefuellt. Widerspruch in Turn 22 korrekt eingearbeitet. 1 Keyword fehlt ("ELO"). |
| UX-Fluessigkeit | BEFRIEDIGEND | 2 Nudges noetig. Median Response 18s, P95 45s. Kein Modus-Ping-Pong. |

## Dialog-Protokoll (gekuerzt)
| # | Modus | User (Auszug) | System (Auszug) | Slots | Flags | Bemerkung |
|---|-------|--------------|-----------------|-------|-------|-----------|
| 1 | moderator | — | "Willkommen! Lassen..." | 0/9 | — | Begruessung OK |
| 2 | moderator | "Ok, los gehts" | "Verstanden. Wir..." | 0/9 | — | Uebergabe an Exploration |
| 3 | exploration | "Der Prozess beginnt..." | "Verstehe. Wer..." | 1/9 | artefakt_updated | Slot 'prozessziel' gefuellt |
| ... | | | | | | |

## Artefakt-Snapshot nach Phase 1
(Vollstaendiger Slot-Inhalt + Completeness-State)

## Artefakt-Snapshot nach Phase 2
(Strukturschritte + Typen + Nachfolger-Graph)

## Artefakt-Snapshot nach Phase 3
(Algorithmusabschnitte + EMMA-Aktionen + struktur_refs)
```

### Teil 2: Bewertungsmatrix (aggregiert ueber alle Szenarien)

```markdown
# Kampagnen-Bewertung

## Bewertungsmatrix
| Dimension | S01 | S02 | S03 | S04 | S05 | S06 | S07 | S08 | Muster |
|-----------|-----|-----|-----|-----|-----|-----|-----|-----|--------|
| Dialogfuehrung | GUT | SEHR GUT | GUT | MANGELHAFT | GUT | GUT | BEFR. | GUT | S04: System gibt bei Ungeduld auf |
| Moderator | SEHR GUT | GUT | GUT | — | GUT | — | — | GUT | Konsistent gut |
| Artefaktqualitaet | GUT | SEHR GUT | BEFR. | MANGELHAFT | GUT | GUT | BEFR. | GUT | Qualitaet sinkt bei Komplexitaet (S03) und Druck (S04) |
| UX-Fluessigkeit | BEFR. | GUT | BEFR. | MANGELHAFT | GUT | GUT | GUT | GUT | Nudge-Problem in Phase 1 (5/8 Szenarien) |

## Erkannte Problemmuster
1. **Phase-Complete-Verzoegerung** (5/8 Szenarien): Explorationsmodus setzt phase_complete zu spaet.
   → Ursache: Modus wartet auf explizite Nutzervalidierung aller Slots, aber validiert nicht aktiv genug.
2. **Ungeduldiger Nutzer bricht System** (S04): Bei kurzen Antworten fuellt das System Slots mit Annahmen.
   → SDD-Verletzung: 1.1 "stellt keine unbegruendeten Annahmen auf"
3. **EMMA-Jargon im Chat** (S03, S08): System erklaert EMMA-Aktionstypen nicht.
   → UX-Problem: Fachanwender versteht "sequenz_aktion" nicht.
4. ...

## Empfehlungen
1. Phase-Complete-Logik ueberarbeiten: Explorationsmodus soll aktiver nach Vollstaendigkeit fragen.
2. Systemprompt-Anpassung: Bei kurzen Antworten nachfragen, nicht annehmen.
3. EMMA-Begriffe im Chat uebersetzen / erklaeren.
```

## Implementierungsplan

### Schritt 1: WebSocket-Client + Typen

**`e2e/framework/types.ts`** — Alle Interfaces (Scenario, Turn, TurnRecord, BehaviorProbe, etc.)

**`e2e/framework/ws-client.ts`** — WebSocket-Client der direkt mit dem Backend kommuniziert:
```typescript
class SessionClient {
  constructor(baseUrl: string) {}

  async createProject(name: string): Promise<string>;   // → project_id
  async sendMessage(projectId: string, message: string): Promise<TurnResponse>;
  async pressButton(projectId: string, button: 'panic'): Promise<TurnResponse>;
  async getArtifacts(projectId: string): Promise<Artifacts>;
  async getWorkingMemory(projectId: string): Promise<WorkingMemory>;
}
```

### Schritt 2: Szenario-Runner

**`e2e/framework/scenario-runner.ts`** — Kern:
```typescript
class ScenarioRunner {
  constructor(client: SessionClient, scenario: Scenario) {}

  async run(): Promise<ScenarioResult> {
    // 1. Projekt erstellen
    // 2. Fuer jede Phase:
    //    a. Jede Nachricht senden via WebSocket
    //    b. Systemzustand nach jedem Turn erfassen (WM, Flags)
    //    c. Artefakte periodisch lesen
    //    d. Panik-Button druecken wenn action === 'panic'
    //    e. Nudges senden wenn phase_complete nicht kommt
    //    f. Turn-Expectations und BehaviorProbes auswerten
    //    g. TurnRecord speichern
    // 3. Final: Artefakte vollstaendig lesen und gegen intent pruefen
    // 4. Alle TurnRecords + Bewertung zurueckgeben
  }
}
```

### Schritt 3: Evaluator

**`e2e/framework/evaluator.ts`** — Zwei Klassen:

```typescript
// Harte Assertions — pass/fail
class AssertionEvaluator {
  // Prueft deterministische Regeln gegen TurnRecord-Sequenz
  checkModeTransitions(records: TurnRecord[]): AssertionResult[];
  checkPhaseTransitions(records: TurnRecord[]): AssertionResult[];
  checkModeratorNoWrite(records: TurnRecord[]): AssertionResult[];
  checkLanguage(records: TurnRecord[]): AssertionResult[];
  checkOutputContract(records: TurnRecord[]): AssertionResult[];
  checkArtifactIntegrity(artifacts: Artifacts): AssertionResult[];
  checkEMMACompatibility(artifacts: Artifacts): AssertionResult[];
}

// Weiche Verhaltensbewertung — Skala
class BehaviorEvaluator {
  evaluateDialogQuality(records: TurnRecord[]): BehaviorScore;
  evaluateModeratorBehavior(records: TurnRecord[]): BehaviorScore;
  evaluateArtifactQuality(artifacts: Artifacts, intent: ScenarioIntent): BehaviorScore;
  evaluateUXFluency(records: TurnRecord[]): BehaviorScore;
}

interface BehaviorScore {
  dimension: string;
  rating: 'SEHR_GUT' | 'GUT' | 'BEFRIEDIGEND' | 'MANGELHAFT';
  metrics: Record<string, number>;  // z.B. { slot_efficiency: 0.78, nudge_count: 2 }
  findings: string[];               // Freitext-Befunde
}
```

### Schritt 4: Kampagnen-Reporter

**`e2e/framework/campaign-reporter.ts`** — Aggregation + Markdown-Ausgabe:
```typescript
class CampaignReporter {
  addScenarioResult(result: ScenarioResult): void;

  // Aggregiert ueber alle Szenarien:
  analyzePatterns(): {
    assertion_summary: { total: number; passed: number; failed: number; warnings: number };
    behavior_matrix: Record<string, Record<string, BehaviorScore>>;  // Dimension → Szenario → Score
    problem_patterns: string[];      // Uebergreifende Problemmuster
    recommendations: string[];       // Handlungsempfehlungen
  };

  writeReport(outputDir: string): void;
  // Schreibt:
  //   campaign-summary.md         — Bewertungsmatrix + Problemmuster + Empfehlungen
  //   scenario-S01.md             — Befundliste pro Szenario
  //   scenario-S02.md
  //   ...
  //   raw-data.json               — Alle TurnRecords (maschinenlesbar)
}
```

### Schritt 5: Szenarien definieren

**`e2e/scenarios/s01-eingangsrechnung.json`** — Referenz-Szenario (41 Turns, 3 Eskalationen, 1 Widerspruch)
**`e2e/scenarios/s02-reisekosten.json`** — Happy Path
**`e2e/scenarios/s03-mitarbeiter-einstellung.json`** — Komplex (>15 Schritte)
**`e2e/scenarios/s04-ungeduldiger-nutzer.json`** — Druck + Ungeduld
**`e2e/scenarios/s05-widersprueche.json`** — 3 Korrekturen
**`e2e/scenarios/s06-abbruch-phase1.json`** — Nur Exploration
**`e2e/scenarios/s07-minimaler-prozess.json`** — "Ich drucke ein Dokument aus."
**`e2e/scenarios/s08-englisch-antworten.json`** — Sprachmischung

### Schritt 6: Test-Runner (Vitest oder standalone Node.js)

**`e2e/run-campaign.ts`** — Standalone Runner (kein Playwright noetig):
```typescript
import { SessionClient } from './framework/ws-client';
import { ScenarioRunner } from './framework/scenario-runner';
import { CampaignReporter } from './framework/campaign-reporter';

const client = new SessionClient(process.env.BACKEND_URL || 'http://localhost:8000');
const scenarios = loadAllScenarios('e2e/scenarios/');
const reporter = new CampaignReporter();

for (const scenario of scenarios) {
  console.log(`Starte Szenario: ${scenario.name}`);
  const runner = new ScenarioRunner(client, scenario);
  const result = await runner.run();
  reporter.addScenarioResult(result);
  console.log(`Fertig: ${result.summary}`);
}

reporter.writeReport('e2e/reports/');
console.log('Kampagne abgeschlossen. Report: e2e/reports/campaign-summary.md');
```

## Dateistruktur

```
e2e/
  framework/
    types.ts                         # Alle Interfaces
    ws-client.ts                     # WebSocket/HTTP Client zum Backend
    scenario-runner.ts               # Kern: Szenario durchfuehren
    evaluator.ts                     # AssertionEvaluator + BehaviorEvaluator
    campaign-reporter.ts             # Markdown-Report-Generator
  scenarios/
    s01-eingangsrechnung.json
    s02-reisekosten.json
    s03-mitarbeiter-einstellung.json
    s04-ungeduldiger-nutzer.json
    s05-widersprueche.json
    s06-abbruch-phase1.json
    s07-minimaler-prozess.json
    s08-englisch-antworten.json
  reports/                           # Generiert (.gitignore'd)
    campaign-summary.md
    scenario-S01.md
    ...
    raw-data.json
  run-campaign.ts                    # Einstiegspunkt
```

## Ausfuehrung

```bash
# Backend muss laufen:
# cd backend && source .venv/bin/activate && uvicorn main:app --reload

# Komplette Kampagne (alle Szenarien, ~3-4h):
npx tsx e2e/run-campaign.ts

# Einzelnes Szenario:
npx tsx e2e/run-campaign.ts --scenario S01

# Reports lesen:
cat e2e/reports/campaign-summary.md      # Bewertungsmatrix + Problemmuster
cat e2e/reports/scenario-S01.md          # Detail-Befundliste
```

## Zusammenfassung: Was dieser Plan anders macht

| Alter Plan | Neuer Plan |
|------------|------------|
| Playwright-Browser-Automation | WebSocket-Client direkt gegen Backend |
| Assertions als primaere Bewertung | Assertions + Verhaltensbewertung als gleichwertige Saeulen |
| "Hat es funktioniert?" (pass/fail) | "Wie gut hat es funktioniert?" (Bewertungsmatrix) |
| Keyword-Matching auf Artefakte | Intent-basierte Bewertung: Key Concepts, Forbidden Concepts, Halluzinations-Check |
| Generische Szenario-Beschreibung | Jedes Szenario hat eine Testabsicht und einen Verhaltensfokus |
| Report zeigt Dialog-Protokoll | Report zeigt Befundliste + Bewertungsmatrix + Problemmuster + Empfehlungen |
| Keine Turn-Level-Erwartungen | TurnExpectations + BehaviorProbes fuer gezielte Pruefpunkte |
