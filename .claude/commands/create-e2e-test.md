# Create E2E Test

Generate end-to-end tests that validate the Digitalisierungsfabrik's
cognitive modes against real LLM calls.

The user specifies the SCOPE. You generate both the test dialog JSON
and the pytest test runner.

Usage: /create-e2e-test <scope> [process-domain]

Scope examples:
  explorer              — Explorer + Moderator only
  structurer            — Structurer + Moderator (seeds Explorer artifact)
  explorer+structurer   — Full chain: Explorer → Moderator → Structurer
  full                  — All 4 phases: Explorer → Structurer → Specifier → Validator
  specifier             — Specifier + Moderator (seeds Explorer + Structure artifacts)
  validator             — Validator + Moderator (seeds all three artifacts)

Process-domain (optional): The business process to use. Default: Eingangsrechnungsverarbeitung.
Examples: Reisekostenabrechnung, Onboarding, Bestellfreigabe

------------------------------------------------
CRITICAL RULES
------------------------------------------------

1. The simulated user is a FACHANWENDER (domain expert) WITHOUT
   programming skills and WITHOUT algorithmic thinking (SDD 1.2).
   - NO technical terminology: no "Entscheidungspunkt", "Verzweigung",
     "Kontrollfluss", "Pfad", "Schleife", "Ausnahme"
   - Use anecdotal, narrative language: stories about colleagues,
     frustrations, concrete examples from daily work
   - Occasional impatience, confusion, off-topic remarks
   - The user does NOT structure their knowledge — the SYSTEM must
     extract structure from unstructured input

2. Every test MUST include at least one ESCALATION (Panik-Button).
   The user gets frustrated or confused and triggers the moderator.
   This tests SDD 2.4 and the full escalation/return cycle.

3. Moderator INVARIANT (SDD 6.6.5): The moderator NEVER modifies
   artifacts. Every moderator turn MUST be checked for artifact
   immutability.

4. Tests must verify BOTH functional behaviour AND artifact quality.
   It is not enough that mode switches work — the artifacts must
   contain the right content.

5. Phase transitions require EXPLICIT user confirmation (SDD 6.1.2).
   The moderator must ask, the user must say yes.

6. The LLM is non-deterministic. Mode switches and flags are HARD
   checks (deterministic orchestrator logic). Artifact content is
   checked via KEYWORD MATCHING (soft checks).

7. PURPOSE TESTING — Not just "does it work?" but "does it HELP?"
   The Digitalisierungsfabrik's core promise (SDD 1.1) is:
   Transforming IMPLICIT process knowledge into EXPLICIT algorithms
   through Socratic dialogue. The system MUST:
   - EXTRACT knowledge from the user, not ASSUME or HALLUCINATE it
   - ASK questions, not just summarize
   - GUIDE the user, not overwhelm them
   - RESOLVE escalations, not just route them
   Tests must verify these qualities, not just mode transitions.

8. NEGATIVE PATHS — Every test MUST include at least one scenario
   where the user does NOT cooperate perfectly:
   - User CONTRADICTS a previous statement or system interpretation
   - User gives INCOMPLETE or CONFUSED information
   - User REFUSES or QUESTIONS a system suggestion
   The system must handle these gracefully, not break.

------------------------------------------------
MANDATORY CONTEXT — READ BEFORE GENERATING
------------------------------------------------

Read these files IN FULL before writing anything:

1. docs/digitalisierungsfabrik_systemdefinition.md — Sections:
   - 1.1-1.2 (Systemzweck, Zielnutzer) — offset=84, limit=70
   - 5.3-5.4 (Explorations- und Strukturartefakt) — offset=623, limit=95
   - 6.1 (Systemphasen, Phasenwechsel) — offset=940, limit=80
   - 6.6 (Kognitive Modi — alle 5) — offset=1171, limit=135
   - 6.7 (Fortschrittsmodell) — offset=1301, limit=40

2. Existing E2E tests as REFERENCE (read in full):
   - backend/tests/test_e2e_moderator.py
   - backend/tests/test_e2e_structurer.py

3. Existing dialog files as REFERENCE:
   - frontend/test-texte/explorer/dialog-e2e-moderator.json
   - frontend/test-texte/structurer/dialog-e2e-structurer.json

