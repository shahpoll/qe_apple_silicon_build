# Ordered implementation and finding closure

This is the original execution specification. Current work states are in [WORK_LEDGER.md](WORK_LEDGER.md); local implementation/proofs have progressed, while independent review and comprehensive qualification remain pending. Proof IDs refer to [VERIFICATION_MATRIX.md](VERIFICATION_MATRIX.md); failure paths refer to [RECOVERY_PLAYBOOK.md](RECOVERY_PLAYBOOK.md). Use the work-record template for each item. Source locations are in the original audit; recheck line numbers after edits.

Start W00–W05 in order. Then W09–W12 (toolchain/build/package), W06 (real MPI qualification), and W07/W08 (workflow repair) may proceed according to the dependencies below. W06 and live workflow checks can use either an existing identified working suite or the new staged W10 suite; a broken/missing installation must not prevent reaching its repair tasks. W13 joins these branches; W14 and W15 require their completed integration.

Compound proof IDs have explicitly named subcases frozen in W00. Each work item closes its local subclaims; later end-to-end extensions belong to the named integration owner. A finding closes only after all its mapped work items and applicable integrated proofs pass. This prevents an early safety/parser task from depending on an installer or module validator that has not yet been written. No deferred subcase is counted as already validated.

**W00 — Establish the baseline, ownership and case catalog**

Dependencies: implementation authorization. Findings: all F01–F15.

Record the working tree, audit hashes, current binaries/dependencies and source identity. Start a ledger with every work item and all selected required case IDs. Archive the original defect evidence unchanged. Identify exact upstream fixture files and benchmarks, licenses, hashes and resource costs; do not assume a directory name is a complete test definition. Authenticate and review at least one upstream SCF seed fixture, its reference and frozen tolerance rationale for W04–W06; historical project Si numbers alone do not qualify. Separate provisional project references from trusted upstream/independent ones. Define core, workstation and comprehensive profiles before execution.

Proof: verify the audit manifest against preserved files; map each finding to an owner, implementation item and proof IDs. Inventory must be read-only. If hashes differ, explain the difference before using that evidence. Close only after the baseline and expected scope are reviewed. Fallback: recover missing evidence from the preserved original revision or mark its provenance unresolved; never reconstruct fake “original” output.

**W01 — Make output and scratch handling safe first**

Dependencies: W00. Findings: F06, F14. Targets: campaign directory preparation, smoke/convergence scratch, output ownership helpers.

Replace recursive deletion of arbitrary output paths with unique owned run directories. Reject root/home/checkout/ancestors, unrelated populated paths and symlink escapes; an ownership marker alone is insufficient if it can be copied into an unrelated directory. Enforce canonical path boundaries, exclusive creation/locks and bounded deletion of only owned temporary artifacts. Keep package/source trees read-only during calculations. Preserve failure evidence and isolate concurrent jobs.

Proof: H08.scratch, H09, I09.scratch-concurrency and I10.paths, using real harmless subprocesses/temp directories. Seed sentinel files and verify byte-for-byte preservation on every rejected path, including spaces, Unicode and symlink aliases. Positive control creates and cleans only its own scratch. Process-group timeout proof belongs to W03; concurrent upgrade proof belongs to W12. Close only after concurrent scratch users cannot collide. Fallback: disable cleanup and retain uniquely named scratch with a disk-budget check until deletion safety is proven.

**W02 — Implement one result contract and durable failure journal**

Dependencies: W01. Findings: F01, F04, F14, F15. Proposed target: importable `scripts/qe_validation/` result/schema/report modules; exact package name is an implementation choice to record.

Implement the protocol's states, typed reasons, frozen expected-case inventory, metrics/assertions and append-only attempt lineage. Make CLI/report/JSON agree on the same records. Catch per-case failures without losing evidence; block only dependents. Finalize partial campaigns and recover abandoned RUNNING records after interruption. Decouple plotting from validation imports. Validate schemas and reject nonfinite JSON values.

