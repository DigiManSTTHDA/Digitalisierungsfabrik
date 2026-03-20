# CR-002: Kontrollfluss-Modellierung und kognitive Lastrebalancierung im Strukturartefakt

| Feld | Wert |
|---|---|
| **ID** | CR-002 |
| **Titel** | Kontrollfluss-Modellierung und kognitive Lastrebalancierung im Strukturartefakt |
| **Status** | Entwurf |
| **Erstellt** | 2026-03-20 |
| **Priorität** | Hoch |
| **Auslöser** | Analyse der kognitiven Lastverteilung zwischen Strukturierung und Spezifikation |
| **Ersetzt** | CR-001 (Entwurf, nicht reviewed) |

---

## 1. Problemstellung

### 1.1 Kernproblem

Das Datenmodell `Strukturschritt` (Datei: `backend/artifacts/models.py`, Zeilen 135–151) kann Kontrollflussstrukturen nicht explizit ausdrücken. Der Specifier (Phase 3) muss Schleifen-Scopes und Bedingung→Nachfolger-Mappings aus impliziten Hinweisen rekonstruieren — das erhöht die kognitive Last in der ohnehin schwersten Phase.

### 1.2 Konkrete Defizite

**A. Entscheidungen mit ≥3 Ausgängen (elif) sind mehrdeutig**

`Strukturschritt` hat EIN `bedingung`-Feld (`str | None`, Zeile 144) und eine `nachfolger`-Liste (`list[str]`, Zeile 143). Bei elif:

```json
{
  "schritt_id": "s5",
  "typ": "entscheidung",
  "bedingung": "Welcher Rechnungstyp?",
  "nachfolger": ["s6", "s7", "s8"]
}
```

**Welche Bedingung führt zu welchem Nachfolger?** Das Mapping ist nicht definiert. Das LLM in der Spezifikation muss in der `beschreibung` nachlesen und interpretieren. In EMMA's DECISION (Zeile 1619 im SDD) hat dagegen jede Regel explizit `{bedingung, nachfolger_id}` — die Lücke zwischen Struktur- und Algorithmusartefakt ist unnötig groß.

Das SDD bestätigt das Defizit: `bedingung` ist als einzelnes String-Feld definiert (SDD Zeile 702), und OP-16 markiert explizit, dass bedingte Kanten im Schema noch nicht modelliert sind (SDD Zeile 1627).

**B. Schleifen haben keinen Scope**

`typ: "schleife"` existiert als Schritttyp (Zeile 76 in models.py), aber es gibt kein Feld, das definiert, welche Schritte INNERHALB der Schleife liegen. Der einzige Weg, eine Schleife darzustellen, sind Rückkanten im `nachfolger`-Graphen:

```
s3 (schleife) → nachfolger: [s3a]
s3a (aktion)  → nachfolger: [s3b]
s3b (aktion)  → nachfolger: [s3]    ← implizite Rückkante = "Schleife"
s4 (aktion)                          ← nirgends definiert als "nach der Schleife"
```

Probleme:
- s3 hat keinen Nachfolger auf s4 — was kommt nach der Schleife?
- Kein Feld identifiziert s3a–s3b als Schleifenkörper.
- Keine Abbruchbedingung als strukturiertes Feld.
- Das SDD definiert keine schleifenspezifischen Felder auf Strukturschritt-Ebene (SDD Zeile 699) — Loop-Semantik wird komplett ans Algorithmusartefakt delegiert.

**C. Branch-Konvergenz ist unsichtbar**

Wenn Branches nach einer Entscheidung zusammenführen, sieht man das nur daran, dass mehrere Schritte zufällig denselben `nachfolger` haben. Es gibt kein explizites Konvergenz-Konzept. Das SDD bestätigt dies als offenes Problem (OP-16, Zeile 1627).

**D. Template-Schema Regex lehnt Prompt-Beispiele ab (Pre-Existing Bug)**

Das Template-Schema verwendet `r"/schritte/s\d+"` (template_schema.py, Zeile 81) — erlaubt nur rein numerische Suffixe wie `s1`, `s99`. Aber der structuring-Prompt zeigt Beispiele mit IDs wie `s2a`, `s_gutschrift`, `s6a` — diese werden vom Template **abgelehnt**. Das Algorithmus-Template verwendet dagegen korrekt `[^/]+` (Zeile 152).

### 1.3 Auswirkungen

