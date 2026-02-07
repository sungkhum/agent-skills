#!/usr/bin/env python3
"""Create a markdown checklist from an observed schema delta report."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List


def _write_section(f, title: str, items: List[str]) -> None:
    f.write(f"## {title}\n")
    if not items:
        f.write("- [x] None\n\n")
        return
    for item in items:
        f.write(f"- [ ] {item}\n")
    f.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a coverage checklist from a delta report")
    parser.add_argument("delta", help="Schema delta JSON report")
    parser.add_argument("--out", required=True, help="Output markdown file")
    args = parser.parse_args()

    delta = json.loads(Path(args.delta).read_text(encoding="utf-8"))

    added_elements = delta.get("added_elements", [])
    removed_elements = delta.get("removed_elements", [])
    added_attrs = delta.get("added_attributes", {})
    removed_attrs = delta.get("removed_attributes", {})
    added_children = delta.get("added_children", {})
    removed_children = delta.get("removed_children", {})

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with out_path.open("w", encoding="utf-8") as f:
        f.write("# Observed Schema Coverage Checklist\n\n")
        f.write("Use this checklist to expand sample coverage.\n")
        f.write("The items below are present in the baseline schema but missing in the new sample.\n\n")

        _write_section(f, "Missing Elements", removed_elements)

        missing_attr_items = [f"{element}: {', '.join(attrs)}" for element, attrs in removed_attrs.items()]
        _write_section(f, "Missing Attributes", missing_attr_items)

        missing_child_items = [f"{element}: {', '.join(children)}" for element, children in removed_children.items()]
        _write_section(f, "Missing Child Elements", missing_child_items)

        if added_elements or added_attrs or added_children:
            f.write("## New Elements/Attributes in Sample\n")
            if added_elements:
                f.write("### Added Elements\n")
                for item in added_elements:
                    f.write(f"- {item}\n")
            if added_attrs:
                f.write("### Added Attributes\n")
                for element, attrs in added_attrs.items():
                    f.write(f"- {element}: {', '.join(attrs)}\n")
            if added_children:
                f.write("### Added Child Elements\n")
                for element, children in added_children.items():
                    f.write(f"- {element}: {', '.join(children)}\n")
            f.write("\n")

    print(f"Wrote checklist to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
