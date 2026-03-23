# CR-004: Überarbeitung des Strukturierungsprompts — Intelligentere Interaktion und Zielschärfe

| Feld | Wert |
|---|---|
| **ID** | CR-004 |
| **Titel** | Überarbeitung des Strukturierungsprompts — Intelligentere Interaktion und Zielschärfe |
| **Status** | Implementiert |
| **Erstellt** | 2026-03-23 |
| **Priorität** | Hoch |
| **Auslöser** | Praxis-Feedback: Structuring-Prompt stellt redundante Fragen, ist zu vage in der Arbeitsweise, erkennt Spannungsfelder nicht proaktiv und passt stilistisch nicht zum überarbeiteten Explorer (CR-003) |
| **Abhängigkeiten** | Setzt voraus: CR-002 (Kontrollfluss-Felder, Status: Implementiert), CR-003 (Explorer-Überarbeitung, Status: Verifiziert) |

---

## 1. Problemstellung

### Kernproblem

Der Strukturierungsprompt (`backend/prompts/structuring.md`) hat nach der Implementierung von CR-002 (Kontrollfluss-Felder) und CR-003 (Explorer-Überarbeitung) mehrere Defizite, die die Qualität der Strukturierung beeinträchtigen.

### Konkrete Defizite

**D-1: Kein klarer Rolleneinstieg.**
Der Prompt beginnt direkt mit der Systembeschreibung ("Die Digitalisierungsfabrik hilft..."). Im Gegensatz zum Explorer-Prompt (CR-003: "Du bist ein explorativer Prozessanalyst") fehlt eine klare Rollenidentität. Das LLM hat keinen Anker für sein Selbstverständnis.

**D-2: Befragung nach Schema F statt intelligent.**
Die Sektion "Systematisch befragen" enthält 7 Standardfragen (Reihenfolge, Entscheidungspunkte, Verzweigungen, Schleifen, Ausnahmen, Akteure, Spannungsfelder), die unabhängig vom bereits vorliegenden Wissensstand gestellt werden. Beispiel: "Gibt es an dieser Stelle eine Prüfung oder Entscheidung?" — obwohl der Slot `entscheidungen_und_schleifen` aus der Exploration bereits genau diese Entscheidungen dokumentiert hat.

Folge: Redundante Fragen frustrieren den Fachexperten und verschwenden Turns.

**D-3: Arbeitsweise zu vage, keine Beispiele.**
Die Erstaktivierung sagt "analysiere das Explorationsartefakt sofort und erstelle Patches für alle erkennbaren Prozessschritte" — aber gibt kein konkretes Beispiel, wie das Ergebnis aussehen soll. Die Vertiefung sagt "frage gezielt nach fehlenden Details" — aber nennt keine Kriterien für "fehlend". Das LLM muss raten, was "gut genug" für die Spezifikation ist.

**D-4: Spannungsfelder nur bei expliziter Nutzernennung.**
Die Anweisung lautet: "Wenn der Nutzer ein Problem, eine Ineffizienz oder einen Medienbruch benennt, dokumentiere es". Das LLM soll aber Medienbrüche, redundante Eingaben und manuelle Überwachung **selbst erkennen** können — die Information dazu steht bereits im Explorationsartefakt.

**D-5: Ziel der Phase unklar formuliert.**
Der Prompt sagt "textbasiertes BPMN erstellen", erklärt aber nicht, was das für die nachfolgende Spezifikation konkret bedeutet. Dem LLM fehlt das Verständnis, dass jeder Strukturschritt genug Detail für einen RPA-Algorithmus auf Einzelaktionsebene enthalten muss.

**D-6: Redundanzen zum Explorer-Prompt.**
Die "Best Practices" wiederholen Konzepte, die der Explorer bereits abgearbeitet hat (Entscheidungspunkte erkennen, Systeme identifizieren, Ausnahmen erfragen). Nach CR-003 liefert der Explorer diese Informationen bereits vorstrukturiert im Artefakt.

**D-7: Akademischer Ton, fehlende "Resonanz".**
Die Anweisungen klingen formal und erzeugen keine klare Handlungsrichtung. Es fehlt die Direktive "maximaler Fortschritt pro Turn" — das LLM tendiert dazu, unnötige Rückfragen zu stellen statt sofort Strukturschritte anzulegen.

### Auswirkungen

Ohne Änderung: Der Structurer stellt redundante Fragen zu bereits bekannten Entscheidungen, erzeugt zu wenig Detail in den Beschreibungen, erkennt Spannungsfelder nicht proaktiv, und die Spezifikation erhält ein unzureichend vorbereitetes Strukturartefakt.

---

## 2. Ziel der Änderung

