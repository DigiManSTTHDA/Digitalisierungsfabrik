# CR-008: Phasenende-Validator — Automatische Vollständigkeitsprüfung vor Phasenabschluss

| Feld | Wert |
|---|---|
| **ID** | CR-008 |
| **Titel** | Phasenende-Validator — Automatische Vollständigkeitsprüfung vor Phasenabschluss |
| **Status** | Entwurf |
| **Erstellt** | 2026-03-24 |
| **Priorität** | Hoch |
| **Auslöser** | Beobachtung: Im Dialog besprochene Informationen werden manchmal nicht vollständig in das Artefakt übernommen. LLM "vergisst" Details aus früheren Turns (außerhalb `DIALOG_HISTORY_N=3`). Fehler propagiert sich durch die gesamte Phasenkette unbemerkt. |
| **Abhängigkeiten** | Setzt voraus: CR-006 (Background-Init, Verifiziert). Empfohlen nach: CR-007 (Init-Progress-Feedback, Entwurf) |

---

## 1. Problemstellung

### Kernproblem

Das LLM-basierte Artefakt-Update via RFC 6902 Patches ist nicht vollständig zuverlässig: Informationen, die der Nutzer im Dialog explizit genannt hat, werden gelegentlich nicht als Patches in das Artefakt geschrieben. Das betrifft vor allem:

- Details aus frühen Turns, die nicht mehr in der Dialog-History (`DIALOG_HISTORY_N=3`) liegen
- Korrekturen, die der Nutzer zu bestehenden Einträgen gemacht hat
- Implizite Informationen (z.B. Variable wird im Kontext erwähnt, aber nicht explizit als Patch erzeugt)

### Konkrete Defizite

**D-1: Dialog-Artefakt-Divergenz durch begrenzten Kontextfenster**

Aktuell lädt `context_assembler.py` nur die letzten N Turns via `load_dialog_history(last_n=...)`. Ein Beispiel:

```
Turn 3:  User: "Und der Antragsteller muss zwingend die IBAN angeben."
Turn 4:  User: "Außerdem gibt es eine Ausnahme für Bestandskunden..."
...
Turn 12: User: "Das war alles, ich denke wir können abschließen."
→ phase_complete
```

Turn 3 liegt nicht mehr im Kontextfenster. Der Explorer hat `iban_pflichtfeld` nie als Patch geschrieben — der Structurer sieht es nicht.

**D-2: Korrekturen werden überschrieben aber nicht nachverfolgt**

```
Turn 5:  Explorer schreibt Patch: /slots/variablen_und_daten/wert = "Name, Adresse"
Turn 7:  User: "Nein, auch IBAN und Geburtsdatum."
Turn 8:  Explorer schreibt Patch: /slots/variablen_und_daten/wert = "Name, Adresse, IBAN, Geburtsdatum"
Turn 9:  User: "Und für Firmenkunden noch die Handelsregisternummer."
→ kein Patch für Turn 9 erzeugt (LLM hat es nicht mehr im Fokus)
```

`Handelsregisternummer` fehlt im Artefakt — kein Fehler, kein Warning, keine Sichtbarkeit.

**D-3: Implizite Informationen ohne Patch**

```
Turn 6: User: "Der Schritt 'Prüfung' kann 3 Werktage dauern."
→ Explorer erwähnt es in der Nutzerantwort, aber kein Patch auf /slots/prozesszeiten/
```

### Auswirkungen

- **Exploration → Structuring**: Fehlende Variable/Ausnahme → Background-Init-Coverage-Validator meldet sie als kritisch → Korrektur-Turns brauchen mehr Iterationen oder schlagen fehl
- **Structuring → Specification**: Fehlende Entscheidungsregel → Specifier-Init erzeugt unvollständigen Algorithmus
- Qualitätsverlust ohne merklichen Fehler — der Nutzer bemerkt es erst in der Validierungsphase oder gar nicht
- CR-006's Coverage-Validator ist ein partieller Workaround, aber er prüft nur strukturelle Vollständigkeit — nicht Dialog-Artefakt-Konsistenz

---

## 2. Ziel der Änderung

