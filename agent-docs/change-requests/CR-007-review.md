# CCB Review: CR-007 — Init-Progress-Feedback

| Feld | Wert |
|---|---|
| **CR** | CR-007 |
| **Review-Datum** | 2026-03-24 |
| **Review-Nr.** | 1 |
| **Empfehlung** | APPROVE WITH CONDITIONS |

## Zusammenfassung

CR-007 führt ein Callback-basiertes Init-Progress-Feedback ein, um den Nutzer während der 10–40 Sekunden dauernden Background-Initialisierung über den Fortschritt zu informieren. Die Architektur (optionaler async Callback im Orchestrator, Closure-basierte WebSocket-Integration) ist sauber, SDD-konform und abwärtskompatibel. Allerdings wurde der CR vor CR-009 (Single-Call-Architektur) verfasst und muss in seiner Turn-Zähler-Semantik angepasst werden.

## Empfehlung

**APPROVE WITH CONDITIONS**

Der Architektur-Ansatz ist korrekt und elegant. Die Entkopplung via Callback-Pattern respektiert HLA 3.3 und ADR-008. Zwei Bedingungen müssen vor/während der Implementierung adressiert werden: (1) Abhängigkeit auf CR-009 dokumentieren und Turn-Semantik anpassen, (2) Event-Serialisierungstest ergänzen.

## Blocker (müssen behoben werden)

Keine Blocker identifiziert.

## Verbesserungsvorschläge (sollten eingearbeitet werden)

1. **V-1: Abhängigkeit auf CR-009 dokumentieren und Turn-Semantik anpassen.**
   CR-009 (Verifiziert) hat `_run_background_init()` auf eine Single-Call-Architektur umgestellt. Der Multi-Turn-Loop mit bis zu 8 Turns existiert nicht mehr — es gibt maximal 1 Init-Call + 1 optionalen Korrektur-Call. Die Felder `turn` und `max_turns` im `InitProgressEvent` sind in der aktuellen Form irreführend. **Empfehlung:** `max_turns` auf 2 setzen (oder das Feld entfernen und durch einen generischen `detail: str`-Feld ersetzen). Abschnitt 3a um "Setzt voraus: CR-009 (Verifiziert)" ergänzen.

