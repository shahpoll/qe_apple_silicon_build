# Command reference

Use `bin/qe-apple-silicon-build COMMAND --help` from a checkout, or the installed `qe-apple-silicon-build`. Installation is described in [README](../README.md).

```sh
qe-apple-silicon-build doctor --blas-library /absolute/path/libopenblas.dylib
qe-apple-silicon-build install --backend openblas --blas-library /absolute/path/libopenblas.dylib --install-prefix /absolute/path/new-prefix --jobs 2
qe-apple-silicon-build check --qe-bin /absolute/path/candidate/bin --out-dir /absolute/path/new-check
qe-apple-silicon-build smoke --qe-bin /absolute/path/candidate/bin --ranks 2 --out-dir /absolute/path/new-smoke
qe-apple-silicon-build status /absolute/path/new-check
qe-apple-silicon-build activate --install-prefix /absolute/path/prefix --release /absolute/path/prefix/releases/qualified-release --qualification /absolute/path/qualification/summary.json
```

`update` makes a new inactive release using the same build path. `rollback` takes the same explicit arguments as `activate` and rechecks the target's dependencies and qualification. A core report cannot activate a workstation release.

`workflow`, `compare`, `convergence`, `physical`, `examples`, `davidson` and `upstream` expose the numerical studies; inspect their help for exact required references and arguments. They do not certify arbitrary user inputs.

The runtime wrapper uses `QE_BIN_PATH`, `QE_RANKS`, `QE_BINDING`, `QE_MPI_LAUNCHER`, `QE_TIMEOUT` and `QE_RUNS_DIR`. It fixes numerical-library thread counts to one and never retries or substitutes serial execution. `QE_CPUSET` is unsupported and rejected. Wrapper PASS covers execution and observed ranks only.
