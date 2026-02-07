# ODF schemas and validation

Use schema validation when making complex or low-level XML edits.

## Where schemas come from
- The authoritative ODF schemas are published by OASIS as Relax NG (RNG) bundles.
- The ODF 1.3 schema artifacts are available under the OASIS `schemas/` directory for the 1.3 Committee Specification.

Recommended layout:
```
odt/
  odf/
    schemas/
      odf-1.3/
        OpenDocument-v1.3-schema.rng
        OpenDocument-v1.3-manifest-schema.rng
        OpenDocument-v1.3-dsig-schema.rng
        OpenDocument-v1.3-metadata.owl
        OpenDocument-v1.3-package-metadata.owl
```

## Validation tools
- Use a Relax NG validator (e.g., `jing`) for RNG or RNC schemas.
- For packaging checks, use `scripts/validate_odt.py` to verify manifest consistency and `mimetype` placement.
  - Optional: use `scripts/fetch_odf_schemas.py` (or `odf/scripts/fetch_schemas.py`) to download the ODF 1.3 schema artifacts into `odf/schemas/odf-1.3`.
- RNG validation helper: `scripts/validate_rng.py <content.xml>` (uses jing under the hood).
- RNG batch helper: `scripts/validate_rng_all.py <unpacked_dir>` (validates content.xml, styles.xml, and manifest.xml).

## Minimal validation workflow
1. Unpack the ODT: `python odf/scripts/unpack.py file.odt unpacked`
2. Run package validation: `python scripts/validate_odt.py unpacked --original file.odt`
3. Fetch schemas (if needed): `python scripts/fetch_odf_schemas.py --out odf/schemas/odf-1.3`
4. Run RNG validation against `content.xml` and `styles.xml`:
   - `python scripts/validate_rng.py unpacked/content.xml`
   - `python scripts/validate_rng.py unpacked/styles.xml`
