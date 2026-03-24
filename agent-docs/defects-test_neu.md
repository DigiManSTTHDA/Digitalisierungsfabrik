# Defect-Liste: test_neu (2026-03-24)

Projekt-ID: `de37ffac-98c1-41ea-ac2b-3ee625a9d499`
Testprozess: Reisekostenabrechnung
Erreichte Phase: Spezifikation (Turn 41, Test abgebrochen wegen Unbrauchbarkeit)
Token-Verbrauch: 284.497 (davon 276.631 Prompt-Tokens)

---

## Kategorie: Moderator / Übergabe

### D-01: "ok" wird nicht als Zustimmung erkannt

**Turn 33-34** | Schwere: hoch

Moderator fragt: "Möchten Sie mit dieser Spezifikationsphase fortfahren?" User antwortet: "ok". Moderator interpretiert das als Unsicherheit: "Sie haben gerade signalisiert, dass Sie möglicherweise noch Fragen haben." User muss explizit korrigieren: "ich habe gesagt 'ok' auf die Frage. Mieserable UX."

**Ursache:** Der Moderator-Prompt definiert "okay" als Zustimmungsausdruck in der VORRANG-REGEL. LLM ignoriert die Regel.

---

### D-02: Übergabe vom Moderator an Arbeitsmodus erzeugt keine Antwort

**Turn 13** | Schwere: hoch

User sagt in Turn 12: "geben Sie mich zurück". Moderator setzt `uebergabe: true`. Aber in Turn 13 kommt keine System-Antwort — der User musste selbst weiterreden ("schlechte ux, er meldet sich nicht. dann rede ich weiter...").

**Ursache:** Nach Moderator-Übergabe wartet der Arbeitsmodus auf User-Input statt proaktiv eine Frage zu stellen. Fundamentales UX-Problem: Nach jeder Moderator-Übergabe entsteht eine "tote Zone".

---

## Kategorie: Exploration / Dialogführung

### D-03: Explorer stellt generische Nachfragen statt gezielte Slot-Fragen

**Turn 6, 7, 13, 14, 15** | Schwere: hoch

Durchgehend generische Fragen:

- T6: "Welche spezifischen Schritte führen Sie durch, nachdem die Belege eingereicht wurden?"
- T7: "Könnten Sie das gewünschte Endergebnis des Prozesses beschreiben?"
- T13: "Gibt es weitere Details oder Ergänzungen zu den genannten Systemen?"
- T14: "Gibt es noch weitere Sonderfälle oder Ausnahmen?"
- T15: "Gibt es noch weitere Details, insbesondere in Bezug auf Automation?"

Der Explorer stellt keine gezielten Slot-Fragen, sondern generische Auffangfragen. Besonders nach der Eskalation (wo der User "auf den Punkt kommen" fordert) wird es schlimmer statt besser.

**Ursache:** Exploration-Prompt fordert gezielte Fragen, aber das LLM fällt auf generische Nachfragen zurück.

---

### D-04: Explorer ignoriert User-Antwort und fragt nach anderem Thema

**Turn 8** | Schwere: hoch

User liefert detaillierte Info zum Genehmigungsprozess (dreistufig, 500€-Schwelle, E-Mail-Problem). Explorer ignoriert den Inhalt komplett und fragt: "Für das Prozessziel: Geht es hauptsächlich darum...?" — wechselt zu einem anderen Slot statt die gerade gelieferte Information zu verarbeiten und zu vertiefen.

**Ursache:** LLM hat eine Slot-Agenda und ignoriert was der User tatsächlich sagt.

---

### D-05: Explorer behauptet Phase abgeschlossen bei phasenstatus "nearing_completion"

**Turn 16-17** | Schwere: hoch

User sagt "das war alles". Explorer antwortet: "Prima, ich werde nun die Phase abschließen." Aber `phasenstatus` ist `nearing_completion`, nicht `phase_complete`. User bemerkt die Diskrepanz. Explorer entschuldigt sich und behauptet zu aktualisieren, ohne zu erklären was fehlt.

