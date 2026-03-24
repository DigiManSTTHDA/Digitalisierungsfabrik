# CR-007: Init-Progress-Feedback — Nutzer-Rückmeldung während Background-Initialisierung

| Feld | Wert |
|---|---|
| **ID** | CR-007 |
| **Titel** | Init-Progress-Feedback — Nutzer-Rückmeldung während Background-Initialisierung |
| **Status** | Entwurf |
| **Erstellt** | 2026-03-24 |
| **Priorität** | Hoch |
| **Auslöser** | CR-006 implementiert die Background-Initialisierung synchron-blockierend (Schritt 10b). Der Nutzer sieht während der ~10–40 Sekunden Init-Phase weder eine Nachricht noch ein Feedback — die UI wirkt eingefroren. Das ist für den Prototyp inakzeptabel: der Nutzer vermutet einen Fehler und bricht ab. |
| **Abhängigkeiten** | Setzt voraus: CR-006 (Background-Init, Verifiziert) |

---

## 1. Problemstellung

### Kernproblem

Die Background-Initialisierung (CR-006) läuft synchron innerhalb von `process_turn()`. Da der WebSocket-Handler erst nach Abschluss des gesamten Turns Events an den Client sendet, erhält der Nutzer für 10–40 Sekunden keinerlei Rückmeldung. Die UI wirkt eingefroren.

### Konkrete Defizite

**D-1: Kein Start-Feedback**
Der Nutzer sieht nicht, dass eine Initialisierung läuft. Die letzte sichtbare Aktion ist die Moderator-Nachricht zum Phasenwechsel.

**D-2: Kein Abschluss-Feedback**
Nach Abschluss der Init wird der erste Dialog-Turn des Structurer/Specifier gesendet, aber ohne Kontext ("Warum hat das so lange gedauert?").

**D-3: Kein Fortschritts-Feedback bei langen Init-Loops**
Bei großen Prozessen (15+ Schritte) kann der Init-Loop 5+ Turns benötigen. Der Nutzer hat keine Information über den Fortschritt.

### Auswirkungen

- Nutzer bricht Session ab, weil UI "hängt"
- Vertrauensverlust in die Systemzuverlässigkeit
- Support-Aufwand durch Rückfragen

## 2. Ziel der Änderung

Der Nutzer erhält vor, während und nach der Background-Initialisierung sichtbare Rückmeldung über den aktuellen Zustand. Minimale Variante: Start- und Fertig-Nachricht. Empfohlene Variante: zusätzlich Fortschrittsinformation pro Init-Turn.

## 3. Lösung

### 3.1 Neues WebSocket-Event: `InitProgressEvent`

```python
class InitProgressEvent(BaseModel):
    event: Literal["init_progress"] = "init_progress"
    phase: str          # "structuring" oder "specification"
    status: str         # "started" | "in_progress" | "validating" | "completed"
    turn: int           # aktueller Init-Turn (1-basiert)
    max_turns: int      # _MAX_INIT_TURNS (8)
    message: str        # Lesbarer Status für die UI
```

### 3.2 Orchestrator: WebSocket-Referenz durchreichen

Der Orchestrator hat aktuell keinen Zugriff auf den WebSocket (Designentscheidung: HLA 3.3 — "Orchestrator kennt weder FastAPI noch WebSocket-Details"). Um die Entkopplung zu bewahren, wird ein **Callback-Pattern** eingeführt:

```python
# In orchestrator.py
class Orchestrator:
    def __init__(self, ..., on_init_progress: Callable[[InitProgressInfo], Awaitable[None]] | None = None):
        self._on_init_progress = on_init_progress
```

Der WebSocket-Handler in `websocket.py` setzt den Callback beim Erstellen des Orchestrators:

```python
async def _on_init_progress(info: InitProgressInfo):
    await _send_event(ws, InitProgressEvent(...))

orchestrator = _build_orchestrator(repo, settings, on_init_progress=_on_init_progress)
```

### 3.3 Events im Init-Loop

In `_run_background_init()` werden Events an folgenden Stellen gesendet:

1. **Vor Init-Loop**: `status="started"`, message="Das System bereitet das {Artefakt} vor..."
2. **Nach jedem Init-Turn**: `status="in_progress"`, message="Verarbeitung läuft (Turn {n}/{max})..."
3. **Vor Validator-Phase**: `status="validating"`, message="Qualitätsprüfung läuft..."
4. **Nach Abschluss**: `status="completed"`, message="Initialisierung abgeschlossen. Das {Artefakt} ist bereit."

### 3.4 Frontend-Handling

Das Frontend zeigt `init_progress`-Events als System-Statusmeldung an (z.B. als dezente Info-Bar über dem Chat oder als Typing-Indicator mit Text). Keine Chat-Bubble — es ist kein Dialog, sondern eine Systemmeldung.

