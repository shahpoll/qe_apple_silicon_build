#!/usr/bin/env python3
"""Run a minimal SCF smoke test and validate energy/Fermi tolerances."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
PW_BIN = ROOT / "artifacts" / "q-e-qe-7.4.1" / "bin" / "pw.x"
INPUT = ROOT / "inputs" / "Si.scf.in"
REFERENCE = {
    "total_energy": -22.83927,
    "fermi": 6.4346,
    "tolerance_energy": 1e-3,
    "tolerance_fermi": 5e-3,
}


def main() -> int:
    if not PW_BIN.exists():
        print(f"pw.x not found at {PW_BIN}; build QE first.", file=sys.stderr)
        return 2
    if not INPUT.exists():
        print(f"Input file {INPUT} missing", file=sys.stderr)
        return 2

    tmp_out = ROOT / "tmp_smoke.out"
    with tmp_out.open("w", encoding="utf-8") as handle:
        subprocess.run(["mpirun", "-n", "2", str(PW_BIN), "-in", str(INPUT)], stdout=handle, stderr=subprocess.STDOUT, check=True)

    total_energy = None
    fermi = None
    for line in tmp_out.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("!    total energy"):
            total_energy = float(line.split("=")[-1].split()[0])
        if "the Fermi energy is" in line:
            fermi = float(line.split()[-2])

    results = {"total_energy": total_energy, "fermi": fermi}
    print(json.dumps(results, indent=2))

    tmp_out.unlink(missing_ok=True)

    if total_energy is None or fermi is None:
        print("Could not parse total energy or Fermi level", file=sys.stderr)
        return 1

    if abs(total_energy - REFERENCE["total_energy"]) > REFERENCE["tolerance_energy"]:
        print("Total energy outside tolerance", file=sys.stderr)
        return 1
    if abs(fermi - REFERENCE["fermi"]) > REFERENCE["tolerance_fermi"]:
        print("Fermi energy outside tolerance", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
