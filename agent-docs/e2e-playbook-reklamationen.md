# E2E Playbook: Kundenreklamationen bearbeiten

Wissensreferenz für den E2E-Test der Explorationsphase.

**Testprozess:** Kundenreklamationen bearbeiten
**Persona:** Frau Hartmann, Sachbearbeiterin Kundendienst, Bauer Elektrotechnik GmbH
**Ziel:** Exploration durchlaufen, Artefakt-Qualität bewerten.

---

# TEIL A — PERSONA & PROZESSWISSEN

## Persona-Briefing: Frau Hartmann

**Rolle:** Sachbearbeiterin Kundendienst bei der **Bauer Elektrotechnik GmbH** in Stuttgart.
**Unternehmen:** Hersteller von Elektroinstallationsmaterial (Schalter, Steckdosen, Verteiler), 200 Mitarbeiter, B2B-Vertrieb an Elektriker und Großhändler.
**Team:** 3 Personen im Kundendienst, plus Teamleiter Herr Fuchs.

**Charakter:**
- Gründlich und strukturiert, erklärt gerne ausführlich
- Kennt die Sonderfälle gut, bringt sie proaktiv ein
- Leicht frustriert über das alte Ticketsystem ("das ist so umständlich")
- Spricht in ganzen Sätzen, benutzt gerne Beispiele
- Kein IT-Wissen, aber versierter System-Anwender

**Typische Formulierungen:**
- "Also das läuft so: ..."
- "Da muss ich Ihnen ein Beispiel geben..."
- "Das ist ein bisschen umständlich, aber..."
- "Das entscheide ich je nachdem..."
- "Da gibt's eine klare Regel: ..."

---

## Prozesswissen: Kundenreklamationen bearbeiten

> **Hinweis:** Vollständige Ground Truth auf RPA-Niveau.

### Überblick

Frau Hartmann bearbeitet Kundenreklamationen. Kunden (B2B — Elektroinstallateure und Großhändler) melden sich per E-Mail oder über das Webportal. Sie prüft die Reklamation, entscheidet über die Lösung (Ersatzlieferung, Gutschrift, Reparatur oder Ablehnung), erfasst alles im Ticketsystem und im ERP, und kommuniziert mit dem Kunden. ~12 Reklamationen pro Tag, ca. 10-15 Minuten pro Fall.

**EMMA automatisiert Frau Hartmanns Computerarbeit — die Datenerfassung und Systemaktualisierung, nicht die fachliche Entscheidung (die trifft Frau Hartmann weiterhin).**

### Systeme

| System | Zugang | Funktion |
|--------|--------|----------|
| **Outlook** | Desktop-Client | E-Mail-Kommunikation mit Kunden |
| **ServiceDesk** | Web-Anwendung (Browser, Firefox) | Ticketsystem: Reklamations-Tickets erfassen, bearbeiten, abschließen |
| **proALPHA** | Desktop-Programm (Terminalserver, Citrix) | ERP-System: Kundenaufträge, Lieferscheine, Gutschriften, Retouren |
| **Excel** | Desktop (lokal) | Reklamationsstatistik (monatliche Auswertung, Pflege der Liste) |

### Der Prozess — Schritt für Schritt

#### Trigger (Start)

Frau Hartmann öffnet morgens Firefox und prüft im ServiceDesk die Ticketliste: Filter "Neue Tickets" zeigt offene Reklamationen. Parallel prüft sie in Outlook, ob Reklamationen direkt per Mail kamen (Betreff enthält "Reklamation", "Beschwerde", "Mangel" o.ä.). Für E-Mail-Reklamationen erstellt sie manuell ein Ticket im ServiceDesk.

#### Schleife: Pro Reklamation (~12x am Tag)

**Schritt 1: Ticket öffnen oder erstellen**
- Wenn Ticket aus Webportal: Im ServiceDesk auf das Ticket klicken, Details lesen (Kundennummer, Artikelnummer, Menge, Fehlerbeschreibung, ggf. Fotos).
- Wenn E-Mail-Reklamation: Im ServiceDesk "Neues Ticket" klicken, Felder ausfüllen: Kundennummer (aus E-Mail oder Signatur), Betreff, Kategorie ("Produktmangel", "Fehllieferung", "Transportschaden", "Sonstiges"), Priorität (Normal/Hoch), Beschreibung (aus E-Mail kopieren). Anhänge (Fotos) aus der Mail speichern und ans Ticket anhängen.

