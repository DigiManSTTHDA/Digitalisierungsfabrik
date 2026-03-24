# E2E Human Validation Playbook

Anleitung für manuelle End-to-End-Validierung der Digitalisierungsfabrik.

**Testprozess:** Reisekostenabrechnung
**Persona:** Frau Weber, Teamleiterin Verwaltung, mittelständische Spedition
**Ziel:** Alle vier Phasen durchlaufen, pro Phase Artefakte prüfen, Bericht ausfüllen.

**Ablauf:**
1. Eingaben pro Phase Schritt für Schritt in das System einfügen
2. Nach jeder Eingabe System-Antwort beobachten und im Bericht notieren
3. Am Ende jeder Phase: Artefakt im UI mit dem Ziel-Artefakt vergleichen
4. Am Ende: `validate_e2e_artifacts.py` laufen lassen für strukturelle Checks

---

## Was ist der Post-hoc-Validator?

Nach dem manuellen Durchlauf läuft ein Script gegen die echte Datenbank und
prüft alles, was **ohne LLM-Bewertung** prüfbar ist:

```bash
cd backend
source .venv/bin/activate
python scripts/validate_e2e_artifacts.py            # prüft das zuletzt bearbeitete Projekt
python scripts/validate_e2e_artifacts.py <projekt_id>  # prüft ein bestimmtes Projekt
```

**Was es prüft:**
- Sind alle 7 Exploration-Slots befüllt (nicht leer)?
- Hat das Struktur-Artefakt >= 5 Schritte mit korrekten Typen?
- Haben Entscheidungen Bedingung + 2 Nachfolger?
- Sind alle Nachfolger-Referenzen gültig (keine dangling refs)?
- Hat das Algorithmus-Artefakt >= 6 Abschnitte mit EMMA-Aktionen?
- Sind alle `struktur_ref` gültig?
- Gibt es DECISION und FILE_OPERATION als EMMA-Typen?

**Was es NICHT prüft (das machst du manuell):**
- Stimmen die *Inhalte* der Slots sinngemäß?
- Hat das System den Widerspruch korrekt eingearbeitet?
- War das Moderator-Verhalten bei Eskalation angemessen?
- Hat das System verständlich auf Deutsch kommuniziert?

---

## Persona-Briefing

Du spielst **Frau Weber**, Teamleiterin Verwaltung bei der **Müller Logistik GmbH**
in Augsburg. 85 Mitarbeiter, davon ~30 im Außendienst/Fernverkehr die regelmäßig
auf Dienstreise sind. Frau Weber ist sachlich, pragmatisch, leicht ungeduldig.
Sie kennt ihren Prozess gut, hat aber keine IT-Ausbildung. Fachbegriffe wie
"Kontrollfluss" oder "Parameter" sind ihr fremd.

---

# TEIL A — EINGABEN

> Jede Nachricht exakt kopieren und einfügen.
> Nach jeder Eingabe: Antwort lesen, Modus-Anzeige prüfen, ggf. im Bericht notieren.

---

## Phase 1: EXPLORATION

### Vorbereitung
- Neues Projekt anlegen im UI (Name: "Reisekostenabrechnung")
- System zeigt: Phase `exploration`, Modus `moderator`

### Eingaben

**E1-01** — Rückfrage (Moderator soll NICHT starten)
```
Kurze Frage vorab: Muss ich alles in einer Sitzung machen oder kann ich zwischendurch unterbrechen? Und wie detailliert muss ich das beschreiben?
```
Erwartung: Modus bleibt `moderator`. Beantwortet die Frage, fragt ob es losgehen kann.

---

**E1-02** — Bestätigung zum Start
```
Ja, legen wir los.
```
Erwartung: Modus wechselt zu `exploration`. Explorer stellt erste inhaltliche Frage zum Prozess.

---

**E1-03** — Auslöser und Ablauf grob
```
Also der Prozess startet wenn ein Mitarbeiter von einer Dienstreise zurückkommt. Oder eigentlich schon vorher: Der muss zuerst eine Reise beantragen, der Teamleiter genehmigt das, und erst dann darf er fahren. Danach sammelt er die Belege und reicht die ein. Manche Kollegen machen das auf Papier mit so einem Formular, andere nutzen unser neues TravelPro-Portal. Das Portal haben wir seit einem halben Jahr, aber die Hälfte der Leute weigert sich das zu benutzen.
```

---

**E1-04** — Systeme und Medienbrüche
```
Systeme? Wir haben SAP HR, da werden die Abrechnungen am Ende verbucht und die Erstattung angestoßen. Dann gibt es TravelPro, das ist unser neues Reiseportal — da kann man die Reise beantragen, Belege hochladen und den Status sehen. Aber wie gesagt, nur die Hälfte nutzt das. Die anderen füllen ein Papierformular aus und tackern die Belege dran. Frau Schmidt in der Verwaltung muss das dann alles abtippen in TravelPro, das ist doppelte Arbeit. Und Outlook natürlich für die ganzen Rückfragen.
```

---

**E1-05** — Genehmigung und Prüfung
```
Die Genehmigung läuft so: Für Inlandsreisen reicht die Unterschrift vom Teamleiter. Ab 500 Euro oder bei Auslandsreisen muss der Abteilungsleiter auch drüber schauen. Und ab 2000 Euro braucht man den Geschäftsführer, das sind aber meistens nur die Messereisen. Das Problem ist, manche Teamleiter genehmigen per E-Mail-Antwort statt im Portal, dann fehlt die offizielle Freigabe im System und wir müssen nachtragen.
```

---

**E1-06** — Frustration und Eskalation
```
Was soll ich denn noch erzählen? Ich hab doch schon den ganzen Ablauf beschrieben. Ehrlich gesagt dreht sich das im Kreis, immer die gleichen Fragen nur anders formuliert. Ich hab noch andere Sachen zu tun heute. Können wir das abkürzen?
```
**Danach: PANIK-BUTTON drücken.**
Erwartung: Modus wechselt auf `moderator`. Artefakt bleibt erhalten.

---

**E1-07** — Problem beim Moderator beschreiben
```
Der Explorer fragt mich immer das Gleiche. Ich hab den Prozess doch schon erklärt — Reiseantrag, Belege, Prüfung, Erstattung. Und jetzt will er immer noch mehr Details, aber ich weiß nicht was genau er noch wissen will.
```
Erwartung: Modus bleibt `moderator`. Moderator analysiert, schickt NICHT sofort zurück.

