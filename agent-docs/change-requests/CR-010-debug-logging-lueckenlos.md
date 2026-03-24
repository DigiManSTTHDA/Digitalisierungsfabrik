# CR-010: Debug-Logging lückenlos machen

| Feld | Wert |
|---|---|
| **ID** | CR-010 |
| **Titel** | Debug-Logging lückenlos machen |
| **Status** | Verifiziert |
| **Erstellt** | 2026-03-24 |
| **Priorität** | Kritisch |
| **Auslöser** | Testlauf `test_neu` (41 Turns, 19 Defects) — Root-Cause-Analyse unmöglich wegen fehlender Daten |
| **Abhängigkeiten** | Setzt voraus: CR-006 (Verifiziert), CR-007 (Verifiziert), CR-009 (Verifiziert) — alle bereits im Code |

---

## 1. Problemstellung

### Kernproblem

Das Debug-Logging-System (`LLM_DEBUG_LOG`) soll pro Turn die vollständige LLM-Kommunikation aufzeichnen. Es ist deaktiviert und hat selbst wenn aktiviert 7 Datenlücken, durch die kritische Informationen verloren gehen. Eine Ursachenanalyse für Defects wie in `test_neu` ist dadurch unmöglich.

### Konkrete Defizite

1. **`LLM_DEBUG_LOG` ist deaktiviert**: Fehlt in `.env`, Default ist `false`. Kein Testlauf erzeugt Debug-Daten.

2. **Rohe LLM-Antwort nicht erfasst**: `debug_request` in `llm/openai_client.py:134` und `llm/anthropic_client.py:103` enthält nur Request-Daten (system_prompt, messages, tool_choice) — der `tool_input` (die tatsächliche LLM-Antwort) fehlt.

   ```python
   # IST (openai_client.py:134-139)
   debug_request = {
       "system_prompt": system,
       "messages": messages,
       "tool_choice": kwargs.get("tool_choice"),
       "model": self._settings.llm_model,
   }
   # tool_input und nutzeraeusserung fehlen
   ```

3. **Fehlerhafter Ternary im Orchestrator**: `orchestrator.py:336-342` übergibt bei leeren Patches `mode_output.debug_request` (= Request-Daten) als `response_tool_input`. Das ist keine Response — es sind die Request-Daten.

   ```python
   # IST (orchestrator.py:336-342)
   response_tool_input=mode_output.debug_request  # ← REQUEST, nicht Response!
   if not mode_output.patches
   else {
       "nutzeraeusserung": mode_output.nutzeraeusserung,  # ← NACH Summarizer
       "patches": mode_output.patches,
       "phasenstatus": wm.phasenstatus.value,
   },
   ```

4. **Summarizer überschreibt LLM-Text unsichtbar**: `structuring.py:244-247` ersetzt `nutzeraeusserung` durch `summarize_patches()`. Die originale LLM-Antwort geht verloren — im Debug-Log landet nur der Summarizer-Output.

   ```python
   # IST (structuring.py:244-247)
   if patches:
       nutzeraeusserung = summarize_patches(patches, context.structure_artifact)
   # Original-Text ist unwiederbringlich weg
   ```

5. **Background-Init-Turns unsichtbar**: `_run_background_init()` (orchestrator.py:380-472) ruft bis zu 3 LLM-Calls auf (Init, Coverage-Validator, Korrektur). Keiner davon wird via `write_turn_debug()` geloggt. Die Init-Qualität (CR-009) ist komplett unsichtbar.

6. **Kein Artefakt-Delta**: `turn_debug_log.py` erfasst keinen Artefakt-Zustand. Die Parameter `patches_applied` und `patch_result` werden im Orchestrator-Aufruf nie befüllt (immer `None`).

7. **Keine Flags im Debug-Log**: Die vom Modus gesetzten Flags (phase_complete, advance_phase, etc.) werden nicht geloggt.

### Auswirkungen

