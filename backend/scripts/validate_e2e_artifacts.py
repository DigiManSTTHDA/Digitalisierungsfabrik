#!/usr/bin/env python3
"""Post-hoc artifact validator for manual E2E tests.

Run this after a manual walkthrough (see agent-docs/e2e-human-playbook.md)
to check all deterministic assertions against the project's DB state.

Usage:
    cd backend
    source .venv/bin/activate
    python scripts/validate_e2e_artifacts.py [projekt_id]

If no projekt_id is given, validates the most recently modified project.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure backend is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from persistence.database import Database  # noqa: E402
from persistence.project_repository import ProjectRepository  # noqa: E402


def _load_project(repo: ProjectRepository, projekt_id: str | None):  # noqa: ANN201
    """Load a specific project or the most recent one."""
    if projekt_id:
        return repo.load(projekt_id)
    projects = repo.list_projects()
    if not projects:
        print("FEHLER: Keine Projekte in der Datenbank.")
        sys.exit(1)
    return projects[0]


def _print_header(title: str) -> None:
    print(f"\n{'=' * 72}")
    print(f"  {title}")
    print(f"{'=' * 72}")


class ValidationResult:
    def __init__(self) -> None:
        self.checks: dict[str, bool] = {}
        self.errors: dict[str, str] = {}

    def check(self, name: str, ok: bool, msg: str) -> None:
        self.checks[name] = ok
        if not ok:
            self.errors[name] = msg
        icon = "PASS" if ok else "FAIL"
        suffix = f" -- {msg}" if not ok else ""
        print(f"  {icon}: {name}{suffix}")

    def summary(self) -> None:
        passed = sum(1 for v in self.checks.values() if v)
        total = len(self.checks)
        failed = total - passed
        _print_header(f"ERGEBNIS: {passed}/{total} bestanden, {failed} fehlgeschlagen")
        if failed > 0:
            print("\n  Fehlgeschlagene Checks:")
            for name, msg in self.errors.items():
                print(f"    - {name}: {msg}")
        print()


def validate_exploration(project, result: ValidationResult) -> None:
    """Validate exploration artifact."""
    _print_header("EXPLORATION")
    art = project.exploration_artifact
    slots = art.slots

    result.check(
        "EXP_SLOTS_EXIST",
        len(slots) >= 8,
        f"Nur {len(slots)} Slots (erwartet >= 8)",
    )

    expected_slots = [
        "prozessausloeser",
        "prozessziel",
        "prozessbeschreibung",
        "scope",
        "beteiligte_systeme",
        "umgebung",
        "randbedingungen",
        "ausnahmen",
        "prozesszusammenfassung",
    ]
    for sid in expected_slots:
        slot = slots.get(sid)
        has_content = slot is not None and slot.inhalt.strip() != ""
        result.check(
            f"EXP_SLOT_{sid}",
            has_content,
            f"Slot '{sid}' leer oder fehlend",
        )

    # Keyword checks (soft — reported but not blocking)
    keyword_map = {
        "prozessausloeser": ["Rechnung"],
        "beteiligte_systeme": ["DATEV", "ELO"],
        "umgebung": ["Nürnberg", "200", "Buchhaltung"],
        "randbedingungen": ["Skonto"],
        "ausnahmen": ["Gutschrift"],
    }
    print("\n  Keyword-Stichproben (informativ):")
    for sid, keywords in keyword_map.items():
        slot = slots.get(sid)
        if not slot or not slot.inhalt:
            print(f"    {sid}: LEER")
            continue
        found = [kw for kw in keywords if kw.lower() in slot.inhalt.lower()]
        miss = [kw for kw in keywords if kw not in found]
        status = "OK" if len(miss) == 0 else f"MISS: {miss}"
        print(f"    {sid}: {status}")

    # Hallucination check
    neg_kws = ["SAP", "OCR", "Blockchain", "Machine Learning", "API", "PowerShell"]
    all_text = " ".join(s.inhalt for s in slots.values() if s.inhalt).lower()
    hallucinations = [kw for kw in neg_kws if kw.lower() in all_text]
    if hallucinations:
        print(f"\n  WARNUNG: Mögliche Halluzinationen: {hallucinations}")


def validate_structure(project, result: ValidationResult) -> None:
    """Validate structure artifact."""
    _print_header("STRUKTUR")
    art = project.structure_artifact
    schritte = art.schritte

    result.check(
        "STRUCT_MIN_SCHRITTE",
        len(schritte) >= 5,
        f"Nur {len(schritte)} Schritte (erwartet >= 5)",
    )

    # Type diversity
    actual_types = {s.typ.value for s in schritte.values()}
    result.check(
        "STRUCT_TYPE_aktion",
        "aktion" in actual_types,
        f"Typ 'aktion' fehlt. Vorhandene: {actual_types}",
    )
    result.check(
        "STRUCT_TYPE_entscheidung",
        "entscheidung" in actual_types,
        f"Typ 'entscheidung' fehlt. Vorhandene: {actual_types}",
    )

    # No empty steps
    leer = [sid for sid, s in schritte.items() if s.completeness_status.value == "leer"]
    result.check(
        "STRUCT_NO_LEER",
        len(leer) == 0,
        f"{len(leer)} Schritte mit Status 'leer': {leer}",
    )

    # All beschreibung filled
    empty_beschr = [
        sid for sid, s in schritte.items() if not s.beschreibung or not s.beschreibung.strip()
    ]
    result.check(
        "STRUCT_BESCHREIBUNG",
        len(empty_beschr) == 0,
        f"{len(empty_beschr)} Schritte ohne Beschreibung: {empty_beschr}",
    )

    # Nachfolger referential integrity
    all_ids = set(schritte.keys())
    dangling = []
    for sid, s in schritte.items():
        for nf in s.nachfolger:
            if nf not in all_ids:
                dangling.append(f"{sid} -> {nf}")
    result.check(
        "STRUCT_NACHFOLGER_VALID",
        len(dangling) == 0,
        f"Dangling Nachfolger: {dangling}",
    )

    # Ascending reihenfolge
    sorted_steps = sorted(schritte.values(), key=lambda s: s.reihenfolge)
    reihenfolgen = [s.reihenfolge for s in sorted_steps]
    ascending = all(reihenfolgen[i] <= reihenfolgen[i + 1] for i in range(len(reihenfolgen) - 1))
    result.check(
        "STRUCT_REIHENFOLGE",
        ascending,
        f"Reihenfolge nicht aufsteigend: {reihenfolgen}",
    )

    # Start/end steps
    all_nachfolger_ids: set[str] = set()
    for s in schritte.values():
        all_nachfolger_ids.update(s.nachfolger)
    start_steps = [sid for sid in schritte if sid not in all_nachfolger_ids]
    end_steps = [sid for sid, s in schritte.items() if len(s.nachfolger) == 0]
    result.check("STRUCT_HAS_START", len(start_steps) >= 1, "Kein Start-Schritt")
    result.check("STRUCT_HAS_END", len(end_steps) >= 1, "Kein End-Schritt")

    # Entscheidung constraints
    for sid, s in schritte.items():
        if s.typ.value == "entscheidung":
            result.check(
                f"ENTSCH_BED_{sid}",
                s.bedingung is not None and s.bedingung.strip() != "",
                f"Entscheidung '{sid}' ohne Bedingung",
            )
            result.check(
                f"ENTSCH_NACHF_{sid}",
                len(s.nachfolger) >= 2,
                f"Entscheidung '{sid}' hat nur {len(s.nachfolger)} Nachfolger",
            )

    # Spannungsfeld check
    has_spannungsfeld = any(s.spannungsfeld and s.spannungsfeld.strip() for s in schritte.values())
    print(f"\n  Spannungsfeld vorhanden: {'JA' if has_spannungsfeld else 'NEIN'}")

    # Print step summary
    print(f"\n  {'Schritt':25s} | {'Typ':12s} | {'Status':15s} | Nachfolger")
    print(f"  {'-' * 25}-+-{'-' * 12}-+-{'-' * 15}-+-{'-' * 30}")
    for sid, s in sorted(schritte.items(), key=lambda x: x[1].reihenfolge):
        nachf = ", ".join(s.nachfolger) if s.nachfolger else "(Ende)"
        print(f"  {sid:25s} | {s.typ.value:12s} | {s.completeness_status.value:15s} | {nachf}")


def validate_algorithm(project, result: ValidationResult) -> None:
    """Validate algorithm artifact."""
    _print_header("ALGORITHMUS")
    art = project.algorithm_artifact
    abschnitte = art.abschnitte

    if len(abschnitte) == 0:
        print("  Kein Algorithmusartefakt vorhanden (Phase 3 noch nicht durchlaufen?).")
        return

    result.check(
        "ALGO_MIN_ABSCHNITTE",
        len(abschnitte) >= 6,
        f"Nur {len(abschnitte)} Abschnitte (erwartet >= 6)",
    )

    # All abschnitte have aktionen
    empty = [aid for aid, a in abschnitte.items() if len(a.aktionen) == 0]
    result.check(
        "ALGO_ALL_HAVE_AKTIONEN",
        len(empty) == 0,
        f"{len(empty)} Abschnitte ohne EMMA-Aktionen: {empty}",
    )

    # Struktur-ref validity
    all_schritt_ids = set(project.structure_artifact.schritte.keys())
    invalid_refs = [
        f"{aid} -> {a.struktur_ref}"
        for aid, a in abschnitte.items()
        if a.struktur_ref not in all_schritt_ids
    ]
    result.check(
        "ALGO_STRUKTUR_REFS",
        len(invalid_refs) == 0,
        f"Ungültige struktur_ref: {invalid_refs}",
    )

    # EMMA type diversity
    all_emma_types: set[str] = set()
    for a in abschnitte.values():
        for ak in a.aktionen.values():
            all_emma_types.add(ak.aktionstyp)
    result.check(
        "EMMA_TYPE_DECISION",
        "DECISION" in all_emma_types,
        f"DECISION fehlt. Vorhandene: {sorted(all_emma_types)}",
    )
    result.check(
        "EMMA_TYPE_FILE_OPERATION",
        "FILE_OPERATION" in all_emma_types,
        f"FILE_OPERATION fehlt. Vorhandene: {sorted(all_emma_types)}",
    )

    # Hallucination check
    neg_kws = ["PowerShell", "SharePoint", "REST API", "SQL", "XML", "VBA", "Python", "JavaScript"]
    all_text = " ".join(
        f"{a.titel} "
        + " ".join(f"{ak.aktionstyp} {json.dumps(ak.parameter)}" for ak in a.aktionen.values())
        for a in abschnitte.values()
    ).lower()
    hallucinations = [kw for kw in neg_kws if kw.lower() in all_text]
    if hallucinations:
        print(f"\n  WARNUNG: Mögliche Halluzinationen: {hallucinations}")

    # Prozesszusammenfassung
    has_zusammenfassung = art.prozesszusammenfassung.strip() != ""
    print(f"\n  Prozesszusammenfassung: {'JA' if has_zusammenfassung else 'NEIN'}")
    print(f"  EMMA-Typen: {sorted(all_emma_types)}")

    # Print abschnitt summary
    print(f"\n  {'Abschnitt':25s} | {'Struktur-Ref':25s} | {'Aktionen':8s} | EMMA-Typen")
    print(f"  {'-' * 25}-+-{'-' * 25}-+-{'-' * 8}-+-{'-' * 30}")
    for aid, a in sorted(abschnitte.items()):
        types_str = ", ".join(sorted({ak.aktionstyp for ak in a.aktionen.values()}))
        print(f"  {aid:25s} | {a.struktur_ref:25s} | {len(a.aktionen):8d} | {types_str}")


def validate_cross_phase(project, result: ValidationResult) -> None:
    """Cross-phase integrity checks."""
    _print_header("PHASENÜBERGREIFEND")

    phase = project.aktive_phase.value
    status = project.projektstatus.value if hasattr(project, "projektstatus") else "?"
    print(f"  Aktive Phase: {phase}")
    print(f"  Projektstatus: {status}")
    print(f"  Aktiver Modus: {project.aktiver_modus}")

    # Exploration artifact survives through all phases
    exp_slots = len(project.exploration_artifact.slots)
    result.check(
        "CROSS_EXP_INTACT",
        exp_slots >= 8,
        f"Exploration nur {exp_slots} Slots nach Phase-Transitions",
    )


def main() -> None:
    """Main entry point."""
    from config import get_settings

    settings = get_settings()
    db = Database(settings.database_path)
    repo = ProjectRepository(db)

    projekt_id = sys.argv[1] if len(sys.argv) > 1 else None
    project = _load_project(repo, projekt_id)

    print(f"\nValidiere Projekt: {project.name} ({project.projekt_id})")
    print(f"Phase: {project.aktive_phase.value} | Modus: {project.aktiver_modus}")

    result = ValidationResult()

    validate_exploration(project, result)
    validate_structure(project, result)
    validate_algorithm(project, result)
    validate_cross_phase(project, result)

    result.summary()
    db.close()

    # Exit code: 0 if all pass, 1 if any fail
    sys.exit(0 if all(result.checks.values()) else 1)


if __name__ == "__main__":
    main()