- **Spezifikation überlastet**: Specifier rekonstruiert Kontrollfluss statt ihn abzulesen. Bei 19 EMMA-Typen + Parameter-Tabellen ist die kognitive Last am oberen Rand.
- **Fehlerquelle**: Implizite Konventionen (erster Nachfolger = true-Branch) werden vom LLM nicht zuverlässig eingehalten.
- **Validierung eingeschränkt**: Ohne expliziten Scope können Schleifen und Branches nicht programmatisch auf Konsistenz geprüft werden.
- **Prompt-Beispiele ungültig**: IDs wie `s2a` im Prompt werden vom Template-Schema zurückgewiesen — silent failure im Produktivbetrieb.

---

## 2. Ziel der Änderung

1. **Entscheidungen mit ≥2 Ausgängen** haben ein explizites Bedingung→Nachfolger-Mapping (`regeln`), das 1:1 auf EMMA DECISION abbildbar ist.
2. **Schleifen** haben einen expliziten Scope (`schleifenkoerper`) und eine Abbruchbedingung.
3. **Branch-Konvergenz** ist optional dokumentierbar (`konvergenz`).
4. **Template-Schema** akzeptiert alle Schritt-IDs, die mit `s` beginnen (inkl. `s2a`, `s_gutschrift`).
5. **Kognitive Last** verschiebt sich vom Specifier (Rekonstruktion) zum Strukturierer (Modellierung) — dahin, wo Kapazitätsreserve besteht.
6. **Zusätzlich**: Strukturierer bereitet Variablen-Hinweise und analoge Schritte vor (zwei kleine Best-Practice-Ergänzungen).

---

## 3. Lösung

### 3.1 Neues Modell: `Entscheidungsregel`

```python
class Entscheidungsregel(BaseModel):
    """Eine Regel innerhalb einer Entscheidung — Bedingung → Nachfolger (SDD OP-16 Teilumsetzung)."""
    bedingung: str          # Textuelle Bedingung, z.B. "Betrag > 5.000 €"
    nachfolger: str         # Schritt-ID des Ziel-Schritts
    bezeichnung: str = ""   # Optionaler Kurzname, z.B. "Freigabe nötig"
```

Platzierung: `backend/artifacts/models.py`, nach `Strukturschritttyp` (nach Zeile 77).

### 3.2 Neue Felder auf `Strukturschritt`

| Feld | Typ | Default | Nur bei | Beschreibung |
|---|---|---|---|---|
| `regeln` | `list[Entscheidungsregel]` | `[]` | `typ: "entscheidung"` | Geordnete Liste Bedingung→Nachfolger. Letzte Regel = Catch-All ("Sonst"). |
| `schleifenkoerper` | `list[str]` | `[]` | `typ: "schleife"` | Schritt-IDs, die INNERHALB der Schleife liegen. |
| `abbruchbedingung` | `str \| None` | `None` | `typ: "schleife"` | Textuelle Abbruchbedingung. |
| `konvergenz` | `str \| None` | `None` | `typ: "entscheidung"` | Schritt-ID des Merge-Points nach der Verzweigung. Optional. |

Platzierung: In `Strukturschritt` nach `ausnahme_beschreibung` (nach Zeile 145).

### 3.3 Abwärtskompatibilität

- Alle neuen Felder haben Defaults (`[]` oder `None`). Pydantic deserialisiert bestehende Artefakte fehlerfrei.
- `bedingung` bleibt erhalten als Fallback für einfache Ja/Nein-Entscheidungen. Bei Entscheidungen mit `regeln` wird `bedingung` ignoriert — `regeln` ist die primäre Quelle.
- `nachfolger` bleibt als flache Liste. Der Executor/Guardrail leitet `nachfolger` aus `regeln` ab, wenn `regeln` befüllt ist (Konsistenz-Enforcement).
- Kein Migrations-Skript nötig. Kein Breaking Change.

### 3.4 Beispiele

#### Entscheidung mit 3 Branches (elif)

```json
{
  "schritt_id": "s5",
  "titel": "Rechnungstyp bestimmen",
  "typ": "entscheidung",
  "beschreibung": "Frau Becker prüft den Rechnungsbetrag und entscheidet über das Vorgehen. Bei hohen Beträgen ist Abteilungsleiter Herr Schmidt zuständig.",
  "regeln": [
    {"bedingung": "Betrag > 5.000 €", "nachfolger": "s6", "bezeichnung": "Freigabe durch Abteilungsleiter"},
    {"bedingung": "Betrag > 1.000 €", "nachfolger": "s7", "bezeichnung": "Standardprüfung"},
    {"bedingung": "Sonst", "nachfolger": "s8", "bezeichnung": "Direktbuchung"}
  ],
  "nachfolger": ["s6", "s7", "s8"],
  "bedingung": null,
  "konvergenz": "s9",
  "reihenfolge": 5,
  "completeness_status": "vollstaendig",
  "algorithmus_status": "ausstehend"
}
```

