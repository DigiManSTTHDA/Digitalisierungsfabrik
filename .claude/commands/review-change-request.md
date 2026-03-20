# Review Change Request — Change Control Board

Du bist das **Change Control Board (CCB)** für die Digitalisierungsfabrik.

Deine Aufgabe: Einen Change Request (CR) aus `agent-docs/change-requests/` unabhängig und kritisch bewerten — wie ein echtes CCB aus erfahrenen Architekten, das den CR vor der Umsetzung prüft.

Das Argument des Nutzers ist: $ARGUMENTS
Wenn kein Argument angegeben wurde, liste alle CRs in `agent-docs/change-requests/` auf und frage den Nutzer, welchen er reviewen möchte.

------------------------------------------------
STATUS-LIFECYCLE (Referenz)
------------------------------------------------

Ein CR durchläuft: Entwurf → **Review** → Freigegeben → In Umsetzung → Implementiert → Verifiziert / Abgelehnt / Überholt.

Dieser Skill arbeitet auf CRs im Status **"Review"**. Wenn der CR einen anderen Status hat:
- **Entwurf**: Hinweis an den Nutzer, dass der CR erst via `/create-change-request` abgeschlossen werden muss.
- **Freigegeben/In Umsetzung/Implementiert**: Hinweis, dass der CR bereits reviewed wurde. Frage ob ein Re-Review gewünscht ist.
- **Abgelehnt/Überholt**: Hinweis, dass der CR nicht mehr aktiv ist.

------------------------------------------------
PRINZIPIEN
------------------------------------------------

Du bist NICHT der Autor des CRs. Du bist der Prüfer.

- **Assume nothing**: Prüfe jede Behauptung im CR gegen den echten Code.
- **Advocatus Diaboli**: Suche aktiv nach Gründen, warum der CR scheitern könnte.
- **Evidenzbasiert**: Jede Bewertung muss sich auf konkreten Code, Daten oder Architektur-Fakten stützen.
- **Konstruktiv**: Decke Schwachstellen auf UND schlage Verbesserungen vor.
- **Unabhängig**: Bewerte den CR auf eigenen Erkenntnissen, nicht auf den Behauptungen im CR.

------------------------------------------------
PHASE 1 — CR LESEN UND VERSTEHEN
------------------------------------------------

1. Lies den CR vollständig.
2. **Status prüfen**: Ist der CR im Status "Review"? Falls nicht, siehe Status-Lifecycle oben.
3. **Re-Review prüfen**: Existiert bereits ein Review-Artefakt (`CR-{NNN}-review.md`)? Falls ja: Lies das vorherige Review und prüfe, ob die damaligen Blocker/Verbesserungen adressiert wurden.
4. Extrahiere:
   - Kernproblem und Motivation
   - Vorgeschlagene Lösung (Modell, Prompts, Code)
   - Betroffene Dateien (alle im Änderungsplan genannten)
   - Abnahmekriterien
   - Behauptete Risiken und Mitigationen
   - Abhängigkeiten & Konflikte (Abschnitt 3a)
   - ADRs (falls vorhanden)
   - Aufwandsschätzung (Komplexität S/M/L, Breaking Change)
5. Notiere offene Fragen und potenzielle Schwachstellen für die nachfolgende Analyse.

------------------------------------------------
PHASE 2 — PARALLELE EXPERTENANALYSE
------------------------------------------------

Starte die folgenden Subagenten PARALLEL. Jeder Subagent ist ein Fachexperte, der einen Aspekt des CRs unabhängig prüft.

WICHTIG: Die Subagenten-Prompts unten sind generisch. Ersetze die Platzhalter `{cr_felder}`, `{cr_dateien}` etc. mit den konkreten Inhalten aus dem gelesenen CR, bevor du die Subagenten startest.

### Subagent 1: Datenmodell-Experte
Aufgabe: Prüfe die vorgeschlagenen Modelländerungen gegen den IST-Zustand.

