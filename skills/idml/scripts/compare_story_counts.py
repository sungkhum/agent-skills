#!/usr/bin/env python3
"""Compare story text counts between two extracted JSONL files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict


def _load_counts(path: Path) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            story = rec.get("story")
            if not story:
                continue
            counts[story] = counts.get(story, 0) + 1
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare story counts between two JSONL extracts")
    parser.add_argument("left", help="Left JSONL (e.g., English)")
    parser.add_argument("right", help="Right JSONL (e.g., Khmer)")
    parser.add_argument("--out", required=True, help="Output report JSON file")
    args = parser.parse_args()

    left = Path(args.left)
    right = Path(args.right)
    out = Path(args.out)

    left_counts = _load_counts(left)
    right_counts = _load_counts(right)

    stories = sorted(set(left_counts) | set(right_counts))
    report = []
    total_left = 0
    total_right = 0
    mismatched = 0

    for story in stories:
        lc = left_counts.get(story, 0)
        rc = right_counts.get(story, 0)
        total_left += lc
        total_right += rc
        if lc != rc:
            mismatched += 1
        report.append({
            "story": story,
            "left_count": lc,
            "right_count": rc,
            "diff": rc - lc,
        })

    summary = {
        "total_left": total_left,
        "total_right": total_right,
        "mismatched_stories": mismatched,
        "story_count": len(stories),
    }

    out.write_text(json.dumps({"summary": summary, "stories": report}, indent=2), encoding="utf-8")
    print(f"Wrote report to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
