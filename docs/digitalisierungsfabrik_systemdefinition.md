# SYSTEM DEFINITIONS DOKUMENT
Digitalisierungsfabrik

---

## Inhaltsverzeichnis

Für gezielten Zugriff: Zeile notieren → Datei mit `offset=<Zeile>` und passendem `limit` lesen.

| Abschnitt | Inhalt | Zeile |
|---|---|---|
| **1** | **SYSTEMÜBERSICHT** | **77** |
| 1.1 | Systemzweck, Artefakte, Systemrolle | 79 |
| 1.2 | Zielnutzer | 118 |
| 1.3 | Systemsprache | 138 |
| **2** | **BENUTZERINTERAKTION & UI** | **148** |
| 2.1 | Kerninteraktion, Turn-Modell | 150 |
| 2.2 | Benutzeroberfläche | 178 |
| 2.3 | Debug-Bereich | 193 |
| 2.4 | Panik-Button | 207 |
| 2.5 | Phasenanzeige & Fortschrittsindikator | 229 |
| **3** | **SYSTEMFÄHIGKEITEN** | **245** |
| **4** | **FUNKTIONALE ANFORDERUNGEN (FR)** | **251** |
| 4 Konventionen | FR-Referenzformat: FR-[Gruppe]-[Nr] | 255 |
| Gruppe A | Wissensextraktion & Dialog (FR-A-01…) | 264 |
| Gruppe B | Artefaktmanagement (FR-B-01…) | 300 |
| Gruppe C | Validierung & Konsistenz (FR-C-01…) | 364 |
| Gruppe D | Orchestrierung & kognitive Modi (FR-D-01…) | 398 |
| Gruppe E | Persistenz & Fehlerbehandlung (FR-E-01…) | 434 |
| Gruppe F | UI & Observability (FR-F-01…) | 464 |
| Gruppe G | Projektverwaltung (FR-G-01…) | 488 |
| **5** | **PROZESSARTEFAKTE** | **518** |
| 5.1 | Überblick, Externes Artefakt-Prinzip | 522 |
| 5.2 | Versionierung | 550 |
| 5.3 | Explorationsartefakt | 571 |
| → | Explorations-Slot Felder-Tabelle | 586 |
| 5.4 | Strukturartefakt | 618 |
| → | Strukturschritt Felder-Tabelle | 635 |
| 5.5 | Algorithmusartefakt | 664 |
| → | Algorithmusabschnitt Felder-Tabelle | 683 |
| → | EMMA-Aktion Felder-Tabelle | 694 |
| 5.5 | Referenzielle Integrität | 750 |
| 5.6 | Completeness-State (Artefakt & Working Memory) | 777 |
| 5.7 | Schreiboperationen — RFC 6902 JSON Patch | 802 |
| 5.8 | Template-Schema | 852 |
| **6** | **SYSTEMSTEUERUNG** | **884** |
| 6.1 | Systemphasen, Phasenwechsel, Validierungsschleife, Rücksprung | 888 |
| 6.2 | Orchestrator — Eigenschaften & Verantwortlichkeiten | 964 |
| 6.3 | Orchestrator-Zyklus (11 Schritte) | 986 |
| → | Moduswechsel-Logik | 1004 |
| 6.4 | Working Memory | 1019 |
| → | Felder-Tabelle | 1025 |
| 6.4.1 | Steuerungsflags / Flag-Enum (NICHT im WM) | 1045 |
| 6.5 | Context Engineering, Output-Kontrakt, Tokenlimit-Strategie | 1067 |
| 6.6 | Kognitive Modi (Übersicht) | 1119 |
| 6.6.1 | Explorationsmodus | 1131 |
| 6.6.2 | Strukturierungsmodus | 1150 |
| 6.6.3 | Spezifikationsmodus | 1170 |
| 6.6.4 | Validierungsmodus, Schweregradskala | 1190 |
| 6.6.5 | Moderator | 1224 |
| 6.7 | Fortschrittsmodell (Phasenstatus, Slot-Zähler) | 1249 |
| **7** | **DATENINTEGRATION & PERSISTENZ** | **1288** |
| 7.1 | Rohdaten-Integration | 1293 |
| 7.2 | Projektmodell — Felder-Tabelle (Projektmetadaten) | 1329 |
| 7.3 | Persistenzmodell (was/wann/ACID/Constraints) | 1369 |
| **8** | **SYSTEMGRENZEN & QUALITÄTSANFORDERUNGEN** | **1434** |
| 8.1.1 | NFR: Wartbarkeit — PRIMÄR | 1444 |
| 8.1.2 | NFR: Zuverlässigkeit — PRIMÄR | 1460 |
| 8.1.3 | NFR: Beobachtbarkeit — PRIMÄR | 1474 |
| 8.1.4 | NFR: Performance — SEKUNDÄR | 1490 |
| 8.1.5 | NFR: Skalierung — SEKUNDÄR | 1504 |
| 8.1.6 | NFR: Sicherheit — PRAGMATISCH | 1509 |
| 8.2 | Architekturrahmen (Constraints) | 1524 |
| 8.3 | EMMA-Aktionskatalog | 1541 |
| 8.4 | Prozessumfang & Partitionierung | 1576 |
| 8.5 | Systemgrenzen (Ausschlüsse) | 1589 |
| 8.6 | Abschlusskriterien | 1605 |
| **Offene Punkte** | **Konsolidierte Gesamtliste** | **1634** |

---

# 1. SYSTEMÜBERSICHT

## 1.1 Systemzweck

Das System unterstützt Menschen ohne Programmier- oder Automatisierungskenntnisse dabei, einen Geschäftsprozess in einen präzisen, strukturierten Algorithmus zu überführen.

Der Ausgangspunkt ist das implizite Prozesswissen eines Nutzers. Ein Mensch kennt häufig den Ablauf eines Prozesses sehr genau, ist jedoch nicht in der Lage, dieses Wissen formal oder algorithmisch zu beschreiben. Genau hier setzt das System an.

Durch dialogische Interaktion mit einem KI-System wird dieses implizite Wissen schrittweise:

- explizit gemacht  
- strukturiert  
- konsolidiert  
- auf Widersprüche geprüft  
- in eine algorithmische Beschreibung überführt  

Ziel des Systems ist die schrittweise Überführung des impliziten Prozesswissens in einen expliziten, hinreichend detaillierten und vollumfänglichen Algorithmus.

Output des Systems besteht aus drei Artefakten:
1. **Explorationsartefakt** — Freitextbasierte Rohbeschreibung des Prozesses, erarbeitet in der Explorationsphase. Grundlage für die Strukturierung.
2. **Strukturartefakt** — Strukturierte Prozessbeschreibung auf BPMN-ähnlicher Granularitätsebene.
3. **Algorithmusartefakt** — Technisch präziser Algorithmus, direkt umsetzbar als Kontrollflussgraph in EMMA RPA. Verknüpft mit dem Strukturartefakt.

Aufbau und Schema aller drei Artefakte sind in Abschnitt 5 definiert.

Das System übernimmt dabei die Rolle eines virtuellen Experten für:

- Prozessanalyse  
- Prozessstrukturierung  
- Automatisierungsdesign  

Der Nutzer wird aktiv durch mehrere Analyse- und Spezifikationsphasen geführt.

Die Rolle des Systems ist vergleichbar mit der Sokratischen Hebammentechnik: Es gewinnt durch gezielte Fragestellung und gewissenhafte Dokumentation gemeinsam mit dem Nutzer eine "Prozesswahrheit" — eine Prozessbeschreibung die geeignet ist, im Ziel-RPA-System umgesetzt zu werden.

Die Prozesslogik selbst kommt ausschließlich vom Nutzer. Das System trifft keine inhaltlichen Entscheidungen über den Prozess und stellt keine unbegründeten Annahmen auf. Es bewertet jedoch aktiv: Es weist auf Inkonsistenzen hin, warnt bei Automatisierungsproblemen, schlägt Alternativen vor und hilft dem Nutzer aktiv weiter wenn er nicht weiterkommt. Die endgültige Entscheidung liegt stets beim Nutzer.

Das System wird zunächst als Prototyp entwickelt, soll jedoch eine robuste und saubere Architektur besitzen, sodass eine spätere Weiterentwicklung problemlos möglich ist.

---

## 1.2 Zielnutzer

Primäre Zielnutzer sind Fachanwender ohne Programmierkenntnisse und ohne ausgebildetem algorithmischen Denkens.

Diese Nutzer besitzen in der Regel:

- tiefes Wissen über einen Geschäftsprozess
- keine Erfahrung mit Softwareentwicklung
- kein ausgeprägtes algorithmisches Denken

Sie sind also in der Regel nicht in der Lage ihr implizites Prozesswissen in einen logischen und hinreichend detaillierten Algorithmus umzuwandeln.

Das System soll diesen Nutzern ermöglichen, ihr vorhandenes Prozesswissen in eine automatisierbare Form zu überführen.

Typischer Nutzungskontext:

Ein Mitarbeiter möchte einen wiederkehrenden Prozess automatisieren.

---

## 1.3 Systemsprache

Die primäre Systemsprache ist Deutsch.

Alle Dialoge, Artefakte und Beschreibungen werden standardmäßig in deutscher Sprache erzeugt.

Mehrsprachigkeit ist aktuell keine Systemanforderung.

---

# 2. BENUTZERINTERAKTION UND UI

## 2.1 Kerninteraktion

Die Interaktion erfolgt über eine Web-Applikation im Browser.

Die Oberfläche besteht aus zwei zentralen Bereichen:

**Chatbereich**

Hier findet der Dialog zwischen Nutzer und System statt. Der Nutzer beschreibt seinen Prozess, beantwortet Rückfragen und liefert zusätzliche Informationen.
Das System gibt hier Antworten aus. ARtefakte werden NICHT im Chatbereich ausgegeben.

**Artefaktbereich**

Hier werden alle drei Prozessartefakte angezeigt: Explorationsartefakt, Strukturartefakt und Algorithmusartefakt. Sie wachsen während des Dialogs kontinuierlich.

Der Nutzer sieht dadurch jederzeit den aktuellen Stand aller drei Artefakte. Artefakte die in der aktuellen Phase noch nicht aktiv sind werden als leer aber sichtbar dargestellt.

Artefaktbereich und Chatbereich sind voneinander getrennt.

Unterstützte Eingabeformen im Chatbereich:

- Texteingaben
- Dokumentuploads
- Bilduploads
- Upload externer Rohdaten (z.B. EMMA Recorder-Eventlogs) — siehe Abschnitt 7.1

---

## 2.2 Benutzeroberfläche

Die Benutzeroberfläche enthält neben Chatbereich und Artefaktbereich mindestens folgende Elemente:

- Panik-Button
- Anzeige der aktuellen Systemphase
- Fortschrittsanzeige
- Download-Button (jederzeit verfügbar; lädt beide Artefakte in den Formaten JSON und Markdown herunter)
- Recorder-Button (reserviert für künftige EMMA Recorder Integration; im Prototyp deaktiviert — Klick zeigt Hinweis "nicht im Prototyp verfügbar")
- Debug-Bereich

Diese Elemente unterstützen den Nutzer dabei, jederzeit Orientierung im System zu behalten.

---

## 2.3 Debug-Bereich

Der Debug-Bereich dient primär der Entwicklung und Analyse. Diese steht im Zentrum während der Prototyp-Entwicklung. Er soll aber später ausgeblendet werden können.

Der Debug-Bereich zeigt interne Systeminformationen und den Systemzustand an, zum Beispiel:

- aktiver kognitiver Modus
- aktueller Systemzustand (zu bestimmen welche Aspekte)
- gesetzte Steuerungsflags der kognitiven Modi an den Orchestrator
- Fortschrittsmetriken
- weitere interne Observablen, Zustände und Metriken nach Bedarf.

---

## 2.4 Panik-Button

Der Nutzer kann jederzeit eine Eskalation auslösen.

Dies geschieht über einen **Panik-Button**.

Der Panik-Button ist vorgesehen für Situationen, in denen der Nutzer das Gefühl hat, dass:

- die Interaktion festgefahren ist
- sich der Dialog im Kreis dreht
- die aktuelle Strategie nicht zielführend ist
- Orientierung verloren gegangen ist

Wird der Panik-Button aktiviert, unterbricht das System (über den Orchestrator, s.u.) den aktuellen Arbeitsmodus und aktiviert den Moderator.

Der Moderator analysiert gemeinsam mit dem Nutzer die Situation und entwickelt eine Strategie für das weitere Vorgehen.
Nach Analyse der Problematik und Erarbeitung einer Lösung schlägt der Moderator dem Nutzer diese Lösungsstrategie vor. 
Bei Genehmigung durch den Nutzer übergibt der Moderator (über Orchestrator) zurück an den zuvor aktiven kognitiven Modus.
Der dabei aufgerufene kognitive Modus empfängt den relevanten Kontext aus dem unterbrochenen Chat und der Lösungsstrategie des Moderators, damit die vereinbarte Lösung umgesetzt wird.

---

## 2.5 Phasenanzeige und Fortschrittsindikator

Der Nutzer sieht jederzeit:

- die aktuelle Phase
- den Fortschritt innerhalb dieser Phase

Die Fortschrittsanzeige besteht aus zwei Komponenten:

- **Phasenstatus** — gemeldet vom aktiven kognitiven Modus: `in_progress` / `nearing_completion` / `phase_complete`
- **Slot-Zähler** — vom Orchestrator berechnet: Anzahl befüllter Slots im Verhältnis zur aktuell bekannten Gesamtzahl (z.B. "7 von 12 Slots befüllt"). Kein Prozentwert — die Gesamtzahl der Slots wächst während des Dialogs und ist zu Beginn nicht bekannt.

Die Anzeige dient dazu, dem Nutzer Orientierung über den aktuellen Stand des Prozesses zu geben.

---

# 3. SYSTEMFÄHIGKEITEN

Abschnitt gestrichen

---

# 4 Funktionale Anforderungen

---

## Konventionen

- Jede Anforderung ist eindeutig referenzierbar (FR-[Gruppe]-[Nr])
- Akzeptanzkriterium (AK) beschreibt, wann die Anforderung als erfüllt gilt
- Abhängigkeiten werden explizit benannt
- `[OFFEN]` markiert Punkte, die noch geklärt werden müssen

---

## Gruppe A — Wissensextraktion & Dialog

**FR-A-01: Dialogischer Interviewprozess**  
Das System führt den Nutzer durch einen strukturierten Dialog zur Extraktion von implizitem Prozesswissen.  
AK: Das System stellt gezielte, kontextabhängige Folgefragen basierend auf vorherigen Nutzerantworten.

**FR-A-02: Anleitungskompetenz**  
Das System kommuniziert zu jedem Zeitpunkt klar, welcher Schritt als nächstes erwartet wird.  
AK: Jede Systemantwort im Interviewmodus enthält eine eindeutige Handlungsaufforderung an den Nutzer.

