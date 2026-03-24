# CR-009: Init-Rewrite — Single-Call-Architektur mit aufgewertetem Coverage-Validator

| Feld | Wert |
|---|---|
| **ID** | CR-009 |
| **Titel** | Init-Rewrite — Single-Call-Architektur mit aufgewertetem Coverage-Validator |
| **Status** | Verifiziert |
| **Erstellt** | 2026-03-24 |
| **Priorität** | Kritisch |
| **Auslöser** | Analyse der bestehenden Init-Implementierung (CR-006): Init-Prompts haben keinen ausreichenden Kontext, Multi-Turn-Loop löst ein nicht-existierendes Problem und erzeugt reale (Context Rot, Konsistenz über Turns), Coverage-Validator ist zahnlos by design, Korrektur-Turns sind konzeptionell nicht angebunden |
| **Abhängigkeiten** | Setzt voraus: CR-006 (Background-Init, Verifiziert). Ersetzt NICHT CR-006 — baut darauf auf und überarbeitet die Implementierung. CR-007 (Init-Progress-Feedback, Entwurf) und CR-008 (Phase-End-Validator, Entwurf) sind unabhängig und nicht betroffen. |

---

## 1. Problemstellung

### Kernproblem

Die in CR-006 eingeführte Background-Initialisierung hat die richtige Architektur-Idee (Artefakt vor Dialog aufbauen), aber die Implementierung hat vier fundamentale Schwächen, die zu schlechter Artefaktqualität führen.

### Konkrete Defizite

**D-1: Init-Prompts haben keinen ausreichenden Kontext**

Der Dialog-Prompt `structuring.md` ist ~420 Zeilen lang und funktioniert gut. Der Init-Prompt `init_structuring.md` ist 73 Zeilen und funktioniert schlecht. Die Init-Prompts enthalten:
- Keine Erklärung, was die Digitalisierungsfabrik ist
- Keine Terminologie-Tabelle
- Keine Modellierungsregeln (Granularität, Entscheidungen, Schleifen, Ausnahmen, Konvergenz)
- Keine Patch-Beispiele
- Keine Artefakt-Schema-Referenz
- Keine Transformationsregeln (wie aus Exploration-Slots Strukturschritte werden)

Vergleich:

| Aspekt | Dialog-Prompt (structuring.md) | Init-Prompt (init_structuring.md) |
|--------|-------------------------------|----------------------------------|
| Kontext Digitalisierungsfabrik | 6 Zeilen | Nichts |
| Terminologie-Tabelle | Ja | Nein |
| Modellierungsregeln | ~60 Zeilen | Einzeiler-Stichpunkte |
| Patch-Beispiele | 7 detaillierte (~150 Zeilen) | Keine |
| Schema-Referenz | Vollständige Feldtabelle | Minimaltabelle ohne Erklärung |
| Informationserhaltung | Detaillierte Checkliste | "Jede Information muss zugeordnet werden" |

Das gleiche Problem besteht bei `init_specification.md` (61 Zeilen vs. ~400 Zeilen `specification.md`) und `init_coverage_validator.md` (67 Zeilen, oberflächliche Entity-Checkliste).

**D-2: Multi-Turn-Loop löst ein nicht-existierendes Problem und erzeugt reale**

Der Loop (`orchestrator.py:372-385`) ist auf `_MAX_INIT_TURNS=8` konfiguriert. Aber:

- **Token-Limits sind kein Problem**: Ein typischer Prozess hat 8–15 Strukturschritte. Ein `add`-Patch für einen vollständigen Strukturschritt sind ~200–300 Output-Tokens. 12 Schritte = ~3.500–4.500 Tokens gesamt. Claude kann 8.000+ Output-Tokens pro Call liefern. Ein einzelner Call reicht.
- **Context Rot ist ein reales Problem**: Jeder Init-Turn bekommt denselben System-Prompt plus den aktuellen Artefaktzustand, aber KEINE Information über vorherige Turns. Der Init-Modus sendet jedes Mal `messages=[{"role": "user", "content": "[Initialisierung starten]"}]` (`init_structuring.py:75`) — kein Dialog-Verlauf, keine History. Das LLM muss raten, was bereits abgearbeitet ist.
- **Das LLM setzt nie `init_in_progress`**: Ohne explizite Steuerung versucht jeder Call, alles in einem Rutsch zu erledigen und setzt `init_complete`. Der Multi-Turn-Loop degeneriert de facto zu einem Single-Call.
- **Konsistenz über Turns**: Wenn Turn 1 Schritte s1–s5 anlegt und Turn 2 Schritte s6–s10, müssen `nachfolger`-Verknüpfungen zwischen s5→s6 stimmen. Turn 2 sieht nur den Artefaktzustand, nicht die Intention — das ist fehleranfällig.

**D-3: Coverage-Validator ist zahnlos by design**

`init_coverage_validator.md:50`: "Alle Befunde haben `schweregrad: "warnung"` — nie `"kritisch"`." In `orchestrator.py:395-397`: Korrektur-Turns werden nur bei `severity == "kritisch"` ausgelöst. Der Coverage-Validator löst also **nie** Korrekturen aus.

Zusätzlich ist der Prompt inhaltlich zu oberflächlich — er prüft nur Entity-Checklisten (Akteur vorhanden? System vorhanden?), nicht:
- Ob die Zuordnung von Information zu Schritten sinnvoll ist
- Ob Beschreibungen ausreichend detailliert sind
- Ob der Kontrollfluss die beschriebene Logik korrekt abbildet
- Ob Informationen fragmentiert, redundant oder verloren gegangen sind

**D-4: Korrektur-Turns sind konzeptionell nicht angebunden**

