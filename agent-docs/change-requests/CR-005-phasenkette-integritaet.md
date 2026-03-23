# CR-005: Phasenketten-Integrität — Variable Lineage, EMMA-Analog-Früherkennung, Specifier-Erstaktivierung

| Feld | Wert |
|---|---|
| **ID** | CR-005 |
| **Titel** | Phasenketten-Integrität: Variable Lineage, EMMA-Analog-Früherkennung, Specifier-Erstaktivierung |
| **Status** | Überholt |
| **Ersetzt durch** | CR-006 |
| **Erstellt** | 2026-03-23 |
| **Priorität** | Hoch |
| **Auslöser** | Strukturanalyse der drei Kernprompts: drei Lücken in der Übergabekette Explorer → Structurer → Specifier identifiziert |
| **Abhängigkeiten** | Setzt voraus: CR-003 (Explorer, Verifiziert), CR-004 (Structurer, Implementiert) |

> **Überholt durch CR-006**: Die hier identifizierten Defizite D-1 (Variable Lineage), D-2 (EMMA-Analog-Früherkennung) und D-3 (Erstaktivierung) werden durch eine übergeordnete Architekturlösung (Background-Initialisierung mit Validierung) grundlegend gelöst. D-1 und D-2 wandern in die neuen Init-Prompts, D-3 entfällt durch die Architektur. CR-006 absorbiert den vollständigen Scope dieses CRs.

---

## 1. Problemstellung

### Kernproblem

Die drei Phasenprompts sind in Terminologie, Output-Kontrakt und Completeness-Model konsistent. Es gibt jedoch drei strukturelle Übergabelücken in der Informationskette, die in realen Durchläufen zu Qualitätsverlust führen: Variablen werden nicht formal übergeben, analoge Prozessanteile werden zu spät entdeckt, und die Erstaktivierung des Specifiers ist für realistische Prozessgrößen nicht erfüllbar.

### Konkrete Defizite

**D-1: Variable Lineage — kein formaler Übergabe-Kontrakt**

Variablen entstehen als Freitext im Slot `variablen_und_daten` (Explorer), werden im Structurer informell in `beschreibung`-Feldern erwähnt ("der Betrag aus dem Dokument"), und erst im Specifier formal mit `[Variable] name (typ) — beschreibung. Quelle: ...` dokumentiert. Zwei Bruchstellen:

- Der Structurer hat kein konsistentes Markierungsformat für Variablen in `beschreibung`-Feldern. Variablen sind nicht von anderen Werten unterscheidbar.
- Der Specifier hat keine explizite Anweisung, `variablen_und_daten` aus dem Explorationsartefakt systematisch gegen seine `kontext`-Felder abzugleichen.

Folge: Variablen aus der Exploration gehen im Specifier unter, wenn sie nicht zufällig im Dialog erneut erwähnt werden.

Beispiel IST-Zustand (Structurer beschreibung):
```
"Frau Becker trägt den Betrag und die Rechnungsnummer in DATEV ein."
```
→ Der Specifier weiß nicht, ob "Betrag" und "Rechnungsnummer" bereits als Variablen in `variablen_und_daten` erfasst sind, oder ob er sie neu definieren soll.

**D-2: EMMA-Kompatibilität wird zu spät entdeckt**

Der Structurer modelliert analoge Prozessanteile (Telefonat, physische Unterschrift, Postversand) als reguläre Strukturschritte, ohne sie zu kennzeichnen. Der Specifier entdeckt diese Anteile erst beim Durcharbeiten des jeweiligen Schritts und setzt dann `emma_kompatibel: false`.

Das hat zwei Konsequenzen:
- **UX-Problem**: Der Nutzer hat nach der Strukturierungsphase das Bild eines vollständig automatisierbaren Prozesses. Die Korrektur in Phase 3 wirkt wie eine Überraschung.
- **Effizienz-Problem**: Der Specifier verliert Turns auf analoge Schritte, bei denen nach dem Muster "WAIT + emma_kompatibel: false" kaum Gestaltungsspielraum besteht.

Beispiel IST-Zustand (Strukturschritt ohne Kennzeichnung):
```json
{
  "schritt_id": "s4",
  "titel": "Freigabe durch Abteilungsleiter einholen",
  "typ": "aktion",
  "beschreibung": "Frau Becker geht zum Abteilungsleiter Herrn Schmidt und lässt ihn die Rechnung unterschreiben.",
  "spannungsfeld": null
}
```
→ Specifier trifft dies unvorbereitet.

