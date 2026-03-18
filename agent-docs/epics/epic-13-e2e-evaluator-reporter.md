# Epic 13 – E2E Evaluator, Reporter & Campaign-Runner

## Summary

Ergänzt das E2E-Framework um die Bewertungslogik (7 harte Assertions + 4 weiche
Verhaltensdimensionen), einen Markdown-Report-Generator (pro Szenario + Kampagnen-
Zusammenfassung) und den vollständigen CLI-Runner. Nach diesem Epic kann eine komplette
Kampagne ausgeführt und als strukturierter Markdown-Report ausgegeben werden.

Dieses Epic entspricht **Schritt 3–4 + 6** im `e2e-testkampagne-plan.md`.

## Goal

Ein vollständiges Bewertungs- und Reporting-System: `AssertionEvaluator` prüft
deterministische SDD-Regeln, `BehaviorEvaluator` bewertet Dialog-, Moderator-,
Artefakt- und UX-Qualität auf einer vierstufigen Skala, und der `CampaignReporter`
erzeugt Markdown-Befundlisten pro Szenario sowie eine aggregierte Bewertungsmatrix
mit Problemmuster-Erkennung.

## Testable Increment

- `npx tsx e2e/run-campaign.ts --scenario S02` erzeugt unter `e2e/reports/`:
  - `scenario-S02.md` — Befundliste mit Eckdaten, Assertion-Ergebnissen,
    Verhaltensbewertung und Dialog-Protokoll
  - `campaign-summary.md` — Bewertungsmatrix (auch bei nur einem Szenario)
  - `raw-data.json` — Alle TurnRecords als JSON
- `npx tsx --test e2e/framework/__tests__/evaluator.test.ts` prüft die Evaluator-Logik
  gegen synthetische TurnRecords (ohne laufendes Backend)

## Dependencies

- Epic 12 (Framework Core muss existieren: Types, SessionClient, ScenarioRunner)

## Key Deliverables

- `e2e/framework/evaluator.ts` – `AssertionEvaluator` + `BehaviorEvaluator` (≤ 400 Zeilen; bei Überschreitung in `assertion-evaluator.ts` + `behavior-evaluator.ts` aufteilen)
- `e2e/framework/campaign-reporter.ts` – Markdown-Report-Generator
- `e2e/run-campaign.ts` – Erweiterung: Report-Erzeugung nach Kampagne
- `e2e/framework/__tests__/evaluator.test.ts` – Unit-Tests für Evaluator-Logik

## Stories

---

### Story 13-01: `evaluator.ts` — AssertionEvaluator (7 harte Checks)

**Als** Entwickler,
**möchte ich** deterministische Assertions gegen SDD-Regeln automatisch prüfen,
**damit** Regelverletzungen sofort erkannt und im Report als PASS/FAIL/WARN dokumentiert werden.

**FR/NFR Traceability:** `e2e-testkampagne-plan.md` Ebene 1 (Deterministische Assertions),
SDD 6.3, 6.1.2, 5.2, 6.6.5, FR-A-08, 6.5.2, FR-B-04.

**Akzeptanzkriterien:**

1. `e2e/framework/evaluator.ts` existiert und exportiert `AssertionEvaluator`.
2. Methode `checkModeTransitions(records: TurnRecord[]): AssertionResult[]`:
   - Prüft: `aktiver_modus` ändert sich nur nach `phase_complete`, `escalate` oder `blocked` Flag
   - Gibt `PASS` wenn alle Moduswechsel regelkonform, `FAIL` mit Detail bei Verstoß
3. Methode `checkPhaseTransitions(records: TurnRecord[]): AssertionResult[]`:
   - Prüft: Zwischen `phase_complete`-Flag und neuem Modus liegt mindestens ein
     Moderator-Turn mit Nutzerbestätigung
   - SDD 6.1.2: Phasenwechsel nur nach Moderator-Bestätigung
4. Methode `checkModeratorNoWrite(records: TurnRecord[]): AssertionResult[]`:
   - Prüft: Während `aktiver_modus === "moderator"` kommt nie `artefakt_updated` in den Flags
   - SDD 6.6.5: Moderator verändert keine Artefakte
