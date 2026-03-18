# E2E Human Validation Playbook

Anleitung für manuelle End-to-End-Validierung der Digitalisierungsfabrik.

**Testprozess:** Eingangsrechnungsverarbeitung
**Ziel:** Drei Phasen durchlaufen, Artefakte mit Soll-Zustand vergleichen,
Bericht ausfüllen.

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
- Sind alle 9 Exploration-Slots befüllt (nicht leer)?
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

# TEIL A — EINGABEN

> Jede Nachricht exakt kopieren und einfügen.
> Nach jeder Eingabe: Antwort lesen, Modus-Anzeige prüfen, ggf. im Bericht notieren.

---

## Phase 1: EXPLORATION

### Vorbereitung
- Neues Projekt anlegen im UI
- System zeigt: Phase `exploration`, Modus `moderator`

### Eingaben

**E1-01** — Rückfrage (Moderator soll NICHT starten)
```
Moment, bevor wir anfangen — wie lange dauert das denn so ungefähr? Und muss ich alles auf einmal erzählen oder kann ich das auch in mehreren Sitzungen machen?
```
Erwartung: Modus bleibt `moderator`.

---

**E1-02** — Prozess beschreiben, KEIN explizites Ja (Moderator soll NICHT starten)
```
Ok verstanden. Also der Prozess den ich beschreiben will ist unsere Eingangsrechnungsverarbeitung. Da kommen Rechnungen rein per Post und per E-Mail, die müssen geprüft, freigegeben und bezahlt werden. Wir kriegen so 400-500 Rechnungen im Monat.
```
Erwartung: Modus bleibt `moderator`. System fragt ob es losgehen soll.

---

**E1-03** — Explizite Bestätigung
```
Ja, legen wir los mit der Exploration.
```
Erwartung: Modus wechselt zu `exploration`. System stellt erste Frage.

---

**E1-04** — Rechnungseingang
```
Also die Rechnungen kommen bei uns im Sekretariat an. Papierrechnungen werden eingescannt, die Frau Becker macht das morgens immer als erstes. E-Mail-Rechnungen kommen an rechnungen@firma.de, das ist ein Sammelpostfach. Manchmal schicken Lieferanten die Rechnung aber auch direkt an den Besteller, dann kriegen wir das gar nicht mit.
```

---

**E1-05** — Systeme und Medienbrüche
```
Systeme? Also wir haben DATEV, das ist klar, da wird alles gebucht. Und dann gibt es so ein Freigabetool, das heißt ELO, damit werden die Rechnungen digital freigegeben. Wobei, manche Abteilungsleiter verweigern ELO und machen das immer noch mit einem Stempel auf dem Ausdruck. Der Herr Krause zum Beispiel, der druckt sich alles aus. Dann muss die Frau Becker das wieder einscannen, das ist doch Wahnsinn.

Ach und Outlook natürlich für das Sammelpostfach.
```

---

**E1-06** — Freigabeprozess
```
Der Freigabeprozess ist dreistufig, aber das ist eigentlich übertrieben für die meisten Rechnungen. Erst prüft die Sachbearbeiterin ob die Rechnung zu einer Bestellung passt, dann gibt der Kostenstellenverantwortliche frei, und bei über 5000 Euro muss noch die Geschäftsführung drüber. Das dauert ewig weil die Leute das tagelang liegen lassen. Können wir zum nächsten Thema?
```

---

**E1-07** — Scope + Frustration
```
Scope? Na von Rechnungseingang bis Zahlung halt. Was soll ich denn da noch groß sagen? Hören Sie, ich glaub wir drehen uns im Kreis, der fragt immer das Gleiche nur anders formuliert. Ich will mit jemandem reden der mir sagt ob wir auf dem richtigen Weg sind.
```
**Danach: PANIK-BUTTON drücken.**
Erwartung: Modus wechselt auf `moderator`. Artefakt bleibt erhalten.

---

**E1-08** — Problem beim Moderator beschreiben
```
Ich hab das Gefühl der Explorer stellt mir immer die gleichen Fragen und kommt nicht voran. Ich hab doch schon fast alles erzählt. Und ich weiß auch gar nicht was er noch von mir will.
```
Erwartung: Modus bleibt `moderator`. Moderator analysiert, schickt NICHT sofort zurück.

---

**E1-09** — Wunsch formulieren
```
Ok, also es fehlen noch Umgebung und die Zusammenfassung? Naja, die Zusammenfassung kann er doch selber schreiben aus dem was ich erzählt habe. Und zur Umgebung: Können wir ihm sagen dass er das kürzer und knapper fragen soll? Ich hab nicht ewig Zeit.
```

---

**E1-10** — Rückkehr zum Explorer bestätigen
```
Ja, passt. Geben Sie mich zurück, aber mit der Ansage dass er sich kurz fassen soll.
```
Erwartung: Modus wechselt zu `exploration`.

---

**E1-11** — Umgebung (Post-Eskalation)
```
Also zur Umgebung: Wir sind ein mittelständisches Maschinenbauunternehmen, 200 Mitarbeiter, ein Standort in Nürnberg. Die Buchhaltung hat 4 Leute, eine davon macht fast nur Eingangsrechnungen.
```
Erwartung: Explorer-Antwort kürzer als vor der Eskalation.

---

**E1-12** — Randbedingungen
```
Zahlungsfristen? Wir versuchen immer Skonto zu ziehen, 2% bei Zahlung innerhalb von 10 Tagen. Das schaffen wir aber selten wegen der langen Freigabe. Ist ein echtes Problem, der Chef hat sich letztens aufgeregt dass wir letztes Jahr 30.000 Euro Skonto verschenkt haben. Und Mahnungen kommen natürlich auch, wenn wir zu langsam sind. Peinlich aber passiert.
```

---

**E1-13** — Letzte Ausnahmen
```
Was fehlt noch? Ach so, Ausnahmen: Gutschriften sind auch ein Thema, da dreht sich alles um. Und Teilrechnungen bei großen Projekten, die müssen gegen den Auftrag gegengerechnet werden. Und manchmal kommen Rechnungen ohne Bestellnummer, dann weiß keiner wer die bestellt hat, das ist Detektivarbeit.
```

---

**E1-14** — Ende signalisieren
```
Ja ich denke das war alles. Mir fällt nichts mehr ein.
```
Erwartung: Explorer schreibt `prozesszusammenfassung` SELBST und meldet `phase_complete`.

Falls KEIN phase_complete, nacheinander eingeben:
1. `Ja das war wirklich alles, wir können zur nächsten Phase.`
2. `Bitte schließen Sie die Exploration ab, ich habe alles gesagt.`
3. `Exploration beenden, weiter zur Strukturierung.`