4. Mode implementations (read key sections):
   - backend/modes/exploration.py
   - backend/modes/structuring.py
   - backend/modes/specification.py (if in scope)
   - backend/modes/validation.py (if in scope)
   - backend/modes/moderator.py
   - backend/core/orchestrator.py — flag handling and mode switching
   - backend/artifacts/models.py — artifact models and enums

5. Backend infrastructure:
   - backend/core/phase_transition.py — PHASE_ORDER, PHASE_TO_MODE

------------------------------------------------
STEP 1 — DETERMINE SCOPE AND PHASES
------------------------------------------------

Parse the user's scope argument. Map to phases and modes:

| Scope keyword   | Phases involved                    | Modes tested                                |
|-----------------|------------------------------------|---------------------------------------------|
| explorer        | exploration                        | exploration, moderator                      |
| structurer      | strukturierung                     | structuring, moderator                      |
| specifier       | spezifikation                      | specification, moderator                    |
| validator       | validierung                        | validation, moderator                       |
| explorer+structurer | exploration → strukturierung   | exploration, structuring, moderator         |
| full            | all 4 phases                       | all 5 modes                                 |

For scopes that skip earlier phases, you MUST create seed artifacts
from the process domain. Study the existing seed in
dialog-e2e-structurer.json as a template.

For multi-phase scopes (explorer+structurer, full), the test runs
CONTINUOUSLY — no seeding between phases. The output of one phase
feeds directly into the next.

------------------------------------------------
STEP 2 — DESIGN THE USER JOURNEY
------------------------------------------------

Design 10-15 user inputs per phase. The journey MUST include:

PER PHASE (mandatory segments):

A) MODERATOR INTRO (2-3 turns)
   - System start or phase transition greeting
   - User asks a confused question (stays in moderator)
   - User confirms explicitly (mode switches to primary mode)

B) PRIMARY MODE WORK (4-6 turns)
   - User provides domain knowledge in NARRATIVE form
   - Each input should map to specific artifact slots/concepts
   - At least one input where user gives PARTIAL or CONFUSED info
   - At least one input where user gets IMPATIENT

C) NEGATIVE PATH: CONTRADICTION OR REFUSAL (1-2 turns)
   At least ONE of these must appear per phase:
   - User CONTRADICTS something they said earlier
     ("Ach nein Moment, das stimmt nicht. Es ist eigentlich anders...")
   - User REFUSES a system interpretation
     ("Nein das hab ich so nicht gemeint. So läuft das bei uns nicht.")
   - User gives INCOMPLETE info and expects system to ask follow-up
     ("Ja da gibt es noch was, aber fragen Sie mich mal genauer.")
   This tests whether the system handles corrections gracefully
   and doesn't just bulldoze forward.

D) ESCALATION CYCLE (3-4 turns)
   - After user frustration: simulate Panik-Button
   - User describes problem to moderator (moderator MUST analyze first)
   - User and moderator agree on solution
   - User confirms return to primary mode

E) POST-ESCALATION WORK (2-3 turns)
   - Primary mode continues with adjusted behaviour
   - User provides remaining information
   - Verify the escalation agreement is ACTUALLY reflected in
     changed behaviour (shorter responses, simpler language, etc.)

F) PHASE COMPLETION (2-3 turns)
   - User signals "I think we're done"
   - Mode triggers phase_complete (with nudge fallback)
   - If multi-phase: moderator proposes next phase, user confirms

USER INPUT DESIGN RULES:

- Write in first person, informal German
- Include filler words: "also", "naja", "halt", "ähm"
- Reference concrete people: "Frau Müller", "der Chef", "mein Kollege"
- Express emotions: frustration, impatience, satisfaction
- Mix relevant info with irrelevant anecdotes
- NEVER use these words in user inputs: Entscheidungspunkt,
  Verzweigung, Kontrollfluss, Schleife, Ausnahme, Algorithmus,
  Prozessschritt, Workflow (unless quoting system output)
- Instead say: "kommt drauf an", "manchmal muss man nochmal",
  "Sonderfall", "das ist anders", "da gibt es zwei Möglichkeiten"

------------------------------------------------
STEP 3 — DEFINE EXPECTED ARTIFACTS
------------------------------------------------

For each artifact type in scope, define:

A) EXPECTED CONCEPTS (keyword-based, soft matching)
   Each concept has:
   - concept name
   - expected type (for Strukturschritte)
   - 3-5 keywords that MUST appear in the artifact
   - structural properties (should_be_start, must_have_bedingung, etc.)

