# CR-006: Background-Initialisierung mit Validierung — Artefaktaufbau vor Dialog-Einstieg

| Feld | Wert |
|---|---|
| **ID** | CR-006 |
| **Titel** | Background-Initialisierung mit Validierung — Artefaktaufbau vor Dialog-Einstieg |
| **Status** | Verifiziert |
| **Erstellt** | 2026-03-23 |
| **Priorität** | Hoch |
| **Auslöser** | Analyse der Erstaktivierungs-Problematik in Structurer und Specifier: LLM-gesteuerte Artefakt-Initialisierung im ersten Dialog-Turn ist unzuverlässig und kognitiv überlastet; übergeordnete Architekturlösung identifiziert |
| **Abhängigkeiten** | Setzt voraus: CR-002 (Kontrollfluss-Felder, Implementiert), CR-003 (Explorer, Verifiziert), CR-004 (Structurer, Implementiert). Ersetzt: CR-005 (Überholt) |

---

## 1. Problemstellung

### Kernproblem

Structurer und Specifier müssen aktuell in ihrem **ersten Dialog-Turn** zwei fundamentale Aufgaben gleichzeitig erledigen: (a) das Zielartefakt vollständig aus dem Quellartefakt aufbauen und (b) den Nutzer sinnvoll ansprechen und führen. Diese Kombination ist für realistische Prozessgrößen (10–20 Strukturschritte) in einem einzigen LLM-Call nicht zuverlässig leistbar. Hinzu kommen drei strukturelle Übergabelücken in der Phasenkette.

### Konkrete Defizite

**D-1: Erstaktivierung überlastet den ersten Dialog-Turn**

Structurer-Prompt: `"Erstelle Patches für ALLE erkennbaren Prozessschritte in diesem Turn."` Specifier-Prompt: `"Lege für jeden Strukturschritt einen Algorithmusabschnitt an [...] lege für alle Strukturschritte, bei denen bereits genug Information vorliegt, vorläufige EMMA-Aktionen an."`

Bei 15 Strukturschritten mit Entscheidungen, Schleifen und Ausnahmen bedeutet das: vollständige Strukturerstellung + korrekte `nachfolger`-Verkettung + Nutzeransprache — alles in einem Pass. Typische Fehler: inkonsistente Schritt-IDs, fehlende `nachfolger`-Updates beim Einfügen, vergessene Entscheidungsregeln, abgeschnittene Beschreibungen.

**D-2: Variable Lineage — kein formaler Übergabe-Kontrakt**

Variablen entstehen als Freitext in `variablen_und_daten` (Explorer), tauchen informell in `beschreibung`-Feldern auf (Structurer), und werden erst im Specifier formal als `[Variable] name (typ) — ...` dokumentiert. Kein konsistentes Markierungsformat, keine Übergabepflicht.

Folge: Variablen aus der Exploration gehen im Specifier unter, wenn sie nicht zufällig im Dialog erneut erwähnt werden.

**D-3: EMMA-Kompatibilität wird zu spät entdeckt**

Analoge Prozessanteile (Telefonat, physische Unterschrift, Postversand) werden im Structurer nicht gekennzeichnet. Der Specifier entdeckt sie ad-hoc beim Durcharbeiten des jeweiligen Schritts.

UX-Konsequenz: Der Nutzer hat nach Phase 2 das Bild eines vollständig automatisierbaren Prozesses. Die Korrektur in Phase 3 wirkt wie eine Überraschung.

**D-4: Kein struktureller Coverage-Check zwischen Phasen**

Es gibt keine Prüfung, ob alle Informationen aus dem Quellartefakt tatsächlich ins Zielartefakt übernommen wurden. Stille Informationsverluste sind nicht detektierbar.

### Auswirkungen

- Qualitätsvarianz im Strukturartefakt je nach Prozessgröße und LLM-Tagesform
- Variablen aus der Exploration werden sporadisch übernommen oder doppelt definiert
- Analoge Schritte erzeugen ungerechtfertigte Erwartungen beim Nutzer
- Informationsverluste zwischen Phasen sind nicht sichtbar und nicht korrigierbar

---

## 2. Ziel der Änderung

