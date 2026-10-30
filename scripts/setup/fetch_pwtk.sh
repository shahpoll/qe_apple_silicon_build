#!/usr/bin/env bash
set -euo pipefail
ROOT_DIR=$(cd -- "$(dirname "$0")/../.." && pwd)
exec "${QE_PYTHON:-python3}" "$ROOT_DIR/scripts/fetch_source.py" pwtk-3.2 "$@"
