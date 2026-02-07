#!/usr/bin/env python3
"""
Library for working with unpacked IDML directories.

Provides helpers for designmap, stories, spreads, and resources.
"""

from __future__ import annotations

from pathlib import Path

try:
    from defusedxml import ElementTree as ET
except Exception:  # pragma: no cover
    import xml.etree.ElementTree as ET

from .utilities import XMLEditor


class IDMLDocument:
    """Helper for editing unpacked IDML directories."""

    def __init__(self, unpacked_dir: str | Path):
        self.root = Path(unpacked_dir)
        if not self.root.is_dir():
            raise ValueError(f"Not a directory: {self.root}")
        self._editors: dict[str, XMLEditor] = {}

    def __getitem__(self, rel_path: str) -> XMLEditor:
        path = self.root / rel_path
        if not path.exists():
            raise ValueError(f"Missing XML file: {rel_path}")
        if rel_path not in self._editors:
            self._editors[rel_path] = XMLEditor(path)
        return self._editors[rel_path]

    def designmap(self) -> XMLEditor:
        return self["designmap.xml"]

    def story_paths(self) -> list[Path]:
        stories_dir = self.root / "Stories"
        if not stories_dir.is_dir():
            return []
        return sorted(stories_dir.glob("*.xml"))

    def spread_paths(self) -> list[Path]:
        spreads_dir = self.root / "Spreads"
        if not spreads_dir.is_dir():
            return []
        return sorted(spreads_dir.glob("*.xml"))

    def master_spread_paths(self) -> list[Path]:
        ms_dir = self.root / "MasterSpreads"
        if not ms_dir.is_dir():
            return []
        return sorted(ms_dir.glob("*.xml"))

    def resource_paths(self) -> list[Path]:
        res_dir = self.root / "Resources"
        if not res_dir.is_dir():
            return []
        return sorted(res_dir.glob("*.xml"))

    def referenced_story_paths(self) -> list[str]:
        """Return story file paths referenced from designmap.xml (best-effort)."""
        dm = self.root / "designmap.xml"
        if not dm.is_file():
            return []
        try:
            tree = ET.parse(dm)
        except Exception:
            return []
        root = tree.getroot()
        refs = []
        for elem in root.iter():
            for attr_name, value in elem.attrib.items():
                if attr_name.endswith("src") and value.startswith("Stories/"):
                    refs.append(value)
        return sorted(set(refs))

    def referenced_spread_paths(self) -> list[str]:
        dm = self.root / "designmap.xml"
        if not dm.is_file():
            return []
        try:
            tree = ET.parse(dm)
        except Exception:
            return []
        root = tree.getroot()
        refs = []
        for elem in root.iter():
            for attr_name, value in elem.attrib.items():
                if attr_name.endswith("src") and value.startswith("Spreads/"):
                    refs.append(value)
        return sorted(set(refs))

    def save(self) -> None:
        for editor in self._editors.values():
            editor.save()
