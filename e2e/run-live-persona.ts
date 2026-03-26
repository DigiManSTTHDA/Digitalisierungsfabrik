/**
 * Live-Persona-Runner — Dynamische E2E-Tests mit LLM-generierter Persona.
 *
 * Statt vorgeskripteter Turns spielt ein LLM die Persona (z.B. Herr Krause)
 * und antwortet natürlich auf die Fragen des Explorers — genau wie ein
 * manueller Test, nur automatisiert.
 *
 * Usage:
 *   npx tsx e2e/run-live-persona.ts --playbook agent-docs/e2e-playbook-angebotsanfragen.md
 *   npx tsx e2e/run-live-persona.ts --playbook agent-docs/e2e-human-playbook.md --max-turns 15
 *
 * Requires:
 *   - Running backend (BACKEND_URL, default http://127.0.0.1:8000)
 *   - OpenAI API key (OPENAI_API_KEY or LLM_API_KEY env var)
 */

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { SessionClient } from './framework/ws-client.js';
import type { TurnResponse } from './framework/types.js';
import OpenAI from 'openai';

const __dirname = fileURLToPath(new URL('.', import.meta.url));

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

interface Config {
  playbookPath: string;
  backendUrl: string;
  maxTurns: number;
  personaModel: string;
  outputDir: string;
}

function parseArgs(): Config {
  const args = process.argv.slice(2);
  const config: Config = {
    playbookPath: '',
    backendUrl: process.env['BACKEND_URL'] ?? 'http://127.0.0.1:8000',
    maxTurns: 20,
    personaModel: process.env['PERSONA_MODEL'] ?? 'gpt-4.1-mini',
    outputDir: join(__dirname, 'reports'),
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--playbook' && args[i + 1]) config.playbookPath = args[++i];
    else if (args[i] === '--max-turns' && args[i + 1]) config.maxTurns = parseInt(args[++i], 10);
    else if (args[i] === '--model' && args[i + 1]) config.personaModel = args[++i];
    else if (args[i] === '--output' && args[i + 1]) config.outputDir = args[++i];
  }

  if (!config.playbookPath) {
    console.error('Usage: npx tsx e2e/run-live-persona.ts --playbook <path-to-playbook.md>');
    process.exit(1);
  }
  return config;
}

// ---------------------------------------------------------------------------
// Persona LLM
// ---------------------------------------------------------------------------

class PersonaLLM {
  private readonly client: OpenAI;
  private readonly model: string;
  private readonly systemPrompt: string;
  private readonly dialog: { role: 'user' | 'assistant'; content: string }[] = [];

  constructor(apiKey: string, model: string, playbook: string) {
    this.client = new OpenAI({ apiKey });
    this.model = model;
    this.systemPrompt = this.buildSystemPrompt(playbook);
  }

  private buildSystemPrompt(playbook: string): string {
    return `Du spielst eine Persona in einem E2E-Test der Digitalisierungsfabrik.

DEINE AUFGABE: Du bist die Person die im Playbook beschrieben ist. Du antwortest natürlich und authentisch auf die Fragen des Interviewers (des "Explorers"). Du kennst deinen Arbeitsprozess genau und beschreibst ihn so wie du ihn jeden Tag machst.

REGELN:
- Antworte als die Persona, nicht als KI-Assistent
- Sprich so wie die Persona spricht (siehe Charakter/typische Formulierungen im Playbook)
- Gib Informationen basierend auf deinem Prozesswissen — aber nur das was gefragt wird
- Wenn der Explorer nach etwas fragt das im Playbook steht: antworte damit
- Wenn der Explorer nach etwas fragt das NICHT explizit im Playbook steht aber plausibel ist: erfinde eine plausible, konsistente Antwort die zum Prozess passt
- Erfinde KEINE Technologien oder Systeme die nicht im Playbook stehen
- Wenn der Explorer fragt ob alles passt oder ob du bestätigst: bestätige knapp
- Antworte auf Deutsch
- Halte dich kurz — Sachbearbeiter reden nicht in Absätzen

PLAYBOOK (dein vollständiges Prozesswissen):

${playbook}`;
  }

