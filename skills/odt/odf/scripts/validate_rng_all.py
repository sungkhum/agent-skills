#!/usr/bin/env python3
"""Wrapper for validate_rng_all."""

from __future__ import annotations

import runpy
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "validate_rng_all.py"
runpy.run_path(str(SCRIPT), run_name="__main__")
