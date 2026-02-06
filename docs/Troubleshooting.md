# Troubleshooting

Baseline target: QE 7.5 on Apple Silicon (macOS 26).

## Build-time errors

### `make[1]: laxlib*.fh ... no input files`

Cause: preprocessor mismatch with Apple CLT defaults.

Fix:

- rerun configure with `CPP="gcc -E"`
- or use `scripts/setup/bootstrap.sh --build-accelerate` (already configured for this)

### `wxml.f90: DP_XML has no implicit type`

Cause: FoX XML mismatch in alternative build paths.

Fix options:

- configure with FoX support (`--with-fox=yes` or equivalent)
- use the default Accelerate build path from this repo

## Runtime issues

### MPI bind/socket errors (`PRTE ERROR`, `bind() failed`)

Cause: restrictive affinity/network behavior on macOS in some environments.

Fix:

- run via `scripts/run_qe.sh` (it has binding fallback)
- explicitly set: `export QE_BINDING="--bind-to none"`
- for quick checks use low ranks (`QE_RANKS=2`)

### Phonon instability on older builds

QE 7.4.1 showed instability on this machine after OS upgrade.
QE 7.5 resolved the issue in validation campaigns.

Run:

```sh
bash scripts/ci_migration_check.sh --qe-bin "$HOME/opt/qe-7.5/bin"
```

and confirm `ph_grid`, `q2r_ifc`, `matdyn_gamma` pass in `final_matrix.tsv`.

### `projwfc.x` or `dos.x` not found

Cause: partial QE build.

Fix:

- rebuild with `scripts/qe_manager.sh install ...`
- or ensure `make -C PP/src bands.x dos.x projwfc.x pp.x pw2wannier90.x` has run

### Pseudopotential not found

Expected path in this repo: `cases/common/pp/`.

Check:

```sh
ls cases/common/pp/Si.pbe-n-rrkjus_psl.1.0.0.UPF
```

## Physics/analysis confusion

### SCF Fermi vs DOS Fermi are different

This is expected with denser NSCF mesh + smearing. Compare trends, not strict equality.

### GPU acceleration on Apple Silicon

Not available in QE mainline for Metal. Treat all workflows here as CPU-only.

## Last resort check

Run the full migration validator and inspect report + plots:

```sh
bash scripts/ci_migration_check.sh --qe-bin "$HOME/opt/qe-7.5/bin"
```
