/**
 * CampaignReporter — Generates Markdown reports from scenario results.
 *
 * Produces per-scenario reports (Befundlisten) and an aggregated
 * campaign summary with Bewertungsmatrix and pattern detection.
 */

import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import type { AssertionResult, BehaviorScore, ScenarioResult } from './types.js';

export class CampaignReporter {
  private results: ScenarioResult[] = [];

  addScenarioResult(result: ScenarioResult): void {
    this.results.push(result);
  }

  /** Write all reports: per-scenario + campaign summary + raw data. */
  async writeReport(outputDir: string): Promise<void> {
    await mkdir(outputDir, { recursive: true });

    for (const result of this.results) {
      await this.writeScenarioReport(result, outputDir);
    }
    await this.writeCampaignSummary(outputDir);
  }

  /** Write a single scenario report as `scenario-<ID>.md`. */
  async writeScenarioReport(result: ScenarioResult, outputDir: string): Promise<void> {
    await mkdir(outputDir, { recursive: true });
    const md = this.generateScenarioMarkdown(result);
    await writeFile(join(outputDir, `scenario-${result.scenario_id}.md`), md, 'utf-8');
  }

  /** Analyze patterns across all scenarios. */
  analyzePatterns(): {
    assertion_summary: { total: number; passed: number; failed: number; warnings: number };
    behavior_matrix: Record<string, Record<string, BehaviorScore>>;
    problem_patterns: string[];
    recommendations: string[];
  } {
    // Assertion summary
    const allAssertions = this.results.flatMap(r => r.assertion_results);
    const assertion_summary = {
      total: allAssertions.length,
      passed: allAssertions.filter(a => a.status === 'PASS').length,
      failed: allAssertions.filter(a => a.status === 'FAIL').length,
      warnings: allAssertions.filter(a => a.status === 'WARN').length,
    };

    // Behavior matrix: dimension → scenario_id → score
    const behavior_matrix: Record<string, Record<string, BehaviorScore>> = {};
    for (const result of this.results) {
      for (const score of result.behavior_scores) {
        if (!behavior_matrix[score.dimension]) behavior_matrix[score.dimension] = {};
        behavior_matrix[score.dimension][result.scenario_id] = score;
      }
    }

    const problem_patterns = this.detectPatterns(behavior_matrix, allAssertions);
    const recommendations = this.generateRecommendations(problem_patterns);

    return { assertion_summary, behavior_matrix, problem_patterns, recommendations };
  }

  /** Write campaign-summary.md and raw-data.json. */
  async writeCampaignSummary(outputDir: string): Promise<void> {
    await mkdir(outputDir, { recursive: true });
    const analysis = this.analyzePatterns();
    const md = this.generateCampaignMarkdown(analysis);
    await writeFile(join(outputDir, 'campaign-summary.md'), md, 'utf-8');

    const rawData = this.results.flatMap(r => r.turns);
    await writeFile(join(outputDir, 'raw-data.json'), JSON.stringify(rawData, null, 2), 'utf-8');
  }

  // -------------------------------------------------------------------------
  // Scenario Markdown
  // -------------------------------------------------------------------------