Die Korrektur-Turns (`orchestrator.py:449-483`) rufen denselben Init-Modus mit demselben Prompt auf. Der einzige Unterschied: ein `error_hint` wird als String injiziert. Aber:
- Der Init-Prompt enthält keine Anleitung, wie mit Korrektur-Feedback umzugehen ist
- Es ist unklar, ob das LLM das bestehende Artefakt überarbeiten oder neu anlegen soll
- Der `error_hint` ist ein Freitext-String, kein strukturiertes Template im Prompt

### Auswirkungen

- Init-Artefakte sind qualitativ schlecht (unvollständig, inkonsistent, ohne Details)
- Der Dialog-Modus muss de facto das Artefakt von Grund auf überarbeiten statt nur zu verfeinern
- Das Ziel von CR-006 (Dialog-Modus startet mit gutem Artefakt) wird verfehlt
- Die Validierungskette ist wirkungslos — der Coverage-Validator erzeugt nie Korrekturen

---

## 2. Ziel der Änderung

- **Single-Call statt Multi-Turn**: Ein einziger, gut prompteter LLM-Call ersetzt den 8-Turn-Loop. Prototyp-Beschränkung: Prozesse bis ~15 Schritte (dokumentiert im README).
- **Init-Prompts auf Dialog-Prompt-Niveau**: Vollständiger Kontext, Modellierungsregeln, Patch-Beispiele, Schema-Referenz, Transformationsregeln. ~300 Zeilen statt ~70.
- **Coverage-Validator als echtes Qualitäts-Gate**: Prüft Informationsvollständigkeit, Zuordnungsplausibilität und Kontrollfluss-Abbildung. Darf `"kritisch"` melden bei substanziellen Lücken.
- **Korrektur im selben Prompt abgebildet**: Eine Template-Variable `{validator_feedback}` — leer beim Init-Call, befüllt beim Korrektur-Call. Kein separater Modus nötig.
- **Python-Validator fokussiert**: Nur referenzielle Integrität (R-1) und Abschnitt-Mapping (R-5) — das einzige, was ein LLM nicht zuverlässig deterministisch prüfen kann.
- **Ablauf maximal 3 LLM-Calls**: Init + Coverage-Validator + (optional) Korrektur.

---

## 3. Lösung

### 3.1 Neuer Ablauf im Orchestrator

Der bestehende `_run_background_init` in `orchestrator.py:356-402` wird ersetzt:

```
Single Init-Call (voller Kontext, reichhaltiger Prompt)
    ↓
Python-Validator (nur R-1: ref. Integrität + R-5: Abschnitt-Mapping)
    ↓
Coverage-Validator (LLM, aufgewertet: echte Qualitätsprüfung)
    ↓
Kritische Befunde (Python ODER Coverage)? → EIN Korrektur-Call
    ↓
Warnungen → wm.init_hinweise → Dialog-Modus
```

Maximal 3 LLM-Calls (Init + Coverage + Korrektur), normalerweise 2 (Init + Coverage).

```python
# orchestrator.py — _run_background_init (ersetzt bestehende Methode)

async def _run_background_init(
    self,
    project: Project,
    wm: WorkingMemory,
    target_mode: str,
) -> None:
    init_mode_key = f"init_{target_mode}"
    init_mode = self._modes.get(init_mode_key)
    if init_mode is None:
        logger.warning("orchestrator.background_init.no_init_mode", key=init_mode_key)
        return

    source_type = "structure" if target_mode == "structuring" else "algorithm"

    # Phase 1: Single Init-Call
    context = build_context(project, {}, repository=self._repository, settings=self._settings)
    output = await init_mode.call(context)

    if output.patches:
        artifact = get_artifact(project, source_type)
        result = self._executor.apply_patches(source_type, artifact, output.patches)
        if result.success and result.artifact is not None:
            set_artifact(project, source_type, result.artifact)
            if result.invalidated_abschnitt_ids:
                apply_invalidations(project, result.invalidated_abschnitt_ids, self._executor)

    # Phase 2: Python-Validator (nur R-1 + R-5)
    py_violations = self._run_structural_validator(project, target_mode)

    # Phase 3: Coverage-Validator (LLM)
    coverage_violations = await self._run_coverage_validator(project, wm)

    # Phase 4: Bei kritischen Befunden → EIN Korrektur-Call
    all_violations = py_violations + coverage_violations
    kritische = [v for v in all_violations if v.severity == "kritisch"]
    if kritische:
        feedback = self._format_validator_feedback(all_violations)
        context = build_context(project, {}, repository=self._repository, settings=self._settings)
        context = context.with_validator_feedback(feedback)
        output = await init_mode.call(context)

        if output.patches:
            artifact = get_artifact(project, source_type)
            result = self._executor.apply_patches(source_type, artifact, output.patches)
            if result.success and result.artifact is not None:
                set_artifact(project, source_type, result.artifact)

    # Phase 5: Warnungen → init_hinweise
    warnungen = [v for v in all_violations if v.severity == "warnung"]
    if warnungen:
        wm.init_hinweise = [v.message for v in warnungen]
```

### 3.2 ModeContext erweitern: `validator_feedback`

`ModeContext` in `modes/base.py` erhält eine neue Methode `with_validator_feedback` analog zum bestehenden `with_error_hint`:

```python
class ModeContext(BaseModel):
    # ... bestehende Felder ...
    validator_feedback: str | None = None  # CR-009: Validator-Befunde für Korrektur-Call

    def with_validator_feedback(self, feedback: str) -> "ModeContext":
        """Kopie des Kontexts mit Validator-Feedback zurückgeben."""
        return self.model_copy(update={"validator_feedback": feedback})
```

Die Init-Modi lesen `context.validator_feedback` und injizieren es als Template-Variable `{validator_feedback}` in den System-Prompt.

### 3.3 Orchestrator-Hilfsmethode: `_format_validator_feedback`

Neue private Methode im Orchestrator, die Violations in lesbares Prompt-Feedback formatiert:

