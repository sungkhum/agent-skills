#!/usr/bin/env python3
"""Validate content.xml, styles.xml, and manifest.xml using validate_rng.py."""

from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path


def _run(script: Path, args: list[str]) -> int:
    old_argv = sys.argv
    try:
        sys.argv = [str(script)] + args
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit as exc:
        return int(exc.code or 0)
    finally:
        sys.argv = old_argv
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate multiple ODF XML files with jing")
    parser.add_argument("unpacked_dir", help="Path to unpacked ODT directory")
    args = parser.parse_args()

    base = Path(args.unpacked_dir)
    if not base.is_dir():
        print(f"Not a directory: {base}", file=sys.stderr)
        return 1

    scripts_dir = Path(__file__).resolve().parent
    validator = scripts_dir / "validate_rng.py"

    targets = [
        base / "content.xml",
        base / "styles.xml",
        base / "META-INF" / "manifest.xml",
    ]

    failed = False
    for xml_path in targets:
        if not xml_path.is_file():
            print(f"Missing file: {xml_path}", file=sys.stderr)
            failed = True
            continue
        code = _run(validator, [str(xml_path)])
        if code != 0:
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
