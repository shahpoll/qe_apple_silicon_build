# Release qualification

1. Preserve the baseline, working diff, source hashes and all failed attempts. Do not change remotes, reset user changes or publish automatically.
2. Run the adversarial harness and affected live numerical contracts on an inactive, identified suite. Record exact tools, inputs, references, ranks and limits.
3. Keep the installer's default manifest URL aligned with the intended release tag. Build the manager archive with `python3 scripts/package_release.py --out-dir /absolute/path/new-package`. Install it using the checksum-pinned curl bootstrap in isolated paths, including spaces/Unicode. Verify every CLI dispatch and real numerical use.
4. Verify checksum/conflict rejection, activation scope, locks, dependency drift and rollback in a dedicated test prefix. Keep production suites inactive until their matching complete qualification passes.
5. Obtain independent code-and-evidence review. A comprehensive workstation release requires all mandatory numerical cases and accepted review; core qualification is a narrower milestone.
6. Check that documentation reports failed, blocked and untested capabilities. Verify archive hashes and actual uploaded contents before announcing a remote installer URL.
7. Commit, push, tag, publish or sync a wiki only under the user's publication authorization. The v2.0.0-rc.1 manager is a preview; publishing it does not close the comprehensive qualification gates.

See [current device status](VALIDATION.md) and the [work ledger](https://github.com/shahpoll/qe_apple_silicon_build/blob/main/docs/implementation-plan/WORK_LEDGER.md).
