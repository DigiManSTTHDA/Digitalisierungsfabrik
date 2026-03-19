/**
 * ScenarioRunner — Executes a scenario against the backend, collecting TurnRecords.
 *
 * Handles the full turn loop: sends messages, handles nudges when phase_complete
 * is missing, evaluates TurnExpectations and BehaviorProbes, and captures
 * artifact snapshots periodically.
 */

import type {
  ArtifactSnapshots, BehaviorProbe, BehaviorProbeResult, Scenario,
  ScenarioResult, Turn, TurnEvaluation, TurnExpectation, TurnMetrics,
  TurnRecord, TurnResponse,
} from './types.js';
import type { SessionClient } from './ws-client.js';

const PHASES = ['exploration', 'strukturierung', 'spezifikation', 'validierung'] as const;
type PhaseName = typeof PHASES[number];

export class ScenarioRunner {
  private readonly client: SessionClient;
  private readonly scenario: Scenario;

  constructor(client: SessionClient, scenario: Scenario) {
    this.client = client;
    this.scenario = scenario;
  }

  async run(): Promise<ScenarioResult> {
    const startTime = Date.now();
    const projectId = await this.client.createProject(this.scenario.name);
    const records: TurnRecord[] = [];
    let turnNr = 0;
    let prevSlots = 0;
    let lastArtifacts: ArtifactSnapshots = { exploration: {}, struktur: {}, algorithmus: {} };

    // Connect and consume greeting
    await this.client.connect(projectId);

    for (const phaseName of PHASES) {
      const turns = this.scenario.phases[phaseName as keyof typeof this.scenario.phases];
      if (!turns || turns.length === 0) continue;

      for (let i = 0; i < turns.length; i++) {
        const turn = turns[i];
        turnNr++;

        const record = await this.executeTurn(
          projectId, turn, turnNr, phaseName, prevSlots
        );
        records.push(record);
        prevSlots = record.state.befuellte_slots;

        // Artifact snapshots: every 5th turn and last turn of phase
        if (turnNr % 5 === 0 || i === turns.length - 1) {
          try {
            lastArtifacts = await this.client.getArtifacts(projectId);
            record.artifacts = lastArtifacts;
          } catch { /* non-fatal */ }
        }

        // Evaluate BehaviorProbes that trigger after this turn
        const probeResults = this.evaluateBehaviorProbes(turn.id, record);
        record.evaluation.behavior_probes.push(...probeResults);

        this.logProgress(turn, turnNr, turns.length, phaseName, record);
      }

      // Nudge handling: if phase_complete missing after last turn
      const lastRecord = records[records.length - 1];
      const lastTurn = turns[turns.length - 1];
      if (!lastRecord.state.flags.includes('phase_complete') && lastTurn.nudges) {
        for (const nudge of lastTurn.nudges) {
          turnNr++;
          const nudgeTurn: Pick<Turn, 'id' | 'message'> = { id: `${lastTurn.id}-nudge`, message: nudge };
          const nudgeRecord = await this.executeTurn(
            projectId, nudgeTurn, turnNr, phaseName, prevSlots
          );
          nudgeRecord.evaluation.metrics.nudge_used = true;
          records.push(nudgeRecord);
          prevSlots = nudgeRecord.state.befuellte_slots;
          this.logProgress(nudgeTurn, turnNr, turns.length, phaseName, nudgeRecord);

          if (nudgeRecord.state.flags.includes('phase_complete')) break;
        }
      }
    }

    this.client.disconnect();

    // Final artifact snapshot
    try {
      lastArtifacts = await this.client.getArtifacts(projectId);
    } catch { /* use last known */ }

    const duration = Date.now() - startTime;
    const phasesReached = [...new Set(records.map(r => r.phase))].join(' → ');
    const summary = `${records.length} turns | ${(duration / 1000).toFixed(0)}s | ${phasesReached}`;

    return {
      scenario_id: this.scenario.id,
      scenario_name: this.scenario.name,
      turns: records,
      final_artifacts: lastArtifacts,
      assertion_results: [],
      behavior_scores: [],
      duration_ms: duration,
      summary,
    };
  }

  private async executeTurn(
    projectId: string, turn: Pick<Turn, 'id' | 'message' | 'action' | 'expect'>,
    turnNr: number, phase: string, prevSlots: number,
  ): Promise<TurnRecord> {
    let response: TurnResponse;

    if (turn.action === 'panic') {
      // Send the message first, then press panic
      response = await this.client.sendMessage(projectId, turn.message);
      const panicResponse = await this.client.pressButton(projectId, 'panic');
      // Use panic response as the final state
      response = {
        message: panicResponse.message,
        state: panicResponse.state,
        artifacts_updated: response.artifacts_updated || panicResponse.artifacts_updated,
        response_time_ms: response.response_time_ms + panicResponse.response_time_ms,
      };
    } else {
      response = await this.client.sendMessage(projectId, turn.message);
    }

    const expectResults = turn.expect
      ? this.evaluateExpectation(turn.expect, response, prevSlots)
      : { passed: [] as string[], failed: [] as string[] };

    const metrics: TurnMetrics = {
      response_length: response.message.length,
      slots_delta: response.state.befuellte_slots - prevSlots,
      mode_changed: false, // updated below if we had a previous record
      nudge_used: false,
    };

    const evaluation: TurnEvaluation = {
      assertions_passed: expectResults.passed,
      assertions_failed: expectResults.failed,
      behavior_probes: [],
      metrics,
    };

    return {
      turn_nr: turnNr,
      timestamp: new Date().toISOString(),
      scenario_id: this.scenario.id,
      phase,
      step_id: turn.id,
      user_message: turn.message,
      action: turn.action,
      assistant_response: response.message,
      response_time_ms: response.response_time_ms,
      state: response.state,
      evaluation,
    };
  }

