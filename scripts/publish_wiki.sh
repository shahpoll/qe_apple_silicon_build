#!/usr/bin/env bash
# Publish docs/wiki pages to the GitHub wiki repository.
set -euo pipefail

ROOT_DIR=$(cd -- "$(dirname "$0")/.." && pwd)
SOURCE_DIR="$ROOT_DIR/docs/wiki"
WIKI_URL_DEFAULT="https://github.com/shahpoll/qe_apple_silicon_build.wiki.git"
WIKI_URL="${WIKI_URL:-$WIKI_URL_DEFAULT}"
COMMIT_MESSAGE="Update wiki pages"
DRY_RUN=0
KEEP_WORKDIR=0
WORKDIR=""

usage() {
  cat <<'USAGE'
Usage: scripts/publish_wiki.sh [options]

Options:
  --wiki-url <url>       Wiki repository URL
  --message <msg>        Commit message (default: "Update wiki pages")
  --workdir <path>       Reuse an existing local wiki clone path
  --dry-run              Show what would change without commit/push
  --keep-workdir         Keep temporary clone directory
  -h, --help             Show help

Examples:
  bash scripts/publish_wiki.sh
  bash scripts/publish_wiki.sh --dry-run
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --wiki-url)
      WIKI_URL="$2"
      shift 2
      ;;
    --message)
      COMMIT_MESSAGE="$2"
      shift 2
      ;;
    --workdir)
      WORKDIR="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --keep-workdir)
      KEEP_WORKDIR=1
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

if [[ ! -d "$SOURCE_DIR" ]]; then
  echo "Missing source wiki directory: $SOURCE_DIR" >&2
  exit 2
fi

pages=(
  Home.md
  Environment.md
  Workflow.md
  Troubleshooting.md
  Results.md
)

if [[ -z "$WORKDIR" ]]; then
  WORKDIR=$(mktemp -d)
  TEMP_WORKDIR=1
else
  TEMP_WORKDIR=0
  mkdir -p "$WORKDIR"
fi

cleanup() {
  if [[ $TEMP_WORKDIR -eq 1 && $KEEP_WORKDIR -eq 0 ]]; then
    rm -rf "$WORKDIR"
  fi
}
trap cleanup EXIT

if [[ -d "$WORKDIR/.git" ]]; then
  git -C "$WORKDIR" fetch --all --prune
  git -C "$WORKDIR" pull --ff-only
else
  git clone "$WIKI_URL" "$WORKDIR"
fi

for page in "${pages[@]}"; do
  if [[ ! -f "$SOURCE_DIR/$page" ]]; then
    echo "Missing source page: $SOURCE_DIR/$page" >&2
    exit 3
  fi
  cp "$SOURCE_DIR/$page" "$WORKDIR/$page"
done

git -C "$WORKDIR" add "${pages[@]}"

if git -C "$WORKDIR" diff --cached --quiet; then
  echo "No wiki changes to publish."
  exit 0
fi

if [[ $DRY_RUN -eq 1 ]]; then
  echo "Dry run; staged wiki changes:"
  git -C "$WORKDIR" status --short
  exit 0
fi

git -C "$WORKDIR" commit -m "$COMMIT_MESSAGE"
branch=$(git -C "$WORKDIR" rev-parse --abbrev-ref HEAD)
git -C "$WORKDIR" push origin "$branch"

echo "Wiki updated on branch: $branch"
