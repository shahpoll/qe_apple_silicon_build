#!/usr/bin/env python3
"""Run a minimal SCF smoke test and validate energy/Fermi tolerances."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
INPUT = ROOT / "inputs" / "Si.scf.in"
RUN_QE = ROOT / "scripts" / "run_qe.sh"
REFERENCE = {
    "total_energy": -22.83927,
    "fermi": 6.4346,
    "tolerance_energy": 1e-3,
    "tolerance_fermi": 5e-3,
}


def resolve_pw() -> pathlib.Path | None:
    explicit_pw = os.environ.get("QE_PW_BIN")
    if explicit_pw:
        pw = pathlib.Path(explicit_pw).expanduser().resolve()
        if pw.exists():
            return pw

    qe_bin_path = os.environ.get("QE_BIN_PATH")
    if qe_bin_path:
        pw = pathlib.Path(qe_bin_path).expanduser().resolve() / "pw.x"
        if pw.exists():
            return pw

    candidates = [
        ROOT / "artifacts" / "q-e-qe-7.5" / "bin" / "pw.x",
        ROOT / "artifacts" / "q-e-qe-7.4.1" / "bin" / "pw.x",
        pathlib.Path.home() / "opt" / "qe-7.5" / "bin" / "pw.x",
        pathlib.Path.home() / "opt" / "qe-7.4.1" / "bin" / "pw.x",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    path_pw = shutil.which("pw.x")
    if path_pw:
        return pathlib.Path(path_pw).resolve()

    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QE SCF smoke test")
    parser.add_argument("--ranks", type=int, default=2, help="MPI ranks")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    pw_bin = resolve_pw()
    if pw_bin is None:
        print("pw.x not found. Set QE_PW_BIN/QE_BIN_PATH or build/install QE first.", file=sys.stderr)
        return 2
    if not INPUT.exists():
        print(f"Input file {INPUT} missing", file=sys.stderr)
        return 2
    if not RUN_QE.exists():
        print(f"Wrapper script missing at {RUN_QE}", file=sys.stderr)
        return 2

    tmp_out = ROOT / "tmp_smoke.out"
    env = os.environ.copy()
    env["QE_BIN_PATH"] = str(pw_bin.parent)
    env["QE_RANKS"] = str(args.ranks)
    env.setdefault("OMP_NUM_THREADS", "1")
    run_mode = "mpi"

    with tmp_out.open("w", encoding="utf-8") as handle:
        try:
            subprocess.run(
                [str(RUN_QE), "pw.x", "--", "-in", INPUT.name],
                stdout=handle,
                stderr=subprocess.STDOUT,
                cwd=INPUT.parent,
                env=env,
                check=True,
            )
        except subprocess.CalledProcessError:
            # Some restricted environments block OpenMPI socket setup.
            run_mode = "serial_fallback"
            handle.write("\n[smoke_test] MPI launch failed; retrying serial pw.x.\n")
            subprocess.run(
                [str(pw_bin), "-in", INPUT.name],
                stdout=handle,
                stderr=subprocess.STDOUT,
                cwd=INPUT.parent,
                check=True,
            )

    total_energy = None
    fermi = None
    for line in tmp_out.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("!    total energy"):
            total_energy = float(line.split("=")[-1].split()[0])
        if "the Fermi energy is" in line:
            fermi = float(line.split()[-2])

    results = {
        "total_energy": total_energy,
        "fermi": fermi,
        "pw_bin": str(pw_bin),
        "ranks": args.ranks,
        "mode": run_mode,
    }
    print(json.dumps(results, indent=2))

    tmp_out.unlink(missing_ok=True)
    shutil.rmtree(INPUT.parent / "tmp", ignore_errors=True)

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
