# CCB Review: CR-012 — Strukturgraph Bidirektionale Verifikation

| Feld | Wert |
|---|---|
| **CR** | CR-012 |
| **Review-Datum** | 2026-03-27 |
| **Review-Nr.** | 1 |
| **Empfehlung** | APPROVE WITH CONDITIONS |

## Zusammenfassung

CR-012 wurde durch 6 unabhängige Fachexperten geprüft (Datenmodell, Orchestrator, Prompts, Tests, SDD/ADR, Abhängigkeiten). Der CR ist architektonisch sound, adressiert eine echte Qualitätslücke (Graph-Konsistenzprüfung O(n) → O(1)) und ist vollständig abwärtskompatibel. Zwei Bedingungen müssen bei der Implementierung berücksichtigt werden: die Entscheidung Code-Guardrail vs. LLM-Pflege muss getroffen werden, und die `reihenfolge`-Korrektur in den Prompts ist bereits erledigt.

## Empfehlung

**APPROVE WITH CONDITIONS**

Der CR ist gut durchdacht, korrekt spezifiziert und konfliktfrei mit allen bestehenden CRs. Zwei Bedingungen (siehe unten) betreffen Implementierungsdetails, die der CR selbst als Empfehlung nennt aber nicht entscheidet.

## Blocker (müssen behoben werden)

Keine Blocker identifiziert.

## Verbesserungsvorschläge (sollten eingearbeitet werden)

1. **Code-Guardrail als Pflicht festlegen, nicht als Empfehlung**: CR-012 §8 empfiehlt einen Code-Guardrail (`_derive_vorgaenger_from_nachfolger` analog zu `_derive_nachfolger_from_regeln`), lässt aber offen ob LLM-Pflege oder automatische Ableitung. Drei Experten (Orchestrator, Prompt, Test) bestätigen unabhängig: LLM-Pflege ist zu fehleranfällig. **Bedingung: Implementierung MUSS den Code-Guardrail umsetzen.** Konsequenz: `vorgaenger` wird nicht in Patch-Beispielen der Prompts gezeigt, sondern automatisch nach jedem Patch-Cycle abgeleitet. Das spart ~200 Tokens pro Prompt-Call und eliminiert das Hauptrisiko.

2. **`reihenfolge`-Korrektur streichen**: CR-012 §3 Punkt 3 fordert die Änderung der `reihenfolge`-Beschreibung von "Position im Prozessablauf" auf "Anzeigereihenfolge". Der Prompt-Experte hat verifiziert, dass **beide Prompts bereits die korrekte Beschreibung verwenden** (`init_structuring.md:243` — "Anzeigereihenfolge (1, 2, 3, ...). Nur für Sortierung", `structuring.md:195` — "Anzeigereihenfolge... Nur für Sortierung, nicht für Ablauflogik"). **Bedingung: Prompt-Änderung für `reihenfolge` entfällt. Nur SDD muss aktualisiert werden.**

3. **Prompt-Änderungen minimieren (Folge von Bedingung 1)**: Wenn der Code-Guardrail umgesetzt wird, reduzieren sich die Prompt-Änderungen auf:
   - Schema-Tabelle: 1 Zeile `vorgaenger` hinzufügen (init_structuring.md + structuring.md)
   - Graph-Konsistenz-Regel: Bidirektionalitätsprüfung ergänzen (structuring.md:47-54)
   - First-Turn-Direktive: Kurzer Hinweis "vorgaenger wird automatisch abgeleitet"
   - Patch-Beispiele: **Nicht anfassen** (Guardrail macht LLM-Pflege überflüssig)

4. **Validator-Logik für alte Artefakte präzisieren**: Der Validator sollte `vorgaenger` bei alten Artefakten (mit Default `[]`) automatisch aus `nachfolger` ableiten, bevor er die Konsistenzprüfung durchführt. Sonst: Falsch-positive Kritisch-Meldungen für alle bestehenden Artefakte.

