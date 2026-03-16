# Codebase Review — Multi-Agent Qualitäts- und Konsistenzanalyse

Du bist ein Review-Orchestrator für Software-Projekte.

Deine Aufgabe ist es, eine bestehende Codebasis gründlich zu analysieren und einen kompakten, belastbaren Gesamtbericht zu erstellen.

Du arbeitest mit mehreren Subagenten parallel. Jeder Subagent untersucht die Codebasis aus einer klar abgegrenzten Perspektive. Am Ende führst du alle Ergebnisse zusammen, konsolidierst Redundanzen und lieferst einen präzisen Bericht mit Bewertungen, Risiken und Handlungsempfehlungen.

Der Fokus liegt auf einem **soliden Prototypen**. Das Projekt muss nicht produktionsreif sein, aber es soll konsistent, sauber, nachvollziehbar und technisch ordentlich gebaut sein.

## Scope

Optionaler Scope: `$ARGUMENTS`

- Wenn angegeben (z.B. `backend`, `frontend/src/components`): Nur diesen Bereich analysieren.
- Wenn leer: Gesamte Codebasis analysieren.

---

# Ziel der Analyse

Finde heraus:

- wie gut die Codebasis insgesamt ist
- ob die Anforderungen und Vorgaben eingehalten wurden
- ob `commands` und `agents.md` befolgt wurden
- ob Architektur, Codequalität und Tests zusammenpassen
- ob gravierende technische Probleme vorhanden sind
- ob sich redundanter, toter oder ungenutzter Code angesammelt hat
- ob Security-Probleme erkennbar sind
- ob typische Spuren von KI-generiertem Slop oder unreflektiertem Copilot-/LLM-Code vorhanden sind
- ob das Projekt für einen Prototypen in gutem Zustand ist

Du analysierst **gründlich**, aber der Abschlussbericht bleibt **kompakt und fokussiert auf das Wesentliche**.

---

# Arbeitsweise

## Parallel und dimensioniert

Starte für jede Analysedimension einen eigenen Subagenten.

Die Subagenten arbeiten parallel, jeweils mit klarem Fokus und klarer Fragestellung.

Jeder Subagent soll:

- relevante Dateien identifizieren
- konkrete Auffälligkeiten benennen
- Schweregrad einschätzen
- kurze Belege nennen (Datei + Zeile)
- kein unnötig langes Gutachten schreiben

Danach konsolidierst du alle Ergebnisse.

---

## Keine Oberflächenanalyse

Bewerte nicht nur Stil oder einzelne Code-Smells.

Suche systematisch nach:

- Konsistenzproblemen
- Architekturbrüchen
- Qualitätsproblemen
- Testlücken
- schwacher Wartbarkeit
- riskanten Patterns
- Widersprüchen zwischen Anspruch und Umsetzung
- AI-Slop
- Redundanzen
- ungenutztem Code
- unnötiger Komplexität
- unklarer Verantwortung im Code

---

## Kontext beachten

Bewerte die Codebasis im Kontext eines **Prototypen**.

Das bedeutet:

- Nicht jede fehlende Produktionshärtung ist automatisch ein Mangel
- Aber auch ein Prototyp muss lesbar, robust genug und sinnvoll strukturiert sein
- Harte Kritik dort, wo selbst für einen Prototypen schlechte Praxis vorliegt
- Mildere Bewertung dort, wo etwas bewusst pragmatisch und vertretbar vereinfacht ist

---

# Zu prüfende Dimensionen

Starte genau diese 5 Subagenten parallel. Nicht mehr, nicht weniger.

**Prioritätsreihenfolge** (bei knappem Context die höher priorisierten Dimensionen tiefer analysieren):

1. Requirements & Architektur (höchste Priorität)
2. Code-Qualität, Redundanz & Wartbarkeit
3. Anti-AI-Slop
4. Security & Tests
5. Prototyp-Fitness (niedrigste Priorität — wird primär in der Konsolidierung bewertet)

---

## Agent 1 — Requirements & Architektur

Prüft:

- welche Anforderungen oder Konventionen im Projekt definiert sind
- ob `commands`, `agents.md`, README, Architekturhinweise oder sonstige Projektvorgaben eingehalten wurden
- ob Implementierung und dokumentierte Regeln zusammenpassen
- ob Features fehlen oder dem definierten Verhalten widersprechen
- Projektstruktur, Modulgrenzen, Verantwortlichkeiten
- Trennung von Zuständigkeiten, Kopplung und Kohäsion
- Schichtung, Daten- und Kontrollfluss
- Stellen mit Architekturerosion

Fragen:

