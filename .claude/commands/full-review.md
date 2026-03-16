# Full Review — Codebase-Analyse mit Kalibrierung

Commands referenced with "/" must be executed exactly.
Do not reinterpret them.

Führe eine vollständige Codebase-Review mit anschließender
skeptischer Kalibrierung durch.

Dieser Command orchestriert zwei Phasen:

1. Multi-Agent Qualitätsanalyse (detect_slob)
2. Skeptischer Evidenz-Check (review_skeptic)

Optionaler Scope: `$ARGUMENTS`

(Wird an /detect_slob weitergereicht.)

------------------------------------------------
CRITICAL: CONTINUATION RULE
------------------------------------------------

Dieser Workflow hat 2 Phasen.
Du MUSST beide Phasen nacheinander ausführen.

Stoppe NICHT nach Phase 1. Der Review ist erst nach
Phase 2 abgeschlossen.

------------------------------------------------
PHASE 1 — Codebase-Analyse
------------------------------------------------

Run:

/detect_slob $ARGUMENTS

Nach Abschluss prüfe, dass die Datei existiert:

agent-docs/reports/codebase-review-latest.md

→ Do NOT stop here. Continue with PHASE 2.

------------------------------------------------
PHASE 2 — Skeptische Kalibrierung
------------------------------------------------

Run:

/review_skeptic

Nach Abschluss prüfe, dass die Datei existiert:

agent-docs/reports/codebase-review-calibrated.md

------------------------------------------------
ABSCHLUSS
------------------------------------------------

Gib dem User eine kurze Zusammenfassung:

- Verweis auf beide Reports mit Dateipfaden
- Die kalibrierten Gesamtnoten aus Phase 2
- Die 3 wichtigsten bestätigten Findings (Kategorie A)
- Anzahl verworfener/abgeschwächter Findings

Der Review ist erst abgeschlossen, wenn beide Reports
geschrieben wurden.
