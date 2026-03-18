# Review: E2E Testkampagne-Plan

**Reviewer:** E2E-Testing-Experte fuer KI-Assistenzsysteme
**Datum:** 2026-03-18
**Gegenstand:** `agent-docs/e2e-testkampagne-plan.md`
**Kontext:** SDD, Human Playbook, Backend-Implementierung (Orchestrator, Modi, WebSocket, API)

---

## Gesamtbewertung

Der Plan ist **konzeptionell stark**. Die Zweiteilung in deterministische Assertions und Verhaltensbewertung ist fuer ein LLM-gestuetztes System genau der richtige Ansatz. Das Szenario-Format (Intent + TurnExpectations + BehaviorProbes) ist durchdacht und erweiterbar. Die Architekturentscheidung, direkt gegen die WebSocket-API zu testen statt ueber einen Browser, ist korrekt — es geht um Systemverhalten, nicht um UI.

Es gibt jedoch **wesentliche Schwaechen** in Vollstaendigkeit, operativer Praezision und Abdeckung von Grenzfaellen, die vor der Implementierung adressiert werden sollten.

---

## Schwaeche 1: Fehlende Validierungsphase und Korrekturschleife

### Problem

Kein einziges Szenario testet die **Validierungsphase** explizit. S01 erwaehnt "exp → str → spec → val" im Beispiel-Report, aber keines der 8 Szenarien definiert Turns fuer die Validierung. Das SDD beschreibt eine komplexe Korrekturschleife:

```
Validierung findet kritische Befunde
  → Moderator praesentiert Befunde
  → Nutzer waehlt: zurueck zur Spezifikation
  → Korrekturen
  → Re-Validierung
  → Wiederholen bis alle kritischen Befunde behoben
```

Das ist einer der kritischsten Pfade des Systems — und er wird nicht getestet.

### Loesungsoptionen

**A) Neues Szenario S09: Validierungs-Korrekturschleife**

Ein Szenario das bewusst ein unvollstaendiges Algorithmus-Artefakt erzeugt (z.B. EMMA-Aktionen ohne Parameter, fehlende Fehlerbehandlung) und dann die Korrekturschleife durchlaeuft:
- Validierung findet kritische Befunde
- Moderator erklaert Befunde
- Ruecksprung zu Spezifikation mit Validierungsbericht als Kontext
- Gezielte Korrekturen
- Re-Validierung → bestanden
- Projekt abgeschlossen

**B) Erweiterung von S01**

S01 als Referenz-Szenario bis zum Projektabschluss durchziehen, inklusive Validierungs-Korrekturschleife. Erhoehte Komplexitaet, aber umfassenderer Baseline-Test.

**Empfehlung:** Option A — separates Szenario, weil die Korrekturschleife ein eigenes Testmuster darstellt und S01 bereits 41 Turns hat.

---

## Schwaeche 2: Nicht-automatisierbare Prozesse werden nicht getestet

### Problem

Ein zentrales Systemrisiko fehlt in der Testabdeckung: **Was passiert, wenn der Nutzer einen Prozess beschreibt, der sich nicht auf RPA abbilden laesst?**

Beispiele:
- Prozess besteht aus rein kognitiven Entscheidungen ("ich schaue mir das an und entscheide nach Gefuehl")
- Prozess erfordert physische Interaktion (z.B. "ich gehe zum Regal und hole die Akte")
- Prozess folgt keiner festen Logik ("jedes Mal anders, kommt drauf an")

Das SDD definiert `emma_kompatibel: false` und `kompatibilitaets_hinweis`, aber kein Szenario prueft ob das System diesen Zustand korrekt erkennt und kommuniziert.

### Loesungsoptionen

**Neues Szenario S10: Nicht-automatisierbarer Prozess**

- Nutzer beschreibt einen Prozess mit ueberwiegend nicht-automatisierbaren Schritten
- System muss Schritte als `emma_kompatibel: false` markieren
- Validierung muss kritische Befunde erzeugen
- System muss dem Nutzer verstaendlich erklaeren, warum der Prozess problematisch ist
- Kein Abbruch mit Fehler, sondern konstruktiver Umgang

**Neues Szenario S11: Chaotischer Prozess**