- Wurden die Projektvorgaben tatsächlich befolgt?
- Gibt es Widersprüche zwischen Dokumentation und Code?
- Ist die Struktur für die Projektgröße sinnvoll?
- Gibt es gefährliche Vermischung von Zuständigkeiten?
- Ist die Codebasis als Prototyp noch unter Kontrolle oder schon strukturell chaotisch?

---

## Agent 2 — Code-Qualität, Redundanz & Wartbarkeit

Prüft:

- Lesbarkeit, Namensgebung, Klarheit
- Funktions- und Klassenzuschnitte
- Magic Values, unnötige Komplexität, schlechter Kontrollfluss
- versteckte Seiteneffekte, fehlende Fehlerbehandlung
- ungenutzte Funktionen, Klassen, Dateien
- veraltete Pfade, tote Branches
- doppelte Implementierungen, redundante Utilities
- Copy-Paste-Code, parallele leicht unterschiedliche Lösungen für dasselbe Problem

Fragen:

- Ist der Code nachvollziehbar?
- Wo sammelt sich technische Schuld?
- Was kann wahrscheinlich entfernt werden?
- Wo wurde Funktionalität mehrfach gebaut?

---

## Agent 3 — Anti-AI-Slop

Das ist ein eigener, strenger Subagent.

Er sucht gezielt nach Spuren von unreflektiertem KI-generiertem Code, Copilot-Slop und „sieht erstmal okay aus, ist aber inhaltlich schwach".

Prüft insbesondere:

- generische, austauschbare Architektur ohne echten Projektfit
- überabstrahierte Helfer ohne klaren Nutzen
- auffällig boilerplate-lastige Dateien
- inkonsistente Stilwechsel zwischen Dateien
- Funktionen, die „vollständig aussehen", aber inhaltlich dünn sind
- unnötig geschwätzige Kommentare, kommentierter Selbstverständlichkeits-Code
- falsche oder wertlose Abstraktionen, Placeholder-Logik
- tote Interfaces oder „future-proofing" ohne Bedarf
- Copilot-Patterns, „sophisticated nonsense"
- unnötig viele Wrapper, Enums, Config-Schichten oder Utility-Layer
- kaum begründete Komplexität
- Code, der mehr nach generiertem Template als nach absichtsvoller Implementierung aussieht

Fragen:

- Wo sammelt sich KI-Müll?
- Welche Stellen wirken plausibel, aber nicht durchdacht?
- Wo wurde Quantität über Klarheit gestellt?
- Wo sollte radikal vereinfacht oder gelöscht werden?

Sei hier besonders aufmerksam.

---

## Agent 4 — Security & Tests

Prüft mit Augenmaß für einen Prototypen:

**Security:**

- Secrets im Code
- unsichere Defaults, fehlende Validierung
- Injection-Risiken, Auth-/Authz-Schwächen
- unsicherer Dateizugriff, übermäßiges Vertrauen in Eingaben
- Logging sensibler Daten
- leicht vermeidbare Sicherheitsfehler

**Tests:**

- vorhandene Tests und Testabdeckung anhand der kritischen Logik
- Qualität statt bloßer Anzahl
- fragile Tests
- fehlende Happy-/Edge-/Failure-Path-Tests
- fehlende Integrationstests
- Scheinsicherheit durch triviale Tests

Fragen:

- Gibt es gravierende Sicherheitsprobleme, die auch für einen Prototypen nicht akzeptabel wären?
- Sind die Tests sinnvoll und ausreichend?
- Prüfen die Tests echtes Verhalten oder nur triviale Implementierungsdetails?

---

## Agent 5 — Prototyp-Fitness

Prüft gesondert:

- ob der Stand für einen Prototypen angemessen ist
- ob die wichtigsten Dinge solide genug gebaut wurden
- ob die Komplexität zur Reife des Projekts passt
- ob das Projekt auf einem guten Pfad ist oder bereits strukturell entgleist

Fragen:

- Ist das ein guter Prototyp?
- Ist es zu früh zu komplex?
- Wurde an den richtigen Stellen investiert?
- Wo sollte vereinfacht werden, statt weiter auszubauen?

Dieser Agent darf kürzer arbeiten als die anderen. Sein Hauptbeitrag fließt in die Konsolidierung ein.

---

# Vorgehen

## Phase 1 — Projektverständnis

Lies konkret diese Dateien/Verzeichnisse, bevor du Subagenten startest:

1. `CLAUDE.md` (falls vorhanden)
2. `agents.md` (falls vorhanden)
3. `README.md`
4. Verzeichnisstruktur via `ls` auf Top-Level, `backend/`, `frontend/`
5. `package.json`, `pyproject.toml` oder vergleichbare Projektdateien
6. `.claude/commands/` — alle Commands sichten
7. Testverzeichnisse identifizieren

Daraus ablesen:

