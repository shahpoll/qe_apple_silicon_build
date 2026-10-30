# Silicon convergence

The archived tables use QE 7.4.1, with a 6³ cutoff-scan mesh, and remain historical evidence. They do not certify the current build or an arbitrary physical observable.

The current `run_convergence.py` selects the exact requested suite, keeps every new calculation outside the source tree, validates finite completed results, and computes direct gaps by first reducing band indices at each k point. All claimed metrics are serialized.

Use `qe-apple-silicon-build convergence --qe-bin /absolute/path/bin --candidate 50,400,12 --energy-target-mev-atom 1 --gap-target-mev 1 --out-dir /absolute/path/new-study`. Wavefunction and charge-density cutoffs, mesh ladders, stronger-point checks, repeated strongest settings, and joint candidate/reference checks are separate gates. A final scan point alone cannot qualify convergence. All gaps are symmetry-path sampled Kohn-Sham gaps.

The 50/400 Ry, 12³ candidate is an explicit variant; the 30/240 Ry, 8³ historical regression fixture is not silently overwritten. Choose error budgets for the intended observable before running a new study.
