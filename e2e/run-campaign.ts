/**
 * E2E Test Campaign — CLI Entry Point
 *
 * Usage:
 *   npx tsx e2e/run-campaign.ts                    # all scenarios
 *   npx tsx e2e/run-campaign.ts --scenario S02     # single scenario
 *
 * Requires a running backend (default: http://localhost:8000).
 * Set BACKEND_URL environment variable to override.
 */

import { readdir, readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

import type { Scenario, ScenarioResult } from './framework/types.js';
import { ScenarioRunner } from './framework/scenario-runner.js';
import { SessionClient, ConnectionError } from './framework/ws-client.js';

const __dirname = fileURLToPath(new URL('.', import.meta.url));

async function loadScenarios(scenarioDir: string, filterId?: string): Promise<Scenario[]> {
  const files = await readdir(scenarioDir);
  const jsonFiles = files.filter(f => f.endsWith('.json')).sort();
  const scenarios: Scenario[] = [];

  for (const file of jsonFiles) {
    const content = await readFile(join(scenarioDir, file), 'utf-8');
    const scenario = JSON.parse(content) as Scenario;
    if (!filterId || scenario.id === filterId) {
      scenarios.push(scenario);
    }
  }

  return scenarios;
}

function parseArgs(): { scenarioId?: string } {
  const args = process.argv.slice(2);
  const idx = args.indexOf('--scenario');
  if (idx !== -1 && args[idx + 1]) {
    return { scenarioId: args[idx + 1] };
  }
  return {};
}

function printResult(result: ScenarioResult): void {
  console.log(`\n${'='.repeat(60)}`);
  console.log(`Szenario: ${result.scenario_name} (${result.scenario_id})`);
  console.log(`${'='.repeat(60)}`);
  console.log(`  Turns:     ${result.turns.length}`);
  console.log(`  Dauer:     ${(result.duration_ms / 1000).toFixed(1)}s`);
  console.log(`  Summary:   ${result.summary}`);

  const assertions = result.turns.reduce(
    (acc, t) => {
      acc.passed += t.evaluation.assertions_passed.length;
      acc.failed += t.evaluation.assertions_failed.length;
      return acc;
    },
    { passed: 0, failed: 0 },
  );

  if (assertions.passed + assertions.failed > 0) {
    console.log(`  Assertions: ${assertions.passed} passed, ${assertions.failed} failed`);
  }

  const probes = result.turns.flatMap(t => t.evaluation.behavior_probes);
  if (probes.length > 0) {
    console.log(`  Probes:    ${probes.filter(p => p.passed).length}/${probes.length} passed`);
  }

  // Show first few turns as preview
  const previewCount = Math.min(3, result.turns.length);
  console.log(`\n  Erste ${previewCount} Turns:`);
  for (const turn of result.turns.slice(0, previewCount)) {
    const responsePreview = turn.assistant_response.slice(0, 80).replace(/\n/g, ' ');
    console.log(`    [${turn.step_id}] ${turn.state.aktiver_modus} | ${turn.state.befuellte_slots}/${turn.state.bekannte_slots} slots | ${turn.response_time_ms}ms`);
    console.log(`      → "${responsePreview}..."`);
  }
}

async function main(): Promise<void> {
  const { scenarioId } = parseArgs();
  const backendUrl = process.env['BACKEND_URL'] ?? 'http://localhost:8000';
  const scenarioDir = join(__dirname, 'scenarios');

  console.log(`E2E Test Campaign — Digitalisierungsfabrik`);
  console.log(`Backend: ${backendUrl}`);
  console.log(`Filter:  ${scenarioId ?? 'alle Szenarien'}\n`);

  // Load scenarios
  const scenarios = await loadScenarios(scenarioDir, scenarioId);
  if (scenarios.length === 0) {
    console.error(`Keine Szenarien gefunden${scenarioId ? ` mit ID "${scenarioId}"` : ''}.`);
    process.exit(1);
  }
  console.log(`${scenarios.length} Szenario(s) geladen: ${scenarios.map(s => s.id).join(', ')}`);

  // Verify backend is reachable
  try {
    await fetch(`${backendUrl}/api/projects`);
  } catch {
    console.error(`\nBackend nicht erreichbar unter ${backendUrl}. Bitte Backend starten.`);
    process.exit(1);
  }

  // Run scenarios
  const results: ScenarioResult[] = [];

  for (const scenario of scenarios) {
    console.log(`\nStarte Szenario: ${scenario.name} (${scenario.id})`);
    const runClient = new SessionClient(backendUrl);
    const runner = new ScenarioRunner(runClient, scenario);

    try {
      const result = await runner.run();
      results.push(result);
      printResult(result);
    } catch (err) {
      if (err instanceof ConnectionError) {
        console.error(`\nBackend nicht erreichbar unter ${backendUrl}. Bitte Backend starten.`);
        process.exit(1);
      }
      console.error(`\nFehler bei Szenario ${scenario.id}:`, err);
    }
  }

  // Final summary
  console.log(`\n${'='.repeat(60)}`);
  console.log(`KAMPAGNE ABGESCHLOSSEN`);
  console.log(`${'='.repeat(60)}`);
  console.log(`  Szenarien:  ${results.length}/${scenarios.length} erfolgreich`);
  const totalTurns = results.reduce((s, r) => s + r.turns.length, 0);
  const totalDuration = results.reduce((s, r) => s + r.duration_ms, 0);
  console.log(`  Turns:      ${totalTurns}`);
  console.log(`  Gesamtdauer: ${(totalDuration / 1000).toFixed(1)}s`);
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
