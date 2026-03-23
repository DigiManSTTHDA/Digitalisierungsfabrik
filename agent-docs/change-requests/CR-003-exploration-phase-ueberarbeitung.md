# CR-003: Überarbeitung der Explorationsphase — Slot-Konsolidierung und Kontrollfluss-Vorbereitung

| Feld | Wert |
|---|---|
| **ID** | CR-003 |
| **Titel** | Überarbeitung der Explorationsphase — Slot-Konsolidierung und Kontrollfluss-Vorbereitung |
| **Status** | Freigegeben |
| **Erstellt** | 2026-03-23 |
| **Priorität** | Hoch |
| **Auslöser** | Praxis-Feedback: Exploration-Slots sind zu akademisch, generieren Fragen die Fachexperten nicht beantworten können, und zerreißen zusammengehörende Informationen |
| **Abhängigkeiten** | Setzt voraus: CR-002 (Kontrollfluss-Modellierung im Strukturartefakt, Status: Implementiert) |

---

## 1. Problemstellung

### Kernproblem

Die aktuelle Explorationsphase arbeitet mit 9 Pflicht-Slots, von denen mehrere zu abstrakt formuliert sind. Dies führt dazu, dass das LLM Fragen stellt, die Fachexperten nicht intuitiv beantworten können. Gleichzeitig werden zusammengehörende Informationen auf separate Slots verteilt, was dem nachgelagerten Strukturierungsmodus die Arbeit erschwert.

### Konkrete Defizite

**D-1: Abstrakte Slots generieren unbrauchbare Fragen.**
Der Slot `randbedingungen` ("Welche Regeln, Fristen oder Einschränkungen gelten?") klingt nach einem Formular, nicht nach einem Interview. Ein Fachexperte antwortet natürlich: "Der Rechnungsbetrag muss innerhalb von 10 Tagen mit 2% Skonto bezahlt werden" — aber nur, wenn man ihn fragt "Was passiert nachdem Sie die Rechnung geprüft haben?", nicht "Welche Randbedingungen gelten?".

Betroffene Slots: `randbedingungen`, `umgebung`, `scope`.

**D-2: Informationen werden aus dem Prozesskontext gerissen.**
Ausnahmen (`ausnahmen`-Slot) werden isoliert vom Prozessablauf dokumentiert. Wenn der Nutzer sagt "Bei Gutschriften läuft das anders", gehört das in die Prozessbeschreibung — dort wo der Kontrollfluss abweicht. Isoliert im `ausnahmen`-Slot fehlt dem Structurer der Kontext, wann und wo die Ausnahme greift.

Beispiel IST-Zustand:
```json
{
  "prozessbeschreibung": {"inhalt": "Rechnungen werden in DATEV erfasst und geprüft."},
  "ausnahmen": {"inhalt": "Gutschriften werden anders behandelt."},
  "randbedingungen": {"inhalt": "Skontofrist 10 Tage, 2%."}
}
```
→ Der Structurer muss rekonstruieren, wo "anders behandelt" im Ablauf passiert und wo die Skontofrist relevant wird.

**D-3: Kontrollfluss wird nicht aktiv herausgearbeitet.**
Entscheidungspunkte ("Wenn der Betrag über 5.000€ liegt...") und Schleifen ("Für jede Rechnung im Stapel...") werden nicht gezielt erfragt. Der Structurer muss diese Strukturen aus Freitext erschließen, obwohl der Explorer sie mit gezielten Fragen leicht herausarbeiten könnte.

**D-4: Variablen-Kandidaten werden nicht erkannt.**
Wenn der Nutzer sagt "Ich prüfe die Rechnungsnummer und den Betrag", sind "Rechnungsnummer" und "Betrag" Variablen-Kandidaten, die in der Spezifikationsphase als EMMA-Parameter relevant werden. Aktuell gehen diese unter.

**D-5: Prompt-Struktur hat Schwächen.**
- Kein klarer Rolleneinstieg ("Du bist ein explorativer Prozessanalyst")
- Redundanzen (Artefakt-als-Langzeitgedächtnis wird 2x erklärt)
- Widerspruchserkennung fehlt als Kernregel
- Explorativer Fokus unklar: Es fehlt die Abgrenzung "Breite vor Tiefe" vs. "algorithmische Details"

