#!/usr/bin/env python3
"""Run a basic IDML roundtrip smoke test and validations."""

from __future__ import annotations

import argparse
import runpy
import sys
from pathlib import Path


def _run_script(script: Path, args: list[str]) -> None:
    old_argv = sys.argv
    try:
        sys.argv = [str(script)] + args
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit as exc:
        if exc.code not in (0, None):
            raise
    finally:
        sys.argv = old_argv


def main() -> int:
    parser = argparse.ArgumentParser(description="IDML smoke test")
    parser.add_argument("idml_file", help="Path to .idml file")
    parser.add_argument("work_dir", help="Working directory")
    parser.add_argument("--out", default="roundtrip.idml", help="Output IDML filename")
    parser.add_argument("--schema", help="Observed schema JSON file")
    parser.add_argument("--schema-report", help="Write observed schema reports (base path or .json)")
    parser.add_argument("--schema-strict", action="store_true", help="Fail if schema validation reports issues")
    args = parser.parse_args()

    idml_file = Path(args.idml_file)
    work_dir = Path(args.work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    unpack_dir = work_dir / "unpacked"
    out_file = work_dir / args.out

    scripts_dir = Path(__file__).resolve().parent

    _run_script(scripts_dir / "unpack_idml.py", [str(idml_file), str(unpack_dir)])
    _run_script(scripts_dir / "validate_idml.py", [str(unpack_dir), "--original", str(idml_file)])
    if args.schema:
        schema_reports = _schema_report_paths(args.schema_report, work_dir)
        _run_script(
            scripts_dir / "validate_observed_schema.py",
            _schema_args(args.schema, idml_file, schema_reports[0], args.schema_strict),
        )
    _run_script(scripts_dir / "pack_idml.py", [str(unpack_dir), str(out_file)])
    _run_script(scripts_dir / "validate_idml.py", [str(unpack_dir), "--original", str(out_file)])
    if args.schema:
        schema_reports = _schema_report_paths(args.schema_report, work_dir)
        _run_script(
            scripts_dir / "validate_observed_schema.py",
            _schema_args(args.schema, out_file, schema_reports[1], args.schema_strict),
        )

    print(f"Smoke test completed: {out_file}")
    return 0


def _schema_report_paths(report_arg: str | None, work_dir: Path) -> tuple[str | None, str | None]:
    if not report_arg:
        return (None, None)

    report_path = Path(report_arg)
    if report_path.suffix.lower() == ".json":
        base = report_path
    else:
        base = report_path / "schema_report.json"

    base = base if base.is_absolute() else (work_dir / base)
    base.parent.mkdir(parents=True, exist_ok=True)

    return (
        str(base.with_name(base.stem + "_original" + base.suffix)),
        str(base.with_name(base.stem + "_roundtrip" + base.suffix)),
    )


def _schema_args(schema: str, idml_path: Path, report_path: str | None, strict: bool) -> list[str]:
    args = [schema, str(idml_path)]
    if report_path:
        args.extend(["--out", report_path])
    if strict:
        args.append("--strict")
    return args


if __name__ == "__main__":
    raise SystemExit(main())
