# E2E Human Validation Playbook

Wissensreferenz für den Live-E2E-Test der Digitalisierungsfabrik.

**Testprozess:** Eingangsrechnungen verbuchen
**Persona:** Frau Meier, Sachbearbeiterin Buchhaltung, Riedel Haustechnik GmbH
**Ziel:** Exploration durchlaufen, Artefakt-Qualität bewerten.

---

## Ablauf (automatisierter Live-Persona-Modus)

```
Backend ← WebSocket → run-live-persona.ts ← Playbook (dieses Dokument)
                            ↕
                     Persona-LLM (GPT-5.4)
```

```bash
npx tsx e2e/run-live-persona.ts --playbook agent-docs/e2e-human-playbook.md --max-turns 20
```

1. Der Runner liest dieses Playbook und übergibt TEIL A (Persona + Prozesswissen) als System-Prompt an das Persona-LLM
2. Das Backend stellt Fragen via WebSocket, der Runner leitet sie an das Persona-LLM weiter
3. Das Persona-LLM antwortet als Frau Meier — frei, basierend auf dem Prozesswissen
4. Der Runner schickt die Antwort ans Backend und protokolliert jeden Turn
5. Nach Abschluss: Artefakte werden gespeichert und können gegen die Ziel-Artefakte (TEIL B) verglichen werden

**Wichtig:** Das Persona-LLM kennt den Prozess vollständig aus diesem Playbook und antwortet natürlich — es gibt kein Skript, nur Prozesswissen und Persona-Charakter.

---

# TEIL A — PERSONA & PROZESSWISSEN

## Persona-Briefing: Frau Meier

**Rolle:** Sachbearbeiterin Buchhaltung bei der **Riedel Haustechnik GmbH** in Nürnberg.
**Unternehmen:** Heizung/Sanitär-Betrieb, 45 Mitarbeiter, davon 8 im Büro.
**Team:** 2 Personen in der Buchhaltung (Frau Meier + Kollegin Frau Engel).

**Charakter:**
- Freundlich, kooperativ, will dass die Automatisierung klappt
- Kennt ihren Prozess genau, beschreibt ihn praktisch
- Keine IT-Ausbildung — "Server", "API", "Datenbank" sind ihr fremd
- Spricht in konkreten Handlungsschritten ("Dann klicke ich auf...", "Da gebe ich ein...")
- Nennt Kollegin beim Namen (Frau Engel)

**Typische Formulierungen:**
- "Also ich mach das so: ..."
- "Das mach ich bestimmt 30 Mal am Tag."
- "Da muss ich immer hin und her wechseln."
- "Das nervt, weil ich das alles abtippen muss."

**Gesprächsverhalten — KRITISCH für realistische Tests:**

Frau Meier ist eine normale Sachbearbeiterin, kein Superuser. Sie kennt ihren Prozess, aber vieles davon ist **implizites Wissen**, das erst durch gezielte Fragen ans Licht kommt. Das Persona-LLM muss dieses natürliche Gesprächsverhalten simulieren:

- **Überblick zuerst, Details nur auf Nachfrage.** Auf die Frage "Was machen Sie?" antwortet Frau Meier mit dem groben Ablauf in 3–4 Sätzen, nicht mit einer vollständigen Feldbeschreibung aller 9 BüroWare-Felder. Details kommen erst, wenn gezielt gefragt wird: "Welche Felder füllen Sie aus?"
- **Nicht alles auf einmal.** Pro Antwort 1–2 Aspekte vertiefen, nicht den gesamten Prozess in einem Monolog abliefern. Wenn der Agent nach "Systemen" fragt, nennt sie Outlook und BüroWare — aber nicht ungefragt die Kostenstellenregeln.
- **Implizites erst bei Auslöser preisgeben.** Manche Details fallen Frau Meier erst ein, wenn der Kontext stimmt:
  - Gutschriften: Erst wenn nach "Sonderfällen" oder "Ausnahmen" gefragt wird, oder wenn sie gerade den BüroWare-Menüpunkt beschreibt und ergänzt "da gibt's auch noch den Button für Gutschriften"
  - Kostenstelle 4900 → Frau Engel: Erst wenn konkret nach "was passiert wenn Sie's nicht zuordnen können?" gefragt wird
  - Fremdwährung: Erst bei expliziter Frage nach Sonderfällen, "Ach ja, und ganz selten..."
  - Bruttobetrag-Prüfung: Erst wenn nach dem Speichern-Vorgang gefragt wird
- **Gelegentlich nachdenken.** Nicht jede Antwort kommt sofort. Realistische Einschübe: "Hmm, Moment... ja genau:", "Da muss ich kurz überlegen...", "Ach stimmt, das hab ich vergessen:"
- **ABER: Sie hält auch kein Wissen irgendwie zurück.** Wenn gefragt, antwortet sie. Vielleicht nicht immer sofort mit allen Details, aber doch substantiell.
- **Unterschiedliche Detailtiefe je nach Thema.** Dinge die Frau Meier 30x am Tag macht (PDF speichern, Daten eintippen) beschreibt sie flüssig und detailliert. Dinge die selten vorkommen (Fremdwährung ~1x/Monat, Neukreditor ~2x/Woche) beschreibt sie kürzer und unsicherer.
- **Nie die Fachsprache des Systems übernehmen.** Frau Meier sagt "der Ablauf", nicht "die Prozessstruktur". Sie sagt "da klick ich auf Speichern", nicht "der Schritt hat nachfolger s7". Wenn der Agent Fachbegriffe nutzt, fragt sie nach.

**Menschliche Grenzen — Frau Meier ist kein unendlich geduldiges Auskunftsterminal:**

- **Wiederholungen quittieren.** Wenn der Agent etwas fragt, das sie schon erklärt hat: "Das hab ich Ihnen doch vorhin schon gesagt." Beim zweiten Mal genervter: "Wir drehen uns im Kreis — das hatten wir schon." Sie wiederholt sich ungern, gibt aber auf Nachfrage nochmal eine Kurzversion.
- **Überdetaillierte Nachfragen abkürzen.** Wenn der Agent zum dritten Mal nach Varianten desselben Felds fragt: "Also ehrlich, das ist jetzt wirklich nicht so kompliziert. Ich klick da drauf und fertig." Sie hat keine Lust, jedes Pixel zu erklären.
- **Bei Zusammenfassungen nicht alles bestätigen.** Nicht einfach "Ja" zu allem sagen. Wenn etwas stimmt: "Ja, passt." Wenn etwas fast stimmt: "Ja, aber [Korrektur]." Wenn etwas überflüssig ist: "Das ist nicht so wichtig, das kommt eigentlich nie vor." Sie hat eine eigene Meinung darüber was relevant ist.
- **Eigene Prioritäten setzen.** Frau Meier weiß was sie nervt (Abtippen, Hin-und-Her-Wechseln) und bringt das von sich aus ein. Sie wartet nicht darauf, nach Schmerzpunkten gefragt zu werden.
- **Irgendwann ist auch mal gut.** Wenn der Agent nach 20+ Detailfragen immer noch nicht fertig ist: "Hören Sie, ich glaub wir haben jetzt wirklich alles durch. Können wir weitermachen?" Sie hat noch 30 Rechnungen auf dem Tisch.

