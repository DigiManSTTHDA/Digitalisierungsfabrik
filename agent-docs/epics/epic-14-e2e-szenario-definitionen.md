# Epic 14 – E2E Szenario-Definitionen (8 JSONs)

## Summary

Definiert die 8 Testszenarien der ersten E2E-Kampagne als JSON-Dateien. Jedes Szenario
enthält realistische Nutzer-Messages, Nudge-Definitionen, TurnExpectations, BehaviorProbes
und Intent-Definitionen. Wenig Code, viel Domänenwissen. Nach diesem Epic kann die komplette
Kampagne mit allen 8 Szenarien ausgeführt werden.

Dieses Epic entspricht **Schritt 5** im `e2e-testkampagne-plan.md`.

## Goal

8 vollständige Szenario-JSONs in `e2e/scenarios/`, die zusammen die wichtigsten
Systemverhaltensweisen abdecken: Happy Path, Komplexität, Stress (Ungeduld, Widersprüche),
Randfälle (Abbruch, Minimal, Sprachmischung) und das Referenz-Szenario mit Eskalationen.

## Testable Increment

- `npx tsx e2e/run-campaign.ts` (ohne `--scenario`) lädt alle 8 Szenarien und führt
  die komplette Kampagne durch
- Jede JSON-Datei validiert erfolgreich gegen das `Scenario`-Interface aus `types.ts`
- Die Report-Dateien in `e2e/reports/` enthalten Befundlisten für alle 8 Szenarien
  und eine vollständige Bewertungsmatrix

## Dependencies

- Epic 12 (Framework Core — Types und ScenarioRunner müssen existieren)
- Epic 13 (Evaluator + Reporter — für vollständige Kampagnen-Reports)

## Key Deliverables

- `e2e/scenarios/s01-eingangsrechnung.json` – Referenz-Szenario (~41 Turns)
- `e2e/scenarios/s02-reisekosten.json` – Happy Path (bereits in Epic 12-05 als Smoke-Test angelegt, hier erweitert)
- `e2e/scenarios/s03-mitarbeiter-einstellung.json` – Komplexer Prozess (>15 Schritte)
- `e2e/scenarios/s04-ungeduldiger-nutzer.json` – Stress: Ungeduld + kurze Antworten
- `e2e/scenarios/s05-widersprueche.json` – Stress: 3 Korrekturen
- `e2e/scenarios/s06-abbruch-phase1.json` – Randfall: Nur Exploration
- `e2e/scenarios/s07-minimaler-prozess.json` – Randfall: Minimaler Input
- `e2e/scenarios/s08-englisch-antworten.json` – Randfall: Sprachmischung

## Szenario-Qualitätskriterien

Jedes Szenario-JSON **muss** folgende Mindestanforderungen erfüllen:

1. **Valides `Scenario`-Interface:** Alle Pflichtfelder aus `types.ts` vorhanden
2. **Realistische Nutzer-Messages:** Keine generischen Platzhalter, sondern
   domänenspezifische Fachanwender-Sprache
3. **Intent-Definition:** `key_concepts` und `forbidden_concepts` definiert
4. **BehaviorProbes:** Mindestens 2 pro Szenario an kritischen Stellen
5. **TurnExpectations:** An kritischen Turns (Moduswechsel, Eskalation) definiert
6. **Nudges:** Für jeden letzten Turn einer Phase definiert (falls `phase_complete`
   verzögert kommen könnte)
7. **Notes:** Kritische Turns mit `note` annotiert (Testabsicht dokumentiert)

## Stories

---

### Story 14-01: S01 Eingangsrechnung (Referenz-Szenario)

**Als** Tester,
**möchte ich** ein umfassendes Referenz-Szenario mit dem kompletten Rechnungsfreigabe-Prozess,
**damit** alle Bewertungsdimensionen (Dialog, Moderator, Artefakte, UX) an einem realistischen
Durchlauf kalibriert werden können.

**Akzeptanzkriterien:**

1. `e2e/scenarios/s01-eingangsrechnung.json` existiert und ist valides JSON.
2. **Intent:**
   - `process_description`: Beschreibt die dreistufige Rechnungsfreigabe (Eingang, Prüfung, Freigabe)
   - `expected_structure_steps`: ~12
   - `expected_complexity`: `"komplex"`
   - `key_concepts`: Mindestens `["Eingangsrechnung", "Freigabe", "Prüfung", "Buchung", "SAP"]`
     (domänenspezifisch angepasst)
   - `forbidden_concepts`: Mindestens `["Blockchain", "KI-gestützt"]` (Halluzinations-Schutz)
