#!/usr/bin/env python3
"""Local verification runner for jaskiniowiec install surfaces."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any, cast


ROOT = Path(__file__).resolve().parents[1]
SKILL_SOURCE = ROOT / "skills/jaskiniowiec/SKILL.md"
RULE_SOURCE = ROOT / "rules/jaskiniowiec-activate.md"
SKILL_COPY_PATHS = [
    ROOT / "jaskiniowiec/SKILL.md",
    ROOT / "plugins/jaskiniowiec/skills/jaskiniowiec/SKILL.md",
    ROOT / ".cursor/skills/jaskiniowiec/SKILL.md",
    ROOT / ".windsurf/skills/jaskiniowiec/SKILL.md",
]
RULE_COPY_PATHS = [
    ROOT / ".clinerules/jaskiniowiec.md",
    ROOT / ".github/copilot-instructions.md",
]
MANIFEST_PATHS = [
    ROOT / ".agents/plugins/marketplace.json",
    ROOT / ".claude-plugin/plugin.json",
    ROOT / ".claude-plugin/marketplace.json",
    ROOT / ".codex/hooks.json",
    ROOT / "gemini-extension.json",
    ROOT / "plugins/jaskiniowiec/.codex-plugin/plugin.json",
]
NODE_SYNTAX_PATHS = [
    "hooks/jaskiniowiec-config.js",
    "hooks/jaskiniowiec-activate.js",
    "hooks/jaskiniowiec-mode-tracker.js",
]
BASH_SYNTAX_PATHS = [
    "hooks/install.sh",
    "hooks/uninstall.sh",
    "hooks/jaskiniowiec-statusline.sh",
]
PLUGIN_ASSET_PATHS = [
    ROOT / "plugins/jaskiniowiec/assets/jaskiniowiec.svg",
    ROOT / "plugins/jaskiniowiec/assets/jaskiniowiec-small.svg",
    ROOT / "plugins/jaskiniowiec/skills/jaskiniowiec/assets/jaskiniowiec.svg",
    ROOT / "plugins/jaskiniowiec/skills/jaskiniowiec/assets/jaskiniowiec-small.svg",
]


class CheckFailure(RuntimeError):
    pass


def section(title: str) -> None:
    print(f"\n== {title} ==")


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def run(
    args: list[str],
    *,
    cwd: Path = ROOT,
    env: dict[str, str] | None = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    result = subprocess.run(
        args,
        cwd=cwd,
        env=merged_env,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        command = " ".join(args)
        raise CheckFailure(
            f"Command failed ({result.returncode}): {command}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def load_module(module_name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise CheckFailure(f"Could not load module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_copies_match(source: Path, copies: list[Path], label: str) -> None:
    source_text = source.read_text()
    for copy in copies:
        ensure(copy.read_text() == source_text, f"{label} copy mismatch: {copy}")



def verify_synced_files() -> None:
    section("Synced Files")
    assert_copies_match(SKILL_SOURCE, SKILL_COPY_PATHS, "Skill")
    assert_copies_match(RULE_SOURCE, RULE_COPY_PATHS, "Rule")

    with zipfile.ZipFile(ROOT / "jaskiniowiec.skill") as archive:
        ensure("jaskiniowiec/SKILL.md" in archive.namelist(), "jaskiniowiec.skill missing jaskiniowiec/SKILL.md")
        ensure(
            archive.read("jaskiniowiec/SKILL.md").decode("utf-8") == SKILL_SOURCE.read_text(),
            "jaskiniowiec.skill payload mismatch",
        )

    print("Synced copies and skill zip OK")


def verify_command_syntax(command: list[str], paths: list[str]) -> None:
    for path in paths:
        _ = run(command + [path])



def verify_manifests_and_syntax() -> None:
    section("Manifests And Syntax")

    for path in MANIFEST_PATHS:
        _ = read_json(path)

    verify_command_syntax(["node", "--check"], NODE_SYNTAX_PATHS)
    verify_command_syntax(["bash", "-n"], BASH_SYNTAX_PATHS)

    install_sh = (ROOT / "hooks/install.sh").read_text()
    uninstall_sh = (ROOT / "hooks/uninstall.sh").read_text()
    ensure("jaskiniowiec-config.js" in install_sh, "install.sh missing jaskiniowiec-config.js")
    ensure("jaskiniowiec-config.js" in uninstall_sh, "uninstall.sh missing jaskiniowiec-config.js")
    for asset_path in PLUGIN_ASSET_PATHS:
        ensure(asset_path.exists(), f"Missing asset: {asset_path}")

    print("JSON manifests and JS/bash syntax OK")


def load_compress_modules() -> tuple[Any, Any]:
    scripts_dir = ROOT / "jaskiniowiec-compress/scripts"
    detect = load_module("jaskiniowiec_compress_detect", scripts_dir / "detect.py")
    validate = load_module("jaskiniowiec_compress_validate", scripts_dir / "validate.py")
    return detect, validate


def verify_compress_fixtures() -> None:
    section("Compress Fixtures")
    detect, validate = load_compress_modules()

    fixtures: list[Path] = sorted((ROOT / "tests/jaskiniowiec-compress").glob("*.original.md"))
    ensure(bool(fixtures), "No compress fixtures found")

    for original in fixtures:
        compressed = original.with_name(original.name.replace(".original.md", ".md"))
        ensure(compressed.exists(), f"Missing compressed fixture for {original.name}")
        result = validate.validate(original, compressed)
        ensure(bool(result.is_valid), f"Fixture validation failed for {compressed.name}: {result.errors}")
        ensure(bool(detect.should_compress(compressed)), f"Fixture should be compressible: {compressed.name}")

    print(f"Validated {len(fixtures)} compress fixture pairs")


def verify_compress_cli() -> None:
    section("Compress CLI")

    skip_result = run(
        ["python3", "-m", "scripts", "../hooks/install.sh"],
        cwd=ROOT / "jaskiniowiec-compress",
        check=False,
    )
    ensure(skip_result.returncode == 0, "compress CLI skip path should exit 0")
    ensure("Wykryto: code" in skip_result.stdout, "compress CLI skip path missing detection output")
    ensure(
        "Pomijam: plik nie wygląda na naturalny język (kod/config)" in skip_result.stdout,
        "compress CLI skip path missing skip output",
    )

    missing_result = run(
        ["python3", "-m", "scripts", "../does-not-exist.md"],
        cwd=ROOT / "jaskiniowiec-compress",
        check=False,
    )
    ensure(missing_result.returncode == 1, "compress CLI missing-file path should exit 1")
    ensure("Nie znaleziono pliku" in missing_result.stdout, "compress CLI missing-file output mismatch")

    print("Compress CLI skip/error paths OK")


def verify_hook_install_flow() -> None:
    section("Claude Hook Flow")

    ensure(shutil.which("node") is not None, "node is required for hook verification")
    ensure(shutil.which("bash") is not None, "bash is required for hook verification")

    with tempfile.TemporaryDirectory(prefix="jaskiniowiec-verify-") as temp_root:
        temp_root_path = Path(temp_root)
        home = temp_root_path / "home"
        claude_dir = home / ".claude"
        claude_dir.mkdir(parents=True)

        existing_settings: dict[str, Any] = {
            "statusLine": {"type": "command", "command": "bash /tmp/existing-statusline.sh"},
            "hooks": {"Notification": [{"hooks": [{"type": "command", "command": "echo keep-me"}]}]},
        }
        (claude_dir / "settings.json").write_text(json.dumps(existing_settings, indent=2) + "\n")

        _ = run(["bash", "hooks/install.sh"], env={"HOME": str(home)})

        settings = cast(dict[str, Any], read_json(claude_dir / "settings.json"))
        hooks = cast(dict[str, Any], settings["hooks"])
        status_line = cast(dict[str, Any], settings["statusLine"])
        ensure(status_line["command"] == "bash /tmp/existing-statusline.sh", "install.sh clobbered existing statusLine")
        ensure("SessionStart" in hooks, "SessionStart hook missing after install")
        ensure("UserPromptSubmit" in hooks, "UserPromptSubmit hook missing after install")

        activate = run(
            ["node", "hooks/jaskiniowiec-activate.js"],
            env={"HOME": str(home)},
        )
        ensure("JASKINIOWIEC MODE ACTIVE" in activate.stdout, "activation output missing banner")
        ensure("STATUSLINE SETUP NEEDED" not in activate.stdout, "activation should stay quiet when custom statusline exists")
        ensure((claude_dir / ".jaskiniowiec-active").read_text() == "full", "activation flag should default to full")

        activate_custom = run(
            ["node", "hooks/jaskiniowiec-activate.js"],
            env={"HOME": str(home), "JASKINIOWIEC_DEFAULT_MODE": "ultra"},
        )
        ensure("JASKINIOWIEC MODE ACTIVE" in activate_custom.stdout, "activation with custom default missing banner")
        ensure((claude_dir / ".jaskiniowiec-active").read_text() == "ultra", "JASKINIOWIEC_DEFAULT_MODE=ultra should set flag to ultra")

        activate_off = run(
            ["node", "hooks/jaskiniowiec-activate.js"],
            env={"HOME": str(home), "JASKINIOWIEC_DEFAULT_MODE": "off"},
        )
        ensure("JASKINIOWIEC MODE ACTIVE" not in activate_off.stdout, "off mode should not emit banner")
        ensure(not (claude_dir / ".jaskiniowiec-active").exists(), "off mode should remove flag file")

        _ = subprocess.run(
            ["node", "hooks/jaskiniowiec-mode-tracker.js"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home), "JASKINIOWIEC_DEFAULT_MODE": "off"},
            text=True,
            input='{"prompt":"/jaskiniowiec"}',
            capture_output=True,
            check=True,
        )
        ensure(not (claude_dir / ".jaskiniowiec-active").exists(), "/jaskiniowiec with off default should not write flag")

        (claude_dir / ".jaskiniowiec-active").write_text("full")

        _ = run(
            ["node", "hooks/jaskiniowiec-mode-tracker.js"],
            env={"HOME": str(home)},
            check=True,
        )

        ultra_prompt = subprocess.run(
            ["node", "hooks/jaskiniowiec-mode-tracker.js"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home)},
            text=True,
            input='{"prompt":"/jaskiniowiec ultra"}',
            capture_output=True,
            check=True,
        )
        ensure(
            ultra_prompt.stdout == '{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"JASKINIOWIEC MODE ACTIVE (ultra). Wytnij filler, kurtuazję i hedging. Krótkie frazy OK. Kod/commity/bezpieczeństwo: pisz normalnie."}}',
            "mode tracker reinforcement output mismatch",
        )
        ensure((claude_dir / ".jaskiniowiec-active").read_text() == "ultra", "mode tracker did not record ultra")

        _ = subprocess.run(
            ["node", "hooks/jaskiniowiec-mode-tracker.js"],
            cwd=ROOT,
            env={**os.environ, "HOME": str(home)},
            text=True,
            input='{"prompt":"normal mode"}',
            capture_output=True,
            check=True,
        )
        ensure(not (claude_dir / ".jaskiniowiec-active").exists(), "normal mode should remove flag file")

        (claude_dir / ".jaskiniowiec-active").write_text("ultra")
        statusline = run(
            ["bash", "hooks/jaskiniowiec-statusline.sh"],
            env={"HOME": str(home)},
        )
        ensure("[JASKINIOWIEC:ULTRA]" in statusline.stdout, "statusline badge output mismatch")

        reinstall = run(["bash", "hooks/install.sh"], env={"HOME": str(home)})
        ensure("Nothing to do" in reinstall.stdout, "install.sh should be idempotent")

        _ = run(["bash", "hooks/uninstall.sh"], env={"HOME": str(home)})
        settings_after = read_json(claude_dir / "settings.json")
        ensure(settings_after == existing_settings, "uninstall.sh did not restore non-jaskiniowiec settings")
        ensure(not (claude_dir / ".jaskiniowiec-active").exists(), "uninstall.sh should remove flag file")

    with tempfile.TemporaryDirectory(prefix="jaskiniowiec-verify-fresh-") as temp_root:
        home = Path(temp_root) / "home"
        _ = run(["bash", "hooks/install.sh"], env={"HOME": str(home)})
        claude_dir = home / ".claude"
        settings = read_json(claude_dir / "settings.json")
        ensure("statusLine" in settings, "fresh install should configure statusline")
        activate = run(["node", "hooks/jaskiniowiec-activate.js"], env={"HOME": str(home)})
        ensure("STATUSLINE SETUP NEEDED" not in activate.stdout, "fresh install should not nudge for statusline")
        _ = run(["bash", "hooks/uninstall.sh"], env={"HOME": str(home)})
        ensure(read_json(claude_dir / "settings.json") == {}, "fresh uninstall should leave empty settings")

    print("Claude hook install/uninstall flow OK")


def main() -> int:
    checks = [
        verify_synced_files,
        verify_manifests_and_syntax,
        verify_compress_fixtures,
        verify_compress_cli,
        verify_hook_install_flow,
    ]

    try:
        for check in checks:
            check()
    except CheckFailure as exc:
        print(f"\nFAIL: {exc}", file=sys.stderr)
        return 1

    print("\nAll local verification checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
