# Codebase Review — Kalibriert

**Scope:** `e2e/` Verzeichnis, E2E Epics 12–14, `backend/tests/e2e_reisekosten.py`
**Datum:** 2026-03-19
**Methode:** Skeptische Kalibrierung des Erstreviews gegen tatsächlichen Code

---

## 1. Kalibrierungsurteil

Die ursprüngliche Review ist **strukturell solide, aber in mehreren Findings überzogen oder faktisch falsch**. Die Architektur- und Strukturbewertung (Note 2) ist zutreffend. Die Slop-Bewertung (Note 4) ist zu hart — der Code ist deutlich projektspezifischer als behauptet. Die Test-Bewertung (Note 5) ist in der Richtung korrekt, aber die Begründung ("tautologische Tests") hält der Prüfung nicht stand. Mehrere Findings basieren auf Annahmen statt auf verifizierter Evidenz.

**Hauptproblem des Erstreviews:** Die Anti-AI-Slop-Analyse hat Oberflächensignale (Schwellwerte, Barrel-Export, Heuristiken) als Copilot-Müll eingestuft, obwohl die Verifikation zeigt, dass der Code projektspezifisch konzipiert ist. Das verzerrt das Gesamtbild.

---

## 2. Re-kalibrierte Findings

### Finding 1 — Tests unzureichend (Original: gravierend)

**Ursprüngliche Aussage:** Nur oberflächliche Evaluator-Unit-Tests mit synthetischen Daten; Tests sind teilweise tautologisch.

**Evidenzprüfung:** 16 Testfälle in `evaluator.test.ts` — 8 für AssertionEvaluator, 5 für BehaviorEvaluator, 3 für CampaignReporter. Die Tests sind **nicht tautologisch**: `test_mode_transition_invalid` würde bei gebrochenem Flag-Check fehlschlagen, `test_artifact_integrity_invalid_refs` prüft echte Referenzintegrität, `test_dialog_quality_sehr_gut` vs `_mangelhaft` testen gegensätzliche Bedingungen.

**Was stimmt:** Keine Tests für ws-client, scenario-runner und den Großteil des campaign-reporters. Das ist eine echte Lücke — ein Bug im WebSocket-Client oder Scenario-Runner invalidiert alle Ergebnisse, ohne entdeckt zu werden.

**Neue Einstufung: B (Plausibler Hinweis)**
Testabdeckung ist lückenhaft (nur 1 von 7 Modulen getestet), aber die vorhandenen Tests sind nicht tautologisch. Die Note 5 war überzogen.

**Korrigierte Fassung:** Testabdeckung ist unvollständig — ws-client, scenario-runner und campaign-reporter haben keine Tests. Vorhandene Evaluator-Tests sind sinnvoll und falsifizierbar, aber decken nur einen Teil des Frameworks ab.

---

### Finding 2 — Assertion-Checks oberflächlich (Original: gravierend, "Sophisticated Nonsense")

**Ursprüngliche Aussage:** checkLanguage() nutzt Stopwort-Heuristik, checkOutputContract() hat willkürlichen 200-Zeichen-Schwellwert, keine fachliche Korrektheitsüberprüfung.

**Evidenzprüfung:**
- `checkLanguage()` ist eine pragmatische Heuristik: filtert Sätze <5 Wörter, prüft nur Sätze >20 Wörter, nutzt deutsches Stopwort-Verhältnis. Für einen Prototypen ist das **vertretbar**.
- `checkOutputContract()` mit 200-Zeichen-Schwellwert: prüft ob JSON-Dumps in Chat-Antworten stecken. Der Schwellwert ist grob, aber der Zweck ist klar und die Implementierung funktional.
- `checkModeTransitions()` prüft tatsächlich nur Zustandswechsel, nicht fachliche Korrektheit — das ist korrekt.
- Der Vorwurf "Sophisticated Nonsense" ist **nicht gerechtfertigt**. Die Checks tun, was sie sollen: strukturelle SDD-Regeln prüfen.

**Was stimmt:** Keine Assertion prüft fachliche Artefakt-Korrektheit (z.B. ob Prozessschritte logisch zusammenhängen). Das ist eine echte Lücke, aber kein "Nonsense" — es ist eine bewusste Scope-Grenze.

**Neue Einstufung: D (Für Prototypen okay)**
Assertions prüfen strukturelle SDD-Regeln zuverlässig. Fachliche Tiefe fehlt, ist aber für einen Prototypen vertretbar und als Erweiterung sinnvoll.

**Korrigierte Fassung:** Assertions prüfen 7 strukturelle SDD-Regeln (Mode-Transitions, Phase-Sequencing, Sprache, Output-Contract, Artefakt-Integrität, EMMA-Kompatibilität). Fachliche/semantische Validierung fehlt — dies ist die logische nächste Ausbaustufe, aber kein Defekt.

---

### Finding 3 — Magic Numbers ohne Kalibrierung (Original: gravierend)

