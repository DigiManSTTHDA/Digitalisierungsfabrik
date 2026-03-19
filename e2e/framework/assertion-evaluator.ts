/**
 * AssertionEvaluator — 7 deterministic SDD rule checks.
 *
 * Stateless: no constructor state needed. All methods take data as input
 * and return AssertionResult arrays.
 */

import type { ArtifactSnapshots, AssertionResult, TurnRecord } from './types.js';

const GERMAN_STOP_WORDS = new Set([
  'der', 'die', 'das', 'und', 'ist', 'in', 'den', 'von', 'zu', 'mit',
  'ein', 'eine', 'es', 'auf', 'für', 'sich', 'nicht', 'als', 'auch',
  'an', 'dem', 'wird', 'aus', 'er', 'hat', 'dass', 'sie', 'nach',
  'bei', 'um', 'noch', 'wie', 'aber', 'vor', 'nur', 'so', 'oder',
  'über', 'kann', 'werden', 'ich', 'wir', 'sind', 'haben', 'was',
]);

const VALID_EMMA_TYPES = new Set([
  'sequenz_aktion', 'entscheidung', 'schleife', 'parallele',
  'ausnahme', 'ereignis', 'datenobjekt',
]);

export class AssertionEvaluator {
  /** Check: mode changes only after phase_complete, escalate, or blocked flags. */
  checkModeTransitions(records: TurnRecord[]): AssertionResult[] {
    const results: AssertionResult[] = [];
    let violations = 0;
    let totalChanges = 0;

    for (let i = 1; i < records.length; i++) {
      const prev = records[i - 1];
      const curr = records[i];
      if (curr.state.aktiver_modus !== prev.state.aktiver_modus && curr.state.aktiver_modus !== '') {
        totalChanges++;
        const hasValidFlag = prev.state.flags.some(f =>
          f === 'phase_complete' || f === 'escalate' || f === 'blocked'
        ) || curr.action === 'panic';

        if (!hasValidFlag) {
          violations++;
          results.push({
            name: 'Moduswechsel nur bei Flags',
            status: 'FAIL',
            detail: `Turn ${curr.turn_nr}: ${prev.state.aktiver_modus} → ${curr.state.aktiver_modus} ohne Flag`,
          });
        }
      }
    }

    if (violations === 0) {
      results.push({
        name: 'Moduswechsel nur bei Flags',
        status: 'PASS',
        detail: `${totalChanges}/${totalChanges} Wechsel korrekt`,
      });
    }
    return results;
  }

  /** Check: between phase_complete and new mode, a moderator turn exists. */
  checkPhaseTransitions(records: TurnRecord[]): AssertionResult[] {
    const results: AssertionResult[] = [];
    let transitions = 0;
    let correct = 0;

    for (let i = 0; i < records.length; i++) {
      if (!records[i].state.flags.includes('phase_complete')) continue;
      transitions++;

      let foundModerator = false;
      for (let j = i + 1; j < records.length; j++) {
        if (records[j].state.aktiver_modus === 'moderator') {
          foundModerator = true;
        }
        if (foundModerator && records[j].state.aktiver_modus !== 'moderator') {
          correct++;
          break;
        }
      }
    }

    if (transitions === 0) {
      results.push({ name: 'Phasenwechsel via Moderator', status: 'PASS', detail: 'Keine Phasenwechsel im Szenario' });
    } else {
      results.push({
        name: 'Phasenwechsel via Moderator',
        status: correct === transitions ? 'PASS' : 'FAIL',
        detail: `${correct}/${transitions} Phasenwechsel korrekt`,
      });
    }
    return results;
  }

  /** Check: during moderator mode, artefakt_updated flag never appears. */
  checkModeratorNoWrite(records: TurnRecord[]): AssertionResult[] {
    const violations: string[] = [];

    for (const record of records) {
      if (record.state.aktiver_modus === 'moderator' &&
          record.state.flags.includes('artefakt_updated')) {
        violations.push(`Turn ${record.turn_nr}`);
      }
    }

    return [{
      name: 'Moderator schreibt keine Artefakte',
      status: violations.length === 0 ? 'PASS' : 'FAIL',
      detail: violations.length === 0
        ? '0 artefakt_updated waehrend Moderator'
        : `artefakt_updated in Moderator-Turns: ${violations.join(', ')}`,
    }];
  }

  /** Check: system responses are in German (heuristic). */
  checkLanguage(records: TurnRecord[]): AssertionResult[] {
    let englishSentences = 0;

    for (const record of records) {
      const text = record.assistant_response;
      if (!text) continue;

      const sentences = text.split(/[.!?]+/).filter(s => s.trim().length > 0);
      for (const sentence of sentences) {
        const words = sentence.trim().split(/\s+/);
        if (words.length <= 5) continue;

        const germanCount = words.filter(w => GERMAN_STOP_WORDS.has(w.toLowerCase())).length;
        const germanRatio = germanCount / words.length;

        if (germanRatio < 0.1 && words.length > 20) {
          englishSentences++;
        }
      }
    }

    if (englishSentences === 0) {
      return [{ name: 'Systemsprache Deutsch', status: 'PASS', detail: 'Alle Antworten auf Deutsch' }];
    } else if (englishSentences <= 2) {
      return [{ name: 'Systemsprache Deutsch', status: 'WARN', detail: `${englishSentences} englische(r) Satz/Sätze erkannt` }];
    }
    return [{ name: 'Systemsprache Deutsch', status: 'FAIL', detail: `${englishSentences} englische Sätze erkannt` }];
  }

