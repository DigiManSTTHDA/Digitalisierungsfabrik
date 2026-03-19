/**
 * BehaviorEvaluator — 4 soft behavioral dimensions.
 *
 * Evaluates dialog quality, moderator behavior, artifact quality,
 * and UX fluency on a four-tier scale (SEHR_GUT / GUT / BEFRIEDIGEND / MANGELHAFT).
 */

import type {
  ArtifactSnapshots, BehaviorScore, ScenarioIntent, TurnRecord,
} from './types.js';

export class BehaviorEvaluator {
  /** Dimension A: Dialog quality — slot efficiency, repetition, nudge count. */
  evaluateDialogQuality(records: TurnRecord[]): BehaviorScore {
    const totalTurns = records.length;
    if (totalTurns === 0) {
      return { dimension: 'Dialogführung', rating: 'MANGELHAFT', metrics: {}, findings: ['Keine Turns'] };
    }

    const turnsWithUpdate = records.filter(r => r.state.flags.includes('artefakt_updated')).length;
    const slotEfficiency = turnsWithUpdate / totalTurns;

    let repetitionCount = 0;
    for (let i = 1; i < records.length; i++) {
      const prev = records[i - 1].assistant_response.slice(0, 50);
      const curr = records[i].assistant_response.slice(0, 50);
      if (prev === curr && prev.length > 0) repetitionCount++;
    }

    const nudgeCount = records.filter(r => r.evaluation.metrics.nudge_used).length;

    const metrics = { slot_efficiency: slotEfficiency, repetition_count: repetitionCount, nudge_count: nudgeCount };
    const findings: string[] = [];
    if (repetitionCount > 0) findings.push(`${repetitionCount} Wiederholungsfragen`);
    if (nudgeCount > 0) findings.push(`${nudgeCount} Nudges benötigt`);

    let rating: BehaviorScore['rating'];
    if (slotEfficiency >= 0.7 && repetitionCount === 0 && nudgeCount <= 1) {
      rating = 'SEHR_GUT';
    } else if (slotEfficiency >= 0.5 && repetitionCount <= 1) {
      rating = 'GUT';
    } else if (slotEfficiency >= 0.3) {
      rating = 'BEFRIEDIGEND';
    } else {
      rating = 'MANGELHAFT';
    }

    return { dimension: 'Dialogführung', rating, metrics, findings };
  }

  /** Dimension B: Moderator behavior — avg turns per transition, escalation resolution. */
  evaluateModeratorBehavior(records: TurnRecord[]): BehaviorScore {
    const moderatorSessions: number[] = [];
    let currentCount = 0;
    let inModerator = false;

    for (const record of records) {
      if (record.state.aktiver_modus === 'moderator') {
        inModerator = true;
        currentCount++;
      } else if (inModerator) {
        moderatorSessions.push(currentCount);
        currentCount = 0;
        inModerator = false;
      }
    }
    if (inModerator && currentCount > 0) moderatorSessions.push(currentCount);

    const avgModeratorTurns = moderatorSessions.length > 0
      ? moderatorSessions.reduce((a, b) => a + b, 0) / moderatorSessions.length
      : 0;

    let escalations = 0;
    let resolved = 0;
    for (let i = 0; i < records.length; i++) {
      if (records[i].action === 'panic') {
        escalations++;
        for (let j = i + 1; j < records.length; j++) {
          if (records[j].state.aktiver_modus !== 'moderator') {
            resolved++;
            break;
          }
        }
      }
    }
    const escalationResolved = escalations > 0 ? resolved / escalations : 1.0;

    const metrics = { avg_moderator_turns: avgModeratorTurns, escalation_resolved: escalationResolved };
    const findings: string[] = [];
    if (avgModeratorTurns > 3) findings.push(`Durchschnittlich ${avgModeratorTurns.toFixed(1)} Moderator-Turns`);

    let rating: BehaviorScore['rating'];
    if (avgModeratorTurns <= 2 && escalationResolved === 1.0) {
      rating = 'SEHR_GUT';
    } else if (avgModeratorTurns <= 3) {
      rating = 'GUT';
    } else if (avgModeratorTurns <= 5) {
      rating = 'BEFRIEDIGEND';
    } else {
      rating = 'MANGELHAFT';
    }
    if (escalationResolved < 0.5) rating = 'MANGELHAFT';

    return { dimension: 'Moderatorverhalten', rating, metrics, findings };
  }

