# Environment Notes

## Hardware / OS

- **Machine**: Mac mini (M4), Apple Silicon.
- **OS**: macOS 15.3 (Sequoia).
- **Kernel**: `Darwin 24.3.0`.
- **Command Line Tools**: `/Library/Developer/CommandLineTools` (16.4).

## Homebrew toolchain

| Package       | Version  | Notes                                  |
|---------------|----------|----------------------------------------|
| gcc           | 15.2.0   | Provides `gfortran` 15.2.0             |
| open-mpi      | 5.0.8    | MPI runtime (Apple Silicon bottle)     |
| cmake         | 4.1.2    | Required for the CMake/OpenBLAS path   |
| veclibfort    | 0.4.3    | Accelerate shim for BLAS/LAPACK        |
| openblas      | 0.3.30   | For experimental CMake builds          |
| wget          | 1.25.0   | Convenience downloader                 |
| python        | 3.13.x   | Matplotlib plotting scripts            |
| tcl-tk@8      | 8.6.x    | Tcl runtime required by PWTK           |

> The `Brewfile` locks the required formulae. Capture exact versions locally via `brew list --versions > logs/versions.txt` when you refresh the toolchain.

## Key macOS considerations

- **Preprocessor quirk**: CLT 16 defaults to `/usr/bin/cpp`, which breaks preprocessing of `laxlib_*.h`. Always run `./configure … CPP="gcc -E"` or set `export CPP="gcc -E"`.
- **FoX XML library**: QE 7.4.1 does not vendor `external/fox`. Clone `https://github.com/pietrodelugas/fox` into `artifacts/q-e-qe-7.4.1/external/fox/` (and remove its `.git` folder) before attempting the CMake + OpenBLAS path.
- **Python placement**: `pip --user` drops executables in `~/Library/Python/3.13/bin`. Add this directory to `PATH` if you want `matplotlib`, `f2py`, or related tools available globally.
- **GPU status**: Quantum ESPRESSO supports CUDA and ROCm backends only. Apple Metal GPUs (M1–M4) are not supported, so QE runs CPU-only on macOS.
- **Workflow layout**: The repo works case-by-case (`cases/si/manual`, `cases/si/pwtk`, `cases/common/pp`), unlike older M1 guides that placed everything at the root. Keep this structure so relative `pseudo_dir` paths continue to resolve.
- **PWTK runtime**: Install `tcl-tk@8` (`brew install tcl-tk@8`) and ensure `pwtk` uses `tclsh8.6`; Tcl 9.0 currently breaks the shipped scripts.
- **Recommended cutoffs**: The silicon example adopts the SSSP Efficiency 1.3.0 values for `Si.pbe-n-rrkjus_psl.1.0.0.UPF` (`ecutwfc = 30 Ry`, `ecutrho = 240 Ry`).

## Cannibalising this setup

1. `git clone https://github.com/shahpoll/qe_macm4_build.git`
2. `cd qe_macm4_build`
3. `brew bundle`
4. `scripts/setup/fetch_qe.sh qe-7.4.1`
5. Follow the [workflow recipes](Workflow.md) to rebuild and validate the silicon example.

For older macOS releases (Monterey/Ventura), these extra steps (`CPP="gcc -E"`, cloning FoX) are generally harmless but may not be strictly required.
