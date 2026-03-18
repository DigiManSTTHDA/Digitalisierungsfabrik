# Test5 — Implementierungsplan (v2)

**Grundlage:** [test5-bug-analysis.md](./test5-bug-analysis.md)
**Research-Grundlage:** 5 Subagenten (Auto-Moderator-Turn, Structuring-Prompt/Patch-Bestätigung, spannungsfelder/Schema, Architektur-Analyse, Codebase-Exploration)
**Datum:** 2026-03-18 — v2: Überarbeitung nach Effektivitäts- und Effizienzprüfung

---

## Übersicht

| Sprint | Bugs | Scope | Aufwand |
|--------|------|-------|---------|
| **Sprint 1** | B1, B2, B3 | Systemfehler + UX-Blocker | Klein–Mittel |
| **Sprint 2** | B4–B10 | Artefakt-Integrität + Agent-Qualität | Mittel |
| **Sprint 3** | B11 | Explorations-Tiefe | Klein |

---

## Sprint 1 — Systemfehler und UX-Blocker

### S1-T1: Retry-Logik für ungültige Patch-Pfade (B1)

**Problem:** `infer_artifact_type(patches)` gibt `None` zurück wenn das LLM ungültige Pfade halluziniert → User sieht `"Ein interner Fehler bei der Datenverarbeitung."` ohne Retry-Möglichkeit.

**Lösung:** Automatischer Retry im Orchestrator (max. 2×), ohne User-Intervention. **Wichtig:** Jeder Retry-Call muss einen Fehler-Hint im Context mitführen — ohne Hint produziert das LLM bei niedrigen Temperaturen deterministisch denselben Fehler.

**Datei:** `backend/core/orchestrator.py`

```python
# Schritt 7: Patches anwenden (wenn vorhanden) — mit Retry
MAX_PATCH_RETRIES = 2
PATCH_RETRY_HINT = (
    "ACHTUNG: Der letzte Aufruf produzierte Patches mit ungültigen Pfaden. "
    "Verwende AUSSCHLIESSLICH Pfade mit diesen Präfixen: "
    "/schritte/{sid}/..., /slots/{slot_id}/..., /abschnitte/{aid}/... "
    "Numerische Indizes wie /schritte/0/ sind ungültig."
)

if mode_output.patches:
    artifact_type = infer_artifact_type(mode_output.patches)

    if artifact_type is None:
        for attempt in range(MAX_PATCH_RETRIES):
            log.warning("orchestrator.patch_retry", attempt=attempt + 1)
            retry_context = context.with_error_hint(
                f"Versuch {attempt + 1}: {PATCH_RETRY_HINT}"
            )
            mode_output = await mode.call(retry_context)
            if not validate(mode_output, context.artifact_template):
                continue
            artifact_type = infer_artifact_type(mode_output.patches)
            if artifact_type is not None:
                break

        if artifact_type is None:
            return self._error_output(
                wm,
                "Ein interner Fehler ist aufgetreten. Bitte erneut versuchen.",
                internal="Patch-Pfade konnten keinem Artefakttyp zugeordnet werden (nach Retries)",
            )
```

**Context API:** `context.with_error_hint(hint: str)` muss existieren oder ergänzt werden. Minimale Implementierung: `dataclasses.replace(context, error_hint=hint)` mit einem optionalen `error_hint: str | None = None`-Feld im Context-Objekt. Der jeweilige Mode injiziert diesen Hint analog zu `_build_first_turn_directive()` in `structuring.py` als zusätzliche System-Direktive in den Prompt-Kontext.

**Ergänzend (Structuring-Prompt):** Explizite Regel hinzufügen, dass beim Signalisieren von `phase_complete` **keine Patches** produziert werden sollen. Diese Regel kommt **an den Anfang des Prompts**, direkt nach der Rollenbeschreibung — nicht am Ende:

```markdown
<!-- In prompts/structuring.md — nach Rollenbeschreibung, VOR den Konsistenzregeln -->
## Abschluss der Strukturierungsphase

Wenn der Nutzer die Strukturierung bestätigt und du `phasenstatus: "phase_complete"` meldest:
- Sende KEINE Patches mehr in diesem Turn
- `patches` muss eine leere Liste `[]` sein
- Schreibe eine kurze Abschluss-Bestätigung in `nutzeraeusserung`
```

