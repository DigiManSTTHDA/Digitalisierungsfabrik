# Verifikation: CR-006 — Background-Initialisierung mit Validierung

| Feld | Wert |
|---|---|
| **CR** | CR-006 |
| **Verifikationsdatum** | 2026-03-23 |
| **Ergebnis** | BESTANDEN |

## Zusammenfassung

CR-006 implementiert eine Background-Initialisierungsphase, die Struktur- und Algorithmusartefakte deterministisch aufbaut, bevor Structurer und Specifier in den Dialog-Modus eintreten. Alle 14 Änderungsplan-Punkte wurden korrekt umgesetzt, alle prüfbaren Abnahmekriterien (12/13) sind erfüllt, 459/460 Tests sind grün (1 pre-existing Failure unabhängig von CR-006), alle Risiko-Mitigationen und Review-Bedingungen sind implementiert, und die Architektur ist vollständig SDD- und ADR-008-konform.

## Ergebnis

**BESTANDEN**

Null Blocker, null echte Lücken. Alle Abweichungen vom ursprünglichen Plan (llm/tools.py, structuring.py, specification.py, test_orchestrator.py-Korrekturen) sind durch Review-Bedingungen C-1/C-2 oder notwendige technische Korrekturen (Hinweis H-2) begründet. AC #13 (SDD-Update) ist explizit per ADR-008 §3.10 auf nach Verifikation verschoben und nicht verifikationspflichtig.

## Änderungsplan-Vollständigkeit

| # | Plan-Zeile | Status | Details |
|---|---|---|---|
| 1 | `models.py`: `InitStatus(StrEnum)` mit `init_in_progress`/`init_complete` | Umgesetzt | `backend/artifacts/models.py` vor `EmmaAktionstyp` |
| 2 | `modes/base.py`: `ModeOutput.init_status: InitStatus \| None = None` | Umgesetzt | `backend/modes/base.py`, Default `None` — abwärtskompatibel |
| 3 | `working_memory.py`: `init_hinweise: list[str]` | Umgesetzt | `Field(default_factory=list)` — abwärtskompatibel |
| 4 | `artifacts/init_validator.py` (neu): R-1 bis R-6 | Umgesetzt | `validate_structure_artifact()` + `validate_algorithm_artifact()` mit `StructuralViolation` |
| 5 | `prompts/init_coverage_validator.md` (neu) | Umgesetzt | Coverage-only-Prompt, JSON-Output, keine Content-Erfindung |
| 6 | `modes/init_structuring.py` (neu): `InitStructuringMode` | Umgesetzt | Erbt von `BaseMode`, gibt `ModeOutput` zurück, liest `init_structuring.md` |
| 7 | `modes/init_specification.py` (neu): `InitSpecificationMode` | Umgesetzt | Analoges Pattern zu `InitStructuringMode` |
| 8 | `modes/init_coverage_validator.py` (neu): `InitCoverageValidatorMode` | Umgesetzt | `tools=None`, JSON-Parsing, gibt `ModeOutput` zurück |
| 9 | `prompts/init_structuring.md` (neu) | Umgesetzt | Variable Lineage `[VAR: name]`, ANALOG-Kennzeichnung, kein Dialog |
| 10 | `prompts/init_specification.md` (neu) | Umgesetzt | ANALOG → WAIT + `emma_kompatibel: false`, `init_status`-Signal |
| 11 | `core/orchestrator.py`: Init-Hook + 5 neue Methoden | Umgesetzt | `_init_required()`, `_run_background_init()`, `_run_structural_validator()`, `_run_coverage_validator()`, `_run_correction_turns()`; `_MAX_INIT_TURNS=8`, `_MAX_CORRECTION_TURNS=2` |
| 12 | `api/websocket.py`: 3 Init-Modi registrieren | Umgesetzt | `init_structuring`, `init_specification`, `init_coverage_validator` in `_build_orchestrator()` |
| 13 | `prompts/structuring.md`: Erstaktivierung entfernen, `{init_hinweise}` | Umgesetzt | Sektion ersetzt durch "Arbeitsstart mit vorhandenem Artefakt" + Platzhalter |
| 14 | `prompts/specification.md`: Erstaktivierung entfernen, `{init_hinweise}` | Umgesetzt | Bullet-Point entfernt, `{init_hinweise}` ergänzt |
| C-1 | `_run_correction_turns()` + `_run_structural_validator()` spezifizieren | Umgesetzt | Korrekte Signatur, `error_hint`-Feedback, `_MAX_CORRECTION_TURNS=2` |
| C-2 | `structuring.py` + `specification.py`: `init_hinweise`-Injektion | Umgesetzt | Beide Modes injecten `init_hinweise` aus `context.working_memory` |
| + | `llm/tools.py`: `INIT_APPLY_PATCHES_TOOL` (nicht im Plan) | Abweichung (sinnvoll) | Notwendig für `init_status`-Feld in LLM-Tool-Schema; Plan implizierte es; keine SDD-Verletzung |
| + | `test_orchestrator.py`: Mode-Key-Inkonsistenz korrigiert (H-2) | Abweichung (sinnvoll) | Review-Hinweis H-2 adressiert; ohne Fix wären Init-Mode-Tests nicht registriert |

