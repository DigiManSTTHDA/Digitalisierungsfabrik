# E2E Human Validation Playbook

Wissensreferenz für den Live-E2E-Test der Digitalisierungsfabrik.

**Testprozess:** Reisekostenabrechnung
**Persona:** Frau Weber, Teamleiterin Verwaltung, mittelständische Spedition
**Ziel:** Alle vier Phasen durchlaufen, pro Phase Artefakte prüfen, Bericht ausfüllen.

---

## Ablauf (Live-Persona-Modus)

```
Tool stellt Frage → User kopiert Frage zu Claude →
Claude antwortet als Frau Weber → User kopiert Antwort ins Tool
```

1. User startet das Tool, leitet jede Frage/Antwort des Systems an Claude weiter
2. Claude schlüpft in die Persona Frau Weber und gibt eine passende Antwort
3. User kopiert die Antwort ins Tool
4. Nach jeder Phase: Artefakt im UI mit Ziel-Artefakt (Teil B) vergleichen
5. Am Ende: `validate_e2e_artifacts.py` laufen lassen

**Wichtig:** Claude kennt den Prozess vollständig und antwortet so, dass die Ziel-Artefakte erreichbar sind. Keine zufälligen Antworten — jede Antwort folgt dem Testplan.

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

# TEIL A — PERSONA & PROZESSWISSEN

## Persona-Briefing: Frau Weber

**Rolle:** Teamleiterin Verwaltung bei der **Müller Logistik GmbH** in Augsburg.
**Unternehmen:** Spedition, 85 Mitarbeiter, davon ~30 im Außendienst/Fernverkehr.
**Team:** 3 Personen in der Verwaltung. Frau Schmidt macht fast nur Reisekosten.

**Charakter:**
- Sachlich, pragmatisch, direkt
- Leicht ungeduldig — hat noch andere Sachen zu tun
- Kennt ihren Prozess sehr gut, beschreibt ihn aus der Praxis
- Keine IT-Ausbildung — Fachbegriffe wie "Kontrollfluss", "Parameter", "Iteration" sind ihr fremd
- Reagiert gereizt auf IT-Jargon und EMMA-Aktionstypen
- Spricht in konkreten Beispielen, nicht abstrakt
- Nennt Kolleginnen beim Namen (Frau Schmidt, Frau Klein, Herr Brenner)
- Verwendet Alltagssprache, gelegentlich Umgangssprache

**Typische Formulierungen:**
- "Also der Prozess läuft so: ..."
- "Das ist ein bekanntes Problem."
- "Das weiß ich nicht genau, da müsste ich die IT fragen."
- "Können wir das abkürzen?"
- "Das hab ich doch schon gesagt."

---

## Prozesswissen: Reisekostenabrechnung

> **Hinweis:** Dieses Prozesswissen ist die **vollständige Ground Truth** auf RPA-Niveau.
> Frau Weber kennt all diese Details implizit, gibt sie aber nicht von sich aus strukturiert preis.
> Der Specifier muss sie durch gezielte Fragen herauskitzeln.
> Die Ziel-Artefakte (Teil B) werden gegen dieses Wissen verglichen.

### Überblick
~40-50 Abrechnungen pro Monat. Vom Reiseantrag bis zur Erstattung auf dem Gehaltszettel.
Müller Logistik GmbH, Spedition in Augsburg, 85 Mitarbeiter, davon ~30 regelmäßig auf Dienstreise.
Verwaltungsteam: 3 Personen (Frau Weber = Teamleiterin, Frau Schmidt = Sachbearbeiterin Reisekosten, eine weitere Kollegin).

### Systeme — Übersicht

| System | Zugang | Wer nutzt es | Funktion |
|--------|--------|-------------|----------|
| **TravelPro** | Browser: travelpro.mueller-logistik.de | Mitarbeiter, Teamleiter, Frau Schmidt | Reiseportal: Anträge, Belege, Genehmigungen, Status |
| **SAP HR** | SAP GUI (Desktop-Client, Icon auf Desktop) | Nur Frau Schmidt + Frau Klein | Erstattungsbelege, Gehaltsabrechnung |
| **Outlook** | Desktop-Client | Alle | E-Mail-Kommunikation, Rückfragen, Backup-Benachrichtigungen |
| **Excel** | Lokale Datei auf Netzlaufwerk | Frau Schmidt | Parallelliste (redundant zu TravelPro) |
| **Scanner** | Flachbettscanner am Arbeitsplatz Frau Schmidt | Frau Schmidt | Papierbelege digitalisieren |
| **Intranet** | Browser: intranet.mueller-logistik.de | Alle | Formulare zum Download |

---

### Prozessschritt 1: Reiseantrag stellen

#### Variante A: TravelPro-Portal (Soll-Weg)

1. Mitarbeiter öffnet Browser → Adressleiste: `travelpro.mueller-logistik.de`
2. **Login-Maske:** Feld "Benutzername" (= Windows-Login, z.B. `m.mueller`), Feld "Passwort". Wird gegen Active Directory geprüft. Button "Anmelden" unterhalb.
3. Nach Login: **Dashboard** erscheint. Oben Menüleiste mit Tabs: "Meine Reisen", "Neue Reise", "Belege", "Status".
4. Klick auf Tab **"Neue Reise"** in der oberen Menüleiste.
5. **Antragsformular** öffnet sich mit folgenden Feldern:
   - "Reiseziel" — Freitextfeld (z.B. "München, Messe")
   - "Von" — Datumsfeld mit Datepicker (Kalender-Icon rechts)
   - "Bis" — Datumsfeld mit Datepicker
   - "Reisegrund" — Dropdown: "Kundenbesuch", "Messe/Konferenz", "Schulung", "Projektarbeit", "Sonstiges"
   - "Geschätzte Kosten" — Zahlenfeld in Euro
   - "Kostenstelle" — Dropdown, vorbelegt mit der Kostenstelle der eigenen Abteilung, änderbar
   - "Transportmittel" — Dropdown: "Firmenwagen", "Bahn", "Flug", "Privatwagen", "Mietwagen"
   - "Bemerkungen" — optionales Freitextfeld