**Tests:**
- Bestehenden Test `test_orchestrator.py::test_invalid_patch_paths_returns_error` anpassen — er soll prüfen, dass nach maximal 2 Retries der Fehler kommt, nicht sofort.
- Neuer Test `test_patch_retry_with_error_hint` — prüft, dass jeder Retry-Call `error_hint` im Context enthält.

---

### S1-T2: Proaktiver Moderator-Turn nach Phasenwechsel (B2, B3)

**Problem:** Nach `phase_complete` wechselt der Orchestrator zu `aktiver_modus: "moderator"`, aber der Moderator sendet keine Nachricht — er wartet auf den nächsten User-Input. User hängt ohne Orientierung.

**Architektur-Entscheidung: Option A (Server-Push).**
Die ursprünglich geplante "Option D" (leerer Text erlauben in websocket.py) ist unvollständig: Sie erlaubt den Empfang leerer Texte, aber definiert nirgends *wer* diesen Text schickt. Client-seitige Trigger (Option B) weichen die Payload-Validierung auf, introduzieren Race Conditions durch Netzwerklatenz und erfordern Frontend-Logik außerhalb des Scope.

Option A löst das Problem vollständig server-seitig in ~15 Zeilen: Nach dem regulären `process_turn`-Call, der `phase_complete` trägt, wird sofort ein zweiter interner Turn für den Moderator mit einem synthetischen Trigger-Text ausgelöst.

#### Schritt 1: `prompts/moderator.md` erweitern

Neue Sektion hinzufügen:

```markdown
## Verhalten bei Phasenwechsel (Proaktive Einleitung)

Wenn du mit dem Text "[Moderator-Einleitung nach Phasenwechsel]" aktiviert wirst:
Du wurdest automatisch nach Abschluss einer Phase aktiviert.
**Schreibe IMMER eine proaktive Einleitungsnachricht.**

Struktur der Nachricht:
1. Kurze Bestätigung: Was in der abgeschlossenen Phase erreicht wurde (1 Satz)
2. Vorschau: Was die nächste Phase bedeutet und was dort passiert (2–3 Sätze)
3. Aufforderung: "Möchten Sie mit der [Phasenname]-Phase fortfahren?"

Setze `uebergabe: false` — der Nutzer muss explizit zustimmen, bevor du übergibst.

Beispiel (nach Exploration → Strukturierung):
"Die Explorationsphase ist abgeschlossen — wir haben Ihren Prozess vollständig
erfasst. In der Strukturierungsphase ordnen wir die gesammelten Informationen
und entwickeln eine klare Schritt-für-Schritt-Übersicht.
Möchten Sie mit der Strukturierung fortfahren?"
```

#### Schritt 2: `api/websocket.py` — Auto-Moderator-Call nach phase_complete

Statt der geplanten "leerer-Text-erlauben"-Änderung: Nach dem regulären `process_turn`-Call beide Outputs sequenziell senden — erst den abschließenden Modus-Output, dann sofort den Moderator-Greeting:

```python
# Nach dem bisherigen process_turn-Call (ca. Z. 209):
output = await orchestrator.process_turn(project_id, turn_input)

# Erst den abschließenden Mode-Output senden (z.B. Exploration-Abschluss)
await _send_turn_events(ws, output, repo, project_id)

# Dann sofort Moderator-Greeting nachschieben
if Flag.phase_complete.value in output.flags and output.working_memory.aktiver_modus == "moderator":
    log.info("websocket.moderator_auto_greeting", trigger="phase_complete")
    moderator_output = await orchestrator.process_turn(
        project_id,
        TurnInput(text="[Moderator-Einleitung nach Phasenwechsel]")
    )
    await _send_turn_events(ws, moderator_output, repo, project_id)
```

**Import ergänzen** (falls noch nicht vorhanden):
```python
from modes.base import Flag
```

