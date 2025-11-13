# Quantum ESPRESSO 7.4.1 on Apple Silicon (M4) — Reproducible Playbook

This guide assumes a clean macOS 15.3 environment with Command Line Tools (CLT) installed (`xcode-select --install`). All commands are executed from the repository root (`qe_macm4_build`).

## 1. Homebrew toolchain
```sh
brew update
brew bundle
```

Notes:
- `veclibfort` exposes Apple’s Accelerate BLAS/LAPACK through the GNU calling convention.
- Homebrew’s Python is optional but guarantees a recent `pip` for plotting utilities.

## 2. Workspace layout

The repository ships with a case-oriented layout:

- `cases/common/pp` — shared pseudopotentials (PSLibrary ultrasoft Si is provided).
- `cases/common/scripts` — reusable plotting/analysis helpers.
- `cases/si/manual` — manual QE run (data, logs, plots, wrappers).
- `cases/si/pwtk` — PWTK-driven reproduction of the manual run.
- `cases/si/comparison` — overlays and diff metrics between the two workflows.

If you are bootstrapping from scratch, create the directories above before populating them.

## 3. Fetch Quantum ESPRESSO
If the `artifacts/q-e-qe-7.4.1` tree is absent:
```sh
scripts/setup/fetch_qe.sh qe-7.4.1
```

### (Optional) FoX XML library
The CMake build path expects FoX sources when `__XML_STANDALONE` is disabled. Clone them ahead of time:
```sh
git clone --depth 1 https://github.com/pietrodelugas/fox.git artifacts/q-e-qe-7.4.1/external/fox
rm -rf artifacts/q-e-qe-7.4.1/external/fox/.git
```

## 4. Configure build (Accelerate + MPI)
```sh
cd artifacts/q-e-qe-7.4.1
./configure MPIF90=mpif90 CC=mpicc CPP="gcc -E" \
  BLAS_LIBS="-L$(brew --prefix veclibfort)/lib -lvecLibFort -framework Accelerate" \
  LAPACK_LIBS="-L$(brew --prefix veclibfort)/lib -lvecLibFort -framework Accelerate"
make -j pw
make -C PP/src bands.x  # brings in bands.x for post-processing
cd ../..
```
The `CPP="gcc -E"` override avoids the header-mangling bug triggered by Apple’s `cpp`.

## 5. Example pseudopotential and inputs
```sh
curl -L -o cases/common/pp/Si.pbe-n-rrkjus_psl.1.0.0.UPF \
  https://pseudopotentials.quantum-espresso.org/upf_files/Si.pbe-n-rrkjus_psl.1.0.0.UPF
```
Sample inputs for the silicon case live under `cases/si/manual/data/` and are
ready to use.

## 6. Run the silicon SCF example
```sh
cd cases/si/manual
../../../scripts/run_qe.sh pw.x -- -in data/Si.scf.in | tee logs/si_scf.txt
```
Outputs:
- `tmp/silicon.save`: wavefunctions and charge density (collected wavefunctions saved).
- `logs/si_scf.txt`: convergence history (≈5 iterations, `E_F ≈ 6.43 eV`).
- SCF mesh is 8×8×8, consistent with the convergence scans in `cases/si/convergence/`.

## 7. Band-structure workflow
Still inside `cases/si/manual`:
```sh
../../../scripts/run_qe.sh pw.x -- -in data/Si.bands.in | tee logs/si_bands_pw.txt
../../../scripts/run_qe.sh bands.x -- -in data/Si.bands_post.in | tee logs/si_bands_post.txt
cp silicon.bands.dat* data/
```
Generate a plot (Matplotlib installed once via `python3 -m pip install --user matplotlib`):
```sh
python3 scripts/plot_bands.py
```
Result: `plots/si_band_structure.png`.

Optional: regenerate DOS/PDOS after the NSCF step (`scripts/plot_dos.py`, `scripts/plot_pdos.py`).

