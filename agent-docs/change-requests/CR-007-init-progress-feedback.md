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

Die Background-Initialisierung (CR-006, ADR-008) läuft synchron innerhalb von `process_turn()` in Schritt 10b des Orchestrator-Zyklus. Da der WebSocket-Handler (`api/websocket.py`) erst **nach Abschluss des gesamten Turns** Events an den Client sendet (`_send_turn_events()`), erhält der Nutzer für 10–40 Sekunden keinerlei Rückmeldung. Die UI wirkt eingefroren.

### Konkrete Defizite

**D-1: Kein Start-Feedback**
Der Nutzer sieht nicht, dass eine Initialisierung läuft. Die letzte sichtbare Aktion ist die Moderator-Nachricht zum Phasenwechsel. Ablauf aktuell:

```
[Moderator]: "Ich wechsle jetzt in die Strukturierungsphase."
→ 10–40 Sekunden Stille (Init läuft intern)
→ [Structurer]: "Hier ist der Prozess, den ich entworfen habe..."
```

**D-2: Kein Abschluss-Feedback**
Nach Abschluss der Init wird der erste Dialog-Turn des Structurer/Specifier gesendet, aber ohne Kontext — der Nutzer weiß nicht, warum die Antwort so lange gedauert hat.

**D-3: Kein Fortschritts-Feedback bei langen Init-Loops**
Bei großen Prozessen (15+ Schritte) kann der Init-Loop 5+ LLM-Turns benötigen. Der Nutzer hat keine Information über den Fortschritt.

### Auswirkungen

- Nutzer bricht Session ab, weil UI "hängt"
- Vertrauensverlust in die Systemzuverlässigkeit
- Support-Aufwand durch Rückfragen

## 2. Ziel der Änderung

- Der Nutzer erhält **vor** der Background-Init eine sichtbare Statusmeldung ("System bereitet Artefakt vor...")
- Der Nutzer erhält **nach** der Init eine Abschlussmeldung ("Initialisierung abgeschlossen")
- Optional: Fortschrittsinformation pro Init-Turn ("Verarbeitung läuft, Turn 3/8...")
- Die HLA-Entkopplung (Orchestrator kennt WebSocket nicht) bleibt erhalten

## 3. Lösung

### 3.1 Neues WebSocket-Event: `InitProgressEvent`

Neuer Event-Typ in `core/events.py`, ergänzt die bestehende `WebSocketEvent`-Union:

```python
class InitProgressEvent(BaseModel):
    """Init progress event — sent during background initialization (CR-007)."""

    event: Literal["init_progress"] = "init_progress"
    phase: str          # "structuring" oder "specification"
    status: str         # "started" | "in_progress" | "validating" | "completed"
    turn: int           # aktueller Init-Turn (1-basiert), 0 bei started/completed
    max_turns: int      # _MAX_INIT_TURNS (8)
    message: str        # Lesbarer Status für die UI
```

Beispiel-Payloads, wie sie über den WebSocket gesendet werden:

```json
{"event": "init_progress", "phase": "structuring", "status": "started", "turn": 0, "max_turns": 8, "message": "Das System bereitet das Strukturartefakt vor..."}
{"event": "init_progress", "phase": "structuring", "status": "in_progress", "turn": 3, "max_turns": 8, "message": "Verarbeitung läuft (Turn 3/8)..."}
{"event": "init_progress", "phase": "structuring", "status": "validating", "turn": 0, "max_turns": 8, "message": "Qualitätsprüfung läuft..."}
{"event": "init_progress", "phase": "structuring", "status": "completed", "turn": 0, "max_turns": 8, "message": "Initialisierung abgeschlossen. Das Strukturartefakt ist bereit."}
```

### 3.2 Orchestrator: Callback-Pattern für Entkopplung

Der Orchestrator hat keinen Zugriff auf den WebSocket (HLA 3.3: "Orchestrator kennt weder FastAPI noch WebSocket-Details"). Um die Entkopplung zu bewahren, wird ein **Callback-Pattern** eingeführt.

Internes Callback-Modell im Orchestrator (kein Pydantic, nur TypedDict):

