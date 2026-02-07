#!/usr/bin/env python3
"""Run a basic ODT roundtrip smoke test and validations."""

from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path


def _run_script(script: Path, args: list[str]) -> None:
    old_argv = sys.argv
    try:
        sys.argv = [str(script)] + args
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit as exc:
        if exc.code not in (0, None):
            raise
    finally:
        sys.argv = old_argv


def main() -> int:
    parser = argparse.ArgumentParser(description="ODT smoke test")
    parser.add_argument("odt_file", help="Path to .odt file")
    parser.add_argument("work_dir", help="Working directory")
    parser.add_argument("--out", default="roundtrip.odt", help="Output ODT filename")
    args = parser.parse_args()

    odt_file = Path(args.odt_file)
    work_dir = Path(args.work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    unpack_dir = work_dir / "unpacked"
    out_file = work_dir / args.out

    scripts_dir = Path(__file__).resolve().parent

    _run_script(scripts_dir / "unpack_odt.py", [str(odt_file), str(unpack_dir)])
    _run_script(scripts_dir / "validate_odt.py", [str(unpack_dir), "--original", str(odt_file)])
    _run_script(scripts_dir / "validate_changes.py", [str(unpack_dir / "content.xml")])
    _run_script(scripts_dir / "pack_odt.py", [str(unpack_dir), str(out_file)])
    _run_script(scripts_dir / "validate_odt.py", [str(unpack_dir), "--original", str(out_file)])

    print(f"Smoke test completed: {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
