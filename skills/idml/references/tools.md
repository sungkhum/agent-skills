# IDML tooling

## Exporting IDML
- Export from Adobe InDesign via **File → Export → InDesign Markup (IDML)**.

## Utilities
- `unpack_idml.py` / `pack_idml.py` — unzip/zip with correct IDML structure.
- `validate_idml.py` — basic package validation.
- `smoke_test.py` — roundtrip validation.

## XML editing
- Use `scripts/utilities.py` for line-based XML edits.
- Prefer editing specific component files (Stories/Spreads) instead of global rewrites.

## Translation helpers
- `extract_story_text.py` — extract Content nodes to JSONL
- `prepare_translation_jsonl.py` — add a blank translation field
- `apply_story_text.py` — apply translated text to Content nodes
- `compare_story_counts.py` — diff story counts between two extracts
- `align_story_text.py` — generate approximate alignment JSONL

## Reporting and safety checks
- `map_story_spreads.py` — map stories to spreads/pages
- `check_resources.py` — report fonts, styles, and linked assets
- `validate_content_only_changes.py` — assert only Content text changed
- `observe_idml_schema.py` — build an observed schema summary from sample IDMLs
- `validate_observed_schema.py` — validate IDML files against the observed schema
- `observed_schema_report.py` — coverage report for observed schema JSON
- `schema_delta_report.py` — compare two observed schema JSON files
- `coverage_checklist.py` — markdown checklist from a schema delta report
- `coverage_plan.py` — combined coverage plan from multiple delta reports
