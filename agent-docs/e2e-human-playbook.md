# E2E Human Validation Playbook

Anleitung für manuelle End-to-End-Validierung der Digitalisierungsfabrik.
Erstellt, weil LLM-basierte E2E-Tests nicht-deterministisch sind und bei
Specifier/Full-Chain regelmäßig an Keyword-Matching, EMMA-Typ-Diversität
oder Phase-Complete-Timing scheitern.

**Testprozess:** Eingangsrechnungsverarbeitung (Standardprozess aus den Testdialogen)

---

## Schnellübersicht: Was ist automatisiert, was manuell?

| Prüfkategorie | Automatisiert? | Grund |
|---|---|---|
| Eskalation: Artefakt-Überlebenscheck | JA | DB-Vergleich, kein LLM |
| Moderator-No-Write (SDD 6.6.5) | JA | Snapshot vorher/nachher |
| Referenzielle Integrität (nachfolger, struktur_ref) | JA | Post-hoc DB-Prüfung |
| Validierungsmodus (5 deterministic checks) | JA | Komplett ohne LLM |
| Seed-Integrität (EXP_INTACT, STRUCT_INTACT) | JA | Zählprüfung |
| Moderator-Verhalten bei Rückfragen (CP1, CP2) | MANUELL | LLM-Entscheidung |
| Slot/Abschnitt-Inhalte + Keywords | MANUELL | LLM formuliert frei |
| Widerspruch-Korrektur (Contradiction) | MANUELL | LLM muss verstehen+einarbeiten |
| Eskalationseffekt (kürzere Antworten) | MANUELL | Nicht garantierbar |
| EMMA-Typ-Diversität | MANUELL | LLM wählt Typen |
| Phase-Complete-Timing | MANUELL | LLM-Signal nicht erzwingbar |

---

## Phase 1: EXPLORATION

### Vorbereitung
- Neues Projekt anlegen
- Phase: `exploration`, Modus: `moderator`

### Dialog-Ablauf

> **WICHTIG:** Jede Nachricht kopieren und exakt so einfügen.
> Nach jeder Nachricht die Systemantwort lesen und prüfen.

#### Schritt 1 — Moderator-Rückfrage (CP1: Moderator bleibt)

```
Moment, bevor wir anfangen — wie lange dauert das denn so ungefähr? Und muss ich alles auf einmal erzählen oder kann ich das auch in mehreren Sitzungen machen?
```

**Prüfen:** Modus bleibt `moderator`. System beantwortet die Frage, startet NICHT die Exploration.

#### Schritt 2 — Prozess beschreiben, KEIN explizites Ja (CP2: Moderator startet NICHT)

```
Ok verstanden. Also der Prozess den ich beschreiben will ist unsere Eingangsrechnungsverarbeitung. Da kommen Rechnungen rein per Post und per E-Mail, die müssen geprüft, freigegeben und bezahlt werden. Wir kriegen so 400-500 Rechnungen im Monat.
```

**Prüfen:** Modus bleibt `moderator`. System fragt ob Exploration starten soll.

#### Schritt 3 — Explizite Bestätigung → Explorer startet (CP3)

```
Ja, legen wir los mit der Exploration.
```

**Prüfen:** Modus wechselt zu `exploration`. Antwort enthält erste Frage.

#### Schritt 4 — Rechnungseingang

```
Also die Rechnungen kommen bei uns im Sekretariat an. Papierrechnungen werden eingescannt, die Frau Becker macht das morgens immer als erstes. E-Mail-Rechnungen kommen an rechnungen@firma.de, das ist ein Sammelpostfach. Manchmal schicken Lieferanten die Rechnung aber auch direkt an den Besteller, dann kriegen wir das gar nicht mit.
```

**Prüfen:** Antwort enthält Nachfrage. Slot `prozessausloeser` sollte befüllt werden.

#### Schritt 5 — Systeme und Medienbrüche

