#!/usr/bin/env python3
"""Build an observed IDML schema summary from sample IDML files or unpacked dirs.

This script does NOT use any external schema bundles. It infers element/attribute
usage from the XML you provide.
"""

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


def _record_attr(bucket: Dict, attr: str, value: str, sample_limit: int) -> None:
    entry = bucket.setdefault(attr, {"count": 0, "samples": []})
    entry["count"] += 1
    if sample_limit <= 0:
        return
    if len(entry["samples"]) < sample_limit and value not in entry["samples"]:
        entry["samples"].append(value)


def _record_element(stats: Dict, elem: ET.Element, sample_limit: int) -> None:
    tag = _strip_ns(elem.tag)
    entry = stats.setdefault(
        tag,
        {
            "count": 0,
            "attributes": {},
            "children": defaultdict(int),
            "text_nodes": 0,
            "tail_nodes": 0,
        },
    )

    entry["count"] += 1
    for attr, value in elem.attrib.items():
        _record_attr(entry["attributes"], attr, value, sample_limit)

    if elem.text and elem.text.strip():
        entry["text_nodes"] += 1
    if elem.tail and elem.tail.strip():
        entry["tail_nodes"] += 1

    for child in list(elem):
        entry["children"][_strip_ns(child.tag)] += 1
        _record_element(stats, child, sample_limit)


def _merge_children(stats: Dict) -> None:
    for entry in stats.values():
        if isinstance(entry.get("children"), defaultdict):
            entry["children"] = dict(entry["children"])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Infer an observed schema summary from IDML XML files",
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="One or more IDML files or unpacked IDML directories",
    )
    parser.add_argument(
        "--out",
        default="idml_observed_schema.json",
        help="Output JSON file",
    )
    parser.add_argument(
        "--sample-limit",
        type=int,
        default=5,
        help="Max unique attribute samples to store per attribute (0 disables)",
    )
    parser.add_argument(
        "--source-mode",
        choices=("basename", "full"),
        default="basename",
        help="How to record input sources (default: basename)",
    )
    args = parser.parse_args()

    element_stats: Dict[str, dict] = {}
    file_roots: Dict[str, str] = {}
    sources: List[str] = []

    for raw_path in args.paths:
        path = Path(raw_path)
        if args.source_mode == "basename":
            sources.append(path.name)
        else:
            sources.append(str(path))
        for name, data in _iter_xml_paths(path):
            try:
                root = ET.fromstring(data)
            except Exception:
                continue
            file_roots[name] = _strip_ns(root.tag)
            _record_element(element_stats, root, args.sample_limit)

    _merge_children(element_stats)

    report = {
        "sources": sources,
        "file_roots": file_roots,
        "elements": element_stats,
    }

    out_path = Path(args.out)
    out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote observed schema report to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