- Nutzer beschreibt einen Prozess ohne klare Logik ("jedes Mal anders")
- Wie reagiert das System? Halluziniert es eine Struktur? Oder fragt es gezielt nach Regeln?
- Testet die Grenze der Systemzuverlaessigkeit

---

## Schwaeche 3: Modi-Registrierung im Backend ist unvollstaendig

### Problem

Die aktuelle WebSocket-Implementierung (`backend/api/websocket.py:43-46`) registriert nur **zwei Modi**:

```python
modes: dict[str, BaseMode] = {
    "exploration": ExplorationMode(llm_client=llm),
    "moderator": Moderator(llm_client=llm),
}
```

Die Modi `structuring`, `specification` und `validation` existieren als Dateien (`backend/modes/structuring.py`, etc.), sind aber **nicht im Orchestrator verdrahtet**. Die E2E-Tests werden bei jedem Szenario scheitern, das ueber Phase 1 hinausgeht, weil `self._modes.get("structuring")` `None` zurueckgibt und auf den Fallback `exploration` zurueckfaellt.

### Loesungsoptionen

1. **Vor E2E-Implementierung**: Alle Modi im `_build_orchestrator` registrieren
2. **Im Testplan dokumentieren**: Vorbedingung "Alle 5 Modi muessen im Orchestrator registriert sein" als Setup-Requirement definieren
3. **Health-Check im Test-Framework**: Vor Kampagnenstart pruefen ob alle erwarteten Modi verfuegbar sind (z.B. via Debug-Endpoint oder Introspektion)

**Empfehlung:** Option 1 + 3 — Backend-Fix als Voraussetzung, Health-Check als Absicherung.

---

## Schwaeche 4: BehaviorEvaluator hat keine definierten Schwellwerte

### Problem

Der Plan definiert Bewertungskategorien (`SEHR_GUT`, `GUT`, `BEFRIEDIGEND`, `MANGELHAFT`) ohne Schwellwerte:

- Ab welcher Slot-Effizienz ist die Dialogfuehrung "GUT"?
- Ab wie vielen Nudges wird UX-Fluessigkeit "MANGELHAFT"?
- Ab welcher Response-Time wird es ein Problem?
- Was ist eine akzeptable Halluzinationsrate?

Ohne Schwellwerte ist die Bewertungsmatrix nicht reproduzierbar und die Bewertungen haengen vom Implementierer ab.

### Loesungsoptionen

**Schwellwert-Tabelle definieren:**

```
Dialogfuehrung:
  SEHR_GUT:      slot_efficiency >= 0.80 AND wiederholungen == 0
  GUT:           slot_efficiency >= 0.60 AND wiederholungen <= 1
  BEFRIEDIGEND:  slot_efficiency >= 0.40 OR wiederholungen <= 3
  MANGELHAFT:    slot_efficiency < 0.40 OR wiederholungen > 3

UX-Fluessigkeit:
  SEHR_GUT:      nudge_count == 0 AND median_response_ms < 15000
  GUT:           nudge_count <= 1 AND median_response_ms < 25000
  BEFRIEDIGEND:  nudge_count <= 3 AND p95_response_ms < 60000
  MANGELHAFT:    nudge_count > 3 OR p95_response_ms > 60000

Artefaktqualitaet:
  SEHR_GUT:      pflicht_coverage == 1.0 AND halluzinationen == 0 AND key_concepts_found >= 0.90
  GUT:           pflicht_coverage == 1.0 AND halluzinationen == 0 AND key_concepts_found >= 0.75
  BEFRIEDIGEND:  pflicht_coverage >= 0.80 AND halluzinationen <= 1
  MANGELHAFT:    pflicht_coverage < 0.80 OR halluzinationen > 1

Moderatorverhalten:
  SEHR_GUT:      eskalation_resolved_ratio == 1.0 AND moderator_turns_avg <= 2
  GUT:           eskalation_resolved_ratio >= 0.80 AND moderator_turns_avg <= 3
  BEFRIEDIGEND:  eskalation_resolved_ratio >= 0.50 AND moderator_turns_avg <= 5
  MANGELHAFT:    eskalation_resolved_ratio < 0.50 OR moderator_turns_avg > 5
```

Diese Werte sollten initial konservativ gesetzt und nach den ersten Kampagnen-Laeufen kalibriert werden.

---

## Schwaeche 5: Nudge-Mechanismus ist untersspezifiziert

### Problem

