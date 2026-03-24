# CR-008: Phasenende-Validator — Automatische Vollständigkeitsprüfung vor Phasenabschluss

| Feld | Wert |
|---|---|
| **ID** | CR-008 |
| **Titel** | Phasenende-Validator — Automatische Vollständigkeitsprüfung vor Phasenabschluss |
| **Status** | Entwurf |
| **Erstellt** | 2026-03-24 |
| **Priorität** | Hoch |
| **Auslöser** | Beobachtung: Im Dialog besprochene Informationen werden manchmal nicht vollständig in das Artefakt übernommen. LLM "vergisst" Details aus früheren Turns, insbesondere bei langen Dialog-Sequenzen. Wenn eine Phase abschließt und das Artefakt lückenhafte Informationen an die nächste Phase weitergibt, propagiert sich der Fehler durch die gesamte Kette. |
| **Abhängigkeiten** | Setzt voraus: CR-006 (Background-Init, Verifiziert). Empfohlen nach: CR-007 (Init-Progress-Feedback) |

---

## 1. Problemstellung

### Kernproblem

Das LLM-basierte Artefakt-Update via RFC 6902 Patches ist nicht vollständig zuverlässig: Informationen, die der Nutzer im Dialog genannt hat, werden gelegentlich nicht als Patches in das Artefakt geschrieben. Das betrifft vor allem:
- Details aus frühen Turns, die nicht mehr in der Dialog-History (`DIALOG_HISTORY_N=3`) liegen
- Korrekturen, die der Nutzer zu bestehenden Einträgen gemacht hat
- Implizite Informationen (z.B. Variable wird im Kontext erwähnt, aber nicht explizit als Patch erzeugt)

### Auswirkungen

- **Exploration → Structuring**: Variable oder Ausnahme wird im Explorer besprochen, fehlt aber im Artefakt → Structurer kann sie nicht berücksichtigen → Background-Init-Coverage-Validator meldet sie als fehlend
- **Structuring → Specification**: Schritt-Detail (z.B. Entscheidungsregel) wird besprochen aber nicht als Patch geschrieben → Specifier-Init erzeugt unvollständigen Algorithmus
- Allgemein: Qualität der Artefaktkette sinkt ohne merklichen Fehler — der Nutzer bemerkt das erst in der Validierungsphase oder gar nicht

## 2. Ziel der Änderung

Vor jedem Phasenabschluss (`phase_complete`-Flag) wird automatisch ein LLM-basierter Validator aufgerufen, der den gesamten Dialogverlauf der aktuellen Phase mit dem Artefakt-Zustand abgleicht. Fehlende Informationen werden nachgetragen, bevor die Phase wirklich abschließt und das Artefakt an die nächste Phase übergeben wird.

## 3. Lösung

### 3.1 Neuer Modus: `PhaseEndValidatorMode`

Ein LLM-basierter Modus, der:
1. Den **vollständigen Dialogverlauf der aktuellen Phase** erhält (nicht nur die letzten N Turns)
2. Den **aktuellen Artefakt-Zustand** als Read-Only sieht
3. **Fehlende Informationen identifiziert** und als RFC 6902 Patches nachträgt
4. **Keine Nutzernachricht generiert** (`nutzeraeusserung=""`) — läuft verdeckt

### 3.2 Prompt-Design

Der Prompt erhält:
- **Vollständiger Dialogverlauf** (alle User- und Assistant-Turns der aktuellen Phase)
- **Aktuelles Artefakt** (JSON)
- **Auftrag**: "Vergleiche den Dialog mit dem Artefakt. Identifiziere konkrete Informationen, die im Dialog besprochen wurden aber im Artefakt fehlen oder unvollständig sind. Erzeuge ausschließlich Patches für tatsächlich fehlende Informationen — keine Umformulierungen, keine Ergänzungen."

### 3.3 Eingriffspunkt im Orchestrator

Der Phasenende-Validator wird im Orchestrator **zwischen `phase_complete`-Flag-Erkennung und Moderator-Aktivierung** eingeschoben:

```
Modus sagt: phase_complete
    ↓
[NEU] PhaseEndValidator aufrufen (sequenziell, verdeckt)
    ├── Dialog-History laden (vollständig für aktuelle Phase)
    ├── Artefakt lesen
    ├── LLM: "Was fehlt?"
    ├── Patches anwenden (falls vorhanden)
    └── Weiter zum Moderator
```

Alternativ: Der Validator wird **innerhalb von Schritt 10** aufgerufen, bevor der Moderator gesetzt wird. Das ist eine rein interne Operation ohne UI-Impact.

### 3.4 Dialog-History-Zugriff

Aktuell wird die Dialog-History via `DIALOG_HISTORY_N=3` beschränkt. Der Phasenende-Validator braucht die **gesamte Phase-History**. Dafür wird `ProjectRepository.load_dialog_history()` um einen optionalen Parameter `since_turn` erweitert, der alle Turns seit einem bestimmten Turn-Zähler lädt. `WorkingMemory` muss den Turn-Zähler des letzten Phasenwechsels speichern.

### 3.5 Guardrails

- **Nur Ergänzungen, keine Überschreibungen**: Der Validator darf bestehende Artefakt-Einträge nicht modifizieren, nur leere oder fehlende Felder befüllen. Das wird über das Prompt-Design gesteuert und kann optional deterministisch geprüft werden (keine `replace`-Ops auf nicht-leere Felder).
- **Token-Budget**: Die vollständige Phase-History kann groß sein (20+ Turns). Wenn das Token-Budget überschritten wird, werden die ältesten Turns gekürzt (Summary statt Volltext).
- **Kein Endlos-Loop**: Der Validator läuft genau 1 Mal. Er ist kein iterativer Korrekturprozess.

