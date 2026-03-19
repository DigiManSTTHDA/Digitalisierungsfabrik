# Agent-basierter Prototyp: Systembeschreibung

> **Dokumenttyp:** Architekturbeschreibung & Entscheidungsgrundlage
> **Bezugsdokument:** `docs/digitalisierungsfabrik_systemdefinition.md` (SDD)
> **Status:** Entwurf — Grundlage für Parallelentwicklung
> **Datum:** 2026-03-19

---

## 1. Motivation

### 1.1 Ausgangslage

Die Digitalisierungsfabrik ist ein KI-geführtes Prozess-Elizitierungssystem, das implizites Geschäftsprozesswissen von Fachanwendern durch strukturierte Interviews in formale EMMA-RPA-Algorithmen überführt. Das aktuelle System (SDD v1) nutzt einen **deterministischen 11-Schritt-Orchestrator**, der kognitive Modi (ExplorationMode, StructuringMode, etc.) aufruft, die ihrerseits LLM-Calls durchführen und RFC 6902 JSON-Patches zurückgeben.

### 1.2 Beobachtete Schwierigkeiten im aktuellen System

Das System funktioniert grundsätzlich, zeigt aber charakteristische Brüchigkeiten:

1. **RFC 6902 Patch-Fragilität:** Das LLM muss exakte JSON-Patch-Pfade produzieren. Jede Abweichung erfordert Retry-Logik, Template-Validierung und Fehlermeldungen. Die `_merge_slot_patches()`-Logik ist ein Symptom dieser Fragilität.

2. **Hoher Änderungsaufwand:** Jede funktionale Änderung erfordert Eingriffe an 4-5 Stellen gleichzeitig: Orchestrator-Logik, Mode-Klasse, Prompt-Template, Guardrail, ggf. Template-Schema.

3. **LLM ohne Agency:** Das LLM ist ein strukturierter Textverarbeiter — es entscheidet nicht *was* passiert, nur *wie* ein vom Orchestrator vorgegebener Schritt ausgeführt wird. Es kann nicht selbst entscheiden, ob es einen Completeness-Check durchführen, eine Validierung anstoßen oder das Thema wechseln sollte.

4. **Deterministische Logik um nicht-deterministisches System:** Der Orchestrator baut rigide, regelbasierte Kontrolle um ein probabilistisches System (LLM). Das erzeugt die Brüchigkeit: Jede Stelle, an der das LLM vom erwarteten Format abweicht, braucht Auffanglogik.

### 1.3 Kernthese

Die Entwicklungen der letzten Monate (Claude Agent SDK, Structured Outputs, Tool Use als Standardparadigma) ermöglichen eine alternative Architektur:

> **Statt** den Orchestrator als determinstische Kontrollschicht *über* dem LLM zu betreiben,
> **wird** der Orchestrator zu einer schlanken "Hard Shell" *um* einen Agent-Loop, der das LLM mit Tools ausstattet, über die es selbst in Artefakte schreibt, Validierungen anstößt und Phasenübergänge signalisiert.

Das Ziel bleibt identisch: Implizites Prozesswissen → strukturierte EMMA-Algorithmen. Nur der Weg ändert sich.

---

## 2. Architektur des Agent-basierten Prototyps

### 2.1 Grundprinzip: "Agent innerhalb einer Hard Shell"

```
┌─────────────────────────────────────────────────────────────┐
│                     HARD SHELL (Python)                      │
│  Deterministisch. 5 Schritte pro Turn.                      │
│                                                              │
│  1. Load State    — Artefakte + Working Memory aus DB laden  │
│  2. Inject Context — Frischen Kontext für Agent aufbauen     │
│  3. Agent Turn    — Agent loop: think → tools → respond      │
│  4. Validate      — Tool-Ergebnisse prüfen, Invarianten     │
│  5. Persist       — Atomisch in DB schreiben                 │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                   AGENT LOOP                          │  │
│  │                                                       │  │
│  │  System-Prompt (phasenspezifisch)                     │  │
│  │  + Aktueller Artefakt-Stand (komprimiert)             │  │
│  │  + Letzte 3-5 Dialog-Turns                            │  │
│  │  + Progress-Anker ("5/9 Slots befüllt, fehlend: ...")│  │
│  │                                                       │  │
│  │  Tools:                                               │  │
│  │  ├── write_slot(slot_id, inhalt)                      │  │
│  │  ├── add_structure_step(titel, typ, beschreibung)     │  │
│  │  ├── add_emma_action(abschnitt_id, aktionstyp, ...)   │  │
│  │  ├── check_completeness() → Gap-Report                │  │
│  │  ├── signal_phase_complete()                          │  │
│  │  ├── read_artifact(type) → aktueller Stand            │  │
│  │  └── request_validation() → Validierungsbericht       │  │
│  │                                                       │  │
│  │  Agent ENTSCHEIDET autonom:                           │  │
│  │  - Welche Tools wann aufgerufen werden                │  │
│  │  - Ob nachgefragt oder geschrieben wird               │  │
│  │  - Ob Completeness geprüft werden soll                │  │
│  │  - Wann die Phase als abgeschlossen signalisiert wird │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         │                              │
         ▼                              ▼
┌─────────────────┐          ┌──────────────────────┐
│  React Frontend │          │  SQLite / Postgres    │
│  Chat + Artefakt│          │  Artefakte + History  │
│  Visualisierung │          │  + Working Memory     │
└─────────────────┘          └──────────────────────┘
```

