# CCB Review: CR-006 — Background-Initialisierung mit Validierung

| Feld | Wert |
|---|---|
| **CR** | CR-006 |
| **Review-Datum** | 2026-03-23 |
| **Review-Nr.** | 2 |
| **Empfehlung** | APPROVE WITH CONDITIONS |

## Zusammenfassung

CR-006 wurde nach REWORK REQUIRED (Review-1) vollständig überarbeitet. Alle 2 Blocker (B-1: `InitModeOutput`-Typinkompatibilität; B-2: LLM-Zugriff im Orchestrator) und alle 4 Verbesserungen (V-1 bis V-4) sowie das SDD-Update als AC #13 sind korrekt im CR-Body eingearbeitet. Die Architektur-Grundlage ist solide und implementierbar. Zwei Verbesserungen bleiben offen: `_run_correction_turns()` ist im CR aufgerufen aber nirgends spezifiziert, und die Verdrahtung von `wm.init_hinweise` zu den Dialog-Prompts fehlt im Änderungsplan.

## Empfehlung

**APPROVE WITH CONDITIONS**

Beide Blocker sind behoben, alle Abhängigkeiten sind erfüllt, der Implementierungspfad ist klar. Zwei Verbesserungen sind vor Implementierung in den CR einzuarbeiten — sie erfordern keine Architekturentscheidungen.

## Blocker (müssen behoben werden)

Keine Blocker identifiziert.

*Blocker B-1 und B-2 aus Review-1 sind korrekt adressiert:*
- B-1 → Option A gewählt: `ModeOutput` bekommt `init_status: InitStatus | None = None`; `InitModeOutput` entfällt; Werte `init_in_progress` / `init_complete` vermeiden Kollision mit `Phasenstatus.in_progress`
- B-2 → Option B gewählt: Coverage-Validator als registrierter Modus (`init_coverage_validator.py`); `_run_coverage_validator()` ruft `self._modes.get("init_coverage_validator").call(context)` auf; kein LLM-Client im Orchestrator nötig

## Verbesserungsvorschläge (sollten eingearbeitet werden)

**V-5: `_run_correction_turns()` in §3.5 ist aufgerufen aber nirgends spezifiziert**

In `_run_background_init()` (§3.5, Zeile 323):
```python
await self._run_correction_turns(project, wm, init_mode, kritische)
```
Diese Methode ist **nicht definiert** — weder als Pseudocode noch als Signatur. `_MAX_CORRECTION_TURNS = 2` ist zwar gesetzt und §3.1 nennt "Korrektur-Turns falls kritische Befunde (max. 2)", aber ein Implementierer muss das Verhalten erraten.

**Erforderliche Ergänzung in §3.5:**
```python
async def _run_correction_turns(
    self,
    project: Project,
    wm: WorkingMemory,
    init_mode: BaseMode,
    violations: list[StructuralViolation],
) -> None:
    """Max. _MAX_CORRECTION_TURNS Init-Turns mit Violation-Feedback."""
    violation_hint = "\n".join(f"[{v.severity}] {v.message}" for v in violations)
    for _ in range(_MAX_CORRECTION_TURNS):
        context = self._build_init_context(project, wm).with_error_hint(
            f"Folgende strukturelle Probleme müssen behoben werden:\n{violation_hint}"
        )
        output = await init_mode.call(context)
        if output.patches:
            source_type = "structure" if ... else "algorithm"
            result = self._executor.apply_patches(source_type, get_artifact(project, source_type), output.patches)
            if result.success:
                set_artifact(project, source_type, result.artifact)
        remaining = self._run_structural_validator(project, ...)
        kritische = [v for v in remaining if v.severity == "kritisch"]
        if not kritische:
            break
```
Auch `_run_structural_validator()` ist aufgerufen (§3.5, Zeile 314) aber nicht explizit definiert — sie sollte ebenfalls in §3.5 als:
```python
def _run_structural_validator(self, project, target_mode) -> list[StructuralViolation]:
    if target_mode == "structuring":
        return validate_structure_artifact(project.exploration_artifact, project.structure_artifact)
    elif target_mode == "specification":
        return validate_algorithm_artifact(project.structure_artifact, project.algorithm_artifact)
    return []
```

