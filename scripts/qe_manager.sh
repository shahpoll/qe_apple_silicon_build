#!/usr/bin/env bash
# One-command QE installer/updater for Apple Silicon migration flows.
set -euo pipefail

ROOT_DIR=$(cd -- "$(dirname "$0")/.." && pwd)
cd "$ROOT_DIR"

usage() {
  cat <<'USAGE'
Usage:
  scripts/qe_manager.sh [menu|install|update] [options]

Modes:
  menu                 Interactive choices (default when no mode is given)
  install              Install workflow (fetch/build/install)
  update               Update workflow (force-fetch/build/install)

Options:
  --qe-tag <tag>             QE tag (default: qe-7.5)
  --install-prefix <path>    Install prefix (default: $HOME/opt/<tag>)
  --with-pwtk                Also fetch PWTK 3.2
  --skip-build               Skip QE build
  --skip-validate            Skip post-build validation campaign
  --rank-sweep <csv>         Validation rank sweep (default: 1,2,4)
  --pipeline-ranks <n>       Validation pipeline ranks (default: 2)
  -h, --help                 Show this help

Examples:
  bash scripts/qe_manager.sh
  bash scripts/qe_manager.sh install --qe-tag qe-7.5 --install-prefix "$HOME/opt/qe-7.5"
  bash scripts/qe_manager.sh update --qe-tag qe-7.5 --with-pwtk
USAGE
}

MODE="menu"
QE_TAG="qe-7.5"
INSTALL_PREFIX=""
INSTALL_PREFIX_SET=0
WITH_PWTK=0
SKIP_BUILD=0
SKIP_VALIDATE=0
RANK_SWEEP="1,2,4"
PIPELINE_RANKS=2

if [[ $# -gt 0 ]]; then
  case "$1" in
    menu|install|update)
      MODE="$1"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
  esac
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --qe-tag)
      QE_TAG="$2"
      shift 2
      ;;
    --install-prefix)
      INSTALL_PREFIX="$2"
      INSTALL_PREFIX_SET=1
      shift 2
      ;;
    --with-pwtk)
      WITH_PWTK=1
      shift
      ;;
    --skip-build)
      SKIP_BUILD=1
      shift
      ;;
    --skip-validate)
      SKIP_VALIDATE=1
      shift
      ;;
    --rank-sweep)
      RANK_SWEEP="$2"
      shift 2
      ;;
    --pipeline-ranks)
      PIPELINE_RANKS="$2"
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

if [[ -z "$INSTALL_PREFIX" ]]; then
  INSTALL_PREFIX="$HOME/opt/${QE_TAG}"
fi

if [[ "$MODE" == "menu" ]]; then
  echo "Select action:"
  echo "  1) Fresh install"
  echo "  2) Update existing build"
  printf "Choice [1/2]: "
  read -r choice
  case "$choice" in
    1) MODE="install" ;;
    2) MODE="update" ;;
    *) echo "Invalid choice: $choice" >&2; exit 1 ;;
  esac

  printf "QE tag [%s]: " "$QE_TAG"
  read -r input
  if [[ -n "${input:-}" ]]; then
    QE_TAG="$input"
  fi

  if [[ $INSTALL_PREFIX_SET -eq 0 ]]; then
    INSTALL_PREFIX="$HOME/opt/${QE_TAG}"
  fi
  printf "Install prefix [%s]: " "$INSTALL_PREFIX"
  read -r input
  if [[ -n "${input:-}" ]]; then
    INSTALL_PREFIX="$input"
    INSTALL_PREFIX_SET=1
  fi

  printf "Fetch PWTK too? [y/N]: "
  read -r input
  if [[ "${input:-}" =~ ^[Yy]$ ]]; then
    WITH_PWTK=1
  fi

  printf "Build QE now? [Y/n]: "
  read -r input
  if [[ "${input:-}" =~ ^[Nn]$ ]]; then
    SKIP_BUILD=1
  fi

  printf "Run validation after setup? [Y/n]: "
  read -r input
  if [[ "${input:-}" =~ ^[Nn]$ ]]; then
    SKIP_VALIDATE=1
  fi
fi

BOOTSTRAP_CMD=(bash scripts/setup/bootstrap.sh --qe-tag "$QE_TAG")
if [[ $WITH_PWTK -eq 1 ]]; then
  BOOTSTRAP_CMD+=(--with-pwtk)
fi
if [[ $SKIP_BUILD -eq 0 ]]; then
  BOOTSTRAP_CMD+=(--build-accelerate --install-prefix "$INSTALL_PREFIX")
fi
if [[ "$MODE" == "update" ]]; then
  BOOTSTRAP_CMD+=(--force-fetch)
fi

echo "[qe_manager] Mode: $MODE"
echo "[qe_manager] QE tag: $QE_TAG"
echo "[qe_manager] Install prefix: $INSTALL_PREFIX"
"${BOOTSTRAP_CMD[@]}"

if [[ $SKIP_VALIDATE -eq 0 ]]; then
  OUT_DIR="validation_reports/${QE_TAG}_migration_check"
  echo "[qe_manager] Running migration validation campaign..."
  python3 scripts/validate_build.py \
    --qe-bin "$INSTALL_PREFIX/bin" \
    --out-dir "$OUT_DIR" \
    --rank-sweep "$RANK_SWEEP" \
    --pipeline-ranks "$PIPELINE_RANKS"
  echo "[qe_manager] Validation report: $OUT_DIR/VALIDATION_REPORT.md"
fi

echo "[qe_manager] Done."