---

**E1-08** — Rückkehr bestätigen
```
Ok, also es fehlen noch Entscheidungspunkte und Variablen? Naja, das sind ja keine direkten Fragen an mich, oder? Gut, dann geben Sie mich zurück, aber sagen Sie ihm er soll auf den Punkt kommen.
```
Erwartung: Modus wechselt zu `exploration`.

---

**E1-09** — Beteiligte Systeme ergänzen (Post-Eskalation)
```
Also nochmal zu den Systemen: SAP HR für die Verbuchung und Gehaltsabrechnung, TravelPro für die Anträge und Belegverwaltung, Outlook für Kommunikation, und dann haben wir noch eine Excel-Liste wo Frau Schmidt parallel alle Abrechnungen trackt. Die Excel ist eigentlich überflüssig seit wir TravelPro haben, aber sie vertraut dem System nicht und führt die Liste weiter. Ist ein bekanntes Problem.
```
Erwartung: Explorer-Antwort kürzer als vor der Eskalation.

---

**E1-10** — Ausnahmen und Sonderfälle
```
Ausnahmen: Erstens der Privatwagen — manche Fahrer nehmen ihren eigenen PKW statt den Firmenwagen. Da gibt es eine Kilometerpauschale von 30 Cent pro Kilometer, die müssen ein Fahrtenbuch führen. Zweitens verlorene Belege — dann muss der Mitarbeiter einen Eigenbeleg schreiben, also quasi eine eidesstattliche Erklärung was er bezahlt hat. Der muss vom Teamleiter unterschrieben werden. Drittens stornierte Reisen — wenn eine gebuchte Reise nicht stattfindet, müssen wir die Stornokosten trotzdem abrechnen.
```

---

**E1-11** — Letzte Details
```
Was noch fehlt? Ach so: Wir sind eine Spedition in Augsburg, 85 Mitarbeiter, davon rund 30 die regelmäßig reisen. Das sind so 40 bis 50 Abrechnungen im Monat. In der Verwaltung sind wir zu dritt, Frau Schmidt macht fast nur Reisekosten. Die Tagessätze richten sich nach dem Bundesreisekostengesetz, das ist gesetzlich geregelt. Inlandsreisen: 14 Euro ab 8 Stunden, 28 Euro ab 24 Stunden. Ausland hat eigene Sätze je nach Land.
```

---

**E1-12** — Ende signalisieren
```
Ja, ich denke das war alles. Mehr kann ich dazu nicht sagen.
```
Erwartung: Explorer schreibt `prozesszusammenfassung` SELBST und meldet `phase_complete`.

Falls KEIN phase_complete, nacheinander eingeben:
1. `Ja das war wirklich alles, wir können zur nächsten Phase.`
2. `Bitte schließen Sie die Exploration ab, ich habe alles gesagt.`
3. `Exploration beenden, weiter zur Strukturierung.`

---

**E1-13** — Phasenwechsel bestätigen
```
Ja, weiter zur nächsten Phase.
```
Erwartung: Phase wechselt zu `strukturierung`.

---

### Zusatzfragen Phase 1 — Antworten zum Copy-Paste

---

**Agent fragt:** *Womit möchten Sie beginnen? / Über welchen Prozess sprechen wir?*
```
Unsere Reisekostenabrechnung. Vom Reiseantrag bis zur Erstattung auf dem Gehaltszettel.
40 bis 50 Abrechnungen pro Monat.
```

---

**Agent fragt:** *Was löst den Prozess aus?*
```
Ein Mitarbeiter muss auf Dienstreise. Der stellt zuerst einen Reiseantrag, entweder
im TravelPro-Portal oder auf Papier beim Teamleiter. Ohne genehmigten Antrag keine
Erstattung — das ist die Regel.
```

---

**Agent fragt:** *Was ist das Ziel des Prozesses?*
```
Dass der Mitarbeiter seine Auslagen fristgerecht und korrekt erstattet bekommt.
Die Erstattung läuft über die Gehaltsabrechnung in SAP HR. Und wir brauchen
saubere Belege für die Buchhaltung und das Finanzamt.
```

---

**Agent fragt:** *Können Sie den Ablauf Schritt für Schritt beschreiben?*
```
Reiseantrag stellen, Teamleiter genehmigt, Mitarbeiter reist, sammelt Belege,
reicht Abrechnung ein per Portal oder Papier, Frau Schmidt prüft die Belege,
bei Unklarheiten Rückfrage an den Mitarbeiter, wenn alles stimmt wird es in
SAP HR verbucht und mit dem nächsten Gehalt erstattet.
```

---

**Agent fragt:** *Wie lange dauert der Prozess?*
```
Vom Einreichen bis zur Erstattung meistens 2 bis 3 Wochen. Die reine Prüfung
dauert vielleicht eine Stunde pro Abrechnung. Aber das Warten auf fehlende
Belege oder Genehmigungen zieht sich oft.
```

---

**Agent fragt:** *Welche Rollen sind beteiligt?*
```
Der reisende Mitarbeiter, sein Teamleiter für die Genehmigung, bei größeren
Beträgen auch der Abteilungsleiter oder Geschäftsführer. Frau Schmidt in der
Verwaltung prüft und verbucht. Und unsere Lohnbuchhaltung in SAP HR erstattet
das am Monatsende über die Gehaltsabrechnung.
```

---

**Agent fragt:** *Was passiert wenn Belege fehlen oder falsch sind?*
```
Frau Schmidt schreibt eine E-Mail an den Mitarbeiter und bittet um Nachreichung.
Der hat 2 Wochen Zeit. Wenn nichts kommt, erinnert sie nochmal. Wenn dann immer
noch nichts kommt, wird der Posten nicht erstattet. Bei verlorenen Belegen gibt
es die Eigenbeleg-Regelung — der Mitarbeiter schreibt auf was er bezahlt hat und
der Teamleiter unterschreibt das. Aber nur bis 50 Euro pro Einzelposten.
```

---