```python
def _format_validator_feedback(self, violations: list[StructuralViolation]) -> str:
    lines = ["## Validator-Befunde\n"]
    lines.append("Das Artefakt wurde geprüft. Folgende Probleme wurden gefunden:\n")
    for v in violations:
        severity_label = "KRITISCH" if v.severity == "kritisch" else "Warnung"
        element = f" ({v.element_id})" if v.element_id else ""
        lines.append(f"- [{severity_label}]{element}: {v.message}")
    lines.append("\nKorrigiere die kritischen Befunde. Überarbeite das bestehende Artefakt gezielt — "
                 "lege KEINE neuen Schritte/Abschnitte an, die bereits existieren.")
    return "\n".join(lines)
```

### 3.4 `InitStatus`-Enum und `init_status` entfernen

Da der Loop entfällt, wird das `InitStatus`-Enum nicht mehr benötigt:

- `models.py:80-84`: `InitStatus` Enum entfernen
- `modes/base.py:83`: `init_status: InitStatus | None = None` aus `ModeOutput` entfernen
- `llm/tools.py:76-127`: `INIT_APPLY_PATCHES_TOOL` vereinfachen — `init_status`-Feld entfernen, `phasenstatus` auf `"in_progress"` fixiert lassen
- Init-Modi: `init_status`-Handling aus Output-Parsing entfernen
- Orchestrator: `output.init_status == InitStatus.init_complete`-Checks entfernen

### 3.5 `_MAX_INIT_TURNS` und `_MAX_CORRECTION_TURNS` entfernen

- `orchestrator.py:345-346`: Beide Konstanten entfernen
- Die Loop-Logik in `_run_background_init` entfällt komplett
- `_run_correction_turns` entfällt als separate Methode — die Korrektur ist jetzt ein einzelner Call inline in `_run_background_init`

### 3.6 Python-Validator fokussieren

`init_validator.py` wird auf zwei Regeln reduziert:

**R-1: Referenzielle Integrität** (unverändert, `validate_structure_artifact`):
- Alle `nachfolger`-IDs existieren als Schritte
- Alle `regeln.nachfolger`-IDs existieren
- Alle `schleifenkoerper`-IDs existieren
- Alle `konvergenz`-IDs existieren

**R-5: Abschnitt-Mapping vollständig** (unverändert, `validate_algorithm_artifact`):
- Für jeden Strukturschritt existiert ein Algorithmusabschnitt mit `struktur_ref`

**Entfernt werden:**
- R-2 (Feldvollständigkeit) → wandert in den Coverage-Validator-Prompt
- R-3 (Graph-Konsistenz: Start/Endschritt) → wandert in den Coverage-Validator-Prompt
- R-4 (Variablen-Crosscheck) → wandert in den Coverage-Validator-Prompt
- R-6 (ANALOG-Konsistenz) → wandert in den Coverage-Validator-Prompt

### 3.7 Coverage-Validator-Prompt: Kompletter Rewrite

Der Coverage-Validator wird zum echten Qualitäts-Gate. Neuer Prompt `init_coverage_validator.md`:

**Struktur:**

```markdown
## Mission

Du bist ein **Qualitätsvalidator** im Rahmen der Digitalisierungsfabrik. [Kontext: was ist
die Digitalisierungsfabrik, 4-Phasen-Modell, Artefakt-Kette]

Deine Aufgabe: Prüfe, ob die Transformation des Quellartefakts in das Zielartefakt
vollständig und qualitativ hochwertig ist. Du bist die letzte Prüfinstanz bevor der
Nutzer mit dem Artefakt arbeitet.

## Aktueller Übergang

{transition_type_description}

[Dynamisch: Beschreibung ob Exploration→Struktur oder Struktur→Algorithmus,
mit phasenspezifischen Prüfkriterien]

## Prüfkriterien

### 1. Informationsvollständigkeit (kritisch wenn verletzt)

Jede substanzielle Information aus dem Quellartefakt muss im Zielartefakt repräsentiert sein.

- **Ganze Prozessabschnitte**: Beschreibt das Quellartefakt einen Ablauf, der im
  Zielartefakt keinen Schritt/Abschnitt hat? → KRITISCH
- **Entscheidungen**: Beschreibt das Quellartefakt eine Entscheidung (Wenn/Dann), die im
  Zielartefakt nicht als Entscheidungsschritt modelliert ist? → KRITISCH
- **Systeme/Tools**: Wird ein System im Quellartefakt mehrfach erwähnt und taucht im
  Zielartefakt nirgends auf? → KRITISCH
- **Einzelne Details**: Fehlt ein einzelner Akteurs-Name oder eine Nebenbemerkung? → WARNUNG
  (der Dialog kann das klären)

### 2. Zuordnungsplausibilität (warnung)

- Sind Informationen sinnvoll auf Schritte/Abschnitte verteilt?
- Gibt es Schritte/Abschnitte, die redundante Informationen tragen?

### 3. Kontrollfluss-Abbildung (kritisch bei fehlenden Pfaden)

- Hat jede Entscheidung die richtige Anzahl Ausgänge?
- Sind Schleifen mit sinnvollen Körpern und Abbruchbedingungen modelliert?
- Gibt es einen plausiblen Start-zu-Ende-Pfad?

### 4. Feldvollständigkeit (warnung)

- Haben alle Schritte eine nicht-leere Beschreibung?
- Haben Entscheidungen eine Bedingung?
- Haben Ausnahmen eine Ausnahmebeschreibung?

### 5. Variable Lineage (warnung)

- Sind Variablen aus dem Quellartefakt im Zielartefakt repräsentiert?

## Schwellen — wann KRITISCH, wann WARNUNG?

**KRITISCH** — nur bei substanziellen Lücken:
- Ein ganzer Prozessabschnitt fehlt
- Eine wichtige Entscheidung ist nicht modelliert
- Ein mehrfach genanntes System fehlt komplett

**WARNUNG** — bei kleineren Lücken, die der Dialog klären kann:
- Einzelne Details fehlen in Beschreibungen
- Variable nicht optimal zugeordnet
- Beschreibung könnte reicher sein

**Kein Befund** — wenn die Abweichung irrelevant ist:
- Synonyme Bezeichnung (z.B. "Sachbearbeiterin" vs "Frau Becker")
- Marginale Umformulierungen
- Information ist sinngemäß vorhanden, nur anders formuliert

## Anti-Halluzinations-Regel

Melde NUR Lücken, die du im Quellartefakt konkret belegen kannst.
Für jeden Befund: Zitiere den Slot/das Feld im Quellartefakt und beschreibe,
was im Zielartefakt fehlt oder falsch ist.

Wenn du unsicher bist, ob etwas fehlt → WARNUNG, nicht KRITISCH.
Wenn du nichts findest → melde "coverage_vollstaendig: true". Das ist ein valides
und gewünschtes Ergebnis.

## Output-Format

Ausschließlich valides JSON — keine Einleitung, kein Kommentar, kein Markdown:

{output_schema}

## Quellartefakt

{source_artifact}

## Zielartefakt

{target_artifact}
```

