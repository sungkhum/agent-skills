#!/usr/bin/env python3
"""Wrapper for tracked-changes validation."""

from __future__ import annotations

import runpy
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "validate_changes.py"
runpy.run_path(str(SCRIPT), run_name="__main__")
