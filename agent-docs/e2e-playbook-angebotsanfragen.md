# E2E Playbook: Angebotsanfragen beantworten

Wissensreferenz für den E2E-Test der Explorationsphase.

**Testprozess:** Angebotsanfragen beantworten
**Persona:** Herr Krause, Sachbearbeiter Vertriebsinnendienst, Bergmann Industrietechnik GmbH
**Ziel:** Exploration durchlaufen, Artefakt-Qualität bewerten.

---

# TEIL A — PERSONA & PROZESSWISSEN

## Persona-Briefing: Herr Krause

**Rolle:** Sachbearbeiter Vertriebsinnendienst bei der **Bergmann Industrietechnik GmbH** in Karlsruhe.
**Unternehmen:** Großhandel für Industriekomponenten (Ventile, Pumpen, Dichtungen), 120 Mitarbeiter.
**Team:** 4 Personen im Innendienst, 6 Außendienstler.

**Charakter:**
- Sachlich, knapp, effizient — gibt nur das Nötigste preis
- Muss bei Details gezielt gefragt werden, erzählt nicht von sich aus
- Kennt seinen Prozess blind, macht ihn seit 8 Jahren
- Leicht genervt von Wiederholungsfragen
- Kein IT-Wissen, aber routinierter System-Anwender

**Typische Formulierungen:**
- "Das geht so: ..."
- "Ja, genau."
- "Nee, das mach ich anders."
- "Das ist immer gleich."
- "Moment, da muss ich ausholen..."

---

## Prozesswissen: Angebotsanfragen beantworten

> **Hinweis:** Vollständige Ground Truth auf RPA-Niveau.
> Herr Krause kennt alle Details, gibt sie aber erst auf gezielte Nachfrage preis.

### Überblick

Herr Krause beantwortet Angebotsanfragen von Kunden. Die Anfragen kommen per E-Mail (Outlook). Er schlägt Produkte und Preise im Warenwirtschaftssystem (WAWI) nach, erstellt das Angebot im CRM-System (ProSales), exportiert es als PDF und schickt es per E-Mail zurück. ~15 Angebote pro Tag, ca. 5-8 Minuten pro Angebot.

**Das ist der Prozess den EMMA automatisieren soll: Herr Krauses Computerarbeit — Kundenanfragen lesen, Produkte/Preise nachschlagen, Angebot im CRM erstellen und als PDF versenden.**

### Systeme

| System | Zugang | Funktion |
|--------|--------|----------|
| **Outlook** | Desktop-Client | E-Mail-Eingang, Anfragen empfangen, Angebote versenden |
| **ProSales** | Web-Anwendung (Browser, Chrome) | CRM-System: Kundenakte, Angebotserstellung |
| **WAWI** | Desktop-Programm | Warenwirtschaft: Artikelstamm, Preise, Verfügbarkeit |

### Der Prozess — Schritt für Schritt

#### Trigger (Start)

Herr Krause öffnet morgens Outlook. Im Posteingang liegen Anfragen von Kunden oder Interessenten — meistens mit Betreff wie "Anfrage", "Angebot erbeten", "Preisanfrage" o.ä. Oft ist eine Stückliste oder Bedarfsliste als Excel- oder PDF-Anhang dabei, manchmal steht alles im E-Mail-Text.

#### Schleife: Pro Anfrage (~15x am Tag)

**Schritt 1: Anfrage lesen und Bedarf erfassen**
1. E-Mail in Outlook öffnen
2. Kundennamen und Ansprechpartner notieren (steht in der E-Mail-Signatur)
3. Angefragte Produkte und Mengen ablesen — aus dem E-Mail-Text oder Anhang (Excel/PDF öffnen)
4. Ggf. Lieferwunschtermin oder Sonderwünsche notieren

**Schritt 2: Kunden in ProSales nachschlagen**
1. Herr Krause wechselt zu ProSales (Chrome, ist immer offen als Tab)
2. Suchfeld "Kunde": Firmenname oder Kundennummer eingeben
3. Wenn Kunde gefunden: Kundenakte öffnen → Adresse, Konditionen, Rabattstufe ablesen
4. Wenn Kunde NICHT gefunden: Button "Neuer Kunde" → Mini-Formular: Firmenname, Ansprechpartner, E-Mail, Telefon, Adresse. Kommt ca. 3x pro Woche vor.

**Schritt 3: Produkte und Preise in WAWI nachschlagen**
1. Wechsel zu WAWI (Desktop-Programm, immer offen in der Taskleiste)
2. Pro angefragtem Produkt: Artikelnummer im Suchfeld eingeben oder über Produktgruppe navigieren
3. Artikeldetail-Ansicht: Listenpreis, Staffelpreise, aktuelle Verfügbarkeit (Lagerbestand)
4. Wenn Artikel nicht verfügbar: voraussichtliches Lieferdatum ablesen (steht im Feld "Nächster Wareneingang")
5. Preise und Verfügbarkeit merken (Herr Krause hat einen Notizblock neben sich, tippt nichts zwischen)

