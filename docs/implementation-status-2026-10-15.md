# Device validation and implementation status — 15 October 2026

Historical snapshot. For the October 30 publication and current installation instructions, see [validation status](VALIDATION.md) and [installation](INSTALL.md). Statements about publication below describe the state on October 15.

The curl manager and validator repairs are implemented. The supported core profile has passed on this device. Comprehensive workstation qualification and independent implementation review remain incomplete; no W00–W15 item is declared CLOSED.

Final assembled integration: the installed manager completed a new clean build with 107 executables and complete dependency manifests, then passed all 21 core qualification cases before activating its isolated `final-built-core/current` pointer. The final strict OpenBLAS convergence study passed 62 cases and final-build force/stress consistency passed 11. The fresh 51-case upstream catalog has 33 PASS, 17 BLOCKED and 1 FAIL: methane Lanczos prints NaN in a response component and its spectrum is blocked. That solver remains unqualified on the fresh build even though the older staged build passed. These latest results supersede any broader interpretation of the historical table below. Exact paths/hashes and all failed attempts are in the external `FINAL_REPORT.md` and `FINAL_MANIFEST.json`.

Authorization: the user requested implementation of the audit suggestions, existing tools without Homebrew, and preserved success/failure logs. The original installation at `/Users/pollob/opt/qe-7.5` was retained. No release was published. The sibling Homebrew tap was left alone.

## Environment and evidence

Apple M4, 16 GiB RAM, 10 CPUs, native arm64 macOS 26.3 (25D125); GCC/gfortran 15.2, OpenMPI 5.0.8, CMake 4.1.2. Existing tools/libraries can live under `/opt/homebrew`; their location does not require invoking that package manager. Python 3.14 produced numerical verdicts without NumPy or Matplotlib. PWTK 3.2 used existing Tcl 8.6.

All new evidence is separate from the repository at `/Users/pollob/QE_macos26/remediation-2026-10-15`. Each command has a unique directory under `commands/`, raw stdout/stderr, argv, timing and terminal state. `commands/index.jsonl` is the command index; `runs/` and `builds/` contain complete campaigns. `baseline/` preserves the original source, audit and hash inventory. `FINAL_REPORT.md` in that evidence directory records final package/integration results and remaining prerequisites. Older attempts are retained even after a correction passes.

## Verified finite scope

| Evidence directory | Result and meaning |
|---|---|
| `builds/openblas-002` | Clean QE 7.5 CMake build, upstream seed, 21 advertised executables staged inactive; original failed compiler-alias attempt preserved. |
| `runs/core-final-source-002` | 21 PASS: authentic NC upstream SCF, silicon core workflow, actual ranks 1/2/4 and three repeats. |
| `runs/convergence-openblas-002` | 62 PASS under the final strict IEEE policy on the fresh OpenBLAS build, with explicit one-rank postprocessing and unchanged numerical budgets. |
| `runs/convergence-001` | Historical 62 PASS under an older warning policy; later raw-log review found severe IEEE flags. Superseded as qualification evidence. The strict OpenBLAS rerun is recorded in the external final report. |
| `runs/openblas-physical-001` | 11 PASS: nonzero analytic force/stress agree with two finite-difference step sizes under fixed budgets. |
| `runs/manual-pwtk-comparison-001` | Four raw-data comparison gates PASS after both 12-stage workflows passed; no fitted normalization. Later installed-package integration is recorded separately. |
| `runs/upstream-openblas-005` | 28 PASS, 20 BLOCKED, two parser ERROR, one parser FAIL; corrected cases are separate below, never rewritten. |
| `runs/response-final-001` | Seven PASS: damped variable-cell optimization, methane Lanczos/spectrum and iron magnon/spectrum. |
| `runs/hubbard-final-001` | Two PASS: LiCoO2 ground state and actual Hubbard response, U = 5.5123 eV matching the upstream reference. |
| `runs/qeheat-004` | Two upstream heat-current reference regressions PASS. Earlier extraction/configuration failures preserved. |
| `runs/openblas-epw-reextract-002` | Actual two-rank/two-pool EPW coupling agrees with upstream numerical metrics after correcting the EPW 6.0 completion/version adapter. |
| `runs/examples-001` + `runs/xspectra-reextract-001` | Converged seven-image NEB barrier 0.204270 eV versus upstream 0.204267 eV; XSpectra ground state and 300-point spectrum pass. |

