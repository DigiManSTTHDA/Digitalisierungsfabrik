# CCB Review: CR-010 — Debug-Logging lückenlos machen

| Feld | Wert |
|---|---|
| **CR** | CR-010 |
| **Review-Datum** | 2026-03-24 |
| **Review-Nr.** | 1 |
| **Empfehlung** | APPROVE WITH CONDITIONS |

## Zusammenfassung

CR-010 wurde durch 6 unabhängige Fachexperten gegen den aktuellen Codestand geprüft: Datenmodell, Orchestrator/Kontrollfluss, Prompts/LLM-Verhalten, Tests/Regression, SDD/ADR-Konformität und Abhängigkeiten/Konflikte. Der CR ist fachlich korrekt, alle Code-Referenzen und Zeilennummern stimmen, und die vorgeschlagene Lösung ist umsetzbar. Zwei Bedingungen sollten bei der Implementierung berücksichtigt werden.

## Empfehlung

**APPROVE WITH CONDITIONS**

Der CR ist vollständig, korrekt und adressiert ein reales Observability-Defizit. Alle behaupteten Code-Defizite wurden durch Analyse verifiziert. Zwei Bedingungen:

1. **ADR-010 formalisieren**: Der CR trifft mindestens 3 architektur-relevante Entscheidungen (Dual-Path-Logging raw/final, Artefakt-Snapshots, Init-Turn-Namensschema), die als ADR dokumentiert werden sollten — kann während der Implementierung erfolgen.
2. **Mindest-Teststrategie**: `write_turn_debug()` hat aktuell 0 Tests und wird um 7 Parameter erweitert. Mindestens ein Unit-Test für die erweiterte Funktion und ein Integrationstest für den Orchestrator-Aufruf sollten ergänzt werden.

## Blocker (müssen behoben werden)

Keine Blocker identifiziert.

## Verbesserungsvorschläge (sollten eingearbeitet werden)

1. **ADR-010 formalisieren** — CR-010 behauptet "Kein ADR erforderlich", trifft aber 3 architektur-relevante Entscheidungen:
   - Dual-Path-Logging (raw LLM-Text vs. finaler Text nach Summarizer)
   - Artefakt-Snapshot-Konvention bei Patch-Anwendung (before/after)
   - Init-Turn-Log-Namensschema (`turn_NNN_init_<modus>.json`)

   **Empfehlung**: ADR-010 als Abschnitt im CR ergänzen. Referenziert und erweitert ADR-008/009.

2. **Mindest-Teststrategie ergänzen** — `write_turn_debug()` hat aktuell **0 Tests** und wird um 7 neue Parameter erweitert. CR-010 fordert nur "Testsuite durchlaufen lassen" (Risiko R-3). Empfohlene Mindest-Tests:
   - Unit-Test: `write_turn_debug()` mit allen neuen Parametern erzeugt korrekte JSON-Struktur
   - Unit-Test: `ModeOutput(summarizer_active=True)` serialisiert korrekt
   - Integrationstest: Orchestrator `process_turn()` mit `LLM_DEBUG_LOG=true` erzeugt Debug-Datei

3. **Konflikttabelle (Abschnitt 3a) vervollständigen** — CR-004 (structuring.py, Implementiert) und CR-008 (orchestrator.py, Entwurf) fehlen in der Tabelle. Kein echter Konflikt, aber die Dokumentation sollte vollständig sein. Insbesondere: CR-008 setzt funktionierendes Debug-Logging voraus.

4. **Ternary-Bug: `phasenstatus` ebenfalls korrigieren** — Der CR identifiziert korrekt den fehlerhaften Ternary in `orchestrator.py:336-342`, aber der Phasenstatus-Fehler wird nicht explizit genannt: `wm.phasenstatus.value` (nach Verarbeitung) statt LLM-Response-Wert wird geloggt. Sollte im gleichen Fix adressiert werden.

## Hinweise