**Schritt 2: Auftragsdaten in proALPHA prüfen**
1. Frau Hartmann wechselt zu proALPHA (Citrix-Fenster, immer offen)
2. Menü: Vertrieb → Auftragsauskunft → Kundennummer eingeben
3. Letzten relevanten Auftrag suchen (anhand Artikelnummer und Lieferdatum aus der Reklamation)
4. Prüft: Wurde der reklamierte Artikel tatsächlich geliefert? Stimmen Menge und Datum? Ist die Reklamationsfrist (30 Tage ab Lieferung) noch offen?
5. Lieferscheinnummer und Auftragsnummer notieren (auf Papier-Notizblock)

**Schritt 3: Entscheidung treffen**

Frau Hartmann entscheidet basierend auf Kategorie und Prüfung:

| Kategorie | Bedingung | Lösung |
|-----------|-----------|--------|
| Produktmangel | Frist offen, Mangel nachvollziehbar | Ersatzlieferung ODER Gutschrift (Kundenwunsch) |
| Produktmangel | Frist abgelaufen | Kulanz: bis 500€ Warenwert → Gutschrift 50%. Über 500€ → Eskalation an Herr Fuchs |
| Fehllieferung | Falscher Artikel geliefert | Retoure + Ersatzlieferung |
| Transportschaden | Schaden dokumentiert (Fotos) | Gutschrift 100% + Schadensfall beim Spediteur eröffnen |
| Transportschaden | Kein Foto/Nachweis | Ablehnung mit Hinweis auf Dokumentationspflicht |
| Sonstiges | — | Einzelfallentscheidung, im Zweifelsfall Eskalation an Herr Fuchs |

Bei Eskalation: Frau Hartmann schreibt eine interne E-Mail an Herr Fuchs mit Ticket-Nr., Sachverhalt und ihrer Empfehlung. Ticket-Status auf "Warten auf Freigabe" setzen.

**Schritt 4: Lösung im ServiceDesk dokumentieren**
1. Im Ticket: Feld "Lösung" ausfüllen (Freitext: was wurde entschieden und warum)
2. Feld "Lösungstyp" setzen: Dropdown ("Ersatzlieferung", "Gutschrift", "Retoure+Ersatz", "Gutschrift+Schadensfall", "Ablehnung", "Eskalation")
3. Feld "Betrag" bei Gutschrift: Netto-Erstattungsbetrag eintragen
4. Feld "Referenz": Lieferscheinnummer aus proALPHA eintragen
5. Ticket-Status auf "In Bearbeitung" setzen (oder "Warten auf Freigabe" bei Eskalation)

**Schritt 5: Lösung in proALPHA umsetzen**

Abhängig vom Lösungstyp:

*Ersatzlieferung:*
- proALPHA → Vertrieb → Neuer Auftrag → Auftragsart "Ersatzlieferung"
- Kundennummer, Artikelnummer, Menge aus dem Ticket übernehmen
- Feld "Bezug": Ticketnummer eintragen
- Speichern → proALPHA erzeugt Auftragsnummer

*Gutschrift:*
- proALPHA → Buchhaltung → Gutschriften → Neue Gutschrift
- Kundennummer, Betrag, Grund ("Reklamation Ticket-Nr. XYZ")
- Bezugs-Lieferschein auswählen
- Speichern → proALPHA erzeugt Gutschriftsnummer

*Retoure:*
- proALPHA → Lager → Retoureneingang → Neue Retoure
- Kundennummer, Artikelnummer, Menge, Bezugs-Lieferschein
- Speichern → proALPHA erzeugt Retourennummer
- Dann Ersatzlieferung wie oben

*Transportschaden:*
- Gutschrift wie oben
- Zusätzlich: E-Mail an Spedition (Vorlage "Schadensfall") mit Fotos aus dem Ticket

**Schritt 6: Kunden benachrichtigen**
1. In Outlook: Antwort auf die Reklamations-Mail (oder neue Mail an Kunden-E-Mail aus Ticket)
2. Textbaustein je nach Lösungstyp einfügen:
   - "Ersatzlieferung" → Textbaustein mit Auftragsnummer und voraussichtlichem Lieferdatum
   - "Gutschrift" → Textbaustein mit Gutschriftsnummer und Betrag
   - "Ablehnung" → Textbaustein mit Begründung
   - "Eskalation" → Textbaustein "Ihr Anliegen wird von der Teamleitung geprüft"
3. Senden

**Schritt 7: Ticket abschließen und Statistik pflegen**
1. Im ServiceDesk: Ticket-Status auf "Abgeschlossen" (oder "Warten auf Freigabe" bei Eskalation)
2. In der Excel-Datei `S:\Kundendienst\Reklamationsstatistik_2026.xlsx`:
   - Neue Zeile: Datum, Ticketnummer, Kunde, Kategorie, Lösungstyp, Betrag
   - Datei speichern
3. Wenn E-Mail-Reklamation: Mail in Outlook in Ordner "Reklamationen erledigt" verschieben