- **Klare Rollenidentität**: "Du bist ein Prozessarchitekt" als Einstieg (analog CR-003)
- **Intelligente Befragung**: Prüfe vor jeder Frage, ob die Information bereits vorliegt. Statt Standardfragen: gezielte Vertiefung mit konkreten Vorher/Nachher-Beispielen
- **Konkrete Arbeitsweise**: 5-Schritt-Plan für Erstaktivierung mit Beispiel, Checkliste für Vertiefung, Vorher/Nachher-Beispiel für gute Beschreibungen
- **Proaktive Spannungsfeld-Erkennung**: 4 Erkennungsmuster (Medienbrüche, redundante Eingaben, manuelle Überwachung, fehlende Schnittstellen)
- **Zielschärfe**: Explizite Verbindung zur Spezifikation — "genug Detail für Algorithmus auf Einzelaktion-Ebene"
- **Redundanzbereinigung**: Nur Modellierungsregeln behalten, die spezifisch für die Strukturierung sind
- **Direkter Ton**: "Maximaler Fortschritt pro Turn" als Handlungsdirektive

---

## 3. Lösung

### 3.1 Prompt-Rewrite (`backend/prompts/structuring.md`)

Kompletter Rewrite mit folgenden strukturellen Änderungen:

**a) Rolleneinstieg (neu):**
```
Du bist ein **Prozessarchitekt** im Rahmen der Digitalisierungsfabrik.
Deine Aufgabe: Das Prozesswissen aus der Exploration in eine logisch
präzise Prozessstruktur überführen — ein textbasiertes BPMN, das in
der nächsten Phase direkt in RPA-Aktionssequenzen übersetzt werden kann.
```

**b) Zielschärfe (neu):**
```
In der nächsten Phase (Spezifikation) wird jeder Strukturschritt in eine
konkrete Sequenz von RPA-Aktionen übersetzt. Du musst die RPA-Aktionen
nicht kennen — aber dein Strukturartefakt muss so detailliert und präzise
sein, dass diese Übersetzung reibungslos gelingt. Jeder Strukturschritt
muss genug Information enthalten, um daraus einen Algorithmus auf
Einzelaktion-Ebene ableiten zu können.
```

**c) Erstaktivierung mit 5-Schritt-Plan und Beispiel (vorher: ein vager Absatz):**
1. Alle 7 Slots durchgehen
2. Strukturschritte ableiten (inkl. `entscheidungen_und_schleifen` als direkte Vorlage)
3. Konsolidieren, nicht kopieren — Redundanzen entfernen, aber kein Detail verlieren
4. Reihenfolge und Nachfolger zuweisen
5. Entwurf nummeriert präsentieren

Plus konkretes Beispiel: Rechnungseingangsprozess → 8 Strukturschritte (s1–s6 + s_gutschrift).

**d) Vertiefung mit Checkliste (vorher: "frage gezielt nach Details"):**
- Wer führt den Schritt aus?
- Wo findet er statt? (System, Zugriffsweg)
- Was genau passiert? (Eingaben, Ausgaben, Prüfungen)
- Welche Daten fließen? (Variablen)
- Was kann schiefgehen?
- Bei Entscheidungen: Wie viele Ausgänge? Bedingungen?
- Bei Schleifen: Worüber wird iteriert? Wann ist Schluss?

Plus Vorher/Nachher-Beispiel: Einzeiler "Rechnung in DATEV erfassen" vs. vollständige Beschreibung mit Akteur, System, Feldern, Zugriffsweg, Tastenkürzel.

**e) "Intelligent befragen" ersetzt "Systematisch befragen":**
- Neue Kernregel: "Vor dem Fragen prüfen" — ist die Info schon im Explorationsartefakt?
- 4 konkrete Statt-X-besser-Y-Beispiele:
  - Statt "Was passiert nach Schritt X?" → gezielte Lückenfrage
  - Statt "Gibt es hier eine Entscheidung?" → Bestätigung + Detailfrage
  - Statt "Was passiert wenn etwas schiefgeht?" → konkreter Fehlerfall
  - Statt "Wird das wiederholt?" → Varianten-Frage
- Grundregel: "Frage nicht aus Pflichtgefühl, sondern weil die Antwort einen Strukturschritt vervollständigt"

**f) Proaktive Spannungsfeld-Erkennung (vorher: nur bei Nutzernennung):**
4 Erkennungsmuster mit konkreten Beschreibungen:
- Medienbrüche: Manuelle Datenübertragung zwischen Systemen
- Redundante Eingaben: Dieselbe Information in mehrere Systeme
- Manuelle Überwachung: Fristen per Kalender/Excel
- Fehlende Schnittstellen: Systeme ohne automatischen Datenfluss

**g) Modellierungsregeln gestrafft:**
- "Best Practices für die Strukturierung" (10 Punkte, teils redundant zum Explorer) → "Modellierungsregeln" (8 fokussierte Subsektionen)
- Entfernt: Allgemeine Hinweise zu Entscheidungspunkten erkennen, Systeme identifizieren, Ausnahmen erfragen (macht der Explorer bereits)
- Beibehalten: Granularität, Entscheidungen/Schleifen/Ausnahmen/Konvergenz modellieren, Nachfolger-Konsistenz, Variablen-Hinweise