- Vor jedem Phasenabschluss (`phase_complete`-Flag) wird ein LLM-basierter Validator aufgerufen, der den **gesamten** Dialogverlauf der aktuellen Phase mit dem Artefakt abgleicht
- Fehlende Informationen werden als RFC 6902 Patches nachgetragen — **bevor** der Moderator aktiviert wird
- Der Validator läuft verdeckt (keine Nutzernachricht), analog zu CR-006's Init-Modi
- Bestehende Artefakt-Einträge werden **nicht** überschrieben — nur leere oder fehlende Felder werden befüllt
- Kein Breaking Change an bestehenden Artefaktmodellen oder Tests

---

## 3. Lösung

### 3.1 Datenmodell: `phase_start_turn` in WorkingMemory

`WorkingMemory` wird um ein Feld erweitert, das den Turn-Zähler zu Beginn der aktuellen Phase speichert. Damit kann der Validator alle Turns der Phase laden — nicht nur die letzten N.

```python
# backend/core/working_memory.py — NEU
phase_start_turn: int = 0  # Turn-Zähler beim letzten Phasenwechsel (CR-008)
```

Default `0` → abwärtskompatibel: Alte `WorkingMemory`-Serialisierungen deserialisieren fehlerfrei. Im Worst Case lädt der Validator mehr History als nötig — kein Fehler.

Bei Phasenwechsel in `advance_phase()`:
```python
# backend/core/phase_transition.py — ERGÄNZUNG in advance_phase()
wm.phase_start_turn = wm.letzter_dialogturn  # CR-008: Phase-Grenze merken
```

### 3.2 Dialog-History-Zugriff: `since_turn` in `load_dialog_history()`

`ProjectRepository.load_dialog_history()` erhält einen optionalen Parameter `since_turn`:

```python
# VORHER
def load_dialog_history(self, projekt_id: str, last_n: int = 20) -> list[dict[str, str]]:

# NACHHER
def load_dialog_history(
    self,
    projekt_id: str,
    last_n: int = 20,
    since_turn: int | None = None,
) -> list[dict[str, str]]:
```

SQL-Logik: Wenn `since_turn` gesetzt ist, werden alle Turns mit `turn_id >= since_turn` geladen (kein `LIMIT`), chronologisch sortiert:

```sql
-- since_turn gesetzt:
SELECT role, inhalt, timestamp FROM dialog_history
WHERE projekt_id = ? AND turn_id >= ?
ORDER BY turn_id ASC, id ASC

-- since_turn=None: bisherige Logik (last_n) bleibt unverändert
```

Bestehende Aufrufer (Context Assembler, Tests) bleiben unverändert — `since_turn=None` ist Default.

### 3.3 Neuer Modus: `PhaseEndValidatorMode`

```python
# backend/modes/phase_end_validator.py (neu)
class PhaseEndValidatorMode(BaseMode):
    """Phasenende-Validator: Dialog-Artefakt-Abgleich vor Phasenabschluss (CR-008)."""

    async def call(self, context: ModeContext) -> ModeOutput:
        # System-Prompt: Vergleichsauftrag (Prompt aus prompts/phase_end_validator.md)
        # User-Message: vollständige Phase-History + aktuelles Artefakt (JSON)
        # Output: RFC 6902 Patches ODER leere Liste
        # nutzeraeusserung="" — kein sichtbarer Output
        ...
```

**Output-Kontrakt**: Der Modus gibt `ModeOutput` zurück mit:
- `patches`: Liste von RFC 6902 Patches (kann leer sein)
- `nutzeraeusserung: ""` — kein Nutzer-sichtbarer Text
- `init_status: None` — nicht relevant für diesen Modus

**Prompt-Design** (`prompts/phase_end_validator.md`):
```
Du erhältst:
1. Den vollständigen Dialogverlauf der aktuellen Phase (User- und Assistant-Turns)
2. Das aktuelle Artefakt (JSON)

Dein Auftrag: Identifiziere konkrete Informationen, die im Dialog vom Nutzer genannt
wurden, aber im Artefakt fehlen oder unvollständig sind.

REGELN:
- Erzeuge NUR Patches für tatsächlich fehlende oder leere Felder
- Keine replace-Operationen auf nicht-leere Felder
- Keine Umformulierungen bestehender Einträge
- Keine Erfindungen — NUR Informationen die explizit im Dialog stehen
- Wenn nichts fehlt: leere patches-Liste zurückgeben
```

