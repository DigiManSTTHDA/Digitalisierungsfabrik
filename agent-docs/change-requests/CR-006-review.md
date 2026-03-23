# CCB Review: CR-006 — Background-Initialisierung mit Validierung

| Feld | Wert |
|---|---|
| **CR** | CR-006 |
| **Review-Datum** | 2026-03-23 |
| **Review-Nr.** | 1 |
| **Empfehlung** | REWORK REQUIRED |

## Zusammenfassung

CR-006 adressiert ein real existierendes und gut dokumentiertes Qualitätsproblem: die Erstaktivierungsüberlastung des ersten Dialog-Turns in Structurer und Specifier. Der Ansatz (Background-Init-Loop, Python-Validator, LLM-Coverage-Check) ist architektonisch schlüssig. Das CCB identifiziert jedoch **zwei harte Blocker**, die den CR in der vorliegenden Form nicht implementierbar machen: eine explizite Interface-Inkonsistenz zwischen `InitModeOutput` und `BaseMode.call()`, sowie ein ungelöstes architektonisches Problem bei der LLM-Nutzung im Orchestrator. Beide Blocker erfordern eine Designentscheidung, die im CR schriftlich fixiert sein muss, bevor mit der Implementierung begonnen werden kann.

## Empfehlung

**REWORK REQUIRED**

Der CR ist konzeptionell ausgereift und qualitativ überdurchschnittlich. Er muss jedoch in zwei Kernabschnitten (§3.2 und §3.5) überarbeitet werden, um die Blocker aufzulösen. Vier weitere Verbesserungen sollten eingearbeitet werden. Nach Überarbeitung wird ein Re-Review erwartet.

## Blocker (müssen behoben werden)

**B-1: `BaseMode.call()` ↔ `InitModeOutput` — nicht implementierbare Typinkompatibilität**

`backend/modes/base.py:107` definiert:
```python
async def call(self, context: ModeContext) -> ModeOutput:
```

`ModeOutput` hat Pflichtfelder: `nutzeraeusserung: str`, `phasenstatus: Phasenstatus`, `flags: list[Flag]`.

CR-006 §3.2 schlägt `InitModeOutput(BaseModel)` vor mit nur `patches` und `init_status` — **ohne die ModeOutput-Pflichtfelder**. Gleichzeitig sagt CR-006 §3.6 "erbt von BaseMode". Das ist ein Typ-Widerspruch: Ein Modus, der von `BaseMode` erbt, muss `ModeOutput` zurückgeben. Der Orchestrator greift in `process_turn` direkt auf `mode_output.nutzeraeusserung`, `.phasenstatus`, `.flags` zu — Code der gegen Init-Modi laufen würde, würde einen `AttributeError` werfen.

**Erforderliche Designentscheidung im CR (eine der folgenden Optionen):**
- Option A: `init_status: InitStatus | None = None` als optionales Feld in `ModeOutput` hinzufügen. Init-Modi setzen dieses Feld, Dialog-Modi ignorieren es. `nutzeraeusserung=""`, `phasenstatus=Phasenstatus.in_progress` als dummy.
- Option B: Separate abstrakte Basisklasse `InitBaseMode` mit eigener Signatur `async def call(context) -> InitModeOutput`. Init-Modi erben von `InitBaseMode`, nicht von `BaseMode`. Der Orchestrator-Init-Hook ruft `init_mode.call(context)` mit dem korrekten Typ auf.
- Option C: `InitModeOutput` erbt von `ModeOutput` und überschreibt Pflichtfelder mit nutzeraeusserung=`""`, phasenstatus als dummy.

Die gewählte Option muss in §3.2 dokumentiert und in §3.6 konsistent referenziert sein.

---

**B-2: `_run_coverage_validator()` hat keinen LLM-Zugriff im Orchestrator**

`backend/core/orchestrator.py` hat keinen LLM-Client. Der Orchestrator-Konstruktor (Zeile 87–98) akzeptiert nur `repository`, `modes`, `settings`. LLM-Zugriff erfolgt ausschließlich über die registrierten Modi (injiziert in `api/websocket.py:_build_orchestrator()`, Zeilen 40–54 — `llm` wird dort erzeugt, aber **nicht** an den Orchestrator übergeben).

CR-006 §3.5 schlägt vor:
```python
coverage_violations = await self._run_coverage_validator(project, target_mode)
```
Diese Methode muss einen LLM-Call machen (gegen `init_coverage_validator.md`). Es gibt keinen Pfad, über den `self` diesen Call ausführen kann.