Ohne lückenloses Debug-Logging sind wir bei jedem Testlauf blind. Wir können nicht unterscheiden ob ein Defect durch den Prompt, das LLM, den Summarizer, den Executor oder den Validator verursacht wird. Die Root-Cause-Analyse für `test_neu` ist ohne diese Daten Spekulation.

---

## 2. Ziel der Änderung

- Pro Dialog-Turn eine JSON-Datei mit vollständigem Audit-Trail: LLM-Input → LLM-Output (roh) → Nachbearbeitung → Artefakt-Delta → Chat-Output
- Pro Background-Init-Call eine separate JSON-Datei mit denselben Daten
- Original-LLM-Text immer erhalten, auch wenn der Summarizer ihn ersetzt
- Artefakt-Zustand vor und nach Patch-Anwendung erfasst
- `LLM_DEBUG_LOG=true` als Standard für Entwicklung

---

## 3. Lösung

### 3.1 LLM-Clients: Response-Daten in `debug_request` aufnehmen

**Dateien**: `backend/llm/openai_client.py`, `backend/llm/anthropic_client.py`

`debug_request` um die rohe LLM-Antwort erweitern:

```python
# SOLL (beide Clients, nach Parsing von tool_input/nutzeraeusserung)
debug_request = None
if self._settings.llm_debug_log:
    debug_request = {
        "system_prompt": system,
        "messages": messages,
        "tool_choice": kwargs.get("tool_choice"),
        "model": self._settings.llm_model,
        "raw_tool_input": tool_input,           # NEU
        "raw_nutzeraeusserung": nutzeraeusserung,  # NEU
    }
```

Keine Modell-Änderung an `LLMResponse` nötig — `debug_request` ist bereits `dict | None`.

### 3.2 ModeOutput: `summarizer_active`-Feld

**Datei**: `backend/modes/base.py`

```python
class ModeOutput(BaseModel):
    # ... bestehende Felder ...
    summarizer_active: bool = False  # NEU: True wenn nutzeraeusserung durch Summarizer ersetzt
```

Default `False` — kein Breaking Change, bestehende Instanziierungen bleiben gültig.

### 3.3 Structuring-Modus: Summarizer-Flag setzen

**Datei**: `backend/modes/structuring.py`

```python
# SOLL (structuring.py, in call(), ca. Zeile 244)
summarizer_used = False
if patches:
    nutzeraeusserung = summarize_patches(patches, context.structure_artifact)
    summarizer_used = True
else:
    nutzeraeusserung = response.nutzeraeusserung

return ModeOutput(
    # ... bestehende Felder ...
    summarizer_active=summarizer_used,  # NEU
)
```

### 3.4 turn_debug_log: Erweiterte Parameter

**Datei**: `backend/core/turn_debug_log.py`

Neue Parameter für `write_turn_debug()`:

```python
def write_turn_debug(
    *,
    # Bestehende Parameter bleiben
    base_dir: str,
    project_id: str,
    turn_number: int,
    mode: str,
    system_prompt: str,
    messages: list[dict],
    tool_choice: dict | None,
    response_nutzeraeusserung: str,
    response_tool_input: dict | None,
    token_usage: dict | None = None,
    cumulative_tokens: dict | None = None,
    # NEU: patches_applied und patch_result werden tatsächlich befüllt
    patches_applied: list[dict] | None = None,
    patch_result: str | None = None,
    # NEU
    raw_llm_nutzeraeusserung: str = "",
    raw_llm_tool_input: dict | None = None,
    final_nutzeraeusserung: str = "",
    summarizer_active: bool = False,
    artifact_before: dict | None = None,
    artifact_after: dict | None = None,
    flags: list[str] | None = None,
) -> None:
```

Payload-Erweiterung:

