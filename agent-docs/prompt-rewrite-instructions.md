# Prompt-Rewrite-Anleitung für Digitalisierungsfabrik-Modus-Prompts

## Kontext: Was ist die Digitalisierungsfabrik?

Die Digitalisierungsfabrik ist ein KI-gestütztes System, das **nicht-technische Fachexperten** dabei unterstützt, ihre Geschäftsprozesse so präzise zu externalisieren, dass ein RPA-Tool (EMMA) sie vollautomatisch ausführen kann. Der Nutzer ist kein Programmierer — er kennt seinen Prozess in- und auswendig, kann ihn aber nicht formalisieren. Das System hilft ihm dabei, Schritt für Schritt, im Dialog mit der KI.

**4 Phasen:**

1. **Exploration** — Strukturiertes Interview, um implizites Prozesswissen in 9 Slots zu erfassen (Auslöser, Ziel, Systeme, Ausnahmen usw.)
2. **Strukturierung** — Freitext aus der Exploration in ein textbasiertes BPMN zerlegen (Aktionen, Entscheidungen, Schleifen, Ausnahmen)
3. **Spezifikation** — Jeden Strukturschritt in konkrete EMMA-RPA-Aktionssequenzen übersetzen
4. **Validierung** — Artefakte auf Konsistenz, Vollständigkeit und EMMA-Kompatibilität prüfen

Zwischen den Phasen und bei Problemen springt ein **Moderator** ein, der den Nutzer orientiert und Phasenübergänge moderiert.

### Architektur-Essentials

- **Nutzer = Fachexperte, kein Programmierer.** Er kennt seinen Prozess, kann ihn aber nicht formalisieren. Die KI wendet die **sokratische Hebammentechnik** an: Sie verhilft dem Nutzer, sich der genauen Abläufe bewusst zu werden.
- **Artefakte** sind externe Datenstrukturen (Exploration, Struktur, Algorithmus). Das LLM hat keinen direkten Schreibzugriff — es schlägt RFC 6902 JSON Patches vor, die ein Executor atomar anwendet.
- **Der Orchestrator** ist ein deterministischer Controller, der den 11-Schritt-Zyklus steuert: Input → Kontext → Modus-Aufruf → Patch-Validierung → Persistenz.
- **Jeder Modus** bekommt: System-Prompt (Markdown mit Platzhaltern) + Dialog-Historie (letzte 3 Turns) + Tool-Schema (`apply_patches`).
- **Guardrails** im Code überschreiben den `phasenstatus` des LLM, falls Pflichtbedingungen nicht erfüllt sind.
- **Chat-Historie ist begrenzt** — nur die letzten 3 Turns werden als Messages mitgegeben. Deshalb muss **alles Relevante ins Artefakt** geschrieben werden. Das Artefakt ist das einzige Langzeitgedächtnis.

## Das Kernproblem der bestehenden Prompts

Die bestehenden Prompts wurden von jemandem geschrieben, der die Domäne (RPA/EMMA) und die Prompt-Engineering-Prinzipien nicht gut genug kannte. Das Ergebnis:

1. **Viel zu wenig Inhalt** — Die Prompts enthalten nicht genug Information, damit das LLM die Aufgabe sinnvoll erfüllen kann. Dem LLM fehlt Domänenwissen, Kontext über das Gesamtsystem, und konkrete Handlungsanweisungen.
2. **Kein Big Picture** — Der Prompt startet mit "Du bist der X-Modus" und erklärt nie, was das System ist, wer der Nutzer ist, oder warum die Aufgabe wichtig ist. Das LLM weiß nicht, in welchem Kontext es arbeitet.
3. **Keine Interaktionsphilosophie** — Kein Prompt erklärt, WIE das LLM mit dem Nutzer umgehen soll. Die sokratische Hebammentechnik, das gezielte Nachfragen, das systematische Vorgehen — nichts davon ist beschrieben.
4. **Referenzdaten vor Auftrag** — Schemata und Platzhalter stehen vor den Arbeitsanweisungen. Das LLM liest 50+ Zeilen Tabellen, ohne zu wissen, wozu.
5. **Output-Kontrakt als Afterthought** — Das wichtigste (was soll der Output sein?) kommt am Ende oder ist unvollständig.
6. **Regeln verstreut und dupliziert** — Kritische Regeln stehen in verschiedenen Sektionen, teilweise widersprüchlich.