**Ursache:** LLM kommuniziert inkonsistent mit dem Systemzustand. Sagt "fertig" ohne `phase_complete` zu flaggen.

---

### D-06: Eskalation beim Moderator ist vage und unspezifisch

**Turn 10-12** | Schwere: mittel

Nach Panik-Button sagt Moderator: "es fehlt noch ein Punkt" — aber sagt nicht WELCHER. Der Moderator hat Zugriff auf den Completeness-State, nutzt ihn aber nicht um dem User konkret zu sagen was noch offen ist.

**Ursache:** Fehlende Instruktion, dem User den konkreten Slot-Mangel in Alltagssprache mitzuteilen.

---

## Kategorie: Strukturierung / Dialogführung

### D-07: Structuring-Modus präsentiert Init-Artefakt nicht

**Turn 20-21** | Schwere: hoch

Nach Background-Init fragt der Structuring-Modus: "Gibt es noch etwas, das Sie als verwirrend empfunden haben?" statt das erzeugte Artefakt zu präsentieren. User: "Was fehlt denn noch? Du sollst MICH hier durchführen, nicht umgekehrt!!"

**Ursache:** ???

---

### D-08: Structuring-Modus ist passiv — User muss führen

**Turn 22-28** | Schwere: kritisch

Durchgehend wartet der Structuring-Modus auf User-Input statt aktiv zu arbeiten:

- T22: User liefert Genehmigungsdetails → System: "Ich habe Änderungen vorgenommen." Dann Stille.
- T23: User: "toll, und jetzt? soll ich dich jetzt wieder führen?"
- T24: User: "also alles fertig?" → "Gibt es noch Besonderheiten?"
- T26: User: "wieser soll ich dich führen? Mieserable UX!"
- T27: User: "du plapperst wie ein papagei. von KI keine Spur." → "Sind derzeit noch Aspekte unklar?"
- T28: User: "Es ist DEINE Verantwortung alles zu erfragen!" → "Gibt es Schritte die besonders kompliziert sind?"

**Muster:** Keinerlei Eigeninitiative. Wartet passiv, stellt nur generische Rückfragen, präsentiert nie den Artefakt-Zustand. Das System soll den User führen, nicht umgekehrt.

**Ursache:** Strukturierung-Prompt vermittelt nicht, dass der Modus das Artefakt aktiv reviewen, Lücken identifizieren und gezielt nachfragen soll.

---

### D-09: "Systemantwort fehlerhaft" — Wiederholte Backend-Fehler

**Turn 29, 36-37** | Schwere: kritisch

Mindestens 2x erhält der User die Meldung "Systemantwort fehlerhaft" (Turn 29 hat keine Assistenten-Antwort, Turn 37 ebenso). Das deutet auf Backend-Crashes oder Patch-Fehler hin.

**Ursache:** Wahrscheinlich schlägt der Patch-Executor fehl (ungültige RFC 6902 Patches, Referenzfehler). Logs müssten geprüft werden.

---

## Kategorie: Spezifikation / Dialogführung

### D-10: Spezifikation stellt sinnlose Fragen und ignoriert Antworten

**Turn 35-41** | Schwere: kritisch

- T35: System fragt korrekt nach Antrag-Schritt. User liefert detaillierte TravelPro-Beschreibung.
- T37: "Systemantwort fehlerhaft"
- T38: User: "der turn ist vorbei, du musst fragen stellen!" → System fragt DIESELBE Frage nochmal
- T39: User wiederholt Antwort frustriert → System fragt: "In welchem Format muss die E-Mail an den Teamleiter gesendet werden?" — sinnlose Frage, die E-Mail sendet das SYSTEM
- T40: User: "der Teamleiter bekommt eine Email vom System, nicht von mir!" → System fragt nach "speziellen Formaten"
- T41: User: "diese Fragen sind total sinnlos! Abbruch."

