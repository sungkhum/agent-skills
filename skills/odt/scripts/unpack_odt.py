#!/usr/bin/env python3
"""Unpack an ODT file safely to a directory."""

from __future__ import annotations

import argparse
import os
import random
import sys
import zipfile
from pathlib import Path

try:
    from defusedxml import minidom
except Exception:  # pragma: no cover - fallback when defusedxml is unavailable
    from xml.dom import minidom


def _is_safe_path(base_dir: str, target_path: str) -> bool:
    base = os.path.abspath(base_dir)
    target = os.path.abspath(target_path)
    return os.path.commonpath([base]) == os.path.commonpath([base, target])


def safe_extract(zip_path: str, out_dir: str) -> None:
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            member_path = os.path.join(out_dir, member.filename)
            if not _is_safe_path(out_dir, member_path):
                raise ValueError(f"Unsafe path in zip: {member.filename}")
        zf.extractall(out_dir)


def _pretty_print_xml_files(out_dir: str) -> None:
    base = Path(out_dir)
    xml_files = list(base.rglob("*.xml"))
    for xml_file in xml_files:
        content = xml_file.read_text(encoding="utf-8")
        if not content.strip():
            continue
        try:
            dom = minidom.parseString(content)
        except Exception:
            # Skip files that are not well-formed XML
            continue
        xml_file.write_bytes(dom.toprettyxml(indent="  ", encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Unpack ODT into a directory")
    parser.add_argument("odt_file", help="Path to .odt file")
    parser.add_argument("out_dir", help="Output directory")
    args = parser.parse_args()

    if not os.path.isfile(args.odt_file):
        print(f"File not found: {args.odt_file}", file=sys.stderr)
        return 1

    os.makedirs(args.out_dir, exist_ok=True)
    safe_extract(args.odt_file, args.out_dir)
    _pretty_print_xml_files(args.out_dir)

    suggested_change_id = "ct" + "".join(random.choices("0123456789abcdef", k=8))
    print(f"Suggested change-id for tracked changes: {suggested_change_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