  async respond(explorerQuestion: string): Promise<string> {
    this.dialog.push({ role: 'user', content: explorerQuestion });

    const response = await this.client.chat.completions.create({
      model: this.model,
      temperature: 0.7,
      max_tokens: 500,
      messages: [
        { role: 'system', content: this.systemPrompt },
        ...this.dialog,
      ],
    });

    const answer = response.choices[0]?.message?.content ?? '';
    this.dialog.push({ role: 'assistant', content: answer });
    return answer;
  }

  getDialog(): { role: string; content: string }[] {
    return [...this.dialog];
  }
}

// ---------------------------------------------------------------------------
// Runner
// ---------------------------------------------------------------------------

interface TurnLog {
  turn: number;
  explorer_question: string;
  persona_response: string;
  phasenstatus: string;
  flags: string[];
  slots_filled: number;
  slots_total: number;
  response_time_ms: number;
}

async function run(config: Config): Promise<void> {
  // Load playbook
  const playbook = await readFile(config.playbookPath, 'utf-8');
  const playbookName = config.playbookPath.split(/[/\\]/).pop() ?? 'unknown';

  // Extract persona name from playbook (first "Persona:" line)
  const personaMatch = playbook.match(/\*\*Persona:\*\*\s*(.+)/);
  const personaName = personaMatch ? personaMatch[1].trim() : 'Unbekannt';

  // Setup OpenAI
  const apiKey = process.env['OPENAI_API_KEY'] ?? process.env['LLM_API_KEY'] ?? '';
  if (!apiKey) {
    console.error('Kein API-Key gefunden. Setze OPENAI_API_KEY oder LLM_API_KEY.');
    process.exit(1);
  }

  console.log(`Live-Persona-Runner — Digitalisierungsfabrik`);
  console.log(`Playbook:  ${playbookName}`);
  console.log(`Persona:   ${personaName}`);
  console.log(`Model:     ${config.personaModel}`);
  console.log(`Backend:   ${config.backendUrl}`);
  console.log(`Max Turns: ${config.maxTurns}\n`);

  const persona = new PersonaLLM(apiKey, config.personaModel, playbook);
  const client = new SessionClient(config.backendUrl, 120_000);

  // Create project and connect
  const projectId = await client.createProject(`live-persona-${Date.now()}`);
  const greeting = await client.connect(projectId);

  console.log(`Projekt erstellt: ${projectId}`);
  console.log(`Begrüßung: ${greeting.message.substring(0, 100)}...\n`);

  const turns: TurnLog[] = [];
  let currentQuestion = greeting.message;
  let phaseComplete = false;

  for (let turn = 1; turn <= config.maxTurns; turn++) {
    // Persona generates response
    const personaAnswer = await persona.respond(currentQuestion);

    console.log(`--- Turn ${turn} ---`);
    console.log(`Explorer: ${currentQuestion.substring(0, 120)}${currentQuestion.length > 120 ? '...' : ''}`);
    console.log(`Persona:  ${personaAnswer.substring(0, 120)}${personaAnswer.length > 120 ? '...' : ''}`);

    // Send to backend
    const response: TurnResponse = await client.sendMessage(projectId, personaAnswer);

    const log: TurnLog = {
      turn,
      explorer_question: currentQuestion,
      persona_response: personaAnswer,
      phasenstatus: response.state.phasenstatus,
      flags: response.state.flags,
      slots_filled: response.state.befuellte_slots,
      slots_total: response.state.bekannte_slots,
      response_time_ms: response.response_time_ms,
    };
    turns.push(log);

    console.log(`Status: ${response.state.phasenstatus} | Slots: ${response.state.befuellte_slots}/${response.state.bekannte_slots} | ${response.response_time_ms}ms`);
    console.log('');

    // Check completion
    if (response.state.flags.includes('phase_complete') || response.state.phasenstatus === 'phase_complete') {
      console.log(`=== Phase complete nach ${turn} Turns ===\n`);
      phaseComplete = true;
      // Collect the moderator auto-response as final message
      currentQuestion = response.message;
      break;
    }

    currentQuestion = response.message;
  }

  if (!phaseComplete) {
    console.log(`=== Max Turns (${config.maxTurns}) erreicht ohne phase_complete ===\n`);
  }

  // Fetch final artifacts
  const artifacts = await client.getArtifacts(projectId);
  client.disconnect();

  // Generate report
  await mkdir(config.outputDir, { recursive: true });
  const reportPath = join(config.outputDir, `live-persona-${playbookName.replace('.md', '')}.md`);
  const jsonPath = join(config.outputDir, `live-persona-${playbookName.replace('.md', '')}.json`);

  const report = generateReport(personaName, playbookName, config, turns, artifacts, phaseComplete, playbook);

  // Generate qualitative analysis via LLM
  console.log('Generiere qualitative Analyse...');
  const analysis = await generateAnalysis(apiKey, config.personaModel, playbook, report, artifacts);

  const fullReport = report + '\n\n---\n\n' + analysis;
  await writeFile(reportPath, fullReport, 'utf-8');
  await writeFile(jsonPath, JSON.stringify({ turns, artifacts, config: { ...config, apiKey: '***' } }, null, 2), 'utf-8');

  console.log(`\nReport: ${reportPath}`);
  console.log(`Rohdaten: ${jsonPath}`);
}