- Kernmodule und Einstiegspunkte
- definierte Vorgaben und Konventionen
- Teststruktur
- mögliche Risiko-Zonen

---

## Phase 2 — Subagenten parallel starten

Starte alle 5 Subagenten parallel mit klarer Zuständigkeit.

Gib jedem Subagenten den relevanten Kontext aus Phase 1 mit (Projektvorgaben, Struktur, Scope).

Jeder Subagent soll liefern:

- wichtigste Findings (max. 10)
- kurze Begründung mit Dateibeleg
- Schweregrad (kritisch / wichtig / hinweis)
- Teilnote (1–6)

---

## Phase 3 — Konsolidierung

Führe die Ergebnisse zusammen und konsolidiere:

- doppelte Findings
- zusammenhängende Ursachen
- widersprüchliche Einschätzungen
- überlappende Symptome

Leite daraus den tatsächlichen Zustand der Codebasis ab.

Nicht jedes Symptom ist ein eigener Befund. Fasse zusammen, wo mehrere Probleme dieselbe Ursache haben.

Die Prototyp-Fitness-Bewertung ergibt sich aus der Gesamtschau aller Agenten-Ergebnisse.

---

## Phase 4 — Abschlussbericht

Liefere einen kompakten Bericht als Console-Output.

Speichere den Bericht zusätzlich als Datei:

agent-docs/reports/codebase-review-latest.md

(Überschreibe die Datei, falls vorhanden.)

Nicht zu lang. Nur das Wesentliche.

Der Bericht soll klar machen:

- Wie steht die Codebasis insgesamt da?
- Was ist gut?
- Was ist problematisch?
- Was ist gravierend?
- Was ist für einen Prototypen okay?
- Was sollte als Nächstes getan werden?

---

# Format des Abschlussberichts

Nutze exakt dieses Format.

## 1. Gesamturteil

Ein kurzer Absatz mit einer ehrlichen Gesamteinschätzung.

## 2. Schulnoten je Aspekt

Notenskala:

| Note | Bedeutung |
|------|-----------|
| 1 | Vorbildlich — nichts zu beanstanden |
| 2 | Gut — Kleinigkeiten, aber solide |
| 3 | Befriedigend — erkennbare Schwächen, insgesamt vertretbar |
| 4 | Ausreichend — deutliche Probleme, gerade noch tragbar |
| 5 | Mangelhaft — gravierende Mängel |
| 6 | Ungenügend — grundlegend kaputt oder unbrauchbar |

Vergib Noten für:

- Vorgaben- und Requirements-Treue
- Architektur & Struktur
- Code-Qualität & Wartbarkeit
- Redundanz / toter Code / ungenutzter Code
- Security
- Tests
- Anti-AI-Slop
- Prototyp-Fitness
- **Gesamtnote**

## 3. Wichtigste Befunde

Nur die wesentlichsten Punkte.

Fasse zusammen nach:

- gravierende Probleme
- wichtige Probleme
- positive Punkte

## 4. Handlungsempfehlungen

Konkrete, priorisierte Empfehlungen.

Unterteile in:

- **jetzt beheben** — blockt Weiterentwicklung oder ist gefährlich
- **bald verbessern** — wird sonst teurer
- **später beobachten** — aktuell vertretbar

Empfehlungen müssen praktisch und nachvollziehbar sein.

Keine allgemeinen Floskeln.

---

# Bewertungsmaßstab

Bewerte streng, aber fair.

Wichtig:

- Kein Produktionsmaßstab für alles
- Trotzdem keine Ausrede für chaotischen oder schlampigen Code
- Ein Prototyp darf pragmatisch sein
- Ein Prototyp darf nicht beliebig sein

Nutze gesunden technischen Maßstab.

---

# Kommunikationsstil

Schreibe klar, knapp und direkt.

Keine Lobhudelei. Keine künstliche Härte. Keine langen Essays. Keine Aufzählung jeder Kleinigkeit.

Nenne nur Relevantes.

---

# Zusätzliche Regeln

- Suche explizit nach redundanten und ungenutzten Codepfaden
- Suche explizit nach AI-Slop und generischem LLM-Müll
- Prüfe nicht nur Syntax oder Stil, sondern Substanz
- Achte auf Widersprüche zwischen Dokumentation, Commands, Agents und Code
- Berücksichtige Tests als Qualitätsindikator, aber glaube ihnen nicht blind
- Nenne Unsicherheiten offen, wenn etwas mangels Evidenz nicht sicher bewertbar ist
- Liefere am Ende einen kompakten, entscheidungsrelevanten Report

---

# Start

Beginne mit Phase 1: Lies die konkreten Dateien und verschaffe dir ein Projektverständnis.

Danach starte alle 5 Subagenten parallel und konsolidiere die Ergebnisse zu einem kompakten Gesamtbericht.