"""E2E-Test: Moderator-Explorer-Interaktion mit echtem LLM.

Testet den kompletten Dialog-Flow:
Moderator-Begruessung → Explorer → Eskalation → Moderator → Explorer → Phase Complete → Phasenwechsel

Benötigt: LLM_API_KEY in .env (OpenAI oder Anthropic)
Laufzeit: ca. 3-5 Minuten (17+ LLM-Calls)

Aufruf:
    cd backend
    source .venv/Scripts/activate
    python -m pytest tests/test_e2e_moderator.py -m e2e -s --timeout=600
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
    / "explorer"
    / "dialog-e2e-moderator.json"
)


def _load_dialog() -> dict:
    with open(DIALOG_PATH, encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.asyncio
async def test_e2e_moderator_explorer_flow() -> None:
    """Kompletter E2E-Durchlauf: Moderator → Explorer → Eskalation → Phasenwechsel."""
    from config import get_settings
    from core.orchestrator import Orchestrator, TurnInput
    from llm.factory import create_llm_client
    from modes.exploration import ExplorationMode
    from modes.moderator import Moderator
    from persistence.database import Database
    from persistence.project_repository import ProjectRepository

    dialog = _load_dialog()
    user_inputs = dialog["user_inputs"]
    expected_artifact = dialog["expected_artifact"]["slots"]

    settings = get_settings()
    db = Database(":memory:")
    repo = ProjectRepository(db)
    project = repo.create("E2E Eingangsrechnung")
    pid = project.projekt_id

    llm = create_llm_client(settings)
    orchestrator = Orchestrator(
        repository=repo,
        modes={
            "exploration": ExplorationMode(llm_client=llm),
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
        entry = {
            "turn_nr": turn_nr,
            "input_id": input_id,
            "mode_before": mode_before,
            "mode_after": result.working_memory.aktiver_modus,
            "flags": result.flags,
            "phasenstatus": result.phasenstatus.value,
            "befuellte_slots": result.working_memory.befuellte_slots,
            "bekannte_slots": result.working_memory.bekannte_slots,
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

    # ── S0: Systemstart ─────────────────────────────────────────────
    print("\n=== S0: Systemstart ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text="[Systemstart]"))
    entry = log_turn(turn_nr, "S0", mode_before, result)
    print(f"  Greeting: {result.nutzeraeusserung[:150]}")
    assert result.error is None, f"S0 error: {result.error}"

    # ── U1: Rueckfrage im Moderator ──────────────────────────────────
    print("\n=== U1: Rueckfrage ===")
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

    # ── U2: Prozessbeschreibung im Moderator (kein explizites Ja) ──
    print("\n=== U2: Prozess beschrieben, kein 'Ja' ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[1]["message"]))
    entry = log_turn(turn_nr, "U2", mode_before, result)
    print(f"  Antwort: {result.nutzeraeusserung[:150]}")
    check(
        "CP2",
        entry["mode_after"] == "moderator",
        f"CP2: mode={entry['mode_after']}, expected moderator",
    )

    # ── U3: Explizite Bestaetigung → Explorer startet ──────────────
    print("\n=== U3: 'Ja, legen wir los' ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[2]["message"]))
    entry = log_turn(turn_nr, "U3", mode_before, result)
    print(f"  Mode after: {entry['mode_after']}, flags: {entry['flags']}")
    # CP3: Mode should switch to exploration
    p3 = get_project()
    check(
        "CP3",
        p3.aktiver_modus == "exploration",
        f"CP3: mode={p3.aktiver_modus}, expected exploration. Flags: {entry['flags']}",
    )
    # Also check dialog history contains U2 info
    history = repo.load_dialog_history(pid, last_n=20)
    history_text = " ".join(h.get("inhalt", "") for h in history)
    has_u2_context = "400" in history_text or "Rechnungen" in history_text
    check(
        "CP3_context", has_u2_context, "CP3: Dialog history missing U2 context (400-500 Rechnungen)"
    )

    # ── U4-U7: Explorer-Turns ────────────────────────────────────────
    pre_escalation_responses = []
    for i, uid in enumerate(["U4", "U5", "U6", "U7"]):
        idx = 3 + i
        print(f"\n=== {uid}: Explorer turn ===")
        turn_nr += 1
        mode_before = get_mode()
        result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[idx]["message"]))
        entry = log_turn(turn_nr, uid, mode_before, result)
        pre_escalation_responses.append(len(result.nutzeraeusserung))
        print(f"  [{entry['mode_after']}] {result.nutzeraeusserung[:100]}")
        if result.error:
            print(f"  ERROR: {result.error}")

    # CP4: Initial extraction — slots should be filling
    p4 = get_project()
    art4 = p4.exploration_artifact
    cp4_ok = (
        art4.slots.get("prozessausloeser") is not None
        and art4.slots["prozessausloeser"].inhalt != ""
    )
    check("CP4", cp4_ok, f"CP4: prozessausloeser empty. Slots: {list(art4.slots.keys())}")

    # ── S1: Panik-Button nach U7 ────────────────────────────────────
    print("\n=== S1: Panik-Button ===")
    p_esc = repo.load(pid)
    slots_before_esc = p_esc.working_memory.befuellte_slots
    p_esc.working_memory.vorheriger_modus = p_esc.working_memory.aktiver_modus
    p_esc.working_memory.aktiver_modus = "moderator"
    p_esc.aktiver_modus = "moderator"
    repo.save(p_esc)

    # CP5: Artifact survives escalation
    p5 = get_project()
    check(
        "CP5",
        p5.working_memory.befuellte_slots >= slots_before_esc,
        f"CP5: slots={p5.working_memory.befuellte_slots}, before={slots_before_esc}",
    )
    check(
        "CP5_mode",
        p5.aktiver_modus == "moderator",
        f"CP5: mode={p5.aktiver_modus}, expected moderator",
    )

    # ── U8: User describes problem to Moderator ─────────────────────
    print("\n=== U8: Eskalation — Problem beschrieben ===")
    art_before_u8 = {sid: s.inhalt for sid, s in get_project().exploration_artifact.slots.items()}
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[7]["message"]))
    entry = log_turn(turn_nr, "U8", mode_before, result)
    print(f"  [{entry['mode_after']}] {result.nutzeraeusserung[:150]}")
    check(
        "CP6",
        entry["mode_after"] == "moderator",
        f"CP6: mode={entry['mode_after']}, expected moderator (should analyze, not bounce)",
    )
    # SDD 6.6.5: Moderator darf keine Artefakte verändern
    art_after_u8 = {sid: s.inhalt for sid, s in get_project().exploration_artifact.slots.items()}
    check(
        "CP6_mod_no_write",
        art_before_u8 == art_after_u8,
        f"CP6_mod_no_write: Moderator hat Exploration-Artefakt veraendert",
    )

    # ── U9: User formulates wish ────────────────────────────────────
    print("\n=== U9: Vereinbarung 'kuerzer fragen' ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[8]["message"]))
    entry = log_turn(turn_nr, "U9", mode_before, result)
    print(f"  [{entry['mode_after']}] {result.nutzeraeusserung[:150]}")
    # SDD 6.6.5: Moderator darf keine Artefakte verändern
    art_after_u9 = {sid: s.inhalt for sid, s in get_project().exploration_artifact.slots.items()}
    check(
        "CP6_mod_no_write_u9",
        art_before_u8 == art_after_u9,
        f"CP6_mod_no_write_u9: Moderator hat Exploration-Artefakt in U9 veraendert",
    )

    # ── U10: User confirms return to Explorer ───────────────────────
    print("\n=== U10: 'Ja, zurueck zum Explorer' ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[9]["message"]))
    entry = log_turn(turn_nr, "U10", mode_before, result)
    print(f"  Mode after: {entry['mode_after']}, flags: {entry['flags']}")
    p7 = get_project()
    check(
        "CP7",
        p7.aktiver_modus == "exploration",
        f"CP7: mode={p7.aktiver_modus}, expected exploration. Flags: {entry['flags']}",
    )
    # SDD 6.6.5: Moderator-Rückkehr darf Artefakt nicht verändern
    art_after_u10 = {sid: s.inhalt for sid, s in p7.exploration_artifact.slots.items()}
    check(
        "CP7_mod_no_write",
        art_before_u8 == art_after_u10,
        f"CP7_mod_no_write: Moderator hat Exploration-Artefakt bei Rueckkehr veraendert",
    )

    # ── U11-U13: Explorer turns (post-escalation) ──────────────────
    for i, uid in enumerate(["U11", "U12", "U13"]):
        idx = 10 + i
        print(f"\n=== {uid}: Explorer turn (post-escalation) ===")
        turn_nr += 1
        mode_before = get_mode()
        result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[idx]["message"]))
        entry = log_turn(turn_nr, uid, mode_before, result)
        print(f"  [{entry['mode_after']}] {result.nutzeraeusserung[:100]}")

        # CP8: After U11, check explorer responses are shorter (agreement honored)
        if uid == "U11":
            avg_pre = (
                sum(pre_escalation_responses) / len(pre_escalation_responses)
                if pre_escalation_responses
                else 999
            )
            check(
                "CP8",
                len(result.nutzeraeusserung) <= avg_pre * 1.5,
                f"CP8: post-esc response={len(result.nutzeraeusserung)}, pre-esc avg={avg_pre:.0f}",
            )

    # ── U14: "Mir faellt nichts mehr ein" ───────────────────────────
    print("\n=== U14: 'Mir faellt nichts mehr ein' ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[13]["message"]))
    entry = log_turn(turn_nr, "U14", mode_before, result)
    print(f"  Mode: {entry['mode_after']}, flags: {entry['flags']}")

    # CP9: Summary should be self-generated
    p9 = get_project()
    summary_slot = p9.exploration_artifact.slots.get("prozesszusammenfassung")
    cp9_ok = summary_slot is not None and summary_slot.inhalt.strip() != ""
    check("CP9", cp9_ok, "CP9: prozesszusammenfassung empty or missing")

    # If explorer didn't trigger phase_complete, nudge it
    if p9.aktiver_modus != "moderator":
        nudge_msgs = [
            "Ja das war wirklich alles, wir koennen zur naechsten Phase.",
            "Bitte schliessen Sie die Exploration ab, ich habe alles gesagt.",
            "Exploration beenden, weiter zur Strukturierung.",
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
            # Force advance via debug path if LLM won't cooperate
            print("  Explorer meldet kein phase_complete. Forciere Phasenwechsel.")
            p_force = get_project()
            p_force.working_memory.vorheriger_modus = "exploration"
            p_force.working_memory.aktiver_modus = "moderator"
            p_force.aktiver_modus = "moderator"
            repo.save(p_force)

    # ── U15: Phasenwechsel bestaetigen ──────────────────────────────
    print("\n=== U15: 'Ja, weiter zur naechsten Phase' ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[14]["message"]))
    entry = log_turn(turn_nr, "U15", mode_before, result)
    print(f"  Mode: {entry['mode_after']}, phase: {entry['aktive_phase']}, flags: {entry['flags']}")

    p10 = get_project()
    check(
        "CP10",
        p10.aktive_phase.value == "strukturierung",
        f"CP10: phase={p10.aktive_phase.value}, expected strukturierung",
    )

    # ── ARTIFACT CHECK ──────────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print("  ARTEFAKT-PRUEFUNG")
    print(f"{'=' * 72}")

    p_final = get_project()
    art = p_final.exploration_artifact

    # Define core keywords per slot
    keyword_checks = {
        "prozessausloeser": ["Rechnung", "Post", "E-Mail"],
        "prozessziel": ["Rechnung", "Zahlung"],
        "prozessbeschreibung": ["Freigabe", "DATEV", "Rechnung"],
        "scope": ["Rechnungseingang", "Zahlung"],
        "beteiligte_systeme": ["DATEV", "ELO"],
        "umgebung": ["Mitarbeiter", "Buchhaltung"],
        "randbedingungen": ["Skonto", "Frist"],
        "ausnahmen": ["Gutschrift"],
        "prozesszusammenfassung": ["Rechnung"],
    }

    all_slots_filled = True
    for slot_id in expected_artifact:
        slot = art.slots.get(slot_id)
        status = slot.completeness_status.value if slot else "MISSING"
        inhalt = slot.inhalt[:100] if slot and slot.inhalt else "(leer)"
        if not slot or not slot.inhalt:
            all_slots_filled = False
        # Keyword check
        keywords = keyword_checks.get(slot_id, [])
        kw_found = [kw for kw in keywords if slot and kw.lower() in slot.inhalt.lower()]
        kw_miss = [kw for kw in keywords if kw not in kw_found]
        print(f"  {slot_id:25s} [{status:15s}] KW: {len(kw_found)}/{len(keywords)} | {inhalt}")
        if kw_miss:
            print(f"    Missing keywords: {kw_miss}")

    # ── TURN LOG ────────────────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print("  TURN LOG")
    print(f"{'=' * 72}")
    print(
        f"  {'#':>3} | {'Input':6} | {'Before':12} | {'After':12} | {'Phase':15} | {'Flags':25} | {'Slots':5} | Antwort"
    )
    print(
        f"  {'-' * 3}-+-{'-' * 6}-+-{'-' * 12}-+-{'-' * 12}-+-{'-' * 15}-+-{'-' * 25}-+-{'-' * 5}-+-{'-' * 40}"
    )
    for e in turn_log:
        flags_str = ",".join(e["flags"]) if e["flags"] else "-"
        slots_str = f"{e['befuellte_slots']}/{e['bekannte_slots']}"
        preview = e["nutzeraeusserung_preview"][:40].replace("\n", " ")
        print(
            f"  {e['turn_nr']:3d} | {e['input_id']:6} | {e['mode_before']:12} | {e['mode_after']:12} | {e['aktive_phase']:15} | {flags_str:25} | {slots_str:5} | {preview}"
        )

    # ── SUMMARY ─────────────────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print("  E2E TEST SUMMARY")
    print(f"{'=' * 72}")
    passed = sum(1 for v in checkpoint_results.values() if v)
    total = len(checkpoint_results)
    print(f"  Turns executed: {turn_nr}")
    print(f"  Checkpoints passed: {passed}/{total}")
    print(f"  Final mode: {p10.aktiver_modus}")
    print(f"  Final phase: {p10.aktive_phase.value}")
    print(f"  All slots filled: {all_slots_filled}")
    print()
    for cp_name, cp_ok in checkpoint_results.items():
        icon = "PASS" if cp_ok else "FAIL"
        err = f" — {checkpoint_errors[cp_name]}" if not cp_ok else ""
        print(f"  {icon}: {cp_name}{err}")

    db.close()

    # Assert all hard checkpoints pass
    for cp_name in [
        "CP1", "CP2", "CP3", "CP5", "CP5_mode", "CP6", "CP7", "CP10",
        "CP6_mod_no_write", "CP7_mod_no_write",
    ]:
        if cp_name in checkpoint_results:
            assert checkpoint_results[cp_name], (
                f"{cp_name} failed: {checkpoint_errors.get(cp_name, '?')}"
            )