#### Schleife mit explizitem Scope

```json
{
  "schritt_id": "s3",
  "titel": "Alle Rechnungspositionen verarbeiten",
  "typ": "schleife",
  "beschreibung": "Für jede Position in der Rechnung werden die Schritte s3a–s3c durchlaufen. Typisch 1–50 Positionen pro Rechnung.",
  "schleifenkoerper": ["s3a", "s3b", "s3c"],
  "abbruchbedingung": "Letzte Rechnungsposition erreicht (keine weitere Zeile vorhanden)",
  "nachfolger": ["s4"],
  "reihenfolge": 3,
  "completeness_status": "vollstaendig",
  "algorithmus_status": "ausstehend"
}
```

#### Einfache Ja/Nein-Entscheidung (Fallback mit `bedingung`)

```json
{
  "schritt_id": "s6",
  "titel": "Rechnung sachlich korrekt?",
  "typ": "entscheidung",
  "beschreibung": "Frau Becker prüft die Rechnung auf sachliche Richtigkeit.",
  "bedingung": "Ist die Rechnung sachlich korrekt?",
  "regeln": [],
  "nachfolger": ["s7", "s6a"],
  "konvergenz": null,
  "reihenfolge": 6,
  "completeness_status": "vollstaendig",
  "algorithmus_status": "ausstehend"
}
```

### 3.5 SDD-Konsistenz

Die SDD definiert `bedingung` als einzelnes String-Feld (Zeile 702) und hat keine Felder für Schleifen-Scope oder Multi-Branch-Mapping. Die neuen Felder **erweitern** das SDD, ohne bestehende Definitionen zu verletzen — `bedingung` und `nachfolger` bleiben erhalten. OP-16 (Zeile 1627) fordert explizit, dass bedingte Kanten im Schema geklärt werden müssen — dieser CR liefert eine Teilumsetzung.

### ADR: Erweiterte Kontrollfluss-Felder im Strukturartefakt

- **Kontext**: SDD 5.4 (Zeile 699) definiert `Strukturschritttyp.schleife` und `.entscheidung`, aber keine expliziten Felder für Schleifen-Scope, Multi-Branch-Mapping oder Konvergenz. OP-16 (Zeile 1627) markiert das Fehlen bedingter Kanten als offenes Problem.
- **Entscheidung**: Vier neue optionale Felder (`regeln`, `schleifenkoerper`, `abbruchbedingung`, `konvergenz`) auf `Strukturschritt`. Bestehende Felder (`bedingung`, `nachfolger`) bleiben als Fallback erhalten.
- **Begründung**: (1) Die Spezifikationsphase hat die höchste kognitive Last — explizitere Eingaben reduzieren Rekonstruktionsaufwand. (2) `regeln` spiegelt 1:1 die EMMA DECISION-Struktur — minimale Übersetzungslücke. (3) Alle Felder sind optional — keine Migration, kein Breaking Change.
- **Konsequenzen**: SDD 5.4 muss nach erfolgreicher Implementierung um die neuen Felder ergänzt werden. Die Invalidierungskaskade (SDD Zeile 817) muss um `regeln` und `schleifenkoerper` erweitert werden.

### 3.6 Prompt-Ergänzungen

**Strukturierer** (`backend/prompts/structuring.md`):
- Terminologie: `Entscheidungsregel`, `Schleifenkörper`, `Abbruchbedingung`, `Konvergenz` definieren.
- Best Practices: Regeln bei Entscheidungen mit ≥2 Ausgängen, Schleifenscope setzen, Konvergenz-Feld bei konvergierenden Branches.
- Patch-Beispiele: Entscheidung mit `regeln` (elif), Schleife mit `schleifenkoerper`.
- Referenz-Schema: Neue Felder in der Strukturschritt-Tabelle.
- Zusätzlich: Variablen-Hinweise vorbereiten ("Werte, die sich pro Durchlauf ändern, in der Beschreibung markieren"), analoge Schritte vormarkieren.

