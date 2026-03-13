"""Debug-Script: führt einen Turn aus und zeigt alle Details."""

import asyncio
import pathlib
import sys

from config import Settings
from core.orchestrator import Orchestrator, TurnInput
from llm.factory import create_llm_client
from modes.base import BaseMode
from modes.exploration import ExplorationMode
from persistence.database import Database
from persistence.project_repository import ProjectRepository

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))


async def main() -> None:
    settings = Settings()
    db = Database(":memory:")
    repo = ProjectRepository(db)
    project = repo.create("Debug")
    llm_client = create_llm_client(settings)
    modes: dict[str, BaseMode] = {"exploration": ExplorationMode(llm_client=llm_client)}
    orchestrator = Orchestrator(repository=repo, modes=modes, settings=settings)

    result = await orchestrator.process_turn(
        project.projekt_id,
        TurnInput(text="Ich möchte unseren Urlaubsantragsprozess digitalisieren."),
    )

    print("\n=== TURN RESULT ===")
    print("nutzeraeusserung:", repr(result.nutzeraeusserung))
    print("error           :", result.error)
    print("phasenstatus    :", result.phasenstatus)
    print("flags           :", result.flags)

    p = repo.load(project.projekt_id)
    slots = p.exploration_artifact.slots
    print(f"\n=== ARTIFACT ({len(slots)} Slots) ===")
    for sid, s in slots.items():
        inhalt_preview = (s.inhalt or "")[:60]
        print(f"  {sid}: status={s.completeness_status.value:15} inhalt={inhalt_preview!r}")

    history = repo.load_dialog_history(project.projekt_id)
    print(f"\n=== DIALOG HISTORY ({len(history)} Einträge) ===")
    for h in history:
        print(f"  [{h['role']}] {(h.get('inhalt') or '')[:120]!r}")


asyncio.run(main())