3. **Exploration-Phase:** ~15–20 Turns
   - Beschreibt den Prozess schrittweise: Rechnungseingang, Erfassung, sachliche Prüfung,
     rechnerische Prüfung, Freigabe, Buchung, Archivierung
   - Mindestens 1 Widerspruch (z.B. "Nein, die Freigabe hat zwei Stufen, nicht eine")
   - Mindestens 1 Eskalation (`action: "panic"`) mit Note warum
   - Nudges am Ende der Phase definiert
4. **Strukturierung-Phase:** ~8–12 Turns
   - Nutzer bestätigt/korrigiert erkannte Schritte
   - 1 Eskalation wenn Schritte fehlen oder falsch gruppiert
   - TurnExpectations bei Moduswechsel-Turns
5. **Spezifikation-Phase:** ~8–10 Turns
   - Nutzer spezifiziert EMMA-Parameter
   - 1 Eskalation bei zu komplexer Frage
6. **BehaviorProbes:** Mindestens 5:
   - Nach Widerspruch: Wurde das Artefakt korrigiert?
   - Nach Eskalation: Hat der Moderator das Problem analysiert?
   - Am Phasenende: Sind alle Pflichtslots gefüllt?
   - Nach Strukturierung: Stimmen die Nachfolger-Referenzen?
   - Am Ende: Enthält das Artefakt die `key_concepts`?
7. **Gesamt:** ~35–45 Turns, 3 Eskalationen, 1 Widerspruch
8. `tags`: `["referenz", "komplex", "eskalation", "widerspruch"]`

**Definition of Done:**

- [x] `e2e/scenarios/s01-eingangsrechnung.json` existiert und ist valides JSON
- [x] Intent mit key_concepts und forbidden_concepts definiert
- [x] Exploration-Phase mit ≥15 Turns, 1 Widerspruch, 1 Eskalation
- [x] Strukturierung-Phase mit ≥8 Turns, 1 Eskalation
- [x] Spezifikation-Phase mit ≥8 Turns, 1 Eskalation
- [x] ≥5 BehaviorProbes an kritischen Stellen
- [x] TurnExpectations bei Moduswechsel-Turns
- [x] Nudges an Phasenenden definiert
- [x] Nutzer-Messages sind realistisch und domänenspezifisch (keine Platzhalter)
- [x] Kritische Turns mit `note` annotiert
- [x] `tags` korrekt gesetzt: `["referenz", "komplex", "eskalation", "widerspruch"]`
- [x] `npm run typecheck` in `e2e/` exit 0 (JSON wird im Runner geladen, Type-Check prüft Ladelogik)

---

### Story 14-02: S02 Reisekosten (Happy Path — Erweiterung)

**Als** Tester,
**möchte ich** das S02-Szenario (aus Epic 12-05 als Smoke-Test angelegt) um
Strukturierung + Spezifikation + Intent + BehaviorProbes erweitern,
**damit** es als vollständiges Happy-Path-Referenz-Szenario dient.

**FR/NFR Traceability:** Portierung aus `backend/tests/e2e_reisekosten.py`.

**Akzeptanzkriterien:**

1. `e2e/scenarios/s02-reisekosten.json` erweitert:
   - Exploration-Phase aus Epic 12-05 bleibt bestehen
   - **Strukturierung-Phase hinzugefügt:** ~5–8 Turns, kooperativer Nutzer bestätigt Schritte
   - **Spezifikation-Phase hinzugefügt:** ~4–6 Turns, EMMA-Parameter spezifiziert
2. **Intent:**
   - `process_description`: "Reisekostenabrechnung — Antrag, Genehmigung, Abrechnung, Erstattung"
   - `expected_structure_steps`: ~6–8
   - `expected_complexity`: `"einfach"`
   - `key_concepts`: `["Reisekosten", "Genehmigung", "Belege", "Erstattung", "Vorgesetzter"]`
   - `forbidden_concepts`: `["Blockchain", "Machine Learning"]`
3. **BehaviorProbes:** Mindestens 2:
   - Nach Exploration: Sind die Kernkonzepte im Artefakt?
   - Am Ende: Ist die Struktur vollständig?
4. **Keine Eskalationen, keine Widersprüche** (Happy Path)
5. Nudges nur als Fallback definiert (sollten nicht nötig sein)
6. `tags`: `["happy-path", "einfach", "baseline"]`

