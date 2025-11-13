#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <qe-tag> [destination]" >&2
  exit 1
fi

TAG="$1"
DEST="${2:-artifacts/q-e-$TAG}"
ARCHIVE_URL="https://gitlab.com/QEF/q-e/-/archive/$TAG/q-e-$TAG.tar.gz"

mkdir -p "$(dirname "$DEST")"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

curl -L "$ARCHIVE_URL" -o "$TMP/qe.tar.gz"
mkdir -p "$DEST"
tar -xzf "$TMP/qe.tar.gz" -C "$TMP"
rm -rf "$DEST"
mv "$TMP/q-e-$TAG" "$DEST"
rm -rf "$DEST/.git" 2>/dev/null || true

cat <<EOF
Fetched Quantum ESPRESSO $TAG into $DEST
EOF
