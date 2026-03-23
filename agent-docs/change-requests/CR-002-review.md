# CCB Review: CR-002 — Kontrollfluss-Modellierung und kognitive Lastrebalancierung im Strukturartefakt

| Feld | Wert |
|---|---|
| **CR** | CR-002 |
| **Review-Datum** | 2026-03-23 |
| **Review-Nr.** | 1 |
| **Empfehlung** | APPROVE WITH CONDITIONS |

## Zusammenfassung

CR-002 wurde durch sechs unabhängige Fachexperten geprüft (Datenmodell, Orchestrator/Kontrollfluss, Prompts/LLM-Verhalten, Tests/Regression, SDD/ADR-Konformität, Abhängigkeiten/Konflikte). Der CR ist architektonisch solide, SDD-konform (Teilumsetzung von OP-16), und das Datenmodell ist abwärtskompatibel. Es wurden keine harten Blocker identifiziert, aber fünf Verbesserungen, die vor oder während der Implementierung adressiert werden sollten.

## Empfehlung

**APPROVE WITH CONDITIONS**

Der CR ist konzeptionell ausgereift, vollständig dokumentiert und architektonisch konform. Die identifizierten Verbesserungen betreffen primär Lücken im Änderungsplan (eine fehlende Datei, eine unterspecifizierte Guardrail-Strategie) und können während der Implementierung adressiert werden, ohne den CR grundlegend zu überarbeiten.

### Bedingungen für die Implementierung

1. **`patch_summarizer.py` in den Änderungsplan aufnehmen** — Die Datei `backend/core/patch_summarizer.py` (Zeilen 48–62) enthält feldspezifische Übersetzungen für `nachfolger`, `bedingung`, `typ`. Die vier neuen Felder (`regeln`, `schleifenkoerper`, `abbruchbedingung`, `konvergenz`) fehlen — ohne Erweiterung wird die Nutzerbestätigung bei Patches auf diese Felder zu einem generischen "Änderungen vorgenommen" degradiert.

2. **Guardrail-Strategie in Phase 2.3 präzisieren** — Der CR beschreibt einen "post-patch Guardrail" für `regeln`↔`nachfolger`-Konsistenz, lässt aber offen, ob dieser (a) `nachfolger` automatisch überschreibt, (b) einen Fehler auslöst, oder (c) nur warnt. Empfehlung: **Automatisches Ableiten** von `nachfolger` aus `regeln` (wenn befüllt) — das ist konsistent mit der CR-Aussage "`regeln` ist die Quelle der Wahrheit".

3. **`nachfolger`-Fallback-Case dokumentieren** — Wenn `regeln` leer ist (einfache Ja/Nein-Entscheidung), können Änderungen an `nachfolger` keine Invalidierung auslösen, da `nachfolger` nicht in `_INVALIDATING_FIELDS` steht. Der CR sollte explizit dokumentieren, warum das akzeptabel ist (z.B.: "Bei einfachen Entscheidungen definiert `bedingung` die Semantik — `nachfolger`-Reihenfolge allein ändert nicht die Algorithmus-Logik"), oder `nachfolger` ebenfalls zu `_INVALIDATING_FIELDS` hinzufügen.

## Blocker (müssen behoben werden)

Keine Blocker identifiziert.

## Verbesserungsvorschläge (sollten eingearbeitet werden)