```python
payload = {
    # ... bestehende Felder (timestamp, project_id, turn, mode, request, token_usage, cumulative_tokens) ...
    "response": {
        "nutzeraeusserung": response_nutzeraeusserung,  # bestehend (Kompatibilität)
        "patches": tool_input.get("patches", []),       # bestehend
        "phasenstatus": tool_input.get("phasenstatus", ""),  # bestehend
        "raw_tool_input": tool_input,                   # bestehend
    },
    "llm_raw": {                                        # NEU
        "raw_nutzeraeusserung": raw_llm_nutzeraeusserung,
        "raw_tool_input": raw_llm_tool_input,
        "final_nutzeraeusserung": final_nutzeraeusserung,
        "summarizer_active": summarizer_active,
    },
    "execution": {                                      # erweitert (nicht mehr immer None)
        "patches_applied": patches_applied,
        "patch_result": patch_result,
    },
    "artifacts": {                                      # NEU
        "before": artifact_before,
        "after": artifact_after,
    },
    "flags": flags,                                     # NEU
}
```

### 3.5 Orchestrator: Korrekte Daten übergeben

**Datei**: `backend/core/orchestrator.py`

Der bestehende `write_turn_debug`-Aufruf (Zeile 326-349) wird ersetzt. Dafür sind Änderungen an zwei Stellen in `process_turn()` nötig:

**a) Artefakt-Snapshot VOR Patch-Anwendung** (vor Schritt 7, ca. Zeile 191):

```python
# Artefakt-Snapshot für Debug-Log
artifact_before_snapshot = None
if self._settings and self._settings.llm_debug_log and mode_output.patches:
    artifact_type_for_log = infer_artifact_type(mode_output.patches)
    if artifact_type_for_log:
        artifact_before_snapshot = get_artifact(project, artifact_type_for_log).model_dump(mode="json")
```

**b) Artefakt-Snapshot NACH Patch-Anwendung** (nach Schritt 7, ca. Zeile 240):

```python
artifact_after_snapshot = None
if self._settings and self._settings.llm_debug_log and artifact_type is not None:
    artifact_after_snapshot = get_artifact(project, artifact_type).model_dump(mode="json")
```

**c) write_turn_debug-Aufruf ersetzen** (Zeile 326-349):

```python
if self._settings and self._settings.llm_debug_log and mode_output.debug_request:
    write_turn_debug(
        base_dir=self._settings.database_path.rsplit("/", 1)[0] or "./data",
        project_id=project_id,
        turn_number=wm.letzter_dialogturn,
        mode=mode_key,
        system_prompt=mode_output.debug_request.get("system_prompt", ""),
        messages=mode_output.debug_request.get("messages", []),
        tool_choice=mode_output.debug_request.get("tool_choice"),
        response_nutzeraeusserung=mode_output.nutzeraeusserung,
        response_tool_input=mode_output.debug_request.get("raw_tool_input"),
        raw_llm_nutzeraeusserung=mode_output.debug_request.get("raw_nutzeraeusserung", ""),
        raw_llm_tool_input=mode_output.debug_request.get("raw_tool_input"),
        final_nutzeraeusserung=mode_output.nutzeraeusserung,
        summarizer_active=mode_output.summarizer_active,
        patches_applied=mode_output.patches if mode_output.patches else None,
        patch_result="success" if mode_output.patches else None,
        artifact_before=artifact_before_snapshot,
        artifact_after=artifact_after_snapshot,
        flags=flag_strings,
        token_usage=turn_usage,
        cumulative_tokens={
            "prompt_tokens": wm.cumulative_prompt_tokens,
            "completion_tokens": wm.cumulative_completion_tokens,
            "total_tokens": wm.cumulative_total_tokens,
        },
    )
```

### 3.6 Orchestrator: Background-Init-Turns loggen

**Datei**: `backend/core/orchestrator.py`, Methode `_run_background_init()`

An drei Stellen in `_run_background_init()` einen `write_turn_debug`-Aufruf einfügen. Der Turn-Nummer-Parameter wird als String codiert, um Kollisionen mit Dialog-Turns zu vermeiden:

**a) Nach Phase 1 — Init-Call (nach Zeile 406):**

