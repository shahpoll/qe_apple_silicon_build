# Homebrew Tap Setup

This guide prepares a btop-style install flow for this project.

## Goal

After setup, users install with one command:

```sh
brew install shahpoll/qe/qe-silicon
```

or

```sh
brew install shahpoll/qe/qe-apple-silicon-build
```

## 1) Create the tap repository (one-time)

Create a GitHub repo named:

- `shahpoll/homebrew-qe`

Homebrew convention is `homebrew-<tapname>`.

## 2) Cut a tagged release from this repo

Formulae should point to stable release tarballs, not only `HEAD`.

```sh
git tag v1.2.0
git push origin v1.2.0
```

## 3) Publish/update formula in tap

Use the automation script:

```sh
bash scripts/publish_homebrew_tap.sh --version v1.2.0
```

This script:

- clones or updates the tap repo
- downloads the release tarball from GitHub
- computes `sha256`
- writes/updates `Formula/qe-apple-silicon-build.rb`
- creates short aliases (`qe-silicon`, `qe-asb`)
- commits and pushes to tap

## 4) User install commands

```sh
brew tap shahpoll/qe
brew install shahpoll/qe/qe-silicon
```

## Naming suggestions (shorter install keywords)

Recommended:

- `qe-silicon` (best balance of short + clear)
- `qe-asb` (very short acronym)

Optional alternatives:

- `qe-apple`
- `qe-build`

Keep one canonical formula name (`qe-apple-silicon-build`) and expose shorter aliases.

## Do we need Homebrew team involvement?

- For tap installs (`brew install shahpoll/qe/...`): **No**
- For global install (`brew install qe-apple-silicon-build`): **Yes**, submit to `homebrew/core`
