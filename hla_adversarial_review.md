# ADVERSARIALE ANALYSE — HLA Digitalisierungsfabrik
**Gegenstand:** `hla_architecture.md`
**Perspektive:** Kritischer Review durch einen skeptischen Architekten
**Ziel:** Schwächen und Risiken der Architekturentscheidungen benennen, Alternativen bewerten

---

## Legende

| Bewertung | Bedeutung |
|---|---|
| **GUT** | Entscheidung ist begründet, Risiken sind gering oder beherrscht |
| **AKZEPTABEL** | Entscheidung ist vertretbar für den Prototyp, trägt aber bekannte Lasten |
| **KONTROVERS** | Entscheidung ist angreifbar — es existieren Alternativen mit materiellem Vorteil |

Kontroverse Entscheidungen werden mit Alternativen, Schwächen-Mitigierung und Komplexitäts-/Stabilitäts-/Wartbarkeitsauswirkung bewertet.

---

## 1. GUT: RFC 6902 JSON Patch als Schreibprotokoll

Das SDD schreibt RFC 6902 explizit vor und begründet die Entscheidung gegenüber Alternativen (Unified Diffs, Search/Replace). Diese Begründung ist valide. Die Implementierung via `jsonpatch`-Bibliothek ist Standard.

**Stärke:** Lokalisierungsproblem wird durch Pfad-Adressierung strukturell gelöst. LLM kann keine unkontrollierten Änderungen vornehmen. Snapshot + Rollback ist deterministisch implementierbar.

**Bekannte Last (nicht disqualifizierend):** Die Bibliothek `jsonpatch` ist stabil aber nicht mehr aktiv maintained (letztes Release 2021). Alternativen wie `jsonpatch2` existieren, sind aber ungetestet in diesem Kontext. Für den Prototyp ist das kein Problem.

---

## 2. GUT: Pydantic v2 für Datenmodelle

Pydantic v2 ist die natürliche Wahl für Python-Datenmodelle mit Pflichtfeldern, Enums und Validierungslogik. Die Schema-Derivation (Pydantic → JSON Schema via `model_json_schema()`) ist dokumentiert und stabil.

**Stärke:** Single Source of Truth für Feldtypen und Pflicht/Optional-Status. Serialisierung zu JSON ist trivial. Kompakte Darstellung von Enums.

---

## 3. GUT: Abstrakte LLM-Schnittstelle (AnthropicClient / OllamaClient)

Das Interface-Muster ist korrekt. Die Anforderung aus dem SDD (Modell ohne Code-Änderung austauschbar) ist strukturell erfüllt.

**Bekannte Last:** Die Abstraktion versteckt Fähigkeitsunterschiede. Claude Opus kann 100k+ Token Kontext verarbeiten; lokale Llama-3-8B-Modelle typischerweise 8k–32k. Ein Modus, der für Claude kalibriert wurde, kann bei einem kleinen Ollama-Modell schlicht abschneiden — nicht wegen eines Code-Fehlers, sondern wegen eines Kapazitätsproblems, das das Interface nicht ausdrücken kann.

Das ist ein akzeptiertes Risiko für den Prototyp. Für eine Produktivstufe wäre ein `capabilities`-Attribut am Interface sinnvoll.

---

## 4. AKZEPTABEL: Python als Sprache

Python ist die vernünftigste Wahl für LLM-Integration, Pydantic-Modelle, anthropic SDK und structlog. Keine Alternative bietet im KI-Kontext vergleichbare Ökosystem-Abdeckung.

**Bekannte Last:** Python ist kein natürlicher Freund für hochperformante Single-Threaded-Event-Loops. Chainlit verwendet asyncio intern — ein blockierender Orchestrator-Schritt (z.B. synchrones File-I/O im Hot Path) kann die gesamte Anwendung einfrieren. Die Performance-NFRs des SDD (Orchestrator-Zykluszeit ohne LLM < 500ms) sind bei korrekter async-Implementierung erreichbar, aber `async` muss konsequent durchgehalten werden.

---

## 5. AKZEPTABEL: Systemprompts als Markdown-Dateien

Markdown-Dateien im `prompts/`-Verzeichnis sind lesbar, editierbar und gut versionierbar. Die Entscheidung ist für den Prototyp richtig.

