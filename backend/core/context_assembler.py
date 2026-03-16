"""ContextAssembler — stellt den Kontext für jeden Modusaufruf zusammen (SDD 6.5).

Baut ModeContext aus den aktuellen Projektdaten und der Dialoghistorie aus der DB.

SDD-Referenz: 6.5 (Context Engineering), 6.5.3 (Kontext-Bestandteile).
"""

from __future__ import annotations

from artifacts.models import CompletenessStatus, EmmaAktionstyp, Projektphase
from artifacts.template_schema import TEMPLATES, ArtifactTemplate
from config import Settings
from core.models import Project
from core.working_memory import WorkingMemory
from modes.base import ModeContext
from persistence.project_repository import ProjectRepository

# Phase → artifact type mapping for template lookup
_PHASE_TO_ARTIFACT_TYPE: dict[Projektphase, str] = {
    Projektphase.exploration: "exploration",
    Projektphase.strukturierung: "structure",
    Projektphase.spezifikation: "algorithm",
    Projektphase.validierung: "algorithm",
}


def build_context(
    project: Project,
    completeness_state: dict[str, CompletenessStatus],
    repository: ProjectRepository | None = None,
    settings: Settings | None = None,
) -> ModeContext:
    """ModeContext aus aktuellem Projektzustand aufbauen (SDD 6.5.3).

    Args:
        project: Das aktive Projekt.
        completeness_state: Aktueller Vollständigkeitsstatus aller Slots.
        repository: ProjectRepository für Dialoghistorie-Lookup. Wenn None,
            wird dialog_history als leere Liste übergeben.
        settings: Application settings. If provided, dialog_history_n is read
            from settings. Otherwise defaults to 20 for backward compatibility.
    """
    history_turns = settings.dialog_history_n if settings is not None else 20

    if repository is not None:
        dialog_history: list[dict[str, str]] = repository.load_dialog_history(
            project.projekt_id, last_n=history_turns
        )
    else:
        dialog_history = []

    # Determine artifact template based on active phase
    artifact_type = _PHASE_TO_ARTIFACT_TYPE.get(project.aktive_phase)
    artifact_template: ArtifactTemplate | None = (
        TEMPLATES.get(artifact_type) if artifact_type else None
    )

    return ModeContext(
        projekt_id=project.projekt_id,
        aktive_phase=project.aktive_phase,
        aktiver_modus=project.aktiver_modus,
        exploration_artifact=project.exploration_artifact,
        structure_artifact=project.structure_artifact,
        algorithm_artifact=project.algorithm_artifact,
        working_memory=project.working_memory,
        dialog_history=dialog_history,
        completeness_state=completeness_state,
        artifact_template=artifact_template,
    )


def prompt_context_summary(context: ModeContext) -> str:
    """Formatiert eine deutsche Zusammenfassung des Kontexts für den Systemprompt.

    Enthält: aktive Phase, aktiver Modus, Slot-Zähler, aktive Spannungsfelder.
    """
    wm: WorkingMemory = context.working_memory

    # Count filled/total slots from exploration artifact
    total_slots = len(context.exploration_artifact.slots)
    filled_slots = sum(
        1
        for s in context.exploration_artifact.slots.values()
        if s.completeness_status != CompletenessStatus.leer
    )

    # Structure artifact slot counts
    total_schritte = len(context.structure_artifact.schritte)
    filled_schritte = sum(
        1
        for s in context.structure_artifact.schritte.values()
        if s.completeness_status != CompletenessStatus.leer
    )

    # Spannungsfelder
    spannungsfelder = wm.spannungsfelder
    spannungsfelder_text = ", ".join(spannungsfelder) if spannungsfelder else "keine"

    # Prozesszusammenfassung status
    zusammenfassung = context.structure_artifact.prozesszusammenfassung
    zusammenfassung_status = "befüllt" if zusammenfassung.strip() else "leer"

    # Algorithm artifact slot counts
    total_abschnitte = len(context.algorithm_artifact.abschnitte)
    filled_abschnitte = sum(
        1
        for a in context.algorithm_artifact.abschnitte.values()
        if a.completeness_status != CompletenessStatus.leer
    )

    # Algorithm prozesszusammenfassung status
    algo_zusammenfassung = context.algorithm_artifact.prozesszusammenfassung
    algo_zusammenfassung_status = "befüllt" if algo_zusammenfassung.strip() else "leer"

    lines = [
        f"Aktive Phase: {wm.aktive_phase.value}",
        f"Aktiver Modus: {wm.aktiver_modus}",
        f"Explorations-Slots: {filled_slots}/{total_slots} befüllt",
        f"Prozesszusammenfassung (Struktur): {zusammenfassung_status}",
        f"Strukturschritte: {filled_schritte}/{total_schritte} befüllt",
        f"Algorithmusabschnitte: {filled_abschnitte}/{total_abschnitte} befüllt",
        f"Prozesszusammenfassung (Algorithmus): {algo_zusammenfassung_status}",
        f"Spannungsfelder: {spannungsfelder_text}",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# EMMA Action Catalog (SDD 8.3)
# ---------------------------------------------------------------------------

_EMMA_DESCRIPTIONS: dict[EmmaAktionstyp, str] = {
    EmmaAktionstyp.FIND: "UI-Element auf dem Bildschirm finden",
    EmmaAktionstyp.FIND_AND_CLICK: "UI-Element finden und anklicken",
    EmmaAktionstyp.CLICK: "Auf ein bekanntes Element klicken",
    EmmaAktionstyp.DRAG: "Element per Drag & Drop verschieben",
    EmmaAktionstyp.SCROLL: "In einem Bereich scrollen",
    EmmaAktionstyp.TYPE: "Text in ein Eingabefeld eingeben",
    EmmaAktionstyp.READ: "Wert aus einem UI-Element auslesen",
    EmmaAktionstyp.READ_FORM: "Mehrere Formularfelder auf einmal auslesen",
    EmmaAktionstyp.GENAI: "Generative KI für Textverarbeitung einsetzen",
    EmmaAktionstyp.EXPORT: "Daten aus einer Anwendung exportieren",
    EmmaAktionstyp.IMPORT: "Daten in eine Anwendung importieren",
    EmmaAktionstyp.FILE_OPERATION: "Dateioperationen durchführen (speichern, kopieren, verschieben, löschen, in Ordner ablegen)",
    EmmaAktionstyp.SEND_MAIL: "E-Mail versenden",
    EmmaAktionstyp.COMMAND: "Systembefehle oder Tastenkombinationen ausführen",
    EmmaAktionstyp.LOOP: "Schleife über eine Menge von Elementen",
    EmmaAktionstyp.DECISION: "Entscheidung basierend auf einer Bedingung",
    EmmaAktionstyp.WAIT: "Auf ein Ereignis oder eine Zeitspanne warten",
    EmmaAktionstyp.SUCCESS: "Erfolgreichen Abschluss einer Aktion markieren",
}


def emma_action_catalog_text() -> str:
    """Return German-language listing of all 18 EMMA action types (SDD 8.3).

    Raises KeyError if an EmmaAktionstyp member is not in the descriptions map.
    """
    lines: list[str] = []
    for member in EmmaAktionstyp:
        if member not in _EMMA_DESCRIPTIONS:
            msg = f"EmmaAktionstyp.{member.name} has no description in _EMMA_DESCRIPTIONS"
            raise KeyError(msg)
        lines.append(f"- {member.value}: {_EMMA_DESCRIPTIONS[member]}")
    return "\n".join(lines)
