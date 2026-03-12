# Epic 02 – Execution Engine (Executor + JSON Patch)

## Summary

Implement the `Executor` – the only component allowed to write to artifacts. All artifact
mutations go through the Executor as RFC 6902 JSON Patch operations. Invalid or failing
patches must trigger a full rollback, leaving artifacts in their previous valid state.

This is a critical correctness boundary: no other component ever writes directly to an
artifact. This epic also defines the `ArtifactTemplate` schema that patches must conform to.

This epic corresponds to **Implementation Step 2** in `AGENTS.md` / `hla_architecture.md`.

## Goal

A battle-tested Executor that applies JSON Patch operations to artifacts atomically, validates
patches against the artifact schema, and rolls back cleanly on any failure. Structural
changes to `Strukturschritte` automatically propagate their invalidation signal back to the
caller so the Orchestrator can mark affected `Algorithmusabschnitte` as invalidated.

## Testable Increment

- `pytest backend/tests/test_executor.py` → all tests pass, including:
  - Valid patch applied → artifact updated, version incremented
  - Invalid RFC 6902 syntax → artifact unchanged, `ExecutorResult.success == False`
  - Path not in Template-Schema → artifact unchanged, error returned
  - Forbidden operation type (e.g. `copy`) → rejected before any write
  - Partially applied patch sequence (first ops succeed, later op fails) → full rollback
  - Preservation-Check: patch that modifies unaddressed fields → rollback
  - Invalidation: `beschreibung` of a `Strukturschritt` changed → `invalidated_abschnitt_ids` returned
  - Invalidation NOT triggered by `titel` / `reihenfolge` changes
- No HTTP server or LLM required; pure unit tests

## Dependencies

- Epic 01 (Pydantic models must exist for the Executor to operate on)

## Key Deliverables

- `backend/artifacts/template_schema.py` – `ArtifactTemplate` Pydantic-Modell +
  statische Template-Instanzen für alle drei Artefakttypen + `is_valid_patch(op, path) → bool`
- `backend/core/executor.py` – `Executor`-Klasse mit
  - `apply_patches(artifact_type, artifact, patches) → ExecutorResult`
  - `ExecutorResult` Dataclass mit `success`, `artifact`, `invalidated_abschnitt_ids`, `error`
  - Volle Pipeline: RFC-6902-Validierung → Template-Check → Snapshot → Patch-Anwendung →
    Preservation-Check → Invalidierungs-Erkennung → Version-Bump
- `backend/tests/test_executor.py` – vollständige Test-Suite gemäß TDD

## OpenAPI Contract Note

The `Executor` is an internal component — it has no API surface of its own. However, the
patch-operation schema it validates against will be referenced in the WebSocket message
contract defined in Epic 05. The `ArtifactTemplate.path_patterns` entries in
`backend/artifacts/template_schema.py` **must** include `description` fields with enough
detail to derive the WebSocket message schemas later — no separate documentation pass needed.

## Status

**Abgeschlossen:** 2026-03-12
**Tests:** 39 neue Executor-Tests, 98 gesamt grün
**Commit:** 65aaf39

---

## Stories

### Story 02-01 – ArtifactTemplate-Schema implementieren

**Als** Entwickler (oder AI-Agent)
**möchte ich** ein maschinenlesbares Template-Schema für alle drei Artefakttypen,
**damit** der Executor RFC 6902 Pfade vor der Ausführung gegen eine vollständige,
statische Allowlist prüfen kann und das LLM in späteren Epics einen maschinenlesbaren
Orientierungsrahmen für gültige Patch-Pfade erhält.

**TDD-Reihenfolge:** Tests in `backend/tests/test_executor.py` zuerst schreiben (rot),
dann `backend/artifacts/template_schema.py` implementieren (grün).

**Akzeptanzkriterien:**