### 2.2 Der 5-Schritt-Zyklus (statt 11 Schritte)

| Schritt | Beschreibung | Deterministisch? |
|---------|-------------|------------------|
| 1. Load State | Artefakte, Working Memory, letzte Turns aus DB | Ja |
| 2. Inject Context | System-Prompt + komprimierter Artefakt-Stand + Progress-Anker + Dialog-Window | Ja |
| 3. Agent Turn | Claude API mit Tools — Agent denkt, ruft Tools, antwortet | Nein (agentisch) |
| 4. Validate | Tool-Ergebnisse gegen Invarianten prüfen, Invalidierungskaskaden auslösen | Ja |
| 5. Persist | Alle Änderungen atomar in DB schreiben | Ja |

Die Agency lebt in Schritt 3. Die Hard Shell (Schritte 1, 2, 4, 5) bleibt vollständig deterministisch.

### 2.3 Tools statt Modes

Das bisherige System hat 5 kognitive Modi (Exploration, Structuring, Specification, Validation, Moderator), die jeweils einen LLM-Call durchführen und RFC 6902 Patches zurückgeben. Im Agent-System werden diese zu **Tools**, die der Agent selbst aufruft:

| Bisheriger Mode / Mechanismus | Neues Tool | Preconditions (deterministisch, im Code) |
|-------------------------------|-----------|------------------------------------------|
| ExplorationMode + RFC 6902 Patches | `write_slot(slot_id, inhalt)` | `slot_id` muss in Enum existieren; Phase muss `exploration` sein |
| StructuringMode + RFC 6902 Patches | `add_structure_step(...)`, `update_step(...)` | Phase muss `strukturierung` sein |
| SpecificationMode + RFC 6902 Patches | `add_emma_action(...)`, `update_action(...)` | Phase muss `spezifikation` sein; `aktionstyp` muss in EMMA-Enum sein |
| Orchestrator Completeness-Check | `check_completeness()` | Keine — Agent kann jederzeit aufrufen |
| Moderator `signal_phase_complete` | `signal_phase_complete()` | Alle Pflicht-Slots/Schritte müssen `vollstaendig` oder `nutzervalidiert` sein |
| ValidationMode | `request_validation()` | Phase muss `validierung` sein |
| Context-Assembler `prompt_context_summary` | `read_artifact(type)` | Keine — Agent kann jederzeit den aktuellen Stand lesen |

**Entscheidender Unterschied:** Im bisherigen System entscheidet der Orchestrator, welcher Mode aufgerufen wird. Im Agent-System entscheidet das LLM, welches Tool aufgerufen wird. Die Sicherheit kommt aus den **Tool-Preconditions** — deterministischer Code, der ungültige Aufrufe ablehnt.

### 2.4 Context Engineering: Fresh Context per Turn

Das bestehende Context-Engineering-System (SDD 6.5) wird übernommen und adaptiert:

| Mechanismus | Bisherig | Agent-Prototyp |
|------------|----------|----------------|
| Dialog-Window | Letzte 3 Turns (Modes) / 10 (Moderator) | Letzte 3-5 Turns (konfigurierbar) |
| Artefakt-Kontext | `prompt_context_summary()` — 8 Zeilen | Identisch — komprimierte Zusammenfassung statt vollständiger Artefakte |
| Phase-spezifischer Content | Mode sieht nur phasenrelevante Daten | System-Prompt ist phasenspezifisch; Tools haben Phase-Preconditions |
| Deterministic Summaries | `patch_summarizer.py` | Tool-Responses sind deterministisch formuliert (kein LLM) |
| Progress-Anker | Working Memory | Bei jedem Turn injiziert: "Phase: Exploration. 5/9 Slots befüllt. Fehlend: randbedingungen, ausnahmen" |

