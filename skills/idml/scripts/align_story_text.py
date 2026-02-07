#!/usr/bin/env python3
"""Generate an approximate alignment between two IDML JSONL extracts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List


def _load_records(path: Path) -> Dict[str, List[dict]]:
    stories: Dict[str, List[dict]] = {}
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            story = rec.get("story")
            if not story:
                continue
            stories.setdefault(story, []).append(rec)
    for story, recs in stories.items():
        recs.sort(key=lambda r: int(r.get("index", 0)))
    return stories


def _score(en: dict, km: dict) -> float:
    score = 0.0
    if en.get("paragraph_style") and en.get("paragraph_style") == km.get("paragraph_style"):
        score += 0.4
    if en.get("character_style") and en.get("character_style") == km.get("character_style"):
        score += 0.2
    en_text = (en.get("text") or "").strip()
    km_text = (km.get("text") or "").strip()
    if en_text and km_text:
        ratio = min(len(en_text), len(km_text)) / max(len(en_text), len(km_text))
        score += 0.4 * ratio
    return round(score, 3)


def _scaled_index(i: int, en_count: int, km_count: int) -> int:
    if en_count <= 1:
        return 0
    return round(i * (km_count - 1) / (en_count - 1))


def main() -> int:
    parser = argparse.ArgumentParser(description="Align two IDML JSONL extracts")
    parser.add_argument("english_jsonl", help="English JSONL extract")
    parser.add_argument("khmer_jsonl", help="Khmer JSONL extract")
    parser.add_argument("--out", required=True, help="Output alignment JSONL")
    args = parser.parse_args()

    en = _load_records(Path(args.english_jsonl))
    km = _load_records(Path(args.khmer_jsonl))

    stories = sorted(set(en) | set(km))
    out_path = Path(args.out)

    with out_path.open("w", encoding="utf-8") as f:
        for story in stories:
            en_list = en.get(story, [])
            km_list = km.get(story, [])
            if not en_list and not km_list:
                continue

            if len(en_list) == len(km_list):
                for i, (e, k) in enumerate(zip(en_list, km_list)):
                    rec = {
                        "story": story,
                        "en_index": e.get("index"),
                        "km_index": k.get("index"),
                        "en_text": e.get("text"),
                        "km_text": k.get("text"),
                        "en_paragraph_style": e.get("paragraph_style"),
                        "km_paragraph_style": k.get("paragraph_style"),
                        "en_character_style": e.get("character_style"),
                        "km_character_style": k.get("character_style"),
                        "score": _score(e, k),
                        "method": "index",
                    }
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                continue

            used_km = set()
            for i, e in enumerate(en_list):
                if not km_list:
                    rec = {
                        "story": story,
                        "en_index": e.get("index"),
                        "km_index": None,
                        "en_text": e.get("text"),
                        "km_text": None,
                        "score": 0.0,
                        "method": "missing-km",
                    }
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    continue

                j = _scaled_index(i, len(en_list), len(km_list))
                j = max(0, min(j, len(km_list) - 1))
                used_km.add(j)
                k = km_list[j]
                rec = {
                    "story": story,
                    "en_index": e.get("index"),
                    "km_index": k.get("index"),
                    "en_text": e.get("text"),
                    "km_text": k.get("text"),
                    "en_paragraph_style": e.get("paragraph_style"),
                    "km_paragraph_style": k.get("paragraph_style"),
                    "en_character_style": e.get("character_style"),
                    "km_character_style": k.get("character_style"),
                    "score": _score(e, k),
                    "method": "scaled",
                }
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

            for j, k in enumerate(km_list):
                if j in used_km:
                    continue
                rec = {
                    "story": story,
                    "en_index": None,
                    "km_index": k.get("index"),
                    "en_text": None,
                    "km_text": k.get("text"),
                    "score": 0.0,
                    "method": "missing-en",
                }
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"Wrote alignment to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