---

## Prozesswissen: Eingangsrechnungen verbuchen

> **Hinweis:** Dieses Prozesswissen ist die **vollständige Ground Truth** auf RPA-Niveau.
> Frau Meier kennt all diese Details implizit, gibt sie aber erst auf Nachfrage preis.
> Die Ziel-Artefakte (Teil B) werden gegen dieses Wissen verglichen.

### Überblick

Frau Meier verbucht Eingangsrechnungen. Rechnungen kommen per E-Mail (PDF-Anhang), sie liest die Daten ab und tippt sie in das ERP-System (BüroWare) ein. ~30 Rechnungen pro Tag. Pro Rechnung ca. 3-4 Minuten — reine Tipparbeit, kein Denken nötig.

**Das ist der Prozess den EMMA automatisieren soll: Frau Meiers wiederholende Computerarbeit — Daten aus PDF-Rechnungen in BüroWare übertragen.**

### Systeme

| System | Zugang | Funktion |
|--------|--------|----------|
| **Outlook** | Desktop-Client | E-Mail-Eingang, Rechnungen als PDF-Anhang |
| **BüroWare** | Desktop-Programm (Verknüpfung auf Desktop) | ERP-System: Rechnungseingang, Kreditorenbuchhaltung |
| **Windows Explorer** | Standard | PDF-Rechnungen lokal abspeichern |
| **PDF-Viewer** | Adobe Acrobat Reader | Rechnung öffnen und Daten ablesen |

### Der Prozess — Schritt für Schritt

#### Trigger (Start)

Frau Meier öffnet morgens Outlook. Im Posteingang liegen neue E-Mails mit Rechnungen — erkennbar am Betreff (z.B. "Rechnung Nr. 2026-1234" oder "Invoice"). Jede Rechnung hat ein PDF als Anhang.

#### Schleife: Pro Rechnung (wiederholt sich ~30x am Tag)

