# Quantum ESPRESSO Apple Silicon audit and remediation plan

Audit date: 2026-09-30. Source baseline: `6d5171e` in `qe_macos15_build` (the repository now calls itself `qe_apple_silicon_build`). Source references below use that baseline and repository-relative paths. Production code has not been changed; this directory contains the audit, reproduction scripts, and evidence.

**Verdict: the installed QE binary passes the silicon SCF checks performed here, but the project's current validation system cannot establish its advertised breadth of numerical correctness.** Several acceptance defects permit false success. The user's rank-sweep/repeatability concern is confirmed, and there are additional workflow defects that can change scientific results.

**What was actually verified**

An isolated calculation with `/Users/pollob/opt/qe-7.5/bin/pw.x` passed on macOS 26.3/arm64, directly and through real MPI with 1, 2, and 4 processes, followed by another independent 2-process run. Every run converged, exited zero, printed `JOB DONE.`, and reported the expected actual process count. All five produced **−22.83927198 Ry** and **6.4346 eV**, equal at the printed precision. Fresh scratch directories were used for every run; no serial fallback was allowed.

Evidence: [host results](live_host/results.json), [independent numerical review](live_host/numerical_review.json), and the associated `.log`/`.in` files in `live_host/`. The review checks finite values, the existing smoke reference tolerances, rank counts, convergence, and maximum energy/Fermi differences. Binary, input, pseudopotential, and reviewed log hashes are recorded. Zero printed difference is not evidence of bitwise identity below output precision.

The first sandbox MPI attempt failed with socket permission errors ([initial results](live_results.json), [log](live_mpi2.log)); host execution subsequently succeeded. An optional further host rerun could not obtain automatic approval because the approval service hit a usage limit. Numerical verification was completed against the already saved host logs. The final [live check script](live_checks.py) includes these numerical gates for future reruns; the independent JSON review documents the gates applied to the completed runs.

The audit inspected the custom installer, launcher, validator, smoke tester, CI, Homebrew packaging, CMake preset, silicon manual/PWTK workflows, analysis/comparison/convergence scripts, and saved evidence. Selected local QE 7.5 build definitions and official QE documentation were checked. It did not rebuild all QE modules, run every upstream regression, audit all upstream Fortran, or establish physical accuracy for arbitrary materials or observables.

**Evidence types and priorities**

“Reproduced” below means a controlled probe demonstrated the defect in the actual project code, or a formula replay demonstrated the stated numerical error. Synthetic output is clearly separated from real QE output. P1 findings can cause false validation, wrong scientific data, or loss of run data. P2 findings concern installation reliability, coverage, or reproducibility. Each case includes the repair and the conditions required to close it.

**F01 — P1: numerical comparisons do not control success**

Evidence: `scripts/validate_build.py:1319–1344,1374–1399` accepts rank/repeat cases based on process completion and parsing. Reference deltas at `1487–1494` and spans/statistics at `1521–1555` are only recorded. Metric exceptions at `1495–1499` write an `ERROR` row without adding a failed case. Final exit at `1586` uses only the case matrix. Empty rank lists and zero repeats are accepted (`90–111,1297,1356`).

Reproduced using the production campaign with injected subprocess output: **42 PASS, 0 FAIL, exit 0** despite **1 Ry** differences between ranks and repeats, **+5 Ry** reference energy error, and **+92.5654 eV** Fermi error. A required metric parser exception also returned success. Empty ranks plus zero repeats returned **38 PASS, 0 FAIL**. See [validator probe results](validator_probe_results.json).

Plan: create explicit required cases for reference agreement, rank agreement, repeatability, and expected coverage. Reject missing and nonfinite values. Use named, unit-bearing absolute/relative tolerances and compare every result with both its reference and its peers. Require distinct valid rank configurations and at least two repetitions; a reduced campaign must report omitted coverage. Never derive a trusted baseline from the candidate build being tested.

Acceptance: values just inside/outside each tolerance change both the case status and process exit. Identically wrong energies at all ranks fail reference agreement. Missing metrics, NaN/Inf, empty/duplicate-only rank lists, invalid ranks, and insufficient repeats cannot produce full validation success.

**F02 — P1: MPI failure and retry can be hidden behind PASS**

