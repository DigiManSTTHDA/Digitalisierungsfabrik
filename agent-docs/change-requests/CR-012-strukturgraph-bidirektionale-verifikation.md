# CR-012: Strukturgraph — Bidirektionale Verifikation und Reihenfolge-Überarbeitung

| Feld           | Wert                                                        |
| -------------- | ----------------------------------------------------------- |
| **ID**         | CR-012                                                      |
| **Titel**      | Strukturgraph — Bidirektionale Verifikation via `vorgaenger` |
| **Status**     | Verifiziert                                                 |
| **Erstellt**   | 2026-03-27                                                  |
| **Priorität**  | Mittel                                                      |
| **Auslöser**   | Prompt-Rewrite Q1/2026: reihenfolge funktioniert nicht bei Verzweigungen |
| **Abhängigkeiten** | Setzt voraus: CR-002 (Kontrollfluss-Felder, implementiert) |

---

## 1. Problemstellung

### Kernproblem

Das Feld `reihenfolge` im `Strukturschritt` suggeriert eine lineare Sequenz, die bei Verzweigungen (Entscheidungen mit mehreren Pfaden) nicht existiert. Die SDD definiert es als "Position im Prozessablauf" — aber bei einer Entscheidung s2 → s3 oder s2a sind s2a und s3 **parallel**, nicht sequenziell. Eine lineare Nummerierung (1, 2, 3, 4) bildet das nicht ab.

### Konkrete Defizite

1. **Irreführende Semantik**: `reihenfolge: 3` für s2a und `reihenfolge: 4` für s3 suggeriert, dass s2a VOR s3 kommt — tatsächlich ist s2a ein alternativer Pfad, und s3 ist der Merge-Punkt beider Pfade.

2. **Keine bidirektionale Verifikation**: Der Graph hat nur Vorwärts-Referenzen (`nachfolger`). Um zu prüfen ob ein Schritt erreichbar ist, muss man den gesamten Graphen traversieren. Ein `vorgaenger`-Feld würde sofortige Plausibilitätsprüfung ermöglichen: "Wenn s3 als Nachfolger von s2 und s2a eingetragen ist, müssen s2 und s2a als Vorgänger von s3 eingetragen sein."

3. **LLM-Verwirrung**: Das LLM muss eine konsistente lineare Nummerierung vergeben, obwohl der Graph nicht linear ist. Bei Einfügungen/Löschungen müssen ggf. alle reihenfolge-Werte umnummeriert werden — zusätzliche Komplexität ohne Nutzen.

### Auswirkungen

- Ohne Änderung: Prompts müssen explizit erklären, dass `reihenfolge` "nur für Sortierung" ist — das ist kontraintuitiv und fehleranfällig.
- Graph-Inkonsistenzen (verwaiste Schritte, fehlende Referenzen) werden erst durch den Python-Validator erkannt, nicht durch das Datenmodell selbst.

---

## 2. Ziel der Änderung

- Neues Feld `vorgaenger: list[str]` auf `Strukturschritt` — Liste der Schritt-IDs die auf diesen Schritt verweisen.
- Bidirektionale Verifikation: `nachfolger` und `vorgaenger` können gegeneinander geprüft werden.
- `reihenfolge` bleibt erhalten (rein für Display-Sortierung), wird aber in Prompts und SDD korrekt als "Anzeigereihenfolge" beschrieben (nicht "Position im Ablauf").
- Der Python-Validator (`init_validator.py`) prüft Konsistenz: Wenn A in `nachfolger` von B steht, muss B in `vorgaenger` von A stehen (und umgekehrt).

---

## 3. Lösung

### Datenmodell-Änderungen

**Neues Feld auf `Strukturschritt`:**

```python
class Strukturschritt(BaseModel):
    # ... bestehende Felder ...
    vorgaenger: list[str] = Field(default_factory=list)  # Schritt-IDs die auf diesen Schritt verweisen
```

- **Typ:** `list[str]`
- **Default:** `[]` (leere Liste)
- **Semantik:** Liste aller Schritt-IDs, deren `nachfolger`-Feld diesen Schritt enthält
- **Startschritt:** `vorgaenger: []` (kein Vorgänger)
- **Ausnahme-Schritte:** `vorgaenger: []` (stehen außerhalb des regulären Flusses)

### Beispiel