6. Button **"Absenden"** unten rechts. Danach Bestätigungsmeldung: "Ihr Reiseantrag wurde eingereicht."
7. Status im Dashboard wechselt auf "Beantragt" (gelbes Label).

#### Variante B: Papierformular (Alt-Weg, ~50% der Mitarbeiter)

1. Mitarbeiter öffnet Browser → `intranet.mueller-logistik.de`
2. Navigiert zu: Bereich "Formulare" → "Personal" → "Reiseantrag"
3. **PDF-Formular** wird heruntergeladen/geöffnet: "Reiseantrag_Vorlage.pdf"
4. Formular enthält Felder (handschriftlich auszufüllen):
   - Name, Personalnummer, Abteilung
   - Reiseziel, Reisezeitraum (von/bis)
   - Reisegrund (Freitext)
   - Geschätzte Kosten
   - Kostenstelle
   - Transportmittel
   - Unterschrift Antragsteller, Datum
   - Unterschrift Genehmiger (leer, wird vom Teamleiter ausgefüllt)
5. Mitarbeiter druckt aus, füllt aus, legt es dem Teamleiter auf den Schreibtisch oder ins Fach.
6. Teamleiter unterschreibt (oder lehnt ab mit Vermerk).
7. Genehmigtes Formular landet in Frau Schmidts Postfach/Ablage.

---

### Prozessschritt 2: Genehmigung

#### Genehmigungsstufen (Regelwerk)

| Bedingung | Genehmiger | Ablauf |
|-----------|-----------|--------|
| Inland, < 500€ | Teamleiter | Nur 1 Genehmigung nötig |
| Inland, ≥ 500€ | Teamleiter + Abteilungsleiter | Sequenziell: TL zuerst, dann AL |
| Ausland (egal welcher Betrag) | Teamleiter + Abteilungsleiter | Wie ≥ 500€ |
| Ab 2.000€ (Inland oder Ausland) | Teamleiter + Abteilungsleiter + Geschäftsführer | Selten, meist Messen/Schulungen im Ausland |

#### Genehmigung im TravelPro-Portal (UI-Detail)

1. **NEU (seit letztem Monat):** Teamleiter sieht oben rechts im Portal ein **Glockensymbol** (🔔) mit roter Zahl = Anzahl offener Genehmigungen.
2. Klick auf Glockensymbol → **Dropdown-Liste** mit offenen Anträgen: "Reiseantrag von [Name] — [Ziel] — [Datum]"
3. Klick auf einen Antrag → **Detailansicht** mit allen Antragsfeldern (read-only).
4. Unten zwei Buttons: **"Genehmigen"** (grün) und **"Ablehnen"** (rot).
5. Bei "Genehmigen": Bestätigungsdialog "Antrag genehmigen?", Button "Ja".
6. Bei "Ablehnen": Pflicht-Textfeld "Ablehnungsgrund" erscheint, dann Button "Ablehnung senden".
7. Nach Genehmigung: Status wechselt auf "Genehmigt" (grünes Label). Bei mehrstufiger Genehmigung: Status "Teilgenehmigt" bis alle Stufen durch.
8. **E-Mail-Backup:** Wenn Teamleiter nach 2 Tagen nicht reagiert, schickt TravelPro automatisch eine E-Mail: "Sie haben einen offenen Reiseantrag von [Name]. Bitte genehmigen Sie im Portal." Mit Link zum Antrag.

#### Problem: Informelle E-Mail-Genehmigung

- **Herr Brenner** (ein Teamleiter) genehmigt grundsätzlich per E-Mail-Antwort an den Mitarbeiter ("Ist genehmigt, fahr los") statt im Portal zu klicken.
- Frau Schmidt muss dann manuell in TravelPro den Status von "Beantragt" auf "Genehmigt" umstellen:
  1. TravelPro → Tab "Meine Reisen" (Frau Schmidt hat Admin-Ansicht: sieht alle) → Antrag suchen
  2. Antrag öffnen → Button "Status ändern" → Dropdown auf "Genehmigt" setzen
  3. Im Feld "Bemerkungen" trägt sie ein: "Genehmigung per E-Mail, siehe Anhang"
  4. E-Mail von Herr Brenner wird als PDF gespeichert und unter "Dokumente" hochgeladen
- **Problem:** Nicht revisionssicher. Wirtschaftsprüfer hat das im letzten Audit angemahnt. "Ein E-Mail-Anhang ist kein rechtsverbindlicher Genehmigungsnachweis."

#### Ablehnung

- Selten (ca. 2x pro Jahr).
- Mitarbeiter bekommt Benachrichtigung im Portal + E-Mail mit Ablehnungsgrund.
- Kann neuen Antrag mit Änderungen stellen.

---

### Prozessschritt 3: Reise durchführen, Belege sammeln

- Mitarbeiter ist unterwegs, sammelt Quittungen, Hotelrechnungen, Tankbelege, Taxiquittungen.
- **Tipp von Frau Weber an neue Mitarbeiter:** "Fotografieren Sie jeden Beleg sofort mit dem Handy, Papier geht zu leicht verloren."
- Belege müssen enthalten: Datum, Betrag, MwSt.-Ausweis (bei Beträgen > 250€ Pflicht), Leistungsbeschreibung.

---

### Prozessschritt 4: Abrechnung einreichen

#### Variante A: TravelPro-Portal

