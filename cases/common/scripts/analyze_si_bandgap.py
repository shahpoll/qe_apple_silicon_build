#!/usr/bin/env python3
"""Extract band-gap information from silicon runs (manual or PWTK)."""

from __future__ import annotations

import argparse
import math
import pathlib
from typing import List, Tuple

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
DEFAULT_BASE = ROOT / "cases" / "si" / "manual"
PT_BASE = ROOT / "cases" / "si" / "pwtk"


def compute_paths(base: pathlib.Path | None) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    base_dir = DEFAULT_BASE if base is None else base
    band_file = base_dir / "data" / "silicon.bands.dat.gnu"
    dos_file = base_dir / "data" / "silicon.dos"
    out_file = base_dir / "data" / "si_band_summary.txt"
    return band_file, dos_file, out_file


def read_fermi(dos_file: pathlib.Path) -> float:
    with dos_file.open("r", encoding="utf-8") as dos:
        line = dos.readline()
        if "EFermi" not in line:
            raise RuntimeError(f"Could not locate EFermi in {dos_file}")
        return float(line.split("EFermi =")[1].split()[0])


def read_bands(band_file: pathlib.Path) -> Tuple[np.ndarray, np.ndarray]:
    bands: List[List[Tuple[float, float]]] = []
    current: List[Tuple[float, float]] = []
    with band_file.open("r", encoding="utf-8") as bf:
        for raw in bf:
            line = raw.strip()
            if not line:
                if current:
                    bands.append(current)
                    current = []
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            current.append((float(parts[0]), float(parts[1])))
    if current:
        bands.append(current)

    if not bands:
        raise RuntimeError(f"No band data parsed from {band_file}")

    nk = len(bands[0])
    for band in bands:
        if len(band) != nk:
            raise RuntimeError("Inconsistent k-point sampling across bands")
    k_path = np.array([pt[0] for pt in bands[0]])
    energies = np.array([[pt[1] for pt in band] for band in bands])
    return k_path, energies


def summarize(base: pathlib.Path | None = None) -> str:
    band_file, dos_file, _ = compute_paths(base)
    k_path, energies = read_bands(band_file)
    fermi = read_fermi(dos_file)

    with np.errstate(invalid="ignore"):
        valence = np.where(energies <= fermi, energies, -math.inf)
        conduction = np.where(energies >= fermi, energies, math.inf)

    valence_max_by_k = valence.max(axis=0)
    conduction_min_by_k = conduction.min(axis=0)

    global_vmax = valence_max_by_k.max()
    global_cmin = conduction_min_by_k.min()

    indirect_gap = global_cmin - global_vmax
    k_vmax_idx = int(valence_max_by_k.argmax())
    k_cmin_idx = int(conduction_min_by_k.argmin())

    direct_deltas = conduction_min_by_k - valence_max_by_k
    direct_gap = direct_deltas.min()
    k_direct_idx = int(direct_deltas.argmin())

    lines = [
        "# Silicon band summary (derived from silicon.bands.dat.gnu)",
        f"Fermi level (from silicon.dos)  : {fermi:8.4f} eV",
        f"Valence band maximum            : {global_vmax:8.4f} eV at k-index {k_vmax_idx} (s = {k_path[k_vmax_idx]:.4f})",
        f"Conduction band minimum         : {global_cmin:8.4f} eV at k-index {k_cmin_idx} (s = {k_path[k_cmin_idx]:.4f})",
        f"Indirect gap (Cmin - Vmax)      : {indirect_gap:8.4f} eV",
        f"Direct gap (min over k)         : {direct_gap:8.4f} eV at k-index {k_direct_idx} (s = {k_path[k_direct_idx]:.4f})",
    ]
    return "\n".join(lines) + "\n"


def main(base: pathlib.Path | None = None) -> None:
    band_file, dos_file, out_file = compute_paths(base)
    summary = summarize(base)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(summary, encoding="utf-8")
    print(summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Summarise silicon band gaps")
    parser.add_argument("--base", type=pathlib.Path, help="Base directory (default cases/si/manual)")
    parser.add_argument("--pwtk", action="store_true", help="Use cases/si/pwtk as base directory")
    args = parser.parse_args()

    base_dir = args.base
    if args.pwtk:
        base_dir = PT_BASE

    main(base_dir)