**Bekannte Last, die nicht adressiert wurde:** Das HLA beschreibt keine Prompt-Versionierungsstrategie. Wenn während eines laufenden Projekts ein Prompt geändert wird, arbeiten Turns 1–N mit Prompt-Version A und Turns N+1–M mit Prompt-Version B. Der Modus hat im Verlauf inkonsistente Instruktionen erhalten. Beim Wiederladen eines Projekts ist nicht klar, mit welchem Prompt der nächste Turn starten soll.

Mitigation (einfach): Projektzustand enthält `prompt_version: str` pro Modus. Bei Prompt-Änderung wird die Versionsnummer erhöht; beim Laden wird gegen die gespeicherte Version geprüft und der Nutzer ggf. informiert.

---

## 6. KONTROVERS: Chainlit als UI-Framework

### Die Entscheidung im HLA

Chainlit wird als Anwendungs-Framework gewählt, weil es nativ Chat-Streams, Datei-Upload, Actions und Custom Elements bietet. Die SDD-Anforderung "Frontend-Backend-Trennung" wird als "auf Modul-Ebene erfüllt" erklärt.

### Schwäche 1: Layout-Kontrolle

Chainlit ist chat-first. Das SDD verlangt ein echtes Dual-Pane-Layout: Chat links, Artefakt-Panel rechts — dauerhaft sichtbar, live-updatend, mit visuellem Zustand (Invalidierungsmarkierungen, Completeness-Badges, Debug-Panel).

Chainlit erreicht das über `cl.CustomElement` (benutzerdefinierte React-Komponenten) oder `cl.Text`-Elemente. Beide Ansätze haben Grenzen:
- `cl.Text`-Elemente erscheinen in der Nachrichtenliste — sie sind nicht "permanent rechts"
- `cl.CustomElement` erfordert das Schreiben einer eigenen React-Komponente in JavaScript, die in die Chainlit-App eingebettet wird

Das bedeutet: der "wir vermeiden React" Vorteil von Chainlit gilt nicht mehr für das Artefakt-Panel. Wir schreiben trotzdem JavaScript/React, nur in einer weniger komfortablen Umgebung (eingebettet in Chainlit statt als eigenständige App). Der Gesamtaufwand ist höher als bei einer sauberen FastAPI + React Lösung.

### Schwäche 2: Die "Modul-Ebene"-Separierung ist eine Fata Morgana

Das SDD definiert "Frontend-Backend-Trennung" als Architektur-Constraint: "Das Frontend hat keinen direkten Zugriff auf LLMs oder Persistenz." In einem Chainlit-Monolithen laufen UI-Callbacks und Orchestrator-Logik im selben Python-Prozess. Technisch ist das genau das Gegenteil von Trennung.

Der entscheidende praktische Effekt: Eine spätere Extraktion des Backends zu einem eigenständigen Service erfordert nicht "kein Umbau", sondern einen vollständigen Schnitt — Chainlit-Callbacks werden zu HTTP/WebSocket-Clients, die API-Calls machen. Das ist nicht inkrementell erweiterbar.

### Schwäche 3: Chainlit-Kopplung im UI-Event-Handler

Jeder Button (Panik, Download, Recorder) ist ein `cl.Action`-Callback. Jede UI-Interaktion verwendet `cl.context`, `cl.user_session`, `cl.Message`. Diese sind Chainlit-spezifisch. Wenn Chainlit ausgetauscht werden soll, sind nicht nur die Template-Dateien zu ändern — jeder Event-Handler muss neu geschrieben werden.

### Alternative A: FastAPI (WebSocket) + React SPA

```
Backend: FastAPI
  - POST /api/turns         → Orchestrator.process_turn()
  - WebSocket /ws/session   → Streaming + Live-Updates
  - GET /api/projects       → Projektliste
  - GET /api/artifacts/{id} → Artefakt-Zustand

Frontend: React/Vite (TypeScript)
  - ChatPane.tsx            → Chat-Stream via WebSocket
  - ArtifactPane.tsx        → Live-Artefakt-Panel
  - DebugPanel.tsx          → Working-Memory-Anzeige
```

**Mitigiert:** Layout-Kontrolle ist vollständig. Echter Frontend-Backend-Split. Kein JavaScript im Python-Prozess.