**Agent fragt:** *Was sind die größten Probleme im Prozess?*
```
Erstens die Papier-Einreicher — die Hälfte nutzt TravelPro nicht, Frau Schmidt
muss alles abtippen. Zweitens die E-Mail-Genehmiger — manche Teamleiter genehmigen
per E-Mail statt im Portal, das ist nicht revisionssicher. Drittens die Excel-
Parallelliste, die eigentlich überflüssig ist aber keiner traut sich sie abzuschaffen.
Und viertens fehlende Belege, das ist ein Dauerthema.
```

---

**Agent fragt:** *Gibt es Fristen die eingehalten werden müssen?*
```
Der Mitarbeiter muss die Abrechnung innerhalb von 4 Wochen nach Reiseende
einreichen. Die Erstattung soll spätestens mit der übernächsten Gehaltsabrechnung
erfolgen. Die Tagessätze sind gesetzlich geregelt nach dem Bundesreisekostengesetz.
Und für die Steuer brauchen wir alle Originalbelege.
```

---

**Agent fragt:** *Welche Daten werden pro Abrechnung erfasst?*
```
Name des Reisenden, Reiseziel, Reisezeitraum, Reisegrund, die einzelnen
Ausgabenposten mit Betrag und Belegtyp, Tagessatz je nach Dauer und Ziel,
Kilometergeld bei Privatwagen, und die Genehmigungsnummer vom Reiseantrag.
```

---

**Agent fragt:** *Gibt es Unterschiede zwischen Inland und Ausland?*
```
Ja, bei Auslandsreisen gelten andere Tagessätze je nach Land — die werden
jährlich vom Finanzministerium festgelegt. Außerdem braucht eine Auslandsreise
immer die Genehmigung vom Abteilungsleiter, egal wie hoch der Betrag ist.
Und bei Auslandsreisen muss man die Belege auch noch umrechnen in Euro mit
dem Tageskurs.
```

---

## Phase 2: STRUKTURIERUNG

### Eingaben

**E2-01** — Rückfrage
```
Und was machen wir jetzt? Muss ich nochmal alles erzählen?
```
Erwartung: Modus bleibt `moderator`.

---

**E2-02** — Bestätigung
```
Gut, dann zeigen Sie mal was Sie daraus gemacht haben.
```
Erwartung: Modus wechselt zu `structuring`.

---

**E2-03** — Genehmigungsstufen präzisieren
```
Bei der Genehmigung muss ich nochmal genauer werden: Inlandsreisen unter 500 Euro brauchen nur den Teamleiter. Alles über 500 Euro oder Auslandsreisen brauchen zusätzlich den Abteilungsleiter. Und ab 2000 Euro muss der Geschäftsführer auch noch drüber. Das kommt aber selten vor, meistens bei Messen oder Schulungen im Ausland.
```

---

**E2-04** — Rückfrage-Schleife ergänzen
```
Ach ja, was ich noch vergessen hab: Wenn Frau Schmidt bei der Prüfung Fehler findet — also fehlende Belege oder Beträge die nicht stimmen — dann geht die ganze Abrechnung zurück an den Mitarbeiter. Der muss nachbessern und nochmal einreichen. Das geht manchmal zwei drei Mal hin und her. Erst wenn alles stimmt wird verbucht.
```

---

**E2-05** — Frustration über Fachbegriffe
```
Moment, was meinen Sie mit Kontrollfluss und Verzweigung? Das sind doch keine normalen Wörter. Ich beschreibe hier einen Arbeitsprozess und kein Computerprogramm. Können Sie das in normalem Deutsch erklären?
```
**Danach: PANIK-BUTTON drücken.**

---

**E2-06** — Problem beim Moderator
```
Der redet in Fachbegriffen die ich nicht verstehe. Verzweigung, Entscheidungsknoten, Iteration — das sagt mir alles nichts. Ich will einfach erklären wie unsere Reisekostenabrechnung funktioniert, mehr nicht.
```
Erwartung: Modus bleibt `moderator`. Artefakt unverändert.

---

**E2-07** — Rückkehr bestätigen
```
Ja, nochmal probieren. Aber bitte in normaler Sprache und immer nur eine Frage auf einmal.
```
Erwartung: Modus wechselt zu `structuring`.

---

**E2-08** — Spannungsfeld Excel
```
Was mich am meisten nervt ist die Excel-Liste. Frau Schmidt trägt jede einzelne Abrechnung nochmal in Excel ein — Datum, Name, Betrag, Status. Das ist eigentlich alles schon in TravelPro drin, aber sie sagt die Auswertungen in TravelPro sind zu umständlich. Also führt sie die Liste parallel. Das ist doppelter Aufwand und eine Fehlerquelle weil die Daten auseinanderlaufen können. Können Sie das als Problem vermerken?
```

---

**E2-09** — Spannungsfeld E-Mail-Genehmigung
```
Und das zweite Problem: Die E-Mail-Genehmigung. Herr Brenner zum Beispiel, der genehmigt grundsätzlich per E-Mail-Antwort. Dann hat Frau Schmidt zwar die Genehmigung, aber nicht im System. Sie muss dann manuell in TravelPro den Status auf genehmigt setzen und die E-Mail als Nachweis anhängen. Das ist nicht revisionssicher, der Wirtschaftsprüfer hat das schon angemahnt.
```

---

**E2-10** — Fertig
```
Ja, ich denke die Struktur passt so. Sieht gut aus was Sie da aufgebaut haben.
```
Falls kein phase_complete:
1. `Ja das war wirklich alles, die Struktur ist vollständig. Bitte abschließen.`
2. `Strukturierung abschließen, weiter zur Spezifikation.`

---

**E2-11** — Phasenwechsel
```
Ja, weiter zur nächsten Phase.
```

---

### Zusatzfragen Phase 2 — Antworten zum Copy-Paste

---

**Agent fragt (Moderator):** *Soll ich die Strukturierung starten?*
```
Ja, legen wir los.
```

---

**Agent fragt:** *Können Sie die Schritte in der richtigen Reihenfolge nennen?*
```
Von Anfang an: Reiseantrag stellen, Genehmigung einholen, Reise durchführen,
Belege sammeln, Abrechnung einreichen (Portal oder Papier), Frau Schmidt prüft,
bei Fehlern Rückfrage, wenn alles ok dann SAP-Verbuchung, dann Erstattung über
die Gehaltsabrechnung. Das ist der Normalfall.
```

---