/** Generate qualitative analysis by feeding playbook + artifacts + report to an LLM. */
async function generateAnalysis(
  apiKey: string, model: string, playbook: string, report: string,
  artifacts: Record<string, unknown>,
): Promise<string> {
  const client = new OpenAI({ apiKey });

  // Always use the strongest available model for analysis — this is a quality gate
  const analysisModel = 'gpt-5.4';

  // Extract slot contents for direct analysis
  const slots = extractActualSlots(artifacts);
  const slotDump = Object.entries(slots)
    .map(([id, content]) => `### ${id}\n${content}`)
    .join('\n\n');

  const response = await client.chat.completions.create({
    model: analysisModel,
    temperature: 0.3,
    max_completion_tokens: 3000,
    messages: [
      {
        role: 'system',
        content: `Du bist ein erfahrener Qualitätsanalyst für RPA-Prozesserhebungen. Du bewertest das Ergebnis eines E2E-Tests der **Explorationsphase**.

WICHTIG — Bewertungsmaßstab:
Dies ist die ERSTE von vier Phasen (Exploration → Strukturierung → Spezifikation → Validierung). Die Exploration muss den Prozess **im Überblick nachvollziehbar** machen — nicht jedes Detail erfassen. Fehlende Einzelfelder, Variable oder Klick-Details sind KEIN Durchfallgrund, solange der Prozess in seinen wesentlichen Abläufen, Systemen, Entscheidungen und Schleifen verstanden wurde. Details werden in den Folgephasen ergänzt.

Bewertungsskala:
- **BESTANDEN** — Prozess ist nachvollziehbar, ein Prozessanalyst könnte damit in die nächste Phase gehen. Fehlende Details sind akzeptabel.
- **BESTANDEN MIT LÜCKEN** — Prozess ist im Kern nachvollziehbar, aber es fehlen wichtige strukturelle Elemente (z.B. ein ganzer Entscheidungspfad, ein System, ein wesentlicher Prozessschritt).
- **NICHT BESTANDEN** — Prozess ist nicht nachvollziehbar oder es fehlen wesentliche Teile (z.B. Start/Ende unklar, Hauptablauf unvollständig, Halluzinationen).

KRITISCH — Sorgfaltspflicht:
Du bekommst drei Quellen. Prüfe JEDE Aussage gegen die ARTEFAKT-ROHDATEN.
- "Implizit enthalten" oder "sinngemäß abgedeckt" zählt NICHT. Wenn ein Konzept nicht im Artefakt-Text steht, fehlt es. Punkt.
- Behaupte nie dass etwas fehlt ohne im Artefakt nachgeschaut zu haben.
- Behaupte nie dass etwas da ist ohne es im Artefakt gefunden zu haben.
- Die Artefakt-Rohdaten sind die Wahrheit — nicht der Dialog, nicht der Report-Text.

ANTI-SCHÖNFÄRBEREI:
- Sei skeptisch. Dein Job ist es Lücken zu finden, nicht das Artefakt zu loben.
- "Für die Exploration akzeptabel" ist KEIN Freibrief. Wenn ein zentraler Entscheidungspfad, eine Geschäftsregel oder ein häufiger Ausnahmefall (~wöchentlich oder öfter) im Playbook steht aber NICHT im Artefakt: das ist eine echte Lücke, auch in der Explorationsphase.
- Unterscheide klar: (a) Detail das in Folgephasen kommt (z.B. exakte Feldnamen, Citrix-Zugang) vs. (b) strukturelles Element das den Prozess unvollständig macht (z.B. fehlende Geschäftsregel, fehlender Ausnahmefall, fehlendes System).

Du bekommst:
1. PLAYBOOK — Ground Truth (was der Prozess wirklich ist, inkl. Ziel-Artefakt)
2. ARTEFAKT-ROHDATEN — Die tatsächlichen Slot-Inhalte die der Explorer geschrieben hat (DIESE sind die Bewertungsgrundlage!)
3. DIALOG — Der vollständige Gesprächsverlauf

Schreibe eine qualitative Analyse auf Deutsch:

## Qualitative Analyse

### Gesamturteil
Ein Absatz: Bestanden / Bestanden mit Lücken / Nicht bestanden? Warum? Könnte ein Prozessanalyst mit diesem Artefakt in die Strukturierungsphase gehen?

### Slot-für-Slot-Bewertung
Pro Slot: Prüfe den TATSÄCHLICHEN Slot-Inhalt aus den Rohdaten gegen das Playbook.
- Was steht drin, was fehlt? Belege mit Zitaten aus den Rohdaten.
- Mechanische "MISS"-Meldungen: False Positive (steht wörtlich oder klar sinngemäß im Artefakt — Beleg angeben!) oder echtes Problem?

### Fehlende Inhalte (gegen Playbook)
Gehe das Playbook Abschnitt für Abschnitt durch und liste ALLES was im Playbook steht aber NICHT im Artefakt:
- Fehlende Entscheidungsregeln oder Geschäftslogik
- Fehlende Ausnahmefälle / Sonderfälle
- Fehlende Systeme oder Systemdetails
- Fehlende Variablen oder Daten

Für jede Lücke: Bewerte ob sie (a) strukturell relevant ist (beeinträchtigt Prozessverständnis) oder (b) ein Detail das in Folgephasen ergänzt wird.

### Was gut funktioniert hat
Was hat der Explorer besonders gut erfasst?

### Dialogführung
Kurz: Fragen zielführend? Wiederholungen? Timing angemessen?

### Fazit
| Aspekt | Bewertung |
Mit: Prozess-Grundverständnis, Entscheidungslogik, Systeme, Sonderfälle, Halluzinationen, Granularität`
      },
      {
        role: 'user',
        content: `PLAYBOOK (Ground Truth):\n\n${playbook}\n\n---\n\nARTEFAKT-ROHDATEN (Slot-Inhalte — dies ist die Bewertungsgrundlage!):\n\n${slotDump}\n\n---\n\nDIALOG (vollständiger Gesprächsverlauf):\n\n${report}`
      }
    ],
  });

  return response.choices[0]?.message?.content ?? '(Analyse konnte nicht generiert werden)';
}

