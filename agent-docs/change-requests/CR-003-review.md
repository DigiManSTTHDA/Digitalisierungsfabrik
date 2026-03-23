# CCB Review: CR-003 — Überarbeitung der Explorationsphase — Slot-Konsolidierung und Kontrollfluss-Vorbereitung

| Feld | Wert |
|---|---|
| **CR** | CR-003 |
| **Review-Datum** | 2026-03-23 |
| **Review-Nr.** | 1 |
| **Empfehlung** | APPROVE WITH CONDITIONS |

## Zusammenfassung

CR-003 wurde von 6 unabhängigen Fachexperten geprüft (Datenmodell, Orchestrator/Kontrollfluss, Prompt/LLM-Verhalten, Tests/Regression, SDD/ADR-Konformität, Abhängigkeiten/Konflikte). Der Ansatz (9→7 Slots, Kontrollfluss-Vorbereitung, Variablen-Erkennung) ist architektonisch sauber, verletzt keine bestehenden ADRs und das eingebettete ADR ist stichhaltig begründet. Der Änderungsplan ist jedoch **signifikant unvollständig** — es fehlen 5+ Testdateien, 3 Prompt-Dateien, eine kritische Code-Anpassung und JSON-Testdaten.

## Empfehlung

**APPROVE WITH CONDITIONS**

Der CR ist konzeptionell korrekt und kann implementiert werden, sofern die 5 Bedingungen vor/während der Implementierung adressiert werden. Keine Blocker im Sinne eines fundamentalen Designfehlers.

## Blocker (müssen behoben werden)

Keine Blocker identifiziert.

## Verbesserungsvorschläge (müssen eingearbeitet werden)

### V-1: Änderungsplan um fehlende Dateien erweitern (Orchestrator-Experte, Test-Experte)

Der CR listet 8 betroffene Dateien. Tatsächlich sind **mindestens 16 Dateien** betroffen (11 Code/Test + 5+ JSON-Testdaten). Fehlende Dateien im Änderungsplan:

**Testdateien (HARD FAIL ohne Anpassung):**

| Datei | Stellen | Bruch-Typ |
|---|---|---|
| `backend/tests/test_orchestrator.py` | Z.217-218, Z.461-469 | `len(patches) == 9`, `bekannte_slots == 10`, Kommentare |
| `backend/tests/test_moderator.py` | Z.41, Z.65, Z.111 | Fixture `bekannte_slots=9`, Assert `"5/9"`, Assert `== 9` |
| `backend/tests/test_progress_tracker.py` | Z.108-110 | `bekannte_slots == 9` |
| `backend/tests/test_e2e_structurer.py` | Z.174, Z.489-491 | `len(slots) == 9` |
| `backend/tests/test_e2e_specifier.py` | Z.202, Z.228, Z.404, Z.560-562 | `len(slots) == 9` |

**Prompt-Dateien (Inkonsistenz ohne Anpassung):**

| Datei | Stellen | Bruch-Typ |
|---|---|---|
| `backend/prompts/structuring.md` | "9 Slots", alte Slot-Namen | LLM erwartet Slots die nicht mehr existieren |
| `backend/prompts/validation.md` | "9 Slots", `slot_ausnahmen`-Beispiel | Validierungsbefund referenziert nicht-existierten Slot |
| `backend/prompts/moderator.md` | "9 Slots" | Moderator kommuniziert falsche Slot-Anzahl |

**JSON-Testdaten:**

| Datei | Bruch-Typ |
|---|---|
| `frontend/test-texte/explorer/dialog-e2e-moderator.json` | `expected_artifact` mit 9 Slots |
| `frontend/test-texte/structurer/dialog-e2e-structurer.json` | `exploration_seed` mit 9 Slots |
| `frontend/test-texte/specifier/dialog-e2e-specifier.json` | `exploration_seed` mit 9 Slots |
| `frontend/test-texte/explorer/expected-artifact-reisekosten.json` | 9 Slots |
| `frontend/test-texte/explorer/dialog-reisekosten.jsonl` | `expected_question_about` alte Slots |
| `frontend/test-texte/explorer/e2e-results.json` | 9 Slots |

**Empfehlung:** Änderungsplan Phase 3-5 um alle oben genannten Dateien erweitern. Die meisten sind mechanische `9→7`-Ersetzungen.

