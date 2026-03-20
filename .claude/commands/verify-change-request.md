# Verify Change Request — Implementierungs-Review

Du bist ein **unabhängiger QA-Prüfer**, der verifiziert, dass ein implementierter Change Request (CR) korrekt und vollständig umgesetzt wurde.

Du bist NICHT der Implementierer. Du prüfst dessen Arbeit.

Das Argument des Nutzers ist: $ARGUMENTS
Wenn kein Argument angegeben wurde, liste alle CRs mit Status "Implementiert" in `agent-docs/change-requests/` auf und frage den Nutzer, welchen er verifizieren möchte.

------------------------------------------------
STATUS-LIFECYCLE (Referenz)
------------------------------------------------

Entwurf → Review → Freigegeben → In Umsetzung → **Implementiert** → **Verifiziert**

Dieser Skill arbeitet auf CRs im Status **"Implementiert"**. Wenn der CR einen anderen Status hat:
- **Freigegeben/In Umsetzung**: Hinweis, dass die Implementierung erst abgeschlossen werden muss (`/implement-change-request`).
- Andere Status: Hinweis, dass eine Verifikation nicht sinnvoll ist.

------------------------------------------------
PHASE 1 — KONTEXT AUFBAUEN
------------------------------------------------

Lies die folgenden Dokumente PARALLEL:

1. **Den CR** (`agent-docs/change-requests/CR-{NNN}-*.md`) — vollständig.
2. **Das CCB-Review** (`agent-docs/change-requests/CR-{NNN}-review*.md`) — falls vorhanden.
3. **Alle im Änderungsplan (Abschnitt 4) genannten Dateien** — den aktuellen Zustand nach Implementierung.

Extrahiere:
- Änderungsplan (Abschnitt 4) — Was sollte implementiert werden?
- Abnahmekriterien (Abschnitt 7) — Woran messen wir den Erfolg?
- Risiken und Mitigationen (Abschnitt 5) — Wurden die Mitigationen umgesetzt?
- Review-Bedingungen — Falls APPROVE WITH CONDITIONS: Wurden die Bedingungen erfüllt?
- ADR (falls vorhanden) — Wurde die Architektur-Entscheidung korrekt umgesetzt?

------------------------------------------------
PHASE 2 — PARALLELE VERIFIKATION
------------------------------------------------

Starte die folgenden Subagenten PARALLEL.

### Subagent 1: Änderungsplan-Vollständigkeit
Aufgabe: Prüfe ob jede Zeile im Änderungsplan umgesetzt wurde UND ob nur geplante Änderungen vorgenommen wurden.

```
Lies den CR und extrahiere den Änderungsplan (Abschnitt 4).
Lies dann jede im Plan genannte Datei im aktuellen Zustand.

Prüfe für JEDE Zeile im Änderungsplan:
1. Wurde die beschriebene Änderung umgesetzt? (Ja/Nein/Teilweise)
2. Entspricht die Umsetzung der Beschreibung? Oder weicht sie ab?
3. Falls abweichend: Ist die Abweichung sinnvoll (z.B. Code hat sich seit CR geändert) oder ein Fehler?

Prüfe auf ungewollte Änderungen (Scope-Check):
4. Führe `git diff --name-only` aus, um ALLE geänderten Dateien zu identifizieren.
5. Vergleiche die geänderten Dateien mit der Liste im Änderungsplan. Markiere jede Datei, die geändert wurde aber NICHT im Plan steht.
6. Prüfe ob Änderungen gemacht wurden, die in "Nicht im Scope" (Abschnitt 6) explizit ausgeschlossen waren.

Liefere:
- Tabelle mit # | Plan-Zeile | Status (Umgesetzt/Teilweise/Fehlend/Abweichend) | Details
- Liste ungeplanter Datei-Änderungen (falls vorhanden)
```

### Subagent 2: Abnahmekriterien-Verifikation
Aufgabe: Prüfe jedes Abnahmekriterium unabhängig.

```
Lies den CR und extrahiere die Abnahmekriterien (Abschnitt 7).
Lies alle relevanten Dateien und Tests.

Prüfe für JEDES Abnahmekriterium:
1. Ist das Kriterium erfüllt? (Ja/Nein)
2. Was ist die Evidenz? (Datei:Zeile, Testname, oder Code-Schnipsel)
3. Falls Nein: Was fehlt genau?

Liefere: Tabelle mit # | Kriterium | Erfüllt? | Evidenz
```

### Subagent 3: Regressions- und Testprüfung
Aufgabe: Führe Tests aus und prüfe auf Regressionen.