2. **V-2: Event-Serialisierungstest ergänzen.**
   Die vorgeschlagenen Tests (AC #10–#12) decken Callback-Verhalten ab, aber nicht die Event-Serialisierung. Ein Round-Trip-Test für `InitProgressEvent` (analog zu bestehenden Tests in `test_events.py:87–93`) sollte ergänzt werden — insbesondere da das Event in die `WebSocketEvent`-Union aufgenommen wird.

3. **V-3: Callback-Positionen für 5-Phasen-Architektur präzisieren.**
   `_run_background_init()` hat 5 logische Phasen (Init-Call, Python-Validator, LLM-Coverage-Validator, Korrektur-Call, Hinweise speichern). Der CR beschreibt 4 Callback-Punkte. **Empfehlung:** Im Änderungsplan die exakten Zeilen/Positionen für jeden Callback-Aufruf benennen, insbesondere ob `status="validating"` vor dem Python-Validator oder dem LLM-Coverage-Validator emittiert wird.

## Hinweise

1. **H-1: Naming-Konvention `phase`/`status` vs. WorkingMemory-Felder.**
   Das InitProgressEvent nutzt `phase: str` und `status: str`, während WorkingMemory `aktive_phase: Projektphase` und `phasenstatus: Phasenstatus` verwendet. Dies ist bewusst und korrekt: Die Event-Felder beschreiben Init-Fortschritt (transient), nicht den Projektzustand (persistent). Kein Handlungsbedarf, aber bei der Implementierung auf konsistente Dokumentation achten.

2. **H-2: `_run_correction_turns()` Callback (Phase 2, #6 im Änderungsplan) ist optional.**
   Der CR markiert den Callback in `_run_correction_turns()` korrekt als "Optional". Nach CR-009 gibt es keine separaten Correction-Turns mehr — die Korrektur ist in `_run_background_init()` integriert (Zeile 388–400). Der optionale Callback in #6 des Änderungsplans ist daher obsolet und kann entfallen.

3. **H-3: Implementierungsreihenfolge.**
   Empfohlene Reihenfolge: CR-009 (bereits verifiziert) → CR-007 → CR-008. CR-007 muss auf dem aktuellen Code-Stand (nach CR-009) implementiert werden.

## Bestätigungen (CR-Behauptungen, die verifiziert wurden)

1. **B-1: HLA 3.3 Konformität bestätigt.** Der Orchestrator bleibt transport-agnostisch. Das Callback-Pattern ist ein textbook-korrektes Entkopplungsmuster — der Orchestrator ruft nur einen generischen `Callable` auf, ohne Wissen über WebSocket oder FastAPI. (SDD §3.3, HLA-Architektur Zeile 212–233)

2. **B-2: ADR-008 Konsistenz bestätigt.** Der Callback ändert nichts an der synchron-blockierenden Init-Architektur. Er fügt Observabilität hinzu, ohne den Kontrollfluss zu verändern. (CR-006, ADR-008 Zeile 416–421)

3. **B-3: Abwärtskompatibilität bestätigt.** `on_init_progress` ist optional mit Default `None`. Alle 10+ bestehenden Orchestrator-Instanziierungen (Tests, Scripts, WebSocket-Handler) funktionieren unverändert. Keine Breaking Changes. (orchestrator.py Zeile 92–102, test_orchestrator.py: 47 Tests)

4. **B-4: `InitProgressEvent` ist kompatibel mit `WebSocketEvent`-Union.** Das Discriminated-Union-Pattern über `event: Literal[...]` wird korrekt genutzt, analog zu allen bestehenden Event-Typen. (events.py Zeile 67–74)

5. **B-5: Frontend-Graceful-Degradation bestätigt.** `default: console.warn(...)` in `websocket.ts` ignoriert unbekannte Events. Backend-Deployment ist unabhängig vom Frontend möglich. (websocket.ts handleEvent-Switch)

6. **B-6: Risikomitigationen R-1 bis R-4 bestätigt.** Die try/except-Wrapper in `_emit_init_progress()` schützen den Init-Loop korrekt. WebSocket-Disconnect wird durch die Fehler-Kaskade (Callback-Exception → catch → log → weiter) abgefangen.

7. **B-7: Keine Prompt-Konflikte.** Init-Modi generieren keine Dialog-Nachrichten (nur Patches). Der Moderator wird während der Init-Phase nicht aktiviert. Kein Konkurrenz-Risiko mit den neuen Progress-Events.

8. **B-8: FR-F-01 Konformität bestätigt.** Die Erweiterung auf die Init-Phase ist eine legitime Konkretisierung der SDD-Anforderung "Fortschritt innerhalb der Phase ist jederzeit sichtbar". (SDD §516, FR-F-01)

## CR-Vollständigkeit

| Pflichtabschnitt | Vorhanden |
|---|---|
| Kopfzeile mit Priorität und Abhängigkeiten | ✅ (Hoch, CR-006) |
| Problemstellung (Kernproblem, Defizite, Auswirkungen) | ✅ |
| Ziel der Änderung | ✅ |
| Lösung mit Datenmodell und Beispielen | ✅ |
| Prompt-Änderungen | ✅ (keine nötig, korrekt dokumentiert) |
| Abwärtskompatibilität | ✅ |
| SDD-Konsistenz | ✅ |
| ADR | ✅ (keiner nötig, korrekt begründet) |
| Abhängigkeiten & Konflikte (3a) | ⚠️ CR-009 fehlt |
| Änderungsplan mit Phasen | ✅ |
| Risiken und Mitigationen | ✅ |
| Nicht im Scope | ✅ |
| Abnahmekriterien (prüfbar) | ✅ (12 Kriterien) |
| Aufwandsschätzung (S/M/L, Breaking Change) | ✅ (S, kein Breaking Change) |

## Lückenanalyse

1. **Fehlende Abhängigkeit:** CR-009 (Verifiziert) wird nicht als Abhängigkeit genannt, obwohl es `_run_background_init()` fundamental umgeschrieben hat. Die Turn-Zähler-Semantik im CR basiert auf dem Pre-CR-009-Zustand.

2. **Fehlender Test:** Event-Serialisierungstest für `InitProgressEvent` (Round-Trip via `model_dump`/`model_validate`). Die bestehenden Event-Tests (`test_events.py:87–93`) testen Union-Validierung — das neue Event muss dort aufgenommen werden.

3. **Unpräzise Callback-Positionen:** Der Änderungsplan (#5) beschreibt 4 Callback-Aufrufe, aber die aktuelle Methode hat 5 logische Phasen. Es fehlt die Zuordnung: Welcher `status`-Wert wird an welcher Code-Stelle emittiert?

## Detaillierte Findings pro Experte

### Datenmodell

- `InitProgressEvent` ist strukturell korrekt und kompatibel mit der bestehenden `WebSocketEvent`-Discriminated-Union (events.py:67–74).
- `InitProgressInfo` als TypedDict ist ein bewusstes Design: Es dient als internes Callback-Datenformat im Orchestrator, nicht als Pydantic-Modell. Das ist korrekt, da der Orchestrator keine Pydantic-Serialisierung braucht — nur die API-Schicht konvertiert via `InitProgressEvent(**info)`.
- `message`-Feld existiert auch in `ChatDoneEvent` und `ErrorEvent` — kein Konflikt dank Discriminated Union.

### Orchestrator & Kontrollfluss

- `_run_background_init()` ist `async` — Callback-Integration ist nativ möglich (orchestrator.py:353).
- Alle 10+ Orchestrator-Instanziierungen verwenden nur 3 Parameter — der optionale 4. Parameter ist backward-compatible.
- Die aktuelle Methode hat 5 Phasen: (1) Init-Call, (2) Python-Validator, (3) LLM-Coverage-Validator, (4) Korrektur-Call, (5) Hinweise speichern. Der CR beschreibt 4 Callback-Punkte — die Zuordnung zu den 5 Phasen muss bei der Implementierung geklärt werden.
- `process_turn()` ruft `_run_background_init()` korrekt in Schritt 10b auf (orchestrator.py:278–281). Keine Änderung an `process_turn()` nötig.

### Prompts & LLM-Verhalten

- Keine Prompt-Änderungen erforderlich. Init-Modi generieren keine Dialog-Nachrichten, nur Patches.
- Moderator wird während Init nicht aktiviert — keine Konkurrenz mit Progress-Events.
- Init-Prompts (`init_structuring.md`, `init_specification.md`, `init_coverage_validator.md`) bleiben unverändert.

### Tests & Regression

- **0 bestehende Tests für `_run_background_init()`** — das ist eine vorbestehende Lücke, kein CR-007-Problem.
- **47 bestehende Orchestrator-Tests** brechen nicht, da `on_init_progress` optional ist (Default `None`).
- **6 WebSocket-Tests** mocken `_build_orchestrator()` komplett — keine Brüche.
- **Test-Gap:** Event-Serialisierungstest fehlt in den vorgeschlagenen Tests (AC #10–#12). Empfehlung: Round-Trip-Test analog zu `test_events.py:87–93`.
- **Test-Helper** `_make_orchestrator()` (test_orchestrator.py:67–68) muss nicht angepasst werden.

### SDD, ADRs & Architektur-Konformität

- **FR-F-01 konform:** Erweiterung der Fortschrittsanzeige auf Init-Phase (SDD §516).
- **HLA 3.3 konform:** Orchestrator bleibt transport-agnostisch via Callback-Pattern.
- **ADR-008 konform:** Init bleibt synchron-blockierend, Callback ist reine Observabilität.
- **Kein SDD-Update nötig.** Kein eigener ADR nötig (Implementierungsmuster, keine Architekturentscheidung).
- **Robust gegenüber CR-009:** Callback-Pattern funktioniert auch mit Single-Call-Architektur.

### Abhängigkeiten & Konflikte

- **CR-006 (Verifiziert):** Abhängigkeit korrekt dokumentiert. `_run_background_init()` existiert.
- **CR-009 (Verifiziert):** NICHT als Abhängigkeit dokumentiert, obwohl es `_run_background_init()` auf Single-Call umgestellt hat. Multi-Turn-Loop mit `turn`/`max_turns` bis zu 8 existiert nicht mehr — maximal 2 LLM-Calls (1 Init + 1 optional Korrektur).
- **CR-008 (Entwurf):** Korrekt als "Ermöglicht" dokumentiert. Kein Konflikt.
- **Dateien-Overlap:** `orchestrator.py` und `api/websocket.py` werden auch von CR-009 geändert. Da CR-009 bereits verifiziert ist, muss CR-007 auf dem aktuellen Code-Stand implementiert werden — kein Merge-Konflikt, aber der Änderungsplan im CR bezieht sich teilweise auf Pre-CR-009-Code.