### 3.4 Eingriffspunkt im Orchestrator

Der Validator wird in **Schritt 10**, innerhalb des `_MODERATOR_TRIGGER_FLAGS`-Blocks, **spezifisch für `Flag.phase_complete`** und **vor** dem Moduswechsel auf "moderator" eingeschoben:

**IST** (orchestrator.py, Zeile 246–255):
```python
active_flags = set(mode_output.flags)
if _MODERATOR_TRIGGER_FLAGS & active_flags and wm.aktiver_modus != "moderator":
    wm.vorheriger_modus = wm.aktiver_modus
    wm.aktiver_modus = "moderator"
    log.info("orchestrator.mode_switch", ...)
```

**SOLL** (neue Methode `_run_phase_end_validator()` wird zwischen Flag-Erkennung und Moduswechsel aufgerufen):
```python
active_flags = set(mode_output.flags)
if _MODERATOR_TRIGGER_FLAGS & active_flags and wm.aktiver_modus != "moderator":
    # CR-008: Phasenende-Validator bei phase_complete (vor Moderator-Aktivierung)
    if Flag.phase_complete in active_flags:
        log.info("orchestrator.phase_end_validator.start")
        await self._run_phase_end_validator(project, wm)
        log.info("orchestrator.phase_end_validator.complete")
    wm.vorheriger_modus = wm.aktiver_modus
    wm.aktiver_modus = "moderator"
    log.info("orchestrator.mode_switch", ...)
```

### 3.5 `_run_phase_end_validator()` Implementierung

```python
async def _run_phase_end_validator(
    self,
    project: "Project",
    wm: WorkingMemory,
) -> None:
    """Phasenende-Validator: Dialog-Artefakt-Abgleich vor Phasenabschluss (CR-008)."""
    validator_mode = self._modes.get("phase_end_validator")
    if validator_mode is None:
        logger.warning("orchestrator.phase_end_validator.no_mode")
        return  # graceful skip — kein Fehler

    # Vollständige Phase-History laden (since phase_start_turn)
    phase_history = self._repository.load_dialog_history(
        project.projekt_id,
        since_turn=wm.phase_start_turn,
    )

    # Kontext mit vollständiger Phase-History bauen
    context = build_context(
        project, {}, repository=self._repository, settings=self._settings
    )
    context = context.with_phase_history(phase_history)  # neues Feld im ModeContext

    output = await validator_mode.call(context)

    if output.patches:
        artifact_type = infer_artifact_type(output.patches)
        if artifact_type:
            artifact = get_artifact(project, artifact_type)
            result = self._executor.apply_patches(artifact_type, artifact, output.patches)
            if result.success and result.artifact is not None:
                set_artifact(project, artifact_type, result.artifact)
                logger.info(
                    "orchestrator.phase_end_validator.patches_applied",
                    count=len(output.patches),
                )
```

### 3.6 `ModeContext` um `phase_history` erweitern

Der `ModeContext` (in `core/context_assembler.py`) benötigt ein neues optionales Feld und eine Builder-Methode:

```python
# backend/core/context_assembler.py
@dataclass
class ModeContext:
    ...
    phase_history: list[dict[str, str]] | None = None  # CR-008: vollständige Phase-History

    def with_phase_history(self, history: list[dict[str, str]]) -> "ModeContext":
        """Gibt eine Kopie des Contexts mit vollständiger Phase-History zurück."""
        return replace(self, phase_history=history)
```

`PhaseEndValidatorMode` greift auf `context.phase_history` zu (statt auf `context.dialog_history`).

### 3.7 Beispiel: Patch-Output des Validators

Für eine Exploration-Phase wo `IBAN-Pflichtfeld` besprochen aber nie als Patch geschrieben wurde:

```json
[
  {
    "op": "replace",
    "path": "/slots/variablen_und_daten/wert",
    "value": "Name, Adresse, IBAN (Pflichtfeld), Geburtsdatum"
  }
]
```

