<p align="center">
  <img src="https://em-content.zobj.net/source/apple/391/rock_1faa8.png" width="120" />
</p>

<h1 align="center">jaskiniowiec</h1>

<p align="center">
  <strong>Polish-first agent prompts, shorter answers, same technical substance</strong>
</p>

<p align="center">
  <a href="#what-it-does">What it does</a> •
  <a href="#install">Install</a> •
  <a href="#usage">Usage</a> •
  <a href="#levels">Levels</a> •
  <a href="#included-commands-and-skills">Skills</a> •
  <a href="#upstream-and-attribution">Attribution</a>
</p>

---

jaskiniowiec is a Polish-first fork of [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman). It keeps the core idea, make agent output shorter without losing technical accuracy, while changing the public identity, commands, and day-to-day usage around Polish workflows.

The README stays in English so it is easy to share, but the fork is meant to feel natural for Polish-speaking users.

This project is inspired by caveman and informed by research on benchmarking and concise model behavior, including Kim, Y., Russell, J., Karpinska, M., Iyyer, M. (2025), [One ruler to measure them all: Benchmarking models](https://www.semanticscholar.org/paper/One-ruler-to-measure-them-all%3A-Benchmarking-models-Kim-Russell/244c0678b20f6050b4691287fe9b2d32d409e616). That research helps motivate the focus on short, disciplined outputs, but this README does not claim findings from it beyond that general inspiration.

## What it does

jaskiniowiec is a skill and plugin set for Claude Code, Codex, Gemini CLI, and other supported agents. It tells the model to keep the answer brief, keep the technical facts, and drop the fluff.

### Example

**Normal**

> The bug is probably caused by a new object being created on every render. React sees a different reference, so the component keeps re-rendering. Wrap the value in `useMemo`.

**jaskiniowiec**

> New object each render. New ref, new render. Use `useMemo`.

## Install

Pick your agent, then install the `jaskiniowiec` skill once.

| Agent | Install |
|-------|---------|
| **Claude Code** | `claude plugin marketplace add mikolaj92/jaskiniowiec && claude plugin install jaskiniowiec@jaskiniowiec` |
| **Codex** | Clone the repo, open Codex in the repo folder, run `/plugins`, search `jaskiniowiec`, install it |
| **Gemini CLI** | `gemini extensions install https://github.com/mikolaj92/jaskiniowiec` |
| **Cursor** | `npx skills add mikolaj92/jaskiniowiec -a cursor` |
| **Windsurf** | `npx skills add mikolaj92/jaskiniowiec -a windsurf` |
| **Copilot** | `npx skills add mikolaj92/jaskiniowiec -a github-copilot` |
| **Cline** | `npx skills add mikolaj92/jaskiniowiec -a cline` |
| **Other supported agents** | `npx skills add mikolaj92/jaskiniowiec` |

If you fork this repository, replace `mikolaj92/jaskiniowiec` with your fork path.

## Usage

Trigger it with:
- `/jaskiniowiec`
- `talk like jaskiniowiec`
- `be brief`
- `less fluff, same answer`

Stop it with:
- `stop jaskiniowiec`
- `normal mode`

## Levels

| Level | Trigger | Behavior |
|-------|---------|----------|
| **Lite** | `/jaskiniowiec lite` | Keep grammar, remove filler |
| **Full** | `/jaskiniowiec full` | Default short mode, compact and direct |
| **Ultra** | `/jaskiniowiec ultra` | Maximum compression, telegraphic style |

## Included commands and skills

### `jaskiniowiec-commit`

Creates short commit messages. Useful when you want the reason, not a paragraph.

### `jaskiniowiec-review`

Writes short review comments with the problem, the line, and the fix.

### `jaskiniowiec-help`

Shows a quick reference for levels, triggers, and supported commands.

### `jaskiniowiec-compress`

Compresses memory or prompt files so the agent reads less while keeping the useful parts intact.

Example:

```bash
/jaskiniowiec-compress CLAUDE.md
```

## Notes on behavior

- Short does not mean vague. Keep technical terms exact.
- Remove filler, hedging, and polite padding when brevity helps.
- Preserve code, commands, paths, and identifiers.
- Use normal writing for security issues, irreversible actions, and anything that needs clarity.

## Upstream and attribution

jaskiniowiec is a fork of JuliusBrussee/caveman. The upstream project deserves clear credit for the original idea, structure, and skill set.

This fork changes the public identity and Polish-first framing, but it does not erase upstream authorship.

The research link above is cited as inspiration for concise model behavior and benchmarking context, not as a claim about this fork's measured performance.

## License

MIT. See `LICENSE` for the full text.

If you use this fork, please keep the upstream attribution intact.