**Specifier** (`backend/prompts/specification.md`):
- Terminologie: Hinweis, dass Strukturschritte `regeln` und `schleifenkoerper` enthalten können.
- Arbeitsweise: "Wenn `regeln` vorhanden → direkt in EMMA DECISION-Regeln übersetzen. Wenn `schleifenkoerper` vorhanden → EMMA LOOP mit den referenzierten Abschnitten als Körper."

**Validierer** (`backend/prompts/validation.md`):
- Prüfregeln: `regeln`↔`nachfolger` Konsistenz, `schleifenkoerper`-Referenzen auf existierende Steps.

---

## 3a. Abhängigkeiten & Konflikte

Keine Konflikte mit bestehenden CRs. CR-001 (Status: Entwurf, nie reviewed) behandelt dasselbe Thema — wird durch diesen CR ersetzt und sollte auf Status "Überholt" gesetzt werden.

---

## 4. Änderungsplan

### Phase 1: Datenmodell

| # | Datei | Änderung |
|---|---|---|
| 1.1 | `backend/artifacts/models.py` | Neues Modell `Entscheidungsregel(BaseModel)` mit Feldern `bedingung: str`, `nachfolger: str`, `bezeichnung: str = ""` einfügen nach Zeile 77 |
| 1.2 | `backend/artifacts/models.py` | `Strukturschritt` um 4 Felder erweitern nach Zeile 145: `regeln: list[Entscheidungsregel] = Field(default_factory=list)`, `schleifenkoerper: list[str] = Field(default_factory=list)`, `abbruchbedingung: str \| None = None`, `konvergenz: str \| None = None` |
| 1.3 | `backend/artifacts/template_schema.py` | **Bugfix**: Alle `s\d+` Patterns (Zeilen 81, 86, 91, 96, 101, 106, 111, 116, 121, 126, 131, 136) auf `s[^/]+` ändern |
| 1.4 | `backend/artifacts/template_schema.py` | Neue Pfad-Patterns in `STRUCTURE_TEMPLATE` nach Zeile 138: `/schritte/s[^/]+/regeln` [replace], `/schritte/s[^/]+/schleifenkoerper` [replace], `/schritte/s[^/]+/abbruchbedingung` [add, replace], `/schritte/s[^/]+/konvergenz` [add, replace] |

### Phase 2: Invalidierung & Guardrails

| # | Datei | Änderung |
|---|---|---|
| 2.1 | `backend/core/executor.py` | `_INVALIDATING_FIELDS` (Zeile 38) erweitern: `{"beschreibung", "typ", "bedingung", "ausnahme_beschreibung", "regeln", "schleifenkoerper"}` hinzufügen |
| 2.2 | `backend/core/executor.py` | Prüfen ob `_collect_invalidated_ids()` (Zeile 236) mit den neuen Feldern korrekt funktioniert — die Regex `_SCHRITTE_PATH_RE` (Zeile 41) extrahiert bereits den Feldnamen, daher sollte die Erweiterung von `_INVALIDATING_FIELDS` ausreichen |
| 2.3 | `backend/modes/structuring.py` | Guardrail prüfen: Falls `regeln` befüllt ist, sollte `nachfolger` aus `regeln` abgeleitet werden (Konsistenz-Check). Empfehlung: als post-patch Guardrail im Mode, nicht im Executor |

### Phase 3: Prompts

| # | Datei | Änderung |
|---|---|---|
| 3.1 | `backend/prompts/structuring.md` | Terminologie-Tabelle: 4 neue Begriffe (`Entscheidungsregel`, `Schleifenkörper`, `Abbruchbedingung`, `Konvergenz`) |
| 3.2 | `backend/prompts/structuring.md` | Best Practices: Abschnitt "Entscheidungen mit Regeln modellieren" (~8 Zeilen), "Schleifen mit Scope modellieren" (~6 Zeilen), "Variablen-Hinweise vorbereiten" (~4 Zeilen), "Analoge Schritte vormarkieren" (~3 Zeilen) |
| 3.3 | `backend/prompts/structuring.md` | Patch-Beispiele: "Entscheidung mit `regeln` (elif)" und "Schleife mit `schleifenkoerper`" — realistische JSON-Beispiele wie in Abschnitt 3.4 oben |
| 3.4 | `backend/prompts/structuring.md` | Referenz Strukturschritt-Schema: 4 neue Zeilen in der Feldtabelle |
| 3.5 | `backend/prompts/specification.md` | Terminologie: 1 Absatz (~4 Zeilen) über `regeln` und `schleifenkoerper` als Eingabe aus dem Strukturartefakt |
| 3.6 | `backend/prompts/specification.md` | Arbeitsweise: 2 Sätze zur Übersetzung `regeln`→EMMA DECISION, `schleifenkoerper`→EMMA LOOP |
| 3.7 | `backend/prompts/validation.md` | Prüfregeln: 2 neue Regeln (~4 Zeilen): `regeln`↔`nachfolger` Konsistenz, `schleifenkoerper`-Referenzen existieren |