Der Validator würde `replace` NUR auf ein leeres oder unvollständiges Feld anwenden. Guardrail im Prompt verhindert Überschreibung nicht-leerer korrekter Werte.

### 3.8 Abwärtskompatibilität

| Komponente | Änderung | Kompatibilität |
|---|---|---|
| `WorkingMemory` | Neues Feld `phase_start_turn: int = 0` | ✅ Default 0 — alte Daten deserialisieren fehlerfrei |
| `load_dialog_history()` | Neuer optionaler Parameter `since_turn=None` | ✅ Bestehende Aufrufer unverändert |
| `ModeContext` | Neues optionales Feld `phase_history=None` | ✅ Bestehende Modi ignorieren es |
| `advance_phase()` | Setzt `wm.phase_start_turn` | ✅ Additiv, kein Breaking Change |
| Modus-Registrierung | `phase_end_validator` optional | ✅ Graceful skip wenn nicht registriert |

### 3.9 SDD-Konsistenz

**Konsistent mit ADR-008 (CR-006):** ADR-008 definiert "Inline-Multi-Call im Orchestrator-Turn" als zulässiges Pattern für verdeckte LLM-Calls ohne Nutzer-Interaktion. Der Phasenende-Validator folgt exakt diesem Pattern (1 LLM-Call, `nutzeraeusserung=""`, Patches anwenden). Keine neue SDD-Abweichung erforderlich.

**Keine Verletzung bestehender ADRs:**
- **ADR-006** (CR-002, EmmaAktionstyp-Enum): nicht berührt
- **ADR-007** (CR-005, Validierungsbericht-Struktur): nicht berührt
- **ADR-008** (CR-006, Background-Init als Inline-Multi-Call): konform — dieses Muster wird erweitert

---

## 3a. Abhängigkeiten & Konflikte

| Typ | CR | Beschreibung |
|---|---|---|
| Setzt voraus | CR-006 (Verifiziert) | Init-Validator-Pattern als Vorlage; `BaseMode`-Pattern, Patch-Anwendungslogik |
| Empfohlen nach | CR-007 (Entwurf) | CR-007 fügt Progress-Feedback ein — Phasenende-Validator verlängert die Phase ebenfalls (~5s); kann selbes Feedback-Mechanism nutzen |
| Konflikt | — | Keine Konflikte mit bestehenden CRs |

**Berührungspunkte mit CR-007**: CR-007 betrifft die Background-Init-Phase (Schritt 10b, `return_to_mode`). CR-008 betrifft den Phasenabschluss (Schritt 10, `phase_complete`). Beide laufen sequenziell, aber in **verschiedenen** Orchestrator-Blöcken — kein struktureller Konflikt. CR-008 kann von CR-007's Feedback-Mechanismus (falls implementiert) profitieren, ist aber nicht davon abhängig.

---

## 4. Änderungsplan