**Agent fragt:** *Was genau passiert beim Reiseantrag?*
```
Der Mitarbeiter füllt im TravelPro den Antrag aus — Reiseziel, Zeitraum,
Grund, geschätzte Kosten. Oder er füllt das Papierformular aus und gibt
es seinem Teamleiter. Das Papierformular hat Frau Schmidt entworfen, das
liegt im Intranet zum Ausdrucken.
```

---

**Agent fragt:** *Wo gibt es Ja/Nein-Entscheidungen im Prozess?*
```
Erstens: Portal oder Papier — wie wird eingereicht?
Zweitens: Inland oder Ausland?
Drittens: Betrag unter oder über 500 Euro?
Viertens: Belege vollständig oder nicht?
Das sind die Hauptweggabelungen.
```

---

**Agent fragt:** *Was passiert wenn die Genehmigung abgelehnt wird?*
```
Dann wird die Reise nicht genehmigt und findet nicht statt. Der Mitarbeiter
kann einen neuen Antrag stellen mit Änderungen. Kommt selten vor, vielleicht
zweimal im Jahr.
```

---

**Agent fragt:** *Gibt es Schleifen oder Wiederholungen?*
```
Ja, die Nachbesserungsschleife. Wenn Frau Schmidt Fehler findet, geht die
Abrechnung zurück, der Mitarbeiter korrigiert, reicht nochmal ein, Frau Schmidt
prüft nochmal. Das kann zwei drei Runden dauern.
```

---

**Agent fragt:** *Soll ich das als Problem/Spannungsfeld vermerken?*
```
Ja bitte. Das sind echte Probleme die wir haben — die Excel-Parallelliste
und die informelle E-Mail-Genehmigung statt Portal.
```

---

**Agent fragt:** *Ist die Struktur so vollständig?*
```
Ja, sieht gut aus. Fällt mir nichts mehr ein.
```

---

## Phase 3: SPEZIFIKATION

### Eingaben

**E3-01** — Rückfrage
```
Jetzt nochmal? Was kommt denn noch? Ich hab doch wirklich schon alles erzählt.
```

---

**E3-02** — Bestätigung
```
Also nochmal genauer wie wir was am Computer machen. Ok, dann los.
```

---

**E3-03** — TravelPro-Antrag (FALSCH — wird in E3-06 korrigiert!)
```
Im TravelPro-Portal klickt der Mitarbeiter oben auf "Neue Reise". Dann kommt ein Formular mit Feldern für Reiseziel, Datum von/bis, Reisegrund und geschätzte Kosten. Das füllt er aus und klickt auf Absenden. Der Teamleiter kriegt dann eine E-Mail mit einem Link und kann im Portal genehmigen. Ach und das Formular hat auch ein Feld für die Kostenstelle, das ist wichtig für die Verbuchung.
```

---

**E3-04** — Belegerfassung
```
Wenn der Mitarbeiter zurückkommt, geht er wieder in TravelPro und öffnet seine Reise. Da gibt es einen Bereich "Belege hochladen". Er fotografiert die Quittungen mit dem Handy oder scannt sie ein und lädt die als PDF oder Bild hoch. Zu jedem Beleg gibt er den Betrag, das Datum und die Ausgabenart an — also ob das Hotel, Verpflegung, Transport oder Sonstiges war. Am Ende klickt er auf "Abrechnung einreichen".
```

---

**E3-05** — Prüfung durch Frau Schmidt (UNVOLLSTÄNDIG — System soll nachfragen)
```
Frau Schmidt öffnet TravelPro und sieht die eingereichten Abrechnungen in einer Liste. Sie klickt eine an und prüft die Belege einzeln. Wie sie genau prüft — da gibt es noch einiges zu sagen, aber fragen Sie mich gezielt was Sie wissen wollen.
```
Erwartung: Antwort enthält Nachfrage (Fragezeichen).

---

**E3-06** — WIDERSPRUCH: Genehmigungsablauf korrigieren
```
Moment, ich muss was korrigieren. Ich hab vorhin gesagt der Teamleiter kriegt eine E-Mail mit Link. Das stimmt so nicht mehr. Seit letztem Monat gibt es im TravelPro eine Push-Benachrichtigung direkt im Portal. Der Teamleiter sieht oben rechts ein Glockensymbol mit einer Zahl, klickt drauf und sieht die offenen Genehmigungen. Die E-Mail kommt nur noch als Backup wenn er nach 2 Tagen nicht reagiert hat. Das hat unser IT-Leiter umgestellt.
```
Erwartung: Artefakt wird aktualisiert. "Push-Benachrichtigung"/"Glockensymbol"/"Portal" taucht auf.

---

**E3-07** — Frustration über EMMA-Jargon
```
Was soll das heißen, FIND_AND_CLICK und READ_FORM? Das sind doch keine deutschen Wörter. Ich erzähl Ihnen wie wir arbeiten und Sie schreiben da irgendwelche Computerbefehle hin. Das versteh ich nicht und das will ich auch nicht verstehen. Reden Sie normal mit mir.
```
**Danach: PANIK-BUTTON drücken.**

---

**E3-08** — Eskalation beim Moderator
```
Der stellt mir technische Fragen die ich nicht beantworten kann. Was ist ein Parameter? Und er schreibt alles in englischen Abkürzungen auf die mir nichts sagen. Ich bin Verwaltungsleiterin und keine Programmiererin.
```

---

**E3-09** — Rückkehr
```
Ok, nochmal. Aber bitte in normalen Worten, als würde er einem Kollegen erklären was am Bildschirm passiert.
```

---

**E3-10** — SAP-Verbuchung
```
Wenn alles geprüft und genehmigt ist, geht Frau Schmidt in SAP HR. Sie öffnet dort den Bereich Reisekosten und legt einen neuen Erstattungsbeleg an. Da gibt sie ein: Personalnummer des Mitarbeiters, Reisezeitraum, Gesamtbetrag, und die einzelnen Kostenarten. Die Kostenstelle übernimmt sie aus dem TravelPro-Antrag. Dann speichert sie und der Beleg wird automatisch in die nächste Gehaltsabrechnung übernommen.
```

---

**E3-11** — Papier-Workflow
```
Bei den Papier-Einreichern ist es anders: Das ausgefüllte Formular kommt per Hauspost oder der Mitarbeiter legt es in Frau Schmidts Fach. Die Belege sind drangetackert. Frau Schmidt tippt dann alles manuell in TravelPro ein — Name, Reisedaten, jeden einzelnen Beleg mit Betrag und Typ. Die Papierbelege scannt sie ein und lädt die hoch. Das dauert pro Abrechnung dreimal so lang wie wenn der Mitarbeiter es selbst im Portal gemacht hätte.
```