#### Ende

Der Vorgang ist fertig wenn das Ticket im ServiceDesk abgeschlossen (oder eskaliert) ist, die Aktion in proALPHA angelegt wurde, der Kunde benachrichtigt wurde und die Statistik aktualisiert ist. Tagesende: alle neuen Tickets bearbeitet.

### Entscheidungen

| Stelle | Bedingung | Dann | Sonst |
|--------|-----------|------|-------|
| Ticket-Quelle | Webportal oder E-Mail? | Portal: Ticket öffnen. E-Mail: Ticket manuell anlegen |
| Reklamationsfrist | Innerhalb 30 Tage? | Volle Leistung (Ersatz/Gutschrift 100%) | Kulanzregelung |
| Kulanz | Warenwert ≤500€? | Gutschrift 50% | Eskalation an Herr Fuchs |
| Lösungstyp | Produktmangel? | Ersatzlieferung oder Gutschrift (Kundenwunsch) | Siehe Kategorie-Matrix |
| Lösungstyp | Fehllieferung? | Retoure + Ersatzlieferung | — |
| Lösungstyp | Transportschaden mit Foto? | Gutschrift + Schadensfall Spedition | Ablehnung |
| Eskalation | Sonderfall oder über Grenzwert? | E-Mail an Herr Fuchs, Ticket "Warten auf Freigabe" | Selbst entscheiden |

### Ausnahmen

**Serienreklamation (~1x pro Monat):**
- Mehrere Kunden reklamieren denselben Artikel
- Frau Hartmann erkennt das am Artikel und erstellt zusätzlich ein "Qualitätsticket" im ServiceDesk (Kategorie "Serienreklamation") und informiert die Qualitätssicherung per E-Mail

**Kein Auftrag in proALPHA gefunden (~2x pro Woche):**
- Kunde reklamiert, aber der Auftrag ist nicht auffindbar (falsche Kundennummer, Bestellung über anderen Kanal)
- Frau Hartmann setzt Ticket auf "Warten auf Klärung" und schreibt dem Kunden eine Rückfrage-Mail

**Großkunde mit Sondervereinbarung (~3x pro Woche):**
- Bestimmte Großkunden haben im proALPHA-Kundenstamm eine Notiz "Sondervereinbarung Kulanz" → immer 100% Gutschrift, unabhängig von Frist
- Frau Hartmann prüft das im Kundenstamm unter "Bemerkungen"

### Variablen & Daten

| Variable | Typ | Quelle | Ziel |
|----------|-----|--------|------|
| Kundennummer | Text | E-Mail/Ticket | proALPHA, ServiceDesk |
| Artikelnummer | Text | E-Mail/Ticket | proALPHA Auftragsauskunft |
| Menge | Zahl | E-Mail/Ticket | proALPHA Retoure/Ersatz |
| Fehlerbeschreibung | Freitext | E-Mail/Ticket | ServiceDesk Beschreibung |
| Fotos | Dateien | E-Mail-Anhang/Webportal | ServiceDesk Anhang, Speditions-Mail |
| Kategorie | Auswahl | Frau Hartmanns Einschätzung | ServiceDesk Dropdown |
| Priorität | Normal/Hoch | Kundenwichtigkeit | ServiceDesk |
| Lieferscheinnummer | Text | proALPHA | ServiceDesk Referenz |
| Auftragsnummer | Text | proALPHA | ServiceDesk Referenz |
| Reklamationsfrist | Berechnet | Lieferdatum + 30 Tage | Entscheidung Kulanz |
| Warenwert | Dezimal (€) | proALPHA Auftrag | Entscheidung Kulanzgrenze |
| Lösungstyp | Auswahl | Frau Hartmanns Entscheidung | ServiceDesk, proALPHA |
| Erstattungsbetrag | Dezimal (€) | Berechnung aus Warenwert | proALPHA Gutschrift, ServiceDesk, Excel |
| Gutschriftsnummer | Text (auto) | proALPHA | Kunden-Mail |
| Retourennummer | Text (auto) | proALPHA | intern |
| Ersatz-Auftragsnummer | Text (auto) | proALPHA | Kunden-Mail |
| Ticketnummer | Text (auto) | ServiceDesk | proALPHA Bezugsfeld, Excel |

---

# TEIL B — ZIEL-ARTEFAKTE

## Ziel-Artefakt: Exploration (6 Slots)

### prozessausloeser
> Neue Reklamation: entweder als Ticket im ServiceDesk (Webportal) oder als E-Mail in Outlook. Frau Hartmann prüft morgens beide Quellen. Bei E-Mail-Reklamationen erstellt sie manuell ein Ticket.

