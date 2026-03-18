# Epic 12 – E2E Framework Core (WebSocket-Client + Scenario-Runner)

## Summary

Erstellt das Herzstück der E2E-Testkampagne: ein TypeScript-basiertes Framework in `e2e/`,
das über WebSocket direkt mit dem Backend kommuniziert, Szenarien durchspielt und
TurnRecords sammelt. Kein Browser, kein Playwright — reiner Systemverhaltenstest gegen
die WebSocket-API. Nach diesem Epic kann ein einzelnes Szenario (S02 Happy Path) vollständig
durchlaufen und TurnRecords erzeugen.

Dieses Epic entspricht **Schritt 1–2** im `e2e-testkampagne-plan.md`.

## Goal

Ein lauffähiges TypeScript-Framework in `e2e/`, das über WebSocket ein Projekt erstellt,
Dialog-Turns sendet, Systemzustand erfasst, Nudges handhabt, `phase_complete` erkennt und
pro Turn ein vollständiges `TurnRecord` erzeugt — verifiziert durch einen Smoke-Test mit
Szenario S02 (Happy Path).

## Testable Increment

- `npx tsx e2e/run-campaign.ts --scenario S02` startet, verbindet sich mit dem Backend,
  erstellt ein Projekt, sendet alle Turns und erzeugt TurnRecords
- Die erzeugten TurnRecords enthalten für jeden Turn: `user_message`, `assistant_response`,
  `state` (aktiver_modus, aktive_phase, flags), `response_time_ms`

## Dependencies

- Epic 05 (Backend API mit WebSocket-Endpoint muss existieren)
- Epic 11 (Stabilisiertes End-to-End System)

## Key Deliverables

- `e2e/package.json` – TypeScript-Projektsetup mit `tsx`, `ws`, Abhängigkeiten
- `e2e/tsconfig.json` – TypeScript-Konfiguration
- `e2e/framework/types.ts` – Alle Interfaces (Scenario, Turn, TurnRecord, BehaviorProbe, TurnExpectation, etc.)
- `e2e/framework/ws-client.ts` – `SessionClient` mit WebSocket-Kommunikation
- `e2e/framework/scenario-runner.ts` – Turn-Loop, Nudge-Logik, `phase_complete`-Erkennung
- `e2e/scenarios/s02-reisekosten.json` – Smoke-Test-Szenario (Happy Path, portiert aus `e2e_reisekosten.py`)
- `e2e/run-campaign.ts` – CLI-Einstiegspunkt (Minimal-Version für Smoke-Test)

> **Hinweis zur Ordnerstruktur:** `e2e/` liegt auf Root-Ebene, analog zu `api-contract/`
> und `agent-docs/`. Das Framework ist weder Backend- noch Frontend-Code, sondern testet
> gegen die WebSocket-API des Backends.
> **Voraussetzung:** ADR-009 muss vor Implementierung erstellt werden (AGENTS.md:
> neue Verzeichnisse außerhalb HLA Section 6 erfordern einen ADR).

## Stories

> **Path Note:** Alle Dateipfade folgen dem `e2e-testkampagne-plan.md`. Da `e2e/` ein
> eigenständiges TypeScript-Projekt ist, gelten keine HLA Section 6 Backend-Pfade.
> Die DoD-Kommandos sind TypeScript-spezifisch.

---

### Story 12-01: TypeScript-Projektsetup in `e2e/`

**Als** Entwickler,
**möchte ich** ein korrekt konfiguriertes TypeScript-Projekt in `e2e/`,
**damit** alle weiteren Framework-Dateien typsicher entwickelt und mit `tsx` ausgeführt werden können.

**Akzeptanzkriterien:**

1. `e2e/package.json` existiert mit:
   - `name`: `"e2e-testkampagne"`
   - `type`: `"module"`
   - `scripts.typecheck`: `"tsc --noEmit"`
   - `scripts.test`: `"tsx --test framework/__tests__/*.test.ts"`
   - Abhängigkeiten: `ws` (WebSocket-Client), `tsx` (TypeScript-Runner)
   - DevDependencies: `typescript`, `@types/ws`, `@types/node`
2. `e2e/tsconfig.json` existiert mit:
   - `target`: `"ES2022"` oder neuer
   - `module`: `"ESNext"` oder `"NodeNext"`
   - `strict`: `true`
   - `outDir`: nicht gesetzt (nur `tsx`-Ausführung, kein Build)
   - `rootDir`: `"."`
