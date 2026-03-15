# Aufgabe: E2E-Test für Moderator-Explorer-Interaktion

Schreibe einen End-to-End-Test in `backend/tests/test_e2e_moderator.py`, der den kompletten Dialog aus `frontend/test-texte/dialog-e2e-moderator.json` gegen das **echte, laufende System** (mit echtem LLM) durchspielt und auswertet.

## Architektur-Kontext

Der Test nutzt den **Orchestrator direkt** (kein HTTP, kein WebSocket). Das ist der gleiche Codepfad wie die WebSocket-Handler, nur ohne Netzwerk.

### Wie der Orchestrator funktioniert:

```python
from core.orchestrator import Orchestrator, TurnInput
from persistence.database import Database
from persistence.project_repository import ProjectRepository
from config import Settings

settings = get_settings()  # Lädt .env (ANTHROPIC_API_KEY etc.)
db = Database(":memory:")  # oder settings.database_path
repo = ProjectRepository(db)

# Projekt erstellen — startet IMMER im Moderator-Modus
project = repo.create("E2E Test Eingangsrechnung")

# Orchestrator mit echten Modes bauen
from llm.factory import create_llm_client
from modes.exploration import ExplorationMode
from modes.moderator import Moderator

llm = create_llm_client(settings)
orchestrator = Orchestrator(
    repository=repo,
    modes={"exploration": ExplorationMode(llm_client=llm), "moderator": Moderator(llm_client=llm)},
    settings=settings,
)

# Turn verarbeiten
result = await orchestrator.process_turn(project.projekt_id, TurnInput(text="Hallo"))
# result.nutzeraeusserung  → Antworttext
# result.flags             → ["phase_complete", "return_to_mode", ...]
# result.working_memory    → WorkingMemory mit aktiver_modus, vorheriger_modus, etc.
# result.phasenstatus      → "in_progress", "phase_complete", etc.
```

### Wie der Panik-Button funktioniert:

Der Panik-Button wird **nicht** über den Orchestrator getriggert, sondern das Frontend (bzw. hier der Test) setzt manuell den Modus um und schickt dann einen Turn. So wie in `backend/api/websocket.py` Zeilen 235-254:

```python
# Panik-Button simulieren:
project = repo.load(project_id)
project.working_memory.vorheriger_modus = project.working_memory.aktiver_modus
project.working_memory.aktiver_modus = "moderator"
project.aktiver_modus = "moderator"
repo.save(project)

# Dann den Moderator-Turn ausführen mit der User-Nachricht:
result = await orchestrator.process_turn(project_id, TurnInput(text="User-Nachricht hier"))
```

### Wie `phase_complete` funktioniert:

Wenn der Explorer `Flag.phase_complete` in seinem Output zurückgibt, wechselt der Orchestrator automatisch den Modus auf "moderator" (siehe `orchestrator.py` Zeilen 163-172). Das passiert am Ende von `process_turn()`, d.h. der nächste Turn läuft dann im Moderator.

### Artefakt auslesen:

```python
project = repo.load(project_id)
artifact = project.exploration_artifact  # ExplorationArtifact
for slot_id, slot in artifact.slots.items():
    print(f"{slot_id}: [{slot.completeness_status}] {slot.inhalt}")
```

## Test-Ablauf

Lies die Datei `frontend/test-texte/dialog-e2e-moderator.json`. Dort findest du:

1. **`user_inputs`** — Eine Queue von 15 User-Nachrichten (U1-U15), die nacheinander eingegeben werden
2. **`system_events`** — 3 Systemereignisse (Systemstart, Panik-Button, phase_complete)
3. **`test_checkpoints`** — 10 Prüfpunkte (CP1-CP10) die nach bestimmten Inputs geprüft werden
4. **`expected_artifact`** — Das erwartete Zielartefakt nach Abschluss aller Inputs

### Schritt-für-Schritt Ablauf des Tests:

