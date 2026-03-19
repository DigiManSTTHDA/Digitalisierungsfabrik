/**
 * Unit tests for AssertionEvaluator, BehaviorEvaluator, and CampaignReporter.
 *
 * All tests use synthetic TurnRecord arrays — no backend dependency.
 */

import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import { AssertionEvaluator } from '../assertion-evaluator.js';
import { BehaviorEvaluator } from '../behavior-evaluator.js';
import { CampaignReporter } from '../campaign-reporter.js';
import type { ArtifactSnapshots, BehaviorScore, ScenarioResult, TurnRecord } from '../types.js';

// ---------------------------------------------------------------------------
// Test Helpers
// ---------------------------------------------------------------------------

function makeTurnRecord(overrides: Partial<TurnRecord> & { turn_nr: number }): TurnRecord {
  const defaultState = {
    aktiver_modus: 'exploration', aktive_phase: 'exploration', phasenstatus: 'aktiv',
    befuellte_slots: 0, bekannte_slots: 9, flags: [] as string[], working_memory: {} as Record<string, unknown>,
  };
  const defaultEval = {
    assertions_passed: [] as string[], assertions_failed: [] as string[], behavior_probes: [] as Array<{ name: string; passed: boolean; detail: string }>,
    metrics: { response_length: 50, slots_delta: 0, mode_changed: false, nudge_used: false },
  };
  const { state, evaluation, ...rest } = overrides;
  return {
    timestamp: '2026-01-01T00:00:00Z',
    scenario_id: 'S01',
    phase: 'exploration',
    step_id: `E1-${String(overrides.turn_nr).padStart(2, '0')}`,
    user_message: 'Test message',
    assistant_response: 'Deutsche Antwort mit vielen Wörtern und so weiter.',
    response_time_ms: 1000,
    ...rest,
    state: { ...defaultState, ...(state ?? {}) },
    evaluation: { ...defaultEval, ...(evaluation ?? {}) },
  };
}

function makeScenarioResult(overrides: Partial<ScenarioResult> & { scenario_id: string }): ScenarioResult {
  return {
    scenario_name: overrides.scenario_id,
    turns: [],
    final_artifacts: { exploration: {}, struktur: {}, algorithmus: {} },
    assertion_results: [],
    behavior_scores: [],
    duration_ms: 10000,
    summary: 'test',
    ...overrides,
  };
}

const emptyArtifacts: ArtifactSnapshots = { exploration: {}, struktur: {}, algorithmus: {} };

// ---------------------------------------------------------------------------
// AssertionEvaluator Tests
// ---------------------------------------------------------------------------