1. Mitarbeiter loggt sich ein (wie bei Schritt 1).
2. Tab **"Meine Reisen"** → Liste der eigenen Reisen mit Status ("Genehmigt", "In Bearbeitung", etc.)
3. Klick auf die genehmigte Reise → **Reise-Detailseite** öffnet sich.
4. Bereich **"Belege"** auf der Detailseite, darunter Button **"Beleg hinzufügen"**.
5. Klick auf "Beleg hinzufügen" → **Upload-Dialog**:
   - **"Datei auswählen"** — Button öffnet Datei-Explorer. Akzeptiert: PDF, JPG, PNG. Max. 10 MB.
   - **"Betrag"** — Zahlenfeld (Dezimal mit Komma, z.B. "87,50")
   - **"Währung"** — Dropdown, vorbelegt "EUR". Bei Ausland: "USD", "GBP", "CHF", etc. TravelPro rechnet automatisch mit EZB-Tageskurs um.
   - **"Datum"** — Datumsfeld mit Datepicker. Muss im Reisezeitraum liegen.
   - **"Ausgabenart"** — Dropdown: "Hotel", "Verpflegung", "Transport/Bahn", "Taxi", "Parkgebühren", "Mietwagen", "Tankbeleg", "Sonstiges"
   - **"Bemerkungen"** — optionales Freitextfeld
6. Button **"Beleg speichern"**. Beleg erscheint in der Liste auf der Detailseite mit Vorschau-Thumbnail.
7. Schritte 5-6 wiederholen für jeden Beleg.
8. **Sonderfall Privatwagen:** Zusätzliches Formular auf der Detailseite: "Kilometerabrechnung"
   - "Startort" — Freitextfeld
   - "Zielort" — Freitextfeld
   - "Gefahrene Kilometer" — Zahlenfeld
   - TravelPro berechnet automatisch: Kilometer × 0,30€ = Erstattungsbetrag (wird angezeigt)
   - "Fahrtenbuch-Scan hochladen" — Upload-Feld (PDF)
9. Wenn alle Belege erfasst: Button **"Abrechnung einreichen"** ganz unten auf der Detailseite.
10. Bestätigungsmeldung: "Ihre Abrechnung wurde zur Prüfung eingereicht."
11. Status wechselt auf "Eingereicht" (blaues Label).

#### Variante B: Papier-Einreichung

1. Mitarbeiter füllt **Abrechnungsformular** aus (separates Formular, auch aus Intranet → "Formulare" → "Personal" → "Reisekostenabrechnung"):
   - Name, Personalnummer, Reisezeitraum
   - Tabelle: Zeile pro Ausgabe (Datum, Art, Betrag, Bemerkung)
   - Summe unten
   - Unterschrift
2. Tackert Originalbelege an das Formular.
3. Legt alles in **Frau Schmidts Postfach** (physisches Ablage-Fach im Büro, beschriftet "Reisekosten") oder schickt es per **Hauspost** (interne Postverteilung der Firma, kommt 1x täglich).

---

### Prozessschritt 5: Prüfung durch Frau Schmidt

#### Im TravelPro-Portal

1. Frau Schmidt loggt sich ein. Hat **Admin-Ansicht** (sieht alle Abrechnungen, nicht nur eigene).
2. Tab **"Prüfung"** → Liste aller eingereichten Abrechnungen, sortiert nach Eingangsdatum.
3. Spalten der Liste: "Name", "Reiseziel", "Zeitraum", "Betrag", "Eingereicht am", "Status".
4. Klick auf eine Abrechnung → **Prüfansicht** mit:
   - **Oberer Bereich:** Reisedaten (Ziel, Zeitraum, Grund, Genehmigungsstatus)
   - **Mittlerer Bereich:** Belegliste mit Vorschau. Klick auf Beleg → Großansicht (Lightbox).
   - **Unterer Bereich:** Summen und Tagessätze (automatisch berechnet)

#### Prüflogik (Schritt für Schritt pro Beleg)

1. Frau Schmidt klickt auf einen Beleg in der Liste → **Vorschau/Lightbox** öffnet sich.
2. Prüft visuell:
   - **Betrag:** Stimmt der eingetragene Betrag mit dem auf dem Beleg überein?
   - **Datum:** Liegt das Belegdatum im Reisezeitraum?
   - **Lesbarkeit:** Ist der Beleg/Scan lesbar? Nicht abgeschnitten, nicht verwaschen?
   - **Ausgabenart:** Passt die gewählte Kategorie zum Beleg? (z.B. Tankquittung ≠ "Hotel")
   - **Plausibilität Hotel:** Übernachtung > 150€/Nacht? → Begründung erforderlich (Feld "Bemerkungen" beim Beleg prüfen)
   - **MwSt.-Ausweis:** Bei Beträgen > 250€: Ist MwSt. auf dem Beleg ausgewiesen?
3. Neben jedem Beleg: Checkbox **"Geprüft"** und Ampelsymbol (grün/gelb/rot).
4. Frau Schmidt setzt Ampel auf:
   - **Grün:** Beleg ok
   - **Gelb:** Kleinigkeit fehlt (z.B. Bemerkung bei teurem Hotel)
   - **Rot:** Beleg nicht akzeptabel (unleserlich, fehlt, Betrag stimmt nicht)

#### Bei Fehlern: Rückfrage

1. Button **"Rückfrage"** auf der Prüfansicht (neben dem fehlerhaften Beleg ODER oben für die ganze Abrechnung).
2. **Rückfrage-Dialog** öffnet sich:
   - Textfeld "Was fehlt / was stimmt nicht?" — Frau Schmidt tippt rein, z.B. "Hotelbeleg vom 15.03. fehlt. Bitte nachreichen."
   - Checkbox "Abrechnung zurückstellen" (Status wird auf "Rückfrage offen" gesetzt)
   - Button "Rückfrage senden"
3. TravelPro schickt automatisch **E-Mail an den Mitarbeiter**: Betreff "Rückfrage zu Ihrer Reisekostenabrechnung [Reiseziel, Datum]", mit dem Rückfrage-Text und Link zur Abrechnung im Portal.
4. Status im Portal wechselt auf **"Rückfrage offen"** (oranges Label).
5. **Frist:** Mitarbeiter hat 2 Wochen. Wenn nichts kommt → TravelPro schickt automatische Erinnerung. Wenn dann immer noch nichts kommt → Frau Schmidt streicht den Posten manuell (Button "Posten streichen" → Betrag wird auf 0 gesetzt, Vermerk "Nicht nachgereicht").

#### Nachbesserungsschleife