## Abnahmekriterien

| # | Kriterium | Erfüllt? | Evidenz |
|---|---|---|---|
| 1 | `_init_required()` gibt `True` nur wenn Exploration vorhanden + Init nicht durchgeführt | Ja | `orchestrator.py`: prüft `exploration_artifact.slots`, `init_status != init_complete` |
| 2 | Init-Loop läuft maximal `_MAX_INIT_TURNS=8` Mal | Ja | `orchestrator.py:_run_background_init()` — `for _ in range(self._MAX_INIT_TURNS)` |
| 3 | `_run_structural_validator()` aggregiert Violations aus R-1 bis R-6 | Ja | Ruft `validate_structure_artifact()` + `validate_algorithm_artifact()` auf |
| 4 | `_run_coverage_validator()` ruft `init_coverage_validator`-Modus auf (nicht direkt LLM) | Ja | `self._modes.get("init_coverage_validator")` — kein direkter LLM-Client |
| 5 | Coverage-Validator gibt ausschließlich `"warnung"` zurück (nie `"kritisch"`) | Ja | `init_coverage_validator.md` Prompt: `"severity": "warnung"` explizit; Python-Validator separat |
| 6 | `_run_correction_turns()` max. `_MAX_CORRECTION_TURNS=2` Iterationen | Ja | `orchestrator.py:_run_correction_turns()` — `range(self._MAX_CORRECTION_TURNS)` |
| 7 | `init_hinweise` aus Validator-Violations in `WorkingMemory` gespeichert | Ja | `_run_background_init()` setzt `working_memory.init_hinweise` |
| 8 | `init_hinweise` in `structuring.py` und `specification.py` injiziert | Ja | Beide Modes ersetzen `{init_hinweise}` aus `context.working_memory.init_hinweise` |
| 9 | Initialisierung ist transparent (kein Nutzer-Turn, kein Warten) | Ja | Init-Modes setzen `nutzeraeusserung=""`, kein WebSocket-Event an Client |
| 10 | Bestehende Tests bleiben grün (Regression) | Ja | 459/460 Tests grün; 1 pre-existing Failure unabhängig von CR-006 |
| 11 | Neue `init_*`-Modi in `test_orchestrator.py:_make_default_modes()` registriert | Ja | Alle 3 Init-Modi + Mode-Key-Korrektur (H-2) in `_make_default_modes()` |
| 12 | `test_init_validator.py` mit ≥15 Tests für R-1 bis R-6 | Ja | 21 Tests (5+4+4+3+2+3) — alle grün |
| 13 | SDD §6.3, §6.5.2, §6.6 um Init-Loop-Beschreibung ergänzt | Ausstehend (post-verification) | Per ADR-008 §3.10 explizit verschoben: "SDD §6.3 wird nach Verifikation ergänzt" |

## Test-Ergebnisse

**459/460 Tests grün.** 21 neue Tests in `test_init_validator.py` (alle grün). Abwärtskompatibilität bestätigt: neue Felder `init_status`, `init_hinweise` haben Pydantic-Defaults und deserialisieren alte JSON-Artefakte ohne Fehler. Der eine fehlgeschlagene Test (`test_specification_system_prompt_contains_operationalisierbarkeit`) ist pre-existing: der Text `"Welche Aktion?"` war nie in `specification.md` enthalten, unabhängig von CR-006 (via `git stash` verifiziert).