**FR-A-03: Identifikation fehlender Informationen**  
Das System erkennt, wenn für die Artefaktgenerierung notwendige Informationen noch nicht vorliegen, und fordert diese gezielt an.  
AK: Das System benennt konkret, welche Information fehlt und warum sie benötigt wird.  
Abhängigkeit: FR-B-01 (Artefakt-Datenmodell muss definiert sein, damit „fehlend" messbar ist)

**FR-A-04: Identifikation von Ausnahmen und Sonderfällen**  
Das System erkennt und dokumentiert prozessrelevante Ausnahmen (z.B. Fehlerbehandlung, Sonderfälle).  
AK: Identifizierte Ausnahmen werden explizit im Strukturartefakt als separate Verzweigungen erfasst.

**FR-A-05: Verarbeitung externer Rohdaten**  
Das System akzeptiert externe Rohdaten (EMMA-Recorder-Eventlogs, Dokumente, Bilder) als Eingabe und transformiert diese in prozessrelevante Informationen.  
AK: (1) Aus einem validen Eventlog werden mindestens Prozessschritte und Aktionssequenzen extrahiert und dem Nutzer zur Bestätigung vorgelegt. Bestätigte Informationen werden als Schreiboperationen auf Artefakt-Slots ausgeführt (s. Abschnitt 5.7). (2) Der Orchestrator erkennt den Dateityp anhand der Dateiendung und leitet die Datei als Kontext-Bestandteil an den aktiven Modus weiter — ohne separaten Verarbeitungsschritt (s. 7.1). (3) Nicht unterstützte oder nicht erkannte Dateiformate werden abgelehnt. Der Nutzer erhält eine Fehlermeldung mit explizitem Hinweis auf die unterstützten Formate.  
Abhängigkeit: s. 7.1 (Verarbeitungsmodell), s. 8.2 (austauschbare Rohdaten-Schnittstelle)  
Einschränkung: Das Eventlog-Format ist nicht final definiert. FR-A-05 ist solange nicht vollständig testbar, bis das EMMA Recorder-Format bekannt ist. `[OFFEN: OP-17]`

**FR-A-06: Bewertung der Automatisierbarkeit**  
Das System bewertet identifizierte Prozessschritte hinsichtlich ihrer Automatisierbarkeit mit EMMA RPA.  
AK: Jeder Prozessschritt erhält eine Klassifikation: automatisierbar / bedingt automatisierbar / nicht automatisierbar — mit Begründung.  
Abhängigkeit: FR-C-03 (EMMA-Aktionskatalog muss als Referenz hinterlegt sein)

**FR-A-07: Warnung bei eingeschränkter Automatisierbarkeit**  
Das System warnt den Nutzer aktiv, wenn ein Prozess Schritte enthält, die mit EMMA nicht oder nur schwer automatisierbar sind.  
AK: Bei mehr als einem nicht automatisierbaren Schritt erfolgt eine explizite Warnung mit Handlungsoptionen (Anpassen, Ignorieren, Abbrechen).

---

## Gruppe B — Artefaktmanagement

**FR-B-00: Explorationsartefakt**
Das System erzeugt ein Explorationsartefakt als primären Output der Explorationsphase.
AK: (1) Das Explorationsartefakt enthält alle Pflicht-Slots gemäß Abschnitt 5.3. (2) Alle Pflicht-Slots müssen den Status `nutzervalidiert` erreichen bevor die Explorationsphase als abgeschlossen gilt. (3) Das Explorationsartefakt wird in der Strukturierungsphase als Read-Only-Lesekontext übergeben — es wird nach Abschluss der Explorationsphase nicht weiter modifiziert. (4) Das Explorationsartefakt unterliegt derselben Schreibkontrolle wie die anderen Artefakte (s. FR-B-09).
Abhängigkeit: Abschnitt 5.3 (Explorationsartefakt), FR-B-09 (Schreibkontrolle)

**FR-B-01: Strukturartefakt**  
Das System erzeugt ein Strukturartefakt auf BPMN-ähnlicher Granularitätsebene.  
Format: JSON mit adressierbaren Slot-IDs `[OFFEN: OP-01]`  
AK: (1) Das Artefakt enthält alle identifizierten Prozessschritte, Verzweigungen und Ausnahmen in einer validen, strukturierten Form. (2) Jeder Strukturschritt ist als eigenständiger Slot adressierbar. (3) Das Artefakt besitzt als ersten Pflichtslot eine Prozesszusammenfassung — Freitext, für Fachanwender lesbar, LLM-generiert. Dieser Slot wird beim Anlegen des Artefakts initialisiert und spätestens am Ende der Strukturierungsphase befüllt.

**FR-B-02: Algorithmusartefakt**  
Das System erzeugt ein Algorithmusartefakt, das ausreichend präzise ist zur direkten Umsetzung als Kontrollflussgraph in EMMA RPA.  
Format: JSON mit adressierbaren Slot-IDs `[OFFEN: OP-01]`  
AK: (1) Jeder Algorithmusabschnitt ist als eigenständiger Slot adressierbar und enthält mindestens: Schritt-ID, Aktionstyp (aus EMMA-Aktionskatalog), Parameter, Nachfolger. (2) Das Artefakt besitzt als ersten Pflichtslot eine Prozesszusammenfassung — Freitext, technisch angereichert, LLM-generiert. Dieser Slot wird beim Anlegen des Artefakts initialisiert und spätestens am Ende der Spezifikationsphase befüllt.

**FR-B-03: Referenzielle Integrität zwischen Artefakten**  
Jeder Strukturschritt besitzt eine stabile Referenz auf einen oder mehrere korrespondierende Algorithmusabschnitte. Jeder Algorithmusabschnitt referenziert genau einen Strukturschritt. Die Beziehung ist 1:n (ein Strukturschritt kann mehrere Algorithmusabschnitte haben), aber nicht umgekehrt.  
AK: (1) Jeder Strukturschritt besitzt mindestens eine valide `algorithmus_ref`. (2) Jeder Algorithmusabschnitt besitzt genau eine valide `struktur_ref`. (3) Eine Änderung an einem Strukturartefakt-Slot löst automatisch die Invalidierung aller referenzierten Algorithmusabschnitte aus — nicht nur des ersten.  
Abhängigkeit: FR-B-09 (Schreibkontrolle stellt sicher, dass Invalidierung ausschließlich systemseitig erfolgt)

**FR-B-04: Invalidierungslogik**  
Bei Änderungen an Strukturartefakt-Slots werden betroffene Algorithmusabschnitte vom System als invalidiert markiert.  
AK: Das System zeigt dem Nutzer explizit an, welche Algorithmusabschnitte nach einer Strukturänderung betroffen sind. Die Invalidierung wird ausschließlich vom System ausgeführt — nicht durch das LLM.

**FR-B-05: Löschung von Strukturschritten**
Die Löschung eines Strukturschritts führt zur Invalidierung aller referenzierten Algorithmusabschnitte.
AK: (1) Vor Ausführung einer `remove`-Operation auf einen Strukturschritt prüft der Orchestrator ob referenzierte Algorithmusabschnitte existieren. (2) Falls ja: Der Nutzer erhält eine explizite Warnung mit Auflistung der betroffenen Abschnitte. (3) Nach Nutzerbestätigung wird die Löschoperation ausgeführt und alle referenzierten Algorithmusabschnitte auf `invalidiert` gesetzt. (4) Die Operation wird nicht automatisch blockiert.
Abhängigkeit: Abschnitt 5.5 (Referenzielle Integrität), FR-B-04 (Invalidierungslogik), FR-B-09 (Schreibkontrolle)

**FR-B-06: Kontinuierliche Artefaktsichtbarkeit**  
Beide Artefakte sind während des gesamten Dialogs im Artefaktbereich sichtbar und spiegeln jederzeit den aktuellen Stand wider.  
AK: Nach jeder vom Orchestrator ausgeführten Schreiboperation wird der Artefaktbereich aktualisiert, ohne dass der Nutzer eine explizite Aktion ausführen muss.

**FR-B-07: Download, Export und Import von Artefakten**  
Der Nutzer kann alle drei Artefakte (Explorationsartefakt, Strukturartefakt, Algorithmusartefakt) jederzeit herunterladen — unabhängig vom aktuellen Phasenstand oder Vollständigkeitsstatus.  
Unterstützte Download-Formate:
- **JSON** — natives Artefaktformat, maschinenlesbar, für Weiterverarbeitung durch nachgelagerte Systeme
- **Markdown** — menschenlesbare Darstellung, für Dokumentation und Review

Zusätzlich können modifizierte Artefakte als JSON reimportiert werden.  
AK: (1) Download ist jederzeit über einen dedizierten Button im UI auslösbar. (2) Importierte Artefakte werden vor der Übernahme auf Schema-Konformität und Slot-Integrität validiert (FR-C-04). Ungültige Artefakte werden mit Fehlerbeschreibung abgelehnt.

**FR-B-07: Artefaktintegrität durch externes Artefaktmodell**  
Artefakte werden außerhalb des LLM-Kontexts verwaltet. Das LLM gibt Artefakte niemals vollständig zurück. Alle Artefaktänderungen erfolgen ausschließlich als chirurgische Schreiboperationen auf benannte Slots.  
AK: (1) Kein LLM-Output enthält das Artefakt als Volltext. (2) Jede Artefaktänderung ist auf einen einzelnen Slot beschränkt und wird vom Orchestrator vor Ausführung validiert. (3) Das Artefakt ist zu jedem Zeitpunkt vollständig und korrekt abrufbar, unabhängig vom LLM-Zustand. (4) Die Versionierung beider Artefakte wird beim Anlegen eines neuen Projekts sofort initialisiert — nicht erst bei der ersten Schreiboperation. Version 0 repräsentiert den leeren Initialzustand.

**FR-B-08: Generierung einer Prozesszusammenfassung**  
Das System kann auf Anforderung eine für Nicht-Techniker verständliche Zusammenfassung des aktuellen Prozessartefakts erzeugen.  
AK: Die Zusammenfassung enthält keine technischen IDs oder Formatdetails und ist für den Fachanwender lesbar.

**FR-B-09: Schreibkontrolle via RFC 6902 JSON Patch Executor**  
Das System validiert jeden LLM-Output als RFC 6902 JSON Patch Objekt und führt Schreiboperationen ausschließlich über den Executor aus. Das LLM hat keine direkten Schreibrechte auf das Artefakt.  
AK: (1) Patch-Objekte die syntaktisch ungültig sind oder Pfade enthalten die nicht im Template-Schema registriert sind werden abgelehnt — keine stille Akzeptanz. (2) Vor jeder Patch-Anwendung wird ein atomarer Snapshot erstellt. Bei Fehler in einem beliebigen Executor-Schritt erfolgt Restore auf diesen Snapshot. (3) Nach Patch-Anwendung prüft der Executor dass ausschließlich adressierte Pfade verändert wurden (Preservation-Check). Bei Abweichung: sofortiger Rollback auf Snapshot. (4) LLM-Outputs die gegen den Output-Kontrakt verstoßen werden nicht ausgeführt und lösen eine kontrollierte Fehlerbehandlung aus.  
Abhängigkeit: Abschnitt 5.7 (RFC 6902 Executor-Pipeline), Abschnitt 6.5.2 (Output-Kontrakt)

**FR-B-10: Versionswiederherstellung durch Nutzer**
Der Nutzer kann jederzeit eine frühere Artefaktversion als aktuellen Stand wiederherstellen.
AK: (1) Die Versionshistorie beider Artefakte ist für den Nutzer einsehbar. (2) Der Nutzer kann eine beliebige frühere Version auswählen und als aktuellen Stand setzen. (3) Die Wiederherstellung erzeugt eine neue Version mit Vermerk `restored_from: <version_id>` — die Versionshistorie wird nicht überschrieben. (4) Der Completeness-State wird nach Wiederherstellung aus dem restaurierten Artefakt rekonstruiert (s. FR-E-02).
Abhängigkeit: Abschnitt 5.2 (Versionierung), `[OFFEN: OP-03]`

---

## Gruppe C — Validierung & Konsistenz

**FR-C-01: Inkonsistenzerkennung**  
Das System erkennt logische Widersprüche innerhalb des Strukturartefakts oder zwischen Strukturartefakt und Algorithmusartefakt.  
AK: Erkannte Inkonsistenzen werden dem Nutzer mit Lokalisation (betroffene Slots) und Beschreibung des Widerspruchs gemeldet.

**FR-C-02: Widerspruchsauflösung durch Rückfrage**  
Erkannte Widersprüche werden nicht automatisch aufgelöst, sondern dem Nutzer zur Klärung vorgelegt.  
AK: Das System stellt eine konkrete Entscheidungsfrage mit mindestens zwei Optionen zur Auflösung.

**FR-C-03: EMMA-Kompatibilitätsprüfung**  
Alle Algorithmusschritte werden gegen den hinterlegten EMMA-Aktionskatalog geprüft.  
AK: Nicht abbildbare Schritte werden erkannt, markiert und dem Nutzer mit Alternativvorschlägen kommuniziert.

**FR-C-04: Validierung importierter Artefakte**  
Importierte Artefakte werden auf Schema-Konformität, Slot-Integrität und referenzielle Integrität geprüft.  
AK: Valide Artefakte werden übernommen. Invalide Artefakte werden abgelehnt mit einer strukturierten Fehlerbeschreibung.

**FR-C-05: Dokumentation von Spannungsfeldern**  
Prozessschritte, die zwar technisch automatisierbar sind, aber inhaltliche Risiken oder Unsicherheiten aufweisen, werden als Spannungsfelder dokumentiert.  
AK: Spannungsfelder sind im Artefakt als eigene Annotation im betroffenen Slot sichtbar und werden nicht still aufgelöst.

**FR-C-06: Operationalisierbarkeit als Completeness-Kriterium**  
Der Spezifikationsmodus verwendet die Operationalisierbarkeits-Checkliste (s. Abschnitt 5.4) als verbindliches Kriterium zur Bewertung der Vollständigkeit eines Algorithmusabschnitts.  
AK: (1) Ein Algorithmusabschnitt wird vom System erst auf `vollständig` gesetzt, wenn alle Pflichtfragen der Checkliste (Aktion, Wie, Endzustand, Timeout, Fehlerbehandlung) für jeden enthaltenen Aktionsschritt beantwortet sind. (2) Kontextabhängige Fragen (Datenquelle, Datenziel, UI-Element, Dialoge) werden vom System erkannt und ebenfalls eingefordert, wenn sie für den jeweiligen Schritt relevant sind. (3) Fehlende Antworten werden dem Nutzer mit konkreter Benennung der offenen Frage kommuniziert — kein stilles Setzen auf `vollständig`.  
Abhängigkeit: Abschnitt 5.4 (Operationalisierbarkeit), Abschnitt 5.6 (Completeness-State), FR-A-03 (Identifikation fehlender Informationen)

**FR-C-07: Nutzervalidierung von Slots**
Ein Slot darf ausschließlich durch explizite Nutzerbestätigung auf den Status `nutzervalidiert` gesetzt werden. Das System darf diesen Status nicht automatisch setzen.
AK: (1) Der Status `nutzervalidiert` wird ausschließlich als Reaktion auf eine explizite Bestätigungsaktion des Nutzers gesetzt — nie automatisch durch das System oder das LLM. (2) Das System fordert die Nutzerbestätigung aktiv an, bevor ein Slot als `nutzervalidiert` markiert wird. (3) Eine Massenbestätigung mehrerer Slots in einem Schritt ist zulässig, erfordert aber eine explizite Nutzeraktion die alle betroffenen Slots benennt. (4) Der Orchestrator ist die einzige Komponente die `nutzervalidiert` schreiben darf — nach expliziter Nutzerbestätigung im Dialog.
Abhängigkeit: Abschnitt 5.6 (Completeness-State), FR-D-01 (Orchestrator als zentraler Steuerknoten)

---

## Gruppe D — Orchestrierung & kognitive Modi

**FR-D-01: Orchestrator als zentraler Steuerknoten**  
Ein Orchestrator-Modul steuert, welcher kognitive Modus aktiv ist, verwaltet den Übergabekontext zwischen Modi und ist die einzige Komponente, die Schreiboperationen am Artefakt ausführt.  
AK: (1) Kein Moduswechsel und keine Artefaktänderung erfolgt ohne explizite Orchestrator-Entscheidung. (2) Kein anderer Systembestandteil — weder ein kognitiver Modus noch das LLM noch das UI — darf einen Moduswechsel direkt auslösen oder eine Schreiboperation am Artefakt direkt ausführen. Verstöße gegen diese Regel sind architektonisch auszuschließen, nicht nur konventionell zu vermeiden.  
Abhängigkeit: Abschnitt 6.2 (Orchestrator), Abschnitt 6.3 (Orchestrator-Zyklus)

**FR-D-02: Moderator-Modus**  
Ein dedizierter Moderator-Modus ist verfügbar für Eskalation, Phasenwechsel und Problemlösung.  
AK: Der Moderator erhält bei Aktivierung: aktuelle Artefakte (Read-Only), Systemzustand inkl. Completeness-State, letzte N Dialogturns.

**FR-D-03: Panik-Button-Eskalation**  
Der Nutzer kann jederzeit über einen Panik-Button den aktiven Modus unterbrechen und den Moderator aktivieren.  
AK: Der Moderator analysiert die Situation, schlägt eine Lösungsstrategie vor und reaktiviert einen Modus erst nach expliziter Nutzer-Zustimmung.

**FR-D-04: Kontextübergabe bei Moduswechsel**  
Bei jedem Moduswechsel übergibt der Orchestrator einen definierten Kontext an den neuen Modus.  
AK: Der empfangende Modus erhält mindestens: aktuelle Artefakte (Read-Only), Template-Schema, aktive Phase, Completeness-State, relevante Dialoghistorie (N Turns), ggf. Moderator-Lösungskontext.

**FR-D-05: Aktives Kontextmanagement**  
Das System verwaltet den LLM-Kontext aktiv nach der in Abschnitt 6.5 definierten Strategie.  
AK: Das Artefakt wird pro Turn vollständig als Read-Only-Lesekontext injiziert. Die Dialoghistorie wird auf N Turns begrenzt. Bei Kontextüberlauf wird die Priorisierungsregel aus 6.5.5 angewendet — ohne Informationsverlust am Artefakt.  
Abhängigkeit: Abschnitt 6.5 (Context Engineering)

**FR-D-06: Token-Monitoring und Prozesspartitionierung**
Das System überwacht kontinuierlich die Token-Größe der Artefakte im Verhältnis zum konfigurierten Modell-Tokenlimit.
AK: (1) Das System erkennt wenn die Artefaktgröße einen konfigurierten Schwellenwert überschreitet. (2) Bei Überschreitung wird der Nutzer aktiv informiert und eine Prozesspartitionierung vorgeschlagen. (3) Die Partitionierung wird nicht automatisch ausgeführt — der Nutzer bestätigt explizit. (4) Konkrete Schwellenwerte sind konfigurierbar ohne Code-Änderung. (5) Wird das Tokenlimit des konfigurierten Modells trotzdem überschritten, wird der laufende Turn abgebrochen. Der Nutzer erhält eine Fehlermeldung und die Handlungsoption Prozesspartitionierung. Der Systemzustand bleibt auf dem letzten validen Stand.
Abhängigkeit: Abschnitt 8.4 (Prozessumfang), `[OFFEN: OP-05]`

**FR-D-07: Fortschrittsmodell pro Modus**  
Jeder kognitive Modus meldet nach jedem Turn einen Phasenstatus (`in_progress` / `nearing_completion` / `phase_complete`) an den Orchestrator. Der Orchestrator berechnet zusätzlich den Slot-Zähler aus den Artefakten und schreibt beide Werte ins Working Memory.  
AK: Phasenstatus und Slot-Zähler sind nach jedem Turn im Working Memory aktuell und im UI sichtbar. Kein Prozentwert.  
Abhängigkeit: Abschnitt 5.6 (Completeness-State), Abschnitt 6.7 (Fortschrittsmodell)

---

## Gruppe E — Persistenz & Fehlerbehandlung

**FR-E-01: Automatische Speicherung**  
Der aktuelle Arbeitsstand (Artefakte + Systemzustand inkl. Completeness-State) wird automatisch gespeichert.  
AK: (1) Mindestens nach jeder abgeschlossenen Orchestrator-Zyklusrunde wird ein Snapshot persistiert (s. 7.3). (2) Der Speichervorgang ist atomar — entweder wird der vollständige Projektzustand gespeichert oder gar nichts. Ein partieller Zustand darf nicht entstehen. Bei Fehler während der Speicherung bleibt der letzte konsistente Stand erhalten.

**FR-E-02: Laden gespeicherter Projekte**  
Ein gespeichertes Projekt kann vollständig wiederhergestellt werden.  
AK: (1) Nach dem Laden entspricht der Systemzustand (Artefakte, Phase, Fortschritt, Completeness-State) dem gespeicherten Stand. (2) Bei einem Import von Artefakten ohne begleitendes Working Memory rekonstruiert der Orchestrator den Completeness-State vollständig aus den Artefakten — der primäre Completeness-Status liegt im Artefakt selbst (s. Abschnitt 5.6). (3) Die Rekonstruktion ist verlustfrei — kein Slot-Status darf dabei verloren gehen oder zurückgesetzt werden.

**FR-E-03: Wiederherstellung nach technischen Fehlern**  
Das System kann nach einem technischen Fehler (z.B. Browser-Absturz, LLM-Timeout) auf den letzten validen Zustand zurückgesetzt werden.  
AK: Kein Datenverlust bei Wiederherstellung eines persistierten Snapshots. Schreiboperationen die zum Zeitpunkt des Fehlers noch nicht vollständig ausgeführt waren werden nicht übernommen.

**FR-E-04: Fehlerbehandlung bei LLM-Fehlern**  
LLM-Fehler (Timeout, ungültige Ausgabe, Output-Kontrakt-Verletzung, Kontextüberlauf) werden abgefangen und dem Nutzer verständlich kommuniziert.  
AK: Bei LLM-Fehlern wird kein inkonsistenter Systemzustand erzeugt. Fehlgeschlagene Schreiboperationen lösen einen Rollback auf den letzten validen Artefaktstand aus. Der Nutzer erhält eine Handlungsoption (Wiederholen, Eskalieren).

**FR-E-05: Konfliktauflösung bei Completeness-State-Abweichung**
Bei Abweichung zwischen dem Completeness-Status im Artefakt und der aggregierten Map im Working Memory gilt der Artefaktstatus als primär.
AK: (1) Das System erkennt Abweichungen zwischen Artefakt-Completeness-Status und Working-Memory-Map beim Laden eines Projekts und nach jedem Persistenzvorgang. (2) Bei erkannter Abweichung wird die Working-Memory-Map automatisch aus dem Artefakt rekonstruiert — ohne Nutzerinteraktion. (3) Die Abweichung wird geloggt (s. 8.1.3). (4) Der Nutzer wird nicht mit technischen Details belastet — die Korrektur erfolgt still im Hintergrund.
Abhängigkeit: Abschnitt 5.6 (Completeness-State), FR-E-02 (Laden gespeicherter Projekte), Abschnitt 8.1.3 (Beobachtbarkeit)

**FR-E-06: Projektisolation**
Projekte sind vollständig voneinander isoliert.
AK: (1) Schreiboperationen auf einem Projekt haben keinen Einfluss auf andere Projekte. (2) Das Laden oder Wechseln eines Projekts verändert den Zustand anderer Projekte nicht. (3) Ein Fehler in einem Projekt führt nicht zum Datenverlust in anderen Projekten.
Abhängigkeit: FR-G-03 (Projektwechsel), s. 8.1.2 (NFR Projektisolation)

---

## Gruppe F — UI & Observability

**FR-F-01: Phasen- und Fortschrittsanzeige**  
Die aktuelle Systemphase und der Fortschritt innerhalb der Phase sind jederzeit sichtbar.  
AK: Phase und Fortschrittswert (aus FR-D-06, basierend auf Completeness-State) werden in Echtzeit im UI aktualisiert.

**FR-F-02: Debug-Modus**  
Ein Debug-Bereich zeigt interne Systemzustände an: aktiver kognitiver Modus, gesetzte Steuerungsflags, Fortschrittsmetriken, Working-Memory-Inhalte, Completeness-State, letzte ausgeführte Schreiboperation.  
AK: Der Debug-Bereich ist im Prototyp standardmäßig sichtbar und kann später deaktiviert werden.

**FR-F-03: Chatbereich und Artefaktbereich sind getrennt**  
Artefakte werden ausschließlich im Artefaktbereich dargestellt, nie im Chatbereich.  
AK: Der Chatbereich enthält keine Artefakt-Rohdaten. LLM-Outputs im Chatbereich bestehen ausschließlich aus der Nutzeräußerung — Schreiboperationen sind für den Nutzer nicht als Rohdaten sichtbar.

**FR-F-04: Unterstützte Eingabetypen**  
Der Chatbereich unterstützt: Texteingabe, Dokumentupload, Bildupload, Eventlog-Upload.  
AK: Alle vier Eingabetypen sind funktional. Nicht unterstützte Dateiformate werden mit einer Fehlermeldung abgelehnt.

**FR-F-05: Visuelle Markierung invalidierter Slots**
Invalidierte Slots beider Artefakte werden im Artefaktbereich visuell hervorgehoben.
AK: (1) Slots mit Status `invalidiert` sind im Artefaktbereich durch eine eindeutige visuelle Markierung erkennbar — unterscheidbar von Slots mit Status `ausstehend` oder `vollständig`. (2) Die Markierung wird sofort nach Setzen des Invalidierungsstatus aktualisiert ohne explizite Nutzeraktion. (3) Der Nutzer kann direkt aus der Markierung heraus den betroffenen Slot aufrufen.
Abhängigkeit: Abschnitt 5.5 (Referenzielle Integrität), FR-B-04 (Invalidierungslogik)
---

## Gruppe G — Projektverwaltung

**FR-G-01: Projektanlage**
Der Nutzer kann ein neues Projekt anlegen.
AK: Bei Anlage eines neuen Projekts werden Projektname (Pflicht) und Beschreibung (optional) erfasst. Das System erzeugt eine eindeutige Projekt-ID, initialisiert leere Artefakte mit Versionierung (s. FR-B-07) und setzt den Systemzustand auf Phase `exploration`. Das neue Projekt wird sofort persistiert.

**FR-G-02: Projektliste und Projektauswahl**
Der Nutzer sieht beim Start der Anwendung eine Übersicht aller vorhandenen Projekte und kann ein bestehendes Projekt laden.
AK: Die Projektliste zeigt mindestens: Projektname, Beschreibung, aktive Phase, letztes Änderungsdatum, Projektstatus. Ein Klick auf ein Projekt lädt es vollständig (s. FR-E-02).
`[OFFEN: OP-12]`

**FR-G-03: Projektwechsel**
Der Nutzer kann während einer Session zwischen Projekten wechseln.
AK: Vor dem Wechsel wird der aktuelle Projektstand automatisch gespeichert (s. FR-E-01). Nach dem Wechsel entspricht der Systemzustand vollständig dem geladenen Projekt.

**FR-G-04: Projektabschluss**
Der Nutzer kann ein Projekt explizit als abgeschlossen markieren.
AK: Das System zeigt vor dem Abschluss den aktuellen Stand (offene kritische Befunde, Artefaktvollständigkeit) und fordert eine explizite Bestätigung. Nach Bestätigung wird `projektstatus` auf `abgeschlossen` gesetzt und ein finaler Snapshot persistiert (s. Abschnitt 8.7).

----

## Offene Punkte — Funktionale Anforderungen

| ID | Anforderung | Thema | Beschreibung |
|---|---|---|---|
| OP-17 | FR-A-05 | Eventlog-Format | Das Eventlog-Format ist nicht definiert. FR-A-05 ist solange nicht vollständig testbar, bis das EMMA Recorder-Format bekannt ist. Im Prototyp als eingeschränkt verfügbar behandeln. |
| OP-18 | FR-A-07 | Automatisierbarkeits-Schwellenwert | Der Schwellenwert "mehr als ein nicht automatisierbarer Schritt" ist arbiträr. Im Implementierungsdesign überprüfen und ggf. konfigurierbar machen. |
| OP-19 | FR-B-06 | Markdown-Renderlogik | Die Transformation des JSON-Artefakts in Markdown ist nicht spezifiziert. Renderlogik muss im Architekturdesign definiert werden. |
| OP-20 | FR-D-04 | Wiederholte Output-Kontrakt-Verletzung | Verhalten bei wiederholter Vertragsverletzung durch das LLM ist nicht definiert. Eskalationsmechanismus (Retry-Limit, Moderator-Aktivierung) im Implementierungsdesign festlegen. |

# Abschnitt 5 — Prozessartefakte

---

## 5.1 Überblick

Das System erzeugt und pflegt drei Artefakte:

- **Explorationsartefakt** — Freitextbasierte Rohbeschreibung des Prozesses. Primärer Output der Explorationsphase und Input für die Strukturierung.
- **Strukturartefakt** — beschreibt die logische Prozessstruktur auf BPMN-ähnlicher Granularitätsebene
- **Algorithmusartefakt** — beschreibt die technische Umsetzung als ausführbarer Kontrollflussgraph für EMMA RPA

Alle drei Artefakte sind eigenständige, versionierte Objekte. Strukturartefakt und Algorithmusartefakt besitzen referenzielle Integrität zueinander. Das Explorationsartefakt ist der inhaltliche Vorläufer des Strukturartefakts — es wird in der Strukturierungsphase als Read-Only-Lesekontext verwendet.

Alle drei Artefakte besitzen als ersten Abschnitt eine **Prozesszusammenfassung** (Freitext, LLM-generiert).

### Grundprinzip: Externes Artefakt

Die Artefakte werden **außerhalb des LLM-Kontexts** verwaltet. Das System — nicht das LLM — ist alleinig verantwortlich für Persistenz, Versionierung und Schreibkontrolle.

Das LLM erhält die Artefakte pro Turn als **Read-Only-Lesekontext**. Es gibt sie **niemals vollständig zurück**. Ausgaben des LLM, die Artefakte betreffen, bestehen ausschließlich aus **chirurgischen Schreiboperationen auf benannte Slots** (s. 5.7).

Dieses Prinzip ist architektonisch nicht verhandelbar. Es eliminiert eine Klasse von LLM-bedingten Degradationseffekten strukturell:

| Effekt | Beschreibung | Eliminiert durch |
|---|---|---|
| Output-Verkürzung | LLMs brechen bei langen Dokumenten ab oder fassen zusammen | Artefakt wird nie vollständig ausgegeben |
| Over-Editing | LLMs verändern bei Volltext-Rückgabe systematisch auch nicht adressierte Abschnitte | Slot-Operationen beschränken Schreibzugriff |
| Kumulativer Drift | Wiederholte Volltext-Replikation degradiert Faktentreue progressiv | Artefakt wird extern verwaltet, nie repliziert |

---

## 5.2 Versionierung

Beide Artefakte werden versioniert.

Bei jeder inhaltlichen Änderung wird eine neue Version erzeugt. Die Versionshistorie bleibt vollständig erhalten. **Versionen werden ausschließlich vom System erzeugt** — nach erfolgreicher Validierung und Ausführung einer Schreiboperation. Das LLM löst keine Versionierung aus.

**Jede Artefaktversion enthält:**

| Feld | Beschreibung |
|---|---|
| `version_id` | Eindeutige, monoton steigende Versions-ID |
| `timestamp` | Zeitpunkt der Erzeugung |
| `created_by` | Auslösender kognitiver Modus |
| `slot_id` | Betroffener Slot dieser Version |
| `change_summary` | Kurzbeschreibung der Änderung (Freitext) |
| `artefakt_inhalt` | Der vollständige Artefaktinhalt dieser Version |

Der Nutzer kann jederzeit auf eine frühere Version zurücksetzen. Das Zurücksetzen aktiviert die gewählte Version als aktuellen Stand und erzeugt daraus eine neue Version mit Vermerk `restored_from: <version_id>`.

---

## 5.3 Explorationsartefakt

### Zweck

Das Explorationsartefakt dokumentiert das implizite Prozesswissen des Nutzers in freier, unstrukturierter Form. Es ist der primäre Output der Explorationsphase und dient dem Strukturierungsmodus als inhaltliche Grundlage.

Es ist bewusst einfach gehalten — kein EMMA-Bezug, keine Aktionstypen, keine referenzielle Integrität. Ziel ist die vollständige und nutzervalidierte Erfassung des Prozesswissens in natürlicher Sprache.

### Aufbau

Das Explorationsartefakt besteht aus zwei Teilen:

1. **Prozesszusammenfassung** — Freitext, für Fachanwender lesbar, LLM-generiert
2. **Explorations-Slots** — geordnete Liste von Freitext-Slots

### Explorations-Slot — Felder

| Feld | Typ | Pflicht | Beschreibung |
|---|---|---|---|
| `slot_id` | String | ja | Stabile, eindeutige ID. Entspricht der `slot_id` für Schreiboperationen. |
| `titel` | String | ja | Thema des Slots (z.B. "Prozessauslöser", "Beteiligte Systeme", "Ausnahmen") |
| `inhalt` | String | ja | Freitextinhalt — natürliche Sprache, keine formale Struktur |
| `completeness_status` | Enum | ja | `leer` / `teilweise` / `vollständig` / `nutzervalidiert` |

### Pflicht-Slots

Das Explorationsartefakt enthält folgende Pflicht-Slots die vom Explorationsmodus vollständig befüllt werden müssen:

| Slot | Beschreibung |
|---|---|
| `prozessausloeser` | Was löst den Prozess aus? Unter welchen Bedingungen startet er? |
| `prozessziel` | Was ist das Ziel des Prozesses? Woran erkennt man Erfolg? |
| `scope` | Was gehört zum Prozess, was nicht? |
| `beteiligte_systeme` | Welche Anwendungen, Tools, Datenquellen sind involviert? |
| `umgebung` | Betriebssystem, Netzwerk, relevante Rahmenbedingungen |
| `randbedingungen` | Einschränkungen, Abhängigkeiten, Voraussetzungen |
| `ausnahmen` | Bekannte Sonderfälle, Fehlerszenarien, Ausnahmebehandlungen |
| `prozesszusammenfassung` | Freitext-Zusammenfassung des Gesamtprozesses |

### Konsistenzregeln

- Kein Explorations-Slot darf durch das LLM direkt überschrieben werden. Änderungen erfolgen ausschließlich über RFC 6902 Schreiboperationen via Executor (s. 5.7). Die Pflicht-Slots sind als stabile JSON-Pfade adressierbar (z.B. `/prozessausloeser`, `/beteiligte_systeme`). Der Inhalt ist Freitext — die Struktur ist bekannt und schema-validierbar.
- Das Explorationsartefakt wird in der Strukturierungsphase als Read-Only-Lesekontext verwendet — es wird nicht weiter modifiziert.
- Alle Pflicht-Slots müssen den Status `nutzervalidiert` erreichen bevor die Explorationsphase als abgeschlossen gilt.

---

## 5.4 Strukturartefakt

### Zweck

Das Strukturartefakt beschreibt den Prozess auf logischer Ebene — vergleichbar mit einem BPMN-Prozessdiagramm, jedoch textbasiert und ohne grafische Darstellung.

Es ist das primäre Artefakt. Das Algorithmusartefakt wird aus ihm abgeleitet.

### Aufbau

Das Strukturartefakt besteht aus zwei Teilen:

1. **Prozesszusammenfassung** — Freitext, für Fachanwender lesbar, LLM-generiert
2. **Prozessstruktur** — geordnete Liste von Strukturschritten

Jeder Strukturschritt ist ein adressierbarer Slot mit einer stabilen `slot_id`. Das LLM schreibt ausschließlich auf einzelne Slots — niemals auf das Gesamtdokument.

### Strukturschritt — Felder

Ein Strukturschritt ist die atomare Einheit des Strukturartefakts.

| Feld | Typ | Pflicht | Beschreibung |
|---|---|---|---|
| `schritt_id` | String | ja | Stabile, eindeutige ID. Entspricht der `slot_id` für Schreiboperationen. Ändert sich nicht bei Umbenennung oder Bearbeitung. |
| `titel` | String | ja | Kurzer, sprechender Name des Schritts |
| `beschreibung` | String | ja | Fachliche Beschreibung in natürlicher Sprache |
| `typ` | Enum | ja | `aktion` / `entscheidung` / `schleife` / `ausnahme` |
| `reihenfolge` | Integer | ja | Position im Prozessablauf |
| `nachfolger` | Liste von `schritt_id` | ja | Ein oder mehrere Nachfolger (bei Entscheidungen: mehrere) |
| `bedingung` | String | nein | Nur bei Typ `entscheidung`: textuelle Beschreibung der Bedingung |
| `ausnahme_beschreibung` | String | nein | Nur bei Typ `ausnahme`: Beschreibung des Ausnahmefalls |
| `algorithmus_ref` | Liste von String | ja | Referenzen auf einen oder mehrere korrespondierende Algorithmusabschnitte (`abschnitt_id`). Mindestens eine Referenz ist Pflicht. |
| `algorithmus_status` | Enum | ja | `aktuell` / `invalidiert` / `ausstehend` |
| `completeness_status` | Enum | ja | `leer` / `teilweise` / `vollständig` / `nutzervalidiert` |
| `spannungsfeld` | String | nein | Freitextbeschreibung eines dokumentierten Spannungsfelds oder Risikos |

### Konsistenzregeln

- Jeder Strukturschritt muss einen eindeutigen `schritt_id` besitzen.
- Jeder Strukturschritt muss mindestens eine `algorithmus_ref` besitzen. Mehrere Referenzen sind zulässig (1:n).
- Der `algorithmus_status` wird vom System automatisch auf `invalidiert` gesetzt — gemäß Invalidierungsregel (s. Abschnitt 5.5).
- Ein Prozess muss genau einen Startschritt und mindestens einen Endschritt besitzen.
- Kein Strukturschritt darf durch das LLM direkt überschrieben werden. Änderungen erfolgen ausschließlich über validierte Schreiboperationen (s. 5.7).

---

## 5.5 Algorithmusartefakt

### Zweck

Das Algorithmusartefakt beschreibt die technische Umsetzung des Prozesses.

Es ist hinreichend präzise, um direkt als Kontrollflussgraph in EMMA RPA umgesetzt zu werden.

Jeder Algorithmusabschnitt entspricht einem oder mehreren Strukturschritten und besteht aus einer Sequenz von EMMA-Aktionen.

### Aufbau

Das Algorithmusartefakt besteht aus zwei Teilen:

1. **Prozesszusammenfassung** — Freitext, technisch angereichert, LLM-generiert
2. **Algorithmusabschnitte** — geordnete Liste von Abschnitten

Jeder Algorithmusabschnitt ist ein adressierbarer Slot mit einer stabilen `abschnitt_id`. Das LLM schreibt ausschließlich auf einzelne Slots — niemals auf das Gesamtdokument.

### Algorithmusabschnitt — Felder

| Feld | Typ | Pflicht | Beschreibung |
|---|---|---|---|
| `abschnitt_id` | String | ja | Stabile, eindeutige ID. Entspricht der `slot_id` für Schreiboperationen. |
| `struktur_ref` | String | ja | Referenz auf den korrespondierenden Strukturschritt (`schritt_id`) |
| `titel` | String | ja | Entspricht in der Regel dem Titel des Strukturschritts |
| `status` | Enum | ja | `aktuell` / `invalidiert` / `ausstehend` |
| `completeness_status` | Enum | ja | `leer` / `teilweise` / `vollständig` / `nutzervalidiert` |
| `aktionen` | Liste | ja | Geordnete Sequenz von EMMA-Aktionen (s. 5.5) |

### EMMA-Aktion — Felder

| Feld | Typ | Pflicht | Beschreibung |
|---|---|---|---|
| `aktion_id` | String | ja | Eindeutige ID innerhalb des Abschnitts |
| `aktionstyp` | Enum | ja | Ein Wert aus dem EMMA-Aktionskatalog (s. Abschnitt 8.3) |
| `parameter` | Key-Value | ja | Aktionsspezifische Parameter |
| `nachfolger` | String | ja | `aktion_id` der nächsten Aktion, oder `END` |
| `emma_kompatibel` | Boolean | ja | Ergebnis der EMMA-Kompatibilitätsprüfung |
| `kompatibilitaets_hinweis` | String | nein | Begründung bei `emma_kompatibel = false` |

### Konsistenzregeln

- Jeder Algorithmusabschnitt muss eine valide `struktur_ref` besitzen.
- Der `status` eines Abschnitts wird vom System automatisch auf `invalidiert` gesetzt, wenn der referenzierte Strukturschritt geändert wird.
- Alle `aktionstyp`-Werte müssen im EMMA-Aktionskatalog enthalten sein.
- Kein Algorithmusabschnitt darf durch das LLM direkt überschrieben werden. Änderungen erfolgen ausschließlich über validierte Schreiboperationen (s. 5.7).

### Operationalisierbarkeit — Definition

Ein Algorithmusabschnitt gilt als operationalisierbar, wenn für jeden enthaltenen Aktionsschritt folgende Fragen beantwortet sind:

| Frage | Beschreibung |
|---|---|
| **Welche Aktion?** | Was soll getan werden — konkretes Ziel der Aktion |
| **Wie genau?** | Mechanismus, Methode, UI-Interaktion, Computer Vision, Befehl |
| **Erwarteter Endzustand?** | Woran ist erkennbar, dass der Schritt erfolgreich war |
| **Timeout?** | Wie lange wird auf den Endzustand gewartet |
| **Fehlerbehandlung?** | Was passiert bei Fehler — wie wird er erkannt, was folgt daraus |
| **Datenquelle?** | Woher kommen Daten — Variable, Pfad, Format |
| **Datenziel?** | Wohin gehen Daten — Ziel, Pfad, Format |
| **UI-Element?** | Wie wird das Element identifiziert — ID, Name, Klasse, XPath, CV-Template |
| **Dialoge?** | Wie werden Popups, Warnungen und Bestätigungen behandelt |

Die ersten fünf Fragen (Aktion, Wie, Endzustand, Timeout, Fehlerbehandlung) sind **Pflicht** für jeden Aktionsschritt. Die weiteren Fragen sind kontextabhängig — sie müssen beantwortet sein, wenn sie für den jeweiligen Schritt relevant sind.

Der Spezifikationsmodus verwendet diese Checkliste als Leitfaden: Ein Algorithmusabschnitt wird erst auf `vollständig` gesetzt, wenn alle relevanten Fragen beantwortet sind.

### Beispiel

**Nicht operationalisierbar:**
Öffne Notepad, trage die Zahl ein, speichere.

**Operationalisierbar:**
1. Shell-Befehl: notepad.exe ausführen. Alternativ: Icon per CV auf Desktop lokalisieren, Doppelklick.
2. Warte auf Fenster "Unbenannt - Editor" (max. 5s). Prüfe per CV ob Fenster sichtbar.
3. Bei Timeout: Fehler "Notepad nicht gestartet" — Prozess abbrechen.
4. Fokus auf Textfeld (Klasse: "Edit", Index: 0).
5. Eingabe: Variable {result} — alternativ Ctrl+V wenn Wert im Clipboard.
6. Ctrl+S — warte auf "Speichern unter"-Dialog.
7. Dateiname eingeben: C:\Output\ergebnis.txt in korrektes Feld (Tab-Navigation oder direkte Feldidentifikation).
8. Klick "Speichern" oder Tab+Enter.
9. Falls Überschreiben-Dialog erscheint: Klick "Ja" oder Enter.

---

## 5.5 Referenzielle Integrität

Strukturartefakt und Algorithmusartefakt sind über ein bidirektionales Referenzpaar verbunden:

```
Strukturschritt.algorithmus_ref  →  Algorithmusabschnitt.abschnitt_id
Algorithmusabschnitt.struktur_ref  →  Strukturschritt.schritt_id
```

**Invariante:** Zu jedem Strukturschritt existiert mindestens ein Algorithmusabschnitt. Ein Strukturschritt kann mehrere Algorithmusabschnitte haben (1:n). Jeder Algorithmusabschnitt referenziert genau einen Strukturschritt.

**Invalidierungsregel:**
Eine Invalidierung wird ausgelöst wenn eines der folgenden Felder eines Strukturschritts geändert wird: `beschreibung`, `typ`, `bedingung`, `ausnahme_beschreibung`. Änderungen an `titel`, `reihenfolge`, `nachfolger` und `spannungsfeld` lösen keine Invalidierung aus.
Bei Invalidierung:
- `Strukturschritt.algorithmus_status` → `invalidiert`
- `Algorithmusabschnitt.status` → `invalidiert` — für **alle** Algorithmusabschnitte die diesen Strukturschritt referenzieren

**Löschung eines Strukturschritts:**
Wird ein Strukturschritt via `remove`-Operation gelöscht, gilt folgende Regel:
(1) Der Orchestrator prüft vor Ausführung der Operation ob referenzierte Algorithmusabschnitte existieren.
(2) Falls ja: Der Nutzer wird explizit gewarnt — mit Auflistung der betroffenen Algorithmusabschnitte.
(3) Nach Nutzerbestätigung wird die Löschoperation ausgeführt. Alle referenzierten Algorithmusabschnitte werden auf `invalidiert` gesetzt.
(4) Die Löschung wird nicht automatisch blockiert — der Nutzer hat das letzte Wort.

Invalidierte Abschnitte werden im Artefaktbereich visuell markiert (s. FR-F-05) und müssen durch den Spezifikationsmodus neu generiert oder manuell bestätigt werden.

---
## 5.6 Completeness-State

### Primärer Speicherort: Artefakt

Der Completeness-Status wird pro Slot direkt im Artefakt gehalten — als Pflichtfeld `completeness_status` in jedem Strukturschritt (s. 5.3) und jedem Algorithmusabschnitt (s. 5.4). Das Artefakt ist damit self-contained: Es trägt seinen eigenen Vollständigkeitsstatus und ist ohne Working Memory vollständig interpretierbar.

| Status | Bedeutung |
|---|---|
| `leer` | Slot wurde noch nicht beschrieben |
| `teilweise` | Slot enthält Information, ist aber noch nicht vollständig |
| `vollständig` | Slot ist aus Systemsicht vollständig befüllt |
| `nutzervalidiert` | Nutzer hat den Inhalt explizit bestätigt |

### Abgeleiteter Speicherort: Working Memory

Das Working Memory hält zusätzlich eine aggregierte Map aller Slot-Status (`completeness_state`: slot_id → Status). Diese Map ist eine abgeleitete Zusammenfassung — sie wird vom Orchestrator nach jeder Schreiboperation aus den Artefakten aktualisiert und dient ausschließlich der schnellen Gesprächssteuerung der kognitiven Modi.

**Invariante:** Der Completeness-Status im Working Memory ist immer konsistent mit dem Status in den Artefakten. Bei Abweichung gilt der Artefaktstatus als primär.

### Konsequenz für Export und Import

Ein exportiertes Artefakt trägt den vollständigen Completeness-Status aller Slots. Ein nachgelagertes System kann den Vollständigkeitsstand ohne Working Memory lesen. Bei einem Reimport rekonstruiert der Orchestrator die Working-Memory-Map aus den Artefakten.

---

## 5.7 Schreiboperationen — RFC 6902 JSON Patch

Das LLM kommuniziert Artefaktänderungen ausschließlich als RFC 6902 JSON Patch Objekt. Es gibt das Artefakt nie vollständig zurück und führt keine Schreiboperationen selbst aus.

Der **Executor** ist das interne Modul des Orchestrators das Patch-Objekte entgegennimmt, validiert und ausführt. Er ist kein eigenständiger Systembestandteil — er ist die interne Schreibmechanik des Orchestrators. Nach außen bleibt der Orchestrator die einzige Komponente mit Schreibzugriff auf die Artefakte.

### Erlaubte Operationen

| Operation | Beschreibung |
|---|---|
| `replace` | Slot-Inhalt ersetzen |
| `add` | Neuen Eintrag hinzufügen |
| `remove` | Slot entfernen |

Slots werden über stabile Pfade adressiert (z.B. `/trigger_conditions`, `/steps/2`) — nicht über Zeilennummern oder Textmuster.

### Executor-Pipeline

Nach Eingang eines Patch-Objekts führt der Executor sequenziell aus:

| Schritt | Beschreibung |
|---|---|
| 1. Formale Validierung | Ist das Patch-Objekt syntaktisch gültiges RFC 6902? Sind alle Pfade im Template-Schema registriert? Enthält das Objekt ausschließlich erlaubte Operationen (`replace`, `add`, `remove`)? |
| 2. Snapshot | Atomarer JSON-Snapshot des aktuellen Artefaktzustands vor jeder Änderung |
| 3. Patch-Anwendung | Standard JSON-Patch-Bibliothek führt die Operationen aus |
| 4. Preservation-Check | Nur adressierte Pfade wurden verändert — alle anderen Slots unverändert |
| 5. Versionierung | Neuer Versionsstand mit Zeitstempel und auslösender Operation |

Bei Fehler in einem beliebigen Schritt: Restore auf Snapshot aus Schritt 2. Kein stiller Datenverlust.

### Bibliotheksimplementierungen

| Sprache | Bibliothek |
|---|---|
| Python | `jsonpatch` |
| JavaScript | `fast-json-patch` |
| .NET | `JsonPatch` |
| Java | `zjsonpatch` |

### Begründung

Die Trennung von Schreibabsicht (LLM) und Schreibausführung (Executor) ist das zentrale Sicherheitsprinzip. Das LLM kann das Artefakt durch fehlerhafte Ausgabe nicht beschädigen. RFC 6902 löst das Lokalisierungsproblem strukturell über stabile Pfade statt fragiler Text-Matches.

Alternativen wurden geprüft und verworfen:
- **Unified Diffs** — brechen bei Kontext-Drift (Zeilennummern stimmen nach mehreren Turns nicht mehr)
- **Search/Replace** — erfordert zeichengenaue Reproduktion; Whitespace-Abweichungen führen zu "String not found"-Fehlern
- **Freies JSON mit custom Feldern** — erfordert eigenen Parser und ist anfällig für Slot-ID-Halluzination

---

## 5.8 Template-Schema

### Zweck

Das Template-Schema ist die maschinenlesbare Beschreibung der Artefakt-Struktur. Es definiert alle gültigen Slot-Pfade, Feldtypen, Pflicht/Optional-Status, erlaubte Werte bei Enums und Abhängigkeiten zwischen Slots.

Es erfüllt zwei Funktionen:
1. **Validierungsgrundlage für den Executor** — jede RFC 6902 Schreiboperation wird vor Ausführung gegen das Template-Schema geprüft. Pfade die nicht im Schema registriert sind werden abgelehnt (s. 5.7).
2. **Orientierungsrahmen für das LLM** — das Template-Schema wird jedem kognitiven Modus als Pflichtbestandteil des Kontexts übergeben (s. 6.5.3). Es verhindert die Halluzination ungültiger Pfade.

### Eigenschaften

- **Statisch** — das Template-Schema wird zur Entwicklungszeit definiert und ändert sich nicht zur Laufzeit.
- **Vom Entwickler gepflegt** — es ist kein Laufzeit-Artefakt und wird nicht vom System generiert.
- **Artefakt-übergreifend** — es beschreibt alle drei Artefakte (Explorations-, Struktur- und Algorithmusartefakt) in einem gemeinsamen Schema.

### Abgrenzung

Die konkrete Implementierung des Template-Schemas (Format, Speicherort, Versionierung) ist Teil des Architekturdesigns.

---

## 5.9 Offene Punkte

| ID | Thema | Beschreibung |
|---|---|---|
| OP-01 | JSON-Schema Artefakte | Formale Schemadefinition aller drei Artefakte inkl. aller Slot-IDs |
| OP-02 | EMMA-Parameterdefinition | Vollständige Parameterliste pro Aktionstyp muss definiert werden (s. 8.3) |
| OP-03 | Versionshistorie im UI | (1) Wie navigiert der Nutzer durch Versionen — Liste, Timeline, Diff-Ansicht? (2) Sieht der Nutzer alle Versionen oder nur einen konfigurierbaren Ausschnitt? (3) Wer erzeugt `change_summary` pro Version — LLM, System automatisch, oder Kombination? |
| OP-04 | Maximale Versionszahl | Gibt es ein Limit für gespeicherte Versionen, oder unbegrenzt? |
| OP-05 | Prozesspartitionierung | Ab welchem Token-Schwellenwert wird Partitionierung ausgelöst? Konkrete Grenzwerte im Architekturdesign definieren (s. 8.4) |

# Abschnitt 6 — Systemsteuerung

---

## 6.1 Systemphasen

Das System arbeitet in vier klar definierten Phasen. Im Prototyp werden diese linear durchlaufen. Ein Rücksprung in eine frühere Phase muss architektonisch vorbereitet werden, aber im Prototyp ausschließlich über den Moderator (Panik-Button) auslösbar — nicht als reguläre Nutzerfunktion.

### 6.1.0 Systemstart

Beim Start der Anwendung unterscheidet das System zwei Fälle:

**Neues Projekt:**
Der Orchestrator initialisiert alle drei Artefakte im Leerstand und aktiviert den Moderator. Der Moderator begrüßt den Nutzer, erklärt kurz das Vorgehen und leitet ihn in die Explorationsphase ein. Nach Bestätigung durch den Nutzer aktiviert der Orchestrator den Explorationsmodus.

**Bestehendes Projekt laden:**
Der Orchestrator lädt den persistierten Projektzustand vollständig (s. FR-E-02) und aktiviert den Moderator. Der Moderator rekonstruiert den aktuellen Stand für den Nutzer — aktive Phase, Fortschritt, offene Punkte — und schlägt vor, wo die Arbeit fortgesetzt wird. Nach Bestätigung durch den Nutzer aktiviert der Orchestrator den zuletzt aktiven Modus.

In beiden Fällen gilt: Der erste aktive Modus nach dem Start wird ausschließlich vom Orchestrator aktiviert — nach expliziter Nutzerbestätigung durch den Moderator.


### 6.1.1 Phasendefinitionen

| Phase | Ziel | Primärer Modus | Output |
|---|---|---|---|
| **Exploration** | Implizites Prozesswissen erfassen, grobes Prozessverständnis herstellen. Analyse des Ziels, der Anfangsbedingungen, des Scope, der Randbedingungen, der involvierten Systeme, des OS und der allgemeinen Umgebung. | Explorationsmodus | Explorationsartefakt (vollständig, nutzervalidiert) |
| **Strukturierung** | Prozess in logische Schritte zerlegen, Entscheidungslogik modellieren. Granularitätsebene: BPMN. | Strukturierungsmodus | Strukturartefakt (vollständig, nutzervalidiert) |
| **Spezifikation** | Jeden Strukturschritt technisch präzisieren, EMMA-Aktionen zuordnen | Spezifikationsmodus | Algorithmusartefakt (vollständig, nutzervalidiert) |
| **Validierung** | Konsistenz, Vollständigkeit und EMMA-Kompatibilität prüfen | Validierungsmodus | Validierungsbericht |

### 6.1.2 Phasenwechsel

Ein Phasenwechsel erfolgt in folgenden Schritten:

1. Der aktive kognitive Modus meldet via Flag `phase_complete` an den Orchestrator, wenn das Phasenziel erreicht ist.
2. Der Orchestrator aktiviert den Moderator, der dem Nutzer den Phasenwechsel vorschlägt und eine Zusammenfassung des Erreichten präsentiert.
3. Der Nutzer bestätigt den Wechsel. Erst dann aktiviert der Orchestrator den Modus der nächsten Phase.
4. Wenn der Nutzer noch Klärungsbedarf beim aktuellen Modus verspürt, reaktiviert der Orchestrator diesen Modus. `phase_complete` wird deaktiviert. Der reaktivierte Modus erhält die Nutzerwünsche als Kontext und muss diese abarbeiten, bevor er erneut `phase_complete` setzen darf.

Ein Phasenwechsel ohne Nutzerbestätigung findet nicht statt.

### 6.1.3 Validierungs-Korrekturschleife

Die Validierungsphase hat eine Sonderrolle: Sie kann mehrfach durchlaufen werden, abwechselnd mit dem Spezifikationsmodus, bis keine kritischen Befunde mehr offen sind oder der Nutzer den Abschluss explizit bestätigt.

**Ablauf:**

1. Der Validierungsmodus läuft durch und setzt `phase_complete`. Der Orchestrator aktiviert den Moderator.
2. Der Moderator präsentiert den Validierungsbericht und bespricht die Befunde mit dem Nutzer.
3. Der Nutzer entscheidet:

| Entscheidung | Konsequenz |
|---|---|
| Befunde beheben | Orchestrator aktiviert Spezifikationsmodus mit Validierungsbericht als Kontext. Spezifikationsmodus arbeitet die Befunde ab. Nach Abschluss setzt er `phase_complete` — der Orchestrator aktiviert erneut den Validierungsmodus. |
| Abschluss trotz offener Befunde | Moderator zeigt explizite Warnung über offene kritische Befunde. Bei Nutzerbestätigung wird das Projekt abgeschlossen (s. Abschnitt 8.7). |
| Abbrechen | Projekt bleibt im Status `aktiv`. Nutzer kann später fortfahren. |

**Invariante:** Der Wechsel zwischen Validierungsmodus und Spezifikationsmodus erfolgt ausschließlich über den Moderator — nie direkt. Der Nutzer bestätigt jeden Wechsel explizit.

**Anzahl der Durchläufe:** Nicht begrenzt. Die Schleife endet ausschließlich durch Nutzerentscheidung — nicht automatisch durch das System.

### 6.1.4 Rücksprung in frühere Phasen

Im Prototyp ist ein Rücksprung ausschließlich über den Moderator möglich, der via Panik-Button aktiviert wird.

Der Moderator kann nach Analyse der Situation einen Rücksprung vorschlagen. Bei Nutzerbestätigung versetzt der Orchestrator das System in die Zielphase zurück.

**Konsequenzen eines Rücksprungs:**

| Rücksprung nach | Konsequenz für Artefakte |
|---|---|
| Exploration | Strukturartefakt und Algorithmusartefakt bleiben erhalten, werden aber als `ausstehend` markiert. Completeness-Status aller Slots bleibt erhalten. |
| Strukturierung | Algorithmusartefakt bleibt erhalten. Ändert der Strukturierungsmodus einen Strukturschritt, erkennt der Orchestrator dies deterministisch und markiert alle referenzierten Algorithmusabschnitte als `invalidiert` (s. FR-B-04, s. 6.3 Schritt 8). |

Die Artefakte werden nicht gelöscht. Durch die Versionierung (s. Abschnitt 5.2) ist der Stand vor dem Rücksprung jederzeit wiederherstellbar.

> **Prototyp-Einschränkung:** Rücksprünge sind im Prototyp nicht als reguläre Navigation implementiert. Die Architektur lässt dies jedoch offen für spätere Erweiterung.

---

## 6.2 Orchestrator

Der Orchestrator ist die zentrale Steuerungskomponente des Systems. Er ist die einzige Komponente, die Modi aktiviert und deaktiviert.

### Eigenschaften

- Arbeitet **deterministisch und regelbasiert**
- Verwendet **keine Sprachmodelle**
- Hat Schreibzugriff auf das Working Memory
- Ist die einzige Komponente die Schreiboperationen am Artefakt ausführt — nach innen delegiert er diese Aufgabe an den **Executor** als internes Modul (s. Abschnitt 5.7). Nach außen ist der Orchestrator der einzige sichtbare Akteur — der Executor ist eine interne Implementierungsdetail des Orchestrators, keine eigenständige Systemkomponente.

### Verantwortlichkeiten

- Empfang und Auswertung von Steuerungsflags der kognitiven Modi (s. 6.4.1)
- Entscheidung über Moduswechsel (s. 6.3 Moduswechsel-Logik)
- Zusammenstellung des Kontexts für den nächsten Modus (s. 6.5)
- Validierung und Ausführung von LLM-Schreiboperationen auf Artefakt-Slots via Executor (s. 5.7)
- Persistierung des Systemzustands nach jedem Zyklus (s. 7.3)
- Initiierung aller Turns — alles geht über den Orchestrator (s. 6.3)

---

## 6.3 Orchestrator-Zyklus

Der Orchestrator arbeitet turnbasiert. Jeder Nutzerturn durchläuft den folgenden Zyklus vollständig:

| Schritt | Beschreibung |
|---|---|
| 1. Input empfangen | Nutzerinput (Text, Datei, Button-Event) wird entgegengenommen |
| 2. Zustand aktualisieren | Working Memory wird mit neuem Input aktualisiert |
| 3. Flags auswerten | Steuerungsflags des aktiven Modus werden gelesen und ausgewertet (s. 6.4.1) |
| 4. Modus bestimmen | Auf Basis der Flags und der aktuellen Phase wird der aktive Modus bestätigt oder gewechselt (s. Moduswechsel-Logik) |
| 5. Context Engineering | Kontext für den Modusaufruf wird zusammengestellt (s. 6.5) |
| 6. Modus aufrufen | Der aktive Modus wird mit dem zusammengestellten Kontext aufgerufen |
| 7. Output verarbeiten | Modusantwort wird ausgewertet: Schreiboperationen werden via Executor validiert und ausgeführt (s. 5.7), neue Flags werden gelesen |
| 8. Invalidierungen auslösen | Der Orchestrator prüft deterministisch ob die ausgeführte Schreiboperation einen Strukturschritt betraf. Falls ja: Der Executor wird beauftragt alle referenzierten Algorithmusabschnitte auf `invalidiert` zu setzen (s. 5.5 Invalidierungsregel). |
| 9. Completeness-State aktualisieren | Der Orchestrator rekonstruiert die Completeness-State-Map im Working Memory aus den aktuellen Artefakten — das Working Memory ist abgeleitet, das Artefakt ist primär (s. 5.6) |
| 10. Fortschritt bewerten | Phasenstatus und Slot-Zähler aus Modus-Output ins Working Memory schreiben (s. 6.7) |
| 11. Zustand persistieren | Aktueller Systemzustand wird gespeichert (s. 7.3) |

### Moduswechsel-Logik

Der Orchestrator wechselt den aktiven Modus ausschließlich in folgenden Fällen:

| Auslöser | Aktion |
|---|---|
| Flag `phase_complete` | Moderator aktivieren → Phasenwechsel nach Nutzerbestätigung |
| Flag `escalate` | Moderator aktivieren (Panik-Button oder interner Eskalationsbedarf) |
| Flag `blocked` | Moderator aktivieren zur Klärung |
| Moderator gibt Kontrolle zurück | Vorherigen oder neu definierten Modus aktivieren |

Ohne eines dieser Signale bleibt der aktive Modus unverändert.

---

## 6.4 Working Memory

Das Working Memory ist der zentrale Zustandsspeicher des Systems. Das Working Memory ist der operative Zustandsspeicher des laufenden Dialogs. Der primäre Zustand liegt in den Artefakten — das Working Memory ist abgeleitet und wird bei Wiederherstellung aus ihnen rekonstruiert (s. 5.6, FR-E-05).

Der Orchestrator hat Lese- und Schreibzugriff. Kognitive Modi haben ausschließlich Lesezugriff — sie schreiben weder ins Working Memory noch direkt in die Artefakte. Flags und Phasenstatus sind Teil des strukturierten Modus-Outputs den der Orchestrator auswertet und verarbeitet (s. 6.3).

### Felder

| Feld | Typ | Beschreibung |
|---|---|---|
| `aktive_phase` | Enum | Aktuelle Systemphase: `exploration` / `strukturierung` / `spezifikation` / `validierung` |
| `aktiver_modus` | Enum | Aktuell aktiver kognitiver Modus |
| `vorheriger_modus` | Enum | Zuletzt aktiver Modus vor einem Moduswechsel (für Rückgabe nach Moderator) |
| `phasenstatus` | Enum | Fortschrittsstatus der aktuellen Phase, gemeldet vom aktiven kognitiven Modus: `in_progress` / `nearing_completion` / `phase_complete` |
| `befuellte_slots` | Integer | Anzahl der Slots mit Status `teilweise`, `vollständig` oder `nutzervalidiert` im aktuellen Artefakt — wird vom Orchestrator nach jeder Schreiboperation aktualisiert |
| `bekannte_slots` | Integer | Gesamtzahl der aktuell im Template-Schema definierten Slots — wird vom Orchestrator nach jeder Schreiboperation aktualisiert |
| `strukturartefakt_ref` | String | Referenz auf aktuelle Version des Strukturartefakts |
| `algorithmusartefakt_ref` | String | Referenz auf aktuelle Version des Algorithmusartefakts |
| `completeness_state` | Map (slot_id → Status) | Aggregierte Zusammenfassung des Befüllungsstatus aller Slots beider Artefakte — abgeleitet aus den Artefakten, nicht primär. Wird vom Orchestrator nach jeder Schreiboperation aktualisiert. Primärer Speicherort des Completeness-Status ist das Artefakt selbst (s. Abschnitt 5.6). |
| `spannungsfelder` | Liste von String | Dokumentierte Spannungsfelder aus dem laufenden Dialog |
| `letzter_dialogturn` | Integer | Index des letzten verarbeiteten Dialogturns |
| `projektstatus` | Enum | `aktiv` / `pausiert` / `abgeschlossen` |
| `explorationsartefakt_ref` | String | Referenz auf aktuelle Version des Explorationsartefakts |

Weitere Felder können in späteren Phasen definiert werden wenn sich Notwendigkeit ergibt.

### 6.4.1 Steuerungsflags - NICHT im working memory

Steuerungsflags sind zyklus-lokale Signale — sie werden vom kognitiven Modus als Teil seines Outputs zurückgegeben, vom Orchestrator im selben Zyklus ausgewertet und danach verworfen. Sie werden nicht ins Working Memory geschrieben und nicht persistiert.

Das ist eine bewusste Entscheidung: Der Orchestrator-Zyklus ist atomar (s. 6.3) — ein unterbrochener Zyklus wird verworfen, nicht fortgesetzt. Flags aus einem unterbrochenen Zyklus wären beim Wiederherstellen bedeutungslos und könnten den Orchestrator irreführen. Debug-Bedarf wird durch Logging abgedeckt (s. 8.1.3) — nicht durch Persistenz.

**Flags sind Pflichtbestandteil jedes Modus-Systemprompts.** Jeder Modus-Systemprompt muss die vollständige Flag-Liste, die Auslösekriterien und die Erwartung enthalten, dass der Modus diese Flags aktiv und konsequent setzt. Ohne explizite Instruktion im Systemprompt ist nicht sichergestellt dass das LLM die Flags korrekt und konsistent verwendet.

Die folgende Liste ist ein initialer Vorschlag und wird im Zuge der Implementierung erweitert.

| Flag | Bedeutung | Auslösekriterium |
|---|---|---|
| `phase_complete` | Die aktuelle Phase ist abgeschlossen | Alle Abbruchbedingungen des aktiven Modus sind erfüllt (s. jeweilige Modus-Beschreibung in 6.6) |
| `needs_clarification` | Der Modus benötigt Nutzerklärung bevor er fortfahren kann | Eine offene Frage blockiert den Fortschritt, kann aber durch Nutzerinput aufgelöst werden — kein strukturelles Problem |
| `escalate` | Der Modus empfiehlt Übergabe an den Moderator | Situation erfordert menschliche Abwägung oder Entscheidung die über den Aufgabenbereich des Modus hinausgeht |
| `blocked` | Der Modus kann nicht fortfahren | Unlösbarer Widerspruch, fehlende Information die nicht durch Nachfrage beschaffbar ist, oder strukturelles Problem das den Prozessfortschritt verhindert |
| `artefakt_updated` | Schreiboperationen wurden ausgegeben | Mindestens eine Schreiboperation ist im aktuellen Output enthalten |
| `validation_failed` | Validierung hat kritische Befunde ergeben | Nur Validierungsmodus: mindestens ein Befund mit Schweregrad `kritisch` im Validierungsbericht |

> **Hinweis:** Diese Liste ist nicht abschließend. Weitere Flags werden im Architektur- und Implementierungsdesign ergänzt.
---

## 6.5 Context Engineering

Context Engineering bezeichnet die gezielte Zusammenstellung des Kontexts für jeden Sprachmodellaufruf. Der Orchestrator ist verantwortlich für diese Zusammenstellung.

### 6.5.1 Prinzip

Das System übergibt **nicht den gesamten Dialogverlauf** an das Modell. Der Kontext wird pro Modusaufruf aktiv kuratiert, um Tokenlimits einzuhalten und Relevanz zu maximieren.

Die Artefakte werden pro Turn vollständig als Read-Only-Lesekontext injiziert. Es ist Lektüre — kein Schreibziel. Das LLM selbst hat keine Schreibrechte, es gibt vorgeschlagene Schreiboperationen zum dem zur Phase passenden Artefakt aus. (s. 6.5.2).

### 6.5.2 Output-Kontrakt

Der Output-Kontrakt ist Bestandteil jedes System-Prompts und für alle kognitiven Modi verbindlich.

**Das LLM gibt pro Turn ausschließlich aus:**
- eine Nutzeräußerung (Frage, Rückmeldung, Zusammenfassung) — als Freitext
- null oder mehr Schreiboperationen auf benannte Artefakt-Slots — im Format gemäß 5.7
- einen Steuerungsoutput — bestehend aus Phasenstatus (`in_progress` / `nearing_completion` / `phase_complete`) und null oder mehr Flags (s. 6.4.1)

**Das LLM gibt niemals aus:**
- das vollständige Artefakt oder Teile davon als Freitext
- unstrukturierten Text, der Artefaktinhalte repliziert oder paraphrasiert
- direkte Schreibbefehle ans Working Memory — der Orchestrator ist die einzige Komponente die ins Working Memory schreibt

Der Orchestrator validiert jeden LLM-Output gegen diesen Kontrakt vor der Weiterverarbeitung. Outputs, die gegen den Kontrakt verstoßen, werden nicht ausgeführt und lösen eine kontrollierte Fehlerbehandlung aus.
Der Nutzer muss Kenntnis erhalten von dem Fehler. In der Prototyp Phase ist keine weitere Fehlerbehandlung (retry etc.) vorgesehen

### 6.5.3 Kontext-Bestandteile

| Bestandteil | Pflicht | Beschreibung |
|---|---|---|
| Systemprompt des Modus | ja | Rollenbeschreibung, Aufgabe, Verhaltensregeln, Output-Kontrakt |
| Template-Schema | ja | Maschinenlesbare Beschreibung der Artefakt-Struktur: alle gültigen Slot-Pfade, Feldtyp pro Slot (String, Enum, Liste), Pflicht/Optional, erlaubte Werte bei Enums, Abhängigkeiten zwischen Slots. Dient dem LLM als Referenz für korrekte RFC 6902 Pfad-Adressierung — verhindert Halluzination ungültiger Pfade. || Aktuelle Artefakte | ja | Vollständiger Inhalt aller drei Artefakte in aktueller Version — Read-Only |
| Completeness-State | ja | Aktueller Befüllungsstatus aller Slots |
| Working Memory (Auszug) | ja | Aktive Phase, Phasenstatus, Slot-Zähler, aktive Spannungsfelder — keine Flags (s. 6.4.1) |
| Dialoghistorie (letzten N Turns) | ja | Konfigurierbare Anzahl der letzten Turns; Standard: 3 |
| Moderator-Lösungskontext | nein | Nur wenn Modus nach Moderator-Übergabe aktiviert wird |
| Validierungsbericht | nein | Nur wenn Spezifikationsmodus nach Validierungsmodus aufgerufen wird |
| EMMA-Aktionskatalog | nein | Nur für Spezifikationsmodus und Validierungsmodus — vollständige Liste der erlaubten Aktionstypen inkl. Beschreibung (s. Abschnitt 8.3) |

### 6.5.4 Konfigurierbarkeit

Die Anzahl der übergebenen Dialogturns (`N`) ist systemseitig konfigurierbar. Dies ermöglicht den Betrieb mit kleineren lokalen Modellen (geringes N) ebenso wie mit großen Cloud-Modellen (hohes N).

### 6.5.5 Tokenlimit-Strategie

Für den Prototyp nicht relevant. Bei realistischen Prozessgrößen (max. 100 RPA-Schritte) und einer beschränkten Dialoghistorie (N=3 Turns) bleibt der zusammengestellte Kontext innerhalb der Tokenlimits gängiger Modelle — lokal wie Cloud.

Eine explizite Tokenlimit-Strategie wird erst notwendig wenn das System auf deutlich größere Prozesse oder kleinere Modelle ausgedehnt wird. `[OFFEN: OP-08]`

---

## 6.6 Kognitive Modi

Jeder kognitive Modus ist ein spezialisierter Sprachmodellaufruf mit definiertem Input, Output und Abbruchbedingung.

**Für alle Modi gilt:** Der Output besteht ausschließlich aus drei Bestandteilen gemäß Output-Kontrakt (s. 6.5.2):
1. **Nutzeräußerung** — Freitext für den Chatbereich
2. **Schreiboperationen** — RFC 6902 Patch Objekt, kann leer sein
3. **Steuerungsoutput** — Phasenstatus + Flags (s. 6.4.1 für vollständige Flag-Definitionen, Auslösekriterien und Systemprompt-Anforderungen)

Kein Modus schreibt direkt ins Working Memory oder in die Artefakte. Der Orchestrator ist die einzige Komponente die aus dem Modus-Output Konsequenzen zieht und Schreiboperationen ausführt.


### 6.6.1 Explorationsmodus

**Ziel:** Implizites Prozesswissen des Nutzers erfassen und ein ausreichend klares Prozessverständnis herstellen.

**Input:** Template-Schema, Nutzerinput, Explorationsartefakt (Read-Only, aktueller Stand), Dialoghistorie (N Turns), Working Memory Auszug, Completeness-State, ggf. externe Rohdaten (s. 7.1)

**Verhalten:**
- Führt den Nutzer durch offene, explorative Fragen
- Identifiziert zentrale Prozessschritte, Auslöser, Ziele und beteiligte Systeme
- Dokumentiert Erkenntnisse als Schreiboperationen auf die Pflicht-Slots im Explorationsartefakt
- Stellt keine Annahmen auf — unklare Punkte werden explizit erfragt
- entscheidet ob Flags gesetzt werden müssen (6.4.1)

**Output:** Nutzeräußerung, Schreiboperationen auf Explorations-Slots im Explorationsartefakt, Steuerungsoutput (Phasenstatus + Flags)

**Abbruchbedingung:** Modus setzt `phase_complete`, wenn alle Pflicht-Slots des Explorationsartefakts den Status `nutzervalidiert` erreicht haben.

---

### 6.6.2 Strukturierungsmodus

**Ziel:** Prozess in ein vollständiges Strukturartefakt überführen.

**Input:** Template-Schema, Explorationsartefakt (Read-Only, vollständig nutzervalidiert), Dialoghistorie (N Turns), Working Memory Auszug, Completeness-State, Strukturartefakt (Read-Only)

**Verhalten:**
- Zerlegt den Prozess systematisch in Strukturschritte gemäß dem Strukturschritt-Schema (s. 5.4): jeder Schritt erhält Typ (`aktion` / `entscheidung` / `schleife` / `ausnahme`), Beschreibung, Reihenfolge und Nachfolger. Ein Prozess muss genau einen Startschritt und mindestens einen Endschritt besitzen.
- Modelliert Entscheidungslogik, Schleifen und Ausnahmen
- Erkennt Inkonsistenzen und legt diese dem Nutzer zur Auflösung vor
- Ergänzt das Strukturartefakt iterativ über Schreiboperationen auf einzelne Slots — bestehende Slots werden nicht ohne Rückfrage ersetzt
- Dokumentiert Spannungsfelder
- entscheidet ob Flags gesetzt werden müssen (6.4.1)

**Output:** Nutzeräußerung, Schreiboperationen auf Strukturartefakt-Slots, Steuerungsoutput (Phasenstatus + Flags)

**Abbruchbedingung:** Modus setzt `phase_complete`, wenn alle Pflichtfelder aller Strukturschritte (s. 5.4) befüllt und nutzervalidiert sind, keine offenen Widersprüche bestehen und der Nutzer den Stand bestätigt hat.

---

### 6.6.3 Spezifikationsmodus

**Ziel:** Jeden Strukturschritt mit konkreten EMMA-Aktionen präzisieren.

**Input:** Template-Schema, Vollständiges Strukturartefakt (Read-Only), Algorithmusartefakt (Read-Only), Dialoghistorie (N Turns), Working Memory Auszug, Completeness-State, EMMA-Aktionskatalog, ggf. Validierungsbericht

**Verhalten:**
- Arbeitet das Strukturartefakt Schritt für Schritt durch, orientiert am Completeness-State
- Ordnet jedem Strukturschritt eine Sequenz von EMMA-Aktionen zu via Schreiboperationen auf Algorithmusartefakt-Slots
- Prüft EMMA-Kompatibilität für jeden Schritt
- Markiert nicht abbildbare Schritte und schlägt Alternativen vor
- Wenn nach Validierungsmodus aufgerufen: arbeitet den Validierungsbericht gemeinsam mit dem Nutzer ab
- entscheidet ob Flags gesetzt werden müssen (6.4.1)

**Output:** Nutzeräußerung, Schreiboperationen auf Algorithmusartefakt-Slots, Steuerungsoutput (Phasenstatus + Flags)

**Abbruchbedingung:** Modus setzt `phase_complete`, wenn alle Strukturschritte einen korrespondierenden Algorithmusabschnitt mit Status `nutzervalidiert` besitzen.

---

### 6.6.4 Validierungsmodus

**Ziel:** Konsistenz, Vollständigkeit und EMMA-Kompatibilität beider Artefakte prüfen.

**Input:** Vollständiges Algorithmusartefakt (Read-Only), EMMA-Aktionskatalog, Working Memory Auszug, Completeness-State

**Verhalten:**
- Prüft referenzielle Integrität zwischen beiden Artefakten
- Prüft alle Algorithmusschritte gegen den EMMA-Aktionskatalog
- Prüft auf Inkonsistenzen im Algorithmusartefakt.
- Prüft ob alle identifizierten Ausnahmen behandelt sind
- Gibt strukturierten Validierungsbericht aus

**Output:** Validierungsbericht (eigenständiges Ausgabedokument, kein Slot-Modell) — Liste von Befunden mit Schweregrad, Steuerungsoutput (Phasenstatus + Flags)

### Schweregradskala

Jeder Befund im Validierungsbericht erhält einen Schweregrad:

| Schweregrad | Bedeutung |
|---|---|
| `kritisch` | Wesentlicher Fehler — z.B. fehlende referenzielle Integrität, nicht-EMMA-kompatibler Schritt ohne Alternative. Sollte vor Abschluss behoben werden. |
| `warnung` | Potentielles Problem — z.B. Spannungsfeld ohne Dokumentation. Kein Abschlusshindernis. |
| `hinweis` | Informativ — z.B. unvollständig befüllter optionaler Slot. Kein Handlungsbedarf. |

**Einschränkungen:**
- Der Validierungsmodus interagiert nicht mit dem Nutzer
- Der Validierungsmodus hat keine Schreibrechte auf die Artefakte — er gibt keine Schreiboperationen aus
- Nach Abschluss wird der Moderator aktiviert, der die Ergebnisse mit dem Nutzer bespricht

**Abbruchbedingung:** Modus setzt `phase_complete`, wenn der Validierungsbericht fertiggestellt wurde.

---

### 6.6.5 Moderator

**Ziel:** Orientierung des Nutzers bei Phasenübergängen, Eskalationen, Einleitung, Problemen und nach der Validierung.

**Aktivierung durch:**
- Panik-Button (Nutzer)
- Flag `phase_complete` (Phasenwechsel-Vorschlag)
- Flag `escalate` oder `blocked` (interne Eskalation)
- Abschluss des Validierungsmodus

**Input:** Aktuelle Artefakte (Read-Only), vollständiger Working Memory Auszug inkl. Completeness-State, letzte M (wobei M > N) Dialogturns, Aktivierungsgrund, ggf. Validierungsbericht

**Verhalten:**
- Analysiert die Situation und erklärt dem Nutzer den aktuellen Stand
- Bei Phasenwechsel: Präsentiert Zusammenfassung des Erreichten, schlägt Wechsel vor
- Nach Validierung: Erläutert die Ergebnisse des Validierungsberichts, entscheidet gemeinsam mit dem Nutzer ob der Prozess produktionsreif ist oder der Spezifikationsmodus erneut aktiviert wird. Bei Rückkehr zum Spezifikationsmodus übergibt der Moderator den Validierungsbericht und die vereinbarten nächsten Schritte als Kontext.
- Bei Eskalation/Panik: Analysiert das Problem gemeinsam mit dem Nutzer, entwickelt Lösungsstrategie
- Bei Rücksprung: Klärt Konsequenzen für Artefakte und Completeness-State, holt Nutzerbestätigung ein
- Gibt Kontrolle erst nach expliziter Nutzerbestätigung zurück

**Output:** Nutzeräußerung, Moderator-Lösungskontext (wird an nächsten Modus übergeben), Ziel-Modus-Angabe an Orchestrator, Steuerungsoutput (Flags). Keine Schreiboperationen auf Artefakt-Slots.

**Einschränkung:** Der Moderator verändert keine Artefakte direkt.

---
## 6.7 Fortschrittsmodell

Jeder kognitive Modus meldet nach jedem Turn zwei Fortschrittskomponenten an den Orchestrator. Der Orchestrator schreibt ins Working Memory:

### Phasenstatus

Der aktive Modus bewertet den Fortschritt der aktuellen Phase als einen von drei Zuständen:

| Status | Bedeutung |
|---|---|
| `in_progress` | Phase läuft, kein Abschluss absehbar |
| `nearing_completion` | Modus bewertet die Phase als nahezu abgeschlossen |
| `phase_complete` | Phase ist abgeschlossen — löst Moderator-Aktivierung aus |

### Slot-Zähler

Der Orchestrator berechnet nach jeder Schreiboperation automatisch aus den Artefakten:

| Wert | Beschreibung |
|---|---|
| `befuellte_slots` | Anzahl der Slots mit Status `teilweise`, `vollständig` oder `nutzervalidiert` |
| `bekannte_slots` | Gesamtzahl der aktuell im Template-Schema definierten Slots |

Die UI zeigt beide Komponenten kombiniert an — z.B. "Strukturierung · fast abgeschlossen · 9 von 12 Slots befüllt". Kein Prozentwert — die Gesamtzahl der Slots wächst während des Dialogs und ist zu Beginn nicht bekannt.

> **Hinweis:** Die konkreten Kriterien wann ein Modus `nearing_completion` setzt werden im Implementierungsdesign pro Modus präzisiert. `[OFFEN: OP-06]`
---

## 6.8 Offene Punkte

| ID | Thema | Beschreibung |
|---|---|---|
| OP-06 | Fortschrittsmetriken | Konkrete `nearing_completion`-Kriterien pro Modus im Implementierungsdesign definieren |
| OP-07 | Steuerungsflags vollständig | Flag-Liste wird im Architektur- und Implementierungsdesign vervollständigt (s. 6.4.1) |
| OP-08 | Tokenlimit-Strategie | Erst relevant bei größeren Prozessen oder kleineren Modellen (s. 6.5.5) |
| OP-21 | Rücksprung-Navigation | Vollständige Implementierung von Phasen-Rücksprüngen als reguläre Nutzerfunktion (post-Prototyp, s. 6.1.4) |
| OP-20 | Wiederholte Output-Kontrakt-Verletzung | Eskalationsmechanismus bei wiederholter Vertragsverletzung durch LLM definieren (s. FR-D-04) |
---

# Abschnitt 7 — Datenintegration und Persistenz

---


## 7.1 Integration externer Rohdaten

### Zweck

Das System kann externe Rohdaten als zusätzliche Informationsquelle zur Prozessdefinition verarbeiten. Der primäre Anwendungsfall sind Eventlogs aus einem UI-Recorder, der Nutzerinteraktionen aufzeichnet.

### Rohdatentypen

| Typ | Beschreibung | Typischer Inhalt |
|---|---|---|
| Eventlog (UI-Recorder) | Aufgezeichnete Nutzerinteraktionen mit einer Anwendung | Klickereignisse, Tastatureingaben, Fensterinteraktionen, Zeitstempel |
| Dokumente | Prozessbeschreibungen, SOPs, Handbücher | Freitext, ggf. strukturierte Tabellen |
| Bilder | Screenshots, Prozessdiagramme | Visuelle Prozessinformation |

### Verarbeitungsmodell (Prototyp)

Im Prototyp werden Rohdaten **direkt als Kontext** in den aktiven kognitiven Modus übergeben. Es gibt keinen separaten Verarbeitungsschritt. Der aktive Modus — in der Regel der Explorationsmodus — interpretiert die Rohdaten und extrahiert prozessrelevante Informationen daraus.

Der Nutzer bestätigt die extrahierten Informationen im Dialog, bevor sie in ein Artefakt übernommen werden.

> **Architektonische Vorbereitung:** Die Architektur muss einen späteren Austausch gegen ein dediziertes Rohdaten-Verarbeitungsmodul ermöglichen, ohne die übrige Systemlogik zu verändern. Dieses Modul würde Rohdaten vorverarbeiten und in ein standardisiertes Zwischenformat überführen, bevor sie an den kognitiven Modus übergeben werden. Die Schnittstelle zwischen Rohdaten-Verarbeitung und kognitivem Modus ist daher als austauschbarer Punkt zu behandeln. `[OFFEN: OP-09]`

### Verarbeitungsablauf (Prototyp)

1. Nutzer lädt Rohdatei über den Chatbereich hoch
2. Orchestrator erkennt Dateityp und leitet Datei als Kontext-Bestandteil an den aktiven Modus weiter
3. Aktiver Modus analysiert die Rohdaten und extrahiert Prozessinformationen
4. Modus präsentiert extrahierte Informationen im Chatbereich zur Nutzerbestätigung
5. Nach Bestätigung übergibt der Modus die Informationen als Schreiboperationen auf Artefakt-Slots an den Orchestrator. Der Orchestrator validiert und führt die Operationen aus (s. Abschnitt 5.7).

### Nicht unterstützte Formate

Nicht erkannte oder nicht unterstützte Dateiformate werden abgelehnt. Der Nutzer erhält eine Fehlermeldung mit Hinweis auf unterstützte Formate.

---

## 7.2 Projektmodell

### Definition

Ein Projekt entspricht genau einem Prozess. Jeder Prozess wird als eigenständiges Projekt verwaltet.

### Projektstruktur

Ein Projekt besteht aus folgenden Bestandteilen:

| Bestandteil | Beschreibung |
|---|---|
| Projektmetadaten | Identifizierende und beschreibende Informationen zum Projekt (s. 7.2.1) |
| Explorationsartefakt | Inkl. vollständiger Versionshistorie |
| Strukturartefakt | Inkl. vollständiger Versionshistorie |
| Algorithmusartefakt | Inkl. vollständiger Versionshistorie |
| Validierungsbericht | Letzter generierter Validierungsbericht — kein Slot-Modell, kein Versionsverlauf. Wird als Kontext beim Laden wiederhergestellt (s. 6.6.4). |
| Working Memory | Letzter persistierter Zustand |
| Dialoghistorie | Vollständiger Gesprächsverlauf des Projekts |

### 7.2.1 Projektmetadaten — Felder

| Feld | Typ | Pflicht | Beschreibung |
|---|---|---|---|
| `projekt_id` | String | ja | Eindeutige, stabile Projekt-ID |
| `name` | String | ja | Vom Nutzer vergebener Projektname |
| `beschreibung` | String | nein | Kurze Beschreibung des Prozesses (Freitext) |
| `erstellt_am` | Timestamp | ja | Zeitpunkt der Projekterstellung |
| `zuletzt_geaendert` | Timestamp | ja | Zeitpunkt der letzten Änderung |
| `aktive_phase` | Enum | ja | Aktuelle Systemphase bei letzter Speicherung |
| `aktiver_modus` | Enum | ja | Aktiver kognitiver Modus bei letzter Speicherung — wird beim Laden für die Wiederherstellung des Systemzustands benötigt (s. 6.1.0) |
| `projektstatus` | Enum | ja | `aktiv` / `pausiert` / `abgeschlossen` |

### Mehrere Projekte

Ein Nutzer kann mehrere Projekte verwalten. Die Projektliste wird beim Start der Anwendung angezeigt. Der Nutzer kann zwischen Projekten wechseln, ein neues Projekt anlegen oder ein bestehendes Projekt laden.

---


## 7.3 Persistenzmodell

### Was wird gespeichert

Das System persistiert den vollständigen Projektzustand:

- Projektmetadaten
- Explorationsartefakt (alle Versionen)
- Strukturartefakt (alle Versionen)
- Algorithmusartefakt (alle Versionen)
- Validierungsbericht (letzter Stand — kein Versionsverlauf, s. 7.2)
- Completeness-State (letzter Stand, s. Abschnitt 5.6)
- Working Memory (letzter Stand)
- Dialoghistorie (vollständig)

### Wann wird gespeichert

| Auslöser | Beschreibung |
|---|---|
| Nach jedem Orchestrator-Zyklus | Automatische Speicherung nach jeder abgeschlossenen Dialogrunde — schließt Artefaktänderungen und Phasenwechsel ein (s. 6.3 Schritt 11) |
| Bei Projektabschluss | Finaler Snapshot mit `projektstatus` = `abgeschlossen` (s. FR-G-04, Abschnitt 8.7) |

### Konsistenzanforderungen

- Ein Speichervorgang ist atomar: entweder wird der vollständige Projektzustand gespeichert oder gar nichts — kein partieller Zustand darf persistiert werden (s. FR-E-01).
- Bei einem Fehler während der Speicherung bleibt der letzte konsistente Stand erhalten.

> **Abgrenzung:** Der Executor-Snapshot (s. 5.7) ist ein kurzlebiger Rollback-Punkt innerhalb einer einzelnen Schreiboperation — er ist kein Persistenz-Snapshot. Der Persistenz-Snapshot in 7.3 ist der dauerhafte Systemzustand der nach jedem abgeschlossenen Orchestrator-Zyklus gespeichert wird. Beide Atomaritätsebenen sind unabhängig voneinander.

### Wiederherstellung

Das System muss nach folgenden Fehlerereignissen wieder herstellbar sein:

| Fehlerereignis | Erwartetes Verhalten |
|---|---|
| Browser-Absturz | Letzter persistierter Snapshot wird beim nächsten Start automatisch angeboten |
| LLM-Timeout | Kein Zustandsverlust; letzter stabiler Stand bleibt erhalten |
| Ungültiger LLM-Output / Output-Kontrakt-Verletzung | Zustand vor dem fehlgeschlagenen Turn wird wiederhergestellt; keine teilweise ausgeführten Schreiboperationen |

### Persistenz-Constraints für die Architektur

Die Wahl der Persistenztechnologie ist eine Architekturentscheidung `[OFFEN: OP-10]`. Folgende Anforderungen müssen dabei berücksichtigt werden:

| Constraint | Beschreibung |
|---|---|
| Atomare Schreibvorgänge | Teilweise gespeicherte Zustände müssen ausgeschlossen sein |
| Versionierte Artefakte | Die Persistenzschicht muss mehrere Versionen pro Artefakt speichern können |
| Completeness-State | Der Completeness-State wird nicht separat persistiert — er wird beim Laden aus den Artefakten rekonstruiert (s. FR-E-05). Die Artefakte sind die einzige persistierte Quelle des Completeness-Status. |
| Projektisolation | Projekte dürfen sich gegenseitig nicht beeinflussen |
| Wiederherstellbarkeit | Letzter valider Zustand muss nach Fehler abrufbar sein |
| Lokaler Betrieb | Das System muss ohne Cloud-Anbindung betreibbar sein (on-premise Anforderung) |

---

## 7.4 Offene Punkte

| ID | Thema | Beschreibung |
|---|---|---|
| OP-09 | Rohdaten-Verarbeitungsmodul | Architektonische Schnittstelle für späteres dediziertes Modul definieren (s. 7.1) |
| OP-10 | Persistenztechnologie | Auswahl der konkreten Speichertechnologie im Architekturdesign |
| OP-11 | Dialoghistorie-Umfang | Wird die vollständige Dialoghistorie gespeichert, oder nur die letzten N Turns? Speicherbedarf abschätzen. |
| OP-12 | Projektliste im UI | Wie wird die Projektübersicht dargestellt? Gehört ins UI-Design (s. FR-G-02). |

---

# 8. SYSTEMGRENZEN UND QUALITÄTSANFORDERUNGEN

---

## 8.1 Nicht-funktionale Anforderungen

NFRs sind nach Priorität für den Prototyp geordnet. **Primäre NFRs** sind implementierungsrelevant und blockieren den Betrieb wenn nicht erfüllt. **Sekundäre NFRs** sind Zielzustände für spätere Ausbaustufen.

---

### 8.1.1 Wartbarkeit — PRIMÄR

**Begründung:** Das System wird als Prototyp entwickelt, soll aber eine saubere Architektur besitzen, die Weiterentwicklung ohne Umbau ermöglicht. Wartbarkeit ist daher die wichtigste strukturelle Anforderung.

| Anforderung | Beschreibung |
|---|---|
| Modulare Komponenten | Orchestrator, kognitive Modi, Persistenz und UI sind klar voneinander getrennte Module mit definierten Schnittstellen |
| Austauschbarkeit von LLM-Modellen | Das verwendete Sprachmodell muss ohne Änderung der Geschäftslogik austauschbar sein (lokal ↔ Cloud) |
| Konfigurierbarkeit | Alle systemrelevanten Parameter müssen in einer zentralen Konfigurationsdatei verwaltet werden — kein Hardcoding im Code. Kein Parameter der das Systemverhalten beeinflusst darf im Code fest verdrahtet sein. Dazu gehören mindestens: Anzahl übergebener Dialogturns (N), LLM-Modellauswahl, Token-Limits, Token-Schwellenwert für Prozesspartitionierung, Automatisierbarkeits-Schwellenwert. Die vollständige Parameterliste wird im Architekturdesign definiert. |
| Erweiterbarkeit kognitiver Modi | Neue Modi können hinzugefügt werden ohne bestehende Modi zu verändern |
| Dokumentierter Code | Alle Module sind ausreichend dokumentiert für einen neuen Entwickler |

---


### 8.1.2 Zuverlässigkeit — PRIMÄR

**Begründung:** Datenverlust bei einem mehrstündigen Nutzungsprozess ist inakzeptabel. Zuverlässigkeit umfasst zwei Ebenen: Persistenz-Integrität und Artefakt-Integrität.

| Anforderung | Beschreibung |
|---|---|
| Kein Datenverlust | Kein Verlust von Artefakten oder Arbeitsständen bei technischen Fehlern |
| Atomare Persistenz | Vor jeder Patch-Anwendung wird ein atomarer JSON-Snapshot des Artefakts erstellt. Bei Fehler in einem beliebigen Executor-Schritt wird auf diesen Snapshot restored — kein inkonsistenter Zustand möglich (s. Abschnitt 5.7, 7.3) |
| Fehlertoleranz bei LLM-Fehlern | LLM-Fehler erzeugen keinen inkonsistenten Systemzustand |
| Wiederherstellbarkeit | Nach jedem Fehlertyp ist der letzte valide Zustand wiederherstellbar (s. Abschnitt 7.3) |
| Artefaktintegrität durch Schreibkontrolle | Jede Schreiboperation wird vor Ausführung gegen das Template-Schema validiert. Nach Ausführung wird per Preservation-Assertion geprüft, dass ausschließlich der adressierte Slot verändert wurde. Bei Abweichung erfolgt sofortiger Rollback (s. Abschnitt 5.7, FR-B-09). |
| Rollback bei fehlgeschlagenen Schreiboperationen | Schreiboperationen die gegen den Output-Kontrakt verstoßen oder die Slot-Validierung nicht bestehen werden nicht ausgeführt. Der Artefaktstand bleibt auf dem letzten validen Zustand. |
| Fehlerbehandlung bei LLM-Fehlern | Bei LLM-Timeout oder API-Fehler wird der laufende Turn abgebrochen. Der Systemzustand verbleibt auf dem letzten validen persistierten Stand. Der Nutzer erhält eine klare Fehlermeldung und kann den Turn erneut absenden. Retry-Logik ist im Prototyp nicht vorgesehen. |

---

### 8.1.3 Beobachtbarkeit — PRIMÄR (Prototyp)

**Begründung:** Im Prototyp steht die Entwicklungs- und Analysearbeit im Vordergrund. Interne Zustände müssen jederzeit einsehbar sein.

| Anforderung | Beschreibung |
|---|---|
| Debug-Bereich | Aktiver Modus, Working Memory, Completeness-State, Fortschrittsmetriken und letzte ausgeführte Schreiboperation sind im UI sichtbar (s. Abschnitt 2.3). Steuerungsflags des aktiven Zyklus werden während der Laufzeit angezeigt — sie sind zyklus-lokal und werden nicht persistiert (s. 6.4.1). |
| Logging | Alle Orchestrator-Entscheidungen, Moduswechsel, Schreiboperationen und LLM-Aufrufe werden geloggt |
| LLM-Input/Output-Logging | Vollständiger Kontext jedes LLM-Aufrufs wird für Analyse gespeichert, inkl. ausgegebener Schreiboperationen und etwaiger Kontrakt-Verletzungen |
| Nachvollziehbarkeit | Jede Artefaktänderung ist auf den auslösenden Modus, Turn und die konkrete Schreiboperation zurückverfolgbar (`created_by`, `slot_id` in Versionierung) |

---


### 8.1.4 Performance — SEKUNDÄR

**Begründung:** Für den Prototyp nicht blockierend. Nutzererfahrung wird durch LLM-Antwortzeiten dominiert, nicht durch Systemlogik.

| Anforderung | Zielwert | Priorität |
|---|---|---|
| Orchestrator-Zykluszeit (ohne LLM) | < 500 ms | Prototyp |
| UI-Aktualisierung nach LLM-Antwort | < 1 s | Prototyp |
| Projektlade-Zeit | < 3 s für typische Projektgröße | Prototyp |

> **Hinweis:** LLM-Latenz ist extern bedingt und keine Systemanforderung.

---

### 8.1.5 Skalierung — SEKUNDÄR

Für den Prototyp nicht relevant. Das System ist Single-User, Single-Project-at-a-time. Skalierungsanforderungen werden bei Produktifreigabe definiert.

---

### 8.1.6 Sicherheit — PRAGMATISCH

Für den Prototyp gilt ein minimaler Sicherheitsrahmen:

| Anforderung | Beschreibung |
|---|---|
| API-Key-Schutz | LLM-API-Keys werden nicht im Frontend gespeichert oder übertragen. Verwaltung ausschließlich im Backend. |
| Keine Authentifizierung | Im Prototyp kein Login erforderlich |
| Lokaler Betrieb | Das System ist on-premise betreibbar ohne Cloud-Abhängigkeit |

> **Hinweis:** Erweiterte Sicherheitsanforderungen (Zugriffsschutz, Verschlüsselung gespeicherter Daten) sind für eine spätere Produktivstufe zu definieren.

---


## 8.2 Architekturrahmen

Dieser Abschnitt beschreibt die Architektur-Constraints — also die Rahmenbedingungen, innerhalb derer das Architekturdesign stattfinden muss. Die konkrete Architektur wird im separaten Architekturdokument definiert.

| Constraint | Beschreibung |
|---|---|
| Frontend-Backend-Trennung | UI-Logik und Systemlogik sind strikt getrennt. Das Frontend hat keinen direkten Zugriff auf LLMs oder Persistenz. |
| Backend als Single Source of Truth | Orchestrator, Working Memory, Artefakte, Completeness-State und Persistenz liegen vollständig im Backend |
| LLM-Flexibilität | Das Backend muss sowohl lokale Modelle (z.B. Ollama/Llama) als auch Cloud-APIs (z.B. Anthropic, OpenAI) unterstützen — konfigurierbar ohne Code-Änderung |
| On-Premise-Fähigkeit | Das Gesamtsystem muss ohne externe Netzwerkverbindung betreibbar sein |
| Kein LLM im Orchestrator | Der Orchestrator arbeitet deterministisch und regelbasiert. LLM-Aufrufe erfolgen ausschließlich durch kognitive Modi. |
| LLM als Textoperator mit beschränkten Schreibrechten | Das LLM erhält Artefakte ausschließlich als Read-Only-Lesekontext. Schreibrechte sind auf benannte Slots beschränkt. Der Orchestrator ist die einzige Komponente, die Schreiboperationen am Artefakt ausführt — nach expliziter Validierung. Das LLM gibt Artefakte niemals vollständig zurück (s. Abschnitt 6.5.2, 5.7). |
| Rücksprungfähigkeit als Design-Invariante | Die Systemarchitektur MUSS Phasen-Rücksprünge strukturell unterstützen — unabhängig davon ob sie im Prototyp als Nutzerfunktion exponiert sind. Kein Architekturentscheid darf Rücksprünge nachträglich unmöglich machen. Im Prototyp sind Rücksprünge ausschließlich über den Moderator auslösbar (s. Abschnitt 6.1.4). |
| Austauschbare Rohdaten-Schnittstelle | Die Schnittstelle zwischen Rohdaten-Verarbeitung und kognitivem Modus MUSS als isolierter, austauschbarer Punkt implementiert werden. Im Prototyp werden Rohdaten direkt als Kontext übergeben. Die Architektur muss einen späteren Austausch gegen ein dediziertes Verarbeitungsmodul ohne Änderung der übrigen Systemlogik ermöglichen (s. Abschnitt 7.1). |

---

## 8.3 EMMA-Aktionskatalog

Der folgende Katalog definiert die verfügbaren Aktionen in EMMA RPA. Alle Algorithmusschritte im Algorithmusartefakt müssen auf einen dieser Aktionstypen abgebildet werden.

> **Hinweis:** Parameter pro Aktion sind aktuell nicht vollständig spezifiziert. `[OFFEN: OP-02]`

| Aktionstyp | Beschreibung | Kategorie |
|---|---|---|
| `FIND` | Element in der UI lokalisieren | UI-Interaktion |
| `FIND_AND_CLICK` | Element lokalisieren und anklicken (kombiniert) | UI-Interaktion |
| `CLICK` | Element anklicken | UI-Interaktion |
| `DRAG` | Element per Drag-and-Drop verschieben | UI-Interaktion |
| `SCROLL` | Scrollaktion ausführen | UI-Interaktion |
| `TYPE` | Text in ein Element eingeben | UI-Interaktion |
| `READ` | Wert oder Text aus einem Element lesen | Datenverarbeitung |
| `READ_FORM` | Formularfelder auslesen | Datenverarbeitung |
| `GENAI` | Generative KI-Aktion ausführen | KI-Integration |
| `EXPORT` | Daten exportieren | Datei & Daten |
| `IMPORT` | Daten importieren | Datei & Daten |
| `FILE_OPERATION` | Dateioperationen ausführen (kopieren, verschieben, löschen, umbenennen) | Datei & Daten |
| `SEND_MAIL` | E-Mail versenden | Kommunikation |
| `COMMAND` | Systembefehl oder Skript ausführen | System |
| `LOOP` | Schleife über eine Menge von Elementen oder Bedingung | Kontrollfluss |
| `DECISION` | Bedingte Verzweigung (IF/ELSE) | Kontrollfluss |
| `WAIT` | Warten auf Bedingung oder Zeitdauer | Kontrollfluss |
| `SUCCESS` | Prozess erfolgreich abgeschlossen | Kontrollfluss |

### Nicht unterstützte Aktionen

Prozessschritte, die keinem der obigen Aktionstypen zugeordnet werden können, gelten als **nicht EMMA-kompatibel**. Das System muss solche Schritte erkennen, markieren und dem Nutzer Alternativen vorschlagen (s. FR-C-03).

> **Offene Frage:** Der aktuelle Katalog modelliert Aktionsknoten, aber keine bedingten Kanten (Erfolgs-/Fehlerkanten zwischen Knoten). `SUCCESS` markiert einen regulären Abschlussknoten — Fehlerübergänge zwischen Knoten sind im aktuellen Algorithmusartefakt-Schema nicht modelliert. Die Modellierung von Erfolgs- und Fehlerkanten im Kontrollflussgraph muss im Architekturdesign geklärt werden. `[OFFEN: OP-16]`

---

## 8.4 Prozessumfang

| Parameter | Wert |
|---|---|
| Typischer Prozessumfang | 50–60 Strukturschritte |
| Maximaler erwarteter Umfang | < 100 Strukturschritte |
| Basis für Tokenlimit-Planung | 100 Schritte × durchschnittliche Schrittgröße im Algorithmusartefakt |

Das System überwacht kontinuierlich die Token-Größe des Artefakts. Nähert sich ein Artefakt den Kapazitätsgrenzen des konfigurierten Modells, initiiert das System eine **Prozesspartitionierung**: Der Prozess wird in Teilprozesse gegliedert, von denen jeder ein eigenes Artefakt erhält. Dies ist kein Fehlerfall — Prozesspartitionierung ist definiertes Systemverhalten und Teil guter Prozessmodellierung. Konkrete Schwellenwerte werden im Architekturdesign definiert `[OFFEN: OP-05]`.

> **Hinweis:** Das externe Artefaktmodell (s. Abschnitt 5.1) hält den pro-Turn-Kontext stabil, da das LLM das Artefakt liest aber nie repliziert. Die kritische Variable für die Kontextgröße ist daher der Lesekontext des Artefakts, nicht die Ausgabegröße.
---

## 8.5 Systemgrenzen

Was das System explizit **nicht** leistet:

| Ausgeschlossen | Begründung |
|---|---|
| Direkte Ausführung von RPA-Prozessen | Das System erzeugt Algorithmen, führt sie nicht aus |
| Grafische BPMN-Darstellung | Artefakte sind textbasiert, keine Diagramme |
| Automatische Übernahme in EMMA | Export ist manuell; kein direkter EMMA-API-Import im Prototyp |
| Multi-User-Betrieb | Single-User im Prototyp |
| Mehrsprachigkeit | Systemsprache ist Deutsch |
| Subprozesse (Nested Process) | Im Prototyp nicht unterstützt; architektonisch nicht verbaut |
| EMMA Recorder Integration | Der EMMA Recorder existiert im Prototyp nicht. Der Recorder-Button ist im UI reserviert, aber deaktiviert. |

---

## 8.6 Abschlusskriterien

Ein Durchlauf gilt als abgeschlossen, wenn der Nutzer ihn explizit beendet. Das System blockiert einen Abschluss nicht — der Nutzer hat jederzeit das letzte Wort.

Das System informiert den Nutzer transparent über den aktuellen Stand vor dem Abschluss:

| Kriterium | Beschreibung |
|---|---|
| Artefaktvollständigkeit | Sind beide Artefakte vollständig `nutzervalidiert`? |
| Offene kritische Befunde | Enthält der Validierungsbericht noch Befunde mit Schweregrad `kritisch`? |

Der Nutzer kann den Durchlauf auch bei offenen kritischen Befunden oder unvollständigen Artefakten beenden. Das System zeigt in diesem Fall eine explizite Warnung, führt den Abschluss aber bei Bestätigung durch.

----

## 8.7 Offene Punkte


| ID | Thema | Beschreibung |
|---|---|---|
| OP-02 | EMMA-Parameterdefinition | Vollständige Parameterliste pro Aktionstyp muss definiert werden (s. 8.3) |
| OP-05 | Prozesspartitionierung | Konkrete Token-Schwellenwerte für Partitionierungsauslösung im Architekturdesign definieren (s. 8.4) |
| OP-13 | Performance-Zielwerte | Konkrete Messung und Validierung der Performance-Zielwerte im Prototyp (s. 8.1.4) |
| OP-14 | LLM-Input/Output-Logging | Format und Speicherort der LLM-Logs definieren, inkl. Logging von Kontrakt-Verletzungen (s. 8.1.3) |
| OP-15 | Subprozesse | Unterstützung von Nested Process / Subflows als post-Prototyp Feature evaluieren (s. 8.5) |
| OP-16 | Erfolgs-/Fehlerkanten im Kontrollflussgraph | Modellierung bedingter Kanten (Erfolg/Fehler) zwischen Algorithmusknoten ist im aktuellen Schema nicht abgebildet. Im Architekturdesign klären. |

------

# Offene Punkte — Digitalisierungsfabrik SDD
## Konsolidierte Gesamtliste (Stand: Review-Session)

| ID | Thema | Beschreibung | Fundstelle |
|---|---|---|---|
| OP-01 | JSON-Schema Artefakte | Formale Schemadefinition aller drei Artefakte inkl. aller Slot-IDs | Abschnitt 5.3–5.5 |
| OP-02 | EMMA-Parameterdefinition | Vollständige Parameterliste pro Aktionstyp muss definiert werden | Abschnitt 8.3 |
| OP-03 | Versionshistorie im UI | (1) Wie navigiert der Nutzer durch Versionen — Liste, Timeline, Diff-Ansicht? (2) Sieht der Nutzer alle Versionen oder nur einen konfigurierbaren Ausschnitt? (3) Wer erzeugt `change_summary` pro Version — LLM, System automatisch, oder Kombination? | Abschnitt 5.2 |
| OP-04 | Maximale Versionszahl | Gibt es ein Limit für gespeicherte Versionen, oder unbegrenzt? | Abschnitt 5.2 |
| OP-05 | Prozesspartitionierung | Ab welchem Token-Schwellenwert wird Partitionierung ausgelöst? Konkrete Grenzwerte im Architekturdesign definieren. | Abschnitt 8.4 |
| OP-06 | Fortschrittsmetriken | Konkrete `nearing_completion`-Kriterien pro Modus im Implementierungsdesign definieren | Abschnitt 6.7 |
| OP-07 | Steuerungsflags vollständig | Flag-Liste wird im Architektur- und Implementierungsdesign vervollständigt | Abschnitt 6.4.1 |
| OP-08 | Tokenlimit-Strategie | Erst relevant bei größeren Prozessen oder kleineren Modellen — Strategie für diesen Fall definieren | Abschnitt 6.5.5 |
| OP-09 | Rohdaten-Verarbeitungsmodul | Architektonische Schnittstelle für späteres dediziertes Verarbeitungsmodul definieren | Abschnitt 7.1 |
| OP-10 | Persistenztechnologie | Auswahl der konkreten Speichertechnologie im Architekturdesign | Abschnitt 7.3 |
| OP-11 | Dialoghistorie-Umfang | Wird die vollständige Dialoghistorie gespeichert, oder nur die letzten N Turns? Speicherbedarf abschätzen. | Abschnitt 7.3 |
| OP-12 | Projektliste im UI | Wie wird die Projektübersicht dargestellt? Gehört ins UI-Design. | FR-G-02 |
| OP-13 | Performance-Zielwerte | Konkrete Messung und Validierung der Performance-Zielwerte im Prototyp | Abschnitt 8.1.4 |
| OP-14 | LLM-Input/Output-Logging | Format und Speicherort der LLM-Logs definieren, inkl. Logging von Kontrakt-Verletzungen | Abschnitt 8.1.3 |
| OP-15 | Subprozesse | Unterstützung von Nested Process / Subflows als post-Prototyp Feature evaluieren | Abschnitt 8.5 |
| OP-16 | Erfolgs-/Fehlerkanten im Kontrollflussgraph | Modellierung bedingter Kanten (Erfolg/Fehler) zwischen Algorithmusknoten ist im aktuellen Schema nicht abgebildet. Im Architekturdesign klären. | Abschnitt 8.3 |
| OP-17 | Eventlog-Format | Das EMMA Recorder-Eventlog-Format ist nicht definiert. FR-A-05 ist solange nicht vollständig testbar. Im Prototyp als eingeschränkt verfügbar behandeln. | FR-A-05 |
| OP-18 | Automatisierbarkeits-Schwellenwert | Der Schwellenwert "mehr als ein nicht automatisierbarer Schritt" ist arbiträr. Im Implementierungsdesign überprüfen und ggf. konfigurierbar machen. | FR-A-07 |
| OP-19 | Markdown-Renderlogik | Die Transformation des JSON-Artefakts in lesbares Markdown ist nicht spezifiziert. Renderlogik muss im Architekturdesign definiert werden. | FR-B-06 |
| OP-20 | Wiederholte Output-Kontrakt-Verletzung | Verhalten bei wiederholter Vertragsverletzung durch das LLM ist nicht definiert. Eskalationsmechanismus (Retry-Limit, Moderator-Aktivierung) im Implementierungsdesign festlegen. | FR-D-04 |
| OP-21 | Rücksprung-Navigation | Vollständige Implementierung von Phasen-Rücksprüngen als reguläre Nutzerfunktion (post-Prototyp). Architektur ist vorbereitet. | Abschnitt 6.1.4 |