Die Template-Variablen `{transition_type_description}`, `{source_artifact}`, `{target_artifact}` werden vom Mode-Code (`init_coverage_validator.py`) phasenspezifisch befüllt.

**Output-Schema (erweitert um "kritisch"):**

```json
{
  "fehlende_entitaeten": [
    {
      "typ": "prozessabschnitt | entscheidung | system | akteur | variable | detail",
      "bezeichnung": "Beschreibung des Befunds",
      "quelle_slot": "Slot/Feld im Quellartefakt mit der Information",
      "zitat": "Wörtliches Zitat aus dem Quellartefakt",
      "schweregrad": "kritisch | warnung"
    }
  ],
  "coverage_vollstaendig": true | false
}
```

### 3.8 Init-Prompts: Kompletter Rewrite

Beide Init-Prompts (`init_structuring.md`, `init_specification.md`) werden komplett neu geschrieben mit folgender Struktur:

**`init_structuring.md` (~300 Zeilen):**

```markdown
## Mission

Du bist ein **Prozessstruktur-Initialisierer** im Rahmen der Digitalisierungsfabrik.

Die **Digitalisierungsfabrik** hilft nicht-technischen Fachexperten, ihre
Geschäftsprozesse so präzise zu externalisieren, dass am Ende ein detaillierter
Algorithmus steht, der in einem RPA-System (EMMA) programmiert werden kann.

Das System führt den Nutzer durch vier Phasen:
Exploration → **Strukturierung** → Spezifikation → Validierung.

[Kontext: was passiert in jeder Phase, was ist das Ziel der Strukturierung]

Deine Aufgabe: Das Explorationsartefakt **vollständig** in ein Strukturartefakt
transformieren — bevor der Nutzer mit dem Dialog beginnt. Du führst keinen Dialog.
Du stellst keine Fragen. Du arbeitest ausschließlich über Patches.

### Terminologie

[Terminologie-Tabelle aus structuring.md — identisch]

### Qualitätsmaßstab

Das Strukturartefakt wird anschließend im Dialog mit dem Nutzer verfeinert.
Dein Init muss NICHT perfekt sein — aber er muss:

1. **Vollständig** sein: Jede substanzielle Information aus allen 7 Exploration-Slots
   findet sich in mindestens einem Strukturschritt
2. **Referenziell integer** sein: Alle nachfolger, regeln.nachfolger,
   schleifenkoerper, konvergenz verweisen auf existierende Schritte
3. **Korrekt typisiert** sein: Entscheidungen haben Bedingungen,
   Schleifen haben Abbruchbedingungen, Ausnahmen haben Beschreibungen
4. **Reichhaltige Beschreibungen** haben: Alle relevanten Details aus der
   Exploration in das beschreibung-Feld übertragen

## Transformationsregeln

So transformierst du die 7 Exploration-Slots in Strukturschritte:

### Slot: prozessbeschreibung → Hauptsequenz der Schritte
Der Hauptcontainer. Enthält den chronologischen Ablauf. Zerlege ihn in logische
Arbeitsabschnitte. Jeder Abschnitt wird ein Strukturschritt vom typ "aktion".

### Slot: prozessausloeser → Typischerweise der Startschritt
Der Auslöser wird oft zum ersten Schritt (z.B. "Rechnung geht per E-Mail ein").

### Slot: prozessziel → Typischerweise der Endschritt
Das Ziel definiert den letzten regulären Schritt (z.B. "Zahlung ist angewiesen").

### Slot: entscheidungen_und_schleifen → Entscheidungs- und Schleifen-Schritte
Jede genannte Entscheidung wird ein Schritt vom typ "entscheidung" mit bedingung
und ≥2 nachfolgern. Jede genannte Schleife wird ein Schritt vom typ "schleife"
mit schleifenkoerper und abbruchbedingung.

### Slot: beteiligte_systeme → In beschreibung-Felder einarbeiten
Systeme werden nicht zu eigenen Schritten, sondern in die beschreibung der Schritte
eingearbeitet, in denen sie verwendet werden.

### Slot: variablen_und_daten → [VAR: name]-Marker in beschreibung
Für jede Variable einen [VAR: name]-Marker in der beschreibung des Schritts setzen,
in dem die Variable gelesen, geschrieben oder geprüft wird. Keine Variable darf
stillschweigend ignoriert werden.

### Slot: prozesszusammenfassung → /prozesszusammenfassung Feld
Direkt übernehmen oder auf Basis der anderen Slots formulieren.

## Modellierungsregeln

[Identisch aus structuring.md übernommen:]
- Granularität (ein Schritt = ein logischer Arbeitsabschnitt)
- Entscheidungen modellieren (Ja/Nein, 2+ Ausgänge mit regeln, Catch-All)
- Schleifen modellieren (schleifenkoerper, abbruchbedingung, nachfolger)
- Ausnahmen modellieren (typ: "ausnahme", reihenfolge: 99+)
- Konvergenz
- Nachfolger konsistent halten
- Spannungsfelder proaktiv erkennen (Medienbrüche, Redundanzen)
- ANALOG-Kennzeichnung: Analoge Prozessanteile → spannungsfeld mit "ANALOG:"-Präfix

## Informationserhaltungspflicht

[Identisch aus structuring.md übernommen:]
- Jeder Akteur → beschreibung
- Jedes System/Tool → beschreibung
- Jeder Pfad/Ordner/Dateiname → beschreibung
- Jede Regel/Schwelle → beschreibung
- Jede Ausnahme → eigener Schritt oder beschreibung
- Jeder Medienbruch → spannungsfeld
- Jede Variable → [VAR: name] in beschreibung

## Kein Dialog

Du stellst KEINE Fragen. Du gibst nutzeraeusserung: "" zurück.
Alles geht in Patches. Gib phasenstatus: "in_progress" zurück.

## Validator-Feedback

{validator_feedback}

Wenn oben Validator-Befunde aufgelistet sind: Überarbeite das bestehende Artefakt
gezielt. Lege KEINE neuen Schritte an, die bereits existieren. Korrigiere nur die
gemeldeten Probleme mit replace-Patches auf bestehende Schritte oder add-Patches
für fehlende Schritte. Wenn kein Feedback vorhanden ist, ignoriere diesen Abschnitt.

## Output-Kontrakt

[Tool-Schema-Beschreibung, Patch-Format]

## Patch-Beispiele

[Identisch aus structuring.md übernommen — alle 7 Beispiele:
- Neuen Schritt einfügen
- Schritt entfernen
- Spannungsfeld setzen
- Ausnahmeschritt
- Entscheidung mit Regeln
- Schleife mit Scope
- Prozesszusammenfassung]

## Referenz: Strukturschritt-Schema

[Identisch aus structuring.md übernommen — vollständige Feldtabelle]

### Konsistenzregeln

[Identisch aus structuring.md übernommen]

## Explorationsartefakt (Quelle — alle Information hieraus muss ins Zielartefakt)

{exploration_content}

## Aktueller Stand der Strukturschritte

{slot_status}
```

