# Troubleshooting (macOS 15.3, Apple Silicon)
- `make[1]: laxlib*.fh ... no input files`: rerun configure with `CPP="gcc -E"`. Ref: QE user guide, “Installation tricks and problems”.
- `wxml.f90: DP_XML has no implicit type`: clone `external/fox` (QE 7.4.1 no longer ships it) or drop the `__XML_STANDALONE` definition before rebuilding `qe_xml`. Alternatively pass `--with-fox=yes` (configure) or `-DFOX=ON` (CMake) so QE builds the FoX dependency automatically.
- MPI quirks: prefer Homebrew OpenMPI bottles for Sequoia; if runtime issues persist, document and consider MPICH after removing OpenMPI.
- Linker proof: keep `otool -L` for `pw.x` to show Accelerate (veclibfort) or OpenBLAS plus MPI.
- Pseudopotentials now live under `cases/common/pp`; update legacy scripts or guides that expect `./pp` at the repo root.
- PWTK needs Tcl 8.6 (`brew install tcl-tk@8`) on macOS 15.3; pin the `pwtk` shebang or adjust `PATH` accordingly.
- Legacy M1 guides assume FoX was bundled and often run everything from the repo root. On M4/Sequoia use the case directories (`cases/si/...`) so relative `pseudo_dir` paths continue to work.
- Expect the NSCF/DOS Fermi level to differ from the SCF value by ~0.2 eV (denser k-mesh, Gaussian smearing). See `cases/si/comparison/data/fermi_consistency.csv` for the recorded values.
- MPI oversubscription: keep `OMP_NUM_THREADS=1` and use a small rank count (e.g. `QE_RANKS=2 ./scripts/run_qe.sh pw.x -- -in ...`) on laptops to avoid misleading timings.
