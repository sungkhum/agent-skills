#!/usr/bin/env python3
"""Prepare JSONL for translation by adding a blank translation field."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare JSONL for translation")
    parser.add_argument("in_jsonl", help="Input JSONL extract")
    parser.add_argument("out_jsonl", help="Output JSONL with translation field")
    parser.add_argument("--field", default="translation", help="Translation field name")
    args = parser.parse_args()

    inp = Path(args.in_jsonl)
    out = Path(args.out_jsonl)

    with inp.open("r", encoding="utf-8") as f_in, out.open("w", encoding="utf-8") as f_out:
        for line in f_in:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if args.field not in rec:
                rec[args.field] = ""
            f_out.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
