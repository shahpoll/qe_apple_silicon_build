# Homebrew Tap Setup

This guide prepares a btop-style install flow for this project.

## Goal

After setup, users install with one command:

```sh
brew install shahpoll/qe/qe
```

or

```sh
brew install shahpoll/qe/qe-macos
```

or

```sh
brew install shahpoll/qe/qe-apple-silicon-build
```

## Prerequisites (first-time machine setup)

- Apple Command Line Tools must be installed (`xcode-select --install`).
- Keep at least ~12 GB free on `/` before running Homebrew install/update steps.
- Verify CLT is active:

```sh
xcode-select -p
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

Or run the one-command publisher (recommended):

```sh
bash scripts/publish_release_and_tap.sh --version v1.2.0
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
- creates short aliases (`qe` and `qe-macos` by default)
- commits and pushes to tap

## 4) User install commands

```sh
brew tap shahpoll/qe
brew install shahpoll/qe/qe
```

## Naming suggestions (shorter install keywords)

Recommended:

- `qe` (shortest command)
- `qe-macos` (explicit platform context)

Optional alternatives:

- `qe-asb`
- `qe-apple`
- `qe-build`

Keep one canonical formula name (`qe-apple-silicon-build`) and expose shorter aliases.

## Do we need Homebrew team involvement?

- For tap installs (`brew install shahpoll/qe/...`): **No**
- For global install (`brew install qe-apple-silicon-build`): **Yes**, submit to `homebrew/core`