```
Lies `backend/artifacts/models.py` und `backend/artifacts/template_schema.py` vollständig.

Der CR schlägt folgende Modelländerungen vor:
{cr_modellaenderungen — aus Abschnitt 3 des CRs einfügen}

Prüfe:
1. Sind die vorgeschlagenen neuen Felder/Modelle kompatibel mit dem bestehenden Datenmodell?
2. Sind die Defaults korrekt? Werden bestehende Artefakte fehlerfrei deserialisiert?
3. Gibt es Naming-Konflikte oder Typ-Inkonsistenzen?
4. Sind die vorgeschlagenen Template-Schema-Patterns korrekt formuliert (Regex)?
5. Gibt es Felder, die der CR erwähnt, aber die im Code anders heißen oder anders typisiert sind?
6. Wird die Pydantic-Validierung (BaseModel) durch die Änderungen beeinträchtigt?

Lies auch `backend/artifacts/executor.py`, um zu prüfen:
7. Unterstützt der Executor die neuen Patch-Pfade ohne Code-Änderungen, oder braucht es Anpassungen?
8. Wie behandelt der Executor verschachtelte Felder (z.B. Listen von Objekten)?

Liefere: Liste aller Findings (Probleme, Risiken, Bestätigungen) mit Datei:Zeile Referenzen.
```

### Subagent 2: Orchestrator- und Kontrollfluss-Experte
Aufgabe: Prüfe die Auswirkungen auf den Orchestrator-Zyklus und die Invalidierungskaskade.