**D-6: `umgebung`-Slot vermischt Technisches mit Organisatorischem.**
"Abteilung, Standort, Teamgröße" sind organisatorische Rahmendaten, die für die RPA-Automatisierung irrelevant sind. Technische Umgebung (Browser, Citrix, Desktop-App) gehört zu `beteiligte_systeme`.

### Auswirkungen

Ohne Änderung: Der Structurer erhält weiterhin fragmentierte, kontextlose Informationen und muss implizite Zusammenhänge rekonstruieren. Die Qualität der Strukturierung leidet. Der Nutzer wird mit abstrakten Fragen konfrontiert, was die Dialogqualität mindert.

---

## 2. Ziel der Änderung

- **Slots von 9 auf 7 konsolidieren**: Abstrakte Slots entfernen, `prozessbeschreibung` als Hauptcontainer stärken
- **Kontrollfluss-Vorbereitung**: Neuer Slot `entscheidungen_und_schleifen` der Entscheidungspunkte und Iterationen gezielt erfasst
- **Variablen-Erkennung**: Neuer Slot `variablen_und_daten` für Daten die pro Prozessdurchlauf variieren
- **Prompt-Qualität**: Klare Rollenidentität, gestraffte Struktur, bessere sokratische Beispielfragen, Widerspruchserkennung
- **Downstream-Kompatibilität**: Structurer erhält reichhaltigere, kontextbezogene Informationen

---

## 3. Lösung

### 3.1 Slot-Konsolidierung (9 → 7)

**Entfernte Slots:**

| Slot | Verbleib der Informationen |
|---|---|
| `scope` | → `prozessbeschreibung` (Anfang und Ende des Prozesses werden natürlich in der Ablaufbeschreibung miterfasst) |
| `umgebung` | Technischer Teil → `beteiligte_systeme`. Organisatorischer Teil (Abteilung, Standort, Teamgröße) entfällt als eigener Slot — wird in `prozessbeschreibung` miterfasst wenn vom Nutzer erwähnt |
| `randbedingungen` | → `prozessbeschreibung` (Regeln, Fristen, Schwellenwerte gehören in den Prozesskontext wo sie wirken) |
| `ausnahmen` | → `prozessbeschreibung` (Sonderfälle gehören dorthin wo der Kontrollfluss abweicht) |

**Neue Slots:**

| Slot | Zweck | Was gehört rein? |
|---|---|---|
| `entscheidungen_und_schleifen` | Kontrollfluss-Vorbereitung für Structurer | Erkannte Entscheidungspunkte ("Wenn Betrag > 5.000€ → Freigabe nötig"), Schleifen ("Für jede Rechnung im Stapel"), Verzweigungen. Wird vom LLM aus der Prozessbeschreibung extrahiert und explizit formuliert. |
| `variablen_und_daten` | Variable-Kandidaten für Spezifikation | Datenfelder die pro Durchlauf wechseln: Rechnungsnummer, Betrag, Lieferantenname, Bestellnummer. Format: `Name — Beschreibung, Quelle` |

**Resultierende 7 Pflicht-Slots:**

| slot_id | Titel | Beschreibung |
|---|---|---|
| `prozessausloeser` | Prozessauslöser | Was löst den Prozess aus? Ereignis, Trigger, Häufigkeit. |
| `prozessziel` | Prozessziel | Was ist das gewünschte Endergebnis? Woran erkennt man Erfolg? |
| `prozessbeschreibung` | Prozessbeschreibung | **Hauptcontainer.** Ablaufschritte, Reihenfolge, Akteure, Regeln, Fristen, Schwellenwerte, Sonderfälle, Ausnahmen, Mengen, Dauer, Schmerzpunkte, Medienbrüche — alles was den Prozess beschreibt. |
| `entscheidungen_und_schleifen` | Entscheidungen und Schleifen | Erkannte Kontrollfluss-Strukturen: Entscheidungspunkte mit Bedingungen, Schleifen/Iterationen über Mengen, Verzweigungen. Vom LLM aus Nutzeraussagen extrahiert. |
| `beteiligte_systeme` | Beteiligte Systeme | IT-Systeme, Software, Hardware, Schnittstellen, Zugangswege (Browser, Desktop-App, Citrix), technische Umgebung. Nur Technik, keine Organisationsstruktur. |
| `variablen_und_daten` | Variablen und Daten | Datenfelder die pro Prozessdurchlauf variieren (Rechnungsnummer, Betrag, Datum, etc.). Format: `Name — Beschreibung, Quelle`. Kandidaten für EMMA-Parameter. |
| `prozesszusammenfassung` | Prozesszusammenfassung | Kompakte Zusammenfassung (2–4 Sätze) — wird vom LLM selbst formuliert bei `nearing_completion`. |