5. Methode `checkLanguage(records: TurnRecord[]): AssertionResult[]`:
   - Prüft: Systemantworten sind auf Deutsch (Heuristik: Anteil deutscher Stoppwörter
     > 50% oder kein englischer Satz > 20 Wörter)
   - FR-A-08: Systemsprache Deutsch
   - `WARN` statt `FAIL` bei einzelnem englischen Satz (Toleranz)
6. Methode `checkOutputContract(records: TurnRecord[]): AssertionResult[]`:
   - Prüft: Keine Artefakt-Dumps im Chat (Systemantwort enthält keine JSON-Blöcke > 200 Zeichen)
   - SDD 6.5.2: Output-Kontrakt
7. Methode `checkArtifactIntegrity(artifacts: ArtifactSnapshots): AssertionResult[]`:
   - Prüft: Jeder `nachfolger_id` in Strukturschritten zeigt auf existierenden Schritt
   - Prüft: Jeder Schritt außer Ende hat mindestens einen Nachfolger
   - Prüft: Keine verwaisten Schritte (Waisen-Check)
8. Methode `checkEMMACompatibility(artifacts: ArtifactSnapshots): AssertionResult[]`:
   - Prüft: Alle `emma_aktion.typ`-Werte gegen den EMMA-Aktionskatalog (SDD 8.3)
   - Gültige Typen: `sequenz_aktion`, `entscheidung`, `schleife`, `parallele`,
     `ausnahme`, `ereignis`, `datenobjekt` (Liste aus SDD)
9. Convenience-Methode `runAll(records: TurnRecord[], artifacts: ArtifactSnapshots): AssertionResult[]`:
   - Führt alle 7 Checks aus und gibt aggregierte Liste zurück
10. `AssertionEvaluator` ist zustandslos (kein Constructor-State nötig).

**Definition of Done:**

- [ ] `e2e/framework/evaluator.ts` existiert und exportiert `AssertionEvaluator`
- [ ] `checkModeTransitions()` prüft Moduswechsel gegen Flag-Regeln
- [ ] `checkPhaseTransitions()` prüft Moderator-Bestätigung bei Phasenwechsel
- [ ] `checkModeratorNoWrite()` prüft dass Moderator keine Artefakte schreibt
- [ ] `checkLanguage()` erkennt nicht-deutsche Systemantworten
- [ ] `checkOutputContract()` erkennt Artefakt-Dumps im Chat
- [ ] `checkArtifactIntegrity()` prüft Nachfolger-Referenzen und Waisen
- [ ] `checkEMMACompatibility()` prüft EMMA-Aktionstypen gegen Katalog
- [ ] `runAll()` aggregiert alle 7 Checks
- [ ] `AssertionEvaluator` ist zustandslos (kein Constructor-State)
- [ ] `e2e/framework/evaluator.ts` ist ≤ 400 Zeilen (nach 13-02; sonst aufteilen)
- [ ] `npm run typecheck` in `e2e/` exit 0

---

### Story 13-02: `evaluator.ts` — BehaviorEvaluator (4 Dimensionen)

**Als** Entwickler,
**möchte ich** eine weiche Verhaltensbewertung auf einer vierstufigen Skala,
**damit** Dialog-, Moderator-, Artefakt- und UX-Qualität quantifiziert und
Szenarien-übergreifend verglichen werden können.

**FR/NFR Traceability:** `e2e-testkampagne-plan.md` Ebene 2 (Verhaltensbeurteilung),
Dimensionen A–D.

**Akzeptanzkriterien:**

