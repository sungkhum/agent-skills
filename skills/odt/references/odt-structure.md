# ODT package structure (quick reference)

## Package basics
- ODT is a ZIP package with XML and assets.
- The package must contain `META-INF/manifest.xml` (manifest of files and media types).
- If a `mimetype` file exists, it must be the first file in the ZIP and uncompressed.
- The `mimetype` file contents must be ASCII and match the root media type.

## Core files and typical locations
- `content.xml` — main document content.
- `styles.xml` — styles used by the document.
- `meta.xml` — document metadata.
- `settings.xml` — document settings.
- `META-INF/manifest.xml` — package manifest.
- `Pictures/` — embedded images (if any).

## MIME type
- ODT media type: `application/vnd.oasis.opendocument.text`.

## Notes for repacking
- Always write `mimetype` first and uncompressed.
- Ensure `META-INF/manifest.xml` lists the root entry `/` and the file media types.