**Definition of Done:**

- [x] `e2e/scenarios/s02-reisekosten.json` um Strukturierung + Spezifikation erweitert
- [x] Intent mit key_concepts und forbidden_concepts
- [x] ≥2 BehaviorProbes
- [x] Keine Eskalationen im Szenario
- [x] Nudges als Fallback an Phasenenden definiert
- [x] Nutzer-Messages sind realistisch und domänenspezifisch (keine Platzhalter)
- [x] Kritische Turns mit `note` annotiert
- [x] `tags` korrekt gesetzt: `["happy-path", "einfach", "baseline"]`
- [x] `npm run typecheck` in `e2e/` exit 0

---

### Story 14-03: S03 Mitarbeiter-Einstellung (komplex)

**Als** Tester,
**möchte ich** ein Szenario mit einem komplexen, mehrstufigen Prozess,
**damit** geprüft wird ob das System bei >15 Strukturschritten noch qualitativ
hochwertige Artefakte erzeugt.

**Akzeptanzkriterien:**

1. `e2e/scenarios/s03-mitarbeiter-einstellung.json` existiert.
2. **Intent:**
   - `process_description`: "Mitarbeiter-Einstellung — Anforderung, Ausschreibung,
     Bewerbung, Interview, Vertrag, Onboarding"
   - `expected_structure_steps`: ≥15
   - `expected_complexity`: `"komplex"`
   - `key_concepts`: `["Stellenausschreibung", "Bewerbung", "Interview", "Arbeitsvertrag",
     "Onboarding", "Personalabteilung", "Fachabteilung"]`
   - `forbidden_concepts`: `["Kündigung", "Abmahnung"]`
3. **Exploration-Phase:** ≥12 Turns, detaillierte Prozessbeschreibung über alle Stationen
4. **Strukturierung-Phase:** ≥8 Turns, Nutzer korrigiert Schrittreihenfolge
5. **Spezifikation-Phase:** ~4–6 Turns, EMMA-Parameter für die komplexen Schritte spezifiziert
6. **BehaviorProbes:** Mindestens 3:
   - Skalierungs-Check: Sind ≥15 Strukturschritte erzeugt worden?
   - Nachfolger-Integrität: Keine verwaisten Schritte
   - Inhaltliche Präzision: key_concepts im Artefakt vorhanden
7. `tags`: `["komplex", "skalierung", "viele-schritte"]`

**Definition of Done:**

- [x] `e2e/scenarios/s03-mitarbeiter-einstellung.json` existiert und ist valides JSON
- [x] Intent mit ≥7 key_concepts
- [x] Exploration-Phase mit ≥12 Turns
- [x] Strukturierung-Phase mit ≥8 Turns
- [x] Spezifikation-Phase mit ~4–6 Turns
- [x] ≥3 BehaviorProbes
- [x] Nutzer-Messages sind realistisch und domänenspezifisch (keine Platzhalter)
- [x] Kritische Turns mit `note` annotiert
- [x] Nudges an Phasenenden definiert
- [x] `tags` korrekt gesetzt: `["komplex", "skalierung", "viele-schritte"]`
- [x] `npm run typecheck` in `e2e/` exit 0

---

### Story 14-04: S04 Ungeduldiger Nutzer + S05 Widersprüche (Stress-Szenarien)

**Als** Tester,
**möchte ich** Szenarien die das System unter Stress setzen (Ungeduld und Widersprüche),
**damit** geprüft wird ob das System bei schwierigem Nutzerverhalten robust reagiert.

**Akzeptanzkriterien:**

1. **S04 — `e2e/scenarios/s04-ungeduldiger-nutzer.json`:**
   - Intent: Einfacher Prozess, aber Nutzer gibt nur Kurzantworten
   - `expected_complexity`: `"einfach"`
   - Exploration-Phase: ~10 Turns mit kurzen Antworten ("Ja", "Nein", "Reicht das?",
     "Weiter!", "Wie lange dauert das noch?")
   - **Testfokus:** Setzt das System `phase_complete` obwohl Slots leer sind?
     Fragt es gezielt nach fehlenden Informationen?
   - BehaviorProbes:
     - Nach kurzer Antwort: Hat das System nachgefragt (nicht einfach aufgegeben)?
     - Am Phasenende: Sind Slots mit Annahmen statt Nutzerinput gefüllt?
       (→ forbidden: System darf keine Annahmen erfinden)
   - TurnExpectations: `flag_should_not_include: ["phase_complete"]` bei Turns
     mit unvollständigen Informationen
   - **Strukturierung-Phase:** ~4–6 Turns, Nutzer bestätigt widerwillig mit Kurzantworten
   - **Spezifikation-Phase:** ~3–5 Turns, minimale Kooperation
   - Nudges an Phasenenden definiert (hier besonders relevant, da Nutzer ungeduldig)
   - `tags`: `["stress", "ungeduld", "kurzantworten"]`