```python
class InitProgressInfo(TypedDict):
    phase: str
    status: str
    turn: int
    max_turns: int
    message: str
```

Neuer optionaler Parameter in `Orchestrator.__init__`:

```python
class Orchestrator:
    def __init__(
        self,
        repository: ProjectRepository,
        modes: dict[str, BaseMode],
        settings: Settings | None = None,
        on_init_progress: Callable[[InitProgressInfo], Awaitable[None]] | None = None,  # NEU
    ) -> None:
        self._repository = repository
        self._modes = modes
        self._settings = settings
        self._on_init_progress = on_init_progress  # NEU
        self._executor = Executor()
        self._calculator = CompletenessCalculator()
```

### 3.3 Callback-Aufrufe im Init-Loop

In `_run_background_init()` werden Callback-Aufrufe an 4 Stellen eingebaut:

1. **Vor Init-Loop**: `status="started"`, `message="Das System bereitet das {Strukturartefakt/Algorithmusartefakt} vor..."`
2. **Nach jedem Init-Turn**: `status="in_progress"`, `message="Verarbeitung läuft (Turn {n}/{max})..."`
3. **Vor Validator-Phase**: `status="validating"`, `message="Qualitätsprüfung läuft..."`
4. **Nach Abschluss**: `status="completed"`, `message="Initialisierung abgeschlossen. Das {Artefakt} ist bereit."`

Jeder Aufruf wird in `try/except` gewrapped — Callback-Fehler dürfen den Init-Loop nicht abbrechen:

```python
async def _emit_init_progress(self, info: InitProgressInfo) -> None:
    if self._on_init_progress is not None:
        try:
            await self._on_init_progress(info)
        except Exception:
            logger.warning("orchestrator.init_progress_callback_error", info=info)
```

### 3.4 WebSocket-Integration

In `api/websocket.py` wird `_build_orchestrator()` um den Callback erweitert. Da `_build_orchestrator()` pro Session in `websocket_session()` aufgerufen wird, wo `ws` verfügbar ist, kann der Callback als Closure gebunden werden:

```python
def _build_orchestrator(
    repo: ProjectRepository, settings: Settings, ws: WebSocket | None = None
) -> Orchestrator:
    # ... modes wie bisher ...

    async def _on_init_progress(info: InitProgressInfo) -> None:
        if ws is not None:
            await _send_event(ws, InitProgressEvent(**info))

    return Orchestrator(
        repository=repo, modes=modes, settings=settings,
        on_init_progress=_on_init_progress if ws else None,
    )
```

Aufruf in `websocket_session()`:
```python
orchestrator = _build_orchestrator(repo, settings, ws=ws)
```

### 3.5 Frontend-Handling

Das Frontend (`frontend/src/api/websocket.ts`) hat bereits einen Switch/Case-Dispatcher mit `default: console.warn(...)` für unbekannte Events. Für die minimale Implementierung:

- Neuer Case `"init_progress"` im `handleEvent`-Switch
- Dispatch einer neuen Action `SET_INIT_PROGRESS` an den Session-State
- UI-Darstellung: Typing-Indicator mit dem `message`-Text aus dem Event
- Bei `status="completed"` → Indicator entfernen

Keine Chat-Bubble — es ist kein Dialog, sondern eine Systemmeldung.

### 3.6 SDD-Konsistenz

**Konsistent.** FR-F-01 (Fortschrittsanzeige) fordert Feedback über den Systemzustand — dieses Feature erweitert diese Anforderung auf die Init-Phase. HLA 3.3 wird durch Callback-Pattern respektiert: der Orchestrator kennt weder WebSocket noch FastAPI, sondern nur einen generischen async Callback.

### 3.7 ADR-Konsistenz

**Konsistent mit ADR-008 (CR-006).** ADR-008 definiert die Background-Init als "Inline-Multi-Call im Orchestrator-Turn". Der Callback ändert nichts an dieser Architektur — er fügt lediglich Observabilität hinzu. Der Init-Loop bleibt synchron-blockierend.

### 3.8 Abwärtskompatibilität