**Auswirkung auf Komplexität:** Höher. Zwei Deployment-Einheiten. TypeScript-Toolchain (Vite, npm). Zwei Sprachen im Projekt.

**Auswirkung auf Stabilität:** Höher. FastAPI ist stabiler und besser testbar als Chainlit. React-Komponenten sind isoliert unit-testbar.

**Auswirkung auf Wartbarkeit:** Besser. Klare Schichtentrennung. Frontend- und Backend-Entwickler können unabhängig arbeiten. Kein Framework-Coupling im Kern.

### Alternative B: FastAPI + Jinja2-Templates + HTMX

```
Backend: FastAPI mit Jinja2
Frontend: HTML + HTMX (serverseitige Updates)
```

Deutlich einfacher als React. HTMX ermöglicht live-Updates via Server-Sent Events. Kein Build-Toolchain. Layout-Kontrolle durch reines HTML/CSS.

**Mitigiert:** Echter Backend-Separation. Keine TypeScript-Komplexität.

**Auswirkung auf Komplexität:** Leicht höher als Chainlit, deutlich geringer als React.

**Auswirkung auf Stabilität:** Gut. HTMX ist minimalistisch und gut verstanden.

**Auswirkung auf Wartbarkeit:** Gut für Entwickler mit HTML/CSS-Kenntnissen. Weniger verbreitet als React in Frontend-Teams.

### Empfehlung

Chainlit ist die schnellste Lösung für einen ersten Funktionsnachweis, bei dem nur der Kern (Orchestrator, Modi, Artefakte) evaluiert werden soll. Wenn die UI über ein Chat-Fenster und expandierbare Textblöcke hinausgehen soll — und das SDD-Artefakt-Panel tut das — wird Chainlit zur Last.

**Urteil:** Chainlit ist für den ersten Sprint akzeptabel. Die Architektur muss ab Tag 1 so strukturiert sein, dass Chainlit ohne Änderung am Orchestrator oder den Modi ersetzt werden kann. Das ist im HLA unzureichend spezifiziert.

---

## 7. KONTROVERS: Monolith vs. echter Frontend-Backend-Split

### Die Entscheidung im HLA

Das HLA erklärt die SDD-Anforderung "Frontend-Backend-Trennung" als auf Modul-Ebene erfüllt und verspricht, sie sei "leicht in einen Prozess-Split überführbar".

### Schwäche

Das ist eine optimistische Einschätzung. Der konkrete Migrationspfad (Chainlit → FastAPI + Client) ist kein inkrementeller Schritt, sondern ein struktureller Umbau. Wenn `app.py` direkt den Orchestrator instanziiert und direkt in `cl.user_session` schreibt, ist das Coupling tief — nicht flach.

Die Erfahrung zeigt: "Das machen wir später sauber" im Prototyp wird regelmäßig nie gemacht. Der Prototyp wird zum Produkt.

### Alternative: Sauberer Schnitt von Anfang an

Die Grenze zwischen UI und Backend ist eine einfache Schnittstelle:

```python
# backend/api.py (FastAPI)
@app.post("/turn")
async def process_turn(request: TurnRequest) -> TurnResponse:
    return await orchestrator.process_turn(request)
```

Das ist eine Woche Mehraufwand. Im Gegenzug:
- Der Orchestrator ist nie an Chainlit gekoppelt
- `TurnRequest` und `TurnResponse` sind Pydantic-Modelle — testbar ohne UI
- Die UI kann jederzeit ausgetauscht werden ohne Regressionsgefahr

**Auswirkung auf Komplexität:** Minimal höher (eine API-Schicht, HTTP-Client im UI).

**Auswirkung auf Stabilität:** Deutlich besser. Zwei isolierte Prozesse mit klaren Crash-Boundaries. Ein UI-Fehler bringt den Orchestrator nicht zum Absturz.

**Auswirkung auf Wartbarkeit:** Deutlich besser. Die SDD-Anforderung ist ehrlich erfüllt.

---

## 8. KONTROVERS: JSON-Dateien — Atomaritätsproblem bei Multi-File-Writes

### Die Entscheidung im HLA

