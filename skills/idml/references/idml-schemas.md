# IDML schemas and validation

This skill intentionally does **not** require or embed any vendor-distributed schema bundles. Instead, use an **observed schema** built from your own IDML files. Treat it as a validation guide rather than a strict spec.

```bash
python scripts/observe_idml_schema.py /path/to/book.idml --out idml_observed_schema.json
```

This produces a JSON summary of element/attribute usage and helps you validate content-only changes without embedding external schema bundles.

Validate new files against the observed schema:

```bash
python scripts/validate_observed_schema.py idml/observed_schema/idml_observed_schema.json /path/to/book.idml --out idml_schema_report.json
```

Generate a coverage report to see which components and elements are represented:

```bash
python scripts/observed_schema_report.py idml/observed_schema/idml_observed_schema.json --out idml_schema_coverage.json
```

Compare a new observed schema against your baseline to see what changed:

```bash
python scripts/schema_delta_report.py idml/observed_schema/idml_observed_schema.json new_observed_schema.json --out idml_schema_delta.json
```

Generate a checklist for expanding coverage:

```bash
python scripts/coverage_checklist.py idml_schema_delta.json --out idml_schema_checklist.md
```

Combine multiple delta reports into a single coverage plan:

```bash
python scripts/coverage_plan.py English=english_schema_delta.json Khmer=khmer_schema_delta.json --out idml_schema_plan.md
```

Recommended workflow:
1. Unpack the IDML file.
2. Validate `designmap.xml` and component XML against the IDML schemas from the specification package.
3. Repack and validate the package with `scripts/validate_idml.py`.

If you do not have the schemas locally, use `validate_idml.py` for basic structural validation.