**Kernprinzip (aus Manus-Erfahrung):** Der Kontext wird nicht akkumuliert, sondern pro Turn frisch aus autoritativen Quellen (Artefakten in DB) generiert. Die Conversation History dient nur der Dialog-Kontinuität.

### 2.5 Phasen: Konzept bleibt, Implementierung ändert sich

Die 4 Phasen (Exploration → Strukturierung → Spezifikation → Validierung) bleiben als pädagogisches Konzept erhalten (SDD 6.1). Die Implementierung ändert sich:

**Bisherig:** Orchestrator → wählt Mode → Mode ruft LLM → LLM liefert Patches → Orchestrator validiert → Orchestrator prüft Phase-Completion

**Neu:** Hard Shell → injiziert phasenspezifischen System-Prompt → Agent arbeitet mit Tools → Hard Shell validiert → Agent signalisiert Phase-Completion via Tool → Hard Shell prüft Preconditions

Die "Sokratische Hebammentechnik" (SDD 6.1, 6.6.1) wird durch den phasenspezifischen System-Prompt gesteuert:

- **Exploration-Prompt:** "Du führst ein Gespräch mit einem Fachanwender. Stelle genau EINE Frage pro Antwort. Verwende keine technischen Begriffe. Dein Ziel: Die 9 Slots des Explorations-Artefakts befüllen."
- **Strukturierungs-Prompt:** "Der Nutzer hat seinen Prozess beschrieben. Hilf ihm, die einzelnen Schritte zu identifizieren und in eine logische Reihenfolge zu bringen."
- **Spezifikations-Prompt:** "Jeder Prozessschritt muss in konkrete EMMA-Aktionen übersetzt werden. Erkläre dem Nutzer, was eine Aktion ist, und erarbeite gemeinsam die Details."
- **Validierungs-Prompt:** "Prüfe mit dem Nutzer gemeinsam, ob der erarbeitete Algorithmus vollständig und korrekt ist."

---

## 3. Vergleich zum bisherigen System (SDD-Mapping)

### 3.1 High-Level-Anforderungen: Erfüllungsstatus

| SDD-Anforderung | Beschreibung | Erfüllung im Agent-Prototyp |
|-----------------|-------------|----------------------------|
| **Kernziel** | Implizites Prozesswissen → EMMA-Algorithmen | **Identisch.** Das Ziel ändert sich nicht. |
| **Zielgruppe** | Fachanwender ohne IT-Kenntnisse | **Identisch.** Agent-Loop ist für den Nutzer unsichtbar. |
| **Phasenmodell** (SDD 6.1) | 4 Phasen: Exploration → Strukturierung → Spezifikation → Validierung | **Erhalten** als pädagogisches Konzept. Implementierung via phasenspezifische System-Prompts + Tool-Preconditions statt Mode-Klassen. |
| **3 verknüpfte Artefakte** (SDD 5.3-5.5) | Exploration (9 Slots), Struktur (Kontrollfluss), Algorithmus (EMMA) | **Identisch.** Datenmodell bleibt unverändert. |
| **Dialogische Interaktion** (SDD 3.1) | Chat-basiertes Interview | **Verbessert.** Agent kann flexibler auf Nutzer eingehen, da er nicht an rigide Output-Formate gebunden ist. |
| **EMMA-Kompatibilität** (SDD 8.3) | 18 EMMA-Aktionstypen | **Identisch.** Enum als Tool-Parameter. |
| **Artefakt-Integrität** (SDD 6.3, Schritt 8) | Invalidierungskaskade bei Struktur-Änderungen | **Erhalten.** Serverseitig in Tool-Implementierung, nicht im Prompt. |
| **Systemsprache Deutsch** (SDD 3.3) | Alle Dialoge, Artefakte, UI auf Deutsch | **Identisch.** System-Prompts und Tool-Responses auf Deutsch. |

### 3.2 Abweichungen vom SDD