#### Schritt 3: Orchestrator — kein Änderungsbedarf

Der synthetische `TurnInput` durchläuft den normalen 11-Schritt-Zyklus. Der Moderator erhält `"[Moderator-Einleitung nach Phasenwechsel]"` als User-Text und reagiert laut Prompt-Regel mit der proaktiven Einleitungsnachricht. Der Marker (eckige Klammern) ist in der Dialog-Historie als interner Trigger erkennbar und filterbar.

**Tests:**
- `test_moderator.py`: Neuer Test `test_moderator_writes_intro_on_phase_complete_trigger` — prüft, dass bei Text `"[Moderator-Einleitung nach Phasenwechsel]"` die `nutzeraeusserung` nicht leer ist und die nächste Phase nennt.
- `test_websocket.py`: Neuer Test `test_auto_moderator_call_after_phase_complete` — prüft, dass nach einem Turn mit `Flag.phase_complete` zwei WebSocket-Events gesendet werden.

---

## Sprint 2 — Artefakt-Integrität und Agent-Qualität

### S2-T1: Structuring-Prompt — Patch-Beispiele (B4, B5, B6, B7, B8, B9)

**Problem:** Der Structuring-Prompt enthält nur 3 rudimentäre Patch-Beispiele ohne vollständige `value`-Objekte. Fehlende Beispiele führen dazu, dass das LLM `remove`-Patches, Schritt-Einfügungen, Spannungsfelder und Ausnahmen nicht korrekt produziert.

**Datei:** `backend/prompts/structuring.md`

**Positionierung:** Die 6 Beispiele werden **am Ende des Prompts** eingefügt — nach allen Regeln und Konsistenzanforderungen. Kritische Regeln (Pfad-Konventionen, phase_complete-Regel) bleiben am Anfang des Prompts und werden zuverlässiger befolgt (Lost-in-the-Middle-Effekt bei langen Prompts).

**IDs in den Beispielen:** Alle Beispiele verwenden abstrakte Platzhalter (`sX`, `sY`, `sZ`), keine prozessspezifischen IDs. Das LLM soll die Struktur lernen, nicht konkrete Bezeichner aus dem test5-Prozess übernehmen.

Folgende 6 Beispiele ergänzen (vollständig ausformuliert, nicht nur Syntax):

#### Beispiel A: Neuen Schritt einfügen (mit Vorgänger-Update)

```markdown
### Schritt einfügen

Wenn du einen neuen Schritt zwischen sX und sY einfügst:
- Vergib eine neue ID (z.B. `sX_neu` oder den nächsten freien Key)
- Aktualisiere IMMER die `nachfolger`-Liste des Vorgängers

\`\`\`json
[
  {"op": "add", "path": "/schritte/sX_neu", "value": {
    "schritt_id": "sX_neu",
    "titel": "Titel des neuen Schritts",
    "typ": "entscheidung",
    "beschreibung": "Beschreibung des Schritts",
    "reihenfolge": 3,
    "nachfolger": ["sY"],
    "bedingung": "Entscheidungsfrage?",
    "ausnahme_beschreibung": null,
    "algorithmus_ref": [],
    "completeness_status": "vollstaendig",
    "algorithmus_status": "ausstehend",
    "spannungsfeld": null
  }},
  {"op": "replace", "path": "/schritte/sX/nachfolger", "value": ["sX_neu"]}
]
\`\`\`
```

#### Beispiel B: Schritt entfernen / Duplikat mergen

```markdown
### Schritt entfernen (merge)

Wenn du sY löschst und sX direkt auf sZ zeigen soll:

\`\`\`json
[
  {"op": "replace", "path": "/schritte/sX/nachfolger", "value": ["sZ"]},
  {"op": "remove", "path": "/schritte/sY"}
]
\`\`\`
```

#### Beispiel C: Spannungsfeld dokumentieren

```markdown
### Spannungsfeld setzen

Wenn der Nutzer ein Problem oder einen Medienbruch bei einem Schritt beschreibt:

\`\`\`json
[
  {"op": "add", "path": "/schritte/sX/spannungsfeld", "value": "Beschreibung des Problems oder Medienbruchs."}
]
\`\`\`

Hinweis: Spannungsfelder sind IMMER dann zu setzen, wenn der Nutzer ein Problem,
eine Ineffizienz oder einen Konflikt bei einem Schritt explizit benennt.
```