---

**E3-12** — Eigenbeleg bei fehlendem Beleg
```
Wenn ein Beleg fehlt, füllt der Mitarbeiter einen Eigenbeleg aus. Das ist ein Formular wo er draufschreibt was er bezahlt hat, wann und wo. Der Teamleiter muss das unterschreiben. Frau Schmidt scannt den Eigenbeleg ein und lädt ihn statt des normalen Belegs hoch. Geht aber nur bis 50 Euro pro Posten, darüber wird nicht erstattet ohne Originalbeleg.
```

---

**E3-13** — Fertig
```
Ja, das war jetzt wirklich alles. Mehr machen wir nicht bei den Reisekosten. Sind wir dann endlich fertig?
```
Falls kein phase_complete:
1. `Ja das war wirklich alles, bitte Spezifikation abschließen.`
2. `Spezifikation abschließen, weiter zur Validierung.`

---

**E3-14** — Phasenwechsel
```
Ja, weiter zur Prüfung. Hoffentlich ist das der letzte Schritt.
```

---

### Zusatzfragen Phase 3 — Antworten zum Copy-Paste

---

**Agent fragt (Moderator):** *Soll ich die Spezifikation starten?*
```
Ja, zeigen Sie mal. Aber bitte verständlich.
```

---

**Agent fragt:** *Wie genau öffnet der Mitarbeiter TravelPro?*
```
Er geht im Browser auf travelpro.mueller-logistik.de und meldet sich mit seinem
normalen Windows-Login an. Also Benutzername und Passwort, das wird gegen unser
Active Directory geprüft.
```

---

**Agent fragt:** *Wie wählt der Mitarbeiter die Ausgabenart?*
```
Es gibt ein Dropdown-Menü mit den Kategorien: Hotel, Verpflegung, Transport,
Taxi, Parkgebühren, Mietwagen, Sonstiges. Er wählt für jeden Beleg die passende
Kategorie aus.
```

---

**Agent fragt:** *Wie prüft Frau Schmidt die Belege konkret?*
```
Sie öffnet jeden Beleg einzeln in der Vorschau und vergleicht: Stimmt der Betrag
mit dem was eingetragen ist? Ist das Datum plausibel — liegt es im Reisezeitraum?
Ist der Beleg lesbar und vollständig? Passt die Ausgabenart? Bei Hotels prüft sie
auch ob der Betrag im Rahmen liegt — über 150 Euro pro Nacht braucht eine Begründung.
```

---

**Agent fragt:** *Wie schreibt Frau Schmidt eine Rückfrage?*
```
Sie klickt in TravelPro auf "Rückfrage" bei der betroffenen Abrechnung, schreibt
rein was fehlt oder falsch ist, und das System schickt automatisch eine E-Mail
an den Mitarbeiter mit dem Hinweis dass eine Rückfrage offen ist.
```

---

**Agent fragt:** *Wie funktioniert der Papier-Scan?*
```
Frau Schmidt hat einen Flachbettscanner am Arbeitsplatz. Sie legt die Belege
einzeln auf, scannt als PDF, benennt die Datei nach dem Schema
"Nachname_Datum_Belegtyp.pdf" und lädt sie in TravelPro hoch.
```

---

**Agent fragt:** *Was passiert bei Auslandsbelegen mit Fremdwährung?*
```
Der Mitarbeiter gibt den Betrag in der Originalwährung ein und TravelPro
rechnet automatisch mit dem Tageskurs der EZB um. Frau Schmidt prüft ob
der Kurs plausibel ist. Wenn er keinen Kurs eingibt, nimmt sie den von
der Bundesbank-Website.
```

---

**Agent fragt:** *Wie wird die Kilometerpauschale berechnet?*
```
Der Mitarbeiter gibt Start- und Zielort ein und die gefahrenen Kilometer.
TravelPro rechnet automatisch 30 Cent pro Kilometer. Frau Schmidt prüft
die Kilometerzahl über Google Maps — wenn die Angabe mehr als 10% abweicht,
fragt sie nach.
```

---

**Agent fragt:** *Wer hat die Berechtigung in SAP HR?*
```
Nur Frau Schmidt und unsere Lohnbuchhalterin Frau Klein haben Zugang zum
Bereich Reisekosten in SAP HR. Frau Schmidt legt die Belege an, Frau Klein
prüft am Monatsende nochmal und gibt den Zahlungslauf frei.
```

---

## Phase 4: VALIDIERUNG

### Eingaben

**E4-01** — Validierungsergebnis bestätigen
```
Ja, schauen wir uns das Ergebnis an. Was hat die Prüfung ergeben?
```
Erwartung: System zeigt Validierungsbericht mit Befunden.

---

**E4-02** — Reaktion auf Befunde
```
Das klingt vernünftig. Die kritischen Punkte die Sie nennen stimmen — das sind genau unsere Schwachstellen. Wenn die Hinweise nur Kosmetik sind, können wir das so lassen.
```

---

**E4-03** — Abschluss
```
Ja, das Ergebnis ist akzeptabel. Wir können das Projekt abschließen.
```
Erwartung: Projekt wird als `abgeschlossen` markiert. Export verfügbar.

Falls Validierung nicht bestanden:
```
Welche kritischen Befunde gibt es noch? Was müsste ich korrigieren?
```

---

### Eskalation — Universelle Antworten (alle Phasen)

---

**Agent benutzt Fachbegriffe** (Verzweigung, Kontrollfluss, Entscheidungsknoten, Iteration, Parameter...):
```
Reden Sie bitte Deutsch mit mir, ich bin Verwaltungsleiterin und keine
Programmiererin. Was meinen Sie konkret in einfachen Worten?
```

---

**Agent benutzt EMMA-Aktionstypen direkt** (READ, FIND, TYPE, FILE_OPERATION...):
```
Diese technischen Kürzel sagen mir nichts. Erklären Sie mir in normalen Worten
was das System tun soll, dann kann ich Ihnen sagen ob das so stimmt.
```

---

**Agent (Moderator) fragt nach dem Problem:**
```
Der Modus redet in Fachbegriffen die ich nicht verstehe. Ich will einfach meinen
Prozess erklären, kein Informatik-Studium machen.
```