B) STRUCTURAL REQUIREMENTS (hard checks)
   - min_schritte / min_slots
   - must_have_types (for Strukturartefakt)
   - must_have_start_step, must_have_end_step
   - entscheidung_must_have_bedingung
   - must_have_prozesszusammenfassung

C) KEYWORD CHECKS PER SLOT (for Explorationsartefakt)
   - 3-5 domain-specific keywords per slot
   - Check: keyword.lower() in slot.inhalt.lower()

D) NEGATIVE KEYWORDS — Hallucination Detection (SDD 1.1)
   Define 5-10 keywords that the user NEVER mentioned but an LLM
   might plausibly hallucinate for the domain. If these appear in
   the artifact, the system fabricated information.

   Example for Eingangsrechnungsverarbeitung:
   - User never mentioned "SAP" → artifact must NOT contain "SAP"
   - User never mentioned "OCR" → artifact must NOT contain "OCR"
   - User never mentioned "Blockchain" → must NOT appear
   - User never mentioned "KI" or "Machine Learning" → must NOT appear
   - User never mentioned "Vier-Augen-Prinzip" → must NOT appear
     (unless user explicitly said it — check dialog!)

   The negative keywords must be PLAUSIBLE hallucinations, not
   absurd ones. "Blockchain" is too easy to exclude. "SAP" or
   "Vier-Augen-Prinzip" are things an LLM might reasonably assume
   for a German invoice process but that THIS specific user never said.

E) CONTRADICTION TRACKING
   For the negative path turn where the user contradicts themselves,
   define:
   - The WRONG information from the earlier user input
   - The CORRECTED information from the contradiction turn
   - Keywords from the CORRECTED version that must appear in artifact
   - Keywords from the WRONG version that must NOT appear in artifact

------------------------------------------------
STEP 4 — DEFINE CHECKPOINTS
------------------------------------------------

Every test needs checkpoints. Categories:

HARD CHECKPOINTS (assert, test fails if wrong):
- Mode switches: aktiver_modus == expected after each transition
- Phase transitions: aktive_phase == expected
- Escalation survival: artifacts intact after Panik-Button
- Moderator no-write: artifact unchanged during moderator turns
- Structural integrity: no dangling nachfolger refs,
  no leer schritte at phase_complete, all Pflichtfelder filled

SOFT CHECKPOINTS (report but don't fail):
- Keyword coverage per concept (>= 50% threshold)
- Response length after escalation agreement
- Completeness status distribution

MANDATORY CHECKPOINTS (must appear in every test):

A) MECHANICAL CHECKS — Does it work?

| ID Pattern           | What it checks                                    | SDD Ref |
|----------------------|---------------------------------------------------|---------|
| CP_mod_stays         | Moderator stays on user question (no premature handoff) | 6.1.0 |
| CP_explicit_confirm  | Mode only starts after explicit user confirmation  | 6.1.0 |
| CP_mode_switch       | Mode switches correctly after confirmation         | 6.3    |
| CP_artifact_survives | Artifact intact after escalation                   | 2.4    |
| CP_mod_no_write      | Moderator doesn't modify artifacts (per turn!)     | 6.6.5  |
| CP_mod_analyzes      | Moderator analyzes before returning (not bounce)   | 6.6.5  |
| CP_return_to_mode    | Correct return after escalation                    | 6.3    |
| CP_phase_complete    | phase_complete with valid artifact                 | 6.6.x  |
| CP_no_leer           | No slot/schritt with status 'leer' at completion   | 6.6.x  |
| CP_pflichtfelder     | All mandatory fields filled                        | 5.3/5.4|
| CP_nachfolger_valid  | All nachfolger-IDs reference existing IDs          | 5.4    |
| CP_phase_transition  | Correct phase after user confirms transition       | 6.1.2  |
| CP_data_intact       | Previous artifacts survive phase transition        | 6.1.2  |

B) PURPOSE CHECKS — Does it HELP? (soft, reported not asserted)