- **Vollständige Artefakt-Initialisierung vor Dialog-Einstieg**: Wenn der Nutzer vom Moderator in den Structurer oder Specifier wechselt, ist das Zielartefakt bereits vollständig aufgebaut. Der Dialog-Modus verfeinert nur noch — er baut nicht mehr auf.
- **Multi-Turn Init ohne Nutzer-Interaktion**: Die Initialisierung läuft intern im Orchestrator, transparent für den Nutzer. Sie kann beliebig viele LLM-Calls benötigen — der Nutzer wartet kurz.
- **Harte strukturelle Garantien**: Ein deterministischer Python-Validator prüft referenzielle Integrität, Feldvollständigkeit und Variablen-Crosscheck nach jedem Init-Turn.
- **Coverage-Check**: Ein LLM-basierter Validator prüft einmalig, ob alle benannten Entitäten (Akteure, Systeme, Regeln, Variablen, Ausnahmen) aus dem Quellartefakt im Zielartefakt auffindbar sind. Er erfindet **keine** Inhalte — er meldet nur, was fehlt.
- **Variable Lineage und ANALOG-Früherkennung**: In den Init-Prompts verankert, nicht in den Dialog-Prompts.
- **Dialog-Prompts** verlieren ihre Erstaktivierungs-Sektionen — sie starten immer mit einem vorhandenen Artefakt.

---

## 3. Lösung

### 3.1 Architektur: Init-Loop im Orchestrator

Der Einhängepunkt ist `Flag.return_to_mode` in `orchestrator.py` (aktuell Zeile 262). Wenn dieser Flag erkannt wird und das Zielartefakt noch leer ist, startet die Background-Initialisierung **inline** — bevor der Dialog-Modus aktiviert wird.

```
Moderator → Flag.advance_phase → Phase gewechselt
Nutzer bestätigt → Flag.return_to_mode
        ↓
Orchestrator: Ist Zielartefakt leer?
   Ja → _run_background_init() ← NEU
        ↓
   Init-Loop (max. MAX_INIT_TURNS):
     1. Init-Modus aufrufen (kein Nutzer-Input)
     2. Patches anwenden
     3. Python-Validator: strukturelle Prüfung
     4. init_status == "complete"? → Loop beendet
        ↓
   LLM-Coverage-Validator (einmalig)
        ↓
   Korrektur-Turns falls kritische Befunde (max. 2)
        ↓
   aktiver_modus = Dialog-Modus ("structuring" / "specification")
   ↓
Dialog-Modus: erste Nutzeransprache mit vorhandenem Artefakt
```

Die gesamte Initialisierung passiert aus Nutzerperspektive in **einem Turn** (dem Turn in dem er "Weiter" sagt). Der Response kommt später zurück, aber das Artefakt ist vollständig wenn er ankommt.

### 3.2 Output-Kontrakt für Init-Modi

Init-Modi sind vollwertige Modi — sie erben von `BaseMode` und geben `ModeOutput` zurück. `ModeOutput` wird um ein optionales Feld `init_status` erweitert, das Dialog-Modi auf `None` lassen:

```python
# backend/artifacts/models.py — NEU

class InitStatus(StrEnum):
    init_in_progress = "init_in_progress"  # Mehr zu tun in nächstem Turn
    init_complete = "init_complete"          # Alle Elemente initialisiert

# backend/modes/base.py — ERGÄNZT (neues optionales Feld in ModeOutput)

class ModeOutput(BaseModel):
    nutzeraeusserung: str
    patches: list[dict] = Field(default_factory=list)
    phasenstatus: Phasenstatus
    flags: list[Flag] = Field(default_factory=list)
    validierungsbericht: Validierungsbericht | None = None
    init_status: InitStatus | None = None  # NEU — nur Init-Modi setzen dieses Feld
    debug_request: dict | None = Field(default=None, exclude=True)
    usage: dict | None = Field(default=None, exclude=True)
```

Init-Modi setzen `init_status` auf `InitStatus.init_in_progress` oder `InitStatus.init_complete` und geben `nutzeraeusserung=""`, `phasenstatus=Phasenstatus.in_progress`, `flags=[]` zurück. Dialog-Modi lassen `init_status` auf `None` (Pydantic-Default, vollständig backward-compatible). `InitModeOutput` als separate Klasse entfällt.

Das LLM im Init-Modus setzt `init_status: "init_complete"` wenn es keine weiteren offenen Elemente sieht. Der Python-Validator prüft danach unabhängig — das LLM-Signal ist nicht die letzte Instanz.

### 3.3 Python-Validator: Deterministische Strukturprüfung

Neue Datei `backend/artifacts/init_validator.py`. Prüft nach jedem Init-Turn und nach Abschluss:

```python
@dataclass
class StructuralViolation:
    severity: Literal["kritisch", "warnung"]
    message: str
    element_id: str | None = None

def validate_structure_artifact(
    exploration: ExplorationArtifact,
    structure: StructureArtifact,
) -> list[StructuralViolation]:
    violations = []

    # R-1: Referenzielle Integrität
    alle_ids = set(structure.schritte.keys())
    for sid, schritt in structure.schritte.items():
        for nf in schritt.nachfolger:
            if nf not in alle_ids:
                violations.append(StructuralViolation(
                    "kritisch", f"nachfolger '{nf}' existiert nicht", sid))
        for regel in schritt.regeln:
            if regel.nachfolger not in alle_ids:
                violations.append(StructuralViolation(
                    "kritisch", f"regeln.nachfolger '{regel.nachfolger}' existiert nicht", sid))
        for kid in schritt.schleifenkoerper:
            if kid not in alle_ids:
                violations.append(StructuralViolation(
                    "kritisch", f"schleifenkoerper '{kid}' existiert nicht", sid))
        if schritt.konvergenz and schritt.konvergenz not in alle_ids:
            violations.append(StructuralViolation(
                "kritisch", f"konvergenz '{schritt.konvergenz}' existiert nicht", sid))

    # R-2: Feldvollständigkeit
    for sid, schritt in structure.schritte.items():
        if not schritt.titel:
            violations.append(StructuralViolation("kritisch", "titel leer", sid))
        if not schritt.beschreibung:
            violations.append(StructuralViolation("warnung", "beschreibung leer", sid))
        if schritt.typ == Strukturschritttyp.entscheidung and not schritt.bedingung:
            violations.append(StructuralViolation("warnung", "entscheidung ohne bedingung", sid))
        if schritt.typ == Strukturschritttyp.ausnahme and not schritt.ausnahme_beschreibung:
            violations.append(StructuralViolation("warnung", "ausnahme ohne ausnahme_beschreibung", sid))

    # R-3: Graph-Konsistenz
    referenziert = {nf for s in structure.schritte.values() for nf in s.nachfolger}
    start_kandidaten = [sid for sid in alle_ids if sid not in referenziert]
    if len(start_kandidaten) != 1:
        violations.append(StructuralViolation(
            "warnung", f"Genau 1 Startschritt erwartet, gefunden: {start_kandidaten}"))
    end_kandidaten = [sid for sid, s in structure.schritte.items() if not s.nachfolger
                      and s.typ != Strukturschritttyp.ausnahme]
    if not end_kandidaten:
        violations.append(StructuralViolation("warnung", "Kein Endschritt (nachfolger: []) gefunden"))

    # R-4: Variablen-Crosscheck
    var_slot = exploration.slots.get("variablen_und_daten")
    if var_slot and var_slot.inhalt:
        # Einfache Heuristik: Prüfe ob Eintrags-Namen (bis " —") in irgendeiner beschreibung auftauchen
        for zeile in var_slot.inhalt.splitlines():
            var_name = zeile.split("—")[0].strip().split(" ")[0].lower()
            if var_name and not any(
                var_name in s.beschreibung.lower()
                for s in structure.schritte.values()
            ):
                violations.append(StructuralViolation(
                    "warnung", f"Variable '{var_name}' aus variablen_und_daten nicht in beschreibung gefunden"))

    return violations

def validate_algorithm_artifact(
    structure: StructureArtifact,
    algorithm: AlgorithmArtifact,
) -> list[StructuralViolation]:
    violations = []

    # R-5: Abschnitt-Mapping vollständig
    for sid in structure.schritte:
        refs = [ab for ab in algorithm.abschnitte.values() if ab.struktur_ref == sid]
        if not refs:
            violations.append(StructuralViolation(
                "kritisch", f"Kein Algorithmusabschnitt für Strukturschritt '{sid}'", sid))

    # R-6: ANALOG-Konsistenz
    for sid, schritt in structure.schritte.items():
        if schritt.spannungsfeld and schritt.spannungsfeld.startswith("ANALOG:"):
            ab = next((a for a in algorithm.abschnitte.values() if a.struktur_ref == sid), None)
            if ab:
                hat_inkompatible_aktion = any(
                    not a.emma_kompatibel for a in ab.aktionen.values()
                )
                if not hat_inkompatible_aktion:
                    violations.append(StructuralViolation(
                        "warnung",
                        f"ANALOG-Schritt '{sid}' hat keine emma_kompatibel=false Aktion", sid))

    return violations
```

### 3.4 LLM-Coverage-Validator: Nur Coverage, kein Content-Inventing