```python
# Debug-Log für Init-Call
if self._settings and self._settings.llm_debug_log and output.debug_request:
    init_artifact_before = get_artifact(project, source_type).model_dump(mode="json")
    # ... Patches anwenden ...
    init_artifact_after = get_artifact(project, source_type).model_dump(mode="json")
    write_turn_debug(
        base_dir=self._settings.database_path.rsplit("/", 1)[0] or "./data",
        project_id=project.projekt_id,
        turn_number=wm.letzter_dialogturn,  # selbe Turn-Nr wie der auslösende Dialog-Turn
        mode=f"init_{target_mode}",          # z.B. "init_structuring"
        system_prompt=output.debug_request.get("system_prompt", ""),
        messages=output.debug_request.get("messages", []),
        tool_choice=output.debug_request.get("tool_choice"),
        response_nutzeraeusserung=output.nutzeraeusserung,
        response_tool_input=output.debug_request.get("raw_tool_input"),
        raw_llm_nutzeraeusserung=output.debug_request.get("raw_nutzeraeusserung", ""),
        raw_llm_tool_input=output.debug_request.get("raw_tool_input"),
        final_nutzeraeusserung=output.nutzeraeusserung,
        patches_applied=output.patches if output.patches else None,
        artifact_before=init_artifact_before,
        artifact_after=init_artifact_after,
        token_usage=output.usage,
    )
```

Dateiname wird: `turn_019_init_structuring.json` (durch den `mode`-Parameter in `turn_debug_log.py`).

**b) Nach Phase 3 — Coverage-Validator (nach Zeile 505):**

Analog mit `mode="init_coverage_validator"`.

**c) Nach Phase 4 — Korrektur-Call (nach Zeile 443):**

Analog mit `mode="init_{target_mode}_correction"`.

**Hinweis**: Die Artefakt-Snapshots müssen VOR und NACH der jeweiligen Patch-Anwendung genommen werden. Das erfordert eine leichte Umstrukturierung: Snapshot nehmen → Patches anwenden → Snapshot nehmen → Debug-Log schreiben.

### 3.7 `.env`: Debug-Log aktivieren

**Datei**: `backend/.env`

Zeile hinzufügen:
```
LLM_DEBUG_LOG=true
```

### Abwärtskompatibilität

- Alle neuen Parameter in `write_turn_debug()` haben Defaults — bestehende Aufrufe (falls vorhanden) brechen nicht.
- `ModeOutput.summarizer_active` hat Default `False` — bestehende Instanziierungen in allen Modi bleiben gültig.
- `debug_request`-Dict wird um zwei Schlüssel erweitert — `dict | None` Typ bleibt.
- Bestehende Debug-Log-JSON-Dateien (falls vorhanden) werden nicht beeinflusst — neue Dateien haben zusätzliche Felder.

### SDD-Konsistenz

Die Änderung erweitert die Beobachtbarkeit (NFR 8.1.3 — Beobachtbarkeit) und schließt eine bestehende Implementierungslücke zwischen NFR 8.1.3-Anforderung ("Vollständiger Kontext jedes LLM-Aufrufs wird für Analyse gespeichert") und dem bisherigen Code-Status. Keine neue Abweichung von der SDD.

### ADR-010: Audit-Trail-Logging mit Summarizer-Transparenz und Artefakt-Snapshots

**Kontext**: NFR 8.1.3 fordert vollständiges LLM-Input/Output-Logging. Der Summarizer in `structuring.py` ersetzt die LLM-Antwort unsichtbar. Background-Init-Turns (bis zu 3 LLM-Calls) waren komplett ungeloggt.