---

**V-6: `init_hinweise`-Verdrahtung zu Dialog-Prompts fehlt im Änderungsplan**

AC #10 fordert: "Dialog-Modus nennt zu Beginn die `init_hinweise` wenn vorhanden."

Analyse des aktuellen Codes:
- `structuring.md` hat **kein** `{init_hinweise}`-Platzhalter
- `structuring.py:192–199` injiziert `{context_summary}`, `{exploration_content}`, `{slot_status}` — kein `init_hinweise`
- `specification.py:200–205`: analog
- `working_memory.init_hinweise` ist für Dialog-Modi **nicht sichtbar**, außer es wird explizit injiziert

Der Änderungsplan (§4) listet `structuring.py` und `specification.py` **nicht** als zu ändernde Dateien. Ohne Injektion kann AC #10 nicht erfüllt werden.

**Erforderliche Ergänzungen in §4:**

| # | Datei | Änderung |
|---|---|---|
| 15 (neu) | `backend/modes/structuring.py` | `{init_hinweise}` in System-Prompt-Injektion einfügen: `system_prompt = system_prompt.replace("{init_hinweise}", "\n".join(context.working_memory.init_hinweise))` |
| 16 (neu) | `backend/modes/specification.py` | Analog |

Außerdem: `structuring.md` und `specification.md` (§4 Punkte 13/14) um `{init_hinweise}`-Sektion ergänzen — z.B.:
```
{init_hinweise}
```
(Zeigt Warnungen aus Init-Validierung, bleibt leer wenn `[]`)

Aufwandsschätzung: +2 Dateien in §4 (Punkte 15/16), Betroffene Dateien von 14 auf 16.

## Hinweise

1. **Pre-existing uncommitted changes in `structuring.md`:** `git status` zeigt `M backend/prompts/structuring.md` — es gibt bereits nicht-committete Änderungen an dieser Datei, unabhängig von CR-006. Der Implementierer muss vor CR-006-Implementierung prüfen, was in diesem Diff steht und ob es mit §4 Punkt 13 kompatibel ist.