**`init_specification.md` (~300 Zeilen):** Analoge Struktur, aber:
- Kontext: Strukturierung → Spezifikation
- Transformationsregeln: Wie aus Strukturschritten Algorithmusabschnitte werden
- Variable Lineage: `[VAR: name]` → `[Variable] name (Typ) — Beschreibung. Quelle: ...`
- ANALOG-Handling: `spannungsfeld: "ANALOG:..."` → WAIT-Aktion mit `emma_kompatibel: false`
- EMMA-Aktionskatalog als Referenz (aus specification.md)
- Keine EMMA-Parameter-Details (zu detailliert für Init, das macht der Dialog)

### 3.9 Init-Modi: Template-Variable `{validator_feedback}` einfügen

Die Init-Modi (`init_structuring.py`, `init_specification.py`) werden angepasst:

```python
# init_structuring.py — call() Methode (angepasst)

async def call(self, context: ModeContext) -> ModeOutput:
    # ... LLM-Client-Check ...

    exploration_content = _build_exploration_content(context)
    slot_status = _build_slot_status(context)

    system_prompt = _load_system_prompt()
    system_prompt = system_prompt.replace("{exploration_content}", exploration_content)
    system_prompt = system_prompt.replace("{slot_status}", slot_status)

    # CR-009: Validator-Feedback injizieren (leer beim Init-Call, befüllt beim Korrektur-Call)
    feedback = context.validator_feedback or ""
    system_prompt = system_prompt.replace("{validator_feedback}", feedback)

    response = await self._llm_client.complete(
        system=system_prompt,
        messages=[{"role": "user", "content": "[Initialisierung starten]"}],
        tools=[INIT_APPLY_PATCHES_TOOL],
        tool_choice={"type": "tool", "name": "apply_patches"},
    )

    tool_input = response.tool_input or {}
    patches = [p for p in (tool_input.get("patches") or []) if isinstance(p, dict)]

    # CR-009: init_status entfällt — kein Loop mehr
    return ModeOutput(
        nutzeraeusserung="",
        patches=patches,
        phasenstatus=Phasenstatus.in_progress,
        flags=[],
        debug_request=response.debug_request,
        usage=response.usage,
    )
```

### 3.10 Coverage-Validator-Modus: Phasenspezifischer Kontext

`init_coverage_validator.py` wird angepasst, um phasenspezifische Template-Variablen zu setzen:

```python
# init_coverage_validator.py — call() Methode (angepasst)

async def call(self, context: ModeContext) -> ModeOutput:
    # ... LLM-Client-Check ...

    system_prompt = _load_system_prompt()

    # CR-009: Phasenspezifischen Kontext bestimmen
    if context.aktive_phase == Projektphase.strukturierung:
        transition_desc = (
            "Du prüfst den Übergang **Exploration → Struktur**.\n\n"
            "Quellartefakt: Explorationsartefakt (7 Slots mit Freitext).\n"
            "Zielartefakt: Strukturartefakt (Strukturschritte mit Kontrollfluss).\n\n"
            "Hauptfrage: Wurde jede substanzielle Information aus den 7 Exploration-Slots "
            "in mindestens einem Strukturschritt repräsentiert?"
        )
        source_artifact = _build_exploration_content(context)
        target_artifact = _build_structure_content(context)
    else:
        transition_desc = (
            "Du prüfst den Übergang **Struktur → Algorithmus**.\n\n"
            "Quellartefakt: Strukturartefakt (Strukturschritte mit Kontrollfluss).\n"
            "Zielartefakt: Algorithmusartefakt (Algorithmusabschnitte mit EMMA-Aktionen).\n\n"
            "Hauptfrage: Hat jeder Strukturschritt einen korrespondierenden "
            "Algorithmusabschnitt mit vollständigem Kontext?"
        )
        source_artifact = _build_structure_content(context)
        target_artifact = _build_algorithm_content(context)

    system_prompt = system_prompt.replace("{transition_type_description}", transition_desc)
    system_prompt = system_prompt.replace("{source_artifact}", source_artifact)
    system_prompt = system_prompt.replace("{target_artifact}", target_artifact)

    # Output-Schema als Template-Variable
    system_prompt = system_prompt.replace("{output_schema}", OUTPUT_SCHEMA_JSON)

    response = await self._llm_client.complete(
        system=system_prompt,
        messages=[{"role": "user", "content": "[Coverage-Prüfung starten]"}],
        tools=None,
        tool_choice=None,
    )

    return ModeOutput(
        nutzeraeusserung=response.nutzeraeusserung or _EMPTY_COVERAGE_JSON,
        patches=[],
        phasenstatus=Phasenstatus.in_progress,
        flags=[],
        debug_request=response.debug_request,
        usage=response.usage,
    )
```

Die Helper-Funktionen `_build_structure_content` und `_build_algorithm_content` werden ergänzt — sie liefern den vollständigen Artefaktinhalt (nicht nur Kurzübersichten wie bisher), damit der Coverage-Validator eine echte Prüfung durchführen kann.

### 3.11 INIT_APPLY_PATCHES_TOOL vereinfachen

Das `init_status`-Feld entfällt:

```python
# llm/tools.py — INIT_APPLY_PATCHES_TOOL (vereinfacht)

INIT_APPLY_PATCHES_TOOL: dict = {
    "name": "apply_patches",
    "description": (
        "Wendet RFC 6902 JSON Patch Operationen auf das aktive Artefakt an."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "nutzeraeusserung": {
                "type": "string",
                "description": "Immer leer lassen: ''",
            },
            "patches": {
                "type": "array",
                "description": "Liste von RFC 6902 JSON Patch Operationen auf das aktive Artefakt",
                "items": {
                    "type": "object",
                    "properties": {
                        "op": {
                            "type": "string",
                            "enum": ["add", "replace", "remove"],
                            "description": "RFC 6902 Operation",
                        },
                        "path": {
                            "type": "string",
                            "description": "RFC 6902 JSON Pointer Pfad",
                        },
                        "value": {
                            "description": "Neuer Wert (erforderlich bei add/replace)",
                        },
                    },
                    "required": ["op", "path"],
                },
            },
            "phasenstatus": {
                "type": "string",
                "enum": ["in_progress"],
                "description": "Immer 'in_progress' — Init-Modi setzen keinen phase_complete.",
            },
        },
        "required": ["nutzeraeusserung", "patches", "phasenstatus"],
    },
}
```

### 3.12 Coverage-Validator Parsing im Orchestrator anpassen

Die Methode `_run_coverage_validator` in `orchestrator.py:422-447` wird angepasst, um das erweiterte Output-Schema zu parsen und auch `"kritisch"` zu akzeptieren:

```python
async def _run_coverage_validator(self, project, wm):
    coverage_mode = self._modes.get("init_coverage_validator")
    if coverage_mode is None:
        return []
    context = build_context(project, {}, repository=self._repository, settings=self._settings)
    output = await coverage_mode.call(context)
    try:
        data = json.loads(output.nutzeraeusserung)
        return [
            StructuralViolation(
                severity=e.get("schweregrad", "warnung"),
                message=f"{e['typ']}: {e['bezeichnung']} (aus {e['quelle_slot']})",
                element_id=None,
            )
            for e in data.get("fehlende_entitaeten", [])
        ]
    except (json.JSONDecodeError, KeyError):
        logger.warning("orchestrator.coverage_validator.parse_error")
        return []
```

(Funktional identisch zum bestehenden Code — der einzige Unterschied ist, dass der Coverage-Validator jetzt auch `"kritisch"` im JSON zurückgeben darf, was der bestehende Code bereits korrekt parst.)

### 3.13 Prototyp-Beschränkung dokumentieren

Im README einen Abschnitt ergänzen:

```markdown
### Bekannte Beschränkungen

- **Prozessgröße**: Die Background-Initialisierung ist für Prozesse mit bis zu ~15
  Strukturschritten optimiert. Bei größeren Prozessen kann der Init-Call unvollständige
  Artefakte erzeugen. Der Dialog-Modus kann fehlende Schritte im Gespräch ergänzen.
```

---

## 3a. Abhängigkeiten & Konflikte

- **CR-006 (Verifiziert)**: Dieser CR überarbeitet die in CR-006 eingeführte Implementierung. Alle CR-006-Dateien werden direkt modifiziert. Kein Konflikt — bewusste Überarbeitung.
- **ADR-008 aus CR-006** ("Background-Init als Inline-Multi-Call im Orchestrator-Turn"): Dieser CR weicht von ADR-008 ab — der Multi-Call-Loop wird durch einen Single-Call ersetzt. Neuer ADR-009 unten.
- **CR-002 (Implementiert)**: Kontrollfluss-Felder (`regeln`, `schleifenkoerper`, `abbruchbedingung`, `konvergenz`) werden in den neuen Init-Prompts korrekt adressiert. Kein Konflikt.
- **CR-007 (Entwurf)**: Init-Progress-Feedback. Da der Init jetzt maximal 3 Calls statt 8 hat, sind die Latenz-Annahmen in CR-007 konservativer als nötig. Kein Konflikt — CR-007 kann unverändert implementiert werden.
- **CR-008 (Entwurf)**: Phase-End-Validator. Unabhängig — betrifft Phasenabschluss, nicht Init. Kein Konflikt.