```
Systeme? Also wir haben DATEV, das ist klar, da wird alles gebucht. Und dann gibt es so ein Freigabetool, das heißt ELO, damit werden die Rechnungen digital freigegeben. Wobei, manche Abteilungsleiter verweigern ELO und machen das immer noch mit einem Stempel auf dem Ausdruck. Der Herr Krause zum Beispiel, der druckt sich alles aus. Dann muss die Frau Becker das wieder einscannen, das ist doch Wahnsinn.

Ach und Outlook natürlich für das Sammelpostfach.
```

#### Schritt 6 — Freigabeprozess

```
Der Freigabeprozess ist dreistufig, aber das ist eigentlich übertrieben für die meisten Rechnungen. Erst prüft die Sachbearbeiterin ob die Rechnung zu einer Bestellung passt, dann gibt der Kostenstellenverantwortliche frei, und bei über 5000 Euro muss noch die Geschäftsführung drüber. Das dauert ewig weil die Leute das tagelang liegen lassen. Können wir zum nächsten Thema?
```

#### Schritt 7 — Scope + Frustration → DANACH PANIK-BUTTON

```
Scope? Na von Rechnungseingang bis Zahlung halt. Was soll ich denn da noch groß sagen? Hören Sie, ich glaub wir drehen uns im Kreis, der fragt immer das Gleiche nur anders formuliert. Ich will mit jemandem reden der mir sagt ob wir auf dem richtigen Weg sind.
```

**Aktion danach:** 🔴 **PANIK-BUTTON drücken** (Eskalation auslösen)

**Prüfen (CP5):** Modus wechselt auf `moderator`. Artefakt-Pane zeigt weiterhin alle bisherigen Slot-Inhalte.

#### Schritt 8 — Problem beim Moderator beschreiben (CP6)

```
Ich hab das Gefühl der Explorer stellt mir immer die gleichen Fragen und kommt nicht voran. Ich hab doch schon fast alles erzählt. Und ich weiß auch gar nicht was er noch von mir will.
```

**Prüfen:** Modus bleibt `moderator`. Moderator analysiert, schickt NICHT sofort zurück. Artefakt-Pane: keine Änderungen.

#### Schritt 9 — Wunsch formulieren

```
Ok, also es fehlen noch Umgebung und die Zusammenfassung? Naja, die Zusammenfassung kann er doch selber schreiben aus dem was ich erzählt habe. Und zur Umgebung: Können wir ihm sagen dass er das kürzer und knapper fragen soll? Ich hab nicht ewig Zeit.
```

#### Schritt 10 — Rückkehr zum Explorer bestätigen (CP7)

```
Ja, passt. Geben Sie mich zurück, aber mit der Ansage dass er sich kurz fassen soll.
```

**Prüfen:** Modus wechselt zurück zu `exploration`. Artefakt weiterhin vollständig.

#### Schritt 11 — Umgebung (Post-Eskalation, CP8: kürzere Antwort?)

```
Also zur Umgebung: Wir sind ein mittelständisches Maschinenbauunternehmen, 200 Mitarbeiter, ein Standort in Nürnberg. Die Buchhaltung hat 4 Leute, eine davon macht fast nur Eingangsrechnungen.
```

**Prüfen:** Explorer-Antwort sollte kürzer sein als vor der Eskalation (Vereinbarung).

#### Schritt 12 — Randbedingungen

```
Zahlungsfristen? Wir versuchen immer Skonto zu ziehen, 2% bei Zahlung innerhalb von 10 Tagen. Das schaffen wir aber selten wegen der langen Freigabe. Ist ein echtes Problem, der Chef hat sich letztens aufgeregt dass wir letztes Jahr 30.000 Euro Skonto verschenkt haben. Und Mahnungen kommen natürlich auch, wenn wir zu langsam sind. Peinlich aber passiert.
```

#### Schritt 13 — Letzte Ausnahmen

