#!/usr/bin/env python3
"""Reproduce audit findings without launching QE or changing existing run data.

These are fault-injection probes of the original smoke tester, not scientific
validation. A zero exit from the smoke tester in these cases is the defect.
"""
import contextlib
import importlib.util
import io
import json
import pathlib
import subprocess
import tempfile
from unittest import mock

ROOT = pathlib.Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location("audited_smoke", ROOT / "scripts/smoke_test.py")
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)


def probe(name, attempts):
    with tempfile.TemporaryDirectory(prefix="qe-smoke-audit-") as tmp:
        root = pathlib.Path(tmp)
        inputs = root / "inputs"
        inputs.mkdir()
        inp = inputs / "Si.scf.in"
        inp.write_text("isolated fault injection input\n")
        wrapper = root / "run_qe.sh"
        wrapper.touch()
        binary = root / "pw.x"
        binary.touch()
        calls = []

        def fake_run(cmd, **kwargs):
            payload, returncode = attempts[len(calls)]
            calls.append({"command": cmd, "explicit_env": "env" in kwargs})
            kwargs["stdout"].write(payload)
            kwargs["stdout"].flush()
            if returncode:
                raise subprocess.CalledProcessError(returncode, cmd)
            return subprocess.CompletedProcess(cmd, 0)

        stdout, stderr = io.StringIO(), io.StringIO()
        with mock.patch.multiple(smoke, ROOT=root, INPUT=inp, RUN_QE=wrapper), \
             mock.patch.object(smoke, "resolve_pw", return_value=binary), \
             mock.patch.object(smoke, "parse_args", return_value=type("Args", (), {"ranks": 4})()), \
             mock.patch.object(smoke.subprocess, "run", side_effect=fake_run), \
             contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            rc = smoke.main()
        return {"probe": name, "smoke_exit_code": rc,
                "false_acceptance_reproduced": rc == 0,
                "output": stdout.getvalue(), "stderr": stderr.getvalue(), "calls": calls}


valid_numbers = "!    total energy = -22.83927 Ry\n     the Fermi energy is 6.4346 ev\n"
results = [
    probe("nonfinite_numbers", [("!    total energy = nan Ry\n     the Fermi energy is nan ev\n", 0)]),
    probe("missing_completion_and_convergence", [(valid_numbers, 0)]),
    probe("failed_mpi_values_reused_for_empty_serial_attempt", [
        (valid_numbers + "fatal calculation failure\n", 1),
        ("serial attempt produced no numerical output\n", 0),
    ]),
]
print(json.dumps({"kind": "synthetic fault injection", "results": results}, indent=2))
raise SystemExit(0 if all(r["false_acceptance_reproduced"] for r in results) else 1)