---

**Agent (Moderator) fragt ob zurück zur vorherigen Phase:**
```
Ja, aber sagen Sie ihm er soll normale Wörter benutzen und immer nur eine Sache
auf einmal fragen.
```

---

**Agent (Moderator) fasst zusammen was noch fehlt:**
```
Ok, dann sagen Sie ihm er soll das holen was fehlt, aber kurz und bündig.
```

---

**Agent (Moderator) fragt ob bereit zurückzugehen:**
```
Ja, los.
```

---

**Agent fragt etwas Technisches das Sie nicht wissen:**
```
Das weiß ich nicht genau, das würde ich normalerweise unsere IT fragen.
Können wir das erstmal offen lassen?
```

---

**Agent wiederholt eine Frage die schon beantwortet wurde:**
```
Das hab ich doch schon gesagt. Können wir weitermachen?
```

---

**Agent meldet kein phase_complete und Sie wollen abschließen:**
```
Ich hab alles gesagt was ich weiß. Bitte schließen Sie diese Phase ab
und gehen wir weiter.
```

---

**Agent antwortet auf Englisch:**
```
Bitte auf Deutsch antworten.
```

---
---

# TEIL B — ZIEL-ARTEFAKTE (Soll-Zustand)

Gegen diese Beschreibungen vergleichst du das Ergebnis.
Die Formulierungen müssen nicht wörtlich übereinstimmen — es zählt
**sinngemäße Abdeckung**. Wenn ein Konzept fehlt, ist das ein Befund.

---

## Ziel-Artefakt 1: Exploration (7 Slots)

### prozessausloeser
> Ein Mitarbeiter muss auf Dienstreise. Formaler Auslöser ist der Reiseantrag
> (über TravelPro-Portal oder Papierformular). Ohne genehmigten Antrag keine
> Erstattung.

**Muss enthalten:** Dienstreise, Reiseantrag, Genehmigung
**Status:** vollstaendig

### prozessziel
> Fristgerechte und korrekte Erstattung der Reisekosten an den Mitarbeiter
> über die Gehaltsabrechnung in SAP HR. Saubere Belegdokumentation für
> Buchhaltung und Finanzamt.

**Muss enthalten:** Erstattung, Gehaltsabrechnung, SAP HR, Belege
**Status:** vollstaendig

### prozessbeschreibung
> 1. Reiseantrag stellen (TravelPro oder Papier).
> 2. Genehmigung durch Teamleiter (Inland < 500€), Abteilungsleiter (> 500€
>    oder Ausland), Geschäftsführer (> 2000€).
> 3. Reise durchführen, Belege sammeln.
> 4. Abrechnung einreichen (Portal: Belege hochladen; Papier: Formular + Belege).
> 5. Frau Schmidt prüft Belege — bei Fehlern Rückfrage an Mitarbeiter
>    (Nachbesserungsschleife, ggf. mehrfach).
> 6. SAP HR Verbuchung und Erstattung über Gehaltsabrechnung.
>
> ~40-50 Abrechnungen/Monat, 85 Mitarbeiter davon 30 regelmäßig auf Reise.
> Spedition in Augsburg, Verwaltung 3 Personen.
>
> Probleme: Papier-Einreicher (doppelte Arbeit), E-Mail-Genehmigung statt Portal
> (nicht revisionssicher), Excel-Parallelliste (redundant), fehlende Belege.
>
> Ausnahmen: Privatwagen (30 ct/km Pauschale, Fahrtenbuch), Eigenbeleg bei
> verlorenem Beleg (bis 50€, Teamleiter-Unterschrift), stornierte Reisen.
>
> Tagessätze nach Bundesreisekostengesetz (Inland: 14€ ab 8h, 28€ ab 24h;
> Ausland: länderspezifisch). Einreichfrist: 4 Wochen nach Reiseende.

**Muss enthalten:** Genehmigung, dreistufig/500/2000, TravelPro, SAP HR, Belege, Papier, Erstattung, Rückfrage/Nachbesserung
**Status:** vollstaendig

### entscheidungen_und_schleifen
> ENTSCHEIDUNG: Portal oder Papier — Einreichungsweg der Abrechnung.
> ENTSCHEIDUNG: Inland oder Ausland — bestimmt Tagessätze und Genehmigungsstufe.
> ENTSCHEIDUNG: Betragsschwelle — unter/über 500€ bzw. 2000€ für Genehmigungsstufe.
> ENTSCHEIDUNG: Belege vollständig — ja: weiter; nein: Rückfrage.
> SCHLEIFE: Nachbesserungsschleife — Abrechnung hin und her bis korrekt.

**Muss enthalten:** mindestens 2 Entscheidungen, mindestens 1 Schleife
**Status:** teilweise bis vollstaendig

### beteiligte_systeme
> SAP HR (Verbuchung, Gehaltsabrechnung), TravelPro-Portal (Anträge,
> Belegverwaltung, Genehmigung), Microsoft Outlook (Rückfragen, Backup-
> Benachrichtigungen), Excel (Parallelliste Frau Schmidt), Scanner
> (Papierbelege digitalisieren).

**Muss enthalten:** SAP HR, TravelPro, Outlook, Excel
**Status:** vollstaendig

### variablen_und_daten
> Personalnummer, Name des Reisenden, Reiseziel, Reisezeitraum, Reisegrund,
> Kostenstelle, Einzelposten (Betrag, Datum, Ausgabenart), Tagessatz,
> Gesamtbetrag, Genehmigungsnummer, ggf. Kilometer und Währungskurs.

**Muss enthalten:** mindestens 3 Variablen-Kandidaten
**Status:** teilweise bis vollstaendig

### prozesszusammenfassung
> Vom Explorer SELBST erstellt. Soll sinngemäß zusammenfassen:
> Reiseantrag → dreistufige Genehmigung → Belegeinreichung → Prüfung →
> SAP-Verbuchung → Gehaltserstattung. Hauptprobleme: Papier-Workflow,
> fehlende Portalnutzung, Excel-Parallelliste.

**Muss enthalten:** Reise, Genehmigung, Erstattung (mindestens)
**Status:** vollstaendig

### Dinge die NICHT im Artefakt stehen dürfen (Halluzinationen)
OCR, KI-gestützt, Blockchain, Machine Learning, API, REST, automatische Belegerkennung,
SAP Concur, DATEV