---

**E1-15** — Phasenwechsel bestätigen
```
Ja, weiter zur nächsten Phase.
```
Erwartung: Phase wechselt zu `strukturierung`.

---

### Zusatzfragen Phase 1 — Antworten zum Copy-Paste

Wenn der Agent Fragen stellt die nicht im Skript oben stehen, hier fertige Antworten.

---

**Agent fragt:** *Womit möchten Sie beginnen? / Was können Sie mir über Ihren Prozess erzählen? / Über welchen Prozess möchten Sie sprechen?*
```
Wir wollen unsere Eingangsrechnungsverarbeitung beschreiben. Das ist der Prozess
von Rechnungseingang bis zur Bezahlung, 400 bis 500 Rechnungen pro Monat.
```

---

**Agent fragt:** *Wie lange steht Ihnen Zeit zur Verfügung?*
```
Ich hab eine Stunde, das sollte reichen. Können wir anfangen?
```

---

**Agent fragt (Slot prozessausloeser):** *Was löst diesen Prozess aus? / Wie beginnt der Prozess? / Was ist der Startpunkt?*
```
Der Prozess beginnt wenn eine Rechnung von einem Lieferanten eingeht. Das passiert
auf zwei Wegen: per Post als Papierrechnung, oder per E-Mail an unser Sammelpostfach
rechnungen@firma.de. Manchmal schicken Lieferanten die Rechnung auch direkt an den
Besteller, das ist dann ein Problem weil wir das nicht mitkriegen.
```

---

**Agent fragt (Slot prozessausloeser):** *Wer initiiert den Prozess? / Gibt es einen konkreten Zeitpunkt?*
```
Niemand initiiert das aktiv — es wird durch den Rechnungseingang ausgelöst.
Frau Becker im Sekretariat bemerkt das morgens bei der Postöffnung, oder das
Sammelpostfach zeigt neue E-Mails an.
```

---

**Agent fragt (Slot prozessziel):** *Was ist das Ziel des Prozesses? / Was soll am Ende erreicht sein?*
```
Das Ziel ist dass die Rechnung korrekt geprüft, freigegeben, in DATEV gebucht
und fristgerecht bezahlt wird. Und wenn möglich wollen wir Skonto ziehen —
das sind 2% wenn wir innerhalb von 10 Tagen zahlen. Das schaffen wir leider
meistens nicht wegen der langen Freigabe.
```

---

**Agent fragt (Slot prozessziel):** *Gibt es Nebenziele oder Qualitätsziele?*
```
Ja, Skonto-Ausnutzung ist wichtig — wir verschenken laut Geschäftsführung
etwa 30.000 Euro pro Jahr weil wir zu langsam sind. Und natürlich keine
Mahnungen kriegen, das ist peinlich und kostet extra.
```

---

**Agent fragt (Slot prozessbeschreibung):** *Können Sie mir den Prozess Schritt für Schritt beschreiben?*
```
Rechnung kommt rein, per Post oder E-Mail. Frau Becker scannt Papierrechnungen ein,
E-Mails werden aus dem Sammelpostfach geholt. Dann prüft die Sachbearbeiterin ob es
eine passende Bestellung gibt. Wenn ja, prüft sie ob Betrag und Daten stimmen.
Dann Freigabe durch den Abteilungsleiter, bei über 5000 Euro auch Geschäftsführung.
Dann Buchung in DATEV, dann Zahlung. So grob.
```

---

**Agent fragt (Slot prozessbeschreibung):** *Wie häufig läuft der Prozess? / Wie viele Rechnungen?*
```
Täglich, wir kriegen 400 bis 500 Rechnungen im Monat. Das sind rund 20 pro
Arbeitstag. Der Scan passiert jeden Morgen, die Bearbeitung läuft den ganzen Tag.
```

---

**Agent fragt (Slot prozessbeschreibung):** *Welche Rollen sind beteiligt?*
```
Frau Becker im Sekretariat macht den Scan. Frau Müller in der Buchhaltung macht die
Prüfung und Zuordnung. Der jeweilige Abteilungsleiter gibt frei. Bei über 5000 Euro
noch die Geschäftsführung. 4 Personen in der Buchhaltung, eine davon fast
ausschließlich für Eingangsrechnungen.
```

---

**Agent fragt (Slot prozessbeschreibung):** *Was sind die größten Schwachstellen?*
```
Erstens die lange Freigabe — die Leute lassen das tagelang liegen, deswegen
verpassen wir Skonto. Zweitens der Medienbruch bei Herrn Krause: der druckt sich
alles aus und stempelt das, dann muss Frau Becker den Zettel wieder einscannen.
Drittens Rechnungen ohne Bestellnummer — da weiß keiner wer das bestellt hat.
```

---

**Agent fragt (Slot scope):** *Wo beginnt und wo endet der Prozess? / Was ist nicht im Scope?*
```
Anfang: wenn die Rechnung eingeht. Ende: wenn die Zahlung rausgegangen ist.
Nicht dazu gehört der Bestellprozess, das Lieferantenmanagement und die
Ausgangsrechnungen — das sind andere Prozesse.
```

---

**Agent fragt (Slot beteiligte_systeme):** *Welche IT-Systeme werden genutzt?*
```
DATEV für die Buchung und den Zahlungslauf. ELO für den Freigabe-Workflow.
Microsoft Outlook für das Sammelpostfach. Und der Scanner im Sekretariat
für die Papierrechnungen. Das ist eigentlich alles.
```

---

**Agent fragt (Slot beteiligte_systeme):** *Gibt es Schnittstellen zwischen den Systemen?*
```
Nicht wirklich automatisch. Die Rechnungs-PDFs liegen auf dem W-Laufwerk und
werden manuell in ELO hochgeladen. Zwischen ELO und DATEV gibt es auch keine
automatische Verbindung. Alles Handarbeit.
```

---

**Agent fragt (Slot umgebung):** *In welchem Unternehmenskontext findet das statt?*
```
Mittelständisches Maschinenbauunternehmen, etwa 200 Mitarbeiter, ein Standort
in Nürnberg. Buchhaltung hat 4 Leute, eine davon macht fast nur Eingangs-
rechnungen. Sekretariat mit Frau Becker ist für Post und Scan zuständig.
```

---

**Agent fragt (Slot umgebung):** *Gibt es besondere technische Einschränkungen?*
```
Windows-Umgebung, alles on-premise. Das W-Laufwerk ist ein Netzlaufwerk das
alle sehen können. Keine Cloud-Lösungen. Der Scanner ist ein Einzugsscanner
im Sekretariat.
```

