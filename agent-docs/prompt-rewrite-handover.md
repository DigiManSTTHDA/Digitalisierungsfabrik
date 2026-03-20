# Prompt-Rewrite Handover

## Was wurde erreicht

### specification.md — komplett überarbeitet (Gold-Standard)

Der Spezifikations-Prompt (`backend/prompts/specification.md`) wurde von ~198 Zeilen auf 396 Zeilen grundlegend neu strukturiert und inhaltlich massiv erweitert. Vorher war der Prompt eine knappe Anweisungsliste ohne Kontext; jetzt ist er ein vollständiger, didaktisch aufgebauter System-Prompt.

**Neue Struktur (7 Abschnitte):**

1. **Mission** — Erklärt das Gesamtsystem, die 4 Phasen, wo der Nutzer steht, wer der Nutzer ist
2. **Terminologie** — Explizite Hierarchie: Strukturschritt → Algorithmusabschnitt → EMMA-Aktion
3. **Ziel + Rolle** — Arbeitsweise, Variablen dokumentieren, systematisch befragen, proaktiv handeln
4. **RPA Best Practices** — Tastatur vor Maus, FIND_AND_CLICK vs FIND+CLICK, Warten, Entscheidungen, Schleifen
5. **Output-Kontrakt** — Exaktes Format, Patch-Beispiele (inkl. analoge Schritte), phasenstatus-Definitionen
6. **Aktueller Status + Artefakte** — Platzhalter-Block (`{context_summary}`, `{structure_content}`, `{algorithm_status}`)
7. **Referenz** — Datenmodell, EMMA-Aktionskatalog mit reichen Detailbeschreibungen (19 Typen), Datenfluss, Parameter-Details

**Inhaltliche Schlüsselentscheidungen:**

- **Sokratische Hebammentechnik** als Interaktionsphilosophie beschrieben
- **Analoge Prozessschritte** werden als EMMA-Aktion mit `emma_kompatibel: false` dokumentiert (Patch-Beispiel "Analogen Schritt markieren")
- **Variablen** werden im `kontext`-Feld mit `[Variable] name (Typ) — Beschreibung. Quelle: ...` dokumentiert
- **EMMA DECISION** unterstützt beliebig viele Regeln (nicht nur 2), Catch-All Pflicht
- **Vorläufige EMMA-Aktionen** dürfen jederzeit verfeinert werden — nur Löschen ganzer Abschnitte braucht Rückfrage
- **`nutzervalidiert`** wird erst nach expliziter Nutzerbestätigung gesetzt
- **EMMA-Aktionskatalog** mit 3-5 Satz-Beschreibungen pro Aktionstyp fest eingebaut (statt dünner Auto-generierung)
- **Datenfluss zwischen Aktionen** erklärt (Gefundener Text, Koordinaten, Ergebnisstatus, Variablen)
- **Parameter-Details** für alle 19 Aktionstypen mit Pflichtfeldern dokumentiert

### Rewrite-Anleitung erstellt

`agent-docs/prompt-rewrite-instructions.md` — Generische Anleitung für Agents, die die anderen Prompts überarbeiten sollen. Enthält:
- Kontext über die Digitalisierungsfabrik
- 6 identifizierte Strukturprobleme der bestehenden Prompts
- 7-Abschnitt-Zielstruktur (Pflicht)
- Inhaltliche Regeln (Platzhalter beibehalten, Regeln konsolidieren, alles behalten)
- Checkliste

### EMMA-Katalog-Ausgabe dokumentiert

`agent-docs/emma-catalog-output.md` — Zeigt die Auto-generierte Ausgabe von `emma_action_catalog_text()`. Diese enthält nur dünne Einzeiler pro Aktionstyp und ist für die Spezifikationsphase **unzureichend**. Der Specification-Prompt enthält deshalb hardcodierte, reichhaltige Beschreibungen.

---

## Probleme, die wir fixen

### Alle 4 Mode-Prompts + Moderator haben dieselben Strukturprobleme:

1. **Kein Big Picture** — Kein Prompt erklärt, was die Digitalisierungsfabrik ist, wer der Nutzer ist, oder warum die Aufgabe wichtig ist
2. **Referenzdaten vor Auftrag** — Schemata und Platzhalter stehen vor den Arbeitsanweisungen
3. **Regeln verstreut** — Kritische Regeln in verschiedenen Sektionen ohne Prioritätsrahmen
4. **Output-Kontrakt als Afterthought** — Das Wichtigste (was soll der Output sein?) kommt am Ende
5. **Kein Beispiel für guten Output** — Das LLM bekommt nie gezeigt, wie ein guter Turn aussieht
6. **Redundanz** — Gleiche Regeln werden an mehreren Stellen unterschiedlich formuliert

### Spezifische Prompt-Probleme:

| Prompt | Datei | Zeilen | Hauptprobleme |
|--------|-------|--------|---------------|
| **Exploration** | `backend/prompts/exploration.md` | 118 | Kein Mission-Block, Output-Kontrakt am Ende, Extraktionsregeln gut aber unstrukturiert, Topic-Drift-Recovery ist eine gute Idee die beibehalten werden sollte |
| **Strukturierung** | `backend/prompts/structuring.md` | 250 | Kein Mission-Block, viele gute Patch-Beispiele (alle beibehalten!), Informationserhaltungspflicht gut formuliert, aber verstreute Regeln |
| **Validierung** | `backend/prompts/validation.md` | 51 | Extrem dünn — nur 51 Zeilen. Keine Erklärung was das System ist. Keine Beispiele für gute Validierungsberichte. Braucht massive Erweiterung |
| **Moderator** | `backend/prompts/moderator.md` | ~150 | ✅ **Überarbeitet.** Mission-Block, Terminologie, 5 Aktivierungsgründe mit Erkennungsmerkmalen, Steuerungslogik beibehalten und besser strukturiert, Best Practices, Alltagssprache-Beispiele für Phasenübergänge, konsolidierte Regeln. |

---

## Künftige TODOs

### Prio 1: Prompts rewriten

- [ ] `backend/prompts/exploration.md` — Rewrite nach Zielstruktur
- [ ] `backend/prompts/structuring.md` — Rewrite nach Zielstruktur
- [ ] `backend/prompts/validation.md` — Rewrite nach Zielstruktur (braucht am meisten Arbeit)
- [x] `backend/prompts/moderator.md` — Rewrite nach Zielstruktur

### Prio 2: Offene Architekturüberlegungen

- [ ] **`{emma_catalog}` Platzhalter eliminieren?** — Die Auto-generierte Liste aus `emma_action_catalog_text()` enthält nur Einzeiler. Im Specification-Prompt sind die reichhaltigen Beschreibungen jetzt hardcodiert. Soll der Platzhalter komplett entfernt werden? Oder soll die Funktion erweitert werden?
- [ ] **Variablen-Feld im Datenmodell?** — Aktuell werden Variablen nur als `[Variable]`-Marker im `kontext`-Feld dokumentiert. Sollte es ein eigenes `variablen`-Dict im Algorithmusabschnitt geben?
- [ ] **`dialog_history_n` anpassen?** — Default ist 3 Turns (in `backend/config.py`). Reicht das für die Spezifikationsphase, wo komplexe Diskussionen über einzelne Schritte geführt werden?

---

## Rewrite-Prompt für die nächsten Prompts

Der folgende Prompt kann direkt an einen Agent übergeben werden, um einen der verbleibenden Prompts zu überarbeiten. Ersetze `{PROMPT_DATEI}` und `{MODE_PY_DATEI}` mit dem jeweiligen Dateinamen.

---

### Agent-Prompt

