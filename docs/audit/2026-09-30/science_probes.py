#!/usr/bin/env python3
"""Read-only audit probes over archived Si artifacts; does not launch QE.

Run from any directory: python3 path/to/science_probes.py
Prints JSON to stdout. Only Python's standard library is required.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
import re
import statistics


ROOT = Path(__file__).resolve().parents[3]


def read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def table(relative: str) -> list[list[float]]:
    return [
        [float(value) for value in line.split()]
        for line in read(relative).splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def projection_sizes(relative: str) -> dict[str, object]:
    text = read(relative)
    return {
        "source": relative,
        "nbnd": int(re.search(r"^\s*nbnd\s*=\s*(\d+)", text, re.M).group(1)),
        "nkstot": int(re.search(r"^\s*nkstot\s*=\s*(\d+)", text, re.M).group(1)),
    }


def main() -> None:
    manual_path = "cases/si/manual/data/silicon.dos"
    pwtk_path = "cases/si/pwtk/data/silicon.dos"
    manual, pwtk = table(manual_path), table(pwtk_path)
    if len(manual) != len(pwtk):
        raise RuntimeError("DOS row counts differ; rowwise comparison is invalid")
    grid_difference = max(abs(a[0] - b[0]) for a, b in zip(manual, pwtk))
    if grid_difference != 0.0:
        raise RuntimeError("DOS energy grids differ; rowwise comparison is invalid")
    ratios = sorted(
        a[1] / b[1]
        for a, b in zip(manual, pwtk)
        if a[1] > 1e-6 and b[1] > 1e-6
    )
    scale = statistics.median(ratios)

    case = "cases/si/convergence/cutoff/cutoff_30"
    fermi = next(
        float(line.split()[-2])
        for line in read(f"{case}/scf.out").splitlines()
        if "the Fermi energy is" in line
    )
    bands = [
        [float(line.split()[1]) for line in block.splitlines() if line.strip()]
        for block in re.split(r"\n\s*\n", read(f"{case}/silicon.bands.dat.gnu"))
        if block.strip()
    ]
    if not bands or len({len(band) for band in bands}) != 1:
        raise RuntimeError("Invalid band dimensions")
    valence = [[e if e <= fermi else -math.inf for e in band] for band in bands]
    conduction = [[e if e >= fermi else math.inf for e in band] for band in bands]
    # Reproduce run_convergence.py:160-167, then reduce band indices correctly.
    current_gap = min(
        c - v for cb, vb in zip(conduction, valence) for c, v in zip(cb, vb)
    )
    corrected_gap = min(
        min(c[k] for c in conduction) - max(v[k] for v in valence)
        for k in range(len(bands[0]))
    )

    convergence_readme = "cases/si/convergence/README.md"
    claimed_mesh = int(
        re.search(r"Cutoff scan \(k = (\d+)×", read(convergence_readme)).group(1)
    )
    actual_mesh = [
        int(value)
        for value in re.search(
            r"K_POINTS automatic\s*\n\s*(\d+\s+\d+\s+\d+)", read(f"{case}/scf.in")
        ).group(1).split()
    ]
    rows = json.loads(read("cases/si/convergence/cutoff/cutoff.json"))

    result = {
        "scope": "Archived artifacts and formula replay; no new QE calculations",
        "path_base": "qe_macos15_build",
        "projection_dataset": {
            "manual": projection_sizes("cases/si/manual/logs/si_projwfc.txt"),
            "pwtk": projection_sizes("cases/si/pwtk/logs/si_projwfc.txt"),
            "finding": "PWTK PDOS consumes 201 band-path points and 8 bands, not the advertised uniform NSCF dataset with 36 bands",
        },
        "dos_comparison": {
            "sources": [manual_path, pwtk_path],
            "rows": len(manual),
            "energy_grid_max_difference_eV": grid_difference,
            "max_absolute_difference_states_per_eV": max(
                abs(a[1] - b[1]) for a, b in zip(manual, pwtk)
            ),
            "ratio_selection": "Both densities > 1e-6 states/eV",
            "ratio_rows": len(ratios),
            "ratio_percentile_method": "Sorted sample at int(p * sample_count); median uses statistics.median",
            "manual_over_pwtk_ratio_p05": ratios[int(0.05 * len(ratios))],
            "manual_over_pwtk_ratio_median": scale,
            "manual_over_pwtk_ratio_p95": ratios[int(0.95 * len(ratios))],
            "median_scaled_max_residual_states_per_eV": max(
                abs(a[1] - scale * b[1]) for a, b in zip(manual, pwtk)
            ),
            "finding": "The archived curves do not differ by a constant normalization factor",
        },
        "direct_gap_formula": {
            "source_formula": "cases/si/convergence/run_convergence.py:160-167",
            "data_source": f"{case}/silicon.bands.dat.gnu",
            "fermi_source": f"{case}/scf.out",
            "fermi_eV": fermi,
            "current_formula_eV": current_gap if math.isfinite(current_gap) else str(current_gap),
            "corrected_per_k_reduction_eV": corrected_gap,
            "finding": "Elementwise masked-band subtraction produces infinity; this field is currently omitted from serialized tables",
        },
        "cutoff_mesh": {
            "claim_source": convergence_readme,
            "input_source": f"{case}/scf.in",
            "table_source": "cases/si/convergence/cutoff/cutoff.json",
            "readme_claim": [claimed_mesh] * 3,
            "actual_input": actual_mesh,
            "archived_table_meshes": sorted({row["kmesh"] for row in rows}),
            "finding": "README says 8x8x8; archived cutoff calculations use 6x6x6",
        },
    }
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