### Phase 4: Context Assembler

| # | Datei | Änderung |
|---|---|---|
| 4.1 | `backend/modes/structuring.py` | `_build_slot_status()` anpassen: Bei `typ: "entscheidung"` `regeln`-Anzahl anzeigen, bei `typ: "schleife"` `schleifenkoerper` auflisten |
| 4.2 | `backend/modes/specification.py` | `_build_structure_content()` anpassen: `regeln` und `schleifenkoerper` in der Read-Only-Darstellung des Strukturartefakts anzeigen |

### Phase 5: Tests

| # | Datei | Änderung |
|---|---|---|
| 5.1 | `backend/tests/test_artifact_models.py` | Tests für `Entscheidungsregel` Modell, `Strukturschritt` mit neuen Feldern, Roundtrip-Serialisierung |
| 5.2 | `backend/tests/test_executor.py` | `TestStructureTemplateKeyFormat` (Zeile 82): Tests für IDs `s2a`, `s_gutschrift` (müssen akzeptiert werden) |
| 5.3 | `backend/tests/test_executor.py` | `TestInvalidationTriggered`: Tests für `regeln`- und `schleifenkoerper`-Änderungen (müssen Invalidierung auslösen) |
| 5.4 | `backend/tests/test_executor.py` | Neue Patch-Tests: `replace` auf `/schritte/s1/regeln`, `replace` auf `/schritte/s1/schleifenkoerper`, `add` auf `/schritte/s1/abbruchbedingung`, `add` auf `/schritte/s1/konvergenz` |
| 5.5 | `backend/tests/test_structuring_mode.py` | Test: Entscheidung mit `regeln` wird korrekt im Slot-Status dargestellt |
| 5.6 | `backend/tests/test_validation_deterministic.py` | Test: `regeln`↔`nachfolger` Inkonsistenz wird als Befund erkannt |

---

## 5. Risiken und Mitigationen

### 5.1 LLM setzt `regeln` und `nachfolger` inkonsistent

**Risiko**: Das LLM schreibt `regeln` mit Nachfolger-IDs, die nicht in `nachfolger` stehen.
**Mitigation**: Post-Patch-Guardrail im Structuring-Mode: Wenn `regeln` befüllt, leite `nachfolger` daraus ab. Alternativ: Konsistenzprüfung in der deterministischen Validierung. `regeln` ist die Quelle der Wahrheit.

### 5.2 LLM ignoriert neue Felder und nutzt weiterhin nur `bedingung`

**Risiko**: Trotz Prompt-Änderungen nutzt das LLM die alten Felder.
**Mitigation**: (1) Prompt-Beispiele zeigen `regeln` für alle Entscheidungen mit ≥2 Ausgängen. (2) First-Turn-Directive nutzt `regeln` in den Sofort-Patches. (3) `bedingung` bleibt als Fallback valide — kein Fehler, nur weniger Information für den Specifier.

### 5.3 `schleifenkoerper`-Referenzen auf nicht existierende Steps

**Risiko**: `schleifenkoerper: ["s3a"]` referenziert einen Step, der noch nicht existiert.
**Mitigation**: (1) Deterministischer Validierungscheck: Alle IDs in `schleifenkoerper` müssen in `schritte` existieren. (2) First-Turn legt alle Steps inklusive Schleifenkörper-Steps in einem Patch-Set an.

### 5.4 Template-Regex-Erweiterung zu permissiv

**Risiko**: `s[^/]+` erlaubt unbeabsichtigte Muster wie `s--` oder `s.`.
**Mitigation**: (1) Das Muster ist immer noch restriktiv (muss mit `s` beginnen, kein Slash). (2) Der Executor greift nur auf Dict-Keys zu — kein Injection-Risiko. (3) Die Lockerung ist beabsichtigt, weil der Prompt IDs wie `s2a` und `s_gutschrift` als Beispiele zeigt.

