# Workflow Recipes (macOS 15.3 / M4)

Reference commands for the silicon validation case. Unless noted otherwise, run them from the repository root. New to QE? Start with `docs/Workflow_Basics.md` for a copy-paste friendly walkthrough, then come back here for the expanded recipe.

## 1. Configure QE (Accelerate + MPI)
```sh
cd artifacts/q-e-qe-7.4.1
./configure MPIF90=mpif90 CC=mpicc CPP="gcc -E" \
  BLAS_LIBS="-L$(brew --prefix veclibfort)/lib -lvecLibFort -framework Accelerate" \
  LAPACK_LIBS="-L$(brew --prefix veclibfort)/lib -lvecLibFort -framework Accelerate"
make -j pw
make -C PP/src bands.x dos.x projwfc.x
cd ../..
```
> `CPP="gcc -E"` is mandatory on Sequoia/CLT16 to avoid `laxlib_*.h` preprocessing failures.

## 2. Place pseudopotentials
```sh
curl -L -o cases/common/pp/Si.pbe-n-rrkjus_psl.1.0.0.UPF \
  https://pseudopotentials.quantum-espresso.org/upf_files/Si.pbe-n-rrkjus_psl.1.0.0.UPF
```

## 3. Manual silicon workflow (`cases/si/manual`)
```sh
cd cases/si/manual
../../../scripts/run_qe.sh pw.x -- -in data/Si.scf.in     | tee logs/si_scf.txt
../../../scripts/run_qe.sh pw.x -- -in data/Si.bands.in   | tee logs/si_bands_pw.txt
../../../scripts/run_qe.sh bands.x -- -in data/Si.bands_post.in  | tee logs/si_bands_post.txt
../../../scripts/run_qe.sh pw.x -- -in data/Si.nscf.in    | tee logs/si_nscf_pw.txt
../../../scripts/run_qe.sh dos.x -- -in data/Si.dos.in    | tee logs/si_dos.txt
../../../scripts/run_qe.sh projwfc.x -- -in data/Si.projwfc.in | tee logs/si_projwfc.txt

python3 scripts/plot_bands.py
python3 scripts/plot_dos.py
python3 scripts/plot_pdos.py
python3 scripts/analyze_bandgap.py
```
Artifacts: `data/` holds QE outputs (`silicon.*`, `si_band_summary.txt`), `logs/` contains transcripts, `plots/` captures the rendered figures. SCF uses an 8×8×8 mesh; NSCF/PDOS uses 12×12×12 with `nbnd=36` and energies shifted so E = 0 is the DOS-derived Fermi level.

## 4. PWTK reproduction (`cases/si/pwtk`)
```sh
cd ../../..
scripts/setup/fetch_pwtk.sh  # one-time download
export PATH="$PWD/external/pwtk-3.2:$PATH"
cd cases/si/pwtk
pwtk scripts/si_workflow.pwtk | tee logs/pwtk_run.log
python3 scripts/plot_bands.py
python3 scripts/plot_dos.py
python3 scripts/plot_pdos.py
python3 scripts/analyze_bandgap.py
```
> Ensure `tclsh8.6` is available (`brew install tcl-tk@8`), add `external/pwtk-3.2` to `PATH`, and keep `cases/common/pp` on the PWTK `pseudo_dir`. To reuse the MPI wrapper, set `prefix /path/to/scripts/run_qe.sh` and optional `QE_RANKS`/`QE_CPUSET` lines in `~/.pwtk/pwtk.tcl`.

## 5. Manual vs PWTK comparison (`cases/si/comparison`)
```sh
cd ../comparison
python3 scripts/compare_runs.py
```
Produces `data/si_comparison.txt` and `plots/si_manual_vs_pwtk.png`.

## Optional: convergence scans (`cases/si/convergence`)
```sh
cd ../../cases/si/convergence
python3 run_convergence.py
```
Generates CSV/JSON tables and ΔE plots for the cutoff (30–60 Ry, dual = 8) and k-mesh (4×4×4 → 10×10×10) studies.

## Optional: CMake + OpenBLAS (still experimental)
```sh
cd ../../artifacts/q-e-qe-7.4.1
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
> Clone `external/fox` or disable `__XML_STANDALONE` to avoid `wxml` compilation failures.