**Schritt 4: Angebot in ProSales erstellen**
1. Zurück zu ProSales, in der Kundenakte: Button "Neues Angebot"
2. Angebotsmaske öffnet sich mit vorausgefüllter Kundenadresse
3. Pro Produkt eine Position hinzufügen:
   - Artikelnummer eingeben → ProSales zieht Bezeichnung und Listenpreis aus WAWI-Schnittstelle
   - Menge eintragen
   - Preis ggf. anpassen (siehe Rabattlogik unten)
   - Lieferzeit eintragen (Standard: "2-3 Werktage", bei Nicht-Verfügbarkeit: Datum aus WAWI)
4. Kopffelder: Angebotsdatum (heute), Gültigkeitsdauer (Standard: 30 Tage), Zahlungsbedingung (aus Kundenakte, Standard: "30 Tage netto")
5. Freitextfeld "Bemerkungen": Sonderwünsche oder Hinweise eintragen (z.B. "Teillieferung möglich")
6. Klick auf "Angebot berechnen" → ProSales berechnet Positionssummen, Gesamtnetto, MwSt., Brutto

**Schritt 5: Angebot prüfen und als PDF exportieren**
1. Herr Krause prüft: Stimmen Positionen, Mengen, Preise, Gesamtbetrag?
2. Klick auf "PDF erzeugen" → ProSales generiert Angebots-PDF mit Firmenlogo und AGB
3. PDF wird automatisch in der Kundenakte unter "Dokumente" abgelegt
4. Herr Krause klickt "PDF herunterladen" → speichert lokal unter `Downloads`

**Schritt 6: Angebot per E-Mail versenden**
1. Zurück zu Outlook: Neue E-Mail
2. Empfänger: E-Mail-Adresse des Ansprechpartners (aus der ursprünglichen Anfrage-Mail → "Antworten")
3. Betreff: "Ihr Angebot AG-2026-XXXX" (Angebotsnummer aus ProSales)
4. Standardtext aus Textbaustein einfügen (Herr Krause hat 3 Textbausteine in Outlook: Neukunde, Bestandskunde, Eilanfrage)
5. PDF-Angebot als Anhang hinzufügen
6. Senden

**Schritt 7: Nachbereitung**
1. Zurück zu ProSales: Angebotsstatus auf "Versendet" setzen
2. Wiedervorlage eintragen: Datum = heute + 7 Tage, Aktion = "Nachfassen"
3. Zurück zu Outlook: Ursprüngliche Anfrage-Mail in Ordner "Erledigt" verschieben

#### Ende

Alle Anfragen bearbeitet wenn Outlook-Posteingang keine Anfrage-Mails mehr enthält.

### Entscheidungen

| Stelle | Bedingung | Dann | Sonst |
|--------|-----------|------|-------|
| Kunde in ProSales | Kunde gefunden? | Akte öffnen, weiter | "Neuer Kunde" anlegen |
| Artikelverfügbarkeit | Auf Lager? | Lieferzeit "2-3 Werktage" | Lieferdatum aus "Nächster Wareneingang" |
| Rabatt (Menge) | Bestellwert > 5.000€? | 5% Rabatt auf Gesamtangebot | Kein Mengenrabatt |
| Rabatt (Menge) | Bestellwert > 10.000€? | 8% Rabatt statt 5% | — |
| Rabatt (Key Account) | Kunde hat Sonderkonditionen in ProSales? | Individuellen Rabatt aus Kundenakte anwenden | Standard-Rabattlogik |
| Textbaustein | Neukunde? (Kunde nicht in ProSales) | Textbaustein "Neukunde" (formeller, mit Firmendarstellung) | Textbaustein "Bestandskunde" (kürzer, persönlicher) |
| Textbaustein | Eilanfrage? (Kunde schreibt "dringend"/"eilig"/"asap" o.ä. in der Mail) | Textbaustein "Eilanfrage" (mit Hinweis auf Express-Lieferung) | — |
| Angebotsnummer | Wann entsteht sie? | Beim Klick auf "Neues Angebot" in ProSales wird die Nummer automatisch vergeben (AG-2026-laufende Nr.) | — |

### Ausnahmen

**Anfrage ohne konkrete Artikelnummern (~3x pro Woche):**
- Kunde beschreibt Bedarf nur umgangssprachlich ("brauche Ventile für 2-Zoll-Rohr, Edelstahl")
- Herr Krause sucht in WAWI über Produktgruppe + Filter, wählt passende Artikel aus
- Dauert deutlich länger (~15min statt 5-8min)

