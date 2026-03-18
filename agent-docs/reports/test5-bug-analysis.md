# Test5 — Bug-Analyse und Verbesserungsvorschläge

**Datum:** 2026-03-18
**Session:** `add2758b-b9b9-4d09-b544-f045309fc8c6` (Projekt: `test5`)
**Getesteter Prozess:** Eingangsrechnungsverarbeitung (400–500 Rechnungen/Monat)
**Abgebrochene Phase:** Strukturierung → Moderator-Übergabe
**User-Rolle:** Proband / externer Testnutzer

---

## Zusammenfassung

Der Test5-Lauf deckte **2 Systemfehler** und **mehrere Qualitätsprobleme** auf:

1. Der Fehler `"Ein interner Fehler bei der Datenverarbeitung."` trat **zweimal** auf, unmittelbar bevor die Strukturierungsphase abgeschlossen werden sollte. Der User brach daraufhin die Session ab.
2. Der Structuring-Agent **bestätigte 5 Korrekturen mündlich, setzte aber nur 2 davon im Artefakt um** — eine schwerwiegende Diskrepanz zwischen Aussage und Artefaktzustand.
3. Die UX an Phasengrenzen verursachte **zweimal dasselbe Problem**: Der User hing nach einem Phasenabschluss ohne Orientierung, obwohl Transitions-Mechanismen vorhanden sind.

---

## Befund-Übersicht

| ID | Priorität | Kategorie | Kurzbeschreibung |
|----|-----------|-----------|-----------------|
| B1 | **P0** | Systemfehler | `"Ein interner Fehler bei der Datenverarbeitung."` (2×, Turn 18) |
| B2 | **P0** | UX | Orientierungslosigkeit nach Explorationsabschluss (Turn 13→14) |
| B3 | **P0** | UX | Erneute Orientierungslosigkeit beim Strukturierungsstart (Turn 15→16) |
| B4 | **P1** | Artefakt-Integrität | s1+s2 nicht zusammengeführt — Duplikat bleibt in v2 und v3 |
| B5 | **P1** | Artefakt-Integrität | Schritt "Manuelle Recherche Frau Müller" fehlt trotz Zusage |
| B6 | **P1** | Artefakt-Integrität | Schritt "Sachliche Prüfung" fehlt trotz Zusage |
| B7 | **P1** | Artefakt-Integrität | s4-Titel falsch: "Bestellung gefunden" statt "Hat die Rechnung eine Bestellnummer?" |
| B8 | **P1** | Artefakt-Integrität | ELO/Medienbruch-Spannungsfeld fehlt (s5.spannungsfeld=null, wm.spannungsfelder=[]) |
| B9 | **P1** | Artefakt-Integrität | Ausnahme "Gutschriften" fehlt trotz expliziter Anweisung |
| B10 | **P1** | Agent-Qualität | Agent halluziniert Bestätigungen — behauptet Änderungen, setzt sie nicht um |
| B11 | **P2** | Agent-Qualität | Explorations-Agent stellt keine Tiefenfragen zu impliziten Schritten |

---

## Detailbefunde

### B1 — `"Ein interner Fehler bei der Datenverarbeitung."` (P0)

**Was passierte:**
Bei Turn 18 ("Ja, das passt so. Bitte schließen Sie die Strukturierung ab") erschien der Fehler **zweimal** für den User. Beim dritten Versuch wurde die Phase erfolgreich abgeschlossen.

**Root Cause (Code):**
`backend/core/orchestrator.py:135–141`:
```python
if mode_output.patches:
    artifact_type = infer_artifact_type(mode_output.patches)
    if artifact_type is None:
        return self._error_output(
            wm,
            "Ein interner Fehler bei der Datenverarbeitung.",
            internal="Patch-Pfade konnten keinem Artefakttyp zugeordnet werden",
        )
```
`infer_artifact_type` matched Patch-Pfade gegen bekannte Präfixe (`/slots/`, `/schritte/`, `/abschnitte/`). Wenn das LLM Pfade halluziniert, die keinem dieser Präfixe entsprechen, gibt die Funktion `None` zurück.

**Wahrscheinliche Ursache:**
Der Structuring-Agent produzierte beim ersten und zweiten Aufruf für Turn 18 Patches mit ungültigen Pfaden — vermutlich, weil das LLM bei der Abschluss-Anweisung ("schließen Sie die Strukturierung ab") in einen anderen Ausgabe-Modus wechselte und Pfade wie `/version` oder andere Top-Level-Felder patchen wollte.

