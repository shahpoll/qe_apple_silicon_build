# Silicon (Si) via PWTK — QE 7.4.1 / macOS 15.3

This folder mirrors the manual QE workflow using PWTK scripts.

## Artifacts

- `scripts/si_workflow.pwtk` — orchestrates SCF → NSCF → BANDS → DOS → PDOS (8×8×8 SCF, 12×12×12 NSCF, `nbnd=36`).
- `logs/pwtk_run.log` — stdout from the PWTK execution.
- QE inputs/outputs:
  - `pw.si.scf.in`, `pw.si.scf.out`, ...
  - `dos.si.in`, `dos.si.out`, etc.
- `data/` — consolidated results (`silicon.dos`, `silicon.bands.dat`, `silicon_pdos.*`, `si_band_summary.txt`).
- `plots/` — visuals regenerated from the data (band structure, total DOS, PDOS).

## Workflow reference

1. Ensure Tcl 8.6 and PWTK 3.2 are on the PATH:
   ```sh
   REPO=/path/to/qe_macm4_build
   export PATH="/opt/homebrew/opt/tcl-tk@8/bin:$PATH"
   export PATH="$REPO/external/pwtk-3.2:$PATH"
   ```
2. Run the PWTK script from this directory:
   ```sh
   cd "$REPO/cases/si/pwtk"
   ../../../external/pwtk-3.2/pwtk scripts/si_workflow.pwtk | tee logs/pwtk_run.log
   ```
3. Generate plots and summaries:
   ```sh
   cd "$REPO/cases/si/pwtk"
   python3 scripts/plot_bands.py
   python3 scripts/plot_dos.py
   python3 scripts/plot_pdos.py
   python3 scripts/analyze_bandgap.py
   ```

Results can now be compared directly with the manual QE run under `../manual/`
or bundled overlays in `../comparison/`. The same convergence and PDOS settings
apply (30/240 Ry cutoffs, energy axis aligned to E_F).

### Parallel wrapper from PWTK

PWTK prepends whatever command you assign to `prefix` inside `~/.pwtk/pwtk.tcl`. To reuse the MPI tuning from this repo, set:

```tcl
# ~/.pwtk/pwtk.tcl
set repo "/path/to/qe_macm4_build"
prefix $repo/scripts/run_qe.sh
set ::env(QE_RANKS) 8           ;# default ranks (edit as desired)
set ::env(QE_CPUSET) "0-9"      ;# optional CPU set covering perf + eff cores
```

PWTK will then invoke `run_qe.sh pw.x ...` (or `bands.x`, etc.) and inherit the same binding/`OMP_NUM_THREADS` defaults as the manual workflow.
