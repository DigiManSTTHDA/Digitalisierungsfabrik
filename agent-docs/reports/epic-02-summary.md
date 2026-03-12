# Management Summary — Epic 02: Execution Engine
**Date:** 2026-03-12
**Project:** Digitalisierungsfabrik Prototype
**Prepared for:** Technical stakeholders / project leadership

---

## Section 1 — Epic Summary

### What was implemented

Epic 02 built the **Executor** — the component that safely writes to process artifacts.

In the Digitalisierungsfabrik system, process knowledge is captured in three structured
artifacts (Exploration, Structure, Algorithm). These artifacts are critical documents that
grow throughout the user dialogue. Any corrupted or inconsistent write to an artifact
could cause silent errors that propagate invisibly through all subsequent AI interactions.

The Executor is the single gateway through which **all artifact changes must pass**. No
other part of the system — not the AI, not the modes, not the orchestrator — may bypass it.
Every change is validated, checked, and either fully applied or fully rejected. There are
no partial writes.

### Why this matters

Without this safeguard:
- An AI error could silently corrupt an artifact, contaminating all future AI turns
- A failed write could leave an artifact in a half-modified, inconsistent state
- There would be no way to enforce which parts of an artifact the AI is allowed to touch

With the Executor in place, the system has a hardened, trustworthy artifact management
layer. The correctness guarantee is: either a change is valid and is fully applied, or
the artifact is left exactly as it was.

---

## Section 2 — Implemented Components

### 2.1 ArtifactTemplate (`backend/artifacts/template_schema.py`)

**Purpose:** Defines exactly which parts of each artifact the AI is allowed to modify,
and which operations (add / replace / remove) are permitted on each part.

Think of it as an access control list for the AI's write operations. Before any change
is applied, the Executor checks it against this template. Any change targeting an
unlisted path is rejected outright — no exceptions.

The system maintains three separate templates:
- **Exploration Template** — controls writes to the free-text slot content
- **Structure Template** — controls writes to process steps (descriptions, types, ordering, etc.)
- **Algorithm Template** — controls writes to EMMA action sequences

**How it fits:** The Executor looks up the relevant template per artifact type before
applying any patch, giving the system a static, auditable allowlist of all permitted AI
write operations. This list can be inspected by developers and expanded in future epics
without touching the Executor logic.

---

### 2.2 Executor (`backend/core/executor.py`)

**Purpose:** Applies AI-proposed artifact changes atomically, with full rollback on any
failure.

Every change passes through a seven-step pipeline:

| Step | What it does |
|---|---|
| 1 — Syntax check | Verifies the change is a valid RFC 6902 JSON Patch operation |
| 2 — Allowlist check | Verifies the target path is in the artifact's template |
| 3 — Snapshot | Takes a complete copy of the artifact as a rollback point |
| 4 — Application | Applies the change using the `jsonpatch` library |
| 5 — Preservation check | Verifies that only the addressed parts of the artifact actually changed |
| 6 — Invalidation detection | Identifies which Algorithm sections become stale when a Structure step changes |
| 7 — Version bump | Increments the artifact version number on success |

If any step fails, the artifact is immediately restored from the snapshot taken in step 3.
No partial state is possible.

**How it fits:** The Executor sits between the AI output layer (not yet built) and the
artifact storage. When the Orchestrator (Epic 03) drives a turn, it will call
`Executor.apply_patches()` with the AI's proposed changes. The Executor either applies
them or reports the exact reason for rejection.

---

### 2.3 Invalidation Signal

**Purpose:** When a Structure step's description, type, or condition changes, the
corresponding Algorithm sections become outdated. The Executor detects this automatically
and returns the IDs of the affected Algorithm sections to the caller.

This implements SDD requirement FR-B-04: invalidation is performed exclusively by the
system, not by the AI.

**How it fits:** The Executor returns a list of stale Algorithm section IDs.
The Orchestrator (Epic 03, not yet built) will then use a second Executor call to mark
those sections as `invalidiert` in the Algorithm artifact.

---

## Section 3 — SDD Progress

### Fulfilled by Epic 02

| SDD Requirement | Status |
|---|---|
| **FR-B-09** — RFC 6902 Patch Executor with schema validation | ✓ Complete |
| **FR-B-09** — Atomic snapshot and rollback on any failure | ✓ Complete |
| **FR-B-09** — Preservation check (only addressed paths changed) | ✓ Complete |
| **FR-B-04** — Invalidation signal (system-driven, not AI-driven) | ✓ Complete |
| **FR-B-03** — Structural changes trigger Algorithm invalidation | ✓ Complete |
| **SDD 5.7** — Executor pipeline (7 steps as specified) | ✓ Complete |
| **SDD 5.5** — Invalidation rule (beschreibung, typ, bedingung, ausnahme_beschreibung) | ✓ Complete |

