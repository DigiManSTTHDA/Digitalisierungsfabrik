# Codebase Review — E2E Testing Subsystem

**Scope:** `e2e/` Verzeichnis, E2E Epics 12–14, `backend/tests/e2e_reisekosten.py`
**Datum:** 2026-03-19
**Methode:** 5-Agenten-Parallelanalyse (Requirements, Code-Qualität, Anti-AI-Slop, Security & Tests, Prototyp-Fitness)

---

## 1. Gesamturteil

Das E2E-Framework ist **strukturell sauber aufgebaut** und wählt den **richtigen Ansatz** (deterministische Assertions + verhaltensbasierte Bewertung) für das Testen eines LLM-getriebenen Systems. Die Modulstruktur ist klar, die Szenarien sind realistisch und domänensprachlich gut geschrieben.

Die **zentrale Schwäche** ist, dass das Framework **generisch** wirkt — es könnte mit minimalen Änderungen für jedes beliebige LLM-Chatbot-System verwendet werden. Die Assertions und Behavior-Scores prüfen oberflächliche Signale (Keyword-Matching, Stopwort-Heuristiken, Flag-Checks), aber nicht, ob das System die **fachliche Substanz** korrekt erfasst hat. Hinzu kommen fehlende ADRs, schwache Tests und durchgehend untuned Magic Numbers.

Für einen Prototypen ist das **vertretbar, aber nicht gut**. Das Gerüst steht, die Substanz fehlt teilweise.

---

## 2. Schulnoten

| Aspekt | Note | Begründung |
|---|---|---|
| Vorgaben- und Requirements-Treue | 3 | Epics größtenteils umgesetzt, aber fehlende ADRs für Dependencies und WebSocket-Architekturentscheidung verletzen AGENTS.md |
| Architektur & Struktur | 2 | Saubere Modultrennung, jede Datei <300 Zeilen, klare Verantwortlichkeiten, einwandfreier Datenfluss |
| Code-Qualität & Wartbarkeit | 3 | Lesbarer Code, aber Magic Numbers überall, redundante Evaluierungslogik, fragile String-basierte Pattern-Erkennung |
| Redundanz / toter Code | 3 | Ungenutzter Barrel-Export `evaluator.ts`, Python-E2E komplett entkoppelt vom TS-Framework, duplizierte Keyword-Matching-Logik |
| Security | 3 | Keine Secrets im Code, aber keine Input-Validierung für Scenario-Dateien, keine Rate-Limits, verbose Fehlermeldungen |
| Tests | 5 | Nur oberflächliche Evaluator-Unit-Tests mit synthetischen Daten; keine Tests für ws-client, scenario-runner, campaign-reporter; Tests sind teilweise tautologisch |
| Anti-AI-Slop | 4 | Framework wirkt generisch statt projektspezifisch; Assertion-Checks sind Checklisten-Theater; Behavior-Thresholds sind Copilot-Defaults ohne Kalibrierung |
| Prototyp-Fitness | 2 | Richtiger Ansatz, angemessene Komplexität, gute Szenarien, ausbaufähig |
| **Gesamtnote** | **3** | Solides Gerüst mit erkennbaren Schwächen in Testabdeckung und fachlicher Tiefe |

---

## 3. Wichtigste Befunde

### Gravierende Probleme

1. **Tests sind unzureichend (Note 5)**
   - Nur `evaluator.test.ts` existiert — testet ausschließlich Evaluator-Logik mit synthetischen Daten
   - Keine Tests für `ws-client.ts`, `scenario-runner.ts`, `campaign-reporter.ts`
   - Vorhandene Tests sind teilweise tautologisch: Testdaten werden so konstruiert, dass sie per Definition bestehen
   - `backend/tests/e2e_reisekosten.py` ist ein System-Test mit echtem LLM-Call, kein Unit-Test — gehört nicht in die reguläre Test-Suite
   - **Referenz:** `e2e/framework/__tests__/evaluator.test.ts`

2. **Assertion-Checks sind oberflächlich ("Sophisticated Nonsense")**
   - `checkLanguage()` nutzt Stopwort-Heuristik (Ratio <0.1, >20 Wörter) — versagt bei Fachbegriffen, gemischter Sprache
   - `checkOutputContract()` sucht JSON-Blöcke >200 Zeichen — willkürlicher Schwellwert ohne Begründung
   - `checkModeTransitions()` prüft nur Zustandswechsel, nicht ob der Moderator das Richtige tat
   - Keine Assertion prüft die **fachliche Korrektheit** der Artefakte (z.B. ob Prozessschritte logisch zusammenhängen)
   - **Referenz:** `e2e/framework/assertion-evaluator.ts:114-162`