```
1. Projekt erstellen
2. Systemstart: orchestrator.process_turn(projekt_id, TurnInput(text="[Systemstart]"))
   → Moderator begrüßt (S0)
   → CP prüfen: Modus ist moderator, keine Flags, keine Patches

3. U1 senden: TurnInput(text=U1.message)
   → CP1 prüfen

4. U2 senden: TurnInput(text=U2.message)
   → CP2 prüfen

5. U3 senden: TurnInput(text=U3.message)
   → CP3 prüfen: Modus muss nach diesem Turn auf "exploration" gewechselt haben

6. U4-U7 senden: Normale Explorer-Turns
   → CP4 nach U4 prüfen

7. Nach U7: Panik-Button simulieren (siehe oben), dann U8 als Turn senden
   → CP5 + CP6 prüfen

8. U9 senden: Moderator-Gespräch
9. U10 senden: Moderator gibt zurück an Explorer
   → CP7 prüfen

10. U11 senden: Explorer mit Vereinbarung
    → CP8 prüfen

11. U12-U13 senden: Restliche Explorer-Turns

12. U14 senden: "Mir fällt nichts mehr ein"
    → CP9 prüfen
    → Wenn Explorer hier phase_complete meldet: Moderator wird automatisch aktiviert
    → Falls nicht: noch einmal nachfragen oder prüfen ob nearing_completion

13. Falls Moderator aktiv: U15 senden → Phasenwechsel
    → CP10 prüfen
```

**WICHTIG: Der Explorer meldet eventuell NICHT sofort `phase_complete` nach U14.** Das LLM entscheidet das. Falls nach U14 der Modus noch "exploration" ist, sende eine Folgenachricht wie "Ja das war wirklich alles, wir können zur nächsten Phase" und prüfe erneut. Baue eine Schleife ein die maximal 3 Zusatznachrichten sendet bevor der Test fehlschlägt.

## Was der Test prüfen soll

### A) Moduswechsel-Prüfungen (hart, müssen exakt stimmen):

Für jeden Checkpoint aus `test_checkpoints`:
- `aktiver_modus` im WorkingMemory == erwarteter Modus
- `vorheriger_modus` == erwarteter Wert (wo angegeben)
- Flags enthalten/enthalten nicht die erwarteten Werte
- `aktive_phase` == erwartete Phase (wo angegeben)

### B) Artefakt-Prüfungen (weich, sinngemäß):

Vergleiche das tatsächliche Artefakt mit `expected_artifact` aus der JSON-Datei:
- **Für jeden Slot:** Prüfe ob der `completeness_status` mindestens so hoch ist wie erwartet (`leer` < `teilweise` < `vollstaendig`)
- **Für jeden Slot:** Prüfe ob die **Kern-Keywords** aus dem erwarteten `inhalt` im tatsächlichen Inhalt vorkommen. Definiere pro Slot 3-5 Keywords die enthalten sein MÜSSEN. Beispiel für `prozessausloeser`: `["Rechnung", "Post", "E-Mail", "rechnungen@firma.de"]`
- **Für `prozesszusammenfassung`:** Prüfe dass `inhalt` NICHT leer ist und NICHT vom User diktiert wurde (der User hat in U14 nur "Mir fällt nichts mehr ein" gesagt)
- **Kein Slot darf `leer` sein** am Ende

### C) Kontext-Übergabe-Prüfungen:

- **CP4 (Moderator→Explorer):** Nach U4 müssen Infos aus U2 (das im Moderator-Modus gesagt wurde — "400-500 Rechnungen", "Eingangsrechnungsverarbeitung") im Artefakt stehen. Die Dialog-History muss die Moderator-Turns enthalten.
- **CP7 (Moderator→Explorer nach Eskalation):** Nach U10 muss der Modus wieder "exploration" sein. Lade die dialog_history (`repo.load_dialog_history(project_id)`) und prüfe, dass die Moderator-Antworten (in denen die Vereinbarung "kürzer fragen" formuliert wurde) in der History stehen — denn der Explorer bekommt sie über `context.dialog_history`.
- **CP5 (Artefakt überlebt Eskalation):** Nach dem Panik-Button müssen alle vorher befüllten Slots noch da sein. `befuellte_slots` im WorkingMemory muss > 0 sein.

