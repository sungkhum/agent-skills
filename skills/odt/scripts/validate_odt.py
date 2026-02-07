#!/usr/bin/env python3
"""Validate basic ODT package integrity and manifest consistency.

Checks:
- META-INF/manifest.xml exists
- Root manifest entry (/) exists and media type matches ODT
- Files in the package (except mimetype and META-INF) are declared in the manifest
- Manifest entries do not point to missing files
- If mimetype exists, it is first and uncompressed in the ZIP
"""

from __future__ import annotations

import argparse
import sys
import zipfile
from pathlib import Path
from typing import Iterable

try:
    from defusedxml import ElementTree as ET
except Exception:  # pragma: no cover - fallback when defusedxml is unavailable
    import xml.etree.ElementTree as ET

ODT_MIMETYPE = "application/vnd.oasis.opendocument.text"
MANIFEST_NS = "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"


def _iter_zip_files(zf: zipfile.ZipFile) -> Iterable[str]:
    for info in zf.infolist():
        if info.is_dir():
            continue
        yield info.filename


def _read_manifest(manifest_path: Path) -> list[dict[str, str]]:
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    entries = []
    for elem in root.findall(f"{{{MANIFEST_NS}}}file-entry"):
        entries.append({
            "full_path": elem.get(f"{{{MANIFEST_NS}}}full-path", ""),
            "media_type": elem.get(f"{{{MANIFEST_NS}}}media-type", ""),
        })
    return entries


def _normalize_manifest_path(path: str) -> str:
    return path.lstrip("/")


def validate(unpacked_dir: Path, original_file: Path, verbose: bool = False) -> int:
    errors: list[str] = []
    warnings: list[str] = []

    manifest_path = unpacked_dir / "META-INF" / "manifest.xml"
    if not manifest_path.is_file():
        errors.append("Missing META-INF/manifest.xml")
        _print_results(errors, warnings, verbose)
        return 1

    # Parse manifest entries
    entries = _read_manifest(manifest_path)
    manifest_paths = [e["full_path"] for e in entries]

    # Root entry
    root_entry = next((e for e in entries if e["full_path"] == "/"), None)
    if not root_entry:
        errors.append("Manifest missing root entry '/'")
    else:
        if root_entry.get("media_type") != ODT_MIMETYPE:
            errors.append(
                f"Root media type should be '{ODT_MIMETYPE}', got '{root_entry.get('media_type')}'"
            )

    # Check manifest does not list itself or mimetype
    if "META-INF/manifest.xml" in manifest_paths:
        errors.append("Manifest should not list META-INF/manifest.xml")
    if "mimetype" in manifest_paths:
        errors.append("Manifest should not list mimetype")

    # Compare manifest entries to zip contents
    with zipfile.ZipFile(original_file, "r") as zf:
        zip_files = list(_iter_zip_files(zf))

        # Check mimetype placement/compression if present
        if "mimetype" in zip_files:
            first = zf.infolist()[0]
            if first.filename != "mimetype":
                errors.append("mimetype must be the first ZIP entry")
            if first.compress_type != zipfile.ZIP_STORED:
                errors.append("mimetype must be stored uncompressed")
        else:
            warnings.append("mimetype file not found in ZIP (recommended for ODF packages)")

    # Build set of file paths that should be in manifest
    zip_declared = set(
        p for p in zip_files
        if not p.startswith("META-INF/") and p != "mimetype"
    )

    manifest_declared = set()
    for path in manifest_paths:
        if path in ("/", "mimetype", "META-INF/manifest.xml"):
            continue
        if path.endswith("/"):
            continue
        manifest_declared.add(_normalize_manifest_path(path))

    # Files present but missing from manifest
    missing_in_manifest = sorted(zip_declared - manifest_declared)
    for path in missing_in_manifest:
        errors.append(f"Manifest missing file entry for: {path}")

    # Files listed in manifest but not present
    missing_files = sorted(manifest_declared - zip_declared)
    for path in missing_files:
        errors.append(f"Manifest references missing file: {path}")

    _print_results(errors, warnings, verbose)
    return 0 if not errors else 1


def _print_results(errors: list[str], warnings: list[str], verbose: bool) -> None:
    if errors:
        print("ODT validation FAILED:\n")
        for err in errors:
            print(f"- {err}")
    else:
        print("ODT validation PASSED.")

    if warnings and (verbose or not errors):
        print("\nWarnings:")
        for w in warnings:
            print(f"- {w}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ODT package structure")
    parser.add_argument("unpacked_dir", help="Path to unpacked ODT directory")
    parser.add_argument("--original", required=True, help="Path to original .odt file")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    unpacked_dir = Path(args.unpacked_dir)
    original_file = Path(args.original)
    if not unpacked_dir.is_dir():
        print(f"Not a directory: {unpacked_dir}", file=sys.stderr)
        return 1
    if not original_file.is_file() or original_file.suffix.lower() != ".odt":
        print(f"Not an .odt file: {original_file}", file=sys.stderr)
        return 1

    return validate(unpacked_dir, original_file, args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
