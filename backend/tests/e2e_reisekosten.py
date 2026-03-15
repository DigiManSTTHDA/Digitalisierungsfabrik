"""End-to-End Test: Reisekosten-Dialog über WebSocket (in-process).

Simuliert einen echten User-Dialog komplett in-process:
- FastAPI TestClient mit echter DB (Datei, nicht :memory:)
- Echter LLM-Call (OpenAI GPT-4o via konfigurierte .env)
- Echter Orchestrator → ExplorationMode → Executor → SQLite

Liest User-Nachrichten aus dialog-reisekosten.jsonl, sendet sie sequentiell
per WebSocket, wartet jeweils die System-Antwort ab, und vergleicht am Ende
das Exploration-Artifact mit expected-artifact-reisekosten.json.

Aufruf:
    cd backend
    source .venv/Scripts/activate
    python tests/e2e_reisekosten.py
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from difflib import SequenceMatcher
from pathlib import Path

# Ensure backend is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

os.chdir(backend_dir)

from fastapi.testclient import TestClient  # noqa: E402

from main import create_app  # noqa: E402

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

TEST_DATA = Path(__file__).resolve().parent.parent.parent / "frontend" / "test-texte"
DIALOG_FILE = TEST_DATA / "dialog-reisekosten.jsonl"
EXPECTED_FILE = TEST_DATA / "expected-artifact-reisekosten.json"

# How many events to expect per successful turn
EVENTS_PER_TURN = 6  # chat_done + 3x artifact_update + progress_update + debug_update


def load_dialog() -> list[dict]:  # type: ignore[type-arg]
    with open(DIALOG_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_expected() -> dict:  # type: ignore[type-arg]
    with open(EXPECTED_FILE, encoding="utf-8") as f:
        return json.load(f)


def run_dialog(
    client: TestClient,
    projekt_id: str,
    dialog: list[dict],  # type: ignore[type-arg]
) -> list[dict]:  # type: ignore[type-arg]
    """Run the full dialog over WebSocket. Returns list of system responses."""
    user_turns = [t for t in dialog if t["role"] == "user"]
    system_responses: list[dict] = []  # type: ignore[type-arg]

    with client.websocket_connect(f"/ws/session/{projekt_id}") as ws:
        print(f"\n  WebSocket verbunden. {len(user_turns)} User-Turns zu senden.\n")

        for i, turn in enumerate(user_turns):
            turn_num = turn["turn"]
            desc = turn.get("description", "")
            msg_preview = turn["message"][:80].replace("\n", " ")

            print(f"  {'─' * 60}")
            print(f"  Turn {turn_num} (User #{i + 1}/{len(user_turns)})")
            print(f"  [{desc}]")
            print(f'  → "{msg_preview}..."')

            t0 = time.time()
            ws.send_text(json.dumps({"type": "turn", "text": turn["message"]}))

            # Collect response events
            events: list[dict] = []  # type: ignore[type-arg]
            chat_response: str | None = None
            error_msg: str | None = None

            for _ in range(EVENTS_PER_TURN):
                try:
                    event = ws.receive_json()
                    events.append(event)
                    etype = event.get("event")

                    if etype == "chat_done":
                        chat_response = event.get("message", "")
                    elif etype == "error":
                        error_msg = event.get("message", "?")
                        break
                except Exception as exc:
                    print(f"  ⚠ Event-Empfang fehlgeschlagen: {exc}")
                    break

            elapsed = time.time() - t0

            if error_msg:
                print(f"  ✗ ERROR ({elapsed:.1f}s): {error_msg}")
            elif chat_response:
                preview = chat_response[:150].replace("\n", " ")
                print(f'  ← System ({elapsed:.1f}s): "{preview}"')
            else:
                print(f"  ⚠ Keine chat_done Antwort erhalten ({elapsed:.1f}s)")
                print(f"    Events: {[e.get('event') for e in events]}")

            print()

            system_responses.append(
                {
                    "user_turn": turn_num,
                    "user_description": desc,
                    "system_response": chat_response,
                    "error": error_msg,
                    "elapsed_seconds": round(elapsed, 1),
                    "event_count": len(events),
                }
            )

    return system_responses


def similarity(a: str, b: str) -> float:
    """Compute text similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def keyword_coverage(expected_text: str, actual_text: str) -> tuple[list[str], list[str]]:
    """Extract key phrases from expected and check which appear in actual.

    Uses substring matching: a keyword like 'Reisekosten' matches
    'Reisekostenerfassung' in the actual text. This prevents false negatives
    from compound words and different word forms.
    """
    chunks = re.split(r"[.;]\s*", expected_text)
    chunks = [c.strip() for c in chunks if len(c.strip()) > 15]

    actual_lower = actual_text.lower()

    found = []
    missing = []
    for chunk in chunks:
        words = [w for w in chunk.split() if len(w) > 4]
        if not words:
            continue
        # Substring matching: "Reisekosten" matches "Reisekostenerfassung"
        matches = sum(
            1
            for w in words
            if w.lower() in actual_lower
            or any(w.lower() in aw or aw in w.lower() for aw in actual_lower.split())
        )
        ratio = matches / len(words) if words else 0
        if ratio >= 0.35:
            found.append(chunk)
        else:
            missing.append(chunk)

    return found, missing