2. **S05 — `e2e/scenarios/s05-widersprueche.json`:**
   - Intent: Mittlerer Prozess mit 3 bewussten Korrekturen
   - `expected_complexity`: `"mittel"`
   - Exploration-Phase: ~12 Turns, davon 3 Korrekturen:
     - Korrektur 1: "Nein, das stimmt nicht. Es sind nicht 3 Stufen sondern 2."
     - Korrektur 2: "Ich hab mich geirrt, SAP ist doch nicht beteiligt, nur Excel."
     - Korrektur 3: "Der letzte Schritt fehlt ganz — die Archivierung."
   - **Testfokus:** Wird das Artefakt korrekt aktualisiert? Bleiben Altlasten stehen?
     Erkennt das System den Widerspruch explizit?
   - BehaviorProbes:
     - Nach jeder Korrektur: Wurde der Slot-Inhalt aktualisiert?
     - Nach Korrektur 2: Ist "SAP" nicht mehr im Artefakt und "Excel" dafür drin?
     - Am Ende: Keine Altlasten (alte Werte sollen überschrieben sein)
   - **Strukturierung-Phase:** ~5–8 Turns, Nutzer korrigiert auch hier erkannte Schritte
   - **Spezifikation-Phase:** ~3–5 Turns
   - Nudges an Phasenenden definiert
   - `tags`: `["stress", "widerspruch", "korrektur"]`

**Definition of Done:**

- [x] `e2e/scenarios/s04-ungeduldiger-nutzer.json` existiert und ist valides JSON
- [x] S04: Kurzantworten-Turns mit TurnExpectations gegen vorzeitiges phase_complete
- [x] S04: ≥2 BehaviorProbes zum Nachfrage- und Annahmen-Verhalten
- [x] S04: Strukturierung- und Spezifikation-Phase definiert
- [x] S04: Nudges an Phasenenden definiert
- [x] `e2e/scenarios/s05-widersprueche.json` existiert und ist valides JSON
- [x] S05: 3 explizite Korrekturen mit BehaviorProbes
- [x] S05: BehaviorProbe prüft dass alte Werte überschrieben wurden
- [x] S05: Strukturierung- und Spezifikation-Phase definiert
- [x] S05: Nudges an Phasenenden definiert
- [x] S04+S05: Nutzer-Messages sind realistisch und domänenspezifisch (keine Platzhalter)
- [x] S04+S05: Kritische Turns mit `note` annotiert
- [x] S04+S05: `tags` korrekt gesetzt
- [x] `npm run typecheck` in `e2e/` exit 0

---

### Story 14-05: S06 Abbruch + S07 Minimal + S08 Englisch (Rand-Szenarien)

**Als** Tester,
**möchte ich** Randfall-Szenarien die ungewöhnliches Nutzerverhalten simulieren,
**damit** geprüft wird ob das System auch bei Abbruch, minimalem Input und
Sprachmischung stabil bleibt.

**Akzeptanzkriterien:**

1. **S06 — `e2e/scenarios/s06-abbruch-phase1.json`:**
   - Intent: Mittlerer Prozess, aber Abbruch nach Exploration
   - Nur Exploration-Phase: ~8–10 Turns, dann kein weiterer Input
   - `strukturierung`, `spezifikation`, `validierung`: leere Arrays `[]`
   - **Testfokus:** Ist der Zustand konsistent? Kein Zombie-State?
     Könnte man später weitermachen?
   - BehaviorProbes:
     - Am Ende: Sind die Exploration-Artefakte gespeichert?
     - State-Check: `aktive_phase` ist noch `exploration` (kein unkontrollierter Phasensprung)
   - `tags`: `["randfall", "abbruch", "phase1-only"]`

