# Quantum ESPRESSO on Apple Silicon — Minimal Guide (M4 / macOS 15.3)
1. Install the toolchain: `brew bundle`.
2. Fetch QE sources: `scripts/setup/fetch_qe.sh qe-7.4.1` (populates `artifacts/q-e-qe-7.4.1/`).
3. Configure the Accelerate build (preferred on macOS):
   ```sh
   cd artifacts/q-e-qe-7.4.1
   ./configure MPIF90=mpif90 CC=mpicc CPP="gcc -E" \
     BLAS_LIBS="-L$(brew --prefix veclibfort)/lib -lvecLibFort -framework Accelerate" \
     LAPACK_LIBS="-L$(brew --prefix veclibfort)/lib -lvecLibFort -framework Accelerate"
   make -j pw
   make -C PP/src bands.x
   cd ../..
   ```
4. Fetch pseudopotentials once: `curl -L -o cases/common/pp/Si.pbe-n-rrkjus_psl.1.0.0.UPF https://pseudopotentials.quantum-espresso.org/upf_files/Si.pbe-n-rrkjus_psl.1.0.0.UPF` (SSSP Efficiency recommends 30/240 Ry for this UPF).
5. Run the silicon workflow (manual path, SCF 8×8×8; NSCF 12×12×12 with nbnd=36):
   ```sh
   cd cases/si/manual
   ../../../scripts/run_qe.sh pw.x -- -in data/Si.scf.in | tee logs/si_scf.txt
   ../../../scripts/run_qe.sh pw.x -- -in data/Si.bands.in | tee logs/si_bands_pw.txt
   ../../../scripts/run_qe.sh bands.x -- -in data/Si.bands_post.in | tee logs/si_bands_post.txt
   ../../../scripts/run_qe.sh pw.x -- -in data/Si.nscf.in | tee logs/si_nscf_pw.txt
   ../../../scripts/run_qe.sh dos.x -- -in data/Si.dos.in | tee logs/si_dos.txt
   ../../../scripts/run_qe.sh projwfc.x -- -in data/Si.projwfc.in | tee logs/si_projwfc.txt
   ```
6. Regenerate plots and summaries in-place: `python3 scripts/plot_bands.py`, `python3 scripts/plot_dos.py`, `python3 scripts/plot_pdos.py`, `python3 scripts/analyze_bandgap.py` (energy axes are shifted so E = 0 is the DOS-derived Fermi level).
7. Optional PWTK reproduction:
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
8. Comparison artefacts live under `cases/si/comparison` (`python3 scripts/compare_runs.py`).
9. Run `python3 cases/si/convergence/run_convergence.py` to regenerate the cutoff/k-mesh scans (CSV/JSON + plots).

### Commands logged
```
./configure MPIF90=mpif90 CC=mpicc CPP="gcc -E" ...
make -j pw
make -C PP/src bands.x
../../../scripts/run_qe.sh pw.x -- -in data/Si.scf.in | tee logs/si_scf.txt
```

10. If CMake complains about FoX (`wxml.f90`), enable it with `-DFOX=ON` or clone `external/fox` as described in the Apple Silicon guide.
11. GPU acceleration on Apple Silicon is not available; all runs execute on CPU cores only.