- `backend/artifacts/template_schema.py` enthält:

  **`TemplatePathPattern`** (Pydantic `BaseModel`):
  - `pattern: str` — Python-Regex; das Segment `{id}` entspricht `[^/]+` und matcht
    beliebige dict-Keys (z. B. `slot_id`, `schritt_id`, `abschnitt_id`, `aktion_id`)
  - `allowed_ops: list[Literal["add", "replace", "remove"]]`
  - `description: str` — Beschreibung des Pfads für LLM-Kontext (OpenAPI-Vorbereitung)

  **`ArtifactTemplate`** (Pydantic `BaseModel`):
  - `artifact_type: Literal["exploration", "structure", "algorithm"]`
  - `path_patterns: list[TemplatePathPattern]`
  - Methode `is_valid_patch(self, op: str, path: str) -> bool`:
    - Gibt `True` genau dann, wenn `path` auf ein `pattern` matcht UND `op` in
      `allowed_ops` dieses Patterns enthalten ist
    - Gibt `False` für jede unbekannte `op` oder jeden unbekannten `path`

  **Statische Template-Instanzen** (Modul-Ebene, unveränderlich):

  `EXPLORATION_TEMPLATE` — erlaubte Pfade:
  - `/slots/{id}` — `add`, `remove`
    - Gesamten Slot hinzufügen oder entfernen
  - `/slots/{id}/titel` — `replace`
    - Titel/Thema eines Slots aktualisieren (SDD 5.3: Pflichtfeld)
  - `/slots/{id}/inhalt` — `replace`
    - Freitextinhalt eines Slots aktualisieren
  - `/slots/{id}/completeness_status` — `replace`
    - Completeness-Status eines Slots setzen

  `STRUCTURE_TEMPLATE` — erlaubte Pfade:
  - `/schritte/{id}` — `add`, `remove`
    - Gesamten Strukturschritt hinzufügen oder entfernen
  - `/schritte/{id}/titel` — `replace`
  - `/schritte/{id}/typ` — `replace`
  - `/schritte/{id}/beschreibung` — `replace`
  - `/schritte/{id}/reihenfolge` — `replace`
  - `/schritte/{id}/nachfolger` — `replace`
  - `/schritte/{id}/bedingung` — `replace`
  - `/schritte/{id}/ausnahme_beschreibung` — `replace`
  - `/schritte/{id}/algorithmus_ref` — `replace`
  - `/schritte/{id}/completeness_status` — `replace`
  - `/schritte/{id}/algorithmus_status` — `replace`
  - `/schritte/{id}/spannungsfeld` — `replace`

  `ALGORITHM_TEMPLATE` — erlaubte Pfade:
  - `/abschnitte/{id}` — `add`, `remove`
    - Gesamten Algorithmusabschnitt hinzufügen oder entfernen
  - `/abschnitte/{id}/titel` — `replace`
  - `/abschnitte/{id}/struktur_ref` — `replace`
  - `/abschnitte/{id}/completeness_status` — `replace`
  - `/abschnitte/{id}/status` — `replace`
  - `/abschnitte/{id}/aktionen/{id}` — `add`, `remove`
    - Einzelne EMMA-Aktion hinzufügen oder entfernen
  - `/abschnitte/{id}/aktionen/{id}/aktionstyp` — `replace`
  - `/abschnitte/{id}/aktionen/{id}/parameter` — `replace`
  - `/abschnitte/{id}/aktionen/{id}/nachfolger` — `replace`
  - `/abschnitte/{id}/aktionen/{id}/emma_kompatibel` — `replace`
  - `/abschnitte/{id}/aktionen/{id}/kompatibilitaets_hinweis` — `replace`

  **`TEMPLATES: dict[str, ArtifactTemplate]`** — Map `artifact_type → Template` für
  den Executor-Lookup: `{"exploration": EXPLORATION_TEMPLATE, ...}`

- `ArtifactTemplate.is_valid_patch()` verwendet Regex-Matching mit `re.fullmatch`
  (kein Partial-Match), sodass Präfix-Pfade wie `/slots` nicht akzeptiert werden

- Alle drei Templates bestehen `template.model_json_schema()` ohne Fehler
- `mypy backend/artifacts/template_schema.py` → 0 Fehler
- `ruff check backend/artifacts/template_schema.py` → 0 Fehler

**Tests in `backend/tests/test_executor.py` (Template-Abschnitt):**

- **T-1 (falsifiable):** Jeder Test prüft exakte Rückgabewerte, nicht nur Nicht-Exception.
- Test: `EXPLORATION_TEMPLATE.is_valid_patch("replace", "/slots/slot_01/titel")` → `True`
  (SDD 5.3 Pflichtfeld — muss patchbar sein)
- Test: `EXPLORATION_TEMPLATE.is_valid_patch("replace", "/slots/slot_01/inhalt")` → `True`
- Test: `EXPLORATION_TEMPLATE.is_valid_patch("add", "/slots/slot_01/inhalt")` → `False`
  (nur `replace` erlaubt auf `/inhalt`)
