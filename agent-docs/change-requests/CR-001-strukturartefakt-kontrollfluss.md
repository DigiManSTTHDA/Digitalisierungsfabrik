# CR-001: Kontrollfluss-Modellierung im Strukturartefakt

| Feld | Wert |
|---|---|
| **ID** | CR-001 |
| **Titel** | Explizite Kontrollfluss-Modellierung für Schleifen und Entscheidungen im Strukturartefakt |
| **Status** | Überholt |
| **Ersetzt durch** | CR-002 |
| **Erstellt** | 2026-03-20 |
| **Priorität** | Hoch |
| **Auslöser** | Analyse der kognitiven Lastverteilung zwischen Strukturierung und Spezifikation |

---

## 1. Problemstellung

### 1.1 Kernproblem

Das aktuelle Datenmodell für `Strukturschritt` kann Kontrollflussstrukturen (Schleifen, Mehrfach-Entscheidungen, Branch-Konvergenz) nicht explizit ausdrücken. Das LLM in der Spezifikationsphase muss diese Strukturen aus impliziten Hinweisen (Nachfolger-Rückkanten, Beschreibungstexte) rekonstruieren. Das erhöht die kognitive Last in der ohnehin schwersten Phase.

### 1.2 Drei konkrete Defizite

**A. Schleifen haben keinen Scope**

`typ: "schleife"` existiert als Schritttyp, aber es gibt kein Feld, das definiert, welche Schritte INNERHALB der Schleife liegen. Der einzige Weg, eine Schleife darzustellen, ist eine Rückkante im `nachfolger`-Graphen — fragil, implizit, und vom LLM schwer zu interpretieren.

Beispiel — aktuell:
```
s3 (schleife) → nachfolger: [s3a]
s3a (aktion)  → nachfolger: [s3b]
s3b (aktion)  → nachfolger: [s3c]
s3c (aktion)  → nachfolger: [s3]    ← implizite Rückkante
s4 (aktion)                          ← wo steht, dass s4 NACH der Schleife kommt?
```

Problem: Die Rückkante s3c → s3 sagt "Schleife", aber:
- Es gibt kein Feld, das s3a–s3c als Schleifenkörper identifiziert.
- s3 selbst hat keinen Nachfolger auf s4 — der Specifier muss raten, was nach der Schleife kommt.
- Es gibt keine Abbruchbedingung als strukturiertes Feld.

**B. Entscheidungen haben kein Bedingung→Nachfolger-Mapping**

`Strukturschritt` hat EIN `bedingung`-Feld (String) und eine `nachfolger`-Liste. Für einfaches if/else reicht die Convention (erster Nachfolger = true, zweiter = false). Aber bei elif (≥3 Ausgänge):

```json
{
  "schritt_id": "s5",
  "typ": "entscheidung",
  "bedingung": "Welcher Rechnungstyp?",
  "nachfolger": ["s6", "s7", "s8"]
}
```

Welche Bedingung führt zu welchem Nachfolger? **Mehrdeutig.** Das LLM muss in der `beschreibung` nachlesen und interpretieren. In EMMA's DECISION ist das gelöst — jede Regel hat explizit `{bedingung, nachfolger_id}`. Im Strukturartefakt fehlt dieses Mapping.

**C. Branch-Konvergenz ist unsichtbar**

Wenn zwei Branches nach einer Entscheidung wieder zusammenführen, sieht man das nur daran, dass beide zufällig denselben Nachfolger haben. Es gibt kein explizites "Merge-Point"-Konzept. Bei verschachtelten Entscheidungen wird das unlesbar.

### 1.3 Auswirkungen

- **Spezifikationsphase überlastet**: Der Specifier muss Kontrollfluss rekonstruieren statt ihn direkt aus dem Artefakt abzulesen.
- **Übersetzung in EMMA aufwändig**: EMMA hat explizite Regeln (DECISION) und Schleifenkörper (LOOP). Die Lücke zwischen dem Strukturartefakt und EMMA-Konstrukten ist unnötig groß.
- **Validierung erschwert**: Ohne expliziten Scope können Schleifen und Branches nicht programmatisch auf Konsistenz geprüft werden.
- **Fehlerquelle**: Implizite Konventionen (erster Nachfolger = true) werden vom LLM nicht zuverlässig eingehalten.

