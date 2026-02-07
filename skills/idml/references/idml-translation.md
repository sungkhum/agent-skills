# IDML translation workflow

Use this workflow to extract text from IDML, translate it, and reapply translations while preserving layout and styles.

## Core idea
- **Text lives in Stories** (`Stories/*.xml`) inside `<Content>` nodes.
- **Layout lives in Spreads**; do not edit layout files when translating.
- Preserve all structure and IDs; only replace `<Content>` node text.

## Extraction
```bash
python scripts/unpack_idml.py book.idml unpacked
python scripts/extract_story_text.py unpacked translations.jsonl
```

This produces JSONL records with:
- `story` (story filename)
- `index` (content index in that story)
- `paragraph_style` / `character_style`
- `text` (original text)

## Translation
Translate the `text` field and add a `translation` field in the same JSONL records. Preserve ordering and IDs.

## Apply translations
```bash
python scripts/apply_story_text.py unpacked translations.jsonl
python scripts/pack_idml.py unpacked translated.idml
python scripts/validate_idml.py unpacked --original translated.idml
```

## Notes
- Some stories may be empty or contain only non-text elements. That is normal.
- Content may be split across multiple nodes; keep the order intact.
- Use styles as a guide for mapping if you need to align bilingual books.
- If you need layout context, map stories to spreads and pages using the story map tool.

## Alignment and diff reports
Generate a story count report:

```bash
python scripts/compare_story_counts.py english.jsonl khmer.jsonl --out story_counts.json
```

Generate an approximate alignment file:

```bash
python scripts/align_story_text.py english.jsonl khmer.jsonl --out alignment.jsonl
```

Use the alignment JSONL for manual review and mapping. It does not rewrite IDML.

## Story-to-spread mapping
Generate a report that maps story IDs to spreads/pages:

```bash
python scripts/map_story_spreads.py unpacked --out story_spreads.json
```

## Resource checks
Check fonts, styles, and linked assets:

```bash
python scripts/check_resources.py unpacked --out resources_report.json
```

## Content-only validation
Confirm that only `<Content>` node text changed (no layout edits):

```bash
python scripts/validate_content_only_changes.py original_unpacked translated_unpacked
```
