# Jaskiniowiec Hooks

These hooks are **bundled with the jaskiniowiec plugin** and activate automatically when the plugin is installed. No manual setup required.

If you installed jaskiniowiec standalone (without the plugin), you can use `bash hooks/install.sh` to wire them into your `settings.json` manually.

## What's Included

### `jaskiniowiec-activate.js` — SessionStart hook

- Runs once when Claude Code starts
- Writes `full` to `~/.claude/.jaskiniowiec-active` (flag file)
- Emits jaskiniowiec rules as hidden SessionStart context
- Detects missing statusline config and emits setup nudge if needed

### `jaskiniowiec-mode-tracker.js` — UserPromptSubmit hook

- Fires on every user prompt and checks for `/jaskiniowiec` commands
- Writes the active mode to the flag file when a jaskiniowiec command is detected
- Supports: `full`, `lite`, `ultra`, `commit`, `review`, `compress`

### `jaskiniowiec-statusline.sh` — statusline badge script

- Read `~/.claude/.jaskiniowiec-active` and output a colored badge
- Show `[JASKINIOWIEC]`, `[JASKINIOWIEC:ULTRA]`, `[JASKINIOWIEC:COMMIT]`, etc.

## Statusline Badge

The statusline badge shows which jaskiniowiec mode is active directly in your Claude Code status bar.

**Plugin users:** If you do not already have a `statusLine` configured, Claude will detect that on your first session after install and offer to set it up for you. Accept and you're done.

If you already have a custom statusline, jaskiniowiec does not overwrite it. Add the badge snippet to your existing script instead.

**Standalone users:** `install.sh` wires the statusline automatically if you do not already have a custom statusline. If you do, the installer leaves it alone and prints a merge note.

**Manual setup:** If you need to configure it yourself, add this to `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "bash /path/to/jaskiniowiec-statusline.sh"
  }
}
```

Replace the path with the actual script location, for example `~/.claude/hooks/` for standalone installs or the plugin install directory for plugin installs.

**Custom statusline:** If you already have a statusline script, add this snippet to it:

```bash
jaskiniowiec_text=""
jaskiniowiec_flag="$HOME/.claude/.jaskiniowiec-active"
if [ -f "$jaskiniowiec_flag" ]; then
  jaskiniowiec_mode=$(cat "$jaskiniowiec_flag" 2>/dev/null)
  if [ "$jaskiniowiec_mode" = "full" ] || [ -z "$jaskiniowiec_mode" ]; then
    jaskiniowiec_text=$'\033[38;5;172m[JASKINIOWIEC]\033[0m'
  else
    jaskiniowiec_suffix=$(echo "$jaskiniowiec_mode" | tr '[:lower:]' '[:upper:]')
    jaskiniowiec_text=$'\033[38;5;172m[JASKINIOWIEC:'"${jaskiniowiec_suffix}"$']\033[0m'
  fi
fi
```

Badge examples:
- `/jaskiniowiec` → `[JASKINIOWIEC]`
- `/jaskiniowiec ultra` → `[JASKINIOWIEC:ULTRA]`
- `/jaskiniowiec-commit` → `[JASKINIOWIEC:COMMIT]`
- `/jaskiniowiec-review` → `[JASKINIOWIEC:REVIEW]`
- `/jaskiniowiec-compress` → `[JASKINIOWIEC:COMPRESS]`

## How It Works

```
SessionStart hook ──writes "full"──▶ ~/.claude/.jaskiniowiec-active ◀──writes mode── UserPromptSubmit hook
                                                    │
                                                 reads
                                                    ▼
                                           Statusline script
                                     [JASKINIOWIEC:ULTRA] │ ...
```

SessionStart stdout is injected as hidden system context. The statusline runs as a separate process. The flag file is the bridge between them.

## Uninstall

If installed via plugin, disable the plugin and the hooks deactivate automatically.

If installed via `install.sh`:

```bash
bash hooks/uninstall.sh
```

Or manually:
1. Remove `~/.claude/hooks/jaskiniowiec-activate.js`, `~/.claude/hooks/jaskiniowiec-mode-tracker.js`, and `~/.claude/hooks/jaskiniowiec-statusline.sh`
2. Remove the `SessionStart`, `UserPromptSubmit`, and `statusLine` entries from `~/.claude/settings.json`
3. Delete `~/.claude/.jaskiniowiec-active`
