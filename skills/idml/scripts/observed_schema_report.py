#!/usr/bin/env python3
"""Summarize coverage of an observed IDML schema JSON file."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Dict, List


def _top_items(counter: Counter, limit: int) -> List[dict]:
    return [
        {"name": name, "count": count}
        for name, count in counter.most_common(limit)
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Summarize observed IDML schema coverage",
    )
    parser.add_argument("schema", help="Observed schema JSON file")
    parser.add_argument("--out", help="Optional JSON report output")
    parser.add_argument(
        "--top",
        type=int,
        default=30,
        help="Number of top elements/attributes to list",
    )
    parser.add_argument(
        "--expected-components",
        nargs="*",
        default=["Stories", "Spreads", "MasterSpreads", "Resources", "XML"],
        help="Expected top-level component folders",
    )
    args = parser.parse_args()

    data = json.loads(Path(args.schema).read_text(encoding="utf-8"))
    file_roots: Dict[str, str] = data.get("file_roots", {})
    elements: Dict[str, dict] = data.get("elements", {})

    component_counts = Counter()
    root_counts = Counter()
    for file_name, root_tag in file_roots.items():
        root_counts[root_tag] += 1
        parts = file_name.split("/")
        if parts:
            component_counts[parts[0]] += 1

    element_counts = Counter()
    attribute_counts = Counter()
    for element_name, entry in elements.items():
        element_counts[element_name] += int(entry.get("count", 0))
        for attr_name, attr_entry in entry.get("attributes", {}).items():
            attribute_counts[attr_name] += int(attr_entry.get("count", 0))

    expected = args.expected_components or []
    missing_components = [c for c in expected if component_counts.get(c, 0) == 0]

    summary = {
        "sources": data.get("sources", []),
        "xml_file_count": len(file_roots),
        "element_count": len(elements),
        "component_counts": dict(component_counts),
        "root_tag_counts": dict(root_counts),
        "missing_components": missing_components,
        "top_elements": _top_items(element_counts, args.top),
        "top_attributes": _top_items(attribute_counts, args.top),
    }

    if args.out:
        out_path = Path(args.out)
        out_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"Wrote report to {out_path}")

    print("Observed schema coverage summary:")
    print(f"- XML files: {summary['xml_file_count']}")
    print(f"- Elements: {summary['element_count']}")
    if summary["missing_components"]:
        print("- Missing components: " + ", ".join(summary["missing_components"]))
    else:
        print("- Missing components: none")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
