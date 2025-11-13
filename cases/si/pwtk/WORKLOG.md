# Si Workflow via PWTK — Notes

## 2025-11-02 — Clean end-to-end run
- Installed Tcl 8.6 from Homebrew (`brew install tcl-tk@8`) and prepended `/opt/homebrew/opt/tcl-tk@8/bin` to `PATH` so `pwtk` picks up `tclsh8.6`.
- Downloaded PWTK 3.2 with `scripts/setup/fetch_pwtk.sh`, which unpacks into `external/pwtk-3.2`.
- Added `export PATH="$REPO/external/pwtk-3.2:$PATH"` (where `REPO=$(pwd)` at the repo root) so `pwtk` resolves without absolute paths.
- Cloned the default config snippet into `~/.pwtk/pwtk.tcl`, pointing `bin_dir` to `artifacts/q-e-qe-7.4.1/bin` and `pseudo_dir` to `cases/common/pp`. Added
  ```tcl
  prefix $REPO/scripts/run_qe.sh
  set ::env(QE_RANKS) 8
  set ::env(QE_CPUSET) "0-9"
  ```
  to make PWTK reuse the same MPI binding policy as the manual workflow (falls back cleanly when hwloc rejects binding).
- From `cases/si/pwtk` ran:
  ```sh
  ../../../external/pwtk-3.2/pwtk scripts/si_workflow.pwtk | tee logs/pwtk_run.log
  ```
  which sequentially launched SCF → NSCF → BANDS → DOS → PDOS (8×8×8 SCF, 12×12×12 NSCF, `nbnd=36`). QE executables came from `artifacts/q-e-qe-7.4.1/bin`.
- Regenerated the plots/data wrappers:
  ```sh
  python3 scripts/plot_bands.py
  python3 scripts/plot_dos.py
  python3 scripts/plot_pdos.py
  python3 scripts/analyze_bandgap.py
  ```
- Copied the resulting `silicon.*` data into `cases/si/pwtk/data/` and compared against the manual run via `cases/si/comparison/scripts/compare_runs.py`. Max discrepancies stayed below 1e-10 eV; DOS traces differ only by the usual normalization factor noted in `si_comparison.txt`.

## Carry-over lessons
- PWTK must run under Tcl 8.6 on macOS 15; Tcl 9.0 triggers “unknown command print/varvalue/time2ms” because bundled modules are not yet 9.x-compatible.
- Keep PWTK outside of git (under `external/`) and refer to it relative to each case directory (`../../../external/pwtk-3.2/pwtk`).
- The MPI wrapper is optional; PWTK will default to serial binaries unless `prefix` points at `scripts/run_qe.sh`. Retain serial preprocessing (`wannier90.x -pp`, etc.) as required by upstream docs.