The silicon regression is −22.83927198 Ry/cell, Fermi energy 6.4346 eV. Its integrated charge is 7.9999988 electrons/cell. The historical 50/400 Ry, 12³ study printed a 0.3712994 meV/atom difference from 80/800 Ry, 16³, but its warning-policy gap prevents that older PASS from establishing qualification. The strict OpenBLAS rerun now passes the original budget with a 0.3712994 meV/atom candidate/reference difference; see the external final report. This does not make every observable converged. Band gaps are path-sampled Kohn–Sham gaps, not experimental fundamental gaps.

The force check gives −0.02880237 Ry/Bohr analytically versus −0.02880250 and −0.02880000 from energy differences. Pressure is 21.62 kbar versus 21.63715 and 21.63261; the frozen pressure budget is 1 kbar. These verify consistency for this displaced silicon fixture.

The current core execution profile uses requested MPI ranks for PW/PH and one managed MPI rank for postprocessors. A singleton MPI diagnostic set an overflow flag even without scientific arithmetic; managed one-rank execution avoided it. A separate two-rank BANDS overflow flag remains unresolved. No IEEE flag is cleared or suppressed by these scripts. Requalification is required for a different layout.

## Remaining qualification limits

- `runs/final-upstream-006` fails methane Lanczos because its third `z1` component contains NaN; the dependent spectrum is blocked. Investigate response-vector/operator initialization and build/compiler identities in a separate instrumented variant before qualifying this solver. No NaN is ignored.
- `runs/backend-comparison-001` fails its raw acoustic-frequency comparison: maximum 0.028272 cm⁻¹ exceeds the frozen 0.01 cm⁻¹ budget. The original comparison remains FAIL. Optical/scalar agreement does not erase it.
- The existing Accelerate suite raised severe floating-point flags in displaced-atom runs and segfaulted during actual EPW coupling. The clean OpenBLAS configuration passed the corresponding contracts; this does not qualify the old suite or establish the exact cause of its failures.
- Exact benchmark pseudopotentials are unavailable for several selected USPP/PAW/metal, electron–phonon, cluster/dipole and related cases. Per-case BLOCKED reasons name the required filename and MD5. Available online replacements were not substituted to obtain a pass.
- The Davidson reference adapter requires the old example's exact H/C pseudopotentials; current files have different hashes. Its independent reference qualification stays BLOCKED. Other TDDFPT solvers passing does not qualify Davidson.
- CP reference trajectories are finite regression checks, not timestep/energy-drift convergence studies. Wannier90 integration and arbitrary production materials/options still need model-specific studies.
- Independent code-and-evidence review is pending. The comprehensive activation gate remains closed. Core activation/rollback is narrower and requires its matching complete campaign, binary/dependency hashes and preserved evidence.
- Pointer rollback restores a selected release, not changed macOS, compiler, MPI or shared libraries. Dependency/platform changes block activation until requalification.

## Repairs and review status

F01–F03/F09: finite required assertions, complete inventory, final-state parsing, exact suite selection, actual ranks, no serial retry. F04: explicit module contracts and honest blocked/untested scope. F05–F08: correct workflow ancestry, fresh artifact manifests, raw-grid comparison and convergence/gap logic. F10–F13: curl/checksum source and manager installation, clean bounded builds, installed-path resolution and complete module inventory. F14–F15: protected output paths, process-group cleanup, failure records, journal, recovery status and CI retention.

The final installed-package integration passed both 21-case core qualifications, the 12-stage PWTK workflow, four raw-data comparisons, all 14 CLI dispatches, and isolated core activation/rollback with rejection controls for tampering, wrong-suite reports, held locks and dependency drift. The external final report identifies the exact archive and records the negative controls as expected rejections.

The implementation removes the supported Formula/Brewfile/tap publishers. Historical September planning documents describe the original target; the [current work ledger](implementation-plan/WORK_LEDGER.md) records partial proof and review status. The self-hosted CI runs on manual dispatch or trusted main-branch pushes; its remote execution has not been verified locally.

## Next qualification gates

Recover and authenticate exact missing UPFs; finish the blocked numerical families. Diagnose fresh-build methane Lanczos NaN, two-rank BANDS and the raw acoustic/backend discrepancy using frozen new variants. Perform independent review of source and preserved evidence. Then assemble a comprehensive campaign with all mandatory cases and accepted review before activating a workstation release. Publish a checksum-pinned remote manager release only under separate publication authorization.