Neuer Prompt `backend/prompts/init_coverage_validator.md`. Dieser Validator hat **eine einzige Aufgabe**: prüfen ob alle benannten Entitäten aus dem Quellartefakt im Zielartefakt auffindbar sind.

**Was er prüft (ausschließlich):**
- Jeder genannte Akteur (Personen, Rollen) aus dem Quellartefakt → auffindbar in mindestens einem Ziel-Feld
- Jedes genannte IT-System/Tool → auffindbar
- Jede genannte Regel oder Schwelle (Beträge, Fristen, Prozentsätze) → auffindbar
- Jede genannte Ausnahme → hat korrespondierenden Schritt oder Eintrag
- Jede Variable aus `variablen_und_daten` → hat `[Variable]`-Eintrag

**Was er NICHT tut:**
- Er erfindet keine fehlenden Inhalte
- Er bewertet nicht, ob der Prozess logisch vollständig ist
- Er schlägt keine zusätzlichen Schritte vor, die im Quellartefakt nicht vorkommen
- Lücken, die bereits im Quellartefakt Lücken waren, bleiben Lücken

Output-Schema (JSON):
```json
{
  "fehlende_entitaeten": [
    {
      "typ": "akteur | system | regel | variable | ausnahme",
      "bezeichnung": "Frau Weber",
      "quelle_slot": "prozessbeschreibung",
      "schweregrad": "warnung"
    }
  ],
  "coverage_vollstaendig": true | false
}
```

Dieser Output wird in `StructuralViolation`-Objekte konvertiert und dem Korrektur-Turn übergeben.

### 3.5 Orchestrator-Erweiterung

In `backend/core/orchestrator.py`: Die bestehende `Flag.return_to_mode`-Logik (aktuell Zeile 262) wird um den Init-Hook erweitert.

```python
# Schritt 10b (NEU) — zwischen advance_phase und return_to_mode
if Flag.return_to_mode in active_flags:
    target_mode = wm.vorheriger_modus or PHASE_TO_MODE.get(wm.aktive_phase, "exploration")

    # Init benötigt? Nur für Structurer und Specifier, nur wenn Artefakt leer
    if self._init_required(target_mode, project):
        log.info("orchestrator.background_init.start", target_mode=target_mode)
        await self._run_background_init(project, wm, target_mode)
        log.info("orchestrator.background_init.complete", target_mode=target_mode)

    # Standard return_to_mode (unverändert)
    wm.aktiver_modus = target_mode
    wm.vorheriger_modus = None
    project.aktiver_modus = target_mode
```

Neue private Methode `_run_background_init`:

```python
_MAX_INIT_TURNS = 8
_MAX_CORRECTION_TURNS = 2

async def _run_background_init(
    self,
    project: Project,
    wm: WorkingMemory,
    target_mode: str,
) -> None:
    init_mode_key = f"init_{target_mode}"  # "init_structuring" | "init_specification"
    init_mode = self._modes.get(init_mode_key)
    if init_mode is None:
        logger.warning("orchestrator.background_init.no_init_mode", key=init_mode_key)
        return

    # Phase 1: Init-Loop
    for turn in range(_MAX_INIT_TURNS):
        context = self._build_init_context(project, wm)
        output = await init_mode.call(context)  # InitModeOutput

        if output.patches:
            source_type = "structure" if target_mode == "structuring" else "algorithm"
            artifact = get_artifact(project, source_type)
            result = self._executor.apply_patches(source_type, artifact, output.patches)
            if result.success:
                set_artifact(project, source_type, result.artifact)

        if output.init_status == InitStatus.init_complete:
            break

    # Phase 2: Python-Validator (immer, deterministisch)
    violations = self._run_structural_validator(project, target_mode)

    # Phase 3: LLM-Coverage-Validator (einmalig, als registrierter Modus)
    coverage_violations = await self._run_coverage_validator(project, wm)
    all_violations = violations + coverage_violations

    # Phase 4: Korrektur-Turns bei kritischen Befunden
    kritische = [v for v in all_violations if v.severity == "kritisch"]
    if kritische:
        await self._run_correction_turns(project, wm, init_mode, kritische)

    # Phase 5: Vertiefungshinweise für Dialog-Modus speichern
    warnungen = [v for v in all_violations if v.severity == "warnung"]
    if warnungen:
        wm.init_hinweise = [v.message for v in warnungen]  # NEU im WorkingMemory

async def _run_coverage_validator(
    self,
    project: Project,
    wm: WorkingMemory,
) -> list[StructuralViolation]:
    """Coverage-Validator als registrierten Modus aufrufen.

    Der Orchestrator hat keinen eigenen LLM-Client — LLM-Zugriff erfolgt
    ausschließlich über registrierte Modi (ADR-008 Option B).
    """
    coverage_mode = self._modes.get("init_coverage_validator")
    if coverage_mode is None:
        logger.warning("orchestrator.background_init.no_coverage_mode")
        return []
    context = self._build_init_context(project, wm)
    output = await coverage_mode.call(context)
    # Coverage-Validator gibt JSON in nutzeraeusserung zurück (kein Dialog-Text)
    try:
        import json
        data = json.loads(output.nutzeraeusserung)
        return [
            StructuralViolation(
                severity=e.get("schweregrad", "warnung"),
                message=f"{e['typ']}: {e['bezeichnung']} (aus {e['quelle_slot']})",
            )
            for e in data.get("fehlende_entitaeten", [])
        ]
    except (json.JSONDecodeError, KeyError):
        logger.warning("orchestrator.coverage_validator.parse_error")
        return []

def _init_required(self, target_mode: str, project: Project) -> bool:
    if target_mode == "structuring":
        return len(project.structure_artifact.schritte) == 0
    if target_mode == "specification":
        return len(project.algorithm_artifact.abschnitte) == 0
    return False
```