1. `e2e/framework/evaluator.ts` exportiert zusätzlich `BehaviorEvaluator`.
2. Methode `evaluateDialogQuality(records: TurnRecord[]): BehaviorScore`:
   - Metriken:
     - `slot_efficiency`: Ratio von Turns mit `artefakt_updated` zu Gesamt-Turns
     - `repetition_count`: Anzahl aufeinanderfolgender Turns mit semantisch ähnlicher
       Systemfrage (vereinfacht: gleiche erste 50 Zeichen)
     - `nudge_count`: Anzahl Turns mit `nudge_used === true`
   - Bewertungslogik:
     - `SEHR_GUT`: `slot_efficiency ≥ 0.7` UND `repetition_count === 0` UND `nudge_count ≤ 1`
     - `GUT`: `slot_efficiency ≥ 0.5` UND `repetition_count ≤ 1`
     - `BEFRIEDIGEND`: `slot_efficiency ≥ 0.3`
     - `MANGELHAFT`: sonst
3. Methode `evaluateModeratorBehavior(records: TurnRecord[]): BehaviorScore`:
   - Metriken:
     - `avg_moderator_turns`: Durchschnittliche Anzahl Moderator-Turns pro Phase-Übergang
     - `escalation_resolved`: Ratio aufgelöster Eskalationen (Panik → Moderator → zurück zu Modus)
   - Bewertungslogik:
     - `SEHR_GUT`: `avg_moderator_turns ≤ 2` UND `escalation_resolved === 1.0`
     - `GUT`: `avg_moderator_turns ≤ 3`
     - `BEFRIEDIGEND`: `avg_moderator_turns ≤ 5`
     - `MANGELHAFT`: `avg_moderator_turns > 5` ODER `escalation_resolved < 0.5`
4. Methode `evaluateArtifactQuality(records: TurnRecord[], artifacts: ArtifactSnapshots, intent: ScenarioIntent): BehaviorScore`:
   - Metriken:
     - `slot_completeness`: Ratio gefüllte Pflichtslots / Gesamt-Pflichtslots
     - `key_concept_coverage`: Ratio von `intent.key_concepts` die in den Artefakten vorkommen
     - `forbidden_concept_violations`: Anzahl `intent.forbidden_concepts` die in Artefakten auftauchen
   - Bewertungslogik:
     - `SEHR_GUT`: `slot_completeness ≥ 0.9` UND `key_concept_coverage ≥ 0.8` UND `forbidden_concept_violations === 0`
     - `GUT`: `slot_completeness ≥ 0.7` UND `key_concept_coverage ≥ 0.6`
     - `BEFRIEDIGEND`: `slot_completeness ≥ 0.5`
     - `MANGELHAFT`: sonst
5. Methode `evaluateUXFluency(records: TurnRecord[]): BehaviorScore`:
   - Metriken:
     - `median_response_ms`: Median der `response_time_ms` über alle Turns
     - `p95_response_ms`: 95. Perzentil der `response_time_ms`
     - `mode_pingpong_count`: Anzahl Muster "Modus A → Moderator → Modus A" ohne
       Slot-Änderung dazwischen
     - `nudge_total`: Gesamt-Nudges im Szenario
   - Bewertungslogik:
     - `SEHR_GUT`: `p95_response_ms < 20000` UND `mode_pingpong_count === 0` UND `nudge_total ≤ 1`
     - `GUT`: `p95_response_ms < 30000` UND `nudge_total ≤ 2`
     - `BEFRIEDIGEND`: `p95_response_ms < 45000`
     - `MANGELHAFT`: sonst
6. Convenience-Methode `evaluateAll(records, artifacts, intent): BehaviorScore[]`:
   - Führt alle 4 Dimensionen aus und gibt Array zurück.

**Definition of Done:**

- [ ] `BehaviorEvaluator` exportiert aus `evaluator.ts`
- [ ] `evaluateDialogQuality()` mit slot_efficiency, repetition_count, nudge_count Metriken
- [ ] `evaluateModeratorBehavior()` mit avg_moderator_turns, escalation_resolved Metriken
- [ ] `evaluateArtifactQuality()` mit slot_completeness, key_concept_coverage, forbidden_concept_violations Metriken
- [ ] `evaluateUXFluency()` mit median_response_ms, p95_response_ms, mode_pingpong_count, nudge_total Metriken
- [ ] Vierstufige Bewertungsskala (SEHR_GUT / GUT / BEFRIEDIGEND / MANGELHAFT) korrekt implementiert
- [ ] `evaluateAll()` aggregiert alle 4 Dimensionen
- [ ] `npm run typecheck` in `e2e/` exit 0

