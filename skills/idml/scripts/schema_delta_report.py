#!/usr/bin/env python3
"""Compare two observed schema JSON files and report differences."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _dict_keys(obj: dict | None) -> set[str]:
    if not obj:
        return set()
    return set(obj.keys())


def main() -> int:
    parser = argparse.ArgumentParser(description="Observed schema delta report")
    parser.add_argument("base", help="Base observed schema JSON")
    parser.add_argument("new", help="New observed schema JSON")
    parser.add_argument("--out", help="Output JSON report")
    args = parser.parse_args()

    base = _load(Path(args.base))
    new = _load(Path(args.new))

    base_elements: Dict[str, dict] = base.get("elements", {})
    new_elements: Dict[str, dict] = new.get("elements", {})

    base_keys = set(base_elements.keys())
    new_keys = set(new_elements.keys())

    added_elements = sorted(new_keys - base_keys)
    removed_elements = sorted(base_keys - new_keys)

    added_attrs: Dict[str, List[str]] = {}
    removed_attrs: Dict[str, List[str]] = {}
    added_children: Dict[str, List[str]] = {}
    removed_children: Dict[str, List[str]] = {}

    for element in sorted(base_keys & new_keys):
        base_entry = base_elements.get(element, {})
        new_entry = new_elements.get(element, {})

        base_attrs = _dict_keys(base_entry.get("attributes"))
        new_attrs = _dict_keys(new_entry.get("attributes"))
        attrs_added = sorted(new_attrs - base_attrs)
        attrs_removed = sorted(base_attrs - new_attrs)
        if attrs_added:
            added_attrs[element] = attrs_added
        if attrs_removed:
            removed_attrs[element] = attrs_removed

        base_children = _dict_keys(base_entry.get("children"))
        new_children = _dict_keys(new_entry.get("children"))
        children_added = sorted(new_children - base_children)
        children_removed = sorted(base_children - new_children)
        if children_added:
            added_children[element] = children_added
        if children_removed:
            removed_children[element] = children_removed

    report = {
        "summary": {
            "added_elements": len(added_elements),
            "removed_elements": len(removed_elements),
            "elements_with_added_attrs": len(added_attrs),
            "elements_with_removed_attrs": len(removed_attrs),
            "elements_with_added_children": len(added_children),
            "elements_with_removed_children": len(removed_children),
        },
        "added_elements": added_elements,
        "removed_elements": removed_elements,
        "added_attributes": added_attrs,
        "removed_attributes": removed_attrs,
        "added_children": added_children,
        "removed_children": removed_children,
    }

    if args.out:
        out_path = Path(args.out)
        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"Wrote report to {out_path}")

    print("Observed schema delta summary:")
    for key, value in report["summary"].items():
        print(f"- {key}: {value}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