Der Plan erwaehnt Nudges (`nudges?: string[]` im Turn-Interface) ohne zu definieren:
- **Wann** wird ein Nudge ausgeloest? (Timeout? Fehlendes Flag?)
- **Wie lange** wartet der Runner bevor er einen Nudge sendet?
- **Was passiert** wenn alle Nudges erschoepft sind? (Test schlaegt fehl? Befund?)
- **Zaehlt** ein Turn mit Nudge als eigenstaendiger Turn oder als Wiederholung?

Das Human Playbook definiert konkrete Nudge-Texte (z.B. E1-14: 3 Nudges), aber der Kampagnen-Runner hat keine Logik dafuer.

### Loesungsoptionen

**Nudge-Strategie definieren:**

```typescript
interface NudgeStrategy {
  wait_after_turn_ms: number;        // z.B. 5000ms — warten ob phase_complete kommt
  max_nudges_per_phase: number;      // z.B. 3
  on_exhaustion: 'fail' | 'warn_and_continue';  // z.B. 'warn_and_continue'
  nudge_counts_as_turn: boolean;     // z.B. true — damit Turn-Count korrekt ist
}
```

Im ScenarioRunner:
```
1. Nachricht senden
2. Response empfangen
3. Wenn Turn.nudges definiert UND erwartetes Flag (z.B. phase_complete) fehlt:
   a. wait_after_turn_ms warten
   b. Nudge[0] senden, Response pruefen
   c. Wenn Flag immer noch fehlt: Nudge[1], etc.
   d. Wenn max_nudges erreicht: Befund "Nudge-Erschoepfung" loggen
```

---

## Schwaeche 6: Session-Persistenz und Wiederaufnahme nicht getestet

### Problem

Das System unterstuetzt Session-Wiederaufnahme (WebSocket-Reconnect + Replay der letzten Nachricht, siehe `websocket.py:98-108`). Kein Szenario testet:
- WebSocket-Disconnect mitten im Turn → Reconnect → Zustand konsistent?
- Projekt nach Tagen wieder oeffnen → Working Memory korrekt geladen?
- Parallelzugriff: Zwei WebSocket-Verbindungen zum selben Projekt?

### Loesungsoptionen

**Neues Szenario S12: Session-Wiederaufnahme**
- 5 Turns in Phase 1
- WebSocket trennen
- Neues WebSocket aufbauen — letzte Nachricht wird replayed
- 3 weitere Turns — Zustand konsistent, Slot-Zaehler korrekt
- Prueft: Kein Datenverlust, kein doppelter Turn-Zaehler

**Erweiterung des Test-Frameworks:**
```typescript
class SessionClient {
  async disconnect(): Promise<void>;
  async reconnect(): Promise<void>;  // Prueft ob Replay korrekt
}
```

---

## Schwaeche 7: Datei-Upload wird nicht getestet

### Problem

Das `TurnInput`-Modell unterstuetzt `datei: str | None` (base64-kodierter Dateiinhalt). Kein Szenario testet:
- Upload einer Rechnung als PDF
- System extrahiert Informationen aus der Datei
- Auswirkung auf Artefakte

### Loesungsoptionen

**Neues Szenario S13: Prozessbeschreibung mit Datei-Upload**
- Nutzer laedt eine Beispielrechnung hoch
- System soll relevante Informationen extrahieren oder zumindest korrekt reagieren
- Prueft: Keine Fehler, sinnvolle Verarbeitung

---

## Schwaeche 8: Fehlende Abgrenzung Assertion vs. Probe im Zeitverlauf

### Problem

Der Plan unterscheidet TurnExpectations (pro Turn) und BehaviorProbes (nach bestimmten Turns), aber es fehlt eine dritte Dimension: **Verlaufs-Assertions** die ueber den gesamten Szenario-Verlauf gelten.

Beispiele fuer Verlaufs-Invarianten:
- `befuellte_slots` darf niemals sinken (monotones Wachstum)
- `aktiver_modus` darf sich nur aendern wenn ein Trigger-Flag gesetzt ist
- Kein Turn darf gleichzeitig `phase_complete` und `escalate` setzen
- Zwischen `phase_complete` und neuem Modus liegt immer mindestens ein Moderator-Turn

Diese Invarianten sind im Plan als "harte Assertions" beschrieben, aber sie werden als punktuelle Checks formuliert statt als kontinuierliche Invarianten.

