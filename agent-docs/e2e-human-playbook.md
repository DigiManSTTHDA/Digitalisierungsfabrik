# E2E Human Validation Playbook

Wissensreferenz für den Live-E2E-Test der Digitalisierungsfabrik.

**Testprozess:** Eingangsrechnungen verbuchen
**Persona:** Frau Meier, Sachbearbeiterin Buchhaltung, Riedel Haustechnik GmbH
**Ziel:** Exploration durchlaufen, Artefakt-Qualität bewerten.

---

## Ablauf (Live-Persona-Modus)

```
Tool stellt Frage → User kopiert Frage zu Claude →
Claude antwortet als Frau Meier → User kopiert Antwort ins Tool
```

1. User startet das Tool, leitet jede Frage/Antwort des Systems an Claude weiter
2. Claude schlüpft in die Persona Frau Meier und gibt eine passende Antwort
3. User kopiert die Antwort ins Tool
4. Nach der Phase: Artefakt mit Ziel-Artefakt (Teil B) vergleichen

**Wichtig:** Claude kennt den Prozess vollständig und antwortet so, dass die Ziel-Artefakte erreichbar sind. Jede Antwort folgt dem Testplan.

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

---

# TEIL A.2 — TESTPLAN

## Phase 1: EXPLORATION

**Ziel:** Alle 7 Slots mit korrekten Inhalten füllen.

**Geplante Gesprächsstrategie:**

| Schritt | Thema | Antwort-Strategie | Erwartetes Systemverhalten |
|---------|-------|-------------------|---------------------------|
| 1 | Vorfrage | "Klar bin ich bereit. Es geht um Rechnungen einbuchen." | Moderator leitet weiter. |
| 2 | Start | "Ich buche Eingangsrechnungen ein. Die kommen per E-Mail als PDF, und ich tippe die Daten in unser System BüroWare. Das mach ich bestimmt 30 Mal am Tag." | Explorer erkennt: eine Person, ein Computerprozess, zwei Systeme. Scoping sollte schnell klar sein. |
| 3 | Wer genau | "Das bin ich, Frau Meier, Sachbearbeiterin Buchhaltung. Meine Kollegin Frau Engel macht eher die Zahlungsläufe und Mahnungen." | Explorer klärt: EMMA soll Frau Meiers Arbeit übernehmen. |
| 4 | Ablauf grob | "Also: E-Mail auf, PDF speichern, PDF öffnen und Daten ablesen, rüber zu BüroWare, alles eintippen, PDF anhängen, E-Mail als erledigt markieren. Nächste E-Mail." | Explorer patcht prozessbeschreibung mit chronologischen Schritten. |
| 5 | BüroWare-Details | Auf Nachfrage: Menü Buchhaltung → Rechnungseingang → Neue Rechnung. Felder: Kreditor (Suche), Rechnungsnr., Datum, Nettobetrag, MwSt., Kostenstelle, Zahlungsziel. Speichern → Belegnummer. | Explorer vertieft prozessbeschreibung. |
| 6 | Entscheidungen | Auf Nachfrage: Kreditor nicht gefunden → neu anlegen. MwSt. mal 7% statt 19%. Kostenstelle hängt von Rechnungsart ab. Bruttobetrag prüfen. | Explorer füllt entscheidungen_und_schleifen. |
| 7 | Ausnahmen | Auf Nachfrage: Gutschriften (anderer Button, ~2x/Woche). Selten: Fremdwährung (CHF, manuell umrechnen). Unleserliches PDF → Rückfrage an Lieferant. | Explorer ergänzt prozessbeschreibung. |
| 8 | Daten | Aus dem Dialog: Lieferant, Rechnungsnr., Datum, Beträge, MwSt.-Satz, Kostenstelle, Zahlungsziel, PDF-Pfad, IBAN bei Neukreditor. | variablen_und_daten gefüllt. |
| 9 | Ende | "Das war's eigentlich. Wenn keine Rechnungs-Mails mehr im Posteingang sind, bin ich fertig." | Explorer schreibt prozesszusammenfassung, meldet nearing_completion. |
| 10 | Bestätigung | "Ja, das passt so." | phase_complete. |

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

## Universelle Reaktionen

| Situation | Frau Meiers Reaktion |
|-----------|---------------------|
| Agent benutzt Fachbegriffe (Parameter, Kontrollfluss, Iteration) | "Können Sie das einfacher sagen? Ich bin Buchhalterin, keine Programmiererin." |
| Agent wiederholt eine schon beantwortete Frage | "Das hab ich doch gerade schon erklärt." |
| Agent fragt etwas Technisches das Frau Meier nicht weiß | "Das weiß ich nicht, da müsste ich unseren IT-Mann fragen." |
| Agent antwortet auf Englisch | "Bitte auf Deutsch." |

---

## Hinweise

### Warum dieser Prozess gut für RPA ist
- **Eine Person** (Frau Meier) macht die Arbeit
- **Repetitiv** (~30x/Tag identischer Ablauf)
- **Regelbasiert** (keine kreativen Entscheidungen, nur Zuordnungen)
- **Zwei Systeme** (Outlook → BüroWare), klarer Datenfluss
- **Klarer Start** (E-Mail da) und **klares Ende** (Posteingang leer)
- **Strukturierte Daten** (Rechnungsfelder sind standardisiert)