**Beweis:** Das Fehler-Pattern trat dreimal auf (2× Fehler, 1× Erfolg), d.h. es ist **LLM-nicht-deterministisch** und kein stabiler Code-Bug. Die Lösung muss auf Prompt- und/oder Retry-Ebene ansetzen.

**Verbesserungsvorschläge:**
1. **Retry-Logik im Orchestrator** für den Fehlerfall `artifact_type is None` — max. 2 Retries ohne User-Intervention, da der Fehler transient und LLM-bedingt ist.
2. **Explizitere Prompt-Anweisung** im Structuring-Prompt: Beim Abschluss KEINE Patches mehr produzieren — stattdessen nur `phase_complete` signalisieren.
3. **Bessere Fehlermeldung für den User** falls doch kein Retry hilft: Aktuell sieht der User einen generischen Fehlertext ohne Handlungshinweis ("bitte erneut versuchen" fehlt in dieser Variante).

---

### B2 — Orientierungslosigkeit nach Explorationsabschluss (P0)

**Was passierte (Turn 13→14):**
Turn 13 [assistant]: *"Damit ist die Exploration vollständig abgeschlossen."*
Turn 14 [user]: **"und jetzt? das ist nicht gut, dass ich jetzt hier einfach hänge. bisher war ok, aber jetzt geht es nicht weiter."**

**Root Cause:**
Der Exploration-Agent beendete die Phase mit einem abschließenden Statement, ohne dem User zu sagen, was als nächstes passiert. Da der Moderator erst beim nächsten User-Input aktiviert wird (er wartet auf einen Turn-Input), entstand eine Pause ohne UI-Feedback.

**Erschwerend:** Das System wechselte zwar intern zu `aktiver_modus: "moderator"`, aber dieser sendet keine proaktive Nachricht — er wartet auf den nächsten User-Input. Der User wusste nicht, dass er "einfach irgendwas eingeben" soll.

**Verbesserungsvorschläge:**
1. **Automischer Moderator-Turn bei `phase_complete`:** Wenn der Explorer `phase_complete` signalisiert, soll der Orchestrator in **demselben Zyklus** direkt einen Moderator-Turn initiieren — mit einer Übergangs-Nachricht, ohne auf User-Input zu warten.
2. **Exploration-Abschluss mit Vorschau:** Der Exploration-Prompt soll beim Abschluss immer eine kurze Vorschau auf die nächste Phase geben: *"Die Exploration ist abgeschlossen. Als nächstes strukturieren wir Ihren Prozess — ich übergebe jetzt..."*

---

### B3 — Erneute Orientierungslosigkeit beim Strukturierungsstart (P0)

**Was passierte (Turn 15→16):**
Turn 15 [assistant]: *"Ich übergebe jetzt an den zuständigen Modus, damit wir damit beginnen können."*
Turn 16 [user]: **"und jetzt? das ist nicht gut, dass ich jetzt hier einfach hänge." (wortgleiche Wiederholung)**

Der User beschwerte sich **zweimal über dieselbe Symptomatik**. Das zeigt, dass der Moderator-Übergabedialog in Turn 15 (nach User "ja") den Structuring-Agent zwar aktiviert, aber kein unmittelbares Feedback gibt — und wieder auf User-Input wartet.

**Verbesserungsvorschlag:**
Wenn der Moderator `advance_phase` + `return_to_mode` signalisiert, soll der Orchestrator den Structuring-Agent **sofort** aufrufen und dessen Einleitungsnachricht zurückgeben. Kein weiteres "jetzt warten" für den User.

---

### B4 — s1+s2 Duplikat nicht behoben (P1)

**Was User anwies (Turn 17):**
*"Schritt 1 und 2 überschneiden sich – bitte zu einem Schritt zusammenfassen."*

**Agent-Antwort (Turn 17):**
*"Der erste und zweite Schritt wurden zu 'Rechnungseingang und Erfassung' zusammengefasst."*

**Artefakt-Realität (v2 und v3):**
```
s1: [aktion] Rechnungseingang und Erfassung
s2: [aktion] Rechnung erfassen          ← IMMER NOCH VORHANDEN
```

**Beide Schritte blieben erhalten.** Der Agent änderte nur den Titel von s1, löschte s2 aber nicht.