| SDD-Element | Abweichung | Begründung |
|-------------|-----------|------------|
| **11-Schritt-Orchestrator** (SDD 6.3) | Ersetzt durch 5-Schritt-Zyklus | Schritte 3-6 und 8-10 des alten Zyklus werden durch den Agent-Loop internalisiert. |
| **5 kognitive Modi** (SDD 6.6) | Ersetzt durch Tools + phasenspezifische Prompts | Modi waren Wrapper um LLM-Calls. Tools sind das native Claude-Äquivalent. |
| **RFC 6902 Patches** (SDD 6.3, Schritt 7) | Ersetzt durch granulare Tool-Calls | `write_slot()` statt `[{"op": "replace", "path": "/slots/prozessziel/inhalt", ...}]` |
| **Moderator-Modus** (SDD 6.6.5) | Entfällt als separater Mode | Agent wechselt Tonfall selbst bei Phasenübergang. `signal_phase_complete()` + Hard-Shell-Preconditions ersetzen Moderator-Logik. |
| **Template-Schema-Validierung** (SDD 6.3, Schritt 2) | Entfällt | Tools haben typisierte Parameter (Enums). Keine Pfad-Validierung nötig, weil es keine freien Pfade gibt. |
| **Flag-System** (SDD 6.4.1) | Vereinfacht | Tools signalisieren direkt. `phase_complete`, `advance_phase`, `return_to_mode` werden zu Tool-Calls statt Flags. |

### 3.3 NFR-Erfüllung

| NFR (SDD 8.1) | Erfüllung | Anmerkung |
|---------------|-----------|-----------|
| **Wartbarkeit** | **Verbessert** | Weniger Code, weniger Stellen für Änderungen. Tool + Prompt statt Mode + Orchestrator + Guardrail + Template. |
| **Zuverlässigkeit** | **Vergleichbar** | Atomische Persistenz bleibt. Rollback via Tool-Preconditions statt Executor. Artefakt-Versioning bleibt. |
| **Beobachtbarkeit** | **Anders** | Statt Flags/Working Memory im DebugPanel: Tool-Call-Trace + Artifact-Diff pro Turn + Extended Thinking Logging. |
| **Performance** | **Potenziell langsamer** | Agent kann 3-8 Tool-Calls pro Turn machen statt 1 LLM-Call. Mitigiert durch Tool-Call-Budget. |

---

## 4. Was wir gewinnen (Stärken des Agent-Ansatzes)

### 4.1 Robustheit bei Format-Abweichungen

**Bisherig:** LLM muss RFC 6902 Patch-Pfade exakt produzieren. Jede Abweichung → Retry → Template-Error → ggf. Failure.

**Agent:** LLM ruft `write_slot(slot_id="prozessziel", inhalt="Rechnungen automatisch prüfen")` auf. Das ist ein normaler Function Call — Claude ist darauf trainiert. Kein Pfad-Format, kein Patch-Syntax.

### 4.2 Flexiblere Gesprächsführung

**Bisherig:** Orchestrator bestimmt den Ablauf starr. Nutzer kann nicht "off-script" gehen, ohne dass das System die Kontrolle verliert.

**Agent:** Agent kann flexibel reagieren. Nutzer erwähnt in Phase 1 schon einen konkreten Prozessschritt → Agent merkt sich das (via Tool-Call) und kommt in Phase 2 darauf zurück. Die pädagogische Führung kommt aus dem System-Prompt, nicht aus Code-Zwängen.

### 4.3 Geringerer Entwicklungsaufwand

**Bisherig:** Änderung an Interview-Logik erfordert: Mode-Klasse → Prompt-Template → Guardrail → Template-Schema → ggf. Orchestrator-Logik.

**Agent:** Änderung am System-Prompt reicht oft aus. Neue Fähigkeit = neues Tool mit Preconditions.

### 4.4 Natürliche Validierung

**Bisherig:** Orchestrator muss explizit Completeness-Check und Validierung anstoßen (Schritt 9-10).

**Agent:** Agent kann `check_completeness()` aufrufen wann es sinnvoll erscheint — nach jeder Antwort, nach 5 Antworten, oder wenn der Nutzer "Ich glaube, das war's" sagt. Die Entscheidung *wann* validiert wird, ist kontextabhängig — genau die Stärke eines LLM.

### 4.5 Potenzial für Sub-Agenten

