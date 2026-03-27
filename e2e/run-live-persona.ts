/**
 * Live-Persona-Runner — Dynamische E2E-Tests mit LLM-generierter Persona.
 *
 * Statt vorgeskripteter Turns spielt ein LLM die Persona (z.B. Frau Meier)
 * und antwortet natürlich auf die Fragen des Systems — genau wie ein
 * manueller Test, nur automatisiert.
 *
 * Unterstützt Multi-Phase: Exploration → Moderator → Strukturierung (und weiter).
 *
 * Usage:
 *   # Nur Exploration (default)
 *   npx tsx e2e/run-live-persona.ts --playbook agent-docs/e2e-human-playbook.md
 *
 *   # Exploration + Strukturierung
 *   npx tsx e2e/run-live-persona.ts --playbook agent-docs/e2e-human-playbook.md --stop-after strukturierung
 *
 *   # Alle Phasen bis Validierung
 *   npx tsx e2e/run-live-persona.ts --playbook agent-docs/e2e-human-playbook.md --stop-after validierung --max-turns 60
 *
 * Requires:
 *   - Running backend (BACKEND_URL, default http://127.0.0.1:8000)
 *   - OpenAI API key (OPENAI_API_KEY or LLM_API_KEY env var)
 */

import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { SessionClient } from './framework/ws-client.js';
import type { TurnResponse, ArtifactSnapshots } from './framework/types.js';
import OpenAI from 'openai';

const __dirname = fileURLToPath(new URL('.', import.meta.url));

const PHASE_ORDER = ['exploration', 'strukturierung', 'spezifikation', 'validierung'] as const;
type Phase = (typeof PHASE_ORDER)[number];

// ---------------------------------------------------------------------------
// Config
// ---------------------------------------------------------------------------

interface Config {
  playbookPath: string;
  backendUrl: string;
  maxTurns: number;
  personaModel: string;
  outputDir: string;
  stopAfter: Phase;
}