2. **Mode-Key-Inkonsistenz in `test_orchestrator.py:_make_default_modes()`:** Zeile 51–58 registriert `"strukturierung"` statt `"structuring"`, `"spezifikation"` statt `"specification"`. Das ist ein **pre-existing Bug**, nicht durch CR-006 eingeführt. Wenn CR-006 die Init-Modi dort registriert (AC #11), sollte die Gelegenheit genutzt werden, die bestehenden Keys auf `"structuring"` / `"specification"` / `"validation"` zu korrigieren.

3. **Tests 813/947 brechen NICHT:** Entgegen der Befürchtung in V-3 (Review-1) werden diese Tests durch den Init-Hook **nicht brechen** — weil `_run_background_init` bei `init_mode is None` mit `logger.warning()` und `return` endet (CR §3.5). Die Custom-Orchestrators in diesen Tests registrieren keinen `init_structuring`-Modus → graceful fallback. AC #11 ist trotzdem korrekt formuliert (Init-Modi in `_make_default_modes()` für vollständige Test-Coverage).

4. **`_build_init_context()` nicht im Änderungsplan:** §3.5 ruft `self._build_init_context(project, wm)` auf. Diese Methode existiert noch nicht — sie muss als Wrapper um `build_context()` aus `context_assembler.py` geschrieben werden. Sie ist implizit in §4 Punkt 11 (`orchestrator.py`) enthalten, sollte aber dort explizit erwähnt werden.

## Bestätigungen (CR-Behauptungen, die verifiziert wurden)

1. ✅ **B-1 behoben**: `init_status: InitStatus | None = None` als optionales Feld in `ModeOutput` ist Pydantic-v2-backward-compatible. Alle bestehenden `ModeOutput()`-Instantiierungen in Tests bleiben grün (optionales Feld mit Default `None`).
2. ✅ **B-2 behoben**: `_run_coverage_validator()` als Orchestrator-Methode, die `self._modes.get("init_coverage_validator").call(context)` aufruft. JSON-Rückgabe in `nutzeraeusserung` ist korrekt implementiert.
3. ✅ **V-1 behoben**: `api/websocket.py` in §4 als Punkt 12 (statt `modes/__init__.py`).
4. ✅ **V-2 behoben**: `InitStatus` Werte `init_in_progress`/`init_complete` — kein Kollision mit `Phasenstatus.in_progress`.
5. ✅ **V-3 behoben**: AC #11 nennt `_make_default_modes()` und Tests ~813/947 explizit.
6. ✅ **V-4 behoben**: ADR-008 mit konkretem Timeout-Budget (40s < Browser/LB-Default 60s), `MAX_INIT_TURNS` als Konfigurierbarkeits-Hebel.
7. ✅ **SDD-Update**: AC #13 (SDD §6.3, §6.5.2, §6.6 nach Verifikation) korrekt als Abnahmekriterium eingetragen.
8. ✅ **Flag.return_to_mode** Einhängepunkt (orchestrator.py:262) bestätigt — korrekt positioniert.
9. ✅ **`get_artifact()` / `set_artifact()`** in `artifact_router.py` vorhanden und bereits importiert im Orchestrator.
10. ✅ **`PHASE_TO_MODE`** hat korrekte String-Werte ("structuring", "specification") — konsistent mit `_init_required()`.
11. ✅ **`build_context()`** in `context_assembler.py` ist universal/phasenunabhängig — direkt nutzbar für `_build_init_context()`.
12. ✅ **`_build_first_turn_directive()`** gibt `""` zurück wenn Artefakt nicht leer ist (structuring.py:75, specification.py:113) — kein Eingriff in Python-Dateien nötig.
13. ✅ **Alle Validator-Felder** (nachfolger, regeln.nachfolger, schleifenkoerper, konvergenz, bedingung, ausnahme_beschreibung, spannungsfeld, struktur_ref, emma_kompatibel, slots["variablen_und_daten"]) existieren in models.py mit korrekten Typen.
14. ✅ **WorkingMemory.init_hinweise** und **ModeOutput.init_status** als optionale Felder mit Pydantic-Default sind vollständig backward-compatible.
15. ✅ **CR-004** ist committed (788411a auf main) — CR-006 darf `structuring.md` weiter modifizieren.
16. ✅ **R-1 bis R-6** im Python-Validator konsistent mit CR-002/CR-003 Felddefinitionen.

## CR-Vollständigkeit

| Abschnitt | Status |
|---|---|
| Kopfzeile mit Priorität und Abhängigkeiten | ✅ vorhanden |
| Problemstellung mit Kernproblem, Defiziten, Auswirkungen | ✅ vorhanden |
| Ziel der Änderung | ✅ vorhanden |
| Lösung mit Datenmodell, Init-Loop, Validator, Coverage | ✅ vorhanden |
| ADR-008 (SDD-Abweichung §6.3) | ✅ vorhanden, konkretisiert |
| Abhängigkeiten & Konflikte (§3a) | ✅ vorhanden |
| Änderungsplan mit Dateipfaden | ⚠️ 2 Dateien fehlen (structuring.py, specification.py für init_hinweise-Injektion) |
| Risiken und Mitigationen | ✅ R-1 bis R-5 vorhanden |
| Nicht im Scope | ✅ vorhanden |
| Abnahmekriterien (prüfbar) | ✅ 13 Kriterien, konkret |
| Aufwandsschätzung | ⚠️ 14 Dateien angegeben, nach V-6 sind es 16 |

## Lückenanalyse

**Fehlende Dateien im Änderungsplan:**
- `backend/modes/structuring.py` (init_hinweise-Injektion in System-Prompt)
- `backend/modes/specification.py` (analog)

**Fehlende Spezifikation in §3.5:**
- `_run_correction_turns()` — Signatur und Verhalten nicht dokumentiert
- `_run_structural_validator()` — Signatur nicht explizit dokumentiert (implizit durch §3.3)

**Fehlende Prompt-Platzhalter:**
- `{init_hinweise}` in `structuring.md` und `specification.md`

**Fehlende Risiken:**
- Keine (R-1 bis R-5 sind vollständig)

**Fehlende Abnahmekriterien:**
- AC #10 kann ohne V-6-Fix nicht verifiziert werden — aber das AC selbst ist korrekt formuliert

## Detaillierte Findings pro Experte

### Datenmodell
- **[Bestätigung]** `InitStatus` StrEnum sicher hinzufügbar — kein Naming-Konflikt mit `CompletenessStatus`, `Phasenstatus`, `Projektstatus`.
- **[Bestätigung]** `init_status: InitStatus | None = None` in `ModeOutput` (base.py): optionales Feld, Pydantic-v2 backward-compatible. Import von `InitStatus` in base.py muss ergänzt werden.
- **[Bestätigung]** `init_hinweise: list[str] = Field(default_factory=list)` in WorkingMemory: identisches Pattern zu `flags: list[str] = Field(default_factory=list)` (Zeile 40) — sicher.
- **[Bestätigung]** Alle vom Validator referenzierten Felder existieren und sind korrekt typisiert (nachfolger: list[str], regel.nachfolger: str, schleifenkoerper: list[str], konvergenz: str|None, emma_kompatibel: bool, exploration.slots: dict[str, ExplorationSlot]).

### Orchestrator & Kontrollfluss
- **[Bestätigung]** `Flag.return_to_mode`-Block in orchestrator.py:262–272 ist der korrekte Einhängepunkt.
- **[Bestätigung]** `get_artifact()` / `set_artifact()` in artifact_router.py vorhanden und importiert (orchestrator.py:21–26). Korrektes Muster für init_patches.
- **[Bestätigung]** `PHASE_TO_MODE` gibt "structuring" / "specification" als Strings zurück — konsistent mit `_init_required()`.
- **[Verbesserung V-5]** `_run_correction_turns()` und `_run_structural_validator()` aufgerufen aber nicht definiert. Muss in §3.5 ergänzt werden.
- **[Bestätigung]** `build_context()` in context_assembler.py ist universell nutzbar für `_build_init_context()`.
- **[Hinweis]** `_build_init_context()` fehlt im Änderungsplan-Text (§4 Punkt 11), ist aber implizit enthalten — sollte explizit erwähnt werden.
- **[Bestätigung]** WM-Mutation in `_run_background_init()` korrekt: `project.working_memory = wm` wird an Zeile 274 des Orchestrators (nach dem return_to_mode-Block) persistiert.

### Prompts & LLM-Verhalten
- **[Bestätigung]** Erstaktivierungs-Sektion in `structuring.md` (Zeilen 42–67, 26 Zeilen) ist vorhanden und korrekt als zu entfernend identifiziert.
- **[Bestätigung]** Erstaktivierungs-Sektion in `specification.md` (Zeilen 42–44, 3 Zeilen) vorhanden.
- **[Bestätigung]** `_build_first_turn_directive()` in structuring.py:75 und specification.py:113 gibt `""` zurück wenn Artefakt nicht leer — Python-Seite braucht keine Änderung.
- **[Verbesserung V-6]** `init_hinweise` nicht in Dialog-Prompts verdrahtet. `structuring.py` und `specification.py` fehlen im Änderungsplan. Ohne Injektion kann AC #10 nicht erfüllt werden.
- **[Hinweis]** Init-Modi (init_structuring.py, init_specification.py) brauchen dieselben Platzhalter wie Dialog-Modi, aber ohne Dialog-spezifischen Kontext. Empfehlung für init_structuring: `{context_summary}` + `{exploration_content}` + `{slot_status}`; für init_specification: `{context_summary}` + `{structure_content}` + `{emma_catalog}`.

### Tests & Regression
- **[Bestätigung]** Tests 813/947 brechen NICHT — `if init_mode is None: return` ist graceful fallback. Custom-Orchestrators in diesen Tests ohne `init_structuring` führen zu Warning-Log und direktem Modus-Wechsel.
- **[Bestätigung]** Alle `ModeOutput()`-Instantiierungen in Tests bleiben grün (optionales `init_status`-Feld).
- **[Bestätigung]** Alle `WorkingMemory()`-Instantiierungen bleiben grün (optionales `init_hinweise`-Feld).
- **[Hinweis]** `_make_default_modes()` (test_orchestrator.py:51–58) hat pre-existing Mode-Key-Inkonsistenz: "strukturierung" statt "structuring". CR-006 sollte dies beim Hinzufügen der Init-Modi korrigieren.
- **[Bestätigung]** `test_init_validator.py` existiert nicht — muss neu erstellt werden (AC #12).
- **[Bestätigung]** `test_structuring_mode.py` und `test_specification_mode.py` sind vorhanden — mocked LLM, keine Orchestrator-Initialisierung, kein Breaking Risk.

### SDD, ADRs & Architektur-Konformität
- **[Bestätigung]** ADR-008 begründet Inline-Multi-Call sauber: 40s < Browser-Timeout (60–120s), MAX_INIT_TURNS konfigurierbar.
- **[Bestätigung]** ADR-008 verstößt nicht gegen ADR-001 bis ADR-007 — komplementäre Ebene.
- **[Bestätigung]** Separation of Concerns bleibt erhalten: Orchestrator ruft Init-Modi auf (kein direkter LLM-Zugriff), Executor schreibt Artefakte.
- **[Bestätigung]** CR-004 ist committed (788411a auf main) — structuring.md-Änderung ist sicher.
- **[Hinweis]** `nutzeraeusserung=""` in Init-Modi widerspricht dem Designintent von SDD §6.5.2 (Freitext für Chatbereich), ist aber nicht explizit verboten. UX-Impact ist akzeptabel da Init transparent für Nutzer ist. ADR-008 dokumentiert dies implizit.
- **[Bestätigung]** Phasenkette (Exploration → Strukturierung → Spezifikation → Validierung) bleibt unverändert — AC #13 SDD-Update erfasst alle notwendigen Abschnitte.

### Abhängigkeiten & Konflikte
- **[Bestätigung]** CR-002 (Implementiert): `regeln`, `schleifenkoerper`, `abbruchbedingung`, `konvergenz` konsistent mit Validator R-1 bis R-4.
- **[Bestätigung]** CR-003 (Verifiziert): 7 Slots inkl. `variablen_und_daten` korrekt referenziert.
- **[Bestätigung]** CR-004 (Implementiert, committed 788411a): CR-006 darf structuring.md weiter modifizieren.
- **[Hinweis]** `git status` zeigt pre-existing uncommitted changes an `structuring.md`. Implementierer muss prüfen was dort steht.
- **[Bestätigung]** Keine aktiven CRs (Freigegeben / In Umsetzung) die mit CR-006 kollidieren.

## Conditions für APPROVE WITH CONDITIONS

| ID | Condition | Umsetzbar ohne Rückfrage? | Priorität |
|---|---|---|---|
| C-1 | `_run_correction_turns()` und `_run_structural_validator()` in §3.5 mit Signatur und Pseudocode spezifizieren | Ja — Verhalten aus §3.1 und `_MAX_CORRECTION_TURNS` ableitbar | Hoch |
| C-2 | `structuring.py` und `specification.py` als Punkte 15/16 in §4 ergänzen; `{init_hinweise}`-Platzhalter in `structuring.md` und `specification.md` beschreiben | Ja — kein Architektur-Entscheid nötig | Hoch |