3. `e2e/.gitignore` existiert mit Einträgen für `node_modules/` und `reports/`
4. `npm install` in `e2e/` läuft fehlerfrei durch
5. `npm run typecheck` in `e2e/` gibt exit 0

**Definition of Done:**

- [x] `e2e/package.json` existiert mit korrekten Feldern
- [x] `e2e/tsconfig.json` existiert mit `strict: true`
- [x] `e2e/.gitignore` enthält `node_modules/` und `reports/`
- [x] `npm install` in `e2e/` exit 0
- [x] `npm run typecheck` in `e2e/` exit 0

---

### Story 12-02: `types.ts` — Alle Interfaces

**Als** Entwickler,
**möchte ich** alle TypeScript-Interfaces für das E2E-Framework in einer zentralen Datei,
**damit** alle Framework-Module typsicher gegen die gleichen Datenstrukturen arbeiten.

**FR/NFR Traceability:** `e2e-testkampagne-plan.md` Abschnitt "Szenario-Format" und
"Was pro Turn erfasst wird".

**Akzeptanzkriterien:**

1. `e2e/framework/types.ts` existiert.
2. `Scenario` Interface mit Feldern:
   - `id: string` (z.B. `"S01"`)
   - `name: string`
   - `description: string`
   - `tags: string[]`
   - `intent: ScenarioIntent`
   - `phases: ScenarioPhases`
   - `behavior_probes: BehaviorProbe[]`
3. `ScenarioIntent` Interface mit Feldern:
   - `process_description: string`
   - `expected_structure_steps: number`
   - `expected_complexity: 'minimal' | 'einfach' | 'mittel' | 'komplex'`
   - `key_concepts: string[]`
   - `forbidden_concepts: string[]`
4. `ScenarioPhases` Interface mit Feldern:
   - `exploration: Turn[]`
   - `strukturierung: Turn[]`
   - `spezifikation: Turn[]`
   - `validierung?: Turn[]`
5. `Turn` Interface mit Feldern:
   - `id: string`
   - `message: string`
   - `action?: 'panic'`
   - `nudges?: string[]`
   - `note?: string`
   - `expect?: TurnExpectation`
6. `TurnExpectation` Interface mit Feldern:
   - `mode_should_be?: string`
   - `flag_should_include?: string[]`
   - `flag_should_not_include?: string[]`
   - `slots_should_increase?: boolean`
   - `response_should_contain?: string[]`
   - `response_should_not_contain?: string[]`
7. `BehaviorProbe` Interface mit Feldern:
   - `after_turn: string`
   - `name: string`
   - `type: 'artifact_check' | 'dialog_check' | 'state_check'`
   - `check: BehaviorProbeCheck`
8. `BehaviorProbeCheck` Interface mit Feldern:
   - `slot_path?: string`
   - `should_contain?: string[]`
   - `should_not_contain?: string[]`
   - `response_pattern?: string`
   - `expected_phase?: string`
   - `expected_mode?: string`
   - `min_filled_slots?: number`
9. `TurnRecord` Interface mit Feldern:
   - `turn_nr: number`
   - `timestamp: string`
   - `scenario_id: string`
   - `phase: string`
   - `step_id: string`
   - `user_message: string`
   - `action?: string`
   - `assistant_response: string`
   - `response_time_ms: number`
   - `state: TurnState`
   - `artifacts?: ArtifactSnapshots`
   - `evaluation: TurnEvaluation`
10. `TurnState` Interface mit Feldern:
    - `aktiver_modus: string`
    - `aktive_phase: string`
    - `phasenstatus: string`
    - `befuellte_slots: number`
    - `bekannte_slots: number`
    - `flags: string[]`
    - `working_memory: Record<string, unknown>`
11. `ArtifactSnapshots` Interface mit Feldern:
    - `exploration: Record<string, unknown>`
    - `struktur: Record<string, unknown>`
    - `algorithmus: Record<string, unknown>`
12. `TurnEvaluation` Interface mit Feldern:
    - `assertions_passed: string[]`
    - `assertions_failed: string[]`
    - `behavior_probes: BehaviorProbeResult[]`
    - `metrics: TurnMetrics`
