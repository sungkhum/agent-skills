#!/usr/bin/env python3
"""Validate that only Content node text changed between two unpacked IDML dirs."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

try:
    from defusedxml import ElementTree as ET
except Exception:  # pragma: no cover
    import xml.etree.ElementTree as ET


def _strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _compare_elements(a: ET.Element, b: ET.Element, errors: List[str], path: str) -> None:
    if a.tag != b.tag:
        errors.append(f"{path}: tag mismatch {a.tag!r} vs {b.tag!r}")
        return

    tag_name = _strip_ns(a.tag)

    if tag_name == "Content":
        if a.attrib != b.attrib:
            errors.append(f"{path}: Content attributes changed")
        if list(a) or list(b):
            errors.append(f"{path}: Content has child elements")
        if a.tail != b.tail:
            errors.append(f"{path}: Content tail changed")
        return

    if a.attrib != b.attrib:
        errors.append(f"{path}: attributes changed")
        return

    if a.text != b.text:
        errors.append(f"{path}: text changed in non-Content element")
        return

    if a.tail != b.tail:
        errors.append(f"{path}: tail changed in non-Content element")
        return

    a_children = list(a)
    b_children = list(b)
    if len(a_children) != len(b_children):
        errors.append(f"{path}: child count changed ({len(a_children)} vs {len(b_children)})")
        return

    for idx, (a_child, b_child) in enumerate(zip(a_children, b_children)):
        child_path = f"{path}/{_strip_ns(a_child.tag)}[{idx}]"
        _compare_elements(a_child, b_child, errors, child_path)


def _compare_story_file(original: Path, modified: Path, errors: List[str]) -> None:
    try:
        a_tree = ET.parse(original)
        b_tree = ET.parse(modified)
    except Exception as exc:
        errors.append(f"{original.name}: failed to parse XML ({exc})")
        return

    a_root = a_tree.getroot()
    b_root = b_tree.getroot()
    _compare_elements(a_root, b_root, errors, f"{original.name}/{_strip_ns(a_root.tag)}")


def _list_files(root: Path) -> List[Path]:
    return sorted([p.relative_to(root) for p in root.rglob("*") if p.is_file()])


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ensure only Content node text changed between unpacked IDML directories"
    )
    parser.add_argument("original_dir", help="Original unpacked IDML directory")
    parser.add_argument("modified_dir", help="Modified unpacked IDML directory")
    args = parser.parse_args()

    original_root = Path(args.original_dir)
    modified_root = Path(args.modified_dir)

    if not original_root.is_dir() or not modified_root.is_dir():
        raise SystemExit("Both directories must exist and be unpacked IDML folders")

    original_files = _list_files(original_root)
    modified_files = _list_files(modified_root)

    errors: List[str] = []

    if set(original_files) != set(modified_files):
        missing = sorted(set(original_files) - set(modified_files))
        extra = sorted(set(modified_files) - set(original_files))
        if missing:
            errors.append(f"Missing files in modified: {missing}")
        if extra:
            errors.append(f"Extra files in modified: {extra}")
        # Continue to report other differences where possible

    for rel_path in sorted(set(original_files).intersection(set(modified_files))):
        orig = original_root / rel_path
        mod = modified_root / rel_path

        if rel_path.parts and rel_path.parts[0] == "Stories" and rel_path.suffix == ".xml":
            _compare_story_file(orig, mod, errors)
            continue

        if orig.read_bytes() != mod.read_bytes():
            errors.append(f"{rel_path}: file changed outside Stories")

    if errors:
        print("Content-only validation failed:")
        for err in errors:
            print(f"- {err}")
        return 1

    print("Content-only validation passed: only Content node text changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
