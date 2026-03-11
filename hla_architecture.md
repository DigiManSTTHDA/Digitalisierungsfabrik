# HIGH-LEVEL ARCHITECTURE — Digitalisierungsfabrik
**Version:** 0.1
**Status:** Entwurf
**Bezug:** SDD `digitalisierungsfabrik_systemdefinition.md`

---

## Inhaltsverzeichnis

1. [Zweck dieses Dokuments](#1-zweck)
2. [Tech Stack](#2-tech-stack)
3. [Komponentenübersicht](#3-komponentenübersicht)
4. [Komponentendiagramm](#4-komponentendiagramm)
5. [Datenfluss: Orchestrator-Zyklus](#5-datenfluss-orchestrator-zyklus)
6. [Projektstruktur](#6-projektstruktur)
7. [Schließung kritischer Open Points](#7-schließung-kritischer-open-points)
8. [Implementierungsreihenfolge](#8-implementierungsreihenfolge)
9. [Offene Punkte (HLA-Ebene)](#9-offene-punkte-hla-ebene)

---

## 1. Zweck

Dieses Dokument beschreibt die High-Level-Architektur (HLA) des Digitalisierungsfabrik-Prototyps.

Es beantwortet drei Fragen:
- **Was** wird gebaut? (Komponenten und ihre Verantwortlichkeiten)
- **Womit** wird gebaut? (Tech Stack mit Begründungen)
- **Wie** ist es strukturiert? (Projektlayout, Interfaces, Datenfluss)

Es ist kein Implementierungsdesign — Prompt-Engineering, Slot-Schemas und Modus-interne Logik werden in einem separaten Implementierungsdesign-Dokument behandelt.

Die Entscheidungen in diesem Dokument sind **bindend für die Implementierung**, soweit nicht explizit als offen markiert.

---

## 2. Tech Stack

### 2.1 Übersicht

| Schicht | Komponente | Version |
|---|---|---|
| Anwendungs-Framework | **Chainlit** | ≥ 1.3 |
| Backend-Sprache | **Python** | ≥ 3.11 |
| Datenmodelle | **Pydantic v2** | ≥ 2.6 |
| LLM-Client (Cloud) | **anthropic SDK** | ≥ 0.25 |
| JSON Patch | **jsonpatch** | ≥ 1.33 |
| Konfiguration | **pydantic-settings** | ≥ 2.2 |
| Logging | **structlog** | ≥ 24.1 |
| Persistenz | JSON-Dateien mit atomarem Write | — |

### 2.2 Begründungen

#### Chainlit (Anwendungs-Framework)

Chainlit ist ein Python-natives Framework, das exakt die im SDD beschriebene UI-Struktur abdeckt:

| SDD-Anforderung | Chainlit-Lösung |
|---|---|
| Chat-Bereich (links) | Nativer Chat-Stream |
| Artefakt-Bereich (rechts) | `cl.CustomElement` / `cl.Text` als Side Panel |
| Datei-Upload (Dokumente, Bilder, Logs) | Nativer Upload-Support |
| Panik-Button | `cl.Action` |
| Download-Button | `cl.Action` + `cl.File` |
| Debug-Bereich | `cl.Step` / expandierbares Element |
| Streaming | Nativ (`cl.Message.stream_token`) |

Chainlit läuft als Python-Prozess und enthält die UI-Logik. Die Systemlogik (Orchestrator, Modi, Artefakte) lebt in separaten Python-Modulen. Die SDD-Anforderung "Frontend-Backend-Trennung" ist auf **Modul-Ebene** eingehalten — die Schnittstelle zwischen UI und Orchestrator ist sauber definiert und kann ohne Aufwand in eine Prozess-Trennung (FastAPI + Chainlit als Client) überführt werden.

> **Prototyp-Entscheidung:** Monolith (ein Python-Prozess). Die modulare Struktur erlaubt die spätere Extraktion des Backends ohne Umbau der Geschäftslogik.

#### Pydantic v2 (Datenmodelle)

Das SDD definiert präzise Slot-Schemas mit Pflichtfeldern, Enums und Konsistenzregeln. Pydantic v2 ist die natürliche Implementierung dieser Schemas:
- Exploration-Slot, Strukturschritt, Algorithmusabschnitt → direkte Pydantic-Modelle
- Enum-Werte (`leer`/`teilweise`/`vollständig`/`nutzervalidiert`) → `StrEnum`
- Das Template-Schema (SDD 5.8) wird aus den Pydantic-Modellen **abgeleitet**, nicht separat gepflegt

#### jsonpatch (RFC 6902)

Das SDD schreibt RFC 6902 JSON Patch für alle Artefakt-Schreiboperationen vor (SDD 5.7). Die Bibliothek `jsonpatch` ist die Standard-Python-Implementierung. Sie wird vom Executor intern verwendet — kein anderer Code verwendet sie direkt.

#### JSON-Dateien (Persistenz)

Begründung für OP-10 (s. Abschnitt 7): JSON-Dateien mit atomarem Write-Protokoll erfüllen alle Persistenz-Constraints des SDD ohne Datenbank-Overhead. Für den Prototyp ist das die einfachste, zuverlässigste Lösung.

#### structlog (Logging)

Das SDD fordert vollständiges Logging aller LLM-Aufrufe, Orchestrator-Entscheidungen und Schreiboperationen (SDD 8.1.3). `structlog` ermöglicht strukturiertes JSON-Logging, das direkt als Analyse-Input genutzt werden kann.

### 2.3 LLM-Flexibilität

Das SDD fordert, dass das verwendete Modell ohne Code-Änderung austauschbar ist (lokal ↔ Cloud). Dies wird durch ein abstraktes `LLMClient`-Interface erreicht:

```
LLMClient (abstrakt)
├── AnthropicClient    → Anthropic API (Claude)
└── OllamaClient       → Ollama (lokale Modelle, z.B. Llama, Mistral)
```

Die Auswahl erfolgt über die Konfiguration (`.env` / `config.yaml`). Kein Modus kennt den konkreten Client — alle arbeiten gegen das Interface.

---

## 3. Komponentenübersicht

Das System besteht aus acht Komponenten-Gruppen:

| Komponente | Verantwortlichkeit | SDD-Referenz |
|---|---|---|
| **UI-Schicht (Chainlit)** | Nutzerinteraktion, Darstellung, Events | Abschnitt 2 |
| **Orchestrator** | Zentraler Steuerknoten, Zyklus-Koordination | Abschnitt 6.2, 6.3 |
| **Executor** (intern im Orchestrator) | RFC 6902 Patch-Validierung und -Ausführung | Abschnitt 5.7 |
| **Working Memory** | Operativer Zustandsspeicher | Abschnitt 6.4 |
| **Kognitive Modi** | LLM-Aufrufe, Modus-spezifische Logik | Abschnitt 6.6 |
| **Artefakt-Store** | Artefakt-Verwaltung, Versionierung, Completeness | Abschnitt 5.1–5.6 |
| **Persistenz-Schicht** | Projekt-Speicherung und -Wiederherstellung | Abschnitt 7.2, 7.3 |
| **LLM-Client** | Abstrakte LLM-Schnittstelle | Abschnitt 8.1.1 |

### 3.1 Orchestrator

**Typ:** Reiner Python-Code, kein LLM-Aufruf.

**Verantwortlichkeiten:**
- Empfang des Nutzer-Inputs (von der UI-Schicht)
- Auswertung von Steuerungsflags aus dem vorherigen Turn
- Entscheidung über den aktiven Modus (Moduswechsel-Logik gemäß SDD 6.3)
- Context-Assembly für den LLM-Aufruf (via ContextAssembler)
- Aufruf des aktiven Modus
- Validierung des LLM-Outputs gegen den Output-Kontrakt (via OutputValidator)
- Beauftragung des Executors mit Schreiboperationen
- Auslösung von Invalidierungen
- Aktualisierung von Working Memory und Completeness-State
- Persistierung nach jedem abgeschlossenen Zyklus

**Schnittstellen:**
- Eingang: Nutzer-Input (Text, Datei, Button-Event)
- Ausgang: Nutzer-Antwort (Text), aktualisierte Artefakte, aktualisierter UI-Zustand

### 3.2 Executor (intern)

**Typ:** Internes Modul des Orchestrators. Nach außen nicht sichtbar.

**Verantwortlichkeiten (gemäß SDD 5.7 Executor-Pipeline):**
1. Formale Validierung des RFC 6902 Patch-Objekts
2. Prüfung aller Pfade gegen das Template-Schema
3. Atomarer Snapshot vor Änderung
4. Patch-Anwendung via `jsonpatch`
5. Preservation-Check (nur adressierte Pfade geändert)
6. Versionserzeugung im Artefakt-Store

Bei Fehler in einem beliebigen Schritt: Restore auf Snapshot. Kein partieller Zustand.

### 3.3 Kognitive Modi

Jeder Modus ist eine Python-Klasse, die von einer gemeinsamen Basisklasse erbt.

**Gemeinsame Basis:**
- `call(context: ModeContext) → ModeOutput`
- Gibt immer `ModeOutput` zurück: `(nutzeraeusserung, patches, phasenstatus, flags)`
- Schreibt nicht direkt ins Working Memory oder in Artefakte
- Enthält den Modus-spezifischen Systemprompt

**Modi:**
| Modus | Klasse | Artefakt-Schreibrechte |
|---|---|---|
| Exploration | `ExplorationMode` | Explorationsartefakt-Slots |
| Strukturierung | `StructuringMode` | Strukturartefakt-Slots |
| Spezifikation | `SpecificationMode` | Algorithmusartefakt-Slots |
| Validierung | `ValidationMode` | keine (gibt Validierungsbericht aus) |
| Moderator | `Moderator` | keine |

> **Wichtig:** Schreibrechte sind konzeptuell — kein Modus kann direkt schreiben. Der Orchestrator/Executor führt alle Schreiboperationen aus. Die Tabelle zeigt, auf welche Artefakte ein Modus *Patches vorschlagen darf*.

### 3.4 Artefakt-Store

**Verantwortlichkeiten:**
- Verwaltung der drei Artefakte (Exploration, Struktur, Algorithmus) in ihrer aktuellen Version
- Versionierung: jede Schreiboperation erzeugt eine neue Version
- Completeness-Berechnung: aggregierte Map aller Slot-Status
- Markdown-Rendering: JSON-Artefakt → menschenlesbare Darstellung

**Wichtig:** Der Completeness-State liegt primär im Artefakt selbst (`completeness_status`-Feld pro Slot). Die Working-Memory-Map ist abgeleitet und wird nach jeder Schreiboperation neu berechnet.

### 3.5 Persistenz-Schicht

**Modell:** Ein Projekt = ein Verzeichnis auf dem Dateisystem.

**Struktur pro Projekt:**
```
data/projects/{projekt_id}/
  metadata.json           ← Projektmetadaten (SDD 7.2.1)
  working_memory.json     ← Letzter Working-Memory-Zustand
  dialog_history.jsonl    ← Vollständige Dialoghistorie (append-only)
  validation_report.json  ← Letzter Validierungsbericht
  artifacts/
    exploration/
      v0000.json          ← Leerstand (initialisiert bei Projektanlage)
      v0001.json
      ...
    structure/
      v0000.json
      ...
    algorithm/
      v0000.json
      ...
  logs/
    llm_calls.jsonl       ← Vollständige LLM I/O-Logs (SDD 8.1.3, OP-14)
    orchestrator.jsonl    ← Orchestrator-Entscheidungen, Moduswechsel
```

**Atomare Schreibvorgänge:**
Alle Schreiboperationen folgen dem Muster: Schreibe in temporäre Datei → `os.replace()` → atomar. Auf POSIX-Systemen ist `os.replace()` atomar wenn Quelle und Ziel auf demselben Dateisystem liegen.

### 3.6 LLM-Client

```
LLMClient (ABC)
  └── complete(messages, system_prompt, **kwargs) → LLMResponse
  └── stream(messages, system_prompt, **kwargs) → AsyncIterator[str]

AnthropicClient(LLMClient)
  → anthropic.AsyncAnthropic

OllamaClient(LLMClient)
  → httpx (async REST-Calls an Ollama API)
```

Der aktive Client wird beim Start über die Konfiguration gewählt. Kein Modus importiert den konkreten Client.

---

## 4. Komponentendiagramm

```
┌─────────────────────────────────────────────────────────────────────┐
│  UI-Schicht (Chainlit)                                               │
│                                                                      │
│  ┌──────────────┐  ┌───────────────┐  ┌───────────┐  ┌──────────┐  │
│  │ Chat-Handler  │  │ Artefakt-Panel │  │ Debug-    │  │ Event-   │  │
│  │ (Nachrichten, │  │ (3 Artefakte,  │  │ Panel     │  │ Handler  │  │
│  │  Datei-Upload)│  │  live-update)  │  │           │  │ (Panic,  │  │
│  └──────┬───────┘  └───────┬───────┘  └─────┬─────┘  │  DL, ..) │  │
│         │                   │                │         └────┬─────┘  │
└─────────┼───────────────────┼────────────────┼──────────────┼────────┘
          │ Nutzer-Input       │ Artefakt-State │ Debug-State  │ Events
          ▼                   ▲                ▲              ▼
┌─────────────────────────────────────────────────────────────────────┐
│  Orchestrator                                                        │
│                                                                      │
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────────┐  │
│  │ ZyklusKoordinator│  │ ContextAssembler  │  │ OutputValidator    │  │
│  │ (11-Schritt-     │  │ (Kontext für LLM- │  │ (Output-Kontrakt,  │  │
│  │  Zyklus SDD 6.3) │  │  Aufruf SDD 6.5)  │  │  SDD 6.5.2)        │  │
│  └────────┬────────┘  └──────────────────┘  └────────────────────┘  │
│           │                                                           │
│  ┌────────▼────────────────────────────────────────────────────────┐ │
│  │ Executor (intern)                                                │ │
│  │  PatchValidator → Snapshot → PatchApplicator → PreservationCheck│ │
│  │  → InvalidationEngine → Versioning (SDD 5.7)                    │ │
│  └─────────────────────────────────────────────────────────────────┘ │
└──────────┬────────────────────────────────────────────────────────────┘
           │ mode.call(context)                   ▲ ModeOutput
           ▼                                      │
┌──────────────────────────────────────────────────────────────────────┐
│  Kognitive Modi                                                       │
│                                                                       │
│  ExplorationMode │ StructuringMode │ SpecificationMode │ Moderator    │
│  ValidationMode                                                       │
│                                                                       │
│  Jeder Modus: call(context) → ModeOutput(text, patches, flags)       │
└──────────────────────────┬───────────────────────────────────────────┘
                           │ LLMClient.complete(...)
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  LLM-Client                                                           │
│  AnthropicClient  │  OllamaClient                                     │
└──────────────────────────────────────────────────────────────────────┘

     Orchestrator liest/schreibt:
     ┌────────────────┐    ┌──────────────────┐    ┌──────────────────┐
     │ Working Memory │    │  Artefakt-Store   │    │ Persistenz-      │
     │ (Laufzeit-     │    │  (3 Artefakte +   │    │ Schicht          │
     │  Zustand)      │    │   Versionen +     │    │ (JSON-Dateien)   │
     │                │    │   Completeness)   │    │                  │
     └────────────────┘    └──────────────────┘    └──────────────────┘
```

---

## 5. Datenfluss: Orchestrator-Zyklus

Ein vollständiger Turn, entsprechend SDD Abschnitt 6.3:

```
Nutzer-Input (Text / Datei / Button-Event)
    │
    ▼
[1] Orchestrator.process_turn(input)
    │
    ▼
[2] WorkingMemory.update(input)
    │
    ▼
[3] Flags aus letztem Turn auswerten
    ├── phase_complete → Moderator aktivieren (nach Turn)
    ├── escalate / blocked → Moderator aktivieren
    └── → Modus bleibt aktiv
    │
    ▼
[4] Aktiven Modus bestimmen (Moduswechsel-Logik)
    │
    ▼
[5] ContextAssembler.build(modus, artefakte, working_memory, history)
    → Systemprompt + Template-Schema + Artefakte (RO) + Completeness +
      Working-Memory-Auszug + Dialoghistorie (N Turns) +
      ggf. Moderator-Kontext / Validierungsbericht / EMMA-Katalog
    │
    ▼
[6] modus.call(context)
    └── LLMClient.complete(messages) → LLM-Antwort
    │
    ▼
[7] OutputValidator.validate(llm_output)
    ├── OK → weiter
    └── Verletzung → Fehlerbehandlung, kein Zustandsänderung,
                     Nutzer-Meldung, Turn abgebrochen
    │
    ▼
[8] Executor.apply_patches(patches)  [wenn artefakt_updated flag gesetzt]
    ├── PatchValidator: RFC 6902 syntaktisch valide?
    ├── PatchValidator: Pfade im Template-Schema registriert?
    ├── Snapshot: atomarer JSON-Snapshot des aktuellen Artefakts
    ├── PatchApplicator: jsonpatch.apply_patch(artefakt, patches)
    ├── PreservationCheck: nur adressierte Pfade geändert?
    ├── InvalidationEngine: Strukturschritt geändert?
    │   └── ja → alle referenzierten Algorithmusabschnitte → invalidiert
    └── Versioning: neue Artefaktversion erzeugen
    │
    ▼
[9] CompletenessCalculator.recalculate(artefakte)
    → WorkingMemory.completeness_state aktualisieren
    │
    ▼
[10] ProgressTracker.update(phasenstatus_from_modus, slot_counts)
     → WorkingMemory.phasenstatus, befuellte_slots, bekannte_slots
    │
    ▼
[11] ProjectRepository.save(projekt)  [atomar]
    │
    ▼
Rückgabe an UI-Schicht:
    ├── nutzeraeusserung → Chat-Bereich
    ├── aktualisierte Artefakte → Artefakt-Panel
    ├── phasenstatus + slot_counts → Fortschrittsanzeige
    └── working_memory → Debug-Panel
```

---

## 6. Projektstruktur

```
digitalisierungsfabrik/
│
├── app.py                          # Chainlit-Einstiegspunkt
├── config.py                       # Konfiguration (pydantic-settings)
├── .env.example                    # Konfig-Template
├── requirements.txt
├── chainlit.md                     # Chainlit Begrüßungstext
│
├── core/                           # Systemlogik
│   ├── orchestrator.py             # Orchestrator-Zyklus (SDD 6.3)
│   ├── context_assembler.py        # Kontext-Zusammenstellung (SDD 6.5)
│   ├── output_validator.py         # Output-Kontrakt-Prüfung (SDD 6.5.2)
│   ├── executor.py                 # RFC 6902 Executor (SDD 5.7)
│   ├── working_memory.py           # Working-Memory-Datenmodell (SDD 6.4)
│   └── progress_tracker.py        # Phasenstatus + Slot-Zähler (SDD 6.7)
│
├── modes/                          # Kognitive Modi (SDD 6.6)
│   ├── base.py                     # Abstrakte Basisklasse + ModeContext/ModeOutput
│   ├── exploration.py              # Explorationsmodus (SDD 6.6.1)
│   ├── structuring.py              # Strukturierungsmodus (SDD 6.6.2)
│   ├── specification.py            # Spezifikationsmodus (SDD 6.6.3)
│   ├── validation.py               # Validierungsmodus (SDD 6.6.4)
│   └── moderator.py                # Moderator (SDD 6.6.5)
│
├── artifacts/                      # Artefakt-Verwaltung (SDD Abschnitt 5)
│   ├── models.py                   # Pydantic-Modelle aller drei Artefakte
│   ├── store.py                    # Artefakt-Store + Versionierung
│   ├── template_schema.py          # Template-Schema (abgeleitet aus models.py)
│   ├── completeness.py             # Completeness-State-Berechnung (SDD 5.6)
│   └── renderer.py                 # JSON-Artefakt → Markdown (OP-19)
│
├── persistence/                    # Persistenz-Schicht (SDD 7.2, 7.3)
│   ├── project_repository.py       # Projekt CRUD
│   ├── atomic_writer.py            # Atomarer Datei-Write
│   └── models.py                   # Persistenz-Datenmodelle
│
├── llm/                            # LLM-Client-Abstraktion
│   ├── base.py                     # Abstraktes Interface LLMClient
│   ├── anthropic_client.py         # Anthropic Claude
│   └── ollama_client.py            # Ollama (lokale Modelle)
│
├── ui/                             # UI-Hilfsmodule
│   ├── artifact_panel.py           # Artefakt-Rendering für Chainlit
│   └── debug_panel.py              # Debug-Bereich für Chainlit
│
├── prompts/                        # Systemprompts der Modi (Markdown)
│   ├── exploration.md
│   ├── structuring.md
│   ├── specification.md
│   ├── validation.md
│   └── moderator.md
│
├── static/                         # Statische Ressourcen
│   └── emma_catalog.json           # EMMA-Aktionskatalog (SDD 8.3)
│
├── data/                           # Laufzeit-Daten (gitignored)
│   └── projects/                   # Projektverzeichnisse
│
└── tests/
    ├── test_executor.py
    ├── test_artifacts.py
    ├── test_orchestrator.py
    ├── test_completeness.py
    └── test_persistence.py
```

### Konfiguration (`.env` / `config.py`)

Alle systemrelevanten Parameter sind konfigurierbar — kein Hardcoding (SDD 8.1.1):

| Parameter | Beschreibung | Standard |
|---|---|---|
| `LLM_PROVIDER` | `anthropic` / `ollama` | `anthropic` |
| `LLM_MODEL` | Modell-ID | `claude-opus-4-6` |
| `LLM_API_KEY` | API-Key | — |
| `OLLAMA_BASE_URL` | URL für Ollama | `http://localhost:11434` |
| `DIALOG_HISTORY_N` | Turns an Dialoghistorie für Modi | `3` |
| `DIALOG_HISTORY_MODERATOR_M` | Turns für Moderator (M > N) | `10` |
| `TOKEN_WARN_THRESHOLD` | Token-Warnschwelle für Partitionierung | `80000` |
| `TOKEN_HARD_LIMIT` | Hartes Tokenlimit, Turn-Abbruch | `100000` |
| `AUTOMATION_WARN_THRESHOLD` | Anzahl nicht-automatisierbarer Schritte | `1` |
| `DATA_DIR` | Wurzelverzeichnis für Projektdaten | `./data` |
| `LOG_LEVEL` | Log-Level | `INFO` |
| `LLM_LOG_ENABLED` | LLM I/O-Logging aktiv | `true` |

---

## 7. Schließung kritischer Open Points

Dieser Abschnitt schließt die vier Blocker-OPs, die für die Implementierung zwingend notwendig sind.

---

### OP-01: JSON-Schema Artefakte

**Entscheidung:** Die formale Schemadefinition aller drei Artefakte wird durch **Pydantic-v2-Modelle** in `artifacts/models.py` implementiert.

**Mapping SDD → Pydantic:**

```
# Exploration
ExplorationSlot:
  slot_id: str
  titel: str
  inhalt: str
  completeness_status: CompletenessStatus  ← StrEnum

ExplorationArtefakt:
  version_id: int
  prozesszusammenfassung: ExplorationSlot
  slots: list[ExplorationSlot]

# Struktur
Strukturschritt:
  schritt_id: str
  titel: str
  beschreibung: str
  typ: SchrittTyp  ← StrEnum: aktion/entscheidung/schleife/ausnahme
  reihenfolge: int
  nachfolger: list[str]
  bedingung: str | None
  ausnahme_beschreibung: str | None
  algorithmus_ref: list[str]  ← min 1
  algorithmus_status: AlgorithmusStatus  ← StrEnum
  completeness_status: CompletenessStatus
  spannungsfeld: str | None

Strukturartefakt:
  version_id: int
  prozesszusammenfassung: str
  schritte: list[Strukturschritt]

# Algorithmus
EmmaAktion:
  aktion_id: str
  aktionstyp: EmmaAktionstyp  ← StrEnum (18 Werte aus EMMA-Katalog)
  parameter: dict[str, Any]
  nachfolger: str  ← aktion_id oder "END"
  emma_kompatibel: bool
  kompatibilitaets_hinweis: str | None

Algorithmusabschnitt:
  abschnitt_id: str
  struktur_ref: str
  titel: str
  status: AbschnittStatus  ← StrEnum
  completeness_status: CompletenessStatus
  aktionen: list[EmmaAktion]

Algorithmusartefakt:
  version_id: int
  prozesszusammenfassung: str
  abschnitte: list[Algorithmusabschnitt]
```

**Template-Schema:** Wird programmatisch aus den Pydantic-Modellen abgeleitet — alle gültigen JSON-Pfade, Feldtypen und Enum-Werte. Dies ist die single source of truth. Kein separates Schema-Dokument.

**RFC 6902 Pfad-Konventionen:**
```
# Exploration
/slots/{slot_id}/inhalt
/slots/{slot_id}/completeness_status
/prozesszusammenfassung/inhalt

# Struktur
/schritte/{schritt_id}/beschreibung
/schritte/{schritt_id}/completeness_status
/schritte/{schritt_id}/algorithmus_status
... (add/remove für neue/gelöschte Schritte)

# Algorithmus
/abschnitte/{abschnitt_id}/aktionen
/abschnitte/{abschnitt_id}/completeness_status
/abschnitte/{abschnitt_id}/status
```

---

### OP-10: Persistenztechnologie

**Entscheidung:** JSON-Dateien mit atomarem Write-Protokoll.

**Begründung:**
- Kein Datenbank-Setup, keine externe Abhängigkeit
- On-Premise-fähig ohne Installation
- Atomar realisierbar via `os.replace()` (POSIX-atomar)
- Versionierung als separate Dateien trivial (keine DB-Migrationen)
- Vollständig lesbar ohne Tools (Debugging, Analyse)
- Für Prototyp-Größen (< 100 Prozessschritte, Single-User) performant genug

**Atomaritäts-Protokoll:**
```
Schreibe vollständigen Projektzustand in .tmp-Datei
→ os.replace(tmp_path, target_path)  # POSIX-atomar
```
Ein unterbrochener Write hinterlässt maximal eine .tmp-Datei — der alte Zustand bleibt intakt.

**Versionierung:** Jede Artefaktversion als eigene Datei `v{n:04d}.json`. Keine Deletions — append-only.

**Projektisolation:** Jedes Projekt hat sein eigenes Verzeichnis. Kein shared state zwischen Projekten.

**Zukünftige Migration:** SQLite oder PostgreSQL wäre später möglich, indem `ProjectRepository` austauschbar implementiert wird. Das Interface bleibt identisch.

---

### OP-19: Markdown-Renderlogik

**Entscheidung:** Renderer in `artifacts/renderer.py` mit festgelegten Regeln pro Artefakt-Typ.

**Explorationsartefakt → Markdown:**
```
# Prozesszusammenfassung
{inhalt}

## {slot.titel}  [{completeness_status}]
{slot.inhalt}
```

**Strukturartefakt → Markdown:**
```
# Prozesszusammenfassung
{text}

## Prozessschritte

### {reihenfolge}. {titel}  [TYP: {typ}] [{completeness_status}]
{beschreibung}
Nachfolger: {nachfolger_liste}
⚠️ INVALIDIERT  ← wenn algorithmus_status = invalidiert
🔴 Spannungsfeld: {spannungsfeld}  ← wenn gesetzt
```

**Algorithmusartefakt → Markdown:**
```
# Prozesszusammenfassung
{text}

## Algorithmusabschnitte

### {titel}  [{status}] [{completeness_status}]
Bezug: Strukturschritt {struktur_ref}

| Nr | Aktion | Parameter | Nachfolger | EMMA-OK |
|---|---|---|---|---|
| {aktion_id} | {aktionstyp} | {parameter} | {nachfolger} | ✓/✗ |
```

**Visuelle Markierung invalidierter Slots (FR-F-05):** In Chainlit werden invalidierte Abschnitte mit einem roten Badge (`⚠️ INVALIDIERT`) markiert. Die Chainlit-Custom-Element-Komponente für den Artefakt-Panel wertet `algorithmus_status` / `status` aus und wendet entsprechende CSS-Klassen an.

---

### OP-16: Erfolgs-/Fehlerkanten im Kontrollflussgraph

**Entscheidung für Prototyp:** Fehlerbehandlung wird als explizite `DECISION`-Knoten im Algorithmusartefakt modelliert.

**Muster:**
```
Aktion_X → DECISION (Erfolg?) → [JA: Aktion_Y] / [NEIN: DECISION (Fehlertyp?) → ...]
```

Damit ist kein neues Feld im Schema nötig. Der Kontrollflussgraph ist vollständig mit den bestehenden `aktionen` und `nachfolger`-Feldern darstellbar.

**Post-Prototyp:** Einführung expliziter `success_edge` / `error_edge`-Felder pro Aktion — als optionale Erweiterung des bestehenden Schemas, rückwärtskompatibel.

---

## 8. Implementierungsreihenfolge

Jeder Schritt ist ein eigenständig testbares Inkrement.

### Schritt 1: Datenmodelle + Persistenz
**Ziel:** Pydantic-Modelle aller Artefakte + Projekt-CRUD + atomare Writes
**Testbar:** Artefakt anlegen, Slot schreiben, Version laden, Projekt speichern/laden
**Module:** `artifacts/models.py`, `persistence/`, `config.py`

### Schritt 2: Executor + Template-Schema
**Ziel:** RFC 6902 Patch-Pipeline vollständig implementiert
**Testbar:** Gültiger Patch auf Artefakt anwenden, ungültiger Patch abgelehnt, Snapshot & Rollback
**Module:** `core/executor.py`, `artifacts/template_schema.py`

### Schritt 3: Orchestrator-Skeleton + Working Memory
**Ziel:** Orchestrator-Zyklus ohne LLM (stub-Modi)
**Testbar:** Zyklus läuft durch, Working Memory wird aktualisiert, Persistenz nach Zyklus
**Module:** `core/orchestrator.py`, `core/working_memory.py`, `core/progress_tracker.py`

### Schritt 4: LLM-Client + Erster Modus (Exploration)
**Ziel:** Vollständiger erster LLM-Turn mit Explorationsmodus
**Testbar:** LLM-Aufruf, Patch-Output, Artefakt-Update, Completeness-State aktualisiert
**Module:** `llm/`, `modes/base.py`, `modes/exploration.py`, `core/context_assembler.py`, `core/output_validator.py`, `prompts/exploration.md`

### Schritt 5: Chainlit-Frontend
**Ziel:** Vollständige UI — Chat, Artefakt-Panel, Debug-Panel, Panik-Button, Download
**Testbar:** Kompletter Nutzerdialog, Artefakt-Anzeige live, alle Buttons funktional
**Module:** `app.py`, `ui/`

### Schritt 6: Moderator + Phasenwechsel
**Ziel:** Vollständiger Phasenwechsel-Zyklus inkl. Moderator
**Module:** `modes/moderator.py`, Orchestrator-Moduswechsel-Logik erweitern

### Schritt 7: Strukturierungsmodus
**Module:** `modes/structuring.py`, `prompts/structuring.md`

### Schritt 8: Spezifikationsmodus
**Module:** `modes/specification.py`, `prompts/specification.md`

### Schritt 9: Validierungsmodus + Korrekturschleife
**Module:** `modes/validation.py`, `prompts/validation.md`

### Schritt 10: End-to-End-Durchlauf + Stabilisierung
**Ziel:** Vollständiger Durchlauf Exploration → Validierung mit echtem Prozess

---

## 9. Offene Punkte (HLA-Ebene)

Die folgenden OPs bleiben offen und werden im Implementierungsdesign-Dokument behandelt:

| ID | Thema | Auswirkung |
|---|---|---|
| OP-02 | EMMA-Parameterdefinition | Felder in `EmmaAktion.parameter` — erst vollständig definierbar wenn EMMA-Spezifikation vorliegt. Prototyp: `dict[str, Any]` |
| OP-03 | Versionshistorie im UI | UI-Detail: Liste oder Timeline? Chainlit-Umsetzung im Schritt 5 klären |
| OP-04 | Maximale Versionszahl | Prototyp: unbegrenzt. Ggf. konfigurierbares Limit post-Prototyp |
| OP-05 | Token-Schwellenwerte | `TOKEN_WARN_THRESHOLD` und `TOKEN_HARD_LIMIT` in Konfiguration als Platzhalter. Konkrete Werte nach erstem Testlauf mit echtem Prozess kalibrieren |
| OP-06 | nearing_completion-Kriterien | Pro Modus im Implementierungsdesign definieren |
| OP-07 | Steuerungsflags vollständig | Basis-Flags (SDD 6.4.1) im Implementierungsdesign vervollständigen |
| OP-11 | Dialoghistorie-Umfang | Prototyp: vollständige History speichern (`.jsonl` append-only). Größe nach Testläufen abschätzen |
| OP-12 | Projektliste im UI | Chainlit-Startseite mit Projekt-Auswahl: im Schritt 5 definieren |
| OP-14 | LLM-Log-Format | `logs/llm_calls.jsonl` mit Feldern: `timestamp`, `modus`, `turn_id`, `input_tokens`, `output_tokens`, `input` (vollständig), `output` (vollständig). Format ist damit hinreichend definiert — Schritt 4 implementiert |
| OP-17 | Eventlog-Format | Prototyp: Eventlog-Upload vorerst als Freitext behandeln, kein strukturiertes Parsing |
| OP-20 | Wiederholte Output-Kontrakt-Verletzung | Prototyp: kein Retry. Fehlermeldung an Nutzer, Turn abgebrochen. Post-Prototyp: konfigurierbares Retry-Limit + Moderator-Eskalation |

---

*Dokument-Ende. Nächstes Dokument: Implementierungsdesign Schritt 1 — Datenmodelle & Persistenz.*
