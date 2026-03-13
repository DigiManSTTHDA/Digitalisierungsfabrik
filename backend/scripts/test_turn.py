"""Manueller CLI-Test fuer einen vollstaendigen Orchestrator-Turn.

Verwendung (aus backend/):
    python -m scripts.test_turn
    python -m scripts.test_turn "Ich moechte den Bestellprozess digitalisieren"
    python -m scripts.test_turn --turns 3

Voraussetzungen:
    - backend/.env mit gueltigem LLM_API_KEY
    - venv aktiviert
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

# Sicherstellen dass backend/ im sys.path ist (falls direkt aufgerufen)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import Settings
from core.orchestrator import Orchestrator, TurnInput
from llm.factory import create_llm_client
from core.models import Project
from modes.base import BaseMode
from modes.exploration import ExplorationMode
from persistence.database import Database
from persistence.project_repository import ProjectRepository


def _print_separator(title: str = "") -> None:
    width = 70
    if title:
        pad = (width - len(title) - 2) // 2
        print("-" * pad + f" {title} " + "-" * pad)
    else:
        print("-" * width)


def _print_artifact(project: Project) -> None:
    slots = project.exploration_artifact.slots
    filled = [s for s in slots.values() if s.inhalt and s.inhalt.strip()]
    print(f"  ExplorationArtifact - {len(filled)}/{len(slots)} Slots befuellt")
    for slot_id, slot in slots.items():
        status = "[x]" if slot.inhalt and slot.inhalt.strip() else "[ ]"
        inhalt = (slot.inhalt[:60] + "...") if slot.inhalt and len(slot.inhalt) > 60 else (slot.inhalt or "")
        print(f"    {status} {slot_id}: {inhalt}")


async def run(messages: list[str]) -> None:
    settings = Settings()

    _print_separator("DIGITALISIERUNGSFABRIK - Manueller Turn-Test")
    print(f"  Provider : {settings.llm_provider}")
    print(f"  Modell   : {settings.llm_model}")
    print(f"  DB       : {settings.database_path}")
    _print_separator()

    # In-Memory-DB fuer den Test (kein Dateisystem-Artefakt)
    db = Database(":memory:")
    repo = ProjectRepository(db)

    # Projekt anlegen
    project = repo.create("Test-Projekt (CLI)")
    print(f"\n  Projekt-ID: {project.projekt_id}")
    _print_separator()

    # LLM-Client und Modus
    llm_client = create_llm_client(settings)
    modes: dict[str, BaseMode] = {"exploration": ExplorationMode(llm_client=llm_client)}
    orchestrator = Orchestrator(repository=repo, modes=modes, settings=settings)

    for i, message in enumerate(messages, start=1):
        _print_separator(f"Turn {i}")
        print(f"  Du: {message}\n")

        result = await orchestrator.process_turn(
            project_id=project.projekt_id,
            input=TurnInput(text=message),
        )

        if result.error:
            print(f"  [!] FEHLER: {result.error}")
            break

        print(f"  System ({result.working_memory.aktiver_modus}):")
        print(f"  {result.nutzeraeusserung}\n")
        print(f"  Flags     : {result.flags or '-'}")
        print(f"  Phase     : {result.phasenstatus.value}")
        print(f"  Turn-Nr.  : {result.working_memory.letzter_dialogturn}")
        _print_separator()

        # Aktuellen Zustand des Projekts laden und Artifact zeigen
        current = repo.load(project.projekt_id)
        _print_artifact(current)

    _print_separator("FERTIG")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manueller Digitalisierungsfabrik-Turn-Test")
    parser.add_argument(
        "message",
        nargs="?",
        default="Ich moechte unseren Bestellprozess digitalisieren. Wir verarbeiten taeglich etwa 200 Bestellungen manuell per E-Mail.",
        help="Nutzernachricht fuer Turn 1",
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=1,
        help="Anzahl Turns mit fest kodierten Folge-Nachrichten (Standard: 1)",
    )
    args = parser.parse_args()

    follow_ups = [
        "Die Bestellungen kommen per E-Mail und manchmal per Telefon. Zustaendig sind drei Mitarbeiterinnen im Innendienst.",
        "Das groesste Problem ist die manuelle Dateneingabe ins ERP-System. Das dauert manchmal bis zu 30 Minuten pro Bestellung.",
        "Als Ergebnis soll eine Bestellung automatisch ins ERP uebertragen werden, sobald sie per E-Mail eingeht.",
    ]

    messages = [args.message] + follow_ups[: args.turns - 1]

    asyncio.run(run(messages))


if __name__ == "__main__":
    main()
