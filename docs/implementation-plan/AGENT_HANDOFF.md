# Instructions for the implementing agent

**Entry condition**

Proceed with implementation only after a subsequent instruction authorizes it. Until then, restrict work to maintaining this plan. Do not interpret examples of future commands, installation paths or deployment steps as current permission to execute them.

The workspace is `/Users/pollob/QE_macos26`; the Git repository is its child `qe_macos15_build`. Audit baseline commit is `6d5171e02181a890a720edd6ba25d1bb06af65a0`. The adjacent `q-e-qe-7.5` is a local upstream source/build tree; do not modify or reuse its mutable build artifacts as an unrecorded source of release binaries. The previously tested installation is `/Users/pollob/opt/qe-7.5`. Paths and versions must be rechecked when work resumes.

At handoff creation, `docs/audit/` is existing untracked user-task work. Preserve it, including hashes and historical output. The new `docs/implementation-plan/` is also planning work, not a production fix. Do not run destructive cleanup or reset the checkout to make it look clean. Check for applicable `AGENTS.md` files again when resuming; none was found during planning.

**First actions after implementation is authorized**

1. Read START_HERE and the entire protocol before changing code. Inspect Git state and existing user changes. Record source revision plus the working diff hash; a commit alone does not identify an uncommitted implementation.
2. Create an isolated working branch/worktree if compatible with repository state, preserving and making the audit/plan available there. Record its location and base. Do not commit or publish automatically merely because the plan describes review gates.
3. Start W00. Create the work ledger/checkpoint and proposed case catalog before changing behavior. Preserve the original audit probe results; their successful exit means the defect was reproduced, not that the project is correct.
4. Inventory the live environment read-only. Confirm workspace/scratch permissions, storage, process limits, native architecture, dependency paths and the prior installation. Do not run `brew bundle` or update shared dependencies as an inventory step.
5. Close W00 and W01 before running repaired campaign code against real QE. Use isolated synthetic fixtures while fixing paths, failure recording and process lifecycle.

**Work loop for every W item**

1. Claim the item and record ownership, dependencies, touched files, hypothesis and proof IDs in a work record. No two agents own the same production files simultaneously.
2. Reproduce the old defect in bounded scratch, or cite the preserved exact-revision reproduction when rerunning it would add no evidence. Demonstrate the regression assertion fails on the old behavior; do not merely write a test that agrees with new implementation details.
3. Implement the smallest coherent change. Consolidate shared result logic instead of maintaining separate success rules in smoke, campaign, wrappers and convergence scripts.
4. Run the item's negative and positive controls, then its relevant integration proof. Record commands, versions, paths, outputs, exit codes and reference/threshold identities. Review raw evidence independently of the generated summary.
5. If a proof fails, open a failure record immediately, preserve the attempt, classify the failure and take only the matching bounded recovery step. Continue unrelated work where safe; dependent scientific steps become `BLOCKED`.
6. Request an independent code-and-evidence review by another agent/reviewer. Fix findings and repeat only affected checks. If no independent reviewer is available, retain `REVIEW_PENDING`; a separate self-review is useful but is not independent acceptance.
7. Close the item only when its applicable proof classes and review pass. Update the ledger and checkpoint with the next eligible item. Do not use a summary count, a plot or lack of exceptions as proof.

**Task and code organization**

The implementation sequence gives proposed code boundaries. Prefer a small importable validation library, thin existing CLI frontends, declarative case/profile manifests and ordinary tests. Do not build a service or scheduler unless an actual requirement demands it. Plotting must not be a prerequisite for parsing or numerical verdicts; presentation failures have separate status and cannot alter measured quantities.

W02–W05 form shared infrastructure and should have a single integration owner. After W05, workflow repair W07/W08 and packaging/build work W09–W12 can be delegated with nonoverlapping file ownership. W06 can qualify either an identified usable existing suite or W10's staged suite; blocked MPI must not block its toolchain repair. A single manifest owner resolves shared schema changes. Rebase/reconcile changes before proving the combined revision; proof for separate branches is not proof for their integration. Hash all source/config files actually used, including new/untracked files and staged changes, as required by the protocol.

**Rules that prevent regressions**

- Explicit binary selection must never fall through to another installation. All executables in one workflow must come from the selected suite manifest.
- Never silently retry serial execution as proof of MPI support. Never replace failed output or merge attempts into one parseable log.
- Never relax a tolerance, remove a required case, suppress a warning, alter a reference or reduce the declared profile solely to obtain green results.
- Keep solver changes distinct from scientific-model changes. Pseudopotential, functional, U, geometry, charge, spin branch, smearing, cutoffs, meshes, bands or time-step changes require recorded input identity and the revalidation specified in the playbook.
- Never assume an empty prefix or clean source merely from its directory name. Never copy a new suite over an existing bin directory.
- Never use a candidate's outputs as its own independent oracle. An alternate backend sharing the same source is useful cross-checking but not complete independence from upstream bugs.
- Never use wall-time improvement, a launch banner, PID existence or `JOB DONE.` alone as a correctness criterion.
- Preserve older evidence. Corrections append a superseding record; they do not rewrite history.

**Resuming after interruption**

Read the newest checkpoint, open failure records and ledger; verify source/dependency fingerprints and evidence hashes. Treat previously `RUNNING` attempts with no terminal record as interrupted/unverified. Confirm process identity before any cleanup to avoid killing a reused PID. Resume a calculation only from an identified compatible checkpoint in a new attempt; otherwise restart in fresh scratch. Changes in code, inputs, pseudopotentials, libraries, launcher or thresholds invalidate the affected proofs.

If a tool, permission or machine resource prevents a check, record `BLOCKED` with the exact prerequisite and next action. Do not bypass permission restrictions. A successful diagnostic performed under another environment remains evidence for that environment only.

**Deliverable on each handoff**

Leave a checkpoint stating the working tree, last verified revision/diff, finished versus merely implemented items, case/profile coverage, evidence paths, outstanding failure IDs, any running processes, and the next exact command/action. Report risks and limits concretely. Final implementation delivery must include the capability matrix, installation/recovery instructions, release evidence and rollback limitations; publication or external deployment remains a separately authorized action.
