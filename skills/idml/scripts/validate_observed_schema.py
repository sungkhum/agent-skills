#!/usr/bin/env python3
"""Validate IDML XML against an observed schema (clean-room)."""

from __future__ import annotations

import argparse
import json
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

try:
    from defusedxml import ElementTree as ET
except Exception:  # pragma: no cover
    import xml.etree.ElementTree as ET


def _strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _iter_xml_paths(path: Path) -> Iterable[Tuple[str, bytes]]:
    if path.is_dir():
        for xml_path in sorted(path.rglob("*.xml")):
            rel = str(xml_path.relative_to(path))
            yield rel, xml_path.read_bytes()
        return

    if path.is_file() and path.suffix.lower() == ".idml":
        with zipfile.ZipFile(path) as zf:
            for name in sorted(zf.namelist()):
                if name.endswith(".xml"):
                    yield name, zf.read(name)
        return

    raise ValueError(f"Unsupported path: {path}")


def _load_schema(path: Path) -> Dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    elements = data.get("elements", {})
    return elements


def _collect_issues(
    schema: Dict[str, dict],
    elem: ET.Element,
    issues: Dict[str, List[dict]],
    file_name: str,
    path: str,
) -> None:
    tag = _strip_ns(elem.tag)
    schema_entry = schema.get(tag)
    if not schema_entry:
        issues["unknown_elements"].append({"file": file_name, "path": path, "tag": tag})
        schema_entry = {"attributes": {}, "children": {}}

    allowed_attrs = set(schema_entry.get("attributes", {}).keys())
    for attr in elem.attrib.keys():
        if attr not in allowed_attrs:
            issues["unknown_attributes"].append(
                {"file": file_name, "path": path, "tag": tag, "attr": attr}
            )

    allowed_children = set(schema_entry.get("children", {}).keys())
    for idx, child in enumerate(list(elem)):
        child_tag = _strip_ns(child.tag)
        if child_tag not in allowed_children:
            issues["unknown_children"].append(
                {
                    "file": file_name,
                    "path": path,
                    "tag": tag,
                    "child_tag": child_tag,
                    "index": idx,
                }
            )
        child_path = f"{path}/{child_tag}[{idx}]"
        _collect_issues(schema, child, issues, file_name, child_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate IDML XML against an observed schema",
    )
    parser.add_argument("schema", help="Observed schema JSON file")
    parser.add_argument("paths", nargs="+", help="IDML files or unpacked dirs")
    parser.add_argument("--out", help="Optional JSON report output")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with status 1 if any issues are found",
    )
    args = parser.parse_args()

    schema = _load_schema(Path(args.schema))

    issues: Dict[str, List[dict]] = {
        "unknown_elements": [],
        "unknown_attributes": [],
        "unknown_children": [],
    }

    for raw_path in args.paths:
        path = Path(raw_path)
        for name, data in _iter_xml_paths(path):
            try:
                root = ET.fromstring(data)
            except Exception:
                issues["unknown_elements"].append(
                    {"file": name, "path": name, "tag": "<parse_error>"}
                )
                continue
            root_tag = _strip_ns(root.tag)
            _collect_issues(schema, root, issues, name, f"{name}/{root_tag}")

    summary = {
        "unknown_elements": len(issues["unknown_elements"]),
        "unknown_attributes": len(issues["unknown_attributes"]),
        "unknown_children": len(issues["unknown_children"]),
    }

    if args.out:
        out_path = Path(args.out)
        out_path.write_text(json.dumps({"summary": summary, "issues": issues}, indent=2), encoding="utf-8")
        print(f"Wrote report to {out_path}")

    print("Observed schema validation summary:")
    for key, count in summary.items():
        print(f"- {key}: {count}")

    if args.strict and any(summary.values()):
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