| ID Pattern           | What it checks                                    | SDD Ref |
|----------------------|---------------------------------------------------|---------|
| CP_no_hallucination  | Artifact content only contains concepts the user   | 1.1    |
|                      | actually mentioned. Check: define 3-5 NEGATIVE     |         |
|                      | keywords per domain that would indicate fabrication.|         |
|                      | Example: If user never mentioned "SAP", artifact   |         |
|                      | must NOT contain "SAP".                            |         |
| CP_asks_questions    | System responses (nutzeraeusserung) contain a       | FR-A-02|
|                      | question mark "?" in at least 70% of primary mode  |         |
|                      | turns. A mode that only summarizes but never asks   |         |
|                      | is failing its purpose.                            |         |
| CP_progress_monotone | phasenstatus progresses monotonically across turns: | 6.7    |
|                      | in_progress → nearing_completion → phase_complete.  |         |
|                      | A jump from in_progress to phase_complete without   |         |
|                      | nearing_completion is a weak signal.               |         |
| CP_escalation_effect | Post-escalation behaviour is measurably different   | 2.4    |
|                      | from pre-escalation. Check response length, or      |         |
|                      | count questions per turn, or check for simpler      |         |
|                      | vocabulary (no Fachbegriffe the user complained    |         |
|                      | about).                                            |         |
| CP_context_handoff   | After mode switch (moderator → primary mode), the   | FR-D-04|
|                      | dialog history contains information from the prior  |         |
|                      | mode. Verify via repo.load_dialog_history().       |         |
| CP_contradiction_handled | After user contradicts previous statement, the  | 1.1    |
|                      | artifact is UPDATED (not left with old info).      |         |
|                      | Verify the corrected info appears in the artifact. |         |

C) NEGATIVE PATH CHECKS — Does it handle trouble?

| ID Pattern           | What it checks                                    | SDD Ref |
|----------------------|---------------------------------------------------|---------|
| CP_handles_confusion | System does not crash or escalate when user gives  | 1.2    |
|                      | confused input. Mode remains correct, no error.    |         |
| CP_no_premature_complete | System does not trigger phase_complete when user | 6.6.x  |
|                      | has only provided partial information. Check that   |         |
|                      | phase_complete is NOT set too early (e.g. after    |         |
|                      | only 2-3 turns of a complex process).              |         |

------------------------------------------------
STEP 5 — WRITE THE DIALOG JSON
------------------------------------------------

Write the dialog file to:

  frontend/test-texte/<scope>/dialog-e2e-<scope>.json

Use this structure:

```json
{
  "_doc": "Description of what this test covers",

  "exploration_seed": { ... },     // Only if skipping explorer
  "structure_seed": { ... },       // Only if skipping structurer
  "algorithm_seed": { ... },       // Only if skipping specifier

  "user_inputs": [
    {
      "id": "U1",
      "phase": "moderator_begruessung",
      "description": "What the user is doing (for humans reading the test)",
      "message": "The actual user message in informal German",
      "expect_mode": "moderator",
      "expect_action": "weiter_moderieren",
      "contains_info_for_slots": ["slot_id_1", "slot_id_2"]
    }
  ],

  "system_events": [
    {
      "id": "S0",
      "when": "before_U1",
      "event": "system_start",
      "description": "...",
      "assertions": ["aktiver_modus == 'moderator'", ...]
    }
  ],

  "test_checkpoints": {
    "CP1_name": {
      "after": "U1",
      "check": "What to verify",
      "verifies": "Which SDD requirement this tests"
    }
  },

  "expected_artifact": { ... },              // For explorer scope
  "expected_structure_artifact": { ... },    // For structurer scope
  "expected_algorithm_artifact": { ... }     // For specifier scope
}
```

------------------------------------------------
STEP 6 — WRITE THE TEST RUNNER
------------------------------------------------

Write the pytest file to:

  backend/tests/test_e2e_<scope>.py

Follow the EXACT patterns from the existing tests:

```python
"""E2E-Test: <Description>

Testet: <what is tested>

Benötigt: LLM_API_KEY in .env (OpenAI oder Anthropic)
Laufzeit: ca. X Minuten (N+ LLM-Calls)

Aufruf:
    cd backend
    source .venv/Scripts/activate
    python -m pytest tests/test_e2e_<scope>.py -m e2e -s --timeout=600
"""

from __future__ import annotations
import json, os, sys
from pathlib import Path
import pytest

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))
os.chdir(backend_dir)

pytestmark = pytest.mark.e2e
```

REQUIRED TEST COMPONENTS:

1. log_turn() function — captures mode_before, mode_after, flags,
   phasenstatus, artifact counts per turn

2. check() function — soft checkpoint recording (does not assert)