### 3.6 Neue Init-Modi

**`backend/modes/init_structuring.py`**: Erbt von `BaseMode`, gibt `ModeOutput` zurück (mit `init_status` gesetzt; `nutzeraeusserung=""`, `phasenstatus=in_progress`, `flags=[]`). Lädt `init_structuring.md`, übergibt Explorations- und Strukturartefakt als Kontext.

**`backend/modes/init_specification.py`**: Analog, lädt `init_specification.md`. Gibt `ModeOutput` zurück (mit `init_status`). Übergibt Struktur- und Algorithmusartefakt als Kontext.

**`backend/modes/init_coverage_validator.py`**: Erbt von `BaseMode`, lädt `init_coverage_validator.md`. Gibt `ModeOutput` zurück, wobei `nutzeraeusserung` ein JSON-String mit dem Coverage-Schema (§3.4) ist — kein menschenlesbarer Text. Der Orchestrator parst diesen JSON-String in `StructuralViolation`-Objekte.

### 3.7 Neue Init-Prompts

**`backend/prompts/init_structuring.md`** — Enthält:
- Mission: Vollständige Transformation des Explorationsartefakts in Strukturschritte
- Pflicht: Jede Information aus allen 7 Slots muss einem Strukturschritt zugeordnet werden
- Variable Lineage: Alle Einträge aus `variablen_und_daten` → `[VAR: name]`-Marker in `beschreibung`
- ANALOG-Kennzeichnung: Analoge Prozessanteile → `spannungsfeld` mit `ANALOG:`-Präfix
- Fortschrittssignal: `init_status: "init_in_progress"` solange Schritte ohne `beschreibung` existieren; `"init_complete"` wenn alle Schritte mindestens `completeness_status: "teilweise"` haben
- Kein Dialog: `nutzeraeusserung: ""`, keine Fragen

**`backend/prompts/init_specification.md`** — Enthält:
- Mission: Vollständige Transformation des Strukturartefakts in Algorithmusabschnitte
- Pflicht: Für jeden Strukturschritt ein `Algorithmusabschnitt` mit vollständigem `kontext` + vorläufigen EMMA-Aktionen
- Variable Lineage: Alle `[VAR: name]`-Marker aus `beschreibung` → `[Variable]`-Einträge im `kontext`
- ANALOG-Handling: `spannungsfeld` mit `ANALOG:` → sofort `WAIT`-Aktion mit `emma_kompatibel: false` anlegen
- Fortschrittssignal: `"init_complete"` wenn alle Abschnitte mindestens `completeness_status: "teilweise"` haben
- Kein Dialog: `nutzeraeusserung: ""`

### 3.8 Dialog-Prompts bereinigen

**`backend/prompts/structuring.md`**: Erstaktivierungs-Sektion entfernen. Ersetzen durch: `"Das Strukturartefakt ist bereits durch die System-Initialisierung vorbelegt. Prüfe den aktuellen Stand und beginne sofort mit der Vertiefung des ersten unvollständigen Schritts."`

**`backend/prompts/specification.md`**: Erstaktivierungs-Sektion entfernen. Analog ersetzen.

### 3.9 WorkingMemory-Erweiterung

`backend/core/working_memory.py`: Neues optionales Feld:

```python
init_hinweise: list[str] = Field(default_factory=list)
# Warnungen aus der Init-Validierung — werden dem Dialog-Modus als Starterkontext mitgegeben
```

Der Dialog-Modus (Structurer/Specifier) liest `wm.init_hinweise` und nennt dem Nutzer gleich zu Beginn die Bereiche, die noch Vertiefung brauchen.

### 3.10 SDD-Konsistenz / ADR

**Abweichung von SDD §6.3 (11-Schritt-Zyklus):** Der Zyklus setzt voraus, dass jeder Turn genau einem Nutzerturn entspricht. `_run_background_init` führt intern mehrere LLM-Calls aus, ohne entsprechende Nutzereingaben. Das ist eine bewusste Abweichung.

**ADR-008: Background-Init als Inline-Multi-Call im Orchestrator-Turn**

- **Kontext**: SDD §6.3 definiert den Orchestrator-Zyklus als 1 Nutzereingabe → 1 LLM-Call → 1 Response. Die Init-Loop benötigt mehrere LLM-Calls ohne Nutzereingabe.
- **Entscheidung**: Init-Calls laufen inline im `process_turn`-Aufruf des `return_to_mode`-Turns. Kein separater Mechanismus (keine WebSocket-Events, keine Background-Tasks). Der Turn dauert länger, liefert aber ein vollständig initialisiertes Artefakt.
- **Begründung**: Inline ist die einfachste Lösung ohne neue Infrastruktur. Timeout-Budget: `MAX_INIT_TURNS=8 × ~5s ≈ 40s`. Browser-WebSocket-Inaktivitäts-Timeouts (Chrome, Firefox) liegen bei 60–120s; typische Load-Balancer-Timeouts (nginx default: 60s, AWS ALB default: 60s) liegen deutlich über 40s. Das Budget ist konservativ. Primärer Mitigation-Hebel: `MAX_INIT_TURNS` ist über `Settings` konfigurierbar — Reduktion auf 4–5 reduziert Budget auf ~20–25s falls nötig. Realistischer Erwartungswert für einfache Prozesse (<10 Schritte): 2–3 Turns (~10–15s). Alternative (Background-Tasks) würde neue Zustandsverwaltung, Locking und WebSocket-Events erfordern — unverhältnismäßig für den aktuellen Reifegrad.
- **Konsequenzen**: Turn-Latenz des `return_to_mode`-Turns steigt. Monitoring via bestehendes Token-Tracking. SDD §6.3 wird nach Verifikation um Init-Loop-Beschreibung ergänzt.

---

## 3a. Abhängigkeiten & Konflikte

- **CR-002 (Implementiert)**: Fügte `regeln`, `schleifenkoerper`, `abbruchbedingung`, `konvergenz` hinzu — Init-Prompts müssen diese Felder korrekt befüllen. Kein Konflikt, Abhängigkeit.
- **CR-003 (Verifiziert)**: Definiert 7 Slots inkl. `variablen_und_daten` und `entscheidungen_und_schleifen` — Init-Structuring-Prompt liest alle 7. Kein Konflikt.
- **CR-004 (Implementiert)**: Letzter Rewrite von `structuring.md` — Erstaktivierungs-Sektion wird in diesem CR entfernt. Kein inhaltlicher Konflikt, aber direkter Eingriff in die von CR-004 erzeugte Datei.
- **CR-005 (Überholt)**: Vollständig absorbiert. Kein Konflikt.

---

## 4. Änderungsplan

