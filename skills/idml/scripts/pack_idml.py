#!/usr/bin/env python3
"""Pack an unpacked IDML directory into a valid IDML file."""

from __future__ import annotations

import argparse
import os
import sys
import zipfile


def pack_idml(src_dir: str, out_path: str) -> None:
    mimetype_path = os.path.join(src_dir, "mimetype")
    with zipfile.ZipFile(out_path, "w") as zf:
        if os.path.isfile(mimetype_path):
            with open(mimetype_path, "rb") as f:
                zf.writestr("mimetype", f.read(), compress_type=zipfile.ZIP_STORED)

        for root, _, files in os.walk(src_dir):
            for name in files:
                full_path = os.path.join(root, name)
                rel_path = os.path.relpath(full_path, src_dir)
                if rel_path == "mimetype":
                    continue
                zf.write(full_path, rel_path, compress_type=zipfile.ZIP_DEFLATED)


def main() -> int:
    parser = argparse.ArgumentParser(description="Pack directory into .idml")
    parser.add_argument("src_dir", help="Unpacked IDML directory")
    parser.add_argument("out_idml", help="Output .idml path")
    args = parser.parse_args()

    if not os.path.isdir(args.src_dir):
        print(f"Directory not found: {args.src_dir}", file=sys.stderr)
        return 1

    pack_idml(args.src_dir, args.out_idml)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