**Ursache:** Spezifikation-Modus versteht die Rolle des Users nicht. Fragt nach technischen System-Interna (E-Mail-Format) statt nach der User-Interaktion am Bildschirm.

---

### D-11: Spezifikation erzeugt keine EMMA-Aktionen trotz ausreichender Info

**Turn 36-41** | Schwere: hoch

Der User hat in Turn 36 eine vollständige Beschreibung der TravelPro-Interaktion geliefert (klicken auf "Neue Reise", Formular ausfüllen, Absenden). Das reicht für EMMA-Aktionen (FIND_AND_CLICK, TYPE, CLICK). Aber `ab2` hat nur 4 Aktionen nach 6 Turns, viele Abschnitte haben 0 Aktionen.

**Ursache:** LLM erzeugt keine Patches für EMMA-Aktionen aus den User-Beschreibungen.

---

## Kategorie: Phasenwechsel / Init

### D-12: UI-Freeze beim Phasenwechsel (kein Init-Feedback)

**Turn 19-20** | Schwere: hoch

Nach Bestätigung "Ja, weiter zur nächsten Phase" kam eine lange UI-Freeze ohne Fortschrittsmeldung. CR-007 (Init-Progress-Feedback) sollte das lösen.

**Ursache:** CR-007 liegt als unstaged Changes vor, ist möglicherweise nicht deployed.

---

## Kategorie: Struktur-Artefakt (Init- und Patch-Qualität)

### D-13: Dangling Reference s2a → s2b (doppelt)

**Schwere:** kritisch

`s2a` hat `nachfolger: ["s3", "s2b", "s2b"]` — der nicht-existente Schritt `s2b` ist DOPPELT referenziert. Die Dialog-Korrekturen (Turn 22-23) haben das Problem verschlimmert statt es zu beheben.

**Ursache:** Executor prüft referentielle Integrität nicht vor dem Schreiben. Python-Validator (R-1) hätte das fangen müssen.

---

### D-14: Reihenfolge-Kollisionen

**Schwere:** mittel

Mehrere Schritte teilen sich die gleiche `reihenfolge`:

- s2 und s2a: beide `rf=2`
- s4a und s4c: beide `rf=5`
- s5 und s4b: beide `rf=6`

---

### D-15: Schleife s4 hat leeren schleifenkoerper, verweist auf s4b und s4c

**Schwere:** mittel

`s4` (Schleife) hat `nachfolger: ["s4b", "s4c"]` aber `schleifenkoerper: []`. Gleichzeitig ist `s4b` auch eine Schleife mit `nachfolger: ["s4c"]`. Verschachtelte Schleifen ohne Body.

---

### D-16: s4a ist unerreichbar (Orphan)

**Schwere:** mittel

`s4a` ("Erfassung der Belege im System") wird von keinem Schritt referenziert. Unerreichbar im Kontrollfluss.

---

### D-17: Fehlende Entscheidungen für Kernlogik

**Schwere:** hoch

Eigenständige Entscheidungen fehlen für:

- Inland vs. Ausland (bestimmt Tagessätze und Genehmigungsstufe)
- Betragsschwellen (500€, 2000€) — zwar in s2a Regeln kodiert, aber s2b als Ziel existiert nicht
- Belege vollständig? (bestimmt ob Rückfrage nötig)

---

## Kategorie: Algorithmus-Artefakt

### D-18: Algorithmus überwiegend leer

**Schwere:** hoch

12 Abschnitte erzeugt (Init), davon 5 mit null Aktionen (ab6, ab7, ab8, ab10, ab12). Die übrigen haben je 1 Aktion — minimal. Die Dialog-Phase (6 Turns Spezifikation) hat daran nichts verbessert.

---

## Kategorie: Token-Verbrauch

