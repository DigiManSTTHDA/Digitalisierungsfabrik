# CCB Review: CR-009 — Init-Rewrite — Single-Call-Architektur mit aufgewertetem Coverage-Validator

| Feld | Wert |
|---|---|
| **CR** | CR-009 |
| **Review-Datum** | 2026-03-24 |
| **Review-Nr.** | 1 |
| **Empfehlung** | APPROVE WITH CONDITIONS |

## Zusammenfassung

CR-009 wurde durch 5 parallele Experten-Analysen geprüft: Datenmodell, Orchestrator/Kontrollfluss, Prompts/LLM-Verhalten, Tests/Regression, und SDD/ADR-Konformitat. Der CR ist konzeptionell solide, gut dokumentiert und adressiert reale Probleme der bestehenden Init-Implementierung. Die Single-Call-Architektur ist eine klare Vereinfachung. Zwei Bedingungen mussen vor Implementierung erfullt werden.

## Empfehlung

**APPROVE WITH CONDITIONS**

Der CR ist architektonisch korrekt, gut begrundet und vollstandig genug fur die Implementierung. Zwei Bedingungen mussen wahrend der Implementierung beachtet werden (siehe unten). Keine Blocker identifiziert.

## Blocker (mussen behoben werden)

Keine Blocker identifiziert.

## Verbesserungsvorschlage (sollten eingearbeitet werden)

### Bedingung 1: `test_init_validator.py` im Anderungsplan erganzen