  /** Dimension C: Artifact quality — completeness, key concepts, hallucination. */
  evaluateArtifactQuality(
    records: TurnRecord[], artifacts: ArtifactSnapshots, intent: ScenarioIntent,
  ): BehaviorScore {
    const lastRecord = records[records.length - 1];
    const totalSlots = lastRecord?.state.bekannte_slots ?? 0;
    const filledSlots = lastRecord?.state.befuellte_slots ?? 0;
    const slotCompleteness = totalSlots > 0 ? filledSlots / totalSlots : 0;

    const artifactText = JSON.stringify(artifacts).toLowerCase();
    const foundConcepts = intent.key_concepts.filter(c => artifactText.includes(c.toLowerCase()));
    const keyConceptCoverage = intent.key_concepts.length > 0
      ? foundConcepts.length / intent.key_concepts.length
      : 1.0;

    const forbiddenViolations = intent.forbidden_concepts.filter(c => artifactText.includes(c.toLowerCase()));

    const metrics = {
      slot_completeness: slotCompleteness,
      key_concept_coverage: keyConceptCoverage,
      forbidden_concept_violations: forbiddenViolations.length,
    };
    const findings: string[] = [];
    if (foundConcepts.length < intent.key_concepts.length) {
      const missing = intent.key_concepts.filter(c => !foundConcepts.includes(c));
      findings.push(`Fehlende Konzepte: ${missing.join(', ')}`);
    }
    if (forbiddenViolations.length > 0) {
      findings.push(`Halluzination: ${forbiddenViolations.join(', ')}`);
    }

    let rating: BehaviorScore['rating'];
    if (slotCompleteness >= 0.9 && keyConceptCoverage >= 0.8 && forbiddenViolations.length === 0) {
      rating = 'SEHR_GUT';
    } else if (slotCompleteness >= 0.7 && keyConceptCoverage >= 0.6) {
      rating = 'GUT';
    } else if (slotCompleteness >= 0.5) {
      rating = 'BEFRIEDIGEND';
    } else {
      rating = 'MANGELHAFT';
    }

    return { dimension: 'Artefaktqualität', rating, metrics, findings };
  }

  /** Dimension D: UX fluency — response times, ping-pong, nudges. */
  evaluateUXFluency(records: TurnRecord[]): BehaviorScore {
    const times = records.map(r => r.response_time_ms).sort((a, b) => a - b);
    const medianResponseMs = times.length > 0 ? times[Math.floor(times.length / 2)] : 0;
    const p95ResponseMs = times.length > 0 ? times[Math.floor(times.length * 0.95)] : 0;

    let modePingpongCount = 0;
    for (let i = 2; i < records.length; i++) {
      const a = records[i - 2];
      const mod = records[i - 1];
      const b = records[i];
      if (a.state.aktiver_modus !== 'moderator' &&
          mod.state.aktiver_modus === 'moderator' &&
          b.state.aktiver_modus === a.state.aktiver_modus &&
          b.state.befuellte_slots === a.state.befuellte_slots) {
        modePingpongCount++;
      }
    }

    const nudgeTotal = records.filter(r => r.evaluation.metrics.nudge_used).length;

    const metrics = {
      median_response_ms: medianResponseMs,
      p95_response_ms: p95ResponseMs,
      mode_pingpong_count: modePingpongCount,
      nudge_total: nudgeTotal,
    };
    const findings: string[] = [];
    if (p95ResponseMs > 30000) findings.push(`P95 Antwortzeit: ${(p95ResponseMs / 1000).toFixed(1)}s`);
    if (modePingpongCount > 0) findings.push(`${modePingpongCount}x Modus-Ping-Pong`);
    if (nudgeTotal > 2) findings.push(`${nudgeTotal} Nudges`);

    let rating: BehaviorScore['rating'];
    if (p95ResponseMs < 20000 && modePingpongCount === 0 && nudgeTotal <= 1) {
      rating = 'SEHR_GUT';
    } else if (p95ResponseMs < 30000 && nudgeTotal <= 2) {
      rating = 'GUT';
    } else if (p95ResponseMs < 45000) {
      rating = 'BEFRIEDIGEND';
    } else {
      rating = 'MANGELHAFT';
    }

    return { dimension: 'UX-Flüssigkeit', rating, metrics, findings };
  }

  /** Run all 4 behavior evaluations. */
  evaluateAll(
    records: TurnRecord[], artifacts: ArtifactSnapshots, intent: ScenarioIntent,
  ): BehaviorScore[] {
    return [
      this.evaluateDialogQuality(records),
      this.evaluateModeratorBehavior(records),
      this.evaluateArtifactQuality(records, artifacts, intent),
      this.evaluateUXFluency(records),
    ];
  }
}
