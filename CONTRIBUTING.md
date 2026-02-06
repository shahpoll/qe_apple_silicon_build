# Contributing

Thanks for contributing.

## Before opening a PR

1. Run smoke test:

```sh
python3 scripts/smoke_test.py --ranks 2
```

2. Run migration validation:

```sh
bash scripts/ci_migration_check.sh --qe-bin "$HOME/opt/qe-7.5/bin"
```

3. Confirm matrix pass/fail table:

```sh
cat validation_reports/ci_migration_check/tables/final_matrix.tsv
```

## Branch and commit style

- Branch prefix: `codex/`
- Keep commits scoped (docs/scripts/validation changes separated when possible).
- Mention validation evidence path in PR description.

## Docs expectations

If user-facing commands or paths change, update:

- `README.md`
- `docs/Workflow_Basics.md`
- `docs/Troubleshooting.md`
- `docs/wiki/` mirror pages (if relevant)