---

### Story 13-03: `campaign-reporter.ts` — Szenario-Befundlisten

**Als** Entwickler,
**möchte ich** pro Szenario einen Markdown-Report mit Eckdaten, Assertions, Verhaltensbewertung
und Dialog-Protokoll,
**damit** Testergebnisse menschenlesbar dokumentiert und archiviert werden können.

**FR/NFR Traceability:** `e2e-testkampagne-plan.md` Teil 1 (Befundliste pro Szenario).

**Akzeptanzkriterien:**

1. `e2e/framework/campaign-reporter.ts` existiert und exportiert `CampaignReporter`.
2. Methode `addScenarioResult(result: ScenarioResult): void`:
   - Speichert das Ergebnis intern für spätere Aggregation
3. Private Methode zur Erzeugung einer Szenario-Befundliste als Markdown-String:
   - **Eckdaten-Sektion:** Turns, Dauer, erreichte Phasen, Nudge-Anzahl, Eskalations-Anzahl
   - **Assertion-Ergebnisse:** Tabelle mit Name | Status (PASS/FAIL/WARN) | Detail
   - **Verhaltensbewertung:** Tabelle mit Dimension | Bewertung | Begründung
   - **Dialog-Protokoll (gekürzt):** Tabelle mit Turn-Nr | Modus | User (erste 50 Zeichen) |
     System (erste 80 Zeichen) | Slots | Flags | Bemerkung
   - **Artefakt-Snapshots:** JSON-Blöcke der finalen Artefakte (als Codeblock)
4. Format entspricht dem Beispiel in `e2e-testkampagne-plan.md` Abschnitt "Befundliste".
5. Methode `writeScenarioReport(result: ScenarioResult, outputDir: string): void`:
   - Schreibt `scenario-<ID>.md` in das angegebene Verzeichnis
   - Erstellt das Verzeichnis wenn es nicht existiert

**Definition of Done:**

- [ ] `e2e/framework/campaign-reporter.ts` existiert und exportiert `CampaignReporter`
- [ ] `addScenarioResult()` speichert Ergebnisse intern
- [ ] Szenario-Befundliste enthält Eckdaten, Assertions, Verhaltensbewertung, Dialog-Protokoll
- [ ] Dialog-Protokoll ist gekürzt (keine vollständigen Nachrichten)
- [ ] Artefakt-Snapshots als JSON-Codeblöcke enthalten
- [ ] `writeScenarioReport()` schreibt `scenario-<ID>.md`
- [ ] Verzeichnis wird erstellt wenn nicht vorhanden
- [ ] `npm run typecheck` in `e2e/` exit 0

---

### Story 13-04: `campaign-reporter.ts` — Bewertungsmatrix + Problemmuster

**Als** Entwickler,
**möchte ich** eine aggregierte Bewertungsmatrix über alle Szenarien mit automatischer
Problemmuster-Erkennung,
**damit** systematische Schwächen szenarioübergreifend sichtbar werden.

**FR/NFR Traceability:** `e2e-testkampagne-plan.md` Teil 2 (Bewertungsmatrix).

**Akzeptanzkriterien:**

1. Methode `analyzePatterns()` gibt zurück:
   - `assertion_summary`: `{ total, passed, failed, warnings }` aggregiert über alle Szenarien
   - `behavior_matrix`: `Record<string, Record<string, BehaviorScore>>` — Dimension → Szenario-ID → Score
   - `problem_patterns`: `string[]` — Erkannte übergreifende Muster (z.B.
     "Phase-Complete-Verzögerung in 5/8 Szenarien")
   - `recommendations`: `string[]` — Handlungsempfehlungen
