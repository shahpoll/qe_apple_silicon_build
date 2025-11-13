#!/usr/bin/env python3
"""
Plot projected DOS for Si (s and p channels per atom, referenced to E_F).

Supports multiple base directories so individual workflows stay isolated:

  python3 cases/common/scripts/plot_si_pdos.py            # default cases/si/manual
  python3 cases/common/scripts/plot_si_pdos.py --pwtk     # cases/si/pwtk
  python3 cases/common/scripts/plot_si_pdos.py --base /path/to/run
"""

from __future__ import annotations

import argparse
import pathlib
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
DEFAULT_BASE = ROOT / "cases" / "si" / "manual"
PT_BASE = ROOT / "cases" / "si" / "pwtk"

PDOS_FILES = {
    "tot": "silicon.pdos_tot",
    "atm1_s": "silicon.pdos_atm#1(Si)_wfc#1(s)",
    "atm1_p": "silicon.pdos_atm#1(Si)_wfc#2(p)",
    "atm2_s": "silicon.pdos_atm#2(Si)_wfc#1(s)",
    "atm2_p": "silicon.pdos_atm#2(Si)_wfc#2(p)",
}


def workflow_label(base: pathlib.Path) -> str:
    if base.samefile(DEFAULT_BASE):
        return "Manual QE workflow (Accelerate, M4)"
    if base.samefile(PT_BASE):
        return "PWTK-driven QE workflow (Accelerate, M4)"
    return f"Custom run: {base}"


def compute_paths(base: pathlib.Path | None) -> tuple[dict[str, pathlib.Path], pathlib.Path]:
    base_dir = DEFAULT_BASE if base is None else base
    data_dir = base_dir / "data"
    files = {key: data_dir / fname for key, fname in PDOS_FILES.items()}
    out = base_dir / "plots" / "si_pdos.png"
    return files, out


def read_pdos(path: pathlib.Path) -> Tuple[np.ndarray, np.ndarray]:
    energy: list[float] = []
    density: list[float] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split()
            if len(parts) < 3:
                continue
            energy.append(float(parts[0]))
            density.append(float(parts[1]))
    return np.array(energy), np.array(density)


def read_fermi(base: pathlib.Path) -> float:
    dos_file = base / "data" / "silicon.dos"
    with dos_file.open("r", encoding="utf-8") as f:
        for line in f:
            if "EFermi" in line:
                token = line.split("EFermi =")[-1].split()[0]
                return float(token)
    raise RuntimeError(f"Could not locate EFermi in {dos_file}")


def main(base: pathlib.Path | None = None) -> None:
    files, out_png = compute_paths(base)
    base_dir = DEFAULT_BASE if base is None else base
    fermi = read_fermi(base_dir)
    energies_tot, dos_tot = read_pdos(files["tot"])
    _, atm1_s = read_pdos(files["atm1_s"])
    _, atm1_p = read_pdos(files["atm1_p"])
    _, atm2_s = read_pdos(files["atm2_s"])
    _, atm2_p = read_pdos(files["atm2_p"])

    energies_tot = energies_tot - fermi
    s_total = atm1_s + atm2_s
    p_total = atm1_p + atm2_p

    fig, ax = plt.subplots(figsize=(6, 4), dpi=150)
    ax.plot(energies_tot, dos_tot, color="0.2", label="Total DOS")
    ax.plot(energies_tot, s_total, color="tab:blue", label="Si s (total)")
    ax.plot(energies_tot, p_total, color="tab:orange", label="Si p (total)")
    ax.axvline(0.0, color="tab:red", linestyle="--", linewidth=0.8, label="E$_F$")
    ax.set_xlabel("Energy – E$_F$ (eV)")
    ax.set_ylabel("DOS (states/eV)")
    ax.set_title(f"Silicon projected DOS — {workflow_label(base_dir)}")
    ax.set_xlim(energies_tot.min(), energies_tot.max())
    ax.set_ylim(bottom=0)
    ax.legend(frameon=False)
    ax.text(
        0.02,
        0.95,
        f"E$_F$ = {fermi:.4f} eV",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9,
    )
    ax.grid(alpha=0.2, which="both", axis="both")

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot silicon projected DOS")
    parser.add_argument("--base", type=pathlib.Path, help="Base directory (default cases/si/manual)")
    parser.add_argument("--pwtk", action="store_true", help="Use cases/si/pwtk as base directory")
    args = parser.parse_args()

    base_dir = args.base
    if args.pwtk:
        base_dir = PT_BASE

    main(base_dir)