**Erforderliche Designentscheidung im CR (eine der folgenden Optionen):**
- Option A: `llm_client: LLMClient` zum Orchestrator-Konstruktor hinzufügen. `_build_orchestrator()` in `api/websocket.py` übergibt `llm`. Orchestrator-Änderungsplan (§4, Punkt 9) und `api/websocket.py` als neue Änderungsdatei ergänzen. **Pro:** Direkter LLM-Zugriff. **Contra:** Orchestrator verliert Separation-of-Concerns.
- Option B: Coverage-Validator als registrierter Modus umsetzen (`backend/modes/init_coverage_validator.py`). Orchestrator ruft `self._modes.get("init_coverage_validator").call(context)` auf. Der Modus gibt ModeOutput/InitModeOutput mit der Coverage-Violation-Liste zurück. **Pro:** Bleibt im Modus-Pattern. **Contra:** Etwas mehr Boilerplate. Erfordert neue Datei in Änderungsplan.
- Option C: Coverage-Validator entfällt in erster Version, nur Python-Validator. LLM-Coverage als separater CR dokumentieren.

Die gewählte Option muss in §3.4 und §3.5 konsistent dokumentiert sein. `api/websocket.py` (bei Option A) oder ein neuer Modus (bei Option B) muss in §4 (Änderungsplan) erscheinen.

## Verbesserungsvorschläge (sollten eingearbeitet werden)

**V-1: Änderungsplan Punkt 10 — Modi-Registrierungsort ist falsch**

`backend/modes/__init__.py` ist eine **leere Datei** (1 Zeile). Modi werden nicht dort, sondern in `api/websocket.py:_build_orchestrator()` (Zeilen 40–54) registriert. Änderungsplan Punkt 10 ("Init-Modi registrieren in `backend/modes/__init__.py`") muss auf `api/websocket.py` korrigiert werden.

**V-2: `InitStatus`-Enum-Wert `"in_progress"` kollidiert mit `Phasenstatus.in_progress`**

Beide StrEnums (`InitStatus` und `Phasenstatus`) würden den identischen String-Wert `"in_progress"` enthalten. Semantisch unterschiedlich (Init-Loop läuft vs. Dialog-Phase läuft), aber in Logs und Debugging schwer unterscheidbar. Empfehlung: `InitStatus`-Werte umbenennen, z.B. `init_in_progress` / `init_complete`.

**V-3: Orchestrator-Tests explizit im Änderungsplan nennen**

`test_orchestrator.py:_make_default_modes()` (Zeile 51–58) registriert keine Init-Modi. Tests die `Flag.return_to_mode` mit leerem Struktur-Artefakt auslösen (Zeile 813, 947) werden durch den Init-Hook brechen, wenn `init_structuring` nicht registriert ist. Änderungsplan und Abnahmekriterium #11 müssen diese Tests explizit nennen.

**V-4: ADR-008 Begründung präzisieren**

ADR-008 (§3.10) nennt "WebSocket-Timeout-Risiko ist akzeptabel (Max-Init-Turns × ~5s ≈ 40s bei MAX_INIT_TURNS=8)" ohne Beleg. Die Aussage "WebSocket-Verbindung bleibt offen" (R-1) ist keine Mitigation gegen Timeout — eine offene Connection ohne Response blockiert Kapazität. ADR-008 sollte explizit quantifizieren: warum 40s < typischer Browser-/Load-Balancer-Timeout, und Konfigurierbarkeit von `MAX_INIT_TURNS` als primären Mitigation-Hebel benennen.

## Hinweise

1. **`_build_first_turn_directive()` erfordert keine Änderung** (`structuring.py:69–94`, `specification.py:106–143`): Beide Funktionen geben `""` zurück, wenn das Zielartefakt nicht leer ist. Nach dem Init-Loop ist das Artefakt nicht leer — die Python-Funktionen verhalten sich korrekt ohne Codeänderung. Sie müssen nicht in den Änderungsplan.

2. **CR-004 muss committed sein, bevor CR-006 beginnt**: CR-004 entfernt die Erstaktivierungs-Sektion aus `structuring.md`. CR-006 §3.8 setzt dies voraus. Die Implementierungsreihenfolge ist CR-002 → CR-003 → CR-004 → CR-006.

3. **SDD-Update als Abnahmekriterium, nicht Folge-Task**: §6 ("Nicht im Scope") sagt "SDD §6.3 und §6.6 werden nach Verifikation aktualisiert". Das ist keine Scope-Ausgrenzung — es ist eine Konsequenz die aktiv als **Abnahmekriterium #13** definiert werden sollte, damit es nicht vergessen wird.

4. **Variablen-Crosscheck R-4 ist eine Heuristik**: Der String-Substring-Match in `validate_structure_artifact()` (§3.3, Zeile 173–183) ist fragil (Variationen, Abkürzungen). Das ist für einen Prototype akzeptabel, sollte aber in den Risiken als R-5 (neu) dokumentiert sein.