- `on_init_progress`-Parameter ist optional (`None` als Default) — alle bestehenden Tests und Orchestrator-Instanzen (insbesondere in `test_orchestrator.py`) funktionieren unverändert
- `InitProgressEvent` ist additiv zur bestehenden `WebSocketEvent`-Union — kein Breaking Change
- Frontend: `default: console.warn(...)` ignoriert unbekannte Events graceful (Zeile 124–126 in `websocket.ts`) — das Feature kann backend-seitig deployed werden, bevor das Frontend aktualisiert wird

---

### 3a. Abhängigkeiten & Konflikte

| Typ | CR | Beschreibung |
|---|---|---|
| Setzt voraus | CR-006 (Verifiziert) | Background-Init muss existieren (`_run_background_init()` in `orchestrator.py`) |
| Ermöglicht | CR-008 (Entwurf) | Phasenende-Validator kann den gleichen Callback nutzen (status="phase_validating") |
| Konflikt | — | Keine Konflikte mit aktiven CRs (CR-002 Implementiert, CR-003 Verifiziert, CR-004 Implementiert betreffen andere Bereiche) |

---

## 4. Änderungsplan

### Phase 1: Datenmodell & Events

| # | Datei | Änderung |
|---|---|---|
| 1 | `core/events.py` | `InitProgressEvent(BaseModel)` hinzufügen mit Feldern `event`, `phase`, `status`, `turn`, `max_turns`, `message`. In `WebSocketEvent`-Union aufnehmen. |
| 2 | `core/orchestrator.py` | `InitProgressInfo = TypedDict("InitProgressInfo", phase=str, status=str, turn=int, max_turns=int, message=str)` am Modulanfang definieren. Import: `from typing import TypedDict`. |

### Phase 2: Orchestrator erweitern

| # | Datei | Änderung |
|---|---|---|
| 3 | `core/orchestrator.py` | `on_init_progress: Callable[[InitProgressInfo], Awaitable[None]] | None = None` als 4. Parameter in `__init__` aufnehmen. Als `self._on_init_progress` speichern. |
| 4 | `core/orchestrator.py` | Neue Hilfsmethode `async _emit_init_progress(self, info: InitProgressInfo) -> None` — ruft Callback in try/except auf, loggt Fehler. |
| 5 | `core/orchestrator.py` `_run_background_init()` | 4 Callback-Aufrufe einbauen: (a) vor Init-Loop `status="started"`, (b) nach jedem Turn `status="in_progress"` mit Turn-Zähler, (c) vor Validator `status="validating"`, (d) nach Abschluss `status="completed"`. |
| 6 | `core/orchestrator.py` `_run_correction_turns()` | Optional: Callback mit `status="correcting"` und Versuchszähler. |

### Phase 3: WebSocket-Integration

| # | Datei | Änderung |
|---|---|---|
| 7 | `api/websocket.py` | Import: `InitProgressEvent` aus `core/events`, `InitProgressInfo` aus `core/orchestrator`. |
| 8 | `api/websocket.py` `_build_orchestrator()` | Neuen Parameter `ws: WebSocket | None = None` aufnehmen. Callback-Closure erstellen, das `InitProgressInfo` in `InitProgressEvent` übersetzt und via `_send_event(ws, ...)` sendet. An `Orchestrator(on_init_progress=...)` übergeben. |
| 9 | `api/websocket.py` `websocket_session()` | `_build_orchestrator(repo, settings, ws=ws)` aufrufen statt `_build_orchestrator(repo, settings)`. |

### Phase 4: Frontend

| # | Datei | Änderung |
|---|---|---|
| 10 | `frontend/src/api/websocket.ts` | Neuer Case `"init_progress"` in `handleEvent`: Dispatch `SET_INIT_PROGRESS` mit `status` und `message`. |
| 11 | `frontend/src/components/` (Chat oder Session-Bereich) | Init-Progress-Indicator anzeigen: bei `status != "completed"` den `message`-Text als Typing-Indicator oder Info-Bar darstellen. Bei `"completed"` entfernen. |

### Phase 5: Tests