13. `BehaviorProbeResult` Interface mit Feldern:
    - `name: string`
    - `passed: boolean`
    - `detail: string`
14. `TurnMetrics` Interface mit Feldern:
    - `response_length: number`
    - `slots_delta: number`
    - `mode_changed: boolean`
    - `nudge_used: boolean`
15. `ScenarioResult` Interface mit Feldern:
    - `scenario_id: string`
    - `scenario_name: string`
    - `turns: TurnRecord[]`
    - `final_artifacts: ArtifactSnapshots`
    - `duration_ms: number`
    - `summary: string`
16. `AssertionResult` Interface mit Feldern:
    - `name: string`
    - `status: 'PASS' | 'FAIL' | 'WARN'`
    - `detail: string`
17. `BehaviorScore` Interface mit Feldern:
    - `dimension: string`
    - `rating: 'SEHR_GUT' | 'GUT' | 'BEFRIEDIGEND' | 'MANGELHAFT'`
    - `metrics: Record<string, number>`
    - `findings: string[]`
18. `TurnResponse` Interface mit Feldern:
    - `message: string`
    - `state: TurnState`
    - `artifacts_updated: boolean`
    - `response_time_ms: number`
19. Alle Interfaces exportiert.
20. `e2e/framework/types.ts` ist ≤ 300 Zeilen.

**Definition of Done:**

- [x] `e2e/framework/types.ts` existiert
- [x] Scenario + ScenarioIntent + ScenarioPhases Interfaces mit allen AC-Feldern
- [x] Turn + TurnExpectation Interfaces mit allen AC-Feldern
- [x] BehaviorProbe + BehaviorProbeCheck Interfaces mit allen AC-Feldern
- [x] TurnRecord + TurnState + ArtifactSnapshots Interfaces mit allen AC-Feldern
- [x] TurnEvaluation + BehaviorProbeResult + TurnMetrics Interfaces mit allen AC-Feldern
- [x] ScenarioResult + AssertionResult + BehaviorScore Interfaces mit allen AC-Feldern
- [x] TurnResponse Interface mit allen AC-Feldern
- [x] Alle 18 Interfaces exportiert
- [x] `e2e/framework/types.ts` ist ≤ 300 Zeilen (170 Zeilen)
- [x] `npm run typecheck` in `e2e/` exit 0

---

### Story 12-03: `ws-client.ts` — SessionClient

**Als** Entwickler,
**möchte ich** einen WebSocket/HTTP-Client der direkt mit dem Backend kommuniziert,
**damit** Szenarien ohne Browser gegen die echte Backend-API ausgeführt werden können.

**FR/NFR Traceability:** `e2e-testkampagne-plan.md` Schritt 1, Epic 05 WebSocket-API.

**Akzeptanzkriterien:**

1. `e2e/framework/ws-client.ts` existiert und exportiert `SessionClient`.
2. `SessionClient` Constructor akzeptiert `baseUrl: string` (Default: `http://localhost:8000`).
3. Methode `createProject(name: string): Promise<string>`:
   - `POST /api/projects` mit `{ name }` Body
   - Gibt `projekt_id` zurück
4. Methode `sendMessage(projectId: string, message: string): Promise<TurnResponse>`:
   - Öffnet WebSocket-Verbindung zu `ws://<host>/ws/session/<projectId>`
   - Sendet `{ type: "turn", text: message, datei: null }`
   - Wartet auf `chat_done`, `artifact_update`, `progress_update`, `debug_update` Events
     (bei `error`-Event → Error-Handling gemäß AC7)
   - Gibt strukturierte `TurnResponse` zurück mit:
     - `message: string` (aus `chat_done`)
     - `state: TurnState` (aus `progress_update` + `debug_update`)
     - `response_time_ms: number`
5. Methode `pressButton(projectId: string, button: 'panic'): Promise<TurnResponse>`:
   - Sendet `{ type: "panic" }` über WebSocket
   - Gibt Response zurück
6. Methode `getArtifacts(projectId: string): Promise<ArtifactSnapshots>`:
   - `GET /api/projects/<projectId>/artifacts`
   - Gibt die drei Artefakte zurück
7. Error-Handling:
   - WebSocket-Verbindungsfehler → wirft `ConnectionError` mit beschreibender Message
   - Timeout (konfigurierbar, Default 60s) → wirft `TimeoutError`
   - Backend `error`-Event → wirft `BackendError` mit Event-Message
