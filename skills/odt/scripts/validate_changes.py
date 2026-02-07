#!/usr/bin/env python3
"""Validate basic ODT tracked-changes consistency in content.xml.

Checks:
- All change markers reference a change-id that exists in text:tracked-changes.
- All change-start markers have a matching change-end marker.
- Warns on change records that are never referenced.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

try:
    from defusedxml import ElementTree as ET
except Exception:  # pragma: no cover
    import xml.etree.ElementTree as ET

CONTENT_NS = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
TEXT_NS = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"


def _ns(tag: str) -> str:
    if tag.startswith("text:"):
        return f"{{{TEXT_NS}}}" + tag.split(":", 1)[1]
    if tag.startswith("office:"):
        return f"{{{CONTENT_NS}}}" + tag.split(":", 1)[1]
    return tag


def validate(content_xml: Path) -> int:
    if not content_xml.is_file():
        print(f"Missing content.xml: {content_xml}", file=sys.stderr)
        return 1

    tree = ET.parse(content_xml)
    root = tree.getroot()

    tracked = root.findall(f".//{_ns('text:tracked-changes')}")
    change_ids = set()
    for tracked_el in tracked:
        for region in tracked_el.findall(_ns("text:changed-region")):
            change_id = region.get(_ns("text:id"))
            if change_id:
                change_ids.add(change_id)

    markers = []
    for tag in ("text:change-start", "text:change-end", "text:change"):
        markers.extend(root.findall(f".//{_ns(tag)}"))

    errors = []
    warnings = []

    ref_ids = []
    for m in markers:
        cid = m.get(_ns("text:change-id"))
        if cid:
            ref_ids.append(cid)
            if cid not in change_ids:
                errors.append(f"Marker references unknown change-id: {cid}")

    starts = [
        m.get(_ns("text:change-id"))
        for m in root.findall(f".//{_ns('text:change-start')}")
    ]
    ends = [
        m.get(_ns("text:change-id"))
        for m in root.findall(f".//{_ns('text:change-end')}")
    ]
    start_counts = Counter([s for s in starts if s])
    end_counts = Counter([e for e in ends if e])

    for cid, count in start_counts.items():
        if end_counts.get(cid, 0) < count:
            warnings.append(f"Change-id {cid} has {count} start marker(s) but only {end_counts.get(cid, 0)} end marker(s)")

    for cid in change_ids:
        if cid not in ref_ids:
            warnings.append(f"Change-id {cid} is defined but never referenced in content")

    if errors:
        print("Tracked-changes validation FAILED:\n")
        for err in errors:
            print(f"- {err}")
    else:
        print("Tracked-changes validation PASSED.")

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"- {w}")

    return 0 if not errors else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ODT tracked changes in content.xml")
    parser.add_argument("content_xml", help="Path to content.xml")
    args = parser.parse_args()

    return validate(Path(args.content_xml))


if __name__ == "__main__":
    raise SystemExit(main())
