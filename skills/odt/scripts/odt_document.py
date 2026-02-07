#!/usr/bin/env python3
"""
Library for working with ODT documents: XML editing, manifest updates, and media management.

Usage:
    from scripts.odt_document import ODTDocument

    doc = ODTDocument('unpacked')
    node = doc["content.xml"].get_node(tag="text:p", contains="Hello")
    doc["content.xml"].replace_node(node, "<text:p>Updated</text:p>")

    # Add an image to Pictures/ and update the manifest
    internal_path = doc.add_picture("/path/to/image.png")

    # Tracked changes (basic)
    change_id = doc.add_change_record("insertion", author="Jane Doe")
    doc.add_change_markers(change_id, start_elem=node, end_elem=node)

    # Save changes
    doc.save()
"""

from __future__ import annotations

import mimetypes
import random
import shutil
from datetime import datetime, timezone
from pathlib import Path

try:
    from defusedxml import ElementTree as ET
except Exception:  # pragma: no cover - fallback when defusedxml is unavailable
    import xml.etree.ElementTree as ET

from .utilities import XMLEditor

MANIFEST_NS = "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"
ODT_MIMETYPE = "application/vnd.oasis.opendocument.text"


def _first_last_elements(nodes):
    """Extract first and last element nodes from a list."""
    elements = [n for n in nodes if getattr(n, "nodeType", None) == n.ELEMENT_NODE]
    if not elements:
        return None, None
    return elements[0], elements[-1]