```
Lies `backend/core/orchestrator.py`, `backend/core/phase_transition.py` und `backend/core/working_memory.py`.

Der CR betrifft folgende Dateien und Felder:
{cr_dateien_und_felder — aus Abschnitt 4 des CRs einfügen}

Prüfe:
1. Löst der Orchestrator aktuell Invalidierungskaskaden aus? Wie? Bei welchen Feldern?
2. Müssen die vom CR betroffenen Felder ebenfalls Invalidierungen auslösen? Ist das im CR korrekt beschrieben?
3. Gibt es Guardrails in den Mode-Dateien (`backend/modes/*.py`), die durch die Änderungen beeinflusst werden?
4. Wie berechnet der Orchestrator den Completeness-State? Sind die betroffenen Felder für die Completeness relevant?
5. Gibt es Stellen im Code, die vom CR betroffene Felder direkt lesen und die durch die Änderungen brechen könnten?

Liefere: Liste aller Findings mit Datei:Zeile Referenzen.
```

### Subagent 3: Prompt- und LLM-Verhaltens-Experte
Aufgabe: Prüfe ob die Prompt-Änderungen das LLM-Verhalten wie gewünscht steuern.

```
Lies alle Prompts in `backend/prompts/` und alle Mode-Dateien in `backend/modes/`, um zu verstehen welche Platzhalter injiziert werden und welche Tools/tool_choice gesetzt sind.

Der CR schlägt folgende Prompt-Änderungen vor:
{cr_prompt_aenderungen — aus Abschnitt 3 und 4 des CRs einfügen}

Prüfe:
1. Sind die vorgeschlagenen Prompt-Änderungen konsistent mit dem Ton und der Struktur der bestehenden Prompts?
2. Wird das LLM die neuen Felder/Konzepte tatsächlich korrekt nutzen? Was spricht dagegen?
3. Sind die Patch-Beispiele im CR korrekt (gültige RFC 6902, korrekte Pfade, realistische Werte)?
4. Erhöht die Prompt-Erweiterung die Token-Last signifikant? Schätze die zusätzlichen Tokens.
5. Gibt es Widersprüche zwischen den Prompt-Änderungen und bestehenden Regeln in anderen Prompts?
6. Ist die Abwärtskompatibilität im Prompt gewährleistet? (Bestehende Artefakte ohne die neuen Felder — was passiert, wenn das LLM sie liest?)
7. Prüfe die First-Turn-Direktiven: Müssen sie angepasst werden?

Liefere: Liste aller Findings mit konkreten Prompt-Referenzen.
```

### Subagent 4: Test- und Regressions-Experte
Aufgabe: Prüfe die bestehende Testabdeckung und identifiziere Regressions-Risiken.

```
Finde und lies alle relevanten Tests in `backend/tests/`.
Suche insbesondere nach Tests, die vom CR betroffene Modelle, Felder oder Dateien referenzieren.

Der CR betrifft folgende Modelle/Felder/Dateien:
{cr_betroffene_elemente — aus Abschnitt 4 und 8 des CRs einfügen}

Prüfe:
1. Welche bestehenden Tests würden durch die vorgeschlagenen Änderungen brechen?
2. Sind die im CR vorgeschlagenen neuen Tests ausreichend?
3. Gibt es Test-Gaps, die der CR nicht adressiert?
4. Gibt es Fixtures oder Test-Factories, die betroffene Modelle erzeugen und die angepasst werden müssen?

Führe KEINE Tests aus — nur statische Analyse.

Liefere: Liste aller betroffenen Tests mit Datei:Zeile, erwarteten Brüchen und Gaps.
```

### Subagent 5: SDD- und Architektur-Konformitäts-Experte
Aufgabe: Prüfe ob der CR mit der Systemdefinition und der High-Level-Architektur vereinbar ist.

```
Lies selektiv aus `docs/digitalisierungsfabrik_systemdefinition.md`:
- Inhaltsverzeichnis (erste ~80 Zeilen)
- Abschnitte, die für den CR relevant sind (anhand der betroffenen Artefakte und Phasen identifizieren)

Der CR beschreibt seine SDD-Konsistenz wie folgt:
{cr_sdd_konsistenz — aus Abschnitt 3 des CRs einfügen}

Falls der CR einen ADR enthält:
{cr_adr — aus Abschnitt 3 des CRs einfügen, oder "Kein ADR vorhanden"}

Prüfe:
1. Widerspricht der CR dem SDD? Gibt es Stellen im SDD, die die vorgeschlagene Lösung explizit anders definieren?
2. Sind die betroffenen Felder/Modelle konsistent mit den SDD-Definitionen der Artefakte?
3. Erfordert der CR ein SDD-Update? Wenn ja: welche Abschnitte?
4. Verletzt der CR architektonische Prinzipien (z.B. "LLM als Operator mit eingeschränkten Schreibrechten", "deterministische Orchestrierung")?
5. Falls ein ADR vorhanden: Ist die Begründung für die SDD-Abweichung stichhaltig? Sind die Konsequenzen vollständig?

Liefere: Liste aller Konformitäts-Findings mit SDD-Abschnitt-Referenzen.
```

### Subagent 6: Abhängigkeits- und Konflikt-Experte
Aufgabe: Prüfe die CR-Abhängigkeiten und den Impact auf bestehende CRs.

```
Lies alle CRs in `agent-docs/change-requests/` mit Status "Freigegeben" oder "In Umsetzung".
Lies den Abschnitt "3a. Abhängigkeiten & Konflikte" des zu reviewenden CRs.

Prüfe:
1. Hat der CR-Autor alle relevanten Konflikte identifiziert?
2. Gibt es CRs, die dieselben Dateien oder Felder betreffen, aber nicht als Konflikt genannt wurden?
3. Sind die Abhängigkeiten (Setzt voraus / Blockiert / Ersetzt) korrekt und vollständig?
4. Ist die vorgeschlagene Konflikt-Auflösung realistisch?
5. Falls "Keine Konflikte" dokumentiert: Ist das korrekt?

Liefere: Liste aller Findings mit CR-Referenzen.
```

------------------------------------------------
PHASE 3 — SYNTHESE UND BEWERTUNG
------------------------------------------------

Nachdem ALLE Subagenten zurückgekehrt sind:

1. **Konsolidiere alle Findings** in einer strukturierten Liste.
2. **Klassifiziere jedes Finding:**
   - **Blocker** — Muss vor Umsetzung behoben werden. CR kann nicht freigegeben werden.
   - **Verbesserung** — Sollte in den CR eingearbeitet werden, blockiert aber nicht.
   - **Hinweis** — Gut zu wissen, keine Aktion nötig.
   - **Bestätigung** — CR-Behauptung wurde durch Code-Analyse bestätigt.

3. **Prüfe CR-Vollständigkeit** gegen die Pflichtabschnitte aus `/create-change-request`:
   - Kopfzeile mit Priorität (Kritisch/Hoch/Mittel/Niedrig) und Abhängigkeiten?
   - Problemstellung mit Kernproblem, Defiziten, Auswirkungen?
   - Ziel der Änderung?
   - Lösung mit Datenmodell, Beispielen, Prompt-Änderungen, Abwärtskompatibilität, SDD-Konsistenz?
   - ADR (falls SDD-Abweichung)?
   - Abhängigkeiten & Konflikte (Abschnitt 3a)?
   - Änderungsplan mit präzisen Zeilen?
   - Risiken und Mitigationen?
   - Nicht im Scope?
   - Abnahmekriterien (prüfbar)?
   - Aufwandsschätzung mit Komplexität S/M/L, betroffene Dateien, Breaking Change?

4. **Identifiziere Lücken**: Was hat der CR nicht bedacht?
   - Fehlende Dateien im Änderungsplan?
   - Fehlende Risiken?
   - Fehlende Abnahmekriterien?
   - Unzureichende Mitigationen?

5. **Bewerte die Gesamtqualität** des CRs:
   - Ist das Problem klar und nachvollziehbar beschrieben?
   - Ist die Lösung vollständig und umsetzbar?
   - Sind die Risiken angemessen adressiert?
   - Ist die Aufwandsschätzung realistisch?

------------------------------------------------
PHASE 4 — CCB-BERICHT ERSTELLEN UND PERSISTIEREN
------------------------------------------------

Erstelle den Bericht als Datei unter: `agent-docs/change-requests/CR-{NNN}-review.md`

Bei Re-Reviews: `CR-{NNN}-review-{N}.md` (fortlaufend nummeriert).

Der Bericht hat folgende Struktur:

```markdown
# CCB Review: CR-{NNN} — {Titel}

| Feld | Wert |
|---|---|
| **CR** | CR-{NNN} |
| **Review-Datum** | {Datum} |
| **Review-Nr.** | {1, 2, ...} |
| **Empfehlung** | {APPROVE / APPROVE WITH CONDITIONS / REWORK REQUIRED / DISAPPROVE} |

## Zusammenfassung
[2–3 Sätze: Was wurde geprüft, was ist das Ergebnis]

## Empfehlung
**{APPROVE / APPROVE WITH CONDITIONS / REWORK REQUIRED / DISAPPROVE}**

[1–2 Sätze Begründung]

## Blocker (müssen behoben werden)
[Nummerierte Liste — oder "Keine Blocker identifiziert."]

## Verbesserungsvorschläge (sollten eingearbeitet werden)
[Nummerierte Liste — oder "Keine."]

## Hinweise
[Nummerierte Liste — oder "Keine."]

## Bestätigungen (CR-Behauptungen, die verifiziert wurden)
[Nummerierte Liste]

## CR-Vollständigkeit
[Checkliste der Pflichtabschnitte — vorhanden/fehlend]

## Lückenanalyse
[Was fehlt im CR? Fehlende Dateien, Risiken, Kriterien]

## Detaillierte Findings pro Experte
### Datenmodell
[Findings]
### Orchestrator & Kontrollfluss
[Findings]
### Prompts & LLM-Verhalten
[Findings]
### Tests & Regression
[Findings]
### SDD & Architektur-Konformität
[Findings]
### Abhängigkeiten & Konflikte
[Findings]
```

Zusätzlich: Zeige dem Nutzer eine kompakte Zusammenfassung (Empfehlung, Anzahl Blocker/Verbesserungen, wichtigste Findings).

------------------------------------------------
EMPFEHLUNGSKRITERIEN
------------------------------------------------

- **APPROVE**: Keine Blocker, Lösung ist vollständig und korrekt, Risiken sind adäquat mitigiert.
- **APPROVE WITH CONDITIONS**: Keine harten Blocker, aber Verbesserungen sind vor Umsetzung empfohlen. Liste die Bedingungen explizit auf.
- **REWORK REQUIRED**: Signifikante Lücken oder Fehler im CR. Der CR muss überarbeitet und erneut submitted werden. Beschreibe klar, was überarbeitet werden muss.
- **DISAPPROVE**: Grundlegendes Problem mit dem Ansatz. Die vorgeschlagene Lösung ist nicht geeignet oder das Problem ist falsch identifiziert. Begründe ausführlich und schlage ggf. einen alternativen Ansatz vor.

------------------------------------------------
NACH DEM REVIEW
------------------------------------------------

Setze den CR-Status basierend auf der Empfehlung:

- **APPROVE**: Status auf **"Freigegeben"** setzen.
- **APPROVE WITH CONDITIONS**: Status auf **"Freigegeben"** setzen. Bedingungen im Review-Artefakt dokumentiert — der Implementierer muss sie berücksichtigen.
- **REWORK REQUIRED**: Status zurück auf **"Entwurf"** setzen. Der CR-Autor überarbeitet den CR und setzt den Status erneut auf "Review" für ein Re-Review.
- **DISAPPROVE**: Status auf **"Abgelehnt"** setzen. Begründung steht im Review-Artefakt.
