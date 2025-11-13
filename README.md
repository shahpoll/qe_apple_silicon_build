# QE on Apple Silicon (M4)

Guides, scripts, and convergence data to build Quantum ESPRESSO 7.4.1 on macOS 15 (Apple Silicon). This repository keeps only helper files; Quantum ESPRESSO sources are fetched on demand.

## Quick Start

*Shortcut:* after cloning, run `bash scripts/setup/bootstrap.sh --with-pwtk --build-accelerate` to install the toolchain, fetch QE 7.4.1, download the silicon pseudopotential, and (optionally) grab PWTK in one go. Manual steps are listed below.

1. Clone: `git clone https://github.com/shahpoll/qe_macm4_build.git`
2. Change directory: `cd qe_macm4_build`
3. Install prerequisites: `brew bundle`
4. Fetch QE: `scripts/setup/fetch_qe.sh qe-7.4.1`
5. Build (Accelerate):
   ```sh
   cd artifacts/q-e-qe-7.4.1
   ./configure MPIF90=mpif90 CC=mpicc CPP="gcc -E"      BLAS_LIBS="-L$(brew --prefix veclibfort)/lib -lvecLibFort -framework Accelerate"      LAPACK_LIBS="-L$(brew --prefix veclibfort)/lib -lvecLibFort -framework Accelerate"
   make -j pw
   make -C PP/src bands.x dos.x projwfc.x
   cd ../..
   ```
6. Optional OpenBLAS build (CMake):
   ```sh
   cd artifacts/q-e-qe-7.4.1
   cmake --preset openblas-release
   cmake --build build/openblas-release -j
   cd ../..
   ```
7. (Optional) Fetch PWTK for automated runs: `scripts/setup/fetch_pwtk.sh` (then `export PATH="$(pwd)/external/pwtk-3.2:$PATH"` as needed)
8. Populate pseudopotential: `curl -L -o cases/common/pp/Si.pbe-n-rrkjus_psl.1.0.0.UPF https://pseudopotentials.quantum-espresso.org/upf_files/Si.pbe-n-rrkjus_psl.1.0.0.UPF`
9. Run SCF/NSCF/BANDS/DOS/PDOS (manual workflow):
   ```sh
   cd cases/si/manual
   ../../../scripts/run_qe.sh pw.x -- -in data/Si.scf.in | tee logs/si_scf.txt
   ../../../scripts/run_qe.sh pw.x -- -in data/Si.bands.in | tee logs/si_bands_pw.txt
   ../../../scripts/run_qe.sh bands.x -- -in data/Si.bands_post.in | tee logs/si_bands_post.txt
   ../../../scripts/run_qe.sh pw.x -- -in data/Si.nscf.in | tee logs/si_nscf_pw.txt
   ../../../scripts/run_qe.sh dos.x -- -in data/Si.dos.in | tee logs/si_dos.txt
   ../../../scripts/run_qe.sh projwfc.x -- -in data/Si.projwfc.in | tee logs/si_projwfc.txt
   ```
10. Regenerate plots: `python3 scripts/plot_bands.py`, `plot_dos.py`, `plot_pdos.py`, `analyze_bandgap.py`
11. Smoke test: `python3 ../../../scripts/smoke_test.py`

Need a friendlier, copy-pasteable walkthrough? See `docs/Workflow_Basics.md`.

## Repository Layout

| Path | Purpose |
|------|---------|
| `Brewfile` | Homebrew bundle for reproducible toolchain. |
| `CMakePresets.json` | Preset for OpenBLAS+CMake build. |
| `scripts/setup/fetch_qe.sh` | Helper to download QE releases. |
| `scripts/setup/fetch_pwtk.sh` | Helper to download PWTK 3.2 (Tcl driver). |
| `scripts/run_qe.sh` | MPI wrapper with binding/CPU-set helpers. |
| `cases/common/scripts/` | Shared plotting/analysis utilities (energy aligned to E_F). |
| `cases/common/pp/` | Pseudopotentials (PSLibrary / SSSP). |
| `cases/si/manual/` | Manual workflow inputs, logs, plots, and derived data (SCF 8×8×8, NSCF 12×12×12, nbnd=36). |
| `cases/si/pwtk/` | Equivalent workflow driven via PWTK. |
| `cases/si/comparison/` | Manual vs PWTK overlays, benchmarks, Fermi table. |
| `cases/si/convergence/` | Cutoff and k-mesh scans (CSV/JSON + plots, see README there). |

## Physics checkpoints

- **Cutoff & k-mesh** — `cases/si/convergence/` holds scripts/results showing that 30/240 Ry with an 8×8×8 SCF mesh keeps ΔE ≤ 2 meV/atom and Δgap ≤ 1 meV relative to tighter settings.
- **SCF ↔ NSCF consistency** — `cases/si/comparison/data/fermi_consistency.csv` records SCF vs DOS Fermi levels (~0.21 eV offset due to denser NSCF grid) and the matching 0.5699 eV indirect gap.
- **PDOS setup** — NSCF & `projwfc.x` run with `nbnd=36`, Gaussian `DeltaE=0.05 eV`, energies shifted so E=0 corresponds to E_F. DOS normalisation differs slightly between manual and PWTK paths (median scaling ≈1.2); shapes coincide after normalisation as noted in `si_comparison.txt`.
- **GPU expectations** — Quantum ESPRESSO GPU acceleration targets CUDA/OpenACC backends; Apple Metal GPUs are unsupported. All workflows here are CPU-only.

