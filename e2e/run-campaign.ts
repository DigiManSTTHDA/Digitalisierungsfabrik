/**
 * E2E Test Campaign — CLI Entry Point
 *
 * Usage:
 *   npx tsx e2e/run-campaign.ts                             # all scenarios
 *   npx tsx e2e/run-campaign.ts --scenario S02              # single scenario
 *   npx tsx e2e/run-campaign.ts --output ./custom-reports   # custom report dir
 *   npx tsx e2e/run-campaign.ts --verbose                   # full dialog in reports
 *
 * Requires a running backend (default: http://localhost:8000).
 * Set BACKEND_URL environment variable to override.
 *
 * Exit codes: 0 = all assertions PASS/WARN, 1 = any assertion FAIL.
 */

import { readdir, readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

import type { Scenario, ScenarioResult } from './framework/types.js';
import { ScenarioRunner } from './framework/scenario-runner.js';
import { SessionClient, ConnectionError } from './framework/ws-client.js';
import { AssertionEvaluator } from './framework/assertion-evaluator.js';
import { BehaviorEvaluator } from './framework/behavior-evaluator.js';
import { CampaignReporter } from './framework/campaign-reporter.js';

const __dirname = fileURLToPath(new URL('.', import.meta.url));

interface CliArgs {
  scenarioId?: string;
  outputDir: string;
  verbose: boolean;
}

function parseArgs(): CliArgs {
  const args = process.argv.slice(2);
  const result: CliArgs = { outputDir: join(__dirname, 'reports'), verbose: false };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--scenario' && args[i + 1]) result.scenarioId = args[++i];
    else if (args[i] === '--output' && args[i + 1]) result.outputDir = args[++i];
    else if (args[i] === '--verbose') result.verbose = true;
  }
  return result;
}

async function loadScenarios(scenarioDir: string, filterId?: string): Promise<Scenario[]> {
  const files = await readdir(scenarioDir);
  const jsonFiles = files.filter(f => f.endsWith('.json')).sort();
  const scenarios: Scenario[] = [];

  for (const file of jsonFiles) {
    const content = await readFile(join(scenarioDir, file), 'utf-8');
    const scenario = JSON.parse(content) as Scenario;
    if (!filterId || scenario.id === filterId) scenarios.push(scenario);
  }
  return scenarios;
}

function printScenarioSummary(result: ScenarioResult): void {
  const passed = result.assertion_results.filter(a => a.status === 'PASS').length;
  const total = result.assertion_results.length;
  const durationSec = (result.duration_ms / 1000).toFixed(0);
  const status = result.assertion_results.some(a => a.status === 'FAIL') ? 'FAIL' : 'PASS';
  const icon = status === 'PASS' ? '✓' : '✗';
  console.log(`${icon} ${result.scenario_id} ${result.scenario_name} — ${result.turns.length} Turns, ${durationSec}s, Assertions: ${passed}/${total} ${status}`);
}

async function main(): Promise<void> {
  const { scenarioId, outputDir, verbose } = parseArgs();
  const backendUrl = process.env['BACKEND_URL'] ?? 'http://localhost:8000';
  const scenarioDir = join(__dirname, 'scenarios');

  console.log(`E2E Test Campaign — Digitalisierungsfabrik`);
  console.log(`Backend: ${backendUrl}`);
  console.log(`Filter:  ${scenarioId ?? 'alle Szenarien'}`);
  console.log(`Output:  ${outputDir}${verbose ? ' (verbose)' : ''}\n`);

  const scenarios = await loadScenarios(scenarioDir, scenarioId);
  if (scenarios.length === 0) {
    console.error(`Keine Szenarien gefunden${scenarioId ? ` mit ID "${scenarioId}"` : ''}.`);
    process.exit(1);
  }
  console.log(`${scenarios.length} Szenario(s) geladen: ${scenarios.map(s => s.id).join(', ')}\n`);

  // Verify backend
  try { await fetch(`${backendUrl}/api/projects`); } catch {
    console.error(`Backend nicht erreichbar unter ${backendUrl}. Bitte Backend starten.`);
    process.exit(1);
  }

  const assertionEvaluator = new AssertionEvaluator();
  const behaviorEvaluator = new BehaviorEvaluator();
  const reporter = new CampaignReporter();
  const results: ScenarioResult[] = [];
  let hasFailure = false;

  for (const scenario of scenarios) {
    const client = new SessionClient(backendUrl);
    const runner = new ScenarioRunner(client, scenario);

    try {
      const result = await runner.run();

      // Evaluate
      result.assertion_results = assertionEvaluator.runAll(result.turns, result.final_artifacts);
      result.behavior_scores = behaviorEvaluator.evaluateAll(
        result.turns, result.final_artifacts, scenario.intent,
      );

      if (result.assertion_results.some(a => a.status === 'FAIL')) hasFailure = true;

      reporter.addScenarioResult(result);
      results.push(result);
      printScenarioSummary(result);
    } catch (err) {
      if (err instanceof ConnectionError) {
        console.error(`\nBackend nicht erreichbar. Abbruch.`);
        process.exit(1);
      }
      console.error(`✗ ${scenario.id} Fehler:`, err instanceof Error ? err.message : err);
    }
  }

  // Write reports
  await reporter.writeReport(outputDir);

  // Final summary
  console.log(`\nKampagne abgeschlossen. ${results.length}/${scenarios.length} Szenarien. Report: ${outputDir}/campaign-summary.md`);
  process.exit(hasFailure ? 1 : 0);
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
