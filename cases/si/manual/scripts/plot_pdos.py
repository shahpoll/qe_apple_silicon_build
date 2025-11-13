#!/usr/bin/env python3
"""Regenerate silicon projected DOS plot for the manual workflow."""

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
COMMON_SCRIPTS = ROOT / "cases" / "common" / "scripts"
if str(COMMON_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(COMMON_SCRIPTS))

import plot_si_pdos  # type: ignore  # pylint: disable=import-error

BASE_DIR = pathlib.Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    plot_si_pdos.main(BASE_DIR)
