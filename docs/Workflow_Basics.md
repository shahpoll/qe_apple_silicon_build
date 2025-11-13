# Beginner Workflow (macOS 15 / Apple Silicon)

Follow these steps verbatim to install the prerequisites, build Quantum ESPRESSO, and run the silicon example without hunting through multiple guides.

## 0. One-liner bootstrap (clone → setup)

```sh
git clone https://github.com/shahpoll/qe_macm4_build.git
cd qe_macm4_build
bash scripts/setup/bootstrap.sh --with-pwtk --build-accelerate
```

> The bootstrapper installs the Homebrew toolchain, fetches QE 7.4.1, downloads the silicon pseudopotential, optionally grabs PWTK 3.2, and builds the Accelerate+MPI executable set.

## 1. Prepare your shell

```sh
cd /path/to/qe_macm4_build
export PATH="$PWD/external/pwtk-3.2:$PATH"   # only if you passed --with-pwtk
```

If you skipped the `--with-pwtk` flag you can still run manual workflows; PWTK is optional.

## 2. ALWAYS set core usage before any QE command

Apple Silicon splits performance and efficiency cores. The MPI wrapper does **not** guess for you—export the layout each time you open a new terminal or before you run a script:

```sh
export QE_RANKS=8          # 4 performance + 4 efficiency cores
export QE_CPUSET=0-9       # cover all 10 cores; adjust (e.g., 0-3) for quieter runs
export OMP_NUM_THREADS=1   # keep QE in pure-MPI mode
```

To run a QE executable, *always* go through the wrapper:

```sh
./scripts/run_qe.sh pw.x -- -in cases/si/manual/data/Si.scf.in
```

If you forget to set `QE_RANKS`/`QE_CPUSET`, QE will default to 8 ranks on arbitrary cores and hwloc may abort. Make it a habit to export these vars (or add them to your shell rc file) before every session.

## 3. Silicon workflow (manual path)

```sh
cd cases/si/manual

# SCF
../../../scripts/run_qe.sh pw.x -- -in data/Si.scf.in     | tee logs/si_scf.txt

# Band path
../../../scripts/run_qe.sh pw.x -- -in data/Si.bands.in   | tee logs/si_bands_pw.txt
../../../scripts/run_qe.sh bands.x -- -in data/Si.bands_post.in | tee logs/si_bands_post.txt

# NSCF, DOS, PDOS
../../../scripts/run_qe.sh pw.x -- -in data/Si.nscf.in    | tee logs/si_nscf_pw.txt
../../../scripts/run_qe.sh dos.x -- -in data/Si.dos.in    | tee logs/si_dos.txt
../../../scripts/run_qe.sh projwfc.x -- -in data/Si.projwfc.in | tee logs/si_projwfc.txt

# Plots + summary
python3 scripts/plot_bands.py
python3 scripts/plot_dos.py
python3 scripts/plot_pdos.py
python3 scripts/analyze_bandgap.py
```

Outputs land in `data/`, `logs/`, and `plots/`. Each plotting script automatically aligns energies so that the DOS-derived Fermi level is at 0 eV.

## 4. Optional: fully automated PWTK workflow

```sh
cd ../../si/pwtk
../../../external/pwtk-3.2/pwtk scripts/si_workflow.pwtk | tee logs/pwtk_run.log
python3 scripts/plot_bands.py
python3 scripts/plot_dos.py
python3 scripts/plot_pdos.py
python3 scripts/analyze_bandgap.py
```

Remember to keep the same `QE_RANKS`/`QE_CPUSET` exports in effect before you start PWTK—the toolkit forwards your environment to `scripts/run_qe.sh`.

## 5. What you just installed

- Homebrew GCC/OpenMPI/CMake/veclibfort/OpenBLAS (see `Brewfile`)
- Quantum ESPRESSO 7.4.1 sources under `artifacts/q-e-qe-7.4.1`
- Silicon PSLibrary pseudopotential under `cases/common/pp/`
- Optional PWTK 3.2 under `external/`

Review `docs/Workflow_Basics.md` any time you need the quick recipe again, and consult `docs/Troubleshooting.md` if a step fails. Keeping the multi-core exports in place is the key difference between smooth runs and hwloc binding errors on Apple Silicon.
