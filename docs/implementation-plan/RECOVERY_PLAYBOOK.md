# Failure diagnosis and bounded recovery

This is an ordered decision procedure for the future implementation. A recovery may make another attempt succeed; it must never turn the original failed attempt into a success or certify a configuration that was not tested.

**Universal sequence**

1. Freeze the attempt and record the failure packet before retrying. Stop or block dependent stages; independent cases may continue within resource limits.
2. Classify the failed requirement from raw evidence. Separate established facts from possible causes. Check input/artifact/binary identity before blaming numerical libraries or physics.
3. Choose the cheapest discriminating diagnostic that could distinguish the leading hypotheses without modifying the model. State its expected observations.
4. Permit a new attempt only under a declared recovery class, with its own input/configuration hashes and remaining budget. Change one explanatory variable where practical; otherwise record why several changed.
5. Reapply every affected original acceptance check. Report the later result, its configuration, the original failure and any lost coverage together.
6. Stop when the attempt/resource budget is exhausted, evidence is ambiguous, or the next change would require an unapproved scientific decision. Record exactly what information, resource or experiment is needed next.

Default maximum is **three calculation attempts per case variant**, including the original; a build candidate may have **four** attempts. Freeze wall-time, memory and storage budgets in the profile. A diagnostic also consumes its declared budget. A changed model/reference or new toolchain is a new candidate/variant, not a reset button for endless retries. Require a reviewed experiment plan before extending a budget. Reference acceptance limits never change as a fallback.

**Recovery classes and equivalence**

| Class | Examples | Effect on proof |
|---|---|---|
| A: transient infrastructure | Interrupted verified download, temporary storage availability, isolated confirmed launcher setup error | Same case may retry once with fresh attempt and unchanged scientific input |
| B: execution configuration | Binding policy, supported rank/decomposition/thread count, lower build parallelism | Must revalidate numerical equivalence and record actual configuration; another rank cannot satisfy the original rank case |
| C: solver strategy | Compatible diagonalizer/mixing/iteration budget | New input hash; prove convergence to the intended electronic/magnetic branch; keep original contract and declared physical settings |
| D: numerical/model parameters | Cutoffs, meshes, smearing, bands, time step, U, functional, UPF, geometry or spin model | New scientific variant and renewed observable-convergence/reference review; cannot stand in as an equivalent original result |
| E: toolchain/platform | Different compiler, MPI, BLAS/FFT backend or larger machine | New build/platform manifest; rerun affected installation, capability and numerical matrix |

Even a class C adjustment can select a different metastable state. Agreement on iteration residual does not establish the same physical solution. A model change may be a useful next experiment, but it is never an automatic repair of the original scientific claim.

Before any restart, verify the selected QE version's restrictions on rank/decomposition, binary/version and saved-wavefunction format. A class B layout change does not authorize checkpoint reuse. Use a documented compatible checkpoint with verified ancestry or start fresh; retain the incompatible checkpoint as evidence where useful.

**Installation and environment ladders**

| Failure/location | Possible reasons to test | Ordered fallback | Proof required before continuing |
|---|---|---|---|
| Preflight/architecture/SDK | Rosetta shell, mixed ARM/Intel packages, stale CLT path, unsupported compiler/SDK | Record `uname`/binary architecture/developer tools and wrapper identities → select a coherent declared native profile → obtain missing supported prerequisites → otherwise BLOCKED | I01–I03; native binaries and selected compiler/MPI dependencies agree |
| Download/provenance | Network/proxy/TLS issue, HTTP error body, partial cache, changed archive/tag | Check status and expected content/hash → reuse an already verified cache → bounded fetch from the pinned source or approved identical-hash mirror → BLOCKED on unverifiable content | I05; exact expected checksum and complete extraction before activation; no disabled TLS or checksum bypass |
| Configure/compile/link | Missing module sources/submodules, ABI mismatch, wrong flags, literal paths, incompatible compiler | Inspect first causal error and configuration → correct the declared path/dependency issue → clean isolated rebuild with bounded jobs → separately manifest a conservative supported compiler/backend | I07/I12; full build logs, exact module outputs, loader checks and numerical gates |
| Build killed/exhausted resources | Unbounded jobs, disk full, RAM pressure | Measure free space/peak use and preserve logs → reduce build parallelism only → fresh bounded build → larger verified build host or BLOCKED | Actual complete build and selected module manifest; a truncated build directory is not an installation |
| Loader/linkage | Missing Homebrew library, wrong architecture, MPI/Fortran ABI change, bad RPATH | Resolve dependency closure and loader error → restore the exact retained closure if available → rebuild a new coherent candidate → keep old verified release if still usable | I03, I08, selected S/R checks; listing dependency names is insufficient |
| Package/CLI/Python | Symlink root error, global Python assumptions, read-only libexec, conflicting environment | Test the installed path from a clean directory → repair wrapper/environment package → run all delegated entry points → use documented source CLI only as separately limited interim route | I04/I10/I11; package support remains blocked until the package itself works |
| Activation/upgrade | Concurrent change, failed validation, interrupted pointer swap, previous dependencies removed | Refuse unvalidated candidate → reconcile journal/lock → keep or restore prior verified pointer plus dependency closure → quarantine candidate | I08/I09; prior release actually loads and passes its rollback smoke; no global-system rollback guarantee |

An upgrade must not begin by blindly upgrading/removing the old installation's dependency closure. If package-manager isolation cannot be provided, document the limitation and keep side-by-side pinned dependencies or defer the upgrade. Running jobs retain their release/dependency references until completion. macOS/CLT updates are external environment changes; requalification is required and this plan does not promise to undo them.