- Mitarbeiter korrigiert/ergänzt im Portal (neuen Beleg hochladen oder Betrag ändern) → Klickt "Erneut einreichen".
- Status wechselt zurück auf "Eingereicht".
- Frau Schmidt prüft erneut.
- Kann 2-3 Runden dauern. Danach akzeptiert Frau Schmidt oder streicht den Posten.

#### Finale Freigabe

- Wenn alle Belege grün: Button **"Abrechnung freigeben"** oben auf der Prüfansicht.
- Status wechselt auf **"Freigegeben"** (grünes Label).
- Abrechnung erscheint auf Frau Schmidts **SAP-Warteliste** (eigene Excel-Zeile + Markierung in TravelPro).

---

### Prozessschritt 6: Papier-Workflow (Erfassung durch Frau Schmidt)

> Dieser Schritt entfällt bei Portal-Einreichern. Betrifft ~50% der Abrechnungen.

1. Frau Schmidt nimmt Papierformular + Belege aus ihrem Postfach.
2. Öffnet TravelPro → Tab "Prüfung" → Button **"Neue Abrechnung erfassen"** (Admin-Funktion).
3. **Erfassungsformular** (ähnlich wie Mitarbeiter-Formular, aber Frau Schmidt füllt stellvertretend aus):
   - "Mitarbeiter" — Dropdown/Suchfeld mit allen Mitarbeitern (tippt Name, Autocomplete)
   - "Reise auswählen" — Dropdown mit genehmigten Reisen dieses Mitarbeiters
   - Falls keine Reise im System (Papierantrag): Button "Reise manuell anlegen" → Mini-Formular (Ziel, Zeitraum, Grund, Kostenstelle)
