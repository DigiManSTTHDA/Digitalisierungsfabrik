# Implement Change Request

Setze einen freigegebenen Change Request (CR) aus `agent-docs/change-requests/` um.

Du bist ein erfahrener Entwickler, der einen präzise dokumentierten Änderungsplan Schritt für Schritt implementiert — ohne Scope Creep, ohne Improvisation, ohne Auslassungen.

Das Argument des Nutzers ist: $ARGUMENTS
Wenn kein Argument angegeben wurde, liste alle CRs mit Status "Freigegeben" in `agent-docs/change-requests/` auf und frage den Nutzer, welchen er implementieren möchte.

------------------------------------------------
STATUS-LIFECYCLE (Referenz)
------------------------------------------------

Entwurf → Review → **Freigegeben** → **In Umsetzung** → Implementiert → Verifiziert / Abgelehnt / Überholt.

Dieser Skill arbeitet auf CRs im Status **"Freigegeben"**. Wenn der CR einen anderen Status hat:
- **Entwurf/Review**: Hinweis, dass der CR erst den Review-Prozess durchlaufen muss (`/review-change-request`).
- **In Umsetzung**: Frage ob die Implementierung fortgesetzt werden soll (z.B. nach Abbruch).
- **Implementiert**: Hinweis, dass der CR bereits umgesetzt wurde.
- **Abgelehnt/Überholt**: Hinweis, dass der CR nicht mehr aktiv ist.

------------------------------------------------
PHASE 0 — VORAUSSETZUNGEN PRÜFEN
------------------------------------------------

1. **Sauberer Working Tree**: Prüfe mit `git status`, dass keine uncommitted Changes vorliegen. Falls doch: Abbruch mit Hinweis an den Nutzer ("Bitte erst committen oder stashen, damit bei Problemen sauber zurückgerollt werden kann.").
2. **Aktuellen Commit notieren**: Merke dir den aktuellen HEAD-Commit (für Rollback-Referenz).

------------------------------------------------
PHASE 1 — VORBEREITUNG
------------------------------------------------

Lies die folgenden Quellen PARALLEL, um Zeit zu sparen:

- **Den CR** (`agent-docs/change-requests/CR-{NNN}-*.md`) — vollständig.
- **Das Review-Artefakt** (`agent-docs/change-requests/CR-{NNN}-review*.md`) — falls vorhanden.
- **Alle im Änderungsplan (Abschnitt 4) genannten Dateien** — aktueller IST-Zustand.

Extrahiere anschließend:

1. **Änderungsplan** (Abschnitt 4) — das ist dein Arbeitsauftrag.
2. **Abnahmekriterien** (Abschnitt 7) — das ist deine Definition of Done.
3. **Risiken und Mitigationen** (Abschnitt 5) — darauf achtest du während der Umsetzung.
4. **Abhängigkeiten** (Abschnitt 3a) — müssen vor Beginn erfüllt sein.
5. **ADR** (falls in Abschnitt 3) — Architektur-Entscheidungen, die du bei JEDER Implementierungsentscheidung respektieren musst. Halte den ADR während der gesamten Implementierung im Blick.
6. **Aufwandsschätzung** (Abschnitt 8) — Komplexität und Breaking-Change-Flag.
7. **Review-Bedingungen** — Bei APPROVE WITH CONDITIONS: Extrahiere die Bedingungen als separate Checkliste. Sie sind Pflicht und werden am Ende explizit abgehakt.

### Abhängigkeiten prüfen

- "Setzt voraus: CR-XXX" — ist CR-XXX im Status "Implementiert"? Falls nein: Abbruch mit Hinweis.
- Konflikt-CRs — sind sie noch im selben Status wie bei CR-Erstellung? Falls sich etwas geändert hat: Warnung an den Nutzer.

### Aufwand und Risiko bewerten

- **Komplexität L oder Breaking Change**: Zeige dem Nutzer eine Warnung mit den Details aus Abschnitt 8 und frage explizit: "Dieser CR hat Komplexität {L} / enthält Breaking Changes. Soll ich fortfahren?" Erst nach Bestätigung weiter.

### Status setzen

Ändere den CR-Status auf **"In Umsetzung"**.

------------------------------------------------
PHASE 2 — IMPLEMENTIERUNG
------------------------------------------------

Arbeite den Änderungsplan (Abschnitt 4) **Phase für Phase, Zeile für Zeile** ab.

### Regeln

- **Strikt am Plan bleiben**: Implementiere genau das, was im Änderungsplan steht. Nicht mehr, nicht weniger.
- **Keine Improvisation**: Wenn eine Zeile im Plan unklar ist, halte inne und frage den Nutzer — rate nicht.
- **Reihenfolge einhalten**: Die Phasen im Plan haben eine definierte Reihenfolge (typisch: Datenmodell → Executor → Prompts → Context Assembler → Tests). Halte sie ein.
- **Mitigationen beachten**: Setze die Mitigationen aus Abschnitt 5 aktiv um, nicht nur die Hauptänderungen.
- **Review-Bedingungen umsetzen**: Falls der Review "APPROVE WITH CONDITIONS" war, sind die Bedingungen Teil des Auftrags. Tracke jede Bedingung einzeln und dokumentiere, wo und wie sie umgesetzt wurde.
- **ADR respektieren**: Falls der CR einen ADR enthält, prüfe bei jeder Architektur-relevanten Entscheidung, ob sie dem ADR entspricht. Weiche NICHT vom ADR ab, ohne den Nutzer zu fragen.
- **Kein Scope Creep**: Entdeckst du während der Implementierung weitere Probleme, die nicht im CR stehen? Notiere sie für einen Folge-CR, aber implementiere sie NICHT.
- **"Nicht im Scope" respektieren**: Abschnitt 6 des CRs definiert explizit, was NICHT gemacht werden soll.