**Schritt 1: PDF speichern**
1. Frau Meier klickt auf die E-Mail in Outlook
2. Rechtsklick auf den PDF-Anhang → "Speichern unter"
3. Speichert in: `S:\Buchhaltung\Rechnungseingang\2026\03\`
4. Dateiname: lässt den Original-Dateinamen (z.B. "RE-2026-1234.pdf")
5. Klickt "Speichern"

**Schritt 2: PDF öffnen und Daten ablesen**
1. Doppelklick auf die gespeicherte PDF → öffnet sich in Adobe Acrobat Reader
2. Frau Meier liest folgende Daten ab:
   - **Lieferantenname** (oben auf der Rechnung, z.B. "Grohe GmbH")
   - **Rechnungsnummer** (z.B. "RE-2026-1234")
   - **Rechnungsdatum** (z.B. "15.03.2026")
   - **Nettobetrag** (z.B. "1.250,00 €")
   - **MwSt.-Betrag** (z.B. "237,50 €")
   - **Bruttobetrag** (z.B. "1.487,50 €")
   - **Zahlungsziel** (z.B. "30 Tage netto" oder konkretes Datum)
   - **Bankverbindung** des Lieferanten (IBAN)

**Schritt 3: In BüroWare erfassen**
1. Frau Meier wechselt zu BüroWare (Alt+Tab oder Klick in Taskleiste)
2. Menü: **Buchhaltung → Rechnungseingang → Neue Rechnung**
3. **Eingabemaske "Rechnungseingang"** erscheint mit folgenden Feldern:
   - **"Kreditor"** — Suchfeld. Frau Meier tippt die ersten Buchstaben des Lieferanten, Dropdown zeigt Treffer. Klick auf den richtigen.
     - Falls Lieferant NICHT im System: Button "Neuer Kreditor" → Mini-Formular (Name, Adresse, IBAN). Kommt ca. 2x pro Woche vor.
   - **"Rechnungsnr."** — Freitextfeld. Tippt die Nummer ab.
   - **"Rechnungsdatum"** — Datumsfeld (TT.MM.JJJJ).
   - **"Eingangsdatum"** — Datumsfeld, trägt das heutige Datum ein.
   - **"Nettobetrag"** — Zahlenfeld (Dezimal mit Komma).
   - **"MwSt.-Satz"** — Dropdown: "19%", "7%", "0%". Standard ist 19%.
   - **"Bruttobetrag"** — wird automatisch berechnet, read-only. Frau Meier prüft ob es mit der Rechnung übereinstimmt.
   - **"Kostenstelle"** — Dropdown. Frau Meier wählt anhand der Rechnungsart:
     - Material/Werkzeug → "4100 Wareneinkauf"
     - Bürobedarf → "4200 Büro"
     - Fahrzeuge → "4300 Fuhrpark"
     - Im Zweifelsfall: "4900 Sonstiges" und Frau Engel klärt das später.
   - **"Zahlungsziel"** — Datumsfeld. Frau Meier rechnet: Rechnungsdatum + Tage aus Zahlungsbedingung.
   - **"Bemerkungen"** — optionales Freitextfeld. Nutzt sie selten.
4. Klick auf **"Speichern"** → BüroWare zeigt Bestätigung: "Rechnung erfasst. Belegnummer: ER-2026-00456"

**Schritt 4: PDF in BüroWare anhängen**
1. In der gerade gespeicherten Rechnung: Button **"Dokument anhängen"** (Büroklammer-Icon)
2. Datei-Dialog öffnet sich → Frau Meier navigiert zum gespeicherten PDF
3. Wählt die Datei aus → Klick "Öffnen"
4. PDF erscheint als Anhang in der Rechnung (Thumbnail-Vorschau)

**Schritt 5: E-Mail als erledigt markieren**
1. Frau Meier wechselt zurück zu Outlook
2. Verschiebt die E-Mail per Drag & Drop in den Ordner "Verarbeitet" (Unterordner von Posteingang)
3. Nächste E-Mail → zurück zu Schritt 1

#### Ende

Der Prozess ist fertig wenn alle Rechnungs-E-Mails aus dem Posteingang in "Verarbeitet" verschoben sind. Frau Meier sieht: Posteingang enthält keine Rechnungs-E-Mails mehr.

### Entscheidungen

| Stelle | Bedingung | Dann | Sonst |
|--------|-----------|------|-------|
| Kreditor suchen | Lieferant im System gefunden? | Auswählen, weiter | "Neuer Kreditor" anlegen (Name, Adresse, IBAN), dann weiter |
| MwSt.-Satz | Rechnung zeigt 7% oder 0%? | Dropdown ändern | Standard 19% lassen |
| Kostenstelle | Art der Rechnung? | Passende Kostenstelle wählen (4100/4200/4300) | "4900 Sonstiges", Frau Engel klärt |
| Bruttobetrag-Check | Berechneter = Rechnungsbetrag? | Weiter | Frau Meier prüft Eingaben nochmal, korrigiert |

### Ausnahmen

**Gutschrift statt Rechnung (~2x pro Woche):**
- Erkennbar an "Gutschrift" im Betreff oder PDF
- In BüroWare: statt "Neue Rechnung" → **"Neue Gutschrift"** (gleiches Menü, anderer Button)
- Alle Felder gleich, aber Betrag wird als negativ gebucht (BüroWare macht das automatisch)

**Rechnung in Fremdwährung (~1x pro Monat):**
- Kommt vor bei Zulieferer aus Österreich (EUR, kein Problem) oder Schweiz (CHF)
- Bei CHF: Frau Meier öffnet Google, sucht "CHF EUR Kurs", rechnet manuell um
- Trägt den EUR-Betrag in BüroWare ein, schreibt Original-Betrag + Kurs in "Bemerkungen"

**Unleserliches PDF:**
- Selten, aber kommt vor (schlechter Scan)
- Frau Meier schreibt Antwort-E-Mail an den Lieferanten: "Rechnung unleserlich, bitte erneut senden"
- Verschiebt E-Mail in Ordner "Klärung" statt "Verarbeitet"

### Variablen & Daten

| Variable | Typ | Quelle | Ziel |
|----------|-----|--------|------|
| Lieferantenname | Text | PDF-Rechnung | BüroWare Kreditor-Suche |
| Rechnungsnummer | Text | PDF-Rechnung | BüroWare Feld "Rechnungsnr." |
| Rechnungsdatum | Datum (TT.MM.JJJJ) | PDF-Rechnung | BüroWare Feld "Rechnungsdatum" |
| Nettobetrag | Dezimalzahl (€) | PDF-Rechnung | BüroWare Feld "Nettobetrag" |
| MwSt.-Betrag | Dezimalzahl (€) | PDF-Rechnung | Kontrollwert (nicht direkt eingegeben) |
| Bruttobetrag | Dezimalzahl (€) | PDF-Rechnung | Vergleich mit BüroWare-Berechnung |
| MwSt.-Satz | 19% / 7% / 0% | PDF-Rechnung | BüroWare Dropdown |
| Kostenstelle | Code (4100/4200/4300/4900) | Rechnungsart (Frau Meiers Einschätzung) | BüroWare Dropdown |
| Zahlungsziel | Datum | Rechnungsdatum + Zahlungsbedingung | BüroWare Feld "Zahlungsziel" |
| PDF-Dateipfad | Dateipfad | Windows Explorer | BüroWare Dokumentanhang |
| Belegnummer | Text (auto) | BüroWare nach Speichern | Bestätigung |
| IBAN | Text | PDF-Rechnung | Nur bei neuem Kreditor |

## Universelle Reaktionen

| Situation | Frau Meiers Reaktion |
|-----------|---------------------|
| Agent benutzt Fachbegriffe (Parameter, Kontrollfluss, Iteration) | "Können Sie das einfacher sagen? Ich bin Buchhalterin, keine Programmiererin." |
| Agent wiederholt eine schon beantwortete Frage | "Das hab ich doch gerade schon erklärt." |
| Agent fragt etwas Technisches das Frau Meier nicht weiß | "Das weiß ich nicht, da müsste ich unseren IT-Mann fragen." |
| Agent antwortet auf Englisch | "Bitte auf Deutsch." |
| Agent fragt nach "Kontrollfluss" oder "Nachfolger" | "Also nach dem Speichern mach ich das mit dem PDF-Anhängen, und danach die E-Mail verschieben. So meinen Sie das?" |
| Agent zeigt eine Zusammenfassung und fragt ob es passt | "Ja, das stimmt so." ODER "Nee, da fehlt noch was: [Detail]" |
| Agent erkennt ein Spannungsfeld und fragt nach | "Ja, das ist echt nervig. Ich muss immer hin und her wechseln zwischen dem PDF und BüroWare. Copy-Paste geht leider nicht weil BüroWare das nicht unterstützt von externen Programmen." |
| Agent will einen Schritt aufteilen | "Ja, kann man so trennen. Für mich ist das ein Vorgang, aber wenn Sie das getrennt brauchen, klar." |

## Prozesswissen: Vertiefung (Oberflächen, Regeln, Sonderfälle)

### BüroWare-Oberfläche im Detail

**Hauptnavigation:**
- Desktop-Verknüpfung "BüroWare" → Programm startet, Login mit Windows-Anmeldung (automatisch)
- Hauptmenü: Menüleiste oben → **Buchhaltung** → **Rechnungseingang** → **Neue Rechnung** (oder **Neue Gutschrift**)
- Eingabemaske "Rechnungseingang" hat alle Felder untereinander, Tab-Taste springt zum nächsten Feld
- Nach Speichern: BüroWare zeigt Statusleiste unten mit Bestätigung + Belegnummer

**Feldabfolge in der Eingabemaske (exakte Reihenfolge):**
1. **Kreditor** (Suchfeld mit Dropdown-Autocomplete)
2. **Rechnungsnr.** (Freitextfeld)
3. **Rechnungsdatum** (Datumsfeld TT.MM.JJJJ, Kalender-Popup verfügbar)
4. **Eingangsdatum** (Datumsfeld, vorausgefüllt mit Tagesdatum, Frau Meier ändert es nie)
5. **Nettobetrag** (Zahlenfeld, Dezimalkomma)
6. **MwSt.-Satz** (Dropdown: "19%", "7%", "0%")
7. **Bruttobetrag** (read-only, automatisch berechnet)
8. **Kostenstelle** (Dropdown mit 4-stelligen Codes)
9. **Zahlungsziel** (Datumsfeld, manuell berechnet)
10. **Bemerkungen** (optionales Freitextfeld, mehrzeilig)
11. **[Speichern]-Button**

**Button "Dokument anhängen" (Büroklammer-Icon):**
- Erscheint erst NACH dem Speichern der Rechnung
- Öffnet Windows-Dateidialog
- Frau Meier navigiert zum Netzlaufwerk-Ordner der aktuellen Rechnung
- Nur PDF-Dateien auswählbar (Filter im Dialog voreingestellt)
- Nach Anhängen: Thumbnail-Vorschau im unteren Bereich der Rechnung

**Button "Neuer Kreditor":**
- Neben dem Kreditor-Suchfeld, kleiner Button mit Plus-Zeichen
- Öffnet modales Fenster mit Feldern: Firmenname, Straße, PLZ, Ort, IBAN
- Nach Speichern: Neuer Kreditor ist sofort im Suchfeld verfügbar
- Frau Meier liest alle Daten von der Rechnung ab (Kopfbereich des PDFs)

### Kostenstelle-Zuordnung: Exakte Regeln

| Rechnungsart | Kostenstelle | Frau Meiers Erkennung |
|---|---|---|
| Material, Werkzeug, Ersatzteile, Rohre, Fittings | **4100 Wareneinkauf** | Lieferant ist Großhändler (Grohe, Viega, Geberit...) oder Rechnung enthält Artikelnummern |
| Bürobedarf, Papier, Toner, Reinigungsmittel | **4200 Büro** | Lieferant ist Büroausstatter (Staples, Viking...) |
| Fahrzeuge, Tanken, Werkstatt, TÜV | **4300 Fuhrpark** | Lieferant ist Tankstelle, Werkstatt oder Leasinggesellschaft |
| Unklar / passt nicht | **4900 Sonstiges** | Frau Meier kann nicht zuordnen → Frau Engel klärt es später |

**Wichtig:** Frau Meier entscheidet anhand des **Lieferantennamens und des Rechnungsinhalts**, nicht anhand eines formalen Regelwerks. Sie kennt die meisten Lieferanten nach Jahren. Bei unbekannten Lieferanten liest sie die Rechnungspositionen.

**Häufigkeit:** ca. 70% Wareneinkauf (4100), 15% Büro (4200), 10% Fuhrpark (4300), 5% Sonstiges (4900).

### MwSt.-Satz: Entscheidungsregeln

| Satz | Wann | Frau Meiers Vorgehen |
|------|------|---------------------|
| **19%** | Standardfall (~90% aller Rechnungen) | Default im Dropdown, nichts ändern |
| **7%** | Ermäßigter Satz (Lebensmittel für Kantine, Bücher/Zeitschriften) | Steht auf der Rechnung, Frau Meier liest es ab und ändert Dropdown |
| **0%** | Steuerfreie Leistungen, innergemeinschaftliche Lieferungen (EU mit USt-IdNr.) | Selten (~1x/Monat), Frau Meier erkennt es an "steuerfrei" oder "Reverse Charge" auf der Rechnung |

### Bruttobetrag-Prüfung

Frau Meier vergleicht **nach Eingabe von Nettobetrag und MwSt.-Satz** den von BüroWare berechneten Bruttobetrag mit dem Bruttobetrag auf der Rechnung:
- **Stimmt überein** → weiter mit Kostenstelle
- **Weicht ab** → Frau Meier prüft: Hat sie den Nettobetrag richtig abgetippt? Stimmt der MwSt.-Satz? Korrigiert und prüft erneut. In seltenen Fällen hat die Rechnung selbst einen Rundungsfehler — dann trägt sie den Cent-Differenzbetrag in "Bemerkungen" ein.

### Gutschrift-Ablauf im Detail

- **Erkennung:** Wort "Gutschrift" im PDF-Titel oder im E-Mail-Betreff
- **BüroWare:** Buchhaltung → Rechnungseingang → **Neue Gutschrift** (Button direkt neben "Neue Rechnung")
- **Felder:** Identisch zur Rechnung. BüroWare setzt den Betrag automatisch negativ.
- **Rest:** Speichern, PDF anhängen, E-Mail verschieben — alles gleich.
- **Häufigkeit:** ~2x pro Woche. Typische Gründe: Retouren, Preiskorrekturen, Mengenabweichungen.

### Fremdwährungs-Ablauf im Detail

- **Erkennung:** Beträge auf der Rechnung in CHF (oder anderer Nicht-EUR-Währung)
- **Umrechnung:** Frau Meier öffnet neuen Browser-Tab → Google → "CHF EUR Kurs" → Google zeigt aktuellen Wechselkurs. Sie rechnet manuell: Nettobetrag × Kurs = EUR-Nettobetrag. Bruttobetrag × Kurs = EUR-Bruttobetrag.
- **BüroWare:** Trägt den EUR-Betrag ein. Im Feld "Bemerkungen": "Original: [Betrag] CHF, Kurs [Kurs], umgerechnet: [EUR-Betrag] EUR"
- **Häufigkeit:** ~1x pro Monat, fast immer CHF (Schweizer Sanitär-Zulieferer)
- **Quelle des Kurses:** Google-Suche, kein offizielles Treasury-Tool

### Unleserliches PDF: Exakter Ablauf

- **Erkennung:** PDF öffnet sich, aber Inhalt ist nicht lesbar (verschmiert, zu dunkel, beschädigt, falsches Dokument angehängt)
- **Aktion:** Frau Meier klickt in Outlook auf "Antworten" und schreibt: "Guten Tag, die beigefügte Rechnung ist leider nicht lesbar. Könnten Sie diese bitte erneut senden? Vielen Dank."
- **E-Mail verschieben:** In Outlook-Ordner "Klärung" (nicht "Verarbeitet")
- **Nachverfolgung:** Keine systematische — Frau Meier schaut "ab und zu" in den Klärungsordner
- **Häufigkeit:** ~1–2x pro Monat

### Warum dieser Prozess gut für RPA ist
- **Eine Person** (Frau Meier) macht die Arbeit
- **Repetitiv** (~30x/Tag identischer Ablauf)
- **Regelbasiert** (keine kreativen Entscheidungen, nur Zuordnungen)
- **Zwei Systeme** (Outlook → BüroWare), klarer Datenfluss
- **Klarer Start** (E-Mail da) und **klares Ende** (Posteingang leer)
- **Strukturierte Daten** (Rechnungsfelder sind standardisiert)

---

# TEIL B — ZIEL-ARTEFAKTE (Soll-Zustand)

Gegen diese Beschreibungen vergleichst du das Ergebnis.
Formulierungen müssen nicht wörtlich übereinstimmen — es zählt **sinngemäße Abdeckung**.

---

## Ziel-Artefakt: Exploration (7 Slots)

### prozessausloeser
> Neue E-Mail mit Rechnungs-PDF im Outlook-Posteingang. Frau Meier öffnet
> morgens Outlook und sieht die unbearbeiteten Rechnungs-E-Mails.

**Muss enthalten:** E-Mail, PDF, Outlook
**Status:** vollstaendig

### prozessziel
> Alle Rechnungs-E-Mails verarbeitet: Daten in BüroWare erfasst, PDF angehängt,
> E-Mail in "Verarbeitet" verschoben. Posteingang enthält keine Rechnungs-Mails mehr.

**Muss enthalten:** BüroWare, erfasst/verbucht, E-Mail verschoben/erledigt
**Status:** vollstaendig

### prozessbeschreibung
> 1. PDF-Anhang aus Outlook speichern (Netzlaufwerk).
> 2. PDF öffnen, Rechnungsdaten ablesen (Lieferant, Nr., Datum, Beträge, MwSt., Zahlungsziel).
> 3. BüroWare öffnen → Buchhaltung → Rechnungseingang → Neue Rechnung.
> 4. Kreditor suchen (ggf. neu anlegen). Rechnungsdaten eintippen.
> 5. Kostenstelle wählen (4100/4200/4300/4900 je nach Rechnungsart).
> 6. Speichern → Belegnummer erhalten.
> 7. PDF in BüroWare anhängen (Büroklammer-Icon).
> 8. Zurück zu Outlook, E-Mail in "Verarbeitet" verschieben.
> Wiederholung: ~30x pro Tag.

**Muss enthalten:** PDF speichern, Daten ablesen, BüroWare eintippen, Kreditor, Kostenstelle, PDF anhängen, E-Mail verschieben
**Status:** vollstaendig

### entscheidungen_und_schleifen
> ENTSCHEIDUNG: Kreditor vorhanden — ja: auswählen, nein: neu anlegen.
> ENTSCHEIDUNG: MwSt.-Satz — 19% (Standard), 7%, oder 0%.
> ENTSCHEIDUNG: Kostenstelle — je nach Rechnungsart (Material/Büro/Fuhrpark/Sonstiges).
> ENTSCHEIDUNG: Bruttobetrag-Check — stimmt Berechnung mit Rechnung überein?
> SCHLEIFE: Jede Rechnungs-E-Mail wird einzeln abgearbeitet (~30/Tag).

**Muss enthalten:** mindestens 2 Entscheidungen (Kreditor, Kostenstelle), 1 Schleife
**Status:** vollstaendig

### beteiligte_systeme
> Outlook (Desktop-Client, E-Mail-Eingang), BüroWare (Desktop-Programm, ERP,
> Rechnungseingang/Kreditorenbuchhaltung), Adobe Acrobat Reader (PDF anzeigen),
> Windows Explorer (Dateien speichern).

**Muss enthalten:** Outlook, BüroWare, PDF-Viewer
**Status:** vollstaendig

### variablen_und_daten
> Lieferantenname — Text, aus PDF, für Kreditor-Suche.
> Rechnungsnummer — Text, aus PDF.
> Rechnungsdatum — Datum, aus PDF.
> Nettobetrag — Dezimal (€), aus PDF.
> MwSt.-Satz — 19%/7%/0%, aus PDF.
> Bruttobetrag — Dezimal (€), aus PDF, Vergleichswert.
> Kostenstelle — Code, aus Rechnungsart (Frau Meiers Zuordnung).
> Zahlungsziel — Datum, berechnet aus Rechnungsdatum + Zahlungsbedingung.

**Muss enthalten:** mindestens 4 Variablen
**Status:** vollstaendig

### prozesszusammenfassung
> Frau Meier (Sachbearbeiterin Buchhaltung) verbucht täglich ~30 Eingangsrechnungen.
> Die Rechnungen kommen als PDF per E-Mail in Outlook. Sie speichert das PDF,
> liest die Rechnungsdaten ab und tippt sie in BüroWare ein (Rechnungseingang →
> Neue Rechnung). Nach dem Speichern hängt sie das PDF in BüroWare an und
> verschiebt die E-Mail in den Ordner "Verarbeitet".

**Muss enthalten:** Frau Meier, E-Mail/PDF, BüroWare, eintippen/übertragen
**Status:** vollstaendig

### Dinge die NICHT im Artefakt stehen dürfen (Halluzinationen)
OCR, KI-gestützt, automatische Belegerkennung, API, REST, Datenbankzugriff,
Machine Learning, SAP, DATEV

---

## Ziel-Artefakte: Strukturierung

### Phasenübergang: Was zwischen Exploration und Strukturierung passiert

```
1. Explorer meldet phase_complete
2. Moderator wird aktiviert, fasst zusammen, fragt: "Sollen wir zur Strukturierung?"
3. User bestätigt → Moderator setzt advance_phase Flag
4. Orchestrator: Phase wechselt auf "strukturierung"
5. InitStructuringMode läuft im Hintergrund (für User unsichtbar):
   a. Ein LLM-Call transformiert ExplorationArtifact → vorläufiges StructureArtifact
   b. Python-Validator prüft referenzielle Integrität (R-1)
   c. LLM-CoverageValidator prüft auf fehlende Entitäten
   d. Optional: Korrektur-Call bei kritischen Befunden
   e. Warnings → working_memory.init_hinweise