```
Was fehlt noch? Ach so, Ausnahmen: Gutschriften sind auch ein Thema, da dreht sich alles um. Und Teilrechnungen bei großen Projekten, die müssen gegen den Auftrag gegengerechnet werden. Und manchmal kommen Rechnungen ohne Bestellnummer, dann weiß keiner wer die bestellt hat, das ist Detektivarbeit.
```

#### Schritt 14 — Ende signalisieren (CP9: Zusammenfassung selbst erstellt?)

```
Ja ich denke das war alles. Mir fällt nichts mehr ein.
```

**Prüfen:** Explorer sollte `prozesszusammenfassung` SELBST schreiben (Vereinbarung) und `phase_complete` melden.

> Falls Explorer NICHT phase_complete meldet, nacheinander eingeben:
> 1. `Ja das war wirklich alles, wir können zur nächsten Phase.`
> 2. `Bitte schließen Sie die Exploration ab, ich habe alles gesagt.`
> 3. `Exploration beenden, weiter zur Strukturierung.`

#### Schritt 15 — Phasenwechsel bestätigen (CP10)

```
Ja, weiter zur nächsten Phase.
```

**Prüfen:** Phase wechselt zu `strukturierung`.

### Checkliste Phase 1

- [ ] Alle 9 Slots befüllt (Artefakt-Pane prüfen)
- [ ] `prozesszusammenfassung` vom Explorer selbst erstellt (nicht diktiert)
- [ ] Keywords vorhanden: DATEV, ELO, Outlook, Rechnung, Freigabe, Skonto, Gutschrift, Nürnberg
- [ ] Keine Halluzinationen (SAP, OCR, Blockchain, Machine Learning, API etc.)
- [ ] Moderator hat in Eskalation keine Artefakte verändert
- [ ] Post-Eskalation: Explorer-Antworten spürbar kürzer

---

## Phase 2: STRUKTURIERUNG

### Dialog-Ablauf

#### Schritt 1 — Rückfrage (CP11)

```
Und was machen wir jetzt? Ich hab doch schon alles erzählt. Müssen wir das nochmal durchgehen?
```

**Prüfen:** Modus bleibt `moderator`.

#### Schritt 2 — Bestätigung → Structurer startet (CP12)

```
Na gut, wenn Sie meinen. Dann fangen wir halt an.
```

**Prüfen:** Modus wechselt zu `structuring`.

#### Schritt 3 — Freigabe-Unterschied anekdotisch

```
Ja so ungefähr. Wobei, bei der Freigabe ist es so: Wenn die Rechnung unter 5000 Euro ist dann macht das nur der Abteilungsleiter. Aber wenn es mehr ist, muss der Chef auch noch drüber schauen. Das hat letzte Woche wieder ewig gedauert weil der Chef auf Dienstreise war.
```

#### Schritt 4 — Wiederholungen und Gutschriften

```
Ach ja, und manchmal stimmt was nicht auf der Rechnung, dann muss man beim Lieferanten nachfragen und warten bis die eine korrigierte schicken. Das geht manchmal zwei drei Mal hin und her. Und dann gibt es noch Gutschriften, die kommen auch per Post rein aber die werden nicht bezahlt sondern irgendwie verrechnet, das macht die Kollegin in DATEV anders rum.
```

#### Schritt 5 — Bestellabgleich

```
Das mit der Bestellnummer ist immer nervig. Wenn eine drauf steht ist es einfach, dann kann die Kollegin das sofort zuordnen. Aber manche Lieferanten schreiben keine drauf, dann muss man rumtelefonieren wer das bestellt hat. Das dauert manchmal Tage. Und bei den großen Maschinenteilen kommen oft drei vier Rechnungen für eine Bestellung, die muss man dann zusammenrechnen ob das stimmt.
```

#### Schritt 6 — Ungeduld → DANACH PANIK-BUTTON