Das HLA beschreibt JSON-Dateien mit `os.replace()` als atomare Persistenztechnik. Das ist korrekt für einzelne Dateien.

### Die fundamentale Schwäche

Das SDD fordert atomare Speicherung des vollständigen Projektzustands (FR-E-01): "entweder wird der vollständige Projektzustand gespeichert oder gar nichts — kein partieller Zustand darf entstehen."

Ein Projektzustand nach einem Turn umfasst minimal:
```
metadata.json             ← zuletzt_geaendert aktualisiert
working_memory.json       ← Completeness-State, Phasenstatus
artifacts/structure/v0005.json   ← neue Artefaktversion
dialog_history.jsonl      ← neuer Turn angehängt
```

`os.replace()` ist atomar pro Datei. Es gibt keine systemseitige Möglichkeit, vier Datei-Writes atomar zu machen. Ein Prozess-Kill zwischen Write 2 und Write 3 hinterlässt:
- `working_memory.json` mit neuem Stand
- `artifacts/structure/v0005.json` noch nicht existierend

Der Projektzustand ist inkonsistent. Das verletzt die explizite Anforderung des SDD.

Das HLA hat dieses Problem nicht adressiert. Es schreibt "Atomare Schreibvorgänge via os.replace()" — das ist für die einzelne Datei richtig, für das Multi-File-Problem falsch.

### Alternative A: SQLite (empfohlen)

SQLite ist in Python's Stdlib (`sqlite3`), braucht keine Installation, ist eine einzelne Datei, und bietet echte ACID-Transaktionen:

```sql
BEGIN TRANSACTION;
  UPDATE projects SET zuletzt_geaendert = ? WHERE projekt_id = ?;
  INSERT INTO artifact_versions (projekt_id, typ, version_id, inhalt) VALUES (?, ?, ?, ?);
  UPDATE working_memory SET inhalt = ? WHERE projekt_id = ?;
  INSERT INTO dialog_history (projekt_id, turn_id, inhalt) VALUES (?, ?, ?);
COMMIT;
-- Crash hier → vollständiger Rollback
```

Ein Crash mitten in der Transaktion hinterlässt exakt den Zustand vor dem BEGIN. Das ist echte Atomarität auf Multi-Entity-Ebene.

**Mitigiert:** Multi-File-Atomaritätsproblem vollständig.

**Auswirkung auf Komplexität:** Geringer als JSON-Files (kein Verzeichnis-Management, keine Pfad-Konstruktion, keine Version-File-Benennung). Queries statt Datei-Parsing.

**Auswirkung auf Stabilität:** Deutlich besser. SQLite's WAL-Mode ist erprobt und robust. Keine Atomaritäts-Lücken.

**Auswirkung auf Wartbarkeit:** Besser. Schema ist explizit (CREATE TABLE), nicht implizit (Verzeichnisstruktur). Migration zwischen Schemas ist via ALTER TABLE handhabbar.

**Nachteil:** Artefakte sind nicht mehr direkt mit einem Texteditor lesbar (JSON im TEXT-Feld statt separate Dateien). Für den Entwickler-Workflow ist das ein spürbarer Verlust. Mitigation: Export-Script, das ein Projekt als JSON-Dateien exportiert.

### Alternative B: Write-Ahead-Log-Muster (WAL-JSON)

Statt Multi-File-Writes: Schreibe den vollständigen Projektzustand als atomaren Single-File-Snapshot:

```
data/projects/{id}/
  snapshots/
    snap_0001.json    ← vollständiger Projektzustand
    snap_0002.json
  current             ← Textdatei mit "snap_0002" (atomar via os.replace)
```

Beim Laden: Lese `current`, lade den entsprechenden Snapshot.

**Mitigiert:** Atomarität durch Single-File-Write.

**Nachteil:** Snapshot-Dateien sind groß (vollständiger Zustand inkl. aller Artefaktversionen). Bei einem Prozess mit 60 Schritten und 200 Turns können Snapshots schnell mehrere MB pro Datei werden.

### Empfehlung

SQLite ist die richtige Wahl. Der Komplexitäts-Overhead ist minimal (sqlite3 ist Stdlib), der Stabilitätsgewinn ist materiell. Die Entscheidung für JSON-Dateien im HLA unterschätzt das Multi-File-Atomaritätsproblem.