2. Problemmuster-Erkennung:
   - Wenn ≥ 50% der Szenarien in einer Dimension `BEFRIEDIGEND` oder schlechter haben →
     Pattern: `"<Dimension> ist systemisch schwach (<N>/<Total> Szenarien)"`
   - Wenn ≥ 3 Szenarien den gleichen Assertion-Fehler haben →
     Pattern: `"<Assertion> schlägt in <N> Szenarien fehl"`
   - Wenn `nudge_total` über alle Szenarien im Median > 2 →
     Pattern: `"Phase-Complete-Erkennung hat systemische Schwäche"`
3. Methode `writeCampaignSummary(outputDir: string): void`:
   - Schreibt `campaign-summary.md` mit:
     - Bewertungsmatrix als Markdown-Tabelle (Dimensionen × Szenarien)
     - Assertion-Zusammenfassung
     - Erkannte Problemmuster
     - Empfehlungen
   - Schreibt `raw-data.json` mit allen TurnRecords aller Szenarien
4. Methode `writeReport(outputDir: string): void`:
   - Convenience: Ruft `writeScenarioReport()` für jedes Szenario und
     `writeCampaignSummary()` auf
   - Erstellt `outputDir` wenn nicht vorhanden
5. Bewertungsmatrix-Format entspricht dem Beispiel in `e2e-testkampagne-plan.md`
   Abschnitt "Bewertungsmatrix".

**Definition of Done:**

- [ ] `analyzePatterns()` gibt assertion_summary, behavior_matrix, problem_patterns, recommendations zurück
- [ ] Problemmuster-Erkennung für systemisch schwache Dimensionen
- [ ] Problemmuster-Erkennung für wiederkehrende Assertion-Fehler
- [ ] `writeCampaignSummary()` schreibt `campaign-summary.md` mit Bewertungsmatrix
- [ ] `writeCampaignSummary()` schreibt `raw-data.json`
- [ ] `writeReport()` erzeugt alle Reports (Szenario + Kampagne)
- [ ] Bewertungsmatrix-Format entspricht `e2e-testkampagne-plan.md` Abschnitt "Bewertungsmatrix"
- [ ] `npm run typecheck` in `e2e/` exit 0

---

### Story 13-05: `run-campaign.ts` — Vollständiger CLI-Runner mit Reports

**Als** Entwickler,
**möchte ich** den CLI-Runner so erweitern, dass nach der Kampagne automatisch Evaluierung
und Report-Generierung laufen,
**damit** eine komplette Kampagne mit einem einzigen Befehl ausgeführt und dokumentiert wird.

**FR/NFR Traceability:** `e2e-testkampagne-plan.md` Schritt 6 (Test-Runner).

**Akzeptanzkriterien:**

1. `e2e/run-campaign.ts` erweitert (aus Epic 12-05):
   - Nach jedem Szenario: `AssertionEvaluator.runAll()` und `BehaviorEvaluator.evaluateAll()`
     ausführen und Ergebnisse in `ScenarioResult` speichern
   - Ergebnisse an `CampaignReporter.addScenarioResult()` übergeben
   - Am Ende: `reporter.writeReport('e2e/reports/')` aufrufen
2. CLI-Flags:
   - `--scenario <ID>` — einzelnes Szenario (bestehend)
   - `--output <dir>` — alternatives Report-Verzeichnis (Default: `e2e/reports/`)
   - `--verbose` — vollständige Dialog-Protokolle im Report (statt gekürzt)
3. Fortschritts-Ausgabe auf stdout:
   - Pro Szenario: `"✓ S02 Reisekostenabrechnung — 13 Turns, 42s, Assertions: 7/7 PASS"`
   - Am Ende: `"Kampagne abgeschlossen. X/Y Szenarien. Report: e2e/reports/campaign-summary.md"`
4. Exit-Code:
   - `0` wenn alle Assertions in allen Szenarien PASS oder WARN
   - `1` wenn mindestens eine Assertion FAIL ist
5. `e2e/run-campaign.ts` ist ≤ 200 Zeilen.

**Definition of Done:**