### 3.2 JSON-Beispiel SOLL-Zustand

```json
{
  "slots": {
    "prozessausloeser": {
      "slot_id": "prozessausloeser",
      "titel": "Prozessauslöser",
      "inhalt": "Eingehende Rechnungen per Post, E-Mail oder Lieferantenportal. Ca. 200 Rechnungen/Monat. Schwerpunkt Monatsanfang.",
      "completeness_status": "vollstaendig"
    },
    "prozessziel": {
      "slot_id": "prozessziel",
      "titel": "Prozessziel",
      "inhalt": "Jede Rechnung ist in DATEV erfasst, geprüft, freigegeben und zur Zahlung angewiesen. Skonto wird ausgenutzt wenn möglich.",
      "completeness_status": "vollstaendig"
    },
    "prozessbeschreibung": {
      "slot_id": "prozessbeschreibung",
      "titel": "Prozessbeschreibung",
      "inhalt": "Rechnungen werden per Post (Scan über ScanPlus) oder per E-Mail empfangen. Frau Weber erfasst jede Rechnung in DATEV: Lieferant, Rechnungsnummer, Betrag, Fälligkeitsdatum. Dann Abgleich mit Bestellung im ELO-Archiv. Bei Übereinstimmung: Kontierung und Freigabe-Workflow. Bei Abweichung: Rückfrage an Einkauf per E-Mail. Rechnungen über 5.000€ brauchen zusätzliche Freigabe durch Abteilungsleiter Herrn Müller. Skontofrist 10 Tage (2%) — wird von Frau Weber manuell im Kalender überwacht. Gutschriften laufen über einen separaten Pfad: werden direkt in DATEV als Gutschrift verbucht ohne Freigabe-Workflow. Zahlungslauf jeden Freitag.",
      "completeness_status": "vollstaendig"
    },
    "entscheidungen_und_schleifen": {
      "slot_id": "entscheidungen_und_schleifen",
      "titel": "Entscheidungen und Schleifen",
      "inhalt": "ENTSCHEIDUNG: Stimmt der Rechnungsbetrag mit der Bestellung überein? → Ja: Kontierung. Nein: Rückfrage an Einkauf. ENTSCHEIDUNG: Ist der Betrag über 5.000€? → Ja: Zusätzliche Freigabe Abteilungsleiter. Nein: Direkte Freigabe. ENTSCHEIDUNG: Ist es eine Gutschrift statt einer Rechnung? → Ja: Separater Verbuchungspfad ohne Freigabe. SCHLEIFE: Jede Rechnung im Tagesstapel wird einzeln abgearbeitet (ca. 10 pro Tag).",
      "completeness_status": "vollstaendig"
    },
    "beteiligte_systeme": {
      "slot_id": "beteiligte_systeme",
      "titel": "Beteiligte Systeme",
      "inhalt": "DATEV Rechnungswesen (Desktop-App, Zugang über Citrix). ELO DMS für Archivierung und Bestellabgleich (Browser). ScanPlus für Post-Digitalisierung (Desktop-App). Outlook für E-Mail-Rechnungen und Rückfragen. Kein automatischer Datenfluss zwischen den Systemen — alles Copy-Paste.",
      "completeness_status": "vollstaendig"
    },
    "variablen_und_daten": {
      "slot_id": "variablen_und_daten",
      "titel": "Variablen und Daten",
      "inhalt": "Rechnungsnummer — eindeutige Kennung auf der Rechnung, Quelle: Rechnungsdokument. Rechnungsbetrag — Bruttobetrag in EUR, Quelle: Rechnungsdokument. Lieferantenname — Name des Rechnungsstellers, Quelle: Rechnungsdokument. Bestellnummer — Referenz auf die Bestellung, Quelle: Rechnungsdokument oder ELO. Fälligkeitsdatum — Zahlungsfrist, Quelle: Rechnungsdokument. Skontobetrag — berechneter Skontowert (2% des Bruttobetrags), Quelle: Berechnung.",
      "completeness_status": "teilweise"
    },
    "prozesszusammenfassung": {
      "slot_id": "prozesszusammenfassung",
      "titel": "Prozesszusammenfassung",
      "inhalt": "Der Rechnungseingangsprozess wird durch eingehende Rechnungen per Post, E-Mail oder Portal ausgelöst. Frau Weber erfasst jede Rechnung in DATEV, gleicht sie mit Bestellungen im ELO-Archiv ab und leitet die Freigabe ein. Bei Beträgen über 5.000€ ist eine Abteilungsleiter-Freigabe erforderlich. Der Prozess endet mit der Zahlungsanweisung im wöchentlichen Zahlungslauf.",
      "completeness_status": "leer"
    }
  },
  "version": 12
}
```