| # | Datei | Änderung |
|---|---|---|
| 1 | `backend/core/working_memory.py` | Feld `phase_start_turn: int = 0` mit Kommentar `# CR-008` ergänzen (nach `init_hinweise`) |
| 2 | `backend/core/phase_transition.py` | In `advance_phase()`: `wm.phase_start_turn = wm.letzter_dialogturn` setzen — direkt vor `return True` (in beiden Zweigen: Normalfall und Terminal-Phase) |
| 3 | `backend/persistence/project_repository.py` | `load_dialog_history()`: Parameter `since_turn: int \| None = None` ergänzen; SQL-Abfrage erweitern (wenn `since_turn` gesetzt: `WHERE turn_id >= since_turn` ohne LIMIT, sonst bisherige Logik) |
| 4 | `backend/core/context_assembler.py` | `ModeContext`: Feld `phase_history: list[dict[str, str]] \| None = None` ergänzen; Methode `with_phase_history(history) -> ModeContext` hinzufügen |
| 5 | `backend/modes/phase_end_validator.py` (neu) | `PhaseEndValidatorMode(BaseMode)`: Prompt aus `prompts/phase_end_validator.md` laden; System-Prompt mit Phase-History + Artefakt bauen; Patches zurückgeben; `nutzeraeusserung=""` |
| 6 | `backend/prompts/phase_end_validator.md` (neu) | Prompt gemäß §3.3 — Vergleichsauftrag, strikte Regeln (nur add/replace auf leere Felder, keine Erfindungen) |
| 7 | `backend/core/orchestrator.py` | In Schritt 10: `if Flag.phase_complete in active_flags:` vor Moduswechsel: `await self._run_phase_end_validator(project, wm)` aufrufen |
| 8 | `backend/core/orchestrator.py` | `_run_phase_end_validator()` implementieren: Phase-History laden (seit `phase_start_turn`), Context mit `with_phase_history()`, Modus aufrufen, Patches anwenden |
| 9 | `backend/api/websocket.py` | `phase_end_validator`-Modus registrieren (analog zu `init_coverage_validator`) |
| 10 | `backend/tests/test_phase_end_validator.py` (neu) | Tests: Mode-Call mit Mock-LLM, Patch-Anwendung, Guardrail (keine replace auf nicht-leere Felder), graceful skip ohne Modus |
| 11 | `backend/tests/test_orchestrator.py` | 2 neue Tests: (a) Validator wird bei `phase_complete`-Flag aufgerufen; (b) ohne registrierten Modus kein Fehler |
| 12 | `backend/tests/test_project_repository.py` | Test für `load_dialog_history(since_turn=...)`: Korrekte Filterung, chronologische Reihenfolge |

**Reihenfolge**: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12

---

## 5. Risiken und Mitigationen

### R-1: Token-Limit-Überschreitung bei langer Phase-History

**Risiko**: Eine Phase mit 30+ Turns erzeugt einen sehr langen Context-String für den Validator. Dieser kann das Token-Budget des LLM überschreiten (typisch 200k, aber Prompt + Artefakt + History kann groß sein).

**Mitigation**: `_run_phase_end_validator()` implementiert History-Truncation: Wenn `len(phase_history) > MAX_PHASE_HISTORY_TURNS` (Default: 40), werden die ältesten Turns auf eine 1-Satz-Zusammenfassung gekürzt. Die jüngsten 20 Turns bleiben immer vollständig. `MAX_PHASE_HISTORY_TURNS = 40` als Klassenattribut im Orchestrator.

### R-2: Validator überschreibt korrekte Artefakt-Einträge

**Risiko**: Das LLM ignoriert den Prompt-Guardrail und erzeugt `replace`-Patches auf nicht-leere Felder.

**Mitigation**: Deterministischer Post-Processing-Check im Orchestrator: Vor Anwendung jedes Patches prüfen ob `op == "replace"` und das Zielfeld im aktuellen Artefakt nicht-leer ist. Solche Patches werden verworfen (Warning-Log). Diese Prüfung ergänzt den Prompt-Guardrail als zweite Sicherheitsebene.

### R-3: Validator erzeugt ungültige Patch-Pfade

**Risiko**: Patch-Pfad passt nicht zum Artefakt-Schema → `Executor.apply_patches()` schlägt fehl.

**Mitigation**: Bestehende Executor-Validierung fängt das ab. Bei Fehler: Warning loggen, Artefakt bleibt unverändert. Der Phasenabschluss läuft trotzdem weiter — der Validator ist nicht blockierend.

### R-4: Verlängerte Wartezeit bei Phasenabschluss

**Risiko**: Der LLM-Call des Validators kostet ~3–8 Sekunden zusätzlich. Das addiert sich zu CR-006's Background-Init-Wartezeit (wenn relevant).

**Mitigation**: Der Validator wird IMMER vor dem Moderator aufgerufen (nicht nur vor Background-Init). Die Wartezeit tritt bei jedem Phasenabschluss auf. CR-007's Feedback-Mechanismus kann genutzt werden um "Qualitätsprüfung läuft..." anzuzeigen, ist aber nicht Voraussetzung.

### R-5: Validator "erfindet" Informationen

**Risiko**: Das LLM ergänzt plausible aber nie genannte Informationen.

**Mitigation**: Striktes Prompt-Design: "NUR Informationen die der Nutzer explizit genannt hat. KEINE Ergänzungen auf Basis von Plausibilität. Im Zweifel: kein Patch." Monitoring via Debug-Log (vorhandener `llm_debug_log`-Mechanismus).

