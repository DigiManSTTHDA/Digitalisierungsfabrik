# Codebase Review — Kalibriert

**Datum:** 2026-03-16
**Grundlage:** `agent-docs/reports/codebase-review-latest.md`
**Methode:** Skeptischer Evidenz-Check gegen tatsächlichen Code

---

## 1. Kalibrierungsurteil

Die ursprüngliche Review ist **überwiegend substanziell**, aber mit messbarem Reviewer-Rauschen in drei Bereichen:

1. **Übertriebene Zahlen**: Die Behauptung "1254 type: ignore-Suppressions" ist falsch — tatsächlich 124, davon ~50% in Testdateien. Das ändert den Schweregrad erheblich.
2. **Falsche Sicherheitsbehauptung**: Ein Subagent behauptete, der API-Key sei im Repository committed. `.env` ist gitignored (Zeile 16 der `.gitignore`), `git ls-files backend/.env` liefert keine Treffer. Die Behauptung ist **faktisch falsch**.
3. **Stub-Kritik ohne Kontextprüfung**: Die Stub-Modes (Specification, Validation) wurden als "irreführend für Nutzer" kritisiert, sind aber in `websocket.py` gar nicht registriert — sie werden im laufenden System **nie aufgerufen**. Ollama raising `NotImplementedError` ist korrekt, nicht problematisch.

Die Architektur- und Testbewertungen sind solide. Die Handlungsempfehlungen sind größtenteils berechtigt, einige aber überdimensioniert.

---

## 2. Re-kalibrierte Findings

### F1 — File-Size-Limit-Verletzungen
**Original:** Kritisch — `router.py` (343) und `project_repository.py` (324) über 300-Zeilen-Limit
**Evidenz:** `wc -l` bestätigt exakt diese Zahlen. Bindende AGENTS.md-Regel.
**Neue Einstufung: A — Belastbares Problem**
Keine Abschwächung nötig. 343 und 324 Zeilen bei Limit 300 — geringfügig, aber die Regel ist explizit.

### F2 — Fehlende Input-Validierung am WebSocket (datei-Feld)
**Original:** Kritisch — Memory-Exhaustion möglich durch unbegrenzte Payloads
**Evidenz:** `websocket.py:200` nimmt `data.get("datei")` ohne Validierung; `schemas.py:160` definiert `datei: str | None = None` ohne `max_length`. Allerdings: Der WebSocket-Handler nutzt das Schema gar nicht für Validierung — er parst rohes JSON.
**Konkreter Schaden:** In einem Prototyp ohne öffentlichen Zugang begrenzt. WebSocket ist nur über localhost:5173 erreichbar (CORS). Ein Angreifer bräuchte lokalen Zugang.
**Neue Einstufung: B — Plausibler Hinweis**
Echte Validierungslücke, aber der konkrete Angriffsvektor für einen lokalen Prototypen ist gering. Vor jeder öffentlichen Demo beheben.

### F3 — CORS zu offen
**Original:** Kritisch — `allow_methods=["*"], allow_headers=["*"]`
**Evidenz:** `main.py:44-46` bestätigt. Aber: `allow_origins` ist auf `["http://localhost:5173"]` beschränkt. Wildcard-Methods/Headers bei einer einzigen, lokalen Origin sind funktional harmlos.
**Neue Einstufung: D — Für Prototypen okay**
Die Origin-Restriction ist das entscheidende Schutzkriterium. Wildcard-Methods bei localhost-Origin sind Prototyp-Pragmatik, kein Sicherheitsproblem.

### F4 — Verbreitete `type: ignore[type-arg]`-Suppressions
**Original:** Kritisch — "unterminiert den Nutzen von mypy strict"
**Evidenz:** Tatsächlich **124** Vorkommen in 26 Dateien (nicht 1254 wie ein Agent behauptete). ~60 davon in Testdateien. In Produktivcode betrifft es primär die `dict`-Parameter der LLM-Client-Interfaces (`list[dict]` statt `list[dict[str, Any]]`).
**Konkreter Schaden:** Begrenzt. Die Ignores betreffen fast ausschließlich `dict` ohne Type-Arg — ein bekanntes mypy-Strict-Artefakt. Die eigentliche Typsicherheit der Domänenmodelle (Pydantic) ist davon nicht betroffen.
**Neue Einstufung: B — Plausibler Hinweis**
Echtes Cleanup-Thema, aber kein "Spam" und kein Sicherheits- oder Korrektheitsproblem. Abschwächung von "kritisch" auf "bald verbessern" ist angemessen.