### V-2: `_next_empty_slot()` um Skip-Logik für Extraktions-Slots erweitern (Prompt-Experte)

**Problem:** `_next_empty_slot()` in `exploration.py:78-89` überspringt aktuell nur `prozesszusammenfassung`. Die neuen Slots `entscheidungen_und_schleifen` und `variablen_und_daten` sind **Extraktions-Slots** — sie werden vom LLM aus dem Dialog extrahiert, nicht durch direkte Nutzerfragen befüllt. Ohne Skip würde der Hint lauten: "Stelle eine Frage zum Slot **Entscheidungen und Schleifen**" — genau die Art abstrakter Frage die CR-003 eliminieren will (Defizit D-1).

**Empfehlung:** Im Änderungsplan Phase 2 eine neue Zeile einfügen: `_next_empty_slot()` erweitern, sodass `entscheidungen_und_schleifen` und `variablen_und_daten` übersprungen werden (analog zu `prozesszusammenfassung`). Alternativ: differenzierter Hint-Text für Extraktions-Slots ("Extrahiere aus den bisherigen Informationen..." statt "Stelle eine Frage zu...").

### V-3: Detailgrad für `entscheidungen_und_schleifen` explizit definieren (Prompt-Experte)

**Problem:** Der CR fordert gleichzeitig "Breite vor Tiefe" (§3.3f) und aktive Kontrollfluss-Extraktion (§3.3d). Das JSON-Beispiel (Zeile 130) zeigt bereits detaillierte Entscheidungsregeln mit konkreten Bedingungen. Das ist nah an Strukturierungs-Tiefe und widersprüchlich zum "Breite"-Fokus.

**Empfehlung:** Im Prompt-Rewrite (§3.3d) explizit definieren: Entscheidungen/Schleifen werden auf **Nennungs-Ebene** erfasst (Existenz + grobe Bedingung), NICHT auf algorithmischer Detail-Ebene. Beispiel: "ENTSCHEIDUNG: Betragsprüfung — ab 5.000€ Sonderfreigabe nötig" ist richtig. Vollständige Regeln mit allen Pfaden gehören in die Strukturierung.

### V-4: Abhängigkeiten-Sektion (§3a) vervollständigen (Abhängigkeits-Experte)

Drei Lücken in §3a:

1. **`exploration.md`-Überlappung nicht dokumentiert:** CR-002 hat `@@@`-Kommentare in `exploration.md` hinterlassen. CR-003 plant den kompletten Rewrite. Das ist der größte Überlappungspunkt, wird aber in §3a nicht erwähnt.
2. **`patch_summarizer.py` nicht geprüft:** CR-002 hat `patch_summarizer.py` geändert. Falls dort Slot-spezifische Übersetzungen existieren, muss CR-003 diese aktualisieren.
3. **CR-002-Status unpräzise:** CR-002 wird als "Implementiert" beschrieben, ist aber faktisch "codiert, nicht committed". Präzisere Formulierung empfohlen.

### V-5: ADR-Konsequenzen und SDD-Zählung präzisieren (SDD/ADR-Experte)

1. **ADR-Konsequenzen ergänzen:** Neben "SDD §5.3 Pflicht-Slots-Tabelle" auch "SDD §5.3 Konsistenzregeln (Pfad-Beispiele, Zeile 667)" und "SDD §6.6.1 Explorationsmodus-Verhalten (Zeile 1192)" als Update-Ziele aufführen.
2. **SDD-Zählung korrigieren:** Die Formulierung "8 Pflicht-Slots (plus prozesszusammenfassung)" ist irreführend. `prozesszusammenfassung` IST einer der 8 SDD-Slots, und `prozessbeschreibung` fehlt in der SDD-Tabelle (Pre-Existing Gap). Empfohlene Korrektur: "Die SDD §5.3 definiert 8 Pflicht-Slots. Die Implementierung führt zusätzlich `prozessbeschreibung` als 9. Slot (Pre-Existing Gap). CR-003 konsolidiert auf 7 Pflicht-Slots."

## Hinweise

