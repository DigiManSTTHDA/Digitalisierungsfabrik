# Create Change Request

Erstelle einen formalen Change Request (CR) für die Digitalisierungsfabrik.

Du bist ein technischer Architekt, der Änderungsanträge so dokumentiert, dass ein anderer Agent (oder ein zukünftiges Ich) die Änderung ohne Rückfragen umsetzen kann.

------------------------------------------------
STATUS-LIFECYCLE
------------------------------------------------

Ein CR durchläuft folgende Status in dieser Reihenfolge:

1. **Entwurf** — CR ist in Arbeit, noch nicht vollständig.
2. **Review** — CR ist vollständig, wird via `/review-change-request` geprüft.
3. **Freigegeben** — Review bestanden, bereit zur Implementierung.
4. **In Umsetzung** — Implementierung läuft.
5. **Implementiert** — Umsetzung abgeschlossen, Abnahmekriterien erfüllt.
6. **Verifiziert** — Unabhängige Verifikation via `/verify-change-request` bestanden.
7. **Abgelehnt** — CR wurde im Review abgelehnt (Begründung im CR dokumentieren).
8. **Überholt** — Ein neuerer CR ersetzt diesen (Verweis auf Nachfolger-CR eintragen).

------------------------------------------------
VORBEREITUNG
------------------------------------------------

1. Verstehe den Änderungswunsch des Nutzers vollständig. Stelle Rückfragen, wenn unklar ist WAS oder WARUM.

2. Lies die relevanten Dateien, um den IST-Zustand zu verstehen:
   - Datenmodelle: `backend/artifacts/models.py`
   - Template-Schema: `backend/artifacts/template_schema.py`
   - Betroffene Prompts: `backend/prompts/*.md`
   - Betroffene Modes: `backend/modes/*.py`
   - Orchestrator: `backend/core/orchestrator.py`
   - SDD: `docs/digitalisierungsfabrik_systemdefinition.md` (selektiv)
   - Bestehende CRs: `agent-docs/change-requests/` (um ID-Konflikte UND inhaltliche Konflikte zu vermeiden)

3. Ermittle die nächste freie CR-Nummer. Lies den Inhalt von `agent-docs/change-requests/` und vergib die nächste Nummer (CR-001, CR-002, ...).

4. **Impact-Check auf bestehende CRs**: Prüfe ALLE CRs in `agent-docs/change-requests/` — insbesondere die mit Status "Freigegeben", "In Umsetzung", "Implementiert" oder "Verifiziert":
   - Berührt dieser CR dieselben Dateien oder Felder?
   - Widerspricht er Annahmen eines bestehenden CRs?
   - Dokumentiere Konflikte in Abschnitt "Abhängigkeiten & Konflikte" (siehe unten).

5. **ADR-Inventar prüfen**: Lies alle bestehenden CRs und extrahiere vorhandene ADRs (Architecture Decision Records). ADRs aus implementierten/verifizierten CRs sind **bindende Architektur-Entscheidungen** — sie haben denselben Stellenwert wie die SDD. Prüfe:
   - Berührt der neue CR einen Bereich, für den bereits ein ADR existiert?
   - Widerspricht der neue CR einem bestehenden ADR?
   - Falls ja: Der neue CR muss den bestehenden ADR explizit referenzieren und begründen, warum er abweicht (neuer ADR, der den alten ablöst).

6. **SDD-Konsistenzprüfung**: Prüfe, ob die geplante Änderung mit der SDD **und** allen bestehenden ADRs konsistent ist.
   - **Konsistent mit SDD und ADRs**: Notiere kurz warum (z.B. "Erweitert bestehendes Konzept X aus SDD Abschnitt Y, konform mit ADR aus CR-001").
   - **Gewünschte Abweichung von SDD**: Erstelle einen ADR als Unterabschnitt im CR. Der ADR dokumentiert: Kontext, Entscheidung, Begründung, Konsequenzen. Die SDD wird NICHT automatisch angepasst — das ist ein bewusster Schritt nach erfolgreicher Implementierung.
   - **Gewünschte Abweichung von bestehendem ADR**: Erstelle einen neuen ADR, der den alten explizit ablöst. Referenziere den alten ADR (CR-Nummer) und begründe die Änderung.

------------------------------------------------
CR-DOKUMENT ERSTELLEN
------------------------------------------------

Erstelle das Dokument unter: `agent-docs/change-requests/CR-{NNN}-{kurzer-slug}.md`

Das Dokument MUSS folgende Abschnitte enthalten:

## Kopfzeile (Tabelle)
- ID, Titel, Status (Entwurf), Erstellt (Datum), Priorität (Kritisch/Hoch/Mittel/Niedrig), Auslöser
- Abhängigkeiten: "Setzt voraus: CR-XXX" / "Blockiert: CR-YYY" / "Ersetzt: CR-ZZZ" (falls zutreffend)

## 1. Problemstellung
- **Kernproblem**: Was funktioniert nicht oder fehlt? Warum ist das ein Problem?
- **Konkrete Defizite**: Nummerierte Liste mit je einem Beispiel (Code, JSON, oder Ablauf)
- **Auswirkungen**: Was passiert, wenn wir nichts tun? Wer ist betroffen?