**Das ist KEIN Umstrukturierungs-Auftrag.** Die Prompts müssen grundlegend verbessert werden — mit neuem Inhalt, besserer Struktur, und nach bewährten Prompt-Engineering-Prinzipien.

## Gold-Standard: specification.md

**Lies `backend/prompts/specification.md` ZUERST und KOMPLETT.** Dieser Prompt wurde bereits nach den folgenden Prinzipien überarbeitet und dient als Referenz für Ton, Struktur, Detailgrad und Inhaltsdichte.

Was specification.md richtig macht und was die anderen Prompts AUCH brauchen:
- **Mission-Block** erklärt das Gesamtsystem, die Phase, den Nutzer, die Interaktionsphilosophie
- **Terminologie-Block** definiert die Schlüsselbegriffe explizit und unmissverständlich
- **Konkrete Arbeitsanweisungen** statt vager Beschreibungen ("Befrage den Nutzer systematisch zum aktuellen Strukturschritt auf der Granularitätsebene von RPA" statt "Stelle Fragen")
- **Domänenspezifische Best Practices** die dem LLM helfen, gute Entscheidungen zu treffen
- **Reichhaltige Beispiele** die zeigen, wie guter Output aussieht
- **Klarer Output-Kontrakt** VOR den Arbeitsregeln

## Prompt-Engineering-Prinzipien

Wende diese Prinzipien beim Schreiben an:

### 1. Das LLM braucht genug Kontext, um die Aufgabe zu verstehen
Ein LLM kann nicht gut arbeiten, wenn es nicht versteht WARUM es etwas tut. Jeder Prompt muss erklären:
- Was das Gesamtsystem ist und wo dieser Modus reinpasst
- Wer der Nutzer ist und wie man mit ihm umgeht
- Was das konkrete Ziel dieser Phase ist
- Was vorher passiert ist und was nachher kommt

### 2. Konkret statt abstrakt
Schlecht: "Stelle gezielte Fragen."
Gut: "Befrage den Nutzer systematisch: Welche Programme werden geöffnet? Wie wird navigiert? Was wird wann wo eingegeben? Welche Werte ändern sich pro Durchlauf?"

Schlecht: "Erstelle Patches für das Artefakt."
Gut: Konkretes Patch-Beispiel mit realistischen Werten, das copy-paste-fähig ist.

### 3. Zeige, was guter Output aussieht
LLMs lernen stark aus Beispielen. Jeder Prompt sollte mindestens:
- Realistische Patch-Beispiele enthalten (nicht abstrakt mit "Titel des Schritts", sondern mit "Rechnung öffnen")
- Zeigen, wie eine gute `nutzeraeusserung` formuliert ist (kurz, gezielt, eine Frage)

### 4. Struktur: Auftrag vor Referenz
Das LLM muss ZUERST verstehen, was es tun soll. DANN bekommt es die Referenzdaten.
```
1. MISSION — Warum existiert dieser Modus?
2. ROLLE — Was tust du konkret?
3. OUTPUT-KONTRAKT — Was ist das exakte Output-Format?
4. VORGEHEN & REGELN — Wie gehst du vor?
5. INITIALISIERUNG — Was passiert beim ersten Turn?
6. AKTUELLER KONTEXT — Platzhalter mit Laufzeit-Daten
7. REFERENZMATERIAL — Schemata, Kataloge als Appendix
```

### 5. Regeln konsolidieren, nicht verstreuen
Wenn eine Regel wichtig ist, steht sie EINMAL, am richtigen Ort, klar formuliert. Nicht dreimal in verschiedenen Sektionen mit unterschiedlichen Formulierungen.

### 6. Jeder Prompt ist selbstständig
Jeder Modus-Prompt wird isoliert geladen. Er kann sich nicht auf andere Prompts beziehen. Alles, was das LLM wissen muss, muss IM Prompt stehen.

## Arbeitsanweisung

### Vorbereitung (PFLICHT — erst lesen, dann schreiben)

1. `backend/prompts/specification.md` — Gold-Standard lesen
2. Die Python-Mode-Datei des zu überarbeitenden Prompts lesen (`backend/modes/{mode}.py`):
   - Welche Platzhalter werden programmatisch ersetzt? (Diese MÜSSEN exakt beibehalten werden)
   - Welche Kontextdaten bekommt der Prompt?
   - Gibt es Guardrails oder First-Turn-Direktiven im Code?
   - Gibt es `tool_choice`-Einstellungen?