5. **Fehlerbehandlung bei kritischen Init-Violations nach 2 Korrektur-Turns**: Der Dialog-Modus startet auch bei verbliebenen kritischen Violations. Die Dialog-Prompts (§3.8) werden mit "Artefakt bereits vorhanden"-Kurzanweisung gestartet ohne Kenntnis kritischer Violations. Empfehlung: `init_hinweise` sollte auch kritische Violations (nicht nur Warnungen) enthalten, wenn Korrektur-Turns ausgeschöpft sind.

## Bestätigungen (CR-Behauptungen, die verifiziert wurden)

1. ✅ `Flag.return_to_mode` existiert in `Flag`-Enum (`base.py:45`) und ist der korrekte Einhängepunkt im Orchestrator (Zeile 262).
2. ✅ `self._executor.apply_patches(artifact_type, artifact, patches)` ist die korrekte und einzige Schreibmethode — passt für Init-Patches (orchestrator.py:194).
3. ✅ `advance_phase()` setzt `wm.vorheriger_modus = primary_mode` (phase_transition.py:80) — synchron mit dem Init-Hook-Design.
4. ✅ `Strukturschritt.spannungsfeld: str | None` existiert bereits (models.py:167) — `ANALOG:`-Konvention ist ohne Schema-Änderung implementierbar.
5. ✅ Alle benötigten Template-Pfade für Init-Patches (structure und algorithm) sind in `STRUCTURE_TEMPLATE` und `ALGORITHM_TEMPLATE` vorhanden (template_schema.py).
6. ✅ `WorkingMemory.init_hinweise: list[str] = Field(default_factory=list)` ist backward-compatible — Pydantic v2 deserialisiert alte WM-Datensätze ohne das Feld fehlerfrei mit Default `[]`.
7. ✅ CR-005 ist vollständig in CR-006 absorbiert: D-1 (Variable Lineage), D-2 (ANALOG-Früherkennung), D-3 (Specifier-Erstaktivierung) sind alle in §3.7 enthalten.
8. ✅ Keine Konflikte mit bestehenden ADRs (ADR-006: EmmaAktionstyp-Enum; ADR-007: Validierungsbericht). ADR-008 ist eine neue, additive Entscheidung.
9. ✅ `_build_init_context()` kann `build_context()` aus `context_assembler.py` direkt nutzen — die Funktion ist universal und phasenunabhängig.
10. ✅ Python-Validator-Prüfregeln R-1 bis R-6 sind konsistent mit dem Datenmodell aus CR-002 und CR-003.

## CR-Vollständigkeit

| Abschnitt | Status |
|---|---|
| Kopfzeile mit Priorität und Abhängigkeiten | ✅ vorhanden |
| Problemstellung mit Kernproblem, Defiziten, Auswirkungen | ✅ vorhanden |
| Ziel der Änderung | ✅ vorhanden |
| Lösung mit Datenmodell, Beispielen, SDD-Konsistenz | ✅ vorhanden (mit Blockers) |
| ADR (bei SDD-Abweichung) | ✅ ADR-008 vorhanden |
| Abhängigkeiten & Konflikte (Abschnitt 3a) | ✅ vorhanden |
| Änderungsplan mit präzisen Dateipfaden | ⚠️ Punkt 10 falsch (modes/__init__.py statt api/websocket.py) |
| Risiken und Mitigationen | ⚠️ R-1 Mitigation schwach, R-4 Halluzination nicht ausgearbeitet |
| Nicht im Scope | ⚠️ SDD-Update fälschlicherweise als "nicht im Scope" |
| Abnahmekriterien (prüfbar) | ✅ 12 Kriterien, konkret |
| Aufwandsschätzung mit Komplexität und Breaking Change | ✅ vorhanden (L, 13 Dateien, Breaking Change: Ja) |

## Lückenanalyse

**Fehlende Dateien im Änderungsplan:**
- `api/websocket.py` fehlt (notwendig für B-2, je nach gewählter Option)
- `backend/modes/init_coverage_validator.py` fehlt (notwendig wenn B-2 Option B gewählt)
- `backend/tests/test_orchestrator.py` nicht explizit als anzupassende Datei genannt (breaking tests)

**Fehlende Risiken:**
- R-5 (neu): Variablen-Crosscheck String-Match ist fragil — sollte explizit als bekannte Schwäche dokumentiert sein
- R-6 (neu): Dialog-Modus erhält keine Notification bei kritischen Violations nach Korrektur-Turns

**Fehlende Abnahmekriterien:**
- AC #13 (neu): SDD §6.3, §6.6 und ggf. §5.8 nach Verifikation aktualisiert

## Detaillierte Findings pro Experte