1. **CR-008 Abhängigkeit**: CR-008 (Phase-End-Validator, Status: Entwurf) referenziert in seiner Monitoring-Sektion den `llm_debug_log`-Mechanismus. CR-010 sollte idealerweise vor CR-008 verifiziert sein.

2. **Nur `structuring.py` verwendet den Summarizer** — verifiziert durch Code-Analyse. Falls zukünftige Modi einen Summarizer einführen, muss `summarizer_active` dort ebenfalls gesetzt werden.

3. **SDD-Formulierung**: CR-010 behauptet "Keine Abweichung von der SDD" — das ist technisch korrekt (es behebt eine bestehende Lücke in NFR 8.1.3), aber die Formulierung sollte präzisiert werden zu: "Schließt bestehende Observability-Lücke gemäß NFR 8.1.3."

4. **Storage-Overhead**: Bei 40+ Turns mit Artefakt-Snapshots können Debug-Daten auf mehrere MB anwachsen. Da `LLM_DEBUG_LOG` opt-in ist, akzeptabel. Kein Handlungsbedarf.

## Bestätigungen (CR-Behauptungen, die verifiziert wurden)

1. **`debug_request` in LLM-Clients enthält nur Request-Daten** — Verifiziert in `openai_client.py:132-139` und `anthropic_client.py:101-108`. Nur `system_prompt`, `messages`, `tool_choice`, `model` vorhanden, keine Response-Daten.

2. **Fehlerhafter Ternary in `orchestrator.py:336-342`** — Verifiziert. Bei leeren Patches wird `mode_output.debug_request` (= Request-Daten) als `response_tool_input` übergeben. Das ist semantisch falsch.

3. **Summarizer überschreibt `nutzeraeusserung` unsichtbar** — Verifiziert in `structuring.py:244-247`. `summarize_patches()` ersetzt die Original-LLM-Antwort, wenn Patches vorhanden sind.

4. **Background-Init-Turns unsichtbar** — Verifiziert. `_run_background_init()` in `orchestrator.py:380-472` enthält keinen einzigen `write_turn_debug()`-Aufruf. Bis zu 3 LLM-Calls (Init, Coverage-Validator, Korrektur) sind komplett ungeloggt.

5. **`patches_applied` und `patch_result` immer None** — Verifiziert in `turn_debug_log.py:43-44`. Die Parameter haben Defaults `None` und werden im Orchestrator-Aufruf nie explizit befüllt.

6. **`flag_strings` wird berechnet aber nicht geloggt** — Verifiziert in `orchestrator.py:270-271`. Flags werden als `[f.value for f in mode_output.flags]` extrahiert und in Working Memory gespeichert, aber nicht an `write_turn_debug()` übergeben.

7. **`ModeOutput` ist Pydantic `BaseModel`** — Verifiziert in `base.py:73`. `summarizer_active: bool = False` ist abwärtskompatibel (Default-Wert).

8. **`infer_artifact_type()` und `get_artifact()` existieren** — Verifiziert in `artifact_router.py:32-50` und `53-61`. Bereits im Orchestrator importiert (Zeile 29-34).

9. **Nur `structuring.py` verwendet `summarize_patches()`** — Verifiziert durch Grep. Kein anderer Modus importiert oder nutzt den Summarizer.

10. **CR-006, CR-007, CR-009 sind "Verifiziert"** — Alle drei Status bestätigt durch Verification-Artefakte.

11. **Keine Konflikte mit CR-006/007/009** — Verifiziert. CR-010 erweitert Observability, ändert keine Logik. Orthogonale Concerns.

12. **ADR-008 ist "Überholt durch ADR-009"** — Verifiziert in CR-009 (Zeile 715: "Ablösung: Löst ADR-008 aus CR-006 ab").

## CR-Vollständigkeit

