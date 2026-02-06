# Command Reference

## Main entrypoints

### Install/update manager

```sh
bash scripts/qe_manager.sh [menu|install|update] [options]
```

### CI-style migration check

```sh
bash scripts/ci_migration_check.sh --qe-bin "$HOME/opt/qe-7.5/bin"
```

### Smoke test

```sh
python3 scripts/smoke_test.py --ranks 2
```

### Full validator

```sh
python3 scripts/validate_build.py --qe-bin "$HOME/opt/qe-7.5/bin" --out-dir validation_reports/qe75_campaign
```

## Brew-style wrapper command

```sh
qe-apple-silicon-build install --qe-tag qe-7.5 --install-prefix "$HOME/opt/qe-7.5"
qe-apple-silicon-build update --qe-tag qe-7.5
qe-apple-silicon-build check --qe-bin "$HOME/opt/qe-7.5/bin"
qe-apple-silicon-build smoke --ranks 2
```

## Publish Homebrew tap formula

```sh
bash scripts/publish_homebrew_tap.sh --version v1.2.0
```

## Runtime env helpers

```sh
export QE_RANKS=8
export QE_CPUSET=0-9
export OMP_NUM_THREADS=1
```
