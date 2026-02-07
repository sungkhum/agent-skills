# ODT Document Library (Python)

Use this file when you need a higher-level workflow for tracked changes, annotations, images, or repeatable XML edits.

**Important: Read this entire document before starting.**

## Setup
Find the ODT skill root (the folder containing `scripts/`), then set `PYTHONPATH` to that root so imports work.

```bash
PYTHONPATH=/path/to/odt-skill/odt python your_script.py
```

## Basic usage
```python
from scripts.odt_document import ODTDocument

# Open an unpacked ODT directory
odt = ODTDocument('unpacked')

# Read/modify XML using XMLEditor
node = odt["content.xml"].get_node(tag="text:p", contains="Hello")
odt["content.xml"].replace_node(node, "<text:p>Updated</text:p>")

# Save all edits + manifest changes
odt.save()
```

## Tracked changes (recommended helpers)
```python
from scripts.odt_document import ODTDocument

odt = ODTDocument('unpacked')

# Find a target node
target = odt["content.xml"].get_node(tag="text:p", contains="Old text")

# Suggest replacement with tracked changes
odt.suggest_replacement(target, "<text:p>New text</text:p>", author="Editor")

# Save
odt.save()
```

### Insertions and deletions
```python
# Insert new content after a node
odt.suggest_insertion(target, "<text:p>Inserted</text:p>")

# Delete a node with change tracking
odt.suggest_deletion(target)
```

## Annotations (comments)
```python
# Point annotation (single location)
odt.add_annotation(target, "Review this paragraph", author="Reviewer")

# Range annotation (spans start..end)
odt.add_annotation_range(start_elem, end_elem, "Check this section")
```

## Images and manifest updates
```python
internal_path = odt.add_picture("/path/to/image.png")
# internal_path is like "Pictures/image.png"
```

## Save and repack
```bash
python scripts/pack_odt.py unpacked output.odt
```

## Validation checks
```bash
python scripts/validate_odt.py unpacked --original output.odt
python scripts/validate_changes.py unpacked/content.xml
python scripts/validate_rng.py unpacked/content.xml
```

## Example scripts
- Tracked changes example: `python scripts/example_tracked_changes.py input.odt work --search \"Old\" --replace \"New\"`
- Annotation smoke test: `python scripts/annotation_smoke_test.py input.odt work`

## Notes
- Use `scripts/utilities.py` for line-number based XML edits.
- If the document already defines styles, reuse them instead of creating new styles.
- For complex XML edits, read `references/odf-xml.md` in full.