### 3.6 SDD-Konsistenz

Kein SDD-Widerspruch. Der Validator ist eine Erweiterung des Orchestrator-Zyklus (SDD 6.3 Schritt 10) und respektiert das Prinzip "LLM als Operator" — er schreibt nur via RFC 6902 Patches.

### 3.7 Abwärtskompatibilität

- Neuer Modus ist optional registriert — wenn nicht vorhanden, wird der Validator übersprungen
- Neues Feld `phase_start_turn` in `WorkingMemory` mit Default `0` — alte WM-Daten deserialisieren fehlerfrei
- Kein Breaking Change an bestehenden Artefakt-Modellen

---

### 3a. Abhängigkeiten & Konflikte

| Typ | CR | Beschreibung |
|---|---|---|
| Setzt voraus | CR-006 | Init-Validator-Pattern als Vorlage |
| Empfohlen nach | CR-007 | Progress-Feedback kann auch für Phasenende-Validator genutzt werden |
| Konflikt | — | Keine bekannten Konflikte |

---

## 4. Änderungsplan

### Phase 1: Datenmodell

1. **`core/working_memory.py`**: `phase_start_turn: int = 0` hinzufügen — wird bei jedem Phasenwechsel auf den aktuellen `letzter_dialogturn` gesetzt.
2. **`core/phase_transition.py`**: In `advance_phase()` den `phase_start_turn` aktualisieren.

### Phase 2: Dialog-History-Zugriff

3. **`persistence/project_repository.py`**: `load_dialog_history()` um optionalen Parameter `since_turn: int | None = None` erweitern — lädt alle Turns >= since_turn.

### Phase 3: Modus & Prompt

4. **`modes/phase_end_validator.py`** (neu): `PhaseEndValidatorMode(BaseMode)` — lädt Prompt, baut System-Prompt mit vollständiger Phase-History + Artefakt, gibt Patches zurück, `nutzeraeusserung=""`.
5. **`prompts/phase_end_validator.md`** (neu): Prompt gemäß §3.2 — Vergleichsauftrag mit strikten Regeln (nur Ergänzungen, keine Umformulierungen).

### Phase 4: Orchestrator-Integration

6. **`core/orchestrator.py`**: In Schritt 10, nach `phase_complete`-Flag-Erkennung und vor Moderator-Aktivierung: `_run_phase_end_validator()` aufrufen. Neue Methode analog zu `_run_background_init()`, aber mit nur 1 Turn.
7. **`core/orchestrator.py`**: `_run_phase_end_validator()` implementieren: Phase-History laden, Modus aufrufen, Patches anwenden, Artefakt aktualisieren.

### Phase 5: Registrierung

8. **`api/websocket.py`**: `phase_end_validator`-Modus registrieren.

### Phase 6: Tests

9. **`tests/test_phase_end_validator.py`** (neu): Tests für den neuen Modus (Mock-LLM, Patch-Anwendung, Guardrails).
10. **`tests/test_orchestrator.py`**: Test, dass Phasenende-Validator bei `phase_complete` aufgerufen wird. Test, dass ohne registrierten Modus kein Fehler auftritt.

---

## 5. Risiken und Mitigationen

| # | Risiko | Mitigation |
|---|---|---|
| R-1 | Token-Limit-Überschreitung bei langer Phase-History | History-Truncation: älteste Turns summarisieren wenn > Token-Budget |
| R-2 | Validator überschreibt korrekte Artefakt-Einträge | Prompt-Guardrail "nur add/replace auf leere Felder"; optional: deterministischer Check im Orchestrator |
| R-3 | Validator erzeugt ungültige Patches | Executor-Validation fängt ab; bei Fehler: Warnung loggen, Artefakt bleibt unverändert |
| R-4 | Verlängerte Wartezeit bei Phasenabschluss (~5s) | CR-007 nutzen für Feedback ("Qualitätsprüfung läuft...") |
| R-5 | Validator "erfindet" Informationen die nie im Dialog waren | Striktes Prompt-Design: "NUR Informationen aus dem Dialog, KEINE Erfindungen" |

---

## 6. Nicht im Scope

- Validierung während der Phase (nach jedem Turn) — zu teuer, nur am Phasenende
- Nutzer-Interaktion des Validators ("Mir fehlt X, stimmt das?") — der Validator arbeitet verdeckt
- Retroaktive Validierung bereits abgeschlossener Phasen (z.B. Exploration nach Structuring)
- Integration mit CR-006 Init-Validator (inhaltlich orthogonal: Init prüft Struktur-Qualität, dieser CR prüft Dialog-Artefakt-Konsistenz)

---

## 7. Abnahmekriterien

1. `PhaseEndValidatorMode` existiert und implementiert `BaseMode.call()`
2. Prompt lädt vollständige Phase-History (nicht nur letzte N Turns)
3. `WorkingMemory.phase_start_turn` wird bei Phasenwechsel aktualisiert
4. Orchestrator ruft Validator bei `phase_complete`-Flag auf (vor Moderator-Aktivierung)
5. Patches werden angewandt; Artefakt ist nach Validator-Lauf aktualisiert
6. Bestehende Tests bleiben grün
7. Neuer Test: Validator ergänzt fehlende Information aus Dialog
8. Neuer Test: Validator ändert keine bestehenden Artefakt-Einträge (Guardrail)
9. Ohne registrierten Modus kein Fehler (graceful skip)

---

## 8. Aufwandsschätzung

| Aspekt | Wert |
|---|---|
| **Komplexität** | M |
| **Betroffene Dateien** | ~8 (working_memory.py, phase_transition.py, project_repository.py, phase_end_validator.py, phase_end_validator.md, orchestrator.py, websocket.py, Tests) |
| **Breaking Change** | Nein |