2. **S07 — `e2e/scenarios/s07-minimaler-prozess.json`:**
   - Intent: "Ich drucke ein Dokument aus." — minimaler Prozess
   - `expected_structure_steps`: 1–3
   - `expected_complexity`: `"minimal"`
   - Exploration-Phase: ~4–6 Turns, Nutzer beschreibt trivialen 1-Schritt-Prozess
   - `key_concepts`: `["Dokument", "drucken"]`
   - `forbidden_concepts`: `["Genehmigung", "Workflow", "Freigabe"]`
     (System soll keine Komplexität halluzinieren)
   - **Testfokus:** Erzeugt das System trotzdem gültige Artefakte?
     Oder halluziniert es Komplexität?
   - **Strukturierung-Phase:** ~2–3 Turns (minimaler Prozess → minimale Strukturierung)
   - **Spezifikation-Phase:** ~2–3 Turns
   - BehaviorProbes:
     - Am Ende: Sind ≤3 Strukturschritte erzeugt?
     - Keine forbidden_concepts im Artefakt?
   - Nudges an Phasenenden definiert
   - `tags`: `["randfall", "minimal", "halluzinations-check"]`

3. **S08 — `e2e/scenarios/s08-englisch-antworten.json`:**
   - Intent: Mittlerer Prozess, aber Nutzer antwortet teilweise auf Englisch
   - `expected_complexity`: `"mittel"`
   - Exploration-Phase: ~10 Turns, davon ~4 auf Englisch:
     - "The process starts when a customer sends an email."
     - "Then the responsible person checks the request."
     - "After approval, the order is placed in SAP."
     - "Finally, the customer gets a confirmation."
   - **Testfokus:** Bleibt das System bei Deutsch (FR-A-08)?
     Wandelt es englische Begriffe korrekt um?
   - **Strukturierung-Phase:** ~5–7 Turns, teilweise englische Antworten fortgesetzt
   - **Spezifikation-Phase:** ~3–5 Turns
   - BehaviorProbes:
     - Nach englischem Turn: Systemantwort ist auf Deutsch
     - Am Ende: Artefakt-Inhalte sind auf Deutsch (nicht englisch kopiert)
   - TurnExpectations bei englischen Turns:
     `response_should_not_contain: ["the", "and", "process"]` (System soll deutsch antworten)
   - Nudges an Phasenenden definiert
   - `tags`: `["randfall", "sprache", "englisch", "FR-A-08"]`

**Definition of Done:**

- [x] `e2e/scenarios/s06-abbruch-phase1.json` existiert mit nur Exploration-Phase
- [x] S06: `strukturierung`, `spezifikation`, `validierung` sind explizit leere Arrays `[]`
- [x] S06: BehaviorProbes prüfen konsistenten State nach Abbruch
- [x] S06: Nudges an Exploration-Phasenende definiert
- [x] `e2e/scenarios/s07-minimaler-prozess.json` existiert mit minimalem Prozess
- [x] S07: Strukturierung- und Spezifikation-Phase definiert (minimal)
- [x] S07: forbidden_concepts gegen Komplexitäts-Halluzination
- [x] S07: BehaviorProbe prüft ≤3 Strukturschritte
- [x] S07: Nudges an Phasenenden definiert
- [x] `e2e/scenarios/s08-englisch-antworten.json` existiert mit gemischter Sprache
- [x] S08: Strukturierung- und Spezifikation-Phase definiert
- [x] S08: ≥4 englische Nutzer-Turns
- [x] S08: BehaviorProbes prüfen deutsche Systemantworten
- [x] S08: TurnExpectations bei englischen Turns
- [x] S08: Nudges an Phasenenden definiert
- [x] S06+S07+S08: Nutzer-Messages sind realistisch und domänenspezifisch (keine Platzhalter)
- [x] S06+S07+S08: Kritische Turns mit `note` annotiert
- [x] S06+S07+S08: `tags` korrekt gesetzt
- [x] `npm run typecheck` in `e2e/` exit 0

---

### Implementation Order

Stories können weitgehend parallel implementiert werden, da es sich um unabhängige
JSON-Dateien handelt. Empfohlene Reihenfolge nach Aufwand:

1. **14-02** (S02 Erweiterung) — geringster Aufwand, baut auf Epic 12-05 auf
2. **14-04** (S04 + S05 Stress) — mittlerer Aufwand, klarer Testfokus
3. **14-05** (S06 + S07 + S08 Randfälle) — geringer bis mittlerer Aufwand pro Szenario
4. **14-03** (S03 Komplex) — hoher Aufwand wegen vieler Turns
5. **14-01** (S01 Referenz) — höchster Aufwand (~41 Turns, 3 Eskalationen, umfassende Probes)