describe('AssertionEvaluator', () => {
  const evaluator = new AssertionEvaluator();

  it('test_mode_transition_valid: legal mode change after phase_complete → PASS', () => {
    const records: TurnRecord[] = [
      makeTurnRecord({ turn_nr: 1, state: { aktiver_modus: 'exploration', aktive_phase: 'exploration', phasenstatus: 'aktiv', befuellte_slots: 5, bekannte_slots: 9, flags: ['phase_complete'], working_memory: {} } }),
      makeTurnRecord({ turn_nr: 2, state: { aktiver_modus: 'moderator', aktive_phase: 'exploration', phasenstatus: 'aktiv', befuellte_slots: 5, bekannte_slots: 9, flags: [], working_memory: {} } }),
    ];
    const results = evaluator.checkModeTransitions(records);
    assert.equal(results.length, 1);
    assert.equal(results[0].status, 'PASS');
  });

  it('test_mode_transition_invalid: mode change without flag → FAIL', () => {
    const records: TurnRecord[] = [
      makeTurnRecord({ turn_nr: 1, state: { aktiver_modus: 'exploration', aktive_phase: 'exploration', phasenstatus: 'aktiv', befuellte_slots: 3, bekannte_slots: 9, flags: [], working_memory: {} } }),
      makeTurnRecord({ turn_nr: 2, state: { aktiver_modus: 'moderator', aktive_phase: 'exploration', phasenstatus: 'aktiv', befuellte_slots: 3, bekannte_slots: 9, flags: [], working_memory: {} } }),
    ];
    const results = evaluator.checkModeTransitions(records);
    assert.equal(results.some(r => r.status === 'FAIL'), true);
  });

  it('test_moderator_no_write_pass: moderator turns without artefakt_updated → PASS', () => {
    const records: TurnRecord[] = [
      makeTurnRecord({ turn_nr: 1, state: { aktiver_modus: 'moderator', aktive_phase: 'exploration', phasenstatus: 'aktiv', befuellte_slots: 0, bekannte_slots: 9, flags: [], working_memory: {} } }),
      makeTurnRecord({ turn_nr: 2, state: { aktiver_modus: 'moderator', aktive_phase: 'exploration', phasenstatus: 'aktiv', befuellte_slots: 0, bekannte_slots: 9, flags: [], working_memory: {} } }),
    ];
    const results = evaluator.checkModeratorNoWrite(records);
    assert.equal(results[0].status, 'PASS');
  });

  it('test_moderator_no_write_fail: moderator turn with artefakt_updated → FAIL', () => {
    const records: TurnRecord[] = [
      makeTurnRecord({ turn_nr: 1, state: { aktiver_modus: 'moderator', aktive_phase: 'exploration', phasenstatus: 'aktiv', befuellte_slots: 0, bekannte_slots: 9, flags: ['artefakt_updated'], working_memory: {} } }),
    ];
    const results = evaluator.checkModeratorNoWrite(records);
    assert.equal(results[0].status, 'FAIL');
  });

  it('test_language_german_pass: German responses → PASS', () => {
    const records: TurnRecord[] = [
      makeTurnRecord({ turn_nr: 1, assistant_response: 'Das ist eine deutsche Antwort mit vielen Wörtern und Inhalt der Sinn ergibt und so weiter und so fort in der deutschen Sprache.' }),
    ];
    const results = evaluator.checkLanguage(records);
    assert.equal(results[0].status, 'PASS');
  });

  it('test_language_english_warn: English sentence → WARN', () => {
    const records: TurnRecord[] = [
      makeTurnRecord({ turn_nr: 1, assistant_response: 'This is a very long English sentence that contains absolutely no German words at all and should be detected as non-German text by the heuristic.' }),
    ];
    const results = evaluator.checkLanguage(records);
    assert.equal(results[0].status !== 'PASS', true, `Expected WARN or FAIL, got ${results[0].status}`);
  });

  it('test_artifact_integrity_valid_refs: valid successor refs → PASS', () => {
    const artifacts: ArtifactSnapshots = {
      exploration: {},
      struktur: {
        schritte: [
          { id: 'step-1', typ: 'start', nachfolger_ids: ['step-2'] },
          { id: 'step-2', nachfolger_ids: ['step-3'] },
          { id: 'step-3', nachfolger_ids: [] },
        ],
      },
      algorithmus: {},
    };
    const results = evaluator.checkArtifactIntegrity(artifacts);
    const nachfolgerResult = results.find(r => r.name.includes('Nachfolger'));
    assert.equal(nachfolgerResult?.status, 'PASS');
  });

  it('test_artifact_integrity_invalid_refs: broken successor ref → FAIL', () => {
    const artifacts: ArtifactSnapshots = {
      exploration: {},
      struktur: {
        schritte: [
          { id: 'step-1', typ: 'start', nachfolger_ids: ['step-99'] },
        ],
      },
      algorithmus: {},
    };
    const results = evaluator.checkArtifactIntegrity(artifacts);
    const nachfolgerResult = results.find(r => r.name.includes('Nachfolger'));
    assert.equal(nachfolgerResult?.status, 'FAIL');
  });

  it('test_emma_compatibility_valid: valid EMMA types → PASS', () => {
    const artifacts: ArtifactSnapshots = {
      exploration: {},
      struktur: {},
      algorithmus: {
        abschnitte: [
          { emma_aktion: { typ: 'sequenz_aktion' } },
          { emma_aktion: { typ: 'entscheidung' } },
        ],
      },
    };
    const results = evaluator.checkEMMACompatibility(artifacts);
    assert.equal(results[0].status, 'PASS');
  });

  it('test_emma_compatibility_invalid: invalid EMMA type → FAIL', () => {
    const artifacts: ArtifactSnapshots = {
      exploration: {},
      struktur: {},
      algorithmus: {
        abschnitte: [
          { emma_aktion: { typ: 'unbekannt_aktion' } },
        ],
      },
    };
    const results = evaluator.checkEMMACompatibility(artifacts);
    assert.equal(results[0].status, 'FAIL');
  });
});

