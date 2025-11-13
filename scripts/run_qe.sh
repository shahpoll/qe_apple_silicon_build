#!/usr/bin/env bash
# Wrapper to run QE executables with sensible MPI binding on Apple Silicon.
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <qe-executable> [-- -in foo.in ...]" >&2
  exit 1
fi

EXE_NAME="$1"
shift
ROOT_DIR=$(cd -- "$(dirname "$0")/.." && pwd)
QE_BIN_PATH="${QE_BIN_PATH:-$ROOT_DIR/artifacts/q-e-qe-7.4.1/bin}"
EXE="$QE_BIN_PATH/$EXE_NAME"
if [[ ! -x "$EXE" ]]; then
  echo "Executable $EXE not found. Set QE_BIN_PATH or build QE first." >&2
  exit 2
fi

RANKS=${QE_RANKS:-8}
# default binding tries to distribute one rank per core; hwloc on macOS may refuse it
DEFAULT_BINDING="--map-by ppr:1:core --bind-to core"
BINDING=${QE_BINDING:-$DEFAULT_BINDING}
export OMP_NUM_THREADS=${OMP_NUM_THREADS:-1}

# Optional cpu set for mixing performance + efficiency cores.
CPU_SET_OPT=""
if [[ -n "${QE_CPUSET:-}" ]]; then
  CPU_SET_OPT="--cpu-set $QE_CPUSET"
fi

echo "[run_qe] Using $RANKS MPI ranks, OMP_NUM_THREADS=$OMP_NUM_THREADS" >&2
echo "[run_qe] Binding args: $BINDING ${QE_CPUSET:+(CPUSET=$QE_CPUSET)}" >&2

if ! mpirun -np "$RANKS" $BINDING $CPU_SET_OPT "$EXE" "$@"; then
  if [[ "${QE_BINDING:-}" == "" && "$BINDING" == "$DEFAULT_BINDING" ]]; then
    echo "[run_qe] hwloc rejected core binding; retrying with --bind-to none" >&2
    mpirun -np "$RANKS" --bind-to none --map-by ppr:1:core $CPU_SET_OPT "$EXE" "$@"
  else
    exit 1
  fi
fi