- Test: `EXPLORATION_TEMPLATE.is_valid_patch("replace", "/slots/slot_01/nonexistent")` → `False`
  (Pfad nicht im Schema)
- Test: `STRUCTURE_TEMPLATE.is_valid_patch("add", "/schritte/s01")` → `True`
- Test: `STRUCTURE_TEMPLATE.is_valid_patch("copy", "/schritte/s01/titel")` → `False`
  (verbotene Operation)
- Test: `ALGORITHM_TEMPLATE.is_valid_patch("add", "/abschnitte/a01/aktionen/ak01")` → `True`
- Test: `ALGORITHM_TEMPLATE.is_valid_patch("replace", "/abschnitte/a01/aktionen/ak01/emma_kompatibel")` → `True`
- Test: `TEMPLATES` enthält genau die Keys `"exploration"`, `"structure"`, `"algorithm"`

**Definition of Done:**

- [x] `backend/artifacts/template_schema.py` existiert
- [x] `TemplatePathPattern` mit `pattern`, `allowed_ops`, `description`
- [x] `ArtifactTemplate` mit `artifact_type`, `path_patterns`, `is_valid_patch()`
- [x] `EXPLORATION_TEMPLATE` enthält alle oben gelisteten Pfade inkl. `allowed_ops`
- [x] `STRUCTURE_TEMPLATE` enthält alle oben gelisteten Pfade inkl. `allowed_ops`
- [x] `ALGORITHM_TEMPLATE` enthält alle oben gelisteten Pfade inkl. `allowed_ops`
- [x] `TEMPLATES`-Dict mit allen 3 Einträgen vorhanden
- [x] `is_valid_patch()` verwendet `re.fullmatch` (kein Partial-Match)
- [x] Alle 9 Template-Tests in `test_executor.py` grün
- [x] `ruff check .` → exit 0
- [x] `ruff format --check .` → exit 0
- [x] `python -m mypy . --explicit-package-bases` → exit 0
- [x] `pytest --tb=short -q` → exit 0, 0 failures

---

### Story 02-02 – Executor: RFC-6902-Validierung, Patch-Anwendung und Preservation-Check

**Als** Entwickler (oder AI-Agent)
**möchte ich** einen `Executor` der RFC 6902 Patches syntaktisch validiert, gegen das
Template-Schema prüft, atomar anwendet und bei jedem Fehler vollständig zurückrollt,
**damit** kein LLM-Output jemals den Artefaktzustand inkonsistent hinterlassen kann.

**TDD-Reihenfolge:** Tests für jeden Szenario-Block zuerst schreiben (rot), dann den
jeweiligen Pipeline-Schritt implementieren (grün).

**Akzeptanzkriterien:**

