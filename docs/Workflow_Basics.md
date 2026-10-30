# Curl build and validation workflow

Use the curl installation instructions in the repository README. Existing native tools are required; the installer never invokes Homebrew or modifies shared dependency installations.

1. Build into a dedicated versioned prefix with `install --backend openblas --blas-library /absolute/path/libopenblas.dylib --install-prefix /absolute/path/qe --jobs 2`. Retain the complete build output and its inactive candidate path.
2. Run `check --qe-bin /absolute/path/candidate/bin --out-dir /absolute/path/new-check` in an environment permitting local MPI. Actual ranks 1/2/4 and three repeats are required. A serial diagnostic cannot substitute for an MPI case.
3. For the reference silicon dataset, run `workflow --qe-bin ... --out-dir /absolute/path/new-manual`. It writes identified data and logs under that owned run directory. Do not run postprocessors in the bundled example directories or copy old results into a new run.
4. For PWTK, use the same workflow command with `--engine pwtk --pwtk /absolute/path/pwtk --tclsh /absolute/path/tclsh8.6`. Compare the two new run directories using `cases/common/scripts/compare_si_runs.py` and a new comparison output directory.
5. Optional plots accept `--base /absolute/path/new-run`; choose a Python environment already containing NumPy/Matplotlib. Plotting errors do not change scientific verdicts.
6. Run observable-specific convergence with a stated error budget before production science. Cutoffs, mesh, smearing, bands, functional, geometry, and UPF changes are explicit variants. Keep failed studies and original tolerances.
7. Numerical activation requires matching release and qualification scope. Leave incomplete workstation candidates inactive. Use `status` to inspect an interrupted run and preserve its evidence before a new attempt.

On failure, inspect the typed reason in the case's `failure.json`, its exact input, command, reference identity, stdout/stderr, and parent hashes. Diagnose before a new attempt. Every new attempt uses a new directory. Unknown or missing quantities remain unknown; no automatic normalization, serial fallback, or tolerance relaxation is permitted.