#### Beispiel D: Ausnahmeschritt hinzufügen

```markdown
### Ausnahmeschritt hinzufügen

Ausnahmen (`typ: "ausnahme"`) sind Sonderfälle, die den regulären Prozessfluss
vollständig umgehen (z.B. Gutschrift statt Rechnung, Storno, Direktzahlung).
Sie haben keine feste Position in der Sequenz und werden am Ende des `schritte`-Dicts angefügt.

\`\`\`json
[
  {"op": "add", "path": "/schritte/s_ausnahme", "value": {
    "schritt_id": "s_ausnahme",
    "titel": "Titel der Ausnahme",
    "typ": "ausnahme",
    "beschreibung": "Was bei dieser Ausnahme passiert",
    "reihenfolge": 99,
    "nachfolger": [],
    "bedingung": null,
    "ausnahme_beschreibung": "Wann tritt diese Ausnahme auf",
    "algorithmus_ref": [],
    "completeness_status": "vollstaendig",
    "algorithmus_status": "ausstehend",
    "spannungsfeld": null
  }}
]
\`\`\`
```

#### Beispiel E: Entscheidungsschritt — Titel UND Bedingung gemeinsam patchen

```markdown
### Entscheidungsschritt umbenennen

Wenn du Titel und Bedingung eines Entscheidungsschritts änderst,
müssen BEIDE Felder gemeinsam gepatchet werden:

\`\`\`json
[
  {"op": "replace", "path": "/schritte/sX/titel", "value": "Neuer Titel"},
  {"op": "replace", "path": "/schritte/sX/bedingung", "value": "Neue Entscheidungsfrage?"}
]
\`\`\`

Regel: Bei `typ: "entscheidung"` sind `titel` und `bedingung` immer synchron zu halten.
```

#### Beispiel F: Schritt mit zwei Ausgangspfaden (Rückkopplung)

```markdown
### Schritt mit zwei Ausgangspfaden

Für einen Entscheidungsschritt mit Normalfall (weiter) und Negativfall (z.B. zurück an Lieferanten):

WICHTIG: Der Negativfall-Schritt ist `typ: "aktion"`, KEIN `typ: "ausnahme"`.
`typ: "ausnahme"` ist für Sonderfälle die den Prozess vollständig umgehen (Gutschriften, Storno).
Ein Schritt auf dem Fehlerpfad ist Teil des regulären Ablaufs und damit `typ: "aktion"`.

\`\`\`json
[
  {"op": "add", "path": "/schritte/sX_pruefung", "value": {
    "schritt_id": "sX_pruefung",
    "titel": "Titel der Prüfung",
    "typ": "entscheidung",
    "beschreibung": "Prüfung einer Bedingung",
    "reihenfolge": 4,
    "nachfolger": ["sY_normalfall", "sZ_negativfall"],
    "bedingung": "Ist die Bedingung erfüllt?",
    "ausnahme_beschreibung": null,
    "algorithmus_ref": [],
    "completeness_status": "vollstaendig",
    "algorithmus_status": "ausstehend",
    "spannungsfeld": null
  }},
  {"op": "add", "path": "/schritte/sZ_negativfall", "value": {
    "schritt_id": "sZ_negativfall",
    "titel": "Negativfall-Aktion",
    "typ": "aktion",
    "beschreibung": "Was beim Negativfall passiert",
    "reihenfolge": 100,
    "nachfolger": [],
    "bedingung": null,
    "ausnahme_beschreibung": null,
    "algorithmus_ref": [],
    "completeness_status": "vollstaendig",
    "algorithmus_status": "ausstehend",
    "spannungsfeld": null
  }},
  {"op": "replace", "path": "/schritte/sVorgaenger/nachfolger", "value": ["sX_pruefung"]}
]
\`\`\`
```