6. StructuringMode wird aktiviert, User sieht erstes Strukturierungsdialog-Turn
   mit vorausgefülltem Artefakt und ggf. Hinweisen aus der Initialisierung
```

### Erwartete Lücken im Init-Artefakt (vom Dialog zu füllen)

| Lücke | Beispiel bei Frau Meier |
|-------|------------------------|
| **Feldlevel-Details** fehlen | Init weiß "Daten eintippen in BüroWare" aber nicht welche Felder in welcher Reihenfolge |
| **Entscheidungsregeln** unscharf | Init weiß "Kostenstelle wählen" aber nicht die 4100/4200/4300/4900-Zuordnung |
| **Sonderfälle** dünn beschrieben | Init weiß "Gutschrift kommt vor" aber nicht den exakten Ablauf |
| **Spannungsfelder** nicht erkannt | Init sieht "PDF und BüroWare" aber erkennt nicht den Medienbruch |
| **Unsicherheiten** aus Init | "Kommentar Initialisierung: Unklar ob Bruttobetrag-Prüfung automatisch" |

### Themen die im Strukturierungsdialog abgedeckt werden müssen

| Thema | Erwartete Artefakt-Änderung |
|-------|----------------------------|
| **Gutschrift-Erkennung** | Entscheidungsschritt vollständig beschrieben (Menüpunkt, Felder, negativer Betrag) |
| **BüroWare-Feldabfolge** | Alle 9 Felder mit Reihenfolge und Feldtypen in Beschreibung |
| **Kostenstelle-Zuordnung** | 4 Kategorien mit Erkennungsmerkmalen und Häufigkeiten |
| **MwSt.-Satz-Regeln** | 19%/7%/0% mit Erkennungsmerkmalen |
| **Bruttobetrag-Prüfung** | Als Prüfschritt in Beschreibung ergänzt |
| **PDF-Speicherort** | Netzlaufwerk-Pfad und Dateibenennungskonvention |
| **PDF-Anhängen in BüroWare** | Büroklammer-Icon, Dateidialog, Thumbnail-Vorschau |
| **Neukreditor-Details** | Plus-Button, modales Fenster, Felder: Name/Adresse/IBAN |
| **Spannungsfeld Medienbruch** | spannungsfeld-Feld am Eintippschritt |

## Ziel-Artefakt: Strukturartefakt nach Init (vorläufig)

> **Hinweis:** Dies zeigt was InitStructuringMode aus dem Explorationsartefakt generieren sollte — BEVOR der Dialog beginnt. Einige Beschreibungen sind dünn, Unsicherheiten mit "Kommentar Initialisierung:" markiert. completeness_status spiegelt wider ob die Beschreibung für eine Spezifikation ausreicht.

**prozesszusammenfassung:** Frau Meier (Buchhaltung, Riedel Haustechnik GmbH) verbucht täglich ca. 30 Eingangsrechnungen. Rechnungen kommen als PDF-Anhang per E-Mail in Outlook. Sie speichert das PDF, liest die Daten ab und erfasst sie in BüroWare (ERP-System). Nach dem Speichern hängt sie das PDF an und verschiebt die E-Mail in den Ordner "Verarbeitet".

**s1** — Rechnungs-E-Mail in Outlook auswählen [aktion, reihenfolge 1, → s2, completeness_status: vollstaendig]
"Frau Meier öffnet den Posteingang in Outlook (Desktop-Client) und wählt die älteste ungelesene E-Mail mit Rechnungs-PDF-Anhang. Erkennbar am Betreff (z.B. 'Rechnung Nr. 2026-1234'). Pro Tag ca. 30 Rechnungs-E-Mails."

**s2** — PDF-Anhang speichern [aktion, reihenfolge 2, → s3, completeness_status: teilweise]
"Frau Meier speichert den PDF-Anhang der E-Mail auf dem Netzlaufwerk. Kommentar Initialisierung: Genauer Speicherpfad und Dateibenennungskonvention aus Exploration nicht ersichtlich."

**s3** — PDF öffnen und Rechnungsdaten ablesen [aktion, reihenfolge 3, → s4, completeness_status: vollstaendig]
"Frau Meier öffnet das gespeicherte PDF in Adobe Acrobat Reader (Doppelklick). Sie liest ab: Lieferantenname, Rechnungsnummer, Rechnungsdatum, Nettobetrag, MwSt.-Betrag, Bruttobetrag, Zahlungsziel, ggf. IBAN des Lieferanten. Außerdem stellt sie fest, ob es sich um eine Gutschrift handelt."

**s4** — Rechnung oder Gutschrift? [entscheidung, reihenfolge 4, bedingung: "Ist das Dokument als Gutschrift gekennzeichnet?", Ja → s4a, Nein → s5, konvergenz: s8, completeness_status: teilweise]
"Frau Meier prüft ob das PDF-Dokument eine Gutschrift ist. Gutschriften kommen ca. 2x pro Woche vor. Kommentar Initialisierung: Unklar woran genau eine Gutschrift erkannt wird (Titel, Betreff, Vermerk auf dem Beleg?)."

**s4a** — Gutschrift in BüroWare erfassen [aktion, reihenfolge 5, → s8, completeness_status: teilweise]
"Gutschriften werden über einen anderen Menüpunkt in BüroWare erfasst (nicht 'Neue Rechnung'). Betrag wird automatisch negativ gebucht. Kommentar Initialisierung: Unklar ob die Eingabefelder identisch zur Rechnungseingabe sind. Unklar ob der Kreditor-Suchschritt auch bei Gutschriften nötig ist."

**s5** — Kreditor in BüroWare vorhanden? [entscheidung, reihenfolge 6, bedingung: "Wird der Lieferant im BüroWare-Kreditor-Suchfeld gefunden?", Ja → s6, Nein → s5a, konvergenz: s6, completeness_status: teilweise]
"Frau Meier wechselt zu BüroWare und öffnet Buchhaltung → Rechnungseingang → Neue Rechnung. Im Feld 'Kreditor' sucht sie nach dem Lieferantennamen. Kommentar Initialisierung: Unklar ob die Suche über Autocomplete-Dropdown funktioniert oder ein separates Suchfenster hat."

**s5a** — Neuen Kreditor anlegen [aktion, reihenfolge 7, → s6, completeness_status: teilweise]
"Frau Meier legt einen neuen Kreditor in BüroWare an mit Name, Adresse und IBAN. Kommt ca. 2x pro Woche vor. Kommentar Initialisierung: Unklar ob das ein separates Formular ist oder in der Rechnungsmaske integriert."

**s6** — Rechnungsdaten in BüroWare eintippen [aktion, reihenfolge 8, → s7, completeness_status: teilweise]
"Frau Meier tippt die Rechnungsdaten in die Eingabemaske: Rechnungsnummer, Rechnungsdatum, Nettobetrag, MwSt.-Satz (19%/7%/0%), Kostenstelle, Zahlungsziel. Der Bruttobetrag wird automatisch berechnet — Frau Meier prüft ob er mit der Rechnung übereinstimmt. Speichern → Belegnummer wird vergeben. Kommentar Initialisierung: Unklar nach welchen Regeln die Kostenstelle zugeordnet wird. Unklar ob es ein Eingangsdatum-Feld gibt."
spannungsfeld: "Frau Meier muss alle Rechnungsdaten manuell vom PDF-Bildschirm in BüroWare abtippen — reiner Medienbruch, kein automatischer Import."

**s7** — PDF in BüroWare anhängen [aktion, reihenfolge 9, → s8, completeness_status: teilweise]
"Nach dem Speichern hängt Frau Meier das zuvor gespeicherte PDF als Beleg in BüroWare an. Kommentar Initialisierung: Unklar über welche Funktion (Menü, Button, Drag&Drop) das Anhängen erfolgt."

**s8** — E-Mail als erledigt markieren [aktion, reihenfolge 10, → [], completeness_status: vollstaendig]
"Frau Meier wechselt zurück zu Outlook und verschiebt die bearbeitete E-Mail per Drag & Drop in den Ordner 'Verarbeitet' (Unterordner im Posteingang). Der Prozess wiederholt sich für die nächste E-Mail."

**s_err_fremd** — Rechnung in Fremdwährung [ausnahme, reihenfolge 99, → [], completeness_status: teilweise]
ausnahme_beschreibung: "Rechnung in Fremdwährung (typisch CHF). Kommt ca. 1x pro Monat vor."
"Frau Meier rechnet den Betrag manuell in EUR um und trägt den umgerechneten Betrag ein. Kommentar Initialisierung: Unklar woher der Wechselkurs stammt und wie er dokumentiert wird."

**s_err_pdf** — Unleserliches PDF [ausnahme, reihenfolge 100, → [], completeness_status: vollstaendig]
ausnahme_beschreibung: "PDF-Anhang ist unleserlich (schlechter Scan, beschädigte Datei). Selten."
"Frau Meier schreibt dem Lieferanten eine Antwort-E-Mail mit der Bitte um erneute Zusendung. Die E-Mail wird in den Outlook-Ordner 'Klärung' verschoben."

### Erwartete Init-Hinweise (init_hinweise)

Typische Warnings die der CoverageValidator melden sollte:
- "Kostenstelle-Zuordnungsregeln nicht dokumentiert — im Dialog klären"
- "Gutschrift-Ablauf dünn beschrieben — Erkennungsmerkmale und genauen BüroWare-Menüpunkt im Dialog klären"
- "Speicherpfad-Konvention unklar"

### Was im Init NICHT enthalten sein darf (Halluzinationen)
- OCR, automatische Belegerkennung, Scanner
- SAP, DATEV (falsches System — richtig ist BüroWare)
- Schritte die in der Exploration nie erwähnt wurden (z.B. "Rechnung drucken", "Vorgesetzte informieren")
- API-Schnittstellen, automatischer Import

---

## Ziel-Artefakt: Strukturartefakt nach Dialog (final)

> **Hinweis:** Dies ist das Soll-Artefakt am **Ende** der Strukturierungsphase. Alle Unsicherheiten aufgelöst, alle Beschreibungen spezifikationsreif, alle completeness_status: vollstaendig.

**prozesszusammenfassung:** Frau Meier (Sachbearbeiterin Buchhaltung, Riedel Haustechnik GmbH) verbucht täglich ca. 30 Eingangsrechnungen, die als PDF-Anhang per E-Mail in Outlook eintreffen. Pro Rechnung: PDF auf Netzlaufwerk speichern, Daten in Adobe Reader ablesen, Rechnung/Gutschrift-Unterscheidung, in BüroWare erfassen (Kreditorenzuordnung, Rechnungsdaten, MwSt.-Satz, Kostenstelle nach Rechnungsart, Zahlungsziel), Bruttobetrag-Gegenprüfung, PDF als Beleg anhängen, E-Mail in "Verarbeitet" verschieben. Bei neuen Lieferanten wird ein Kreditor angelegt (~2x/Woche), Gutschriften werden über separaten Menüpunkt erfasst (~2x/Woche).

**s1** — Rechnungs-E-Mail in Outlook auswählen [aktion, reihenfolge 1, → s2, completeness_status: vollstaendig]
"Frau Meier öffnet den Posteingang in Outlook (Desktop-Client). Sie wählt die älteste ungelesene E-Mail, die eine Rechnung als PDF-Anhang enthält. Rechnungs-E-Mails sind am Betreff erkennbar (z.B. 'Rechnung Nr. 2026-1234' oder 'Invoice'). Pro Tag liegen ca. 30 Rechnungs-E-Mails im Posteingang."

**s2** — PDF-Anhang auf Netzlaufwerk speichern [aktion, reihenfolge 2, → s3, completeness_status: vollstaendig]
"Frau Meier macht einen Rechtsklick auf den PDF-Anhang der E-Mail und wählt 'Speichern unter'. Zielordner: S:\Buchhaltung\Rechnungseingang\[Jahr]\[Monat]\ (z.B. S:\Buchhaltung\Rechnungseingang\2026\03\). Sie behält den Original-Dateinamen bei (z.B. 'RE-2026-1234.pdf') und klickt 'Speichern'."

**s3** — PDF öffnen und Rechnungsdaten ablesen [aktion, reihenfolge 3, → s4, completeness_status: vollstaendig]
"Frau Meier macht einen Doppelklick auf die gespeicherte PDF-Datei, die sich in Adobe Acrobat Reader öffnet. Sie liest ab: Lieferantenname (Kopfbereich), Rechnungsnummer, Rechnungsdatum, Nettobetrag, MwSt.-Betrag, MwSt.-Satz (19%, 7% oder 0%), Bruttobetrag, Zahlungsziel (z.B. '30 Tage netto'), und bei unbekannten Lieferanten die IBAN. Außerdem stellt sie fest, ob das Dokument als 'Gutschrift' gekennzeichnet ist."

**s4** — Rechnung oder Gutschrift? [entscheidung, reihenfolge 4, bedingung: "Ist das Dokument als Gutschrift gekennzeichnet (Wort 'Gutschrift' im Titel oder auf dem Beleg)?", Ja → s4a, Nein → s5, konvergenz: s8, completeness_status: vollstaendig]
"Frau Meier prüft anhand des PDF-Dokuments, ob es sich um eine Gutschrift handelt. Erkennungsmerkmale: Das Wort 'Gutschrift' im Dokumenttitel, im E-Mail-Betreff, oder als Vermerk auf dem Beleg. Gutschriften kommen ca. 2x pro Woche vor, typisch bei Retouren oder Preiskorrekturen."

**s4a** — Gutschrift in BüroWare erfassen [aktion, reihenfolge 5, → s8, completeness_status: vollstaendig]
"Frau Meier wechselt zu BüroWare und navigiert zu Buchhaltung → Rechnungseingang → Neue Gutschrift (Button direkt neben 'Neue Rechnung'). Die Eingabemaske ist identisch zur Rechnungseingabe (Kreditor, Gutschriftnummer, Datum, Nettobetrag, MwSt.-Satz, Kostenstelle, Zahlungsziel), aber BüroWare bucht den Betrag automatisch als negativen Wert. Speichern → Belegnummer wird vergeben. Danach PDF anhängen (wie bei Rechnung)."

**s5** — Kreditor in BüroWare vorhanden? [entscheidung, reihenfolge 6, bedingung: "Wird der Lieferant im BüroWare-Kreditor-Suchfeld gefunden?", Ja → s6, Nein → s5a, konvergenz: s6, completeness_status: vollstaendig]
"Frau Meier wechselt zu BüroWare (Alt+Tab) und öffnet: Buchhaltung → Rechnungseingang → Neue Rechnung. Im Feld 'Kreditor' tippt sie die ersten Buchstaben des Lieferantennamens. BüroWare zeigt ein Dropdown mit passenden Treffern. Wenn der richtige Lieferant erscheint, klickt sie darauf. Wenn kein Treffer: Der Lieferant muss erst angelegt werden."

**s5a** — Neuen Kreditor anlegen [aktion, reihenfolge 7, → s6, completeness_status: vollstaendig]
"Frau Meier klickt neben dem Kreditor-Suchfeld auf den Button 'Neuer Kreditor' (Plus-Zeichen). Ein modales Mini-Formular öffnet sich mit den Feldern: Firmenname, Straße, PLZ, Ort, IBAN. Alle Daten liest sie vom PDF ab (Lieferanten-Kopfbereich). Nach Klick auf 'Speichern' ist der neue Kreditor sofort im Suchfeld verfügbar. Kommt ca. 2x pro Woche vor."

**s6** — Rechnungsdaten in BüroWare eintippen und speichern [aktion, reihenfolge 8, → s7, completeness_status: vollstaendig]
"In der Eingabemaske 'Rechnungseingang' füllt Frau Meier per Tab-Taste die Felder in folgender Reihenfolge:
(1) 'Rechnungsnr.' — Freitextfeld, tippt Nummer vom PDF ab.
(2) 'Rechnungsdatum' — Datumsfeld TT.MM.JJJJ.
(3) 'Eingangsdatum' — vorausgefüllt mit Tagesdatum, wird nicht geändert.
(4) 'Nettobetrag' — Zahlenfeld, Dezimal mit Komma (z.B. 1.250,00).
(5) 'MwSt.-Satz' — Dropdown: '19%' (Standard, ~90%), '7%' (ermäßigt: Lebensmittel, Bücher, ~8%), '0%' (steuerfrei/Reverse Charge, ~2%). Frau Meier liest den Satz von der Rechnung ab.
(6) 'Bruttobetrag' — read-only, von BüroWare berechnet. Frau Meier vergleicht mit dem Bruttobetrag auf der Rechnung. Bei Abweichung: prüft Netto und MwSt.-Satz, korrigiert, prüft erneut.
(7) 'Kostenstelle' — Dropdown: 4100 Wareneinkauf (Material/Werkzeug, ~70%), 4200 Büro (Bürobedarf, ~15%), 4300 Fuhrpark (Fahrzeuge/Tanken, ~10%), 4900 Sonstiges (unklar → Frau Engel klärt, ~5%). Zuordnung anhand Lieferantenname und Rechnungsinhalt.
(8) 'Zahlungsziel' — Datumsfeld, Frau Meier rechnet: Rechnungsdatum + Zahlungsfrist (z.B. 30 Tage).
(9) 'Bemerkungen' — optional, selten genutzt (nur bei Fremdwährung oder Besonderheiten).
Klick auf 'Speichern' → Statusleiste zeigt: 'Rechnung erfasst. Belegnummer: ER-2026-00456'."
spannungsfeld: "Frau Meier muss alle Rechnungsdaten manuell vom PDF (Adobe Reader) in BüroWare abtippen. Kein Copy-Paste möglich, da BüroWare keine Datenübernahme aus externen Programmen unterstützt. Bei 30 Rechnungen täglich erheblicher Zeitaufwand durch reines Abtippen."

**s7** — PDF in BüroWare anhängen [aktion, reihenfolge 9, → s8, completeness_status: vollstaendig]
"In der gerade gespeicherten Rechnung klickt Frau Meier auf den Button 'Dokument anhängen' (Büroklammer-Icon). Ein Windows-Dateidialog öffnet sich (nur PDF-Dateien sichtbar). Sie navigiert zum Netzlaufwerk S:\Buchhaltung\Rechnungseingang\[Jahr]\[Monat]\ und wählt die zuvor gespeicherte PDF-Datei. Klick 'Öffnen' → PDF erscheint als Anhang mit Thumbnail-Vorschau im unteren Bereich der Rechnung."

**s8** — E-Mail in Outlook als erledigt markieren [aktion, reihenfolge 10, → [], completeness_status: vollstaendig]
"Frau Meier wechselt zurück zu Outlook und verschiebt die bearbeitete E-Mail per Drag & Drop in den Unterordner 'Verarbeitet' (unter Posteingang). Dann wählt sie die nächste Rechnungs-E-Mail. Der Gesamtprozess ist abgeschlossen wenn keine Rechnungs-E-Mails mehr im Posteingang liegen."

**s_err_pdf** — Unleserliches PDF [ausnahme, reihenfolge 99, → [], completeness_status: vollstaendig]
ausnahme_beschreibung: "PDF-Anhang ist unleserlich (schlechter Scan, beschädigte Datei, falsches Dokument). Tritt selten auf (~1–2x pro Monat), kann in Schritt s3 erkannt werden."
"Frau Meier klickt in Outlook auf 'Antworten' und schreibt eine Standardnachricht: 'Guten Tag, die beigefügte Rechnung ist leider nicht lesbar. Könnten Sie diese bitte erneut senden? Vielen Dank.' Sie verschiebt die E-Mail in den Outlook-Ordner 'Klärung' (statt 'Verarbeitet'). Keine systematische Nachverfolgung — Frau Meier schaut gelegentlich in den Klärungsordner."

**s_err_fremd** — Rechnung in Fremdwährung [ausnahme, reihenfolge 100, → [], completeness_status: vollstaendig]
ausnahme_beschreibung: "Rechnung in Nicht-EUR-Währung (fast immer CHF von Schweizer Sanitär-Zulieferern). Kommt ca. 1x pro Monat vor. Kann in Schritt s3 beim Ablesen der Rechnungsdaten erkannt werden."
"Frau Meier öffnet einen neuen Browser-Tab, sucht bei Google 'CHF EUR Kurs' und liest den aktuellen Wechselkurs ab. Sie rechnet manuell um: Nettobetrag × Kurs = EUR-Nettobetrag. In BüroWare trägt sie den umgerechneten EUR-Betrag ein. Im Feld 'Bemerkungen' dokumentiert sie: 'Original: 1.500,00 CHF, Kurs 0,95 = 1.425,00 EUR'. Rest des Ablaufs wie bei normaler Rechnung."

### Prüfkriterien: Init-Artefakt vs. Final-Artefakt

| Kriterium | Init | Final |
|-----------|------|-------|
| Anzahl Schritte (regulär) | 10 (s1–s8 + s4a + s5a) | 10 (s1–s8 + s4a + s5a) |
| Anzahl Ausnahmen | 2 (s_err_fremd, s_err_pdf) | 2 (s_err_pdf, s_err_fremd) |
| Entscheidungsschritte | 2 (Gutschrift + Kreditor), aber dünn | 2 (Gutschrift + Kreditor), voll detailliert |
| completeness_status: vollstaendig | ~40% (s1, s3, s8, s_err_pdf) | 100% |
| "Kommentar Initialisierung:" | 5–6 Stück | 0 |
| Felder in s6 (BüroWare-Eintippen) | Grob ("Rechnungsdaten eintippen") | Alle 9 Felder mit Reihenfolge und Feldtypen |
| Kostenstelle-Regeln | "Kostenstelle wählen" | 4 Kategorien mit Erkennungsmerkmalen und Häufigkeiten |
| spannungsfeld | 1 (Medienbruch, bereits von Init erkannt) | 1 (Medienbruch, detaillierter) |
| Gutschrift | Als Entscheidung im Hauptfluss (prompt-konform), aber Beschreibung dünn | Als Entscheidung s4, vollständig mit Menüpunkt, Feldern, negativem Betrag |

**Hinweis: Abdeckungslimit dieses Testprozesses.** Frau Meiers Prozess enthält keine `regeln`-Entscheidung (≥3 Ausgänge) und keine `schleife` (keine Mehrfachpositionen pro Rechnung). Diese Typen werden durch die Prompt-Beispiele (init_structuring: Versandart mit 3 Regeln, Bestellpositionen als Schleife; structuring: Freigabestufen, Rechnungspositionen kontieren) abgedeckt, aber nicht durch diesen E2E-Testfall. Für vollständige Typ-Abdeckung müsste ein zweiter Testprozess herangezogen werden (z.B. Angebotsanfragen oder Reklamationen).

### Dinge die NICHT im Strukturartefakt stehen dürfen (Halluzinationen)
- OCR, automatische Belegerkennung, Scanner, KI-gestützt
- SAP, DATEV (falsches System — richtig ist BüroWare)
- Dreistufige Freigabe, Geschäftsführungsfreigabe (das ist ein anderer Prozess)
- API-Schnittstellen, automatischer Import, Webservices
- Schritte die weder in der Exploration noch im Dialog vorkamen
- Abteilungsleiter, Teamleiter, Kostenstellenverantwortliche (gibt es in diesem Prozess nicht)
