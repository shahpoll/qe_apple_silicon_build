# Supported entrypoints

`bin/qe-apple-silicon-build` dispatches the read-only prerequisite check `doctor`, install/update, check, smoke, workflow, convergence, upstream, activation/rollback, and read-only status. It resolves its installed symlink to the package root. Scientific verdicts use `scripts/qe_validation/` and Python's standard library.

`install.sh` bootstraps the manager from a versioned release manifest and checksum-pinned curl archive. `package_release.py` creates a local reviewable archive; it does not publish it. Source fetch helpers verify pins and refuse replacement of existing source trees. Builds and calculations use external owned directories and retain failures.

The historical Homebrew Formula/Brewfile/tap publisher are no longer supported and were removed from the current implementation. Their originals remain in the remediation baseline snapshot.