**Tests:** Kein neuer Unit-Test nötig — der Prompt ist opak für Unit-Tests. Manuelles Testen mit einem Teststep des Typs "merge" und "add with loop" ausreichend.

---

### S2-T2: `spannungsfelder`-Aggregation (B8)

**Problem:** `wm.spannungsfelder` (list[str]) wird nie befüllt. Es werden keine `schritt.spannungsfeld`-Werte in das Working Memory hochgerechnet.

**Research-Empfehlung:** Aggregation in `progress_tracker.update_working_memory()` — dort sind alle Artefakte bereits aktuell nach Patch-Anwendung.

**Datei:** `backend/core/progress_tracker.py`

```python
# Signatur erweitern
def update_working_memory(
    wm: WorkingMemory,
    phasenstatus: Phasenstatus,
    befuellte_slots: int,
    bekannte_slots: int,
    structure_artifact=None,  # neu: StructureArtifact | None
) -> WorkingMemory:
    wm.phasenstatus = phasenstatus
    wm.befuellte_slots = befuellte_slots
    wm.bekannte_slots = bekannte_slots

    # Spannungsfelder aus allen Strukturschritten aggregieren
    if structure_artifact is not None:
        spannungsfelder = []
        for schritt in structure_artifact.schritte.values():
            if schritt.spannungsfeld and schritt.spannungsfeld.strip():
                if schritt.spannungsfeld not in spannungsfelder:  # deduplizieren
                    spannungsfelder.append(schritt.spannungsfeld)
        wm.spannungsfelder = spannungsfelder

    return wm
```

**Datei:** `backend/core/orchestrator.py` — Aufruf anpassen (Schritt 10):

```python
wm = update_working_memory(
    wm,
    mode_output.phasenstatus,
    befuellte,
    bekannte,
    project.structure_artifact,  # neu
)
```

**Tests:** Neuer Test in `backend/tests/test_progress_tracker.py`:

```python
def test_update_working_memory_aggregates_spannungsfelder():
    """Spannungsfelder aus Strukturschritten werden in WM aggregiert."""
    # Arrange: Structure-Artefakt mit zwei Schritten, einer hat spannungsfeld
    ...
    assert wm.spannungsfelder == ["Medienbruch: ELO vs. Stempel"]
```

---

### S2-T3: Deterministischer PatchSummarizer mit Titel-Lookup (B10)

**Problem:** Der Structuring-Agent generiert `nutzeraeusserung` unabhängig von den tatsächlich produzierten Patches. Er kann Änderungen bestätigen, die er nicht gepatchet hat.

**Research-Empfehlung:** Deterministischer Summarizer (Option B). Kein zweiter LLM-Call, kein Feature-Flag, niedrigster Aufwand, löst das Problem zu ~95%.

**Änderung gegenüber v1:** Der Summarizer erhält das aktuelle Struktur-Artefakt und übersetzt Schritt-IDs in lesbare Titel. Reine technische IDs (`s2a`, `s5`) im User-Text sind für nicht-technische Nutzer (Sachbearbeiter, Probanden) nicht akzeptabel.

#### Neue Datei: `backend/core/patch_summarizer.py`