Evidence: `validate_build.py:608–618,983–993` substitutes direct execution after MPI failure and returns only status/duration. Requested ranks are then reported as if tested. This happened in saved evidence: `validation_reports/ci_final_check` reports 43 PASS/0 FAIL, but `logs/scf_rank_2.log:10,24` and `scf_rank_4.log:7,21` show serial retry and **one** actual process. Their zero rank span is not evidence of 2/4-process agreement.

Additionally, `scripts/run_qe.sh:65–68` retries any failing application under a message blaming hwloc. The build probe demonstrates application exit 17 followed by an accepted retry. `smoke_test.py:91–101` falls back after any `CalledProcessError`, combines attempts into one log, and omits the controlled environment on the fallback. `validate_build.py:623–634` parses the first matching values, so combined attempts can mix numerical and completion evidence.

Plan: return a structured attempt record containing exact executable, launcher, requested/observed ranks, environment, exit code, and attempt-specific log. Required MPI checks must fail or report blocked if MPI cannot run. Permit an explicitly requested serial diagnostic as separate coverage. Only retry a recognized pre-execution binding failure, preserve the initial failure, and keep each attempt's scratch and output separate.

Acceptance: requested 4 ranks with observed 1 fails MPI validation. A numerical application failure is not relabeled as a binding problem. A failed attempt's energy cannot satisfy a later attempt's checks. Revalidate archived rank claims with real MPI; the small host checks in this audit establish only the tested silicon SCF case.

**F03 — P1: smoke success does not require valid, completed numerical work**

Evidence: `scripts/smoke_test.py:103–134` checks parsed floats against tolerances but never requires completion/convergence or finite values. In Python, `abs(nan - reference) > tolerance` is false. The [smoke probes](smoke_probe_results.json) demonstrate exit zero for NaN energy/Fermi values, reference numbers without completion/convergence, and numbers left by a failed MPI attempt followed by a numerically empty successful fallback.

Plan: use the same calculation-specific result validator as the full campaign. Require a completed converged SCF, a clean current attempt, finite final quantities, and agreement with an identified fixture. Store the log instead of deleting the evidence. Preserve separate SCF and NSCF rules; a blanket SCF-marker requirement would incorrectly reject legitimate non-SCF calculations.

Acceptance: all three reproduced cases fail; truncated output, nonfinite values, error markers and nonconvergence fail. A genuine converged SCF with values on the tolerance boundary behaves according to the documented rule.

**F04 — P1/P2: broad module PASS overstates computational and numerical coverage**

Evidence: core steps at `validate_build.py:1252,1270` require only exit zero and `JOB DONE.`. Phonon frequencies, force constants, charge-density integrals, DOS normalization and PDOS structure have no numerical gates. NEB at `820–824` accepts exit 0 or 1 plus completion, without requiring a barrier or convergence. The saved `ci_final_check/logs/neb_mini.log:119,128,138–139` shows residual path error **0.191942 eV/Å**, a step-limit termination and floating-point flags/`STOP 1`, yet the case passed. This establishes an unconverged mini-run; the flags alone do not diagnose its cause.

EPW at `921–923` accepts a section heading; injected heading-only output passed. Its generated input disables electron-phonon coupling (`521–522`). HP intentionally requests only perturbation counting (`325,801–805`). Module checks at `1426–1429` deliberately accept a launch banner; that is legitimate launch coverage but not successful calculation coverage. Plot generation is also counted beside scientific cases.

Plan: report launch, execution, convergence, numerical agreement, and plotting as distinct coverage. Label bounded demonstrations accordingly. Add module-specific checks: SCF final convergence/residuals; phonon mode count, finite frequencies and reference tolerances; q2r/matdyn consistency with an explicit ASR convention; density/electron-count checks; DOS/PDOS grid and spectral checks; NEB converged path plus barrier/profile; EPW numerical interpolation outputs; actual HP response/U only if claiming that support. Select official reference cases for each supported mode.

Acceptance: a banner/heading alone never satisfies numerical coverage. Missing, empty or corrupted artifacts fail. The archived NEB result cannot receive a converged-barrier verdict. HP counting and EPW interpolation with coupling disabled remain accurately labeled limited tests unless stronger workflows are added.

**F05 — P1: PWTK DOS/PDOS consumes the wrong saved calculation**