**Muss enthalten:** ServiceDesk, Outlook, Ticket
**Status:** vollstaendig

### prozessziel
> Ticket im ServiceDesk abgeschlossen (oder "Warten auf Freigabe" bei Eskalation), Lösung in proALPHA umgesetzt (Ersatzlieferung/Gutschrift/Retoure), Kunde per E-Mail benachrichtigt, Reklamationsstatistik in Excel aktualisiert.

**Muss enthalten:** ServiceDesk, proALPHA, E-Mail, Excel/Statistik
**Status:** vollstaendig

### prozessbeschreibung
> 1. Ticket im ServiceDesk öffnen oder bei E-Mail-Reklamation manuell erstellen.
> 2. Auftragsdaten in proALPHA prüfen (Auftragsauskunft, Lieferschein, Frist).
> 3. Lösung entscheiden: Ersatzlieferung, Gutschrift, Retoure+Ersatz, Ablehnung oder Eskalation — abhängig von Kategorie, Frist und Warenwert.
> 4. Lösung im ServiceDesk dokumentieren (Lösungstyp, Betrag, Referenz).
> 5. Lösung in proALPHA umsetzen (je nach Typ: Ersatzauftrag, Gutschrift, Retoure).
> 6. Kunden per E-Mail aus Outlook benachrichtigen (Textbaustein je nach Lösungstyp).
> 7. Ticket abschließen, Reklamationsstatistik in Excel pflegen.
> Wiederholung: ~12x pro Tag.

**Muss enthalten:** Ticket, proALPHA, Ersatzlieferung, Gutschrift, Retoure, Ablehnung, E-Mail, Excel
**Status:** vollstaendig

### entscheidungen_und_schleifen
> ENTSCHEIDUNG: Ticket-Quelle? Webportal → Ticket öffnen. E-Mail → Ticket manuell erstellen.
> ENTSCHEIDUNG: Reklamationsfrist (30 Tage) offen? Ja → volle Leistung. Nein → Kulanz.
> ENTSCHEIDUNG: Kulanz: Warenwert ≤500€ → Gutschrift 50%. >500€ → Eskalation.
> ENTSCHEIDUNG: Kategorie → Lösungstyp (Produktmangel/Fehllieferung/Transportschaden/Sonstiges).
> ENTSCHEIDUNG: Transportschaden: Fotos vorhanden? Ja → Gutschrift + Schadensfall. Nein → Ablehnung.
> ENTSCHEIDUNG: Sonderfall → Eskalation an Herr Fuchs.
> SCHLEIFE: Jede Reklamation wird einzeln bearbeitet (~12/Tag).

**Muss enthalten:** Reklamationsfrist, Produktmangel, Fehllieferung, Transportschaden, Eskalation, SCHLEIFE
**Status:** vollstaendig

### beteiligte_systeme
> Outlook (E-Mail), ServiceDesk (Ticketsystem, Web/Firefox), proALPHA (ERP, Citrix), Excel (Reklamationsstatistik, Netzlaufwerk).

**Muss enthalten:** Outlook, ServiceDesk, proALPHA, Excel
**Status:** vollstaendig

### variablen_und_daten
> Kundennummer — aus Ticket/Mail, für proALPHA und ServiceDesk.
> Artikelnummer — aus Ticket/Mail, für proALPHA.
> Kategorie — Frau Hartmanns Einschätzung (Produktmangel/Fehllieferung/Transportschaden/Sonstiges).
> Lieferscheinnummer — aus proALPHA, als Referenz im Ticket.
> Lösungstyp — Entscheidung (Ersatzlieferung/Gutschrift/Retoure/Ablehnung/Eskalation).
> Erstattungsbetrag — bei Gutschrift, aus Warenwert berechnet.
> Ticketnummer — von ServiceDesk, für proALPHA-Bezug und Excel.

**Muss enthalten:** Kundennummer, Artikelnummer, Kategorie, Lösungstyp, Ticketnummer
**Status:** vollstaendig

### Dinge die NICHT im Artefakt stehen dürfen (Halluzinationen)
OCR, KI-gestützt, automatische Belegerkennung, API, REST, Datenbankzugriff,
Machine Learning, SAP, BüroWare, Chatbot, automatische Klassifikation

---

## Universelle Reaktionen

| Situation | Frau Hartmanns Reaktion |
|-----------|------------------------|
| Agent benutzt Fachbegriffe | "Können Sie das normaler sagen? Ich bin kein IT-Mensch." |
| Agent wiederholt eine Frage | "Das hab ich gerade eben schon gesagt." |
| Agent fragt etwas Technisches | "Da müssten Sie unsere IT fragen, damit hab ich nichts zu tun." |
| Agent lobt | (ignoriert es) "Also weiter..." |
