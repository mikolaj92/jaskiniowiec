#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const os = require('os');
const { getDefaultMode, safeWriteFlag } = require('./jaskiniowiec-config');

const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
const flagPath = path.join(claudeDir, '.jaskiniowiec-active');
const settingsPath = path.join(claudeDir, 'settings.json');

const mode = getDefaultMode();

if (mode === 'off') {
  try { fs.unlinkSync(flagPath); } catch (e) {}
  process.stdout.write('OK');
  process.exit(0);
}

safeWriteFlag(flagPath, mode);

const INDEPENDENT_MODES = new Set(['commit', 'review', 'compress']);
if (INDEPENDENT_MODES.has(mode)) {
  process.stdout.write('JASKINIOWIEC MODE ACTIVE — poziom: ' + mode + '. Zachowanie definiuje skill /jaskiniowiec-' + mode + '.');
  process.exit(0);
}

let skillContent = '';
try {
  skillContent = fs.readFileSync(
    path.join(__dirname, '..', 'skills', 'jaskiniowiec', 'SKILL.md'),
    'utf8'
  );
} catch (e) {
}

let output;

if (skillContent) {
  const body = skillContent.replace(/^---[\s\S]*?---\s*/, '');
  const filtered = body.split('\n').reduce((acc, line) => {
    const tableRowMatch = line.match(/^\|\s*\*\*(\S+?)\*\*\s*\|/);
    if (tableRowMatch) {
      if (tableRowMatch[1] === mode) {
        acc.push(line);
      }
      return acc;
    }

    const exampleMatch = line.match(/^- (\S+?):\s/);
    if (exampleMatch) {
      if (exampleMatch[1] === mode) {
        acc.push(line);
      }
      return acc;
    }

    acc.push(line);
    return acc;
  }, []);

  output = 'JASKINIOWIEC MODE ACTIVE — poziom: ' + mode + '\n\n' + filtered.join('\n');
} else {
  output =
    'JASKINIOWIEC MODE ACTIVE — poziom: ' + mode + '\n\n' +
    'Odpowiadaj zwięźle jak sprytny jaskiniowiec. Zachowaj całą treść techniczną. Zabij watę słowną.\n\n' +
    '## Trwałość\n\n' +
    'AKTYWNE W KAŻDEJ ODPOWIEDZI. Bez dryfu do rozwlekłości. Wyłącz tylko: "stop jaskiniowiec" / "normal mode".\n\n' +
    'Aktualny poziom: **' + mode + '**. Przełącz: `/jaskiniowiec lite|full|ultra`.\n\n' +
    '## Zasady\n\n' +
    'Wytnij filler, kurtuazję i hedging. Krótkie frazy OK. Terminy techniczne mają być dokładne. Kod bez zmian.\n\n' +
    'Wzorzec: `[rzecz] [akcja] [powód]. [następny krok].`\n\n' +
    '## Auto-Clarity\n\n' +
    'Wyłącz styl jaskiniowca dla ostrzeżeń bezpieczeństwa, operacji nieodwracalnych i sytuacji wymagających pełnej klarowności.\n\n' +
    '## Granice\n\n' +
    'Kod/commity/PR-y: normalnie. Poziom trwa do zmiany lub końca sesji.';
}

try {
  let hasStatusline = false;
  if (fs.existsSync(settingsPath)) {
    const settings = JSON.parse(fs.readFileSync(settingsPath, 'utf8'));
    if (settings.statusLine) {
      hasStatusline = true;
    }
  }

  if (!hasStatusline) {
    const scriptPath = path.join(__dirname, 'jaskiniowiec-statusline.sh');
    const command = `bash "${scriptPath}"`;
    const statusLineSnippet = '"statusLine": { "type": "command", "command": ' + JSON.stringify(command) + ' }';
    output += "\n\n" +
      "STATUSLINE SETUP NEEDED: Plugin jaskiniowiec ma badge statusline z aktywnym poziomem " +
      "(np. [JASKINIOWIEC], [JASKINIOWIEC:ULTRA]). Nie jest jeszcze skonfigurowany. " +
      "Dodaj do " + path.join(claudeDir, 'settings.json') + ": " +
      statusLineSnippet + " Zaproponuj użytkownikowi konfigurację przy pierwszej interakcji.";
  }
} catch (e) {
}

process.stdout.write(output);