### Datenmodell
- **[Blocker B-1]** `BaseMode.call() -> ModeOutput` ist inkompatibel mit der vorgeschlagenen `InitModeOutput` ohne `nutzeraeusserung`/`phasenstatus`/`flags`. Typinkompatibilität, kein valides Python-Subtyping.
- **[Verbesserung V-2]** `InitStatus.in_progress == "in_progress"` kollidiert semantisch mit `Phasenstatus.in_progress`.
- **[Bestätigung]** `WorkingMemory.init_hinweise: list[str]` mit `default_factory=list` ist backward-compatible mit Pydantic v2 — keine Migration nötig.
- **[Bestätigung]** Template-Pfade für alle Init-Patches sind in bestehenden TEMPLATES vorhanden.

### Orchestrator & Kontrollfluss
- **[Blocker B-2]** `Orchestrator.__init__()` hat keinen `llm_client`. `_run_coverage_validator()` ist nicht implementierbar ohne LLM-Zugriff. Modi werden in `api/websocket.py:_build_orchestrator()` registriert, nicht in `modes/__init__.py`.
- **[Verbesserung V-1]** Änderungsplan Punkt 10 referenziert falsche Datei.
- **[Bestätigung]** `Flag.return_to_mode` Hook-Point (orchestrator.py:262) ist korrekt. `advance_phase()` → `wm.vorheriger_modus = primary_mode` ist synchron mit Init-Hook-Design.
- **[Bestätigung]** `_build_init_context()` kann direkt auf `build_context()` aufbauen.

### Prompts & LLM-Verhalten
- **[Hinweis]** `_build_first_turn_directive()` in Python (structuring.py:69, specification.py:106) braucht keine Änderung — gibt `""` zurück wenn Artefakt nicht leer ist. Python-Dateien müssen nicht in den Änderungsplan.
- **[Bestätigung]** Erstaktivierungs-Sektionen in beiden Prompt-Dateien existieren und müssen entfernt werden (CR §3.8 ist korrekt).
- **[Hinweis]** Init-Prompts brauchen dieselben Platzhalter-Injektionen wie Dialog-Prompts, aber ohne Dialog-spezifischen Context (_build_first_turn_directive etc.).
- **[Hinweis]** Dialog-Prompts sind ca. 10.000–18.000 Tokens nach Injektion. Init-Prompts werden kürzer (kein Dialog-Overhead) — ~3.000–4.000 Tokens geschätzt.

### Tests & Regression
- **[Verbesserung V-3]** test_orchestrator.py Zeile 813 und 947: Tests mit `return_to_mode` und leerem Struktur-Artefakt werden durch Init-Hook brechen, wenn Init-Modi nicht registriert sind. `_make_default_modes()` (Zeile 51–58) muss `init_structuring` und `init_specification` enthalten.
- **[Bestätigung]** test_flag_enum_has_expected_values (len(Flag)==8) bricht nicht — CR-006 fügt keine neuen Flags hinzu.
- **[Bestätigung]** WorkingMemory-Round-Trip-Tests bleiben grün dank Pydantic-Defaults für `init_hinweise`.

### SDD, ADRs & Architektur-Konformität
- **[Bestätigung]** ADR-008 dokumentiert die SDD §6.3-Abweichung (Inline-Multi-Call). Konzeptionell nachvollziehbar.
- **[Verbesserung V-4]** ADR-008-Begründung ist zu knapp: Timeout-Budget nicht quantifiziert, Konfigurierbarkeit `MAX_INIT_TURNS` nicht als Mitigation genannt.
- **[Hinweis SDD-Update]** SDD §6.3 (Schritt 10b), §6.5.2 ("Pro Turn") und neu §6.6.6 ("Init-Submodi") müssen nach Verifikation aktualisiert werden. Dies sollte als Abnahmekriterium #13 in den CR.
- **[Bestätigung]** Keine Verletzung bestehender ADRs (ADR-006, ADR-007). Init-Modi verletzen nicht das Mode-Pattern, da sie als Orchestrator-interne Subroutinen laufen.

### Abhängigkeiten & Konflikte
- **[Bestätigung]** CR-005 vollständig absorbiert (D-1, D-2, D-3 alle in CR-006 §3.7 enthalten).
- **[Bestätigung]** Keine Konflikte mit CR-001–CR-004. Python-Validator R-1 bis R-6 konsistent mit CR-002-Feldern (`regeln`, `schleifenkoerper`, `konvergenz`).
- **[Hinweis]** CR-004 muss committed sein vor CR-006-Implementierungsstart (structuring.md Erstaktivierung).
- **[Bestätigung]** Abhängigkeiten auf CR-002 (Implementiert), CR-003 (Verifiziert), CR-004 (Implementiert) sind korrekt und erfüllt.
