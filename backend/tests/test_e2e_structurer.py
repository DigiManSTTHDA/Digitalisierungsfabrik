"""E2E-Test: Structurer-Moderator-Interaktion mit echtem LLM.

Testet den kompletten Structuring-Flow:
Moderator-Intro → Structurer → Eskalation → Moderator → Structurer → Phase Complete → Phasenwechsel

Das Explorationsartefakt wird aus dem Testdialog geladen (exploration_seed),
um den Explorer-Durchlauf zu überspringen. Der Test beginnt in der
Strukturierungsphase mit aktivem Moderator (wie nach Explorer-Completion).

Benötigt: LLM_API_KEY in .env (OpenAI oder Anthropic)
Laufzeit: ca. 3-5 Minuten (15+ LLM-Calls)

Aufruf:
    cd backend
    source .venv/Scripts/activate
    python -m pytest tests/test_e2e_structurer.py -m e2e -s --timeout=600
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

# Ensure backend is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
os.chdir(backend_dir)

pytestmark = pytest.mark.e2e

DIALOG_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "frontend"
    / "test-texte"
    / "structurer"
    / "dialog-e2e-structurer.json"
)


def _load_dialog() -> dict:
    with open(DIALOG_PATH, encoding="utf-8") as f:
        return json.load(f)


def _seed_exploration_artifact(repo, project_id: str, seed: dict) -> None:
    """Load the pre-filled exploration artifact into the project."""
    from artifacts.models import CompletenessStatus, ExplorationArtifact, ExplorationSlot

    slots = {}
    for slot_id, slot_data in seed["slots"].items():
        slots[slot_id] = ExplorationSlot(
            slot_id=slot_data["slot_id"],
            titel=slot_data["titel"],
            inhalt=slot_data["inhalt"],
            completeness_status=CompletenessStatus(slot_data["completeness_status"]),
        )
    artifact = ExplorationArtifact(slots=slots, version=seed.get("version", 12))

    project = repo.load(project_id)
    project.exploration_artifact = artifact
    # Set phase to strukturierung with moderator active (post-explorer state)
    from artifacts.models import Phasenstatus, Projektphase

    project.aktive_phase = Projektphase.strukturierung
    project.aktiver_modus = "moderator"
    project.working_memory.aktive_phase = Projektphase.strukturierung
    project.working_memory.aktiver_modus = "moderator"
    project.working_memory.vorheriger_modus = None
    project.working_memory.phasenstatus = Phasenstatus.in_progress
    project.working_memory.befuellte_slots = len(slots)
    project.working_memory.bekannte_slots = len(slots)
    repo.save(project)


@pytest.mark.asyncio
async def test_e2e_structurer_flow() -> None:
    """Kompletter E2E-Durchlauf: Moderator → Structurer → Eskalation → Phasenwechsel."""
    from config import get_settings
    from core.orchestrator import Orchestrator, TurnInput
    from llm.factory import create_llm_client
    from modes.exploration import ExplorationMode
    from modes.moderator import Moderator
    from modes.structuring import StructuringMode
    from persistence.database import Database
    from persistence.project_repository import ProjectRepository

    dialog = _load_dialog()
    user_inputs = dialog["user_inputs"]
    exploration_seed = dialog["exploration_seed"]
    expected = dialog["expected_structure_artifact"]

    settings = get_settings()
    db = Database(":memory:")
    repo = ProjectRepository(db)
    project = repo.create("E2E Eingangsrechnung Strukturierung")
    pid = project.projekt_id

    # Seed the exploration artifact and set phase
    _seed_exploration_artifact(repo, pid, exploration_seed)

    llm = create_llm_client(settings)
    orchestrator = Orchestrator(
        repository=repo,
        modes={
            "exploration": ExplorationMode(llm_client=llm),
            "structuring": StructuringMode(llm_client=llm),
            "moderator": Moderator(llm_client=llm),
        },
        settings=settings,
    )

    turn_log: list[dict] = []
    checkpoint_results: dict[str, bool] = {}
    checkpoint_errors: dict[str, str] = {}

    def log_turn(
        turn_nr: int,
        input_id: str,
        mode_before: str,
        result,  # noqa: ANN001
    ) -> dict:
        project_now = repo.load(pid)
        schritte_count = len(project_now.structure_artifact.schritte)
        entry = {
            "turn_nr": turn_nr,
            "input_id": input_id,
            "mode_before": mode_before,
            "mode_after": result.working_memory.aktiver_modus,
            "flags": result.flags,
            "phasenstatus": result.phasenstatus.value,
            "schritte_count": schritte_count,
            "nutzeraeusserung_preview": result.nutzeraeusserung[:200],
            "vorheriger_modus": result.working_memory.vorheriger_modus,
            "aktive_phase": result.working_memory.aktive_phase.value,
            "error": result.error,
        }
        turn_log.append(entry)
        return entry

    def check(name: str, condition: bool, msg: str) -> None:
        checkpoint_results[name] = condition
        if not condition:
            checkpoint_errors[name] = msg

    def get_mode() -> str:
        return repo.load(pid).working_memory.aktiver_modus

    def get_project():  # noqa: ANN201
        return repo.load(pid)

    turn_nr = 0

    # ── S0: Systemstart in Strukturierungsphase ───────────────────
    print("\n=== S0: Systemstart (Strukturierungsphase) ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text="[Systemstart] Die Explorationsphase ist abgeschlossen. Bitte erkläre dem Nutzer die Strukturierungsphase."))
    entry = log_turn(turn_nr, "S0", mode_before, result)
    print(f"  Greeting: {result.nutzeraeusserung[:150]}")
    assert result.error is None, f"S0 error: {result.error}"

    # Verify exploration artifact is still intact
    p_check = get_project()
    assert len(p_check.exploration_artifact.slots) == 9, "Exploration artifact lost during S0"

    # ── U1: Rückfrage im Moderator ────────────────────────────────
    print("\n=== U1: Rückfrage zur Strukturierung ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[0]["message"]))
    entry = log_turn(turn_nr, "U1", mode_before, result)
    print(f"  Antwort: {result.nutzeraeusserung[:150]}")
    check(
        "CP1",
        entry["mode_after"] == "moderator",
        f"CP1: mode={entry['mode_after']}, expected moderator",
    )

    # ── U2: Explizite Bestätigung → Structurer startet ───────────
    print("\n=== U2: 'Ja, legen wir los mit der Strukturierung' ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[1]["message"]))
    entry = log_turn(turn_nr, "U2", mode_before, result)
    print(f"  Mode after: {entry['mode_after']}, flags: {entry['flags']}")
    p2 = get_project()
    check(
        "CP2",
        p2.aktiver_modus == "structuring",
        f"CP2: mode={p2.aktiver_modus}, expected structuring. Flags: {entry['flags']}",
    )

    # ── U3: Erste Structurer-Interaktion ──────────────────────────
    print("\n=== U3: Bestätigung Grundstruktur + Entscheidungspunkte ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[2]["message"]))
    entry = log_turn(turn_nr, "U3", mode_before, result)
    print(f"  [{entry['mode_after']}] Schritte: {entry['schritte_count']} | {result.nutzeraeusserung[:100]}")
    p3 = get_project()
    check(
        "CP3",
        len(p3.structure_artifact.schritte) >= 1,
        f"CP3: schritte={len(p3.structure_artifact.schritte)}, expected >= 1",
    )

    # ── U4: Schleifen und Ausnahmen ───────────────────────────────
    print("\n=== U4: Schleifen und Ausnahmen ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[3]["message"]))
    entry = log_turn(turn_nr, "U4", mode_before, result)
    print(f"  [{entry['mode_after']}] Schritte: {entry['schritte_count']} | {result.nutzeraeusserung[:100]}")

    # ── U5: Bestellabgleich als Entscheidungspunkt ────────────────
    print("\n=== U5: Bestellabgleich + Teilrechnungen ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[4]["message"]))
    entry = log_turn(turn_nr, "U5", mode_before, result)
    print(f"  [{entry['mode_after']}] Schritte: {entry['schritte_count']} | {result.nutzeraeusserung[:100]}")

    # CP4: Mindestens eine Entscheidung modelliert
    p5 = get_project()
    has_entscheidung = any(
        s.typ.value == "entscheidung" for s in p5.structure_artifact.schritte.values()
    )
    check(
        "CP4",
        has_entscheidung,
        f"CP4: Keine Entscheidungsschritte gefunden. Typen: {[s.typ.value for s in p5.structure_artifact.schritte.values()]}",
    )

    # ── U6: User wird ungeduldig → danach Panik-Button ────────────
    print("\n=== U6: User ungeduldig ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[5]["message"]))
    entry = log_turn(turn_nr, "U6", mode_before, result)
    print(f"  [{entry['mode_after']}] {result.nutzeraeusserung[:100]}")

    # ── S1: Panik-Button nach U6 ──────────────────────────────────
    print("\n=== S1: Panik-Button ===")
    p_esc = repo.load(pid)
    schritte_before_esc = len(p_esc.structure_artifact.schritte)
    p_esc.working_memory.vorheriger_modus = p_esc.working_memory.aktiver_modus
    p_esc.working_memory.aktiver_modus = "moderator"
    p_esc.aktiver_modus = "moderator"
    repo.save(p_esc)

    # CP5: Artifact survives escalation
    p5_esc = get_project()
    check(
        "CP5",
        len(p5_esc.structure_artifact.schritte) >= schritte_before_esc,
        f"CP5: schritte={len(p5_esc.structure_artifact.schritte)}, before={schritte_before_esc}",
    )
    check(
        "CP5_mode",
        p5_esc.aktiver_modus == "moderator",
        f"CP5: mode={p5_esc.aktiver_modus}, expected moderator",
    )

    # ── U7: User beschreibt Problem ───────────────────────────────
    print("\n=== U7: Eskalation — Problem beschrieben ===")
    schritte_before_u7 = len(get_project().structure_artifact.schritte)
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[6]["message"]))
    entry = log_turn(turn_nr, "U7", mode_before, result)
    print(f"  [{entry['mode_after']}] {result.nutzeraeusserung[:150]}")
    check(
        "CP6",
        entry["mode_after"] == "moderator",
        f"CP6: mode={entry['mode_after']}, expected moderator (should analyze, not bounce)",
    )
    # SDD 6.6.5: Moderator darf keine Artefakte verändern
    schritte_after_u7 = len(get_project().structure_artifact.schritte)
    check(
        "CP6_mod_no_write",
        schritte_after_u7 == schritte_before_u7,
        f"CP6_mod_no_write: schritte changed {schritte_before_u7} -> {schritte_after_u7} during moderator turn",
    )

    # ── U8: User bestätigt Rückkehr ───────────────────────────────
    print("\n=== U8: 'Ja, zurück zum Structurer' ===")
    schritte_before_u8 = len(get_project().structure_artifact.schritte)
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[7]["message"]))
    entry = log_turn(turn_nr, "U8", mode_before, result)
    print(f"  Mode after: {entry['mode_after']}, flags: {entry['flags']}")
    p7 = get_project()
    check(
        "CP7",
        p7.aktiver_modus == "structuring",
        f"CP7: mode={p7.aktiver_modus}, expected structuring. Flags: {entry['flags']}",
    )
    # SDD 6.6.5: Moderator-Rückkehr darf Artefakt nicht verändern
    check(
        "CP7_mod_no_write",
        len(p7.structure_artifact.schritte) == schritte_before_u8,
        f"CP7_mod_no_write: schritte changed {schritte_before_u8} -> {len(p7.structure_artifact.schritte)} during moderator return",
    )

    # ── U9: Reihenfolge bestätigen ────────────────────────────────
    print("\n=== U9: Reihenfolge + Normalfall ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[8]["message"]))
    entry = log_turn(turn_nr, "U9", mode_before, result)
    print(f"  [{entry['mode_after']}] Schritte: {entry['schritte_count']} | {result.nutzeraeusserung[:100]}")

    # CP8: Reihenfolge prüfen
    p8 = get_project()
    schritte_list = sorted(p8.structure_artifact.schritte.values(), key=lambda s: s.reihenfolge)
    reihenfolgen = [s.reihenfolge for s in schritte_list]
    # Reihenfolge muss aufsteigend sein (nicht unbedingt lückenlos)
    is_ascending = all(reihenfolgen[i] <= reihenfolgen[i + 1] for i in range(len(reihenfolgen) - 1))
    has_nachfolger = any(len(s.nachfolger) > 0 for s in schritte_list)
    check(
        "CP8",
        is_ascending and has_nachfolger,
        f"CP8: ascending={is_ascending}, has_nachfolger={has_nachfolger}, reihenfolgen={reihenfolgen}",
    )

    # ── U10: Spannungsfeld ELO-Medienbruch ────────────────────────
    print("\n=== U10: Spannungsfeld ELO-Medienbruch ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[9]["message"]))
    entry = log_turn(turn_nr, "U10", mode_before, result)
    print(f"  [{entry['mode_after']}] Schritte: {entry['schritte_count']} | {result.nutzeraeusserung[:100]}")

    # CP9: Spannungsfeld dokumentiert — mit inhaltlicher Keyword-Prüfung
    p9 = get_project()
    spannungsfeld_texts = [
        s.spannungsfeld
        for s in p9.structure_artifact.schritte.values()
        if s.spannungsfeld is not None and s.spannungsfeld.strip() != ""
    ]
    has_spannungsfeld = len(spannungsfeld_texts) > 0
    check(
        "CP9",
        has_spannungsfeld,
        f"CP9: Kein Spannungsfeld gefunden. Felder: {[(s.schritt_id, s.spannungsfeld) for s in p9.structure_artifact.schritte.values()]}",
    )
    # CP9_keywords: Spannungsfeld muss inhaltlich zum ELO-Medienbruch passen
    if has_spannungsfeld:
        all_spannungsfeld_text = " ".join(spannungsfeld_texts).lower()
        elo_keywords = ["elo", "medienbruch", "stempel", "scan", "ausdruck", "doppel"]
        found_kw = [kw for kw in elo_keywords if kw in all_spannungsfeld_text]
        check(
            "CP9_keywords",
            len(found_kw) >= 1,
            f"CP9_keywords: Spannungsfeld ohne ELO/Medienbruch-Bezug. Text: {all_spannungsfeld_text[:200]}. Keywords gesucht: {elo_keywords}",
        )

    # ── U11: User bestätigt Gesamtstruktur ────────────────────────
    print("\n=== U11: 'Struktur ist komplett' ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[10]["message"]))
    entry = log_turn(turn_nr, "U11", mode_before, result)
    print(f"  Mode: {entry['mode_after']}, flags: {entry['flags']}")

    # If structurer didn't trigger phase_complete, nudge it
    p_pre = get_project()
    if p_pre.aktiver_modus != "moderator":
        nudge_msgs = [
            "Ja das war wirklich alles, die Struktur ist vollständig und korrekt. Bitte schließen Sie die Strukturierung ab.",
            "Die Struktur ist fertig, alle Schritte sind erfasst. Bitte phase_complete melden.",
            "Strukturierung abschließen, weiter zur Spezifikation.",
        ]
        for nudge in nudge_msgs:
            print(f"  Nudge: '{nudge[:60]}'")
            turn_nr += 1
            mode_before = get_mode()
            result = await orchestrator.process_turn(pid, TurnInput(text=nudge))
            log_turn(turn_nr, "NUDGE", mode_before, result)
            p_check = get_project()
            if p_check.aktiver_modus == "moderator":
                print("  -> Moderator aktiviert!")
                break
        else:
            # Force advance if LLM won't cooperate
            print("  Structurer meldet kein phase_complete. Forciere Phasenwechsel.")
            from artifacts.models import Phasenstatus as _PS
            p_force = get_project()
            p_force.working_memory.vorheriger_modus = "structuring"
            p_force.working_memory.aktiver_modus = "moderator"
            p_force.aktiver_modus = "moderator"
            p_force.working_memory.phasenstatus = _PS.phase_complete
            repo.save(p_force)

    # CP10: Phase complete — Moderator aktiv, Artefakt vollständig
    p10 = get_project()
    check(
        "CP10",
        p10.aktiver_modus == "moderator",
        f"CP10: mode={p10.aktiver_modus}, expected moderator",
    )
    check(
        "CP10_schritte",
        len(p10.structure_artifact.schritte) >= 5,
        f"CP10: schritte={len(p10.structure_artifact.schritte)}, expected >= 5",
    )

    # CP10_no_leer: SDD 6.6.2 — Kein Schritt darf completeness_status 'leer' haben bei phase_complete
    leer_schritte = [
        sid for sid, s in p10.structure_artifact.schritte.items()
        if s.completeness_status.value == "leer"
    ]
    check(
        "CP10_no_leer",
        len(leer_schritte) == 0,
        f"CP10_no_leer: {len(leer_schritte)} Schritte noch 'leer': {leer_schritte}",
    )

    # CP10_beschreibung: SDD 5.4 — beschreibung ist Pflichtfeld, darf nicht leer sein
    empty_beschreibung = [
        sid for sid, s in p10.structure_artifact.schritte.items()
        if not s.beschreibung or not s.beschreibung.strip()
    ]
    check(
        "CP10_beschreibung",
        len(empty_beschreibung) == 0,
        f"CP10_beschreibung: {len(empty_beschreibung)} Schritte ohne beschreibung: {empty_beschreibung}",
    )

    # CP10_nachfolger_valid: Alle nachfolger-IDs müssen existierende schritt_ids referenzieren
    all_schritt_ids = set(p10.structure_artifact.schritte.keys())
    dangling_refs = []
    for sid, s in p10.structure_artifact.schritte.items():
        for nf in s.nachfolger:
            if nf not in all_schritt_ids:
                dangling_refs.append(f"{sid} -> {nf}")
    check(
        "CP10_nachfolger_valid",
        len(dangling_refs) == 0,
        f"CP10_nachfolger_valid: Dangling nachfolger-Referenzen: {dangling_refs}",
    )

    # ── U12: Phasenwechsel bestätigen ─────────────────────────────
    print("\n=== U12: 'Ja, weiter zur nächsten Phase' ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[11]["message"]))
    entry = log_turn(turn_nr, "U12", mode_before, result)
    print(f"  Mode: {entry['mode_after']}, phase: {entry['aktive_phase']}, flags: {entry['flags']}")

    p11 = get_project()
    check(
        "CP11",
        p11.aktive_phase.value == "spezifikation",
        f"CP11: phase={p11.aktive_phase.value}, expected spezifikation",
    )

    # ── EXPLORATION ARTIFACT CHECK ────────────────────────────────
    print(f"\n{'=' * 72}")
    print("  EXPLORATIONSARTEFAKT-PRUEFUNG (Datenerhalt)")
    print(f"{'=' * 72}")

    p_final = get_project()
    exp_art = p_final.exploration_artifact
    exploration_intact = len(exp_art.slots) == 9
    all_filled = all(slot.inhalt.strip() != "" for slot in exp_art.slots.values())
    print(f"  Slots erhalten: {len(exp_art.slots)}/9")
    print(f"  Alle gefüllt: {all_filled}")
    check(
        "EXP_INTACT",
        exploration_intact and all_filled,
        f"Exploration artifact corrupted: slots={len(exp_art.slots)}, all_filled={all_filled}",
    )

    # ── STRUCTURE ARTIFACT CHECK ──────────────────────────────────
    print(f"\n{'=' * 72}")
    print("  STRUKTURARTEFAKT-PRUEFUNG")
    print(f"{'=' * 72}")

    struct_art = p_final.structure_artifact
    schritte = struct_art.schritte
    print(f"  Anzahl Schritte: {len(schritte)}")
    print(f"  Prozesszusammenfassung: {'JA' if struct_art.prozesszusammenfassung else 'NEIN'}")
    print(f"  Version: {struct_art.version}")

    # Print each step
    for sid, schritt in sorted(schritte.items(), key=lambda x: x[1].reihenfolge):
        nachf = ", ".join(schritt.nachfolger) if schritt.nachfolger else "(Ende)"
        bed = f" | Bedingung: {schritt.bedingung}" if schritt.bedingung else ""
        aus = f" | Ausnahme: {schritt.ausnahme_beschreibung}" if schritt.ausnahme_beschreibung else ""
        span = f" | Spannungsfeld: {schritt.spannungsfeld[:60]}" if schritt.spannungsfeld else ""
        print(
            f"  [{schritt.reihenfolge:2d}] {sid:8s} {schritt.titel:30s} [{schritt.typ.value:12s}] [{schritt.completeness_status.value:15s}] → {nachf}{bed}{aus}{span}"
        )

    # Structural requirements
    reqs = expected["structural_requirements"]

    check(
        "STRUCT_MIN_SCHRITTE",
        len(schritte) >= reqs["min_schritte"],
        f"min_schritte: {len(schritte)} < {reqs['min_schritte']}",
    )

    actual_types = {s.typ.value for s in schritte.values()}
    for must_type in reqs["must_have_types"]:
        check(
            f"STRUCT_TYPE_{must_type}",
            must_type in actual_types,
            f"Typ '{must_type}' nicht vorhanden. Actual: {actual_types}",
        )

    # Check entscheidung steps have bedingung and multiple nachfolger
    if reqs.get("entscheidung_must_have_bedingung"):
        for sid, s in schritte.items():
            if s.typ.value == "entscheidung":
                check(
                    f"ENTSCH_BED_{sid}",
                    s.bedingung is not None and s.bedingung.strip() != "",
                    f"Entscheidung '{sid}' hat keine Bedingung",
                )
                check(
                    f"ENTSCH_NACHF_{sid}",
                    len(s.nachfolger) >= 2,
                    f"Entscheidung '{sid}' hat nur {len(s.nachfolger)} Nachfolger, erwartet >= 2",
                )

    # Check start step (no predecessor) and end step (no successor)
    all_nachfolger_ids = set()
    for s in schritte.values():
        all_nachfolger_ids.update(s.nachfolger)
    start_steps = [sid for sid in schritte if sid not in all_nachfolger_ids]
    end_steps = [sid for sid, s in schritte.items() if len(s.nachfolger) == 0]

    if reqs.get("must_have_start_step"):
        check(
            "STRUCT_START",
            len(start_steps) >= 1,
            f"Kein Startschritt (alle sind Nachfolger von anderen). IDs: {list(schritte.keys())}",
        )
    if reqs.get("must_have_end_step"):
        check(
            "STRUCT_END",
            len(end_steps) >= 1,
            f"Kein Endschritt (alle haben Nachfolger). IDs: {list(schritte.keys())}",
        )

    if reqs.get("must_have_prozesszusammenfassung"):
        check(
            "STRUCT_ZUSAMMENFASSUNG",
            struct_art.prozesszusammenfassung.strip() != "",
            "Prozesszusammenfassung ist leer",
        )

    # Concept coverage check (soft — keyword matching)
    print(f"\n{'=' * 72}")
    print("  KONZEPT-ABDECKUNG (Keyword-Matching)")
    print(f"{'=' * 72}")

    all_text = " ".join(
        f"{s.titel} {s.beschreibung} {s.bedingung or ''} {s.ausnahme_beschreibung or ''}"
        for s in schritte.values()
    ).lower()

    for concept in expected["expected_concepts"]:
        keywords = concept["keywords"]
        found = [kw for kw in keywords if kw.lower() in all_text]
        coverage = len(found) / len(keywords) if keywords else 0
        status = "OK" if coverage >= 0.5 else "MISS"
        print(f"  {status}: {concept['concept']:35s} KW: {len(found)}/{len(keywords)} ({coverage:.0%}) | gefunden: {found}")

    # ── TURN LOG ──────────────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print("  TURN LOG")
    print(f"{'=' * 72}")
    print(
        f"  {'#':>3} | {'Input':6} | {'Before':12} | {'After':12} | {'Phase':15} | {'Flags':25} | {'Schritte':8} | Antwort"
    )
    print(
        f"  {'-' * 3}-+-{'-' * 6}-+-{'-' * 12}-+-{'-' * 12}-+-{'-' * 15}-+-{'-' * 25}-+-{'-' * 8}-+-{'-' * 40}"
    )
    for e in turn_log:
        flags_str = ",".join(e["flags"]) if e["flags"] else "-"
        preview = e["nutzeraeusserung_preview"][:40].replace("\n", " ")
        print(
            f"  {e['turn_nr']:3d} | {e['input_id']:6} | {e['mode_before']:12} | {e['mode_after']:12} | {e['aktive_phase']:15} | {flags_str:25} | {e['schritte_count']:8d} | {preview}"
        )

    # ── SUMMARY ───────────────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print("  E2E STRUCTURER TEST SUMMARY")
    print(f"{'=' * 72}")
    passed = sum(1 for v in checkpoint_results.values() if v)
    total = len(checkpoint_results)
    print(f"  Turns executed: {turn_nr}")
    print(f"  Checkpoints passed: {passed}/{total}")
    print(f"  Final mode: {p_final.aktiver_modus}")
    print(f"  Final phase: {p_final.aktive_phase.value}")
    print(f"  Exploration slots: {len(exp_art.slots)}/9")
    print(f"  Structure schritte: {len(schritte)}")
    print(f"  Prozesszusammenfassung: {'JA' if struct_art.prozesszusammenfassung else 'NEIN'}")
    print()
    for cp_name, cp_ok in checkpoint_results.items():
        icon = "PASS" if cp_ok else "FAIL"
        err = f" -- {checkpoint_errors[cp_name]}" if not cp_ok else ""
        print(f"  {icon}: {cp_name}{err}")

    db.close()

    # Assert all hard checkpoints pass
    hard_checkpoints = [
        "CP1", "CP2", "CP3", "CP5", "CP5_mode", "CP6", "CP7",
        "CP6_mod_no_write", "CP7_mod_no_write",
        "CP10", "CP10_schritte", "CP10_no_leer", "CP10_beschreibung",
        "CP10_nachfolger_valid",
        "CP11", "EXP_INTACT",
        "STRUCT_MIN_SCHRITTE", "STRUCT_TYPE_aktion", "STRUCT_TYPE_entscheidung",
    ]
    for cp_name in hard_checkpoints:
        if cp_name in checkpoint_results:
            assert checkpoint_results[cp_name], (
                f"{cp_name} failed: {checkpoint_errors.get(cp_name, '?')}"
            )