---

## 9. KONTROVERS: Listen statt Dicts für Artefakt-Slots — RFC 6902 Pfadstabilität

### Die Entscheidung im HLA

Das HLA definiert Pydantic-Modelle mit Listen:

```python
Strukturartefakt:
  schritte: list[Strukturschritt]

Algorithmusartefakt:
  abschnitte: list[Algorithmusabschnitt]
```

### Die fundamentale Schwäche

RFC 6902 adressiert Listen-Elemente über numerische Indizes: `/schritte/2/beschreibung`. Das SDD fordert "stabile Pfade" für Schreiboperationen.

Numerische Listen-Indizes sind **nicht stabil** wenn die Liste mutiert wird. Beispiel:

```
Zustand nach Turn 5:
  schritte: [step_A, step_B, step_C]
  Pfad /schritte/2 → step_C

Turn 6: LLM fügt step_X zwischen step_A und step_B ein:
  PATCH: {"op": "add", "path": "/schritte/1", "value": step_X}

Zustand nach Turn 6:
  schritte: [step_A, step_X, step_B, step_C]
  Pfad /schritte/2 → step_B  ← war vorher step_C!
```

Wenn das LLM in Turn 7 `/schritte/2/beschreibung` schreibt, schreibt es in `step_B`, nicht in `step_C`. Das ist ein silenter Datenfehler. Der Preservation-Check im Executor (prüft "nur adressierte Pfade geändert") hilft hier nicht, weil die Operation syntaktisch korrekt ist — sie trifft nur den falschen Slot.

Das SDD schreibt explizit: "Slots werden über stabile Pfade adressiert" und nennt als Beispiel `/trigger_conditions`, `/steps/2`. Der Widerspruch zwischen "stabile Pfade" und numerischen List-Indizes ist im SDD angelegt, wurde aber im HLA übernommen ohne das Problem zu adressieren.

### Alternative: Dict-Keyed Artefakt-Slots (empfohlen)

```python
Strukturartefakt:
  schritte: dict[str, Strukturschritt]  # key = schritt_id

Algorithmusartefakt:
  abschnitte: dict[str, Algorithmusabschnitt]  # key = abschnitt_id
```

RFC 6902 Pfade werden zu:
```
/schritte/step_003/beschreibung    ← stabil, unabhängig von Reihenfolge
/abschnitte/algo_007/aktionen      ← stabil
```

Diese Pfade sind stabil durch Einfügen, Löschen und Umsortieren. Das LLM kann Schritt-IDs aus dem Read-Only-Kontext lesen und für Patches wiederverwenden — eine robustere Grundlage.

Die Reihenfolge der Schritte wird durch das `reihenfolge`-Feld im Strukturschritt codiert (wie im SDD definiert), nicht durch die Listenposition.

**Mitigiert:** RFC 6902 Pfadinstabilität vollständig.

**Auswirkung auf Komplexität:** Gering. Pydantic-Modell-Änderung (list → dict). JSON-Serialisierung bleibt identisch. Template-Schema-Pfade ändern sich.

**Auswirkung auf Stabilität:** Deutlich besser. Silente Schreibfehler auf falsche Slots sind strukturell ausgeschlossen.

**Auswirkung auf Wartbarkeit:** Besser. Patches sind im Log mit `schritt_id` lesbar statt mit numerischem Index, der ohne Artefakt-Kontext nicht interpretierbar ist.

**Nachteil:** Artefakt-Serialisierung als JSON gibt ein Objekt (Dict) statt eines Arrays zurück. Rendering-Logik muss nach `reihenfolge`-Feld sortieren statt Listenreihenfolge verwenden. Das ist geringer Mehraufwand.

---

## 10. KONTROVERS: LLM Structured Output — nicht adressiert

### Das Problem

Das HLA definiert einen `OutputValidator`, der den LLM-Output gegen den Output-Kontrakt prüft. Der Output-Kontrakt (SDD 6.5.2) fordert:
1. Eine Nutzeräußerung (Freitext)
2. Null oder mehr RFC 6902 Patches (strukturiertes JSON)
3. Steuerungsoutput: Phasenstatus + Flags (strukturiertes JSON)