class ODTDocument:
    """Helper for editing unpacked ODT directories."""

    def __init__(self, unpacked_dir: str | Path):
        self.root = Path(unpacked_dir)
        if not self.root.is_dir():
            raise ValueError(f"Not a directory: {self.root}")

        self._editors: dict[str, XMLEditor] = {}
        self._manifest_path = self.root / "META-INF" / "manifest.xml"
        if not self._manifest_path.exists():
            raise ValueError("Missing META-INF/manifest.xml in unpacked ODT")

        self._manifest_tree = ET.parse(self._manifest_path)
        self._manifest_root = self._manifest_tree.getroot()

    def __getitem__(self, rel_path: str) -> XMLEditor:
        path = self.root / rel_path
        if not path.exists():
            raise ValueError(f"Missing XML file: {rel_path}")
        if rel_path not in self._editors:
            self._editors[rel_path] = XMLEditor(path)
        return self._editors[rel_path]

    def new_change_id(self, prefix: str = "ct") -> str:
        """Generate a change-id for tracked changes (use as text:change-id)."""
        suffix = "".join(random.choices("0123456789abcdef", k=8))
        return f"{prefix}{suffix}"

    def ensure_tracked_changes(self):
        """Ensure <text:tracked-changes> exists in content.xml and return it."""
        content = self["content.xml"]
        dom = content.dom
        existing = dom.getElementsByTagName("text:tracked-changes")
        if existing:
            return existing[0]

        office_text = dom.getElementsByTagName("office:text")
        if not office_text:
            raise ValueError("content.xml missing <office:text>")

        parent = office_text[0]
        tracked = dom.createElement("text:tracked-changes")

        # Insert after any <text:sequence-decls> if present, otherwise first element
        insert_after = None
        for node in parent.childNodes:
            if node.nodeType == node.ELEMENT_NODE and node.tagName == "text:sequence-decls":
                insert_after = node

        if insert_after is not None and insert_after.nextSibling is not None:
            parent.insertBefore(tracked, insert_after.nextSibling)
        else:
            first_elem = None
            for node in parent.childNodes:
                if node.nodeType == node.ELEMENT_NODE:
                    first_elem = node
                    break
            if first_elem is None:
                parent.appendChild(tracked)
            else:
                parent.insertBefore(tracked, first_elem)

        return tracked

    def add_change_record(
        self,
        change_type: str,
        author: str = "Claude",
        date: str | None = None,
        content_xml: str | None = None,
        change_id: str | None = None,
    ) -> str:
        """Add a change record to <text:tracked-changes>.

        change_type: one of "insertion", "deletion", "format-change".
        content_xml: optional XML payload to include inside the change element.
        """
        if change_type not in {"insertion", "deletion", "format-change"}:
            raise ValueError("change_type must be insertion, deletion, or format-change")

        change_id = change_id or self.new_change_id()
        content = self["content.xml"]
        dom = content.dom

        tracked = self.ensure_tracked_changes()
        changed_region = dom.createElement("text:changed-region")
        changed_region.setAttribute("text:id", change_id)

        change_elem = dom.createElement(f"text:{change_type}")
        change_info = dom.createElement("office:change-info")

        creator = dom.createElement("dc:creator")
        creator.appendChild(dom.createTextNode(author))
        change_info.appendChild(creator)

        timestamp = date or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        date_elem = dom.createElement("dc:date")
        date_elem.appendChild(dom.createTextNode(timestamp))
        change_info.appendChild(date_elem)

        change_elem.appendChild(change_info)

        if content_xml:
            content.append_to(change_elem, content_xml)

        changed_region.appendChild(change_elem)
        tracked.appendChild(changed_region)
        return change_id

    def add_change_markers(self, change_id: str, start_elem, end_elem=None) -> None:
        """Insert change-start/end markers around a range in content.xml."""
        content = self["content.xml"]
        end_elem = end_elem or start_elem
        content.insert_before(start_elem, f'<text:change-start text:change-id="{change_id}"/>')
        content.insert_after(end_elem, f'<text:change-end text:change-id="{change_id}"/>')

    def add_change_point(self, change_id: str, after_elem) -> None:
        """Insert a point change marker (<text:change>) after a node."""
        content = self["content.xml"]
        content.insert_after(after_elem, f'<text:change text:change-id="{change_id}"/>')

    def add_annotation(
        self,
        target_elem,
        text: str,
        author: str = "Claude",
        date: str | None = None,
        name: str | None = None,
    ) -> str:
        """Insert an office:annotation element before a target node."""
        content = self["content.xml"]
        annotation_name = name or "c" + "".join(random.choices("0123456789abcdef", k=6))
        timestamp = date or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        xml = (
            f'<office:annotation office:name="{annotation_name}">'
            f"<dc:creator>{author}</dc:creator>"
            f"<dc:date>{timestamp}</dc:date>"
            f"<text:p>{text}</text:p>"
            f"</office:annotation>"
        )
        content.insert_before(target_elem, xml)
        return annotation_name

    def add_annotation_range(
        self,
        start_elem,
        end_elem,
        text: str,
        author: str = "Claude",
        date: str | None = None,
        name: str | None = None,
    ) -> str:
        """Insert a range annotation with annotation-end marker."""
        annotation_name = self.add_annotation(start_elem, text, author=author, date=date, name=name)
        content = self["content.xml"]
        content.insert_after(end_elem, f'<office:annotation-end office:name="{annotation_name}"/>')
        return annotation_name

    def suggest_insertion(self, after_elem, xml_content: str, author: str = "Claude") -> str:
        """Insert new content with tracked-change markers and record."""
        change_id = self.add_change_record("insertion", author=author, content_xml=xml_content)
        content = self["content.xml"]
        inserted_nodes = content.insert_after(after_elem, xml_content)
        start_elem, end_elem = _first_last_elements(inserted_nodes)
        if start_elem and end_elem:
            self.add_change_markers(change_id, start_elem, end_elem)
        else:
            self.add_change_point(change_id, after_elem)
        return change_id

    def suggest_deletion(self, target_elem, author: str = "Claude") -> str:
        """Remove content and record a deletion change at its former location."""
        content_xml = target_elem.toxml()
        change_id = self.add_change_record("deletion", author=author, content_xml=content_xml)
        content = self["content.xml"]
        marker_nodes = content.insert_after(target_elem, f'<text:change text:change-id=\"{change_id}\"/>')
        content.remove_node(target_elem)
        return change_id

    def suggest_replacement(self, target_elem, xml_content: str, author: str = "Claude") -> tuple[str, str]:
        """Replace content by recording a deletion then insertion."""
        del_id = self.suggest_deletion(target_elem, author=author)
        # Insert replacement after the deletion marker
        content = self["content.xml"]
        marker = content.get_node(tag="text:change", attrs={"text:change-id": del_id})
        ins_id = self.suggest_insertion(marker, xml_content, author=author)
        return del_id, ins_id

    def ensure_manifest_entry(self, full_path: str, media_type: str = "") -> None:
        """Ensure a manifest:file-entry exists for the given path."""
        if full_path.startswith("/"):
            full_path = full_path.lstrip("/")

        for elem in self._manifest_root.findall(f"{{{MANIFEST_NS}}}file-entry"):
            if elem.get(f"{{{MANIFEST_NS}}}full-path") == full_path:
                if media_type and not elem.get(f"{{{MANIFEST_NS}}}media-type"):
                    elem.set(f"{{{MANIFEST_NS}}}media-type", media_type)
                return

        entry = ET.SubElement(self._manifest_root, f"{{{MANIFEST_NS}}}file-entry")
        entry.set(f"{{{MANIFEST_NS}}}full-path", full_path)
        entry.set(f"{{{MANIFEST_NS}}}media-type", media_type)

    def add_picture(self, file_path: str | Path, dest_name: str | None = None) -> str:
        """Copy an image into Pictures/ and add a manifest entry.

        Returns the internal ODT path (e.g., "Pictures/image.png").
        """
        src = Path(file_path)
        if not src.is_file():
            raise ValueError(f"Image not found: {src}")

        pictures_dir = self.root / "Pictures"
        pictures_dir.mkdir(parents=True, exist_ok=True)

        target_name = dest_name or src.name
        dest = pictures_dir / target_name
        shutil.copy2(src, dest)

        media_type, _ = mimetypes.guess_type(dest.name)
        media_type = media_type or "application/octet-stream"

        internal_path = f"Pictures/{target_name}"
        self.ensure_manifest_entry(internal_path, media_type)
        return internal_path

    def save(self) -> None:
        """Save all XML editors and persist manifest.xml changes."""
        for editor in self._editors.values():
            editor.save()

        # Ensure root entry exists and is correct
        root_entry = None
        for elem in self._manifest_root.findall(f"{{{MANIFEST_NS}}}file-entry"):
            if elem.get(f"{{{MANIFEST_NS}}}full-path") == "/":
                root_entry = elem
                break
        if root_entry is None:
            root_entry = ET.SubElement(self._manifest_root, f"{{{MANIFEST_NS}}}file-entry")
            root_entry.set(f"{{{MANIFEST_NS}}}full-path", "/")
        root_entry.set(f"{{{MANIFEST_NS}}}media-type", ODT_MIMETYPE)

        self._manifest_tree.write(self._manifest_path, encoding="UTF-8", xml_declaration=True)
