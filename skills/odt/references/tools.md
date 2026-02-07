# ODT tooling quick reference

## Python libraries
- **odfdo**: High-level ODF/ODT manipulation library with CLI utilities.
- **odfpy**: Lower-level library for ODF/ODT with direct element access.

## odfdo CLI utilities (examples)
- `odfdo-show <file.odt>` — inspect structure and content.
- `odfdo-markdown <file.odt> > output.md` — extract to Markdown.
- `odfdo-replace <file.odt> <search> <replace> -o out.odt` — simple text replacement.
- `odfdo-style -l <file.odt>` — list styles.

## Converters
- **pandoc**: Convert ODT to/from Markdown and other formats.
- **LibreOffice (soffice)**: Headless conversion to PDF.
- **Poppler (pdftoppm)**: Render PDF pages to images.
- **jing** (optional): Relax NG validation for ODF schema checks.

## Library usage hints
- Prefer odfdo for common edits and safer, higher-level operations.
- Use odfpy when you need direct control of ODF elements or strict schema-level operations.