**Execution and numerical ladders**

| Failure/location | Possible reasons to test | Ordered fallback | Stop condition / affected proof |
|---|---|---|---|
| MPI launch before QE starts | Socket restrictions, wrong launcher/runtime, unsupported binding or oversubscription | Inspect launch-only evidence and linked MPI → correct a verified launcher/binding issue once → retry exact requested ranks → optional direct diagnostic in a separate case | Serial success never closes MPI failure. Permission restrictions require an authorized environment, not a workaround that bypasses them. R01–R03 remain blocked |
| Wrong rank count or mixed executable | Fallback to another install, serial binary under MPI, conflicting environment | Compare manifest, binary hash and QE process banner → resolve exact selected suite → rerun requested configuration | No numerical comparison can rescue wrong execution identity; H06/I02 must pass |
| Nonzero application exit | Input error, numerical exception, unsupported feature, resource failure | Parse the QE error and stage → validate input/UPF/features and resources → apply only the matching row below | Never reclassify all application errors as hwloc failures; do not keep rerunning until an intermittent pass appears |
| SCF/eigenproblem nonconvergence | Poor initial density, charge sloshing, unsuitable solver, insufficient iterations, metastable state | Verify geometry/electrons/UPF and intended state → controlled compatible solver/mixing change → increase iteration budget if justified → propose a separately reviewed parameter/model study | Check residual, observables and magnetic branch; changing smearing, U, spin or PP creates a new variant. Persistent failure is a recorded negative result |
| Numeric/reference disagreement | Wrong fixture/input/units, parser issue, legitimate branch difference, precision/FFT effect, toolchain error | Check hashes/units/grids and re-extract raw output → repeat unchanged case → compare trusted backend/platform with identical physics → isolate compiler/library/solver factors | Do not loosen limits or promote candidate values to reference. Unresolved discrepancies block the capability |
| Rank/repeat disagreement | Different actual ranks/threads, mixed binaries, stale scratch, nondeterministic branch, reduction sensitivity, hardware/runtime issue | Verify identity and fresh scratch → repeat under fixed threads/decomposition → trusted-backend comparison at the same ranks | A matching mean with outliers fails; smaller-rank success is narrower evidence, not proof of the failed rank |
| Stale/missing/wrong parent artifact | Overwritten NSCF save, mixed run directory, failed prerequisite, interrupted write | Verify parent hashes/mesh/bands/stage → rebuild the failed prerequisite in fresh scratch → rerun descendants with new ancestry | Copying old output to satisfy existence checks is forbidden; H08 must detect the injected case |
| Timeout/apparent stall | Legitimate expensive phase, waiting for input, dead MPI rank, disk/resource contention | Inspect process identity, CPU/memory/I/O and last stage → compare with declared hard limit → terminate process group only under timeout/abort policy → restart only from verified checkpoint or fresh input | Silence alone is not failure; PID existence alone is not progress or success. H10/H15 and evidence-finalization tests apply |
| Parser/unknown warning | Version drift, alternate output format, incomplete log, invalid selector | Preserve raw evidence → compare versioned documentation/structured output → extend parser with positive and adversarial fixtures → rerun extraction against raw data | Unknown values stay unknown. No regex default, zero substitution or broad warning suppression. ERROR blocks numerical claims |
| Filesystem/full disk | Shared outdir, permissions, ownership error, quota, volume full | Stop dependents and preserve emergency evidence → reclaim only proven owned disposable scratch or choose a new volume → new attempt | If evidence cannot be saved, no PASS. Verify protected sentinels and concurrent jobs remain intact |

QE documents several possible causes of convergence, library and MPI failures; a symptom alone does not prove one of them. This plan requires discriminating experiments rather than automatic blame. See the [official troubleshooting guide](https://www.quantum-espresso.org/Doc/pw_user_guide/node21.html).

**Scientific failures need interpretation**

- Relaxation/NEB step-limit termination: report incomplete optimization and final residual; extend steps or improve a recorded initial path only as a new attempt. Changed endpoints, constraints or target pressure are new scientific variants.
- Imaginary phonon modes: first assess calculation convergence, masses, structure and q sampling. A converged unstable structure can be a valid scientific result. Applying ASR or deleting imaginary modes must not manufacture stability.
- Spectral disagreement: inspect parent sampling, occupation, broadening, bands, energy reference and integration window. A freely fitted shift/scale must not hide differences. PDOS projections need not exactly sum to DOS for an incomplete projector basis.
- MD divergence: inspect ensemble, electronic convergence, time-step resolution and conservation/statistical diagnostics. Long trajectories may separate while both are valid; compare the declared invariants/statistics rather than arbitrary pointwise equality.
- Unavailable feature/large calculation: report the unsupported combination or resource requirement, retain the exact input and propose a validated external machine or explicit smaller diagnostic. Neither a different model nor a smaller job is success for the original request.

**Worked failure record logic**

If a 4-rank test prints a one-process banner after launcher failure: record `MPI_RANK_MISMATCH`, requested 4, observed 1, the exact launch/fallback evidence, and block rank-agreement qualification. Possible causes are launcher restriction, unintended serial recovery or a serial-only binary; distinguish them using launcher logs and suite metadata. A later successful 4-rank run receives a new attempt ID, passes the same numerical gates, and links to the original failure. A successful direct run is recorded only as direct execution coverage.

If an energy is NaN: record `METRIC_NONFINITE` before any tolerance comparison, include its raw extraction location, and block downstream numerical analysis. Inspect the original QE diagnostic and parser independently. A clean later run does not justify discarding the original evidence or ignoring an unexplained intermittent numerical failure in release qualification.