## Mitigationen & Review-Bedingungen

| # | Mitigation/Bedingung | Umgesetzt? | Evidenz |
|---|---|---|---|
| R-1 | Timeout-Budget: `_MAX_INIT_TURNS=8`, ADR-008 ~40s < 60s | Ja | `orchestrator.py`: `_MAX_INIT_TURNS = 8` als Klassenattribut |
| R-2 | Init-Fehler sicher abfangen, kein Absturz | Ja | `_run_background_init()` wrapped in try/except, setzt `init_hinweise` bei Fehler |
| R-3 | Coverage-Validator gibt nur `"warnung"` (keine `"kritisch"`-Violations) | Ja | Prompt explizit, Parsing-Code filtert `"warnung"` |
| R-4 | Prompt-Token-Budget: Init-Prompts ohne Dialog-History | Ja | Init-Modes übergeben leere History / kurzen Kontext |
| R-5 | Abwärtskompatibilität: alle neuen Felder optional mit Defaults | Ja | `init_status: ... = None`, `init_hinweise: ... = Field(default_factory=list)` |
| C-1 | `_run_correction_turns()` + `_run_structural_validator()` spezifiziert | Ja | Beide Methoden mit korrekter Signatur, `error_hint`-Feedback, `_MAX_CORRECTION_TURNS=2` |
| C-2 | `{init_hinweise}`-Platzhalter + Injection in `structuring.py`/`specification.py` | Ja | Beide Prompts haben Platzhalter; beide Mode-Klassen injizieren `init_hinweise` |

## SDD- & ADR-Konformität

**SDD-Konformität: konform.** Die Implementierung verletzt keine SDD-Prinzipien. Deterministischer Orchestrator steuert Init-Loop (nicht LLM), LLM-Schreibrechte bleiben auf Patch-Mechanismus beschränkt, alle neuen Felder sind optional und abwärtskompatibel. AC #13 (SDD-Update) ist gemäß ADR-008 §3.10 explizit auf nach Verifikation verschoben.

**ADR-008-Konformität: konform.**

| ADR-008-Aspekt | Konform? | Evidenz |
|---|---|---|
| Init-Loop max. `_MAX_INIT_TURNS=8` | Ja | `orchestrator.py:_MAX_INIT_TURNS = 8` |
| Coverage-Validator als registrierter Modus (nicht direkter LLM-Call) | Ja | `self._modes.get("init_coverage_validator")` |
| `ModeOutput.init_status` statt separatem `InitModeOutput` | Ja | `base.py`: `init_status: InitStatus | None = None` |
| Correction-Turns max. `_MAX_CORRECTION_TURNS=2` | Ja | `orchestrator.py:_MAX_CORRECTION_TURNS = 2` |
| Init transparent für Nutzer | Ja | `nutzeraeusserung=""`, kein Client-Event |
| SDD-Update nach Verifikation | Ausstehend (korrekt verschoben) | ADR-008 §3.10 explizit |
| Timeout-Budget ~40s < 60s Browser/LB | Ja | 8 Turns × ~5s = ~40s Budget |

## Blocker (müssen nachgebessert werden)

Keine.

## Abweichungen vom Plan

1. **`llm/tools.py`: `INIT_APPLY_PATCHES_TOOL` (nicht explizit im Plan)** — sinnvoll und notwendig. Init-Modi brauchen ein Tool-Schema mit `init_status`-Feld; der Plan implizierte diese Änderung durch die Vorgabe `init_status` im LLM-Response-Format. Keine SDD-Verletzung.
2. **`test_orchestrator.py`: Mode-Key-Korrektur (H-2, Review-Hinweis)** — sinnvoll. Ohne Korrektur wären Init-Mode-Tests mit falschen Keys registriert und hätten Folgetests gebrochen.
3. **`modes/structuring.py`, `modes/specification.py` (C-2, nicht im Original-Plan)** — Review-Bedingung C-2 explizit beauftragt.

## Lücken

Keine.