## 8. (Optional) CMake + OpenBLAS build
This path is still experimental on macOS due to FoX preprocessing issues. To attempt it:
```sh
cd artifacts/q-e-qe-7.4.1
OBLAS=$(brew --prefix openblas)
cmake -S . -B buildA \
  -DCMAKE_Fortran_COMPILER=mpif90 \
  -DCMAKE_C_COMPILER=mpicc \
  -DQE_ENABLE_MPI=ON \
  -DQE_ENABLE_OPENMP=ON \
  -DBLAS_LIBRARIES="$OBLAS/lib/libopenblas.dylib" \
  -DLAPACK_LIBRARIES="$OBLAS/lib/libopenblas.dylib"
cmake --build buildA --target pw -j
```
If `wxml.f90` fails with `DP_XML` errors, ensure `external/fox` exists **and** remove the `target_compile_definitions(qe_xml PRIVATE __XML_STANDALONE)` line from `upflib/CMakeLists.txt`. This forces QE to reuse the FoX-provided `DP_XML` type.

## 9. Housekeeping
- Band/project files are archived under `cases/si/manual/data/` (manual) and `cases/si/pwtk/data/` (PWTK).
- Convergence artefacts (CSV/JSON + plots) live in `cases/si/convergence/`; re-run with `python3 cases/si/convergence/run_convergence.py`.
- Shared plotting helpers live in `cases/common/scripts/`; workflow-specific wrappers sit beside each case.
- Bundle artefacts with `zip -r qe_macm4_attempt_bundle_v*.zip logs docs cases artifacts/q-e-qe-7.4.1/INSTALL.md` as needed.

## 10. Apple Silicon evolution notes
- **macOS/CLT vintage matters more than the chip.** Sequoia (macOS 15.3+) plus CLT 16.x introduces the stricter `/usr/bin/cpp` that mangles `laxlib_*.h`, so `CPP="gcc -E"` is mandatory here. This flag is harmless on older releases.
- **FoX XML now external.** QE 7.4.1 no longer ships the FoX subtree; clone `external/fox` (or drop `__XML_STANDALONE`) before attempting a CMake/OpenBLAS build. Legacy M1 guides assumed the library was bundled.
- **Python user installs.** The system Python on Sequoia is sandboxed; we rely on `pip --user` and adjust `PATH` for Matplotlib. Earlier guides that used `/usr/local/bin/python3` from Homebrew still work, but this approach is future-proof.
- **Accelerate-first stance.** veclibfort + Accelerate is the stable option on current macOS. The OpenBLAS/CMake combo mirrors Linux but remains experimental until the FoX toggle is addressed.
- **GPU expectation unchanged.** QE still exposes CUDA/ROCm only; Apple’s Metal GPUs (including M4) remain unsupported.

Following these steps on any Apple Silicon Mac that runs Sequoia+CLT16 will yield the same result; on older macOS versions the extra workarounds simply become no-ops.

## 11. Limitations
- **GPU acceleration:** QE’s GPU backends target NVIDIA CUDA and AMD ROCm. Apple’s Metal API is not supported, so the M4’s GPU remains unused.
- **OpenBLAS path:** The CMake toolchain requires manual FoX setup; Accelerate is the stable default on macOS today.
- **Library paths:** Homebrew installs everything under `/opt/homebrew`; no `DYLD_LIBRARY_PATH` tweaks were required in testing.

Follow these steps to reproduce the working configuration captured in the repository. Adapt k-point meshes, cutoffs, or post-processing tools as your workloads demand.

## PWTK helper

Download the Tcl-based PWTK front-end only when needed:
```sh
scripts/setup/fetch_pwtk.sh
export PATH="$PWD/external/pwtk-3.2:$PATH"
```
Ensure `tclsh8.6` comes from Homebrew (`brew bundle` installs `tcl-tk@8`).

## Wannier90 MPI build

After `make w90`, switch into `external/wannier90`, remove any old objects (`rm -rf src/obj src/objp`), and rebuild with MPI enabled:
```sh
cd artifacts/q-e-qe-7.4.1/external/wannier90
rm -rf src/obj src/objp
make COMMS=mpi wannier
cp wannier90.x ../../bin/wannier90.x_mpi
rm -rf src/obj src/objp
make wannier
```
`wannier90.x -pp` stays serial; launch the MPI binary with the usual wrapper, e.g. `scripts/run_qe.sh wannier90.x_mpi -- mycalc`.