### Loesungsoptionen

**Invarianten-Checker als separate Evaluator-Klasse:**

```typescript
class InvariantChecker {
  // Wird nach JEDEM Turn aufgerufen, nicht nur bei spezifischen Probes
  checkMonotonicSlotGrowth(current: TurnRecord, previous: TurnRecord): AssertionResult;
  checkModeTransitionRequiresFlag(current: TurnRecord, previous: TurnRecord): AssertionResult;
  checkNoConflictingFlags(record: TurnRecord): AssertionResult;
  checkModeratorBetweenPhases(records: TurnRecord[]): AssertionResult;
  checkLanguageConsistency(record: TurnRecord): AssertionResult;
}
```

Integration in ScenarioRunner: Nach jedem Turn alle Invarianten pruefen, Verletzungen sofort als kritische Befunde loggen.

---

## Schwaeche 9: WebSocket-Client-Design matcht nicht die tatsaechliche API

### Problem

Der Plan definiert den SessionClient mit REST-aehnlichen Methoden:

```typescript
async createProject(name: string): Promise<string>;
async sendMessage(projectId: string, message: string): Promise<TurnResponse>;
```

Die tatsaechliche API funktioniert aber anders:
- Projekt-Erstellung laeuft ueber REST (`POST /api/projects`)
- Kommunikation laeuft ueber WebSocket mit JSON-Nachrichten: `{"type": "turn", "text": "..."}` und `{"type": "panic"}`
- Antworten kommen als Event-Stream: `chat_done`, `artifact_update`, `progress_update`, `debug_update`
- Die Greeting wird automatisch beim WebSocket-Connect ausgeloest (wenn `letzter_dialogturn == 0`)

### Loesungsoptionen

**Client-Interface an die reale API anpassen:**

```typescript
class SessionClient {
  // REST
  async createProject(name: string): Promise<string>;
  async getArtifacts(projectId: string): Promise<Artifacts>;
  async getValidationReport(projectId: string): Promise<ValidationReport>;
  async getExport(projectId: string): Promise<ExportData>;

  // WebSocket
  async connect(projectId: string): Promise<void>;
  async disconnect(): Promise<void>;
  async waitForGreeting(): Promise<TurnResponse>;        // Wartet auf auto-Greeting
  async sendTurn(text: string): Promise<TurnResponse>;   // {"type": "turn", "text": "..."}
  async sendPanic(): Promise<TurnResponse>;               // {"type": "panic"}

  // Hilfsmethoden
  private collectEvents(until: 'chat_done'): Promise<EventStream>;
  private parseEventStream(events: EventStream): TurnResponse;
}

interface TurnResponse {
  message: string;                    // aus chat_done
  artifacts: {                        // aus artifact_update Events
    exploration: object;
    struktur: object;
    algorithmus: object;
  };
  progress: {                         // aus progress_update
    phasenstatus: string;
    befuellte_slots: number;
    bekannte_slots: number;
  };
  debug: {                            // aus debug_update
    working_memory: object;
    flags: string[];
  };
  error?: string;                     // aus error Event
}
```

---

## Schwaeche 10: Keine Grenzwert-Tests fuer Systembelastung

### Problem

Keine Szenarien testen die Grenzen des Systems:
- Sehr langer Nutzer-Input (>2000 Woerter in einer Nachricht)
- Sehr viele Turns (>50) in einer Phase
- Extrem kurze Antworten ("ja", "nein", "weiss nicht") ueber lange Strecken
- LLM-Timeout oder -Fehler mitten im Prozess
- Maximale Artefaktgroesse (>20 Strukturschritte, >30 Algorithmusabschnitte)

### Loesungsoptionen

**Zwei neue Szenarien:**

**S14: Stress-Test — Uebergroesser Prozess**
- Nutzer beschreibt einen Prozess mit >15 Strukturschritten, >10 Entscheidungen
- Prueft: Artefaktintegritaet bei grossem Umfang, Token-Limit-Handling, Nachfolger-Graph-Konsistenz

**S15: Stress-Test — Minimale Interaktion**
- Nutzer antwortet nur mit "ja", "nein", "weiss nicht", "keine Ahnung"
- Prueft: Kann das System trotzdem Fortschritt machen? Oder haengt es?

