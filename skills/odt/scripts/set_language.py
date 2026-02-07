#!/usr/bin/env python3
"""Set language and complex-script attributes in styles.xml."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from defusedxml import ElementTree as ET
except Exception:  # pragma: no cover
    import xml.etree.ElementTree as ET

STYLE_NS = "urn:oasis:names:tc:opendocument:xmlns:style:1.0"
FO_NS = "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"

ATTR_FO_LANGUAGE = f"{{{FO_NS}}}language"
ATTR_FO_COUNTRY = f"{{{FO_NS}}}country"
ATTR_FO_LANGUAGE_COMPLEX = f"{{{FO_NS}}}language-complex"
ATTR_FO_COUNTRY_COMPLEX = f"{{{FO_NS}}}country-complex"
ATTR_STYLE_LANGUAGE_COMPLEX = f"{{{STYLE_NS}}}language-complex"
ATTR_STYLE_COUNTRY_COMPLEX = f"{{{STYLE_NS}}}country-complex"
ATTR_STYLE_FONT_NAME_COMPLEX = f"{{{STYLE_NS}}}font-name-complex"


def main() -> int:
    parser = argparse.ArgumentParser(description="Set language properties in styles.xml")
    parser.add_argument("styles_xml", help="Path to styles.xml")
    parser.add_argument("--lang", required=True, help="Language tag (e.g., km, en)")
    parser.add_argument("--country", required=True, help="Country/region (e.g., KH, US)")
    parser.add_argument("--no-base", action="store_true", help="Do not set base fo:language/fo:country")
    parser.add_argument("--no-complex", action="store_true", help="Do not set complex-script language")
    parser.add_argument("--font", help="Complex-script font name (optional)")
    args = parser.parse_args()

    styles_path = Path(args.styles_xml)
    if not styles_path.is_file():
        print(f"Missing styles.xml: {styles_path}", file=sys.stderr)
        return 1

    tree = ET.parse(styles_path)
    root = tree.getroot()

    changed = 0
    for tp in root.findall(f".//{{{STYLE_NS}}}text-properties"):
        if not args.no_base:
            tp.set(ATTR_FO_LANGUAGE, args.lang)
            tp.set(ATTR_FO_COUNTRY, args.country)
        if not args.no_complex:
            tp.set(ATTR_STYLE_LANGUAGE_COMPLEX, args.lang)
            tp.set(ATTR_STYLE_COUNTRY_COMPLEX, args.country)
            if ATTR_FO_LANGUAGE_COMPLEX in tp.attrib:
                tp.set(ATTR_FO_LANGUAGE_COMPLEX, args.lang)
            if ATTR_FO_COUNTRY_COMPLEX in tp.attrib:
                tp.set(ATTR_FO_COUNTRY_COMPLEX, args.country)
            if args.font:
                tp.set(ATTR_STYLE_FONT_NAME_COMPLEX, args.font)
        changed += 1

    tree.write(styles_path, encoding="UTF-8", xml_declaration=True)
    print(f"Updated {changed} style:text-properties elements")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
