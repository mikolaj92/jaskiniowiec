#!/usr/bin/env python3
"""
CLI kompresji Jaskiniowca.

Użycie:
    jaskiniowiec <filepath>
"""

import sys
from pathlib import Path

from .compress import compress_file
from .detect import detect_file_type, should_compress


def print_usage():
    print("Użycie: jaskiniowiec <filepath>")


def main():
    if len(sys.argv) != 2:
        print_usage()
        sys.exit(1)

    filepath = Path(sys.argv[1])

    if not filepath.exists():
        print(f"❌ Nie znaleziono pliku: {filepath}")
        sys.exit(1)

    if not filepath.is_file():
        print(f"❌ To nie jest plik: {filepath}")
        sys.exit(1)

    filepath = filepath.resolve()

    file_type = detect_file_type(filepath)
    print(f"Wykryto: {file_type}")

    if not should_compress(filepath):
        print("Pomijam: plik nie wygląda na naturalny język (kod/config)")
        sys.exit(0)

    print("Start kompresji jaskiniowca...\n")

    try:
        success = compress_file(filepath)

        if success:
            print("\nKompresja zakończona powodzeniem")
            backup_path = filepath.with_name(filepath.stem + ".original.md")
            print(f"Skompresowano: {filepath}")
            print(f"Oryginał:      {backup_path}")
            sys.exit(0)
        else:
            print("\n❌ Kompresja nie powiodła się po ponowieniach")
            sys.exit(2)

    except KeyboardInterrupt:
        print("\nPrzerwano przez użytkownika")
        sys.exit(130)

    except Exception as e:
        print(f"\n❌ Błąd: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