**Error-Injection im Test-Framework:**
```typescript
interface ErrorInjection {
  simulate_llm_timeout_at_turn?: number;
  simulate_llm_error_at_turn?: number;
  max_response_wait_ms?: number;
}
```

---

## Schwaeche 11: Export-/Download-Verifikation fehlt

### Problem

Das System hat einen Export-Endpoint (`GET /api/projects/{id}/export`) der JSON + Markdown erzeugt. Kein Test prueft:
- Ist der Export nach Projektabschluss vollstaendig?
- Stimmt das Markdown mit den JSON-Artefakten ueberein?
- Kann der Export re-importiert werden?

### Loesungsoptionen

**Export-Verifikation als Post-Szenario-Check:**

Im `ScenarioRunner` nach Abschluss des letzten Turns:
```typescript
// Wenn Projekt abgeschlossen:
const exportData = await client.getExport(projectId);
// Pruefe: JSON valide, Markdown nicht leer, Artefakte konsistent
```

---

## Schwaeche 12: Panik-Button waehrend Moderator nicht getestet

### Problem

Was passiert wenn der Nutzer den Panik-Button drueckt waehrend er bereits beim Moderator ist? Die WebSocket-Implementierung setzt `vorheriger_modus = aktiver_modus` — wenn `aktiver_modus` bereits "moderator" ist, wuerde `vorheriger_modus` auf "moderator" gesetzt, was zu einer Endlosschleife fuehren koennte (Moderator → Moderator → Moderator).

### Loesungsoptionen

**Neues Szenario oder Erweiterung von S01:**

- Nutzer ist beim Moderator (nach Eskalation)
- Nutzer drueckt erneut Panik-Button
- Erwartung: System faengt das ab, kein Modus-Ping-Pong

**Backend-Fix pruefen:**
```python
# websocket.py, panic handler:
if project.working_memory.aktiver_modus != "moderator":
    project.working_memory.vorheriger_modus = project.working_memory.aktiver_modus
    project.working_memory.aktiver_modus = "moderator"
# else: bereits beim Moderator, kein Mode-Switch noetig
```

---

## Schwaeche 13: Fehlende Szenarios fuer spezifische Nuterprofile

### Problem

Das SDD definiert drei Nutzerprofile (Anfaenger, Prozessexperte, IT-Liaison), aber die Szenarien bilden diese nur teilweise ab:
- S01 = generischer Nutzer mit Eskalationen
- S04 = ungeduldiger Nutzer (teilweise Prozessexperte)
- S08 = Sprachmischung (teilweise IT-Liaison)

Es fehlt:
- **Dezidierter Anfaenger**: Jemand der bei jeder Frage unsicher ist, nachfragt, Fachbegriffe nicht versteht
- **Dezidierter Prozessexperte**: Jemand der alles auf einmal erzaehlt und ungeduldig wird weil das System zu langsam ist
- **IT-Liaison**: Jemand der technische Begriffe verwendet, EMMA versteht, und auf Detailtiefe dringt

### Loesungsoptionen

Bestehende Szenarien um Nutzerprofile anreichern oder dezidierte Profil-Szenarien ergaenzen. Mindestens S04 (ungeduldig) erweitern um auch zu testen ob das System bei einem Prozessexperten die Slot-Effizienz steigert (weniger Fragen, hoehere Informationsausbeute pro Turn).

---

## Zusammenfassung der Empfehlungen

### Kritisch (vor Implementierung loesen)

| # | Schwaeche | Empfehlung |
|---|-----------|------------|
| 3 | Modi nicht registriert | Backend-Fix: Alle 5 Modi im Orchestrator registrieren |
| 1 | Keine Validierungsphase | Neues Szenario S09: Validierungs-Korrekturschleife |
| 9 | Client-Interface matcht nicht API | SessionClient an reale WebSocket-API anpassen |
| 4 | Keine Schwellwerte | Bewertungstabelle mit initialen Schwellwerten definieren |

### Hoch (erste Kampagne sollte sie abdecken)

| # | Schwaeche | Empfehlung |
|---|-----------|------------|
| 2 | Nicht-automatisierbare Prozesse | Neues Szenario S10 + S11 |
| 5 | Nudge-Mechanismus | NudgeStrategy definieren und im Runner implementieren |
| 8 | Keine Verlaufs-Invarianten | InvariantChecker als kontinuierlichen Post-Turn-Check |
| 12 | Panik waehrend Moderator | Backend-Guard + Testfall |