### 3.3 Prompt-Änderungen (`backend/prompts/exploration.md`)

**Kompletter Rewrite** des Prompts mit folgenden strukturellen Änderungen:

**a) Rolleneinstieg (neu):**
Erster Absatz definiert sofort die Rolle: "Du bist ein explorativer Prozessanalyst im Rahmen der Digitalisierungsfabrik." Dann Überleitung zum Systemkontext.

**b) Redundanzen straffen:**
- "Artefakt = Langzeitgedächtnis" wird 1x erklärt, nicht 2x
- Wiederholungen zu "der Nutzer ist kein Programmierer" konsolidieren
- Terminologie-Tabelle enthält nur die neuen 7 Slots

**c) Neue Kernregel: Widerspruchserkennung:**
```
Wenn der Nutzer Widersprüche zu bereits dokumentierten Informationen generiert:
- Lass diese NICHT einfach stehen
- Frage aktiv nach und löse sie im Dialog auf
- Vergleiche stets alle Informationen im Artefakt mit den Nutzerangaben
- Unterscheide zwischen echten Widersprüchen (müssen aufgelöst werden)
  und Ergänzungen/Details (können koexistieren)
```

**d) Neue Kernregel: Kontrollfluss herausarbeiten:**
```
Arbeite aktiv Entscheidungen und Schleifen aus den Nutzeraussagen heraus.
Wenn der Nutzer sagt "dann prüfe ich ob..." → erkenne die Entscheidung.
Wenn der Nutzer sagt "für jede Rechnung..." → erkenne die Schleife.
Formuliere diese explizit im Slot entscheidungen_und_schleifen.
```

**e) Neue Kernregel: Variablen erkennen:**
```
Wenn der Nutzer Datenfelder erwähnt die pro Durchlauf variieren
(Rechnungsnummer, Betrag, Name, Datum, etc.), dokumentiere diese
als Variablen-Kandidaten im Slot variablen_und_daten.
```

**f) Explorativer Fokus klarstellen:**
```
Dein Fokus ist BREITE vor TIEFE. Du willst den Gesamtprozess verstehen,
nicht einzelne Schritte bis ins algorithmische Detail vertiefen. Das kommt
in der nächsten Phase (Strukturierung). Hier geht es darum, möglichst viel
über den Prozess zu erfahren — besonders Entscheidungen und Schleifen.
```

**g) Bessere sokratische Beispielfragen:**
```
Beispiele für gute Explorationsfragen:
- "Sie haben erwähnt, dass Sie die Rechnungen prüfen. Gibt es dabei eine
  Prüfung, bei der Sie entscheiden müssen — also wo es verschiedene Wege
  gibt je nach Ergebnis?"
- "Bearbeiten Sie die Rechnungen einzeln nacheinander, oder gibt es einen
  Stapel den Sie abarbeiten? Wie viele sind das typischerweise?"
- "Was passiert, wenn bei der Prüfung etwas nicht stimmt? Gibt es einen
  festen Ablauf dafür oder entscheiden Sie spontan?"
- "Welche Daten von der Rechnung brauchen Sie für Ihre Arbeit? Welche
  Nummern, Beträge oder Namen tippen Sie irgendwo ein?"
```