5. **Executor braucht keine Änderung**: Der Datenmodell-Experte hat bestätigt, dass `vorgaenger` automatisch als nicht-invalidierend behandelt wird, weil es nicht in `_INVALIDATING_FIELDS` steht (`executor.py:38`). Punkt 4 im Änderungsplan kann entfallen.

## Hinweise

1. **Konvergenz-Redundanz**: Mit `vorgaenger` wird `konvergenz` teilweise redundant — wenn s3 `vorgaenger: ["s2", "s2a"]` hat, ist erkennbar dass s3 ein Merge-Punkt ist. Das ist kein Blocker, aber eine Beobachtung für zukünftige CRs.

2. **CR-003 ADR nicht referenziert**: CR-012 referenziert CR-002 ADR, aber nicht CR-003 ADR (Slot-Konsolidierung). Kein Konflikt, aber für Transparenz könnte es erwähnt werden.

3. **OP-16 (Fehlerkanten)**: CR-012 adressiert OP-16 nicht — das ist korrekt so, da es ein separates architektonisches Problem ist.

4. **Token-Overhead**: ~300-400 zusätzliche Tokens wenn `vorgaenger` in alle Patch-Beispiele aufgenommen würde. Mit Code-Guardrail (Bedingung 1) reduziert sich das auf ~50 Tokens (nur Schema-Tabelle + Hinweis).

5. **~30+ Tests müssen Fixtures aktualisieren**: Da `vorgaenger` einen Default `[]` hat, brechen die Tests nicht — aber 10+ Test-Factories (`_make_schritt()` in verschiedenen Test-Dateien) sollten das neue Feld der Vollständigkeit halber setzen.

## Bestätigungen (CR-Behauptungen, die verifiziert wurden)

1. **Modellkompatibilität bestätigt**: `vorgaenger: list[str] = Field(default_factory=list)` folgt dem etablierten Pattern (`nachfolger`, `regeln`, `schleifenkoerper`, `algorithmus_ref` verwenden alle `Field(default_factory=list)`). Referenz: `models.py:152-165`.

2. **Abwärtskompatibilität bestätigt**: Pydantic v2 initialisiert fehlende Felder mit Default `[]`. Bestehende Artefakte deserialisieren fehlerfrei. `model_validate()` und `model_dump()` funktionieren korrekt.

3. **Nicht-Invalidierung bestätigt**: `nachfolger` und `reihenfolge` sind NICHT in `_INVALIDATING_FIELDS` (`executor.py:38`). `vorgaenger` wird automatisch ebenso behandelt — keine Code-Änderung nötig.

4. **Template-Schema-Pattern korrekt**: `r"/schritte/s[^/]+/vorgaenger"` mit `allowed_ops=["replace"]` folgt dem Muster von `nachfolger` (`template_schema.py:106-109`).

5. **Preservation-Check kompatibel**: `_addressed_items()` in `executor.py:188-204` extrahiert korrekt `("schritte", "s1")` aus `/schritte/s1/vorgaenger`.

6. **Keine Naming-Konflikte**: `vorgaenger` existiert nicht im aktuellen Codebase. Name folgt der deutschen Konvention und ist symmetrisch zu `nachfolger`.

7. **Completeness nicht betroffen**: `CompletenessCalculator` (`completeness.py:35-69`) berücksichtigt nur `completeness_status`, nicht Graph-Struktur.

8. **CR-002 Abhängigkeit korrekt**: CR-002 ist implementiert. `vorgaenger` ergänzt die Vorwärts-Referenzen komplementär — kein Widerspruch.

9. **Keine Konflikte mit anderen CRs**: Alle 10 bestehenden CRs geprüft. Keine Dateien- oder Logik-Konflikte. CR-012 kann unabhängig implementiert werden.

10. **SDD-Abweichung stichhaltig**: Die `reihenfolge`-Klarstellung ist eine Dokumentationskorrektur (Code behandelt es bereits als Anzeigereihenfolge). `vorgaenger` ist eine Erweiterung ohne SDD-Widerspruch.

