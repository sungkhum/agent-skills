# IDML package structure

IDML is a ZIP-based package following the Open Packaging Conventions (OPC/UCF). It uses UNIX-style path separators, and the ZIP must not contain a top-level subdirectory. The `mimetype` file should be first and uncompressed.

## Required top-level files
- `mimetype` (contents: `application/vnd.adobe.indesign-idml-package`)
- `designmap.xml` (root document, references components)
- `META-INF/container.xml` (points to `designmap.xml`)
- `META-INF/metadata.xml`

## Common component folders
- `Stories/` — story XML files (text content)
- `Spreads/` — spread XML files (layout and page items)
- `MasterSpreads/` — master spreads
- `Resources/` — shared resources (e.g., `Styles.xml`, `Fonts.xml`, `Preferences.xml`, `Graphic.xml`)
- `XML/` — XML mapping files (e.g., `BackingStory.xml`, `Mapping.xml`, `Tags.xml`)

## Notes
- IDML uses component files (stories, spreads, master spreads) referenced from `designmap.xml`.
- Text is stored in story files and referenced by frames in spreads.