```python
"""Deterministischer Patch-Summarizer für nutzeraeusserung (SDD 6.5.x).

Übersetzt ein Patch-Array in einen lesbaren deutschen Satz.
Kein LLM — reine Logik. Verhindert halluzinierte Bestätigungen.
Schritt-IDs werden anhand des Artefakts in Titel übersetzt.
"""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from artifacts.structure import StructureArtifact


def _get_titel(sid: str, structure_artifact: "StructureArtifact | None") -> str:
    """Schritt-ID → Titel aus Artefakt, Fallback auf ID."""
    if structure_artifact is None:
        return sid
    schritt = structure_artifact.schritte.get(sid)
    return schritt.titel if schritt else sid


def summarize_patches(
    patches: list[dict],
    structure_artifact: "StructureArtifact | None" = None,
) -> str:
    """Patches → lesbare deutsche Bestätigung."""
    if not patches:
        return ""

    parts = []
    for patch in patches:
        op = patch.get("op")
        path = patch.get("path", "")
        value = patch.get("value")
        segments = path.strip("/").split("/")

        if segments[0] == "schritte" and len(segments) >= 2:
            sid = segments[1]
            field = segments[2] if len(segments) > 2 else None

            if op == "add" and not field:
                titel = value.get("titel", sid) if isinstance(value, dict) else sid
                parts.append(f"'{titel}' hinzugefügt")
            elif op == "remove" and not field:
                titel = _get_titel(sid, structure_artifact)
                parts.append(f"'{titel}' entfernt")
            elif op == "replace":
                titel = _get_titel(sid, structure_artifact)
                if field == "titel":
                    parts.append(f"Titel von '{titel}' geändert")
                elif field == "beschreibung":
                    parts.append(f"Beschreibung von '{titel}' aktualisiert")
                elif field == "nachfolger":
                    parts.append(f"Reihenfolge nach '{titel}' angepasst")
                elif field == "bedingung":
                    parts.append(f"Entscheidungsfrage bei '{titel}' aktualisiert")
                elif field == "typ":
                    parts.append(f"Typ von '{titel}' geändert")
            elif op == "add" and field == "spannungsfeld":
                titel = _get_titel(sid, structure_artifact)
                parts.append(f"Problem bei '{titel}' dokumentiert")

        elif segments[0] == "prozesszusammenfassung":
            parts.append("Prozesszusammenfassung aktualisiert")

    if not parts:
        return "Änderungen vorgenommen."

    return "Ich habe folgende Änderungen vorgenommen: " + ", ".join(parts) + "."
```

**Datei:** `backend/modes/structuring.py` — Integration:

```python
from core.patch_summarizer import summarize_patches

# In call() / _build_output(), nach LLM-Response:
patches = tool_input.get("patches", [])
llm_nutzeraeusserung = tool_input.get("nutzeraeusserung", "")

# Patch-basierte Bestätigung überschreibt LLM-Bestätigung wenn Patches vorhanden
if patches:
    nutzeraeusserung = summarize_patches(patches, structure_artifact=context.structure_artifact)
else:
    nutzeraeusserung = llm_nutzeraeusserung  # Fragen/Rückfragen bleiben LLM-generiert
```

**Wichtig:** Wenn `patches` leer ist (der Agent stellt eine Rückfrage), bleibt `nutzeraeusserung` LLM-generiert — das ist korrekt, da in diesem Fall keine Patches zu bestätigen sind.

**Tests:** `backend/tests/test_patch_summarizer.py` — je ein Test pro Patch-Typ (add, remove, replace/titel, spannungsfeld), je einmal ohne Artefakt (Fallback auf ID) und einmal mit Artefakt (Titel-Lookup).

---

## Sprint 3 — Explorations-Tiefe

### S3-T1: Topic-Drift-Recovery im Explorations-Prompt (B11)

**Problem:** Wenn der User bei einer offenen Frage zum Thema driftet, akzeptiert der Exploration-Agent die Abweichung ohne Nachfassen. Dadurch fehlen später Informationen im Artefakt (hier: Manuelle Recherche ohne Bestellnummer).

**Datei:** `backend/prompts/exploration.md`

Neue Regel hinzufügen:

```markdown
## Offene Fragen zurückverfolgen

Wenn du eine explizite Frage gestellt hast und der Nutzer antwortet mit
einem anderen Thema (Topic-Drift):

1. Beantworte das neue Thema kurz (nicht ignorieren)
2. Kehre dann explizit zur offenen Frage zurück:
   "Sie hatten noch nicht beschrieben, [ursprüngliche Frage].
    Können Sie das kurz ergänzen?"

Beispiel: Du fragst "Wie wird bei Rechnungen ohne Bestellnummer vorgegangen?"
Der Nutzer antwortet über Mahnungen. Korrekte Reaktion:
"Verstanden — Mahnungen werden von Frau Müller bearbeitet.
 Zurück zur offenen Frage: Was passiert, wenn eine Rechnung ohne Bestellnummer
 eingeht? Gibt es einen festen Prozess?"
```

**Tests:** Kein Unit-Test möglich. Manueller Test mit einem Dialog, der bewusst topic-driftet.