**h) Slot-Referenztabelle aktualisiert auf 7 Slots** (siehe §3.1)

**i) Patch-Beispiele aktualisiert** — neue Beispiele für `entscheidungen_und_schleifen` und `variablen_und_daten`:
```json
{"op": "replace", "path": "/slots/entscheidungen_und_schleifen/inhalt", "value": "ENTSCHEIDUNG: Stimmt der Rechnungsbetrag mit der Bestellung überein? → Ja: Kontierung. Nein: Rückfrage an Einkauf."}
{"op": "replace", "path": "/slots/entscheidungen_und_schleifen/completeness_status", "value": "teilweise"}

{"op": "replace", "path": "/slots/variablen_und_daten/inhalt", "value": "Rechnungsnummer — eindeutige Kennung, Quelle: Rechnungsdokument. Rechnungsbetrag — Bruttobetrag in EUR, Quelle: Rechnungsdokument."}
{"op": "replace", "path": "/slots/variablen_und_daten/completeness_status", "value": "teilweise"}
```

### 3.4 Abwärtskompatibilität

**Bestehende Artefakte:** Da die Slot-Struktur des `ExplorationArtifact` ein `dict[str, ExplorationSlot]` ist (keine festen Felder im Pydantic-Modell), ist die Änderung **nicht breaking auf Modellebene**. Die Slots werden dynamisch erzeugt über `PFLICHT_SLOTS` in `exploration.py`.

- Bestehende Projekte mit alten 9 Slots: Alte Slot-Daten bleiben erhalten, werden aber nicht mehr als Pflicht-Slots geführt. Beim nächsten Turn in der Explorationsphase werden die neuen Pflicht-Slots per `_build_init_patches()` hinzugefügt.
- Bestehende Projekte in späteren Phasen: Keine Auswirkung — das Explorationsartefakt ist dort read-only.

**Migration:** Keine Datenmigration nötig. Alte Slots bleiben im Artefakt, werden aber nicht mehr aktiv genutzt.

### 3.5 SDD-Konsistenz

Die SDD §5.3 definiert 8 Pflicht-Slots (plus `prozesszusammenfassung`). Dieser CR ändert die Slot-Zusammensetzung, was eine **gewünschte Abweichung** von der SDD darstellt.

### ADR: Konsolidierung der Explorations-Pflicht-Slots

**Kontext:** SDD §5.3 definiert die Pflicht-Slots des Explorationsartefakts als: `prozessausloeser`, `prozessziel`, `scope`, `beteiligte_systeme`, `umgebung`, `randbedingungen`, `ausnahmen`, `prozesszusammenfassung` (plus `prozessbeschreibung` im Prompt). In der Praxis führen die Slots `scope`, `umgebung`, `randbedingungen` und `ausnahmen` zu abstrakten Fragen die Fachexperten schlecht beantworten können. Gleichzeitig fehlt eine gezielte Erfassung von Kontrollfluss-Strukturen, die der Structurer (besonders nach CR-002) dringend braucht.

**Entscheidung:** Die Pflicht-Slots werden von 9 auf 7 konsolidiert. `scope`, `umgebung`, `randbedingungen`, `ausnahmen` werden entfernt; ihre Inhalte fließen in `prozessbeschreibung` und `beteiligte_systeme`. Zwei neue Slots werden eingeführt: `entscheidungen_und_schleifen` (Kontrollfluss-Vorbereitung für Structurer) und `variablen_und_daten` (Variable-Kandidaten für Spezifikation).

**Begründung:** (1) Pragmatischere Interaktion: Alle Fragen leiten sich aus dem natürlichen Prozessablauf ab, statt abstrakte Kategorien abzufragen. (2) Besserer Informationsfluss: Zusammengehörende Informationen bleiben im Kontext (Ausnahmen dort wo sie auftreten, Regeln dort wo sie wirken). (3) Kontrollfluss-Synergie mit CR-002: Der Structurer erhält vorstrukturierte Entscheidungen und Schleifen, die direkt in `regeln`, `schleifenkoerper` und `abbruchbedingung` überführbar sind. (4) Variablen-Frühkennung: EMMA-Parameter-Kandidaten werden schon in der Exploration identifiziert.