4. Dann pro Beleg:
   - Frau Schmidt legt Papierbeleg auf den **Flachbettscanner** (Canon CanoScan, steht rechts auf ihrem Schreibtisch).
   - Scannt als PDF (Taste am Scanner oder über Canon-Software auf dem PC).
   - Benennt die Datei: **"Nachname_Datum_Belegtyp.pdf"** (z.B. "Mueller_20260315_Hotel.pdf").
   - Speichert auf Netzlaufwerk: `S:\Verwaltung\Reisekosten\Scans\2026\`
   - Zurück in TravelPro: "Beleg hinzufügen" → Datei auswählen → Betrag, Datum, Ausgabenart eintragen (liest sie vom Papierbeleg ab) → "Beleg speichern"
5. Wiederholen für jeden Beleg. **Dauert ca. 15-20 Minuten pro Abrechnung** (vs. 5 Minuten bei Portal-Einreichung).
6. Wenn alle Belege erfasst: direkt weiter mit Prüfung (Schritt 5) — Frau Schmidt prüft ihre eigene Erfassung nochmal gegen die Papierbelege.
7. Papierbelege kommen in einen **Ordner** ("Reisekosten 2026"), sortiert nach Monat, im Aktenschrank im Büro. Aufbewahrungsfrist: 10 Jahre (steuerlich).

---

### Prozessschritt 7: SAP-Verbuchung

1. Frau Schmidt öffnet **SAP GUI** (Desktop-Verknüpfung "SAP Logon" auf dem Desktop).
2. SAP Logon → System "PRD" (Produktivsystem) auswählen → Doppelklick.
3. **SAP-Anmeldebildschirm:** Mandant "100", Benutzer "FSCHMIDT", Passwort → Enter.
4. **SAP Easy Access** Startbildschirm erscheint. Transaktionscode-Feld oben links.
5. Frau Schmidt gibt Transaktion **"PR05"** ein (Reisekosten) → Enter.
6. Alternativ: Menüpfad "Personal" → "Personaladministration" → "Reisekosten" → "Erstattungsbeleg anlegen".
7. **Erstattungsbeleg-Maske** erscheint:
   - **"Personalnummer"** — 8-stellig, z.B. "00012345". Frau Schmidt schaut die in TravelPro nach (Mitarbeiterprofil) oder in ihrer Excel-Liste.
   - **"Reisezeitraum"** — Feld "Von" und "Bis" (Datumsformat TT.MM.JJJJ)
   - **"Reiseart"** — Dropdown: "Inland", "Ausland"
   - Tab **"Kostenübersicht"**: Tabelle mit Zeilen pro Kostenart:
     - "Kostenart" — Dropdown: "Übernachtung", "Verpflegung", "Fahrtkosten", "Nebenkosten"
     - "Betrag" — Zahlenfeld
     - "Kostenstelle" — wird aus TravelPro übernommen (Frau Schmidt tippt die 6-stellige Nummer ab)
   - Tab **"Tagessätze"**: Automatisch berechnet nach Reiseart + Dauer. Frau Schmidt prüft nur.
   - **"Gesamtbetrag"** — wird automatisch summiert, read-only.
8. Button **"Prüfen"** (oben in der Toolbar, Häkchen-Symbol) → SAP validiert die Eingaben.
9. Bei Fehler: SAP zeigt rote Meldung unten im Statusbalken (z.B. "Kostenstelle ungültig").
10. Button **"Sichern"** (Disketten-Symbol) → Belegnummer wird vergeben (z.B. "5000012345").
11. Frau Schmidt notiert die **SAP-Belegnummer** in TravelPro: Abrechnung öffnen → Feld "SAP-Referenz" → Belegnummer eintragen → Speichern.
12. Status in TravelPro wechselt auf **"Verbucht"** (dunkelgrünes Label).

---

### Prozessschritt 8: Zahlungslauf & Erstattung

1. **Frau Klein** (Lohnbuchhaltung) öffnet SAP HR am Monatsende.
2. Transaktion **"PC00_M99_CIPE"** (Gehaltsabrechnung) oder spezifisch den Reisekosten-Zahlungslauf.
3. Prüft alle offenen Erstattungsbelege → Stichproben auf Plausibilität.
4. Gibt den **Zahlungslauf frei** (Button "Freigabe" im SAP).
5. Erstattung erscheint auf dem **Gehaltszettel** des Mitarbeiters als separate Position "Reisekostenerstattung".
6. Auszahlung mit dem nächsten regulären Gehaltslauf (spätestens übernächste Gehaltsabrechnung).

---

### Prozessschritt 9: Excel-Parallelliste (Frau Schmidt)

> Dieses Spannungsfeld läuft parallel zu den Schritten 5-7.

1. Frau Schmidt öffnet Excel-Datei: `S:\Verwaltung\Reisekosten\Reisekosten_Tracking_2026.xlsx`
2. **Tabellenblatt** des aktuellen Monats (z.B. "März 2026").
3. Spalten:
   - A: "Lfd. Nr." (fortlaufend)
   - B: "Name"
   - C: "Personalnummer"
   - D: "Reiseziel"
   - E: "Zeitraum"
   - F: "Betrag"
   - G: "Eingereicht am"
   - H: "Status" (Freitext: "eingereicht", "geprüft", "Rückfrage", "verbucht", "erstattet")
   - I: "SAP-Belegnummer"
   - J: "Bemerkungen"
4. Frau Schmidt trägt **jede einzelne Abrechnung** hier ein — parallel zu TravelPro.
5. Nutzt die Liste für:
   - Monatsübersicht: Summenformel unten zeigt Gesamtbetrag des Monats
   - Status-Tracking: Schnellblick wer noch offen ist
   - Jahresauswertung: Pivot-Tabelle auf separatem Blatt "Auswertung" (nach Mitarbeiter, nach Kostenstelle, nach Monat)
6. **Problem:** Daten laufen auseinander. Wenn Frau Schmidt einen Status in TravelPro ändert aber in Excel vergisst (oder umgekehrt) → Inkonsistenz. Ist schon vorgekommen.

---

### Fristen & Regelungen

- **Einreichfrist:** 4 Wochen nach Reiseende. Danach Erstattung nur mit Begründung und Genehmigung des Abteilungsleiters.
- **Erstattungsfrist:** Spätestens übernächste Gehaltsabrechnung nach Freigabe.
- **Tagessätze** nach Bundesreisekostengesetz (BRKG):
  - Inland: 14€ ab 8h Abwesenheit, 28€ ab 24h Abwesenheit
  - Ausland: länderspezifisch, Tabelle wird jährlich vom Finanzministerium veröffentlicht. Frau Schmidt hat die aktuelle Tabelle als PDF im Ordner `S:\Verwaltung\Reisekosten\Tagessaetze\BRKG_Ausland_2026.pdf`
- **Belege:** Originalbelege (Papier) müssen 10 Jahre aufbewahrt werden (steuerlich). Scans sind zusätzlich, nicht Ersatz.
- **Hotelkosten > 150€/Nacht:** Begründung erforderlich im Bemerkungsfeld.
- **MwSt.-Ausweis:** Pflicht bei Einzelbelegen > 250€.

### Ausnahmen & Sonderfälle

#### Privatwagen (statt Firmenwagen/Bahn)
- Pauschale: 30 ct/km
- Im TravelPro: Detailseite der Reise → Bereich "Kilometerabrechnung":
  - "Startort" (Freitext), "Zielort" (Freitext), "Gefahrene Kilometer" (Zahl)
  - TravelPro berechnet automatisch: km × 0,30€
  - Upload-Feld "Fahrtenbuch-Scan" (PDF)
- **Frau Schmidts Prüfung:** Öffnet Google Maps im Browser, gibt Start-/Zielort ein, vergleicht die angezeigte Strecke mit der angegebenen Kilometerzahl. Bei > 10% Abweichung → Rückfrage an den Mitarbeiter.

#### Eigenbeleg (verlorener Beleg)
- Formular "Eigenbeleg" aus Intranet: `intranet.mueller-logistik.de` → "Formulare" → "Personal" → "Eigenbeleg"
- Felder: Was bezahlt (Beschreibung), Wann (Datum), Wo (Ort/Anbieter), Betrag, Unterschrift Mitarbeiter, Unterschrift Teamleiter
- **Limit:** Max. 50€ pro Einzelposten. Darüber wird ohne Originalbeleg nicht erstattet.
- Frau Schmidt scannt den unterschriebenen Eigenbeleg ein und lädt ihn in TravelPro als Beleg hoch (Ausgabenart "Sonstiges", Bemerkung "Eigenbeleg").

#### Stornierte Reise
- Gebuchte Reise findet nicht statt (z.B. Messe abgesagt, Kunde storniert).
- Stornokosten (Hotel-Storno, Flug-Storno) werden trotzdem über TravelPro abgerechnet.
- Mitarbeiter reicht Stornobelege ein wie normale Belege.
- Im Feld "Reisegrund" ergänzt er "STORNIERT" und im Bemerkungsfeld den Stornogrund.

#### Auslandsbelege in Fremdwährung
- Mitarbeiter gibt im TravelPro den **Betrag in Originalwährung** ein und wählt die Währung im Dropdown.
- TravelPro rechnet automatisch mit dem **EZB-Tageskurs** des Belegdatums um und zeigt den Euro-Betrag an.
- Falls Mitarbeiter keinen Kurs eingibt (z.B. bei Papier-Einreichung): Frau Schmidt öffnet `bundesbank.de` → "Statistiken" → "Wechselkurse" → sucht den Tageskurs zum Belegdatum → trägt den umgerechneten Euro-Betrag manuell in TravelPro ein.

### Hauptprobleme (Spannungsfelder)

1. **Papier-Einreicher:** ~50% nutzen TravelPro nicht → Frau Schmidt muss alles abtippen + scannen. 3x Zeitaufwand. Fehleranfällig (Tippfehler bei Beträgen).
2. **E-Mail-Genehmigung:** Teamleiter (v.a. Herr Brenner) genehmigen per E-Mail statt Portal → nicht revisionssicher. Wirtschaftsprüfer hat es angemahnt. Frau Schmidt muss Status manuell umstellen und E-Mail als Nachweis anhängen.
3. **Excel-Parallelliste:** Frau Schmidt trackt alles in Excel UND in TravelPro → doppelter Aufwand, Daten laufen auseinander. Frau Schmidt sagt: "Die Auswertungen in TravelPro sind zu umständlich, in Excel hab ich alles auf einen Blick."
4. **Fehlende Belege:** Dauerthema. Mitarbeiter vergessen Belege, reichen unleserliche Scans ein, oder verlieren Quittungen. Nachbesserungsschleifen kosten Zeit (2-3 Runden keine Seltenheit).

### Beteiligte Rollen

| Rolle | Person(en) | System-Zugang | Aufgaben im Prozess |
|-------|-----------|---------------|---------------------|
| Reisender Mitarbeiter | ~30 verschiedene | TravelPro (eigene Reisen) | Antrag stellen, Belege einreichen |
| Teamleiter | Div., u.a. Herr Brenner | TravelPro (Genehmigungen) | Reisen genehmigen (Stufe 1) |
| Abteilungsleiter | Div. | TravelPro (Genehmigungen) | Reisen genehmigen (Stufe 2, ≥500€/Ausland) |
| Geschäftsführer | 1 Person | TravelPro (selten) | Reisen genehmigen (Stufe 3, ≥2000€) |
| Frau Schmidt | 1 Person | TravelPro (Admin), SAP HR, Excel, Scanner | Prüfung, Papier-Erfassung, SAP-Verbuchung, Excel-Liste |
| Frau Klein | 1 Person | SAP HR | Monatsend-Prüfung, Zahlungslauf-Freigabe |

### Variablen & Daten (vollständig)

| Variable | Typ | Quelle | Verwendet in |
|----------|-----|--------|-------------|
| Personalnummer | 8-stellig numerisch | SAP HR / TravelPro-Profil | SAP-Verbuchung, Excel-Liste |
| Name des Reisenden | Text | TravelPro-Profil | Überall |
| Reiseziel | Freitext | Reiseantrag | Antrag, Abrechnung, SAP |
| Reisezeitraum Von | Datum (TT.MM.JJJJ) | Reiseantrag | Antrag, Tagessatzberechnung, SAP |
| Reisezeitraum Bis | Datum (TT.MM.JJJJ) | Reiseantrag | Antrag, Tagessatzberechnung, SAP |
| Reisegrund | Dropdown + Freitext | Reiseantrag | Antrag |
| Kostenstelle | 6-stellig numerisch | Abteilungszuordnung | Antrag, SAP-Verbuchung |
| Geschätzte Kosten | Dezimalzahl (€) | Reiseantrag | Genehmigungsstufe |
| Transportmittel | Dropdown | Reiseantrag | Antrag, ggf. km-Pauschale |
| Einzelbeleg-Betrag | Dezimalzahl (€ oder Fremdwährung) | Beleg | Abrechnung, Prüfung |
| Einzelbeleg-Datum | Datum | Beleg | Prüfung (im Reisezeitraum?) |
| Ausgabenart | Dropdown (7 Werte) | Beleg-Erfassung | Abrechnung, SAP-Kostenart |
| Belegdatei | PDF/JPG/PNG | Upload/Scan | Prüfung, Archivierung |
| Tagessatz | Berechnet (BRKG) | Reisezeitraum + Ziel | Abrechnung, SAP |
| Gesamtbetrag | Berechnet (Summe) | Alle Belege + Tagessätze | SAP-Verbuchung, Excel |
| Genehmigungsstatus | Enum | Portal/E-Mail | Genehmigungsstufe |
| SAP-Belegnummer | 10-stellig numerisch | SAP nach Sichern | TravelPro-Referenz, Excel |
| Gefahrene Kilometer | Ganzzahl | Kilometerpauschale | km × 0,30€ |
| Währung | ISO-Code (EUR, USD...) | Beleg-Erfassung (Ausland) | Umrechnung |
| Wechselkurs | Dezimalzahl | EZB/Bundesbank | Umrechnung Fremdwährung → EUR |

---

# TEIL A.2 — TESTPLAN

## Teststrategie pro Phase

### Phase 1: EXPLORATION

**Ziel:** Alle 7 Slots mit korrekten Inhalten füllen.

**Vorbereitung:**
- Neues Projekt anlegen (Name: "Reisekostenabrechnung")
- System zeigt: Phase `exploration`, Modus `moderator`

**Geplante Gesprächsstrategie:**

| Schritt | Thema | Antwort-Strategie | Erwartetes Systemverhalten |
|---------|-------|-------------------|---------------------------|
| 1 | Vorfrage | Frau Weber fragt vorab ob man unterbrechen kann, wie detailliert es sein muss | Moderator beantwortet, fragt ob es losgehen kann. Modus bleibt `moderator`. |
| 2 | Start bestätigen | Kurzes "Ja, legen wir los" | Wechsel zu `exploration`. Erste inhaltliche Frage. |
| 3 | Auslöser + Grobablauf | Reiseantrag, Genehmigung, Belege, Prüfung, Erstattung. Portal vs. Papier erwähnen. Beiläufig TravelPro-Akzeptanzproblem. | Explorer extrahiert prozessausloeser, beginnt prozessbeschreibung. |
| 4 | Systeme + Medienbrüche | SAP HR, TravelPro, Outlook, Excel-Liste, Papierformular. Frau Schmidt muss abtippen. | Explorer füllt beteiligte_systeme. |
| 5 | Genehmigungsstufen | Dreistufig: TL < 500€, AL ≥ 500€/Ausland, GF ≥ 2000€. E-Mail-Genehmigungsproblem. | Explorer erkennt Entscheidungen. |
| 6 | **ESKALATION** | Frau Weber wird ungeduldig: "dreht sich im Kreis", "hab noch andere Sachen zu tun". **Danach: Panik-Button.** | Modus wechselt zu `moderator`. Artefakt bleibt intakt. |
| 7 | Eskalation beim Moderator | Frau Weber beschreibt Problem: "fragt immer das Gleiche" | Moderator analysiert, schickt NICHT sofort zurück. |
| 8 | Rückkehr bestätigen | "Ok, geben Sie mich zurück, aber er soll auf den Punkt kommen" | Wechsel zurück zu `exploration`. |
| 9 | Systeme ergänzen (post-Eskalation) | SAP HR, TravelPro, Outlook, Excel-Liste nochmal zusammenfassen + Vertrauensproblem Excel. | Explorer-Antwort sollte kürzer sein als vor Eskalation. |
| 10 | Ausnahmen + Sonderfälle | Privatwagen (30ct/km, Fahrtenbuch), Eigenbeleg (bis 50€, TL-Unterschrift), stornierte Reisen. | Explorer füllt entscheidungen_und_schleifen weiter. |
| 11 | Letzte Details | Unternehmensdaten (85 MA, 30 Reisende, 40-50/Monat), Tagessätze (BRKG), Fristen. | variablen_und_daten wird gefüllt. |
| 12 | Ende signalisieren | "Das war alles. Mehr kann ich nicht sagen." | Explorer schreibt prozesszusammenfassung SELBST, meldet phase_complete. |
| 13 | Phasenwechsel bestätigen | "Ja, weiter zur nächsten Phase." | Phase wechselt zu `strukturierung`. |

**Falls kein phase_complete nach Schritt 12:**
Nudges: "Ja das war wirklich alles" → "Bitte schließen Sie die Exploration ab" → "Exploration beenden, weiter zur Strukturierung"

**Eskalations-Prüfpunkte:**
- [ ] Panik-Button → Moderator aktiv?
- [ ] Artefakt nach Eskalation intakt?
- [ ] Moderator analysiert (schickt nicht sofort zurück)?
- [ ] Moderator hat Artefakt NICHT verändert?
- [ ] Rückkehr zu exploration nach Schritt 8?
- [ ] Explorer-Antwort kürzer nach Eskalation?

---

### Phase 2: STRUKTURIERUNG

**Ziel:** Mindestens 5 Strukturschritte mit korrekten Typen, Entscheidungen mit Bedingungen und Nachfolgern.

**Geplante Gesprächsstrategie:**

| Schritt | Thema | Antwort-Strategie | Erwartetes Systemverhalten |
|---------|-------|-------------------|---------------------------|
| 1 | Rückfrage | "Was machen wir jetzt? Muss ich nochmal alles erzählen?" | Modus bleibt `moderator`. |
| 2 | Start bestätigen | "Gut, dann zeigen Sie mal was Sie daraus gemacht haben." | Wechsel zu `structuring`. |
| 3 | Genehmigung präzisieren | Dreistufig nochmal genau: < 500 TL, ≥ 500/Ausland AL, ≥ 2000 GF. Selten, meist Messen. | Entscheidungsschritte werden verfeinert. |
| 4 | Rückfrage-Schleife | Nachbesserungsschleife bei Prüfung: Abrechnung zurück, korrigieren, nochmal einreichen. 2-3 Runden. | Schleifencharakter erkannt. |
| 5 | **ESKALATION** | Frau Weber stört sich an Fachbegriffen: "Kontrollfluss", "Verzweigung" — "Das sind keine normalen Wörter." **Danach: Panik-Button.** | Modus wechselt zu `moderator`. |
| 6 | Eskalation beim Moderator | "Redet in Fachbegriffen. Verzweigung, Entscheidungsknoten, Iteration — sagt mir nichts." | Moderator analysiert. Artefakt unverändert. |
| 7 | Rückkehr bestätigen | "Ja, nochmal. Aber normale Sprache und immer nur eine Frage." | Wechsel zu `structuring`. |
| 8 | Spannungsfeld Excel | Excel-Parallelliste detailliert beschreiben. "Das nervt mich am meisten." | Spannungsfeld wird im Artefakt vermerkt. |
| 9 | Spannungsfeld E-Mail | Herr Brenner genehmigt per E-Mail, nicht im Portal. Wirtschaftsprüfer hat angemahnt. | Zweites Spannungsfeld vermerkt. |
| 10 | Fertig | "Ja, die Struktur passt so." | phase_complete. |
| 11 | Phasenwechsel | "Ja, weiter zur nächsten Phase." | Phase wechselt zu `spezifikation`. |

---

### Phase 3: SPEZIFIKATION

**Ziel:** Mindestens 6 Algorithmus-Abschnitte mit EMMA-Aktionen. Widerspruch-Korrektur eingearbeitet.

**Geplante Gesprächsstrategie:**

| Schritt | Thema | Antwort-Strategie | Erwartetes Systemverhalten |
|---------|-------|-------------------|---------------------------|
| 1 | Rückfrage | "Jetzt nochmal? Was kommt denn noch?" (leicht genervt) | Modus bleibt `moderator`. |
| 2 | Start bestätigen | "Also nochmal genauer wie wir was am Computer machen. Ok, dann los." | Wechsel zu `specification`. |
| 3 | TravelPro-Antrag (**FALSCH!**) | Beschreibt Portal-Antrag. Sagt dabei FALSCH: "Teamleiter kriegt eine E-Mail mit Link." (Wird in Schritt 6 korrigiert!) | System erfasst die Beschreibung. |
| 4 | Belegerfassung | TravelPro → "Belege hochladen" → Foto/Scan → Betrag, Datum, Ausgabenart (Dropdown) → "Abrechnung einreichen" | Algorithmus-Abschnitt für Belegerfassung. |
| 5 | Prüfung (**UNVOLLSTÄNDIG**) | Frau Schmidt öffnet Liste, prüft Belege. Aber bewusst vage: "Da gibt es noch einiges, fragen Sie mich gezielt." | System soll nachfragen (Fragezeichen in Antwort). |
| 6 | **WIDERSPRUCH-KORREKTUR** | "Moment, ich muss was korrigieren." Push-Benachrichtigung statt E-Mail. Glockensymbol. E-Mail nur noch Backup nach 2 Tagen. IT-Leiter hat umgestellt. | Artefakt wird aktualisiert. Push/Glockensymbol taucht auf. |
| 7 | **ESKALATION** | Frau Weber stört sich an EMMA-Jargon: "FIND_AND_CLICK, READ_FORM — das sind keine deutschen Wörter." **Danach: Panik-Button.** | Modus wechselt zu `moderator`. |
| 8 | Eskalation beim Moderator | "Stellt technische Fragen. Was ist ein Parameter? Schreibt englische Abkürzungen. Ich bin Verwaltungsleiterin." | Moderator analysiert. |
| 9 | Rückkehr | "Ok, nochmal. Aber als würde er einem Kollegen erklären was am Bildschirm passiert." | Wechsel zu `specification`. |
| 10 | SAP-Verbuchung | SAP HR → Reisekosten → neuer Erstattungsbeleg → Personalnummer, Zeitraum, Betrag, Kostenarten, Kostenstelle → Speichern → automatisch in Gehaltsabrechnung. | Algorithmus-Abschnitt für SAP. |
| 11 | Papier-Workflow | Hauspost/Fach, Frau Schmidt tippt alles in TravelPro, scannt Belege, 3x so lang. | Algorithmus-Abschnitt für Papier. |
| 12 | Eigenbeleg | Formular, was/wann/wo, TL-Unterschrift, Scan, max 50€. | Algorithmus-Abschnitt für Eigenbeleg. |
| 13 | Fertig | "Das war wirklich alles. Sind wir endlich fertig?" | phase_complete. |
| 14 | Phasenwechsel | "Ja, weiter zur Prüfung. Hoffentlich der letzte Schritt." | Phase wechselt zu `validierung`. |

**Kritische Prüfpunkte Phase 3:**
- [ ] Bei Schritt 5: System fragt nach bei unvollständiger Info?
- [ ] Bei Schritt 6: Widerspruch-Korrektur eingearbeitet? (Push-Benachrichtigung/Glockensymbol statt E-Mail)
- [ ] Nach Eskalation: System vermeidet EMMA-Jargon oder erklärt ihn?

---

### Phase 4: VALIDIERUNG

**Ziel:** Validierungsbericht angezeigt, Projekt abgeschlossen.

| Schritt | Thema | Antwort-Strategie | Erwartetes Systemverhalten |
|---------|-------|-------------------|---------------------------|
| 1 | Ergebnis ansehen | "Ja, was hat die Prüfung ergeben?" | Validierungsbericht mit Befunden. |
| 2 | Reaktion auf Befunde | "Klingt vernünftig. Die kritischen Punkte stimmen." | System nimmt Feedback entgegen. |
| 3 | Abschluss | "Ergebnis ist akzeptabel. Projekt abschließen." | Projekt wird als `abgeschlossen` markiert. Export verfügbar. |

---

## Universelle Reaktionen (alle Phasen)

Diese Reaktionsmuster wendet Frau Weber an, unabhängig von der Phase:

| Situation | Frau Webers Reaktion |
|-----------|---------------------|
| Agent benutzt Fachbegriffe (Verzweigung, Kontrollfluss, Iteration, Parameter) | "Reden Sie bitte Deutsch mit mir, ich bin Verwaltungsleiterin und keine Programmiererin." |
| Agent benutzt EMMA-Aktionstypen (READ, FIND, TYPE, FILE_OPERATION) | "Diese technischen Kürzel sagen mir nichts. Erklären Sie in normalen Worten." |
| Agent wiederholt eine schon beantwortete Frage | "Das hab ich doch schon gesagt. Können wir weitermachen?" |
| Agent fragt etwas Technisches das Frau Weber nicht weiß | "Das weiß ich nicht genau, da müsste ich unsere IT fragen. Können wir das erstmal offen lassen?" |
| Agent antwortet auf Englisch | "Bitte auf Deutsch antworten." |
| Phase will nicht enden nach mehreren Versuchen | "Ich hab alles gesagt was ich weiß. Bitte schließen Sie diese Phase ab." |

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
| 1 | Vorfrage | Modus bleibt moderator | | |
| 2 | Start bestätigen | Wechsel zu exploration | | |

### Eskalation

| Prüfpunkt | Ergebnis | OK? |
|-----------|----------|-----|
| Panik-Button → Moderator aktiv? | | |
| Artefakt nach Eskalation intakt? | | |
| Moderator analysiert (nicht sofort zurück)? | | |
| Moderator hat Artefakt NICHT verändert? | | |
| Rückkehr zu exploration nach Schritt 8? | | |
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
| 1 | Modus bleibt moderator | | |
| 2 | Wechsel zu structuring | | |

### Eskalation

| Prüfpunkt | Ergebnis | OK? |
|-----------|----------|-----|
| Panik-Button → Moderator aktiv? | | |
| Artefakt nach Eskalation intakt? | | |
| Moderator hat Artefakt NICHT verändert? | | |
| Rückkehr zu structuring nach Schritt 7? | | |

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
| 1 | Modus bleibt moderator | | |
| 2 | Wechsel zu specification | | |

### Eskalation

| Prüfpunkt | Ergebnis | OK? |
|-----------|----------|-----|
| Panik-Button → Moderator aktiv? | | |
| Artefakt nach Eskalation intakt? | | |
| Moderator hat Artefakt NICHT verändert? | | |
| Rückkehr zu specification nach Schritt 9? | | |

### Spezielle Prüfpunkte

| Prüfpunkt | Ergebnis | OK? |
|-----------|----------|-----|
| Schritt 5: System fragt nach bei unvollst. Info? | | |
| Schritt 6: Widerspruch-Korrektur eingearbeitet? | | |
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
Das ist der Testfall. In Phase 3 (Schritt 7) wird genau das als Problem
eskaliert. Nach der Eskalation sollte das System verständlicher werden.

### Init-Progress-Feedback (CR-007)
Beim Eintritt in Phase 2 und Phase 3 wird ein Background-Init ausgeführt.
Während der Wartezeit (10-40 Sekunden) sollte das System Fortschrittsmeldungen
anzeigen. Wenn keine Meldungen erscheinen oder die Wartezeit übermäßig lang
ist, ist das ein Befund.
