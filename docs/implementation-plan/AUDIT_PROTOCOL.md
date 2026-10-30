# Evidence, verdicts and closure protocol

This document specifies behavior to implement. It does not describe a system already present. All numerical limits and feature combinations must be part of a frozen case/profile revision before candidate results are judged.

**1. Keep four claims distinct**

| Claim | What must be established | What it does not establish |
|---|---|---|
| Runtime capability | Exact binaries load and execute with identified dependencies/ranks | Correct physics or completed calculation |
| Workflow completion | Requested stages finish, converge where applicable, and consume the right parent data | Agreement with a trusted reference |
| Numerical regression | Named observables agree with independently established fixtures within justified limits | Adequacy of production cutoffs, model or sampling |
| Scientific adequacy | Intended observable meets a stated convergence/error budget and scientific assumptions | Universal correctness for other systems or models |

Track launch, execution, convergence, ancestry, numerical agreement, scientific convergence and presentation as separate predicates. A predicate can be not applicable only through the case contract, with a reason. A fixed-occupation SCF need not print a Fermi value; NSCF does not need an SCF convergence message; a planned finite MD trajectory is not a geometry optimization.

**2. State machines and campaign outcome**

Work item states: `PLANNED → ACTIVE → IMPLEMENTED → VERIFIED → REVIEWED → CLOSED`. Use `BLOCKED` for an unmet external prerequisite with an explicit next action; retain the previous state. A failed verification returns the item to active work, without removing the failed evidence. Implementation without proof is not accomplishment.

Attempt states: `NOT_RUN → RUNNING → PASS | FAIL | ERROR | BLOCKED | SKIP`.

| State | Meaning |
|---|---|
| PASS | All required case predicates and evidence are present and valid |
| FAIL | Execution or a measured result violates its case contract; include a typed reason |
| ERROR | Harness/parser/schema/reporting malfunction prevents a reliable verdict |
| BLOCKED | A prerequisite is unavailable, including failed ancestry, insufficient resources or forbidden MPI launch |
| SKIP | Excluded by the selected profile before it was frozen; mandatory cases cannot be skipped |
| NOT_RUN / RUNNING | No final validation claim yet |

Capability states are separate: `VERIFIED`, `UNTESTED`, `UNSUPPORTED`, `BLOCKED`, scoped to exact feature/configuration combinations. “Optional” means the user did not select that capability; once selected, its checks are mandatory. Never edit the profile after seeing failures to exclude them.

Each case has exactly one terminal **case-result record** that references all its uniquely identified immutable attempts and, if permitted, the qualifying attempt. Multiple attempts are valid; duplicate case-result records or duplicate attempt IDs are not. The frozen recovery policy determines aggregation: a demonstrated transient pre-computation infrastructure failure may be superseded by a same-contract successful retry, with `recovered=true` and review of the cause. An unexplained numerical, application or reference failure cannot be erased by selecting a later success. It leaves the case failed; a diagnosed fix creates a new candidate/campaign with fresh qualification and links to the failure. Solver/model variants likewise do not replace the original scientific case.

Freeze the campaign's expected case IDs, parameter expansion, required roles and evidence before launch. Reconcile every expected case-result afterward; absent, duplicate, unexpected or malformed records are harness errors. A required case-result FAIL makes the campaign FAIL. Otherwise, any required case-result state other than PASS makes it INCOMPLETE. Only complete required coverage can PASS. Proposed CLI outcomes: 0 for complete success, 1 for a failed required contract, 2 for invalid configuration/incomplete execution/harness error. Always include the detailed reason; do not depend on exit code alone.

Fault-injection tests have **two** outcomes: the injected calculation should FAIL/ERROR/BLOCKED as specified, while the test assertion passes when the validator detects it. Keep `test_assertion_status` distinct from `observed_case_status`. Do not include fake calculations in the count of validated real QE cases. Unexpected process crashes are not acceptable ways for a rejection test to pass: require the expected typed verdict, nonzero aggregate exit and preserved evidence.

**3. Evidence layout and identity**

Proposed runtime layout, outside installed package/source trees:

```text
runs/<campaign-id>/
  campaign.json                  # frozen profile, expected cases, code/diff identity
  events.jsonl                   # append-only lifecycle/decision journal
  environment.json               # filtered environment and dependency identity
  cases/<case-id>/<attempt-id>/
    manifest.json                # command argv, inputs, build, ranks, parents, limits
    input/                       # exact materialized input and UPF hash references
    stdout.log
    stderr.log
    artifacts.json               # relative paths, hashes, units, shapes, parent links
    metrics.json                 # observations with extraction location and precision
    assertions.json              # observed/reference/delta/limit/verdict per predicate
    result.json                  # terminal attempt verdict and reason codes
    failure.json                 # when not successful
  cases/<case-id>/case-result.json # reconciles attempts under the frozen policy
  summary.json                   # derived solely from validated terminal records
  REPORT.md                      # human-readable rendering of the same records
  review.json                    # independent review, evidence hashes and findings
```

Record UTC timestamps and monotonic durations, hardware/OS/SDK, source archive/commit hash, build flags, compiler versions, full executable realpaths/hashes, transitive dependency identity, launcher realpath/version, requested and observed ranks, threads and decomposition. A Git revision/diff alone may omit untracked or staged files: hash and archive every code/configuration file actually used, including new files and submodule state. Prefer a clean committed candidate for release proof; otherwise archive the exact source snapshot, excluding secrets/caches. Store input/UPF hashes and the actual parser/schema/tolerance versions. Capture a filtered set of relevant environment variables; do not dump credentials or unrelated environment secrets.

