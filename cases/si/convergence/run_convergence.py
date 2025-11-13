#!/usr/bin/env python3
"""Run cutoff and k-point convergence studies for silicon."""

from __future__ import annotations

import json
import math
import pathlib
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
PW_BIN = ROOT / "artifacts" / "q-e-qe-7.4.1" / "bin" / "pw.x"
BANDS_BIN = ROOT / "artifacts" / "q-e-qe-7.4.1" / "bin" / "bands.x"
COMMON_SCRIPTS = ROOT / "cases" / "common" / "scripts"
if str(COMMON_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(COMMON_SCRIPTS))

import analyze_si_bandgap  # type: ignore  # noqa: E402

RY_TO_EV = 13.605693009
N_ATOMS = 2
PP_DIR = ROOT / "cases" / "common" / "pp"

CUTOFF_LIST = [30, 40, 50, 60]
KMESH_LIST = [4, 6, 8, 10]

RUN_ROOT = ROOT / "cases" / "si" / "convergence"
CUTOFF_DIR = RUN_ROOT / "cutoff"
KMESH_DIR = RUN_ROOT / "kmesh"


@dataclass
class RunResult:
    label: str
    total_energy_ry: float
    fermi_ev: float
    band_gap_ev: float
    direct_gap_ev: float
    info: dict[str, float]

    @property
    def energy_mev_per_atom(self) -> float:
        return (self.total_energy_ry * RY_TO_EV * 1000.0) / N_ATOMS