def compare_artifacts(actual_exploration: dict, expected: dict) -> dict:  # type: ignore[type-arg]
    """Compare actual exploration artifact against expected, slot by slot."""
    results: dict = {}  # type: ignore[type-arg]
    expected_slots = expected.get("slots", {})
    actual_slots = actual_exploration.get("slots", {})

    print(f"\n{'=' * 72}")
    print("  ARTIFACT-VERGLEICH: Slot für Slot")
    print(f"{'=' * 72}")

    all_slot_ids = sorted(set(list(expected_slots.keys()) + list(actual_slots.keys())))

    total_score = 0.0
    total_slots = 0

    for slot_id in all_slot_ids:
        exp = expected_slots.get(slot_id)
        act = actual_slots.get(slot_id)

        if exp is None:
            print(f"\n  [{slot_id}] + EXTRA — existiert im Actual aber nicht im Expected")
            results[slot_id] = {"status": "extra", "score": 0}
            continue

        if act is None:
            print(f"\n  [{slot_id}] ✗ FEHLT — erwartet aber nicht vorhanden")
            results[slot_id] = {"status": "missing", "score": 0}
            total_slots += 1
            continue

        total_slots += 1
        exp_inhalt = exp.get("inhalt", "")
        act_inhalt = act.get("inhalt", "")
        exp_status = exp.get("completeness_status", "")
        act_status = act.get("completeness_status", "")

        sim = similarity(exp_inhalt, act_inhalt)
        found, missing = keyword_coverage(exp_inhalt, act_inhalt)
        coverage = len(found) / (len(found) + len(missing)) if (found or missing) else 0
        score = coverage * 0.6 + sim * 0.4
        total_score += score

        status_match = exp_status == act_status

        if score >= 0.7:
            grade, icon = "GUT", "✓"
        elif score >= 0.4:
            grade, icon = "TEILWEISE", "~"
        else:
            grade, icon = "SCHLECHT", "✗"

        status_icon = "✓" if status_match else "✗"

        print(
            f"\n  [{slot_id}] {icon} {grade} "
            f"(Score: {score:.0%}, Sim: {sim:.0%}, Keywords: {coverage:.0%})"
        )
        print(f"    Titel: {exp.get('titel', '?')}")
        print(f"    Status: {status_icon} expected={exp_status}, actual={act_status}")

        if act_inhalt:
            preview = act_inhalt[:200].replace("\n", " ")
            print(f'    Actual: "{preview}"')
        else:
            print("    Actual: [LEER]")

        if missing:
            print(f"    Fehlende Aspekte ({len(missing)}):")
            for m in missing[:5]:
                print(f"      - {m[:100]}")

        results[slot_id] = {
            "status": grade.lower(),
            "score": round(score, 3),
            "similarity": round(sim, 3),
            "keyword_coverage": round(coverage, 3),
            "status_match": status_match,
            "missing_aspects": [m[:120] for m in missing[:10]],
        }

    avg_score = total_score / total_slots if total_slots > 0 else 0

    print(f"\n{'=' * 72}")
    print(f"  GESAMT-SCORE: {avg_score:.0%} ({total_slots} Slots bewertet)")
    print(f"{'=' * 72}")

    results["_summary"] = {
        "average_score": round(avg_score, 3),
        "total_slots_evaluated": total_slots,
        "slots_in_actual": len(actual_slots),
        "slots_in_expected": len(expected_slots),
    }

    return results


