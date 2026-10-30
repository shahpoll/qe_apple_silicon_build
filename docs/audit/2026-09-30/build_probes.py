#!/usr/bin/env python3
"""Reproduce audited launcher/build defects using temporary files and fake MPI.

This script does not run QE, install packages, or modify production files. Each
``reproduced`` flag means the audited defect remains observable, not that the
production behavior is acceptable. Optional compiler/CMake probes may be skipped.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[3]


def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, timeout=60, **kwargs)


def write_executable(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")
    path.chmod(0o755)


def probe(base: Path) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    env = os.environ.copy()
    env["MPLCONFIGDIR"] = str(base / "matplotlib")

    # Match the Formula's public symlink without installing Homebrew packages.
    public_bin = base / "prefix/bin"
    public_bin.mkdir(parents=True)
    cli = public_bin / "qe-apple-silicon-build"
    cli.symlink_to(ROOT / "bin/qe-apple-silicon-build")
    help_run = run([str(cli), "help"], env=env)
    delegated_help = run([str(cli), "install", "--help"], env=env)
    results.append({
        "id": "homebrew_symlink_root",
        "reproduced": help_run.returncode == 0 and delegated_help.returncode != 0
            and "No such file" in delegated_help.stderr,
        "help_exit": help_run.returncode,
        "install_help_exit": delegated_help.returncode,
        "stderr": delegated_help.stderr.strip(),
    })

    wrapper = base / "wrapper"
    (wrapper / "scripts").mkdir(parents=True)
    shutil.copy2(ROOT / "scripts/run_qe.sh", wrapper / "scripts/run_qe.sh")
    fake_bin = base / "fakebin"
    write_executable(fake_bin / "pw.x", "#!/bin/sh\nexit 0\n")
    write_executable(fake_bin / "mpirun", """#!/bin/sh
if [ ! -f "$PROBE_STATE" ]; then
    touch "$PROBE_STATE"
    echo "APPLICATION FAILED: numerical error" >&2
    exit 17
fi
echo "SECOND ATTEMPT SUCCESS"
""")
    for key in ("QE_BINDING", "QE_CPUSET"):
        env.pop(key, None)
    env.update({
        "PATH": str(fake_bin) + os.pathsep + env["PATH"],
        "QE_BIN_PATH": str(fake_bin),
        "QE_RANKS": "2",
        "PROBE_STATE": str(base / "state"),
    })
    wrapper_cmd = ["bash", str(wrapper / "scripts/run_qe.sh"), "pw.x", "-in", "input.in"]
    retry = run(wrapper_cmd, env=env)
    results.append({
        "id": "application_failure_masked_by_retry",
        "reproduced": retry.returncode == 0 and "APPLICATION FAILED" in retry.stderr
            and "hwloc rejected" in retry.stderr,
        "exit": retry.returncode,
        "stdout": retry.stdout.strip(),
        "stderr": retry.stderr.strip(),
    })

    alternate_pw = wrapper / "artifacts/q-e-qe-7.5/bin/pw.x"
    write_executable(alternate_pw, "#!/bin/sh\nexit 0\n")
    env["QE_BIN_PATH"] = str(base / "missing-requested-build")
    fallback = run(wrapper_cmd, env=env)
    results.append({
        "id": "explicit_binary_directory_silently_falls_back",
        "reproduced": fallback.returncode == 0 and str(alternate_pw) in fallback.stderr,
        "exit": fallback.returncode,
        "stderr": fallback.stderr.strip(),
    })

    cmake = shutil.which("cmake")
    if cmake:
        cmproj = base / "cmake"
        cmproj.mkdir()
        shutil.copy2(ROOT / "CMakePresets.json", cmproj / "CMakePresets.json")
        (cmproj / "CMakeLists.txt").write_text(
            'cmake_minimum_required(VERSION 3.20)\nproject(PresetProbe NONE)\n'
            'message(STATUS "AUDIT_BLAS=${BLAS_LIBRARIES}")\n', encoding="utf-8")
        preset = run([cmake, "--preset", "openblas-release"], cwd=cmproj)
        observed = [line for line in preset.stdout.splitlines() if "AUDIT_BLAS=" in line]
        results.append({
            "id": "cmake_preset_literal_shell_substitution",
            "reproduced": preset.returncode == 0 and any("$(brew --prefix openblas)" in s for s in observed),
            "exit": preset.returncode,
            "observed": observed,
        })
    else:
        results.append({"id": "cmake_preset_literal_shell_substitution", "skipped": "cmake unavailable"})

    if shutil.which("clang") and shutil.which("otool"):
        linkage = base / "linkage"
        (linkage / "bin").mkdir(parents=True)
        (linkage / "logs").mkdir()
        (linkage / "lib.c").write_text("int foo(void) { return 0; }\n", encoding="utf-8")
        (linkage / "main.c").write_text(
            "extern int foo(void); int main(void) { return foo(); }\n", encoding="utf-8")
        lib = linkage / "libtest.dylib"
        exe = linkage / "bin/probe.x"
        compile_commands = [
            ["clang", "-dynamiclib", str(linkage / "lib.c"), "-Wl,-install_name," + str(lib), "-o", str(lib)],
            ["clang", str(linkage / "main.c"), str(lib), "-o", str(exe)],
        ]
        for command in compile_commands:
            compiled = run(command)
            if compiled.returncode:
                raise RuntimeError(compiled.stderr)
        lib.unlink()
        # Execute only the actual checker function, avoiding third-party imports
        # and all campaign entry points. No equivalent checker is reimplemented.
        parsed = ast.parse((ROOT / "scripts/validate_build.py").read_text(encoding="utf-8"))
        checker = next(n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name == "linkage_check")
        namespace = {"pathlib": __import__("pathlib"), "subprocess": subprocess}
        exec(compile(ast.Module(body=[checker], type_ignores=[]), "<actual linkage_check>", "exec"), namespace)
        check_result = namespace["linkage_check"](linkage / "bin", linkage / "logs")
        results.append({
            "id": "missing_dylib_linkage_false_pass",
            "reproduced": not lib.exists() and check_result[0] is True,
            "deleted_dependency_exists": lib.exists(),
            "checker_pass": check_result[0],
            "log": (linkage / "logs/linkage_check.log").read_text(encoding="utf-8").strip(),
        })
    else:
        results.append({"id": "missing_dylib_linkage_false_pass", "skipped": "clang/otool unavailable"})

    venv = base / "clean-python"
    created = run([sys.executable, "-m", "venv", "--without-pip", str(venv)])
    if created.returncode:
        raise RuntimeError(created.stderr)
    clean_python = run([str(venv / "bin/python"), str(ROOT / "scripts/validate_build.py"), "--help"], env=env)
    results.append({
        "id": "undeclared_python_validation_dependencies",
        "reproduced": clean_python.returncode != 0 and "ModuleNotFoundError" in clean_python.stderr,
        "exit": clean_python.returncode,
        "error": clean_python.stderr.strip().splitlines()[-1],
    })
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="qe-build-audit-") as temp_dir:
        results = probe(Path(temp_dir))
        # Remove machine-specific temporary paths from the reviewable evidence.
        payload = json.dumps({"purpose": "Defect characterization; true means defect reproduced", "probes": results}, indent=2)
        payload = payload.replace(temp_dir, "<temporary-directory>")
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if all(row.get("reproduced", True) for row in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