**D-3: Specifier Erstaktivierung — "alle Steps in einem Turn" ist unrealistisch**

Der Specifier-Prompt fordert in der Erstaktivierung:

> "Lege für jeden Strukturschritt einen Algorithmusabschnitt an. [...] Analysiere die kontext Felder und lege für alle Strukturschritte, bei denen bereits genug Information vorliegt, vorläufige EMMA-Aktionen an"

Bei einem typischen Prozess mit 10–15 Strukturschritten (inklusive Entscheidungen, Schleifen, Ausnahmen) ist das in einem einzigen LLM-Turn nicht zuverlässig leistbar. Kein Fallback-Kriterium ist definiert.

Folge: Das LLM erzeugt unter Zeitdruck entweder unvollständige Abschnitte oder generische EMMA-Aktionen, die dem Nutzer wenig Mehrwert bieten und im Dialog ohnehin neu erarbeitet werden müssen.

### Auswirkungen

Ohne Änderung:
- Variablen aus der Exploration werden sporadisch übernommen oder doppelt definiert
- Nutzer erlebt in Phase 3 unerwartete Einschränkungen bei analogen Prozessanteilen
- Erster Turn im Specifier liefert schlechte Qualität, was das Vertrauen des Nutzers in das System reduziert

---

## 2. Ziel der Änderung

- **Structurer**: Variablen aus `variablen_und_daten` werden mit konsistentem `[VAR: name]`-Inline-Marker in `beschreibung`-Feldern gekennzeichnet. Analoge Prozessanteile werden mit `ANALOG:`-Präfix im `spannungsfeld` dokumentiert.
- **Specifier**: Erstaktivierung iteriert explizit über `variablen_und_daten` und überträgt alle Einträge in `kontext`-Felder. Erstaktivierung hat eine klare Priorisierung (Hauptpfad zuerst) mit definiertem Fallback für größere Prozesse. Analoge Schritte werden aus Structurer-`spannungsfeld` proaktiv erkannt und mit `emma_kompatibel: false` behandelt.

---

## 3. Lösung

Alle Änderungen sind **prompt-only** — keine Modell-, Code- oder Test-Änderungen erforderlich.

### 3.1 Änderungen in `backend/prompts/structuring.md`

#### Änderung S-1: "Variablen-Hinweise vorbereiten" — konsistentes Inline-Format

**IST:**
```
Wenn sich Werte pro Durchlauf ändern (Rechnungsnummer, Betrag, Kundennummer), markiere sie
in der `beschreibung` des Schritts. Das hilft der Spezifikation bei der Variablen-Modellierung.
Nutze die Informationen aus dem Slot `variablen_und_daten` des Explorationsartefakts als
Ausgangspunkt.
```

**SOLL:**
```
Wenn sich Werte pro Durchlauf ändern (Rechnungsnummer, Betrag, Kundennummer), markiere sie
in der `beschreibung` des Schritts mit dem Inline-Format `[VAR: name]`. Das macht Variablen
für die Spezifikationsphase maschinell erkennbar.

Verwende den Slot `variablen_und_daten` des Explorationsartefakts als vollständige Ausgangsliste:
Jede dort dokumentierte Variable MUSS in der `beschreibung` mindestens eines Strukturschritts
als `[VAR: name]` erscheinen. Ergänze Variablen, die der Nutzer im Strukturierungsdialog
zusätzlich nennt.

Beispiel:
"Frau Becker trägt [VAR: rechnungsnummer] und [VAR: rechnungsbetrag] in DATEV ein."
```

#### Änderung S-2: Neue Modellierungsregel "Analoge Prozessanteile kennzeichnen"

Ergänze als neuen Unterabschnitt in den **Modellierungsregeln** (nach "Konvergenz", vor "Nachfolger konsistent halten"):