function parseArgs(): Config {
  const args = process.argv.slice(2);
  const config: Config = {
    playbookPath: '',
    backendUrl: process.env['BACKEND_URL'] ?? 'http://127.0.0.1:8000',
    maxTurns: 30,
    personaModel: process.env['PERSONA_MODEL'] ?? 'gpt-5.4',
    outputDir: join(__dirname, 'reports'),
    stopAfter: 'exploration',
  };

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--playbook' && args[i + 1]) config.playbookPath = args[++i];
    else if (args[i] === '--max-turns' && args[i + 1]) config.maxTurns = parseInt(args[++i], 10);
    else if (args[i] === '--model' && args[i + 1]) config.personaModel = args[++i];
    else if (args[i] === '--output' && args[i + 1]) config.outputDir = args[++i];
    else if (args[i] === '--stop-after' && args[i + 1]) {
      const phase = args[++i] as Phase;
      if (!PHASE_ORDER.includes(phase)) {
        console.error(`Ungültige Phase: ${phase}. Erlaubt: ${PHASE_ORDER.join(', ')}`);
        process.exit(1);
      }
      config.stopAfter = phase;
    }
  }

  if (!config.playbookPath) {
    console.error('Usage: npx tsx e2e/run-live-persona.ts --playbook <path> [--stop-after exploration|strukturierung|spezifikation|validierung] [--max-turns N]');
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

DEINE AUFGABE: Du bist die Person die im Playbook beschrieben ist. Du kennst deinen Arbeitsprozess genau, aber vieles davon ist dir nicht explizit bewusst — du hast ein tiefes, aber eher implizites Wissen. Du machst das jeden Tag, es ist Routine, du denkst nicht in Schritten und Feldern sondern in "ich mach halt immer so".

GESPRÄCHSVERHALTEN:
- Gib auf eine offene Frage erstmal den groben Überblick (3-4 Sätze), nicht alle Details sofort
- Details kommen erst wenn gezielt nachgefragt wird — Feldnamen, exakte Reihenfolgen, Sonderfälle
- Manche Dinge fallen dir erst ein wenn der Kontext stimmt ("Ach ja, und dann gibt's noch...")
- Du darfst gelegentlich kurz nachdenken ("Hmm, Moment...", "Da muss ich überlegen...")
- Häufiges (30x/Tag) beschreibst du flüssig und sicher. Seltenes (1x/Monat) eher knapp und unsicher
- Lies das Playbook-Kapitel "Gesprächsverhalten" genau — es beschreibt dein Verhalten im Detail

REGELN:
- Antworte als die Persona, nicht als KI-Assistent
- Sprich so wie die Persona spricht (siehe Charakter/typische Formulierungen im Playbook)
- Wenn nach etwas gefragt wird das NICHT im Playbook steht: sag "Das weiß ich nicht" oder "Da müssten Sie unsere IT fragen". Erfinde KEINE Prozessschritte, Systeme oder Regeln!
- Wenn gefragt wird ob alles passt: bestätige knapp
- Antworte auf Deutsch
- Halte dich kurz — Sachbearbeiter reden nicht in Absätzen

PLAYBOOK (dein vollständiges Prozesswissen):

${playbook}`;
  }

  async respond(question: string): Promise<string> {
    this.dialog.push({ role: 'user', content: question });

    const response = await this.client.chat.completions.create({
      model: this.model,
      temperature: 0.7,
      max_completion_tokens: 500,
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
  phase: string;
  mode: string;
  explorer_question: string;
  persona_response: string;
  phasenstatus: string;
  flags: string[];
  slots_filled: number;
  slots_total: number;
  response_time_ms: number;
}

interface PhaseResult {
  phase: string;
  turns: number;
  completed: boolean;
  artifacts: ArtifactSnapshots | null;
}

async function run(config: Config): Promise<void> {
  const playbook = await readFile(config.playbookPath, 'utf-8');
  const playbookName = config.playbookPath.split(/[/\\]/).pop() ?? 'unknown';

  const personaMatch = playbook.match(/\*\*Persona:\*\*\s*(.+)/);
  const personaName = personaMatch ? personaMatch[1].trim() : 'Unbekannt';

  const apiKey = process.env['OPENAI_API_KEY'] ?? process.env['LLM_API_KEY'] ?? '';
  if (!apiKey) {
    console.error('Kein API-Key gefunden. Setze OPENAI_API_KEY oder LLM_API_KEY.');
    process.exit(1);
  }

  const stopIdx = PHASE_ORDER.indexOf(config.stopAfter);
  const targetPhases = PHASE_ORDER.slice(0, stopIdx + 1);

  console.log(`Live-Persona-Runner — Digitalisierungsfabrik`);
  console.log(`Playbook:    ${playbookName}`);
  console.log(`Persona:     ${personaName}`);
  console.log(`Model:       ${config.personaModel}`);
  console.log(`Backend:     ${config.backendUrl}`);
  console.log(`Phasen:      ${targetPhases.join(' → ')}`);
  console.log(`Max Turns:   ${config.maxTurns}\n`);

  const persona = new PersonaLLM(apiKey, config.personaModel, playbook);
  const client = new SessionClient(config.backendUrl, 180_000);

  const projectId = await client.createProject(`live-persona-${Date.now()}`);
  const greeting = await client.connect(projectId);

  console.log(`Projekt erstellt: ${projectId}`);
  console.log(`Begrüßung: ${greeting.message.substring(0, 100)}...\n`);

  const allTurns: TurnLog[] = [];
  const phaseResults: PhaseResult[] = [];
  let currentQuestion = greeting.message;
  let turnNr = 0;
  let lastPhase = '';

  // ── Main loop — runs until target phase completes or max turns ──

  while (turnNr < config.maxTurns) {
    const personaAnswer = await persona.respond(currentQuestion);
    turnNr++;

    const response: TurnResponse = await client.sendMessage(projectId, personaAnswer);

    const phase = response.state.aktive_phase || 'unknown';
    const mode = response.state.aktiver_modus || 'unknown';

    const log: TurnLog = {
      turn: turnNr,
      phase,
      mode,
      explorer_question: currentQuestion,
      persona_response: personaAnswer,
      phasenstatus: response.state.phasenstatus,
      flags: response.state.flags,
      slots_filled: response.state.befuellte_slots,
      slots_total: response.state.bekannte_slots,
      response_time_ms: response.response_time_ms,
    };
    allTurns.push(log);

    // Phase change detection
    if (phase !== lastPhase && lastPhase !== '') {
      console.log(`\n══════ Phasenwechsel: ${lastPhase} → ${phase} ══════\n`);
    }
    lastPhase = phase;

    console.log(`--- Turn ${turnNr} [${phase}/${mode}] ---`);
    console.log(`System:  ${currentQuestion.substring(0, 120)}${currentQuestion.length > 120 ? '...' : ''}`);
    console.log(`Persona: ${personaAnswer.substring(0, 120)}${personaAnswer.length > 120 ? '...' : ''}`);
    console.log(`Status: ${response.state.phasenstatus} | Slots: ${response.state.befuellte_slots}/${response.state.bekannte_slots} | ${response.response_time_ms}ms`);
    console.log('');

    // ── Phase complete handling ──

    const isPhaseComplete = response.state.flags.includes('phase_complete')
      || response.state.phasenstatus === 'phase_complete';

    if (isPhaseComplete) {
      const completedPhase = phase === 'moderator' ? lastPhase : phase;

      // Snapshot artifacts at phase boundary
      const artifacts = await client.getArtifacts(projectId);
      const phaseTurns = allTurns.filter(t => t.phase === completedPhase || t.phase === phase).length;
      phaseResults.push({ phase: completedPhase, turns: phaseTurns, completed: true, artifacts });

      console.log(`=== ${completedPhase} complete nach ${phaseTurns} Turns ===\n`);

      // Check if we've reached our target phase
      const completedIdx = PHASE_ORDER.indexOf(completedPhase as Phase);
      const targetIdx = PHASE_ORDER.indexOf(config.stopAfter);

      if (completedIdx >= targetIdx) {
        console.log(`Zielphase '${config.stopAfter}' erreicht — Test beendet.\n`);
        break;
      }

      // Continue to next phase — moderator message is in response.message
      // The persona needs to confirm the phase transition
      console.log(`Moderator fragt nach Phasenwechsel, Persona bestätigt...\n`);
      currentQuestion = response.message;

      // Loop through moderator interaction until phase actually advances
      const prevPhase = phase;
      let moderatorTurns = 0;
      while (moderatorTurns < 5 && turnNr < config.maxTurns) {
        const confirmAnswer = await persona.respond(currentQuestion);
        turnNr++;

        const confirmResponse = await client.sendMessage(projectId, confirmAnswer);
        const confirmPhase = confirmResponse.state.aktive_phase || 'unknown';
        const confirmMode = confirmResponse.state.aktiver_modus || 'unknown';

        allTurns.push({
          turn: turnNr,
          phase: confirmPhase,
          mode: confirmMode,
          explorer_question: currentQuestion,
          persona_response: confirmAnswer,
          phasenstatus: confirmResponse.state.phasenstatus,
          flags: confirmResponse.state.flags,
          slots_filled: confirmResponse.state.befuellte_slots,
          slots_total: confirmResponse.state.bekannte_slots,
          response_time_ms: confirmResponse.response_time_ms,
        });

        console.log(`--- Turn ${turnNr} [${confirmPhase}/${confirmMode}] (Moderator-Übergang) ---`);
        console.log(`Persona: ${confirmAnswer.substring(0, 120)}${confirmAnswer.length > 120 ? '...' : ''}`);
        console.log(`Status: ${confirmResponse.state.phasenstatus} | ${confirmResponse.response_time_ms}ms\n`);

        currentQuestion = confirmResponse.message;
        moderatorTurns++;

        // Phase has advanced — break out of moderator loop
        if (confirmPhase !== prevPhase && confirmMode !== 'moderator') {
          lastPhase = confirmPhase;
          break;
        }
      }
      continue;
    }

    currentQuestion = response.message;
  }

  if (turnNr >= config.maxTurns) {
    console.log(`=== Max Turns (${config.maxTurns}) erreicht ===\n`);
  }

  // ── Fetch final artifacts and generate report ──

  const finalArtifacts = await client.getArtifacts(projectId);
  client.disconnect();

  await mkdir(config.outputDir, { recursive: true });
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').substring(0, 19);
  const baseName = `live-persona-${playbookName.replace('.md', '')}-${timestamp}`;
  const reportPath = join(config.outputDir, `${baseName}.md`);
  const jsonPath = join(config.outputDir, `${baseName}.json`);

  const completedPhases = phaseResults.filter(p => p.completed).map(p => p.phase);

  const report = generateReport(personaName, playbookName, config, allTurns, finalArtifacts, phaseResults);

  console.log('Generiere qualitative Analyse...');
  const analysis = await generateAnalysis(apiKey, playbook, finalArtifacts, allTurns, completedPhases);

  const fullReport = report + '\n\n---\n\n' + analysis;
  await writeFile(reportPath, fullReport, 'utf-8');
  await writeFile(jsonPath, JSON.stringify({
    turns: allTurns, artifacts: finalArtifacts, phaseResults,
    config: { ...config, apiKey: '***' },
  }, null, 2), 'utf-8');

  console.log(`\nReport: ${reportPath}`);
  console.log(`Rohdaten: ${jsonPath}`);
}

// ---------------------------------------------------------------------------
// Analysis (LLM-gestützt, phasenübergreifend)
// ---------------------------------------------------------------------------

async function generateAnalysis(
  apiKey: string, playbook: string,
  artifacts: ArtifactSnapshots, turns: TurnLog[], completedPhases: string[],
): Promise<string> {
  const client = new OpenAI({ apiKey });
  const analysisModel = 'gpt-5.4';

  // Build artifact dumps per phase
  const artifactSections: string[] = [];

  // Exploration slots
  const explorationSlots = extractExplorationSlots(artifacts);
  if (Object.keys(explorationSlots).length > 0) {
    artifactSections.push('## EXPLORATION — Slot-Inhalte\n\n' +
      Object.entries(explorationSlots)
        .map(([id, content]) => `### ${id}\n${content}`)
        .join('\n\n'));
  }

  // Structure artifact
  const structureData = extractStructureData(artifacts);
  if (structureData) {
    artifactSections.push('## STRUKTURIERUNG — Strukturartefakt\n\n' + structureData);
  }

  const dialogSummary = turns
    .map(t => `Turn ${t.turn} [${t.phase}/${t.mode}] ${t.phasenstatus}: System: "${t.explorer_question.substring(0, 120)}" → Persona: "${t.persona_response.substring(0, 120)}"`)
    .join('\n');

  const phasenInfo = completedPhases.length > 0
    ? `Abgeschlossene Phasen: ${completedPhases.join(', ')}`
    : 'Keine Phase vollständig abgeschlossen';

  const systemPrompt = buildAnalysisPrompt(completedPhases);

  const response = await client.chat.completions.create({
    model: analysisModel,
    temperature: 0.3,
    max_completion_tokens: 12000,
    messages: [
      { role: 'system', content: systemPrompt },
      {
        role: 'user',
        content: `PLAYBOOK (Ground Truth):\n\n${playbook}\n\n---\n\nARTEFAKT-ROHDATEN (${phasenInfo}):\n\n${artifactSections.join('\n\n---\n\n')}\n\n---\n\nDIALOG-ZUSAMMENFASSUNG (${turns.length} Turns):\n\n${dialogSummary}`,
      },
    ],
  });

  const analysisContent = response.choices[0]?.message?.content;
  const finishReason = response.choices[0]?.finish_reason;
  console.log(`Analyse: ${analysisContent ? analysisContent.length + ' Zeichen' : 'LEER'}, finish_reason: ${finishReason}`);
  if (!analysisContent) {
    console.error('Analyse-Response:', JSON.stringify(response.choices[0]?.message).substring(0, 500));
  }
  return analysisContent ?? '(Analyse konnte nicht generiert werden)';
}

