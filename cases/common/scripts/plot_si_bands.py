#!/usr/bin/env python3
"""
Plot the silicon band structure with energies referenced to the DOS-derived Fermi level.

Expected inputs (relative to --base):
  - data/silicon.bands.dat.gnu (from bands.x)
  - logs/si_bands_post.txt (for symmetry point abscissae)

The script emits plots/si_band_structure.png under the chosen base.
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass
from typing import List, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
DEFAULT_BASE = ROOT / "cases" / "si" / "manual"
PT_BASE = ROOT / "cases" / "si" / "pwtk"


def compute_paths(base: pathlib.Path | None) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path, pathlib.Path]:
    base_dir = DEFAULT_BASE if base is None else base
    data = base_dir / "data" / "silicon.bands.dat.gnu"
    log = base_dir / "logs" / "si_bands_post.txt"
    dos = base_dir / "data" / "silicon.dos"
    out = base_dir / "plots" / "si_band_structure.png"
    return data, log, dos, out


def workflow_label(base: pathlib.Path) -> str:
    if base.samefile(DEFAULT_BASE):
        return "Manual QE workflow (Accelerate, M4)"
    if base.samefile(PT_BASE):
        return "PWTK-driven QE workflow (Accelerate, M4)"
    return f"Custom run: {base}"


@dataclass
class BandCurve:
    k_path: np.ndarray
    energies: np.ndarray


def parse_band_file(path: pathlib.Path) -> List[BandCurve]:
    bands: List[BandCurve] = []
    buffer: List[Tuple[float, float]] = []

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                if buffer:
                    arr = np.array(buffer, dtype=float)
                    bands.append(BandCurve(arr[:, 0], arr[:, 1]))
                    buffer = []
                continue

            parts = stripped.split()
            if len(parts) < 2:
                continue
            buffer.append((float(parts[0]), float(parts[1])))

    if buffer:
        arr = np.array(buffer, dtype=float)
        bands.append(BandCurve(arr[:, 0], arr[:, 1]))

    return bands


def read_fermi(dos_path: pathlib.Path) -> float:
    with dos_path.open("r", encoding="utf-8") as f:
        for line in f:
            if "EFermi" in line:
                token = line.split("EFermi =")[-1].split()[0]
                return float(token)
    raise RuntimeError(f"Could not locate EFermi in {dos_path}")


def extract_symmetry_points(path: pathlib.Path) -> Sequence[Tuple[str, float]]:
    if not path.exists():
        return []
    labels: List[Tuple[float, str]] = []
    order = ["Γ", "X", "W", "K", "Γ", "L"]

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if "high-symmetry point" not in line:
                continue
            segments = line.strip().split()
            # last token is the abscissa value
            try:
                k_abscissa = float(segments[-1])
            except ValueError:
                continue
            if len(labels) < len(order):
                labels.append((k_abscissa, order[len(labels)]))

    return labels


def main(base: pathlib.Path | None = None) -> None:
    data_file, log_file, dos_file, out_png = compute_paths(base)
    base_dir = DEFAULT_BASE if base is None else base
    if not data_file.exists():
        raise SystemExit(f"Band data not found: {data_file}")

    bands = parse_band_file(data_file)
    if not bands:
        raise SystemExit("No band curves parsed; aborting")

    fermi_level = read_fermi(dos_file)
    shifted_bands = [
        BandCurve(b.k_path, b.energies - fermi_level) for b in bands
    ]

    sym_points = extract_symmetry_points(log_file)

    fig, ax = plt.subplots(figsize=(6, 6), dpi=150)

    for band in shifted_bands:
        ax.plot(band.k_path, band.energies, color="tab:blue", linewidth=1)

    ax.axhline(0.0, color="tab:red", linestyle="--", linewidth=0.8)

    if sym_points:
        xticks, xticklabels = zip(*sym_points)
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticklabels)
        for x in xticks[1:-1]:
            ax.axvline(x, color="0.8", linestyle="-", linewidth=0.6)

    x_min = min(float(b.k_path.min()) for b in shifted_bands)
    x_max = max(float(b.k_path.max()) for b in shifted_bands)
    ax.set_xlim(x_min, x_max)
    ax.set_ylabel("Energy – E$_F$ (eV)")
    ax.set_title(f"Silicon band structure — {workflow_label(base_dir)}")
    ax.grid(alpha=0.2, which="both", axis="y")
    ax.text(
        0.02,
        0.95,
        f"E$_F$ = {fermi_level:.4f} eV",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=9,
    )

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_png)
    plt.close(fig)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Plot silicon band structure")
    parser.add_argument(
        "--base",
        type=pathlib.Path,
        help="Base directory containing data/logs/plots (default cases/si/manual)",
    )
    parser.add_argument(
        "--pwtk",
        action="store_true",
        help="Shortcut for --base analysis_pwtk/Si",
    )
    args = parser.parse_args()

    base_dir = args.base
    if args.pwtk:
        base_dir = PT_BASE

    main(base_dir)
