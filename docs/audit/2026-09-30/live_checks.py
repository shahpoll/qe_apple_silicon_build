#!/usr/bin/env python3
"""Bounded, isolated SCF audit; never substitutes serial for failed MPI."""
import argparse
import hashlib
import json
import math
import os
import pathlib
import re
import shutil
import signal
import subprocess
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--qe-bin", type=pathlib.Path, required=True)
parser.add_argument("--output", type=pathlib.Path, required=True,
                    help="New output directory; existing directories are refused")
args = parser.parse_args()
dest = args.output.resolve()
dest.mkdir(parents=True, exist_ok=False)
binary = (args.qe_bin / "pw.x").resolve(strict=True)
launcher = shutil.which("mpirun")
pp = ROOT / "cases/common/pp/Si.pbe-n-rrkjus_psl.1.0.0.UPF"
base = ROOT / "inputs/Si.scf.in"
env = os.environ.copy()
env.update(OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", VECLIB_MAXIMUM_THREADS="1")
results = []
with tempfile.TemporaryDirectory(prefix="qe-live-audit-") as tmp:
    for label, ranks in [("direct", 1), ("mpi1", 1), ("mpi2", 2), ("mpi4", 4), ("mpi2_repeat", 2)]:
        case = pathlib.Path(tmp) / label
        case.mkdir()
        source = base.read_text().replace("pseudo_dir='../cases/common/pp'", f"pseudo_dir='{pp.parent}'")
        inp = case / "scf.in"
        inp.write_text(source)
        (dest / f"{label}.in").write_text(source)
        cmd = [str(binary), "-in", str(inp)]
        if label != "direct":
            if launcher is None:
                raise RuntimeError("mpirun not found")
            cmd = [launcher, "-np", str(ranks), "--bind-to", "none", *cmd]
        start = time.monotonic()
        with (dest / f"{label}.log").open("w") as out:
            proc = subprocess.Popen(cmd, cwd=case, env=env, stdout=out,
                                    stderr=subprocess.STDOUT, start_new_session=True)
            try:
                rc = proc.wait(timeout=90)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
                rc = 124
        log = (dest / f"{label}.log").read_text()
        energy = re.findall(r"!\s+total energy\s*=\s*([-+0-9.Ee]+)", log)
        fermi = re.findall(r"the Fermi energy is\s+([-+0-9.Ee]+)", log)
        results.append(dict(label=label, requested_ranks=ranks, returncode=rc,
                            seconds=round(time.monotonic()-start, 3),
                            actual_ranks=re.findall(r"running on\s+(\d+) processors", log),
                            converged="convergence has been achieved" in log,
                            job_done="JOB DONE." in log,
                            energy_ry=energy[-1] if energy else None,
                            fermi_ev=fermi[-1] if fermi else None, fallback=False))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

report = dict(binary=str(binary), binary_sha256=digest(binary),
              launcher=launcher, pseudopotential_sha256=digest(pp), input_sha256=digest(base),
              platform=subprocess.check_output(["sw_vers"], text=True).strip(),
              thread_environment={k: env[k] for k in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS")},
              results=results)
complete = all(r["returncode"] == 0 and r["converged"] and r["job_done"]
               and r["actual_ranks"] == [str(r["requested_ranks"])] for r in results)
energies = [float(r["energy_ry"]) for r in results if r["energy_ry"] is not None]
fermis = [float(r["fermi_ev"]) for r in results if r["fermi_ev"] is not None]
finite = (len(energies) == len(results) == len(fermis)
          and all(math.isfinite(x) for x in energies + fermis))
# Baseline limits come from the existing smoke tester. Agreement limits below
# are proposed audit limits for this exact Si input, not universal QE tolerances.
baseline_ok = finite and all(abs(e + 22.83927) <= 1e-3 for e in energies) \
                    and all(abs(f - 6.4346) <= 5e-3 for f in fermis)
agreement_ok = finite and max(energies)-min(energies) <= 1e-7 \
                     and max(fermis)-min(fermis) <= 1e-4
report["checks"] = dict(completion_and_ranks=complete, finite_values=finite,
                       baseline_match=baseline_ok, agreement=agreement_ok,
                       energy_span_ry=max(energies)-min(energies) if finite else None,
                       fermi_span_ev=max(fermis)-min(fermis) if finite else None,
                       agreement_limits=dict(energy_ry=1e-7, fermi_ev=1e-4))
(dest / "results.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
raise SystemExit(0 if complete and finite and baseline_ok and agreement_ok else 1)