---

## Datei-Übersicht

| Datei | Änderung | Sprint |
|-------|----------|--------|
| `backend/core/orchestrator.py` | Retry-Logik mit Fehler-Hint für `infer_artifact_type` | S1-T1 |
| `backend/prompts/structuring.md` | Regel "kein Patch bei phase_complete" (AM ANFANG des Prompts) | S1-T1 |
| `backend/api/websocket.py` | Auto-Moderator-Call nach `Flag.phase_complete` (~15 Zeilen) | S1-T2 |
| `backend/prompts/moderator.md` | Proaktive Einleitung bei `[Moderator-Einleitung nach Phasenwechsel]` | S1-T2 |
| `backend/prompts/structuring.md` | 6 Patch-Beispiele mit abstrakten IDs (AM ENDE des Prompts) | S2-T1 |
| `backend/core/progress_tracker.py` | `spannungsfelder`-Aggregation aus Structure-Artefakt | S2-T2 |
| `backend/core/orchestrator.py` | `structure_artifact` an `update_working_memory` übergeben | S2-T2 |
| `backend/core/patch_summarizer.py` | **Neue Datei** — deterministischer Summarizer mit Titel-Lookup | S2-T3 |
| `backend/modes/structuring.py` | `nutzeraeusserung` durch `summarize_patches()` ersetzen | S2-T3 |
| `backend/prompts/exploration.md` | Topic-Drift-Recovery-Regel | S3-T1 |

**Ggf. neu (falls nicht vorhanden):**

| Datei | Änderung | Sprint |
|-------|----------|--------|
| `backend/core/context.py` (o.ä.) | `with_error_hint(hint: str)` am Context-Objekt | S1-T1 |

### Neue Test-Dateien / Test-Erweiterungen

| Datei | Test | Sprint |
|-------|------|--------|
| `backend/tests/test_orchestrator.py` | `test_patch_retry_with_error_hint` | S1-T1 |
| `backend/tests/test_moderator.py` | `test_moderator_writes_intro_on_phase_complete_trigger` | S1-T2 |
| `backend/tests/test_websocket.py` | `test_auto_moderator_call_after_phase_complete` | S1-T2 |
| `backend/tests/test_progress_tracker.py` | `test_update_working_memory_aggregates_spannungsfelder` | S2-T2 |
| `backend/tests/test_patch_summarizer.py` | Tests je Patch-Typ (mit/ohne Artefakt) | S2-T3 |

---

## Optionale Erweiterung (Post-Sprint 3)

### Zwei-LLM-Call-Flow für nutzeraeusserung (B10 — erweitert)

Falls der deterministische Summarizer (S2-T3) sprachlich zu technisch klingt:

- Zweiter LLM-Call nach Patch-Anwendung, der die angewendeten Patches als Kontext erhält
- Hinter Feature-Flag `Settings.use_double_llm_for_acks = False`
- Separater leichtgewichtiger LLM-Call ohne Tools (`temperature=0.3`)
- Aktivierbar per Environment-Variable ohne Code-Änderung

**Empfehlung:** Erst nach Evaluation von S2-T3 entscheiden — wenn der Summarizer ausreicht, ist dieser Aufwand unnötig.

---

## Abhängigkeiten und Reihenfolge

```
S1-T1 (Retry + Fehler-Hint) ───────────────────────────► Context API prüfen (ggf. with_error_hint ergänzen)
S1-T2 (Moderator-Prompt + WS Server-Push) ─────────────► unabhängig

S2-T1 (Prompt-Beispiele, abstrakt, AM ENDE) ───────────► unabhängig
S2-T2 (spannungsfelder) ───────────────────────────────► unabhängig
S2-T3 (PatchSummarizer mit Titel-Lookup) ───────────────► S2-T1 empfohlen zuerst
                                                           (Beispiele verbessern LLM-Patches,
                                                           Summarizer ist dann konsistenter)

S3-T1 (Exploration) ───────────────────────────────────► unabhängig
```

Alle Tasks innerhalb eines Sprints können parallel bearbeitet werden.