### R-6: `since_turn=0` bei Projekten ohne Phasenwechsel

**Risiko**: Für ein Projekt das nie `advance_phase()` aufgerufen hat, ist `phase_start_turn=0`. `load_dialog_history(since_turn=0)` lädt die gesamte History — potentiell sehr groß für ein langes Exploration-Dialog.

**Mitigation**: `since_turn=0` ist für Exploration der korrekte Wert (die gesamte Exploration-Phase). History-Truncation aus R-1 greift. Kein Fehler — höchstens größerer Context.

---

## 6. Nicht im Scope

- **Validierung nach jedem Turn** (intra-phase): zu teuer, semantisch falsch — der Dialog ist noch nicht abgeschlossen
- **Nutzer-Interaktion des Validators** ("Mir fehlt X, stimmt das?"): Validator arbeitet verdeckt, analog zu CR-006 Init-Modi
- **Retroaktive Validierung abgeschlossener Phasen**: Nur beim aktuellen Phasenabschluss
- **Integration mit CR-006 Init-Validator**: Inhaltlich orthogonal — Init-Validator prüft Struktur-/Referenz-Integrität; Phasenende-Validator prüft Dialog-Artefakt-Konsistenz
- **Validierung bei `escalate`- oder `blocked`-Flags**: Nur bei `phase_complete` sinnvoll
- **Iterativer Korrekturprozess**: Der Validator läuft genau 1 Mal — kein Loop, keine Korrektur-Turns

---

## 7. Abnahmekriterien

1. `PhaseEndValidatorMode` existiert in `modes/phase_end_validator.py` und implementiert `BaseMode.call()`
2. `WorkingMemory.phase_start_turn` existiert mit Default `0`; alte `WorkingMemory`-Serialisierungen deserialisieren ohne Fehler
3. `advance_phase()` setzt `wm.phase_start_turn = wm.letzter_dialogturn` bei jedem Phasenwechsel
4. `load_dialog_history(since_turn=5)` gibt nur Turns mit `turn_id >= 5` zurück, chronologisch sortiert
5. `ModeContext.with_phase_history()` existiert und gibt eine Kopie mit gesetztem `phase_history` zurück
6. Orchestrator ruft `_run_phase_end_validator()` bei `Flag.phase_complete` auf — **vor** dem Moduswechsel auf "moderator"
7. Bei `Flag.escalate` oder `Flag.blocked` wird `_run_phase_end_validator()` **nicht** aufgerufen
8. Patches des Validators werden auf das Artefakt angewandt; Artefakt ist nach Validator-Lauf aktualisiert
9. Deterministischer Guardrail: `replace`-Patches auf nicht-leere Felder werden verworfen (Warning-Log, kein Fehler)
10. Ohne registrierten `phase_end_validator`-Modus: kein Fehler, kein Abbruch (graceful skip mit Warning-Log)
11. Bestehende Tests (459/460 grün, 1 pre-existing Failure) bleiben unverändert
12. Neuer Test: Validator ergänzt fehlende Information aus Dialog-History
13. Neuer Test: Validator verwirft `replace`-Patches auf nicht-leere Felder (Guardrail)
14. Neuer Test: `load_dialog_history(since_turn=N)` filtert korrekt

---

## 8. Aufwandsschätzung

| Aspekt | Wert |
|---|---|
| **Komplexität** | M |
| **Breaking Change** | Nein |

| Phase | Betroffene Dateien | Komplexität |
|---|---|---|
| Datenmodell | `working_memory.py`, `phase_transition.py` | S |
| Repository | `project_repository.py` | S |
| Context | `context_assembler.py` | S |
| Modus & Prompt | `phase_end_validator.py` (neu), `phase_end_validator.md` (neu) | M |
| Orchestrator | `orchestrator.py` (2 Ergänzungen) | S |
| Registrierung | `api/websocket.py` | S |
| Tests | `test_phase_end_validator.py` (neu), `test_orchestrator.py`, `test_project_repository.py` | M |

**Betroffene Dateien gesamt**: 10 (7 bestehend, 3 neu)