function buildAnalysisPrompt(completedPhases: string[]): string {
  const hasExploration = completedPhases.includes('exploration');
  const hasStrukturierung = completedPhases.includes('strukturierung');

  let prompt = `Du bist ein erfahrener Qualitätsanalyst für RPA-Prozesserhebungen. Du bewertest das Ergebnis eines E2E-Tests der Digitalisierungsfabrik.

ABGESCHLOSSENE PHASEN: ${completedPhases.join(', ') || 'keine'}

BEWERTUNGSSKALA (pro Phase):
- **BESTANDEN** — Artefakt erfüllt die Phase-Anforderungen. Fehlende Details akzeptabel.
- **BESTANDEN MIT LÜCKEN** — Im Kern ok, aber wichtige strukturelle Elemente fehlen.
- **NICHT BESTANDEN** — Artefakt unbrauchbar für die Folgephase.

SORGFALTSPFLICHT:
- Prüfe JEDE Aussage gegen die ARTEFAKT-ROHDATEN (nicht den Dialog).
- Behaupte nie dass etwas fehlt/existiert ohne es im Artefakt geprüft zu haben.

ANTI-SCHÖNFÄRBEREI:
- Sei skeptisch. Finde Lücken. Unterscheide: (a) Detail für Folgephasen vs. (b) strukturelles Element das den Prozess unvollständig macht.

HALLUZINATIONS-CHECK:
- Prüfe ob Konzepte im Artefakt stehen die NICHT im Playbook vorkommen. Wenn ja: flaggen.

WAS IST EINE ENTSCHEIDUNG:
Eine Entscheidung = Prozessablauf verzweigt sich. Dropdown/Auswahl (Kostenstelle, MwSt-Satz) ist KEINE Entscheidung wenn danach derselbe Schritt kommt.

PASSIVE SYSTEME:
Programme die sich automatisch öffnen (PDF-Viewer, Dateidialog) sind KEINE beteiligten Systeme.`;

  // Phase-specific instructions
  if (hasExploration) {
    prompt += `

## Bewertung: EXPLORATION
Die Exploration muss den Prozess im Überblick nachvollziehbar machen. Prüfe die 6 Slots (prozessausloeser, prozessziel, prozessbeschreibung, entscheidungen_und_schleifen, beteiligte_systeme, variablen_und_daten) gegen das Playbook-Zielartefakt.`;
  }

  if (hasStrukturierung) {
    prompt += `

## Bewertung: STRUKTURIERUNG
Das Strukturartefakt muss den Prozess als logische Schrittfolge modellieren. Prüfe:
- **Vollständigkeit:** Jeder substanzielle Prozessschritt aus der Exploration findet sich als Strukturschritt wieder.
- **Entscheidungen:** Geschäftliche Varianten (z.B. Gutschrift) als typ "entscheidung" modelliert, nicht als "ausnahme". Bedingung als Frage, Nachfolger klar zugeordnet.
- **Graph-Konsistenz:** Alle nachfolger/konvergenz/schleifenkoerper verweisen auf existierende Schritte. Ein Start, mindestens ein Ende.
- **Beschreibungstiefe:** Spezifikationsreif — Wer, Wo, Was, Welche Daten, Was kann schiefgehen.
- **Spannungsfelder:** Medienbrüche und analoge Abhängigkeiten erkannt und dokumentiert.
- Vergleiche gegen das Strukturartefakt-Ziel im Playbook (TEIL B).`;
  }

  if (hasExploration && hasStrukturierung) {
    prompt += `

## Phasenübergreifende Konsistenz
- Geht Information aus der Exploration im Strukturartefakt verloren?
- Wurden Explorationsdetails korrekt in Strukturschritte überführt?
- Stimmen die Systeme/Akteure/Entscheidungen zwischen beiden Artefakten überein?`;
  }

  prompt += `

## Output-Format

Schreibe deine Analyse EXAKT in diesem Format auf Deutsch:

# Qualitative Analyse

## Gesamturteil

**Ergebnis: BESTANDEN / BESTANDEN MIT LÜCKEN / NICHT BESTANDEN**

Ein Absatz Begründung.`;

  if (hasExploration) {
    prompt += `

## Exploration: Soll/Ist-Vergleich

Für JEDEN der 6 Slots:

**{slot_id}**
- Soll: {Zusammenfassung der Playbook-Vorgaben}
- Ist: {Was tatsächlich im Artefakt steht}
- Fehlend / Halluziniert: {oder "nichts"}
- Bewertung: VOLLSTÄNDIG / LÜCKENHAFT / UNZUREICHEND`;
  }

  if (hasStrukturierung) {
    prompt += `

## Strukturierung: Soll/Ist-Vergleich

Für JEDEN Strukturschritt im Soll-Artefakt:
- Existiert er im Ist? Unter welcher ID?
- Beschreibungstiefe: ausreichend für Spezifikation?
- Fehlende Schritte / Halluzinierte Schritte

**Graph-Analyse:**
- Referenzielle Integrität (alle Verweise gültig?)
- Entscheidungen korrekt typisiert?
- Konvergenz/Schleifen korrekt?

**Spannungsfelder:**
- Welche erkannt? Welche fehlen?`;
  }

  prompt += `

## Fehlende Inhalte
Nummerierte Liste aller Lücken mit Schweregrad (strukturell / Detail).

## Halluzinationen
Liste oder "Keine gefunden."

## Dialogführung
Kurz: Gesprächsführung, Effizienz, Persona-Verhalten realistisch?

## Fazit

| Phase | Aspekt | Bewertung |
|-------|--------|-----------|
${hasExploration ? '| Exploration | Prozess-Grundverständnis | ... |\n| Exploration | Entscheidungslogik | ... |\n| Exploration | Systeme | ... |\n| Exploration | Sonderfälle | ... |' : ''}
${hasStrukturierung ? '| Strukturierung | Schrittabdeckung | ... |\n| Strukturierung | Beschreibungstiefe | ... |\n| Strukturierung | Graph-Konsistenz | ... |\n| Strukturierung | Entscheidungsmodellierung | ... |' : ''}
| Gesamt | Halluzinationen | ... |

**Endurteil: BESTANDEN / BESTANDEN MIT LÜCKEN / NICHT BESTANDEN**`;

  return prompt;
}

