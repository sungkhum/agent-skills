#!/usr/bin/env python3
"""Extract text content from IDML story files into JSONL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Iterator, Tuple

try:
    from defusedxml import ElementTree as ET
except Exception:  # pragma: no cover
    import xml.etree.ElementTree as ET


def _iter_stories(stories_dir: Path) -> Iterable[Path]:
    return sorted(stories_dir.glob("*.xml"))


def _walk_content(root: ET.Element) -> Iterator[Tuple[str, str, str]]:
    """Yield (paragraph_style, character_style, text) for each Content node."""
    def recurse(elem: ET.Element, p_style: str, c_style: str):
        tag = _strip_ns(elem.tag)
        if tag == "ParagraphStyleRange":
            p_style = elem.attrib.get("AppliedParagraphStyle", p_style)
        if tag == "CharacterStyleRange":
            c_style = elem.attrib.get("AppliedCharacterStyle", c_style)
        if tag == "Content":
            text = elem.text or ""
            yield (p_style, c_style, text)
        for child in list(elem):
            yield from recurse(child, p_style, c_style)

    yield from recurse(root, "", "")


def _strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract IDML story text to JSONL")
    parser.add_argument("idml_dir", help="Path to unpacked IDML directory")
    parser.add_argument("out_jsonl", help="Output JSONL file")
    args = parser.parse_args()

    root = Path(args.idml_dir)
    stories_dir = root / "Stories"
    if not stories_dir.is_dir():
        raise SystemExit(f"Stories directory not found: {stories_dir}")

    out_path = Path(args.out_jsonl)
    records = []

    for story_path in _iter_stories(stories_dir):
        try:
            tree = ET.parse(story_path)
        except Exception:
            continue
        story_root = tree.getroot()
        idx = 0
        for p_style, c_style, text in _walk_content(story_root):
            records.append({
                "id": f"{story_path.name}::{idx}",
                "story": story_path.name,
                "index": idx,
                "paragraph_style": p_style,
                "character_style": c_style,
                "text": text,
            })
            idx += 1

    with out_path.open("w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False))
            f.write("\n")

    print(f"Wrote {len(records)} records to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