### Mittel (spaetere Kampagnen)

| # | Schwaeche | Empfehlung |
|---|-----------|------------|
| 6 | Session-Wiederaufnahme | Szenario S12 |
| 7 | Datei-Upload | Szenario S13 |
| 10 | Grenzwert-Tests | Szenarien S14 + S15 |
| 11 | Export-Verifikation | Post-Szenario-Check |
| 13 | Nutzerprofile | Profil-Szenarien |

---

## Staerken des Plans (was beibehalten werden sollte)

1. **Zwei-Ebenen-Bewertung** (Assertions + Verhaltensbewertung) — genau richtig fuer ein LLM-System
2. **Intent-basiertes Szenario-Design** — `key_concepts` und `forbidden_concepts` sind der korrekte Ansatz fuer Halluzinations-Checks
3. **WebSocket-direkt statt Browser** — korrekte Architekturentscheidung fuer Systemverhaltenstests
4. **TurnExpectations + BehaviorProbes** — gezielte Pruefpunkte statt "alles auf einmal am Ende"
5. **Campaign Reporter mit Musteranalyse** — die Cross-Szenario-Analyse ist der wichtigste Output
6. **Erweiterbarkeit** — das JSON-Szenario-Format erlaubt einfaches Hinzufuegen neuer Tests
7. **Human Playbook als Referenz** — S01 ist detailliert genug um als Ground Truth zu dienen
8. **Artefakt-Snapshots pro Phase** — korrekt, nicht nur am Ende

---

## Vorgeschlagene erweiterte Szenario-Landkarte

| # | Szenario | Phase | Fokus | Prioritaet |
|---|----------|-------|-------|------------|
| S01 | Eingangsrechnung (Referenz) | E→S→Sp→V | Baseline, Eskalationen, Widerspruch | P0 |
| S02 | Reisekosten (Happy Path) | E→S→Sp→V | Effizienz, minimale Turns | P0 |
| S03 | Mitarbeiter-Einstellung | E→S→Sp→V | Skalierung, grosse Artefakte | P0 |
| S04 | Ungeduldiger Nutzer | E→S | Druck-Resilienz | P0 |
| S05 | Widersprueche | E→S→Sp | Korrektur, Artefakt-Update | P0 |
| S06 | Abbruch nach Phase 1 | E | Zustandskonsistenz | P1 |
| S07 | Minimaler Prozess | E→S→Sp→V | Halluzinationsresistenz | P1 |
| S08 | Englisch-Antworten | E→S | Sprachkonsistenz | P1 |
| **S09** | **Validierungs-Korrekturschleife** | **E→S→Sp→V→Sp→V** | **Korrekturschleife, Re-Validierung** | **P0** |
| **S10** | **Nicht-automatisierbarer Prozess** | **E→S→Sp→V** | **EMMA-Inkompatibilitaet, konstruktives Feedback** | **P0** |
| **S11** | **Chaotischer/unlogischer Prozess** | **E** | **Systemgrenzen, Halluzinations-Widerstand** | **P1** |
| **S12** | **Session-Wiederaufnahme** | **E** | **Persistenz, Reconnect, Zustandskonsistenz** | **P1** |
| **S13** | **Datei-Upload** | **E→S** | **Dateiverarbeitung, Informationsextraktion** | **P2** |
| **S14** | **Stress: Uebergroesser Prozess** | **E→S→Sp** | **Token-Limits, Artefaktintegritaet bei Groesse** | **P2** |
| **S15** | **Stress: Minimale Interaktion** | **E** | **Fortschritt bei unkooperativem Nutzer** | **P2** |

---

## Nachtrag: Befunde aus der Backend-Analyse

### Befund A: Moderator-Uebergabe-Logik (VORRANG-REGEL)

Der Moderator hat eine hartcodierte Regel: Zustimmungsausdruecke ("ja", "okay", "los", "gut", "klar", "weiter") werden **immer** als `uebergabe=true` interpretiert. Das bedeutet:

- Wenn der Nutzer "Ja, aber..." sagt, wird er trotzdem weitergeleitet
- Kein Szenario testet **ambige Zustimmung** ("Ja, aber ich hab noch eine Frage")
- Kein Szenario testet **falsch-positive Uebergabe** ("Gut, dass Sie das sagen, aber nein")

