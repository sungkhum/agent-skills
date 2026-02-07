#!/usr/bin/env python3
"""
Utilities for editing ODF XML documents.

This module provides XMLEditor, a tool for manipulating XML files with support for
line-number-based node finding and DOM manipulation. Each element is automatically
annotated with its original line and column position during parsing.

Example usage:
    editor = XMLEditor("content.xml")

    # Find node by line number or range
    elem = editor.get_node(tag="text:p", line_number=120)
    elem = editor.get_node(tag="text:span", line_number=range(200, 260))

    # Find node by text content
    elem = editor.get_node(tag="text:p", contains="specific text")

    # Find node by attributes
    elem = editor.get_node(tag="text:h", attrs={"text:outline-level": "2"})

    # Replace, insert, or manipulate
    new_elem = editor.replace_node(elem, "<text:span>new text</text:span>")
    editor.insert_after(new_elem, "<text:span>more</text:span>")

    # Save changes
    editor.save()
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Optional, Union

import defusedxml.minidom
import defusedxml.sax


class XMLEditor:
    """
    Editor for manipulating ODF XML files with line-number-based node finding.

    This class parses XML files and tracks the original line and column position
    of each element. This enables finding nodes by their line number in the original
    file, which is useful when working with Read tool output.

    Attributes:
        xml_path: Path to the XML file being edited
        encoding: Detected encoding of the XML file ('ascii' or 'utf-8')
        dom: Parsed DOM tree with parse_position attributes on elements
    """

    def __init__(self, xml_path):
        """
        Initialize with path to XML file and parse with line number tracking.

        Args:
            xml_path: Path to XML file to edit (str or Path)

        Raises:
            ValueError: If the XML file does not exist
        """
        self.xml_path = Path(xml_path)
        if not self.xml_path.exists():
            raise ValueError(f"XML file not found: {xml_path}")

        with open(self.xml_path, "rb") as f:
            header = f.read(200).decode("utf-8", errors="ignore")
        self.encoding = "ascii" if 'encoding="ascii"' in header else "utf-8"

        parser = _create_line_tracking_parser()
        self.dom = defusedxml.minidom.parse(str(self.xml_path), parser)

    def get_node(
        self,
        tag: str,
        attrs: Optional[dict[str, str]] = None,
        line_number: Optional[Union[int, range]] = None,
        contains: Optional[str] = None,
    ):
        """
        Get a DOM element by tag and identifier.

        Finds an element by either its line number in the original file or by
        matching attribute values. Exactly one match must be found.

        Args:
            tag: The XML tag name (e.g., "text:p", "text:h", "text:span")
            attrs: Dictionary of attribute name-value pairs to match
            line_number: Line number (int) or line range (range) in original XML file (1-indexed)
            contains: Text string that must appear in any text node within the element.

        Returns:
            defusedxml.minidom.Element: The matching DOM element

        Raises:
            ValueError: If node not found or multiple matches found
        """
        matches = []
        for elem in self.dom.getElementsByTagName(tag):
            # Check line_number filter
            if line_number is not None:
                parse_pos = getattr(elem, "parse_position", (None,))
                elem_line = parse_pos[0]

                # Handle both single line number and range
                if isinstance(line_number, range):
                    if elem_line not in line_number:
                        continue
                else:
                    if elem_line != line_number:
                        continue

            # Check attrs filter
            if attrs is not None:
                if not all(
                    elem.getAttribute(attr_name) == attr_value
                    for attr_name, attr_value in attrs.items()
                ):
                    continue

            # Check contains filter
            if contains is not None:
                elem_text = self._get_element_text(elem)
                normalized_contains = html.unescape(contains)
                if normalized_contains not in elem_text:
                    continue

            matches.append(elem)

        if not matches:
            filters = []
            if line_number is not None:
                line_str = (
                    f"lines {line_number.start}-{line_number.stop - 1}"
                    if isinstance(line_number, range)
                    else f"line {line_number}"
                )
                filters.append(f"at {line_str}")
            if attrs is not None:
                filters.append(f"with attributes {attrs}")
            if contains is not None:
                filters.append(f"containing '{contains}'")

            filter_desc = " ".join(filters) if filters else ""
            base_msg = f"Node not found: <{tag}> {filter_desc}".strip()

            if contains:
                hint = "Text may be split across elements or use different wording."
            elif line_number:
                hint = "Line numbers may have changed if document was modified."
            elif attrs:
                hint = "Verify attribute values are correct."
            else:
                hint = "Try adding filters (attrs, line_number, or contains)."

            raise ValueError(f"{base_msg}. {hint}")
        if len(matches) > 1:
            raise ValueError(
                f"Multiple nodes found: <{tag}>. "
                f"Add more filters (attrs, line_number, or contains) to narrow the search."
            )
        return matches[0]

    def replace_node(self, elem, xml_content):
        """
        Replace a DOM element with new XML content.

        Returns:
            defusedxml.minidom.Node: First inserted node
        """
        parent = elem.parentNode
        nodes = self._parse_fragment(xml_content)
        for node in nodes:
            parent.insertBefore(node, elem)
        parent.removeChild(elem)
        return nodes[0]

    def insert_after(self, elem, xml_content):
        """Insert XML content immediately after a DOM element."""
        parent = elem.parentNode
        nodes = self._parse_fragment(xml_content)
        for node in nodes:
            if elem.nextSibling is None:
                parent.appendChild(node)
            else:
                parent.insertBefore(node, elem.nextSibling)
        return nodes

    def insert_before(self, elem, xml_content):
        """Insert XML content immediately before a DOM element."""
        parent = elem.parentNode
        nodes = self._parse_fragment(xml_content)
        for node in nodes:
            parent.insertBefore(node, elem)
        return nodes

    def append_to(self, elem, xml_content):
        """Append XML content as a child of a DOM element."""
        nodes = self._parse_fragment(xml_content)
        for node in nodes:
            elem.appendChild(node)
        return nodes

    def remove_node(self, elem):
        """Remove a DOM element from the document."""
        parent = elem.parentNode
        parent.removeChild(elem)

    def save(self):
        """Save the edited XML back to the file."""
        content = self.dom.toxml(encoding=self.encoding)
        self.xml_path.write_bytes(content)

    def _get_element_text(self, elem):
        text_parts = []
        for node in elem.childNodes:
            if node.nodeType == node.TEXT_NODE:
                if node.data.strip():
                    text_parts.append(node.data)
            else:
                text_parts.append(self._get_element_text(node))
        return "".join(text_parts)

    def _parse_fragment(self, xml_content):
        root_elem = self.dom.documentElement
        namespaces = []
        if root_elem and root_elem.attributes:
            for i in range(root_elem.attributes.length):
                attr = root_elem.attributes.item(i)
                if attr.name.startswith("xmlns"):  # type: ignore
                    namespaces.append(f'{attr.name}="{attr.value}"')  # type: ignore

        ns_decl = " ".join(namespaces)
        wrapper = f"<root {ns_decl}>{xml_content}</root>"
        fragment_doc = defusedxml.minidom.parseString(wrapper)
        nodes = [
            self.dom.importNode(child, deep=True)
            for child in fragment_doc.documentElement.childNodes  # type: ignore
        ]
        elements = [n for n in nodes if n.nodeType == n.ELEMENT_NODE]
        assert elements, "Fragment must contain at least one element"
        return nodes


def _create_line_tracking_parser():
    """
    Create a SAX parser that tracks line and column numbers for each element.
    """

    def set_content_handler(dom_handler):
        def startElementNS(name, tagName, attrs):
            orig_start_cb(name, tagName, attrs)
            cur_elem = dom_handler.elementStack[-1]
            cur_elem.parse_position = (
                parser._parser.CurrentLineNumber,  # type: ignore
                parser._parser.CurrentColumnNumber,  # type: ignore
            )

        orig_start_cb = dom_handler.startElementNS
        dom_handler.startElementNS = startElementNS
        orig_set_content_handler(dom_handler)

    parser = defusedxml.sax.make_parser()
    orig_set_content_handler = parser.setContentHandler
    parser.setContentHandler = set_content_handler  # type: ignore
    return parser
