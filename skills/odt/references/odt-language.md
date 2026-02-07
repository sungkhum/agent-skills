# Language and locale handling (ODF)

ODF language properties are set on `style:text-properties` and can be applied at the paragraph, span, or style level. Language values should follow BCP 47 language tags (e.g., `km`, `en-US`).

## Common attributes
Use the attributes that match the pattern already present in the document (LibreOffice often uses `style:language-*` and `style:country-*` for complex/Asian script variants).

- `fo:language` — base language.
- `fo:country` — base country/region.
- `fo:language-asian` — Asian script language.
- `fo:language-complex` — complex script language.
- `style:language-asian` — Asian script language (alternate form in some producers).
- `style:language-complex` — complex script language (alternate form in some producers).
- `style:country-asian` — Asian script country/region.
- `style:country-complex` — complex script country/region.

## Khmer (example)
- Use language tag `km` and region `KH` where applicable.
- For complex scripts, set `fo:language-complex="km"` (or `style:language-complex="km"` if that is what the file already uses) and `style:country-complex="KH"` on the relevant `style:text-properties`.
- Assign a Khmer-capable font in `style:text-properties` to ensure shaping and glyph coverage.
  - Helper: `python scripts/set_language.py styles.xml --lang km --country KH --font "Khmer OS System"`

## Where to set
- `styles.xml` for document-wide styles.
- `content.xml` (automatic styles or inline `text:span`) for localized runs.
