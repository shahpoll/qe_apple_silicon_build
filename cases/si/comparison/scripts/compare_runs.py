#!/usr/bin/env python3
"""Generate manual vs PWTK silicon comparison plots and metrics."""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
COMMON_SCRIPTS = ROOT / "cases" / "common" / "scripts"
if str(COMMON_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(COMMON_SCRIPTS))

import compare_si_runs  # type: ignore  # pylint: disable=import-error

MANUAL = ROOT / "cases" / "si" / "manual"
PWTK = ROOT / "cases" / "si" / "pwtk"

if __name__ == "__main__":
    compare_si_runs.compare(MANUAL, PWTK)