function generateReport(
  personaName: string,
  playbookName: string,
  config: Config,
  turns: TurnLog[],
  artifacts: Record<string, unknown>,
  phaseComplete: boolean,
  playbook: string,
): string {
  const totalTime = turns.reduce((sum, t) => sum + t.response_time_ms, 0);
  const nearingIdx = turns.findIndex(t => t.phasenstatus === 'nearing_completion');
  const personaShort = personaName.split(',')[0];

  // Extract target/actual for comparison
  const targetArtifact = extractTargetArtifact(playbook);
  const actualSlots = extractActualSlots(artifacts);
  const forbidden = extractForbiddenConcepts(playbook);

  // Run all checks upfront for summary
  const slotIds = ['prozessausloeser', 'prozessziel', 'prozessbeschreibung',
    'entscheidungen_und_schleifen', 'beteiligte_systeme', 'variablen_und_daten'];

  const slotResults: { id: string; keywords: { kw: string; found: boolean }[]; hasSoll: boolean; hasIst: boolean }[] = [];
  for (const slotId of slotIds) {
    const target = targetArtifact[slotId];
    const actual = actualSlots[slotId];
    const keywords = (target?.mustContain ?? []).map(kw => {
      // Smart matching: split compound keywords on / and check each alternative
      const alternatives = kw.split('/').map(s => s.trim());
      const found = alternatives.some(alt => actual?.toLowerCase().includes(alt.toLowerCase()));
      return { kw, found };
    });
    slotResults.push({ id: slotId, keywords, hasSoll: !!target, hasIst: !!actual?.trim() });
  }

  // Check forbidden concepts across all actual content
  const allActual = Object.values(actualSlots).join(' ').toLowerCase();
  const forbiddenFound = forbidden.filter(f => allActual.includes(f.toLowerCase()));

  // Count totals
  const totalKeywords = slotResults.flatMap(s => s.keywords);
  const passCount = totalKeywords.filter(k => k.found).length;
  const missCount = totalKeywords.filter(k => !k.found).length;
  const filledSlots = slotResults.filter(s => s.hasIst).length;

  // Avg response length
  const avgPersonaLen = Math.round(turns.reduce((s, t) => s + t.persona_response.length, 0) / turns.length);

  // =========================================================================
  // Build report
  // =========================================================================
  const lines: string[] = [];

  // --- Summary ---
  lines.push(`# Live-Persona-Test: ${personaName}`, '');
  lines.push('## Zusammenfassung', '');

  const verdict = !phaseComplete ? 'NICHT ABGESCHLOSSEN'
    : missCount === 0 && forbiddenFound.length === 0 ? 'BESTANDEN'
    : forbiddenFound.length > 0 ? 'HALLUZINATION'
    : missCount <= 2 ? 'BESTANDEN MIT LÜCKEN'
    : 'LÜCKENHAFT';

  lines.push(`**Ergebnis: ${verdict}**`, '');
  lines.push(`| Metrik | Wert |`);
  lines.push(`|--------|------|`);
  lines.push(`| Turns bis phase_complete | ${phaseComplete ? turns.length : 'nicht erreicht'} |`);
  lines.push(`| nearing_completion ab | Turn ${nearingIdx >= 0 ? nearingIdx + 1 : 'nie'} |`);
  lines.push(`| Backend-Dauer | ${(totalTime / 1000).toFixed(0)}s |`);
  lines.push(`| Slots befüllt | ${filledSlots}/${slotIds.length} |`);
  lines.push(`| Pflichtbegriffe | ${passCount}/${totalKeywords.length} (${missCount} fehlend) |`);
  lines.push(`| Halluzinationen | ${forbiddenFound.length === 0 ? 'keine' : forbiddenFound.join(', ')} |`);
  lines.push(`| Persona-Model | ${config.personaModel} |`);
  lines.push(`| Mittlere Antwortlänge Persona | ${avgPersonaLen} Zeichen |`);
  lines.push('');

  if (missCount > 0) {
    lines.push('### Fehlende Pflichtbegriffe', '');
    for (const sr of slotResults) {
      const misses = sr.keywords.filter(k => !k.found);
      if (misses.length > 0) {
        lines.push(`- **${sr.id}:** ${misses.map(m => `"${m.kw}"`).join(', ')}`);
      }
    }
    lines.push('');
  }

  if (forbiddenFound.length > 0) {
    lines.push('### Halluzinationen gefunden', '');
    lines.push(`Im Artefakt gefunden: ${forbiddenFound.map(f => `"${f}"`).join(', ')}`, '');
  }

  // --- Eckdaten ---
  lines.push('---', '', '## Eckdaten', '');
  lines.push(`| Parameter | Wert |`);
  lines.push(`|-----------|------|`);
  lines.push(`| Playbook | \`${playbookName}\` |`);
  lines.push(`| Persona-Model | ${config.personaModel} |`);
  lines.push(`| Explorer-Model | GPT-5.4 (Backend) |`);
  lines.push(`| Max Turns | ${config.maxTurns} |`);
  lines.push(`| Tatsächliche Turns | ${turns.length} |`);
  lines.push('');

  // --- Dialog ---
  lines.push('---', '', '## Vollständiger Dialog', '');

  for (const t of turns) {
    lines.push(`### Turn ${t.turn} — \`${t.phasenstatus}\` | ${t.slots_filled}/${t.slots_total} Slots | ${(t.response_time_ms / 1000).toFixed(1)}s`);
    lines.push('');
    lines.push(`**Explorer:**`);
    lines.push(`> ${t.explorer_question.replace(/\n/g, '\n> ')}`);
    lines.push('');
    lines.push(`**${personaShort}:**`);
    lines.push(`> ${t.persona_response.replace(/\n/g, '\n> ')}`);
    lines.push('');
  }

  // --- Artefakt-Vergleich ---
  lines.push('---', '', '## Artefakt-Vergleich: Soll vs. Ist', '');

  for (const sr of slotResults) {
    const target = targetArtifact[sr.id];
    const actual = actualSlots[sr.id];

    lines.push(`### ${sr.id}`);
    lines.push('');

    if (target) {
      lines.push('<details><summary>Soll (Playbook)</summary>', '');
      lines.push(`> ${target.content.replace(/\n/g, '\n> ')}`);
      lines.push('', '</details>', '');

      if (sr.keywords.length > 0) {
        const checks = sr.keywords.map(k => `${k.found ? 'PASS' : '**MISS**'} ${k.kw}`);
        lines.push(`**Pflichtbegriffe:** ${checks.join(' | ')}`, '');
      }
    }

    lines.push('**Ist:**');
    if (actual) {
      lines.push(`> ${actual.replace(/\n/g, '\n> ')}`);
    } else {
      lines.push('> (leer)');
    }
    lines.push('');
  }

  // --- Raw artifacts ---
  lines.push('---', '', '<details><summary>Artefakt (Rohdaten JSON)</summary>', '',
    '```json', JSON.stringify(artifacts, null, 2), '```', '', '</details>');

  return lines.join('\n');
}