### Fortschritt dokumentieren

Nach jeder abgeschlossenen Phase: Kurzes Status-Update an den Nutzer.
Format: `Phase {N}/{Total} abgeschlossen: {Was wurde gemacht}`

### Bei Problemen

- **Code hat sich seit CR geändert**: Passe die Implementierung an den aktuellen Code an, aber halte das Ziel des Plans ein. Dokumentiere die Abweichung.
- **Plan ist falsch oder veraltet**: Halte inne, beschreibe das Problem, frage den Nutzer ob der Plan angepasst werden soll.
- **Tests schlagen fehl**: Analysiere und behebe — aber nur wenn der Fix im Scope des CRs liegt. Neue Bugs, die nicht mit dem CR zusammenhängen, sind kein Grund zum Stoppen.

------------------------------------------------
PHASE 3 — TESTS AUSFÜHREN
------------------------------------------------

1. **Relevante Tests identifizieren**: Finde alle Tests, die vom CR betroffene Dateien, Modelle oder Felder referenzieren. Nutze dazu den Testpfad `backend/tests/` und suche nach Imports/Referenzen der geänderten Module.
2. **Bestehende Tests ausführen**: Führe die identifizierten Tests aus (`pytest` auf die relevanten Test-Dateien). Ziel: Regressionen erkennen.
3. **Neue Tests ausführen**: Falls der CR neue Tests vorsieht (siehe Änderungsplan), führe auch diese aus.
4. **Vollständigen Test-Lauf**: Führe danach die gesamte Test-Suite aus (`pytest backend/tests/`), um Seiteneffekte auf nicht offensichtlich betroffene Bereiche zu erkennen.
5. **Fehleranalyse**: Bei fehlgeschlagenen Tests:
   - Wurde der Fehler durch die CR-Änderungen verursacht? → Beheben.
   - Ist der Fehler unabhängig vom CR? → Dem Nutzer melden. NICHT im Scope dieses CRs beheben.
   - Fehlt ein Test, den der CR vorsieht? → Implementieren (ist Teil des Auftrags).

------------------------------------------------
PHASE 4 — ABNAHMEKRITERIEN PRÜFEN
------------------------------------------------

Gehe die Abnahmekriterien (Abschnitt 7) einzeln durch und prüfe jedes Kriterium:

```
| # | Abnahmekriterium | Erfüllt? | Evidenz |
|---|---|---|---|
| 1 | {Kriterium aus dem CR} | Ja/Nein | {Datei:Zeile oder Testname} |
| ... | ... | ... | ... |
```

Falls der Review "APPROVE WITH CONDITIONS" war, prüfe zusätzlich die Review-Bedingungen:

```
| # | Review-Bedingung | Erfüllt? | Evidenz |
|---|---|---|---|
| 1 | {Bedingung aus dem Review} | Ja/Nein | {Datei:Zeile oder Beschreibung} |
| ... | ... | ... | ... |
```

Falls der CR einen ADR enthält, prüfe:

```
| ADR-Aspekt | Konform? | Evidenz |
|---|---|---|
| {Architektur-Entscheidung aus dem ADR} | Ja/Nein | {Datei:Zeile} |
```

Alle Abnahmekriterien, Review-Bedingungen und ADR-Aspekte müssen "Ja" sein, bevor der CR als implementiert gilt.

------------------------------------------------
PHASE 5 — ABSCHLUSS
------------------------------------------------

1. **Status setzen**: Ändere den CR-Status auf **"Implementiert"**.
2. **Zusammenfassung an den Nutzer**:
   - Was wurde implementiert (Kurzfassung)
   - Abweichungen vom Plan (falls vorhanden)
   - Abnahmekriterien-Tabelle
   - Review-Bedingungen-Tabelle (falls APPROVE WITH CONDITIONS)
   - ADR-Konformitäts-Tabelle (falls ADR vorhanden)
   - Hinweis: "Zur Verifikation kann `/verify-change-request {CR-NNN}` ausgeführt werden."

------------------------------------------------
BEI ABBRUCH / ROLLBACK
------------------------------------------------

Falls die Implementierung abgebrochen werden muss (unlösbares Problem, falscher Plan, Nutzer bricht ab):

1. **Status zurücksetzen**: CR-Status zurück auf **"Freigegeben"**.
2. **Nutzer informieren**: Beschreibe was bereits implementiert wurde und was nicht.
3. **Rollback-Option**: Weise den Nutzer auf den in Phase 0 notierten HEAD-Commit hin, damit er bei Bedarf `git reset` oder `git stash` nutzen kann. Führe KEIN destruktives git-Kommando eigenständig aus.

------------------------------------------------
QUALITÄTSREGELN
------------------------------------------------

- **Abwärtskompatibilität sicherstellen**: Bestehende Artefakte, Tests und Prompts dürfen nicht brechen — es sei denn, der CR dokumentiert einen Breaking Change mit Migrationsstrategie.
- **Keine stilistischen Änderungen**: Ändere keinen Code, der nicht im Plan steht. Kein Refactoring, keine Formatierung, keine Docstrings außerhalb des Scopes.
- **Datei-Pfade relativ** zum Projekt-Root, konsistent mit dem CR.
- **Kein Commit**: Committe NICHT eigenständig. Die Änderungen bleiben uncommitted, damit `/verify-change-request` sie per `git diff` prüfen kann. Der Commit erfolgt erst nach bestandener Verifikation.