### F5 — Duplizierte Hilfsfunktionen in Modes
**Original:** Wichtig — `_translate_dialog_history()` und `_build_slot_status()` dupliziert
**Evidenz:**
- `_translate_dialog_history()`: Tatsächlich **identisch** in `exploration.py:125-133` und `structuring.py:62-70`. Bestätigt.
- `_build_slot_status()`: **NICHT identisch**. `exploration.py:65-75` iteriert über Exploration-PFLICHT_SLOTS mit Inhalt/Status. `structuring.py:40-59` iteriert über Strukturschritte mit Typ/Reihenfolge/Nachfolger. Unterschiedliche Datenquellen, unterschiedliche Formatierung, unterschiedlicher Output. Gleicher Funktionsname, aber verschiedene Logik.
**Neue Einstufung: B → nur `_translate_dialog_history()` ist echtes Duplikat**
`_build_slot_status()` ist ein False Positive — gleicher Name, andere Funktion. Nur 1 von 2 beanstandeten Duplikaten ist real.

### F6 — Magic Values ohne Konfiguration
**Original:** Wichtig — `max_tokens=4096`, 50-Zeichen-Heuristik, Polling-Loop
**Evidenz:**
- `max_tokens=4096`: Bestätigt in `anthropic_client.py:59` und `openai_client.py:78`. Für einen Prototyp ist 4096 ein vernünftiger Default. Konfigurierbar zu machen wäre nice-to-have, blockiert aber nichts.
- 50-Zeichen-Heuristik (`exploration.py:116`): `existing[:50] not in value` — tatsächlich undokumentiert und fragil, aber kontextspezifische Merge-Logik mit begrenzter Schadwirkung.
- Polling-Loop (`websocket.py:138-139`): `range(50)` + `sleep(0.2)` mit erklärendem Kommentar `# up to 10 seconds`. Der Kommentar IST die Dokumentation.
**Neue Einstufung: C — Überwiegend Geschmack/Konvention**
`max_tokens` und Polling-Loop sind Prototyp-pragmatisch. Die 50-Zeichen-Heuristik ist das einzig fragile Element (B — plausibler Hinweis als Einzelfinding).

### F7 — Stub-Modes als laufender Code
**Original:** Wichtig — Nutzer erhalten irreführende Stub-Antworten
**Evidenz:** Die Behauptung ist **faktisch falsch**.
- `specification.py` und `validation.py` sind Stubs, aber sie sind in `websocket.py:43-46` **nicht registriert**. Nur `exploration` und `moderator` werden dem Orchestrator übergeben. Die Stubs werden **nie aufgerufen**.
- `ollama_client.py` wirft korrekterweise `NotImplementedError` — genau das, was der Review als Best Practice forderte.
- Die Stubs existieren als Code-Skelette für zukünftige Epics (09, 10) und erfüllen den BaseMode-Contract.
**Neue Einstufung: F — Verwerfen**
Kein Problem. Die Stubs sind korrekt implementiert und werden nicht aufgerufen.

### F8 — `assert` statt Error-Handling in Orchestrator
**Original:** Wichtig — `orchestrator.py:142`: `assert result.artifact is not None`
**Evidenz:** Zeile 138 prüft `if not result.success:` und gibt vorher einen Fehler zurück. Der `assert` auf Zeile 142 dokumentiert die Invariante: "Wenn success=True, dann ist artifact immer nicht-None". Das ist ein **Typ-Narrowing-Assert** für mypy, kein Error-Handling.
**Konkreter Schaden:** Keiner. Die Bedingung kann nach der success-Prüfung nie eintreten. Der Assert dient als Typ-Annotation.
**Neue Einstufung: D — Für Prototypen okay**
Standard-Pattern für mypy Typ-Narrowing nach optionalen Returns. Kein Handlungsbedarf.

### F9 — Kein WebSocket Rate-Limiting
**Original:** Wichtig — LLM-Kosten-Explosion, DoS
**Evidenz:** Korrekt, es gibt kein Rate-Limiting. Aber: Der WebSocket ist nur über localhost:5173 erreichbar. Es gibt keinen externen Zugang. DoS müsste vom lokalen Entwicklerrechner kommen.
**Neue Einstufung: D — Für Prototypen okay**
Wird relevant bei öffentlichem Deployment oder Demo-Betrieb. Für lokale Prototyp-Entwicklung kein Problem.

---

## 3. Verworfene oder deutlich abgeschwächte Findings

