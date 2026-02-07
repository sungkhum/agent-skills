#!/usr/bin/env python3
"""Apply translated text to IDML story Content nodes using JSONL mapping."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterator, Tuple

try:
    from defusedxml import ElementTree as ET
except Exception:  # pragma: no cover
    import xml.etree.ElementTree as ET


def _iter_records(path: Path) -> Iterator[dict]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def _strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _walk_content_nodes(root: ET.Element) -> Iterator[ET.Element]:
    for elem in root.iter():
        if _strip_ns(elem.tag) == "Content":
            yield elem


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply translations to IDML story files")
    parser.add_argument("idml_dir", help="Path to unpacked IDML directory")
    parser.add_argument("translations", help="JSONL with id + translation fields")
    parser.add_argument("--field", default="translation", help="Field containing translated text")
    args = parser.parse_args()

    root = Path(args.idml_dir)
    stories_dir = root / "Stories"
    if not stories_dir.is_dir():
        raise SystemExit(f"Stories directory not found: {stories_dir}")

    # Build mapping: story -> index -> translation
    mapping: dict[str, dict[int, str]] = {}
    for rec in _iter_records(Path(args.translations)):
        story = rec.get("story")
        idx = rec.get("index")
        translated = rec.get(args.field)
        if story is None or idx is None or translated is None:
            continue
        mapping.setdefault(story, {})[int(idx)] = str(translated)

    updated = 0
    for story_path in sorted(stories_dir.glob("*.xml")):
        if story_path.name not in mapping:
            continue
        tree = ET.parse(story_path)
        root_el = tree.getroot()
        idx = 0
        for content in _walk_content_nodes(root_el):
            if idx in mapping[story_path.name]:
                content.text = mapping[story_path.name][idx]
                updated += 1
            idx += 1
        tree.write(story_path, encoding="utf-8", xml_declaration=True)

    print(f"Updated {updated} content nodes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