| # | Datei | Änderung |
|---|---|---|
| 1 | `backend/artifacts/models.py` | `InitStatus` (StrEnum: `init_in_progress`/`init_complete`) hinzufügen — `InitModeOutput` entfällt |
| 2 | `backend/modes/base.py` | `ModeOutput` um optionales Feld `init_status: InitStatus \| None = None` ergänzen |
| 3 | `backend/core/working_memory.py` | Neues Feld `init_hinweise: list[str]` mit Default `[]` |
| 4 | `backend/artifacts/init_validator.py` (neu) | Python-Validator: `validate_structure_artifact()` und `validate_algorithm_artifact()` gemäß §3.3 |
| 5 | `backend/prompts/init_coverage_validator.md` (neu) | LLM-Coverage-Validator-Prompt gemäß §3.4 — nur Coverage-Check, kein Content-Inventing |
| 6 | `backend/modes/init_structuring.py` (neu) | Init-Modus Structurer: erbt von `BaseMode`, gibt `ModeOutput` zurück (mit `init_status`) |
| 7 | `backend/modes/init_specification.py` (neu) | Init-Modus Specifier: erbt von `BaseMode`, gibt `ModeOutput` zurück (mit `init_status`) |
| 8 | `backend/modes/init_coverage_validator.py` (neu) | Coverage-Validator-Modus: erbt von `BaseMode`, gibt `ModeOutput` zurück (JSON in `nutzeraeusserung`) |
| 9 | `backend/prompts/init_structuring.md` (neu) | Init-Prompt Structurer gemäß §3.7: vollständige Transformation, Variable Lineage, ANALOG-Flags |
| 10 | `backend/prompts/init_specification.md` (neu) | Init-Prompt Specifier gemäß §3.7: vollständige Transformation, Variablen-Übergabe, ANALOG-Handling |
| 11 | `backend/core/orchestrator.py` | `_init_required()`, `_run_background_init()`, `_run_coverage_validator()` hinzufügen; `Flag.return_to_mode`-Block um Init-Hook erweitern gemäß §3.5 |
| 12 | `backend/api/websocket.py` | In `_build_orchestrator()`: Init-Modi registrieren — `"init_structuring"`, `"init_specification"`, `"init_coverage_validator"` |
| 13 | `backend/prompts/structuring.md` | Erstaktivierungs-Sektion (§ "Erstaktivierung", ca. 25 Zeilen) entfernen, durch Kurzanweisung "Artefakt bereits vorhanden" ersetzen |
| 14 | `backend/prompts/specification.md` | Erstaktivierungs-Sektion entfernen, durch Kurzanweisung ersetzen |

**Reihenfolge**: #1–4 (Modell/Infrastruktur) → #5–10 (Prompts + Modi) → #11–12 (Orchestrator + Registrierung) → #13–14 (Dialog-Prompts bereinigen)

---

## 5. Risiken und Mitigationen

### R-1: Turn-Latenz beim return_to_mode-Turn

**Risiko**: MAX_INIT_TURNS=8 × ~5s pro Call = bis zu 40s Wartezeit für den Nutzer.

**Mitigation**: MAX_INIT_TURNS ist konfigurierbar (Settings). Realistisch: einfache Prozesse (<10 Schritte) sind in 2–3 Turns fertig (~10–15s). WebSocket-Verbindung bleibt offen. Optional später: Streaming-Progress-Events (separater CR). Fallback: Wenn MAX_INIT_TURNS erreicht und nicht alle Elemente initialisiert — Dialog-Modus startet trotzdem, `init_hinweise` enthält Liste offener Elemente.

### R-2: Init-Loop generiert fehlerhafte Patches

**Risiko**: Init-Modus erzeugt inkonsistente IDs oder ungültige Patch-Pfade.

**Mitigation**: Bestehender `Executor` mit Template-Schema-Validierung läuft weiterhin für jeden Init-Patch. Fehlerhafte Patches werden abgelehnt (existing behavior). Python-Validator nach der Loop deckt verbleibende Inkonsistenzen auf. Korrektur-Turns reparieren kritische Befunde.

### R-3: Coverage-Validator meldet false positives

**Risiko**: Der Coverage-Validator findet "fehlende" Entitäten, die eigentlich vorhanden sind (Namensvariation, Abkürzungen).

**Mitigation**: Der Validator gibt nur `schweregrad: "warnung"`, nie `"kritisch"` — Warnungen lösen keine Korrektur-Turns aus, sondern nur `init_hinweise`. Der Dialog-Modus kann sie mit dem Nutzer klären. Keine automatische Korrektur basierend auf Coverage-Warnungen.

### R-4: Init-Prompts weichen vom Quellartefakt ab (Halluzination)

**Risiko**: Der Init-Modus erfindet Strukturschritte, die im Explorationsartefakt nicht vorkommen.

**Mitigation**: Init-Prompts enthalten explizite Negative-Constraint: "Erstelle KEINE Strukturschritte für Informationen, die nicht im Explorationsartefakt enthalten sind." Der Coverage-Validator prüft in die andere Richtung (Was fehlt), nicht ob Extra-Inhalte vorhanden sind — Extra-Inhalte werden vom Dialog-Modus im Nutzergespräch auffallen.

### R-5: Bestehende Tests brechen

**Risiko**: Orchestrator-Tests oder Modus-Tests erwarten das alte Verhalten ohne Init-Loop.

**Mitigation**: `_init_required()` gibt `False` zurück wenn das Zielartefakt nicht leer ist — bestehende Tests die mit vorhandenen Artefakten arbeiten, sehen keine Verhaltensänderung. Neue Tests für Init-Modi werden isoliert geschrieben.