Evidence: `cases/si/pwtk/scripts/si_workflow.pwtk:5–7` shares `silicon`/`./tmp`; `37–51` computes a uniform NSCF mesh with 36 bands, `54–75` overwrites it with band-path data, and `77–96` then computes DOS/PDOS. Archived PWTK `logs/si_projwfc.txt:54–55` confirms **8 bands, 201 path points**, whereas manual `logs/si_projwfc.txt:51–52` has **36 bands, 72 irreducible uniform-grid points**. DOS requires suitable uniform Brillouin-zone sampling, as described in [QE's electronic-structure workflow](https://www.quantum-espresso.org/Doc/pw_user_guide/node10.html).

The source DOS block also omits broadening settings that are explicit in the manual input. PWTK source, edited generated input and archived logs therefore do not consistently describe the same workflow. Gaussian type and width must be explicit; output spacing `DeltaE` is not broadening `degauss`, and their units differ. See the [official DOS input reference](https://www.quantum-espresso.org/Doc/INPUT_DOS.html).

Plan: order SCF → bands → bands postprocessing → uniform NSCF → DOS/PDOS, or branch into independent save directories with explicit SCF ancestry. Make all material settings canonical, including mesh, band count, smearing and broadening. Check each postprocessor's parent dataset before launch.

Acceptance: a clean PWTK run consumes the declared uniform NSCF data with 36 bands and the agreed broadening. Placing a band-path calculation immediately before DOS triggers a failed prerequisite check. Only then regenerate manual/PWTK comparisons.

**F06 — P1: documented reruns can plot old data**

Evidence: `docs/Workflow_Basics.md:45–58` runs in `cases/si/manual` and immediately plots. `manual/data/Si.bands_post.in:2` writes a bare `silicon.bands.dat` into that working directory, while `cases/common/scripts/plot_si_bands.py:26–31` and `analyze_si_bandgap.py:18–22` read `base/data/`. Other postprocessors follow the same pattern. There is no collection step. Existing checked-in artifacts can therefore be plotted after a fresh or failed calculation. The PWTK workflow has a similar output-location split. The documented `| tee` sequence neither preserves producer failure through pipefail nor stops dependent commands.

Plan: supply a fail-fast workflow runner that writes into a fresh run directory, specifies all output paths, and collects only artifacts from that run. Analysis must consume its manifest. Keep example/reference data separate from current results; block dependent stages if a prerequisite fails.

Acceptance: changing the input changes the identified plotted dataset. Failed SCF prevents dependent processing. Seed old valid files, fail the new run, and verify that no fresh-success plot/report is emitted from those old files.

**F07 — P1: comparison output asserts agreement without checking it**

Evidence: `cases/common/scripts/compare_si_runs.py:147–165` records differences but applies no tolerance; it always asserts constant scaling and overlapping normalized shapes. It also lacks coordinate-grid checks before subtraction. The bundled comparison reports **5.626 states/eV** DOS disagreement and PDOS differences above **1 states/eV**. Recalculation finds a median scale near **1.196** but widely varying ratios; applying that scale leaves a maximum residual of **6.772 states/eV**. The reassurance is unsupported. The README's machine-precision agreement claim is inconsistent with the saved comparison.

Plan: validate identical physics, units, grid coordinates, dimensions, band coverage and energy alignment before comparing. Require finite values and toleranced pointwise/integrated residuals. Permit only declared, justified normalization conversions. Return nonzero for disagreement and generate prose from the verdict.

Acceptance: the current archived pair fails with specific diagnostics. Grid mismatch, nonfinite values, shape changes and an unauthorized scaling all fail. A known identical fixture passes. Claims and plots reflect the same tested data.

**F08 — P2: convergence tooling is not a current-build accuracy gate and contains a direct-gap bug**

Evidence: `cases/si/convergence/run_convergence.py:19–20` hardcodes QE 7.4.1. Lines `58–76` do not verify completed, converged, finite results; `202–247` report differences from the final scan point without an acceptance target. The direct gap at `160–167` subtracts masked conduction/valence arrays elementwise, yielding infinity. Formula replay on saved `cutoff_30` gives **inf** instead of a per-k reduced **2.56 eV**; this field is omitted from current serialized tables, so the error is latent rather than an explanation of the published indirect gaps. The README says the cutoff scan uses 8³ k points, while line `258` and archived input use 6³.

Plan: select the campaign's executable explicitly, share validated parsing, fix the reduction over band indices before comparing at each k point, and serialize all claimed metrics. Introduce observable-specific error budgets and stronger references. Check wavefunction and charge-density cutoffs, k mesh, smearing, empty-band coverage and spectral settings as appropriate. A final scan point is a comparison reference, not automatically a converged limit. Generate documentation from the actual settings.

Acceptance: known synthetic bands produce the correct direct gap; unfinished/nonfinite calculations fail. Deliberately insufficient cutoffs/meshes yield “not converged to target.” The selected production settings meet declared observable tolerances against stronger settings. The actual QE identity and cutoff-scan mesh agree with the report.

**F09 — P1/P2: explicit binary selection is not enforced consistently**

Evidence: `scripts/run_qe.sh:18–38` silently searches other installations if an explicitly supplied `QE_BIN_PATH` lacks a requested executable. `smoke_test.py:25–50` can similarly fall through after invalid explicit paths. A surviving `QE_PW_BIN` takes precedence over the CI wrapper's `QE_BIN_PATH` (`scripts/ci_migration_check.sh:68–73`), allowing smoke and full validation to target different builds. A probe reproduces explicit-path fallback. Main validator `--qe-bin` handling is stricter; the problem is inconsistency across entry points.

Plan: explicit configuration must either resolve exactly or fail. Resolve one suite manifest before running, enforce it across smoke/wrapper/campaign/convergence, and record real paths and hashes. Resolve the MPI launcher separately and verify its compatibility with the linked MPI runtime. Control and record OpenMP/BLAS thread variables in every execution path.

Acceptance: a deliberately invalid explicit path fails even when another valid installation is available. A partial suite cannot borrow modules from another version. Conflicting environment variables produce a clear error or documented single selection; all child commands use that same build and thread policy.

**F10 — P2: build targets and validator requirements differ; reused installs can mix provenance**

Evidence: `scripts/setup/bootstrap.sh:116–118` builds selected PW/PH/NEB/HP/EPW/PP/Wannier targets, while `validate_build.py:45–57,1411–1418` requires CP, XSpectra, all_currents and turbo executables too. Local QE 7.5 Makefile defines those as separate targets. Copying `bin/*` into an existing prefix at `bootstrap.sh:119–122` can retain older executables not rebuilt in the current operation. Installation occurs before validation (`qe_manager.sh:166–175`). There is no recorded source/dependency/binary manifest; source/pseudopotential downloads are not checksum-verified, and the pseudopotential download does not fail on HTTP error (`bootstrap.sh:93–95`; `fetch_qe.sh:17–21`). `make -j` is unbounded.

Plan: share a supported-module manifest between builder and validator. Either build all required modules or declare optional ones absent without claiming coverage. Build and validate in a fresh staging prefix, then activate the complete validated installation atomically and retain the prior version. Pin source and pseudopotential hashes, validate downloads, record compiler/library versions and flags, and bound parallel build jobs. Treat dependency updates as reasons to retest/rebuild.

Acceptance: an empty-prefix install builds every advertised required executable. A seeded old binary never survives as an untracked part of a new suite. Failed validation leaves the previous installation active. Invalid downloads fail before replacing valid files. Record a clean-install test; this audit did not perform a complete rebuild.

**F11 — P2: the linkage checker can PASS a missing library**

Evidence: `validate_build.py:1008–1027` runs `otool -L` and looks for the text “not found.” That command lists install names; it does not establish successful loader resolution. A temporary compiled Mach-O linked to a subsequently removed temporary dylib still produced `No missing dynamic libraries detected.` The current real `pw.x` loaded successfully in this audit; the finding concerns the check's reliability.

Plan: check architecture, resolve absolute/install-relative/RPATH dependencies with appropriate handling of system libraries, and add a controlled loader execution. Record the BLAS/LAPACK/FFT/MPI backend actually used. The [QE library guide](https://www.quantum-espresso.org/Doc/user_guide/node12.html) recommends inspecting the resolved build library settings.

Acceptance: missing dylibs, incompatible architecture and an incompatible runtime fail preflight. Correct system-library references remain valid. Supplement loader success with numerical reference tests; successful loading alone cannot establish ABI/numerical correctness.

**F12 — P2: installed Homebrew CLI and Python dependencies are insufficiently tested**

Evidence: `Formula/qe-apple-silicon-build.rb:17` installs a public symlink, but `bin/qe-apple-silicon-build:5–9` derives its root from the invocation path. In an isolated Formula-style layout, `help` succeeds but `install --help` fails looking for `prefix/scripts/qe_manager.sh`. The Formula test at `39–40` checks only the self-contained help. The validator imports Matplotlib/NumPy at `validate_build.py:24–26`, but neither the Formula nor Brewfile provisions a Python environment containing them. A clean virtual environment fails even `validate_build.py --help` with missing Matplotlib.

Plan: resolve symlinks to the real package root or install a wrapper targeting `libexec` explicitly. Supply an isolated supported Python environment with declared dependencies and make entry points use it. Use writable user cache/work/output locations for runtime data. Keep Formula publication templates consistent with the canonical packaging.

Acceptance: install/update/check/smoke dispatch works through the installed public path from another working directory. A clean machine can import validation dependencies without relying on the user's global Python packages. Package tests exercise delegated commands, not just top-level help.

**F13 — P2: the OpenBLAS CMake preset contains unevaluated shell syntax**

Evidence: `CMakePresets.json:21–22` puts `$(brew --prefix openblas)` in cache values. A minimal CMake probe confirms it remains a literal string. The repository root also has no QE `CMakeLists.txt`; using the preset requires an explicit source-tree arrangement. This alternative path has not been established as a working independent numerical reference build.

Plan: resolve Homebrew paths in an orchestration step, or use a documented CMake-supported environment/toolchain mechanism. Run configuration against the actual QE source and record resolved BLAS/LAPACK paths and compiler settings. Maintain one documented invocation that works from a clean checkout.

Acceptance: configuration contains existing library paths, no shell-substitution literals, and identifies the intended backend. Build the chosen regression executables and compare pinned fixtures across Accelerate and OpenBLAS within justified tolerances.

**F14 — P1/P2: scratch, timeouts and evidence handling are not safe or complete**

Evidence: `validate_build.py:143–145,1212` recursively deletes any existing `--out-dir` with no ownership/boundary check. A mistaken `--out-dir .` can delete the checkout. `smoke_test.py:74,120–121` uses a shared output filename and deletes shared `inputs/tmp`; concurrent runs can collide and erase another run's data. Smoke and convergence subprocesses have no timeout. The campaign has per-command timeouts (`548–571`), but exceptions reach the outer fatal handler (`1590–1596`) without a finalized case matrix/report, and it does not explicitly manage the entire MPI process group. This audit did not assert that orphan processes occurred; lifecycle handling needs a direct test.

CI artifact upload at `.github/workflows/migration-check.yml:49–56` is conditional on preceding success by default and omits raw logs/inputs. Thus failures can lose the very evidence needed to diagnose them. A fresh complete campaign does clear its own scratch; stale-output risks above concern the unsafe shared paths, retries, examples and dependency handling rather than a claim that every campaign reuses old scratch.

Plan: use uniquely named owned run/scratch directories; refuse checkout/home/root/ancestor and unrelated populated output paths. Make overwrite explicit and bounded. Add wall-clock limits, process-group termination and interrupt cleanup. Finalize structured failure/timeout/blocked records in a `finally` path, preserve logs and input manifests, and upload them with `if: always()` in CI. Prevent overlapping CI installs from mutating one prefix concurrently.

Acceptance: protected output paths remain untouched; concurrent runs are isolated. A deliberately hung MPI worker is terminated with its descendants and gets a timeout result. Interrupted/failed runs leave a readable report and raw evidence. CI retains the logs when validation fails.

**F15 — P2: reference provenance and scientific coverage remain limited**

Evidence: constants in `validate_build.py:36–42` and `smoke_test.py:17–22` do not carry fixture hashes, baseline-generation provenance or a supported-build envelope. Some bundled artifacts are inconsistent: manual `logs/si_bands_post.txt:97` gives Γ valence 6.21261 eV, whereas `data/silicon.bands.dat.gnu:203` gives 6.2198 eV. PWTK root and consolidated logs also differ. Agreement with those files cannot by itself establish an independent numerical reference. The existing convergence tables show finite errors whose acceptability depends on the intended observable and accuracy.

Plan: retain historical artifacts with explicit provenance limitations; regenerate trusted fixtures only from corrected workflows. Store QE source revision, executable hash, compiler/flags, OS/architecture, resolved libraries, launcher, thread configuration, input/UPF hashes, grid settings, units, expected values and tolerance rationale. Validate against upstream reference suites and an independently built supported backend/platform. Start with PW energies/forces/stress, PH and representative pseudopotential/spin modes, then add supported modules. [QE's test-suite guide](https://www.quantum-espresso.org/Doc/user_guide/node15.html) describes automated reference testing and its coverage limits.

Acceptance: every claimed metric traces to matching raw outputs and immutable inputs. Modifying a pseudopotential/input/binary invalidates fixture identity. A common-mode numerical error cannot be blessed by updating expected values from that same candidate run. Report build regression, numerical convergence and model adequacy separately. A high-symmetry-path gap must be labeled path-sampled unless a suitable Brillouin-zone search supports a fundamental-gap claim.

**Implementation order and release criteria**

| Work package | Cases | Concrete deliverable | Completion gate |
|---|---|---|---|
| 1. Make validation verdicts trustworthy | F01–F04, F09 | Shared result schema/parser, finite/convergence checks, explicit tolerances, actual-rank verification, attempt isolation, supported coverage profiles | All synthetic false-success cases become nonzero failures or explicit blocked/incomplete results; valid fixtures pass |
| 2. Protect run state and evidence | F06, F14 | Isolated fail-fast runner, owned output directories, timeout/process cleanup, durable reports and CI uploads | Stale files, concurrent jobs, failures and timeouts cannot produce false fresh success or remove unrelated data |
| 3. Correct scientific workflows | F05, F07, F08 | Fixed PWTK dependencies/broadening, strict comparison, corrected gap/convergence analysis | Fresh manual/PWTK datasets match in configuration and meet declared numerical tolerances; production settings meet the chosen accuracy budget |
| 4. Make clean installation reproducible | F09–F13 | Shared module manifest, validated staging install, resolved toolchain, working packaged CLI/dependencies | Fresh-prefix installation and package invocation pass; upgrades cannot retain untracked old modules; missing dependencies are detected |
| 5. Establish release evidence | F04, F15 | Pinned trusted reference fixtures, upstream regression selection, independent-backend comparison, honest coverage report | Real rank/repeat tests and all required numerical cases pass on each advertised configuration; no missing/blocked required coverage is counted as release success |

Implement packages 1 and 2 first. Scientific workflow repair and packaging repair can then proceed independently, with fixture regeneration last so defective workflows do not become the new oracle. Do not silently loosen tolerances to accommodate failing candidates.

For the exact silicon SCF fixture, an initial rank/repeat proposal is a maximum span of **1e−7 Ry** in energy and **1e−4 eV** in the printed Fermi value, subject to validation over supported builds and output precision. The live checks meet these proposed limits. Existing smoke reference limits are **1e−3 Ry** and **5e−3 eV**; they are regression thresholds, not a promise of that accuracy for forces, gaps or other physical predictions. Choose each new metric's tolerance from independent reference evidence and the observable's accuracy requirement. Small backend-dependent differences can be legitimate, as the [QE troubleshooting guide](https://www.quantum-espresso.org/Doc/pw_user_guide/node21.html) explains.

**Reproducing the audit**

Run from the project root:

```sh
python3 docs/audit/2026-09-30/smoke_probes.py
python3 docs/audit/2026-09-30/validator_probes.py
python3 docs/audit/2026-09-30/build_probes.py
python3 docs/audit/2026-09-30/science_probes.py
```

These characterize existing defects: a `reproduced: true` flag or successful probe execution means the defect was observed, not that QE was validated. Smoke/build probes use temporary files and injected processes; the validator probe substitutes process execution while retaining production decisions; science probes read historical artifacts and replay the documented formula. Validator probes require NumPy/Matplotlib; build probes use locally available CMake/Clang/otool and skip unavailable optional tools.

To repeat the bounded real checks, choose a **new** output directory and an explicit binary directory:

```sh
python3 docs/audit/2026-09-30/live_checks.py \
  --qe-bin "$HOME/opt/qe-7.5/bin" \
  --output /tmp/qe-audit-new-run
```

This requires an environment that permits local MPI sockets. It does not use serial fallback. It is intentionally a silicon SCF audit, not a replacement for the full release plan.
