# Beginner Workflow (Apple Silicon)

This is the shortest reliable path for a newcomer.

## 0) Clone the repository

```sh
git clone https://github.com/shahpoll/qe_apple_silicon_build.git
cd qe_apple_silicon_build
```

## 1) Install QE (one command)

Interactive:

```sh
bash scripts/qe_manager.sh
```

Non-interactive:

```sh
bash scripts/qe_manager.sh install --qe-tag qe-7.5 --install-prefix "$HOME/opt/qe-7.5" --with-pwtk
```

What this does:

- installs Homebrew dependencies from `Brewfile`
- fetches QE sources
- builds the QE binaries
- optionally fetches PWTK

## 2) Configure runtime environment

```sh
export QE_RANKS=8
export QE_CPUSET=0-9
export OMP_NUM_THREADS=1
```

Use fewer ranks for quiet test runs (for example, `QE_RANKS=2`).

## 3) Run the silicon reference workflow

```sh
cd cases/si/manual

../../../scripts/run_qe.sh pw.x -- -in data/Si.scf.in | tee logs/si_scf.txt
../../../scripts/run_qe.sh pw.x -- -in data/Si.bands.in | tee logs/si_bands_pw.txt
../../../scripts/run_qe.sh bands.x -- -in data/Si.bands_post.in | tee logs/si_bands_post.txt
../../../scripts/run_qe.sh pw.x -- -in data/Si.nscf.in | tee logs/si_nscf_pw.txt
../../../scripts/run_qe.sh dos.x -- -in data/Si.dos.in | tee logs/si_dos.txt
../../../scripts/run_qe.sh projwfc.x -- -in data/Si.projwfc.in | tee logs/si_projwfc.txt

python3 scripts/plot_bands.py
python3 scripts/plot_dos.py
python3 scripts/plot_pdos.py
python3 scripts/analyze_bandgap.py
```

Outputs:

- raw data: `cases/si/manual/data/`
- logs: `cases/si/manual/logs/`
- plots: `cases/si/manual/plots/`

## 4) Validate migration/build stability

```sh
cd ../../..
bash scripts/ci_migration_check.sh --qe-bin "$HOME/opt/qe-7.5/bin"
```

Check these files:

- `validation_reports/ci_migration_check/VALIDATION_REPORT.md`
- `validation_reports/ci_migration_check/tables/final_matrix.tsv`
- `validation_reports/ci_migration_check/plots/`

## 5) Optional brew-style command

```sh
brew install --HEAD ./Formula/qe-apple-silicon-build.rb
qe-apple-silicon-build install --qe-tag qe-7.5 --install-prefix "$HOME/opt/qe-7.5"
qe-apple-silicon-build check --qe-bin "$HOME/opt/qe-7.5/bin"
```

## 6) If something fails

Go to `Troubleshooting.md` first.