3. **Magic Numbers ohne Kalibrierung**
   - `EVENTS_PER_TURN = 6` (ws-client.ts:25) — hardcoded, bricht wenn Backend Event-Struktur ändert
   - `slotEfficiency >= 0.7` für SEHR_GUT (behavior-evaluator.ts:38) — woher kommt 0.7?
   - `germanRatio < 0.1` für Englisch-Erkennung (assertion-evaluator.ts:130) — woher kommt 0.1?
   - `weak >= totalScenarios * 0.5` für Pattern-Erkennung (campaign-reporter.ts:215) — woher kommt 50%?
   - Keine dieser Schwellwerte ist durch Daten gestützt oder konfigurierbar

### Wichtige Probleme

4. **Fehlende ADRs verletzen AGENTS.md**
   - ADR-009 existiert für das `e2e/` Verzeichnis
   - Keine ADR für neue Dependencies (`ws`, `tsx`, `typescript`, `@types/ws`)
   - Keine ADR für die WebSocket-basierte Testarchitektur (vs. REST-Polling, In-Process-Testing)
   - **Referenz:** `agent-docs/decisions/` — fehlt ADR-010, ADR-011

5. **Python-E2E und TypeScript-E2E sind komplett entkoppelt**
   - `backend/tests/e2e_reisekosten.py` hat eigene WebSocket-Logik, eigene Artefakt-Vergleiche, eigene Testdaten
   - Kein Shared Code, keine gemeinsamen Konstanten (z.B. `EVENTS_PER_TURN` in beiden hartcodiert)
   - Zwei Wartungslasten für denselben Zweck
   - **Referenz:** `backend/tests/e2e_reisekosten.py`, `e2e/framework/ws-client.ts`

6. **Behavior-Probes in Szenarien sind inkonsistent**
   - S01 hat 6 detaillierte Probes, S02 nur 3, S04 prüft nur ob ein `?` in der Antwort steht
   - Turn-ID-Referenzen in Probes werden nicht validiert — Tippfehler führen zu stillem Ignorieren
   - **Referenz:** `e2e/scenarios/s04-ungeduldiger-nutzer.json:140-146`

7. **Ungenutzter Barrel-Export**
   - `e2e/framework/evaluator.ts` re-exportiert AssertionEvaluator und BehaviorEvaluator
   - Wird nirgends importiert — alle Consumer importieren direkt
   - **Referenz:** `e2e/framework/evaluator.ts`

### Positive Punkte

8. **Modulstruktur ist vorbildlich** — Jede Datei hat eine klare Verantwortung, keine zirkulären Imports, alle unter 300 Zeilen

9. **Szenarien sind realistisch und domänensprachlich gut** — S01-S08 decken Happy Path, Edge Cases, Stresstest und Sprachverhalten ab. Deutsche Fachsprache, keine Platzhalter

10. **Architekturansatz ist korrekt** — Trennung deterministische Assertions vs. verhaltensbasierte Scores ist die richtige Strategie für LLM-Testing

---

## 4. Handlungsempfehlungen

### Jetzt beheben

| # | Empfehlung | Begründung |
|---|---|---|
| 1 | **Tests für ws-client und scenario-runner schreiben** | Kernkomponenten sind ungetestet; ein Bug dort invaliert alle Szenario-Ergebnisse |
| 2 | **Tautologische Tests in evaluator.test.ts durch echte Tests ersetzen** | Tests mit synthetischen Daten, die per Design bestehen, bieten keine Sicherheit |
| 3 | **Turn-ID-Validierung beim Laden von Szenarien einbauen** | Stille Fehler bei Tippfehlern in behavior_probes verhindern |

### Bald verbessern

| # | Empfehlung | Begründung |
|---|---|---|
| 4 | **ADRs nachdokumentieren** (Dependencies + WebSocket-Architektur) | AGENTS.md-Compliance; auch für Nachvollziehbarkeit bei Teamübergabe |
| 5 | **Magic Numbers in Konfigurationsdatei extrahieren** | `EVENTS_PER_TURN`, Behavior-Thresholds, Language-Detection-Schwellwerte zentral konfigurierbar machen |
| 6 | **Ungenutzten `evaluator.ts` Barrel-Export entfernen oder durchsetzen** | Toter Code verwirrt |
| 7 | **Python-E2E (`e2e_reisekosten.py`) bewusst positionieren** | Entweder als Legacy-Smoke-Test kennzeichnen oder in das TS-Framework migrieren — Parallelwartung ist Verschwendung |

### Später beobachten

| # | Empfehlung | Begründung |
|---|---|---|
| 8 | **Assertion-Tiefe erhöhen** | Keyword-Matching prüft Vorkommen, nicht Korrektheit; mittelfristig semantische Validierung (z.B. LLM-as-Judge für Artefakt-Konsistenz) evaluieren |
| 9 | **Behavior-Thresholds nach echten Kampagnen-Läufen kalibrieren** | Aktuelle Werte (0.7, 0.5, etc.) sind Annahmen; nach 10+ Läufen datengestützt anpassen |
| 10 | **Szenario-Probes vereinheitlichen** | Alle Szenarien auf konsistente Probe-Dichte bringen; S04 hat nur Fragezeichen-Check |

---

*Dieser Report wurde durch 5 parallel arbeitende Analyse-Agenten erstellt und manuell konsolidiert.*
