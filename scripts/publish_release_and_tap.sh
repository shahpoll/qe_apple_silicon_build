#!/usr/bin/env bash
# Publish source repo release tag and update Homebrew tap in one command.
set -euo pipefail

ROOT_DIR=$(cd -- "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

VERSION_TAG=""
TAP_URL="https://github.com/shahpoll/homebrew-qe.git"
SKIP_TAG=0
SKIP_PUSH_MAIN=0

usage() {
  cat <<'USAGE'
Usage: scripts/publish_release_and_tap.sh --version <tag> [options]

Required:
  --version <tag>         Release tag like v1.2.0

Options:
  --tap-url <url>         Homebrew tap repository URL
  --skip-tag              Do not create local tag (assume it already exists)
  --skip-push-main        Do not push main before tag/tap update
  -h, --help              Show help

Example:
  bash scripts/publish_release_and_tap.sh --version v1.2.0
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version)
      VERSION_TAG="$2"
      shift 2
      ;;
    --tap-url)
      TAP_URL="$2"
      shift 2
      ;;
    --skip-tag)
      SKIP_TAG=1
      shift
      ;;
    --skip-push-main)
      SKIP_PUSH_MAIN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$VERSION_TAG" ]]; then
  echo "--version is required." >&2
  usage
  exit 2
fi

if [[ ! "$VERSION_TAG" =~ ^v[0-9] ]]; then
  echo "Version tag should look like v1.2.0 (got: $VERSION_TAG)" >&2
  exit 2
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Working tree is not clean. Commit or stash changes before publishing." >&2
  exit 3
fi

if [[ $SKIP_TAG -eq 0 ]]; then
  if git rev-parse "$VERSION_TAG" >/dev/null 2>&1; then
    echo "Tag $VERSION_TAG already exists locally. Use --skip-tag or choose another version." >&2
    exit 4
  fi
  git tag -a "$VERSION_TAG" -m "Release $VERSION_TAG"
fi

if [[ $SKIP_PUSH_MAIN -eq 0 ]]; then
  git push origin main
fi

git push origin "$VERSION_TAG"

bash scripts/publish_homebrew_tap.sh --version "$VERSION_TAG" --tap-url "$TAP_URL"

echo "Release publishing completed for $VERSION_TAG"
echo "Install command: brew install shahpoll/qe/qe"
