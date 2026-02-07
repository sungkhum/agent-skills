#!/usr/bin/env python3
"""Validate basic IDML package integrity and structure."""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path

try:
    from defusedxml import ElementTree as ET
except Exception:  # pragma: no cover
    import xml.etree.ElementTree as ET

IDML_MIMETYPE = "application/vnd.adobe.indesign-idml-package"


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore").strip()


def _container_rootfile(container_path: Path) -> str | None:
    try:
        tree = ET.parse(container_path)
    except Exception:
        return None
    root = tree.getroot()
    for elem in root.iter():
        for attr_name, value in elem.attrib.items():
            if attr_name.endswith("full-path"):
                return value
    return None


def validate(unpacked_dir: Path, original_file: Path | None, verbose: bool = False) -> int:
    errors: list[str] = []
    warnings: list[str] = []

    designmap = unpacked_dir / "designmap.xml"
    container = unpacked_dir / "META-INF" / "container.xml"
    mimetype = unpacked_dir / "mimetype"

    if not designmap.is_file():
        errors.append("Missing designmap.xml")
    if not container.is_file():
        errors.append("Missing META-INF/container.xml")

    if mimetype.is_file():
        if _read_text(mimetype) != IDML_MIMETYPE:
            errors.append("mimetype file does not match IDML media type")
    else:
        warnings.append("mimetype file not found (recommended for IDML)")

    if container.is_file():
        rootfile = _container_rootfile(container)
        if not rootfile:
            errors.append("container.xml missing rootfile full-path")
        else:
            root_path = unpacked_dir / rootfile
            if not root_path.is_file():
                errors.append(f"container.xml rootfile not found: {rootfile}")

    # Check expected directories
    for dirname in ("Resources", "Spreads", "Stories"):
        if not (unpacked_dir / dirname).is_dir():
            warnings.append(f"Missing {dirname}/ directory")

    # If original is provided, verify mimetype placement and compression
    if original_file and original_file.is_file():
        with zipfile.ZipFile(original_file, "r") as zf:
            names = [i.filename for i in zf.infolist()]
            if "mimetype" in names:
                first = zf.infolist()[0]
                if first.filename != "mimetype":
                    errors.append("mimetype must be the first ZIP entry")
                if first.compress_type != zipfile.ZIP_STORED:
                    errors.append("mimetype must be stored uncompressed")

    _print_results(errors, warnings, verbose)
    return 0 if not errors else 1


def _print_results(errors: list[str], warnings: list[str], verbose: bool) -> None:
    if errors:
        print("IDML validation FAILED:\n")
        for err in errors:
            print(f"- {err}")
    else:
        print("IDML validation PASSED.")

    if warnings and (verbose or not errors):
        print("\nWarnings:")
        for w in warnings:
            print(f"- {w}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate IDML package structure")
    parser.add_argument("unpacked_dir", help="Path to unpacked IDML directory")
    parser.add_argument("--original", help="Path to original .idml file")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    unpacked_dir = Path(args.unpacked_dir)
    if not unpacked_dir.is_dir():
        print(f"Not a directory: {unpacked_dir}", file=sys.stderr)
        return 1

    original = Path(args.original) if args.original else None
    if original and not original.is_file():
        print(f"Not a file: {original}", file=sys.stderr)
        return 1

    return validate(unpacked_dir, original, args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
