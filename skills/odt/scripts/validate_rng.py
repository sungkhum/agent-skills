#!/usr/bin/env python3
"""Validate ODF XML against a Relax NG schema using jing.

Defaults to ODF 1.3 schemas in odf/schemas/odf-1.3.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def _default_schema(xml_path: Path, base_dir: Path) -> Path:
    schemas_dir = base_dir / "odf" / "schemas" / "odf-1.3"
    if xml_path.name == "manifest.xml":
        return schemas_dir / "OpenDocument-v1.3-manifest-schema.rng"
    return schemas_dir / "OpenDocument-v1.3-schema.rng"


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate ODF XML with jing")
    parser.add_argument("xml_file", help="Path to XML file (content.xml, styles.xml, or manifest.xml)")
    parser.add_argument("--schema", help="Path to RNG schema (optional)")
    args = parser.parse_args()

    xml_path = Path(args.xml_file)
    if not xml_path.is_file():
        print(f"Not a file: {xml_path}", file=sys.stderr)
        return 1

    base_dir = Path(__file__).resolve().parents[1]
    schema_path = Path(args.schema) if args.schema else _default_schema(xml_path, base_dir)

    if not schema_path.is_file():
        print(f"Schema not found: {schema_path}", file=sys.stderr)
        print("Fetch schemas first: python scripts/fetch_odf_schemas.py --out odf/schemas/odf-1.3", file=sys.stderr)
        return 1

    jing = shutil.which("jing")
    if not jing:
        print("jing not found in PATH. Install jing to run RNG validation.", file=sys.stderr)
        print(f"Then run: jing {schema_path} {xml_path}", file=sys.stderr)
        return 1

    result = subprocess.run([jing, str(schema_path), str(xml_path)])
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