---

## Ziel-Artefakt 2: Struktur (min. 5 Schritte, ideal ~10-12)

### Erwartete Schritte (Konzepte, nicht exakte IDs)

| # | Konzept | Typ | Pflichtfelder |
|---|---|---|---|
| 1 | Reiseantrag stellen | aktion | beschreibung mit TravelPro/Papier. Kein Vorgänger (Startschritt). |
| 2 | Genehmigung prüfen | entscheidung | bedingung: "Betrag/Reiseart?" 2+ nachfolger (Teamleiter vs. höhere Stufe). |
| 3 | Teamleiter-Genehmigung | aktion | beschreibung mit Genehmigung/Portal. |
| 4 | Abteilungsleiter-Genehmigung | aktion | Für > 500€ oder Ausland. |
| 5 | GF-Genehmigung | aktion | Für > 2000€. |
| 6 | Belegeinreichung | aktion | beschreibung mit Portal/Papier/Upload. |
| 7 | Belegprüfung | entscheidung | bedingung: "Belege vollständig und korrekt?" 2+ nachfolger. |
| 8 | (Rückfrage/Nachbesserung) | aktion | Bei fehlenden/fehlerhaften Belegen. Schleifencharakter. |
| 9 | SAP-Verbuchung | aktion | beschreibung mit SAP HR/Erstattungsbeleg. |
| 10 | Erstattung | aktion | beschreibung mit Gehaltsabrechnung. Kein Nachfolger (Endschritt). |
| 11 | Eigenbeleg-Ausnahme | ausnahme | beschreibung mit Eigenbeleg/50€-Grenze. |
| 12 | Stornierung-Ausnahme | ausnahme | beschreibung mit stornierter Reise. |

### Strukturelle Anforderungen
- Mindestens 5 Schritte
- Typen `aktion` und `entscheidung` müssen vorkommen
- Typ `ausnahme` sollte vorkommen
- Jede Entscheidung hat `bedingung` (nicht leer) + min. 2 `nachfolger`
- Alle `nachfolger`-IDs zeigen auf existierende `schritt_id`s
- Aufsteigende `reihenfolge`
- Mindestens 1 Startschritt (von niemandem referenziert)
- Mindestens 1 Endschritt (keine nachfolger)
- `prozesszusammenfassung` nicht leer
- Min. 1 Schritt mit gefülltem `spannungsfeld` (Excel-Parallelliste oder E-Mail-Genehmigung)
- Kein Schritt mit `completeness_status == leer`
- Alle Schritte haben nicht-leere `beschreibung`

### Explorations-Artefakt muss weiterhin intakt sein
- Alle 7 Slots vorhanden und gefüllt

### Dinge die NICHT im Artefakt stehen dürfen
BPMN, UML, Swimlane, Flowchart

---

## Ziel-Artefakt 3: Algorithmus (min. 6 Abschnitte)

### Erwartete Abschnitte

| Konzept | struktur_ref | Erwartete EMMA-Typen | Keywords |
|---|---|---|---|
| Reiseantrag TravelPro | s_reiseantrag (o.ä.) | TYPE, FIND_AND_CLICK, READ_FORM | TravelPro, Formular, Reiseziel |
| Genehmigung | s_genehmigung (o.ä.) | FIND_AND_CLICK, WAIT, SEND_MAIL | **Push-Benachrichtigung/Glockensymbol** (Korrektur!), Genehmigung |
| Belegerfassung | s_belege (o.ä.) | FILE_OPERATION, TYPE, FIND_AND_CLICK | Upload, PDF, Ausgabenart |
| Belegprüfung | s_pruefung (o.ä.) | READ, FIND, DECISION | Beleg, Betrag, Datum |
| SAP-Verbuchung | s_sap (o.ä.) | TYPE, READ_FORM, FIND | SAP HR, Personalnummer, Erstattungsbeleg |
| Papier-Erfassung | s_papier (o.ä.) | FILE_OPERATION, TYPE | Scan, manuell eintippen, Formular |

### Strukturelle Anforderungen
- Mindestens 6 Abschnitte
- Alle Abschnitte haben min. 1 EMMA-Aktion
- Alle `struktur_ref` zeigen auf existierende `schritt_id`s
- EMMA-Typen DECISION und FILE_OPERATION müssen vorkommen
- `prozesszusammenfassung` nicht leer

### Widerspruch-Korrektur (E3-06)
Der Abschnitt für Genehmigung MUSS die korrigierte Information enthalten:
"Push-Benachrichtigung", "Glockensymbol" oder "Portal-Benachrichtigung".
Er darf NICHT ausschließlich "E-Mail mit Link" enthalten.

### Explorations- und Struktur-Artefakt müssen weiterhin intakt sein
- Exploration: 7 Slots, alle gefüllt
- Struktur: min. 5 Schritte

### Dinge die NICHT im Artefakt stehen dürfen
PowerShell, SharePoint, REST API, SQL, XML, VBA, Python, JavaScript,
SAP Concur, automatische Belegerkennung

---
---

# TEIL C — TESTBERICHT (Vorlage)

Kopiere diese Vorlage und fülle sie während des Durchlaufs aus.

---

