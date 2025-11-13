#!/usr/bin/env bash
set -euo pipefail

VERSION="3.2"
DEST="external/pwtk-${VERSION}"
URL="http://pwtk.ijs.si/download/pwtk-${VERSION}.tar.gz"

mkdir -p external
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

curl -L "$URL" -o "$TMP/pwtk.tar.gz"
tar -xzf "$TMP/pwtk.tar.gz" -C external
rm -rf "$DEST".tar.gz
rm -rf "$DEST/.git" 2>/dev/null || true

cat <<EOF
Fetched PWTK ${VERSION} into ${DEST}. Add it to PATH, e.g.:
  export PATH="$PWD/${DEST}:$PATH"
EOF
