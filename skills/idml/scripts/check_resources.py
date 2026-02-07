#!/usr/bin/env python3
"""Check IDML resource files for fonts, styles, and linked assets."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, List

try:
    from defusedxml import ElementTree as ET
except Exception:  # pragma: no cover
    import xml.etree.ElementTree as ET


def _strip_ns(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _list_fonts(fonts_xml: Path) -> Dict[str, List[str]]:
    families = {}
    if not fonts_xml.is_file():
        return families
    try:
        tree = ET.parse(fonts_xml)
    except Exception:
        return families
    root = tree.getroot()
    for fam in root.iter():
        if _strip_ns(fam.tag) == "FontFamily":
            name = fam.attrib.get("Name") or fam.attrib.get("Self")
            if not name:
                continue
            families.setdefault(name, [])
            for child in list(fam):
                if _strip_ns(child.tag) == "Font":
                    fam_name = child.attrib.get("FontStyleName") or child.attrib.get("Name")
                    if fam_name:
                        families[name].append(fam_name)
    return families


def _count_styles(styles_xml: Path) -> Dict[str, int]:
    counts = {}
    if not styles_xml.is_file():
        return counts
    try:
        tree = ET.parse(styles_xml)
    except Exception:
        return counts
    root = tree.getroot()
    for elem in root.iter():
        tag = _strip_ns(elem.tag)
        if tag.endswith("Style"):
            counts[tag] = counts.get(tag, 0) + 1
    return counts


def _extract_links_any(xml_path: Path) -> List[str]:
    text = xml_path.read_text(encoding="utf-8", errors="ignore")
    # Heuristic: find attribute values that look like file paths
    links = re.findall(r'="([^"]+\.(?:png|jpg|jpeg|tif|tiff|pdf|eps|ai|psd))"', text, flags=re.IGNORECASE)
    return sorted(set(links))


def main() -> int:
    parser = argparse.ArgumentParser(description="Check IDML resource files")
    parser.add_argument("unpacked_dir", help="Path to unpacked IDML directory")
    parser.add_argument("--out", required=True, help="Output JSON report")
    args = parser.parse_args()

    root = Path(args.unpacked_dir)
    res = root / "Resources"
    report = {
        "fonts": {},
        "style_counts": {},
        "links": [],
        "missing_links": [],
        "notes": [],
    }

    report["fonts"] = _list_fonts(res / "Fonts.xml")
    report["style_counts"] = _count_styles(res / "Styles.xml")

    link_candidates = []
    links_xml = res / "Links.xml"
    if links_xml.is_file():
        link_candidates.extend(_extract_links_any(links_xml))
    else:
        report["notes"].append("Resources/Links.xml not found")

    # Scan all resource XML for potential links
    for xml_path in res.glob("*.xml"):
        link_candidates.extend(_extract_links_any(xml_path))

    links = sorted(set(link_candidates))
    report["links"] = links

    # Check Links/ directory for missing assets if present
    links_dir = root / "Links"
    if links_dir.is_dir():
        for link in links:
            candidate = links_dir / Path(link).name
            if not candidate.exists():
                report["missing_links"].append(link)
    else:
        if links:
            report["notes"].append("Links/ directory not found; cannot verify linked assets")

    out = Path(args.out)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Wrote report to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