## CR-Vollständigkeit

| Pflichtabschnitt | Status |
|---|---|
| Kopfzeile mit Priorität und Abhängigkeiten | ✅ Vorhanden |
| Problemstellung (Kernproblem, Defizite, Auswirkungen) | ✅ Vorhanden |
| Ziel der Änderung | ✅ Vorhanden |
| Lösung (Datenmodell, Beispiele, Prompts, Abwärtskompatibilität) | ✅ Vorhanden |
| SDD-Konsistenz | ✅ Vorhanden |
| ADR | ✅ Vorhanden (Bidirektionale Graphreferenzen) |
| Abhängigkeiten & Konflikte (3a) | ✅ Vorhanden und verifiziert |
| Änderungsplan mit Dateien | ✅ Vorhanden (10 Dateien) |
| Risiken und Mitigationen | ✅ Vorhanden (3 Risiken) |
| Nicht im Scope | ✅ Vorhanden |
| Abnahmekriterien | ✅ Vorhanden (8 Kriterien, prüfbar) |
| Aufwandsschätzung (S/M/L, Breaking Change) | ✅ Vorhanden |

## Lückenanalyse

1. **Fehlende Entscheidung: Code-Guardrail vs. LLM-Pflege**: CR-012 §8 empfiehlt den Code-Guardrail, aber §3 und §4 beschreiben die Lösung als ob das LLM `vorgaenger` pflegt. Die Implementierungsstrategie ist nicht eindeutig festgelegt. → Durch Bedingung 1 (oben) gelöst.

2. **Executor-Änderung unnötig**: Punkt 4 im Änderungsplan ("vorgaenger zu nicht-invalidierenden Feldern hinzufügen") ist nicht nötig — das Feld ist automatisch nicht-invalidierend. → Kann aus dem Änderungsplan entfernt werden.

3. **Fehlende Datei im Änderungsplan**: Wenn der Code-Guardrail umgesetzt wird, fehlt `backend/modes/structuring.py` im Änderungsplan (dort müsste `_derive_vorgaenger_from_nachfolger` implementiert werden).

4. **Test-Gaps**: Der CR nennt 3 Test-Dateien. Folgende Tests fehlen im Plan:
   - Referenzielle Integrität von `vorgaenger`-IDs (analog zu `test_nachfolger_ungueltig`)
   - Bidirektionale Konsistenzprüfung (nachfolger↔vorgaenger)
   - Template-Schema-Akzeptanz für vorgaenger-Patches
   - Step-Removal-Impact auf vorgaenger

5. **Prompt-Korrektur `reihenfolge` unnötig**: Die Prompts beschreiben `reihenfolge` bereits korrekt. Nur die SDD muss korrigiert werden.

## Detaillierte Findings pro Experte

### Datenmodell

- ✅ `vorgaenger: list[str] = Field(default_factory=list)` folgt etabliertem Pattern (models.py:152-165)
- ✅ Template-Schema-Pattern `r"/schritte/s[^/]+/vorgaenger"` mit `["replace"]` ist korrekt
- ✅ Pydantic v2 Serialisierung/Deserialisierung funktioniert mit Default `[]`
- ✅ Preservation-Check in Executor behandelt neuen Pfad korrekt
- ✅ Keine Naming-Konflikte, Typ `list[str]` konsistent mit `nachfolger`
- ✅ Executor braucht keine Änderung an `_INVALIDATING_FIELDS` — Feld ist automatisch nicht-invalidierend

### Orchestrator & Kontrollfluss

