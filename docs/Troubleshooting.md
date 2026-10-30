# Troubleshooting

For setup problems, run `qe-apple-silicon-build doctor --blas-library /path/to/libopenblas.dylib` and follow the [installation guide](INSTALL.md). If the shell cannot find the command, add `~/.local/bin` to PATH.

Inspect the new run's `VALIDATION_REPORT.md`, `summary.json`, failing case `failure.json`, input and raw stdout/stderr. Preserve the attempt and choose a new output directory for a correction.

- `PREREQUISITE_MISSING` / `BLAS_PATH_REQUIRED`: provide the existing native compiler/MPI tools and an explicit OpenBLAS dylib. The installer does not install or update a package manager.
- `OUTPUT_EXISTS` / `OUTPUT_PROTECTED`: select a new external run directory. Do not delete another run to satisfy the check.
- MPI socket/binding error: inspect launcher evidence and host permissions. The default is `--bind-to none`. A serial diagnostic cannot replace required MPI proof.
- `PSEUDOPOTENTIAL_IDENTITY`: recover the exact authenticated reference UPF. A current file with the same name may have different contents. Do not loosen the identity check.
- `FLOATING_POINT_EXCEPTION`: preserve the flag and diagnose that layout/build. Current core postprocessing uses one managed MPI rank; two-rank BANDS remains unqualified on this device.
- `OPTIMIZATION_NOT_CONVERGED`: electronic completion alone does not establish ionic/cell convergence. The supported parser requires explicit BFGS or damped-minimization convergence.
- Missing DOS/PDOS parent or coverage: run the canonical workflow. It processes bands first, then uniform NSCF with the required 36 bands before DOS/PDOS.
- `DEPENDENCY_DRIFT` / `PLATFORM_DRIFT`: requalify after the external library/OS change. Pointer rollback does not roll back shared tools or macOS.
- `QUALIFICATION_SCOPE`: core and seed reports cannot authorize a comprehensive workstation activation. Missing mandatory cases and review stay blocked.

SCF and DOS Fermi values use different sampling here and have separate fixed regression references. Their difference is not evidence that arbitrary grids or normalization are interchangeable. See [device status](VALIDATION.md) for unresolved backend, reference and scientific limits.