---

**Agent fragt (Slot randbedingungen):** *Welche Regeln oder Fristen müssen eingehalten werden?*
```
Wichtigste Frist: Skonto — 2% Rabatt wenn wir innerhalb von 10 Tagen zahlen.
Zweites: die Freigabeschwelle von 5000 Euro — darüber muss die Geschäftsführung
freigeben. Und die gesetzliche Aufbewahrungspflicht für Belege, 10 Jahre.
```

---

**Agent fragt (Slot randbedingungen):** *Was passiert wenn eine Frist versäumt wird?*
```
Bei Skonto-Frist: wir zahlen den vollen Betrag, kein Rabatt. Bei Zahlungsfristen
allgemein: der Lieferant schickt eine Mahnung, das kostet extra und ist peinlich.
Ist uns letztes Jahr auch passiert.
```

---

**Agent fragt (Slot ausnahmen):** *Welche Ausnahmen gibt es? / Was passiert wenn etwas schiefläuft?*
```
Gutschriften — die gehen andersrum, da kriegen wir Geld zurück, das bucht die
Kollegin in DATEV umgekehrt. Dann Teilrechnungen bei großen Projekten — da kommen
mehrere Rechnungen für eine Bestellung, die müssen zusammengerechnet werden.
Rechnungen ohne Bestellnummer — da weiß keiner wer das bestellt hat, Frau Müller
muss rumtelefonieren. Und manchmal stimmt was nicht auf der Rechnung, dann geht
sie zurück zum Lieferanten, das kann mehrfach hin- und hergehen.
```

---

**Agent fragt (Slot ausnahmen):** *Was ist mit Mahnungen?*
```
Wenn wir zu spät zahlen kommt eine Mahnung vom Lieferanten. Frau Müller muss dann
prüfen ob die Rechnung wirklich noch offen ist und entweder zahlen oder erklären
warum nicht. Kostet Zeit und manchmal auch Mahngebühren.
```

---

**Agent fragt (Zusammenfassung):** *Kann ich jetzt eine Zusammenfassung schreiben? / Darf ich zusammenfassen?*
```
Ja, bitte schreiben Sie die Zusammenfassung selbst aus dem was ich erzählt habe.
Ich möchte nicht nochmal alles wiederholen.
```

---

**Agent fragt:** *Bitte bestätigen Sie ob diese Zusammenfassung korrekt ist: [Zusammenfassung]*
```
Ja das passt soweit. Können wir weitermachen?
```

---

**Agent fragt:** *Ist dieser Slot / diese Information vollständig und korrekt?*
```
Ja das ist korrekt, so haben wir das besprochen.
```

---

## Phase 2: STRUKTURIERUNG

### Eingaben

**E2-01** — Rückfrage
```
Und was machen wir jetzt? Ich hab doch schon alles erzählt. Müssen wir das nochmal durchgehen?
```
Erwartung: Modus bleibt `moderator`.

---

**E2-02** — Bestätigung
```
Na gut, wenn Sie meinen. Dann fangen wir halt an.
```
Erwartung: Modus wechselt zu `structuring`.

---

**E2-03** — Freigabe-Unterschied
```
Ja so ungefähr. Wobei, bei der Freigabe ist es so: Wenn die Rechnung unter 5000 Euro ist dann macht das nur der Abteilungsleiter. Aber wenn es mehr ist, muss der Chef auch noch drüber schauen. Das hat letzte Woche wieder ewig gedauert weil der Chef auf Dienstreise war.
```

---

**E2-04** — Wiederholungen und Gutschriften
```
Ach ja, und manchmal stimmt was nicht auf der Rechnung, dann muss man beim Lieferanten nachfragen und warten bis die eine korrigierte schicken. Das geht manchmal zwei drei Mal hin und her. Und dann gibt es noch Gutschriften, die kommen auch per Post rein aber die werden nicht bezahlt sondern irgendwie verrechnet, das macht die Kollegin in DATEV anders rum.
```

---

**E2-05** — Bestellabgleich
```
Das mit der Bestellnummer ist immer nervig. Wenn eine drauf steht ist es einfach, dann kann die Kollegin das sofort zuordnen. Aber manche Lieferanten schreiben keine drauf, dann muss man rumtelefonieren wer das bestellt hat. Das dauert manchmal Tage. Und bei den großen Maschinenteilen kommen oft drei vier Rechnungen für eine Bestellung, die muss man dann zusammenrechnen ob das stimmt.
```

---

**E2-06** — Ungeduld
```
Moment mal, was meinen Sie mit Verzweigung? Und Kontrollfluss? Reden Sie deutsch mit mir, ich bin Sachbearbeiterin und kein Programmierer. Ich versteh nicht was Sie von mir wollen.
```
**Danach: PANIK-BUTTON drücken.**

---

**E2-07** — Problem beim Moderator
```
Also der redet die ganze Zeit in so einem Computerdeutsch das ich nicht verstehe. Verzweigung, Kontrollfluss, Entscheidungsknoten — ich weiß nicht was das bedeuten soll. Ich will einfach nur meinen Prozess erklären, nicht Informatik studieren.
```
Erwartung: Modus bleibt `moderator`. Artefakt unverändert.

---

**E2-08** — Rückkehr bestätigen
```
Ja, probieren wir es nochmal. Aber sagen Sie ihm er soll normale Wörter benutzen und immer nur eine Sache auf einmal fragen. Nicht so viel auf einmal.
```
Erwartung: Modus wechselt zu `structuring`.

---

**E2-09** — Reihenfolge bestätigen
```
Also von Anfang an: Die Rechnung kommt rein, per Post oder Mail. Frau Becker scannt die ein. Dann schaut die Kollegin in der Buchhaltung ob es eine Bestellung dazu gibt. Wenn ja, prüft sie ob alles stimmt. Dann muss der Abteilungsleiter das freigeben, und wenns über 5000 ist auch noch der Chef. Dann wird es in DATEV gebucht und dann bezahlt. So läuft das normalerweise.
```

---

**E2-10** — Spannungsfeld ELO
```
Was mich wirklich ärgert ist das mit dem ELO. Das ist eigentlich dafür da dass die Freigabe digital läuft. Aber der Herr Krause druckt sich alles aus und stempelt das, und dann muss Frau Becker den Zettel wieder einscannen. Das ist doppelte Arbeit und kostet extra Zeit. Können Sie das irgendwo vermerken dass das ein Problem ist?
```

---

**E2-11** — Fertig
```
Ja ich glaub das passt so. Ich seh da alles was wir besprochen haben. Fällt mir nichts mehr ein was noch fehlt.
```
Falls kein phase_complete:
1. `Ja das war wirklich alles, die Struktur ist vollständig. Bitte abschließen.`
2. `Strukturierung abschließen, weiter zur Spezifikation.`

