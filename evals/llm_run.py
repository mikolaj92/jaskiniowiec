"""
Run each prompt through Claude Code in three conditions and snapshot the
real LLM outputs:

  1. baseline      — no extra system prompt at all
  2. terse         — system prompt: "Answer concisely."
  3. terse+skill   — system prompt: "Answer concisely.\n\n{SKILL.md}"

The honest delta is (3) vs (2): how much does the SKILL itself add on top
of a plain "be terse" instruction? Comparing (3) vs (1) conflates the
skill with the generic terseness ask, which is what the previous version
of this harness did.

This is the source-of-truth generator. It calls a real LLM and produces
evals/snapshots/results.json. Run it locally when SKILL.md files change.
The CI-side `measure.py` only reads the snapshot and counts tokens.

Requires:
  - `claude` CLI on PATH (Claude Code), authenticated

Run: uv run python evals/llm_run.py

Environment:
  JASKINIOWIEC_EVAL_MODEL  optional --model flag value passed through to claude
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

EVALS = Path(__file__).parent
SKILLS = EVALS.parent / "skills"
PROMPTS = EVALS / "prompts" / "en.txt"
SNAPSHOT = EVALS / "snapshots" / "results.json"

TERSE_PREFIX = "Answer concisely."


def run_claude(prompt: str, system: str | None = None) -> str:
    cmd = ["claude", "-p"]
    if system:
        cmd += ["--system-prompt", system]
    if model := os.environ.get("JASKINIOWIEC_EVAL_MODEL"):
        cmd += ["--model", model]
    cmd.append(prompt)
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return out.stdout.strip()


def claude_version() -> str:
    try:
        out = subprocess.run(
            ["claude", "--version"], capture_output=True, text=True, check=True
        )
        return out.stdout.strip()
    except Exception:
        return "unknown"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate eval snapshots for baseline, terse, and jaskiniowiec skill arms."
    )
    parser.add_argument(
        "--check-prereqs",
        action="store_true",
        help="Only validate local prerequisites and exit.",
    )
    return parser.parse_args()



def ensure_claude_available() -> None:
    if shutil.which("claude") is None:
        print(
            "ERROR: Missing 'claude' CLI on PATH. Install and authenticate Claude Code before running eval snapshots.",
            file=sys.stderr,
        )
        raise SystemExit(1)



def main() -> None:
    args = parse_args()
    ensure_claude_available()

    if args.check_prereqs:
        print("OK: 'claude' CLI detected on PATH.")
        return

    prompts = [p.strip() for p in PROMPTS.read_text().splitlines() if p.strip()]
    skills = sorted(p.name for p in SKILLS.iterdir() if (p / "SKILL.md").exists())

    print(
        f"=== {len(prompts)} prompts × ({len(skills)} skills + 2 control arms) ===",
        flush=True,
    )

    snapshot: dict[str, object] = {
        "metadata": {
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "claude_cli_version": claude_version(),
            "model": os.environ.get("JASKINIOWIEC_EVAL_MODEL", "default"),
            "n_prompts": len(prompts),
            "terse_prefix": TERSE_PREFIX,
        },
        "prompts": prompts,
        "arms": {},
    }

    arms = snapshot["arms"]
    assert isinstance(arms, dict)

    print("baseline (no system prompt)", flush=True)
    arms["__baseline__"] = [run_claude(p) for p in prompts]

    print("terse (control: terse instruction only, no skill)", flush=True)
    arms["__terse__"] = [run_claude(p, system=TERSE_PREFIX) for p in prompts]

    for skill in skills:
        skill_md = (SKILLS / skill / "SKILL.md").read_text()
        system = f"{TERSE_PREFIX}\n\n{skill_md}"
        print(f"  {skill}", flush=True)
        arms[skill] = [run_claude(p, system=system) for p in prompts]

    SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2))
    print(f"\nWrote {SNAPSHOT}")


if __name__ == "__main__":
    main()