```json
{
  "s1": {
    "schritt_id": "s1", "titel": "Bestellung öffnen", "typ": "aktion",
    "reihenfolge": 1,
    "nachfolger": ["s2"],
    "vorgaenger": []
  },
  "s2": {
    "schritt_id": "s2", "titel": "Kunde vorhanden?", "typ": "entscheidung",
    "reihenfolge": 2,
    "nachfolger": ["s3", "s2a"],
    "vorgaenger": ["s1"],
    "bedingung": "Existiert der Kunde in SAP?",
    "konvergenz": "s3"
  },
  "s2a": {
    "schritt_id": "s2a", "titel": "Kundenstamm anlegen", "typ": "aktion",
    "reihenfolge": 3,
    "nachfolger": ["s3"],
    "vorgaenger": ["s2"]
  },
  "s3": {
    "schritt_id": "s3", "titel": "Auftrag erfassen", "typ": "aktion",
    "reihenfolge": 4,
    "nachfolger": ["s4"],
    "vorgaenger": ["s2", "s2a"]
  }
}
```

Verifikationsregel: Für jeden Schritt X mit `nachfolger: [Y, Z]` muss gelten: X ∈ Y.vorgaenger UND X ∈ Z.vorgaenger. Und umgekehrt.

### Prompt-Änderungen

1. **init_structuring.md**: `vorgaenger` in Typbeschreibung, Patch-Beispiele und Beispiel-Artefakt ergänzen.
2. **structuring.md**: `vorgaenger` in Schema-Referenz und Graph-Konsistenz-Regel ergänzen. Regel: "Bei jeder Änderung an `nachfolger` auch `vorgaenger` des Zielschritts aktualisieren."
3. **SDD**: `reihenfolge`-Beschreibung von "Position im Prozessablauf" auf "Anzeigereihenfolge" korrigieren.

### Abwärtskompatibilität

- **Default `[]`**: Bestehende Artefakte ohne `vorgaenger` laden korrekt (Pydantic-Default).
- **Keine Migration nötig**: Bestehende Artefakte funktionieren weiter. `vorgaenger` wird bei neuen Artefakten automatisch gesetzt.
- **Bestehende Tests**: Bleiben grün — neues Feld hat Default.

### SDD-Konsistenz

- **Abweichung von SDD**: Die SDD beschreibt `reihenfolge` als "Position im Prozessablauf". Der CR ändert die Semantik zu "Anzeigereihenfolge". Dies ist eine Klarstellung, keine funktionale Änderung (Code behandelt es bereits so).
- **Neues Feld**: `vorgaenger` ist nicht in der SDD. Wird als Erweiterung hinzugefügt.

### ADR-Konsistenz

- **CR-002 ADR** (Kontrollfluss-Felder): Konsistent. CR-002 hat `nachfolger`, `regeln`, `schleifenkoerper`, `konvergenz` eingeführt. `vorgaenger` ergänzt die Vorwärts-Referenzen um Rückwärts-Referenzen.

### ADR: Bidirektionale Graphreferenzen

- **Kontext**: Der Strukturgraph hat nur Vorwärts-Referenzen (`nachfolger`). Inkonsistenzen (verwaiste Schritte, nicht-erreichbare Schritte) erfordern aufwändige Graph-Traversierung zur Erkennung.
- **Entscheidung**: Neues Feld `vorgaenger` als inverse Referenz zu `nachfolger`. Wird vom LLM bei jeder Patch-Operation mitgepflegt.
- **Begründung**: Bidirektionale Referenzen ermöglichen O(1)-Konsistenzprüfung statt O(n)-Graph-Traversierung. Das LLM kann Fehler sofort erkennen statt sie zu akkumulieren.
- **Konsequenzen**: SDD-Update nach Implementierung. Template-Schema um erlaubte Pfade erweitern. Prompts müssen `vorgaenger` in Beispielen zeigen.

---

## 3a. Abhängigkeiten & Konflikte

- **CR-002** (Implementiert): Führte `nachfolger`, `regeln`, `schleifenkoerper`, `konvergenz` ein. `vorgaenger` ergänzt diese — kein Konflikt.
- Keine Konflikte mit anderen aktiven CRs.

---

## 4. Änderungsplan

| #  | Datei                              | Änderung                                                                                                |
| -- | ---------------------------------- | ------------------------------------------------------------------------------------------------------- |
| 1  | `backend/artifacts/models.py`      | `vorgaenger: list[str] = Field(default_factory=list)` auf `Strukturschritt` hinzufügen                  |
| 2  | `backend/artifacts/template_schema.py` | Erlaubte Patch-Pfade: `/schritte/{id}/vorgaenger` mit Operationen `["replace"]` hinzufügen          |
| 3  | `backend/artifacts/init_validator.py` | Neue Validierungsregel: Für jeden Schritt prüfen ob nachfolger↔vorgaenger konsistent sind            |
| 4  | `backend/core/executor.py`         | `vorgaenger` zu den nicht-invalidierenden Feldern hinzufügen (wie `nachfolger`, `reihenfolge`)          |
| 5  | `backend/prompts/init_structuring.md` | `vorgaenger` in Typbeschreibung, allen Patch-Beispielen und Beispiel-Artefakt ergänzen              |
| 6  | `backend/prompts/structuring.md`   | `vorgaenger` in Schema-Referenz, Graph-Konsistenz-Regel und Beispiel-Artefakt ergänzen                 |
| 7  | `backend/tests/test_artifact_models.py` | Test: Strukturschritt mit vorgaenger erstellen, Default-Verhalten prüfen                           |
| 8  | `backend/tests/test_init_validator.py` | Test: Konsistenzprüfung nachfolger↔vorgaenger (konsistent → ok, inkonsistent → kritisch)            |
| 9  | `backend/tests/test_executor.py`   | Test: vorgaenger-Änderung löst keine Invalidierung aus                                                  |
| 10 | `docs/digitalisierungsfabrik_systemdefinition.md` | `reihenfolge` Beschreibung: "Position im Prozessablauf" → "Anzeigereihenfolge". `vorgaenger` dokumentieren. |