---

**E2-12** — Phasenwechsel
```
Ja, weiter zur nächsten Phase.
```

---

### Zusatzfragen Phase 2 — Antworten zum Copy-Paste

---

**Agent fragt (Moderator):** *Soll ich die Strukturierung starten? / Sind Sie bereit?*
```
Ja, legen wir los.
```

---

**Agent fragt:** *Können Sie die Schritte des Prozesses in der richtigen Reihenfolge nennen?*
```
Von Anfang an: Rechnung kommt rein per Post oder Mail. Frau Becker scannt die
Papierrechnungen ein. Dann prüft die Kollegin ob eine Bestellung dazu passt.
Wenn ja, prüft sie ob alles stimmt. Dann Freigabe durch den Abteilungsleiter,
bei über 5000 Euro auch Geschäftsführung. Dann DATEV-Buchung. Dann Zahlung.
Das ist der Normalfall.
```

---

**Agent fragt:** *Was passiert beim Rechnungseingang genau?*
```
Papierpost: kommt morgens an, Frau Becker öffnet die Post, erkennt Rechnungen,
legt sie zum Scannen. E-Mail: landen im Sammelpostfach rechnungen@firma.de.
Seit März gibt es eine automatische Weiterleitung in einen Unterordner, Frau
Müller muss nur noch diesen Unterordner prüfen.
```

---

**Agent fragt:** *Was passiert beim Scannen?*
```
Frau Becker legt den ganzen Stapel Papierrechnungen in den Einzugsscanner. Der
zieht die Seiten automatisch durch, erzeugt PDFs. Die werden gespeichert auf dem
W-Laufwerk im Ordner Eingang-Rechnungen. E-Mail-Rechnungen legt Frau Müller auch
als PDF in denselben Ordner.
```

---

**Agent fragt:** *Was passiert wenn keine Bestellnummer auf der Rechnung steht?*
```
Dann beginnt die Detektivarbeit. Frau Müller schaut sich an welcher Lieferant das
ist und was auf der Rechnung steht. Dann ruft sie in den Abteilungen an oder
schreibt E-Mails: "Hat jemand beim Lieferanten XY was bestellt?" Das kann Tage
dauern.
```

---

**Agent fragt:** *Was ist der Unterschied zwischen Abteilungsleiter-Freigabe und GF-Freigabe?*
```
Alle Rechnungen müssen vom Abteilungsleiter freigegeben werden. Nur wenn der
Betrag über 5000 Euro ist, braucht es zusätzlich die Geschäftsführung. Also:
unter 5000 Euro — nur Abteilungsleiter. Über 5000 Euro — erst Abteilungsleiter,
dann Geschäftsführer.
```

---

**Agent fragt:** *Was genau passiert bei der sachlichen Prüfung?*
```
Frau Müller prüft: stimmt der Betrag mit der Bestellung überein, sind die
gelieferten Positionen korrekt, stimmt das Datum, ist die Rechnung an uns
adressiert. Wenn was nicht stimmt, geht sie zurück zum Lieferanten.
```

---

**Agent fragt:** *Was passiert wenn eine Rechnung fehlerhaft ist?*
```
Frau Müller kontaktiert den Lieferanten und erklärt den Fehler. Der schickt
eine korrigierte Rechnung — manchmal mehrfach hin- und her. Die fehlerhafte
Rechnung bleibt so lange offen.
```

---

**Agent fragt:** *Was ist eine Gutschrift und wie wird sie verarbeitet?*
```
Eine Gutschrift ist wenn der Lieferant uns Geld zurückgibt. Die kommt auch
per Post oder E-Mail. In DATEV wird das umgekehrt gebucht — als Einnahme
statt Ausgabe. Die Kollegin macht das anders rum.
```

---

**Agent fragt:** *Wie werden Teilrechnungen behandelt?*
```
Bei großen Projekten kommen manchmal 3 oder 4 Rechnungen für eine einzige
Bestellung. Frau Müller muss dann alle zusammenrechnen und prüfen ob die
Gesamtsumme mit dem Auftrag übereinstimmt.
```

---

**Agent fragt:** *An welchen Stellen gibt es Ja/Nein-Entscheidungen?* (wenn Fachbegriffe vermieden werden)
```
Erstens bei der Bestellnummer: Bestellnummer vorhanden oder nicht?
Zweitens beim Betrag: über 5000 Euro oder nicht? Das sind die zwei
Hauptweggabelungen im normalen Ablauf.
```

---

**Agent fragt:** *Was passiert wenn [Entscheidung] Ja / wenn Nein?*
```
Bei Bestellnummer vorhanden: direkt zur sachlichen Prüfung.
Bei keine Bestellnummer: erst manuelle Zuordnung, dann weiter.

Bei über 5000 Euro: Abteilungsleiter-Freigabe UND dann GF-Freigabe.
Bei unter 5000 Euro: nur Abteilungsleiter-Freigabe.
```

---

**Agent fragt:** *Gibt es Schleifen im Prozess? / Passiert etwas mehrfach?*
```
Ja, bei fehlerhaften Rechnungen: das Hin- und Herschicken mit dem Lieferanten
kann mehrfach passieren. Und beim Bestellabgleich ohne Bestellnummer: man
telefoniert vielleicht mehrmals. Das ist kein schöner Ablauf aber so ist es.
```

---

**Agent fragt:** *Soll ich das als Problem vermerken?* (beim ELO-Medienbruch)
```
Ja bitte. Das Problem: ELO ist das offizielle Freigabesystem, digital.
Aber Herr Krause benutzt es nicht, macht das auf Papier. Das verursacht
Medienbruch, Extra-Scanarbeit und Zeitverlust. Das ist ein bekanntes Problem.
```

---

**Agent fragt:** *Haben Sie noch Schritte die fehlen? / Ist die Struktur vollständig?*
```
Ich glaub das passt so. Ich seh da alles was wir besprochen haben.
```

---

## Phase 3: SPEZIFIKATION

### Eingaben

**E3-01** — Rückfrage
```
Ja und was passiert jetzt noch? Ich hab doch schon alles erzählt über die Rechnungen. Was wollen Sie noch von mir?
```

---

**E3-02** — Bestätigung
```
Ah ok, also nochmal aber jetzt noch genauer was wir konkret tun. Na gut, dann fangen wir halt an.
```

---

