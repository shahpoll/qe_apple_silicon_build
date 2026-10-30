# QE reliability implementation handoff

Status updated 15 October 2026: **IMPLEMENTED IN PART — PROOF AND INDEPENDENT REVIEW PENDING.** The user subsequently authorized remediation using curl and existing tools without Homebrew. See the [current status](../implementation-status-2026-10-15.md) and work ledger. Historical proof requirements below remain applicable; publication has not been authorized.

The objective is a reproducible Apple Silicon QE installation with broad, explicitly tested calculation support, trustworthy verdicts, preserved evidence, bounded recovery, and safe upgrades. No finite test suite can certify arbitrary materials or every possible combination of QE options. The required behavior for an untested or failed case is a precise diagnosis and an honest capability status, never an invented success.

**Read in this order**

1. [Agent instructions](AGENT_HANDOFF.md): workspace, constraints, work loop and resumption.
2. [Implementation sequence](IMPLEMENTATION_SEQUENCE.md): dependencies, changes, exact proof cases and closure gates for W00–W15.
3. [Audit protocol](AUDIT_PROTOCOL.md): result states, evidence, review, failure records and reference governance.
4. [Recovery playbook](RECOVERY_PLAYBOOK.md): fallback ladders, likely causes, stop rules and equivalence limits.
5. [Verification matrix](VERIFICATION_MATRIX.md): installation, adversarial and scientific cases; support profiles and release gates.
6. [Original audit](../audit/2026-09-30/AUDIT_AND_PLAN.md) and [evidence manifest](../audit/2026-09-30/audit_manifest.json).

Track execution in the [current work ledger](WORK_LEDGER.md). No item is CLOSED; successful local proofs and remaining coverage/review gates are recorded there.

The [planning audit record](PLAN_REVIEW.md) documents independent reviews, their corrections, and document-consistency checks. It is not evidence that implementation or scientific qualification is complete.

**Scope and initial assumptions**

- Start with pinned QE 7.5, native arm64 CPU execution and the currently audited macOS 26 family. Record the actual minor OS, chip, SDK/CLT, compilers, MPI and libraries; do not claim other combinations were tested.
- Retain the currently working installation until a staged replacement passes its declared profile. An independently validated OpenBLAS profile is the proposed conservative numerical comparison path; the existing Accelerate path remains a candidate requiring equivalent proof. Neither backend is intrinsically certified by its name.
- The target is the comprehensive workstation profile defined in the verification matrix. Smaller profiles are development milestones, not a substitute for completing that target. External/nonbundled modules require their own manifests and tests.
- The existing audit established only an isolated silicon SCF result, including real MPI ranks 1/2/4 and a 2-rank repeat. It did not certify the full installation or all modules. That evidence is a dated baseline, not a current result for a changed build.
- The original September task was planning only. The October implementation is separately authorized and preserves that baseline outside the repository.

**Non-negotiable completion rule**

A work item is closed only when its required proof cases are recorded, its independent review is accepted, and its dependencies are closed. A scientific case passes only when its declared evidence and predicates pass. Missing tests, unknown convergence, missing references, skipped mandatory modules, serial substitution and successful plotting do not count as numerical validation.

The handoff templates are [case specification](templates/CASE_SPEC.json), [failure record](templates/FAILURE_RECORD.json), [work record](templates/WORK_RECORD.md), and [checkpoint](templates/CHECKPOINT.md). These are proposed document contracts, not executable schemas or implemented CLI features. Placeholder or null acceptance limits block release qualification until resolved.