  private generateScenarioMarkdown(result: ScenarioResult): string {
    const lines: string[] = [];
    const durationSec = (result.duration_ms / 1000).toFixed(0);
    const phases = [...new Set(result.turns.map(t => t.phase))].join(' → ');
    const nudges = result.turns.filter(t => t.evaluation.metrics.nudge_used).length;
    const escalations = result.turns.filter(t => t.action === 'panic').length;

    lines.push(`# Szenario ${result.scenario_id} — ${result.scenario_name}`);
    lines.push('');
    lines.push('## Eckdaten');
    lines.push(`- Turns: ${result.turns.length} | Dauer: ${durationSec}s | Phasen erreicht: ${phases}`);
    lines.push(`- Nudges benötigt: ${nudges}`);
    lines.push(`- Eskalationen: ${escalations}`);
    lines.push('');

    // Assertion results
    if (result.assertion_results.length > 0) {
      lines.push('## Assertion-Ergebnisse');
      lines.push('| Assertion | Status | Detail |');
      lines.push('|-----------|--------|--------|');
      for (const a of result.assertion_results) {
        lines.push(`| ${a.name} | ${a.status} | ${a.detail} |`);
      }
      lines.push('');
    }

    // Behavior scores
    if (result.behavior_scores.length > 0) {
      lines.push('## Verhaltensbewertung');
      lines.push('| Dimension | Bewertung | Begründung |');
      lines.push('|-----------|-----------|------------|');
      for (const s of result.behavior_scores) {
        const reason = s.findings.length > 0 ? s.findings.join('. ') : 'Keine Auffälligkeiten';
        lines.push(`| ${s.dimension} | ${s.rating} | ${reason} |`);
      }
      lines.push('');
    }

    // Dialog protocol (truncated)
    lines.push('## Dialog-Protokoll (gekürzt)');
    lines.push('| # | Modus | User (Auszug) | System (Auszug) | Slots | Flags | Bemerkung |');
    lines.push('|---|-------|---------------|-----------------|-------|-------|-----------|');
    for (const turn of result.turns) {
      const userMsg = turn.user_message.slice(0, 50).replace(/\|/g, '\\|');
      const sysMsg = turn.assistant_response.slice(0, 80).replace(/\|/g, '\\|').replace(/\n/g, ' ');
      const slots = `${turn.state.befuellte_slots}/${turn.state.bekannte_slots}`;
      const flags = turn.state.flags.join(', ') || '—';
      const note = turn.evaluation.metrics.nudge_used ? 'Nudge' :
        turn.action === 'panic' ? 'Eskalation' : '';
      lines.push(`| ${turn.turn_nr} | ${turn.state.aktiver_modus} | ${userMsg} | ${sysMsg} | ${slots} | ${flags} | ${note} |`);
    }
    lines.push('');

    // Artifact snapshots
    lines.push('## Artefakt-Snapshot (final)');
    lines.push('```json');
    lines.push(JSON.stringify(result.final_artifacts, null, 2));
    lines.push('```');

    return lines.join('\n');
  }

  // -------------------------------------------------------------------------
  // Campaign Markdown
  // -------------------------------------------------------------------------

  private generateCampaignMarkdown(analysis: ReturnType<CampaignReporter['analyzePatterns']>): string {
    const lines: string[] = [];
    lines.push('# Kampagnen-Bewertung');
    lines.push('');

    // Assertion summary
    const s = analysis.assertion_summary;
    lines.push('## Assertion-Zusammenfassung');
    lines.push(`- Gesamt: ${s.total} | Bestanden: ${s.passed} | Fehlgeschlagen: ${s.failed} | Warnungen: ${s.warnings}`);
    lines.push('');

    // Behavior matrix
    const dimensions = Object.keys(analysis.behavior_matrix);
    const scenarioIds = this.results.map(r => r.scenario_id);

    if (dimensions.length > 0) {
      lines.push('## Bewertungsmatrix');
      lines.push(`| Dimension | ${scenarioIds.join(' | ')} | Muster |`);
      lines.push(`|-----------|${scenarioIds.map(() => '-----').join('|')}|--------|`);

      for (const dim of dimensions) {
        const scores = scenarioIds.map(id => {
          const score = analysis.behavior_matrix[dim]?.[id];
          return score ? score.rating : '—';
        });
        const pattern = this.findDimensionPattern(dim, analysis.behavior_matrix[dim] ?? {});
        lines.push(`| ${dim} | ${scores.join(' | ')} | ${pattern} |`);
      }
      lines.push('');
    }

    // Problem patterns
    if (analysis.problem_patterns.length > 0) {
      lines.push('## Erkannte Problemmuster');
      for (let i = 0; i < analysis.problem_patterns.length; i++) {
        lines.push(`${i + 1}. ${analysis.problem_patterns[i]}`);
      }
      lines.push('');
    }

    // Recommendations
    if (analysis.recommendations.length > 0) {
      lines.push('## Empfehlungen');
      for (let i = 0; i < analysis.recommendations.length; i++) {
        lines.push(`${i + 1}. ${analysis.recommendations[i]}`);
      }
      lines.push('');
    }

    return lines.join('\n');
  }