```
Finde alle relevanten Tests in `backend/tests/` für die im CR betroffenen Dateien.
Suche nach Tests, die die geänderten Module importieren oder referenzieren.

Führe die Tests aus:
1. Relevante Tests zuerst: `pytest backend/tests/{relevante_test_dateien}` — um schnell Feedback zu bekommen.
2. Dann die gesamte Test-Suite: `pytest backend/tests/` — um Seiteneffekte zu erkennen.

Prüfe:
1. Laufen alle bestehenden Tests grün?
2. Gibt es neue Tests, die der CR vorsieht? Sind sie vorhanden und grün?
3. Gibt es Test-Gaps (Abnahmekriterien ohne zugehörigen Test)?
4. Prüfe Abwärtskompatibilität: Werden bestehende Artefakte/Daten weiterhin korrekt verarbeitet? (z.B. Deserialisierung alter JSON-Daten ohne neue Felder)

Liefere: Test-Ergebnisse (bestanden/fehlgeschlagen), identifizierte Gaps, Regressionsbefunde, Abwärtskompatibilitäts-Check.
```

### Subagent 4: Mitigations- und Bedingungsprüfung
Aufgabe: Prüfe ob Risiko-Mitigationen und Review-Bedingungen umgesetzt wurden.

```
Lies den CR (Abschnitt 5: Risiken und Mitigationen).
Lies das Review-Artefakt (falls APPROVE WITH CONDITIONS: die Bedingungen).
Lies den aktuellen Code.

Prüfe für JEDE Mitigation:
1. Wurde die Mitigation umgesetzt? (Ja/Nein/Nicht zutreffend)
2. Evidenz?

Prüfe für JEDE Review-Bedingung (falls vorhanden):
1. Wurde die Bedingung erfüllt? (Ja/Nein)
2. Evidenz?

Liefere: Tabelle mit Mitigation/Bedingung | Umgesetzt? | Evidenz
```

### Subagent 5: SDD- und ADR-Konformitätsprüfung
Aufgabe: Prüfe ob die Implementierung mit der SDD und ggf. dem ADR konform ist.

```
Lies den CR (Abschnitt 3: SDD-Konsistenz, und ggf. den ADR-Unterabschnitt).
Lies selektiv die relevanten Abschnitte der SDD (`docs/digitalisierungsfabrik_systemdefinition.md`).
Lies die implementierten Code-Änderungen.

Prüfe SDD-Konformität:
1. Ist die Implementierung konsistent mit den SDD-Vorgaben für die betroffenen Artefakte/Phasen?
2. Wurden SDD-Prinzipien verletzt (z.B. "LLM als Operator", "deterministische Orchestrierung")?
3. Falls der CR SDD-Konsistenz behauptet: Stimmt das nach der Implementierung noch?

Falls der CR einen ADR enthält:
4. Wurde die im ADR dokumentierte Architektur-Entscheidung korrekt umgesetzt?
5. Stimmt der implementierte Code mit der ADR-Entscheidung überein — oder weicht er davon ab?
6. Sind die im ADR genannten Konsequenzen berücksichtigt (z.B. geplantes SDD-Update)?

Liefere:
- SDD-Konformitäts-Befund (konform/abweichend mit Referenzen)
- ADR-Konformitäts-Tabelle (falls ADR vorhanden): ADR-Aspekt | Konform? | Evidenz
```

------------------------------------------------
PHASE 3 — SYNTHESE
------------------------------------------------

Nachdem ALLE Subagenten zurückgekehrt sind:

1. **Konsolidiere alle Ergebnisse**.
2. **Klassifiziere jedes Finding:**
   - **Blocker** — Implementierung ist unvollständig oder fehlerhaft. Muss nachgebessert werden.
   - **Abweichung** — Implementierung weicht vom Plan ab, aber sinnvoll. Dokumentieren.
   - **Lücke** — Etwas fehlt, das im CR steht (Test, Mitigation, etc.).
   - **Bestätigung** — Korrekt umgesetzt wie geplant.

3. **Gesamtbewertung**:
   - Alle Abnahmekriterien erfüllt?
   - Alle Tests grün?
   - Alle Mitigationen umgesetzt?
   - Alle Review-Bedingungen erfüllt?
   - ADR korrekt umgesetzt (falls vorhanden)?
   - SDD-Konformität gegeben?
   - Abwärtskompatibilität gewährleistet?
   - Scope eingehalten (keine ungeplanten Datei-Änderungen)?

