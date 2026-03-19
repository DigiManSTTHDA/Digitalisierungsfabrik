/**
 * E2E Test Campaign — Type Definitions
 *
 * All interfaces for the E2E framework: scenarios, turns, records,
 * evaluations, and results. Based on e2e-testkampagne-plan.md.
 */

// ---------------------------------------------------------------------------
// Scenario Definition
// ---------------------------------------------------------------------------

export interface Scenario {
  id: string;
  name: string;
  description: string;
  tags: string[];
  intent: ScenarioIntent;
  phases: ScenarioPhases;
  behavior_probes: BehaviorProbe[];
}

export interface ScenarioIntent {
  process_description: string;
  expected_structure_steps: number;
  expected_complexity: 'minimal' | 'einfach' | 'mittel' | 'komplex';
  key_concepts: string[];
  forbidden_concepts: string[];
}

export interface ScenarioPhases {
  exploration: Turn[];
  strukturierung: Turn[];
  spezifikation: Turn[];
  validierung?: Turn[];
}

export interface Turn {
  id: string;
  message: string;
  action?: 'panic';
  nudges?: string[];
  note?: string;
  expect?: TurnExpectation;
}

export interface TurnExpectation {
  mode_should_be?: string;
  flag_should_include?: string[];
  flag_should_not_include?: string[];
  slots_should_increase?: boolean;
  response_should_contain?: string[];
  response_should_not_contain?: string[];
}

// ---------------------------------------------------------------------------
// Behavior Probes
// ---------------------------------------------------------------------------

export interface BehaviorProbe {
  after_turn: string;
  name: string;
  type: 'artifact_check' | 'dialog_check' | 'state_check';
  check: BehaviorProbeCheck;
}

export interface BehaviorProbeCheck {
  slot_path?: string;
  should_contain?: string[];
  should_not_contain?: string[];
  response_pattern?: string;
  expected_phase?: string;
  expected_mode?: string;
  min_filled_slots?: number;
}

// ---------------------------------------------------------------------------
// Turn Recording
// ---------------------------------------------------------------------------

export interface TurnRecord {
  turn_nr: number;
  timestamp: string;
  scenario_id: string;
  phase: string;
  step_id: string;
  user_message: string;
  action?: string;
  assistant_response: string;
  response_time_ms: number;
  state: TurnState;
  artifacts?: ArtifactSnapshots;
  evaluation: TurnEvaluation;
}

export interface TurnState {
  aktiver_modus: string;
  aktive_phase: string;
  phasenstatus: string;
  befuellte_slots: number;
  bekannte_slots: number;
  flags: string[];
  working_memory: Record<string, unknown>;
}

export interface ArtifactSnapshots {
  exploration: Record<string, unknown>;
  struktur: Record<string, unknown>;
  algorithmus: Record<string, unknown>;
}

// ---------------------------------------------------------------------------
// Evaluation
// ---------------------------------------------------------------------------

export interface TurnEvaluation {
  assertions_passed: string[];
  assertions_failed: string[];
  behavior_probes: BehaviorProbeResult[];
  metrics: TurnMetrics;
}

export interface BehaviorProbeResult {
  name: string;
  passed: boolean;
  detail: string;
}

export interface TurnMetrics {
  response_length: number;
  slots_delta: number;
  mode_changed: boolean;
  nudge_used: boolean;
}

// ---------------------------------------------------------------------------
// Results
// ---------------------------------------------------------------------------

export interface ScenarioResult {
  scenario_id: string;
  scenario_name: string;
  turns: TurnRecord[];
  final_artifacts: ArtifactSnapshots;
  assertion_results: AssertionResult[];
  behavior_scores: BehaviorScore[];
  duration_ms: number;
  summary: string;
}

export interface AssertionResult {
  name: string;
  status: 'PASS' | 'FAIL' | 'WARN';
  detail: string;
}

export interface BehaviorScore {
  dimension: string;
  rating: 'SEHR_GUT' | 'GUT' | 'BEFRIEDIGEND' | 'MANGELHAFT';
  metrics: Record<string, number>;
  findings: string[];
}

// ---------------------------------------------------------------------------
// WebSocket Communication
// ---------------------------------------------------------------------------

export interface TurnResponse {
  message: string;
  state: TurnState;
  artifacts_updated: boolean;
  response_time_ms: number;
}