  // -------------------------------------------------------------------------
  // Pattern Detection
  // -------------------------------------------------------------------------

  private detectPatterns(
    behaviorMatrix: Record<string, Record<string, BehaviorScore>>,
    allAssertions: AssertionResult[],
  ): string[] {
    const patterns: string[] = [];
    const totalScenarios = this.results.length;

    // Pattern 1: ≥50% of scenarios are BEFRIEDIGEND or worse in a dimension
    for (const [dim, scores] of Object.entries(behaviorMatrix)) {
      const weak = Object.values(scores).filter(s =>
        s.rating === 'BEFRIEDIGEND' || s.rating === 'MANGELHAFT'
      ).length;
      if (weak >= totalScenarios * 0.5 && totalScenarios > 0) {
        patterns.push(`${dim} ist systemisch schwach (${weak}/${totalScenarios} Szenarien)`);
      }
    }

    // Pattern 2: ≥3 scenarios have the same assertion failure
    const failCounts = new Map<string, number>();
    for (const result of this.results) {
      const failNames = new Set(result.assertion_results.filter(a => a.status === 'FAIL').map(a => a.name));
      for (const name of failNames) {
        failCounts.set(name, (failCounts.get(name) ?? 0) + 1);
      }
    }
    for (const [name, count] of failCounts) {
      if (count >= 3) {
        patterns.push(`${name} schlägt in ${count} Szenarien fehl`);
      }
    }

    // Pattern 3: Median nudge_total > 2 across all scenarios
    const nudgeTotals = this.results.map(r =>
      r.turns.filter(t => t.evaluation.metrics.nudge_used).length
    ).sort((a, b) => a - b);
    if (nudgeTotals.length > 0) {
      const medianNudge = nudgeTotals[Math.floor(nudgeTotals.length / 2)];
      if (medianNudge > 2) {
        patterns.push('Phase-Complete-Erkennung hat systemische Schwäche');
      }
    }

    return patterns;
  }

  private generateRecommendations(patterns: string[]): string[] {
    const recs: string[] = [];
    for (const pattern of patterns) {
      if (pattern.includes('Phase-Complete')) {
        recs.push('Phase-Complete-Logik überarbeiten: Explorationsmodus soll aktiver nach Vollständigkeit fragen.');
      } else if (pattern.includes('Dialogführung')) {
        recs.push('Systemprompt-Anpassung: Bei kurzen Antworten nachfragen, nicht annehmen.');
      } else if (pattern.includes('systemisch schwach')) {
        recs.push(`Dimension "${pattern.split(' ')[0]}" gezielt verbessern.`);
      } else if (pattern.includes('schlägt in')) {
        const name = pattern.split(' schlägt')[0];
        recs.push(`Assertion "${name}" analysieren und Ursache beheben.`);
      }
    }
    return recs;
  }

  private findDimensionPattern(dim: string, scores: Record<string, BehaviorScore>): string {
    const values = Object.values(scores);
    const weak = values.filter(s => s.rating === 'BEFRIEDIGEND' || s.rating === 'MANGELHAFT');
    if (weak.length >= values.length * 0.5 && values.length > 0) {
      return `Systemisch schwach (${weak.length}/${values.length})`;
    }
    const bad = values.filter(s => s.rating === 'MANGELHAFT');
    if (bad.length > 0) {
      return `${bad.length} MANGELHAFT`;
    }
    return 'Konsistent gut';
  }
}