4. **Ergebnis-Logik** (Entscheidungsregeln):
   - **BESTANDEN**: Null Blocker UND null Lücken. Abweichungen sind akzeptabel, solange sie sinnvoll begründet sind.
   - **NACHBESSERUNG ERFORDERLICH**: Null Blocker, ABER mindestens eine Lücke (fehlender Test, fehlende Mitigation, ungeplante Änderung ohne Begründung). Oder: mehr als 3 Abweichungen, die in Summe das Vertrauen in die Plan-Treue mindern.
   - **NICHT BESTANDEN**: Mindestens ein Blocker (Abnahmekriterium nicht erfüllt, Tests rot, wesentlicher Plan-Teil nicht umgesetzt).

------------------------------------------------
PHASE 4 — VERIFIKATIONSBERICHT
------------------------------------------------

Erstelle den Bericht als Datei unter: `agent-docs/change-requests/CR-{NNN}-verification.md`
Bei Re-Verifikationen: `agent-docs/change-requests/CR-{NNN}-verification-{N}.md` (fortlaufend nummeriert).

```markdown
# Verifikation: CR-{NNN} — {Titel}

| Feld | Wert |
|---|---|
| **CR** | CR-{NNN} |
| **Verifikationsdatum** | {Datum} |
| **Ergebnis** | {BESTANDEN / NACHBESSERUNG ERFORDERLICH / NICHT BESTANDEN} |

## Zusammenfassung
[2–3 Sätze: Was wurde geprüft, was ist das Ergebnis]

## Ergebnis
**{BESTANDEN / NACHBESSERUNG ERFORDERLICH / NICHT BESTANDEN}**
[1–2 Sätze Begründung]

## Änderungsplan-Vollständigkeit
| # | Plan-Zeile | Status | Details |
|---|---|---|---|
| ... | ... | ... | ... |

## Abnahmekriterien
| # | Kriterium | Erfüllt? | Evidenz |
|---|---|---|---|
| ... | ... | ... | ... |

## Test-Ergebnisse
[Zusammenfassung: X Tests grün, Y fehlgeschlagen, Z Gaps]

## Mitigationen & Review-Bedingungen
| # | Mitigation/Bedingung | Umgesetzt? | Evidenz |
|---|---|---|---|
| ... | ... | ... | ... |

## SDD- & ADR-Konformität
[SDD-Konformitäts-Befund. Falls ADR vorhanden: ADR-Konformitäts-Tabelle]

## Blocker (müssen nachgebessert werden)
[Nummerierte Liste — oder "Keine."]

## Abweichungen vom Plan
[Nummerierte Liste — oder "Keine."]

## Lücken
[Nummerierte Liste — oder "Keine."]
```

------------------------------------------------
ERGEBNISKRITERIEN
------------------------------------------------

- **BESTANDEN**: Alle Abnahmekriterien erfüllt, alle Tests grün, keine Blocker. Der CR ist korrekt und vollständig implementiert.
- **NACHBESSERUNG ERFORDERLICH**: Kleinere Lücken oder Abweichungen. Beschreibe konkret, was nachgebessert werden muss. Nach Nachbesserung erneut verifizieren.
- **NICHT BESTANDEN**: Wesentliche Teile des Plans nicht oder falsch umgesetzt. Zurück an den Implementierer.

------------------------------------------------
NACH DER VERIFIKATION
------------------------------------------------

- **BESTANDEN**:
  1. Status auf **"Verifiziert"** setzen.
  2. **Commit erstellen**: Alle geänderten Dateien stagen und committen. Commit-Message-Format:
     ```
     feat(CR-{NNN}): {Kurzbeschreibung der Änderung}

     Change Request: CR-{NNN} — {Titel}
     Status: Verifiziert
     Verifikation: agent-docs/change-requests/CR-{NNN}-verification.md

     Änderungen:
     - {Bullet-Points der wesentlichen Änderungen aus dem CR}
     ```
     Nutze `feat` für neue Features, `fix` für Bugfixes, `refactor` für Umstrukturierungen — analog zu Conventional Commits.
  3. Bestätige dem Nutzer den Commit mit Hash und Message.

- **NACHBESSERUNG ERFORDERLICH**: Status bleibt "Implementiert". **Kein Commit.** Liste der Nachbesserungen an den Nutzer. Nach Nachbesserung erneut `/verify-change-request {CR-NNN}` ausführen (erzeugt nummeriertes Folge-Artefakt).
- **NICHT BESTANDEN**: Status zurück auf **"In Umsetzung"** setzen. **Kein Commit.** Detaillierter Fehlerbericht an den Nutzer. Erneut `/implement-change-request {CR-NNN}` zur Nacharbeit.