**Entscheidung**:
1. **Dual-Path-Logging**: Jeder Debug-Log-Eintrag enthält sowohl den rohen LLM-Text (`llm_raw.raw_nutzeraeusserung`) als auch den finalen Text nach Summarizer (`llm_raw.final_nutzeraeusserung`). Das Flag `summarizer_active` zeigt an, ob der Summarizer aktiv war.
2. **Artefakt-Snapshots**: Bei Turns mit Patches werden `artifacts.before` und `artifacts.after` als vollständige Artefakt-Dumps gespeichert — nur das betroffene Artefakt (per `infer_artifact_type`), nicht alle drei.
3. **Init-Turn-Differenzierung**: Background-Init-Calls erhalten eigene Debug-Log-Dateien mit dem Namensschema `turn_NNN_init_<modus>.json` (z.B. `turn_019_init_structuring.json`, `turn_019_init_coverage_validator.json`, `turn_019_init_structuring_correction.json`). Die Turn-Nummer ist identisch mit dem auslösenden Dialog-Turn.

**Konsequenzen**:
- Storage-Overhead: ~5-10 KB pro Turn mit Artefakt-Snapshots. Nur bei `LLM_DEBUG_LOG=true` aktiv.
- `ModeOutput` erhält ein neues Feld `summarizer_active: bool = False` (Default, kein Breaking Change).
- `write_turn_debug()` erhält 7 neue optionale Parameter (alle mit Defaults).
- Referenziert und erweitert ADR-008/009 (Inline-Multi-Call / Single-Call-Init).

### ADR-Konsistenz

- **ADR-009** (CR-009, Single-Call-Init): Konform. Die Init-Turn-Logs spiegeln die Single-Call-Architektur (max. 3 Calls) wider.
- **ADR-008** (CR-006): Überholt durch ADR-009. Nicht relevant.

---

## 3a. Abhängigkeiten & Konflikte

Keine Konflikte mit bestehenden CRs. Alle berührten Dateien werden nur erweitert, nicht umstrukturiert:

| CR | Status | Berührte Datei | Konflikt? |
|---|---|---|---|
| CR-006 | Verifiziert | `orchestrator.py` (_run_background_init) | Nein — wir fügen Logging hinzu, ändern keine Logik |
| CR-007 | Verifiziert | `orchestrator.py` (on_init_progress) | Nein — unabhängige Funktionalität |
| CR-009 | Verifiziert | `orchestrator.py` (_run_background_init) | Nein — wir loggen die existierende Single-Call-Architektur |

---

## 4. Änderungsplan

| # | Datei | Änderung |
|---|---|---|
| 1 | `backend/modes/base.py` | Feld `summarizer_active: bool = False` zu `ModeOutput` hinzufügen |
| 2 | `backend/modes/structuring.py` | Variable `summarizer_used` tracken, `summarizer_active=summarizer_used` in ModeOutput setzen |
| 3 | `backend/llm/openai_client.py` | `raw_tool_input` und `raw_nutzeraeusserung` in `debug_request`-Dict aufnehmen |
| 4 | `backend/llm/anthropic_client.py` | Dasselbe wie #3 |
| 5 | `backend/core/turn_debug_log.py` | Neue Parameter + erweitertes Payload (Abschnitte `llm_raw`, `artifacts`, `flags`) |
| 6 | `backend/core/orchestrator.py` | Artefakt-Snapshots vor/nach Patches; `write_turn_debug`-Aufruf korrigieren und erweitern |
| 7 | `backend/core/orchestrator.py` | `write_turn_debug`-Aufrufe in `_run_background_init()` an 3 Stellen einfügen |
| 8 | `backend/.env` | `LLM_DEBUG_LOG=true` hinzufügen |

---

## 5. Risiken und Mitigationen

### R-1: Debug-Log-Dateien werden groß

**Risiko**: Artefakt-Snapshots (vor/nach) können bei großen Prozessen mehrere KB pro Turn betragen. Bei 40+ Turns entstehen große Datenmengen.

**Mitigation**: Nur das betroffene Artefakt (per `artifact_type`) loggen, nicht alle drei. Snapshots nur wenn Patches vorhanden. Kein Risiko für Produktion — `LLM_DEBUG_LOG` ist opt-in.

### R-2: Performance-Einbußen durch Serialisierung

**Risiko**: `model_dump(mode="json")` auf Artefakten kostet CPU-Zeit.

