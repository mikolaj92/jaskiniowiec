#!/usr/bin/env python3
"""
Orkiestrator kompresji pamięci Jaskiniowca.

Użycie:
    python scripts/compress.py <filepath>
"""

import os
import re
import subprocess
from pathlib import Path
from typing import List

OUTER_FENCE_REGEX = re.compile(
    r"\A\s*(`{3,}|~{3,})[^\n]*\n(.*)\n\1\s*\Z", re.DOTALL
)

SENSITIVE_BASENAME_REGEX = re.compile(
    r"(?ix)^("
    r"\.env(\..+)?"
    r"|\.netrc"
    r"|credentials(\..+)?"
    r"|secrets?(\..+)?"
    r"|passwords?(\..+)?"
    r"|id_(rsa|dsa|ecdsa|ed25519)(\.pub)?"
    r"|authorized_keys"
    r"|known_hosts"
    r"|.*\.(pem|key|p12|pfx|crt|cer|jks|keystore|asc|gpg)"
    r")$"
)

SENSITIVE_PATH_COMPONENTS = frozenset({".ssh", ".aws", ".gnupg", ".kube", ".docker"})

SENSITIVE_NAME_TOKENS = (
    "secret", "credential", "password", "passwd",
    "apikey", "accesskey", "token", "privatekey",
)


def is_sensitive_path(filepath: Path) -> bool:
    name = filepath.name
    if SENSITIVE_BASENAME_REGEX.match(name):
        return True
    lowered_parts = {p.lower() for p in filepath.parts}
    if lowered_parts & SENSITIVE_PATH_COMPONENTS:
        return True
    lower = re.sub(r"[_\-\s.]", "", name.lower())
    return any(tok in lower for tok in SENSITIVE_NAME_TOKENS)


def strip_llm_wrapper(text: str) -> str:
    m = OUTER_FENCE_REGEX.match(text)
    if m:
        return m.group(2)
    return text

from .detect import should_compress
from .validate import validate

MAX_RETRIES = 2


def call_claude(prompt: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        try:
            from importlib import import_module

            anthropic = import_module("anthropic")
            client = anthropic.Anthropic(api_key=api_key)
            msg = client.messages.create(
                model=os.environ.get("JASKINIOWIEC_MODEL", "claude-sonnet-4-5"),
                max_tokens=8192,
                messages=[{"role": "user", "content": prompt}],
            )
            return strip_llm_wrapper(msg.content[0].text.strip())
        except ImportError:
            pass
    try:
        result = subprocess.run(
            ["claude", "--print"],
            input=prompt,
            text=True,
            capture_output=True,
            check=True,
        )
        return strip_llm_wrapper(result.stdout.strip())
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Wywołanie Claude nie powiodło się:\n{e.stderr}")


def build_compress_prompt(original: str) -> str:
    return f"""
Compress this markdown into Polish jaskiniowiec format.

STRICT RULES:
- Do NOT modify anything inside ``` code blocks
- Do NOT modify anything inside inline backticks
- Preserve ALL URLs exactly
- Preserve ALL headings exactly
- Preserve file paths and commands
- Return ONLY the compressed markdown body — do NOT wrap the entire output in a ```markdown fence or any other fence. Inner code blocks from the original stay as-is; do not add a new outer fence around the whole file.
- Use Polish-only jaskiniowiec style. No Wenyan, no Chinese variants.

Only compress natural language.

TEXT:
{original}
"""


def build_fix_prompt(original: str, compressed: str, errors: List[str]) -> str:
    errors_str = "\n".join(f"- {e}" for e in errors)
    return f"""You are fixing a Polish jaskiniowiec-compressed markdown file. Specific validation errors were found.

CRITICAL RULES:
- DO NOT recompress or rephrase the file
- ONLY fix the listed errors — leave everything else exactly as-is
- The ORIGINAL is provided as reference only (to restore missing content)
- Preserve Polish jaskiniowiec style in all untouched sections
- Do not introduce Wenyan, Chinese, or English-only mode variants

ERRORS TO FIX:
{errors_str}

HOW TO FIX:
- Missing URL: find it in ORIGINAL, restore it exactly where it belongs in COMPRESSED
- Code block mismatch: find the exact code block in ORIGINAL, restore it in COMPRESSED
- Heading mismatch: restore the exact heading text from ORIGINAL into COMPRESSED
- Do not touch any section not mentioned in the errors

ORIGINAL (reference only):
{original}

COMPRESSED (fix this):
{compressed}

Return ONLY the fixed compressed file. No explanation.
"""


def compress_file(filepath: Path) -> bool:
    filepath = filepath.resolve()
    MAX_FILE_SIZE = 500_000
    if not filepath.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku: {filepath}")
    if filepath.stat().st_size > MAX_FILE_SIZE:
        raise ValueError(f"Plik jest za duży do bezpiecznej kompresji (max 500KB): {filepath}")

    if is_sensitive_path(filepath):
        raise ValueError(
            f"Odmowa kompresji {filepath}: nazwa pliku wygląda na wrażliwą "
            "(sekrety, klucze, credentiale albo znane prywatne ścieżki). "
            "Kompresja wysyła zawartość pliku do API Anthropic. "
            "Jeśli to fałszywy alarm, zmień nazwę pliku."
        )

    print(f"Przetwarzanie: {filepath}")

    if not should_compress(filepath):
        print("Pomijam (to nie jest naturalny język)")
        return False

    original_text = filepath.read_text(errors="ignore")
    backup_path = filepath.with_name(filepath.stem + ".original.md")

    if backup_path.exists():
        print(f"⚠️ Backup już istnieje: {backup_path}")
        print("Ten backup może zawierać ważną treść oryginalną.")
        print("Przerywam, żeby uniknąć utraty danych. Usuń albo zmień nazwę backupu, jeśli chcesz kontynuować.")
        return False

    print("Kompresuję przez Claude...")
    compressed = call_claude(build_compress_prompt(original_text))

    backup_path.write_text(original_text)
    filepath.write_text(compressed)

    for attempt in range(MAX_RETRIES):
        print(f"\nPróba walidacji {attempt + 1}")

        result = validate(backup_path, filepath)

        if result.is_valid:
            print("Walidacja przeszła")
            break

        print("❌ Walidacja nie przeszła:")
        for err in result.errors:
            print(f"   - {err}")

        if attempt == MAX_RETRIES - 1:
            filepath.write_text(original_text)
            backup_path.unlink(missing_ok=True)
            print("❌ Nie udało się po ponowieniach — oryginał przywrócony")
            return False

        print("Naprawiam przez Claude...")
        compressed = call_claude(
            build_fix_prompt(original_text, compressed, result.errors)
        )
        filepath.write_text(compressed)

    return True