**Root Cause:** Dem Structuring-Agent fehlt eine explizite Anweisung im Prompt, wie ein "merge/delete"-Vorgang auf Schrittebene über Patches umzusetzen ist. Um s2 zu entfernen, wäre ein JSON-Patch `{"op": "remove", "path": "/schritte/s2"}` nötig — das LLM produzierte diesen Patch offenbar nicht.

**Verbesserungsvorschlag:**
- Prompt-Ergänzung: Explizites Beispiel für `remove`-Patches auf Schritt-Ebene.
- Möglicher Guard: Nach User-Korrekturen sollte der Agent vor dem Bestätigen der Änderungen eine interne Konsistenzprüfung gegen das Artefakt durchführen.

---

### B5 — Schritt "Manuelle Recherche" fehlt (P1)

**Was User anwies (Turn 17):**
*"Manuelle Recherche durch Frau Müller (Detektivarbeit, kann Tage dauern). Das fehlt komplett."*

**Agent-Antwort (Turn 17):**
*"ich habe den neuen Schritt 'Manuelle Recherche durch Frau Müller' eingefügt"*

**Artefakt-Realität (v2 und v3):**
Kein entsprechender Schritt vorhanden. **Die Zusage wurde nicht umgesetzt.**

**Root Cause:**
Das Einfügen eines neuen Schritts in eine bestehende Sequenz erfordert:
1. `add`-Patch auf `/schritte/sX` mit einem neuen Key
2. Anpassung der `nachfolger`-Felder des Vorgänger-Schritts

Der Prompt enthält kein Beispiel für diese Operation. Das LLM schrieb die Bestätigung aus dem Dialog-Kontext heraus, ohne den entsprechenden Patch tatsächlich zu generieren. Zusätzlich ist unklar, ob das Artefakt-Schema die Einfüge-Reihenfolge über den `reihenfolge`-Wert oder die `nachfolger`-Kette steuert — diese Ambiguität führt zum LLM-Versagen bei Einfügeoperationen.

**Verbesserungsvorschlag:**
- Prompt-Ergänzung: Beispiel für das Einfügen eines neuen Schritts (neuer Key, `reihenfolge`, `nachfolger`-Update beim Vorgänger).
- Strukturierungsprompt soll explizit fordern, dass bei Einfüge-Befehlen immer beide Patches (add + update Vorgänger) zusammen produziert werden.

---

### B6 — Schritt "Sachliche Prüfung" fehlt (P1)

**Was User anwies (Turn 17):**
*"Nach dem Bestellabgleich kommt eine sachliche Prüfung – stimmt der Betrag, stimmen die Positionen? Wenn nicht, geht die Rechnung zurück an den Lieferanten."*

**Artefakt-Realität (v2 und v3):**
Kein entsprechender Schritt. **Nicht umgesetzt, nicht einmal in der Agent-Antwort erwähnt.**

**Root Cause:**
Dieser Schritt enthält auch eine Rückkopplungsschleife (Rechnung zurück an Lieferanten → ggf. Neueingang). Solche Loops erfordern bidirektionale `nachfolger`-Verknüpfungen, die das Prompt-Schema nicht adressiert. Das LLM hat diesen Schritt gar nicht erst versucht zu modellieren — vermutlich weil er in einer einfachen linearen Sequenz nicht trivial unterzubringen ist.

**Verbesserungsvorschlag:**
- Prompt-Ergänzung: Explizites Muster für Korrekturschleifen (Schritt mit zwei `nachfolger`: Normalfall + Rückgabe-Pfad).
- Gleiche Lösung wie B5: Einfüge-Beispiel im Prompt.

---

### B7 — s4-Titel falsch (P1)

**Was User anwies (Turn 17):**
*"Die Entscheidung bei Schritt 4 soll heißen: 'Hat die Rechnung eine Bestellnummer?'"*

**Artefakt-Realität (v2 und v3):**
```
s4.titel:     "Entscheidung: Bestellung gefunden"     ← FALSCH (alt)
s4.bedingung: "Hat die Rechnung eine Bestellnummer?"  ← korrekt
```

Der Agent hat `bedingung` korrekt gesetzt, aber `titel` nicht angepasst. Für den User im Frontend ist der Titel das primär sichtbare Feld.

**Root Cause:**
Der Prompt beschreibt `titel` und `bedingung` als separate Felder ohne klare Rollentrennung. Das LLM interpretierte "soll heißen" als Zuweisung an `bedingung` (den inhaltlichen Entscheidungstext) und ließ `titel` unverändert. Es fehlt eine Prompt-Regel: *"Wenn der User den Namen eines Entscheidungsschritts ändert, sind immer beide Felder — `titel` und `bedingung` — zu aktualisieren."*