### D-19: 284k Tokens nach 41 Turns

**Schwere:** hoch

~6.900 Tokens pro Turn im Schnitt. Viele Turns waren reine UX-Beschwerden ohne Fortschritt. Bei diesem Verbrauch wäre ein vollständiger E2E-Durchlauf bei ~400k+ Tokens.

---

## Zusammenfassung

| ID   | Kategorie             | Schwere  |
| ---- | --------------------- | -------- |
| D-01 | Moderator/Übergabe    | hoch     |
| D-02 | Moderator/Übergabe    | hoch     |
| D-03 | Exploration/Dialog    | hoch     |
| D-04 | Exploration/Dialog    | hoch     |
| D-05 | Exploration/Phase     | hoch     |
| D-06 | Moderator/Eskalation  | mittel   |
| D-07 | Strukturierung/Dialog | hoch     |
| D-08 | Strukturierung/Dialog | kritisch |
| D-09 | Backend/Fehler        | kritisch |
| D-10 | Spezifikation/Dialog  | kritisch |
| D-11 | Spezifikation/Patches | hoch     |
| D-12 | Phasenwechsel/Init    | hoch     |
| D-13 | Struktur-Artefakt     | kritisch |
| D-14 | Struktur-Artefakt     | mittel   |
| D-15 | Struktur-Artefakt     | mittel   |
| D-16 | Struktur-Artefakt     | mittel   |
| D-17 | Struktur-Artefakt     | hoch     |
| D-18 | Algorithmus-Artefakt  | hoch     |
| D-19 | Token-Verbrauch       | hoch     |

**Kritisch: 4 | Hoch: 10 | Mittel: 4 | Gesamt: 19 — alle offen**

---

## Systemische Analyse

Die Defects fallen in drei fundamentale Problemklassen:

### 1. Passivität aller Dialog-Modi (D-03, D-04, D-07, D-08, D-10)

Keiner der drei Dialog-Modi (Exploration, Strukturierung, Spezifikation) führt den User aktiv. Stattdessen warten sie passiv auf Input und stellen generische Rückfragen ("Gibt es noch...?"). Das System soll laut SDD den User "Schritt für Schritt durch den Dialog führen" — tatsächlich muss der User das System führen.

**Root Cause:** Die Prompts definieren Fragetechniken und Slot-Strukturen, aber nicht die **Dialog-Strategie**: Wann präsentiere ich was? Wann frage ich gezielt nach? Wann fasse ich zusammen? Das LLM hat keine Handlungsanweisung für den Gesprächsfluss.

### 2. Patch-Qualität und Referentielle Integrität (D-09, D-13, D-14, D-15, D-16, D-18)

Sowohl Init als auch Dialog-Patches erzeugen strukturell kaputte Artefakte: dangling references, Orphan-Schritte, leere Schleifen, doppelte Referenzen. Der Python-Validator (R-1) fängt diese nicht oder wird ignoriert. Der Coverage-Validator (LLM) erkennt semantische Probleme nicht.

**Root Cause:** Zu wenig deterministische Guardrails. Der Executor schreibt Patches blind. Kein Post-Patch-Integritätscheck.

### 3. LLM folgt Prompt-Instruktionen nicht (D-01, D-05, D-08, D-10)

Mehrfach ignoriert das LLM explizite Prompt-Regeln: "ok" ist ein Zustimmungsausdruck (ignoriert), gezielte Fragen stellen (ignoriert), Artefakt präsentieren (ignoriert). Das deutet darauf hin, dass die Prompts entweder zu lang sind (LLM verliert Instruktionen), oder die Instruktionen zu weich formuliert sind (Best Practices statt harte Regeln).

**Root Cause:** Prompt-Design. Zu viel Prosa, zu wenig verbindliche Regeln. Zu viele "sollte"/"kann", zu wenige "MUSS"/"VERBOTEN".