Das HLA beschreibt nicht, wie diese strukturierte Ausgabe technisch erzwungen wird. Das ist keine Detail-Entscheidung — es ist eine der kritischsten Designfragen im gesamten System.

### Das Spektrum der Optionen

**Option A: System-Prompt-Instruktionen (nur Format-Vorgabe)**

Das LLM wird im Systemprompt instruiert, immer im definierten JSON-Format zu antworten. Keine technische Erzwingung.

- Vorteil: Einfach
- Nachteil: Unzuverlässig. LLMs weichen vom Format ab — besonders wenn der Input komplex ist, der Kontext lang ist, oder das Modell klein ist. Der OutputValidator wird bei jeder Abweichung einen Fehler produzieren. Bei einem lokalen 7B-Modell kann das in 20–30% der Turns passieren.
- Konsequenz: Häufige Output-Kontrakt-Verletzungen, schlechte Nutzererfahrung.

**Option B: Anthropic Tool Use / Structured Output API**

Anthropic's API ermöglicht es, ein JSON-Schema als "Tool" zu definieren, das das Modell aufrufen muss. Das erzwingt strukturierte Ausgabe technisch, nicht nur konventionell.

```python
tools = [{
    "name": "modus_output",
    "input_schema": {
        "type": "object",
        "properties": {
            "nutzeraeusserung": {"type": "string"},
            "patches": {"type": "array", ...},
            "phasenstatus": {"type": "string", "enum": [...]},
            "flags": {"type": "array", ...}
        },
        "required": ["nutzeraeusserung", "phasenstatus"]
    }
}]
```

Das Modell muss dieses Tool aufrufen. Der `nutzeraeusserung`-Text wird dabei als Freitext-Parameter übergeben.

- Vorteil: Strukturierte Ausgabe ist technisch garantiert, nicht konventionell.
- Nachteil: Koppelt den Output-Kontrakt an Anthropic's Tool-Use-API-Format. Bei Modellwechsel (z.B. zu Ollama) muss der Mechanismus angepasst werden — die abstrakte LLM-Schnittstelle muss Tool-Use unterstützen.
- Konsequenz: Das `LLMClient`-Interface braucht eine `complete_with_tools()`-Methode zusätzlich zu `complete()`.

**Option C: Instructor-Bibliothek**

`instructor` (Python) wraps jeden LLM-Client und erzwingt Pydantic-Modell-Ausgabe via Retry-Schleife. Bei Abweichung vom Schema: automatischer Retry mit Fehlermeldung im Prompt.

```python
client = instructor.from_anthropic(anthropic.Anthropic())
output = client.chat.completions.create(
    model="claude-opus-4-6",
    response_model=ModeOutput,  # Pydantic-Modell
    messages=[...]
)
```

- Vorteil: Universell (funktioniert mit Anthropic, OpenAI, Ollama-kompatiblen Endpunkten). Kein API-spezifisches Tool-Use-Format. Retry ist eingebaut.
- Nachteil: Zusätzliche Abhängigkeit. Retry bedeutet zusätzliche LLM-Aufrufe und Latenz. Die abstrakte LLM-Schnittstelle im HLA würde durch `instructor` ersetzt oder umhüllt.
- Konsequenz: Mittlere Komplexitätserhöhung, aber die zuverlässigste Lösung quer über Modelle.

### Bewertung

Option A ist nicht produktionsreif. Das HLA hätte klar benennen müssen, dass der OutputValidator nur die letzte Verteidigungslinie ist — und dass er ohne technische Erzwingung häufig ausgelöst wird.

Option B (Tool Use) ist für Anthropic-Modelle die robusteste Lösung und sollte als primärer Mechanismus gewählt werden. Option C (Instructor) ist der Fallback für Ollama.

**Auswirkung auf Komplexität:** Moderat. Das `LLMClient`-Interface wird um `complete_structured()` erweitert. `ModeOutput` als Pydantic-Modell wird definiert.

**Auswirkung auf Stabilität:** Erheblich besser. Output-Kontrakt-Verletzungen sind strukturell selten statt häufig.

**Auswirkung auf Wartbarkeit:** Neutral. Der Mechanismus ist in der LLM-Schicht gekapselt — Modi sehen nur `ModeOutput`.

