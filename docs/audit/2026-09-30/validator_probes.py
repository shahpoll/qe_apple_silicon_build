#!/usr/bin/env python3
"""Reproduce validator false positives using injected output, not QE calculations.

Run from any directory with the project's numpy/matplotlib dependencies:
    python3 docs/audit/2026-09-30/validator_probes.py

All campaign outputs and fake binaries are isolated in a fresh temporary folder.
Only subprocess execution, plotting, system metadata and linkage are substituted;
campaign decisions, result tables, parsing and advanced workflow gates are the
production implementation. These probes demonstrate acceptance-policy defects;
they do not measure the scientific accuracy of any installed QE binary.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import os
import pathlib
import sys
import tempfile
from argparse import Namespace

ROOT = pathlib.Path(__file__).resolve().parents[3]
SOURCE = ROOT / "scripts" / "validate_build.py"


def load_validator(module_name: str):
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(module_name, SOURCE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def read_tsv(path: pathlib.Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def probe() -> dict:
    base = pathlib.Path(tempfile.mkdtemp(prefix="qe-validator-audit-"))
    os.environ.setdefault("MPLCONFIGDIR", str(base / "mplconfig"))
    module = load_validator("qe_validation_audit")
    qe_bin = base / "bin"
    qe_bin.mkdir()
    for name in {"pw.x", "ph.x", "wannier90.x", "pw2wannier90.x", *module.MODULE_EXECUTABLES}:
        (qe_bin / name).touch()

    def fake_command(cmd, *, cwd, log_path, **kwargs):
        exe = pathlib.Path(cmd[0]).name
        text, rc = "JOB DONE.\n", 0
        if exe in module.MODULE_EXECUTABLES and len(cmd) == 1:
            text, rc = "Program TEST starts\nFATAL injected calculation error\n", 99
        elif exe == "wannier90.x":
            (cwd / "siepw.nnkp").touch()
        elif exe == "neb.x":
            # No energy, profile, or convergence evidence.
            rc = 1
        elif exe == "epw.x":
            # A section heading with no completion or numerical evidence.
            text = "Electron-Phonon interpolation\n"
        log_path.write_text(text, encoding="utf-8")
        return rc, 0.01

    def fake_mpi(exe, input_file, *, ranks, cwd, log_path, **kwargs):
        energy = -17.83927198  # intentional +5 Ry versus built-in reference
        if log_path.stem.startswith("scf_rank_"):
            energy = -22.0 + ranks
        if log_path.stem.startswith("scf_repeat_"):
            energy = -22.0 + int(log_path.stem.rsplit("_", 1)[1])
        log_path.write_text(
            f"!    total energy = {energy} Ry\n"
            "the Fermi energy is 99.0 ev\n"
            "convergence NOT achieved\nJOB DONE.\n",
            encoding="utf-8",
        )
        (cwd / "silicon.dos").write_text("# EFermi = 6.2130 eV\n0 1\n", encoding="utf-8")
        (cwd / "silicon.bands.dat.gnu").write_text(
            "0 1.0\n1 1.0\n\n0 9.0\n1 9.0\n", encoding="utf-8"
        )
        return 0, 0.01

    module.run_command = fake_command
    module.run_mpi_qe = fake_mpi
    module.linkage_check = lambda *args: (True, "stubbed linkage")
    module.run_plot_script = lambda *args: (0, 0.01)
    module.system_metadata = lambda: dict(
        timestamp="audit probe", uname="stub", sw_vers="stub", python="stub", mpirun="stub"
    )
    for name in [
        "plot_category_pass_fail", "plot_rank_sweep", "plot_repeatability",
        "plot_metric_deltas", "plot_advanced_module_durations",
    ]:
        setattr(module, name, lambda *args: None)

    def run_campaign(name: str, *, omit_metrics=False, empty_repro=False) -> dict:
        out_dir = base / name
        original_parser = module.parse_dos_fermi
        if omit_metrics:
            def missing_metric(path):
                raise RuntimeError("injected missing metrics")
            module.parse_dos_fermi = missing_metric
        try:
            rc = module.campaign(Namespace(
                qe_bin=qe_bin, out_dir=out_dir,
                rank_sweep="" if empty_repro else "1,2", pipeline_ranks=2,
                repeat_count=0 if empty_repro else 2, timeout=1, keep_work=True,
            ))
        finally:
            module.parse_dos_fermi = original_parser
        cases = read_tsv(out_dir / "tables" / "final_matrix.tsv")
        relevant = (
            "pw_scf", "scf_rank_", "scf_repeat_", "module_cp_", "neb_path_mini", "epw_interp"
        )
        return {
            "exit_code": rc,
            "pass_count": sum(row["status"] == "PASS" for row in cases),
            "fail_count": sum(row["status"] == "FAIL" for row in cases),
            "selected_cases": [row for row in cases if row["case"].startswith(relevant)],
            "metrics": read_tsv(out_dir / "tables" / "metrics_compare.tsv"),
            "rank_runs": read_tsv(out_dir / "tables" / "scf_rank_sweep.tsv"),
            "repeat_runs": read_tsv(out_dir / "tables" / "scf_repeatability.tsv"),
        }

    results = {
        "method": "Synthetic fault injection into production validator; no real QE execution.",
        "source": "scripts/validate_build.py",
        "wrong_numbers_and_nonconvergence": run_campaign("wrong_numbers"),
        "unavailable_metrics": run_campaign("unavailable_metrics", omit_metrics=True),
        "empty_reproducibility": run_campaign("empty_reproducibility", empty_repro=True),
    }

    # Exercise production MPI fallback with only its command runner substituted.
    real_module = load_validator("qe_validation_fallback_audit")
    seen = []

    def socket_then_serial(cmd, *, log_path, **kwargs):
        seen.append([pathlib.Path(item).name if str(qe_bin) in item else item for item in cmd])
        with log_path.open("a" if kwargs.get("append") else "w", encoding="utf-8") as handle:
            handle.write(
                "PRTE ERROR: No network interfaces were found\n" if cmd[0] == "mpirun" else
                "!    total energy = -22.0 Ry\nthe Fermi energy is 6.0 ev\nJOB DONE.\n"
            )
        return (1 if cmd[0] == "mpirun" else 0), 0.01

    real_module.run_command = socket_then_serial
    rc, duration = real_module.run_mpi_qe(
        qe_bin / "pw.x", pathlib.Path("unused.in"), ranks=8, cwd=base,
        log_path=base / "fallback.log", timeout_s=1,
    )
    results["serial_fallback"] = {
        "requested_ranks": 8, "return_code": rc, "executed_commands": seen,
        "returned_metadata": ["return_code", "duration"],
    }
    results["parser_acceptance"] = {
        "first_not_last_energy": real_module.parse_total_energy(
            "!    total energy = -20 Ry\n!    total energy = -30 Ry\n"
        ),
        "nonfinite_energy": str(real_module.parse_total_energy("!    total energy = nan Ry\n")),
        "nonfinite_fermi": str(real_module.parse_fermi("the Fermi energy is inf ev")),
    }
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=pathlib.Path, help="Optional path for concise JSON evidence.")
    args = parser.parse_args()
    serialized = json.dumps(probe(), indent=2) + "\n"
    if args.results is not None:
        args.results.write_text(serialized, encoding="utf-8")
        print(args.results)
    else:
        print(serialized, end="")


if __name__ == "__main__":
    main()
