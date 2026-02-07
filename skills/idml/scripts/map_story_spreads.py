#!/usr/bin/env python3
"""Map stories to spreads/pages by reading IDML component files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List

try:
    from defusedxml import ElementTree as ET
except Exception:  # pragma: no cover
    import xml.etree.ElementTree as ET


def _strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _story_id_map(stories_dir: Path) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for story in sorted(stories_dir.glob("*.xml")):
        try:
            tree = ET.parse(story)
        except Exception:
            continue
        root = tree.getroot()
        story_id = root.attrib.get("Self")
        if story_id:
            mapping[story_id] = story.name
    return mapping


def _spread_pages(root: ET.Element) -> List[str]:
    pages = []
    for elem in root.iter():
        if _strip_ns(elem.tag) == "Page":
            name = elem.attrib.get("Name")
            if name:
                pages.append(name)
    return pages


def main() -> int:
    parser = argparse.ArgumentParser(description="Map stories to spreads/pages")
    parser.add_argument("unpacked_dir", help="Path to unpacked IDML directory")
    parser.add_argument("--out", required=True, help="Output JSON report")
    args = parser.parse_args()

    root = Path(args.unpacked_dir)
    stories_dir = root / "Stories"
    spreads_dir = root / "Spreads"

    if not stories_dir.is_dir() or not spreads_dir.is_dir():
        raise SystemExit("Missing Stories/ or Spreads/ directory")

    story_ids = _story_id_map(stories_dir)
    story_map: Dict[str, dict] = {}

    for spread in sorted(spreads_dir.glob("*.xml")):
        try:
            tree = ET.parse(spread)
        except Exception:
            continue
        root_el = tree.getroot()
        pages = _spread_pages(root_el)

        for elem in root_el.iter():
            if _strip_ns(elem.tag) != "TextFrame":
                continue
            parent_story = elem.attrib.get("ParentStory")
            if not parent_story:
                continue
            story_name = story_ids.get(parent_story, None)
            entry = story_map.setdefault(parent_story, {
                "story_id": parent_story,
                "story_file": story_name,
                "spreads": [],
            })
            entry["spreads"].append({
                "spread": spread.name,
                "pages": pages,
                "frame_id": elem.attrib.get("Self"),
            })

    # Build report
    report = {
        "stories": sorted(story_map.values(), key=lambda x: x["story_id"]),
        "unmapped_story_ids": sorted([sid for sid in story_ids if sid not in story_map]),
        "story_id_count": len(story_ids),
        "mapped_story_count": len(story_map),
    }

    out = Path(args.out)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote report to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
