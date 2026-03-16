# Codebase Review — Digitalisierungsfabrik

**Datum:** 2026-03-16
**Scope:** Gesamte Codebasis
**Methode:** 5 parallele Analyse-Agenten, konsolidiert

---

## 1. Gesamturteil

Die Digitalisierungsfabrik ist ein **solider, gut strukturierter Prototyp** mit sauberer Architektur, umfassender Testabdeckung und disziplinierter Governance. Die Kernanforderungen aus SDD und HLA sind korrekt umgesetzt: RFC 6902 Patches, dict-keyed Slots, ACID-Transaktionen, framework-agnostischer Orchestrator, Tool-Use-basierte LLM-Interaktion. Das System funktioniert End-to-End für die Epics 0–8 (Exploration, Structuring, Moderator). Schwächen liegen in verbreiteten `type: ignore`-Suppressions, duplizierten Hilfsfunktionen in Modes, fehlender Input-Validierung am WebSocket und einigen AI-Slop-Mustern (Stubs als laufender Code, magische Zahlen, verbose Kommentare). Für einen Prototypen ist das Ergebnis überdurchschnittlich gut.

---

## 2. Schulnoten

| Aspekt | Note | Kommentar |
|---|---|---|
| Vorgaben- & Requirements-Treue | **2** | Kernanforderungen sauber umgesetzt; 2 Dateien >300 Zeilen, einige tautologische Tests |
| Architektur & Struktur | **2** | Saubere Schichtung, Orchestrator framework-agnostisch, Executor-Pattern eingehalten |
| Code-Qualität & Wartbarkeit | **3** | Lesbar und modular, aber `type: ignore`-Spam, Magic Values, Assert statt Error-Handling |
| Redundanz / toter Code | **3** | Duplizierte Funktionen in Modes, sonst wenig toter Code |
| Security | **3** | Parameterisierte SQL-Queries gut; Input-Validierung am WebSocket fehlt, CORS zu offen |
| Tests | **2** | 305 Tests, 1.76:1 Test-Ratio; einige tautologische Tests, Security-Pfade nicht getestet |
| Anti-AI-Slop | **3** | `type: ignore`-Pattern, Stubs als laufender Code, verbose Kommentare; insgesamt aber zweckgerichtet |
| Prototyp-Fitness | **2** | Funktioniert E2E, gut dokumentiert, architektonisch übergabefähig |
| **Gesamtnote** | **2** | Guter Prototyp mit klar identifizierbaren Verbesserungsbereichen |

---

## 3. Wichtigste Befunde

### Gravierende Probleme

**F1 — File-Size-Limit-Verletzungen (AGENTS.md §9)**
- `backend/api/router.py`: 343 Zeilen (Limit: 300)
- `backend/persistence/project_repository.py`: 324 Zeilen
- Bindende Regel verletzt; Refactoring erforderlich

**F2 — Fehlende Input-Validierung am WebSocket**
- `backend/api/websocket.py:193-201`: `datei`-Feld wird ohne Größen- oder Formatvalidierung an TurnInput weitergereicht
- `backend/api/schemas.py:160`: `datei: str | None = None` ohne Constraints
- Ermöglicht Memory-Exhaustion durch überdimensionierte Payloads

**F3 — CORS zu offen**
- `backend/main.py:42-47`: `allow_methods=["*"], allow_headers=["*"]`
- Für Prototyp vertretbar, muss vor Produktion eingeschränkt werden

**F4 — Verbreitete `type: ignore[type-arg]`-Suppressions**
- Betrifft insbesondere `modes/exploration.py`, `modes/structuring.py`, `llm/anthropic_client.py`, `llm/openai_client.py`, `api/schemas.py`
- Statt `dict` ohne Type-Args sollte `dict[str, Any]` oder TypedDict verwendet werden
- Unterminiert den Nutzen von `mypy strict`

### Wichtige Probleme

**F5 — Duplizierte Hilfsfunktionen in Modes**
- `_translate_dialog_history()`: identisch in `exploration.py:125-133` und `structuring.py:62-70`
- `_build_slot_status()`: parallele Implementierungen in `exploration.py:65-75` und `structuring.py:40-59`
- Sollte in gemeinsame Utility extrahiert werden

**F6 — Magic Values ohne Konfiguration**
- `max_tokens=4096` hardcoded in `anthropic_client.py:59` und `openai_client.py:78`
- 50-Zeichen-Prefix-Heuristik in `exploration.py:115-119` ohne Erklärung
- Polling-Loop `range(50)` + `sleep(0.2)` in `websocket.py:138-141`