**E3-03** — E-Mail-Eingang (FALSCH — wird in E3-06 korrigiert!)
```
Also die E-Mails kommen ins Sammelpostfach rechnungen@firma.de, das ist in Outlook. Frau Müller öffnet das jeden Morgen und geht alle neuen Mails durch. Den Anhang — meistens eine PDF — speichert sie dann in einen Ordner auf dem W-Laufwerk, da gibt es extra einen Ordner der heißt Eingang-Rechnungen oder so ähnlich. Die klickt das halt manuell durch.
```

---

**E3-04** — Scan-Prozess
```
Beim Scannen macht das Frau Becker jeden Morgen als erstes. Sie hat so einen Einzugsscanner — da legt sie den ganzen Stapel Papierrechnungen rein und der zieht die Seiten automatisch durch. Das geht eigentlich recht schnell. Die werden dann auch als PDFs gespeichert und Frau Becker legt die in denselben Ordner auf dem W-Laufwerk. Also da landen am Ende alle Rechnungen zusammen, egal ob Post oder E-Mail.
```

---

**E3-05** — Bestellabgleich (UNVOLLSTÄNDIG — System soll nachfragen)
```
Das mit dem Bestellabgleich... also wenn eine Bestellnummer drauf steht, öffnet Frau Müller in DATEV die Suche und gibt die Nummer ein. Dann zeigt DATEV sofort die passende Bestellung an. Was dann passiert wenn keine Nummer drauf steht, da gibt es noch einiges mehr zu sagen — aber fragen Sie mich da nochmal gezielt was Sie wissen wollen.
```
Erwartung: Antwort enthält Nachfrage (Fragezeichen).

---

**E3-06** — WIDERSPRUCH: E-Mail-Prozess korrigieren
```
Warten Sie mal, ich muss da was korrigieren. Ich hab eben gesagt Frau Müller geht die Mails manuell durch. Das stimmt so nicht mehr. Seit März haben wir eine Weiterleitung in Outlook eingerichtet — alle Mails an rechnungen@firma.de gehen automatisch in einen Unterordner. Frau Müller muss nur noch diesen Unterordner aufmachen, nicht das ganze Postfach durchsuchen. Das hat unser IT-Mann eingerichtet.
```
Erwartung: Artefakt wird aktualisiert. "Weiterleitung"/"automatisch"/"Unterordner" taucht auf.

---

**E3-07** — Frust über EMMA-Jargon
```
Ich kapier nicht was Sie von mir wollen. Sie zeigen mir da so Sachen wie FIND und READ_FORM und TYPE — was soll das sein? Ich bin keine IT-Fachkraft. Ich soll Ihnen sagen wie die Arbeit läuft, nicht wie ein Computerprogramm aussieht. Das versteht doch kein Mensch.
```
**Danach: PANIK-BUTTON drücken.**

---

**E3-08** — Eskalation beim Moderator
```
Also der stellt mir Fragen die ich nicht verstehen kann. Was ist zum Beispiel ein 'Parameter'? Oder er fragt mich in welcher Reihenfolge das System etwas tun soll — das weiß ich, aber dann schreibt er das mit irgendwelchen englischen Abkürzungen auf die ich nicht kenne. Das macht mir Angst ehrlich gesagt.
```

---

**E3-09** — Rückkehr
```
Ja wenn er das auf Deutsch erklärt was er meint dann gut. Aber bitte kein Computerfachchinesisch mehr. Einfache Wörter, wie wenn Sie einem normalen Menschen erklären was passiert.
```

---

**E3-10** — ELO-Freigabe
```
Also die Freigabe in ELO läuft so: Das System schickt dem Abteilungsleiter eine E-Mail mit einem Link drin. Der klickt auf den Link, dann öffnet sich ELO im Browser und der sieht die Rechnung und einen Knopf zum Freigeben. Wenn er draufklickt, ist es erledigt. Das ist eigentlich ganz einfach. Aber der Herr Krause macht das nie über den Computer, der druckt immer alles aus.
```

---

**E3-11** — DATEV-Buchung
```
In DATEV tippt die Kollegin dann die Daten ein: Rechnungsnummer, Datum, Betrag, Lieferant und die Kostenstelle. Das geht über ein Eingabeformular mit verschiedenen Feldern. Manchmal muss sie auch noch die Mehrwertsteuer extra angeben je nach Lieferant. Das ist halt Tipparbeit.
```

---

**E3-12** — Zahlungslauf
```
Das mit der Zahlung ist dann auch in DATEV. Es gibt dort einen Zahlungslauf — da werden alle freigegebenen Rechnungen zusammengestellt und als Sammelüberweisung rausgeschickt. Das macht die Buchhalterin einmal die Woche, montags meistens. Damit wären wir dann glaube ich fertig.
```

---

**E3-13** — Fertig
```
Ja, mir fällt wirklich nichts mehr ein. Das war alles was wir so machen bei den Rechnungen. Können wir jetzt aufhören?
```
Falls kein phase_complete:
1. `Ja das war wirklich alles, bitte Spezifikation abschließen.`
2. `Spezifikation abschließen, weiter zur Validierung.`

---

**E3-14** — Phasenwechsel
```
Ja gut, dann weiter zur Prüfung. Was auch immer das bedeutet.
```

---

### Zusatzfragen Phase 3 — Antworten zum Copy-Paste

---

**Agent fragt (Moderator):** *Soll ich die Spezifikation starten? / Wissen Sie was diese Phase bedeutet?*
```
Ah ok, also nochmal aber jetzt noch genauer was wir konkret tun.
Na gut, dann fangen wir halt an.
```

---

**Agent fragt (E-Mail-Eingang):** *Wie genau wird der E-Mail-Eingang abgearbeitet?*
```
Frau Müller öffnet Outlook und geht in den Unterordner — da landen seit März alle
E-Mails automatisch drin wegen der Weiterleitung. Sie öffnet jede Mail, speichert
den PDF-Anhang auf das W-Laufwerk in den Ordner Eingang-Rechnungen. Das macht sie
manuell für jede Mail.
```

---

**Agent fragt:** *Wie erkennt Frau Müller welche E-Mails Rechnungen sind?*
```
Die kommen alle in den speziellen Unterordner für Rechnungen, da ist also schon
klar was das ist. Den Anhang erkennt man daran dass es ein PDF ist.
```

---

**Agent fragt:** *Wo genau auf dem W-Laufwerk wird gespeichert?*
```
W:\Eingang-Rechnungen oder so ähnlich, ich weiß den genauen Pfad nicht auswendig.
Es gibt einen definierten Ordner dafür, den kennt Frau Müller.
```

---

