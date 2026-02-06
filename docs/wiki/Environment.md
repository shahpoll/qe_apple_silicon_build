# Environment Notes

## Baseline

- Machine class: Apple Silicon (validated on Mac mini M4)
- OS baseline: macOS 26
- QE baseline: 7.5

## Toolchain (via `Brewfile`)

- `gcc`
- `open-mpi`
- `cmake`
- `veclibfort`
- `openblas`
- `python`
- `tcl-tk@8`

Install in one step:

```sh
brew bundle
```

## Important runtime notes

- Use `CPP="gcc -E"` in configure builds (handled by bootstrap scripts).
- QE on Apple Silicon here is CPU-only (no Metal backend).
- Prefer `OMP_NUM_THREADS=1` unless intentionally benchmarking hybrid MPI/OpenMP.