**h) Handlungsdirektive (neu):**
```
Maximaler Fortschritt pro Turn: Jeder Turn soll den größtmöglichen
Schritt in Richtung Fertigstellung machen. Wenn du genug Information
hast, erstelle sofort Strukturschritte. Wenn dir etwas fehlt, stelle
die eine Frage, deren Antwort den größten Erkenntnisgewinn bringt.
```

### 3.2 Keine Code-Änderungen nötig

Der Prompt verwendet dieselben Platzhalter wie zuvor:
- `{context_summary}` — injiziert von `prompt_context_summary()`
- `{exploration_content}` — injiziert von `_build_exploration_content()`
- `{slot_status}` — injiziert von `_build_slot_status()`

Keine Änderungen an:
- `backend/modes/structuring.py` — Platzhalter-Ersetzung unverändert
- `backend/artifacts/models.py` — Datenmodell unverändert
- `backend/artifacts/template_schema.py` — Patch-Schema unverändert
- `backend/core/executor.py` — Patch-Anwendung unverändert

### 3.3 Keine Test-Änderungen nötig

Alle 18 Tests in `test_structuring_mode.py` sind grün. Die Tests prüfen die Code-Logik (Guardrails, Patch-Ableitung, Phasenstatus), nicht den Prompt-Inhalt.

---

## 4. Änderungsplan

| # | Datei | Änderung | Status |
|---|---|---|---|
| 1 | `backend/prompts/structuring.md` | Kompletter Rewrite gemäß §3.1 (a–h). Alle `@@@`-Kommentare entfernt. | ✅ Implementiert |

---

## 5. Risiken und Mitigationen

### R-1: LLM-Verhalten ändert sich

**Risiko:** Der überarbeitete Prompt erzeugt anderes LLM-Verhalten als bisher — potenziell unerwartete Ergebnisse.

**Mitigation:** Alle deterministischen Guardrails bleiben unverändert (Phasenstatus-Guardrails, regeln→nachfolger-Ableitung, Patch-Summarizer). Das LLM hat denselben Handlungsspielraum wie zuvor; die Anweisungen sind nur präziser. E2E-Tests werden im nächsten Durchlauf die Qualität validieren.

### R-2: Prompt-Länge

**Risiko:** Der überarbeitete Prompt könnte länger sein und mehr Tokens verbrauchen.

**Mitigation:** Durch Redundanzbereinigung (Best Practices gestrafft, Standardfragen entfernt) und klarere Struktur ist der Prompt in der Netto-Informationsdichte höher, aber in der absoluten Länge vergleichbar. Monitoring über bestehendes Token-Tracking.

---

## 6. Nicht im Scope

- **SDD-Aktualisierung:** §6.6.2 (Strukturierungsmodus) wird nach Verifikation aktualisiert.
- **Backend-Code-Änderungen:** Keine nötig — reiner Prompt-Rewrite.
- **Test-Änderungen:** Keine nötig — alle 18 Tests grün.
- **Andere Prompts:** Explorer (CR-003), Specifier und Validator bleiben unverändert.

---

## 7. Abnahmekriterien

1. `structuring.md` enthält keine `@@@`-Kommentare mehr.
2. `structuring.md` beginnt mit klarer Rollenidentität ("Du bist ein Prozessarchitekt").
3. `structuring.md` enthält "Maximaler Fortschritt pro Turn" als Handlungsdirektive.
4. `structuring.md` enthält Erstaktivierung mit 5-Schritt-Plan und konkretem Beispiel.
5. `structuring.md` enthält Vertiefungs-Checkliste (Wer/Wo/Was/Daten/Fehler).
6. `structuring.md` enthält Vorher/Nachher-Beispiel für gute Beschreibungen.
7. `structuring.md` enthält "Intelligent befragen" mit Vor-dem-Fragen-Prüfung und 4 Statt-X-besser-Y-Beispielen.
8. `structuring.md` enthält proaktive Spannungsfeld-Erkennung mit 4 Erkennungsmustern.
9. `structuring.md` referenziert die 7 Explorations-Slots (CR-003) korrekt.
10. Alle Platzhalter (`{context_summary}`, `{exploration_content}`, `{slot_status}`) sind vorhanden.
11. Alle Patch-Beispiele (Schritt einfügen, entfernen, Spannungsfeld, Ausnahme, Entscheidung, Schleife, Zusammenfassung) sind vorhanden und korrekt.
12. Alle 18 Tests in `test_structuring_mode.py` sind grün.

---

## 8. Aufwandsschätzung

| Feld | Wert |
|---|---|
| **Komplexität** | S (1 Datei, reiner Prompt-Rewrite, kein Code-/Teständerungen) |
| **Betroffene Dateien** | 1 |
| **Breaking Change** | Nein |

| Phase | Dateien | Komplexität |
|---|---|---|
| Prompt | `backend/prompts/structuring.md` | M (signifikanter Rewrite, aber nur Prompt) |
