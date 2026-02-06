#!/usr/bin/env bash
# Convenience bootstrapper for newcomers.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/setup/bootstrap.sh [options]

Options:
  --qe-tag <tag>        QE archive tag (default: qe-7.5)
  --with-pwtk           Download PWTK 3.2 into external/
  --build-accelerate    Configure + build QE with Accelerate + veclibfort
  --force-fetch         Re-download QE sources even if artifacts already exist
  --install-prefix <p>  Copy built binaries to prefix/bin after build
  -h, --help            Show this help

Examples:
  # Install brew deps, fetch QE, grab pseudopotential
  bash scripts/setup/bootstrap.sh

  # Full setup including PWTK download and Accelerate build
  bash scripts/setup/bootstrap.sh --with-pwtk --build-accelerate
EOF
}

QE_TAG="qe-7.5"
WITH_PWTK=0
BUILD_ACCEL=0
FORCE_FETCH=0
INSTALL_PREFIX=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --qe-tag)
      QE_TAG="$2"
      shift 2
      ;;
    --with-pwtk)
      WITH_PWTK=1
      shift
      ;;
    --build-accelerate)
      BUILD_ACCEL=1
      shift
      ;;
    --force-fetch)
      FORCE_FETCH=1
      shift
      ;;
    --install-prefix)
      INSTALL_PREFIX="$2"
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

ROOT_DIR=$(cd -- "$(dirname "$0")/../.." && pwd)
cd "$ROOT_DIR"

printf '[bootstrap] Repository root: %s\n' "$ROOT_DIR"

if ! command -v brew >/dev/null 2>&1; then
  echo "[bootstrap] Homebrew not found. Install from https://brew.sh/ first." >&2
  exit 2
fi

echo "[bootstrap] Installing/upgrading Homebrew packages (see Brewfile)..."
brew bundle --no-lock

QE_DIR="artifacts/q-e-${QE_TAG}"
if [[ $FORCE_FETCH -eq 1 ]]; then
  echo "[bootstrap] Force-fetching Quantum ESPRESSO $QE_TAG ..."
  scripts/setup/fetch_qe.sh "$QE_TAG"
elif [[ ! -d "$QE_DIR" ]]; then
  echo "[bootstrap] Fetching Quantum ESPRESSO $QE_TAG ..."
  scripts/setup/fetch_qe.sh "$QE_TAG"
else
  echo "[bootstrap] QE sources already present at $QE_DIR (skipping fetch)."
fi

PP_DIR="cases/common/pp"
PP_FILE="$PP_DIR/Si.pbe-n-rrkjus_psl.1.0.0.UPF"
mkdir -p "$PP_DIR"
if [[ ! -f "$PP_FILE" ]]; then
  echo "[bootstrap] Downloading silicon pseudopotential to $PP_FILE ..."
  curl -L "https://pseudopotentials.quantum-espresso.org/upf_files/Si.pbe-n-rrkjus_psl.1.0.0.UPF" -o "$PP_FILE"
else
  echo "[bootstrap] Pseudopotential already present at $PP_FILE."
fi

if [[ $WITH_PWTK -eq 1 ]]; then
  DEST="external/pwtk-3.2"
  if [[ -d "$DEST" ]]; then
    echo "[bootstrap] PWTK already exists at $DEST (skipping download)."
  else
    echo "[bootstrap] Downloading PWTK 3.2 ..."
    scripts/setup/fetch_pwtk.sh
  fi
fi

if [[ $BUILD_ACCEL -eq 1 ]]; then
  echo "[bootstrap] Configuring + building QE with Accelerate ..."
  pushd "$QE_DIR" >/dev/null
  ./configure MPIF90=mpif90 CC=mpicc CPP="gcc -E" \
    BLAS_LIBS="-L$(brew --prefix veclibfort)/lib -lvecLibFort -framework Accelerate" \
    LAPACK_LIBS="-L$(brew --prefix veclibfort)/lib -lvecLibFort -framework Accelerate"
  make -j pw ph neb hp epw
  make -C PP/src bands.x dos.x projwfc.x pp.x pw2wannier90.x
  make w90
  if [[ -n "$INSTALL_PREFIX" ]]; then
    mkdir -p "$INSTALL_PREFIX/bin"
    cp -f bin/* "$INSTALL_PREFIX/bin/"
    echo "[bootstrap] Installed QE binaries to $INSTALL_PREFIX/bin"
  fi
  popd >/dev/null
fi

cat <<'EOF'
[bootstrap] Done. Next steps:
  1. (Optional) export PATH="$PWD/external/pwtk-3.2:$PATH" if you downloaded PWTK.
  2. Set QE_RANKS/QE_CPUSET/OMP_NUM_THREADS before each QE command, e.g.:
       export QE_RANKS=8 QE_CPUSET=0-9 OMP_NUM_THREADS=1
       ./scripts/run_qe.sh pw.x -- -in cases/si/manual/data/Si.scf.in
  3. Follow docs/Workflow_Basics.md for a complete beginner walk-through.
EOF
