# Installation guide

Start with the [README quick start](../README.md). This guide explains prerequisites, installation locations, checksums, and recovery.

## Prerequisites

This preview targets native **arm64 macOS** and pins Quantum ESPRESSO 7.5. The recorded numerical study used an M4 with 16 GiB RAM and macOS 26.3. Intel Macs, Rosetta, and other OS/toolchain combinations have not been qualified by that study.

The manager uses an existing compiler and numerical-library stack. It does not provision that stack. You need:

- Apple Command Line Tools. `xcode-select -p` should print the selected developer directory. If they are absent, Apple's `xcode-select --install` opens the installation dialog.
- [Python 3.12+](https://www.python.org/downloads/macos/). Check `python3 --version`. If a suitable Python has a different name, set `QE_PYTHON` to its absolute executable path.
- curl, Git, and [CMake](https://cmake.org/download/).
- [GNU Fortran](https://gcc.gnu.org/fortran/) and a compatible [MPI installation](https://docs.open-mpi.org/en/main/installing-open-mpi/index.html). The `mpif90` wrapper must use the same Fortran compiler/runtime as the QE build. Keep the C and Fortran MPI wrappers in one installation.
- An existing [OpenBLAS](https://github.com/OpenMathLib/OpenBLAS) library providing BLAS and LAPACK. Set `QE_BLAS_LIBRARY` to its `libopenblas.dylib` file, or pass `--blas-library` explicitly. A directory is insufficient.

Existing tools may come from any coherent installation. Their location does not require running a package manager. If you do not yet have a working Fortran/MPI/OpenBLAS stack, arrange that first using the upstream installation documentation; this project will report missing prerequisites instead of guessing or replacing tools.

The prerequisite check is read-only:

```sh
qe-apple-silicon-build doctor --blas-library /path/to/libopenblas.dylib
```

`doctor --work-dir /Volumes/Work/qe-runs` checks the volume you intend to use. A clean build requires at least 8 GiB free. Larger scientific studies and retained evidence need additional space.

## Install the manager

The README downloads `install.sh` from the versioned preview release. With no archive arguments, it downloads that release's `manager.json`, then checks the specified archive against its SHA256 before extraction or execution. This trusts the publisher's HTTPS release, not an independent signature.

The default locations are:

| Content | Location |
|---|---|
| Public manager command | `~/.local/bin/qe-apple-silicon-build` |
| Versioned manager packages | `~/.local/share/qe-manager/releases/` |
| Manager-install logs | `~/.local/share/qe-manager/attempts/` |
| Versioned QE suites | `~/.local/share/qe/releases/` |
| Selected qualified QE suite | `~/.local/share/qe/current/bin/` |
| Build/calculation evidence | `~/.local/state/qe/runs/` |

Add `~/.local/bin` to PATH in each terminal, or put the export line from the README in your shell configuration. No administrator access is needed for these user-owned locations.

To use different manager locations:

```sh
bash qe-install.sh \
  --manager-prefix "$HOME/Applications/qe-manager" \
  --bin-dir "$HOME/Applications/bin"
export PATH="$HOME/Applications/bin:$PATH"
```

The installer preserves unrelated commands. Reinstalling an already stored manager archive returns `RELEASE_EXISTS`; use the installed command instead. A future manager version uses a new versioned package.

## Verify downloaded assets yourself

The preview release provides `install.sh`, `manager.json`, `qe-manager.tar.gz`, and `SHA256SUMS`. Download all four from the **same release** into one new directory, then run:

```sh
shasum -a 256 -c SHA256SUMS
```

For an explicit archive/checksum installation, supply both values:

```sh
bash qe-install.sh \
  --source-url "https://github.com/shahpoll/qe_apple_silicon_build/releases/download/v2.0.0-rc.1/qe-manager.tar.gz" \
  --source-sha256 THE_ARCHIVE_SHA256_FROM_SHA256SUMS
```

The automatic manifest path avoids manually copying a checksum; the explicit form is useful for reproducible scripts. A mismatch fails and preserves its logs.

## Build and qualify QE

The recommended starting point is:

```sh
export QE_BLAS_LIBRARY="/path/to/libopenblas.dylib"
qe-apple-silicon-build install --profile core --jobs 2 --activate
export QE_BIN_PATH="$HOME/.local/share/qe/current/bin"
```

This compiles all default QE build targets, inventories the generated programs and their dependencies, then runs the **core** qualification before updating the dedicated prefix's `current` pointer. Extra installed programs do not inherit numerical qualification from the core checks.

To keep the candidate inactive for inspection, omit `--activate`. The command prints its candidate path; use that exact `bin` directory for `check --qe-bin ...`. The default `workstation` profile stays inactive until comprehensive qualification and independent review are available. Start with `--profile core` as shown above.

For a different QE prefix or build volume:

```sh
qe-apple-silicon-build install --profile core --jobs 2 \
  --install-prefix /Volumes/Work/qe \
  --out-dir /Volumes/Work/qe-runs/build-001 \
  --blas-library /path/to/libopenblas.dylib
```

Every `--out-dir` must be new and outside the source or installed package. Builds use existing tools, verified QE source, and separate source/build trees. They never copy over an old unversioned `bin` directory.

## Files and recovery

Keep each run's `VALIDATION_REPORT.md`, `summary.json`, `campaign.json`, and per-case inputs/logs together. `status RUN_DIRECTORY` checks the terminal evidence. A failed build or calculation is retained; diagnose its typed reason before creating a new attempt. See [troubleshooting](Troubleshooting.md).

`update` builds another versioned QE candidate using the same arguments as `install`. It does not update shared dependencies. Activation and `rollback` require an explicit release path and its matching qualification report; see [command reference](Command_Reference.md). Rollback checks dependency hashes and OS identity again. It cannot restore changed macOS or shared libraries.

The manager does not remove old evidence automatically. Review owned run directories before any manual cleanup; do not delete files belonging to another installation.

## Local or offline manager installation

From a source checkout:

```sh
python3 scripts/package_release.py --out-dir "$HOME/qe-manager-package-001"
bash install.sh --local-file \
  --source-url "file://$HOME/qe-manager-package-001/qe-manager.tar.gz" \
  --source-sha256 THE_PRINTED_ARCHIVE_SHA256
```

This installs the manager from local files. A fresh QE build still needs the pinned source archive and the external source dependencies used by CMake; this command does not promise a fully offline QE build.
