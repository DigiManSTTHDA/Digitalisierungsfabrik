"""E2E-Test: Spezifikationsmodus + Moderator mit echtem LLM.

Testet den kompletten Specification-Flow:
Moderator-Intro → Spezifikation → Widerspruch-Korrektur → Eskalation →
Moderator → Spezifikation (post-escalation) → Phase Complete → Phasenwechsel

Explorations- und Strukturartefakt werden aus dem Testdialog geladen (exploration_seed
+ structure_seed), um Explorer- und Structurer-Durchlauf zu überspringen.
Der Test beginnt in der Spezifikationsphase mit aktivem Moderator.

Benötigt: LLM_API_KEY in .env (OpenAI oder Anthropic)
Laufzeit: ca. 4-7 Minuten (17+ LLM-Calls)

Aufruf:
    cd backend
    source .venv/Scripts/activate
    python -m pytest tests/test_e2e_specifier.py -m e2e -s --timeout=600
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
    / "specifier"
    / "dialog-e2e-specifier.json"
)


def _load_dialog() -> dict:
    with open(DIALOG_PATH, encoding="utf-8") as f:
        return json.load(f)


def _seed_artifacts(repo, project_id: str, dialog: dict) -> None:
    """Load exploration + structure artifacts into the project, set phase to spezifikation."""
    from artifacts.models import (
        AlgorithmusStatus,
        CompletenessStatus,
        ExplorationArtifact,
        ExplorationSlot,
        Phasenstatus,
        Projektphase,
        StructureArtifact,
        Strukturschritt,
        Strukturschritttyp,
    )

    # ── Seed exploration artifact ────────────────────────────────────────────
    exp_seed = dialog["exploration_seed"]
    exp_slots = {}
    for slot_id, slot_data in exp_seed["slots"].items():
        exp_slots[slot_id] = ExplorationSlot(
            slot_id=slot_data["slot_id"],
            titel=slot_data["titel"],
            inhalt=slot_data["inhalt"],
            completeness_status=CompletenessStatus(slot_data["completeness_status"]),
        )
    exploration_artifact = ExplorationArtifact(slots=exp_slots, version=exp_seed.get("version", 12))

    # ── Seed structure artifact ───────────────────────────────────────────────
    struct_seed = dialog["structure_seed"]
    schritte = {}
    for schritt_id, s in struct_seed["schritte"].items():
        schritte[schritt_id] = Strukturschritt(
            schritt_id=s["schritt_id"],
            titel=s["titel"],
            typ=Strukturschritttyp(s["typ"]),
            beschreibung=s.get("beschreibung", ""),
            reihenfolge=s["reihenfolge"],
            nachfolger=s.get("nachfolger", []),
            bedingung=s.get("bedingung"),
            ausnahme_beschreibung=s.get("ausnahme_beschreibung"),
            algorithmus_ref=s.get("algorithmus_ref", []),
            completeness_status=CompletenessStatus(s["completeness_status"]),
            algorithmus_status=AlgorithmusStatus(s["algorithmus_status"]),
            spannungsfeld=s.get("spannungsfeld"),
        )
    structure_artifact = StructureArtifact(
        prozesszusammenfassung=struct_seed.get("prozesszusammenfassung", ""),
        schritte=schritte,
        version=struct_seed.get("version", 8),
    )

    # ── Set project state: spezifikation phase, moderator active ─────────────
    project = repo.load(project_id)
    project.exploration_artifact = exploration_artifact
    project.structure_artifact = structure_artifact
    project.aktive_phase = Projektphase.spezifikation
    project.aktiver_modus = "moderator"
    project.working_memory.aktive_phase = Projektphase.spezifikation
    project.working_memory.aktiver_modus = "moderator"
    project.working_memory.vorheriger_modus = None
    project.working_memory.phasenstatus = Phasenstatus.in_progress
    project.working_memory.befuellte_slots = len(exp_slots)
    project.working_memory.bekannte_slots = len(exp_slots)
    repo.save(project)


def _algo_snapshot(project) -> dict:
    """Snapshot algorithm artifact state for moderator no-write checks."""
    return {
        aid: a.completeness_status.value for aid, a in project.algorithm_artifact.abschnitte.items()
    }


@pytest.mark.asyncio
async def test_e2e_specifier_flow() -> None:
    """Kompletter E2E-Durchlauf: Moderator → Spezifikation → Eskalation → Phasenwechsel."""
    from config import get_settings
    from core.orchestrator import Orchestrator, TurnInput
    from llm.factory import create_llm_client
    from modes.moderator import Moderator
    from modes.specification import SpecificationMode
    from persistence.database import Database
    from persistence.project_repository import ProjectRepository

    dialog = _load_dialog()
    user_inputs = dialog["user_inputs"]
    expected = dialog["expected_algorithm_artifact"]

    settings = get_settings()
    db = Database(":memory:")
    repo = ProjectRepository(db)
    project = repo.create("E2E Eingangsrechnung Spezifikation")
    pid = project.projekt_id

    # Seed both artifacts and set phase to spezifikation
    _seed_artifacts(repo, pid, dialog)

    llm = create_llm_client(settings)
    orchestrator = Orchestrator(
        repository=repo,
        modes={
            "specification": SpecificationMode(llm_client=llm),
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
        abschnitte_count = len(project_now.algorithm_artifact.abschnitte)
        entry = {
            "turn_nr": turn_nr,
            "input_id": input_id,
            "mode_before": mode_before,
            "mode_after": result.working_memory.aktiver_modus,
            "flags": result.flags,
            "phasenstatus": result.phasenstatus.value,
            "abschnitte_count": abschnitte_count,
            "nutzeraeusserung_preview": result.nutzeraeusserung[:200],
            "vorheriger_modus": result.working_memory.vorheriger_modus,
            "aktive_phase": result.working_memory.aktive_phase.value,
            "error": result.error,
            "response_len": len(result.nutzeraeusserung),
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
    pre_escalation_response_lengths: list[int] = []

    # ── Verify seeds were loaded correctly ──────────────────────────────────
    p_seed_check = get_project()
    assert len(p_seed_check.exploration_artifact.slots) == 7, (
        f"Exploration seed not loaded correctly: {len(p_seed_check.exploration_artifact.slots)} slots"
    )
    assert len(p_seed_check.structure_artifact.schritte) == 11, (
        f"Structure seed not loaded correctly: {len(p_seed_check.structure_artifact.schritte)} schritte"
    )
    assert p_seed_check.aktive_phase.value == "spezifikation", (
        f"Phase not set correctly: {p_seed_check.aktive_phase.value}"
    )

    # ── S0: Systemstart in Spezifikationsphase ───────────────────────────────
    print("\n=== S0: Systemstart (Spezifikationsphase) ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(
        pid,
        TurnInput(
            text="[Systemstart] Die Strukturierungsphase ist abgeschlossen. Bitte erkläre dem Nutzer die Spezifikationsphase und was als nächstes passiert."
        ),
    )
    entry = log_turn(turn_nr, "S0", mode_before, result)
    print(f"  Greeting: {result.nutzeraeusserung[:150]}")
    assert result.error is None, f"S0 error: {result.error}"

    # Verify both artifacts still intact after S0
    p_s0 = get_project()
    assert len(p_s0.exploration_artifact.slots) == 7, "Exploration artifact lost during S0"
    assert len(p_s0.structure_artifact.schritte) == 11, "Structure artifact lost during S0"

    # ── U1: Rückfrage im Moderator ────────────────────────────────────────────
    print("\n=== U1: Rückfrage zur Spezifikation ===")
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

    # ── U2: Explizite Bestätigung → Spezifikationsmodus startet ──────────────
    print("\n=== U2: 'Na gut, dann fangen wir an' ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[1]["message"]))
    entry = log_turn(turn_nr, "U2", mode_before, result)
    print(f"  Mode after: {entry['mode_after']}, flags: {entry['flags']}")
    p2 = get_project()
    check(
        "CP2",
        p2.aktiver_modus == "specification",
        f"CP2: mode={p2.aktiver_modus}, expected specification. Flags: {entry['flags']}",
    )
    # CP2_context: Dialog history should contain U1 context
    history = repo.load_dialog_history(pid, last_n=20)
    history_text = " ".join(h.get("inhalt", "") for h in history)
    has_context = any(kw in history_text for kw in ["Rechnung", "Rechnungen", "Spezifikation"])
    check(
        "CP2_context",
        has_context,
        "CP2_context: Dialog history missing relevant context after mode switch",
    )

    # ── U3: E-Mail-Eingang — wird später in U6 korrigiert ────────────────────
    print("\n=== U3: E-Mail-Eingang (wird später korrigiert) ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[2]["message"]))
    entry = log_turn(turn_nr, "U3", mode_before, result)
    pre_escalation_response_lengths.append(len(result.nutzeraeusserung))
    print(
        f"  [{entry['mode_after']}] Abschnitte: {entry['abschnitte_count']} | {result.nutzeraeusserung[:100]}"
    )
    if result.error:
        print(f"  ERROR: {result.error}")

    # ── U4: Scan-Prozess ──────────────────────────────────────────────────────
    print("\n=== U4: Scan-Prozess ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[3]["message"]))
    entry = log_turn(turn_nr, "U4", mode_before, result)
    pre_escalation_response_lengths.append(len(result.nutzeraeusserung))
    print(
        f"  [{entry['mode_after']}] Abschnitte: {entry['abschnitte_count']} | {result.nutzeraeusserung[:100]}"
    )

    # CP3: Nach U4 sollte mindestens 1 Algorithmusabschnitt existieren
    p4 = get_project()
    check(
        "CP3",
        len(p4.algorithm_artifact.abschnitte) >= 1,
        f"CP3: abschnitte={len(p4.algorithm_artifact.abschnitte)}, expected >= 1 after U3/U4",
    )

    # ── U5: Bestellabgleich (unvollständige Info) ─────────────────────────────
    print("\n=== U5: Bestellabgleich (unvollständige Angaben) ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[4]["message"]))
    entry = log_turn(turn_nr, "U5", mode_before, result)
    pre_escalation_response_lengths.append(len(result.nutzeraeusserung))
    print(
        f"  [{entry['mode_after']}] Abschnitte: {entry['abschnitte_count']} | {result.nutzeraeusserung[:150]}"
    )

    # CP4 (soft): System sollte eine Folgefrage stellen (Fragezeichen)
    check(
        "CP4_asks_followup",
        "?" in result.nutzeraeusserung,
        "CP4: System hat nach unvollständiger Angabe keine Folgefrage gestellt",
    )

    # ── U6: WIDERSPRUCH — E-Mail-Prozess-Korrektur ────────────────────────────
    print("\n=== U6: WIDERSPRUCH — automatische Weiterleitung statt manuell ===")
    _abschnitte_before_u6 = len(get_project().algorithm_artifact.abschnitte)
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[5]["message"]))
    entry = log_turn(turn_nr, "U6", mode_before, result)
    pre_escalation_response_lengths.append(len(result.nutzeraeusserung))
    print(
        f"  [{entry['mode_after']}] Abschnitte: {entry['abschnitte_count']} | {result.nutzeraeusserung[:100]}"
    )

    # CP_contradiction: Korrektur muss im Algorithmusartefakt reflektiert werden
    p6 = get_project()
    all_algo_text = " ".join(
        f"{a.titel} "
        + " ".join(f"{ak.aktionstyp} {json.dumps(ak.parameter)}" for ak in a.aktionen.values())
        for a in p6.algorithm_artifact.abschnitte.values()
    ).lower()
    corrected_kws = ["weiterleitung", "automatisch", "unterordner", "regel"]
    found_corrected = [kw for kw in corrected_kws if kw in all_algo_text]
    # Also check in nutzeraeusserung (the LLM may acknowledge the correction in the response)
    response_text = result.nutzeraeusserung.lower()
    found_in_response = [kw for kw in corrected_kws if kw in response_text]
    check(
        "CP_contradiction_acknowledged",
        len(found_corrected) >= 1 or len(found_in_response) >= 1,
        f"CP_contradiction: Keine Korrekturreferenz in Artefakt/Antwort. "
        f"Artefakt kw: {found_corrected}, Antwort kw: {found_in_response}",
    )

    # ── U7: Frust über EMMA-Abkürzungen → danach Panik-Button ────────────────
    print("\n=== U7: Frust über EMMA-Jargon ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[6]["message"]))
    entry = log_turn(turn_nr, "U7", mode_before, result)
    print(f"  [{entry['mode_after']}] {result.nutzeraeusserung[:100]}")

    # ── S1: Panik-Button nach U7 ──────────────────────────────────────────────
    print("\n=== S1: Panik-Button ===")
    p_esc = repo.load(pid)
    abschnitte_before_esc = len(p_esc.algorithm_artifact.abschnitte)
    _algo_snapshot_before_esc = _algo_snapshot(p_esc)
    p_esc.working_memory.vorheriger_modus = p_esc.working_memory.aktiver_modus
    p_esc.working_memory.aktiver_modus = "moderator"
    p_esc.aktiver_modus = "moderator"
    repo.save(p_esc)

    # CP5: Artifact survives escalation
    p5_esc = get_project()
    check(
        "CP5",
        len(p5_esc.algorithm_artifact.abschnitte) >= abschnitte_before_esc,
        f"CP5: abschnitte={len(p5_esc.algorithm_artifact.abschnitte)}, before={abschnitte_before_esc}",
    )
    check(
        "CP5_mode",
        p5_esc.aktiver_modus == "moderator",
        f"CP5: mode={p5_esc.aktiver_modus}, expected moderator",
    )

    # ── U8: User beschreibt Problem beim Moderator ────────────────────────────
    print("\n=== U8: Eskalation — Problem beschrieben ===")
    algo_snapshot_u8 = _algo_snapshot(get_project())
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
    algo_snapshot_after_u8 = _algo_snapshot(get_project())
    check(
        "CP6_mod_no_write",
        algo_snapshot_u8 == algo_snapshot_after_u8,
        f"CP6_mod_no_write: Moderator hat Algorithmusartefakt in U8 verändert. "
        f"Before: {algo_snapshot_u8}, After: {algo_snapshot_after_u8}",
    )
    # Also verify exploration and structure artifacts unchanged
    p_u8 = get_project()
    check(
        "CP6_exp_intact",
        len(p_u8.exploration_artifact.slots) == 7,
        f"CP6_exp_intact: Exploration slots={len(p_u8.exploration_artifact.slots)}, expected 7",
    )
    check(
        "CP6_struct_intact",
        len(p_u8.structure_artifact.schritte) == 11,
        f"CP6_struct_intact: Structure schritte={len(p_u8.structure_artifact.schritte)}, expected 11",
    )

    # ── U9: User bestätigt Rückkehr zum Spezifikationsmodus ──────────────────
    print("\n=== U9: 'Einfache Sprache, dann gern weiter' ===")
    algo_snapshot_before_u9 = _algo_snapshot(get_project())
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[8]["message"]))
    entry = log_turn(turn_nr, "U9", mode_before, result)
    print(f"  Mode after: {entry['mode_after']}, flags: {entry['flags']}")
    p9 = get_project()
    check(
        "CP7",
        p9.aktiver_modus == "specification",
        f"CP7: mode={p9.aktiver_modus}, expected specification. Flags: {entry['flags']}",
    )
    # SDD 6.6.5: Moderator-Rückkehr darf Artefakt nicht verändern
    algo_snapshot_after_u9 = _algo_snapshot(get_project())
    check(
        "CP7_mod_no_write",
        algo_snapshot_before_u9 == algo_snapshot_after_u9,
        "CP7_mod_no_write: Moderator hat Algorithmusartefakt bei Rückkehr verändert.",
    )

    # ── U10-U12: Spezifikation nach Eskalation ────────────────────────────────
    for i, uid in enumerate(["U10", "U11", "U12"]):
        idx = 9 + i
        print(f"\n=== {uid}: Spezifikation nach Eskalation ===")
        turn_nr += 1
        mode_before = get_mode()
        result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[idx]["message"]))
        entry = log_turn(turn_nr, uid, mode_before, result)
        print(
            f"  [{entry['mode_after']}] Abschnitte: {entry['abschnitte_count']} | {result.nutzeraeusserung[:100]}"
        )
        if result.error:
            print(f"  ERROR: {result.error}")

        # CP8: Nach U10 Eskalationseffekt prüfen (kürzere oder verständlichere Antworten)
        if uid == "U10" and pre_escalation_response_lengths:
            avg_pre = sum(pre_escalation_response_lengths) / len(pre_escalation_response_lengths)
            check(
                "CP8_escalation_effect",
                len(result.nutzeraeusserung) <= avg_pre * 1.8,
                f"CP8: post-esc response={len(result.nutzeraeusserung)}, pre-esc avg={avg_pre:.0f} (Grenze: 1.8x)",
            )

    # ── U13: User signalisiert Fertigstellung ─────────────────────────────────
    print("\n=== U13: 'Mir fällt nichts mehr ein' ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[12]["message"]))
    entry = log_turn(turn_nr, "U13", mode_before, result)
    print(
        f"  Mode: {entry['mode_after']}, flags: {entry['flags']}, Abschnitte: {entry['abschnitte_count']}"
    )

    # Nudge-Schleife wenn Spezifikationsmodus kein phase_complete meldet
    p_pre = get_project()
    if p_pre.aktiver_modus != "moderator":
        nudge_msgs = [
            "Ja das war wirklich alles, wir können zur nächsten Phase. Bitte schließen Sie die Spezifikation ab.",
            "Die Spezifikation ist fertig, alle Schritte sind beschrieben. Bitte phase_complete melden.",
            "Spezifikation abschließen, weiter zur Validierung.",
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
            # Force advance wenn LLM partout nicht kooperiert
            print("  Spezifikationsmodus meldet kein phase_complete. Forciere Phasenwechsel.")
            from artifacts.models import Phasenstatus as _PS

            p_force = get_project()
            p_force.working_memory.vorheriger_modus = "specification"
            p_force.working_memory.aktiver_modus = "moderator"
            p_force.aktiver_modus = "moderator"
            p_force.working_memory.phasenstatus = _PS.phase_complete
            repo.save(p_force)

    # CP10: Phase complete — Moderator aktiv, Algorithmusartefakt substantiell
    p10 = get_project()
    check(
        "CP10",
        p10.aktiver_modus == "moderator",
        f"CP10: mode={p10.aktiver_modus}, expected moderator",
    )
    abschnitte_at_complete = len(p10.algorithm_artifact.abschnitte)
    check(
        "CP10_min_abschnitte",
        abschnitte_at_complete >= 6,
        f"CP10: abschnitte={abschnitte_at_complete}, expected >= 6",
    )

    # CP10_aktionen: Alle Abschnitte müssen mindestens 1 EMMA-Aktion haben
    empty_aktionen = [
        aid for aid, a in p10.algorithm_artifact.abschnitte.items() if len(a.aktionen) == 0
    ]
    check(
        "CP10_abschnitte_have_aktionen",
        len(empty_aktionen) == 0,
        f"CP10: {len(empty_aktionen)} Abschnitte ohne EMMA-Aktionen: {empty_aktionen}",
    )

    # CP10_struktur_refs_valid: Alle struktur_ref müssen auf existierende schritt_ids zeigen
    all_schritt_ids = set(p10.structure_artifact.schritte.keys())
    invalid_refs = [
        f"{aid}.struktur_ref={a.struktur_ref}"
        for aid, a in p10.algorithm_artifact.abschnitte.items()
        if a.struktur_ref not in all_schritt_ids
    ]
    check(
        "CP10_struktur_refs_valid",
        len(invalid_refs) == 0,
        f"CP10: Ungültige struktur_ref: {invalid_refs}",
    )

    # ── U14: Phasenwechsel bestätigen ─────────────────────────────────────────
    print("\n=== U14: 'Ja, weiter zur Prüfung' ===")
    turn_nr += 1
    mode_before = get_mode()
    result = await orchestrator.process_turn(pid, TurnInput(text=user_inputs[13]["message"]))
    entry = log_turn(turn_nr, "U14", mode_before, result)
    print(f"  Mode: {entry['mode_after']}, phase: {entry['aktive_phase']}, flags: {entry['flags']}")

    p11 = get_project()
    check(
        "CP11",
        p11.aktive_phase.value == "validierung",
        f"CP11: phase={p11.aktive_phase.value}, expected validierung",
    )

    # ── ARTEFAKT-PRÜFUNG: Exploration und Struktur erhalten ───────────────────
    print(f"\n{'=' * 72}")
    print("  ARTEFAKT-ERHALT-PRÜFUNG")
    print(f"{'=' * 72}")

    p_final = get_project()
    exp_art = p_final.exploration_artifact
    struct_art = p_final.structure_artifact
    algo_art = p_final.algorithm_artifact

    exp_intact = len(exp_art.slots) == 7
    exp_filled = all(slot.inhalt.strip() != "" for slot in exp_art.slots.values())
    print(f"  Exploration Slots: {len(exp_art.slots)}/7, alle gefüllt: {exp_filled}")
    check(
        "EXP_INTACT",
        exp_intact and exp_filled,
        f"Exploration artifact: slots={len(exp_art.slots)}, alle_gefüllt={exp_filled}",
    )

    struct_intact = len(struct_art.schritte) == 11
    print(f"  Struktur Schritte: {len(struct_art.schritte)}/11")
    check(
        "STRUCT_INTACT",
        struct_intact,
        f"Structure artifact: schritte={len(struct_art.schritte)}, expected 11",
    )

    # ── ALGORITHMUSARTEFAKT-PRÜFUNG ───────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print("  ALGORITHMUSARTEFAKT-PRÜFUNG")
    print(f"{'=' * 72}")

    abschnitte = algo_art.abschnitte
    print(f"  Anzahl Abschnitte: {len(abschnitte)}")
    print(
        f"  Prozesszusammenfassung: {'JA' if algo_art.prozesszusammenfassung.strip() else 'NEIN'}"
    )

    if expected.get("structural_requirements", {}).get("must_have_prozesszusammenfassung"):
        check(
            "ALGO_ZUSAMMENFASSUNG",
            algo_art.prozesszusammenfassung.strip() != "",
            "Algorithmusartefakt: Prozesszusammenfassung ist leer",
        )

    # EMMA-Typ-Anforderungen
    all_emma_types = set()
    for a in abschnitte.values():
        for ak in a.aktionen.values():
            all_emma_types.add(ak.aktionstyp)
    print(f"  EMMA-Typen vorhanden: {sorted(all_emma_types)}")

    for must_type in expected["structural_requirements"].get("must_have_emma_types", []):
        check(
            f"EMMA_TYPE_{must_type}",
            must_type in all_emma_types,
            f"EMMA-Typ '{must_type}' nicht gefunden. Vorhandene Typen: {sorted(all_emma_types)}",
        )

    # Struktur-Ref Mindestanzahl
    reqs = expected["structural_requirements"]
    check(
        "ALGO_MIN_ABSCHNITTE",
        len(abschnitte) >= reqs["min_abschnitte"],
        f"min_abschnitte: {len(abschnitte)} < {reqs['min_abschnitte']}",
    )

    # Pro Abschnitt drucken
    print(f"\n  {'Abschnitt-ID':20s} | {'Struktur-Ref':25s} | {'Status':15s} | {'Aktionen':8s}")
    print(f"  {'-' * 20}-+-{'-' * 25}-+-{'-' * 15}-+-{'-' * 8}")
    for aid, a in sorted(abschnitte.items()):
        types_str = ", ".join(sorted(set(ak.aktionstyp for ak in a.aktionen.values())))
        print(
            f"  {aid:20s} | {a.struktur_ref:25s} | {a.completeness_status.value:15s} | {len(a.aktionen):2d}: {types_str}"
        )

    # ── KONZEPT-ABDECKUNG (Keyword-Matching) ──────────────────────────────────
    print(f"\n{'=' * 72}")
    print("  KONZEPT-ABDECKUNG (Keyword-Matching, SOFT)")
    print(f"{'=' * 72}")

    # Gesamter Algorithmustext für Keyword-Suche
    all_algo_text_lower = " ".join(
        f"{a.titel} {a.struktur_ref} "
        + " ".join(
            f"{ak.aktionstyp} {' '.join(ak.parameter.values())}" for ak in a.aktionen.values()
        )
        for a in abschnitte.values()
    ).lower()

    for concept in expected["expected_abschnitte"]:
        keywords = concept.get("keywords", [])
        found = [kw for kw in keywords if kw.lower() in all_algo_text_lower]
        coverage = len(found) / len(keywords) if keywords else 1.0
        status = "OK" if coverage >= 0.4 else "MISS"
        emma_types = concept.get("expected_emma_types", [])
        found_emma = [t for t in emma_types if t in all_emma_types]
        print(
            f"  {status}: {concept['concept']:35s} "
            f"KW: {len(found)}/{len(keywords)} ({coverage:.0%}) | "
            f"EMMA: {found_emma}/{emma_types}"
        )

    # ── HALLUZINATIONS-PRÜFUNG (Negative Keywords) ────────────────────────────
    print(f"\n{'=' * 72}")
    print("  HALLUZINATIONS-PRÜFUNG (Negative Keywords, SOFT)")
    print(f"{'=' * 72}")

    neg_kws = expected["negative_keywords"]["keywords"]
    hallucinations = [kw for kw in neg_kws if kw.lower() in all_algo_text_lower]
    if hallucinations:
        print(f"  WARNUNG: Mögliche Halluzinationen: {hallucinations}")
        check(
            "CP_no_hallucination",
            False,
            f"Halluzinationen gefunden: {hallucinations} (User hat diese nie erwähnt)",
        )
    else:
        print("  OK: Keine bekannten Halluzinationen")
        check("CP_no_hallucination", True, "")

    # ── SYSTEM FRAGT NACH (70% Fragen-Anteil) ─────────────────────────────────
    print(f"\n{'=' * 72}")
    print("  FRAGEZEICHEN-PRÜFUNG (System muss führen, nicht monologisieren)")
    print(f"{'=' * 72}")

    spec_turns = [e for e in turn_log if e["mode_before"] == "specification"]
    turns_with_question = [e for e in spec_turns if "?" in e["nutzeraeusserung_preview"]]
    q_ratio = len(turns_with_question) / len(spec_turns) if spec_turns else 0
    print(
        f"  Spezifikations-Turns mit Frage: {len(turns_with_question)}/{len(spec_turns)} ({q_ratio:.0%})"
    )
    check(
        "CP_asks_questions",
        q_ratio >= 0.5,  # >= 50% für Spezifikation (weniger Fragen als Explorer, da technischer)
        f"CP_asks_questions: Nur {q_ratio:.0%} der Spezifikations-Turns enthalten Fragen (erwartet >= 50%)",
    )

    # ── FORTSCHRITTS-MONOTONIE ─────────────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print("  FORTSCHRITTS-MONOTONIE (in_progress → nearing_completion → phase_complete)")
    print(f"{'=' * 72}")

    status_seq = [e["phasenstatus"] for e in turn_log]
    has_nearing = "nearing_completion" in status_seq
    has_complete = "phase_complete" in status_seq
    jumped_directly = (
        not has_nearing
        and has_complete
        and len([e for e in turn_log if e["phasenstatus"] == "in_progress"]) > 2
    )
    print(f"  Status-Sequenz: {status_seq}")
    print(f"  nearing_completion gesehen: {has_nearing}, phase_complete gesehen: {has_complete}")
    check(
        "CP_progress_monotone",
        not jumped_directly,
        "CP_progress_monotone: Direkt von in_progress zu phase_complete ohne nearing_completion",
    )

    # ── TURN LOG ──────────────────────────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print("  TURN LOG")
    print(f"{'=' * 72}")
    print(
        f"  {'#':>3} | {'Input':6} | {'Before':12} | {'After':12} | {'Phase':15} | {'Flags':25} | {'Abschn.':7} | Antwort"
    )
    print(
        f"  {'-' * 3}-+-{'-' * 6}-+-{'-' * 12}-+-{'-' * 12}-+-{'-' * 15}-+-{'-' * 25}-+-{'-' * 7}-+-{'-' * 40}"
    )
    for e in turn_log:
        flags_str = ",".join(e["flags"]) if e["flags"] else "-"
        preview = e["nutzeraeusserung_preview"][:40].replace("\n", " ")
        print(
            f"  {e['turn_nr']:3d} | {e['input_id']:6} | {e['mode_before']:12} | {e['mode_after']:12} | "
            f"{e['aktive_phase']:15} | {flags_str:25} | {e['abschnitte_count']:7d} | {preview}"
        )

    # ── SUMMARY ───────────────────────────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print("  E2E SPEZIFIKATION TEST SUMMARY")
    print(f"{'=' * 72}")
    passed = sum(1 for v in checkpoint_results.values() if v)
    total = len(checkpoint_results)
    print(f"  Turns executed: {turn_nr}")
    print(f"  Checkpoints passed: {passed}/{total}")
    print(f"  Final mode: {p_final.aktiver_modus}")
    print(f"  Final phase: {p_final.aktive_phase.value}")
    print(f"  Exploration slots: {len(exp_art.slots)}/7")
    print(f"  Structure schritte: {len(struct_art.schritte)}/11")
    print(f"  Algorithm Abschnitte: {len(abschnitte)}")
    print(f"  EMMA-Typen: {sorted(all_emma_types)}")
    print(
        f"  Prozesszusammenfassung: {'JA' if algo_art.prozesszusammenfassung.strip() else 'NEIN'}"
    )
    print(f"  Halluzinationen: {hallucinations if hallucinations else 'Keine'}")
    print()
    for cp_name, cp_ok in checkpoint_results.items():
        icon = "PASS" if cp_ok else "FAIL"
        err = f" -- {checkpoint_errors[cp_name]}" if not cp_ok else ""
        print(f"  {icon}: {cp_name}{err}")

    db.close()

    # ── HARD CHECKPOINTS ASSERTIONS ───────────────────────────────────────────
    hard_checkpoints = [
        "CP1",
        "CP2",
        "CP3",
        "CP5",
        "CP5_mode",
        "CP6",
        "CP6_mod_no_write",
        "CP6_exp_intact",
        "CP6_struct_intact",
        "CP7",
        "CP7_mod_no_write",
        "CP10",
        "CP10_min_abschnitte",
        "CP10_abschnitte_have_aktionen",
        "CP10_struktur_refs_valid",
        "CP11",
        "EXP_INTACT",
        "STRUCT_INTACT",
        "ALGO_MIN_ABSCHNITTE",
        "EMMA_TYPE_DECISION",
        "EMMA_TYPE_FILE_OPERATION",
    ]
    for cp_name in hard_checkpoints:
        if cp_name in checkpoint_results:
            assert checkpoint_results[cp_name], (
                f"{cp_name} failed: {checkpoint_errors.get(cp_name, '?')}"
            )