```
Du sollst den System-Prompt `backend/prompts/{PROMPT_DATEI}` der Digitalisierungsfabrik grundlegend NEU SCHREIBEN.

Das ist KEINE Umstrukturierung. Die bestehenden Prompts enthalten viel zu wenig Information, damit das LLM sinnvoll arbeiten kann. Du musst den Prompt von Grund auf besser machen — mit neuem Inhalt, besserer Struktur, und nach bewährten Prompt-Engineering-Prinzipien.

## Vorbereitung (PFLICHT — erst lesen, dann schreiben)

Lies folgende Dateien in dieser Reihenfolge:

1. `backend/prompts/specification.md` — **GOLD-STANDARD.** Lies diesen Prompt KOMPLETT. Er zeigt den Ziel-Detailgrad, den Ton, die Struktur und die Inhaltsdichte. Dein Prompt muss auf diesem Niveau sein.
2. `agent-docs/prompt-rewrite-instructions.md` — Prompt-Engineering-Prinzipien, Zielstruktur, Domänenkontext, Checkliste.
3. `backend/prompts/{PROMPT_DATEI}` — Der bestehende Prompt. Nutze ihn als QUELLE für fachliche Details (Patch-Pfade, Feldnamen, Validierungsregeln) — aber NICHT als Struktur-Vorlage.
4. `backend/modes/{MODE_PY_DATEI}` — Die Python-Datei, die den Prompt lädt:
   - Welche Platzhalter programmatisch ersetzt werden (MÜSSEN exakt beibehalten werden)
   - Welche Kontextdaten der Mode dem Prompt mitgibt
   - Ob es Guardrails oder First-Turn-Direktiven im Code gibt
5. Exploriere das SDD und relevante Backend-Dateien, um die Phase und ihre Artefakte richtig zu verstehen.

## Was der Prompt leisten muss

Das LLM, das diesen Prompt erhält, muss OHNE weitere Hilfe:
- Verstehen, was die Digitalisierungsfabrik ist und wo dieser Modus reinpasst
- Wissen, wer der Nutzer ist und wie man mit ihm umgeht (sokratische Hebammentechnik)
- Genau wissen, was es in dieser Phase tun soll und wie es das tut
- Domänenspezifische Best Practices anwenden können
- Wissen, wie sein Output exakt aussehen muss (Patches, Formate, Feldnamen)
- Eigenständig entscheiden können, wann es Patches schreibt und wann es nur nachfragt

## 7-Abschnitt-Zielstruktur (PFLICHT)

1. **MISSION** — Was ist die Digitalisierungsfabrik? 4 Phasen. Wo stehst du? Was kam vorher, was kommt danach? Wer ist der Nutzer? Sokratische Hebammentechnik. (Orientiere dich am Mission-Block in specification.md.)
2. **TERMINOLOGIE** — Schlüsselbegriffe dieser Phase explizit definieren (was ist ein Slot / Strukturschritt / Algorithmusabschnitt / etc.)
3. **ROLLE + ARBEITSWEISE** — Was tust du konkret? Wie gehst du vor? Erstaktivierung, Schritt-für-Schritt, Dialogführung. Domänenspezifische Best Practices.
4. **OUTPUT-KONTRAKT** — Exaktes Format. Realistische (nicht abstrakte!) Patch-Beispiele. phasenstatus-Definitionen. Alle Patch-Beispiele aus dem Original übernehmen (ggf. verbessern).
5. **INITIALISIERUNG** — Was beim allerersten Turn passiert. "WARTE NICHT."
6. **AKTUELLER KONTEXT** — Platzhalter-Block. Alle Platzhalter aus der Python-Datei, exakt beibehalten.
7. **REFERENZMATERIAL** — Schemata, Datenmodelle, Kataloge als Appendix.

## Kritische Regeln

- **Genug Inhalt** — Der Prompt muss so viel Kontext und Anleitung enthalten, dass das LLM die Aufgabe SINNVOLL erfüllen kann. Lieber zu viel als zu wenig.
- **Konkret, nicht abstrakt** — Nicht "stelle gezielte Fragen", sondern WAS fragen. Nicht "erstelle Patches", sondern realistische Beispiele.
- **Platzhalter exakt beibehalten** — Sie werden programmatisch ersetzt. Prüfe in der Python-Datei.
- **Patch-Beispiele beibehalten und verbessern** — Alle aus dem Original übernehmen. Realistische Werte statt Platzhalter.
- **Artefakt = Langzeitgedächtnis** — Chat-Historie ist auf 3 Turns begrenzt. Alles Relevante MUSS ins Artefakt.
- **Sprache: Deutsch** — Gesamter Prompt-Inhalt auf Deutsch.
- **Ton: specification.md** — Direkt, klar, handlungsorientiert. Keine Floskeln, keine Wiederholungen.

## Checkliste (vor Abgabe prüfen)

- [ ] Mission-Block erklärt Gesamtsystem, Phase, Nutzer, Interaktionsphilosophie?
- [ ] Terminologie definiert Schlüsselbegriffe unmissverständlich?
- [ ] Output-Kontrakt steht VOR den Arbeitsregeln?
- [ ] Realistische, copy-paste-fähige Patch-Beispiele?
- [ ] Alle Platzhalter aus der Python-Datei exakt beibehalten?
- [ ] Domänenspezifische Best Practices enthalten?
- [ ] Arbeitsweise KONKRET beschrieben (nicht "stelle Fragen" sondern WAS fragen)?
- [ ] Hinweis auf begrenzten Chat-Kontext (Artefakt = Langzeitgedächtnis)?
- [ ] Kontext-Platzhalter stehen NACH dem Auftrag?
- [ ] Referenzmaterial steht am Ende?
- [ ] Sprache durchgängig Deutsch?
- [ ] Qualität auf Niveau von specification.md?
```

### Zuordnung Prompt → Python-Datei

| Prompt | Python-Mode |
|--------|-------------|
| `exploration.md` | `backend/modes/exploration.py` |
| `structuring.md` | `backend/modes/structuring.py` |
| `validation.md` | `backend/modes/validation.py` |
| `moderator.md` | `backend/modes/moderator.py` |

### Empfohlene Reihenfolge

1. **structuring.md** — Am meisten Substanz vorhanden (250 Zeilen, gute Patch-Beispiele). Nutzt dieselbe Artefakt-Logik wie Specification.
2. **exploration.md** — Gute Extraktionsregeln, Topic-Drift-Recovery. Anderes Artefakt (Slots statt Abschnitte).
3. **moderator.md** — Sondermodus ohne Artefakt-Schreibzugriff. Steuerungslogik beibehalten.
4. **validation.md** — Am dünnsten, braucht am meisten neue Inhalte. Zuletzt, weil man dann alle anderen Prompts als Kontext hat.
