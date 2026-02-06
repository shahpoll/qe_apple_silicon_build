# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.1.0] - 2026-02-07

### Changed

- **macOS 26 compatibility** - Validated and tested on macOS 26.2 (Darwin 25.2.0, arm64)
- **QE 7.5 as new baseline** - Upgraded from QE 7.4.1 to QE 7.5 for improved stability
- **Open MPI 5.0.8** - Updated MPI runtime compatibility

### Added

- **Comprehensive validation framework** (`scripts/validate_build.py`)
  - 39 automated test cases covering SCF, bands, DOS, PDOS, phonons
  - MPI rank sweep (1, 2, 4, 8 ranks) for portability testing
  - Reproducibility tests (5 repeated runs, σ = 0.0 energy variance)
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