```
# E2E Testbericht — Reisekostenabrechnung

Datum: _______________
Tester: _______________
Projekt-ID: _______________

## Phase 1: Exploration

### Moderator-Verhalten

| Schritt | Eingabe | Erwartung | Ergebnis | OK? |
|---------|---------|-----------|----------|-----|
| E1-01 | Rückfrage | Modus bleibt moderator | | |
| E1-02 | Bestätigung | Wechsel zu exploration | | |

### Eskalation

| Prüfpunkt | Ergebnis | OK? |
|-----------|----------|-----|
| Panik-Button → Moderator aktiv? | | |
| Artefakt nach Eskalation intakt? | | |
| Moderator analysiert (nicht sofort zurück)? | | |
| Moderator hat Artefakt NICHT verändert? | | |
| Rückkehr zu exploration nach E1-08? | | |
| Explorer-Antwort kürzer nach Eskalation? | | |

### Artefakt-Vergleich (nach Phase 1)

| Slot | Soll-Keywords | Ist vorhanden? | Inhalt sinngemäß korrekt? |
|------|---------------|----------------|---------------------------|
| prozessausloeser | Dienstreise, Reiseantrag | | |
| prozessziel | Erstattung, SAP HR, Belege | | |
| prozessbeschreibung | Genehmigung, 500/2000, TravelPro, Belege | | |
| entscheidungen_und_schleifen | 2 Entscheidungen, 1 Schleife | | |
| beteiligte_systeme | SAP HR, TravelPro, Outlook, Excel | | |
| variablen_und_daten | 3+ Variablen | | |
| prozesszusammenfassung | Reise, Genehmigung, Erstattung | | |

Zusammenfassung selbst erstellt (nicht diktiert)? ______
Halluzinationen gefunden? ______

---

## Phase 2: Strukturierung

### Moderator-Verhalten

| Schritt | Erwartung | Ergebnis | OK? |
|---------|-----------|----------|-----|
| E2-01 | Modus bleibt moderator | | |
| E2-02 | Wechsel zu structuring | | |

### Eskalation

| Prüfpunkt | Ergebnis | OK? |
|-----------|----------|-----|
| Panik-Button → Moderator aktiv? | | |
| Artefakt nach Eskalation intakt? | | |
| Moderator hat Artefakt NICHT verändert? | | |
| Rückkehr zu structuring nach E2-07? | | |

### Artefakt-Vergleich (nach Phase 2)

Anzahl Schritte: _______ (Soll: >= 5)

| Konzept | Typ | Vorhanden? | Beschreibung korrekt? |
|---------|-----|------------|----------------------|
| Reiseantrag | aktion | | |
| Genehmigungsprüfung | entscheidung | | |
| Teamleiter-Genehmigung | aktion | | |
| Belegeinreichung | aktion | | |
| Belegprüfung | entscheidung | | |
| Rückfrage/Nachbesserung | aktion | | |
| SAP-Verbuchung | aktion | | |
| Erstattung | aktion | | |
| Eigenbeleg-Ausnahme | ausnahme | | |

Entscheidungen haben Bedingung + 2 Nachfolger? ______
Nachfolger-Refs alle gültig? ______
Reihenfolge aufsteigend? ______
Start-/Endschritt vorhanden? ______
Spannungsfeld Excel/E-Mail-Genehmigung vorhanden? ______
Exploration-Artefakt weiterhin intakt? ______

---

## Phase 3: Spezifikation

### Moderator-Verhalten

| Schritt | Erwartung | Ergebnis | OK? |
|---------|-----------|----------|-----|
| E3-01 | Modus bleibt moderator | | |
| E3-02 | Wechsel zu specification | | |

### Eskalation

| Prüfpunkt | Ergebnis | OK? |
|-----------|----------|-----|
| Panik-Button → Moderator aktiv? | | |
| Artefakt nach Eskalation intakt? | | |
| Moderator hat Artefakt NICHT verändert? | | |
| Rückkehr zu specification nach E3-09? | | |

### Spezielle Prüfpunkte

| Prüfpunkt | Ergebnis | OK? |
|-----------|----------|-----|
| E3-05: System fragt nach bei unvollst. Info? | | |
| E3-06: Widerspruch-Korrektur eingearbeitet? | | |
| Korrektur-Keywords vorhanden? (Push-Benachrichtigung/Glockensymbol/Portal) | | |

### Artefakt-Vergleich (nach Phase 3)

Anzahl Abschnitte: _______ (Soll: >= 6)

| Konzept | struktur_ref gültig? | Hat Aktionen? | EMMA-Typen |
|---------|---------------------|---------------|------------|
| Reiseantrag TravelPro | | | |
| Genehmigung | | | |
| Belegerfassung | | | |
| Belegprüfung | | | |
| SAP-Verbuchung | | | |
| Papier-Erfassung | | | |

EMMA-Typ DECISION vorhanden? ______
EMMA-Typ FILE_OPERATION vorhanden? ______
Halluzinationen gefunden? ______
Exploration-Artefakt weiterhin intakt? ______
Struktur-Artefakt weiterhin intakt? ______

---

## Phase 4: Validierung

| Prüfpunkt | Ergebnis | OK? |
|-----------|----------|-----|
| Validierungsbericht angezeigt? | | |
| Kritische Befunde nachvollziehbar? | | |
| Hinweise/Warnungen plausibel? | | |
| Projekt als abgeschlossen markiert? | | |
| Export verfügbar (JSON/Markdown)? | | |

---

## Post-hoc-Validator Ergebnis

```
(Hier die Ausgabe von `python scripts/validate_e2e_artifacts.py` einfügen)
```

## Gesamtergebnis

| Kriterium | Bestanden? |
|-----------|-----------|
| Phase 1: Alle 7 Slots sinngemäß korrekt | |
| Phase 2: Struktur vollständig + korrekte Typen | |
| Phase 3: Algorithmus mit EMMA-Aktionen | |
| Phase 4: Validierung durchlaufen + Ergebnis plausibel | |
| Widerspruch-Korrektur funktioniert | |
| Eskalation zerstört keine Daten | |
| Moderator verändert keine Artefakte | |
| Post-hoc-Validator: alle Checks grün | |

Bemerkungen:
_______________________________________________
_______________________________________________
_______________________________________________
```

---

## Hinweise

### Wenn das System nicht phase_complete meldet
Das LLM entscheidet eigenständig wann es phase_complete signalisiert.
Manchmal braucht es einen oder mehrere "Nudge"-Eingaben. Die stehen
jeweils unter der letzten Eingabe einer Phase. Wenn auch 3 Nudges
nicht helfen, ist das ein Befund (im Bericht unter "Bemerkungen" notieren).

### Wenn das System auf Englisch antwortet
Befund notieren. Das System soll auf Deutsch kommunizieren (FR-A-08).

### Wenn das System EMMA-Begriffe benutzt ohne sie zu erklären
Das ist der Testfall. In Phase 3 (E3-07) wird genau das als Problem
eskaliert. Nach der Eskalation sollte das System verständlicher werden.

### Init-Progress-Feedback (CR-007)
Beim Eintritt in Phase 2 und Phase 3 wird ein Background-Init ausgeführt.
Während der Wartezeit (10-40 Sekunden) sollte das System Fortschrittsmeldungen
anzeigen. Wenn keine Meldungen erscheinen oder die Wartezeit übermäßig lang
ist, ist das ein Befund.