### 5.5 Erhöhte Prompt-Länge

**Risiko**: Neue Terminologie, Beispiele und Felder erhöhen den Strukturierer-Prompt.
**Mitigation**: Geschätzte Erhöhung: ~60–80 Zeilen (von 271 auf ~340). Der Specifier-Prompt hat 396 Zeilen und funktioniert. Der Strukturierer hat Kapazitätsreserve.

### 5.6 Executor-Handling von `regeln` als Liste von Objekten

**Risiko**: Der Executor nutzt `jsonpatch.apply_patch()` (executor.py, Zeile 125) und `model_validate()` (Zeile 130). Wenn das LLM `regeln` als `replace` patcht, muss der Wert eine gültige Liste von Dicts sein, die Pydantic als `list[Entscheidungsregel]` parsen kann.
**Mitigation**: (1) Pydantic's `model_validate()` parsed automatisch Dict→BaseModel. (2) Die `EmmaAktion.parameter` nutzt bereits ein Dict-Feld mit Validator (`_coerce_parameter_values_to_str`, Zeile 185) — das Pattern ist etabliert. (3) Patch-Beispiele im Prompt zeigen das korrekte Format.

---

## 6. Nicht im Scope

- **Hierarchische Step-Verschachtelung** (Steps als Kinder anderer Steps) — zu großer Architektur-Umbau. Flache Liste mit Scope-Feldern reicht.
- **Specification-Phase splitten** — Analyse ergab, dass Rebalancing + besseres Strukturartefakt ausreicht.
- **Frontend-Anpassungen** — Falls das Frontend den Strukturgraphen visualisiert, braucht es die neuen Felder. Separater CR.
- **SDD-Update** — Wird nach erfolgreicher Implementierung als separater Schritt gemacht (siehe ADR).
- **`nachfolger`-Ableitung automatisieren** — Konsistenz-Enforcement als Guardrail, aber kein automatisches Überschreiben von `nachfolger` durch den Executor.

---

## 7. Abnahmekriterien

1. `Entscheidungsregel` existiert als Pydantic-Modell mit `bedingung: str`, `nachfolger: str`, `bezeichnung: str = ""`.
2. `Strukturschritt` hat die Felder `regeln`, `schleifenkoerper`, `abbruchbedingung`, `konvergenz` — alle optional mit korrekten Defaults.
3. Bestehende Artefakte (ohne neue Felder) werden fehlerfrei deserialisiert (Roundtrip-Test).
4. Template-Schema akzeptiert Patches auf `/schritte/s1/regeln`, `/schritte/s1/schleifenkoerper`, `/schritte/s1/abbruchbedingung`, `/schritte/s1/konvergenz`.
5. Template-Schema akzeptiert Schritt-IDs `s2a`, `s_gutschrift` (Bugfix).
6. Änderungen an `regeln` und `schleifenkoerper` lösen Invalidierungskaskade aus (Executor `_INVALIDATING_FIELDS`).
7. Strukturierer-Prompt enthält Terminologie, Patch-Beispiele und Best Practices für alle neuen Felder.
8. Specifier-Prompt beschreibt die Übersetzung `regeln`→DECISION und `schleifenkoerper`→LOOP.
9. Validierer-Prompt prüft `regeln`↔`nachfolger` Konsistenz und `schleifenkoerper`-Referenzen.
10. Alle bestehenden Tests laufen weiterhin grün (keine Regression).
11. Neue Tests existieren für: Modell-Validierung, Patch-Pfade, Invalidierung, Slot-Status-Darstellung.

---

## 8. Aufwandsschätzung

- **Komplexität**: **M** (10–12 Dateien, kein Breaking Change, aber Querschnitt-Änderung über Modell + Executor + 3 Prompts + 2 Modes + Tests)
- **Betroffene Dateien**: 12
- **Breaking Change**: Nein (alle neuen Felder optional mit Defaults)

| Phase | Dateien | Komplexität |
|---|---|---|
| 1: Datenmodell | `models.py`, `template_schema.py` | S |
| 2: Invalidierung | `executor.py`, `structuring.py` (Guardrail) | S |
| 3: Prompts | `structuring.md`, `specification.md`, `validation.md` | M |
| 4: Context Assembler | `structuring.py`, `specification.py` | S |
| 5: Tests | `test_artifact_models.py`, `test_executor.py`, `test_structuring_mode.py`, `test_validation_deterministic.py` | M |