---

## 11. AKZEPTABEL: Template-Schema als abgeleitete Pydantic-Ausgabe

### Das Problem

Das HLA sagt: "Template-Schema wird programmatisch aus den Pydantic-Modellen abgeleitet." Das ist richtig als technische Beschreibung, aber es fehlt eine entscheidende Aussage: **in welchem Format wird das Schema dem LLM übergeben?**

`model_json_schema()` gibt ein JSON Schema (Draft 7) zurück — ein komplexes, verschachteltes Objekt mit `$defs`, `anyOf`, Referenz-Auflösung. Das ist für maschinelle Validierung gut, aber für LLM-Instruktionen suboptimal.

Ein LLM versteht "Du darfst diese Pfade beschreiben: `/schritte/{schritt_id}/beschreibung`, `/schritte/{schritt_id}/completeness_status`..." besser als ein JSON-Schema-Dokument mit `$ref`-Auflösung.

**Mitigation (vertretbar für Prototyp):** Das Pydantic-JSON-Schema wird generiert und in den Kontext injiziert. Wenn das LLM damit gut umgeht, ist kein Problem. Wenn nicht, wird das Schema in ein menschenlesbares Template überführt (eine einmalige manuelle Transformation). Dieser Schritt ist nicht aufwändig, muss aber als explizite Aufgabe eingeplant werden.

---

## Zusammenfassung: Entscheidungsmatrix

| Entscheidung | Bewertung | Hauptrisiko | Empfehlung |
|---|---|---|---|
| RFC 6902 JSON Patch | **GUT** | `jsonpatch` unmaintained | behalten |
| Pydantic v2 Datenmodelle | **GUT** | — | behalten |
| Abstrakte LLM-Schnittstelle | **GUT** | Fähigkeitsunterschiede unsichtbar | behalten, ggf. `capabilities`-Attribut |
| Python als Sprache | **AKZEPTABEL** | async-Disziplin nötig | behalten |
| Systemprompts als Markdown | **AKZEPTABEL** | keine Prompt-Versionierung | Prompt-Version ins Projektzustand aufnehmen |
| Chainlit als UI-Framework | **KONTROVERS** | Layout-Grenzen, Kopplung | FastAPI + HTMX oder FastAPI + React |
| Monolith (kein Prozess-Split) | **KONTROVERS** | SDD-Constraint nominell erfüllt | saubere API-Schnittstelle ab Tag 1 |
| JSON-Dateien Multi-File-Atomic | **KONTROVERS** | kein atomares Multi-File-Write | SQLite ersetzen |
| Listen statt Dicts für Slots | **KONTROVERS** | RFC 6902 Pfadinstabilität | `dict[slot_id, Slot]` verwenden |
| Structured Output nicht adressiert | **KONTROVERS** | häufige Output-Kontrakt-Verletzungen | Tool Use (Anthropic) + Instructor (Ollama) |
| Template-Schema-Format für LLM | **AKZEPTABEL** | JSON Schema ≠ LLM-optimiertes Format | menschenlesbares Schema-Format als Fallback |

---

## Priorisierung der Korrekturen

Nicht alle kontroversen Entscheidungen haben das gleiche Korrekturgewicht. Vorgeschlagene Reihenfolge:

**Korrekturen vor Implementierungsstart (Blocker):**
1. **Listen → Dicts für Artefakt-Slots** — Schemaänderung jetzt ist billig, später teuer
2. **Structured Output Strategie definieren** — beeinflusst LLM-Client-Interface-Design ab Schritt 4
3. **SQLite statt JSON-Files** — Persistenz-Layer-Änderung in Schritt 1, später strukturell teuer

**Korrekturen akzeptabel im ersten Sprint, aber mit Deadline:**
4. **Saubere API-Grenze (FastAPI)** — akzeptabel in Sprint 1 als Monolith, muss in Sprint 2 extrahiert sein bevor weitere UI-Komplexität entsteht

**Deferred (post-Prototyp):**
5. **Chainlit → React** — wenn Prototyp-Evaluation zeigt, dass UI-Anforderungen mit Chainlit nicht erfüllbar sind
6. **Prompt-Versionierung** — vor erster Nutzerstudie

---

*Ende der adversarialen Analyse.*