- `backend/core/executor.py` enthält:

  **`ExecutorResult`** (`dataclass`):
  - `success: bool`
  - `artifact: ExplorationArtifact | StructureArtifact | AlgorithmArtifact | None`
    — das aktualisierte Artefakt (bei Erfolg), `None` bei Fehler
  - `invalidated_abschnitt_ids: list[str]` — Standardwert `[]`
    — Abschnitt-IDs die nach Anwendung invalidiert werden müssen (befüllt von Story 02-03)
  - `error: str | None` — Standardwert `None`
    — beschreibender Fehlertext bei `success=False`

  **`Executor`** (Klasse):
  - `apply_patches(self, artifact_type: Literal["exploration", "structure", "algorithm"], artifact: ExplorationArtifact | StructureArtifact | AlgorithmArtifact, patches: list[dict]) -> ExecutorResult`
  - Führt die folgende Pipeline **sequenziell** aus; bei jedem Fehler wird sofort auf den
    Snapshot zurückgerollt:

  **Pipeline Schritt 1 — Formale RFC 6902 Validierung:**
  - Jedes Element in `patches` ist ein `dict` mit genau dem Key `"op"` und `"path"`,
    ggf. `"value"` (bei `add`, `replace`)
  - `"op"` muss in `{"add", "replace", "remove"}` sein — jeder andere Wert (`"copy"`,
    `"move"`, `"test"`, etc.) → sofortiger Fehler ohne Snapshot
  - `"path"` muss ein nicht-leerer String sein, der mit `/` beginnt
  - Leere `patches`-Liste → `ExecutorResult(success=True, artifact=artifact)`
    (Identitätsoperation, kein Version-Bump)

  **Pipeline Schritt 2 — Template-Schema-Prüfung:**
  - Für jeden Patch: `TEMPLATES[artifact_type].is_valid_patch(op, path)` muss `True` ergeben
  - Schlägt ein Pfad/Op-Kombination fehl → Fehler mit Hinweis auf den abgelehnten Pfad
  - Keine Schreiboperation wurde noch ausgeführt (Validierung vor Snapshot)

  **Pipeline Schritt 3 — Atomarer Snapshot:**
  - Deep-Copy des Artefakts als `dict` via `artifact.model_dump()` — dient als Rollback-Punkt
  - Snapshot wird NACH den Validierungsschritten (Schritte 1+2) erstellt

  **Pipeline Schritt 4 — Patch-Anwendung:**
  - Serialisiert das Artefakt zu einem `dict` via `artifact.model_dump()`
  - Wendet alle Patches atomisch an via `jsonpatch.apply_patch(data, patches, in_place=False)`
  - Bei `JsonPatchException` (z. B. Pfad existiert nicht, falscher Typ) → Rollback auf
    Snapshot, Fehler zurückgeben
  - Deserialisiert das Ergebnis zurück in das Pydantic-Modell via `model_validate()`
  - Bei Pydantic-`ValidationError` (Typ-Verletzung nach Patch) → Rollback, Fehler

  **Pipeline Schritt 5 — Preservation-Check:**
  - Vergleicht das originale `model_dump()`-Dict (Snapshot) mit dem gepatchten Dict
  - Ermittelt die Menge der tatsächlich geänderten JSON-Pfade (flache Schlüsselmengen
    auf erster Ebene der Top-Level-Collections)
  - Prüft, dass ausschließlich Pfade geändert wurden, die in `patches` adressiert wurden
  - Bei Abweichung (nicht adressierte Felder geändert) → Rollback, Fehler mit Pfadangabe
  - **Hinweis:** In der Praxis schützt dieser Check vor unerwarteten Seiteneffekten
    (z. B. Patches die übergeordnete Felder überschreiben statt Unterfelder)

  **Pipeline Schritt 7 — Version-Bump:**
  - `artifact.version += 1` auf dem aktualisierten Artefakt (nach erfolgreichem Preservation-Check)
  - Nur bei nicht-leerer `patches`-Liste (Identitätsoperationen erhalten die Version)

  **Logging:**
  - Jeder Executor-Aufruf wird via `structlog` geloggt:
    - Auf INFO-Level: `artifact_type`, Anzahl Patches, `success`, neue Version
    - Auf WARNING-Level: Fehlertyp und Fehlertext bei `success=False`

**Tests in `backend/tests/test_executor.py` (Executor-Kern-Abschnitt):**

Fixture `executor: Executor` — Instanz ohne Konfiguration.
Fixture `exploration_artifact` — `ExplorationArtifact` mit einem vordefinierten `ExplorationSlot`
(slot_id=`"s01"`, bezeichnung=`"Test"`, completeness_status=`leer`), version=0.

- **Happy Path:**
  - Test: Gültiger `replace`-Patch auf `/slots/s01/inhalt` → `result.success == True`,
    `result.artifact.slots["s01"].inhalt == <neuer Wert>`, `result.artifact.version == 1`
  - Test: Gültiger `add`-Patch auf `/slots/s02` mit vollständigem Slot-Objekt →
    `result.success == True`, `"s02" in result.artifact.slots`, `result.artifact.version == 1`
  - Test: Gültiger `remove`-Patch auf `/slots/s01` →
    `result.success == True`, `"s01" not in result.artifact.slots`, `result.artifact.version == 1`
  - Test: Leere Patches-Liste → `result.success == True`, `result.artifact.version == 0`
    (kein Version-Bump)

- **RFC 6902 Syntaxfehler (Schritt 1) — T-2 negative tests:**
  - Test: `"op": "copy"` → `result.success == False`, Artefakt unverändert
    (version bleibt 0), `result.error` ist nicht leer
  - Test: `"path": ""` (leerer Pfad) → `result.success == False`, Artefakt unverändert
  - Test: Dict ohne `"op"`-Key → `result.success == False`, Artefakt unverändert
  - Test: Dict ohne `"path"`-Key → `result.success == False`, Artefakt unverändert