**Verbesserungsvorschlag:**
- Prompt-Regel: Bei Entscheidungsschritten (`typ: "entscheidung"`) immer `titel` = kurze Variante der `bedingung`.
- Alternativ: `titel` aus `bedingung` zur Render-Zeit ableiten (Artefakt-Schema-Änderung).

---

### B8 — ELO/Medienbruch-Spannungsfeld fehlt (P1)

**Was User anwies (Turn 17):**
*"Bei der Abteilungsleiter-Freigabe bitte vermerken: Freigabe läuft über ELO, aber Herr Krause druckt aus und stempelt, dann muss Frau Becker wieder einscannen. Das ist ein Problem."*

**Agent-Antwort (Turn 17):**
*"Der Freigabeschritt durch den Abteilungsleiter wurde kommentiert, dass Herr Krause ausdruckt und stempelt, was ein Problem darstellt."*

**Artefakt-Realität:**
```
s5.spannungsfeld:   null
wm.spannungsfelder: []
```

**Root Cause:**
Das `spannungsfeld`-Feld existiert im Artefakt-Schema, wird aber im Structuring-Prompt nicht erklärt — weder wann es befüllt werden soll noch wie (Freitext? Strukturiert?). Das LLM ignorierte das Feld vollständig und verbalisierte das Problem nur in der nutzeraeusserung. Das ELO/Medienbruch-Problem ist das konkreteste Digitalisierungspotenzial des gesamten Prozesses und wäre für die Spezifikationsphase essenziell.

**Verbesserungsvorschlag:**
- Prompt-Ergänzung: Explizite Instruktion, wann `spannungsfeld` zu befüllen ist — nämlich immer dann, wenn der User ein Problem, einen Medienbruch oder eine Ineffizienz in einem Schritt nennt.
- Patch-Beispiel für `spannungsfeld`-Zuweisung auf Schritt-Ebene.
- `wm.spannungsfelder` sollte durch den Orchestrator oder den Structuring-Agent automatisch aus allen befüllten `spannungsfeld`-Feldern aggregiert werden, nicht manuell.

---

### B9 — Gutschriften fehlen als Ausnahme (P1)

**Was User anwies (Turn 17):**
*"Gutschriften als Ausnahme ergänzen."*

**Artefakt-Realität:** Kein `typ: "ausnahme"` Schritt für Gutschriften vorhanden.

**Root Cause:**
Gleiche Ursache wie B5: Das Einfügen eines neuen Schritts mit `typ: "ausnahme"` erfordert einen `add`-Patch, für den kein Beispiel im Prompt existiert. Ausnahmen haben zudem keine `nachfolger` und keinen festen `reihenfolge`-Platz — das LLM ist unsicher, wo im Artefakt dieser Schritt anzusiedeln ist.

**Verbesserungsvorschlag:**
- Prompt-Ergänzung: Ausnahmen (`typ: "ausnahme"`) sind eigenständige Schritte ohne `nachfolger`, werden am Ende des `schritte`-Dicts angehängt.
- Gleiche Lösung wie B5: Einfüge-Beispiel mit `add`-Patch.

---

### B10 — Agent halluziniert Bestätigungen (P1)

**Muster:** Der Structuring-Agent bestätigte in Turn 17 **5 konkrete Änderungen verbatim**, von denen er **nur 2 tatsächlich im Artefakt umsetzte**:

| Zusage | Im Artefakt? |
|--------|-------------|
| s1+s2 zusammenfassen | ❌ s2 blieb erhalten |
| Entscheidungstext "Hat die Rechnung eine Bestellnummer?" | ✅ (als Bedingung, nicht Titel) |
| Manuelle Recherche Frau Müller eingefügt | ❌ fehlt komplett |
| Sachliche Prüfung eingefügt | ❌ fehlt komplett |
| ELO/Medienbruch kommentiert | ❌ spannungsfeld=null |
| Mahnung als Ausnahme definiert | ✅ (war bereits Typ "ausnahme" in v1) |
| Gutschriften als Ausnahme | ❌ fehlt |

**Root Cause:** Das LLM generiert die nutzeraeusserung (Zusammenfassung) aus dem Dialog-Kontext, nicht aus den tatsächlich generierten Patches. Die Bestätigung ist eine Interpretation der User-Anfrage, keine Reflexion des tatsächlichen Artefakt-Zustands.