## Build options

### Accelerate + veclibfort (default)

Links QE against Apple's Accelerate framework while vecLibFort provides GNU-compatible BLAS/LAPACK symbols (Accelerate exports BLAS with mixed symbol names; vecLibFort shims them for Fortran). This path mirrors the official QE documentation for macOS and requires the `CPP="gcc -E"` workaround documented above.

### OpenBLAS via CMake

Use the supplied preset or run CMake manually with Homebrew OpenBLAS. This mirrors Linux builds and avoids the CPP quirks that sometimes appear with `configure`. If XML I/O fails at `wxml.f90`, either clone FoX into `external/fox/` or pass `-DFOX=ON`/`--with-fox` per the QE build notes.

## MPI & CPU layout

Apple Silicon splits cores into performance (`hw.perflevel0`) and efficiency (`hw.perflevel1`). Query the counts:

```sh
sysctl -n hw.perflevel0.physicalcpu hw.perflevel1.physicalcpu
```

On this Mac mini M4 the output is `4 6`, i.e. 4 performance and 6 efficiency cores (10 total hardware threads). To drive QE across these cores we provide `scripts/run_qe.sh`, a thin wrapper around `mpirun` that:

- defaults to 8 MPI ranks, `--map-by ppr:1:core --bind-to core` (fill all four performance cores plus four efficiency cores),
- exports `OMP_NUM_THREADS=1` unless you override it,
- honours `QE_RANKS`, `QE_BINDING`, and `QE_CPUSET` env vars.

Examples (run from the repo root so the `cases/si/manual/...` paths resolve):

```sh
# Use only the four performance cores
QE_RANKS=4 QE_CPUSET=0-3 ./scripts/run_qe.sh pw.x -- -in cases/si/manual/data/Si.scf.in

# Use all 10 cores (4 P + 6 E); expect diminishing returns beyond 8 ranks
QE_RANKS=10 QE_CPUSET=0-9 ./scripts/run_qe.sh pw.x -- -in cases/si/manual/data/Si.nscf.in
```

Re-export `QE_RANKS`, `QE_CPUSET`, and `OMP_NUM_THREADS` every time you start a new shell session; otherwise the wrapper falls back to its defaults and hwloc may reject the binding on macOS.
Start with the performance cores (4 ranks), then add efficiency cores in pairs (6, 8, 10 ranks) and watch scaling. QE’s FFT-heavy workload typically benefits up to ~8 ranks on this machine; the last two efficiency cores provide modest gains. Always keep `OMP_NUM_THREADS=1` unless conducting a hybrid MPI/OMP study. The wrapper works for any QE executable (`pw.x`, `bands.x`, `dos.x`, `projwfc.x`, etc.) and prints the chosen configuration before launching.

macOS’s hwloc can refuse to set CPU affinity. When that happens Open MPI aborts with “binding not available”; `scripts/run_qe.sh` detects this and retries with `--bind-to none --map-by ppr:1:core`. If you need custom binding, set `QE_BINDING` (e.g. `QE_BINDING="--bind-to none"`) to override the default.

## Wannier90 (serial vs MPI)

`make w90` (run at the QE top level) fetches Wannier90 into `artifacts/q-e-qe-7.4.1/external/wannier90/` and links the serial executables into `artifacts/q-e-qe-7.4.1/bin`. Wannier preprocessing (`wannier90.x -pp`) must remain serial, but production runs benefit from MPI. Building the MPI-aware binary avoids the “file cannot be deleted” error you hit when launching the serial executable under `mpirun`.

Steps to produce `wannier90.x_mpi` (assuming QE is already configured):

```sh
cd artifacts/q-e-qe-7.4.1/external/wannier90
rm -rf src/obj src/objp                 # clean without relying on python
make COMMS=mpi wannier                  # rebuild with MPI comms enabled
cp wannier90.x ../../bin/wannier90.x_mpi
rm -rf src/obj src/objp
make wannier                            # restore the default serial build
```

Usage:

- Pre-processing: `wannier90.x -pp mycalc` (serial).
- Parallel run: `scripts/run_qe.sh wannier90.x_mpi -- mycalc` (override `QE_RANKS`/`QE_CPUSET` just like for `pw.x`).

## Documentation

- [Apple Silicon Guide](docs/AppleSilicon_QE_Guide.md)
- [Beginner Workflow](docs/Workflow_Basics.md)
- [Troubleshooting](docs/Troubleshooting.md)
- [Si Worklog](docs/Si_Worklog.md)
- [Pseudopotentials](docs/PP.md)
- [Wiki snapshots](docs/wiki/)

## How to cite

Use the metadata in `CITATION.cff` or cite this repository directly. The project is released under the MIT License (see `LICENSE`).