// ---------------------------------------------------------------------------
// BehaviorEvaluator Tests
// ---------------------------------------------------------------------------

describe('BehaviorEvaluator', () => {
  const evaluator = new BehaviorEvaluator();

  it('test_dialog_quality_sehr_gut: high slot efficiency, no repetition → SEHR_GUT', () => {
    const records: TurnRecord[] = [];
    for (let i = 1; i <= 10; i++) {
      records.push(makeTurnRecord({
        turn_nr: i,
        state: { aktiver_modus: 'exploration', aktive_phase: 'exploration', phasenstatus: 'aktiv',
          befuellte_slots: i, bekannte_slots: 10, flags: ['artefakt_updated'], working_memory: {} },
        assistant_response: `Unique response ${i} with different content each time`,
      }));
    }
    const result = evaluator.evaluateDialogQuality(records);
    assert.equal(result.rating, 'SEHR_GUT');
    assert.ok(result.metrics['slot_efficiency'] >= 0.7);
  });

  it('test_dialog_quality_mangelhaft: low slot efficiency → MANGELHAFT', () => {
    const records: TurnRecord[] = [];
    for (let i = 1; i <= 10; i++) {
      records.push(makeTurnRecord({
        turn_nr: i,
        state: { aktiver_modus: 'exploration', aktive_phase: 'exploration', phasenstatus: 'aktiv',
          befuellte_slots: 0, bekannte_slots: 10, flags: [], working_memory: {} },
      }));
    }
    const result = evaluator.evaluateDialogQuality(records);
    assert.equal(result.rating, 'MANGELHAFT');
    assert.equal(result.metrics['slot_efficiency'], 0);
  });

  it('test_ux_fluency_gut: moderate responses, some nudges → GUT', () => {
    const records: TurnRecord[] = [];
    for (let i = 1; i <= 10; i++) {
      records.push(makeTurnRecord({
        turn_nr: i,
        response_time_ms: 15000 + i * 1000, // 16-25 seconds — p95 < 30s but >= 20s
        evaluation: i <= 2
          ? { assertions_passed: [], assertions_failed: [], behavior_probes: [],
              metrics: { response_length: 50, slots_delta: 0, mode_changed: false, nudge_used: true } }
          : undefined,
      }));
    }
    const result = evaluator.evaluateUXFluency(records);
    assert.equal(result.rating, 'GUT');
    assert.ok(result.metrics['p95_response_ms'] < 30000);
    assert.ok(result.metrics['p95_response_ms'] >= 20000);
  });

  it('test_artifact_quality_mit_halluzination: forbidden concept in artifact → downgrade', () => {
    const records: TurnRecord[] = [
      makeTurnRecord({ turn_nr: 1, state: { aktiver_modus: 'exploration', aktive_phase: 'exploration', phasenstatus: 'aktiv', befuellte_slots: 8, bekannte_slots: 10, flags: [], working_memory: {} } }),
    ];
    const artifacts: ArtifactSnapshots = {
      exploration: { slots: { prozessziel: 'Rechnungsfreigabe' } },
      struktur: {},
      algorithmus: {},
    };
    const intent = {
      process_description: 'Rechnungsfreigabe',
      expected_structure_steps: 5,
      expected_complexity: 'einfach' as const,
      key_concepts: ['Rechnungsfreigabe'],
      forbidden_concepts: ['Blockchain'],
    };
    const result = evaluator.evaluateArtifactQuality(records, artifacts, intent);
    // No hallucination present, should be reasonable rating
    assert.equal(result.metrics['forbidden_concept_violations'], 0);

    // Now with hallucination
    const artifactsWithHallucination: ArtifactSnapshots = {
      exploration: { slots: { prozessziel: 'Rechnungsfreigabe mit Blockchain' } },
      struktur: {},
      algorithmus: {},
    };
    const result2 = evaluator.evaluateArtifactQuality(records, artifactsWithHallucination, intent);
    assert.equal(result2.metrics['forbidden_concept_violations'], 1);
    assert.ok(result2.findings.some(f => f.includes('Halluzination')));
  });

  it('test_moderator_behavior_sehr_gut: short sessions, resolved escalations → SEHR_GUT', () => {
    const records: TurnRecord[] = [
      makeTurnRecord({ turn_nr: 1, state: { aktiver_modus: 'exploration', aktive_phase: 'exploration', phasenstatus: 'aktiv', befuellte_slots: 5, bekannte_slots: 9, flags: [], working_memory: {} } }),
      makeTurnRecord({ turn_nr: 2, action: 'panic', state: { aktiver_modus: 'moderator', aktive_phase: 'exploration', phasenstatus: 'aktiv', befuellte_slots: 5, bekannte_slots: 9, flags: [], working_memory: {} } }),
      makeTurnRecord({ turn_nr: 3, state: { aktiver_modus: 'moderator', aktive_phase: 'exploration', phasenstatus: 'aktiv', befuellte_slots: 5, bekannte_slots: 9, flags: [], working_memory: {} } }),
      makeTurnRecord({ turn_nr: 4, state: { aktiver_modus: 'exploration', aktive_phase: 'exploration', phasenstatus: 'aktiv', befuellte_slots: 5, bekannte_slots: 9, flags: [], working_memory: {} } }),
    ];
    const result = evaluator.evaluateModeratorBehavior(records);
    assert.equal(result.rating, 'SEHR_GUT');
    assert.equal(result.metrics['escalation_resolved'], 1.0);
  });
});