**Verbesserungsvorschlag:**
- Nach Patch-Anwendung: Artefakt-Diff als Kontext zurück ans LLM, damit die Bestätigungsantwort auf tatsächliche Änderungen basiert.
- Alternativ: Die nutzeraeusserung im Structuring-Modus direkt aus dem generierten Patch-Set ableiten (strukturiert statt generativ).

---

### B11 — Explorations-Agent: Fehlende Tiefenfragen (P2)

**Kontext:**
Der User erwähnte in Turn 10 explizit: *"Rechnungen ohne Bestellnummer – da weiß keiner wer das bestellt hat, Frau Müller muss rumtelefonieren."*

Der Explorer-Agent fragte in Turn 10 nach: *"wie die Ausnahmen behandelt werden, insbesondere bei Teilrechnungen und bei Rechnungen ohne Bestellnummer?"* — aber der User antwortete stattdessen über Mahnungen (Topic-Drift), und der Agent akzeptierte das.

**Resultat:** Das Thema "Manuelle Recherche ohne Bestellnummer" wurde nie vollständig im Explorations-Artefakt verankert. Daher fehlte der entsprechende Schritt dann auch im ersten Struktur-Entwurf und musste im Nachgang mühsam nachgebessert werden (und scheiterte letztlich daran).

**Verbesserungsvorschlag:**
Der Explorer soll bei Topic-Drifts explizit zurückkehren: *"Sie haben noch nicht beantwortet, wie bei Rechnungen ohne Bestellnummer vorgegangen wird. Können Sie das kurz beschreiben, bevor wir weitergehen?"*

---

## Zusammenfassung: Kritischer Pfad

Der gesamte Abbruch-Pfad des Users lässt sich auf **3 verkettete Probleme** zurückführen:

```
Exploration abgeschlossen (Turn 13)
    └─ [B2] Keine proaktive Überleitung → User hängt (Turn 14)
        └─ Moderator aktiviert, aber wieder passiv → [B3] User hängt erneut (Turn 16)

Structuring gestartet → 10-Schritt-Entwurf (Turn 16)
    └─ User gibt 7 Korrekturen (Turn 17)
        └─ [B10] Agent bestätigt alle, setzt nur 2 um
            └─ [B4–B9] 5 Korrekturen fehlen im Artefakt

User sagt "passt" (irrtümlich) und will Phase abschließen (Turn 18)
    └─ [B1] LLM halluziniert ungültige Patch-Pfade → 2× Fehler
        └─ User bricht ab
```

---

## Prioritisierte Maßnahmen

### Sofort (Sprint 1)

| Maßnahme | Löst | Aufwand |
|----------|------|---------|
| Retry-Logik für `infer_artifact_type`-Fehler (max. 2 Retries) | B1 | Klein |
| Structuring-Prompt: `remove`-Patch-Beispiel + `phase_complete` ohne Patches | B1, B4 | Klein |
| Orchestrator: Auto-Moderator-Turn nach `phase_complete` ohne User-Warteloop | B2, B3 | Mittel |

### Kurzfristig (Sprint 2)

| Maßnahme | Löst | Aufwand |
|----------|------|---------|
| Structuring-Agent: Patch-basierte Bestätigung (nicht generativ) | B10 | Mittel |
| Structuring-Prompt: Explizite Abdeckung aller Korrekturoperationen (merge, add, rename, add-exception) | B4–B9 | Mittel |
| Exploration-Prompt: Topic-Drift-Recovery bei offenen Fragen | B11 | Klein |

### Mittelfristig (Sprint 3)

| Maßnahme | Löst | Aufwand |
|----------|------|---------|
| Artefakt-Diff-Ansicht im UI nach Structuring-Korrekturen | B10 | Groß |
| `wm.spannungsfelder` automatisch aus Schritt-`spannungsfeld`-Feldern aggregieren | B8 | Klein |

---

## Datenbasis

- **Dialog:** 18 Turns (Turn 18 mit 3 User-Nachrichten wegen Fehler-Retries)
- **Artefakt-Versionen:** exploration v0–v9, structure v0–v3
- **Working Memory Final:** `aktiver_modus=moderator`, `phasenstatus=phase_complete`, `spannungsfelder=[]`
- **Error-Code:** `orchestrator.py:139` — `"Ein interner Fehler bei der Datenverarbeitung."` / `"Patch-Pfade konnten keinem Artefakttyp zugeordnet werden"`
- **Analysiert am:** 2026-03-18