**Konsequenzen:** SDD §5.3 (Pflicht-Slots-Tabelle) muss nach Implementierung aktualisiert werden. FR-B-00 AK(1) ("alle Pflicht-Slots gemäß Abschnitt 5.3") bleibt formal gültig, da die Referenz auf §5.3 zeigt, das dann die neuen 7 Slots enthält. Alle Backend-Tests die auf die alten 9 Slots referenzieren müssen angepasst werden.

### 3.6 ADR-Konsistenz

- **ADR-006 (EMMA Parameter Schema, CR-002):** Nicht direkt betroffen, aber der neue Slot `variablen_und_daten` erzeugt einen natürlichen Vorbereitungsschritt für die `parameter: dict[str, str]`-Befüllung in der Spezifikation.
- Alle anderen ADRs (001–005, 007–009): Nicht betroffen.

---

## 3a. Abhängigkeiten & Konflikte

**CR-002 (Status: Implementiert):**
- CR-002 führt `regeln`, `schleifenkoerper`, `abbruchbedingung`, `konvergenz` im Strukturartefakt ein.
- CR-003 ist **komplementär**: Der neue Exploration-Slot `entscheidungen_und_schleifen` liefert dem Structurer genau die Eingangsinformationen, die er braucht um die CR-002-Felder sinnvoll zu befüllen.
- **Kein Konflikt.** CR-003 verändert das Strukturartefakt nicht.

**CR-002-Implementierung (unstaged changes):**
- Die aktuell auf dem Branch liegenden, uncommitteten Änderungen aus CR-002 betreffen `structuring.py` Zeile 83, die alte Exploration-Slot-Namen referenziert (`prozessbeschreibung, prozessausloeser, ausnahmen, randbedingungen`).
- **Auflösung:** CR-003 aktualisiert diese Referenz auf die neuen Slot-Namen. CR-002 muss erst committing werden, bevor CR-003 implementiert wird.

---

## 4. Änderungsplan

### Phase 1: Prompt

| # | Datei | Änderung |
|---|---|---|
| 1 | `backend/prompts/exploration.md` | Kompletter Rewrite gemäß §3.3 (a–i). Alle `@@@`-Kommentare entfernen. Neue Slot-Tabelle mit 7 Slots. Neue sokratische Beispielfragen. Widerspruchserkennung als Kernregel. Kontrollfluss-Extraktion als Kernregel. Variablen-Erkennung als Kernregel. Explorativer Fokus (Breite vor Tiefe). |

### Phase 2: Backend-Code

| # | Datei | Änderung |
|---|---|---|
| 2 | `backend/modes/exploration.py` | `PFLICHT_SLOTS` dict von 9 auf 7 Einträge ändern: `scope`, `umgebung`, `randbedingungen`, `ausnahmen` entfernen; `entscheidungen_und_schleifen: "Entscheidungen und Schleifen"` und `variablen_und_daten: "Variablen und Daten"` hinzufügen. Docstring von "9 Pflicht-Slots" auf "7 Pflicht-Slots" ändern. |
| 3 | `backend/modes/structuring.py` | Zeile 83: Referenz `"(prozessbeschreibung, prozessausloeser, ausnahmen, randbedingungen)"` aktualisieren auf `"(prozessbeschreibung, prozessausloeser, entscheidungen_und_schleifen, variablen_und_daten)"` |

### Phase 3: Tests

