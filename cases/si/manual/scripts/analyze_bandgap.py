#!/usr/bin/env python3
"""Write band-gap summary for the manual silicon workflow."""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
COMMON_SCRIPTS = ROOT / "cases" / "common" / "scripts"
if str(COMMON_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(COMMON_SCRIPTS))

import analyze_si_bandgap  # type: ignore  # pylint: disable=import-error

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    analyze_si_bandgap.main(BASE_DIR)
