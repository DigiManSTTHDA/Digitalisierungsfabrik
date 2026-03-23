# Run Change Request

Führe den vollständigen Change-Request-Lifecycle in einem kontrollierten Workflow aus.

Dieser Skill orchestriert alle CR-Skills und stellt sicher, dass jeder Change sicher, vollständig und nachvollziehbar umgesetzt wird.

Das Argument des Nutzers ist: $ARGUMENTS
Wenn kein Argument angegeben wurde, liste alle CRs in `agent-docs/change-requests/` auf und frage den Nutzer, welchen er durchführen möchte.

------------------------------------------------
KRITISCH: SICHERHEITS-GATES
------------------------------------------------

Anders als `/run-epic` läuft dieser Workflow NICHT blind durch.
Jeder Schritt hat ein **Gate**, das bei Problemen STOPPT.

Automatisches Weiterfahren NUR bei eindeutigem Erfolg.
Bei Unklarheiten, Blockern oder Fehlschlägen: STOPP und Nutzer informieren.

Nach jedem erfolgreichen Step:

"✅ Step N abgeschlossen. Weiter mit Step N+1..."

------------------------------------------------
STATUS-LIFECYCLE (Referenz)
------------------------------------------------

Entwurf → Review → Freigegeben → In Umsetzung → Implementiert → Verifiziert

Dieser Skill kann bei JEDEM Status einsteigen:
- **Entwurf** → Start ab STEP 1 (Review)
- **Review** → Start ab STEP 1 (Review, falls noch kein Review existiert)
- **Freigegeben** → Start ab STEP 3 (Implementierung)
- **In Umsetzung** → Start ab STEP 3 (Implementierung fortsetzen)
- **Implementiert** → Start ab STEP 4 (Verifikation)
- **Verifiziert** → Hinweis: CR ist bereits abgeschlossen.
- **Abgelehnt/Überholt** → Hinweis: CR ist nicht mehr aktiv.

------------------------------------------------
STEP 0 — CR BESTIMMEN UND LOG ANLEGEN
------------------------------------------------

1. CR identifizieren (aus Argument oder Nutzer-Auswahl).
2. CR vollständig lesen.
3. Status prüfen und Einstiegspunkt bestimmen (siehe oben).
4. Log-Datei anlegen oder fortsetzen:

   `agent-docs/cr-runs/CR-{NNN}.md`

   Initialisierung:
   ```
   # CR Run: CR-{NNN} — {Titel}

   | Feld | Wert |
   |---|---|
   | **CR** | CR-{NNN} |
   | **Start** | {Datum} |
   | **Einstieg bei Status** | {Status} |
   | **Ziel** | Verifiziert |

   ## Verlauf
   ```

5. Falls der Einstiegspunkt nicht STEP 1 ist: Springe direkt zum passenden Step.

→ Weiter mit dem ermittelten Einstiegs-Step.

------------------------------------------------
STEP 1 — REVIEW
------------------------------------------------

**Vorbedingung**: CR ist im Status "Entwurf" oder "Review".

Falls Status "Entwurf": Setze Status auf "Review" (der Nutzer hat durch Aufruf von `/run-change-request` implizit bestätigt).

Führe aus:

/review-change-request CR-{NNN}

**GATE — Review-Ergebnis auswerten:**

- **APPROVE**: ✅ Weiter mit STEP 3.
- **APPROVE WITH CONDITIONS**: ✅ Weiter mit STEP 2 (Escalation Checkpoint).
- **REWORK REQUIRED**: 🛑 **STOPP.**
  Log: Review-Ergebnis und Rework-Gründe.
  Meldung an Nutzer: "Der CR muss überarbeitet werden. Siehe Review-Artefakt für Details. Nach Überarbeitung erneut `/run-change-request CR-{NNN}` ausführen."
- **DISAPPROVE**: 🛑 **STOPP.**
  Log: Ablehnungsgründe.
  Meldung an Nutzer: "Der CR wurde abgelehnt. Siehe Review-Artefakt für Begründung."

Log: Review-Ergebnis, Empfehlung, Anzahl Blocker/Verbesserungen.

→ Bei APPROVE: Weiter mit STEP 3 (STEP 2 überspringen).
→ Bei APPROVE WITH CONDITIONS: Weiter mit STEP 2.

------------------------------------------------
STEP 2 — ESCALATION CHECKPOINT
------------------------------------------------

Dieser Step wird NUR bei APPROVE WITH CONDITIONS ausgeführt.

1. Lies das Review-Artefakt (`CR-{NNN}-review*.md`).
2. Extrahiere alle Bedingungen (Conditions) aus dem Review.
3. Prüfe jede Bedingung:

   - **Umsetzbar ohne Rückfragen**: Bedingung ist klar, kann während der Implementierung erfüllt werden. → Notieren und weiter.
   - **Architektur-Entscheidung nötig**: Bedingung erfordert eine Design-Entscheidung, die nicht im CR steht. → **STOPP.**

4. Falls STOPP nötig:
   - Präsentiere dem Nutzer:
     - Welche Bedingung ist betroffen
     - Was genau ist unklar
     - 2–3 konkrete Optionen mit Trade-offs
     - Eigene Empfehlung
   - Warte auf Nutzer-Entscheidung.
   - Dokumentiere die Entscheidung als ADR im CR.

5. Falls alle Bedingungen klar sind: Weiter ohne Stopp.

Log: Bedingungen-Liste, Escalation-Ergebnis (keine Escalation / Entscheidung getroffen).

→ Weiter mit STEP 3.

------------------------------------------------
STEP 3 — IMPLEMENTIERUNG
------------------------------------------------