### ADR-009: Single-Call-Init statt Multi-Turn-Loop

- **Kontext**: ADR-008 (CR-006) definiert die Background-Initialisierung als Inline-Multi-Call mit bis zu `MAX_INIT_TURNS=8` sequentiellen LLM-Aufrufen. Die Begründung war Token-Budget-Unsicherheit bei großen Prozessen.
- **Entscheidung**: Ersetze den Multi-Turn-Loop durch einen einzelnen Init-Call. Der Coverage-Validator und ein optionaler Korrektur-Call bilden die Nachbearbeitung. Maximal 3 LLM-Calls statt maximal 10 (8 Init + 2 Korrektur).
- **Begründung**: (a) Token-Limits sind kein Problem — typische Prozesse (8–15 Schritte) erzeugen 3.500–4.500 Output-Tokens, weit unter der Kapazitätsgrenze. (b) Context Rot über Turns ist ein reales Problem — jeder Turn verliert den Bezug zu vorherigen Turns. (c) Das `init_status`-Signal funktioniert in der Praxis nicht — das LLM setzt immer `init_complete`. (d) Prototyp-Scope: Prozesse >15 Schritte sind eine dokumentierte Beschränkung.
- **Ablösung**: Löst ADR-008 aus CR-006 ab.
- **Konsequenzen**: `InitStatus`-Enum entfällt. `_MAX_INIT_TURNS` entfällt. Maximale Init-Latenz sinkt von ~40s auf ~15s (3 Calls × ~5s). HLA und README werden nach Implementierung aktualisiert.

---

## 4. Änderungsplan

| # | Datei | Änderung |
|---|---|---|
| 1 | `backend/artifacts/models.py` | `InitStatus` Enum entfernen (Zeilen 80–84) |
| 2 | `backend/modes/base.py` | `init_status` aus `ModeOutput` entfernen (Zeile 83). Neues Feld `validator_feedback: str \| None = None` auf `ModeContext` mit Methode `with_validator_feedback()` |
| 3 | `backend/llm/tools.py` | `INIT_APPLY_PATCHES_TOOL`: `init_status`-Feld entfernen, `phasenstatus` auf `["in_progress"]` fixiert lassen (Zeilen 76–127 ersetzen) |
| 4 | `backend/artifacts/init_validator.py` | Auf R-1 + R-5 reduzieren: R-2 (Feldvollständigkeit), R-3 (Graph-Konsistenz), R-4 (Variablen-Crosscheck), R-6 (ANALOG-Konsistenz) entfernen |
| 5 | `backend/prompts/init_structuring.md` | Kompletter Rewrite: ~300 Zeilen mit vollem Kontext, Modellierungsregeln, Patch-Beispielen, Transformationsregeln, Schema-Referenz, `{validator_feedback}`-Variable gemäß §3.8 |
| 6 | `backend/prompts/init_specification.md` | Kompletter Rewrite: ~300 Zeilen analog zu init_structuring, mit EMMA-Aktionskatalog, Variable-Lineage-Regeln, ANALOG-Handling, `{validator_feedback}`-Variable gemäß §3.8 |
| 7 | `backend/prompts/init_coverage_validator.md` | Kompletter Rewrite: Echte Qualitätsprüfung mit 5 Prüfkriterien, Schwellendefinition (kritisch/warnung), Anti-Halluzinations-Regel, phasenspezifische Template-Variablen gemäß §3.7 |
| 8 | `backend/modes/init_structuring.py` | `init_status`-Handling entfernen, `{validator_feedback}` Template-Variable aus `context.validator_feedback` injizieren gemäß §3.9 |
| 9 | `backend/modes/init_specification.py` | Analog zu #8 |
| 10 | `backend/modes/init_coverage_validator.py` | Phasenspezifische Template-Variablen (`{transition_type_description}`, `{source_artifact}`, `{target_artifact}`) setzen. Vollständige Artefaktinhalte statt Kurzübersichten übergeben gemäß §3.10 |
| 11 | `backend/core/orchestrator.py` | `_run_background_init` ersetzen: Loop entfernen, Single-Call + Python-Validator + Coverage-Validator + optionaler Korrektur-Call gemäß §3.1. `_MAX_INIT_TURNS` und `_MAX_CORRECTION_TURNS` entfernen. `_run_correction_turns` entfernen. Neue Methode `_format_validator_feedback` gemäß §3.3 |
| 12 | `README.md` | Prototyp-Beschränkung (Prozesse bis ~15 Schritte) dokumentieren gemäß §3.13. Init-Ablauf-Beschreibung aktualisieren (Single-Call statt Loop) |

**Reihenfolge**: #1–3 (Modell-Cleanup) → #4 (Validator fokussieren) → #5–7 (Prompts neu schreiben) → #8–10 (Modi anpassen) → #11 (Orchestrator) → #12 (Doku)

---

## 5. Risiken und Mitigationen

### R-1: Single-Call reicht nicht für große Prozesse

**Risiko**: Bei Prozessen mit >15 Schritten könnte ein einzelner Call die Output-Token-Grenze erreichen und ein unvollständiges Artefakt liefern.

**Mitigation**: Dokumentierte Prototyp-Beschränkung. Der Dialog-Modus kann fehlende Schritte im Gespräch ergänzen. Bei Bedarf in einem späteren CR: Fallback auf zweiten Call wenn Artefakt leer/unvollständig.

### R-2: Coverage-Validator meldet false positives als "kritisch"

**Risiko**: Der Coverage-Validator könnte substanzielle Lücken melden, die keine sind (Synonyme, Umformulierungen), und einen unnötigen Korrektur-Call auslösen.