### 1.4 Kontextanalyse: Kognitive Last

Die Strukturierungsphase hat **Kapazitätsreserve** — ihre Aufgabe (logische Zerlegung) ist eine natürliche LLM-Stärke. Die Spezifikationsphase ist **am oberen Rand** — EMMA-Katalog (19 Typen), Parameter-Details (~150 Zeilen Tabellen), RPA Best Practices, Variablen-Erkennung, komplexe Patch-Strukturen. Durch explizitere Kontrollfluss-Modellierung im Strukturartefakt verschiebt sich Last vom Specifier (Rekonstruktion) zum Strukturierer (Modellierung) — dahin, wo Kapazität frei ist.

---

## 2. Ziel der Änderung

1. **Explizite Kontrollflussstrukturen** im Strukturartefakt: Schleifen-Scope, Mehrfach-Regeln bei Entscheidungen, Branch-Konvergenz.
2. **Bessere Übersetzbarkeit** in EMMA-Konstrukte: Strukturartefakt → Algorithmusartefakt mit minimalem Informationsverlust.
3. **Kognitive Last rebalancieren**: Strukturierer übernimmt mehr Modellierungsverantwortung, Specifier bekommt reichere Eingabe.
4. **Zusätzlich**: Strukturierer bereitet Variablen-Hinweise und analoge Schritte vor (zwei kleine Ergänzungen, die ~20% der Spezifikations-Rückfragen eliminieren).

---

## 3. Lösung

### 3.1 Datenmodell-Erweiterungen

Drei neue optionale Felder für `Strukturschritt`, ein neues Hilfsmodell:

#### Neues Modell: `Entscheidungsregel`

```python
class Entscheidungsregel(BaseModel):
    """Eine Regel innerhalb einer Entscheidung — Bedingung → Nachfolger."""
    bedingung: str          # Textuelle Bedingung, z.B. "Betrag > 5.000 €"
    nachfolger: str         # Schritt-ID des Ziel-Schritts
    bezeichnung: str = ""   # Optionaler Kurzname, z.B. "Freigabe nötig"
```

#### Neue Felder auf `Strukturschritt`

| Feld | Typ | Nur bei | Beschreibung |
|---|---|---|---|
| `regeln` | `list[Entscheidungsregel]` | `typ: "entscheidung"` | Geordnete Liste von Bedingung→Nachfolger-Mappings. Reihenfolge = Auswertungsreihenfolge. Letzte Regel = Catch-All ("Sonst"). Ersetzt `bedingung` als primäre Quelle. |
| `schleifenkoerper` | `list[str]` | `typ: "schleife"` | Liste der Schritt-IDs, die INNERHALB der Schleife liegen. Definiert den Scope explizit. |
| `abbruchbedingung` | `str` | `typ: "schleife"` | Textuelle Beschreibung der Abbruchbedingung, z.B. "Alle Positionen verarbeitet" |
| `konvergenz` | `str \| None` | `typ: "entscheidung"` | Schritt-ID, bei der alle Branches wieder zusammenführen. Optional — nicht jede Entscheidung konvergiert. |

#### Abwärtskompatibilität

- `bedingung` bleibt erhalten (für einfache if/else und bestehende Artefakte). Bei Neuanlage von Entscheidungen mit ≥2 Ausgängen soll das LLM `regeln` verwenden. `bedingung` dient als Fallback für einfache binäre Entscheidungen.
- `nachfolger` bleibt als flache Liste erhalten. Bei Entscheidungen wird sie aus `regeln` abgeleitet (Konsistenzprüfung im Executor oder Guardrail).
- Alle neuen Felder sind optional mit Default `None` / `[]` → bestehende Artefakte bleiben valide.

### 3.2 Beispiele für das erweiterte Modell

#### Entscheidung mit 3 Branches (elif)

