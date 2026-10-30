#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR=$(cd -- "$(dirname "$0")/../.." && pwd)
TAG="${1:-qe-7.5}"
ARGS=("$TAG")
if [[ $# -gt 1 ]]; then ARGS+=(--destination "$2"); fi
exec "${QE_PYTHON:-python3}" "$ROOT_DIR/scripts/fetch_source.py" "${ARGS[@]}"
