# Troubleshooting

Full guide: `docs/Troubleshooting.md`

## Common issues

### LAXlib preprocessing errors

Reconfigure with `CPP="gcc -E"`.

### MPI socket/bind errors

Run through `scripts/run_qe.sh` and set:

```sh
export QE_BINDING="--bind-to none"
```

### Missing post-processing binaries (`dos.x`, `projwfc.x`, `bands.x`)

Rebuild using `scripts/qe_manager.sh install ...` or build PP tools explicitly.

### Phonon regression suspicion

Run:

```sh
bash scripts/ci_migration_check.sh --qe-bin "$HOME/opt/qe-7.5/bin"
```

and inspect `final_matrix.tsv`.