**Agent fragt (Scan):** *Wie genau funktioniert der Scanvorgang?*
```
Frau Becker legt morgens den Stapel Papierrechnungen in den Einzugsscanner. Der
scannt alles durch und erzeugt für jede Rechnung eine PDF-Datei. Die landen direkt
auf dem W-Laufwerk in Eingang-Rechnungen. Frau Becker benennt die Dateien dann noch,
nach Lieferant und Datum oder so.
```

---

**Agent fragt:** *Was passiert mit den Originalen nach dem Scannen?*
```
Die werden aufbewahrt, Aufbewahrungspflicht 10 Jahre. Die kommen in Ablageordner
nach Datum sortiert. Das Original muss bleiben, die Digitalisierung ist für die
Bearbeitung.
```

---

**Agent fragt (Bestellabgleich):** *Was macht Frau Müller konkret in DATEV?*
```
Sie öffnet DATEV auf ihrem Computer, geht in den Bereich Eingangsrechnungen, dort
gibt es eine Suchfunktion. Sie gibt die Bestellnummer aus der Rechnung ein und DATEV
zeigt die passende Bestellung an. Sie vergleicht dann Betrag, Positionen und Lieferant
visuell — kein automatischer Abgleich.
```

---

**Agent fragt:** *Was macht sie wenn keine Bestellnummer da ist?*
```
Sie schaut auf den Lieferantennamen und die Beschreibung. Dann sucht sie in der
E-Mail-Korrespondenz oder fragt in den Abteilungen nach. Meistens telefoniert sie
oder schreibt eine kurze E-Mail: "Hat jemand beim Lieferanten XY was bestellt?"
Das kann Tage dauern.
```

---

**Agent fragt:** *Wie lange wartet Frau Müller auf Rückmeldungen?*
```
Meistens ein bis zwei Tage. Wenn niemand antwortet fragt sie nochmal nach.
Nach einer Woche wird der Chef informiert. Einen festen Eskalationsprozess
gibt es da nicht wirklich.
```

---

**Agent fragt (ELO-Freigabe):** *Wie genau startet der Freigabeprozess in ELO?*
```
Frau Müller lädt die geprüfte Rechnung in ELO hoch. ELO schickt dann automatisch
eine E-Mail an den zuständigen Abteilungsleiter mit einem direkten Link zur Rechnung.
```

---

**Agent fragt:** *Was macht der Abteilungsleiter in ELO?*
```
Er klickt auf den Link, ELO öffnet sich im Browser, er sieht die Rechnung und
einen Freigabe-Button. Er klickt drauf, fertig. ELO benachrichtigt dann Frau Müller.
```

---

**Agent fragt:** *Was passiert wenn der Abteilungsleiter ablehnt?*
```
ELO schickt eine Benachrichtigung an Frau Müller mit dem Ablehnungsgrund. Dann
klärt sie intern was nicht stimmt. Es gibt keinen automatischen Prozess dafür.
```

---

**Agent fragt:** *Wie lange wartet das System auf Freigabe? / Gibt es eine Frist?*
```
Keine automatische Erinnerung in ELO. Frau Müller schaut nach ein bis zwei Tagen
ob eine Freigabe noch aussteht und erinnert dann manuell per E-Mail oder Telefon.
```

---

**Agent fragt (GF-Freigabe):** *Wie läuft die GF-Freigabe ab?*
```
Genauso wie beim Abteilungsleiter: ELO schickt eine E-Mail mit Link. Der
Geschäftsführer klickt drauf und gibt frei. Das Problem ist wenn der auf
Dienstreise ist — dann hängt alles. Eine Vertretungsregelung gibt es nicht.
```

---

**Agent fragt (DATEV-Buchung):** *Was genau gibt Frau Müller in DATEV ein?*
```
Sie öffnet das Buchungsformular für Eingangsrechnungen. Felder: Rechnungsnummer,
Rechnungsdatum, Betrag, Lieferant (aus dem Lieferantenstamm), Kostenstelle, manchmal
Mehrwertsteuer-Schlüssel. Das füllt sie manuell von der Rechnung ab und speichert.
```

---

**Agent fragt:** *Wie wählt sie den Lieferanten in DATEV?*
```
Es gibt eine Suchfunktion, sie gibt den Lieferantennamen ein, DATEV zeigt die
Treffer. Bekannte Lieferanten sind schon im System, neue müssen erst angelegt
werden — Name, Adresse, Bankdaten, Steuernummer.
```

---

**Agent fragt:** *Wie wird die Mehrwertsteuer behandelt?*
```
Für normale deutsche Lieferanten ist der Standard-MwSt-Schlüssel vorgegeben.
Bei ausländischen Lieferanten gibt es andere Schlüssel. Frau Müller wählt das
manuell aus — sie kennt die Lieferanten und weiß welcher Schlüssel passt.
```

---

**Agent fragt (Zahlungslauf):** *Wie funktioniert der Zahlungslauf in DATEV?*
```
In DATEV gibt es einen Menüpunkt Zahlungslauf. Da werden alle offenen, freige-
gebenen Rechnungen angezeigt. Die Buchhalterin wählt alle aus die bezahlt werden
sollen, dann wird eine Datei erzeugt die ans Online-Banking geht. Der Chef
bestätigt das im Online-Banking, dann gehen die Überweisungen raus.
```

---

**Agent fragt:** *Wer hat die Berechtigung den Zahlungslauf zu starten?*
```
Die Chefbuchhalterin startet den Zahlungslauf in DATEV. Die finale Freigabe
im Online-Banking macht der Geschäftsführer oder eine zeichnungsberechtigte Person.
```

---

**Agent fragt:** *Wie wird die Rechnung nach der Buchung archiviert?*
```
Das Papier-Original kommt in den Ablageordner. Die digitale PDF ist auf dem
W-Laufwerk. In ELO bleibt die Rechnung auch gespeichert. DATEV hat die Buchung.
Also an drei Orten, aber das ist so gewachsen.
```

---

**Agent fragt:** *Gibt es noch Schritte die wir nicht spezifiziert haben?*
```
Ich glaub das war alles was wir so machen. Mir fällt nichts mehr ein.
```

---

### Eskalation — Universelle Antworten (alle Phasen)

---

**Agent benutzt Fachbegriffe** (Verzweigung, Kontrollfluss, Entscheidungsknoten, Iteration, Parameter...):
```
Reden Sie bitte Deutsch mit mir, ich bin Sachbearbeiterin und kein Programmierer.
Was meinen Sie konkret in einfachen Worten?
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
Der Explorer / Strukturierungsmodus redet die ganze Zeit in Fachbegriffen die ich
nicht verstehe. Ich will einfach meinen Prozess erklären, kein Informatik-Studium
machen.
```

---