```markdown
### Analoge Prozessanteile kennzeichnen

Wenn ein Strukturschritt Aktivitäten enthält, die nicht am Computer stattfinden
(Telefonat, physische Unterschrift, Postversand, persönliche Abstimmung ohne
Systemunterstützung), dokumentiere das im `spannungsfeld` mit dem Präfix `ANALOG:`.

Format: `ANALOG: [Beschreibung der analogen Aktivität] — nicht per RPA automatisierbar.`

Dies bereitet den Specifier auf eine informierte Grenzziehung vor und setzt die
Erwartungen des Nutzers noch in Phase 2 korrekt.

Beispiel:
```json
{"op": "replace", "path": "/schritte/s4/spannungsfeld", "value": "ANALOG: Freigabe erfolgt durch persönliche Rücksprache mit Herrn Schmidt (Abteilungsleiter) — nicht per RPA automatisierbar."}
```

Ist der **gesamte** Strukturschritt analog (kein computergestützter Anteil), setze
zusätzlich `completeness_status: "vollstaendig"` — der Specifier braucht für diesen
Schritt keine weiteren Informationen vom Nutzer.
```

### 3.2 Änderungen in `backend/prompts/specification.md`

#### Änderung P-1: Erstaktivierung — Priorisierung und Fallback

**IST:**
```
Erstaktivierung: Wenn das Algorithmusartefakt noch leer ist, erstelle es vollständig:
Lege für jeden Strukturschritt einen Algorithmusabschnitt an. Übernimm dabei alle
Informationen aus dem Strukturartefakt — jede Beschreibung, jeder Akteur, jedes System
geht in das `kontext`-Feld des jeweiligen Abschnitts. Analysiere die kontext Felder und
lege für alle Strukturschritte, bei denen bereits genug Information vorliegt, vorläufige
EMMA-Aktionen an und bringe sie in eine logische Sequenz. [...] WARTE NICHT auf
Nutzereingaben — handle sofort.
```

**SOLL:**
```
Erstaktivierung: Wenn das Algorithmusartefakt noch leer ist, gehe in dieser Reihenfolge vor:

**Schritt 1 — Alle Abschnitte anlegen**: Lege für jeden Strukturschritt einen
Algorithmusabschnitt an. Übernimm alle Informationen aus dem Strukturartefakt in das
`kontext`-Feld (Beschreibung, Akteure, Systeme, Regeln, Schwellen).

**Schritt 2 — Variablen-Übergabe sichern**: Prüfe den Slot `variablen_und_daten` im
Explorationsartefakt. Für jede dort dokumentierte Variable: Ordne sie dem Abschnitt zu,
in dem sie erstmals verwendet wird, und trage sie mit dem `[Variable]`-Format im
`kontext`-Feld ein. Ergänze Variablen, die aus `[VAR: name]`-Markierungen in den
Strukturschritt-Beschreibungen erkennbar sind, aber noch nicht im `kontext` stehen.

**Schritt 3 — Analoge Schritte vormarkieren**: Prüfe alle Strukturschritte auf
`ANALOG:`-Einträge im `spannungsfeld`. Lege für diese Schritte sofort eine
WAIT-Aktion mit `emma_kompatibel: false` an — sie brauchen keinen Dialogaufwand.

**Schritt 4 — Vorläufige EMMA-Aktionen nach Priorität**:
- Wenn ≤ 8 Strukturschritte: Lege für alle nicht-analogen Schritte vorläufige
  EMMA-Aktionen an.
- Wenn > 8 Strukturschritte: Lege vorläufige EMMA-Aktionen für den **Hauptpfad**
  an (Schritte in Reihenfolge, ohne Ausnahmen und Alternativpfade). Für alle
  weiteren Schritte: `aktionen: {}` — sie werden im Dialog gefüllt.

Informiere den Nutzer, welcher Strukturschritt zuerst bearbeitet wird, und stelle
die erste gezielte Frage. **WARTE NICHT** auf Nutzereingaben — handle sofort.
```

#### Änderung P-2: Analoge Schritte proaktiv kommunizieren

Ergänze in der Sektion **"Proaktiv und intelligent"** einen neuen Bullet-Punkt:

```markdown
- **Analoge Prozessanteile proaktiv kommunizieren**: Wenn ein Strukturschritt ein
  `spannungsfeld` mit `ANALOG:`-Eintrag hat, informiere den Nutzer zu Beginn dieses
  Abschnitts klar: "Dieser Schritt enthält analoge Anteile, die per RPA nicht
  automatisierbar sind. Ich dokumentiere sie als WAIT-Aktion mit Hinweis. Soll ich
  das so anlegen, oder gibt es eine digitale Alternative?" Warte auf Bestätigung,
  bevor du weitermachst.
```

### 3.3 Keine Code-Änderungen

