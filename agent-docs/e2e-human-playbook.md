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

### Überblick
~40-50 Abrechnungen pro Monat. Vom Reiseantrag bis zur Erstattung auf dem Gehaltszettel.

### Systeme
| System | Funktion |
|--------|----------|
| **TravelPro** | Neues Reiseportal (seit ~6 Monaten). Anträge, Belegverwaltung, Genehmigung. Nur ~50% nutzen es. URL: travelpro.mueller-logistik.de, Login über Active Directory. |
| **SAP HR** | Verbuchung der Erstattung, Gehaltsabrechnung. Zugang nur Frau Schmidt + Frau Klein (Lohnbuchhaltung). |
| **Outlook** | Kommunikation, Rückfragen, Backup-Benachrichtigungen. |
| **Excel** | Parallelliste von Frau Schmidt (Datum, Name, Betrag, Status). Redundant zu TravelPro, aber Frau Schmidt vertraut den TravelPro-Auswertungen nicht. |
| **Scanner** | Flachbettscanner bei Frau Schmidt. Belege einzeln scannen, benennen nach "Nachname_Datum_Belegtyp.pdf". |

### Prozessablauf (Normalfall)

1. **Reiseantrag stellen**
   - TravelPro: "Neue Reise" klicken → Formular (Reiseziel, Datum von/bis, Reisegrund, geschätzte Kosten, Kostenstelle) → Absenden
   - Papier: Formular ausdrucken (liegt im Intranet), ausfüllen, Teamleiter vorlegen

2. **Genehmigung** (dreistufig)
   - Inland < 500€: nur Teamleiter
   - Inland ≥ 500€ oder Ausland: Teamleiter + Abteilungsleiter
   - Ab 2.000€: zusätzlich Geschäftsführer (selten, meist Messen/Schulungen)
   - **NEU (seit letztem Monat):** Push-Benachrichtigung im Portal (Glockensymbol oben rechts). E-Mail nur noch als Backup nach 2 Tagen ohne Reaktion.
   - **Problem:** Herr Brenner genehmigt grundsätzlich per E-Mail statt im Portal → nicht revisionssicher, Wirtschaftsprüfer hat das angemahnt

3. **Reise durchführen, Belege sammeln**

4. **Abrechnung einreichen**
   - TravelPro: Reise öffnen → "Belege hochladen" → Foto/Scan als PDF/Bild → Betrag, Datum, Ausgabenart (Dropdown: Hotel, Verpflegung, Transport, Taxi, Parkgebühren, Mietwagen, Sonstiges) → "Abrechnung einreichen"
   - Papier: Formular + angetackerte Belege per Hauspost oder in Frau Schmidts Fach

5. **Prüfung durch Frau Schmidt**
   - Öffnet TravelPro, sieht eingereichte Abrechnungen in Liste
   - Prüft jeden Beleg einzeln: Betrag stimmt? Datum im Reisezeitraum? Beleg lesbar? Ausgabenart korrekt? Hotel > 150€/Nacht braucht Begründung
   - Bei Fehlern: "Rückfrage"-Button in TravelPro → automatische E-Mail an Mitarbeiter
   - Mitarbeiter hat 2 Wochen zur Nachreichung, danach Erinnerung, dann Streichung des Postens
   - **Nachbesserungsschleife:** Abrechnung geht zurück, Mitarbeiter korrigiert, reicht neu ein — kann 2-3 Runden dauern

6. **Papier-Workflow** (bei ~50% der Einreicher)
   - Frau Schmidt tippt alles manuell in TravelPro: Name, Reisedaten, jeden Beleg
   - Papierbelege scannen und hochladen
   - Dauert 3x so lang wie Portal-Einreichung

7. **SAP-Verbuchung**
   - Frau Schmidt öffnet SAP HR → Bereich Reisekosten → neuer Erstattungsbeleg
   - Eingabe: Personalnummer, Reisezeitraum, Gesamtbetrag, Kostenarten, Kostenstelle (aus TravelPro)
   - Beleg wird automatisch in nächste Gehaltsabrechnung übernommen
   - Frau Klein (Lohnbuchhaltung) prüft am Monatsende und gibt Zahlungslauf frei

8. **Erstattung über Gehaltsabrechnung**

### Fristen & Regelungen
- Einreichfrist: 4 Wochen nach Reiseende
- Erstattung: spätestens übernächste Gehaltsabrechnung
- Tagessätze nach Bundesreisekostengesetz:
  - Inland: 14€ ab 8h, 28€ ab 24h
  - Ausland: länderspezifisch, jährlich vom Finanzministerium festgelegt
- Belege im Original für Steuer erforderlich

### Ausnahmen & Sonderfälle
- **Privatwagen:** 30 ct/km Pauschale, Fahrtenbuch erforderlich. TravelPro berechnet automatisch. Frau Schmidt prüft Kilometer gegen Google Maps (>10% Abweichung → Rückfrage)
- **Eigenbeleg:** Bei verlorenem Beleg. Formular mit Angabe was/wann/wo bezahlt. Teamleiter-Unterschrift. Max. 50€ pro Posten. Frau Schmidt scannt ein und lädt statt normalem Beleg hoch.
- **Stornierte Reise:** Stornokosten werden trotzdem abgerechnet
- **Auslandsbelege Fremdwährung:** Betrag in Originalwährung eingeben, TravelPro rechnet mit EZB-Tageskurs um. Ohne Kurs: Frau Schmidt nimmt Bundesbank-Website.

### Hauptprobleme (Spannungsfelder)
1. **Papier-Einreicher:** ~50% nutzen TravelPro nicht → doppelte Arbeit für Frau Schmidt
2. **E-Mail-Genehmigung:** Teamleiter (v.a. Herr Brenner) genehmigen per E-Mail statt Portal → nicht revisionssicher
3. **Excel-Parallelliste:** Frau Schmidt trackt alles nochmal in Excel → redundant, Fehlerquelle
4. **Fehlende Belege:** Dauerthema, Nachbesserungsschleifen kosten Zeit

### Beteiligte Rollen
- Reisender Mitarbeiter
- Teamleiter (Genehmigung Stufe 1)
- Abteilungsleiter (Genehmigung Stufe 2)
- Geschäftsführer (Genehmigung Stufe 3)
- Frau Schmidt (Verwaltung — Prüfung, Papier-Erfassung, SAP-Verbuchung)
- Frau Klein (Lohnbuchhaltung — Zahlungslauf-Freigabe)

### Variablen & Daten
Personalnummer, Name des Reisenden, Reiseziel, Reisezeitraum (von/bis), Reisegrund, Kostenstelle, Einzelposten (Betrag, Datum, Ausgabenart/Belegtyp), Tagessatz, Gesamtbetrag, Genehmigungsnummer, ggf. Kilometer, ggf. Währungskurs

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
