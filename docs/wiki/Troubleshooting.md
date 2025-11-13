# Troubleshooting FAQ

See also [`docs/Troubleshooting.md`](../Troubleshooting.md) for the full in-repo version.

## `make[1]: laxlib*.fh ... no input files`

- Symptom: preprocessing fails while building `LAXlib`.
- Fix: rerun `./configure` with `CPP="gcc -E"` (or export `CPP` globally) so that CLT 16 uses GNU cpp semantics.

## `wxml.f90: DP_XML has no implicit type`

- Symptom: CMake/OpenBLAS build fails compiling `upflib/wxml.f90`.
- Cause: QE 7.4.1 expects FoX sources when `__XML_STANDALONE` is off; cloning FoX or removing the `__XML_STANDALONE` define resolves it. You can also pass `--with-fox=yes` (configure) or `-DFOX=ON` (CMake) to let QE build the library automatically.

## `pp.x`/`pw.x` cannot find pseudopotentials

- Ensure pseudopotentials live in `cases/common/pp` (e.g., `Si.pbe-n-rrkjus_psl.1.0.0.UPF`).
- Workflow inputs target `pseudo_dir='../../common/pp'`; run QE from the corresponding case directory (`cases/si/manual`, `cases/si/pwtk`).

## `projwfc.x` missing

- By default `make pw` does not build post-processing tools. Run `make -C PP/src projwfc.x dos.x bands.x` in the QE source tree.

## Where is Matplotlib?

- `pip --user` installs to `~/Library/Python/3.13/bin`. Add this directory to `PATH` if the plotting wrappers under `cases/si/*/scripts` cannot find `matplotlib`.

## GPU acceleration?

- Not on Apple Silicon. QE supports CUDA/ROCm only; Metal GPUs are not yet supported upstream.

## SCF vs DOS Fermi level mismatch

- Expect DOS/PDOS workflows (denser k-mesh, Gaussian smearing) to report Fermi levels ~0.2 eV lower than the SCF value.
- See `cases/si/comparison/data/fermi_consistency.csv` for the recorded offsets (manual vs PWTK).

## MPI oversubscription

- Use a small number of MPI ranks (e.g. `mpirun -n 2`) and set `OMP_NUM_THREADS=1` to avoid oversubscription on Apple Silicon laptops; treat timings as illustrative only.