Das bestehende Datenmodell deckt alle Anforderungen ab:
- `Strukturschritt.spannungsfeld: str | None` (vorhanden) — wird als Träger für `ANALOG:`-Präfix genutzt
- `Strukturschritt.beschreibung: str` (vorhanden) — nimmt `[VAR: name]`-Inline-Marker auf
- `EmmaAktion.emma_kompatibel: bool` (vorhanden) — wird durch Specifier korrekt gesetzt
- `Algorithmusabschnitt.kontext: str` (vorhanden) — nimmt `[Variable]`-Einträge auf

Keine Änderungen an:
- `backend/artifacts/models.py`
- `backend/artifacts/template_schema.py`
- `backend/modes/*.py`
- `backend/core/orchestrator.py`
- Tests

### 3.4 SDD-Konsistenz

**Konsistent mit SDD.** Die Änderungen erweitern bestehende Konzepte:
- Variable Lineage: Konkretisierung von SDD §5.3 (`variablen_und_daten`) und §5.5 (`kontext`-Feld)
- Analog-Früherkennung: Die SDD definiert `spannungsfeld` als "dokumentiertes Risiko, Problem oder Medienbruch" — analoge Prozessanteile sind ein Medienbruch im weiteren Sinn (digital ↔ analog)
- Erstaktivierung-Priorisierung: Keine SDD-Abweichung, reine Prozessoptimierung

Kein ADR erforderlich.

### 3.5 ADR-Konsistenz

- **ADR-006** (CR-002): `EmmaAktionstyp`-Enum, `nachfolger: list[str]` — nicht berührt
- Keine weiteren relevanten ADRs in CR-001 bis CR-004

---

## 3a. Abhängigkeiten & Konflikte

- **CR-003 (Verifiziert)**: Definiert die 7 Explorations-Slots inkl. `variablen_und_daten`. Änderung P-1 referenziert diesen Slot explizit — konsistent, kein Konflikt.
- **CR-004 (Implementiert)**: Letzter Rewrite von `structuring.md`. Änderungen S-1 und S-2 ergänzen diesen Prompt (Sektion "Variablen-Hinweise" erweitern, neue Modellierungsregel hinzufügen) — additive Ergänzungen, kein Konflikt.

**Keine Konflikte mit bestehenden CRs.**

---

## 4. Änderungsplan

| # | Datei | Änderung | Status |
|---|---|---|---|
| 1 | `backend/prompts/structuring.md` | Sektion "Variablen-Hinweise vorbereiten" ersetzen gemäß S-1: `[VAR: name]`-Format, Vollständigkeitspflicht gegenüber `variablen_und_daten` | Ausstehend |
| 2 | `backend/prompts/structuring.md` | Neue Untersektion "Analoge Prozessanteile kennzeichnen" nach "Konvergenz" einfügen gemäß S-2: `ANALOG:`-Präfix im `spannungsfeld`, Patch-Beispiel | Ausstehend |
| 3 | `backend/prompts/specification.md` | Erstaktivierung ersetzen gemäß P-1: 4-Schritt-Plan mit Variablen-Übergabe, ANALOG-Vormarkierung, Priorisierung Hauptpfad, Fallback ≤8/> 8 Steps | Ausstehend |
| 4 | `backend/prompts/specification.md` | Sektion "Proaktiv und intelligent" ergänzen gemäß P-2: Bullet-Punkt für analoge Prozessanteile kommunizieren | Ausstehend |

---

## 5. Risiken und Mitigationen

### R-1: `ANALOG:`-Konvention wird vom Structurer nicht konsistent angewendet

**Risiko:** Das LLM im Structurer wendet das `ANALOG:`-Präfix inkonsistent an — mal im `spannungsfeld`, mal in der `beschreibung`, mal gar nicht.

**Mitigation:** Die Anweisung in S-2 enthält ein konkretes Patch-Beispiel mit dem korrekten Pfad (`/schritte/sX/spannungsfeld`). Der Specifier ist in P-1 defensiv formuliert: Er prüft das `spannungsfeld` auf `ANALOG:`, stützt sich aber nicht ausschließlich darauf — er erkennt analoge Schritte weiterhin auch im Dialog. Kein Datenverlust, nur potenzielle Redundanz.

### R-2: `[VAR: name]`-Marker führt zu Übermarkierung

**Risiko:** Das LLM markiert zu viele Werte als Variablen, was die `beschreibung`-Felder unlesbar macht.