---

## 5. Risiken und Mitigationen

### Risiko: LLM vergisst vorgaenger zu pflegen

- **Risiko**: Das LLM aktualisiert `nachfolger` aber vergisst `vorgaenger` des Zielschritts.
- **Mitigation**: Code-Guardrail wie bei `_derive_nachfolger_from_regeln` in `structuring.py` — automatische Ableitung von `vorgaenger` aus `nachfolger` nach jedem Patch-Cycle. Dann muss das LLM `vorgaenger` gar nicht selbst pflegen.

### Risiko: Bestehende Artefakte ohne vorgaenger

- **Risiko**: Ältere Artefakte haben kein `vorgaenger`-Feld.
- **Mitigation**: Default `[]` in Pydantic. Validator meldet nur Inkonsistenz wenn `vorgaenger` vorhanden aber falsch ist — nicht wenn es fehlt.

### Risiko: Prompt-Länge

- **Risiko**: `vorgaenger` in jedem Patch-Beispiel vergrößert den Prompt.
- **Mitigation**: Wenn Code-Guardrail (automatische Ableitung) umgesetzt wird, muss `vorgaenger` nicht in den Prompts erscheinen — es wird im Hintergrund berechnet.

---

## 6. Nicht im Scope

- **Entfernung von `reihenfolge`**: Das Feld bleibt erhalten (wird in Frontend und Backend für Sortierung verwendet). Nur die Semantik wird klargestellt.
- **Automatische Umnummerierung von `reihenfolge`**: Keine Code-Logik die reihenfolge automatisch neu vergibt.
- **Änderungen am Algorithmusartefakt**: `vorgaenger` betrifft nur das Strukturartefakt.

---

## 7. Abnahmekriterien

1. `Strukturschritt` hat ein Feld `vorgaenger: list[str]` mit Default `[]`.
2. Template-Schema erlaubt `replace` auf `/schritte/{id}/vorgaenger`.
3. `vorgaenger`-Änderungen lösen keine Algorithmus-Invalidierung aus.
4. Python-Validator prüft nachfolger↔vorgaenger-Konsistenz und meldet Inkonsistenzen als `kritisch`.
5. Bestehende Tests bleiben grün (Default `[]` bricht nichts).
6. Neue Tests für: Model-Default, Validator-Konsistenzprüfung, Nicht-Invalidierung.
7. Prompts (init_structuring.md, structuring.md) dokumentieren `vorgaenger` korrekt.
8. SDD: `reihenfolge` als "Anzeigereihenfolge" beschrieben, `vorgaenger` dokumentiert.

---

## 8. Aufwandsschätzung

| Phase                    | Dateien                                                  | Komplexität |
| ------------------------ | -------------------------------------------------------- | ----------- |
| Datenmodell              | `models.py`                                              | S           |
| Schema/Validierung       | `template_schema.py`, `init_validator.py`, `executor.py` | S           |
| Prompts                  | `init_structuring.md`, `structuring.md`                  | M           |
| Tests                    | `test_artifact_models.py`, `test_init_validator.py`, `test_executor.py` | S |
| SDD                      | `digitalisierungsfabrik_systemdefinition.md`              | S           |

- **Komplexität:** S (8 Dateien, kein Breaking Change)
- **Betroffene Dateien:** 10
- **Breaking Change:** Nein — Default `[]` ist abwärtskompatibel.

### Empfehlung: Code-Guardrail statt LLM-Pflege

Statt das LLM `vorgaenger` in jedem Patch mitpflegen zu lassen (fehleranfällig), empfiehlt sich eine automatische Ableitung im Code — analog zu `_derive_nachfolger_from_regeln` in `structuring.py`. Nach jedem Patch-Cycle wird `vorgaenger` deterministisch aus allen `nachfolger`-Referenzen berechnet. Das eliminiert Risiko 1 und reduziert die Prompt-Änderungen auf die Schema-Referenz.