  /** Check: no artifact dumps in chat (no JSON blocks > 200 chars). */
  checkOutputContract(records: TurnRecord[]): AssertionResult[] {
    const violations: string[] = [];
    const jsonPattern = /```(?:json)?\s*\n[\s\S]{200,}?\n```/;

    for (const record of records) {
      if (jsonPattern.test(record.assistant_response)) {
        violations.push(`Turn ${record.turn_nr}`);
      }
    }

    return [{
      name: 'Output-Kontrakt',
      status: violations.length === 0 ? 'PASS' : 'FAIL',
      detail: violations.length === 0
        ? 'Kein Artefakt-Dump im Chat'
        : `JSON-Dumps in: ${violations.join(', ')}`,
    }];
  }

  /** Check: artifact structural integrity (successor refs, orphans). */
  checkArtifactIntegrity(artifacts: ArtifactSnapshots): AssertionResult[] {
    const results: AssertionResult[] = [];
    const steps = this.extractSteps(artifacts.struktur);
    if (steps.length === 0) {
      return [{ name: 'Artefakt-Integrität', status: 'PASS', detail: 'Keine Strukturschritte vorhanden' }];
    }

    const stepIds = new Set(steps.map(s => s.id));
    const referenced = new Set<string>();
    const invalidRefs: string[] = [];

    for (const step of steps) {
      for (const ref of step.nachfolger_ids ?? []) {
        if (!stepIds.has(ref)) invalidRefs.push(`${step.id} → ${ref}`);
        referenced.add(ref);
      }
    }

    const orphans = steps.filter(s =>
      !referenced.has(s.id) && s.typ !== 'start' && steps.indexOf(s) !== 0
    );

    if (invalidRefs.length > 0) {
      results.push({ name: 'Artefakt-Integrität: Nachfolger', status: 'FAIL', detail: `Ungültige Referenzen: ${invalidRefs.join(', ')}` });
    } else {
      results.push({ name: 'Artefakt-Integrität: Nachfolger', status: 'PASS', detail: 'Alle Nachfolger-Referenzen gültig' });
    }

    if (orphans.length > 0) {
      results.push({ name: 'Artefakt-Integrität: Waisen', status: 'WARN', detail: `Verwaiste Schritte: ${orphans.map(o => o.id).join(', ')}` });
    } else {
      results.push({ name: 'Artefakt-Integrität: Waisen', status: 'PASS', detail: 'Keine verwaisten Schritte' });
    }

    return results;
  }

  /** Check: all EMMA action types are valid per SDD 8.3 catalog. */
  checkEMMACompatibility(artifacts: ArtifactSnapshots): AssertionResult[] {
    const actions = this.extractEMMAActions(artifacts.algorithmus);
    if (actions.length === 0) {
      return [{ name: 'EMMA-Kompatibilität', status: 'PASS', detail: 'Keine EMMA-Aktionen vorhanden' }];
    }

    const invalid = actions.filter(a => !VALID_EMMA_TYPES.has(a));
    return [{
      name: 'EMMA-Kompatibilität',
      status: invalid.length === 0 ? 'PASS' : 'FAIL',
      detail: invalid.length === 0
        ? `${actions.length} Aktionen, alle gültig`
        : `Ungültige Typen: ${[...new Set(invalid)].join(', ')}`,
    }];
  }

  /** Run all 7 checks and return aggregated results. */
  runAll(records: TurnRecord[], artifacts: ArtifactSnapshots): AssertionResult[] {
    return [
      ...this.checkModeTransitions(records),
      ...this.checkPhaseTransitions(records),
      ...this.checkModeratorNoWrite(records),
      ...this.checkLanguage(records),
      ...this.checkOutputContract(records),
      ...this.checkArtifactIntegrity(artifacts),
      ...this.checkEMMACompatibility(artifacts),
    ];
  }

  private extractSteps(struktur: Record<string, unknown>): Array<{
    id: string; nachfolger_ids?: string[]; typ?: string;
  }> {
    if (Array.isArray(struktur['schritte'])) {
      return struktur['schritte'] as Array<{ id: string; nachfolger_ids?: string[]; typ?: string }>;
    }
    if (typeof struktur['slots'] === 'object' && struktur['slots'] !== null) {
      return Object.values(struktur['slots'] as Record<string, unknown>).filter(
        (v): v is { id: string; nachfolger_ids?: string[]; typ?: string } =>
          typeof v === 'object' && v !== null && 'id' in v
      );
    }
    return [];
  }

  private extractEMMAActions(algorithmus: Record<string, unknown>): string[] {
    const actions: string[] = [];
    const traverse = (obj: unknown): void => {
      if (typeof obj !== 'object' || obj === null) return;
      const record = obj as Record<string, unknown>;
      if (typeof record['emma_aktion'] === 'object' && record['emma_aktion'] !== null) {
        const typ = (record['emma_aktion'] as Record<string, unknown>)['typ'];
        if (typeof typ === 'string') actions.push(typ);
      }
      for (const val of Object.values(record)) {
        if (Array.isArray(val)) val.forEach(traverse);
        else if (typeof val === 'object') traverse(val);
      }
    };
    traverse(algorithmus);
    return actions;
  }
}