8. `TurnResponse` Type definiert in `types.ts` (siehe Story 12-02 AC18).
9. `e2e/framework/ws-client.ts` ist ≤ 300 Zeilen.

**Definition of Done:**

- [x] `e2e/framework/ws-client.ts` existiert und exportiert `SessionClient`
- [x] Constructor akzeptiert `baseUrl` mit Default `http://localhost:8000`
- [x] `createProject()` erstellt Projekt via REST API
- [x] `sendMessage()` kommuniziert via WebSocket und gibt `TurnResponse` zurück
- [x] `pressButton()` sendet Panik-Button via WebSocket
- [x] `getArtifacts()` liest Artefakte via REST API
- [x] Timeout- und Fehlerbehandlung implementiert (ConnectionError, TimeoutError, BackendError)
- [x] `TurnResponse` Type in `types.ts` definiert (Story 12-02 AC18)
- [x] `e2e/framework/ws-client.ts` ist ≤ 300 Zeilen (259 Zeilen)
- [x] `npm run typecheck` in `e2e/` exit 0

---

### Story 12-04: `scenario-runner.ts` — Turn-Loop mit Nudge-Handling

**Als** Entwickler,
**möchte ich** einen ScenarioRunner der ein komplettes Szenario automatisch durchspielt,
**damit** jedes Szenario-JSON vollständig ausgeführt und alle TurnRecords gesammelt werden.

**FR/NFR Traceability:** `e2e-testkampagne-plan.md` Schritt 2.

**Akzeptanzkriterien:**

1. `e2e/framework/scenario-runner.ts` existiert und exportiert `ScenarioRunner`.
2. Constructor akzeptiert `client: SessionClient` und `scenario: Scenario`.
3. Methode `run(): Promise<ScenarioResult>`:
   - Erstellt ein neues Projekt via `client.createProject(scenario.name)`
   - Iteriert über alle Phasen (`exploration`, `strukturierung`, `spezifikation`, `validierung`)
   - Für jeden Turn in der Phase:
     a. Sendet `turn.message` via `client.sendMessage()`
     b. Drückt Panik-Button wenn `turn.action === 'panic'`
     c. Prüft `TurnExpectation` (wenn vorhanden) und speichert Ergebnis
     d. Prüft `BehaviorProbe` (wenn `after_turn` === aktueller Turn-ID)
     e. Erzeugt `TurnRecord` mit allen erfassten Daten
   - Nudge-Handling: Wenn nach dem letzten Turn einer Phase `phase_complete` nicht in
     den Flags ist und `turn.nudges[]` definiert sind → sendet Nudge-Messages nacheinander,
     bis `phase_complete` erscheint oder Nudges erschöpft sind
   - Artefakt-Snapshots: Liest Artefakte nach jedem 5. Turn und nach dem letzten Turn
     jeder Phase via `client.getArtifacts()`
   - Gibt `ScenarioResult` zurück mit allen TurnRecords, finalen Artefakten, Gesamtdauer
4. `phase_complete`-Erkennung:
   - Prüft `state.flags` nach jedem Turn auf `"phase_complete"`
   - Wenn `phase_complete` erkannt → wartet auf Moderator-Turn (nächster Turn sollte
     Moderator sein) → geht zur nächsten Phase über
5. Fortschritts-Logging:
   - Gibt pro Turn eine Zeile auf `stderr` aus: `[S02] Turn 3/13 | exploration | 2/9 slots`
6. `TurnExpectation`-Auswertung:
   - `mode_should_be` → prüft `state.aktiver_modus`
   - `flag_should_include` → prüft ob alle Flags in `state.flags` enthalten
   - `flag_should_not_include` → prüft ob keine der Flags in `state.flags` enthalten
   - `slots_should_increase` → prüft ob `state.befuellte_slots` > vorheriger Wert
   - `response_should_contain` → prüft ob alle Keywords in `assistant_response`
   - `response_should_not_contain` → prüft ob keine Keywords in `assistant_response`
7. `e2e/framework/scenario-runner.ts` ist ≤ 300 Zeilen.

**Definition of Done:**

