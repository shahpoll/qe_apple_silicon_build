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

resolve_qe_exe() {
  local exe_name="$1"
  local -a candidates=()

  if [[ -n "${QE_BIN_PATH:-}" ]]; then
    candidates+=("${QE_BIN_PATH%/}")
  fi
  candidates+=(
    "$ROOT_DIR/artifacts/q-e-qe-7.5/bin"
    "$ROOT_DIR/artifacts/q-e-qe-7.4.1/bin"
    "$HOME/opt/qe-7.5/bin"
    "$HOME/opt/qe-7.4.1/bin"
  )

  local bin_dir
  for bin_dir in "${candidates[@]}"; do
    if [[ -x "$bin_dir/$exe_name" ]]; then
      printf "%s\n" "$bin_dir/$exe_name"
      return 0
    fi
  done

  if command -v "$exe_name" >/dev/null 2>&1; then
    command -v "$exe_name"
    return 0
  fi

  return 1
}

if ! EXE=$(resolve_qe_exe "$EXE_NAME"); then
  echo "Executable '$EXE_NAME' not found. Set QE_BIN_PATH or build/install QE first." >&2
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
echo "[run_qe] Executable: $EXE" >&2

if ! mpirun -np "$RANKS" $BINDING $CPU_SET_OPT "$EXE" "$@"; then
  if [[ "${QE_BINDING:-}" == "" && "$BINDING" == "$DEFAULT_BINDING" ]]; then
    echo "[run_qe] hwloc rejected core binding; retrying with --bind-to none" >&2
    mpirun -np "$RANKS" --bind-to none --map-by ppr:1:core $CPU_SET_OPT "$EXE" "$@"
  else
    exit 1
  fi
fi