### D) Datenübergabe Moderator↔Explorer:

Sammle nach JEDEM Turn folgende Daten in einer Liste/Log-Struktur:
```python
turn_log = {
    "turn_nr": int,
    "user_input_id": "U1",  # oder "S0" für Systemstart
    "active_mode_before": str,  # Modus VOR dem Turn
    "active_mode_after": str,   # Modus NACH dem Turn
    "flags": list[str],
    "phasenstatus": str,
    "befuellte_slots": int,
    "bekannte_slots": int,
    "nutzeraeusserung_preview": str,  # Erste 200 Zeichen der Antwort
    "vorheriger_modus": str | None,
    "aktive_phase": str,
}
```

Am Ende des Tests: Gib dieses Log als übersichtliche Tabelle aus (print, nicht assert). Das hilft bei der Fehleranalyse.

## Teststruktur

```python
"""E2E-Test: Moderator-Explorer-Interaktion mit echtem LLM.

Testet den kompletten Dialog-Flow:
Moderator-Begrüßung → Explorer → Eskalation → Moderator → Explorer → Phase Complete → Phasenwechsel

Benötigt: ANTHROPIC_API_KEY in .env
Laufzeit: ca. 3-5 Minuten (15+ LLM-Calls)
"""

import json
import pytest
from pathlib import Path

# Markierung damit der Test nicht bei jedem pytest-Lauf mitläuft:
pytestmark = pytest.mark.e2e

DIALOG_PATH = Path(__file__).resolve().parent.parent / "frontend" / "test-texte" / "dialog-e2e-moderator.json"

@pytest.fixture
async def setup():
    """Projekt + Orchestrator mit echtem LLM erstellen."""
    ...

@pytest.mark.asyncio
async def test_e2e_moderator_explorer_flow(setup):
    """Kompletter E2E-Durchlauf mit allen 10 Checkpoints."""
    ...
```

## Wichtige Details

- Nutze `pytest.mark.e2e` damit der Test nicht bei normalem `pytest` mitläuft. Man muss ihn explizit mit `pytest -m e2e` starten.
- Jeder LLM-Call kann 5-15 Sekunden dauern. Setze Timeouts großzügig (10 Minuten für den ganzen Test).
- Die LLM-Antworten sind nicht-deterministisch. Deshalb:
  - Moduswechsel: HART prüfen (die Logik ist deterministisch im Orchestrator)
  - Slot-Inhalte: WEICH prüfen (Keywords, nicht exakter Text)
  - Moderator-Aktionen: HART prüfen (exploration_starten, zurueck_zum_modus etc. kommen aus dem Tool-Call)
- Wenn ein Checkpoint fehlschlägt, gib den gesamten Turn-Log bis zu diesem Punkt aus, damit man debuggen kann.
- Der Test läuft gegen das echte Anthropic API. Der ANTHROPIC_API_KEY muss in `backend/.env` stehen.
- Arbeite im Verzeichnis `backend/`. Alle Imports sind relativ zum backend-Package.
- Prüfe VOR dem Schreiben des Tests welche pytest-Plugins installiert sind (`pip list | grep pytest`). Du brauchst mindestens `pytest-asyncio`.
- Nutze `asyncio_mode = "auto"` in der pytest-Config falls nötig.
- Schreibe den Test in EINE Datei. Keine Hilfsdateien, keine Fixtures in conftest.
- Gib am Ende des Tests eine Zusammenfassung aus:
  ```
  === E2E Test Summary ===
  Turns executed: 17
  Checkpoints passed: 10/10
  Final mode: structuring
  Final phase: strukturierung
  Slots filled: 9/9

  Turn Log:
  | # | Input | Mode Before | Mode After | Flags | Slots |
  |---|-------|-------------|------------|-------|-------|
  | 1 | S0    | moderator   | moderator  | []    | 0/9   |
  | 2 | U1    | moderator   | moderator  | []    | 0/9   |
  ...
  ```
