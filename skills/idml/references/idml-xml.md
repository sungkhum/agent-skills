# IDML XML reference (high level)

**Important: Read this file before editing XML directly.**

## Designmap
- `designmap.xml` is the root document and references component files.
- Component references include story and spread files (`Stories/Story_*.xml`, `Spreads/Spread_*.xml`).

## Stories
- Story files contain the document’s text content and text styling ranges.
- Spreads reference stories; story files do not include page geometry.

## Spreads
- Spread files define layout, pages, frames, and page items.
- Text frames reference story content (do not inline the full text in spreads).

## Master spreads
- Master spreads contain reusable layout elements and are applied to spreads/pages.

## Resources
- Shared resources live in `Resources/` (styles, fonts, preferences, graphics, etc.).
- When editing styles, check `Resources/Styles.xml` and the referencing structure in `designmap.xml`.

## Editing guidance
- Prefer minimal changes: update only the component file you need.
- Keep IDs consistent; do not regenerate IDs unless required.
- Validate the package after edits using `scripts/validate_idml.py`.

## Story text structure example
```xml
<ParagraphStyleRange AppliedParagraphStyle="ParagraphStyle/Body">
  <CharacterStyleRange AppliedCharacterStyle="CharacterStyle/$ID/[No character style]">
    <Content>Hello world</Content>
  </CharacterStyleRange>
</ParagraphStyleRange>
```