**Ursprüngliche Aussage:** Schwellwerte (0.7, 0.1, 50%) sind "Copilot-Defaults ohne Kalibrierung".

**Evidenzprüfung:** Die BehaviorEvaluator-Schwellwerte sind **nicht** generische Copilot-Defaults. Sie referenzieren projektspezifische Konzepte: `slotEfficiency`, `nudgeCount`, `moderator turns`, `keyConceptCoverage`, `responseTime p95`. Die Werte (0.7/0.5/0.3 für Slot-Effizienz, ≤2/≤3 Moderator-Turns, 20s/30s Response-Zeiten) sind **domänenspezifisch dimensioniert**.

**Was stimmt:** `EVENTS_PER_TURN = 6` in ws-client.ts ist tatsächlich hartcodiert ohne Erklärung und bricht bei Backend-Änderungen. Das ist ein echtes Fragilisierungsrisiko. Die Schwellwerte könnten konfigurierbar sein, aber ihr aktueller Zustand ist kein gravierendes Problem.

**Neue Einstufung: B (Plausibler Hinweis)**
`EVENTS_PER_TURN` ist fragil (echtes Problem). Behavior-Thresholds sind nicht kalibriert, aber auch nicht "Copilot-Defaults" — sie sind domänenspezifisch geschätzt.

**Korrigierte Fassung:** `EVENTS_PER_TURN = 6` ist fragil und sollte dokumentiert oder dynamisch erkannt werden. Behavior-Thresholds sind unkalibriert aber projektspezifisch; Konfigurierbarkeit wäre wünschenswert, ist aber kein gravierender Mangel.

---

### Finding 4 — Fehlende ADRs (Original: wichtig)

**Ursprüngliche Aussage:** Keine ADR für Dependencies (ws, tsx, typescript) und WebSocket-Architektur.

**Evidenzprüfung:** **ADR-009 existiert und deckt beides ab** — sowohl das `e2e/` Verzeichnis als auch die Dependencies (ws, tsx, typescript). Die Review hat die ADR nicht gelesen oder nicht gründlich genug geprüft.

**Was stimmt:** Die WebSocket-basierte Testarchitektur als Design-Entscheidung (vs. REST-Polling, In-Process) wird in ADR-009 angesprochen, könnte aber expliziter begründet sein.

**Neue Einstufung: E (Nicht ausreichend belegt)**
Die Kernbehauptung (fehlende ADRs für Dependencies) ist faktisch falsch.

---

### Finding 5 — Python-E2E und TypeScript-E2E entkoppelt (Original: wichtig)

**Ursprüngliche Aussage:** Zwei komplett getrennte E2E-Implementierungen ohne Shared Code.

**Evidenzprüfung:** Bestätigt. `backend/tests/e2e_reisekosten.py` ist ein eigenständiger System-Test mit eigener WebSocket-Logik, echten LLM-Calls (OpenAI GPT-4o), eigener Artefakt-Vergleichslogik (60% keyword + 40% string similarity) und eigener Datenladung. Kein Shared Code mit dem TS-Framework.

**Konkreter Schaden:** Bei API-Änderungen müssen zwei Codebases aktualisiert werden. Allerdings: der Python-Test ist ein Smoke-Test mit anderer Zielsetzung (echte LLM-Integration) als das TS-Framework (strukturelle/behaviorale Assertions). Die Entkopplung ist **teilweise bewusst**.

**Neue Einstufung: B (Plausibler Hinweis)**
Die Parallelwartung ist real, aber die Testziele unterscheiden sich. Klarere Positionierung wäre hilfreich.

---

### Finding 6 — Behavior-Probes inkonsistent (Original: wichtig)

**Ursprüngliche Aussage:** S01 hat 6 Probes, S02 nur 3, S04 prüft nur ein Fragezeichen.

**Evidenzprüfung:** **Übertrieben.**
- S01 (komplex, mit Eskalationen) hat 6 Probes — angemessen für die Komplexität
- S02 (einfacher Happy Path) hat 3 Probes — angemessen für den Scope
- S04 hat 3 Probes (nicht nur einen Fragezeichen-Check!): einen dialog_check mit `?`-Pattern, einen state_check auf `expected_mode`, und einen artifact_check mit Slot-Validierung

**Was stimmt:** Turn-ID-Referenzen in Probes werden nicht validiert — ein Tippfehler führt zu stillem Ignorieren. Das ist ein echtes, wenn auch kleines Problem.

**Neue Einstufung: C (Stil/Konvention) für die Probe-Dichte, B (Plausibler Hinweis) für die fehlende Turn-ID-Validierung**

**Korrigierte Fassung:** Die unterschiedliche Probe-Dichte ist intentional (komplex vs. einfach). Turn-ID-Referenzen in Probes sollten beim Laden validiert werden, um stille Fehler zu vermeiden.

---