**Mitigation**: (a) Anti-Halluzinations-Regel im Prompt mit Zitatpflicht. (b) Klare Schwellendefinition: "kritisch" nur bei ganzen fehlenden Abschnitten/Entscheidungen, nicht bei einzelnen Details. (c) Schlimmstfall ist ein überflüssiger Korrektur-Call — ~5s Latenz, kein Qualitätsverlust.

### R-3: Init-Prompt zu lang → Input-Token-Kosten steigen

**Risiko**: Die neuen Init-Prompts (~300 Zeilen) plus das vollständige Quellartefakt sind ein substantieller Input. Bei Claude mit 1M Context kein technisches Problem, aber höhere Token-Kosten pro Init.

**Mitigation**: Für den Prototyp akzeptabel. Prompt-Länge ist investierte Qualität — die Dialog-Prompts sind ähnlich lang und funktionieren gut. Optimierung (z.B. Template-Includes, kontextabhängiges Prompt-Trimming) ist ein späterer CR.

### R-4: Bestehende Tests brechen durch Entfernung von InitStatus

**Risiko**: Tests die `InitStatus` oder `init_status` in `ModeOutput` referenzieren, kompilieren nicht mehr.

**Mitigation**: Alle Tests die `InitStatus` verwenden müssen angepasst werden. Der Init-Loop-Test wird durch einen Single-Call-Test ersetzt. `ModeOutput`-Assertions die `init_status` prüfen, werden entfernt.

### R-5: Korrektur-Call überschreibt gutes Artefakt

**Risiko**: Wenn der Coverage-Validator fälschlich "kritisch" meldet, könnte der Korrektur-Call bestehende gute Schritte überschreiben statt nur zu ergänzen.

**Mitigation**: Der Korrektur-Abschnitt im Init-Prompt enthält explizit: "Lege KEINE neuen Schritte an, die bereits existieren. Korrigiere nur die gemeldeten Probleme." Zusätzlich: Das Artefakt wird per `replace`-Patches modifiziert, nicht komplett ersetzt.

---

## 6. Nicht im Scope

- **Multi-Turn-Fallback für große Prozesse**: Bewusst ausgeschlossen. Prototyp-Beschränkung dokumentiert.
- **Template-Include-System für gemeinsame Prompt-Fragmente**: Duplikation zwischen Dialog- und Init-Prompts wird akzeptiert. Refactoring in separatem CR.
- **WebSocket Progress-Events während Init**: Unverändert aus CR-007 (Entwurf), separater Scope.
- **Init für Explorer-Phase oder Validierungs-Phase**: Unverändert — kein Init sinnvoll (kein Quellartefakt / eigene Logik).
- **SDD-Aktualisierung**: Erfolgt nach Verifikation, nicht in diesem CR.

---

## 7. Abnahmekriterien

1. `InitStatus` Enum existiert nicht mehr in `models.py`. `init_status` existiert nicht mehr in `ModeOutput`.
2. `INIT_APPLY_PATCHES_TOOL` in `tools.py` hat kein `init_status`-Feld mehr.
3. `_run_background_init` in `orchestrator.py` enthält keinen Loop mehr — maximal 3 sequentielle LLM-Calls (Init, Coverage, Korrektur).
4. `_MAX_INIT_TURNS` und `_MAX_CORRECTION_TURNS` existieren nicht mehr in `orchestrator.py`.
5. `init_validator.py` enthält nur noch R-1 (referenzielle Integrität) und R-5 (Abschnitt-Mapping). R-2, R-3, R-4, R-6 sind entfernt.
6. `init_structuring.md` enthält: Mission mit Digitalisierungsfabrik-Kontext, Terminologie, Transformationsregeln, Modellierungsregeln, Patch-Beispiele, Schema-Referenz, `{validator_feedback}`-Variable. Mindestens 250 Zeilen.
7. `init_specification.md` enthält: Analoge Struktur zu #6 mit EMMA-Aktionskatalog. Mindestens 250 Zeilen.
8. `init_coverage_validator.md` enthält: 5 Prüfkriterien (Vollständigkeit, Zuordnung, Kontrollfluss, Feldvollständigkeit, Variable Lineage), Schwellendefinition (kritisch/warnung), Anti-Halluzinations-Regel, phasenspezifische Template-Variablen.
9. Coverage-Validator darf `"kritisch"` im JSON-Output melden. Kritische Befunde lösen einen Korrektur-Call aus.
10. `ModeContext` hat Feld `validator_feedback: str | None` mit Methode `with_validator_feedback()`.
11. Init-Modi injizieren `context.validator_feedback` als Template-Variable `{validator_feedback}` in den System-Prompt.
12. Coverage-Validator-Modus setzt phasenspezifische Template-Variablen (`{transition_type_description}`, `{source_artifact}`, `{target_artifact}`).
13. Alle bestehenden Tests in `test_orchestrator.py`, `test_structuring_mode.py`, `test_specification_mode.py` sind nach Anpassung grün.
14. README enthält Prototyp-Beschränkung für Prozessgröße.

---

## 8. Aufwandsschätzung

| Feld | Wert |
|---|---|
| **Komplexität** | M (12 geänderte Dateien, Breaking Change durch Entfernung von InitStatus) |
| **Betroffene Dateien** | 12 |
| **Breaking Change** | Ja — `InitStatus` Enum und `init_status` auf `ModeOutput` werden entfernt; Tests die diese referenzieren müssen angepasst werden |

| Phase | Dateien | Komplexität |
|---|---|---|
| Modell-Cleanup | `models.py`, `base.py`, `tools.py` | S |
| Validator fokussieren | `init_validator.py` | S |
| Prompts neu schreiben | `init_structuring.md`, `init_specification.md`, `init_coverage_validator.md` | L |
| Modi anpassen | `init_structuring.py`, `init_specification.py`, `init_coverage_validator.py` | M |
| Orchestrator | `orchestrator.py` | M |
| Dokumentation | `README.md` | S |