| # | Datei | Änderung |
|---|---|---|
| 4 | `backend/tests/test_exploration_mode.py` | `test_first_turn_initializes_pflicht_slots`: `expected_ids` Set von 9 auf 7 aktualisieren (alte Slots raus, neue rein). Kommentar "9 Pflicht-Slots" → "7 Pflicht-Slots". |
| 5 | `backend/tests/test_exploration_mode.py` | `test_second_turn_does_not_reinitialize_slots`: `expected_ids` Set analog anpassen. `len() == 9` → `len() == 7`. Kommentare anpassen. |
| 6 | `backend/tests/test_exploration_mode.py` | `test_build_slot_status_shows_leer_for_uninitialized_slots`: Titel-Tuple aktualisieren — `"Scope"`, `"Umgebung"`, `"Randbedingungen"`, `"Ausnahmen"` entfernen; `"Entscheidungen und Schleifen"`, `"Variablen und Daten"` hinzufügen. `len(lines) == 9` → `len(lines) == 7`. |
| 7 | `backend/tests/test_exploration_mode.py` | `test_nearing_completion_phasenstatus_when_all_slots_filled`: Verwendet `PFLICHT_SLOTS.items()` — passt sich automatisch an, keine Code-Änderung nötig. Aber Kommentar "all 9 Pflicht-Slots" → "all 7 Pflicht-Slots". |
| 8 | `backend/tests/test_exploration_mode.py` | `test_nearing_completion_escalates_to_phase_complete`: Verwendet `PFLICHT_SLOTS.items()` — Kommentar "all 9 slots" → "all 7 slots" anpassen. |

### Phase 4: E2E-Skript (informativ, nicht blocking)

| # | Datei | Änderung |
|---|---|---|
| 9 | `backend/scripts/validate_e2e_artifacts.py` | `expected_slots` Liste und `keyword_map` auf neue 7 Slots aktualisieren. `len(slots) >= 8` → `len(slots) >= 6`. Keyword-Map: `umgebung`, `randbedingungen`, `ausnahmen` Einträge entfernen, neue Einträge für `entscheidungen_und_schleifen` und `variablen_und_daten` hinzufügen. |

### Phase 5: E2E-Testdaten (informativ)

| # | Datei | Änderung |
|---|---|---|
| 10 | `backend/tests/test_e2e_moderator.py` | Zeilen 364–371: Keyword-Map für Content-Checks auf neue Slots aktualisieren. `scope`, `umgebung`, `randbedingungen`, `ausnahmen` Einträge entfernen, `entscheidungen_und_schleifen` und `variablen_und_daten` hinzufügen. Zeile 192–195: `prozessausloeser`-Check bleibt unverändert. |

---

## 5. Risiken und Mitigationen

### R-1: Bestehende Exploration-Artefakte haben alte Slots

**Risiko:** Projekte die bereits in der Exploration sind, haben 9 Slots. Nach dem Update werden nur noch 7 als Pflicht-Slots geführt.

**Mitigation:** Die `_build_init_patches()`-Funktion fügt nur fehlende Pflicht-Slots hinzu und löscht keine bestehenden. Alte Slots (`scope`, `umgebung`, `randbedingungen`, `ausnahmen`) bleiben erhalten, werden aber nicht mehr als Pflicht-Slot geführt. Die Guardrails in `_apply_guardrails()` prüfen nur gegen `PFLICHT_SLOTS` — alte Slots sind damit irrelevant für die Phasen-Completion-Logik.

### R-2: LLM schreibt in alte Slot-Pfade

**Risiko:** Das LLM könnte aus Chat-Historie oder Kontext-Resten versuchen, in `/slots/ausnahmen/inhalt` zu schreiben.

**Mitigation:** Das Template-Schema (`EXPLORATION_TEMPLATE`) validiert mit Regex `/slots/[^/]+/inhalt` — das akzeptiert jeden Slot-Namen. Alte Slot-Pfade werden also nicht rejected, was bedeutet dass das LLM Patches für nicht-existierende Slots schicken könnte. Da `_build_init_patches()` nur Pflicht-Slots erzeugt, existiert z.B. `/slots/ausnahmen` nicht, und der `jsonpatch.apply_patch()` würde fehlschlagen. **Kein zusätzlicher Schutz nötig** — der Executor fängt das ab.

### R-3: Prompt-Länge

**Risiko:** Der überarbeitete Prompt könnte länger werden und mehr Tokens verbrauchen.

**Mitigation:** Durch Redundanz-Streichung (2 Slot-Erklärungen weniger, weniger Wiederholungen) und weniger Slots in der Referenztabelle wird der Prompt eher kürzer. Monitoring über das bestehende Token-Tracking.