Proof: H04–H05, H10.journal, H11, H15.state, using controlled event/record fixtures. Inject parser errors, missing cases, duplicate IDs, report-write errors, interruption and failed prerequisites. Require complete terminal records or an explicit recoverable incomplete journal, never a success exit. Positive control reconciles every case exactly once. Real timeout/checkpoint process integration belongs to W03/W14. Fallback: emit a minimal structured failure plus stderr when rich rendering fails; if durable evidence cannot be written, the campaign remains ERROR/INCOMPLETE.

**W03 — Unify process execution and exact executable selection**

Dependencies: W02. Findings: F02, F09, F14. Targets: `run_qe.sh`, smoke/campaign/convergence subprocess paths and the shared runner.

Resolve the selected binary directory once, reject conflicting/invalid explicit selectors, and carry it to every executable. Record argv rather than shell-interpolated command strings. Capture the launcher and thread policy, isolate attempts, handle process groups, timeouts and interrupts, and record actual exit/signal. Support controlled checkpoint stops separately from completed calculations. Introduce bounded recovery hooks; disable generic retry and serial substitution in required MPI cases.

Proof: H06–H07, H10.process, H13, H15.process and I02 through isolated process fixtures. Simulate an application failure followed by a superficially successful retry; ensure the first remains failed and its metrics cannot be reused. Verify children terminate on timeout and benign long silent work is not killed solely for log inactivity. Positive controls exercise direct execution and launcher argv/dispatch using harmless fixtures; real MPI/QE integration is W06. Fallback: direct execution is a separately labeled diagnostic; missing MPI prevents MPI capability closure.

**W04 — Parse the final valid calculation state**

Dependencies: W03. Findings: F03, F04, F08. Targets: energy/Fermi/band parsers and calculation-specific validators.

Implement supported-version parsing with explicit units and final-state selection. Prefer structured QE output where appropriate, with a documented independently checked text adapter for supported versions. Parse Fortran numeric notation; reject NaN/Inf, truncated data and dimension errors. Tie output to one attempt and one final stage. Distinguish SCF convergence, eigenproblem completion, ionic/cell optimization, phonon perturbations, NEB and finite-step dynamics. Define versioned warning rules, preserving unknown warnings for review rather than suppressing them.

Proof: H01–H02, H04, H08.parser, H14/H15.parser; S01.seed-parser and S08.parser archived positive fixtures. A fixed-occupation insulator without printed EF must pass its proper contract. Mixed attempts, first-versus-final value mismatch, false completion and nonconverged final state must fail. Implement the shared contract plus PW adapters here; PH/advanced adapters and their real integrations are W13, and remain untested until then. Fallback: keep an unsupported output version BLOCKED/ERROR and retain raw output; never substitute zero/default values or assume the first match is final.

**W05 — Enforce numerical agreement and expected coverage**

Dependencies: W04. Findings: F01, F03, F07, F15. Targets: common comparison engine, smoke/campaign verdicts, profile arguments.

Make reference, rank and repeat comparisons explicit required cases. Apply finite-value checks before comparisons, then metric-specific units/shape/grid contracts and documented limits. Include max deviation/span, not sigma alone. Validate positive ranks, distinct configurations, repeat cardinality and full expected coverage. Select limits before candidate qualification and refuse missing reference/tolerance metadata. Convert audit characterization into genuine negative regression assertions.

Proof: H01, H03–H05, H11–H12 and S01.seed-comparison, using analytic comparator fixtures and the reviewed W00 archived seed. Reproduce injected +5 Ry reference and 1 Ry inter-run errors, common-mode errors, missing metrics, empty sweeps and boundary cases; each must yield the intended failure and nonzero aggregate exit. A known finite matching fixture passes. Live QE integration belongs to W06, not W05's engine closure. Fallback: unresolved tolerances/reference identity block numerical qualification while execution-only evidence remains available. Broader trusted fixture governance closes at W13.