- [ ] Evaluierung (Assertion + Behavior) läuft automatisch nach jedem Szenario
- [ ] Reports werden automatisch in `e2e/reports/` geschrieben
- [ ] `--scenario`, `--output`, `--verbose` Flags implementiert
- [ ] Fortschritts-Ausgabe pro Szenario auf stdout
- [ ] Exit-Code 0 bei Erfolg, 1 bei Assertion-FAIL
- [ ] `e2e/run-campaign.ts` ist ≤ 200 Zeilen
- [ ] `npm run typecheck` in `e2e/` exit 0

---

### Story 13-06: Unit-Tests für Evaluator-Logik

**Als** Entwickler,
**möchte ich** die Evaluator-Logik ohne laufendes Backend testen,
**damit** Bewertungsregeln deterministisch verifiziert werden können.

**Akzeptanzkriterien:**

1. `e2e/framework/__tests__/evaluator.test.ts` existiert.
2. Tests verwenden synthetische `TurnRecord[]`-Arrays (keine echten Backend-Calls).
3. AssertionEvaluator-Tests:
   - `test_mode_transition_valid`: Legaler Moduswechsel nach `phase_complete` → `PASS`
   - `test_mode_transition_invalid`: Moduswechsel ohne Flag → `FAIL`
   - `test_moderator_no_write_pass`: Moderator-Turns ohne `artefakt_updated` → `PASS`
   - `test_moderator_no_write_fail`: Moderator-Turn mit `artefakt_updated` → `FAIL`
   - `test_language_german_pass`: Deutsche Antworten → `PASS`
   - `test_language_english_warn`: Englischer Satz → `WARN`
4. BehaviorEvaluator-Tests:
   - `test_dialog_quality_sehr_gut`: Hohe slot_efficiency, keine Wiederholungen → `SEHR_GUT`
   - `test_dialog_quality_mangelhaft`: Niedrige slot_efficiency → `MANGELHAFT`
   - `test_ux_fluency_gut`: Schnelle Antworten, wenig Nudges → `GUT`
   - `test_artifact_quality_mit_halluzination`: `forbidden_concept` im Artefakt → Abwertung
5. Pattern-Detection-Tests (CampaignReporter.analyzePatterns):
   - `test_pattern_weak_dimension`: ≥50% Szenarien BEFRIEDIGEND → Pattern erkannt
   - `test_pattern_recurring_assertion_fail`: ≥3 Szenarien gleicher FAIL → Pattern erkannt
   - `test_pattern_no_issues`: Alle Szenarien gut → leere `problem_patterns`
6. Alle Tests laufen mit `npx tsx --test e2e/framework/__tests__/evaluator.test.ts`.
7. Mindestens 13 Tests insgesamt.

**Definition of Done:**

- [ ] `e2e/framework/__tests__/evaluator.test.ts` existiert
- [ ] Mindestens 6 AssertionEvaluator-Tests mit synthetischen TurnRecords
- [ ] Mindestens 4 BehaviorEvaluator-Tests mit synthetischen TurnRecords
- [ ] Mindestens 3 Pattern-Detection-Tests mit synthetischen Szenario-Ergebnissen
- [ ] Mindestens 13 Tests insgesamt
- [ ] Alle Tests laufen ohne Backend-Abhängigkeit
- [ ] `npx tsx --test e2e/framework/__tests__/evaluator.test.ts` exit 0
- [ ] `npm run typecheck` in `e2e/` exit 0

---

### Implementation Order

Stories müssen in dieser Reihenfolge implementiert werden:

1. **13-01** (AssertionEvaluator) — hängt von Epic 12 Types ab
2. **13-02** (BehaviorEvaluator) — kann parallel zu 13-01
3. **13-03** (Szenario-Befundlisten) — hängt von 13-01 und 13-02 ab
4. **13-04** (Bewertungsmatrix) — hängt von 13-03 ab
5. **13-06** (Unit-Tests) — hängt von 13-01, 13-02 und 13-04 ab (testet auch Pattern-Detection)
6. **13-05** (CLI-Runner Erweiterung) — hängt von allen vorherigen Stories ab