- [x] `e2e/framework/scenario-runner.ts` existiert und exportiert `ScenarioRunner`
- [x] `run()` iteriert über alle Phasen und Turns
- [x] Nudge-Handling implementiert (sendet Nudges wenn `phase_complete` ausbleibt)
- [x] `phase_complete`-Erkennung via `state.flags`
- [x] Artefakt-Snapshots nach jedem 5. Turn und am Phasenende
- [x] `TurnExpectation`-Auswertung für alle 6 Felder
- [x] `BehaviorProbe`-Auswertung nach korrektem Turn
- [x] Fortschritts-Logging auf stderr
- [x] `ScenarioResult` mit TurnRecords, finalen Artefakten, Gesamtdauer
- [x] `e2e/framework/scenario-runner.ts` ist ≤ 300 Zeilen (286 Zeilen)
- [x] `npm run typecheck` in `e2e/` exit 0

---

### Story 12-05: Smoke-Test — S02 Happy Path durchlaufen

**Als** Entwickler,
**möchte ich** verifizieren, dass das Framework ein einfaches Szenario end-to-end durchführt,
**damit** ich sicher bin, dass WebSocket-Kommunikation, Turn-Loop und TurnRecord-Erzeugung korrekt funktionieren.

**FR/NFR Traceability:** `e2e-testkampagne-plan.md` Szenario S02 (Reisekostenabrechnung),
`backend/tests/e2e_reisekosten.py` als Vorlage für die Turn-Definitionen.

**Akzeptanzkriterien:**

1. `e2e/scenarios/s02-reisekosten.json` existiert:
   - Portiert aus `backend/tests/e2e_reisekosten.py` und
     `frontend/test-texte/dialog-reisekosten.jsonl`
   - Mindestens 10 Turns in der Exploration-Phase
   - `intent` mit `key_concepts` (z.B. `["Reisekosten", "Genehmigung", "Belege"]`)
   - `expected_complexity: "einfach"`
   - Keine Eskalationen, kein Nudge-Bedarf (Happy Path)
2. `e2e/run-campaign.ts` existiert als CLI-Einstiegspunkt:
   - Akzeptiert `--scenario <ID>` Flag (z.B. `--scenario S02`)
   - Ohne Flag: lädt alle Szenarien aus `e2e/scenarios/`
   - Instanziiert `SessionClient` mit `BACKEND_URL` aus Umgebungsvariable
     (Default: `http://localhost:8000`)
   - Erstellt `ScenarioRunner` pro Szenario und ruft `run()` auf
   - Gibt Zusammenfassung auf stdout aus
3. `npx tsx e2e/run-campaign.ts --scenario S02` läuft gegen ein laufendes Backend:
   - Erstellt ein Projekt
   - Sendet alle Turns
   - Erzeugt TurnRecords mit `assistant_response` (nicht leer)
   - Erzeugt mindestens einen Artefakt-Snapshot
   - Gibt Zusammenfassung aus (Turns, Dauer, erreichte Phase)
4. Fehlermeldung wenn Backend nicht erreichbar:
   `"Backend nicht erreichbar unter <url>. Bitte Backend starten."`
5. `e2e/run-campaign.ts` ist ≤ 150 Zeilen.

**Definition of Done:**

- [x] `e2e/scenarios/s02-reisekosten.json` existiert mit ≥10 Turns (12 Turns)
- [x] `e2e/run-campaign.ts` existiert mit `--scenario` Flag
- [x] Szenario-Laden aus `e2e/scenarios/` Verzeichnis funktioniert
- [x] Fehlermeldung bei nicht erreichbarem Backend
- [ ] Smoke-Test: `npx tsx e2e/run-campaign.ts --scenario S02` erzeugt TurnRecords (manuell gegen laufendes Backend verifiziert)
- [x] `e2e/run-campaign.ts` ist ≤ 150 Zeilen (143 Zeilen)
- [x] `npm run typecheck` in `e2e/` exit 0

---

### Implementation Order

Stories müssen in dieser Reihenfolge implementiert werden:

1. **12-01** (Projektsetup) — keine Abhängigkeiten
2. **12-02** (types.ts) — hängt von 12-01 ab (braucht TypeScript-Konfiguration)
3. **12-03** (ws-client.ts) — hängt von 12-02 ab (braucht Types)
4. **12-04** (scenario-runner.ts) — hängt von 12-02 und 12-03 ab
5. **12-05** (Smoke-Test) — hängt von allen vorherigen Stories ab
