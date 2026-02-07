# ODF XML technical reference (ODT)

**Important: Read this entire document before starting.** This file provides XML patterns for headings, lists, tables, images, hyperlinks, bookmarks, notes, and tracked changes. Use it when editing ODT files directly in `content.xml` and `styles.xml`.

## Technical guidelines

- Keep existing namespaces on the root element; add new namespaces only when required.
- Preserve `office:version` on the root elements of `content.xml` and `styles.xml`.
- Use `styles.xml` for named styles and page styles; use `content.xml` automatic styles for inline or one-off changes.
- When adding new files (images, RDF, etc.), update `META-INF/manifest.xml`.

## Document content patterns

### Paragraph and text styles (in styles.xml)
```xml
<style:style style:name="Text_20_body" style:family="paragraph" style:class="text">
  <style:paragraph-properties fo:margin-bottom="0.0835in"/>
  <style:text-properties fo:font-size="12pt" fo:language="en" fo:country="US"/>
</style:style>

<style:style style:name="Emphasis" style:family="text">
  <style:text-properties fo:font-style="italic"/>
</style:style>
```

**Tip:** If the document already defines styles, reuse or extend them instead of creating new ones.

### Paragraphs
```xml
<text:p text:style-name="Text_20_body">Regular paragraph text.</text:p>
```

### Headings
```xml
<text:h text:style-name="Heading_20_1" text:outline-level="1">Heading 1</text:h>
<text:h text:style-name="Heading_20_2" text:outline-level="2">Heading 2</text:h>
```

### Inline spans
```xml
<text:p>
  Normal text
  <text:span text:style-name="Emphasis">emphasis</text:span>
  and normal text again.
</text:p>
```

### Line breaks
```xml
<text:p>Line 1<text:line-break/>Line 2</text:p>
```

### Whitespace, tabs, and soft breaks
```xml
<text:p>
  <text:s text:c="3"/>  <!-- 3 spaces -->
  <text:tab/>           <!-- tab stop -->
  <text:soft-page-break/>
</text:p>
```

### Lists
```xml
<text:list text:style-name="List_1">
  <text:list-item>
    <text:p>First item</text:p>
  </text:list-item>
  <text:list-item>
    <text:p>Second item</text:p>
  </text:list-item>
</text:list>
```

### List styles (in styles.xml)
```xml
<text:list-style style:name="List_1">
  <text:list-level-style-bullet text:level="1" text:bullet-char="•">
    <style:list-level-properties text:list-level-position-and-space-mode="label-alignment"/>
  </text:list-level-style-bullet>
</text:list-style>
```

### Tables
```xml
<table:table table:name="Table1" table:style-name="Table1">
  <table:table-column table:number-columns-repeated="2"/>
  <table:table-row>
    <table:table-cell office:value-type="string">
      <text:p>Cell 1</text:p>
    </table:table-cell>
    <table:table-cell office:value-type="string">
      <text:p>Cell 2</text:p>
    </table:table-cell>
  </table:table-row>
</table:table>
```

### Table styles (in styles.xml)
```xml
<style:style style:name="Table1" style:family="table">
  <style:table-properties table:display="true"/>
</style:style>
```

### Images
```xml
<draw:frame draw:name="Image1" text:anchor-type="as-char" svg:width="2in" svg:height="1.5in">
  <draw:image xlink:href="Pictures/image1.png" xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/>
</draw:frame>
```

**Remember:** add the image file under `Pictures/` and update `META-INF/manifest.xml` with the new file entry.

### Frames and text boxes
Text boxes are stored in a `draw:frame` containing a `draw:text-box`, which itself contains paragraph content.
```xml
<draw:frame draw:name="TextBox1" text:anchor-type="as-char" svg:width="2in" svg:height="1in">
  <draw:text-box>
    <text:p>Text inside a box.</text:p>
  </draw:text-box>
</draw:frame>
```

### Hyperlinks
```xml
<text:a xlink:href="https://example.com" xlink:type="simple" text:style-name="Internet_20_link">
  Example link
</text:a>
```

### Comments (annotations)
Use the existing annotation pattern in the document. Typical structure looks like:
```xml
<office:annotation>
  <dc:creator>Author Name</dc:creator>
  <dc:date>2026-02-02T12:34:56Z</dc:date>
  <text:p>Comment text.</text:p>
</office:annotation>
```
If the file uses a range comment, you may also see a matching end marker:
```xml
<office:annotation office:name="c1">
  <dc:creator>Author Name</dc:creator>
  <dc:date>2026-02-02T12:34:56Z</dc:date>
  <text:p>Comment text.</text:p>
</office:annotation>
<office:annotation-end office:name="c1"/>
```

### Bookmarks
```xml
<text:bookmark-start text:name="bm1"/>
<text:p>Target paragraph</text:p>
<text:bookmark-end text:name="bm1"/>
```

### Notes (footnotes/endnotes)
```xml
<text:note text:note-class="footnote">
  <text:note-citation>1</text:note-citation>
  <text:note-body>
    <text:p>Footnote text.</text:p>
  </text:note-body>
</text:note>
```

### Variables and fields
Declare variables before use, then set/get values in content:
```xml
<text:variable-decls>
  <text:variable-decl text:name="CaseNumber" office:value-type="string"/>
</text:variable-decls>

<text:p>
  <text:variable-set text:name="CaseNumber" office:value-type="string">2025-001</text:variable-set>
  <text:variable-get text:name="CaseNumber"/>
</text:p>
```

### Table of contents (TOC)
Tables of contents are represented with `text:table-of-content`, which contains a `text:table-of-content-source` and `text:index-body`.
```xml
<text:table-of-content text:name="Table of Contents">
  <text:table-of-content-source/>
  <text:index-body>
    <text:index-title><text:p>Table of Contents</text:p></text:index-title>
  </text:index-body>
</text:table-of-content>
```

### Page breaks
Define a paragraph style that forces a page break:
```xml
<style:style style:name="PageBreak" style:family="paragraph">
  <style:paragraph-properties fo:break-before="page"/>
</style:style>
```
Then use it:
```xml
<text:p text:style-name="PageBreak"/>
```

### Headers and footers
Headers/footers live in `styles.xml` under a master page:
```xml
<style:master-page style:name="Standard" style:page-layout-name="Mpm1">
  <style:header>
    <text:p>Header text</text:p>
  </style:header>
  <style:footer>
    <text:p>Footer text</text:p>
  </style:footer>
</style:master-page>
```

### Sections
```xml
<text:section text:name="Section1">
  <text:p>Section content.</text:p>
</text:section>
```

## Tracked changes (overview)

Tracked changes use a change record and one or more change markers:

1. Add a `text:changed-region` entry inside `text:tracked-changes`.
2. Insert `text:change-start` and `text:change-end` markers in the content (or `text:change` for point changes).
3. Inside `text:changed-region`, add `text:insertion`, `text:deletion`, or `text:format-change` with `office:change-info`.

See `references/odt-change-tracking.md` for structure and guidance.

### Tracked changes (inline markers example)
```xml
<text:change-start text:change-id="ct12345678"/>
<text:p text:style-name="Text_20_body">Inserted text</text:p>
<text:change-end text:change-id="ct12345678"/>
```