1. **`patch_summarizer.py` fehlt im Änderungsplan** — Phase 4 (Context Assembler) sollte um `backend/core/patch_summarizer.py` erweitert werden. Vier neue `elif`-Zweige für `regeln`, `schleifenkoerper`, `abbruchbedingung`, `konvergenz` sind nötig (Aufwand: ~8 Zeilen). *[Quelle: Orchestrator-Experte, Finding #7]*

2. **Guardrail-Implementierungsstrategie präzisieren** — Phase 2.3 sagt "Empfehlung: als post-patch Guardrail im Mode", spezifiziert aber nicht das Verhalten. Vorschlag: `_apply_guardrails()` in `structuring.py` erweitern — wenn `schritt.regeln` nicht leer, setze `schritt.nachfolger = [r.nachfolger for r in schritt.regeln]` via zusätzlichem Patch. *[Quelle: Orchestrator-Experte, Finding #4; Abhängigkeits-Experte, Finding #8]*

3. **`nachfolger`-Invalidierung im Fallback-Case klären** — `nachfolger` ist heute nicht in `_INVALIDATING_FIELDS`. Bei einfachen Entscheidungen (nur `bedingung`, kein `regeln`) löst eine Nachfolger-Änderung keine Invalidierung aus. Entweder dokumentiert begründen oder `nachfolger` aufnehmen. *[Quelle: Orchestrator-Experte, Finding #3]*

4. **First-Turn-Direktive in `specification.py` erweitern** — `_build_first_turn_directive()` (Zeile 94–127) listet wartende Strukturschritte ohne Hinweis auf `regeln` oder `schleifenkoerper`. Wenn ein Schritt bereits `regeln` enthält, sollte die First-Turn-Direktive dies erwähnen, damit der Specifier die Regeln direkt in EMMA DECISION übersetzen kann. *[Quelle: Prompt-Experte, Finding #7.1]*

5. **Semantik `abbruchbedingung` vs. EMMA LOOP `maximale_anzahl_loops` abgrenzen** — Der Specifier-Prompt beschreibt LOOP mit `maximale_anzahl_loops` und optionaler DECISION als Abbruchbedingung. Das neue Feld `abbruchbedingung` auf Strukturebene ist textuell. Der CR sollte kurz klären, wie der Specifier beides zusammenführt (z.B.: "abbruchbedingung → textueller Hinweis für den Specifier, wird in LOOP-Parameter oder innere DECISION übersetzt"). *[Quelle: Prompt-Experte, Finding #5.2]*

## Hinweise

1. **ADR-006-Konflikt ist ein False Positive** — Der Abhängigkeits-Experte meldete einen Konflikt mit ADR-006 (`EmmaAktion.parameter` als `dict[str, str]`). Nach Prüfung: CR-002's `regeln` liegt auf `Strukturschritt` (Strukturartefakt-Ebene), ADR-006 betrifft `EmmaAktion.parameter` (Algorithmusartefakt-Ebene). Das sind verschiedene Architekturebenen — kein Konflikt. Die `regeln` in `validation.md` Zeile 264 ("DECISION: `verzweigungstyp`, `regeln`") bezieht sich auf EMMA-Parameter-Keys im `dict[str, str]`, nicht auf das neue `Entscheidungsregel`-Modell.

2. **Token-Erhöhung moderat** — Strukturierer-Prompt wächst von ~270 auf ~323 Zeilen (+19%, ~795 Tokens). Der Specifier-Prompt ist mit 395 Zeilen bereits größer und funktioniert zuverlässig. Kein Risiko.

3. **Completeness-Berechnung nicht betroffen** — `completeness.py` zählt Slots auf Top-Level-Ebene (Schritte, Abschnitte). Die neuen Felder sind Sub-Slot-Attribute und beeinflussen die Completeness-Berechnung nicht.

4. **Bugfix Template-Regex ist berechtigt** — Der Pre-Existing Bug (`s\d+` statt `s[^/]+`) in `template_schema.py` ist real: Der Prompt zeigt Beispiele mit `s2a`, `s_gutschrift`, die vom Template aktuell stumm abgelehnt werden. Die Integration in diesen CR ist sinnvoll, da die neuen Pfad-Patterns ohnehin `s[^/]+` verwenden.

5. **Tests werden nicht brechen** — Alle neuen Felder haben optionale Defaults. Bestehende Fixtures und Factories erzeugen Strukturschritte ohne die neuen Felder — Pydantic füllt automatisch `regeln=[]`, `schleifenkoerper=[]`, `abbruchbedingung=None`, `konvergenz=None`.

## Bestätigungen (CR-Behauptungen, die verifiziert wurden)

1. **SDD-Konformität bestätigt** — Die neuen Felder erweitern SDD 5.4 ohne bestehende Definitionen zu verletzen. OP-16 (Zeile 1627) fordert explizit die Klärung bedingter Kanten — CR-002 liefert eine Teilumsetzung. *[SDD-Experte]*

2. **ADR stichhaltig begründet** — Alle drei Begründungspunkte (kognitive Lastreduktion, 1:1 EMMA-DECISION-Abbildung, keine Migration) sind im SDD evidenzbasiert. *[SDD-Experte]*

3. **Pydantic-Abwärtskompatibilität funktioniert** — `Field(default_factory=list)` und `None`-Defaults garantieren fehlerfreie Deserialisierung bestehender Artefakte. Pattern ist etabliert (vgl. `EmmaAktion.parameter`). *[Datenmodell-Experte]*

4. **Executor-Regex ist robust** — `_SCHRITTE_PATH_RE` (executor.py:41) nutzt bereits `[^/]+` und extrahiert Feldnamen korrekt für alle neuen Felder. Keine Executor-Änderung nötig außer `_INVALIDATING_FIELDS`. *[Datenmodell-Experte]*

5. **CR-001-Ablösung korrekt** — CR-001 (Entwurf, nie reviewed) behandelt dasselbe Thema. CR-002 ist substantiell detaillierter (erweiterte Risikoanalyse, ADR, Guardrail-Details). Die Ablösung ist berechtigt. *[Abhängigkeits-Experte]*

6. **Template-Schema-Bugfix notwendig** — Regex `s\d+` auf 16 Zeilen in `template_schema.py` lehnt Prompt-Beispiele wie `s2a` ab. Das Algorithmus-Template nutzt bereits korrekt `[^/]+`. Inkonsistenz bestätigt. *[Datenmodell-Experte, Orchestrator-Experte]*

7. **Keine Breaking Changes** — Alle neuen Felder optional, alle Tests laufen weiterhin grün, kein Migrations-Skript nötig. *[Test-Experte, Datenmodell-Experte]*

## CR-Vollständigkeit

| Pflichtabschnitt | Status |
|---|---|
| Kopfzeile mit Priorität und Abhängigkeiten | ✅ Vorhanden (Hoch, Ersetzt CR-001) |
| Problemstellung mit Kernproblem, Defiziten, Auswirkungen | ✅ Vorhanden (4 Defizite, 4 Auswirkungen) |
| Ziel der Änderung | ✅ Vorhanden (6 Ziele) |
| Lösung mit Datenmodell, Beispielen, Prompt-Änderungen | ✅ Vorhanden (3.1–3.6) |
| Abwärtskompatibilität | ✅ Vorhanden (3.3) |
| SDD-Konsistenz | ✅ Vorhanden (3.5) |
| ADR (bei SDD-Abweichung) | ✅ Vorhanden (ADR mit Kontext, Entscheidung, Begründung, Konsequenzen) |
| Abhängigkeiten & Konflikte (3a) | ✅ Vorhanden (CR-001 Ablösung) |
| Änderungsplan mit präzisen Zeilen | ✅ Vorhanden (5 Phasen, 19 Einzeländerungen) |
| Risiken und Mitigationen | ✅ Vorhanden (6 Risiken mit Mitigationen) |
| Nicht im Scope | ✅ Vorhanden (5 Abgrenzungen) |
| Abnahmekriterien (prüfbar) | ✅ Vorhanden (11 Kriterien) |
| Aufwandsschätzung mit Komplexität | ✅ Vorhanden (M, 12 Dateien, kein Breaking Change) |

## Lückenanalyse

### Fehlende Dateien im Änderungsplan

- **`backend/core/patch_summarizer.py`** — Enthält feldspezifische Übersetzungen (Zeilen 48–62), die für die neuen Felder erweitert werden müssen. Ohne Anpassung degradiert die Nutzerbestätigung zu generischem Text.

### Fehlende Risiken

- **Nachfolger-Invalidierung im Fallback-Case** — Wenn eine einfache Entscheidung (nur `bedingung`, kein `regeln`) ihren `nachfolger` ändert, wird keine Invalidierung ausgelöst. Das ist eine potenzielle Inkonsistenzquelle, die im CR nicht als Risiko genannt wird.

### Fehlende Präzision

- **Guardrail-Implementierungsstrategie** — Phase 2.3 lässt offen, ob Override, Validierung oder Warnung. Die Implementierung könnte dadurch in eine falsche Richtung laufen.
- **First-Turn-Direktive Specification** — Nicht im Änderungsplan explizit als eigene Änderung aufgeführt, obwohl `_build_first_turn_directive()` in `specification.py` angepasst werden muss.

### Fehlende Abnahmekriterien

- Kein Kriterium für `patch_summarizer.py` (da nicht im Änderungsplan).
- Kein Kriterium für die Guardrail-Konsistenzprüfung als solche (nur indirekt über Abnahmekriterium 9: "Validierer-Prompt prüft `regeln`↔`nachfolger` Konsistenz").

## Detaillierte Findings pro Experte

### Datenmodell

1. **✅ Entscheidungsregel-Modell kompatibel** — Standard-Pydantic-BaseModel, kein Naming-Konflikt, etabliertes Pattern (vgl. EmmaAktion). *[models.py nach Zeile 77]*
2. **✅ Strukturschritt-Felder kompatibel** — Alle Defaults korrekt, Typ-Konsistenz mit bestehenden Feldern (z.B. `schleifenkoerper: list[str]` analog zu `nachfolger: list[str]`). *[models.py nach Zeile 145]*
3. **✅ Template-Regex-Vorschlag korrekt** — `s[^/]+` ist passend, harmonisiert mit ALGORITHM_TEMPLATE. 16 Zeilen betroffen. *[template_schema.py:81–136]*
4. **✅ Neue Pfad-Patterns korrekt** — Allowed-Ops (`replace` für Listen, `add+replace` für optionale Skalare) sind konsistent mit bestehendem Schema. *[template_schema.py nach Zeile 138]*
5. **✅ Executor unterstützt verschachtelte Objekte** — `jsonpatch.apply_patch()` + `model_validate()` handelt `list[dict]` → `list[Entscheidungsregel]` korrekt. *[executor.py:125–137]*
6. **✅ Pydantic-Fehlerbehandlung robust** — Ungültige `regeln`-Formate werden durch `except Exception → _fail()` abgefangen. *[executor.py:138–141]*

### Orchestrator & Kontrollfluss

1. **✅ Invalidierungskaskade korrekt beschrieben** — `_collect_invalidated_ids()` funktioniert wie im CR beschrieben. Erweiterung von `_INVALIDATING_FIELDS` reicht aus. *[executor.py:236–273]*
2. **⚠️ `nachfolger` nicht in `_INVALIDATING_FIELDS`** — Fallback-Case (einfache Entscheidung ohne `regeln`) kann Nachfolger ändern ohne Invalidierung. *[executor.py:38]*
3. **⚠️ Guardrail für `regeln`↔`nachfolger` fehlt** — `_apply_guardrails()` in structuring.py muss erweitert werden. *[structuring.py:91–125]*
4. **⚠️ `patch_summarizer.py` nicht im CR-Plan** — Neue Felder erzeugen generische Bestätigungstexte. *[patch_summarizer.py:48–62]*
5. **✅ Completeness-Berechnung nicht betroffen** — Calculator arbeitet auf Slot-Ebene, nicht auf Feld-Ebene. *[completeness.py:35–69]*
6. **⚠️ Deterministische Validierungschecks fehlen im Code** — `validation_checks.py:21–127` prüft 5 Bereiche, aber nicht `regeln`- oder `schleifenkoerper`-Konsistenz. CR Phase 3.7 plant das korrekt. *[validation_checks.py]*

### Prompts & LLM-Verhalten

1. **✅ Terminologie-Ansatz konsistent** — Bestehende Tabellen in allen Prompts folgen demselben Pattern. 4 neue Begriffe passen. *[structuring.md:19–28]*
2. **✅ Patch-Beispiele im CR korrekt** — RFC 6902 konform, korrekte Pfade, realistische Werte für Entscheidung mit elif und Schleife mit Scope. *[CR Abschnitt 3.4]*
3. **✅ Token-Erhöhung akzeptabel** — ~795 Tokens (+19%) auf structuring.md. Specifier-Prompt ist mit ~5.925 Tokens bereits größer. *[Prompt-Analyse]*
4. **⚠️ First-Turn-Direktive Specification ignoriert neue Felder** — `_build_first_turn_directive()` in specification.py muss `regeln`/`schleifenkoerper` erwähnen. *[specification.py:94–127]*
5. **⚠️ Semantik `abbruchbedingung` vs. EMMA LOOP nicht abgegrenzt** — Textuell auf Strukturebene vs. `maximale_anzahl_loops` Parameter auf Algorithmusebene. *[specification.md:86]*
6. **✅ Abwärtskompatibilität in Prompts gewährleistet** — Alte Artefakte ohne neue Felder werden mit Defaults geladen. `regeln: []` = Fallback auf `bedingung`+`nachfolger`.

### Tests & Regression

1. **✅ Keine brechenden Tests** — Alle neuen Felder haben optionale Defaults. Bestehende Fixtures funktionieren weiterhin. *[Alle test_*.py]*
2. **✅ CR referenziert korrekte Testdateien** — `test_artifact_models.py`, `test_executor.py`, `test_structuring_mode.py`, `test_validation_deterministic.py` existieren und sind relevant.
3. **⚠️ Signifikante Test-Gaps** — Folgende Tests fehlen und müssen während der Implementierung geschrieben werden:
   - Template-Schema: `s2a`, `s_gutschrift` akzeptieren (test_executor.py)
   - Template-Schema: Neue Pfad-Patterns `regeln`, `schleifenkoerper`, `abbruchbedingung`, `konvergenz` (test_executor.py)
   - Modelle: `Entscheidungsregel` Instantiation + Roundtrip (test_artifact_models.py)
   - Modelle: `Strukturschritt` mit neuen Feldern Roundtrip (test_artifact_models.py)
   - Invalidierung: `regeln`- und `schleifenkoerper`-Änderungen (test_executor.py)
   - Darstellung: Slot-Status und Structure-Content für neue Felder (test_structuring_mode.py, test_specification_mode.py)
   - Validierung: `regeln`↔`nachfolger` Konsistenz, `schleifenkoerper`-Referenzen (test_validation_deterministic.py)
4. **ℹ️ CR-Phase 5 plant alle notwendigen Tests** — Die genannten Tests sind im CR vorgesehen (Zeilen 251–260), müssen aber während der Implementierung geschrieben werden.

### SDD, ADRs & Architektur-Konformität

1. **✅ Kein Widerspruch zum SDD** — Neue Felder erweitern SDD 5.4, ohne bestehende Definitionen zu verletzen. `bedingung` und `nachfolger` bleiben erhalten. *[SDD Zeile 699]*
2. **✅ OP-16 Teilumsetzung** — SDD 8.3 (Zeile 1627) fordert Klärung bedingter Kanten. CR-002 liefert genau das. *[SDD Zeile 1627]*
3. **✅ Architektonische Prinzipien eingehalten** — LLM-Schreibzugriffe bleiben über Executor/Template-Schema reguliert. Deterministische Orchestrierung nicht beeinträchtigt. Artefakte bleiben Single Source of Truth. *[SDD 5.1, 5.7, 6.3]*
4. **✅ ADR-Begründung stichhaltig** — Drei Punkte (kognitive Last, EMMA-Abbildung, kein Breaking Change) sind SDD-evidenzbasiert.
5. **✅ SDD-Update korrekt als Konsequenz identifiziert** — Abschnitt 5.4 (Feldtabelle) und 5.5 (Invalidierungsregel) müssen nach Implementierung ergänzt werden. *[CR ADR, Zeile 185–186]*
6. **✅ Keine Verletzung bestehender ADRs** — Einziger relevanter ADR ist ADR-006 (EMMA Parameter Schema). Kein Konflikt, da verschiedene Architekturebenen (Strukturartefakt vs. Algorithmusartefakt).

### Abhängigkeiten & Konflikte

1. **✅ CR-001-Ablösung korrekt** — CR-001 (Entwurf, nie reviewed) behandelt dasselbe Thema. CR-002 ist substantiell detaillierter und ersetzt ihn vollständig. CR-001 sollte auf "Überholt" gesetzt werden.
2. **✅ Keine Konflikte mit anderen CRs** — Es existieren nur CR-001 und CR-002. Keine weiteren aktiven CRs im Verzeichnis.
3. **❌ ADR-006-Konflikt ist ein False Positive** — Der Abhängigkeits-Experte meldete einen Konflikt zwischen CR-002's `Entscheidungsregel` und ADR-006's `EmmaAktion.parameter: dict[str, str]`. Nach Prüfung: Dies sind verschiedene Architekturebenen. `Strukturschritt.regeln` (Strukturartefakt) wird vom Specifier in `EmmaAktion.parameter["regeln"]` (Algorithmusartefakt) übersetzt — das ist keine Verletzung von ADR-006, sondern genau der beabsichtigte Datenfluss.
4. **⚠️ `validation.md` erwähnt bereits `regeln` als DECISION-Parameter** — Zeile 264 listet `verzweigungstyp`, `regeln` als EMMA DECISION-Parameter. Das bezieht sich auf die Parameter-Keys im `dict[str, str]`, nicht auf das neue `Entscheidungsregel`-Modell. Keine Inkonsistenz.