- ✅ `_INVALIDATING_FIELDS` (executor.py:38) enthält nicht `nachfolger`/`reihenfolge` — `vorgaenger` wird automatisch korrekt als nicht-invalidierend behandelt
- ✅ Completeness-Berechnung nicht betroffen (nur `completeness_status` zählt)
- ✅ Orchestrator-Zyklus ist robust — Completeness wird nach jedem Patch neu berechnet
- ⚠️ Guardrail `_derive_nachfolger_from_regeln` in `structuring.py:134-165` existiert als Pattern — sollte analog für `vorgaenger` adaptiert werden
- ✅ Template-Schema muss um vorgaenger-Pattern erweitert werden (sonst Executor-Rejection)
- ⚠️ `validation_checks.py:127-144` prüft nachfolger↔regeln — könnte optional um nachfolger↔vorgaenger erweitert werden

### Prompts & LLM-Verhalten

- ✅ `reihenfolge` ist bereits als "Anzeigereihenfolge" dokumentiert (init_structuring.md:243, structuring.md:195) — CR-Behauptung einer nötigen Korrektur ist falsch
- ⚠️ LLM-Pflege von `vorgaenger` ist hochriskant — bei jedem nachfolger-Patch müssten auch alle vorgaenger der Zielschritte aktualisiert werden
- ⚠️ Bestehende Graph-Konsistenz-Direktive (structuring.md:52) prüft bereits auf "mindestens einen Vorgänger" — funktioniert nur mit Feld `vorgaenger`
- ⚠️ First-Turn-Direktive (structuring.py:69-94) muss `vorgaenger`-Handling erklären
- ✅ Token-Overhead ~300-400 Tokens (mit Guardrail nur ~50 Tokens) — akzeptabel
- ⚠️ Patch-Beispiele in init_structuring.md (7 Beispiele) und structuring.md (3 Beispiele) müssten aktualisiert werden — entfällt bei Code-Guardrail

### Tests & Regression

- ⚠️ **~30+ Tests** haben Fixtures die `Strukturschritt` ohne `vorgaenger` erstellen — brechen NICHT dank Default `[]`, sollten aber aktualisiert werden
- ⚠️ **10 Test-Factories** (`_make_schritt()` in verschiedenen Dateien) müssen um `vorgaenger`-Parameter erweitert werden
- ⚠️ CR nennt 3 Test-Dateien, aber 4 zusätzliche Test-Gaps identifiziert (referenzielle Integrität, bidirektionale Konsistenz, Template-Akzeptanz, Step-Removal)
- ✅ Bestehende Tests bleiben grün dank Default `[]`
- ⚠️ Kein E2E-Test für `vorgaenger`-Generierung geplant

### SDD, ADRs & Architektur-Konformität

- ✅ CR-012 ADR (Bidirektionale Graphreferenzen) ist konsistent mit CR-002 ADR (Kontrollfluss-Felder)
- ✅ Keine Widersprüche zu bestehenden ADRs
- ✅ NFR-konform: Wartbarkeit (O(1) statt O(n)), Zuverlässigkeit (bidirektionale Invarianten), Beobachtbarkeit
- ✅ Designprinzipien nicht verletzt (externes Artefakt-Prinzip, Slot-basierte Schreibvorgänge)
- ⚠️ SDD-Update erforderlich: §5.4 (vorgaenger-Feld), §5.4 (reihenfolge-Semantik), §5.5 (neue Invariante)
- ⚠️ CR-003 ADR nicht referenziert (kein Konflikt, aber unvollständige Dokumentation)

### Abhängigkeiten & Konflikte

- ✅ Alle 10 bestehenden CRs geprüft — keine Konflikte
- ✅ CR-002 Abhängigkeit korrekt dokumentiert und erfüllt (Status: Implementiert)
- ✅ Dateien-Überlappungen mit CR-002/CR-004 sind additiv, nicht konfliktierend
- ✅ Abhängigkeitskette erfüllt: CR-002 ✅ → CR-012 kann implementiert werden
- ✅ Abwärtskompatibilität folgt etabliertem Pattern (Default `[]` wie CR-002)
- ⚠️ Potenzielle Synergien mit CR-006 (Init-Validator) und CR-008 (Phasenende-Validator) nicht dokumentiert — nicht blocking