```json
{
  "schritt_id": "s5",
  "titel": "Rechnungstyp bestimmen",
  "typ": "entscheidung",
  "beschreibung": "Frau Becker prüft den Rechnungsbetrag und entscheidet über das weitere Vorgehen...",
  "regeln": [
    {"bedingung": "Betrag > 5.000 €", "nachfolger": "s6", "bezeichnung": "Freigabe durch Abteilungsleiter"},
    {"bedingung": "Betrag > 1.000 €", "nachfolger": "s7", "bezeichnung": "Standardprüfung"},
    {"bedingung": "Sonst", "nachfolger": "s8", "bezeichnung": "Direktbuchung"}
  ],
  "nachfolger": ["s6", "s7", "s8"],
  "konvergenz": "s9",
  "bedingung": null,
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
  "beschreibung": "Für jede Position in der Rechnung werden die folgenden Schritte durchlaufen. Die Anzahl der Positionen variiert pro Rechnung (typisch: 1–50).",
  "schleifenkoerper": ["s3a", "s3b", "s3c"],
  "abbruchbedingung": "Letzte Rechnungsposition erreicht (keine weitere Zeile vorhanden)",
  "nachfolger": ["s4"],
  "reihenfolge": 3,
  "completeness_status": "vollstaendig",
  "algorithmus_status": "ausstehend"
}
```

### 3.3 Prompt-Ergänzungen für den Strukturierer

Zwei zusätzliche "Best Practices" (jeweils ~3–5 Zeilen):

1. **Variablen-Hinweise vorbereiten**: "Wenn der Nutzer Werte nennt, die sich pro Durchlauf ändern (Rechnungsnummer, Betrag, Dateiname), notiere das in der `beschreibung` — z.B. 'der **Rechnungsbetrag** (ändert sich pro Rechnung)'. Kein formales Variable-Format nötig."

2. **Analoge Schritte vormarkieren**: "Wenn ein Schritt nicht am Computer stattfindet (Telefonat, Unterschrift auf Papier, Postversand), notiere in der `beschreibung`: 'Analoger Schritt — nicht digital automatisierbar.' Das `spannungsfeld`-Feld kann ergänzend den Medienbruch dokumentieren."

### 3.4 Prompt-Anpassungen für den Specifier

- Terminologie-Tabelle ergänzen: Hinweis auf `regeln`, `schleifenkoerper`, `konvergenz` als Eingabe aus dem Strukturartefakt.
- Arbeitsweise: "Wenn der Strukturschritt `regeln` enthält, übersetze jede Regel direkt in eine EMMA DECISION-Regel. Wenn `schleifenkoerper` vorhanden, erstelle einen EMMA LOOP mit den referenzierten Abschnitten als Schleifenkörper."

---

## 4. Änderungsplan

### Phase 1: Datenmodell (Backend)

| # | Datei | Änderung |
|---|---|---|
| 1.1 | `backend/artifacts/models.py` | Neues Modell `Entscheidungsregel(BaseModel)` anlegen |
| 1.2 | `backend/artifacts/models.py` | `Strukturschritt` um 4 Felder erweitern: `regeln`, `schleifenkoerper`, `abbruchbedingung`, `konvergenz` — alle optional |
| 1.3 | `backend/artifacts/template_schema.py` | Neue Pfad-Patterns für die neuen Felder in `STRUCTURE_TEMPLATE` registrieren: `/schritte/{id}/regeln`, `/schritte/{id}/schleifenkoerper`, `/schritte/{id}/abbruchbedingung`, `/schritte/{id}/konvergenz` |
| 1.4 | `backend/artifacts/template_schema.py` | **Bugfix (Pre-Existing):** Pfad-Regex `s\d+` auf `s[^/]+` erweitern — aktuell werden IDs wie `s2a`, `s_gutschrift` (die der Prompt als Beispiele zeigt!) vom Template abgelehnt |

### Phase 2: Executor & Validierung (Backend)

| # | Datei | Änderung |
|---|---|---|
| 2.1 | `backend/artifacts/executor.py` | Sicherstellen, dass die neuen Felder als valide Patch-Ziele akzeptiert werden |
| 2.2 | `backend/core/orchestrator.py` | Invalidierungskaskade prüfen: Änderungen an `regeln` und `schleifenkoerper` sollten wie `bedingung`-Änderungen die referenzierten Algorithmusabschnitte invalidieren |
| 2.3 | `backend/modes/validation.py` | Deterministische Checks erweitern: `regeln`-Nachfolger müssen mit `nachfolger`-Liste konsistent sein; `schleifenkoerper`-Steps müssen existieren |