**Mitigation**: Nur wenn `LLM_DEBUG_LOG=true`. In Produktion deaktiviert. Serialisierung ist << LLM-Call-Latenz.

### R-3: Bestehende Tests

**Risiko**: Tests die `ModeOutput` instanziieren könnten durch neues Feld brechen.

**Mitigation**: `summarizer_active` hat Default `False` — bestehende Instanziierungen bleiben gültig. Trotzdem: Testsuite durchlaufen lassen.

### R-4: Dateiname-Kollisionen bei Init-Turns

**Risiko**: Init-Turns teilen sich die `turn_number` mit dem auslösenden Dialog-Turn. Dateinamen könnten kollidieren.

**Mitigation**: Der `mode`-Parameter differenziert: `turn_019_moderator.json` vs. `turn_019_init_structuring.json`. Keine Kollision möglich.

---

## 6. Nicht im Scope

- **Patch-Summarizer entfernen oder ändern**: Das ist ein separates Problem (potentieller CR-011). CR-010 macht den Summarizer-Effekt sichtbar, ändert ihn aber nicht.
- **Validator erweitern** (R-1 Lücken, Self-References, Orphans): Separates Problem.
- **Dialog-History-Window-Size**: Kein Thema dieses CRs.
- **Auto-Greeting nach Phase-Advance**: Kein Thema dieses CRs.
- **Frontend-Änderungen**: Keine — Debug-Logs sind reine Backend-Dateien.
- **Log-Rotation oder Cleanup**: Manuelles Löschen von `data/debug_turns/` ist ausreichend.

---

## 7. Abnahmekriterien

1. `LLM_DEBUG_LOG=true` in `backend/.env` gesetzt.
2. Nach einem Dialog-Turn existiert eine JSON-Datei unter `backend/data/debug_turns/<project_id>/turn_NNN_<mode>.json`.
3. Die JSON-Datei enthält `request.system_prompt` (vollständiger System-Prompt, > 1000 Zeichen).
4. Die JSON-Datei enthält `request.messages` (die an das LLM gesendeten Dialog-Nachrichten).
5. Die JSON-Datei enthält `llm_raw.raw_nutzeraeusserung` (LLM-Text VOR Summarizer).
6. Die JSON-Datei enthält `llm_raw.raw_tool_input` (rohe LLM-Tool-Antwort mit patches und phasenstatus).
7. Die JSON-Datei enthält `llm_raw.final_nutzeraeusserung` (Text NACH Summarizer — was der User sieht).
8. Die JSON-Datei enthält `llm_raw.summarizer_active` (Boolean).
9. Bei Turns mit Patches: `artifacts.before` und `artifacts.after` sind nicht-null und zeigen unterschiedliche Zustände.
10. Bei Turns ohne Patches: `artifacts.before` und `artifacts.after` sind null.
11. Nach einem Phasenwechsel mit Background-Init: Separate JSON-Dateien für Init-Calls (z.B. `turn_019_init_structuring.json`, `turn_019_init_coverage_validator.json`).
12. Die JSON-Datei enthält `flags` (Liste der Flags aus dem ModeOutput).
13. Bestehende Tests sind grün (keine Regression durch `summarizer_active`-Feld).

---

## 8. Aufwandsschätzung

| Phase | Dateien | Komplexität |
|---|---|---|
| ModeOutput + Structuring (Summarizer-Flag) | `modes/base.py`, `modes/structuring.py` | S |
| LLM-Clients (debug_request erweitern) | `llm/openai_client.py`, `llm/anthropic_client.py` | S |
| turn_debug_log (neue Parameter + Payload) | `core/turn_debug_log.py` | S |
| Orchestrator (Dialog-Turn-Log korrigieren) | `core/orchestrator.py` | M |
| Orchestrator (Init-Turn-Logs) | `core/orchestrator.py` | M |
| .env | `.env` | S |

- **Komplexität**: S (8 Dateien, kein Breaking Change)
- **Betroffene Dateien**: 7 (+ .env)
- **Breaking Change**: Nein