Der Agent kann eigenständig Validierungs-Sub-Agenten aufrufen (via `request_validation()` Tool), die als separate, fokussierte LLM-Calls laufen:
- Konsistenz-Check: "Stimmen Exploration-Slots und Strukturschritte überein?"
- Informationsverlust-Check: "Hat der Nutzer in den letzten 5 Turns etwas gesagt, das nicht im Artefakt steht?"
- EMMA-Kompatibilitäts-Check: "Sind alle Aktionen durch EMMA-Typen abbildbar?"

---

## 5. Risiken und Schwächen (Agent vs. Orchestrator)

### 5.1 Context Rot — KRITISCH

**Risiko:** Jeder Tool-Call addiert 200-500 Tokens. Bei 3-8 Calls pro Turn × 50 Turns = potenziell Hunderttausende Tokens. "Lost in the Middle"-Effekt (Liu et al., 2024): 15-47% Performance-Verlust bei mittleren Kontextpositionen.

**Mitigation (aus bestehendem System übernommen):**
- Fresh Context per Turn aus DB (Manus-Prinzip)
- Dialog-Window: Nur letzte 3-5 Turns
- `prompt_context_summary()` statt vollständiger Artefakte
- Phase-spezifischer System-Prompt filtert irrelevanten Kontext

### 5.2 Goal Drift — KRITISCH

**Risiko:** Über 50+ Turns "vergisst" der Agent seine Phase. Nutzer erwähnt ein neues System → Agent wechselt ungewollt den Fokus.

**Mitigation:**
- Phase-Injektion bei jedem Turn im System-Prompt
- Tool-Preconditions: `write_slot()` verweigert Ausführung wenn Phase ≠ exploration
- Progress-Anker: "5/9 Slots befüllt. Fehlend: randbedingungen, ausnahmen"

### 5.3 Tool-Parameter-Halluzination — HOCH

**Risiko:** Agent erfindet IDs: `write_slot(slot_id="prozessdetails")` statt `"prozessbeschreibung"`. Forschungsdaten: 15-30% Parameter-Fehler wenn gültige IDs nicht sichtbar sind.

**Mitigation:**
- Enum-Parameter wo möglich
- Gültige IDs in Tool-Beschreibungen injizieren
- Runtime-Validierung mit spezifischen Fehlermeldungen

### 5.4 Vorzeitige Phasen-Completion — HOCH

**Risiko:** Agent signalisiert "fertig" obwohl kritische Aspekte fehlen. 15-30% Premature-Completion-Rate bei komplexen Multi-Step-Tasks.

**Mitigation:**
- `signal_phase_complete()` hat harte Preconditions (identisch zu bisherigen Guardrails)
- `check_completeness()` liefert expliziten Gap-Report

### 5.5 Kosten-Explosion — MITTEL

**Risiko:** 3-8 Tool-Calls pro Turn statt 1 LLM-Call. Faktor 3-8x Kostensteigerung.

**Mitigation:**
- Tool-Call-Budget: Max 15 Calls pro User-Turn
- Batched Tools wo sinnvoll (z.B. `update_slots(patches=[...])`)
- Haiku für einfache Checks, Sonnet/Opus für Content-Generierung

### 5.6 Cross-Artifact-Konsistenz — HOCH

**Risiko:** Agent updatet Strukturschritt, vergisst Algorithmus-Abschnitt zu invalidieren.

**Mitigation:** Server-side Invarianten in Tool-Implementierung. `update_structure_step()` triggert automatisch Invalidierungskaskade. Agent muss davon nichts wissen.

### 5.7 Debugging-Opazität — MITTEL

**Risiko:** Warum hat der Agent Tool X statt Y aufgerufen? Im bisherigen System ist jeder Schritt deterministisch nachvollziehbar.

**Mitigation:**
- Structured Logging: Jeden Tool-Call mit Parametern + Ergebnis
- Extended Thinking (Claude): Agent-Reasoning wird sichtbar
- DebugPanel-Äquivalent: Tool-Call-Trace + Artifact-Diff pro Turn

### 5.8 Infinite Loops / Retry-Spirale — MITTEL

**Risiko:** Tool schlägt fehl → Agent versucht es nochmal mit denselben Params → Endlosschleife. 5-10% der Agent-Runs zeigen Schleifenverhalten.

**Mitigation:**
- Hard Limit: Max 15-20 Tool-Calls pro Turn
- Hard Limit: Max 10 autonomous Turns ohne User-Input
- Typed Errors mit `suggested_action`

### 5.9 Terminologie-Drift — MITTEL