### Phase 3: Prompts

| # | Datei | Änderung |
|---|---|---|
| 3.1 | `backend/prompts/structuring.md` | Terminologie: `Entscheidungsregel`, `Schleifenkörper`, `Abbruchbedingung`, `Konvergenz` definieren |
| 3.2 | `backend/prompts/structuring.md` | Best Practices: Regeln bei Entscheidungen, Schleifenscope, Konvergenz-Felder |
| 3.3 | `backend/prompts/structuring.md` | Patch-Beispiele: Entscheidung mit `regeln` (elif), Schleife mit `schleifenkoerper` |
| 3.4 | `backend/prompts/structuring.md` | Best Practices: Variablen-Hinweise vorbereiten, analoge Schritte vormarkieren |
| 3.5 | `backend/prompts/structuring.md` | Referenz: Strukturschritt-Schema um neue Felder erweitern |
| 3.6 | `backend/prompts/specification.md` | Terminologie + Arbeitsweise: Hinweis auf `regeln`→DECISION und `schleifenkoerper`→LOOP Übersetzung |
| 3.7 | `backend/prompts/validation.md` | Prüfregeln erweitern: `regeln`↔`nachfolger` Konsistenz, `schleifenkoerper`-Scope-Validierung |

### Phase 4: Context Assembler

| # | Datei | Änderung |
|---|---|---|
| 4.1 | `backend/modes/structuring.py` | `_build_slot_status()` anpassen: `regeln` und `schleifenkoerper` in der Slot-Status-Anzeige darstellen |
| 4.2 | `backend/modes/specification.py` | `_build_structure_content()` anpassen: `regeln` und `schleifenkoerper` in der Read-Only-Darstellung anzeigen |

### Phase 5: Tests

| # | Datei | Änderung |
|---|---|---|
| 5.1 | `backend/tests/test_models.py` | Unit-Tests für `Entscheidungsregel`, erweiterten `Strukturschritt` |
| 5.2 | `backend/tests/test_executor.py` | Patch-Tests für die neuen Felder |
| 5.3 | `backend/tests/test_template_schema.py` | Pfad-Validierung für neue Patterns; **Regression**: `s2a`/`s_gutschrift` IDs müssen akzeptiert werden |
| 5.4 | `backend/tests/test_orchestrator.py` | Invalidierungskaskade: Änderung an `regeln` löst Invalidierung aus |
| 5.5 | `backend/tests/test_structuring.py` | Slot-Status-Darstellung enthält `regeln`/`schleifenkoerper` |

---

## 5. Risiken und Mitigationen

### 5.1 Bestehende Artefakte brechen

**Risiko**: Bestehende Artefakte in der Datenbank haben die neuen Felder nicht.
**Mitigation**: Alle neuen Felder haben Defaults (`None` / `[]`). Pydantic deserialisiert bestehende Artefakte fehlerfrei, da die Felder optional sind. Kein Migration-Skript nötig.

### 5.2 LLM setzt `regeln` und `nachfolger` inkonsistent

**Risiko**: Das LLM schreibt `regeln` mit Nachfolger-IDs, die nicht in `nachfolger` stehen (oder umgekehrt).
**Mitigation**: Deterministische Konsistenzprüfung im Executor oder als Guardrail: `set(r.nachfolger for r in regeln) == set(nachfolger)`. Bei Inkonsistenz: `nachfolger` aus `regeln` ableiten (regeln ist die Quelle der Wahrheit).

### 5.3 LLM ignoriert neue Felder

**Risiko**: Das LLM nutzt weiterhin nur `bedingung` + `nachfolger` statt `regeln`.
**Mitigation**: Prompt-Beispiele zeigen explizit `regeln` für alle Entscheidungen mit ≥2 Ausgängen. `bedingung` wird als "Fallback für einfache Ja/Nein-Entscheidungen" positioniert. Die Patch-Beispiele normalisieren den Gebrauch. First-Turn-Directive nutzt `regeln`.

