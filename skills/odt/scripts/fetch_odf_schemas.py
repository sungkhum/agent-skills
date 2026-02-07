#!/usr/bin/env python3
"""Download ODF 1.3 schema artifacts from OASIS into a local folder."""

from __future__ import annotations

import argparse
import sys
import urllib.request
from pathlib import Path

BASE_URL = "https://docs.oasis-open.org/office/OpenDocument/v1.3/os/schemas"
FILES = [
    "OpenDocument-v1.3-schema.rng",
    "OpenDocument-v1.3-manifest-schema.rng",
    "OpenDocument-v1.3-dsig-schema.rng",
    "OpenDocument-v1.3-metadata.owl",
    "OpenDocument-v1.3-package-metadata.owl",
]


def download_file(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as resp:  # nosec - controlled source
        data = resp.read()
    dest.write_bytes(data)


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch ODF schema files")
    parser.add_argument(
        "--out",
        default="odf/schemas/odf-1.3",
        help="Output directory for schema files",
    )
    parser.add_argument(
        "--base-url",
        default=BASE_URL,
        help="Base URL for schema files",
    )
    args = parser.parse_args()

    out_dir = Path(args.out)
    base = args.base_url.rstrip("/")

    for name in FILES:
        url = f"{base}/{name}"
        dest = out_dir / name
        try:
            download_file(url, dest)
            print(f"Downloaded: {dest}")
        except Exception as exc:
            print(f"Failed to download {url}: {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