| Finding | Original | Kalibriert | Begründung |
|---|---|---|---|
| F7 — Stub-Modes | Wichtig | **F — Verworfen** | Stubs nicht im laufenden System registriert; Ollama korrekt mit NotImplementedError |
| F8 — Assert in Orchestrator | Wichtig | **D — Prototyp ok** | Typ-Narrowing-Assert nach bereits geprüfter Bedingung, kein Error-Handling-Defizit |
| F3 — CORS | Kritisch | **D — Prototyp ok** | Origins auf localhost beschränkt; Wildcard-Methods irrelevant |
| F6 — Magic Values | Wichtig | **C — Geschmack** (bis auf 50-Char-Heuristik) | max_tokens und Polling mit Kommentar sind vertretbar |
| F5 — `_build_slot_status` Duplikat | Wichtig | **Teilweise F** | Gleicher Name, verschiedene Logik und Datenquelle |
| F9 — Rate-Limiting | Wichtig | **D — Prototyp ok** | Kein externer Zugang; wird erst bei öffentlichem Betrieb relevant |
| (Subagent) — API-Key committed | Kritisch | **F — Verwerfen** | Faktisch falsch. `.env` ist gitignored, nicht getrackt |
| (Subagent) — 1254 type:ignore | Kritisch | **Korrektur auf 124** | Zahl um Faktor 10 übertrieben |

---

## 4. Bereinigtes Gesamtbild

Nach Entfernung von Reviewer-Theater und Faktenchecks bleiben **3 belastbare Probleme**:

### Kategorie A — Belastbar

1. **F1 — File-Size-Limit-Verletzungen**: `router.py` (343) und `project_repository.py` (324) verletzen die bindende 300-Zeilen-Regel aus AGENTS.md. Einfach zu beheben, sollte im nächsten Commit passieren.

2. **F5 (nur `_translate_dialog_history`)**: Identische Funktion in zwei Dateien. Kleine, aber echte DRY-Verletzung. Extraction in Shared-Utility.

3. **README veraltet**: Zeigt nur Epic 0–1 als fertig, tatsächlich sind 0–8 implementiert. Irreführend für Stakeholder.

### Kategorie B — Plausibel, begrenzte Auswirkung

4. **F2 — WebSocket datei-Validierung**: Echte Lücke, aber nur bei öffentlichem Zugang relevant.
5. **F4 — type: ignore (124 Vorkommen)**: Cleanup-Thema für Code-Hygiene, kein Korrektheitsproblem.
6. **50-Zeichen-Heuristik** in `exploration.py:116`: Undokumentiert und fragil.

### Alles andere: Prototyp-vertretbar oder verworfen.

Die Codebasis ist **solide für einen Prototypen**. Die Architektur ist sauber, die Testabdeckung ist hoch, die Governance wird eingehalten. Die tatsächlichen Probleme sind geringfügig und leicht behebbar.

---

## 5. Korrigierte Noten

| Aspekt | Original | Kalibriert | Begründung |
|---|---|---|---|
| Vorgaben- & Requirements-Treue | 2 | **2** | Bestätigt. File-Size-Verletzung bleibt. |
| Architektur & Struktur | 2 | **1–2** | Eher 1. Saubere Schichtung, keine echten Architekturprobleme gefunden. |
| Code-Qualität & Wartbarkeit | 3 | **2** | type:ignore ist Hygiene, nicht Qualität. Assert ist Standard-Pattern. Keine echten Qualitätsmängel. |
| Redundanz / toter Code | 3 | **2** | Nur 1 echtes Duplikat bestätigt statt 2. Kein toter Code gefunden. |
| Security | 3 | **2** | API-Key-Behauptung falsch. CORS nur bei localhost. SQL parameterisiert. Für Prototyp gut. |
| Tests | 2 | **2** | Bestätigt. Einige tautologische Enum-Tests, aber Gesamtqualität hoch. |
| Anti-AI-Slop | 3 | **2** | Stub-Kritik verworfen, Magic-Values abgeschwächt. Code ist zweckgerichtet, nicht generisch. |
| Prototyp-Fitness | 2 | **1–2** | Funktioniert E2E, gut dokumentiert, architektonisch übergabefähig. |
| **Gesamtnote** | **2** | **2** | Bestätigt. Tendenz Richtung 1–2 nach Kalibrierung. Guter bis sehr guter Prototyp. |

---

## Fazit

Die ursprüngliche Review war insgesamt fair, aber mit typischen Multi-Agent-Review-Artefakten: übertriebene Zahlen (type:ignore), faktisch falsche Behauptungen (API-Key), und Findings ohne Kontextprüfung (Stub-Modes). Nach Kalibrierung bleibt ein Bild von einem **gut gebauten Prototypen** mit 3 klaren Handlungspunkten (File-Size-Refactoring, DRY-Extraction, README-Update) und einigen optionalen Verbesserungen. Kein Befund ist architektonisch oder sicherheitskritisch.

---

*Kalibrierung durchgeführt am 2026-03-16 gegen tatsächlichen Codestand.*