**Empfehlung:** BehaviorProbe in S01 oder neues Szenario: Nutzer sagt etwas das mit "Ja" beginnt aber eine Verneinung enthaelt. System sollte nicht vorschnell uebergeben.

### Befund B: Dialog-History-Limit ist extrem niedrig

`config.py` setzt `dialog_history_n: int = 3` — nur die letzten 3 Turns werden dem LLM als Kontext mitgegeben. Das SDD erwaehnt 20 Turns. Bei einem Szenario mit 40+ Turns koennte das System frueh den Kontext verlieren.

**Empfehlung:**
- Szenario S01 sollte explizit pruefen ob das System nach Turn 20 noch Bezug auf fruehere Aussagen nehmen kann
- InvariantChecker: Pruefe ob Artefakt-Inhalte, die auf fruehere Turns zurueckgehen, nach Turn N noch korrekt sind
- Konfigurationsparameter `dialog_history_n` im Test-Setup dokumentieren — bei zu niedrigem Wert werden Verhaltensbewertungen verfaelscht

### Befund C: Patch-Merging in Exploration — Inhalt wird konkateniert, nicht ersetzt

Der ExplorationMode konkateniert neue Slot-Inhalte mit bestehenden (statt zu ueberschreiben). Das ist fuer die Widerspruch-Korrektur (S05, E3-06) relevant: Wenn ein Widerspruch korrigiert wird, steht moeglicherweise **sowohl die alte als auch die neue Information** im Slot.

**Empfehlung:**
- BehaviorProbe nach Widerspruch-Korrektur: Pruefe ob der **veraltete** Inhalt noch im Slot steht
- Assertion: Nach E3-06 darf "manuell durchklicken" nicht mehr im Slot stehen (laut Playbook), aber Patch-Merging koennte beides behalten

### Befund D: Structuring/Specification haben First-Turn-Directives

Beide Modi haben `_build_first_turn_directive()`: Wenn das jeweilige Artefakt leer ist, **muss** das LLM im ersten Turn alle erkennbaren Schritte/Abschnitte anlegen. Das ist ein kritischer Moment — ein einzelner LLM-Call erzeugt die gesamte Grundstruktur.

**Empfehlung:**
- TurnExpectation fuer den ersten Turn nach Phasenwechsel (Structuring, Specification): `slots_should_increase: true` mit hoher Erwartung (>= 5 Schritte, >= 6 Abschnitte)
- Wenn der erste Turn fehlschlaegt, ist die gesamte Phase kompromittiert — expliziter Testfall

### Befund E: Executor hat Invalidation-Detection (Structure → Algorithm)

Wenn ein Strukturschritt geaendert wird (beschreibung, typ, bedingung, ausnahme_beschreibung), werden alle referenzierten Algorithmusabschnitte automatisch auf `status: invalidiert` gesetzt. Das ist ein **kaskadeneffekt** den kein Szenario explizit testet.

**Empfehlung:**
- Szenario S05 (Widersprueche) erweitern: Nach Korrektur in Phase 3 pruefen ob betroffene Algorithmusabschnitte invalidiert wurden
- Assertion: `status === "invalidiert"` fuer betroffene Abschnitte nach Struktur-Aenderung

---

## Anmerkung zur Test-Harness-Architektur

Der Plan sieht eine sinnvolle Architektur vor (ScenarioRunner + Evaluator + Reporter). Fuer die Erweiterbarkeit empfehle ich zusaetzlich:

1. **Plugin-System fuer Evaluatoren**: Neue Bewertungsdimensionen als separate Module, nicht im monolithischen `evaluator.ts`
2. **Szenario-Validierung**: Vor dem Lauf pruefen ob das JSON-Szenario valide ist (alle Turn-IDs eindeutig, BehaviorProbes referenzieren existierende Turns, etc.)
3. **Diff-Reporting**: Zwischen Kampagnen-Laeufen Veraenderungen visualisieren (Regression-Erkennung)
4. **Seed-Steuerung**: Wenn der LLM-Provider `seed`-Parameter unterstuetzt, fuer Reproduzierbarkeit nutzen
5. **Parallel-Ausfuehrung**: Szenarien parallel ausfuehren koennen (separate Projekte, kein Shared State) fuer kuerzere Kampagnen-Laufzeiten