3. get_mode() and get_project() helpers

4. Seed functions (if skipping phases) — load artifacts from dialog JSON

5. Nudge loop — max 3 attempts if LLM doesn't trigger phase_complete

6. Moderator no-write checks — before/after EVERY moderator turn,
   compare artifact state

7. Turn log printout — formatted table at the end

8. Checkpoint summary — PASS/FAIL for all checkpoints

9. Hard checkpoint assertions — only at the very end, after summary

ORCHESTRATOR SETUP:

```python
orchestrator = Orchestrator(
    repository=repo,
    modes={
        "exploration": ExplorationMode(llm_client=llm),
        "structuring": StructuringMode(llm_client=llm),
        "specification": SpecificationMode(llm_client=llm),  # if in scope
        "validation": ValidationMode(llm_client=llm),        # if in scope
        "moderator": Moderator(llm_client=llm),
    },
    settings=settings,
)
```

Only include modes that are in scope. The orchestrator only needs
modes that will actually be activated during the test.

PANIK-BUTTON SIMULATION:

```python
p_esc = repo.load(pid)
p_esc.working_memory.vorheriger_modus = p_esc.working_memory.aktiver_modus
p_esc.working_memory.aktiver_modus = "moderator"
p_esc.aktiver_modus = "moderator"
repo.save(p_esc)
```

MODERATOR NO-WRITE CHECK PATTERN:

```python
# Before moderator turn
artifact_snapshot = <capture current artifact state>

# ... moderator turn ...

# After moderator turn
check(
    "CP_mod_no_write_<turn>",
    <artifact state unchanged>,
    "Moderator modified artifact during <turn>",
)
```

For Explorations-Artefakt: snapshot = {sid: s.inhalt for sid, s in art.slots.items()}
For Struktur-Artefakt: snapshot = len(schritte) AND {sid: s.beschreibung for ...}

------------------------------------------------
STEP 7 — VERIFY COMPLETENESS
------------------------------------------------

Before presenting the result, verify:

1. Every user_input in the dialog JSON is consumed by the test
2. Every test_checkpoint in the dialog JSON has a corresponding
   check() call in the test
3. Every moderator turn has a no-write check
4. The hard_checkpoints list includes all mandatory CPs
5. The test handles the nudge case (LLM doesn't cooperate)
6. The test handles the force-advance case (LLM really won't cooperate)
7. All seed artifacts (if any) are complete and valid
8. The dialog JSON is valid JSON (parse it)
9. The test file has valid Python syntax (ast.parse it)

Run these verification steps:

```bash
python -c "import json; json.load(open('<dialog_path>', encoding='utf-8')); print('JSON OK')"
python -c "import ast; ast.parse(open('<test_path>', encoding='utf-8').read()); print('Python OK')"
```

------------------------------------------------
STEP 8 — SUMMARY
------------------------------------------------

Present a summary table:

| Aspect              | Value                          |
|---------------------|--------------------------------|
| Scope               | <scope>                        |
| Process Domain      | <domain>                       |
| Phases tested       | <list>                         |
| Modes tested        | <list>                         |
| User inputs         | <count>                        |
| Escalations         | <count>                        |
| Hard checkpoints    | <count>                        |
| Soft checkpoints    | <count>                        |
| Seed artifacts      | <yes/no, which>                |
| Dialog file         | <path>                         |
| Test file           | <path>                         |
| Est. LLM calls      | <count>                        |
| Est. runtime         | <minutes>                      |

------------------------------------------------
PROHIBITIONS
------------------------------------------------

Do NOT:
- Use technical jargon in user messages
- Skip the escalation cycle
- Skip the negative path (contradiction/refusal)
- Skip moderator no-write checks
- Make artifact checks purely structural (must check content keywords)
- Hardcode expected artifact text (use keyword matching)
- Create tests that only work for one specific LLM response
- Forget the nudge/force-advance fallback for phase_complete
- Use assert for soft checks (use check() function)
- Put hard assertions before the summary printout
- Create a "perfect user" who always cooperates flawlessly
- Skip the hallucination check (negative keywords)
- Skip the "asks questions" check (system must guide, not monologue)
- Assume escalation is tested by just checking the mode switch —
  verify the POST-ESCALATION behaviour actually changed
- Test only happy paths — every test needs at least one moment
  where the user pushes back, contradicts, or refuses