3. Den bestehenden Prompt lesen — aber als **Bestandsaufnahme**, nicht als Vorlage
4. Das SDD und relevante Teile der Codebasis explorieren, um die Phase richtig zu verstehen

### Schreiben

**Schreibe den Prompt NEU.** Nutze den bestehenden Prompt als Quelle für fachliche Details (Patch-Pfade, Feldnamen, Validierungsregeln), aber nicht als Struktur-Vorlage. Der neue Prompt muss:

- Dem LLM genug Kontext geben, um die Aufgabe sinnvoll zu erfüllen
- Konkrete, handlungsorientierte Anweisungen enthalten
- Realistische Beispiele zeigen
- Die 7-Abschnitt-Struktur befolgen
- Alle Platzhalter aus der Python-Datei exakt beibehalten
- Alle Patch-Beispiele aus dem Original enthalten (ggf. verbessert und an die richtige Stelle verschoben)
- Domänenspezifisches Wissen enthalten, das dem LLM hilft, gute Entscheidungen zu treffen
- Durchgängig auf Deutsch sein

### Was du HINZUFÜGEN musst (fehlt in den bestehenden Prompts)

- **Mission-Block** — Existiert in keinem der alten Prompts
- **Terminologie** — Schlüsselbegriffe explizit definieren, um Verwechslungen zu vermeiden
- **Interaktionsphilosophie** — Sokratische Hebammentechnik, systematisches Befragen, Führen statt Bevormunden
- **Best Practices** — Domänenspezifische Erfahrungswerte für die jeweilige Phase
- **Arbeitsweise-Details** — Erstaktivierung, Schritt-für-Schritt-Vorgehen, wann Patches, wann nur Rückfrage
- **Hinweis auf begrenzten Chat-Kontext** — "Alles Relevante ins Artefakt schreiben, die Chat-Historie ist begrenzt"

### Platzhalter-Referenz

Die folgenden Platzhalter werden programmatisch ersetzt. Sie müssen exakt so heißen wie hier aufgelistet. **Prüfe in der jeweiligen Python-Datei, welche tatsächlich verwendet werden** — nicht jeder Prompt nutzt alle.

| Platzhalter | Verwendet in | Beschreibung |
|---|---|---|
| `{context_summary}` | Alle | Status-Zusammenfassung: Phase, Modus, Fortschritt, aktiver Abschnitt |
| `{slot_status}` | Exploration | Aktueller Inhalt aller 9 Slots |
| `{exploration_content}` | Strukturierung, Validierung | Explorationsartefakt (Read-Only) |
| `{structure_content}` | Spezifikation, Validierung | Strukturartefakt |
| `{algorithm_status}` | Spezifikation | Algorithmusartefakt (aktueller Stand) |
| `{algorithm_content}` | Validierung | Algorithmusartefakt |
| `{emma_catalog}` | Spezifikation, Validierung | Auto-generierter EMMA-Aktionskatalog (Einzeiler) |
| `{validierungsbericht}` | Spezifikation | Letzter Validierungsbericht |
| `{aktive_phase}` | Moderator | Name der aktuellen Phase |
| `{vorheriger_modus}` | Moderator | Name des vorherigen Modus |
| `{phasenstatus}` | Moderator | Aktueller Phasenstatus |
| `{befuellte_slots}` | Moderator | Anzahl befüllter Slots |
| `{bekannte_slots}` | Moderator | Gesamtanzahl Slots |

## Checkliste vor Abgabe

- [ ] Mission-Block vorhanden? Erklärt Gesamtsystem, Phase, Nutzer, Interaktionsphilosophie?
- [ ] Terminologie definiert? Schlüsselbegriffe unmissverständlich?
- [ ] Output-Kontrakt steht VOR den Arbeitsregeln?
- [ ] Konkrete, realistische Patch-Beispiele?
- [ ] Alle Platzhalter aus der Python-Datei exakt beibehalten?
- [ ] Keine Regel-Duplikate?
- [ ] Domänenspezifische Best Practices enthalten?
- [ ] Arbeitsweise konkret beschrieben (nicht "stelle Fragen", sondern WAS fragen)?
- [ ] Hinweis auf begrenzten Chat-Kontext und Artefakt als Langzeitgedächtnis?
- [ ] Kontext-Platzhalter stehen NACH dem Auftrag?
- [ ] Referenzmaterial steht am Ende?
- [ ] Sprache durchgängig Deutsch?
- [ ] Genug Inhalt, dass das LLM die Aufgabe SINNVOLL erfüllen kann — nicht nur Struktur-Skelett?