def send_one_turn(
    ws,  # type: ignore[no-untyped-def]
    text: str,
    label: str = "",
) -> dict:  # type: ignore[type-arg]
    """Send a single turn message and collect the response."""
    t0 = time.time()
    ws.send_text(json.dumps({"type": "turn", "text": text}))

    events: list[dict] = []  # type: ignore[type-arg]
    chat_response: str | None = None
    error_msg: str | None = None

    for _ in range(EVENTS_PER_TURN):
        try:
            event = ws.receive_json()
            events.append(event)
            if event.get("event") == "chat_done":
                chat_response = event.get("message", "")
            elif event.get("event") == "error":
                error_msg = event.get("message", "?")
                break
        except Exception:
            break

    elapsed = time.time() - t0
    if label:
        preview = (chat_response or error_msg or "")[:150].replace("\n", " ")
        print(f"  [{label}] ({elapsed:.1f}s): {preview}")

    return {
        "text": text,
        "label": label,
        "system_response": chat_response,
        "error": error_msg,
        "elapsed_seconds": round(elapsed, 1),
        "events": events,
    }


def main() -> None:
    print("=" * 72)
    print("  E2E-TEST: Reisekostenabrechnung (Full Chain)")
    print("  Moderator Greeting → Explorer Dialog → Moderator Phase-Transition")
    print("  Stack: FastAPI TestClient → Orchestrator → OpenAI GPT-4o → SQLite")
    print("=" * 72)

    # Load test data
    dialog = load_dialog()
    expected = load_expected()
    user_turns = [t for t in dialog if t["role"] == "user"]
    print(f"\n  Dialog geladen: {len(dialog)} Turns total, {len(user_turns)} User-Turns")

    # Create app + client
    app = create_app()
    client = TestClient(app)

    # Create project via REST
    resp = client.post(
        "/api/projects",
        json={"name": "E2E Reisekosten", "beschreibung": "Automatischer E2E-Test"},
    )
    assert resp.status_code == 201, f"Projekt-Erstellung fehlgeschlagen: {resp.text}"
    projekt_id = resp.json()["projekt_id"]
    aktiver_modus = resp.json()["aktiver_modus"]
    print(f"  Projekt erstellt: {projekt_id}")
    print(f"  Aktiver Modus: {aktiver_modus}")
    assert aktiver_modus == "moderator", (
        f"Neues Projekt muss mit Moderator starten (FR-D-11), ist: {aktiver_modus}"
    )

    # ──────────────────────────────────────────────────────────────────
    # PHASE 1: Moderator Greeting (FR-D-11)
    # ──────────────────────────────────────────────────────────────────
    print(f"\n{'─' * 72}")
    print("  PHASE 1: MODERATOR-BEGRUESSUNG (FR-D-11)")
    print(f"{'─' * 72}")

    with client.websocket_connect(f"/ws/session/{projekt_id}") as ws:
        greeting = send_one_turn(
            ws, "Hallo, ich möchte einen Prozess beschreiben.", "Moderator Greeting"
        )

    assert greeting["system_response"], "Moderator muss eine Begruessung senden"
    assert not greeting["error"], f"Moderator Greeting Error: {greeting['error']}"
    print("\n  Moderator Greeting: OK")
    print(f"  Antwort: {greeting['system_response'][:200]}")

    # Check that mode switched to exploration after greeting
    proj_after_greeting = client.get(f"/api/projects/{projekt_id}").json()
    modus_after = proj_after_greeting["aktiver_modus"]
    print(f"  Modus nach Greeting: {modus_after}")
    assert modus_after == "exploration", (
        f"Nach Moderator-Greeting muss Modus 'exploration' sein, ist: {modus_after}"
    )

    # ──────────────────────────────────────────────────────────────────
    # PHASE 2: Explorer Dialog (existing test)
    # ──────────────────────────────────────────────────────────────────
    print(f"\n{'─' * 72}")
    print("  PHASE 2: EXPLORER-DIALOG (13 User-Turns)")
    print(f"{'─' * 72}")

    t_start = time.time()
    responses = run_dialog(client, projekt_id, dialog)
    t_total = time.time() - t_start

    successful = sum(1 for r in responses if r["system_response"] and not r["error"])
    errors = sum(1 for r in responses if r["error"])

    print(f"  Dialog abgeschlossen in {t_total:.0f}s")
    print(f"  {successful}/{len(responses)} Turns erfolgreich, {errors} Fehler")
    print(f"  Durchschnitt: {t_total / len(responses):.1f}s pro Turn")

    # Fetch final artifact
    resp = client.get(f"/api/projects/{projekt_id}/artifacts")
    assert resp.status_code == 200
    actual_exploration = resp.json().get("exploration", {})

    # Compare
    results = compare_artifacts(actual_exploration, expected)

    # Final assessment
    summary = results.get("_summary", {})
    avg = summary.get("average_score", 0)

    print(f"\n{'=' * 72}")
    print("  BEWERTUNG DES EXPLORATION-MODUS")
    print(f"{'=' * 72}")

    if avg >= 0.7:
        verdict = "GUT"
        print(f"  Gesamtbewertung: {verdict} ({avg:.0%})")
        print("  Der Explorer extrahiert die wesentlichen Informationen aus")
        print("  dem rambling User-Input und strukturiert sie korrekt in Slots.")
    elif avg >= 0.4:
        verdict = "BEFRIEDIGEND"
        print(f"  Gesamtbewertung: {verdict} ({avg:.0%})")
        print("  Der Explorer erfasst die Grundstruktur, aber es fehlen")
        print("  Details oder Informationen werden nicht korrekt zugeordnet.")
    else:
        verdict = "UNGENUEGEND"
        print(f"  Gesamtbewertung: {verdict} ({avg:.0%})")
        print("  Der Explorer hat erhebliche Schwierigkeiten, die relevanten")
        print("  Informationen aus dem Dialog zu extrahieren und zu strukturieren.")

    # Print dialog flow summary
    print(f"\n{'─' * 72}")
    print("  DIALOG-VERLAUF (Kurzfassung)")
    print(f"{'─' * 72}")
    for r in responses:
        status = "✓" if r["system_response"] and not r["error"] else "✗"
        resp_preview = ""
        if r["system_response"]:
            resp_preview = r["system_response"][:80].replace("\n", " ")
        elif r["error"]:
            resp_preview = f"ERROR: {r['error'][:60]}"
        print(f"  {status} Turn {r['user_turn']:2d} ({r['elapsed_seconds']:5.1f}s): {resp_preview}")

    # ──────────────────────────────────────────────────────────────────
    # PHASE 3: Moderator Phase-Transition (simulate phase_complete)
    # ──────────────────────────────────────────────────────────────────
    print(f"\n{'─' * 72}")
    print("  PHASE 3: MODERATOR PHASE-TRANSITION")
    print(f"{'─' * 72}")

    # Use debug endpoint to advance phase — simulates the Moderator flow
    # (In production, the Explorer would set phase_complete → Moderator activates)
    proj_state = client.get(f"/api/projects/{projekt_id}").json()
    print(f"  Aktuelle Phase: {proj_state['aktive_phase']}")
    print(f"  Aktiver Modus: {proj_state['aktiver_modus']}")

    advance_resp = client.post(f"/api/projects/{projekt_id}/debug/advance-phase")
    if advance_resp.status_code == 200:
        new_phase = advance_resp.json()["project"]["aktive_phase"]
        new_modus = advance_resp.json()["project"]["aktiver_modus"]
        print(f"  Phase advanced: {proj_state['aktive_phase']} -> {new_phase}")
        print(f"  Neuer Modus: {new_modus}")
        phase_transition_ok = new_phase == "strukturierung"
    else:
        print(f"  Phase advance fehlgeschlagen: {advance_resp.status_code}")
        phase_transition_ok = False

    # ──────────────────────────────────────────────────────────────────
    # FINAL SUMMARY
    # ──────────────────────────────────────────────────────────────────
    print(f"\n{'=' * 72}")
    print("  GESAMTERGEBNIS")
    print(f"{'=' * 72}")
    print(
        f"  Moderator Greeting:     {'OK' if greeting['system_response'] and not greeting['error'] else 'FAIL'}"
    )
    print(f"  Modus-Handoff:          {'OK' if modus_after == 'exploration' else 'FAIL'}")
    print(f"  Explorer Dialog:        {successful}/{len(responses)} Turns OK")
    print(f"  Artifact Score:         {avg:.0%} ({verdict})")
    print(f"  Phase Transition:       {'OK' if phase_transition_ok else 'FAIL'}")

    print(f"\n  Projekt-ID: {projekt_id}")
    print(f"  Gesamtdauer: {t_total:.0f}s")
    print()

    # Write results to file
    results_file = TEST_DATA / "e2e-results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "projekt_id": projekt_id,
                "verdict": verdict,
                "average_score": avg,
                "total_duration_seconds": round(t_total, 1),
                "turns_successful": successful,
                "turns_total": len(responses),
                "responses": [
                    {
                        "user_turn": r["user_turn"],
                        "user_description": r["user_description"],
                        "system_response": r["system_response"],
                        "error": r["error"],
                        "elapsed_seconds": r["elapsed_seconds"],
                    }
                    for r in responses
                ],
                "slot_comparison": results,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"  Ergebnisse gespeichert: {results_file}")

    # Exit code based on result
    sys.exit(0 if avg >= 0.4 else 1)


if __name__ == "__main__":
    main()