// ---------------------------------------------------------------------------
// Report generation
// ---------------------------------------------------------------------------

function generateReport(
  personaName: string,
  playbookName: string,
  config: Config,
  turns: TurnLog[],
  artifacts: ArtifactSnapshots,
  phaseResults: PhaseResult[],
): string {
  const totalTime = turns.reduce((sum, t) => sum + t.response_time_ms, 0);
  const personaShort = personaName.split(',')[0];

  const explorationSlots = extractExplorationSlots(artifacts);
  const slotIds = ['prozessausloeser', 'prozessziel', 'prozessbeschreibung',
    'entscheidungen_und_schleifen', 'beteiligte_systeme', 'variablen_und_daten'];
  const filledSlots = slotIds.filter(id => explorationSlots[id]?.trim()).length;

  const avgPersonaLen = turns.length > 0
    ? Math.round(turns.reduce((s, t) => s + t.persona_response.length, 0) / turns.length)
    : 0;

  const completedPhases = phaseResults.filter(p => p.completed).map(p => p.phase);

  const lines: string[] = [];

  // ── Eckdaten ──
  lines.push(`# Live-Persona-Test: ${personaName}`, '');
  lines.push('## Eckdaten', '');
  lines.push(`| Parameter | Wert |`);
  lines.push(`|-----------|------|`);
  lines.push(`| Playbook | \`${playbookName}\` |`);
  lines.push(`| Persona-Model | ${config.personaModel} |`);
  lines.push(`| Stop-After | ${config.stopAfter} |`);
  lines.push(`| Max Turns | ${config.maxTurns} |`);
  lines.push(`| Tatsächliche Turns | ${turns.length} |`);
  lines.push(`| Abgeschlossene Phasen | ${completedPhases.join(', ') || 'keine'} |`);
  lines.push(`| Backend-Dauer | ${(totalTime / 1000).toFixed(0)}s |`);
  lines.push(`| Exploration: Slots befüllt | ${filledSlots}/${slotIds.length} |`);
  lines.push(`| Mittlere Antwortlänge Persona | ${avgPersonaLen} Zeichen |`);
  lines.push('');

  // ── Phase summary ──
  if (phaseResults.length > 0) {
    lines.push('## Phasen-Übersicht', '');
    lines.push('| Phase | Turns | Abgeschlossen |');
    lines.push('|-------|-------|---------------|');
    for (const pr of phaseResults) {
      lines.push(`| ${pr.phase} | ${pr.turns} | ${pr.completed ? 'Ja' : 'Nein'} |`);
    }
    lines.push('');
  }

  // ── Dialog ──
  lines.push('---', '', '## Vollständiger Dialog', '');

  for (const t of turns) {
    lines.push(`### Turn ${t.turn} — \`${t.phase}/${t.mode}\` · \`${t.phasenstatus}\` · ${t.slots_filled}/${t.slots_total} Slots · ${(t.response_time_ms / 1000).toFixed(1)}s`);
    lines.push('');
    lines.push(`**System:**`);
    lines.push(`> ${t.explorer_question.replace(/\n/g, '\n> ')}`);
    lines.push('');
    lines.push(`**${personaShort}:**`);
    lines.push(`> ${t.persona_response.replace(/\n/g, '\n> ')}`);
    lines.push('');
  }

  // ── Exploration artifact ──
  lines.push('---', '', '## Artefakt: Exploration', '');
  for (const slotId of slotIds) {
    const actual = explorationSlots[slotId];
    lines.push(`### ${slotId}`, '');
    lines.push(actual?.trim() ? `> ${actual.replace(/\n/g, '\n> ')}` : '> (leer)');
    lines.push('');
  }

  // ── Structure artifact ──
  const structureData = extractStructureData(artifacts);
  if (structureData) {
    lines.push('---', '', '## Artefakt: Strukturierung', '');
    lines.push(structureData, '');
  }

  // ── Raw artifacts ──
  lines.push('---', '', '<details><summary>Artefakte (Rohdaten JSON)</summary>', '',
    '```json', JSON.stringify(artifacts, null, 2), '```', '', '</details>');

  return lines.join('\n');
}

