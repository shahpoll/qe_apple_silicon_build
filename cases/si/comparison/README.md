# Silicon — Manual vs PWTK Comparison

Generated artefacts:

- `data/si_comparison.txt` — maximum absolute differences between manual and PWTK runs.
- `data/si_benchmarks.txt` — wall-clock timings parsed from QE logs (seconds).
- `data/fermi_consistency.csv` — SCF vs DOS Fermi levels and indirect gaps per workflow.
- `plots/si_manual_vs_pwtk.png` — overlay of band structure, total DOS, and PDOS.

Recreate with:
```sh
cd /path/to/qe_macm4_build/cases/si/comparison
python3 scripts/compare_runs.py
```

Notes:
- Band energies align to machine precision; total/projected DOS traces agree up to
  the smearing tolerance used by `dos.x` (ΔE = 0.02 eV).
- Energy axes in all plots are referenced to the DOS-derived Fermi level (E = 0).
- QE runtimes are not captured in current logs; add `/usr/bin/time` wrappers if you need benchmarking.