**W06 — Prove real MPI and controlled repeatability**

Dependencies: W05 plus an identified usable existing suite or staged W10 suite. Findings: F01, F02, F09. Targets: launcher preflight, rank extraction, suite identity and thread policy. W09–W10 remain eligible if this item is blocked.

Run the small Si fixture in fresh scratch with real 1/2/4 MPI ranks and at least three independent repeats at a selected rank count. Record requested/observed process counts and linked MPI compatibility. Compare each result against its reference and peers. Test the intended pool/band decomposition only where valid for the fixture. Store an explicit serial-only capability if that's all the environment supports; do not complete MPI qualification on fallback.

Proof: R01–R03 plus H06–H07. Reviewer checks raw QE banners, convergence and numerical assertions. Change a controlled rank record and verify detection. Fallback: diagnose launcher restrictions, use a known permitted local host environment, or report MPI BLOCKED; after a verified binding workaround rerun the required rank cases. Closure proves this fixture/configuration, not all materials.

**W07 — Repair workflow ancestry, output collection and comparison**

Dependencies: W05; live proofs additionally need an identified usable suite or W10. Findings: F05, F06, F07. Targets: PWTK/manual workflow scripts, common plotting/comparison helpers and beginner docs. Real rank qualification remains a separate W06 gate.

Make canonical input settings generate both manual and PWTK workflows. Preserve independent bands/NSCF datasets or order postprocessing before a saved dataset is overwritten. Explicitly set broadening, band count and all output paths. Bind each stage to parent hashes/mesh metadata and collect only artifacts it produced. Route plots to a run manifest. Validate comparable coordinates/units/normalization before numerical overlays; remove unconditional agreement prose. Fail dependent stages on prerequisite failure.

Proof: H08, S08–S10 and R05. Reproduce the 8-band/201-point PWTK misuse and reject it; a corrected fresh NSCF parent is accepted. Current historical mismatched spectra must fail comparison. Seed old valid data and fail a new calculation: it must not yield a fresh successful plot. Fallback: run the canonical manual path while PWTK remains unverified; do not certify PWTK by borrowing manual outputs.

**W08 — Repair convergence and gap analysis**

Dependencies: W07. Findings: F08, F15. Targets: `run_convergence.py`, shared band analysis and generated convergence documentation.

Use the selected suite, correct the direct-gap reduction, serialize all claimed metrics and report actual meshes. Separate a path-sampled gap from a global-gap claim. Define per-observable accuracy targets and convergence ladders for cutoffs, charge-density basis, meshes, smearing, empty states and relevant response parameters. Require stronger validation points and joint checks at the chosen settings; the last sampled point is not automatically converged. Preserve negative convergence outcomes.

Proof: S18 and H01–H04. Synthetic band fixtures have an analytically known direct gap; the archived formula replay must no longer return infinity. A deliberately underconverged grid produces a failed accuracy target; a sufficiently converged fixture passes. Fallback: extend one declared scan within budget; if accuracy cannot be established, report the measured uncertainty/insufficient convergence and do not label settings production-ready.

**W09 — Specify and verify the toolchain and dependency closure**

Dependencies: W05; read-only preflight/design may begin after W00. Findings: F09, F10, F11, F15. Targets: preflight, build manifests, linkage checker and dependency provisioning design. This work does not require successful MPI beforehand.

Inventory native architecture, CLT/SDK, compiler/MPI wrapper identity, integer/complex ABI, FFT/BLAS/LAPACK libraries, Python and feature dependencies. Pin supported versions after actual compatibility verification; record transitive dependencies and resolved realpaths. Replace the `otool` text heuristic with resolution checks plus controlled loader/numerical probes. Design dependency isolation/version retention before upgrading anything. Record whether the prior release can still run using its preserved dependency set.