### 3.5 SDD-Konsistenz

Kein SDD-Widerspruch. HLA 3.3 wird durch Callback-Pattern respektiert (Orchestrator kennt WebSocket nicht, nur einen generischen Callback). Neuer Event-Typ erweitert das bestehende Event-Modell (ADR-003).

### 3.6 Abwärtskompatibilität

- Callback ist optional (`None` als Default) — bestehende Tests und Orchestrator-Instanzen ohne Callback funktionieren unverändert
- Neuer Event-Typ: Frontend ignoriert unbekannte Events (bestehendes Verhalten) — kein Breaking Change
- `InitProgressEvent` ist additiv zum bestehenden Event-Union

---

### 3a. Abhängigkeiten & Konflikte

| Typ | CR | Beschreibung |
|---|---|---|
| Setzt voraus | CR-006 | Background-Init muss existieren |
| Konflikt | — | Keine bekannten Konflikte |

---

## 4. Änderungsplan

### Phase 1: Datenmodell & Events

1. **`core/events.py`**: `InitProgressEvent` hinzufügen (Felder: `event`, `phase`, `status`, `turn`, `max_turns`, `message`). In `WebSocketEvent`-Union aufnehmen.
2. **`core/orchestrator.py`**: `InitProgressInfo`-Dataclass oder TypedDict anlegen (gleiche Felder wie Event, aber ohne Pydantic — internes Modell). `on_init_progress`-Callback als optionalen Parameter in `__init__` aufnehmen.

### Phase 2: Init-Loop erweitern

3. **`core/orchestrator.py`** `_run_background_init()`: Callback-Aufrufe an den 4 Stellen aus §3.3 einbauen (started, in_progress pro Turn, validating, completed). Bei `on_init_progress is None` keine Aktion.
4. **`core/orchestrator.py`** `_run_correction_turns()`: Optional ebenfalls Callback für Korrektur-Fortschritt (status="correcting").

### Phase 3: WebSocket-Integration

5. **`api/websocket.py`** `_build_orchestrator()`: Callback-Closure erstellen, das `InitProgressInfo` in `InitProgressEvent` übersetzt und via `_send_event(ws, ...)` sendet. WebSocket-Referenz via Closure binden.
6. **`api/websocket.py`**: Sicherstellen, dass der Callback auch bei Fehlern im Init-Loop korrekt funktioniert (try/except um Callback-Aufruf).

### Phase 4: Frontend (minimal)

7. **`frontend/src/components/`**: `init_progress`-Events empfangen und als Typing-Indicator oder Info-Bar anzeigen. Bei `status="completed"` Indicator entfernen.

### Phase 5: Tests

8. **`tests/test_orchestrator.py`**: Test, dass Callback bei Init aufgerufen wird (Mock-Callback, Aufrufreihenfolge prüfen). Test, dass ohne Callback kein Fehler auftritt.
9. **`tests/test_websocket.py`** oder ähnlich: Integration-Test, dass `InitProgressEvent` über WebSocket gesendet wird.

---

## 5. Risiken und Mitigationen

| # | Risiko | Mitigation |
|---|---|---|
| R-1 | Callback-Fehler bricht Init-Loop ab | try/except um jeden Callback-Aufruf; Fehler loggen, aber Init fortsetzen |
| R-2 | WebSocket wird während Init geschlossen | Callback prüft Connection-State vor Send; bei Disconnect graceful abbrechen |
| R-3 | Frontend nicht aktualisiert → ignoriert neues Event | Frontend ignoriert unbekannte Events bereits; Feature ist additiv |

---

## 6. Nicht im Scope

- Parallelisierung der Init mit dem Moderator-Turn (separate Architektur-Entscheidung, ggf. eigener CR)
- Abbrechen der Init durch den Nutzer (Cancel-Button)
- Detailliertes Fortschritts-Feedback auf Ebene einzelner Strukturschritte

---

## 7. Abnahmekriterien

1. Neues `InitProgressEvent` in `core/events.py` mit allen Feldern aus §3.1
2. Orchestrator akzeptiert optionalen `on_init_progress`-Callback
3. `_run_background_init()` ruft Callback an mindestens 3 Stellen auf (started, in_progress, completed)
4. WebSocket-Handler setzt Callback und sendet Events an den Client
5. Bestehende Tests bleiben grün (Callback ist optional)
6. Neuer Test: Callback wird bei Init in korrekter Reihenfolge aufgerufen
7. Frontend zeigt mindestens Start- und Fertig-Meldung an

---

## 8. Aufwandsschätzung

| Aspekt | Wert |
|---|---|
| **Komplexität** | S–M |
| **Betroffene Dateien** | ~5 (events.py, orchestrator.py, websocket.py, Frontend-Komponente, Tests) |
| **Breaking Change** | Nein |
