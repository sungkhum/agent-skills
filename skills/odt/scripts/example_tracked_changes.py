#!/usr/bin/env python3
"""Apply a tracked-change replacement to the first matching paragraph."""

from __future__ import annotations

import argparse
import html
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


def _build_replacement_xml(node, text: str) -> str:
    escaped = html.escape(text)
    style = node.getAttribute("text:style-name")
    if style:
        return f'<text:p text:style-name="{style}">{escaped}</text:p>'
    return f"<text:p>{escaped}</text:p>"


def main() -> int:
    parser = argparse.ArgumentParser(description="Tracked-change replacement example")
    parser.add_argument("odt_file", help="Path to .odt file")
    parser.add_argument("work_dir", help="Working directory")
    parser.add_argument("--search", required=True, help="Text to search for")
    parser.add_argument("--replace", required=True, help="Replacement text")
    parser.add_argument("--author", default="Editor", help="Author name")
    parser.add_argument("--out", default="tracked-changes.odt", help="Output ODT filename")
    args = parser.parse_args()

    odt_file = Path(args.odt_file)
    work_dir = Path(args.work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    unpack_dir = work_dir / "unpacked"
    out_file = work_dir / args.out

    scripts_dir = Path(__file__).resolve().parent

    _run_script(scripts_dir / "unpack_odt.py", [str(odt_file), str(unpack_dir)])

    odt = ODTDocument(unpack_dir)
    node = odt["content.xml"].get_node(tag="text:p", contains=args.search)
    replacement_xml = _build_replacement_xml(node, args.replace)
    odt.suggest_replacement(node, replacement_xml, author=args.author)
    odt.save()

    _run_script(scripts_dir / "validate_changes.py", [str(unpack_dir / "content.xml")])
    _run_script(scripts_dir / "pack_odt.py", [str(unpack_dir), str(out_file)])
    _run_script(scripts_dir / "validate_odt.py", [str(unpack_dir), "--original", str(out_file)])

    print(f"Tracked-change example completed: {out_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