- **Template-Verletzung (Schritt 2) — T-2 negative tests:**
  - Test: Gültige RFC-6902-Syntax, aber Pfad nicht im Template
    (`/slots/s01/nonexistent`) → `result.success == False`, Artefakt unverändert (version 0)
  - Test: Gültige Syntax, gültiger Pfad, aber verbotene Op
    (`add` auf `/slots/s01/inhalt`) → `result.success == False`

- **Patch-Fehler (Schritt 4):**
  - Test: Patch auf nicht-existierenden Slot (`replace /slots/s99/inhalt`) →
    `result.success == False`, Artefakt unverändert (version 0)
  - Test: Mehrere Patches — erster valide, zweiter auf nicht-existierenden Pfad →
    `result.success == False`, Artefakt unverändert (version 0) — vollständiger Rollback

- **Preservation-Check (Schritt 5):**
  - Test: Patch-Objekt das korrekt auf `/slots/s01/inhalt` zeigt, aber durch
    Manipulation des `model_dump()`-Dicts (simuliert durch manuelles Hinzufügen eines
    Felds vor Neuvalidierung) ein nicht-adressiertes Feld ändert →
    `result.success == False`, Artefakt unverändert
    *(Hinweis: Dieser Test muss den Preservation-Check direkt testen — am einfachsten
    durch Monkey-Patching von `jsonpatch.apply_patch` oder durch einen Patch auf
    ein Unterfeld das das Parent-Dict ersetzt)*

- **T-3 (tight assertions):**
  - Bei Erfolg: Assertion auf exakten Feldwert (`==`), nicht nur `is not None`
  - Bei Fehler: Assertion auf `result.success == False` UND `result.error is not None`
    UND `result.artifact is None`

**Definition of Done:**

- [x] `backend/core/executor.py` existiert
- [x] `ExecutorResult` Dataclass mit `success`, `artifact`, `invalidated_abschnitt_ids`, `error`
- [x] `Executor.apply_patches()` implementiert mit korrekter Typ-Annotation (mypy-sauber)
- [x] Pipeline Schritt 1 (RFC-6902-Syntaxcheck) implementiert
- [x] Pipeline Schritt 2 (Template-Schema-Prüfung) implementiert
- [x] Pipeline Schritt 3 (Snapshot via `model_dump()`) implementiert
- [x] Pipeline Schritt 4 (Patch-Anwendung via `jsonpatch`) implementiert
- [x] Pipeline Schritt 5 (Preservation-Check) implementiert
- [x] Pipeline Schritt 6 (Invalidierungs-Check) ist bewusst NICHT in dieser Story — wird in Story 02-03 implementiert
- [x] Pipeline Schritt 7 (Version-Bump bei nicht-leerem Patch) implementiert
- [x] Logging via `structlog` für jeden Aufruf (INFO und WARNING)
- [x] Alle Happy-Path-Tests grün (≥ 4 Tests)
- [x] Alle Syntaxfehler-Tests grün (≥ 4 Tests)
- [x] Alle Template-Verletzungs-Tests grün (≥ 2 Tests)
- [x] Alle Patch-Fehler-Tests grün inkl. Rollback-Test (≥ 2 Tests)
- [x] Preservation-Check-Test grün (≥ 1 Test)
- [x] `ruff check .` → exit 0
- [x] `ruff format --check .` → exit 0
- [x] `python -m mypy . --explicit-package-bases` → exit 0
- [x] `pytest --tb=short -q` → exit 0, 0 failures

---

### Story 02-03 – Executor: Invalidierungslogik und vollständige Test-Suite

**Als** Entwickler (oder AI-Agent)
**möchte ich** dass der Executor bei Patches auf Strukturschritte erkennt, welche
Algorithmusabschnitte invalidiert werden müssen, und diese IDs im `ExecutorResult`
zurückgibt — ohne selbst das Algorithmusartefakt zu schreiben,
**damit** der Orchestrator (Epic 03) die Invalidierungsentscheidung kontrolliert trifft
und ein separater Executor-Call das Algorithmusartefakt atomar aktualisiert.

**TDD-Reihenfolge:** Invalidierungstests zuerst schreiben (rot), dann Logik in
`Executor.apply_patches` ergänzen (grün).

**Akzeptanzkriterien:**

**Invalidierungsregel (SDD 5.5, SDD Abschnitt "Invalidierungsregel"):**

