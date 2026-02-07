#!/usr/bin/env python3
"""Add a sample annotation to the first paragraph and repack."""

from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path

from scripts.odt_document import ODTDocument


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
    parser = argparse.ArgumentParser(description="Annotation smoke test")
    parser.add_argument("odt_file", help="Path to .odt file")
    parser.add_argument("work_dir", help="Working directory")
    parser.add_argument("--text", default="Review this paragraph", help="Annotation text")
    parser.add_argument("--author", default="Reviewer", help="Author name")
    parser.add_argument("--out", default="annotated.odt", help="Output ODT filename")
    args = parser.parse_args()

    odt_file = Path(args.odt_file)
    work_dir = Path(args.work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    unpack_dir = work_dir / "unpacked"
    out_file = work_dir / args.out

    scripts_dir = Path(__file__).resolve().parent

    _run_script(scripts_dir / "unpack_odt.py", [str(odt_file), str(unpack_dir)])

    odt = ODTDocument(unpack_dir)
    content = odt["content.xml"]
    paragraphs = content.dom.getElementsByTagName("text:p")
    if not paragraphs:
        raise ValueError("No text:p elements found in content.xml")
    node = paragraphs[0]

    odt.add_annotation(node, args.text, author=args.author)
    odt.save()

    _run_script(scripts_dir / "pack_odt.py", [str(unpack_dir), str(out_file)])
    _run_script(scripts_dir / "validate_odt.py", [str(unpack_dir), "--original", str(out_file)])

    print(f"Annotation smoke test completed: {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