### Finding 7 — Ungenutzter Barrel-Export (Original: wichtig)

**Ursprüngliche Aussage:** `evaluator.ts` wird nirgends importiert.

**Evidenzprüfung:** Korrekt — aktuell importieren beide Consumer (`run-campaign.ts`, `evaluator.test.ts`) direkt von den spezifischen Dateien. Der Barrel-Export ist ein bewusstes Public-API-Pattern für externe Konsumenten.

**Konkreter Schaden:** Minimal. 10 Zeilen Code ohne Funktion, aber auch ohne Verwirrungspotential.

**Neue Einstufung: F (Verwerfen)**
Ein unbenutzter Barrel-Export in einem 7-Datei-Framework ist kein "wichtiges Problem". Es ist eine Stilfrage.

---

## 3. Verworfen oder deutlich abgeschwächt

| Finding | Original-Einstufung | Kalibriert | Grund |
|---|---|---|---|
| "Sophisticated Nonsense" bei Assertions | Gravierend | D (Prototyp okay) | Checks tun was sie sollen; "Nonsense"-Label ist Reviewer-Theater |
| "Copilot-Defaults" bei Behavior-Thresholds | Gravierend | Widerlegt | Thresholds sind projektspezifisch, nicht generisch |
| Fehlende ADRs für Dependencies | Wichtig | E (Nicht belegt) | ADR-009 existiert und deckt Dependencies ab |
| S04 "nur Fragezeichen-Check" | Wichtig | Faktisch falsch | S04 hat 3 verschiedene Probes |
| Ungenutzter Barrel-Export | Wichtig | F (Verwerfen) | 10 Zeilen, kein Schaden, Stilfrage |
| "Generisches Framework" (Anti-Slop Note 4) | Note 4 | Widerlegt | BehaviorEvaluator ist hochgradig projektspezifisch |
| "Tautologische Tests" | Gravierend | Widerlegt | 16 Tests sind falsifizierbar; würden bei Bugs fehlschlagen |

---

## 4. Bereinigtes Gesamtbild

Nach Entfernung von Reviewer-Theater bleiben **drei echte Findings**:

### A — Belastbare Probleme

1. **Testabdeckung ist lückenhaft.** Nur Evaluator-Modul hat Tests (16 Tests, sinnvoll). ws-client, scenario-runner, campaign-reporter sind ungetestet. Ein Bug dort invalidiert alle Kampagnen-Ergebnisse unentdeckt.

2. **`EVENTS_PER_TURN = 6` ist fragil.** Hardcoded ohne Erklärung. Bricht bei Backend-Änderungen. Sollte dokumentiert oder dynamisch erkannt werden.

### B — Plausible Hinweise

3. **Python-E2E sollte bewusst positioniert werden.** Der Python-Test (`e2e_reisekosten.py`) hat eine andere Zielsetzung (echte LLM-Integration) als das TS-Framework (strukturelle Assertions). Beides ist sinnvoll, aber die Abgrenzung fehlt.

4. **Turn-ID-Validierung beim Szenario-Laden fehlt.** Tippfehler in `behavior_probes.after_turn` führen zu stillem Ignorieren.

5. **campaign-reporter Pattern-Detection ist String-basiert.** `generateRecommendations()` matcht auf Substrings in Pattern-Texten — fragil bei Textänderungen.

### Alles andere ist Prototyp-vertretbar oder Stilkritik.

---

## 5. Korrigierte Teilnoten

| Aspekt | Original | Kalibriert | Begründung |
|---|---|---|---|
| Vorgaben- und Requirements-Treue | 3 | **2** | ADR-009 deckt ab, was die Review als fehlend bemängelt hat |
| Architektur & Struktur | 2 | **2** | Bestätigt — saubere Modultrennung |
| Code-Qualität & Wartbarkeit | 3 | **2–3** | Magic Numbers sind weniger gravierend als dargestellt; Code ist projektspezifisch |
| Redundanz / toter Code | 3 | **3** | Python/TS-Parallelität ist real, Barrel-Export ist vernachlässigbar |
| Security | 3 | **3** | Bestätigt — angemessen für Prototyp, keine groben Fehler |
| Tests | 5 | **3–4** | Vorhandene Tests sind sinnvoll, aber Abdeckung lückenhaft (1 von 7 Modulen) |
| Anti-AI-Slop | 4 | **2** | Code ist projektspezifisch, nicht generisch; "Slop"-Diagnose war falsch |
| Prototyp-Fitness | 2 | **2** | Bestätigt — richtiger Ansatz, angemessene Komplexität |
| **Gesamtnote** | **3** | **2–3** | Solider Prototyp mit lückenhafter Testabdeckung als einzigem substanziellem Mangel |

---

*Kalibrierung durchgeführt durch Evidenzprüfung gegen den tatsächlichen Quellcode. Sieben von zehn Findings des Erstreviews wurden abgeschwächt, widerlegt oder verworfen.*