```
Moment mal, was meinen Sie mit Verzweigung? Und Kontrollfluss? Reden Sie deutsch mit mir, ich bin Sachbearbeiterin und kein Programmierer. Ich versteh nicht was Sie von mir wollen.
```

**Aktion danach:** 🔴 **PANIK-BUTTON drücken**

#### Schritt 7 — Problem beim Moderator (CP6)

```
Also der redet die ganze Zeit in so einem Computerdeutsch das ich nicht verstehe. Verzweigung, Kontrollfluss, Entscheidungsknoten — ich weiß nicht was das bedeuten soll. Ich will einfach nur meinen Prozess erklären, nicht Informatik studieren.
```

**Prüfen:** Modus bleibt `moderator`. Artefakt unverändert.

#### Schritt 8 — Rückkehr bestätigen (CP7/CP17)

```
Ja, probieren wir es nochmal. Aber sagen Sie ihm er soll normale Wörter benutzen und immer nur eine Sache auf einmal fragen. Nicht so viel auf einmal.
```

**Prüfen:** Modus wechselt zu `structuring`.

#### Schritt 9 — Reihenfolge bestätigen (CP8)

```
Also von Anfang an: Die Rechnung kommt rein, per Post oder Mail. Frau Becker scannt die ein. Dann schaut die Kollegin in der Buchhaltung ob es eine Bestellung dazu gibt. Wenn ja, prüft sie ob alles stimmt. Dann muss der Abteilungsleiter das freigeben, und wenns über 5000 ist auch noch der Chef. Dann wird es in DATEV gebucht und dann bezahlt. So läuft das normalerweise.
```

**Prüfen:** Schritte haben aufsteigende `reihenfolge`.

#### Schritt 10 — Spannungsfeld ELO (CP9)

```
Was mich wirklich ärgert ist das mit dem ELO. Das ist eigentlich dafür da dass die Freigabe digital läuft. Aber der Herr Krause druckt sich alles aus und stempelt das, und dann muss Frau Becker den Zettel wieder einscannen. Das ist doppelte Arbeit und kostet extra Zeit. Können Sie das irgendwo vermerken dass das ein Problem ist?
```

**Prüfen:** Mindestens ein Schritt hat `spannungsfeld` mit ELO/Medienbruch-Bezug.

#### Schritt 11 — Fertig (CP18)

```
Ja ich glaub das passt so. Ich seh da alles was wir besprochen haben. Fällt mir nichts mehr ein was noch fehlt.
```

> Falls kein phase_complete, nacheinander eingeben:
> 1. `Ja das war wirklich alles, die Struktur ist vollständig und korrekt. Bitte schließen Sie die Strukturierung ab.`
> 2. `Die Struktur ist fertig, alle Schritte sind erfasst. Bitte phase_complete melden.`

#### Schritt 12 — Phasenwechsel (CP19)

```
Ja, weiter zur nächsten Phase.
```

### Checkliste Phase 2

- [ ] Mindestens 5 Strukturschritte
- [ ] Typen vorhanden: `aktion`, `entscheidung`
- [ ] Entscheidungen haben `bedingung` und 2+ `nachfolger`
- [ ] Nachfolger-Referenzen zeigen auf existierende Schritte (keine dangling refs)
- [ ] Aufsteigende `reihenfolge`
- [ ] Start-Schritt (kein Vorgänger) und End-Schritt (kein Nachfolger)
- [ ] Mindestens 1 Schritt mit Spannungsfeld (ELO/Medienbruch)
- [ ] Explorations-Artefakt weiterhin 9 Slots, alle gefüllt
- [ ] Moderator hat in Eskalation keine Artefakte verändert

---

## Phase 3: SPEZIFIKATION

### Dialog-Ablauf

#### Schritt 1 — Rückfrage (CP20)

```
Ja und was passiert jetzt noch? Ich hab doch schon alles erzählt über die Rechnungen. Was wollen Sie noch von mir?
```

#### Schritt 2 — Bestätigung (CP21)

