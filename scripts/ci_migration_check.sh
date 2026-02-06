#!/usr/bin/env bash
# CI-style one-command QE migration check.
set -euo pipefail

ROOT_DIR=$(cd -- "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

usage() {
  cat <<'USAGE'
Usage: scripts/ci_migration_check.sh [options]

Options:
  --qe-bin <path>         QE bin path (default: auto-detect)
  --out-dir <path>        Validation output dir (default: validation_reports/ci_migration_check)
  --rank-sweep <csv>      Rank sweep for validator (default: 1,2,4)
  --pipeline-ranks <n>    MPI ranks for main workflow (default: 2)
  --repeat-count <n>      Repeat count for SCF repeatability (default: 2)
  --smoke-ranks <n>       Ranks for smoke test (default: 2)
  -h, --help              Show help
USAGE
}

QE_BIN=""
OUT_DIR="validation_reports/ci_migration_check"
RANK_SWEEP="1,2,4"
PIPELINE_RANKS=2
REPEAT_COUNT=2
SMOKE_RANKS=2

while [[ $# -gt 0 ]]; do
  case "$1" in
    --qe-bin)
      QE_BIN="$2"
      shift 2
      ;;
    --out-dir)
      OUT_DIR="$2"
      shift 2
      ;;
    --rank-sweep)
      RANK_SWEEP="$2"
      shift 2
      ;;
    --pipeline-ranks)
      PIPELINE_RANKS="$2"
      shift 2
      ;;
    --repeat-count)
      REPEAT_COUNT="$2"
      shift 2
      ;;
    --smoke-ranks)
      SMOKE_RANKS="$2"
      shift 2
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

if [[ -n "$QE_BIN" ]]; then
  export QE_BIN_PATH="$QE_BIN"
fi

echo "[ci_check] Running smoke test..."
python3 scripts/smoke_test.py --ranks "$SMOKE_RANKS"

echo "[ci_check] Running full validation campaign..."
VALIDATE_CMD=(python3 scripts/validate_build.py
  --out-dir "$OUT_DIR"
  --rank-sweep "$RANK_SWEEP"
  --pipeline-ranks "$PIPELINE_RANKS"
  --repeat-count "$REPEAT_COUNT")
if [[ -n "$QE_BIN" ]]; then
  VALIDATE_CMD+=(--qe-bin "$QE_BIN")
fi
"${VALIDATE_CMD[@]}"

echo "[ci_check] Final matrix summary:"
awk -F '\t' 'NR>1{total++; if($2=="PASS") pass++; else fail++} END{printf("PASS=%d FAIL=%d TOTAL=%d\n", pass, fail, total)}' "$OUT_DIR/tables/final_matrix.tsv"

echo "[ci_check] Report: $OUT_DIR/VALIDATION_REPORT.md"
