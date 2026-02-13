# QE Apple Silicon Build

Build, run, and validate Quantum ESPRESSO on Apple Silicon with a clean newcomer workflow.

- Current baseline: macOS 26 + QE 7.5
- Focus: reproducible CPU workflows (SCF/BANDS/DOS/PDOS/phonons + HP/NEB/EPW mini-workflows)
- Previous repository name: `qe_macos15_build` (now `qe_apple_silicon_build`)

## Quick Start

### 1) Clone

```sh
git clone https://github.com/shahpoll/qe_apple_silicon_build.git
cd qe_apple_silicon_build
```

### 2) Install or update QE (single command)

Interactive (recommended first time):

```sh
bash scripts/qe_manager.sh
```

Non-interactive install:

```sh
bash scripts/qe_manager.sh install --qe-tag qe-7.5 --install-prefix "$HOME/opt/qe-7.5" --with-pwtk
```

Non-interactive update:

```sh
bash scripts/qe_manager.sh update --qe-tag qe-7.5 --install-prefix "$HOME/opt/qe-7.5"
```

### 3) Validate the build (CI-style command)

```sh
bash scripts/ci_migration_check.sh --qe-bin "$HOME/opt/qe-7.5/bin"
```

Outputs are written under `validation_reports/...`.

## Brew-Style Command UX

If you prefer an app-like command surface (`brew install ...` then run one command):

```sh
brew install --HEAD ./Formula/qe-apple-silicon-build.rb
qe-apple-silicon-build install --qe-tag qe-7.5 --install-prefix "$HOME/opt/qe-7.5"
```

For production distribution through your own tap:

```sh
brew tap shahpoll/qe
brew install shahpoll/qe/qe-macos
```

Canonical formula name stays `qe-apple-silicon-build`; short alias is `qe-macos`.
Setup details: `docs/Homebrew_Tap.md`

Then you can run:

- `qe-apple-silicon-build install ...`
- `qe-apple-silicon-build update ...`
- `qe-apple-silicon-build check --qe-bin "$HOME/opt/qe-7.5/bin"`
- `qe-apple-silicon-build smoke --ranks 2`

## What Gets Validated

The validator (`scripts/validate_build.py`) runs:

- Core silicon pipeline: `pw.x`, `bands.x`, `dos.x`, `projwfc.x`, `pp.x`
- Phonon chain: `ph.x`, `q2r.x`, `matdyn.x`
- Wrapper and linkage checks
- Reproducibility: rank sweep + repeatability
- Optional module launch checks
- Deeper mini-workflows:
  - `hp.x`: Hubbard perturbation setup path
  - `neb.x`: short real path optimization with barrier extraction
  - `epw.x`: SCF/NSCF + Wannier + EPW interpolation sanity path

Generated evidence includes TSV matrices, plots, and `VALIDATION_REPORT.md`.

## Repository Map

| Path | Purpose |
|---|---|
| `scripts/qe_manager.sh` | One-command install/update orchestration |
| `scripts/ci_migration_check.sh` | One-command smoke + full validation |
| `scripts/validate_build.py` | Validation campaign generator |
| `scripts/run_qe.sh` | MPI wrapper for QE executables |
| `bin/qe-apple-silicon-build` | User-facing CLI entrypoint |
| `Formula/qe-apple-silicon-build.rb` | Homebrew formula (local/HEAD install) |
| `cases/si/manual` | Manual silicon workflow |
| `cases/si/pwtk` | PWTK-driven workflow |
| `cases/si/comparison` | Manual vs PWTK comparisons |
| `cases/si/convergence` | Cutoff and k-mesh convergence studies |
| `docs/` | Beginner docs, troubleshooting, release guidance |
| `docs/wiki/` | Wiki-ready mirror pages |

Note: GitHub wiki content is a separate `.wiki.git` repo. See `docs/wiki/README.md` for sync steps.

## For Newcomers

Start here in this order:

1. `docs/Workflow_Basics.md`
2. `docs/Troubleshooting.md`
3. `docs/Release_Checklist.md` (before publishing)

## Notes and Limits

- Apple GPU acceleration is not available in QE (CPU-only on Apple Silicon).
- Keep `OMP_NUM_THREADS=1` unless you are intentionally running hybrid MPI/OpenMP tests.
- Prefer QE 7.5 for macOS 26 stability.

## Documentation Index

- `docs/README.md`
- `docs/Workflow_Basics.md`
- `docs/Command_Reference.md`
- `docs/Troubleshooting.md`
- `docs/PP.md`
- `docs/Release_Checklist.md`
- `docs/archive/` (legacy notes and historical worklogs)
- `CONTRIBUTING.md`

## License and Citation

- License: `LICENSE` (MIT)
- Citation metadata: `CITATION.cff`