**F7 — Stub-Modes als laufender Code**
- `modes/specification.py` und `modes/validation.py` liefern statische Stub-Antworten statt `NotImplementedError`
- `llm/ollama_client.py` ebenso
- Nutzer erhalten irreführende Antworten statt klarer Fehlermeldung

**F8 — `assert` statt Error-Handling in Orchestrator**
- `core/orchestrator.py:142`: `assert result.artifact is not None`
- Assertions können mit `-O` deaktiviert werden; gehört in produktionsnahen Code nicht

**F9 — Kein WebSocket Rate-Limiting**
- Unbegrenzte Turn-Nachrichten möglich → LLM-Kosten-Explosion, DoS
- Kein Token-Budget-Tracking pro Projekt

### Positive Punkte

**P1 — Architektur sauber umgesetzt**
- Orchestrator kennt weder FastAPI noch WebSocket (framework-agnostisch)
- Modes liefern nur Patches; alle Writes gehen durch Executor
- RFC 6902 + dict-keyed Slots durchgängig eingehalten

**P2 — Umfassende Testabdeckung**
- 305 Tests in 18 Dateien; ~6000 LOC Tests bei ~3400 LOC Backend-Code
- E2E-Tests mit echtem LLM-Flow (Moderator → Exploration → Phasenwechsel)
- Executor-Tests: Rollback-Semantik, Invalidierungs-Kaskade, RFC-6902-Validierung

**P3 — ADR-Compliance**
- 5 ADRs (001–005), alle vor Implementierung geschrieben und akzeptiert
- Abweichungen sauber dokumentiert (z.B. ADR-002: Flags-Persistierung)

**P4 — Funktionsfähiges End-to-End-System**
- Epics 0–8 vollständig implementiert (obwohl README nur 0–1 als fertig zeigt)
- React-Frontend mit Split-Pane-Layout, WebSocket-Integration, Echtzeit-Updates
- System ist als Prototyp demonstrierbar

**P5 — Keine TODOs/FIXMEs im Code**
- `grep TODO` im Backend liefert 0 Treffer — AGENTS.md-Compliance bestätigt

---

## 4. Handlungsempfehlungen

### Jetzt beheben

1. **`router.py` und `project_repository.py` refactoren** — unter 300 Zeilen bringen (bindende AGENTS.md-Regel). Router: Hilfsfunktionen in separates Modul extrahieren. Repository: Artifact-Versioning in eigene Klasse.

2. **WebSocket `datei`-Feld validieren** — `max_length` im Schema, Base64-Format prüfen, Größenlimit (z.B. 5 MB). Ohne dies ist Memory-Exhaustion trivial.

3. **README aktualisieren** — Implementierungsfortschritt spiegelt Epic 0–1 wider, tatsächlich sind Epics 0–8 fertig. Stakeholder werden irregeführt.

### Bald verbessern

4. **`type: ignore[type-arg]` eliminieren** — `dict` durch `dict[str, Any]` oder TypedDict ersetzen. Macht `mypy strict` erst sinnvoll nutzbar.

5. **Duplizierte Mode-Funktionen extrahieren** — `_translate_dialog_history()` und `_build_slot_status()` in shared Utility (z.B. `modes/helpers.py`).

6. **Magic Values in Settings überführen** — `max_tokens=4096` → `Settings.llm_max_tokens`; Polling-Timeout als benannte Konstante.

7. **Stub-Modes mit `NotImplementedError` ersetzen** — Specification, Validation, Ollama: klare Fehlermeldung statt irreführende Stub-Antworten.

8. **CORS einschränken** — `allow_methods` und `allow_headers` explizit auf benötigte Werte setzen.

### Später beobachten

9. **WebSocket Rate-Limiting** — Turn-Frequenz pro Projekt begrenzen (z.B. max 5/Minute). Aktuell kein externer Zugriff, aber vor Demo-Betrieb nötig.

10. **Tautologische Tests rewriten** — `test_models.py`: Enum-Wert-Tests durch Behavior-Tests ersetzen (AGENTS.md Rule T-1).

11. **E2E-Pytest-Mark registrieren** — `markers = ["e2e: real LLM end-to-end tests"]` in `pyproject.toml`, damit selektive Ausführung möglich wird.

12. **Frontend-Typing verbessern** — `ArtifactTab.tsx`: Mega-Interface `Slot` durch Discriminated Unions ersetzen (`ExplorationSlot | StructureSlot | AlgorithmSlot`).

---

*Report generiert am 2026-03-16 durch Multi-Agent Codebase Review.*