Proof: I01–I03 and R04 prerequisites using controlled compiler/library/loader probes; no pre-existing QE installation is required. Missing dylib, wrong architecture, mixed MPI runtime/launcher and invalid explicit binary selections must be diagnosed correctly. Actual QE loading/numerical integration belongs to W10/W06; evidence from an existing suite is supplementary here. System shared-cache libraries need correct platform handling rather than naive file-existence checks. Fallback: choose one coherent verified dependency profile or keep the environment BLOCKED; never mix arbitrary library directories until linking succeeds.

**W10 — Build complete staged suites from verified sources**

Dependencies: W09. Findings: F10, F13. Targets: fetch/bootstrap/manager, CMake presets and shared module manifest.

Create one manifest mapping selected capabilities to sources, dependencies, actual build targets, executable outputs and required tests. Verify archives/UPFs/submodules using pinned hashes, HTTP errors, format checks and atomic cache/extraction. Use clean out-of-source or otherwise isolated build directories, bounded jobs and full configure/build logs. Fix preset path expansion against the real QE source. Build into a unique versioned final-location directory that remains inactive until validated, avoiding relocation surprises; never overlay an existing suite. Track exactly which modules were built.

Proof: I05–I07 and I12, then the applicable small QE checks from the staged suite. Fresh install contains every selected executable; seeded old modules cannot leak in. Failed download/build/validation leaves the old release untouched. Fallback: same sources with reduced jobs, then a clean conservative supported compiler/backend candidate; each candidate needs a new manifest and full affected proof. Missing selected modules block that profile.

**W11 — Make the installed CLI self-contained and usable**

Dependencies: W10. Findings: F12 and F09. Targets: CLI entry point, Formula, generated tap templates and Python environment packaging.

Resolve installed symlinks to the package or use an explicit libexec wrapper. Provide pinned compatible Python dependencies in an isolated environment; keep rendering dependencies optional to scientific parsing. Store runs/cache in user-writable locations. Ensure all entry points call the same suite selection and result engine. Maintain one tested source for Formula/template behavior. Provide actionable preflight/unsupported diagnostics and document the supported source/package invocation.

Proof: I04, I10–I11. From an unrelated directory and clean environment, test every subcommand's dispatch and a small real check through the installed public path. Include spaces/Unicode, noninteractive shells, missing global packages and read-only package trees. Top-level help alone is insufficient. Fallback: an explicit supported source-tree CLI can be an interim route; packaged-install capability remains open until its installed-path proofs pass.

**W12 — Add safe activation, rollback and CI evidence retention**

Dependencies: W11. Findings: F10, F14, F15. Targets: manager activation/upgrade, locks, CI artifact upload and release state.

Implement validation of an inactive suite in its final location followed by an atomic pointer/manifest switch with concurrency protection. Test this mechanism using isolated test pointers and a declared test profile in W12; do not activate the user's comprehensive release until W15 qualification/review (or a separately explicit selection of a narrower verified profile). Keep the last verified release and its dependency closure while referenced by jobs. Test rollback by actual loading and computation, not pointer existence. Do not promise rollback of macOS/CLT/global Homebrew changes. Require confirmation of dependency preservation before any upgrade that would otherwise break the previous release. CI must isolate installations and always publish inputs/logs/results/failure packets, including incomplete runs.

Proof: I08–I09 and H10. Inject validation failure, activation interruption, concurrent upgrade, stale lock and dependency movement. First installation failure must leave no falsely active release; failed upgrades keep the prior usable release. Fallback: leave the candidate quarantined, retain the previous verified configuration, and record recovery limitations if external system updates already invalidated it.

**W13 — Establish broad module fixtures and independent numerical evidence**

Dependencies: W06, W08 and W12. Findings: F04, F15; final broad reference closure for F01/F03/F07/F08.

Freeze the comprehensive profile's concrete upstream fixture files and independent reference provenance. Cover the scientific rows in the matrix: separate pseudopotential/spin/functional modes and actual advanced-module observables. Use official benchmarks plus a separately validated backend/platform or additional physical/analytic checks; record what is and is not independent. Compare observables, not timing or raw floating-point text. Add version-specific parser fixtures and meaningful bad-output cases for each family. Unknown feature combinations are explicitly untested.

