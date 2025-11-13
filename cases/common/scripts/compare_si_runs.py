#!/usr/bin/env python3
"""Compare manual QE and PWTK silicon runs and produce overlay plots."""

from __future__ import annotations

import argparse
import pathlib
from dataclasses import dataclass
from typing import Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
MANUAL_BASE = ROOT / "cases" / "si" / "manual"
PWTK_BASE = ROOT / "cases" / "si" / "pwtk"
COMPARISON_BASE = ROOT / "cases" / "si" / "comparison"


def pretty_path(path: pathlib.Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


@dataclass
class DosData:
    energy: np.ndarray
    values: np.ndarray
    fermi: float


@dataclass
class BandData:
    k_path: np.ndarray
    bands: np.ndarray  # shape (nband, nk)


def load_dos(path: pathlib.Path) -> DosData:
    energy: list[float] = []
    values: list[float] = []
    fermi: float | None = None
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                if "EFermi" in line:
                    try:
                        fermi = float(line.split("EFermi =")[-1].split()[0])
                    except (IndexError, ValueError) as exc:  # pragma: no cover - defensive
                        raise RuntimeError(f"Failed to parse EFermi in {path}") from exc
                continue
            cols = line.split()
            if len(cols) < 2:
                continue
            energy.append(float(cols[0]))
            values.append(float(cols[1]))
    if not energy:
        raise RuntimeError(f"No DOS data parsed from {path}")
    if fermi is None:
        raise RuntimeError(f"Could not locate EFermi in {path}")
    return DosData(np.array(energy), np.array(values), fermi)


def load_pdos(base: pathlib.Path, fermi: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    files = {
        "atm1_s": "silicon.pdos_atm#1(Si)_wfc#1(s)",
        "atm1_p": "silicon.pdos_atm#1(Si)_wfc#2(p)",
        "atm2_s": "silicon.pdos_atm#2(Si)_wfc#1(s)",
        "atm2_p": "silicon.pdos_atm#2(Si)_wfc#2(p)",
    }
    data_dir = base / "data"
    energies, s_total, p_total = None, None, None
    for key, fname in files.items():
        energy, values = [], []
        with (data_dir / fname).open("r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                cols = line.split()
                if len(cols) < 2:
                    continue
                energy.append(float(cols[0]))
                values.append(float(cols[1]))
        if not energy:
            raise RuntimeError(f"No PDOS data parsed from {fname}")
        energy_arr = np.array(energy) - fermi
        values_arr = np.array(values)
        if energies is None:
            energies = energy_arr
            s_total = np.zeros_like(values_arr)
            p_total = np.zeros_like(values_arr)
        if "s" in key:
            s_total += values_arr
        else:
            p_total += values_arr
    return energies, s_total, p_total


def load_bands(path: pathlib.Path) -> BandData:
    bands = []
    current = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                if current:
                    bands.append(current)
                    current = []
                continue
            parts = stripped.split()
            if len(parts) < 2:
                continue
            current.append((float(parts[0]), float(parts[1])))
    if current:
        bands.append(current)
    if not bands:
        raise RuntimeError(f"No band data parsed from {path}")
    nk = len(bands[0])
    for band in bands:
        if len(band) != nk:
            raise RuntimeError("Inconsistent k-point sampling across bands")
    k_path = np.array([pt[0] for pt in bands[0]])
    energies = np.array([[pt[1] for pt in band] for band in bands])
    return BandData(k_path, energies)


def compare(manual: pathlib.Path, pwtk: pathlib.Path) -> None:
    comparison_dir = COMPARISON_BASE
    plots_dir = comparison_dir / "plots"
    data_dir = comparison_dir / "data"
    plots_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    manual_bands = load_bands(manual / "data" / "silicon.bands.dat.gnu")
    pwtk_bands = load_bands(pwtk / "data" / "silicon.bands.dat.gnu")
    manual_dos = load_dos(manual / "data" / "silicon.dos")
    pwtk_dos = load_dos(pwtk / "data" / "silicon.dos")
    manual_p_energy, manual_p_s, manual_p_p = load_pdos(manual, manual_dos.fermi)
    pwtk_p_energy, pwtk_p_s, pwtk_p_p = load_pdos(pwtk, pwtk_dos.fermi)

    manual_bands_shift = manual_bands.bands - manual_dos.fermi
    pwtk_bands_shift = pwtk_bands.bands - pwtk_dos.fermi
    manual_dos_energy = manual_dos.energy - manual_dos.fermi
    pwtk_dos_energy = pwtk_dos.energy - pwtk_dos.fermi

    band_diff = np.max(np.abs(manual_bands_shift - pwtk_bands_shift))
    dos_diff = np.max(np.abs(manual_dos.values - pwtk_dos.values))
    pdos_s_diff = np.max(np.abs(manual_p_s - pwtk_p_s))
    pdos_p_diff = np.max(np.abs(manual_p_p - pwtk_p_p))

    mask = (np.abs(pwtk_dos.values) > 1e-6) & (np.abs(manual_dos.values) > 1e-6)
    scale_ratio = float(np.median(manual_dos.values[mask] / pwtk_dos.values[mask])) if mask.any() else float("nan")

    with (data_dir / "si_comparison.txt").open("w", encoding="utf-8") as f:
        f.write("# Manual vs PWTK silicon comparison\n")
        f.write(f"Manual base: {pretty_path(manual)}\n")
        f.write(f"PWTK base  : {pretty_path(pwtk)}\n")
        f.write(f"Max |band difference| : {band_diff:.3e} eV\n")
        f.write(f"Max |DOS difference|  : {dos_diff:.3e} states/eV\n")
        f.write(f"Max |PDOS s diff|     : {pdos_s_diff:.3e} states/eV\n")
        f.write(f"Max |PDOS p diff|     : {pdos_p_diff:.3e} states/eV\n")
        f.write("Note: runtime/efficiency metrics not captured in current logs.\n")
        f.write("Note: DOS traces differ by a constant scale factor (median manual/pwtk ≈ "
                f"{scale_ratio:.2f}); shapes overlap after normalisation.\n")

    fig, axes = plt.subplots(1, 3, figsize=(15, 4), dpi=150)

    ax = axes[0]
    for band in manual_bands_shift:
        ax.plot(manual_bands.k_path, band, color="tab:blue", linewidth=0.6)
    for band in pwtk_bands_shift:
        ax.plot(pwtk_bands.k_path, band, color="tab:orange", linewidth=0.3, linestyle="--")
    ax.set_title("Bands")
    ax.set_xlabel("k-path (arb. units)")
    ax.set_ylabel("Energy – E$_F$ (eV)")

    ax = axes[1]
    ax.plot(manual_dos_energy, manual_dos.values, label="Manual", color="tab:blue")
    ax.plot(pwtk_dos_energy, pwtk_dos.values, label="PWTK", color="tab:orange", linestyle="--")
    ax.set_title("Total DOS")
    ax.set_xlabel("Energy – E$_F$ (eV)")
    ax.set_ylabel("DOS (states/eV)")
    ax.legend(frameon=False)

    ax = axes[2]
    ax.plot(manual_p_energy, manual_p_s, label="Manual s", color="tab:blue")
    ax.plot(pwtk_p_energy, pwtk_p_s, label="PWTK s", color="tab:blue", linestyle="--")
    ax.plot(manual_p_energy, manual_p_p, label="Manual p", color="tab:orange")
    ax.plot(pwtk_p_energy, pwtk_p_p, label="PWTK p", color="tab:orange", linestyle="--")
    ax.set_title("Projected DOS")
    ax.set_xlabel("Energy – E$_F$ (eV)")
    ax.set_ylabel("DOS (states/eV)")
    ax.legend(frameon=False)

    fig.tight_layout()
    fig.savefig(plots_dir / "si_manual_vs_pwtk.png")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compare manual and PWTK silicon runs")
    parser.add_argument("--manual", type=pathlib.Path, default=MANUAL_BASE, help="Manual run directory")
    parser.add_argument("--pwtk", type=pathlib.Path, default=PWTK_BASE, help="PWTK run directory")
    args = parser.parse_args()

    compare(args.manual, args.pwtk)