def write_file(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def run_command(cmd: Sequence[str], log_path: pathlib.Path, workdir: pathlib.Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log_file:
        subprocess.run(cmd, check=True, stdout=log_file, stderr=subprocess.STDOUT, cwd=workdir)


def parse_total_energy(output_path: pathlib.Path) -> float:
    for line in output_path.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("!    total energy"):
            token = line.split("=")[-1].split()[0]
            return float(token)
    raise RuntimeError(f"total energy not found in {output_path}")


def parse_fermi(output_path: pathlib.Path) -> float:
    for line in output_path.read_text(encoding="utf-8").splitlines():
        if "the Fermi energy is" in line:
            return float(line.split()[-2])
    raise RuntimeError(f"Fermi energy not found in {output_path}")


def build_scf_input(*, ecut: float, ecutrho: float, kmesh: int, prefix: str, outdir: str) -> str:
    return f"""&control
  calculation='scf', prefix='{prefix}', pseudo_dir='{PP_DIR}', outdir='{outdir}'
/
&system
  ibrav=2, celldm(1)=10.26, nat=2, ntyp=1,
  ecutwfc={ecut:.1f}, ecutrho={ecutrho:.1f},
  occupations='smearing', smearing='mp', degauss=0.02
/
&electrons
  conv_thr=1.0d-8, mixing_beta=0.7
/
ATOMIC_SPECIES
 Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF
ATOMIC_POSITIONS crystal
 Si 0.00 0.00 0.00
 Si 0.25 0.25 0.25
K_POINTS automatic
 {kmesh} {kmesh} {kmesh}  0 0 0
"""


def build_bands_input(*, ecut: float, ecutrho: float, prefix: str, outdir: str) -> str:
    return f"""&control
  calculation='bands', prefix='{prefix}', pseudo_dir='{PP_DIR}', outdir='{outdir}'
/
&system
  ibrav=2, celldm(1)=10.26, nat=2, ntyp=1,
  ecutwfc={ecut:.1f}, ecutrho={ecutrho:.1f},
  occupations='smearing', smearing='mp', degauss=0.02
/
&electrons
  conv_thr=1.0d-8, mixing_beta=0.7
/
ATOMIC_SPECIES
 Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF
ATOMIC_POSITIONS crystal
 Si 0.00 0.00 0.00
 Si 0.25 0.25 0.25
K_POINTS crystal_b
 6
 0.0000 0.0000 0.0000 40
 0.5000 0.0000 0.5000 40
 0.5000 0.2500 0.7500 40
 0.3750 0.3750 0.7500 40
 0.0000 0.0000 0.0000 40
 0.5000 0.5000 0.5000 40
"""


def run_single_case(run_dir: pathlib.Path, settings: dict[str, float]) -> RunResult:
    run_dir.mkdir(parents=True, exist_ok=True)
    prefix = settings["label"]
    outdir = f"./tmp_{prefix}"
    ecut = settings["ecut"]
    ecutrho = settings["ecutrho"]
    kmesh = int(settings["kmesh"])

    scf_input = run_dir / "scf.in"
    bands_input = run_dir / "bands.in"
    bands_post = run_dir / "bands_post.in"
    scf_log = run_dir / "scf.out"
    bands_log = run_dir / "bands.out"
    post_log = run_dir / "bands_post.out"

    write_file(scf_input, build_scf_input(ecut=ecut, ecutrho=ecutrho, kmesh=kmesh, prefix=prefix, outdir=outdir))
    write_file(bands_input, build_bands_input(ecut=ecut, ecutrho=ecutrho, prefix=prefix, outdir=outdir))
    write_file(bands_post, "&bands\n  prefix='" + prefix + "', outdir='" + outdir + "', filband='silicon.bands.dat'\n/\n")

    run_command(["mpirun", "-n", "2", str(PW_BIN), "-in", scf_input.name], scf_log, run_dir)
    run_command(["mpirun", "-n", "2", str(PW_BIN), "-in", bands_input.name], bands_log, run_dir)
    run_command(["mpirun", "-n", "2", str(BANDS_BIN), "-in", bands_post.name], post_log, run_dir)

    total_energy = parse_total_energy(scf_log)
    fermi = parse_fermi(scf_log)

    bands_path = run_dir / "silicon.bands.dat.gnu"
    if not bands_path.exists():
        raise RuntimeError(f"bands data missing: {bands_path}")
    _, energies = analyze_si_bandgap.read_bands(bands_path)
    with np.errstate(invalid="ignore"):
        valence = np.where(energies <= fermi, energies, -math.inf)
        conduction = np.where(energies >= fermi, energies, math.inf)
    v_max = float(np.max(valence))
    c_min = float(np.min(conduction))
    indirect_gap = c_min - v_max

    deltas = conduction - valence
    direct_gap = float(np.min(deltas))

    result = RunResult(
        label=prefix,
        total_energy_ry=total_energy,
        fermi_ev=fermi,
        band_gap_ev=indirect_gap,
        direct_gap_ev=direct_gap,
        info={"ecut": ecut, "ecutrho": ecutrho, "kmesh": float(kmesh)},
    )
    tmp_path = (run_dir / outdir).resolve()
    if tmp_path.is_dir():
        shutil.rmtree(tmp_path)
    return result


def to_table(results: list[RunResult], reference: RunResult) -> list[dict[str, float]]:
    ref_energy = reference.energy_mev_per_atom
    ref_gap = reference.band_gap_ev
    table: list[dict[str, float]] = []
    for res in results:
        entry = {
            "label": res.label,
            "ecut": res.info["ecut"],
            "ecutrho": res.info["ecutrho"],
            "kmesh": res.info["kmesh"],
            "total_energy_meV_per_atom": res.energy_mev_per_atom,
            "delta_energy_meV_per_atom": res.energy_mev_per_atom - ref_energy,
            "gap_eV": res.band_gap_ev,
            "delta_gap_meV": (res.band_gap_ev - ref_gap) * 1000.0,
        }
        table.append(entry)
    return table


def save_results(results: list[RunResult], out_dir: pathlib.Path, stem: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    reference = results[-1]
    table = to_table(results, reference)
    (out_dir / f"{stem}.json").write_text(json.dumps(table, indent=2), encoding="utf-8")

    header = [
        "label",
        "ecut (Ry)",
        "ecutrho (Ry)",
        "kmesh",
        "E (meV/atom)",
        "ΔE (meV/atom)",
        "gap (eV)",
        "Δgap (meV)",
    ]
    lines = [",".join(header)]
    for row in table:
        lines.append(
            ",".join(
                [
                    row["label"],
                    f"{row['ecut']:.1f}",
                    f"{row['ecutrho']:.1f}",
                    f"{int(row['kmesh'])}",
                    f"{row['total_energy_meV_per_atom']:.4f}",
                    f"{row['delta_energy_meV_per_atom']:.4f}",
                    f"{row['gap_eV']:.4f}",
                    f"{row['delta_gap_meV']:.2f}",
                ]
            )
        )
    (out_dir / f"{stem}.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # Simple plot: ΔE vs parameter
    if stem == "cutoff" or stem == "kmesh":
        x_vals = [row["ecut"] if stem == "cutoff" else row["kmesh"] for row in table]
        y_vals = [row["delta_energy_meV_per_atom"] for row in table]
        plt.figure(figsize=(5, 3), dpi=150)
        plt.plot(x_vals, y_vals, marker="o")
        plt.axhline(0.0, color="gray", linestyle="--", linewidth=0.8)
        plt.xlabel("ecutwfc (Ry)" if stem == "cutoff" else "k-point mesh (N×N×N)")
        plt.ylabel("ΔE (meV/atom)")
        plt.title(f"Si convergence: {stem}")
        plt.tight_layout()
        plt.savefig(out_dir / f"{stem}_deltaE.png")
        plt.close()


def main() -> None:
    cutoff_results: list[RunResult] = []
    for ecut in CUTOFF_LIST:
        settings = {
            "label": f"cutoff_{int(ecut)}",
            "ecut": float(ecut),
            "ecutrho": float(ecut * 8),
            "kmesh": 6.0,
        }
        result = run_single_case(CUTOFF_DIR / settings["label"], settings)
        cutoff_results.append(result)

    save_results(cutoff_results, CUTOFF_DIR, "cutoff")

    kmesh_results: list[RunResult] = []
    for kmesh in KMESH_LIST:
        settings = {
            "label": f"kmesh_{int(kmesh)}",
            "ecut": 30.0,
            "ecutrho": 240.0,
            "kmesh": float(kmesh),
        }
        result = run_single_case(KMESH_DIR / settings["label"], settings)
        kmesh_results.append(result)

    save_results(kmesh_results, KMESH_DIR, "kmesh")


if __name__ == "__main__":
    main()