**Vorbedingung**: CR ist im Status "Freigegeben" oder "In Umsetzung".

Führe aus:

/implement-change-request CR-{NNN}

**GATE — Implementierungs-Ergebnis auswerten:**

Der Implement-Skill endet mit einer Abnahmekriterien-Tabelle.

- **Alle Kriterien erfüllt + Tests grün**: ✅ Weiter mit STEP 4.
- **Kriterien nicht erfüllt oder Tests rot**: 🛑 **STOPP.**
  Log: Fehlende Kriterien, fehlgeschlagene Tests.
  Meldung an Nutzer: "Implementierung hat offene Punkte. Siehe Details oben."
- **Abbruch/Rollback**: 🛑 **STOPP.**
  Log: Abbruchgrund.
  Meldung an Nutzer: "Implementierung wurde abgebrochen. CR-Status ist wieder 'Freigegeben'."

Log: Implementierte Phasen, Abnahmekriterien-Status, Test-Ergebnisse.

→ Weiter mit STEP 4.

------------------------------------------------
STEP 4 — VERIFIKATION
------------------------------------------------

**Vorbedingung**: CR ist im Status "Implementiert".

Führe aus:

/verify-change-request CR-{NNN}

**GATE — Verifikations-Ergebnis auswerten:**

- **BESTANDEN**: ✅ Weiter mit STEP 5.
  (Verify-Skill hat bereits den Commit erstellt und Status auf "Verifiziert" gesetzt.)
- **NACHBESSERUNG ERFORDERLICH**: ⚠️ **Retry-Loop.**
  - Zähler: Versuch {N} von maximal 2.
  - Log: Nachbesserungs-Punkte.
  - Falls Versuch 1: Behebe die identifizierten Lücken, dann zurück zu STEP 4 (Re-Verifikation).
  - Falls Versuch 2 ebenfalls NACHBESSERUNG: 🛑 **STOPP.**
    Meldung an Nutzer: "Zweite Nachbesserung gescheitert. Manuelle Prüfung empfohlen."
- **NICHT BESTANDEN**: 🛑 **STOPP.**
  Log: Blocker-Liste.
  Meldung an Nutzer: "Verifikation nicht bestanden. CR ist zurück im Status 'In Umsetzung'. Siehe Verifikationsbericht."

Log: Verifikations-Ergebnis, Commit-Hash (bei BESTANDEN), Nachbesserungs-Versuche.

------------------------------------------------
STEP 5 — ABSCHLUSS UND ZUSAMMENFASSUNG
------------------------------------------------

**Vorbedingung**: CR ist im Status "Verifiziert".

1. Lies das Log (`agent-docs/cr-runs/CR-{NNN}.md`) und ergänze den Abschluss.

2. Abschluss-Eintrag im Log:
   ```
   ## Ergebnis
   | Feld | Wert |
   |---|---|
   | **Status** | Verifiziert ✅ |
   | **Ende** | {Datum} |
   | **Commit** | {Hash} |
   | **Review-Ergebnis** | {APPROVE / APPROVE WITH CONDITIONS} |
   | **Verifikations-Ergebnis** | BESTANDEN |
   | **Nachbesserungs-Versuche** | {0/1/2} |
   ```

3. Zusammenfassung an den Nutzer:
   - CR-Titel und ID
   - Was wurde geändert (1–3 Sätze)
   - Review-Empfehlung
   - Verifikations-Ergebnis
   - Commit-Hash
   - Verweis auf Artefakte:
     - CR: `agent-docs/change-requests/CR-{NNN}-*.md`
     - Review: `agent-docs/change-requests/CR-{NNN}-review*.md`
     - Verifikation: `agent-docs/change-requests/CR-{NNN}-verification*.md`
     - Run-Log: `agent-docs/cr-runs/CR-{NNN}.md`

------------------------------------------------
RETRY-LOGIK (NACHBESSERUNG)
------------------------------------------------

Bei NACHBESSERUNG ERFORDERLICH in STEP 4:

1. Lies den Verifikationsbericht und extrahiere die Nachbesserungs-Punkte.
2. Behebe NUR die identifizierten Lücken — kein Scope Creep.
3. Führe die betroffenen Tests erneut aus, um die Fixes zu bestätigen.
4. Zurück zu STEP 4 (Re-Verifikation mit nummeriertem Artefakt).

Maximum: **2 Nachbesserungs-Versuche**. Danach STOPP.

Begründung: Wenn nach 2 Versuchen noch Lücken bestehen, ist wahrscheinlich der CR selbst das Problem — nicht die Implementierung.

------------------------------------------------
LOG-PFLICHT
------------------------------------------------

Nach JEDEM Step wird das Log aktualisiert:

```
### Step {N} — {Name} ({Datum} {Uhrzeit})
**Ergebnis**: {Kurz-Ergebnis}
**Details**: {Relevante Details}
**Gate**: {✅ Weiter / 🛑 Stopp / ⚠️ Retry}
```

Das Log dient der Nachvollziehbarkeit und ermöglicht es,
bei einem STOPP den Workflow später an der richtigen Stelle
fortzusetzen.

------------------------------------------------
ABBRUCH-VERHALTEN
------------------------------------------------

Bei jedem STOPP:
1. Log wird mit aktuellem Stand geschrieben.
2. CR-Status wird konsistent gehalten (kein Zwischenstatus).
3. Nutzer erhält klare Anweisung, was als nächstes zu tun ist.
4. Workflow kann mit `/run-change-request CR-{NNN}` fortgesetzt werden — der Einstiegspunkt wird automatisch anhand des CR-Status ermittelt.