- Die Invalidierungslogik tritt in Kraft wenn `artifact_type == "structure"` UND
  das Patch-Objekt mindestens einen `replace`- oder `add`/`remove`-Patch enthält,
  der auf einen der folgenden Felder eines Strukturschritts zielt:
  - `beschreibung`
  - `typ`
  - `bedingung`
  - `ausnahme_beschreibung`
- Patches auf `titel`, `reihenfolge`, `nachfolger`, `algorithmus_ref`, `spannungsfeld`,
  `completeness_status`, `algorithmus_status` lösen **keine** Invalidierung aus.
- Ein `add`- oder `remove`-Patch auf `/schritte/{id}` (ganzer Schritt) löst Invalidierung
  aus, da `beschreibung` und `typ` dadurch implizit verändert werden.

**`apply_patches` ergänzt `ExecutorResult.invalidated_abschnitt_ids` wie folgt:**
- Nach erfolgreichem Preservation-Check (Schritt 5): Für jeden geänderten Strukturschritt
  (anhand der Patch-Pfade bestimmt) werden dessen `algorithmus_ref`-IDs gesammelt
- Alle gesammelten IDs werden dedupliziert und in `invalidated_abschnitt_ids` zurückgegeben
- `invalidated_abschnitt_ids` ist **niemals** `None`, immer eine Liste (ggf. leer)
- Der Executor schreibt **nicht** selbst auf das Algorithmusartefakt — er gibt nur die IDs zurück

**Verantwortungsteilung für die vollständige Invalidierung (SDD 5.5):**
SDD 5.5 fordert, dass bei Invalidierung **zwei** Flags gesetzt werden:
1. `Algorithmusabschnitt.status` → `invalidiert` (für alle referenzierten Abschnitte)
2. `Strukturschritt.algorithmus_status` → `invalidiert` (auf dem auslösenden Strukturschritt)

Der Executor übernimmt ausschließlich Schritt 1 — er gibt die betroffenen `abschnitt_ids` zurück.
Schritt 2 liegt in der Verantwortung des **Orchestrators (Epic 03)**: Der Orchestrator führt nach
Erhalt der `invalidated_abschnitt_ids` einen separaten `Executor.apply_patches()`-Aufruf aus, der
`/schritte/{schritt_id}/algorithmus_status` → `replace: "invalidiert"` setzt.
Diese Aufteilung ist bewusst: Der Executor bleibt zustandslos; der Orchestrator koordiniert
alle Schreiboperationen gemäß SDD 6.3 (11-Schritt-Zyklus).

**Tests in `backend/tests/test_executor.py` (Invalidierungs-Abschnitt):**

Fixture `structure_artifact_with_refs` — `StructureArtifact` mit:
- Schritt `"s01"`: `typ=aktion`, `beschreibung="alt"`, `algorithmus_ref=["a01", "a02"]`
- Schritt `"s02"`: `typ=entscheidung`, `beschreibung="entscheidung"`, `algorithmus_ref=["a03"]`
- `version=0`

- **Invalidierung ausgelöst (T-2 happy path):**
  - Test: `replace /schritte/s01/beschreibung` → `result.invalidated_abschnitt_ids == ["a01", "a02"]`
    (exakte Menge, T-3: `==` nicht `in`)
  - Test: `replace /schritte/s01/typ` → `result.invalidated_abschnitt_ids == ["a01", "a02"]`
  - Test: `replace /schritte/s02/bedingung` → `result.invalidated_abschnitt_ids == ["a03"]`
  - Test: `replace /schritte/s02/ausnahme_beschreibung` → `result.invalidated_abschnitt_ids == ["a03"]`
  - Test: Beide Schritte in einem Batch-Patch (`s01/beschreibung` + `s02/beschreibung`) →
    `set(result.invalidated_abschnitt_ids) == {"a01", "a02", "a03"}` (dedupliziert)
  - Test: `remove /schritte/s01` (ganzen Schritt entfernen) →
    `result.invalidated_abschnitt_ids` enthält `"a01"` und `"a02"`