// ---------------------------------------------------------------------------
// Artifact extraction helpers
// ---------------------------------------------------------------------------

function extractExplorationSlots(artifacts: ArtifactSnapshots): Record<string, string> {
  const result: Record<string, string> = {};
  const exploration = artifacts.exploration;
  if (!exploration) return result;
  const slots = exploration['slots'] as Record<string, Record<string, unknown>> | undefined;
  if (!slots) return result;

  for (const [slotId, slot] of Object.entries(slots)) {
    result[slotId] = (slot['inhalt'] as string) ?? '';
  }
  return result;
}

function extractStructureData(artifacts: ArtifactSnapshots): string | null {
  const struktur = artifacts.struktur;
  if (!struktur) return null;

  const schritte = struktur['schritte'] as Record<string, Record<string, unknown>> | undefined;
  if (!schritte || Object.keys(schritte).length === 0) return null;

  const zusammenfassung = (struktur['prozesszusammenfassung'] as string) ?? '';

  const lines: string[] = [];
  if (zusammenfassung) {
    lines.push(`**prozesszusammenfassung:** ${zusammenfassung}`, '');
  }

  // Sort by reihenfolge
  const sorted = Object.entries(schritte)
    .sort(([, a], [, b]) => ((a['reihenfolge'] as number) ?? 99) - ((b['reihenfolge'] as number) ?? 99));

  for (const [id, schritt] of sorted) {
    const titel = schritt['titel'] ?? '';
    const typ = schritt['typ'] ?? '';
    const reihenfolge = schritt['reihenfolge'] ?? '';
    const nachfolger = schritt['nachfolger'] as string[] ?? [];
    const beschreibung = schritt['beschreibung'] ?? '';
    const completeness = schritt['completeness_status'] ?? '';
    const bedingung = schritt['bedingung'] ?? '';
    const konvergenz = schritt['konvergenz'] ?? '';
    const spannungsfeld = schritt['spannungsfeld'] ?? '';

    let header = `**${id}** — ${titel} [${typ}, reihenfolge ${reihenfolge}, → ${JSON.stringify(nachfolger)}`;
    if (bedingung) header += `, bedingung: "${bedingung}"`;
    if (konvergenz) header += `, konvergenz: ${konvergenz}`;
    header += `, ${completeness}]`;

    lines.push(header);
    lines.push(`"${beschreibung}"`);
    if (spannungsfeld) lines.push(`spannungsfeld: "${spannungsfeld}"`);
    lines.push('');
  }

  return lines.join('\n');
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

const config = parseArgs();
run(config).catch((err) => {
  console.error('Fatal:', err instanceof Error ? err.message : err);
  process.exit(1);
});
