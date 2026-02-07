# odfdo library tutorial

Generate and edit .odt files with Python using odfdo. Use odfdo for high-level edits; fall back to raw XML (`references/odf-xml.md`) for complex or low-level control.

**Important: Read this entire document before starting.**

## Installation
```bash
pip install odfdo
```

## Create a new document (hello world)
```python
from odfdo import Document, Paragraph

# Create a new text document
odt = Document('text')

# Append a paragraph
odt.body.append(Paragraph('Hello ODT'))

# Save to file
odt.save('hello.odt')
```

## Open and modify an existing document
```python
from odfdo import Document, Paragraph

odt = Document('existing.odt')

# Append a paragraph
odt.body.append(Paragraph('Appended paragraph'))

odt.save('updated.odt')
```

## Add an image (frame-based)
```python
from odfdo import Document, Frame, Paragraph

doc = Document("text")
uri = doc.add_file("image.png")
image_frame = Frame.image_frame(uri, size=("6cm", "4cm"), position=("0cm", "0cm"))

para = Paragraph("")
para.append(image_frame)
doc.body.append(para)

doc.save("with-image.odt")
```

## Tables (outline)
Use `Table`, `Cell`, and `Paragraph` to build tables, then append to the document body. See the odfdo recipes for complete examples.

## Styling guidance (important)
- Prefer **merging styles from a template ODT** rather than generating complex styles programmatically.
- Keep edits minimal when altering styles; ODF styles can be deep and interdependent.

## When to use odfdo vs odfpy
- Use **odfdo** for most edits and automation.
- Use **odfpy** when you need direct element-level control or strict schema alignment.

## Useful odfdo CLI utilities
These are fast ways to inspect and extract content:
- `odfdo-show <file.odt>` — inspect structure and content.
- `odfdo-markdown <file.odt> > output.md` — extract to Markdown.
- `odfdo-replace <file.odt> <search> <replace> -o out.odt` — simple text replacement.
- `odfdo-style -l <file.odt>` — list styles.

For advanced operations (tables, images, lists, headers/footers), use the official odfdo documentation and recipes, then map the resulting XML patterns back to `references/odf-xml.md` if you need low-level edits.
