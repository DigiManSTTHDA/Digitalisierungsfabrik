"""Interaktiver CLI-Dialog mit dem Explorationsmodus.

Verwendung (aus backend/):
    python -m scripts.interactive_explorer
    python -m scripts.interactive_explorer --db explorer_test.sqlite

Du unterhältst dich live mit dem Explorer. Nach jedem Turn siehst du:
- Die Antwort des Explorers
- Alle Slot-Inhalte mit Status
- Was sich geändert hat (Diff zum vorherigen Turn)

Beenden: leere Eingabe, 'q', 'quit' oder Ctrl+C.
Sonderbefehle:
    /slots   — Zeigt alle Slots im Detail
    /reset   — Startet ein neues Projekt
    /export  — Exportiert das Artefakt als JSON
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import Settings
from core.models import Project
from core.orchestrator import Orchestrator, TurnInput
from llm.factory import create_llm_client
from modes.base import BaseMode
from modes.exploration import ExplorationMode
from persistence.database import Database
from persistence.project_repository import ProjectRepository

# --- Farben (ANSI) ---
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
DIM = "\033[2m"
BOLD = "\033[1m"
RESET = "\033[0m"


def _print_header(settings: Settings) -> None:
    print(f"\n{BOLD}{'=' * 70}")
    print("  DIGITALISIERUNGSFABRIK — Interaktiver Explorer-Test")
    print(f"{'=' * 70}{RESET}")
    print(f"  Provider : {settings.llm_provider}")
    print(f"  Modell   : {settings.llm_model}")
    print("  Befehle  : /slots /reset /export | q/quit/Enter = Beenden")
    print(f"{BOLD}{'=' * 70}{RESET}\n")


def _print_slots(project: Project, previous_slots: dict | None = None) -> None:
    """Zeigt alle Slots mit Status und markiert Änderungen."""
    slots = project.exploration_artifact.slots
    filled = sum(1 for s in slots.values() if s.inhalt and s.inhalt.strip())
    total = len(slots)

    print(f"\n  {BOLD}Slots ({filled}/{total} befüllt):{RESET}")
    print(f"  {'─' * 66}")

    for slot_id, slot in slots.items():
        status = slot.completeness_status.value
        inhalt = slot.inhalt or ""

        # Änderungsmarker
        changed = ""
        if previous_slots is not None:
            prev = previous_slots.get(slot_id)
            if prev is None:
                changed = f" {GREEN}[NEU]{RESET}"
            elif prev.get("inhalt", "") != inhalt:
                changed = f" {YELLOW}[GEÄNDERT]{RESET}"

        # Status-Farbe
        if status == "vollstaendig":
            status_color = GREEN
        elif status == "teilweise":
            status_color = YELLOW
        else:
            status_color = DIM

        # Inhalt kürzen für Übersicht
        if len(inhalt) > 100:
            display = inhalt[:100] + "..."
        else:
            display = inhalt or "(leer)"

        print(f"  {status_color}[{status:15}]{RESET} {BOLD}{slot_id}{RESET}{changed}")
        if inhalt:
            # Mehrzeiligen Inhalt einrücken
            for line in display.split("\n"):
                print(f"                    {line}")
        else:
            print(f"                    {DIM}(leer){RESET}")

    print(f"  {'─' * 66}")


def _print_slot_detail(project: Project) -> None:
    """Zeigt alle Slots mit vollem Inhalt."""
    slots = project.exploration_artifact.slots
    print(f"\n{BOLD}{'=' * 70}")
    print("  ALLE SLOTS — VOLLSTÄNDIGER INHALT")
    print(f"{'=' * 70}{RESET}")

    for slot_id, slot in slots.items():
        status = slot.completeness_status.value
        print(f"\n  {BOLD}{slot.titel}{RESET} ({slot_id}) [{status}]")
        print(f"  {'─' * 50}")
        if slot.inhalt:
            for line in slot.inhalt.split("\n"):
                print(f"    {line}")
        else:
            print(f"    {DIM}(leer){RESET}")

    print(f"\n{'=' * 70}\n")


def _slots_snapshot(project: Project) -> dict:
    """Erstellt einen Snapshot der aktuellen Slot-Inhalte für Diff."""
    return {
        sid: {"inhalt": s.inhalt, "status": s.completeness_status.value}
        for sid, s in project.exploration_artifact.slots.items()
    }


def _export_artifact(project: Project) -> None:
    """Exportiert das Artefakt als JSON."""
    data = project.exploration_artifact.model_dump()
    filename = f"explorer_export_{project.projekt_id[:8]}.json"
    Path(filename).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  {GREEN}Exportiert nach: {filename}{RESET}\n")


async def _create_session(settings: Settings, db_path: str) -> tuple:
    """Erstellt eine neue Session mit Orchestrator und Projekt."""
    db = Database(db_path)
    repo = ProjectRepository(db)
    project = repo.create("Explorer-Test")
    llm_client = create_llm_client(settings)
    modes: dict[str, BaseMode] = {"exploration": ExplorationMode(llm_client=llm_client)}
    orchestrator = Orchestrator(repository=repo, modes=modes, settings=settings)
    return orchestrator, repo, project


async def run(db_path: str) -> None:
    settings = Settings()
    _print_header(settings)

    orchestrator, repo, project = await _create_session(settings, db_path)
    print(f"  {DIM}Projekt-ID: {project.projekt_id}{RESET}")

    previous_slots: dict | None = None
    turn_nr = 0

    while True:
        # Eingabe
        try:
            user_input = input(f"\n  {CYAN}{BOLD}Du:{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n\n  {DIM}Beendet.{RESET}")
            break

        if not user_input or user_input.lower() in ("q", "quit", "exit"):
            print(f"\n  {DIM}Beendet.{RESET}")
            break

        # Sonderbefehle
        current = repo.load(project.projekt_id)
        if user_input == "/slots":
            _print_slot_detail(current)
            continue
        elif user_input == "/reset":
            orchestrator, repo, project = await _create_session(settings, db_path)
            previous_slots = None
            turn_nr = 0
            print(f"\n  {GREEN}Neues Projekt gestartet.{RESET}")
            continue
        elif user_input == "/export":
            _export_artifact(current)
            continue

        # Turn verarbeiten
        turn_nr += 1
        print(f"\n  {DIM}Verarbeite Turn {turn_nr}...{RESET}")

        result = await orchestrator.process_turn(
            project_id=project.projekt_id,
            input=TurnInput(text=user_input),
        )

        if result.error:
            print(f"\n  {RED}FEHLER: {result.error}{RESET}")
            continue

        # Antwort anzeigen
        print(f"\n  {GREEN}{BOLD}Explorer:{RESET} {result.nutzeraeusserung}")
        print(
            f"\n  {DIM}Phase: {result.phasenstatus.value} | "
            f"Turn: {result.working_memory.letzter_dialogturn} | "
            f"Flags: {result.flags or '-'}{RESET}"
        )

        # Slots anzeigen mit Diff
        current = repo.load(project.projekt_id)
        _print_slots(current, previous_slots)
        previous_slots = _slots_snapshot(current)


def main() -> None:
    parser = argparse.ArgumentParser(description="Interaktiver Explorer-Dialog")
    parser.add_argument(
        "--db",
        default=":memory:",
        help="SQLite-DB Pfad (Standard: :memory:)",
    )
    args = parser.parse_args()
    asyncio.run(run(args.db))


if __name__ == "__main__":
    main()