**Mitigation:** Die Anweisung in S-1 begrenzt explizit auf "Werte die sich pro Durchlauf ändern" und verweist auf `variablen_und_daten` als Ausgangsliste. Zusätzlich: Der Marker `[VAR: ...]` ist im Fließtext nicht aufdringlich und beeinträchtigt die Lesbarkeit minimal.

### R-3: Specifier-Erstaktivierung mit 4 Schritten erhöht kognitive Last

**Risiko:** Der 4-Schritt-Plan in P-1 erhöht die Komplexität der Erstaktivierung gegenüber dem bisherigen Einzeiler.

**Mitigation:** Die 4 Schritte sind sequenziell und klar voneinander abgegrenzt. Jeder Schritt hat ein eindeutiges Zielobjekt (Abschnitte anlegen → Variablen übertragen → Analoge vormarkieren → EMMA-Aktionen anlegen). Die Gesamtkomplexität sinkt, weil Schritt 3 (Analoge) und Schritt 2 (Variablen) die nachfolgenden Dialog-Turns entlasten.

### R-4: Prompt-Länge

**Risiko:** Beide Prompts werden durch die Ergänzungen länger.

**Mitigation:** Alle Ergänzungen ersetzen oder präzisieren bestehende Anweisungen (S-1 ersetzt einen Absatz, P-1 ersetzt die Erstaktivierung). Netto-Längenzuwachs: ~15–25 Zeilen pro Datei. Unkritisch für Tokenlimit-Strategie.

---

## 6. Nicht im Scope

- **NESTED_PROCESS** als 19. EMMA-Aktion: In `specification.md` erwähnt, aber nicht in `models.py` (EmmaAktionstyp-Enum). Separate Analyse erforderlich.
- **`spannungsfeld`-Downstream-Kontrakt**: Was nach der Strukturierung mit `spannungsfeld`-Einträgen passiert (Reporting, Management Summary) bleibt undefiniert. Separater CR wenn Bedarf.
- **Backward-Signal-Protokoll** (Specifier → Structurer bei entdeckten Strukturlücken): Separater CR wenn Bedarf.
- **Explorer-Änderungen**: Der Explorer-Prompt (`exploration.md`) benötigt keine Änderungen — die bestehende Anweisung "Format: Name — Beschreibung, Quelle" im `variablen_und_daten`-Slot ist ausreichend.

---

## 7. Abnahmekriterien

1. `structuring.md` enthält in der Sektion "Variablen-Hinweise vorbereiten" das Format `[VAR: name]` mit Anweisung zur Vollständigkeit gegenüber `variablen_und_daten`.
2. `structuring.md` enthält einen Patch-Beispiel-Block für `[VAR: name]` in einem `beschreibung`-Feld.
3. `structuring.md` enthält den neuen Unterabschnitt "Analoge Prozessanteile kennzeichnen" mit `ANALOG:`-Konvention und Patch-Beispiel.
4. `specification.md` enthält in der Erstaktivierung einen 4-Schritt-Plan (Abschnitte anlegen → Variablen → Analog → EMMA-Aktionen nach Priorität).
5. `specification.md` enthält explizite Anweisung, `variablen_und_daten` aus dem Explorationsartefakt in `kontext`-Felder zu übertragen.
6. `specification.md` enthält Fallback-Regel: Hauptpfad zuerst, bei > 8 Strukturschritten `aktionen: {}` für den Rest.
7. `specification.md` enthält in "Proaktiv und intelligent" den Bullet-Punkt für analoge Schritte kommunizieren.
8. Alle bestehenden Platzhalter in beiden Prompts (`{context_summary}`, `{exploration_content}`, `{slot_status}`, `{structure_content}`, `{algorithm_status}`) sind weiterhin vorhanden und unverändert.
9. Alle Tests in `test_structuring_mode.py` und `test_specification_mode.py` (falls vorhanden) sind grün — es gibt keine Code-Änderungen, die Tests sollten unberührt bleiben.

---

## 8. Aufwandsschätzung

| Feld | Wert |
|---|---|
| **Komplexität** | S (2 Dateien, reiner Prompt-Ergänzung, kein Code/Modell/Test) |
| **Betroffene Dateien** | 2 |
| **Breaking Change** | Nein |

| Phase | Dateien | Komplexität |
|---|---|---|
| Prompt Structurer | `backend/prompts/structuring.md` | S (2 gezielte Ergänzungen) |
| Prompt Specifier | `backend/prompts/specification.md` | S (Erstaktivierung ersetzen + 1 Bullet) |