### R-4: Structurer bekommt weniger strukturierte Eingabe

**Risiko:** Wenn alles in `prozessbeschreibung` steht, ist der Freitext unstrukturierter als separate Slots.

**Mitigation:** Der neue Slot `entscheidungen_und_schleifen` liefert dem Structurer explizit vorstrukturierte Kontrollfluss-Informationen — das ist *mehr* Struktur als vorher, nicht weniger. Die `prozessbeschreibung` war schon immer der Hauptcontainer; die anderen Slots enthielten oft nur 1-2 Sätze die auch in der Beschreibung standen.

---

## 6. Nicht im Scope

- **SDD-Aktualisierung:** §5.3 wird nach erfolgreicher Implementierung und Verifikation in einem separaten Commit aktualisiert, nicht als Teil dieses CRs.
- **Structuring-Prompt-Überarbeitung:** Der Structuring-Prompt muss ebenfalls überarbeitet werden (eigener CR).
- **Frontend-Änderungen:** Das Frontend zeigt Slots generisch an (`dict[str, ExplorationSlot]`) — keine Anpassung nötig.
- **Migrations-Skript für bestehende Projekte:** Nicht nötig, da alte Slots erhalten bleiben.
- **Änderungen am ExplorationSlot-Modell oder am Template-Schema:** Beide sind generisch genug und brauchen keine Änderung.

---

## 7. Abnahmekriterien

1. `PFLICHT_SLOTS` in `exploration.py` enthält genau 7 Einträge: `prozessausloeser`, `prozessziel`, `prozessbeschreibung`, `entscheidungen_und_schleifen`, `beteiligte_systeme`, `variablen_und_daten`, `prozesszusammenfassung`.
2. `exploration.md` enthält keine `@@@`-Kommentare mehr.
3. `exploration.md` beginnt mit einer klaren Rollenidentität ("Du bist ein explorativer Prozessanalyst").
4. `exploration.md` enthält Widerspruchserkennung als Kernregel.
5. `exploration.md` enthält Kontrollfluss-Extraktion als Kernregel.
6. `exploration.md` enthält Variablen-Erkennung als Kernregel.
7. `exploration.md` enthält mindestens 4 sokratische Beispielfragen die gezielt nach Entscheidungen, Schleifen und Variablen fragen.
8. `exploration.md` referenziert genau 7 Pflicht-Slots in der Slot-Tabelle.
9. `exploration.md` enthält Patch-Beispiele für `entscheidungen_und_schleifen` und `variablen_und_daten`.
10. `test_first_turn_initializes_pflicht_slots` ist grün mit 7 Slots.
11. `test_second_turn_does_not_reinitialize_slots` ist grün mit 7 Slots.
12. `test_build_slot_status_shows_leer_for_uninitialized_slots` ist grün mit 7 Slot-Titeln.
13. Alle bestehenden Tests in `test_exploration_mode.py` sind grün.
14. `structuring.py` Zeile 83 referenziert die neuen Slot-Namen.
15. Keine Änderungen an `models.py`, `template_schema.py` oder `executor.py` nötig.

---

## 8. Aufwandsschätzung

| Feld | Wert |
|---|---|
| **Komplexität** | M (8 Dateien, kein Breaking Change auf Modellebene, aber signifikanter Prompt-Rewrite) |
| **Betroffene Dateien** | 8 |
| **Breaking Change** | Nein (Datenmodell bleibt unverändert, alte Slots bleiben erhalten) |

| Phase | Dateien | Komplexität |
|---|---|---|
| Prompt | `backend/prompts/exploration.md` | L (kompletter Rewrite) |
| Backend-Code | `backend/modes/exploration.py`, `backend/modes/structuring.py` | S (Dict-Einträge ändern, 1 String-Referenz) |
| Tests | `backend/tests/test_exploration_mode.py` | S (Sets und Kommentare anpassen) |
| E2E-Skript | `backend/scripts/validate_e2e_artifacts.py` | S (Listen anpassen) |
| E2E-Test | `backend/tests/test_e2e_moderator.py` | S (Keyword-Map anpassen) |