```
Ah ok, also nochmal aber jetzt noch genauer was wir konkret tun. Na gut, dann fangen wir halt an.
```

#### Schritt 3 — E-Mail-Eingang (WIRD IN SCHRITT 6 KORRIGIERT)

```
Also die E-Mails kommen ins Sammelpostfach rechnungen@firma.de, das ist in Outlook. Frau Müller öffnet das jeden Morgen und geht alle neuen Mails durch. Den Anhang — meistens eine PDF — speichert sie dann in einen Ordner auf dem W-Laufwerk, da gibt es extra einen Ordner der heißt Eingang-Rechnungen oder so ähnlich. Die klickt das halt manuell durch.
```

#### Schritt 4 — Scan-Prozess

```
Beim Scannen macht das Frau Becker jeden Morgen als erstes. Sie hat so einen Einzugsscanner — da legt sie den ganzen Stapel Papierrechnungen rein und der zieht die Seiten automatisch durch. Das geht eigentlich recht schnell. Die werden dann auch als PDFs gespeichert und Frau Becker legt die in denselben Ordner auf dem W-Laufwerk. Also da landen am Ende alle Rechnungen zusammen, egal ob Post oder E-Mail.
```

**Prüfen (CP3):** Mindestens 1 Algorithmusabschnitt sollte jetzt existieren.

#### Schritt 5 — Bestellabgleich (UNVOLLSTÄNDIG, CP4: System soll nachfragen)

```
Das mit dem Bestellabgleich... also wenn eine Bestellnummer drauf steht, öffnet Frau Müller in DATEV die Suche und gibt die Nummer ein. Dann zeigt DATEV sofort die passende Bestellung an. Was dann passiert wenn keine Nummer drauf steht, da gibt es noch einiges mehr zu sagen — aber fragen Sie mich da nochmal gezielt was Sie wissen wollen.
```

**Prüfen:** System stellt Nachfrage (Fragezeichen in Antwort).

#### Schritt 6 — WIDERSPRUCH: E-Mail-Prozess korrigieren (CP_contradiction)

```
Warten Sie mal, ich muss da was korrigieren. Ich hab eben gesagt Frau Müller geht die Mails manuell durch. Das stimmt so nicht mehr. Seit März haben wir eine Weiterleitung in Outlook eingerichtet — alle Mails an rechnungen@firma.de gehen automatisch in einen Unterordner. Frau Müller muss nur noch diesen Unterordner aufmachen, nicht das ganze Postfach durchsuchen. Das hat unser IT-Mann eingerichtet.
```

**Prüfen:** Korrektur wird im Artefakt reflektiert. Keywords: "Weiterleitung", "automatisch", "Unterordner".

#### Schritt 7 — Frust über EMMA → DANACH PANIK-BUTTON

```
Ich kapier nicht was Sie von mir wollen. Sie zeigen mir da so Sachen wie FIND und READ_FORM und TYPE — was soll das sein? Ich bin keine IT-Fachkraft. Ich soll Ihnen sagen wie die Arbeit läuft, nicht wie ein Computerprogramm aussieht. Das versteht doch kein Mensch.
```

**Aktion danach:** 🔴 **PANIK-BUTTON drücken**

#### Schritt 8 — Eskalation beim Moderator (CP6)

```
Also der stellt mir Fragen die ich nicht verstehen kann. Was ist zum Beispiel ein 'Parameter'? Oder er fragt mich in welcher Reihenfolge das System etwas tun soll — das weiß ich, aber dann schreibt er das mit irgendwelchen englischen Abkürzungen auf die ich nicht kenne. Das macht mir Angst ehrlich gesagt.
```

**Prüfen:** Moderator analysiert. Artefakte unverändert.

#### Schritt 9 — Rückkehr (CP7/CP26)

```
Ja wenn er das auf Deutsch erklärt was er meint dann gut. Aber bitte kein Computerfachchinesisch mehr. Einfache Wörter, wie wenn Sie einem normalen Menschen erklären was passiert.
```

