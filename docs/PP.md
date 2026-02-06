# Pseudopotentials

This repo expects pseudopotentials in:

- `cases/common/pp/`

Silicon reference file used throughout workflows:

- `Si.pbe-n-rrkjus_psl.1.0.0.UPF`

Download example:

```sh
curl -L -o cases/common/pp/Si.pbe-n-rrkjus_psl.1.0.0.UPF \
  https://pseudopotentials.quantum-espresso.org/upf_files/Si.pbe-n-rrkjus_psl.1.0.0.UPF
```

Recommended reference cutoffs for this Si setup:

- `ecutwfc = 30 Ry`
- `ecutrho = 240 Ry`

Always re-run convergence checks (`cases/si/convergence/`) if you change pseudopotentials.