## 2. Ziel der Änderung
- Was soll nach der Änderung anders sein? Bullet Points, messbar wo möglich.

## 3. Lösung
- **Datenmodell-Änderungen**: Neue Modelle/Felder mit Typ, Default, Beschreibung
- **Beispiele**: Realistische JSON-Beispiele, die den SOLL-Zustand zeigen
- **Prompt-Änderungen**: Was wird wo ergänzt (Terminologie, Beispiele, Best Practices)
- **Abwärtskompatibilität**: Wie werden bestehende Daten behandelt?
- **SDD-Konsistenz**: Ist die Lösung konsistent mit der SDD? Falls nein: ADR (siehe unten).
- **ADR-Konsistenz**: Ist die Lösung konsistent mit bestehenden ADRs aus früheren CRs? Liste die relevanten ADRs mit CR-Referenz auf.

### ADR (bei gewünschter SDD-Abweichung oder ADR-Ablösung)
Wenn die Lösung bewusst von der SDD oder einem bestehenden ADR abweicht, dokumentiere einen Architecture Decision Record:
- **Kontext**: Welche SDD-Vorgabe oder welcher bestehende ADR (CR-Referenz) ist betroffen? Warum reicht sie/er nicht?
- **Entscheidung**: Was machen wir stattdessen?
- **Begründung**: Warum ist die Abweichung die bessere Wahl?
- **Ablösung** (falls zutreffend): "Löst ADR aus CR-{XXX} ab."
- **Konsequenzen**: Was folgt daraus? (SDD-Update nach Implementierung, betroffene Komponenten, etc.)

## 3a. Abhängigkeiten & Konflikte
- Liste aller CRs (Status "Freigegeben" oder "In Umsetzung"), die von dieser Änderung berührt werden.
- Pro Konflikt: Was genau kollidiert? Wie wird der Konflikt aufgelöst?
- Falls keine Konflikte: Explizit "Keine Konflikte mit bestehenden CRs" dokumentieren.

## 4. Änderungsplan
- Phasen-Tabelle: Jede Änderung als Zeile mit #, Datei, Änderung
- Reihenfolge: Datenmodell → Executor/Validierung → Prompts → Context Assembler → Tests
- Jede Zeile muss so präzise sein, dass ein Agent sie ohne Rückfrage umsetzen kann

## 5. Risiken und Mitigationen
- Jedes Risiko als eigenen Unterabschnitt mit:
  - **Risiko**: Was kann schiefgehen?
  - **Mitigation**: Was tun wir dagegen?
- Mindestens prüfen: Bestehende Daten, LLM-Verhalten, Template-Schema, Tests, Prompt-Länge

## 6. Nicht im Scope
- Was gehört NICHT zu diesem CR? Explizit abgrenzen, um Scope Creep zu vermeiden.

## 7. Abnahmekriterien
- Nummerierte Liste von prüfbaren Kriterien (ja/nein-Fragen)
- Tests müssen grün sein, bestehende Artefakte müssen weiter funktionieren

## 8. Aufwandsschätzung
- **Komplexität**: S (< 5 Dateien, kein Breaking Change) / M (5–15 Dateien oder Breaking Change) / L (> 15 Dateien oder mehrere Breaking Changes)
- **Betroffene Dateien**: Anzahl und Liste
- **Breaking Change**: Ja/Nein — falls Ja: Was bricht? Migrationsstrategie?
- Tabelle: Phase → betroffene Dateien → Komplexität (S/M/L)

------------------------------------------------
QUALITÄTSREGELN
------------------------------------------------

- **Konkret, nicht abstrakt**: Nicht "Modell erweitern", sondern "Feld `regeln: list[Entscheidungsregel]` auf `Strukturschritt` mit Default `[]` hinzufügen".
- **Beispiele sind Pflicht**: Jede Modelländerung braucht ein JSON-Beispiel. Jede Prompt-Änderung braucht ein konkretes Patch-Beispiel.
- **Abwärtskompatibilität IMMER adressieren**: Bestehende Artefakte, bestehende Tests, bestehende Prompts.
- **Kein Scope Creep**: Nur das dokumentieren, was zum Problem gehört. Verwandte Wünsche in "Nicht im Scope" referenzieren.
- **Sprache**: Deutsch. Technische Begriffe (Pydantic, RFC 6902, etc.) dürfen englisch sein.
- **Datei-Pfade immer relativ** zum Projekt-Root.

------------------------------------------------
NACH DEM ERSTELLEN
------------------------------------------------

1. Zeige dem Nutzer eine Zusammenfassung des CRs (Titel, Kernproblem, Lösung in 3 Sätzen, Komplexität, Breaking Change Ja/Nein).
2. Frage: "Soll ich etwas anpassen, oder soll der CR in den Review?"
3. Status bleibt "Entwurf" bis der Nutzer bestätigt.
4. Nach Bestätigung: Status auf "Review" setzen und auf `/review-change-request` verweisen.
5. Erst nach bestandenem Review wird der Status auf "Freigegeben" gesetzt — das macht der Review-Skill, nicht dieser.