**Risiko:** Agent nutzt "Rechnungsprüfung" in Turn 5, "Überprüfung" in Turn 20, "Check" in Turn 35.

**Mitigation:**
- Kanonische Begriffe aus Artefakten: Tools geben offizielle Bezeichnungen zurück
- Deterministische Tool-Responses (wie bisheriger `patch_summarizer.py`)

### 5.10 Pädagogische Regression — MITTEL

**Risiko:** Agent wird zu schnell zu technisch, stellt mehrere Fragen gleichzeitig, verliert die "Sokratische" Gesprächsführung.

**Mitigation:**
- Explizite Instruktion im System-Prompt: "Stelle genau EINE Frage pro Antwort. Verwende keine technischen Begriffe."
- Phasenspezifische Prompts mit didaktischen Leitplanken

---

## 6. Offene Architekturentscheidungen

### 6.1 Ein Agent oder phasenspezifische Agents?

| Option | Vorteile | Nachteile |
|--------|---------|-----------|
| **Ein Agent, alle Phasen** | Einfacher, weniger Code, natürlicher Gesprächsfluss | Längerer Kontext, höheres Goal-Drift-Risiko |
| **4 phasenspezifische Agents** | Fokussierter, kürzerer Kontext, klare Trennung | Handoff-Komplexität, Kontext-Übergabe zwischen Agents |
| **Hybrid: 1 Agent, phasenspezifischer Prompt** | Kombiniert Einfachheit mit Fokus | System-Prompt-Wechsel muss sauber implementiert werden |

**Empfehlung:** Hybrid — Ein Agent, dessen System-Prompt bei Phasenwechsel ausgetauscht wird. Die Hard Shell steuert den Prompt-Wechsel.

### 6.2 Claude Agent SDK vs. direkte Claude API?

| Option | Vorteile | Nachteile |
|--------|---------|-----------|
| **Claude Agent SDK** | Agent-Loop eingebaut, Tool-Handling, Retry | Alpha-Status (v0.1.49), weniger Kontrolle |
| **Claude API direkt** | Volle Kontrolle, Structured Outputs, production-ready | Agent-Loop selbst implementieren (~50 LOC) |

**Empfehlung:** Claude API direkt. Der Agent-Loop ist trivial (while tool_calls: execute → re-call). Die Hard Shell braucht volle Kontrolle über Context-Injection.

### 6.3 Persistenz

SQLite bleibt für den Prototyp. Postgres als Option für Produktion (LangGraph/Temporal-Kompatibilität falls gewünscht).

---

## 7. Implementierungsplan (High-Level)

### Phase 1: Minimal Viable Agent (1 Phase, Exploration)
- Hard Shell (5-Schritt-Zyklus)
- 3 Tools: `write_slot()`, `check_completeness()`, `read_artifact()`
- Exploration-System-Prompt
- Vorhandenes Pydantic-Datenmodell
- Vergleichstest gegen bisheriges System

### Phase 2: Vollständiger Prototyp (alle 4 Phasen)
- Alle Tools implementiert
- Phasenspezifische System-Prompts
- `signal_phase_complete()` mit Preconditions
- Validierungs-Sub-Agent

### Phase 3: Vergleichsevaluation
- Identische Testszenarien auf beiden Systemen
- Metriken: Artefakt-Qualität, Vollständigkeit, Kosten, Nutzererfahrung
- Entscheidung über Weiterentwicklungsrichtung

---

## 8. Zusammenfassung

Der Agent-basierte Prototyp verfolgt das **identische Ziel** wie das bisherige System (SDD): Implizites Prozesswissen von Fachanwendern in EMMA-Algorithmen überführen.

Der **Weg** ändert sich fundamental:
- **Bisherig:** Deterministischer Orchestrator steuert passive LLM-Calls
- **Neu:** Schlanke Hard Shell rahmt einen aktiven Agent mit Tools

Das **Datenmodell** (Artefakte, Slots, EMMA-Aktionen) bleibt unverändert. Die **pädagogische Struktur** (Phasen, schrittweise Führung) bleibt konzeptionell erhalten, wird aber über Prompts statt Code implementiert.

Die **Risiken** sind identifiziert und adressierbar. Die meisten Mitigationen können direkt aus dem bestehenden System übernommen werden (Context Engineering, Guardrails → Preconditions, Deterministic Summaries).

Ob der Ansatz dem bisherigen überlegen ist, kann nur ein **paralleler Prototyp** mit vergleichender Evaluation zeigen.
