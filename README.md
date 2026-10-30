# Quantum ESPRESSO on Apple Silicon

[![Checks](https://github.com/shahpoll/qe_apple_silicon_build/actions/workflows/checks.yml/badge.svg?branch=main)](https://github.com/shahpoll/qe_apple_silicon_build/actions/workflows/checks.yml)
[![QE 7.5](https://img.shields.io/badge/Quantum_ESPRESSO-7.5-blue)](https://www.quantum-espresso.org/)
[![MIT](https://img.shields.io/badge/installer-MIT-green)](LICENSE)

Build **Quantum ESPRESSO 7.5** on a Mac with Apple Silicon, check the installation with real calculations, and keep a clear record of what passed and what failed.

Quantum ESPRESSO is a collection of scientific programs for electronic-structure calculations. This project provides the installation manager and reproducible example workflows around it. It downloads verified source archives and compiles QE locally using your existing tools.

**Preview release:** [v2.0.0-rc.1](https://github.com/shahpoll/qe_apple_silicon_build/releases/tag/v2.0.0-rc.1). The core workflow has been tested on an M4 running macOS 26.3. Advanced calculations have known failures and missing references; see [validation status](docs/VALIDATION.md).

[Installation guide](docs/INSTALL.md) · [Example workflows](docs/Workflow_Basics.md) · [Troubleshooting](docs/Troubleshooting.md) · [Command reference](docs/Command_Reference.md)

## Before you start

You need a **native Apple Silicon macOS environment** and these tools already installed:

| Requirement | Purpose |
|---|---|
| Apple Command Line Tools | C compiler, SDK, and development utilities |
| Python 3.12 or newer | Installer and validation commands |
| curl, Git, and CMake | Download and build the source |
| gfortran and a compatible MPI installation | Fortran compiler plus `mpicc`, `mpif90`, and `mpirun` |
| An existing OpenBLAS library | BLAS/LAPACK numerical routines |
| At least 8 GiB free for a clean build | Source, build files, and retained evidence |

The installer **does not require or invoke Homebrew** and does not install compilers or upgrade shared libraries. Starting with a stock Mac? Read [prerequisites](docs/INSTALL.md#prerequisites) first. NumPy and Matplotlib are optional plotting tools; numerical checks use Python's standard library.

## Quick start

### 1. Install the manager

Download the preview installer, then run it:

```sh
curl --fail --location --proto '=https' --proto-redir '=https' \
  https://github.com/shahpoll/qe_apple_silicon_build/releases/download/v2.0.0-rc.1/install.sh \
  --output qe-install.sh
bash qe-install.sh
export PATH="$HOME/.local/bin:$PATH"
```

This installs the small manager. **QE itself is built in the next step.** The installer obtains the versioned release manifest and verifies the manager archive's SHA256 before extraction. It saves its download and installation logs.

### 2. Check your tools and build QE

Replace the example below with the path to your **existing** OpenBLAS library:

```sh
export QE_BLAS_LIBRARY="/absolute/path/to/libopenblas.dylib"
qe-apple-silicon-build doctor
qe-apple-silicon-build install --profile core --jobs 2 --activate
```

`doctor` checks prerequisites without changing them. The build uses a new directory, records its dependencies, and runs the complete core qualification before selecting the new version. A failed check leaves the candidate inactive. Existing QE installations are preserved.

### 3. Use the qualified installation

```sh
export QE_BIN_PATH="$HOME/.local/share/qe/current/bin"
qe-apple-silicon-build smoke --qe-bin "$QE_BIN_PATH" --ranks 2
```

A successful smoke check reports `PASS` and the evidence directory. For a first complete example, follow the [silicon workflow guide](docs/Workflow_Basics.md). Run `qe-apple-silicon-build help` to see all commands.

To keep the manager on your PATH in future terminals, add `export PATH="$HOME/.local/bin:$PATH"` to your shell configuration. Custom prefixes, offline installation, checksums, and updates are covered in the [installation guide](docs/INSTALL.md).

## What is checked?

The recommended **core profile** covers SCF, bands, uniform NSCF, DOS, projected DOS, charge density, and phonon processing. It also requires actual MPI runs with 1, 2, and 4 ranks and three repeated calculations. PW/PH use the requested pipeline ranks; postprocessors use one managed MPI rank in this tested profile.

The October 15 device study recorded **21 core checks**, **62 convergence checks**, and **11 force/stress consistency checks** passing. The broader upstream catalog recorded **33 passed, 17 blocked, and one failed**. The methane Lanczos response produced NaN, so its dependent spectrum was blocked. These are dated results for specific inputs and one device, not a guarantee for every material or QE option. The CI badge checks the tooling; it does not certify physical accuracy.

Read [validation status and known limits](docs/VALIDATION.md) before using an advanced module or starting production science.

## Your results stay separate

New runs default to `~/.local/state/qe/runs/`. Each has its own inputs, commands, logs, numerical assertions, and report. You can select a **new external directory** with `--out-dir`; an existing directory is refused. Failed attempts are retained, and MPI failures are never silently replaced with serial execution.

```sh
qe-apple-silicon-build status /path/to/your/run
```

Builds, convergence studies, and retained wavefunctions can use several additional GiB. See [files and recovery](docs/INSTALL.md#files-and-recovery) for what is stored and how updates work.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development checks and evidence requirements. The [changelog](CHANGELOG.md) describes the curl migration. Detailed audits and historical plans are available from the [documentation index](docs/README.md).

The installer and project tooling use the [MIT license](LICENSE). Quantum ESPRESSO and bundled upstream reference material retain their own licenses; see the [reference fixture license](fixtures/upstream-qe75/pw_scf/UPSTREAM_LICENSE). This is a community project, independent of the Quantum ESPRESSO developers.