### 5.4 Schleifenkoerper-Referenzen auf nicht existierende Steps

**Risiko**: `schleifenkoerper: ["s3a", "s3b"]` referenziert Steps, die (noch) nicht existieren.
**Mitigation**: Deterministische Validierung: Alle IDs in `schleifenkoerper` müssen in `schritte` existieren. Beim First-Turn (Sofort-Aktion) legt der Strukturierer alle Steps inklusive Schleifenkörper-Steps in einem Patch-Set an.

### 5.5 Template-Schema Regex-Erweiterung bricht bestehende Pfade

**Risiko**: Änderung von `s\d+` zu `s[^/]+` könnte unbeabsichtigte Pfade zulassen.
**Mitigation**: Die Regex `s[^/]+` ist immer noch restriktiv (muss mit `s` beginnen, kein Slash). LLM-generierte IDs wie `s1`, `s2a`, `s_gutschrift` werden alle korrekt erfasst. Kein Risiko für Injection, da der Executor nur auf Dict-Keys zugreift.

### 5.6 Erhöhte Prompt-Länge beim Strukturierer

**Risiko**: Neue Terminologie, Patch-Beispiele und Felder erhöhen den Prompt um geschätzt ~60–80 Zeilen.
**Mitigation**: Der Strukturierer-Prompt hat Kapazitätsreserve (271 Zeilen aktuell → ~340–350 Zeilen danach). Der Specification-Prompt ist mit 396 Zeilen größer und funktioniert. Kein Token-Budget-Problem.

---

## 6. Nicht im Scope

- **Hierarchische Schritt-Verschachtelung** (Steps als Kinder anderer Steps) — zu großer Architektur-Umbau für den Nutzen. Die flache Liste mit expliziten Scope-Feldern reicht.
- **Specification-Phase splitten** — Analyse ergab, dass die kognitive Last mit dieser Änderung + kleinen Prompt-Ergänzungen ausreichend rebalanciert wird.
- **Frontend-Anpassungen** — Falls das Frontend den Strukturgraphen visualisiert, muss es die neuen Felder auswerten. Das ist ein separates CR.
- **SDD-Update** — Die Systemdefinition muss nach Umsetzung aktualisiert werden. Wird in der Implementierung als letzter Schritt gemacht.

---

## 7. Abnahmekriterien

1. `Strukturschritt` hat die Felder `regeln`, `schleifenkoerper`, `abbruchbedingung`, `konvergenz` — alle optional.
2. `Entscheidungsregel` existiert als Modell mit `bedingung`, `nachfolger`, `bezeichnung`.
3. Template-Schema akzeptiert Patches auf alle neuen Felder.
4. Template-Schema akzeptiert Schritt-IDs wie `s2a`, `s_gutschrift` (Bugfix).
5. Änderungen an `regeln` und `schleifenkoerper` lösen Invalidierungskaskade aus.
6. Strukturierer-Prompt enthält Terminologie, Beispiele und Best Practices für die neuen Felder.
7. Specifier-Prompt beschreibt die Übersetzung `regeln`→DECISION und `schleifenkoerper`→LOOP.
8. Validierungs-Prompt prüft `regeln`↔`nachfolger` Konsistenz und `schleifenkoerper`-Referenzen.
9. Bestehende Artefakte (ohne neue Felder) werden fehlerfrei deserialisiert.
10. Alle bestehenden Tests laufen weiterhin grün.
11. Neue Tests für alle neuen Felder, Pfad-Patterns und Guardrails.

---

## 8. Aufwandsschätzung

| Phase | Geschätzter Umfang |
|---|---|
| Datenmodell | ~30 Zeilen Code + Template-Patterns |
| Executor & Validierung | ~50 Zeilen Code |
| Prompts | ~120 Zeilen Prompt-Text (über 3 Prompts) |
| Context Assembler | ~20 Zeilen Code |
| Tests | ~150 Zeilen Testcode |
| **Gesamt** | **~370 Zeilen** |
