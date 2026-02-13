# Release Checklist

Use this before pushing to GitHub.

## 0) Repository identity

- Canonical name: `qe_apple_silicon_build`
- If local remote still points to old repo name:

```sh
git remote set-url origin git@github.com:shahpoll/qe_apple_silicon_build.git
```

## 1) Sync and branch

```sh
git pull --rebase origin main
git switch -c codex/release-<topic>
git status --short
```

## 2) Confirm core paths

```sh
ls "$HOME/opt/qe-7.5/bin/pw.x"
ls cases/common/pp/Si.pbe-n-rrkjus_psl.1.0.0.UPF
```

## 3) Run checks

Smoke:

```sh
python3 scripts/smoke_test.py --ranks 2
```

CI-style migration validation:

```sh
bash scripts/ci_migration_check.sh --qe-bin "$HOME/opt/qe-7.5/bin"
```

Confirm summary matrix:

```sh
cat validation_reports/ci_migration_check/tables/final_matrix.tsv
```

## 4) Review and stage

```sh
git add README.md docs/ scripts/ Formula/ bin/ .github/
git diff --staged
```

## 5) Commit and push

```sh
git commit -m "Polish docs and tooling for newcomer-first QE workflow"
git push -u origin codex/release-<topic>
```

## 6) PR checklist

Include in PR body:

- what changed (docs/scripts/layout)
- validation summary (`PASS/FAIL/TOTAL`)
- path to validation report (`validation_reports/.../VALIDATION_REPORT.md`)

## 7) Publish Homebrew tap formula (optional release step)

After tagging and pushing a release tag:

```sh
bash scripts/publish_homebrew_tap.sh --version v1.2.0
```

Details and naming options are documented in `docs/Homebrew_Tap.md`.

Or use the one-shot publisher:

```sh
bash scripts/publish_release_and_tap.sh --version v1.2.0
```