---

## 6. Nicht im Scope

- **WebSocket Progress-Events während Init**: Technisch machbar, aber separater CR. Aktuell: Nutzer wartet auf komplette Response.
- **Init für Explorer-Phase**: Explorer startet mit leerem Artefakt — kein Quellartefakt vorhanden, kein Init sinnvoll.
- **Init für Validierungs-Phase**: Validierung arbeitet auf vorhandenen Artefakten, hat eigene Aktivierungslogik.
- **`spannungsfeld`-Downstream-Reporting**: Was nach der Strukturierung mit `spannungsfeld`-Einträgen im Reporting passiert, ist separater CR.
- **Parallelisierung der Init-Calls**: Init-Calls sequenziell. Parallelisierung für unabhängige Schritte wäre Optimierung (separater CR).

---

## 7. Abnahmekriterien

1. Nach `Flag.return_to_mode` für "structuring": `project.structure_artifact.schritte` ist nicht leer.
2. Nach `Flag.return_to_mode` für "specification": `project.algorithm_artifact.abschnitte` ist nicht leer — für jeden Strukturschritt existiert ein Abschnitt.
3. Alle `nachfolger`-IDs in `structure_artifact.schritte` referenzieren existierende Schritte (Python-Validator: keine `kritisch`-Verletzungen nach Init).
4. Alle Einträge aus `variablen_und_daten` haben einen korrespondierenden `[Variable]`-Eintrag in mindestens einem `kontext`-Feld des Algorithmusartefakts.
5. Strukturschritte mit analogem `spannungsfeld` (`ANALOG:`) haben in ihrem Algorithmusabschnitt mindestens eine `emma_kompatibel: false`-Aktion.
6. `structuring.md` enthält keine Erstaktivierungs-Sektion mehr.
7. `specification.md` enthält keine Erstaktivierungs-Sektion mehr.
8. Die Init-Loop gibt `init_status: "complete"` innerhalb von MAX_INIT_TURNS=8 für einen Standardprozess mit ≤15 Schritten.
9. `wm.init_hinweise` ist nach der Init-Loop befüllt, wenn Validierungswarnungen vorliegen.
10. Der Dialog-Modus (Structurer/Specifier) nennt zu Beginn die `init_hinweise` wenn vorhanden.
11. Alle bestehenden Tests in `test_structuring_mode.py`, `test_specification_mode.py` und `test_orchestrator.py` sind weiterhin grün. Insbesondere: `test_orchestrator.py:_make_default_modes()` (Zeile 51–58) enthält `init_structuring`, `init_specification` und `init_coverage_validator`; Tests `test_phase_complete_triggers_moderator_then_advance` (ca. Zeile 813) und `test_phase_transition_advances_directly_to_primary_mode` (ca. Zeile 947) laufen mit dem neuen Init-Hook durch.
12. Neuer `test_init_validator.py`: Python-Validator erkennt alle 6 Prüfkategorien korrekt (Unit-Tests mit Fixtures).
13. SDD §6.3 (11-Schritt-Zyklus, neuer Schritt 10b Init-Loop), §6.5.2 (Init-Modi als Sonderfall), §6.6 (kognitives Modus-Verzeichnis — neuer Abschnitt §6.6.6 Init-Submodi) nach Verifikation aktualisiert.

---

## 8. Aufwandsschätzung

| Feld | Wert |
|---|---|
| **Komplexität** | L (11 neue/geänderte Python-Dateien, 4 neue Prompt-Dateien, Breaking-Change in Orchestrator-Flow) |
| **Betroffene Dateien** | 14 |
| **Breaking Change** | Ja — `return_to_mode`-Verhalten des Orchestrators ändert sich; bestehende Integrationstests die Phase-Transitions testen müssen angepasst werden |

| Phase | Dateien | Komplexität |
|---|---|---|
| Modell / Infrastruktur | `models.py`, `working_memory.py`, `init_validator.py` | M |
| Init-Modi | `init_structuring.py`, `init_specification.py` | S |
| Init-Prompts | `init_structuring.md`, `init_specification.md`, `init_coverage_validator.md` | M |
| Orchestrator | `orchestrator.py` | M |
| Registrierung | `api/websocket.py` | S |
| Dialog-Prompt-Cleanup | `structuring.md`, `specification.md` | S |
| Tests | `test_init_validator.py` (neu), ggf. `test_orchestrator.py` (anpassen) | M |