  private evaluateExpectation(
    expect: TurnExpectation, response: TurnResponse, prevSlots: number,
  ): { passed: string[]; failed: string[] } {
    const passed: string[] = [];
    const failed: string[] = [];

    if (expect.mode_should_be !== undefined) {
      const ok = response.state.aktiver_modus === expect.mode_should_be;
      (ok ? passed : failed).push(`mode=${expect.mode_should_be}`);
    }

    if (expect.flag_should_include) {
      for (const flag of expect.flag_should_include) {
        const ok = response.state.flags.includes(flag);
        (ok ? passed : failed).push(`flag_include=${flag}`);
      }
    }

    if (expect.flag_should_not_include) {
      for (const flag of expect.flag_should_not_include) {
        const ok = !response.state.flags.includes(flag);
        (ok ? passed : failed).push(`flag_exclude=${flag}`);
      }
    }

    if (expect.slots_should_increase) {
      const ok = response.state.befuellte_slots > prevSlots;
      (ok ? passed : failed).push('slots_increased');
    }

    if (expect.response_should_contain) {
      const lower = response.message.toLowerCase();
      for (const kw of expect.response_should_contain) {
        const ok = lower.includes(kw.toLowerCase());
        (ok ? passed : failed).push(`contains=${kw}`);
      }
    }

    if (expect.response_should_not_contain) {
      const lower = response.message.toLowerCase();
      for (const kw of expect.response_should_not_contain) {
        const ok = !lower.includes(kw.toLowerCase());
        (ok ? passed : failed).push(`not_contains=${kw}`);
      }
    }

    return { passed, failed };
  }

  private evaluateBehaviorProbes(turnId: string, record: TurnRecord): BehaviorProbeResult[] {
    const results: BehaviorProbeResult[] = [];

    for (const probe of this.scenario.behavior_probes) {
      if (probe.after_turn !== turnId) continue;
      results.push(this.evaluateProbe(probe, record));
    }

    return results;
  }

  private evaluateProbe(probe: BehaviorProbe, record: TurnRecord): BehaviorProbeResult {
    const { check } = probe;

    if (probe.type === 'state_check') {
      const checks: string[] = [];
      let passed = true;
      if (check.expected_phase && record.state.aktive_phase !== check.expected_phase) {
        checks.push(`phase: expected ${check.expected_phase}, got ${record.state.aktive_phase}`);
        passed = false;
      }
      if (check.expected_mode && record.state.aktiver_modus !== check.expected_mode) {
        checks.push(`mode: expected ${check.expected_mode}, got ${record.state.aktiver_modus}`);
        passed = false;
      }
      if (check.min_filled_slots !== undefined && record.state.befuellte_slots < check.min_filled_slots) {
        checks.push(`slots: ${record.state.befuellte_slots} < ${check.min_filled_slots}`);
        passed = false;
      }
      return { name: probe.name, passed, detail: checks.join('; ') || 'OK' };
    }

    if (probe.type === 'dialog_check' && check.response_pattern) {
      const regex = new RegExp(check.response_pattern, 'i');
      const passed = regex.test(record.assistant_response);
      return { name: probe.name, passed, detail: passed ? 'Pattern matched' : 'Pattern not found' };
    }

    if (probe.type === 'artifact_check') {
      const lower = record.assistant_response.toLowerCase();
      let passed = true;
      const details: string[] = [];
      if (check.should_contain) {
        for (const kw of check.should_contain) {
          if (!lower.includes(kw.toLowerCase())) {
            passed = false;
            details.push(`missing: ${kw}`);
          }
        }
      }
      if (check.should_not_contain) {
        for (const kw of check.should_not_contain) {
          if (lower.includes(kw.toLowerCase())) {
            passed = false;
            details.push(`found forbidden: ${kw}`);
          }
        }
      }
      return { name: probe.name, passed, detail: details.join('; ') || 'OK' };
    }

    return { name: probe.name, passed: true, detail: 'No check implemented for type' };
  }

  private logProgress(
    turn: Pick<Turn, 'id'>, turnNr: number, totalInPhase: number,
    phase: string, record: TurnRecord,
  ): void {
    const slots = `${record.state.befuellte_slots}/${record.state.bekannte_slots} slots`;
    const mode = record.state.aktiver_modus;
    process.stderr.write(
      `[${this.scenario.id}] Turn ${turnNr} (${turn.id}) | ${phase} | ${mode} | ${slots}\n`
    );
  }
}