**Anfrage mit Sonderkonditionen (~2x pro Woche):**
- Großkunde will Sonderpreis, der über den Standard-Rabatt hinausgeht
- Herr Krause kann bis 12% selbst entscheiden
- Darüber: Weiterleitung per E-Mail an Vertriebsleitung (Herr Berger) zur Freigabe
- Herr Krause legt das Angebot in ProSales als "Entwurf" an und wartet auf Rückmeldung

**Anfrage auf Englisch (~1x pro Woche):**
- Kommt von internationalen Kunden
- Herr Krause wechselt in ProSales den Textbaustein auf "English" und erstellt das Angebot auf Englisch
- Antwort-Mail auch auf Englisch (anderer Textbaustein)

### Variablen & Daten

| Variable | Typ | Quelle | Ziel |
|----------|-----|--------|------|
| Kundenname/Firma | Text | E-Mail | ProSales Kundensuche |
| Ansprechpartner | Text | E-Mail-Signatur | ProSales Kundenakte |
| E-Mail-Adresse | Text | E-Mail | Antwort-Mail |
| Artikelnummer(n) | Text | E-Mail / Anhang | WAWI Suche, ProSales Positionen |
| Menge(n) | Zahl | E-Mail / Anhang | ProSales Positionen |
| Listenpreis | Dezimal (€) | WAWI | ProSales Positionspreis |
| Rabattstufe | % | ProSales Kundenakte / Bestellwert | ProSales Positionspreis |
| Verfügbarkeit | Ja/Nein | WAWI Lagerbestand | Lieferzeit im Angebot |
| Lieferdatum | Datum | WAWI "Nächster Wareneingang" | ProSales Lieferzeit |
| Angebotsnummer | Text (auto) | ProSales | E-Mail-Betreff |
| Gültigkeitsdauer | Tage | Standard: 30 | ProSales Kopf |
| Zahlungsbedingung | Text | ProSales Kundenakte | ProSales Kopf |
| PDF-Angebot | Datei | ProSales Export | E-Mail-Anhang |

---

# TEIL A.2 — TESTPLAN

## Phase 1: EXPLORATION

**Geplante Gesprächsstrategie:**

Herr Krause ist wortkarger als Frau Meier. Er gibt kompakte Antworten und muss bei Details gezielt nachgefragt werden. Das testet die Fähigkeit des Explorers, bei knappen Antworten nachzubohren.

| Schritt | Thema | Antwort-Strategie |
|---------|-------|-------------------|
| 1 | Einstieg + Überblick | "Ja, bin bereit. Angebote schreiben, 15x am Tag, Mail → CRM → PDF → zurückschicken." |
| 2 | Wer + Systeme | Herr Krause, Bergmann Industrietechnik. Outlook, ProSales (CRM, Chrome), WAWI (Desktop). |
| 3 | Start + Ende | Start: Outlook Posteingang, Anfrage-Mails. Ende: Angebot versendet, Status "Versendet" in ProSales, Wiedervorlage 7 Tage, Mail in "Erledigt". |
| 4 | Ablauf Teil 1 | Mail → Kunden in ProSales suchen (ggf. Neukunde) → Artikel in WAWI nachschlagen (Preis, Verfügbarkeit). |
| 5 | Ablauf Teil 2 | "Neues Angebot" in ProSales (Nummer automatisch), Positionen, Rabattlogik, Kopffelder, Berechnen. |
| 6 | Ablauf Teil 3 | PDF erzeugen, prüfen. Outlook: Antworten, Textbaustein (Neukunde/Bestandskunde/Eilanfrage + Regel wann welcher), PDF anhängen, Betreff mit Angebotsnummer, senden. |
| 7 | Nachbereitung | Status "Versendet", Wiedervorlage, Mail verschieben. |
| 8 | Sonderfälle | Ohne Artikelnr., Sonderpreis >12% → Herr Berger, Englisch. |
| 9 | Abschluss | "Nee, das war's. Keine Anfrage-Mails mehr → fertig." |

**Prinzip:** Herr Krause beantwortet was gefragt wird. Wenn der Explorer nach dem Endzustand fragt, kommt der Endzustand. Wenn er nach Entscheidungen fragt, kommen Entscheidungen. Die Turns oben sind der Idealfall — bei unerwarteten Fragen spielt der Tester Herr Krause und antwortet mit dem passenden Detail aus dem Prozesswissen.

---

# TEIL B — ZIEL-ARTEFAKTE

## Ziel-Artefakt: Exploration (6 Slots)

