# Scripts Overview

Primary commands:

- `qe_manager.sh`
  - Install/update QE toolchain and optionally run full validation.
- `ci_migration_check.sh`
  - Run smoke test + full validation in one command.
- `publish_wiki.sh`
  - Publish `docs/wiki/` pages to the GitHub wiki repository.
- `publish_homebrew_tap.sh`
  - Publish/update the Homebrew tap formula from a tagged release.
- `publish_release_and_tap.sh`
  - One-command publish for source release tag plus Homebrew tap update.
- `validate_build.py`
  - Full campaign generator (tables, plots, report).
- `smoke_test.py`
  - Fast SCF health check.
- `run_qe.sh`
  - MPI wrapper for QE executables.

Setup helpers:

- `setup/bootstrap.sh`
  - Installs dependencies, fetches sources, builds binaries.
- `setup/fetch_qe.sh`
  - Download QE source archive by tag.
- `setup/fetch_pwtk.sh`
  - Download PWTK helper toolkit.

Typical flow:

```sh
bash scripts/qe_manager.sh install --qe-tag qe-7.5 --install-prefix "$HOME/opt/qe-7.5"
bash scripts/ci_migration_check.sh --qe-bin "$HOME/opt/qe-7.5/bin"
```