- **Keine Invalidierung (T-2 negative tests):**
  - Test: `replace /schritte/s01/titel` → `result.invalidated_abschnitt_ids == []`
  - Test: `replace /schritte/s01/reihenfolge` → `result.invalidated_abschnitt_ids == []`
  - Test: `replace /schritte/s01/nachfolger` → `result.invalidated_abschnitt_ids == []`
  - Test: `replace /schritte/s01/algorithmus_ref` → `result.invalidated_abschnitt_ids == []`
  - Test: `replace /schritte/s01/spannungsfeld` → `result.invalidated_abschnitt_ids == []`
  - Test: `replace /schritte/s01/completeness_status` → `result.invalidated_abschnitt_ids == []`
  - Test: `replace /schritte/s01/algorithmus_status` → `result.invalidated_abschnitt_ids == []`

- **Kein algorithmus_ref → leere Liste:**
  - Test: Strukturschritt ohne `algorithmus_ref`, Patch auf `beschreibung` →
    `result.invalidated_abschnitt_ids == []`
  - Test: `add /schritte/s_new` (neuer Schritt, `algorithmus_ref=[]`) →
    `result.success == True`, `result.invalidated_abschnitt_ids == []`
    *(add eines neuen Schritts löst die Invalidierungslogik aus, aber da noch keine
    Algorithmusreferenzen existieren, ist die resultierende Menge leer)*

- **Invalidierung bei gescheitertem Patch → keine IDs:**
  - Test: Invalidierender Patch der in Schritt 4 scheitert (Pfad nicht existent) →
    `result.success == False`, `result.invalidated_abschnitt_ids == []`

- **Nicht-Structure Artefakte → keine Invalidierung:**
  - Test: `replace /slots/s01/inhalt` auf ExplorationArtifact →
    `result.invalidated_abschnitt_ids == []`

**Gesamte Test-Suite Vollständigkeit (T-4):**

Abschluss-Check: `backend/tests/test_executor.py` deckt alle Akzeptanzkriterien aller
drei Stories dieses Epics ab:

| Kategorie | Mindest-Testanzahl |
|---|---|
| Template-Validierung (`is_valid_patch`) | ≥ 9 Tests |
| Executor Happy Path (Patch angewendet) | ≥ 4 Tests |
| RFC-6902-Syntaxfehler | ≥ 4 Tests |
| Template-Schema-Verletzung | ≥ 2 Tests |
| Patch-Fehler / Rollback | ≥ 2 Tests |
| Preservation-Check | ≥ 1 Test |
| Invalidierung ausgelöst | ≥ 6 Tests |
| Keine Invalidierung | ≥ 7 Tests |
| Randfall: kein `algorithmus_ref` / neuer Schritt | ≥ 2 Tests |
| Randfall: Fehler → keine IDs | ≥ 1 Test |
| **Gesamt** | **≥ 38 Tests** |

**Definition of Done:**

- [x] `Executor.apply_patches()` befüllt `invalidated_abschnitt_ids` korrekt für
      alle triggerenden Felder: `beschreibung`, `typ`, `bedingung`, `ausnahme_beschreibung`
- [x] `invalidated_abschnitt_ids` ist bei `add`/`remove` auf ganzen Schritt befüllt
- [x] `invalidated_abschnitt_ids` ist bei `add` eines neuen Schritts ohne `algorithmus_ref` leer (`[]`)
- [x] `invalidated_abschnitt_ids` ist leer bei nicht-triggerenden Feldern (`titel` etc.)
- [x] `invalidated_abschnitt_ids` ist leer wenn `success == False`
- [x] `invalidated_abschnitt_ids` ist leer für `ExplorationArtifact` und `AlgorithmArtifact`
- [x] Epic-Dokument beschreibt explizit: `Strukturschritt.algorithmus_status` wird vom Orchestrator (Epic 03) gesetzt, nicht vom Executor (siehe Verantwortungsteilung-Abschnitt in Story 02-03)
- [x] Alle Invalidierungstests grün (≥ 6 positive + ≥ 7 negative + ≥ 3 Randfälle)
- [x] Gesamte Test-Suite ≥ 38 Tests, alle grün (39 Tests)
- [x] Kein Test ist tautologisch (T-1 geprüft: jeder Test würde bei korrekter Regression scheitern)
- [x] Alle Tests prüfen exakte Werte (`==`), nicht nur Truthiness (T-3)
- [x] `ruff check .` → exit 0
- [x] `ruff format --check .` → exit 0
- [x] `python -m mypy . --explicit-package-bases` → exit 0
- [x] `pytest --tb=short -q` → exit 0, 0 failures
- [x] `backend/tests/test_executor.py` existiert
- [x] `backend/artifacts/template_schema.py` existiert
- [x] `backend/core/executor.py` existiert