1. **Kein konkreter Prompt-Entwurf:** Der CR beschreibt Prompt-Änderungen als prosaische Bullet-Points, liefert aber keinen Entwurfstext. Für einen "kompletten Rewrite" erhöht das den Interpretationsspielraum bei der Implementierung. (Prompt-Experte F1)
2. **`prozessbeschreibung` wird deutlich länger:** Durch die Absorption von 4 Slots wird der Freitext umfangreicher. Empfehlung: Im Prompt einen Strukturierungshinweis einfügen ("Gliedere chronologisch, nutze Absätze"). (Prompt-Experte F6)
3. **Migrationstest empfohlen (GAP-1):** Es gibt keinen Test für das Szenario "bestehendes Projekt mit 9 Slots öffnet nach Update → Artefakt hat 11 Slots (9 alt + 2 neu)". Empfehlung: Expliziter Testfall der verifiziert, dass `_build_init_patches()` nur fehlende Pflicht-Slots hinzufügt und Guardrails korrekt nur die 7 Pflicht-Slots prüfen. (Test-Experte GAP-1)
4. **SDD-Update zeitnah nach Implementierung:** Das Muster "Implementierung vor SDD-Update" ist etabliert (CR-002), erzeugt aber ein Divergenz-Fenster. Empfehlung: SDD-Update innerhalb 1 Woche nach Merge. (SDD/ADR-Experte F-10)

## Bestätigungen (CR-Behauptungen, die verifiziert wurden)

1. **`models.py` braucht keine Änderung** — `ExplorationArtifact` nutzt `dict[str, ExplorationSlot]`, vollständig generisch. (Datenmodell-Experte F1)
2. **`template_schema.py` braucht keine Änderung** — Regex `/slots/[^/]+` akzeptiert jeden Slot-Namen. (Datenmodell-Experte F2)
3. **`executor.py` braucht keine Änderung** — Keine hardcoded Slot-Referenzen, arbeitet generisch. (Datenmodell-Experte F3)
4. **Orchestrator arbeitet generisch** — `orchestrator.py`, `context_assembler.py`, `completeness.py` referenzieren keine spezifischen Exploration-Slot-Namen. (Orchestrator-Experte F1-F2)
5. **Guardrails passen sich automatisch an** — `_apply_guardrails()`, `_merge_slot_patches()`, `_build_slot_status()` iterieren über `PFLICHT_SLOTS` generisch. (Orchestrator-Experte F3-F6)
6. **ADR stichhaltig begründet** — Alle 4 Begründungspunkte sind SDD-evidenzbasiert. (SDD/ADR-Experte F-02)
7. **Keine ADR-Verletzungen** — Keiner der 9 bestehenden ADRs betrifft die Exploration-Slot-Struktur. (SDD/ADR-Experte F-05/F-06)
8. **Keine Architektur-Prinzip-Verletzungen** — "LLM als Operator" und "deterministische Orchestrierung" bleiben intakt. (SDD/ADR-Experte F-08/F-09)
9. **Alle @@@-Kommentare im CR adressiert** — 8 von 8 Kommentaren. (Prompt-Experte F8)
10. **Patch-Beispiele valide** — Korrekte RFC 6902, korrekte Pfade. (Prompt-Experte F3)
11. **`test_executor.py` nicht betroffen** — Keine hardcoded Exploration-Slot-Namen. (Test-Experte)
12. **`specification.py` und `validation_checks.py` nicht betroffen** — Keine Exploration-Slot-Referenzen. (Orchestrator-Experte F8)

## CR-Vollständigkeit

| Pflichtabschnitt | Vorhanden? | Anmerkung |
|---|---|---|
| Kopfzeile mit Priorität und Abhängigkeiten | Ja | |
| Problemstellung (Kernproblem, Defizite, Auswirkungen) | Ja | 6 Defizite, gut dokumentiert |
| Ziel der Änderung | Ja | |
| Lösung (Datenmodell, Beispiele, Prompts, Abwärtskompatibilität) | Ja | JSON-Beispiel realistisch |
| SDD-Konsistenz und ADR | Ja | Konsequenzen unvollständig (V-5) |
| ADR-Konsistenz | Ja | |
| Abhängigkeiten & Konflikte (§3a) | Ja | Lücken (V-4) |
| Änderungsplan | **Unvollständig** | 8 statt ~16 Dateien (V-1) |
| Risiken und Mitigationen | Ja | 4 Risiken, R-2 korrekt analysiert |
| Nicht im Scope | Ja | Bewusste Abgrenzungen dokumentiert |
| Abnahmekriterien | Ja | 15 Kriterien, aber fehlende Tests nicht abgedeckt |
| Aufwandsschätzung | **Zu niedrig** | M statt M-L, 8 statt ~16 Dateien |