| Pflichtabschnitt | Status |
|---|---|
| Kopfzeile mit Priorität und Abhängigkeiten | ✅ Vorhanden (Kritisch, Abhängigkeiten CR-006/007/009) |
| Problemstellung (Kernproblem, Defizite, Auswirkungen) | ✅ Vorhanden (7 konkrete Defizite mit Code-Referenzen) |
| Ziel der Änderung | ✅ Vorhanden (5 klare Ziele) |
| Lösung mit Code-Beispielen | ✅ Vorhanden (7 Unterabschnitte 3.1–3.7 mit IST/SOLL) |
| Abwärtskompatibilität | ✅ Vorhanden |
| SDD-Konsistenz | ✅ Vorhanden (NFR 8.1.3) |
| ADR-Konsistenz | ⚠️ Vorhanden, aber "Kein ADR erforderlich" ist strittig (siehe Verbesserung #1) |
| Abhängigkeiten & Konflikte (3a) | ⚠️ Vorhanden, aber unvollständig (siehe Verbesserung #3) |
| Änderungsplan | ✅ Vorhanden (8 Zeilen mit Dateien und Änderungen) |
| Risiken und Mitigationen | ✅ Vorhanden (4 Risiken R-1 bis R-4) |
| Nicht im Scope | ✅ Vorhanden (6 explizite Ausschlüsse) |
| Abnahmekriterien | ✅ Vorhanden (13 prüfbare Kriterien) |
| Aufwandsschätzung | ✅ Vorhanden (Komplexität S, 8 Dateien, kein Breaking Change) |

## Lückenanalyse

1. **Fehlende Teststrategie**: CR-010 erweitert `write_turn_debug()` um 7 Parameter und fügt 3 neue Aufrufstellen in `_run_background_init()` hinzu. Die Funktion hat aktuell 0 Tests. Der CR fordert keine neuen Tests.

2. **Fehlender ADR**: 3 Architekturentscheidungen (Dual-Path-Logging, Snapshot-Konvention, Init-Turn-Namensschema) sind nicht als ADR formalisiert.

3. **`phasenstatus`-Bug im Ternary**: Der CR identifiziert den Ternary als fehlerhaft (Request statt Response), benennt aber nicht explizit, dass auch `phasenstatus` falsch ist (`wm.phasenstatus.value` statt LLM-Response-Wert).

4. **Konflikt-Tabelle unvollständig**: CR-004 (structuring.py) und CR-008 (orchestrator.py, Entwurf) fehlen. Kein echter Konflikt, aber Dokumentationslücke.

## Detaillierte Findings pro Experte

### Datenmodell

| # | Finding | Datei:Zeile | Typ |
|---|---------|-------------|-----|
| D-1 | `ModeOutput` ist Pydantic BaseModel, `summarizer_active: bool = False` abwärtskompatibel | `base.py:73-88` | Bestätigung |
| D-2 | Keine Feldkollision mit `summarizer_active` | `base.py:82-88` | Bestätigung |
| D-3 | `debug_request` enthält nur Request-Daten in beiden Clients | `openai_client.py:132-139`, `anthropic_client.py:101-108` | Bestätigung |
| D-4 | `write_turn_debug()` Signatur stimmt mit CR überein (14 Parameter) | `turn_debug_log.py:32-47` | Bestätigung |
| D-5 | `patches_applied` und `patch_result` sind immer None | `turn_debug_log.py:43-44` | Bestätigung |
| D-6 | Zeilennummern in CR stimmen mit aktuellem Code überein | Alle Dateien | Bestätigung |

### Orchestrator & Kontrollfluss

| # | Finding | Datei:Zeile | Typ |
|---|---------|-------------|-----|
| O-1 | Fehlerhafter Ternary bestätigt: `debug_request` als `response_tool_input` bei leeren Patches | `orchestrator.py:336-342` | Bestätigung |
| O-2 | Zusätzlicher Bug: `phasenstatus` wird aus `wm.phasenstatus.value` statt LLM-Response genommen | `orchestrator.py:341` | Verbesserung |
| O-3 | `_run_background_init()` hat 0 `write_turn_debug()`-Aufrufe, 3 LLM-Calls | `orchestrator.py:380-472` | Bestätigung |
| O-4 | `infer_artifact_type()` und `get_artifact()` existieren und sind importiert | `artifact_router.py:32-61`, `orchestrator.py:29-34` | Bestätigung |
| O-5 | `flag_strings` wird in Zeile 270 berechnet, nicht an Debug-Log übergeben | `orchestrator.py:270-271` | Bestätigung |
| O-6 | Artefakt-Snapshots fehlen vor/nach Patch-Anwendung | `orchestrator.py:188-251` | Bestätigung |

### Prompts & LLM-Verhalten

| # | Finding | Datei:Zeile | Typ |
|---|---------|-------------|-----|
| P-1 | Keine Prompt-Änderungen in CR-010 — korrekt, reine Backend-Logging-Erweiterung | — | Bestätigung |
| P-2 | Summarizer in `structuring.py:244-247` überschreibt `nutzeraeusserung` bei Patches | `structuring.py:244-247` | Bestätigung |
| P-3 | Nur `structuring.py` nutzt Summarizer — kein anderer Modus | `modes/*.py` | Bestätigung |
| P-4 | `summarizer_active` muss nur in `structuring.py` gesetzt werden | `structuring.py:249-256` | Bestätigung |

### Tests & Regression

| # | Finding | Datei:Zeile | Typ |
|---|---------|-------------|-----|
| T-1 | Kein Breaking Change durch `summarizer_active: bool = False` (Default schützt) | `tests/test_orchestrator.py` | Bestätigung |
| T-2 | `write_turn_debug()` hat 0 Tests — wird um 7 Parameter erweitert | `core/turn_debug_log.py` | Verbesserung |
| T-3 | Kein Test für `debug_request`-Erzeugung in LLM-Clients | `tests/test_llm_client.py` | Hinweis |
| T-4 | Kein Test für Background-Init Debug-Logging (3 neue Aufrufstellen) | `tests/test_orchestrator.py` | Verbesserung |
| T-5 | CR-010 schlägt keine neuen Tests vor | CR-010 | Verbesserung |
| T-6 | Bestehende ModeOutput-Fixtures funktionieren weiter (Default-Feld) | `tests/test_output_validator.py:24` | Bestätigung |

### SDD, ADRs & Architektur-Konformität

| # | Finding | Referenz | Typ |
|---|---------|----------|-----|
| S-1 | NFR 8.1.3 existiert und fordert vollständiges LLM-Input/Output-Logging | SDD Zeilen 1530-1540 | Bestätigung |
| S-2 | CR-010 schließt bestehende Implementierungslücke in NFR 8.1.3 | SDD 8.1.3 vs. Code | Bestätigung |
| S-3 | "Keine Abweichung von der SDD" ist technisch korrekt, Formulierung ungenau | CR-010 Abschnitt 3 | Hinweis |
| S-4 | ADR-010 sollte formalisiert werden (3 Architekturentscheidungen) | CR-010 Abschnitte 3.4-3.6 | Verbesserung |
| S-5 | ADR-008 korrekt als "überholt durch ADR-009" referenziert | CR-009 Zeile 715 | Bestätigung |
| S-6 | ADR-009 Konformität bestätigt (Single-Call-Architektur) | CR-009, CR-010 | Bestätigung |

### Abhängigkeiten & Konflikte

| # | Finding | Referenz | Typ |
|---|---------|----------|-----|
| A-1 | CR-006, CR-007, CR-009 sind "Verifiziert" — bestätigt | Verification-Artefakte | Bestätigung |
| A-2 | Keine echten Konflikte mit aktiven CRs | Alle CRs | Bestätigung |
| A-3 | CR-004 (structuring.py) fehlt in Konflikttabelle — kein Konflikt, aber Dokumentationslücke | CR-004, CR-010 §3a | Hinweis |
| A-4 | CR-008 (Entwurf, orchestrator.py) fehlt in Konflikttabelle — kein Konflikt, aber Abhängigkeit | CR-008, CR-010 §3a | Hinweis |
| A-5 | CR-008 setzt funktionierendes Debug-Logging voraus → CR-010 sollte zuerst verifiziert werden | CR-008 Monitoring-Sektion | Hinweis |
