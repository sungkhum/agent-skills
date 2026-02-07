# IDML Document Library (Python)

Use this file when you need a higher-level workflow for editing IDML components.

## Setup
```bash
PYTHONPATH=/path/to/idml-skill/idml python your_script.py
```

## Basic usage
```python
from scripts.idml_document import IDMLDocument

idml = IDMLDocument('unpacked')

# Access designmap
idml.designmap()

# List story files
for story in idml.story_paths():
    print(story)

# Edit a specific story
editor = idml["Stories/Story_u1.xml"]
node = editor.get_node(tag="Content", contains="Hello")
editor.replace_node(node, "<Content>Updated</Content>")

idml.save()
```

## Validation
```bash
python scripts/validate_idml.py unpacked --original input.idml
python scripts/smoke_test.py input.idml workdir
```