### Partially addressed

| SDD Requirement | Status |
|---|---|
| **FR-B-03** — `Strukturschritt.algorithmus_status` set to `invalidiert` | Executor returns the IDs; the Orchestrator (Epic 03) will apply the flag |
| **FR-B-05** — User warning before deleting a Structure step | Orchestrator responsibility (Epic 03) |

### Not yet implemented (future epics)

- Artifact Store with full version history and restore capability (Epic 03/04)
- Completeness calculation (Epic 03)
- REST/WebSocket API layer (Epic 05)
- React frontend (Epic 06)
- All cognitive modes (Exploration, Structuring, Specification, Validation) (Epics 04, 07–10)

---

## Section 4 — Test Status

**Total tests in the project: 98 — all passing**

Epic 02 added 39 new tests covering:

| Test category | Count | What it proves |
|---|---|---|
| Template validation | 9 | Allowlist correctly permits and rejects paths/operations |
| Happy path (patch applied) | 4 | Valid changes update artifacts and bump version |
| RFC-6902 syntax errors | 4 | Malformed AI output is rejected before touching the artifact |
| Template violations | 2 | Unlisted paths are blocked even if syntax is valid |
| Patch failure / rollback | 2 | Failed writes leave the artifact unchanged |
| Preservation check | 1 | Side-effect writes (AI touching fields it shouldn't) are caught |
| Invalidation triggered | 6 | Correct Algorithm sections are flagged as stale |
| No invalidation | 7 | Non-critical changes (title, order) do NOT trigger stale flags |
| Edge cases | 4 | Empty ref lists, new steps, failed-patch-returns-empty-IDs |

**Guarantee:** Any regression in the Executor's safety logic — rollback failure, missing
invalidation, incorrect template check — will be caught by the test suite before it can
reach production.

---

## Section 5 — Problems Encountered

### 1. Audit finding: SDD field name mismatch

During the post-implementation audit, a discrepancy was found between the SDD and the
Epic 01 implementation: SDD Section 5.3 defines the slot label field of
`ExplorationSlot` as **`titel`**, but Epic 01 had named it **`bezeichnung`**.

The template schema (Epic 02) correctly used the SDD name `titel` for the patch path
`/slots/{id}/titel`. This created a silent bug: patches targeting this path passed all
validation but the value was silently ignored by the model because the field didn't
exist under that name.

**Resolution:** The field was renamed from `bezeichnung` to `titel` across the model and
all affected tests. 98 tests remain green.

### 2. Preservation check granularity

The initial implementation of the Preservation Check compared top-level collection keys
(e.g. the entire `slots` dict), which was insufficient. If the AI's patch added an extra
slot it wasn't supposed to touch, the check passed because `slots` as a whole was
"addressed." The check was refined to compare at the entity level (individual slot IDs),
correctly catching any side-effect write to unaddressed entries.

---

## Section 6 — Remaining Issues

| Issue | Severity | Notes |
|---|---|---|
| `EmmaAktion.nachfolger` is `list[str]` but SDD says `String` | Low | SDD specifies a single next-action ID (`END` for terminal). Prototype uses a list for flexibility. Acceptable for prototype phase. |
| `Strukturschritt.algorithmus_status` invalidation write | By design | Executor returns IDs; Orchestrator (Epic 03) applies the flag write. Not a deficiency — it's the specified architecture. |
| No LLM yet | By design | Epic 02 covers the write safety layer. LLM integration is Epic 04. |

---

## Section 7 — System Integration

The Executor is the write-safety core of the entire Digitalisierungsfabrik system.
Here is how the full system will use it once all epics are complete:

```
User types a message in the browser
    ↓
WebSocket (Epic 05) delivers the message to the Orchestrator
    ↓
Orchestrator (Epic 03) selects the active cognitive mode
    ↓
Mode (Epics 04, 07–10) calls the AI (Claude) with the current artifact as read-only context
    ↓
AI returns a list of proposed changes (RFC 6902 JSON Patch format)
    ↓
Orchestrator passes the changes to → EXECUTOR (Epic 02, this epic)
    ↓
Executor validates, checks template, snapshots, applies, checks preservation
    ↓
  ├── Success: updated artifact returned, version bumped
  │       ↓ Orchestrator saves to SQLite (Epic 01)
  │       ↓ WebSocket sends artifact_update event to browser
  └── Failure: original artifact unchanged, error returned to Orchestrator
              ↓ WebSocket sends error event to browser
```

The Executor is now fully implemented and tested. All epics from 03 onwards will rely
on it without modification.

---

## Section 8 — Project Progress

### What is working now (Epics 00–02)

| Capability | Status |
|---|---|
| Project creation, saving, and loading (SQLite) | ✓ Working |
| All three artifact data models (Exploration, Structure, Algorithm) | ✓ Working |
| Artifact patch application with full rollback guarantee | ✓ Working |
| Automatic invalidation detection | ✓ Working |
| 98 automated tests, all passing | ✓ Working |

### What still needs to be built (Epics 03–11)

- **Epic 03** — Orchestrator and Working Memory: the control loop that drives each turn
- **Epic 04** — First actual AI interaction (Exploration Mode + LLM client)
- **Epic 05** — REST and WebSocket API (backend becomes a running server)
- **Epic 06** — React frontend (the browser interface)
- **Epics 07–10** — All cognitive modes (Moderator, Structuring, Specification, Validation)
- **Epic 11** — End-to-end stabilization and final export

### How close to a full run?

The system has a solid foundation (data layer + write safety layer) but is not yet
interactive. An end-to-end user session requires Epics 03–06 at minimum. That represents
roughly 4 of the 9 remaining epics to reach a first testable conversation in the browser.

---

## Section 9 — Project Status Overview

### Completed Epics

| Epic | Title | Key deliverable |
|---|---|---|
| 00 | Project Foundation & Dev Setup | Repository, tooling, health endpoint |
| 01 | Data Models & Persistence | All Pydantic models, SQLite schema, ProjectRepository |
| **02** | **Execution Engine** | **Executor with RFC 6902 + rollback + invalidation** |

### Current Epic

**Epic 02 — Execution Engine** — completed 2026-03-12.

### Remaining Epics

| Epic | Title |
|---|---|
| 03 | Orchestrator & Working Memory |
| 04 | Exploration Mode & LLM Integration |
| 05 | Backend API (REST + WebSocket) |
| 06 | React Frontend |
| 07 | Moderator & Phase Transitions |
| 08 | Structuring Mode |
| 09 | Specification Mode |
| 10 | Validation & Correction Loop |
| 11 | End-to-End Stabilization & Export |

---

## Section 10 — SDD Coverage

| SDD Area | Coverage |
|---|---|
| **Section 2 — UI / Browser interface** | Not yet (Epic 06) |
| **Section 4 — Functional requirements (FR groups A–G)** | Partially: FR-B-09, FR-B-04, FR-B-03 done; most FRs pending |
| **Section 5.1–5.2 — Artifact overview & versioning** | Data models complete; version history UI pending |
| **Section 5.3 — Exploration Artifact model** | ✓ Complete (incl. audit fix for `titel` field) |
| **Section 5.4 — Structure Artifact model** | ✓ Complete |
| **Section 5.5 — Algorithm Artifact model + EMMA actions** | ✓ Complete |
| **Section 5.5 — Invalidation rule** | ✓ Complete |
| **Section 5.6 — Completeness State** | Model fields present; calculation logic pending (Epic 03) |
| **Section 5.7 — RFC 6902 Executor pipeline** | ✓ Complete |
| **Section 6 — Orchestrator & cognitive modes** | Not yet (Epics 03–10) |
| **Section 7 — Persistence** | ✓ Complete (Epic 01) |
| **Section 8 — System configuration & LLM** | Not yet (Epic 04) |

**Estimated overall prototype progress: ~20%**
(Foundation + write-safety layer done; orchestration, AI, and UI remain)

---

## Section 11 — Major Risks

| Risk | Likelihood | Impact | Notes |
|---|---|---|---|
| LLM output quality (Epic 04) | Medium | High | The Executor now guarantees safety of writes, but the quality of AI-proposed patches depends on prompt engineering — not yet done |
| WebSocket streaming stability (Epic 05) | Low | Medium | Standard FastAPI pattern; low risk |
| Orchestrator complexity (Epic 03) | Medium | High | The 11-step cycle must coordinate multiple components correctly; the most complex single component in the system |
| EMMA action catalog not finalized (OP-02) | Low | Low | Prototype uses `str` for `aktionstyp`; no block to progress |
| Token limit management (FR-D-06) | Medium | Medium | Large artifacts may exceed LLM context windows; handling defined but not implemented |
| End-to-end integration surprises (Epic 11) | Medium | Medium | First real user sessions may reveal unexpected interaction patterns between modes |

---

## Section 12 — Next Steps

**Next Epic: Epic 03 — Orchestrator & Working Memory**

Epic 03 builds the central control loop of the system: the **Orchestrator**. This is
the component that receives user input, decides which cognitive mode is active, calls
that mode (currently as a stub returning no-op patches), passes the result to the
Executor, updates the session state (Working Memory), and persists everything to SQLite.

After Epic 03:
- A complete turn cycle will be testable end-to-end (without a browser or LLM)
- The system will demonstrate that data flows correctly through all layers
- Working Memory will track session state between turns

This sets up Epic 04 — the first real AI interaction — where the stub mode will be
replaced with an actual Claude API call and the Exploration phase dialogue will begin.