### prozessausloeser
> Kundenanfrage per E-Mail im Outlook-Posteingang. Herr Krause öffnet morgens Outlook und bearbeitet eingegangene Anfrage-Mails (Betreff z.B. "Anfrage", "Preisanfrage"). Oft mit Excel-/PDF-Anhang (Stückliste).

**Muss enthalten:** E-Mail, Outlook, Anfrage
**Status:** vollstaendig

### prozessziel
> Angebot als PDF per E-Mail an den Kunden versendet. In ProSales: Angebotsstatus auf "Versendet", Wiedervorlage in 7 Tagen. Anfrage-Mail in Outlook in "Erledigt" verschoben.

**Muss enthalten:** PDF, E-Mail, ProSales, versendet
**Status:** vollstaendig

### prozessbeschreibung
> 1. Anfrage-Mail in Outlook öffnen, Kundennamen und angefragte Produkte/Mengen ablesen.
> 2. In ProSales Kunden suchen (ggf. Neukunde anlegen).
> 3. In WAWI Artikel nachschlagen: Preise und Verfügbarkeit prüfen.
> 4. In ProSales neues Angebot erstellen: Positionen mit Artikelnr., Menge, Preis erfassen. Rabatt anwenden (>5k€: 5%, >10k€: 8%, Key-Account: individuell).
> 5. Angebot berechnen, prüfen, als PDF exportieren.
> 6. Angebot per E-Mail aus Outlook an den Kunden senden (Textbaustein je nach Kundentyp).
> 7. In ProSales Status auf "Versendet" setzen, Wiedervorlage 7 Tage eintragen. Anfrage-Mail in "Erledigt" verschieben.
> Wiederholung: ~15x pro Tag.

**Muss enthalten:** Anfrage lesen, Kunden suchen, WAWI Preise, Angebot erstellen, PDF, E-Mail senden, Wiedervorlage
**Status:** vollstaendig

### entscheidungen_und_schleifen
> ENTSCHEIDUNG: Kunde in ProSales vorhanden? Ja → Akte öffnen. Nein → Neukunde anlegen.
> ENTSCHEIDUNG: Artikel verfügbar? Ja → Lieferzeit "2-3 Werktage". Nein → Lieferdatum aus WAWI.
> ENTSCHEIDUNG: Rabatt? Bestellwert >5.000€ → 5%. >10.000€ → 8%. Key-Account → individuell aus Kundenakte.
> ENTSCHEIDUNG: Textbaustein? Neukunde (nicht in ProSales) → "Neukunde". Bestandskunde → "Bestandskunde". Eilanfrage ("dringend"/"eilig" in der Mail) → "Eilanfrage".
> ENTSCHEIDUNG: Sonderpreis >12%? Ja → Angebot als Entwurf, Weiterleitung an Vertriebsleitung.
> SCHLEIFE: Jede Anfrage-Mail wird einzeln bearbeitet (~15/Tag).

**Muss enthalten:** mindestens 2 Entscheidungen (Kunde, Rabatt), 1 Schleife
**Status:** vollstaendig

### beteiligte_systeme
> Outlook (Desktop-Client, E-Mail), ProSales (CRM, Web-Anwendung in Chrome, Kundenakte, Angebotserstellung), WAWI (Desktop-Programm, Warenwirtschaft, Artikelstamm, Preise, Verfügbarkeit).

**Muss enthalten:** Outlook, ProSales, WAWI
**Status:** vollstaendig

### variablen_und_daten
> Kundenname/Firma — Text, aus E-Mail, für ProSales-Suche.
> Artikelnummer — Text, aus E-Mail/Anhang, für WAWI-Suche und ProSales-Position.
> Menge — Zahl, aus E-Mail/Anhang, für ProSales-Position.
> Listenpreis — Dezimal (€), aus WAWI, für ProSales-Position.
> Rabattstufe — Prozent, aus Bestellwert oder Kundenakte.
> Verfügbarkeit — Ja/Nein + Lieferdatum, aus WAWI.
> Angebotsnummer — Text (auto), von ProSales, für E-Mail-Betreff.

**Muss enthalten:** mindestens 4 Variablen
**Status:** vollstaendig

### Dinge die NICHT im Artefakt stehen dürfen (Halluzinationen)
OCR, KI-gestützt, automatische Belegerkennung, API, REST, Datenbankzugriff,
Machine Learning, SAP, automatische Texterkennung, Chatbot

---

## Universelle Reaktionen

| Situation | Herr Krauses Reaktion |
|-----------|----------------------|
| Agent benutzt Fachbegriffe | "Können Sie das auf Deutsch sagen?" |
| Agent wiederholt eine Frage | "Das hab ich schon gesagt." |
| Agent fragt etwas Technisches | "Keine Ahnung, da müssen Sie unsere IT fragen." |
| Agent lobt oder paraphrasiert | (ignoriert es, wartet auf nächste Frage) |
