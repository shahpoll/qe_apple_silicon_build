# Documentation Hub

This folder is organized for first-time users first, then deeper references.

## Start Here

1. `Workflow_Basics.md`
2. `Troubleshooting.md`
3. `Release_Checklist.md`

## Guide Map

- `Workflow_Basics.md`
  - Beginner path: install, run silicon workflow, validate.
- `Troubleshooting.md`
  - Common build/runtime failures and exact fixes.
- `Command_Reference.md`
  - Fast command cheat sheet for install/run/validate workflows.
- `Homebrew_Tap.md`
  - How to publish and maintain the tap for one-command `brew install`.
- `PP.md`
  - Pseudopotential notes and cutoff guidance.
- `Release_Checklist.md`
  - Pre-push checklist for clean reproducible updates.

## Legacy Material

Older long-form notes are kept under `archive/`:

- `archive/AppleSilicon_QE_Guide.md`
- `archive/Guide.md`
- `archive/Si_Worklog.md`

These are useful for historical context but are not the main onboarding path.

## Wiki Mirror

`wiki/` contains pages that can be copied into the GitHub wiki with minimal edits.

To publish them to the actual GitHub wiki repository:

```sh
git clone https://github.com/shahpoll/qe_apple_silicon_build.wiki.git /tmp/qe_wiki
cp docs/wiki/*.md /tmp/qe_wiki/
cd /tmp/qe_wiki
git add .
git commit -m "Update wiki pages"
git push
```
