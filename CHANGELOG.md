# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0-rc.1] - 2026-10-30

This preview replaces the former Homebrew distribution path with a curl-installed manager using existing native tools. The core profile is the recommended starting point; comprehensive scientific qualification remains incomplete.

### Added

- Versioned manager archive, release manifest, and SHA256 checksums.
- Read-only `doctor` prerequisite check and a beginner installation guide.
- Standard-library validation, frozen case inventories, finite-value checks, actual MPI-rank verification, and preserved success/failure evidence.
- Fresh dataset manifests, strict manual/PWTK comparisons, corrected gap/convergence analysis, and selected physical reference contracts.
- Hosted macOS tooling CI and a separate manual device-qualification workflow.

### Changed

- Builds create versioned suites with complete dependency inventories. Core activation requires its full numerical qualification; rollback rechecks identity.
- Canonical workflows process bands before uniform NSCF, so DOS/PDOS use the intended parent dataset.
- README and documentation now distinguish installation, execution, convergence, numerical agreement, and scientific adequacy.

### Removed

- Supported Homebrew Formula, Brewfile, and tap publishing scripts.
- Automatic serial fallback, generic retries, implicit historical-data analysis, and plotting dependencies for numerical verdicts.

### Known limitations

- The October device catalog recorded 33 passed cases, 17 blocked cases, and a methane Lanczos NaN failure. Missing exact references, some execution layouts, and independent comprehensive review remain open. See [validation status](docs/VALIDATION.md).

## [1.2.0] - 2026-02-16

### Added

- Homebrew tap distribution path via `shahpoll/homebrew-qe`.
- Short Homebrew install alias `qe-macos` for the canonical formula `qe-apple-silicon-build`.
- One-command release publisher (`scripts/publish_release_and_tap.sh`) to push source tag and tap update together.
- One-command wiki publisher (`scripts/publish_wiki.sh`) for syncing `docs/wiki` to the GitHub wiki repository.

### Changed

- Release and command reference docs updated for tap-based install and publish flow.
- Added tap publishing automation (`scripts/publish_homebrew_tap.sh`) and linked workflows in docs.

## [1.1.0] - 2026-02-06

### Changed

- **macOS 26 compatibility** - Validated and tested on macOS 26.2 (Darwin 25.2.0, arm64)
- **QE 7.5 as new baseline** - Upgraded from QE 7.4.1 to QE 7.5 for improved stability
- **Open MPI 5.0.8** - Updated MPI runtime compatibility

### Added

- **Comprehensive validation framework** (`scripts/validate_build.py`)
  - 43 automated validation checks in the CI migration profile
  - MPI rank sweep portability checks (CI default: 1, 2, 4; configurable)
  - Reproducibility tests with repeated SCF runs
  - Module launch checks for all QE executables
- **Advanced mini-workflows**
  - HP (Hubbard perturbation) setup validation
  - NEB (nudged elastic band) path optimization with barrier extraction
  - EPW (electron-phonon) interpolation sanity check
- **One-command install/update** (`scripts/qe_manager.sh`)
  - Interactive and non-interactive modes
  - Automatic dependency installation via Brewfile
  - Integrated post-install validation
- **CI migration check script** (`scripts/ci_migration_check.sh`)
- **Homebrew formula** (`Formula/qe-apple-silicon-build.rb`)
- **User-facing CLI** (`bin/qe-apple-silicon-build`)
- **Evidence-based validation reports**
  - TSV matrices for test results
  - Plots: band structure, DOS, PDOS, NEB profiles
  - `VALIDATION_REPORT.md` auto-generated summary

### Fixed

- **Phonon calculation stability** - QE 7.4.1 showed instability on macOS 26; resolved by upgrading to QE 7.5
- **MPI socket binding errors** - Added automatic fallback to serial execution when MPI bind fails

## [1.0.0] - 2025-11-15

### Added

- Initial release targeting macOS 15 (Apple Silicon M4)
- QE 7.4.1 build support with Accelerate framework
- Silicon reference workflows (manual and PWTK)
- Basic smoke test script
- Convergence study cases (ecutwfc, k-mesh)
- Documentation: Workflow_Basics.md, Troubleshooting.md, PP.md