**Agent (Moderator) fragt ob zurück zur vorherigen Phase:**
```
Ja, aber sagen Sie ihm er soll normale Wörter benutzen und immer nur eine Sache
auf einmal fragen. Nicht so viel auf einmal und kein Computerfachchinesisch.
```

---

**Agent (Moderator) fasst zusammen was noch fehlt:**
```
Ok, dann sagen Sie ihm er soll das holen was fehlt, aber kurz und bündig bitte.
Ich hab nicht ewig Zeit.
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
Können wir das erstmal offen lassen oder mit einem Platzhalter weiterarbeiten?
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

## Ziel-Artefakt 1: Exploration (9 Slots)

### prozessausloeser
> Eingang einer Lieferantenrechnung per Post (Papierrechnung) oder per
> E-Mail an das Sammelpostfach rechnungen@firma.de. In Einzelfällen
> auch direkte Zusendung an den Besteller (wird nicht zentral erfasst).

**Muss enthalten:** Rechnung, Post, E-Mail, Sammelpostfach
**Status:** vollstaendig

### prozessziel
> Fristgerechte, sachlich und rechnerisch korrekte Prüfung, Freigabe
> und Bezahlung von Eingangsrechnungen. Buchung in DATEV. Angestrebtes
> Nebenziel: Skonto-Ausnutzung (2% bei Zahlung innerhalb von 10 Tagen).

**Muss enthalten:** Zahlung, Prüfung, Freigabe, DATEV, Skonto
**Status:** vollstaendig

### prozessbeschreibung
> 1. Rechnungseingang im Sekretariat (Frau Becker scannt morgens).
>    E-Mail-Rechnungen über Sammelpostfach. Problem: direkte Zusendung.
> 2. Sachbearbeiterin prüft Bestellabgleich. Ohne Bestellnummer: manuelle
>    Zuordnung ("Detektivarbeit").
> 3. Freigabe (dreistufig bei > 5000 EUR): Sachbearbeiterin → Kostenstellen-
>    verantwortlicher → Geschäftsführung. Digital über ELO, aber Herr Krause
>    druckt aus + stempelt → Frau Becker muss erneut scannen (Medienbruch).
> 4. Buchung in DATEV.
> 5. Zahlung. Skonto (2%/10 Tage) wird meist verpasst (~30.000 EUR/Jahr).
>    400-500 Rechnungen/Monat.

**Muss enthalten:** Freigabe, dreistufig, 5000/5.000, DATEV, ELO, Medienbruch, Skonto
**Status:** vollstaendig

### scope
> Beginn: Eingang der Rechnung (Post oder E-Mail).
> Ende: Zahlung an den Lieferanten.
> Nicht im Scope: Bestellprozess, Lieferantenmanagement, Ausgangsrechnungen.

**Muss enthalten:** Eingang, Zahlung
**Status:** vollstaendig

### beteiligte_systeme
> DATEV (Buchung), ELO (Freigabe-Workflow), Microsoft Outlook (Sammelpostfach),
> Scanner (Sekretariat).

**Muss enthalten:** DATEV, ELO, Outlook
**Status:** vollstaendig

### umgebung
> Mittelständisches Maschinenbauunternehmen, ~200 Mitarbeiter, Nürnberg.
> Buchhaltung: 4 Personen, eine fast ausschließlich Eingangsrechnungen.
> Sekretariat: Frau Becker (Scannen, Posteingang).

**Muss enthalten:** 200, Nürnberg, Buchhaltung, 4
**Status:** vollstaendig

### randbedingungen
> Skonto-Frist: 2% bei 10 Tagen (wird meist verpasst, ~30.000 EUR/Jahr).
> Freigabeschwelle: 5.000 EUR für GF-Freigabe.
> Gesetzliche Aufbewahrungspflicht.

**Muss enthalten:** Skonto, 5000/5.000, 10 Tage
**Status:** teilweise bis vollstaendig

### ausnahmen
> Gutschriften (umgekehrter Buchungsprozess), Teilrechnungen (Großprojekte),
> Rechnungen ohne Bestellnummer (manuelle Recherche),
> ELO-Verweigerung (Stempel-Freigabe), Direktzustellung an Besteller,
> Mahnungen.

**Muss enthalten:** Gutschrift, Teilrechnung, Bestellnummer
**Status:** vollstaendig

### prozesszusammenfassung
> Vom Explorer SELBST erstellt (Vereinbarung aus E1-09). Soll sinngemäß
> zusammenfassen: Rechnungseingang → dreistufige Freigabe → Buchung/Zahlung,
> ~400-500/Monat, Hauptprobleme: lange Freigabe, Skonto-Verlust, Medienbruch.

**Muss enthalten:** Rechnung, Freigabe (mindestens)
**Status:** vollstaendig

### Dinge die NICHT im Artefakt stehen dürfen (Halluzinationen)
SAP, OCR, Blockchain, Machine Learning, KI-gestützt, API, Vier-Augen-Prinzip

---

## Ziel-Artefakt 2: Struktur (min. 5 Schritte, ideal ~9-11)

### Erwartete Schritte (Konzepte, nicht exakte IDs)

| # | Konzept | Typ | Pflichtfelder |
|---|---|---|---|
| 1 | Rechnungseingang | aktion | beschreibung mit Post/E-Mail. Kein Vorgänger (Startschritt). |
| 2 | Erfassung/Scannen | aktion | beschreibung mit Scan/digital. |
| 3 | Bestellabgleich | entscheidung | bedingung: "Hat die Rechnung eine Bestellnummer?" 2+ nachfolger. |
| 4 | (Manuelle Zuordnung) | aktion | Für den Fall ohne Bestellnummer. |
| 5 | Sachliche Prüfung | aktion | beschreibung mit Prüfung. |
| 6 | Betragsprüfung GF | entscheidung | bedingung: "> 5.000 EUR?" 2+ nachfolger. |
| 7 | Abteilungsleiter-Freigabe | aktion | beschreibung mit ELO/Freigabe. **spannungsfeld** mit ELO/Medienbruch/Stempel. |
| 8 | GF-Freigabe | aktion | Für Rechnungen > 5.000 EUR. |
| 9 | Buchung DATEV | aktion | beschreibung mit DATEV. |
| 10 | Zahlung | aktion | beschreibung mit Zahlung/Skonto. Kein Nachfolger (Endschritt). |
| 11 | Gutschrift-Ausnahme | ausnahme | beschreibung mit Gutschrift/Gegenbuchung. |

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
- Min. 1 Schritt mit gefülltem `spannungsfeld` (ELO/Medienbruch-Bezug)
- Kein Schritt mit `completeness_status == leer`
- Alle Schritte haben nicht-leere `beschreibung`

### Explorations-Artefakt muss weiterhin intakt sein
- Alle 9 Slots vorhanden und gefüllt

### Dinge die NICHT im Artefakt stehen dürfen
BPMN, UML, Swimlane, Flowchart

---

## Ziel-Artefakt 3: Algorithmus (min. 6 Abschnitte)

### Erwartete Abschnitte

| Konzept | struktur_ref | Erwartete EMMA-Typen | Keywords |
|---|---|---|---|
| E-Mail-Eingang | s01_eingang (o.ä.) | READ, FILE_OPERATION, FIND | Outlook, E-Mail, **Unterordner/Weiterleitung/automatisch** (Korrektur!) |
| Erfassung/Scan | s02_erfassung (o.ä.) | FILE_OPERATION | Scanner, PDF, W-Laufwerk |
| Bestellabgleich | s03_bestellabgleich (o.ä.) | FIND, DECISION, READ | Bestellnummer, DATEV |
| Freigabe ELO | s06_abt_freigabe (o.ä.) | SEND_MAIL, FIND_AND_CLICK, WAIT | ELO, Freigabe, Link |
| Buchung DATEV | s08_buchung (o.ä.) | TYPE, READ_FORM, FIND | DATEV, Formular, Betrag |
| Zahlung | s09_zahlung (o.ä.) | TYPE, FIND_AND_CLICK | Zahlung, DATEV, Zahlungslauf |

### Strukturelle Anforderungen
- Mindestens 6 Abschnitte
- Alle Abschnitte haben min. 1 EMMA-Aktion
- Alle `struktur_ref` zeigen auf existierende `schritt_id`s
- EMMA-Typen DECISION und FILE_OPERATION müssen vorkommen
- `prozesszusammenfassung` nicht leer

### Widerspruch-Korrektur (E3-06)
Der Abschnitt für Rechnungseingang (s01_eingang o.ä.) MUSS die korrigierte
Information enthalten: "Weiterleitung", "automatisch" oder "Unterordner".
Er darf NICHT ausschließlich "manuell durchklicken" enthalten.

### Explorations- und Struktur-Artefakt müssen weiterhin intakt sein
- Exploration: 9 Slots, alle gefüllt
- Struktur: min. 5 Schritte

### Dinge die NICHT im Artefakt stehen dürfen
PowerShell, SharePoint, REST API, SQL, XML, VBA, Python, JavaScript

---
---

# TEIL C — TESTBERICHT (Vorlage)

Kopiere diese Vorlage und fülle sie während des Durchlaufs aus.

---

```
# E2E Testbericht — Eingangsrechnungsverarbeitung