## Lückenanalyse

1. **Fehlende Dateien im Änderungsplan:** 5 Testdateien, 3 Prompt-Dateien, 5+ JSON-Testdaten (Details in V-1)
2. **Fehlende Code-Änderung:** `_next_empty_slot()` Skip-Logik für Extraktions-Slots (V-2)
3. **Fehlender Detailgrad-Definition:** Tiefe der Kontrollfluss-Erfassung vs. "Breite vor Tiefe" (V-3)
4. **Fehlende Abnahmekriterien:** Kein Kriterium für test_orchestrator.py, test_moderator.py, test_progress_tracker.py, E2E-Tests, JSON-Testdaten, Prompt-Konsistenz in structuring.md/validation.md/moderator.md
5. **Fehlender Migrationstest:** Szenario "altes Projekt mit 9 Slots nach Update"
6. **Aufwandsschätzung:** "8 betroffene Dateien" ist signifikant zu niedrig (~16 Dateien)

## Detaillierte Findings pro Experte

### Datenmodell
- F1-F3: **Bestätigt** — models.py, template_schema.py, executor.py brauchen keine Änderung
- F4: **Risiko (niedrig)** — replace-Patch auf nicht-existierenden Slot → atomarer Batch-Fail. Executor fängt das sicher ab, aber valide Patches im selben Batch werden mitgerissen.
- F5-F7: **Probleme (im CR adressiert)** — Hardcoded alte Slot-Namen in exploration.md, structuring.py, Tests
- F8: **Bestätigt** — PFLICHT_SLOTS ist einziger Definitionsort

### Orchestrator & Kontrollfluss
- Orchestrator, ContextAssembler, CompletenessCalculator, PatchSummarizer arbeiten generisch — kein Impact auf Laufzeitcode
- Einzige Laufzeit-Änderungsstelle: `exploration.py` PFLICHT_SLOTS dict
- **27 Folgestellen** in 11 Dateien identifiziert (CR listete nur 10 Stellen in 8 Dateien)
- `specification.py`, `validation_checks.py`, `patch_summarizer.py`: keine Exploration-Slot-Referenzen

### Prompts & LLM-Verhalten
- **Kritisch:** `_next_empty_slot()` generiert abstrakte Fragen für Extraktions-Slots (V-2)
- **Kritisch:** structuring.md, validation.md, moderator.md referenzieren "9 Slots" und alte Namen (V-1)
- **Kritisch:** Spannungsfeld "Breite vor Tiefe" vs. Detailgrad undefiniert (V-3)
- **Warnung:** Kein konkreter Prompt-Entwurf, nur Prosa-Beschreibung
- **OK:** Alle @@@-Kommentare adressiert, Patch-Beispiele valide, Platzhalter-Infrastruktur generisch

### Tests & Regression
- CR identifiziert 7 Test-Stellen korrekt
- CR übersieht **8+ weitere** Test-Stellen in 5 Dateien (HARD FAILs in test_orchestrator.py, test_moderator.py)
- CR übersieht 6 JSON-Testdaten-Dateien
- **4 Test-Gaps:** Migrationstest, LLM-schreibt-alte-Pfade, Happy-Path neue Slots, gemischte alte/neue Slots

### SDD, ADRs & Architektur-Konformität
- ADR stichhaltig, keine ADR-Verletzungen, keine Architektur-Prinzip-Verletzungen
- ADR-Konsequenzen unvollständig (2 weitere SDD-Stellen)
- SDD-Zählung irreführend (Pre-Existing Gap `prozessbeschreibung`)
- SDD-Update nach Implementierung: etabliertes Muster, architektonisch vertretbar

### Abhängigkeiten & Konflikte
- CR-002-Abhängigkeit korrekt erkannt (komplementär, kein Konflikt)
- **Nicht dokumentiert:** `exploration.md`-Überlappung mit CR-002
- **Nicht dokumentiert:** `patch_summarizer.py` als implizite Abhängigkeit
- **Unpräzise:** CR-002 als "Implementiert" beschrieben, ist aber uncommitted
- Reihenfolge CR-002 committen → CR-003 implementieren: korrekt und realistisch