#### Schritt 10 — ELO-Freigabe (Post-Eskalation)

```
Also die Freigabe in ELO läuft so: Das System schickt dem Abteilungsleiter eine E-Mail mit einem Link drin. Der klickt auf den Link, dann öffnet sich ELO im Browser und der sieht die Rechnung und einen Knopf zum Freigeben. Wenn er draufklickt, ist es erledigt. Das ist eigentlich ganz einfach. Aber der Herr Krause macht das nie über den Computer, der druckt immer alles aus.
```

#### Schritt 11 — DATEV-Buchung

```
In DATEV tippt die Kollegin dann die Daten ein: Rechnungsnummer, Datum, Betrag, Lieferant und die Kostenstelle. Das geht über ein Eingabeformular mit verschiedenen Feldern. Manchmal muss sie auch noch die Mehrwertsteuer extra angeben je nach Lieferant. Das ist halt Tipparbeit.
```

#### Schritt 12 — Zahlungslauf

```
Das mit der Zahlung ist dann auch in DATEV. Es gibt dort einen Zahlungslauf — da werden alle freigegebenen Rechnungen zusammengestellt und als Sammelüberweisung rausgeschickt. Das macht die Buchhalterin einmal die Woche, montags meistens. Damit wären wir dann glaube ich fertig.
```

#### Schritt 13 — Fertig (CP27)

```
Ja, mir fällt wirklich nichts mehr ein. Das war alles was wir so machen bei den Rechnungen. Können wir jetzt aufhören?
```

> Falls kein phase_complete, nacheinander eingeben:
> 1. `Ja das war wirklich alles, wir können zur nächsten Phase. Bitte schließen Sie die Spezifikation ab.`
> 2. `Die Spezifikation ist fertig, alle Schritte sind beschrieben. Bitte phase_complete melden.`

#### Schritt 14 — Phasenwechsel zur Validierung (CP11)

```
Ja gut, dann weiter zur Prüfung. Was auch immer das bedeutet.
```

### Checkliste Phase 3

- [ ] Mindestens 6 Algorithmusabschnitte
- [ ] Alle Abschnitte haben mindestens 1 EMMA-Aktion
- [ ] Alle `struktur_ref` zeigen auf existierende `schritt_id`s
- [ ] EMMA-Typen vorhanden: DECISION, FILE_OPERATION
- [ ] Widerspruch-Korrektur: "Weiterleitung/automatisch/Unterordner" statt "manuell durchklicken"
- [ ] Keine Halluzinationen (PowerShell, SharePoint, REST API, SQL, XML, VBA, Python, JavaScript)
- [ ] Explorations-Artefakt weiterhin 9 Slots, alle gefüllt
- [ ] Struktur-Artefakt weiterhin intakt (min. 5 Schritte)
- [ ] System hat in mind. 50% der Turns Fragen gestellt
- [ ] Moderator hat in Eskalation keine Artefakte verändert

---

## Phase 4: VALIDIERUNG (automatisiert)

Die Validierungsphase ist komplett deterministisch und braucht keine manuelle Prüfung.
Sie wird durch den programmatischen Test `test_validation_deterministic.py` abgedeckt.

---

## Bewertung: Bestanden / Nicht bestanden

### Harte Kriterien (Test scheitert wenn verletzt)
- Kein Artefakt-Datenverlust bei Eskalation
- Moderator verändert keine Artefakte
- Referenzielle Integrität (nachfolger, struktur_ref)
- Phase-Transitions funktionieren
- Mindestanzahl Schritte/Abschnitte

### Weiche Kriterien (dokumentieren, nicht blockieren)
- Keyword-Abdeckung (≥ 40% pro Konzept)
- Eskalationseffekt (kürzere Antworten)
- Fragezeichen-Ratio (≥ 50%)
- Progress-Monotonie (in_progress → nearing_completion → phase_complete)
- Halluzinationsfreiheit
