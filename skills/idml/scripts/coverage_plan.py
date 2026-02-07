#!/usr/bin/env python3
"""Create a combined coverage plan from multiple schema delta JSON files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple


def _load_delta(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _labelled_args(items: List[str]) -> List[Tuple[str, Path]]:
    labelled: List[Tuple[str, Path]] = []
    for item in items:
        if "=" not in item:
            raise ValueError(f"Expected label=path, got: {item}")
        label, raw_path = item.split("=", 1)
        labelled.append((label.strip(), Path(raw_path.strip())))
    return labelled


def _append_missing(mapping: Dict[str, Set[str]], key: str, label: str) -> None:
    mapping.setdefault(key, set()).add(label)


def main() -> int:
    parser = argparse.ArgumentParser(description="Combine schema delta reports into a coverage plan")
    parser.add_argument(
        "inputs",
        nargs="+",
        help="One or more label=path pairs pointing to schema delta JSON files",
    )
    parser.add_argument("--out", required=True, help="Output markdown file")
    args = parser.parse_args()

    labelled = _labelled_args(args.inputs)

    missing_elements: Dict[str, Set[str]] = {}
    missing_attrs: Dict[str, Set[str]] = {}
    missing_children: Dict[str, Set[str]] = {}

    summary: Dict[str, dict] = {}

    for label, path in labelled:
        delta = _load_delta(path)
        removed_elements = delta.get("removed_elements", [])
        removed_attrs = delta.get("removed_attributes", {})
        removed_children = delta.get("removed_children", {})

        summary[label] = {
            "missing_elements": len(removed_elements),
            "missing_attributes": sum(len(v) for v in removed_attrs.values()),
            "missing_children": sum(len(v) for v in removed_children.values()),
        }

        for element in removed_elements:
            _append_missing(missing_elements, element, label)

        for element, attrs in removed_attrs.items():
            for attr in attrs:
                _append_missing(missing_attrs, f"{element}::{attr}", label)

        for element, children in removed_children.items():
            for child in children:
                _append_missing(missing_children, f"{element}::{child}", label)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    def _write_section(f, title: str, mapping: Dict[str, Set[str]]) -> None:
        f.write(f"## {title}\n")
        if not mapping:
            f.write("- [x] None\n\n")
            return
        for key in sorted(mapping.keys()):
            labels = ", ".join(sorted(mapping[key]))
            f.write(f"- [ ] {key} (missing in: {labels})\n")
        f.write("\n")

    with out_path.open("w", encoding="utf-8") as f:
        f.write("# Observed Schema Coverage Plan (Combined)\n\n")
        f.write("This plan lists items missing from one or more sample sets.\n\n")
        f.write("## Summary\n")
        for label in sorted(summary.keys()):
            stats = summary[label]
            f.write(
                f"- {label}: elements={stats['missing_elements']}, "
                f"attributes={stats['missing_attributes']}, "
                f"children={stats['missing_children']}\n"
            )
        f.write("\n")

        _write_section(f, "Missing Elements", missing_elements)
        _write_section(f, "Missing Attributes", missing_attrs)
        _write_section(f, "Missing Child Elements", missing_children)

    print(f"Wrote coverage plan to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
