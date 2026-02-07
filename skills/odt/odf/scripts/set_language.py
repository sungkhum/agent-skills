#!/usr/bin/env python3
"""Wrapper for language settings script."""

from __future__ import annotations

import runpy
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "set_language.py"
runpy.run_path(str(SCRIPT), run_name="__main__")
