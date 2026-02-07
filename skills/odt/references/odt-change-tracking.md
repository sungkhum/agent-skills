# ODT tracked changes (ODF)

ODF change tracking is represented in XML using tracked-change containers, change records, and change markers.

## Core elements
- `text:tracked-changes` — container listing change entries.
- `text:changed-region` — associates a change record with the document.
- `text:insertion` — inserted content (change record).
- `text:deletion` — deleted content (change record).
- `text:format-change` — formatting-only change (change record).
- `text:change-start` / `text:change-end` — range markers for changes.
- `text:change` — change marker for point changes (often deletions).
- `office:change-info` — metadata about who/when made the change.

## How it fits together
1. A `text:changed-region` entry appears in `text:tracked-changes`.
2. The document content contains `text:change-start` / `text:change-end` (or `text:change`) markers that reference that change-id.
3. The `text:changed-region` contains the `text:insertion`, `text:deletion`, or `text:format-change` element with `office:change-info`.

## Minimal example
```xml
<text:tracked-changes>
  <text:changed-region text:id="ct12345678">
    <text:insertion>
      <office:change-info>
        <dc:creator>Jane Doe</dc:creator>
        <dc:date>2026-02-03T10:20:30Z</dc:date>
      </office:change-info>
      <text:p>Inserted text</text:p>
    </text:insertion>
  </text:changed-region>
</text:tracked-changes>

<!-- In document content: -->
<text:change-start text:change-id="ct12345678"/>
<text:p>Inserted text</text:p>
<text:change-end text:change-id="ct12345678"/>
```

## Practical guidance
- Use `text:change-start` and `text:change-end` for insertions and format changes that span a range.
- Use `text:change` for point changes that do not span a range.
- Keep changes minimal and localized to avoid noisy reviews.

## Validation tips
- Re-open with LibreOffice to confirm change tracking renders correctly.
- Re-convert to Markdown (pandoc or odfdo) for a quick textual diff.
- Run `scripts/validate_changes.py content.xml` to catch missing change records or unmatched markers.