Der Anderungsplan (Abschnitt 4) listet 12 Dateien auf, nennt aber `backend/tests/test_init_validator.py` nicht. Die Entfernung von R-2, R-3, R-4, R-6 aus `init_validator.py` (Punkt #4) bricht 11 bestehende Tests:

| Test-Klasse | Regel | Aktion |
|-------------|-------|--------|
| `TestR2Feldvollstaendigkeit` (4 Tests) | R-2 | Loschen |
| `TestR3GraphKonsistenz` (3 Tests, 1 kann bleiben) | R-3 | Loschen |
| `TestR4VariablenCrosscheck` (2 Tests, 1 kann bleiben) | R-4 | Loschen |
| `TestR6AnalogKonsistenz` (2 Tests, 1 kann bleiben) | R-6 | Loschen |

Tests fur R-1 (5 Tests) und R-5 (2 Tests) bleiben unverandert.

**Aktion**: Punkt #4a zum Anderungsplan hinzufugen: `backend/tests/test_init_validator.py` — Tests fur R-2, R-3, R-4, R-6 entfernen; Docstring aktualisieren.

### Bedingung 2: Fehlerbehandlung in `_run_background_init` sicherstellen

Der vorgeschlagene Code in Abschnitt 3.1 hat keine Exception-Handling fur LLM-Call-Fehler. Die bestehende Implementierung hat das gleiche Problem, aber bei 3 sequentiellen LLM-Calls (Init + Coverage + Korrektur) sollte ein `try/except` um die gesamte Methode oder um jeden LLM-Call sichergestellt werden, damit der Dialog-Modus auch bei Init-Fehlern gestartet wird.

**Aktion**: Wahrend der Implementierung `try/except` um `_run_background_init` oder die einzelnen `await`-Calls sicherstellen. Bei Fehler: `logger.error()` + Dialog-Modus trotzdem starten (mit leerem/unvollstandigem Artefakt).

## Hinweise

1. **`_format_validator_feedback` ubergibt alle Violations (inkl. Warnungen), nicht nur kritische.** Das ist sinnvoll — der Korrektur-Call bekommt mehr Kontext. Der Prompt-Text sagt "Korrigiere die kritischen Befunde", was das LLM korrekt steuert. Kein Handlungsbedarf.

2. **Keine Re-Validierung nach Korrektur-Call.** Der CR dokumentiert das als bewusste Entscheidung ("einmal reicht"). Fur den Prototyp akzeptabel. Optional: Eine schnelle Python-Validierung (nur R-1 + R-5, kein LLM) nach dem Korrektur-Call ware billig und wurde dangling references fangen.

3. **Phase-Timing beim Coverage-Validator ist korrekt.** Die Phase ist beim Coverage-Validator-Aufruf bereits auf die neue Phase gesetzt (z.B. `strukturierung`). Der CR nutzt `context.aktive_phase == Projektphase.strukturierung` um den Ubergang Exploration→Struktur zu identifizieren. Das ist korrekt, weil: wenn aktive_phase=strukturierung, dann wurde gerade das Strukturartefakt initialisiert (aus Exploration). Wenn aktive_phase=spezifikation, dann das Algorithmusartefakt (aus Struktur).

4. **CR-007 Kompatibilitat.** CR-007 wurde fur `MAX_INIT_TURNS=8` konzipiert. Mit CR-009 sinkt die Anzahl auf max 3 Calls. CR-007 bleibt kompatibel, aber seine `max_turns`-Annahmen sind konservativer als notig. Kein Handlungsbedarf — CR-007 wird ggf. bei Implementierung angepasst.

5. **ADR-Referenzierung.** CR-009 referenziert ADR-008 korrekt und erstellt ADR-009 als Ablosung. Weitere ADRs (ADR-001 bis ADR-007) sind nicht betroffen. Eine explizite Abgrenzung ware schon, ist aber nicht notwendig.

6. **SDD-Update.** Die SDD (Abschnitt 6.3, 11-Schritt-Zyklus) beschreibt keinen Platz fur Multi-Call-Loops innerhalb eines Turns. CR-009 dokumentiert korrekt: "SDD-Aktualisierung erfolgt nach Verifikation." Das ist das etablierte Pattern (CR-006 handhabte es genauso).

## Bestatigungen (CR-Behauptungen, die verifiziert wurden)

1. **InitStatus wird nur in Init-Modi und Orchestrator referenziert.** Grep bestatigt: `models.py`, `base.py`, `orchestrator.py`, `init_structuring.py`, `init_specification.py`, `tools.py`. Keine versteckten Abhangigkeiten in anderen Dateien.

2. **`_run_correction_turns` wird nur von `_run_background_init` aufgerufen.** Sicheres Loschen.

3. **`_MAX_INIT_TURNS` und `_MAX_CORRECTION_TURNS` werden nur in den entfallenden Loops referenziert.** Sicheres Loschen.

4. **`init_hinweise` in WorkingMemory funktioniert korrekt.** Wird von `structuring.py:197-204` und `specification.py:206-214` als `{init_hinweise}` in die Dialog-Prompts injiziert. Unabhangig von `{validator_feedback}` (anderer Mechanismus, anderer Zeitpunkt).

5. **`validator_feedback` auf ModeContext hat keine Naming-Konflikte.** Semantisch getrennt von `error_hint` (Patch-Validierung vs. Content-Validierung). Modellierung mit `with_validator_feedback()` analog zu `with_error_hint()` ist konsistent.

6. **Python-Validator-Fokussierung auf R-1 + R-5 ist architektonisch sinnvoll.** R-1 (referenzielle Integritat) und R-5 (Abschnitt-Mapping) sind deterministische Strukturprufungen, die ein LLM nicht zuverlassig leisten kann. R-2, R-3, R-4, R-6 sind semantische Prufungen, die besser in den Coverage-Validator-Prompt gehoren.

7. **CR-007 und CR-008 sind tatsachlich unabhangig.** CR-007 betrifft UI-Feedback wahrend Init (kompatibel). CR-008 betrifft Phasenabschluss-Validierung (vollig unabhangig).

8. **ADR-009 ist formal korrekt.** Kontext, Entscheidung, Begrundung, Ablosung, Konsequenzen sind vollstandig dokumentiert.

9. **Architektonische Prinzipien werden respektiert.** "LLM als Operator mit beschrankten Schreibrechten" (Init-Modi geben nur Patches zuruck, Orchestrator fuhrt aus). "Deterministische Orchestrierung" (Entscheidungen im Orchestrator sind regelbasiert, LLM-Zugriff nur uber registrierte Modi).

10. **Bestehende Tests in `test_orchestrator.py`, `test_structuring_mode.py`, `test_specification_mode.py` bleiben grun.** Keine dieser Dateien referenziert `InitStatus`, `_MAX_INIT_TURNS` oder die entfallenden Methoden.

## CR-Vollstandigkeit

| Pflichtabschnitt | Status |
|------------------|--------|
| Kopfzeile mit Prioritat und Abhangigkeiten | Vorhanden |
| Problemstellung (Kernproblem, Defizite, Auswirkungen) | Vorhanden, gut belegt |
| Ziel der Anderung | Vorhanden, messbar |
| Losung (Modell, Beispiele, Prompts, Abwartskompatibilitat) | Vorhanden, umfangreich |
| ADR (bei SDD-Abweichung) | Vorhanden (ADR-009) |
| Abhangigkeiten & Konflikte (3a) | Vorhanden, korrekt |
| Anderungsplan | Vorhanden, 12 Eintrage (1 fehlt, s. Bedingung 1) |
| Risiken und Mitigationen | Vorhanden, 5 Risiken |
| Nicht im Scope | Vorhanden |
| Abnahmekriterien | Vorhanden, 14 prufbare Kriterien |
| Aufwandsschatzung | Vorhanden (M, 12 Dateien, Breaking Change) |

## Luckenanalyse

1. **Fehlende Datei im Anderungsplan**: `backend/tests/test_init_validator.py` — muss fur Regel-Entfernung angepasst werden (s. Bedingung 1).

2. **Fehlendes Abnahmekriterium fur Fehlerbehandlung**: Kein AC pruft, ob `_run_background_init` bei LLM-Fehlern graceful degradiert (s. Bedingung 2).

3. **Kein explizites AC fur `_build_structure_content` und `_build_algorithm_content`**: Der CR erwahnt diese neuen Helper-Funktionen in Abschnitt 3.10 (Coverage-Validator-Modus soll vollstandige Artefaktinhalte statt Kurzubersichten liefern), aber es gibt kein AC, das pruft, ob diese Funktionen existieren und den vollen Inhalt liefern. Kann wahrend Implementierung implizit erfullt werden.

## Detaillierte Findings pro Experte

### Datenmodell

- `InitStatus` Enum-Entfernung ist sicher (nur in Init-Modi und Orchestrator referenziert)
- `init_status` auf `ModeOutput` Entfernung ist sicher (nicht persistiert, nicht in nicht-Init-Modi verwendet)
- `validator_feedback` auf `ModeContext` ist korrekt modelliert, keine Naming-Konflikte
- `INIT_APPLY_PATCHES_TOOL` Vereinfachung ist sicher
- Pydantic-Validierung wird nicht beeintrachtigt

### Orchestrator & Kontrollfluss

- Neuer `_run_background_init` Ablauf ist logisch korrekt
- `_format_validator_feedback` und `with_validator_feedback()` sind neue Methoden, die implementiert werden mussen (kein Blocker im CR, das IST die Arbeit)
- Fehlerbehandlung sollte sichergestellt werden (Bedingung 2)
- Keine Re-Validierung nach Korrektur ist dokumentiert und akzeptabel
- Keine versteckten Abhangigkeiten auf `_MAX_INIT_TURNS` oder `InitStatus`

### Prompts & LLM-Verhalten

- Template-Variablen-Injection (`{validator_feedback}`, `{transition_type_description}`, etc.) mussen wahrend Implementierung erstellt werden (das ist der Kern der Arbeit, kein Blocker)
- Phase-Timing beim Coverage-Validator ist korrekt (aktive_phase = neue Phase = korrekte Transitionsidentifikation)
- `{init_hinweise}` ist ein separater Mechanismus (Dialog-Prompts, nach Init), kein Konflikt mit `{validator_feedback}` (Init-Prompts, wahrend Korrektur)
- Prompt-Rewrites auf ~300 Zeilen sind angemessen und konsistent mit Dialog-Prompt-Qualitat

### Tests & Regression

- 11 Tests in `test_init_validator.py` mussen geloscht werden (R-2, R-3, R-4, R-6)
- 7 Tests bleiben (R-1: 5, R-5: 2)
- Keine Tests in `test_orchestrator.py`, `test_structuring_mode.py`, `test_specification_mode.py` brechen
- Lucke: Keine bestehenden Tests fur `_run_background_init` — neue Tests sollten nach Implementierung geschrieben werden (nicht im CR-Scope, da kein Test-Rewrite gefordert)

### SDD, ADRs & Architektur-Konformitat

- ADR-009 lost ADR-008 korrekt ab (formal und inhaltlich)
- SDD-Konsistenz: Bekannte Abweichung (Multi-Call in einem Turn), handhabbar durch Post-Verifikation-Update
- Architektonische Prinzipien werden respektiert
- CR-007 und CR-008 Unabhangigkeit bestatigt

### Abhangigkeiten & Konflikte

- Alle genannten Abhangigkeiten sind korrekt
- Keine unentdeckten Konflikte mit aktiven CRs
- CR-002 Kontrollfluss-Felder werden in Init-Prompts implizit adressiert (uber Modellierungsregeln aus structuring.md)