// ---------------------------------------------------------------------------
// CampaignReporter Pattern Detection Tests
// ---------------------------------------------------------------------------

describe('CampaignReporter.analyzePatterns', () => {
  it('test_pattern_weak_dimension: ≥50% BEFRIEDIGEND → pattern detected', () => {
    const reporter = new CampaignReporter();
    const weakScore: BehaviorScore = { dimension: 'Dialogführung', rating: 'BEFRIEDIGEND', metrics: {}, findings: [] };

    reporter.addScenarioResult(makeScenarioResult({
      scenario_id: 'S01', behavior_scores: [weakScore],
    }));
    reporter.addScenarioResult(makeScenarioResult({
      scenario_id: 'S02', behavior_scores: [{ ...weakScore, rating: 'MANGELHAFT' }],
    }));
    reporter.addScenarioResult(makeScenarioResult({
      scenario_id: 'S03', behavior_scores: [{ ...weakScore, rating: 'GUT' }],
    }));

    const analysis = reporter.analyzePatterns();
    assert.ok(
      analysis.problem_patterns.some(p => p.includes('systemisch schwach')),
      `Expected 'systemisch schwach' pattern, got: ${analysis.problem_patterns.join(', ')}`
    );
  });

  it('test_pattern_recurring_assertion_fail: ≥3 same FAIL → pattern detected', () => {
    const reporter = new CampaignReporter();
    const failResult = { name: 'Moduswechsel nur bei Flags', status: 'FAIL' as const, detail: 'violation' };

    reporter.addScenarioResult(makeScenarioResult({ scenario_id: 'S01', assertion_results: [failResult] }));
    reporter.addScenarioResult(makeScenarioResult({ scenario_id: 'S02', assertion_results: [failResult] }));
    reporter.addScenarioResult(makeScenarioResult({ scenario_id: 'S03', assertion_results: [failResult] }));

    const analysis = reporter.analyzePatterns();
    assert.ok(
      analysis.problem_patterns.some(p => p.includes('schlägt in 3 Szenarien fehl')),
      `Expected recurring failure pattern, got: ${analysis.problem_patterns.join(', ')}`
    );
  });

  it('test_pattern_no_issues: all good → empty problem_patterns', () => {
    const reporter = new CampaignReporter();
    const goodScore: BehaviorScore = { dimension: 'Dialogführung', rating: 'SEHR_GUT', metrics: {}, findings: [] };
    const passResult = { name: 'Test', status: 'PASS' as const, detail: 'ok' };

    reporter.addScenarioResult(makeScenarioResult({
      scenario_id: 'S01', behavior_scores: [goodScore], assertion_results: [passResult],
    }));
    reporter.addScenarioResult(makeScenarioResult({
      scenario_id: 'S02', behavior_scores: [goodScore], assertion_results: [passResult],
    }));

    const analysis = reporter.analyzePatterns();
    assert.equal(analysis.problem_patterns.length, 0, `Expected no patterns, got: ${analysis.problem_patterns.join(', ')}`);
  });
});