/** Extract forbidden concepts from playbook. */
function extractForbiddenConcepts(playbook: string): string[] {
  const match = playbook.match(/NICHT im Artefakt stehen dürfen[^]*?\n([^#]+)/i);
  if (!match) return [];
  return match[1].split(/[,\n]/)
    .map(s => s.trim())
    .filter(s => s.length > 2 && !s.startsWith('*') && !s.startsWith('-'));
}

/** Extract target artifact sections from playbook markdown. */
function extractTargetArtifact(playbook: string): Record<string, { content: string; mustContain: string[] }> {
  const result: Record<string, { content: string; mustContain: string[] }> = {};
  const slotIds = ['prozessausloeser', 'prozessziel', 'prozessbeschreibung',
    'entscheidungen_und_schleifen', 'beteiligte_systeme', 'variablen_und_daten'];

  for (const slotId of slotIds) {
    // Find ### slotId section
    const headerPattern = new RegExp(`### ${slotId}\\b`, 'i');
    const match = playbook.match(headerPattern);
    if (!match || match.index === undefined) continue;

    const startIdx = match.index + match[0].length;
    // Find next ### or --- or end
    const rest = playbook.substring(startIdx);
    const endMatch = rest.match(/\n###\s|\n---/);
    const section = endMatch ? rest.substring(0, endMatch.index) : rest.substring(0, 500);

    // Extract quoted content (lines starting with >)
    const quotedLines = section.split('\n')
      .filter(l => l.trim().startsWith('>'))
      .map(l => l.replace(/^>\s*/, '').trim())
      .filter(Boolean);
    const content = quotedLines.join('\n');

    // Extract "Muss enthalten:" line
    const mustMatch = section.match(/\*\*Muss enthalten:\*\*\s*(.+)/);
    const mustContain = mustMatch
      ? mustMatch[1].split(',').map(s => s.trim()).filter(Boolean)
      : [];

    result[slotId] = { content, mustContain };
  }
  return result;
}

/** Extract actual slot contents from artifacts response. */
function extractActualSlots(artifacts: Record<string, unknown>): Record<string, string> {
  const result: Record<string, string> = {};
  const exploration = artifacts['exploration'] as Record<string, unknown> | undefined;
  if (!exploration) return result;
  const slots = exploration['slots'] as Record<string, Record<string, unknown>> | undefined;
  if (!slots) return result;

  for (const [slotId, slot] of Object.entries(slots)) {
    result[slotId] = (slot['inhalt'] as string) ?? '';
  }
  return result;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

const config = parseArgs();
run(config).catch((err) => {
  console.error('Fatal:', err instanceof Error ? err.message : err);
  process.exit(1);
});