| # | Datei | Änderung |
|---|---|---|
| 12 | `tests/test_orchestrator.py` | Test: Mock-Callback an Orchestrator übergeben. Init auslösen. Prüfen: Callback wurde in Reihenfolge `started → in_progress → validating → completed` aufgerufen. |
| 13 | `tests/test_orchestrator.py` | Test: Orchestrator ohne Callback (`on_init_progress=None`). Init auslösen. Prüfen: kein Fehler, Init läuft normal. |
| 14 | `tests/test_orchestrator.py` | Test: Callback wirft Exception. Init auslösen. Prüfen: Init läuft trotzdem vollständig durch (R-1 Mitigation). |

---

## 5. Risiken und Mitigationen

| # | Risiko | Mitigation |
|---|---|---|
| R-1 | Callback-Fehler bricht Init-Loop ab | `_emit_init_progress()` wrapped jeden Aufruf in try/except; Fehler wird geloggt, Init läuft weiter. Test AC #14 verifiziert. |
| R-2 | WebSocket wird während Init geschlossen (Nutzer schließt Tab) | `_send_event()` wrapped in try/except im Callback-Closure. Bei Disconnect: Callback-Fehler wird von R-1 abgefangen, Init läuft intern zuende. |
| R-3 | Frontend nicht aktualisiert → ignoriert neues Event | `default: console.warn(...)` in `websocket.ts` ignoriert unbekannte Events graceful. Backend-Deployment ist unabhängig vom Frontend-Deployment möglich. |
| R-4 | Erhöhte Komplexität im Orchestrator-Konstruktor | Callback ist optional mit Default `None`. Bestehende Instanziierungen in Tests müssen nicht angepasst werden (Keyword-Argument). |

---

## 6. Nicht im Scope

- Parallelisierung der Init mit dem Moderator-Turn (separate Architektur-Entscheidung, ggf. eigener CR)
- Abbrechen der Init durch den Nutzer (Cancel-Button)
- Detailliertes Fortschritts-Feedback auf Ebene einzelner Strukturschritte
- Init-Fortschritt in Working Memory persistieren (nur transient via WebSocket)

---

## 7. Abnahmekriterien

1. `InitProgressEvent` in `core/events.py` mit allen 6 Feldern (`event`, `phase`, `status`, `turn`, `max_turns`, `message`), aufgenommen in `WebSocketEvent`-Union
2. `InitProgressInfo` als TypedDict in `core/orchestrator.py`
3. `Orchestrator.__init__` akzeptiert optionalen `on_init_progress`-Callback (Default `None`)
4. `_run_background_init()` ruft Callback an mindestens 4 Stellen auf: `started`, `in_progress` (pro Turn), `validating`, `completed`
5. Jeder Callback-Aufruf ist in try/except gewrapped (Fehler-Resilienz)
6. `_build_orchestrator()` in `websocket.py` akzeptiert `ws`-Parameter und erstellt Callback-Closure
7. `websocket_session()` übergibt `ws` an `_build_orchestrator()`
8. Frontend zeigt mindestens Start- und Fertig-Meldung an (Typing-Indicator oder Info-Bar)
9. Bestehende Tests bleiben grün (Callback ist optional, kein Breaking Change)
10. Neuer Test: Callback wird bei Init in korrekter Reihenfolge aufgerufen (started → in_progress → … → completed)
11. Neuer Test: Ohne Callback kein Fehler (graceful None-Handling)
12. Neuer Test: Callback-Exception bricht Init nicht ab

---

## 8. Aufwandsschätzung

| Phase | Betroffene Dateien | Komplexität |
|---|---|---|
| Phase 1: Events & TypedDict | `core/events.py`, `core/orchestrator.py` | S |
| Phase 2: Orchestrator Callback | `core/orchestrator.py` | S |
| Phase 3: WebSocket-Integration | `api/websocket.py` | S |
| Phase 4: Frontend | `frontend/src/api/websocket.ts`, UI-Komponente | S |
| Phase 5: Tests | `tests/test_orchestrator.py` | S |

| Aspekt | Wert |
|---|---|
| **Komplexität** | S (additive Änderung, kein neues Architektur-Paradigma) |
| **Betroffene Dateien** | 5–6 (events.py, orchestrator.py, websocket.py, websocket.ts, UI-Komponente, test_orchestrator.py) |
| **Breaking Change** | Nein |