Every retry gets a new attempt directory and links to its predecessor. Store operational changes and scientific changes separately. Record scratch ownership and parent-data hashes; timestamps alone do not prove freshness. Separate log streams or explicitly record merged ordering within one attempt; never merge different attempts.

Use temporary writes plus atomic final-file replacement for result records, and a durable lifecycle journal. A `finally` handler is necessary but cannot survive power loss or SIGKILL: on resumption reconcile abandoned RUNNING attempts, process identity and partial files and mark them interrupted/unverified. If storage is full, emit an emergency failure on stderr and a separately provisioned evidence location if available; never claim a completed report was saved when it was not.

Preserve small critical outputs and sufficient raw logs to reconstruct every assertion. Large wavefunctions may be removed only after finalization and review according to a declared retention policy; retain them for unresolved numerical/restart failures where needed. Do not remove active-job or prior-release dependencies. Append superseding results instead of rewriting past failures. Hashes establish identity, not independent scientific truth.

**4. Case contract and reference policy**

Every case must declare: ID/revision; positive or adversarial role; feature combination; executable set; source/input/UPF hashes; prerequisites and parent-artifact identities; rank/thread/decomposition configuration; wall-time/memory/storage limits; expected process behavior; calculation-specific completion/convergence conditions; required artifacts and dimensions; metric names, units, normalization and parser selectors; expected outcome; reference provenance; finite-value rules; numeric tolerances and their rationale; allowed recovery classes; and reviewer.

Reference lineage must identify its independent origin: versioned upstream benchmark, separately verified trusted build/platform, analytic invariant, or manually reviewed archived result. Mark historical project numbers `PROVISIONAL` until traced and corroborated. Parser fixtures may use synthetic known values; they cannot certify QE science. Candidate/reference input or pseudopotential mismatch blocks comparison unless a specific transformation was justified beforehand.

For scalar metrics, define explicitly whether the rule is `abs(observed-reference) <= atol + rtol*abs(reference)`, a one-sided bound, or another domain-specific rule. All operands must be finite. Include an absolute floor near zero and units such as Ry/cell versus meV/atom. Define equality at the boundary and use representable test values to avoid accidental floating-point ambiguity. For arrays, check dimensions, coordinates, weights and alignment before residuals. Handle degeneracy by groups/subspaces when meaningful, not arbitrary eigenvector phases.

Choose limits from output precision, independently measured supported-build variation, solver settings and the physical error budget. Record calibration before qualification. Do not increase a tolerance automatically when a candidate fails. The audit's Si proposals (rank energy span 1e-7 Ry, printed Fermi span 1e-4 eV) are provisional fixture-specific values, not generic defaults. Use max span/max deviation as mandatory repeatability checks; standard deviation alone can hide an outlier. Match references as well as peers to catch identical wrong answers.

Use at least 3 fresh repetitions for release qualification and distinct real MPI ranks 1, 2 and 4 where that declared platform has sufficient resources. Test other advertised decompositions separately; unknown actual ranks cannot PASS. If resources cannot support the selected profile, mark it BLOCKED and report the narrower diagnostic separately. Fixed seeds are recorded where applicable; long dynamical trajectories need conservation/statistical contracts rather than pointwise equality.

**5. Proof dossier for every finding**

| Proof | Required record |
|---|---|
| Original failure | Old revision/input/evidence and exact failed requirement |
| Regression | Assertion that fails on old behavior and passes on corrected behavior, including expected typed rejection |
| Positive control | A valid fixture still accepted; appropriate boundary checks |
| Integration | Smallest realistic test through the actual changed entry point and its dependent workflow; real QE when the claim concerns QE computation |
| Independent review | Reviewer re-extracts selected measurements and checks the complete required-case inventory |

For pure safety/path/packaging changes, a real isolated subprocess/filesystem/package invocation is the relevant integration proof; numerical smoke is added when execution selection or libraries change. A deferred applicable real-QE test keeps the corresponding scientific finding open. Preserve original characterization probes; create new correctness assertions with explicit expected behavior rather than simply reusing their old exit codes.

Reviewer checklist: revision/diff and artifact hashes match; inputs and units agree; requested ranks match actual ranks; no inherited attempts or stale artifacts; negative tests reject for the intended reason; limits predate candidate judgment; all mandatory cases ran; claimed capabilities are no broader than evidence; failures and unresolved hypotheses remain visible. Build/profile changes invalidate affected earlier review.

**6. Failure record and diagnosis quality**

Use [FAILURE_RECORD.json](templates/FAILURE_RECORD.json). Include the exact stage, exit/signal/timeout, failed predicate with observed/reference/delta/limit, artifact/log location, attempted diagnosis, likely causes with confidence and supporting/contradicting evidence, next discriminating experiment, fallback eligibility and affected dependents. State `unknown` until a cause is established. A pattern match such as `PRTE ERROR` is a symptom, not by itself a diagnosis of binding failure.

Required reason families: configuration/schema, download/provenance, build/compile/link, architecture/ABI/loader, launcher/rank, input/physics incompatibility, convergence, numerical discrepancy, artifact ancestry/freshness, resource, timeout/stall, filesystem, parser, interruption, reporting/evidence, unsupported capability. Use stable subcodes, for example `MPI_RANK_MISMATCH`, `SCF_NOT_CONVERGED`, `METRIC_NONFINITE`, `REFERENCE_MISSING`, `PARENT_HASH_MISMATCH`, `DYLIB_UNRESOLVED`, `TIMEOUT`, `REPORT_WRITE_FAILED`.

Every recovery record answers: what failed, where, what is known, what remains a hypothesis, what changed, why that change is allowed, what must be rechecked, and what the resulting success would actually prove. See the recovery playbook for ordered actions.
