# Validation status and known limits

**Status:** core workflow validated on one recorded device; broader scientific qualification is incomplete. The public manager is a preview.

## Recorded device study

These results are from **15 October 2026**, not a fresh test of every later OS or toolchain. The device was an Apple M4 with 16 GiB RAM, native arm64 macOS 26.3 (25D125), GCC/gfortran 15.2, OpenMPI 5.0.8, and CMake 4.1.2. The recommended numerical backend was an explicitly selected OpenBLAS library.

| Check | Recorded outcome | Scope |
|---|---|---|
| Clean source build | 107 generated executables | Presence and dependency inventory |
| Core campaign | 21 passed | Silicon workflow, upstream SCF seed, actual MPI ranks 1/2/4, three repeats |
| Convergence study | 62 passed | Declared cutoff/density/mesh study and stronger repeated references |
| Force/stress consistency | 11 passed | Nonzero displacement and two finite-difference step sizes |
| Manual/PWTK comparison | Four gates passed | Same canonical inputs and raw grids, without fitted normalization |
| Selected upstream catalog | 33 passed, 17 blocked, one failed | Finite module-specific references; incomplete coverage |

The silicon regression gave −22.83927198 Ry/cell and an SCF Fermi energy of 6.4346 eV. The 50/400 Ry, 12³ candidate differed from the 80/800 Ry, 16³ reference by 0.3713 meV/atom, within its predeclared 1 meV/atom budget. These values are reproducibility checks for that fixture. They are not universal cutoff recommendations or experimental validation.

PW and PH use the requested pipeline ranks. Postprocessors use **one managed MPI rank** in the tested core profile. Other layouts require their own qualification. Path-sampled Kohn–Sham gaps are labeled accordingly; they are not measured fundamental gaps.

## Open issues

- **Methane Lanczos:** the fresh build printed NaN in a response component. Its case failed and the dependent spectrum was blocked. The older staged build passed the fixture; that pass does not qualify the new binary.
- **Missing exact references:** several USPP/PAW/metal and dependent response cases require historical pseudopotentials with exact benchmark hashes. Current files with the same names were not substituted. Davidson reference qualification is also blocked by missing exact files.
- **Execution-layout sensitivity:** two-rank BANDS raised a severe floating-point flag. The managed one-rank postprocessing profile passed; the two-rank layout remains unqualified.
- **Backend comparison:** raw acoustic-mode differences exceeded the fixed 0.01 cm⁻¹ budget. A separate comparison of explicitly ASR-corrected Gamma modes passed that same budget. The raw comparison remains failed.
- **Advanced scope:** CP trajectory references do not establish timestep or energy-drift convergence. Full Wannier90 integration, arbitrary materials/options, and comprehensive independent review remain unfinished.

An earlier convergence report accepted outputs before the severe-IEEE policy was enforced. Reinspection rejected 60 flagged execution cases and blocked their agreement gates. A separate strict OpenBLAS rerun passed all 62 cases with unchanged numerical budgets. The older report is retained as superseded evidence.

## How to interpret a result

A build proves that programs were produced. A launch proves they started. A completed calculation, converged calculation, reference agreement, and adequacy for a scientific question are additional claims with separate checks. Successful plotting is not numerical qualification.

Every campaign freezes its expected cases and records actual ranks, finite metrics, tolerances, inputs, command identity, and raw output. Missing prerequisites or failed parents remain blocked. A serial retry cannot satisfy an MPI requirement, and a failed tolerance is not widened to obtain a pass.

The GitHub **Checks** workflow tests the installer, parsers, paths, and failure handling. It does not build a complete QE suite or establish physical correctness. Full device numerical CI is a separate manual workflow requiring prepared hardware and tools.

## Evidence and historical records

New users get their own evidence under `~/.local/state/qe/runs/` or an explicit fresh `--out-dir`. Raw October build/calculation logs and source snapshots are retained separately on the maintainer's device; they are **not included in the manager download**. The [dated implementation record](https://github.com/shahpoll/qe_apple_silicon_build/blob/main/docs/implementation-status-2026-10-15.md) lists the local evidence names. Maintainer-only historical plans are linked from the [documentation index](README.md).

Before production science, choose the model and observables, then converge the relevant cutoffs, sampling, empty bands, smearing, broadening, or dynamics settings. A passing silicon example does not make a different material or feature combination qualified.
