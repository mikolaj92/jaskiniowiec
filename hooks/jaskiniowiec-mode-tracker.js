#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const os = require('os');
const { getDefaultMode, safeWriteFlag, readFlag } = require('./jaskiniowiec-config');

const claudeDir = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), '.claude');
const flagPath = path.join(claudeDir, '.jaskiniowiec-active');

let input = '';
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', () => {
  try {
    const data = JSON.parse(input);
    const prompt = (data.prompt || '').trim().toLowerCase();

    if (/\b(activate|enable|turn on|start|włącz|uruchom|mów jak)\b.*\b(jaskiniowiec)\b/i.test(prompt) ||
        /\bjaskiniowiec\b.*\b(tryb|mode|activate|enable|turn on|start|włącz|uruchom)\b/i.test(prompt)) {
      if (!/\b(stop|disable|turn off|deactivate|wyłącz)\b/i.test(prompt)) {
        const mode = getDefaultMode();
        if (mode !== 'off') {
          safeWriteFlag(flagPath, mode);
        }
      }
    }

    if (prompt.startsWith('/jaskiniowiec')) {
      const parts = prompt.split(/\s+/);
      const cmd = parts[0];
      const arg = parts[1] || '';

      let mode = null;

      if (cmd === '/jaskiniowiec-commit') {
        mode = 'commit';
      } else if (cmd === '/jaskiniowiec-review') {
        mode = 'review';
      } else if (cmd === '/jaskiniowiec-compress' || cmd === '/jaskiniowiec:jaskiniowiec-compress') {
        mode = 'compress';
      } else if (cmd === '/jaskiniowiec' || cmd === '/jaskiniowiec:jaskiniowiec') {
        if (arg === 'lite') mode = 'lite';
        else if (arg === 'ultra') mode = 'ultra';
        else mode = getDefaultMode();
      }

      if (mode && mode !== 'off') {
        safeWriteFlag(flagPath, mode);
      } else if (mode === 'off') {
        try { fs.unlinkSync(flagPath); } catch (e) {}
      }
    }

    if (/\b(stop|disable|deactivate|turn off|wyłącz)\b.*\bjaskiniowiec\b/i.test(prompt) ||
        /\bjaskiniowiec\b.*\b(stop|disable|deactivate|turn off|wyłącz)\b/i.test(prompt) ||
        /\bnormal mode\b/i.test(prompt) ||
        /\btryb normalny\b/i.test(prompt)) {
      try { fs.unlinkSync(flagPath); } catch (e) {}
    }

    const INDEPENDENT_MODES = new Set(['commit', 'review', 'compress']);
    const activeMode = readFlag(flagPath);
    if (activeMode && !INDEPENDENT_MODES.has(activeMode)) {
      process.stdout.write(JSON.stringify({
        hookSpecificOutput: {
          hookEventName: 'UserPromptSubmit',
          additionalContext: 'JASKINIOWIEC MODE ACTIVE (' + activeMode + '). ' +
            'Wytnij filler, kurtuazję i hedging. Krótkie frazy OK. ' +
            'Kod/commity/bezpieczeństwo: pisz normalnie.'
        }
      }));
    }
  } catch (e) {
  }
});