Proof: all selected S01–S17 and S20, R01–R07 and relevant H cases. Require actual HP response and actual EPW coupling for those claims, converged NEB for barriers, CP-specific dynamics, nonbulk fixtures and independent force/stress sanity checks. A trusted reviewer checks reference provenance and extracts selected quantities independently. Fallback: diagnose a failing family and keep that capability blocked; passing core checks do not close the comprehensive target. Do not generate new “expected” values from the failing candidate.

**W14 — Define production readiness and operational diagnostics**

Dependencies: W13. Findings: F08, F14, F15 and generalization beyond Si.

Implement a preflight/admission path that reports whether a requested workflow is supported, tested, has compatible inputs/UPFs and sufficient resources, and has a suitable validation contract. For user science, require a declared target observable/error budget and preserve all convergence changes. Add run status that distinguishes active processes/progress evidence from final success. Document bounded recovery for common failures, restart compatibility, negative scientific results, uncertain model adequacy and larger-machine escalation.

Proof: S18–S19, H10/H14/H15 and I13. Exercise representative production-sized resource behavior under declared budgets; simulate unavailable capability, unsupported combination and insufficient resources. A small equivalent test is diagnostic, not success for a larger failed job. Fallback: return precise blocked/unsupported/convergence status and a new proposed experiment; never silently shrink the scientific task.

**W15 — Independent release audit and final handoff**

Dependencies: W14, all applicable earlier findings closed. Findings: all.

Freeze source/diff, toolchain, dependencies, fixtures, tolerances and profile. Run the release matrix on a clean supported machine/environment using the installed public CLI and a fresh prefix; verify upgrade/rollback against a prior release. Perform a separate reviewer audit of complete case counts, negative controls, actual ranks, artifact ancestry and numerical metrics. Generate capability and limitation tables directly from reviewed evidence. Preserve a reproduction manifest and installation/recovery guide.

Proof: every mandatory case is PASS under the protocol; expected-failure harness tests correctly reject their targets; there are no unresolved required BLOCKED/ERROR/NOT_RUN cases, provisional references or null limits. Compare the assembled integrated revision, not isolated task branches. Provide the evidence index and completed checkpoints to the user. If any gate fails, reopen the owning item and retain the prior release; publication is not part of this planning authorization.

**Finding-to-work traceability**

| Finding | Implementing work | Required closure emphasis |
|---|---|---|
| F01 comparisons/coverage | W02, W05, W06, W13 | H03–H05/H12, R01–R03; independent baseline |
| F02 MPI/fallback/retry | W03, W06 | H06–H07; real actual-rank proof |
| F03 smoke acceptance | W04–W05 | H01–H02; valid SCF through public smoke |
| F04 module claims | W04, W13 | S11–S17; per-module numerical evidence |
| F05 PWTK ancestry | W07 | S09 and R05; correct uniform NSCF parent |
| F06 stale plotting | W01, W07 | H08; fresh-data positive/negative pair |
| F07 false comparison | W05, W07, W13 | H12, S09, R05; disagreement must fail |
| F08 convergence/gap | W04, W08, W14 | S18; finite known gap and unmet-target failure |
| F09 wrong suite | W03, W06, W09 | I02, H13; consistent paths/hash/ranks |
| F10 build/install | W09–W10, W12 | I05–I09; no mixed suite and usable rollback |
| F11 linkage | W09 | I03; broken dylib rejection and actual loader proof |
| F12 package/CLI | W11 | I04/I10/I11; clean installed-path invocation |
| F13 CMake | W10 | I12/R04; actual libraries and numerical backend proof |
| F14 lifecycle/evidence | W01–W03, W12, W14 | H09–H11/H15, I08–I09; isolation and durable failure |
| F15 references/scope | W00, W02, W08, W13–W15 | reviewed fixture lineage and complete capability matrix |