Datum: _______________
Tester: _______________
Projekt-ID: _______________

## Phase 1: Exploration

### Moderator-Verhalten

| Schritt | Eingabe | Erwartung | Ergebnis | OK? |
|---------|---------|-----------|----------|-----|
| E1-01 | Rückfrage | Modus bleibt moderator | | |
| E1-02 | Prozess ohne Ja | Modus bleibt moderator | | |
| E1-03 | Explizites Ja | Wechsel zu exploration | | |

### Eskalation

| Prüfpunkt | Ergebnis | OK? |
|-----------|----------|-----|
| Panik-Button → Moderator aktiv? | | |
| Artefakt nach Eskalation intakt? | | |
| Moderator analysiert (nicht sofort zurück)? | | |
| Moderator hat Artefakt NICHT verändert? | | |
| Rückkehr zu exploration nach E1-10? | | |
| Explorer-Antwort kürzer nach Eskalation? | | |

### Artefakt-Vergleich (nach Phase 1)

| Slot | Soll-Keywords | Ist vorhanden? | Inhalt sinngemäß korrekt? |
|------|---------------|----------------|---------------------------|
| prozessausloeser | Rechnung, Post, E-Mail | | |
| prozessziel | Zahlung, DATEV, Skonto | | |
| prozessbeschreibung | Freigabe, 5000, DATEV, ELO | | |
| scope | Eingang, Zahlung | | |
| beteiligte_systeme | DATEV, ELO, Outlook | | |
| umgebung | 200, Nürnberg, Buchhaltung | | |
| randbedingungen | Skonto, 5000, 10 Tage | | |
| ausnahmen | Gutschrift, Bestellnummer | | |
| prozesszusammenfassung | Rechnung, Freigabe | | |

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
| Rückkehr zu structuring nach E2-08? | | |

### Artefakt-Vergleich (nach Phase 2)

Anzahl Schritte: _______ (Soll: >= 5)

| Konzept | Typ | Vorhanden? | Beschreibung korrekt? |
|---------|-----|------------|----------------------|
| Rechnungseingang | aktion | | |
| Erfassung/Scan | aktion | | |
| Bestellabgleich | entscheidung | | |
| Sachliche Prüfung | aktion | | |
| Betragsprüfung | entscheidung | | |
| Freigabe | aktion | | |
| Buchung DATEV | aktion | | |
| Zahlung | aktion | | |
| Gutschrift | ausnahme | | |

Entscheidungen haben Bedingung + 2 Nachfolger? ______
Nachfolger-Refs alle gültig? ______
Reihenfolge aufsteigend? ______
Start-/Endschritt vorhanden? ______
Spannungsfeld ELO/Medienbruch vorhanden? ______
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
| Korrektur-Keywords vorhanden? (Weiterleitung/automatisch/Unterordner) | | |

### Artefakt-Vergleich (nach Phase 3)

Anzahl Abschnitte: _______ (Soll: >= 6)

| Konzept | struktur_ref gültig? | Hat Aktionen? | EMMA-Typen |
|---------|---------------------|---------------|------------|
| E-Mail-Eingang | | | |
| Erfassung/Scan | | | |
| Bestellabgleich | | | |
| Freigabe ELO | | | |
| Buchung DATEV | | | |
| Zahlung | | | |

EMMA-Typ DECISION vorhanden? ______
EMMA-Typ FILE_OPERATION vorhanden? ______
Halluzinationen gefunden? ______
Exploration-Artefakt weiterhin intakt? ______
Struktur-Artefakt weiterhin intakt? ______

---

## Post-hoc-Validator Ergebnis

```
(Hier die Ausgabe von `python scripts/validate_e2e_artifacts.py` einfügen)
```

## Gesamtergebnis

| Kriterium | Bestanden? |
|-----------|-----------|
| Phase 1: Alle 9 Slots sinngemäß korrekt | |
| Phase 2: Struktur vollständig + korrekte Typen | |
| Phase 3: Algorithmus mit EMMA-Aktionen | |
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
