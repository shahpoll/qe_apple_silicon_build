# Workflow

## Install/update in one command

Interactive:

```sh
bash scripts/qe_manager.sh
```

Non-interactive install:

```sh
bash scripts/qe_manager.sh install --qe-tag qe-7.5 --install-prefix "$HOME/opt/qe-7.5"
```

## Run migration check

```sh
bash scripts/ci_migration_check.sh --qe-bin "$HOME/opt/qe-7.5/bin"
```

## Manual silicon workflow

```sh
cd cases/si/manual
../../../scripts/run_qe.sh pw.x -- -in data/Si.scf.in
../../../scripts/run_qe.sh pw.x -- -in data/Si.bands.in
../../../scripts/run_qe.sh bands.x -- -in data/Si.bands_post.in
../../../scripts/run_qe.sh pw.x -- -in data/Si.nscf.in
../../../scripts/run_qe.sh dos.x -- -in data/Si.dos.in
../../../scripts/run_qe.sh projwfc.x -- -in data/Si.projwfc.in
```

For newcomer details, use `docs/Workflow_Basics.md`.
