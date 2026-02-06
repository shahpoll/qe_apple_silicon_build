#!/usr/bin/env python3
"""Run a reproducible QE validation campaign with evidence plots."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import math
import os
import pathlib
import re
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from typing import Callable, Iterable

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("MPLCONFIGDIR", str(pathlib.Path(tempfile.gettempdir()) / "qe_validate_mpl"))

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.use("Agg")

ROOT = pathlib.Path(__file__).resolve().parents[1]
pathlib.Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
INPUTS_DIR = ROOT / "inputs"
PP_DIR = ROOT / "cases" / "common" / "pp"
COMMON_SCRIPTS = ROOT / "cases" / "common" / "scripts"

REFERENCE_METRICS = {
    "SCF total energy (Ry)": -22.83927198,
    "SCF Fermi (eV)": 6.4346,
    "DOS EFermi (eV)": 6.2130,
    "Indirect gap (eV)": 0.5720,
    "Direct gap (eV)": 2.5625,
}

MODULE_EXECUTABLES = [
    "cp.x",
    "neb.x",
    "hp.x",
    "epw.x",
    "xspectra.x",
    "all_currents.x",
    "turbo_davidson.x",
    "turbo_lanczos.x",
    "turbo_eels.x",
    "turbo_magnon.x",
    "turbo_spectrum.x",
]


@dataclass
class CaseResult:
    case: str
    status: str
    duration_s: float
    note: str


@dataclass
class ScfRun:
    label: str
    ranks: int
    total_energy_ry: float
    fermi_ev: float
    duration_s: float


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QE validation campaign")
    parser.add_argument(
        "--qe-bin",
        type=pathlib.Path,
        help="Directory with QE executables (pw.x, ph.x, ...).",
    )
    parser.add_argument(
        "--out-dir",
        type=pathlib.Path,
        default=ROOT / "validation_reports" / "qe75_campaign",
        help="Output directory for logs, tables, and plots.",
    )
    parser.add_argument(
        "--rank-sweep",
        default="1,2,4,8",
        help="Comma-separated MPI ranks for SCF portability sweep.",
    )
    parser.add_argument(
        "--pipeline-ranks",
        type=int,
        default=4,
        help="MPI ranks for the full workflow run.",
    )
    parser.add_argument(
        "--repeat-count",
        type=int,
        default=5,
        help="Repeat count for SCF reproducibility test.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=1800,
        help="Timeout (seconds) for each QE command.",
    )
    parser.add_argument(
        "--keep-work",
        action="store_true",
        help="Keep work/ directory (tmp wavefunctions) after campaign.",
    )
    return parser.parse_args()


def detect_qe_bin(explicit: pathlib.Path | None) -> pathlib.Path:
    if explicit is not None:
        candidate = explicit.expanduser().resolve()
        if (candidate / "pw.x").is_file() and (candidate / "ph.x").is_file():
            return candidate
        raise FileNotFoundError(f"Missing pw.x/ph.x in --qe-bin: {candidate}")

    candidates = [
        pathlib.Path(os.environ.get("QE_BIN_PATH", "")),
        ROOT / "artifacts" / "q-e-qe-7.5" / "bin",
        ROOT / "artifacts" / "q-e-qe-7.4.1" / "bin",
        pathlib.Path.home() / "opt" / "qe-7.5" / "bin",
        pathlib.Path.home() / "opt" / "qe-7.4.1" / "bin",
    ]
    for candidate in candidates:
        if not str(candidate):
            continue
        if (candidate / "pw.x").is_file() and (candidate / "ph.x").is_file():
            return candidate.resolve()
    raise FileNotFoundError("Could not find a QE bin directory with pw.x and ph.x.")


def prepare_dirs(out_dir: pathlib.Path) -> dict[str, pathlib.Path]:
    if out_dir.exists():
        shutil.rmtree(out_dir)
    paths = {
        "root": out_dir,
        "work": out_dir / "work",
        "input": out_dir / "input",
        "logs": out_dir / "logs",
        "data": out_dir / "data",
        "plots": out_dir / "plots",
        "tables": out_dir / "tables",
    }
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
    return paths


def replace_pseudo_dir(content: str) -> str:
    return re.sub(r"pseudo_dir\s*=\s*'[^']*'", f"pseudo_dir='{PP_DIR}'", content)


def replace_prefix_and_outdir(content: str, prefix: str, outdir: str) -> str:
    content = re.sub(r"prefix\s*=\s*'[^']*'", f"prefix='{prefix}'", content)
    content = re.sub(r"outdir\s*=\s*'[^']*'", f"outdir='{outdir}'", content)
    return content


def write_inputs(input_dir: pathlib.Path) -> dict[str, pathlib.Path]:
    mapping: dict[str, pathlib.Path] = {}
    for name in [
        "Si.scf.in",
        "Si.bands.in",
        "Si.bands_post.in",
        "Si.nscf.in",
        "Si.dos.in",
        "Si.projwfc.in",
    ]:
        src = INPUTS_DIR / name
        dst = input_dir / name
        content = src.read_text(encoding="utf-8")
        if "pseudo_dir" in content:
            content = replace_pseudo_dir(content)
        dst.write_text(content, encoding="utf-8")
        mapping[name] = dst

    # Additional generated inputs used by the validation campaign.
    pp_in = input_dir / "Si.pp.in"
    pp_in.write_text(
        "&inputpp\n"
        "  prefix='silicon',\n"
        "  outdir='./tmp',\n"
        "  filplot='silicon.rho',\n"
        "  plot_num=0\n"
        "/\n"
        "&plot\n"
        "  nfile=1,\n"
        "  filepp(1)='silicon.rho',\n"
        "  weight(1)=1.0,\n"
        "  iflag=3,\n"
        "  output_format=6,\n"
        "  fileout='silicon_rho.cube'\n"
        "/\n",
        encoding="utf-8",
    )
    mapping["Si.pp.in"] = pp_in

    scf_ph_in = input_dir / "Si.scf_ph.in"
    scf_ph_in.write_text(
        "&control\n"
        "  calculation='scf', prefix='siliconph', pseudo_dir='" + str(PP_DIR) + "', outdir='./tmp_ph'\n"
        "/\n"
        "&system\n"
        "  ibrav=2, celldm(1)=10.26, nat=2, ntyp=1, ecutwfc=30.0, ecutrho=240.0,\n"
        "  occupations='fixed'\n"
        "/\n"
        "&electrons\n"
        "  conv_thr=1.0d-8, mixing_beta=0.7\n"
        "/\n"
        "ATOMIC_SPECIES\n"
        " Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF\n"
        "ATOMIC_POSITIONS crystal\n"
        " Si 0.00 0.00 0.00\n"
        " Si 0.25 0.25 0.25\n"
        "K_POINTS automatic\n"
        " 8 8 8  0 0 0\n",
        encoding="utf-8",
    )
    mapping["Si.scf_ph.in"] = scf_ph_in

    ph_in = input_dir / "Si.ph.in"
    ph_in.write_text(
        "&inputph\n"
        " tr2_ph=1.0d-14,\n"
        " prefix='siliconph',\n"
        " outdir='./tmp_ph',\n"
        " amass(1)=28.085,\n"
        " fildyn='siliconph.dynG'\n"
        "/\n"
        "0.0 0.0 0.0\n",
        encoding="utf-8",
    )
    mapping["Si.ph.in"] = ph_in

    ph_grid = input_dir / "Si.ph_grid.in"
    ph_grid.write_text(
        "&inputph\n"
        " tr2_ph=1.0d-14,\n"
        " prefix='siliconph',\n"
        " outdir='./tmp_ph',\n"
        " amass(1)=28.085,\n"
        " ldisp=.true.,\n"
        " nq1=1,\n"
        " nq2=1,\n"
        " nq3=1,\n"
        " fildyn='siliconph_grid.dyn'\n"
        "/\n",
        encoding="utf-8",
    )
    mapping["Si.ph_grid.in"] = ph_grid

    q2r = input_dir / "Si.q2r.in"
    q2r.write_text(
        "&input\n"
        "  fildyn = 'siliconph_grid.dyn'\n"
        "  zasr = 'simple'\n"
        "  flfrc = 'silicon.fc'\n"
        "/\n",
        encoding="utf-8",
    )
    mapping["Si.q2r.in"] = q2r

    matdyn = input_dir / "Si.matdyn.in"
    matdyn.write_text(
        "&input\n"
        "  asr='simple'\n"
        "  flfrc='silicon.fc'\n"
        "  flfrq='silicon.freq'\n"
        "  q_in_cryst_coord=.true.\n"
        "/\n"
        "1\n"
        "0.0 0.0 0.0\n",
        encoding="utf-8",
    )
    mapping["Si.matdyn.in"] = matdyn

    hp_scf = input_dir / "Si.hp.scf.in"
    hp_scf.write_text(
        "&control\n"
        "  calculation='scf',\n"
        "  prefix='sihp',\n"
        "  pseudo_dir='" + str(PP_DIR) + "',\n"
        "  outdir='./tmp_hp'\n"
        "/\n"
        "&system\n"
        "  ibrav=2, celldm(1)=10.26, nat=2, ntyp=1,\n"
        "  ecutwfc=30.0, ecutrho=240.0,\n"
        "  occupations='fixed'\n"
        "/\n"
        "&electrons\n"
        "  conv_thr=1.0d-8, mixing_beta=0.7\n"
        "/\n"
        "ATOMIC_SPECIES\n"
        " Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF\n"
        "ATOMIC_POSITIONS crystal\n"
        " Si 0.00 0.00 0.00\n"
        " Si 0.25 0.25 0.25\n"
        "K_POINTS automatic\n"
        " 4 4 4 0 0 0\n"
        "HUBBARD (ortho-atomic)\n"
        "U Si-3p 1.0\n",
        encoding="utf-8",
    )
    mapping["Si.hp.scf.in"] = hp_scf

    hp_in = input_dir / "Si.hp.in"
    hp_in.write_text(
        "&inputhp\n"
        "  prefix='sihp'\n"
        "  outdir='./tmp_hp'\n"
        "  nq1=1\n"
        "  nq2=1\n"
        "  nq3=1\n"
        "  determine_num_pert_only=.true.\n"
        "/\n",
        encoding="utf-8",
    )
    mapping["Si.hp.in"] = hp_in

    neb_in = input_dir / "Si.neb.in"
    neb_in.write_text(
        "BEGIN\n"
        "BEGIN_PATH_INPUT\n"
        "&PATH\n"
        "  restart_mode='from_scratch',\n"
        "  string_method='neb',\n"
        "  nstep_path=5,\n"
        "  num_of_images=3,\n"
        "  opt_scheme='quick-min',\n"
        "  ds=1.0d0,\n"
        "/\n"
        "END_PATH_INPUT\n"
        "\n"
        "BEGIN_ENGINE_INPUT\n"
        "&CONTROL\n"
        "  calculation='scf',\n"
        "  prefix='sineb',\n"
        "  pseudo_dir='" + str(PP_DIR) + "',\n"
        "  outdir='./tmp_neb',\n"
        "  tprnfor=.true.\n"
        "/\n"
        "&SYSTEM\n"
        "  ibrav=2, celldm(1)=10.26,\n"
        "  nat=2, ntyp=1,\n"
        "  ecutwfc=30.0, ecutrho=240.0,\n"
        "  occupations='fixed'\n"
        "/\n"
        "&ELECTRONS\n"
        "  conv_thr=1.0d-7,\n"
        "  mixing_beta=0.7\n"
        "/\n"
        "ATOMIC_SPECIES\n"
        " Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF\n"
        "K_POINTS automatic\n"
        " 2 2 2 0 0 0\n"
        "\n"
        "BEGIN_POSITIONS\n"
        "FIRST_IMAGE\n"
        "ATOMIC_POSITIONS crystal\n"
        " Si 0.00 0.00 0.00\n"
        " Si 0.25 0.25 0.25\n"
        "INTERMEDIATE_IMAGE\n"
        "ATOMIC_POSITIONS crystal\n"
        " Si 0.00 0.00 0.00\n"
        " Si 0.30 0.25 0.25\n"
        "LAST_IMAGE\n"
        "ATOMIC_POSITIONS crystal\n"
        " Si 0.00 0.00 0.00\n"
        " Si 0.35 0.25 0.25\n"
        "END_POSITIONS\n"
        "END_ENGINE_INPUT\n"
        "END\n",
        encoding="utf-8",
    )
    mapping["Si.neb.in"] = neb_in

    epw_scf = input_dir / "Si.epw.scf.in"
    epw_scf.write_text(
        "&control\n"
        " calculation='scf',\n"
        " prefix='siepw',\n"
        " pseudo_dir='" + str(PP_DIR) + "',\n"
        " outdir='./tmp_epw',\n"
        " verbosity='high',\n"
        " wf_collect=.true.\n"
        "/\n"
        "&system\n"
        " ibrav=2,\n"
        " celldm(1)=10.26,\n"
        " nat=2,\n"
        " ntyp=1,\n"
        " ecutwfc=30.0,\n"
        " ecutrho=240.0,\n"
        " occupations='fixed',\n"
        " nbnd=8\n"
        "/\n"
        "&electrons\n"
        " conv_thr=1.0d-10,\n"
        " mixing_beta=0.7\n"
        "/\n"
        "ATOMIC_SPECIES\n"
        " Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF\n"
        "ATOMIC_POSITIONS crystal\n"
        " Si 0.00 0.00 0.00\n"
        " Si 0.25 0.25 0.25\n"
        "K_POINTS automatic\n"
        " 2 2 2 0 0 0\n",
        encoding="utf-8",
    )
    mapping["Si.epw.scf.in"] = epw_scf

    epw_nscf = input_dir / "Si.epw.nscf.in"
    epw_nscf.write_text(
        "&control\n"
        " calculation='nscf',\n"
        " prefix='siepw',\n"
        " pseudo_dir='" + str(PP_DIR) + "',\n"
        " outdir='./tmp_epw',\n"
        " wf_collect=.true.\n"
        "/\n"
        "&system\n"
        " ibrav=2,\n"
        " celldm(1)=10.26,\n"
        " nat=2,\n"
        " ntyp=1,\n"
        " ecutwfc=30.0,\n"
        " ecutrho=240.0,\n"
        " occupations='fixed',\n"
        " nbnd=8\n"
        "/\n"
        "&electrons\n"
        " conv_thr=1.0d-10,\n"
        " mixing_beta=0.7\n"
        "/\n"
        "ATOMIC_SPECIES\n"
        " Si 28.085 Si.pbe-n-rrkjus_psl.1.0.0.UPF\n"
        "ATOMIC_POSITIONS crystal\n"
        " Si 0.00 0.00 0.00\n"
        " Si 0.25 0.25 0.25\n"
        "K_POINTS crystal\n"
        "8\n"
        "0.0000000000 0.0000000000 0.0000000000 0.1250000000\n"
        "0.0000000000 0.0000000000 0.5000000000 0.1250000000\n"
        "0.0000000000 0.5000000000 0.0000000000 0.1250000000\n"
        "0.0000000000 0.5000000000 0.5000000000 0.1250000000\n"
        "0.5000000000 0.0000000000 0.0000000000 0.1250000000\n"
        "0.5000000000 0.0000000000 0.5000000000 0.1250000000\n"
        "0.5000000000 0.5000000000 0.0000000000 0.1250000000\n"
        "0.5000000000 0.5000000000 0.5000000000 0.1250000000\n",
        encoding="utf-8",
    )
    mapping["Si.epw.nscf.in"] = epw_nscf

    epw_win = input_dir / "siepw.win"
    epw_win.write_text(
        "num_wann = 4\n"
        "num_bands = 8\n"
        "dis_win_max = 20.0\n"
        "dis_froz_max = 10.0\n"
        "iprint = 2\n"
        "conv_tol = 1.0d-10\n"
        "begin unit_cell_cart\n"
        "bohr\n"
        " -5.1300000000  0.0000000000  5.1300000000\n"
        "  0.0000000000  5.1300000000  5.1300000000\n"
        " -5.1300000000  5.1300000000  0.0000000000\n"
        "end unit_cell_cart\n"
        "begin atoms_frac\n"
        " Si 0.000000 0.000000 0.000000\n"
        " Si 0.250000 0.250000 0.250000\n"
        "end atoms_frac\n"
        "begin projections\n"
        " Si:sp3\n"
        "end projections\n"
        "mp_grid = 2 2 2\n"
        "begin kpoints\n"
        " 0.0000000000 0.0000000000 0.0000000000\n"
        " 0.0000000000 0.0000000000 0.5000000000\n"
        " 0.0000000000 0.5000000000 0.0000000000\n"
        " 0.0000000000 0.5000000000 0.5000000000\n"
        " 0.5000000000 0.0000000000 0.0000000000\n"
        " 0.5000000000 0.0000000000 0.5000000000\n"
        " 0.5000000000 0.5000000000 0.0000000000\n"
        " 0.5000000000 0.5000000000 0.5000000000\n"
        "end kpoints\n",
        encoding="utf-8",
    )
    mapping["siepw.win"] = epw_win

    epw_pw2wan = input_dir / "Si.epw.pw2wan.in"
    epw_pw2wan.write_text(
        "&inputpp\n"
        " outdir='./tmp_epw',\n"
        " prefix='siepw',\n"
        " seedname='siepw',\n"
        " write_amn=.true.,\n"
        " write_mmn=.true.,\n"
        " write_unk=.false.\n"
        "/\n",
        encoding="utf-8",
    )
    mapping["Si.epw.pw2wan.in"] = epw_pw2wan

    epw_in = input_dir / "Si.epw.in"
    epw_in.write_text(
        "&inputepw\n"
        " prefix='siepw',\n"
        " amass(1)=28.085,\n"
        " outdir='./tmp_epw',\n"
        " elph=.false.,\n"
        " ep_coupling=.false.,\n"
        " epwwrite=.true.,\n"
        " epwread=.false.,\n"
        " nbndsub=4,\n"
        " wannierize=.false.,\n"
        " num_iter=10,\n"
        " iprint=2,\n"
        " dis_win_max=20.0,\n"
        " dis_froz_max=10.0,\n"
        " proj(1)='f=0,0,0:l=-3',\n"
        " elecselfen=.false.,\n"
        " phonselfen=.false.,\n"
        " a2f=.false.,\n"
        " nk1=2,\n"
        " nk2=2,\n"
        " nk3=2,\n"
        " nq1=1,\n"
        " nq2=1,\n"
        " nq3=1\n"
        "/\n",
        encoding="utf-8",
    )
    mapping["Si.epw.in"] = epw_in
    return mapping


def run_command(
    cmd: list[str],
    *,
    cwd: pathlib.Path,
    log_path: pathlib.Path,
    env: dict[str, str] | None = None,
    timeout_s: int = 1800,
    stdin_text: str | None = None,
    append: bool = False,
) -> tuple[int, float]:
    start = time.perf_counter()
    with log_path.open("a" if append else "w", encoding="utf-8") as handle:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
            text=True,
            input=stdin_text,
            stdout=handle,
            stderr=subprocess.STDOUT,
            timeout=timeout_s,
            check=False,
        )
    return proc.returncode, time.perf_counter() - start


def has_mpi_socket_error(log_path: pathlib.Path) -> bool:
    text = log_path.read_text(encoding="utf-8", errors="replace")
    markers = [
        "PRTE ERROR",
        "No sockets were able to be opened",
        "No network interfaces were found",
        "bind() failed for port",
    ]
    return any(marker in text for marker in markers)


def run_mpi_qe(
    exe: pathlib.Path,
    input_file: pathlib.Path,
    *,
    ranks: int,
    cwd: pathlib.Path,
    log_path: pathlib.Path,
    timeout_s: int,
) -> tuple[int, float]:
    cmd = [
        "mpirun",
        "-np",
        str(ranks),
        "--bind-to",
        "none",
        str(exe),
        "-in",
        str(input_file),
    ]
    rc, duration = run_command(cmd, cwd=cwd, log_path=log_path, timeout_s=timeout_s)
    if rc == 0:
        return rc, duration

    if has_mpi_socket_error(log_path):
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write("\n[validate_build] MPI launch failed; retrying serial execution.\n")
        rc2, duration2 = run_command(
            [str(exe), "-in", str(input_file)],
            cwd=cwd,
            log_path=log_path,
            timeout_s=timeout_s,
            append=True,
        )
        return rc2, duration + duration2

    return rc, duration


def parse_total_energy(log_text: str) -> float:
    for line in log_text.splitlines():
        if line.strip().startswith("!    total energy"):
            return float(line.split("=")[-1].split()[0])
    raise RuntimeError("total energy not found")


def parse_fermi(log_text: str) -> float:
    for line in log_text.splitlines():
        if "the Fermi energy is" in line:
            return float(line.split()[-2])
    raise RuntimeError("Fermi level not found")


def parse_dos_fermi(dos_path: pathlib.Path) -> float:
    header = dos_path.read_text(encoding="utf-8").splitlines()[0]
    match = re.search(r"EFermi\s*=\s*([-+0-9.]+)", header)
    if not match:
        raise RuntimeError(f"EFermi not found in {dos_path}")
    return float(match.group(1))


def parse_bands(path: pathlib.Path) -> tuple[np.ndarray, np.ndarray]:
    bands: list[list[tuple[float, float]]] = []
    current: list[tuple[float, float]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            if current:
                bands.append(current)
                current = []
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        current.append((float(parts[0]), float(parts[1])))
    if current:
        bands.append(current)
    if not bands:
        raise RuntimeError(f"No bands parsed from {path}")
    nk = len(bands[0])
    for band in bands:
        if len(band) != nk:
            raise RuntimeError(f"Inconsistent band lengths in {path}")
    k_path = np.array([item[0] for item in bands[0]], dtype=float)
    energies = np.array([[item[1] for item in band] for band in bands], dtype=float)
    return k_path, energies


def compute_gaps(bands_path: pathlib.Path, fermi: float) -> tuple[float, float]:
    _, energies = parse_bands(bands_path)
    with np.errstate(invalid="ignore"):
        valence = np.where(energies <= fermi, energies, -math.inf)
        conduction = np.where(energies >= fermi, energies, math.inf)
    valence_max_by_k = valence.max(axis=0)
    conduction_min_by_k = conduction.min(axis=0)
    vmax = float(np.max(valence_max_by_k))
    cmin = float(np.min(conduction_min_by_k))
    indirect = cmin - vmax
    direct = float(np.min(conduction_min_by_k - valence_max_by_k))
    return indirect, direct


def has_job_done(log_path: pathlib.Path) -> bool:
    text = log_path.read_text(encoding="utf-8", errors="replace")
    return "JOB DONE." in text


def has_epw_interpolation_marker(log_path: pathlib.Path) -> bool:
    text = log_path.read_text(encoding="utf-8", errors="replace")
    return "Electron-Phonon interpolation" in text


def parse_neb_activation_ev(log_path: pathlib.Path) -> float | None:
    text = log_path.read_text(encoding="utf-8", errors="replace")
    matches = re.findall(r"activation energy \(\-\>\)\s*=\s*([-+0-9.]+)\s*eV", text)
    if not matches:
        return None
    return float(matches[-1])


def parse_neb_profile(dat_path: pathlib.Path) -> tuple[np.ndarray, np.ndarray]:
    x: list[float] = []
    energy: list[float] = []
    for raw in dat_path.read_text(encoding="utf-8", errors="replace").splitlines():
        parts = raw.split()
        if len(parts) < 2:
            continue
        try:
            x.append(float(parts[0]))
            energy.append(float(parts[1]))
        except ValueError:
            continue
    if not x:
        raise RuntimeError(f"No NEB profile data in {dat_path}")
    return np.array(x, dtype=float), np.array(energy, dtype=float)


def plot_neb_profile(dat_path: pathlib.Path, out_path: pathlib.Path) -> None:
    x, energy = parse_neb_profile(dat_path)
    fig, ax = plt.subplots(figsize=(7, 4), dpi=170)
    ax.plot(x, energy, marker="o", color="#264653")
    ax.set_xlabel("Reaction coordinate")
    ax.set_ylabel("Energy (eV, relative)")
    ax.set_title("NEB mini-workflow profile")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_advanced_module_durations(rows: list[list[str]], out_path: pathlib.Path) -> None:
    if not rows:
        return
    labels = [row[0] for row in rows]
    durations = [float(row[2]) for row in rows]
    colors = ["#2a9d8f" if row[1] == "PASS" else "#e76f51" for row in rows]
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=170)
    bars = ax.bar(np.arange(len(labels)), durations, color=colors)
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_ylabel("Duration (s)")
    ax.set_title("Advanced module mini-workflow durations")
    ax.grid(axis="y", alpha=0.25)
    for bar, value in zip(bars, durations):
        ax.text(bar.get_x() + bar.get_width() / 2.0, value, f"{value:.2f}", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def run_advanced_workflows(
    *,
    qe_bin: pathlib.Path,
    inputs: dict[str, pathlib.Path],
    paths: dict[str, pathlib.Path],
    timeout_s: int,
    add_case: Callable[[str, str, float, str], None],
) -> dict[str, str]:
    work = paths["work"]
    logs = paths["logs"]
    data = paths["data"]
    plots = paths["plots"]

    advanced_rows: list[list[str]] = []
    metrics = {
        "hp_determine_num_pert_only": "NA",
        "neb_activation_energy_eV": "NA",
        "epw_interpolation_marker": "NO",
    }

    def add_adv(case: str, status: str, duration: float, note: str) -> None:
        add_case(case, status, duration, note)
        advanced_rows.append([case, status, f"{duration:.3f}", note])

    # HP mini-workflow (SCF + determine_num_pert_only)
    hp_scf_log = logs / "hp_scf.log"
    hp_log = logs / "hp_run.log"
    if not (qe_bin / "pw.x").exists() or not (qe_bin / "hp.x").exists():
        add_adv("hp_scf_hubbard", "FAIL", 0.0, "missing pw.x/hp.x")
        add_adv("hp_num_pert", "FAIL", 0.0, "skipped (missing pw.x/hp.x)")
    else:
        hp_scf_rc, hp_scf_dt = run_command(
            [str(qe_bin / "pw.x"), "-in", str(inputs["Si.hp.scf.in"])],
            cwd=work,
            log_path=hp_scf_log,
            timeout_s=timeout_s,
        )
        hp_scf_ok = hp_scf_rc == 0 and has_job_done(hp_scf_log)
        add_adv("hp_scf_hubbard", "PASS" if hp_scf_ok else "FAIL", hp_scf_dt, "prefix=sihp")

        if hp_scf_ok:
            hp_rc, hp_dt = run_command(
                [str(qe_bin / "hp.x"), "-in", str(inputs["Si.hp.in"])],
                cwd=work,
                log_path=hp_log,
                timeout_s=timeout_s,
            )
            hp_ok = hp_rc == 0 and has_job_done(hp_log)
            note = "determine_num_pert_only"
            add_adv("hp_num_pert", "PASS" if hp_ok else "FAIL", hp_dt, note)
            if hp_ok:
                metrics["hp_determine_num_pert_only"] = "PASS"
        else:
            add_adv("hp_num_pert", "FAIL", 0.0, "skipped (hp_scf_hubbard failed)")

    # NEB mini-workflow
    neb_log = logs / "neb_mini.log"
    if not (qe_bin / "neb.x").exists():
        add_adv("neb_path_mini", "FAIL", 0.0, "missing neb.x")
    else:
        neb_rc, neb_dt = run_command(
            [str(qe_bin / "neb.x"), "-in", str(inputs["Si.neb.in"])],
            cwd=work,
            log_path=neb_log,
            timeout_s=timeout_s,
        )
        neb_done = has_job_done(neb_log)
        neb_ok = neb_done and neb_rc in (0, 1)
        barrier = parse_neb_activation_ev(neb_log)
        note = f"barrier={barrier:.6f} eV" if barrier is not None else f"exit={neb_rc}"
        add_adv("neb_path_mini", "PASS" if neb_ok else "FAIL", neb_dt, note)
        if barrier is not None:
            metrics["neb_activation_energy_eV"] = f"{barrier:.6f}"

        for neb_artifact in ["sineb.dat", "sineb.int", "sineb.path"]:
            src = work / neb_artifact
            if src.exists():
                shutil.copy2(src, data / neb_artifact)
        if (work / "sineb.dat").exists():
            try:
                plot_neb_profile(work / "sineb.dat", plots / "neb_profile.png")
            except Exception:
                pass

    # EPW mini-workflow: SCF -> NSCF -> wannier90 -pp -> pw2wannier90 -> epw interpolation mode.
    epw_required = ["pw.x", "wannier90.x", "pw2wannier90.x", "epw.x"]
    if any(not (qe_bin / exe).exists() for exe in epw_required):
        missing = ",".join(exe for exe in epw_required if not (qe_bin / exe).exists())
        add_adv("epw_scf", "FAIL", 0.0, f"missing {missing}")
        add_adv("epw_nscf", "FAIL", 0.0, "skipped (missing EPW stack)")
        add_adv("epw_wannier90_pp", "FAIL", 0.0, "skipped (missing EPW stack)")
        add_adv("epw_pw2wannier90", "FAIL", 0.0, "skipped (missing EPW stack)")
        add_adv("epw_interp", "FAIL", 0.0, "skipped (missing EPW stack)")
    else:
        for stale in [
            "siepw.nnkp",
            "siepw.amn",
            "siepw.mmn",
            "siepw.eig",
            "siepw.wout",
            "EPW.bib",
        ]:
            (work / stale).unlink(missing_ok=True)
        shutil.rmtree(work / "tmp_epw", ignore_errors=True)
        shutil.copy2(inputs["siepw.win"], work / "siepw.win")

        epw_scf_log = logs / "epw_scf.log"
        epw_nscf_log = logs / "epw_nscf.log"
        epw_w90pp_log = logs / "epw_wannier90_pp.log"
        epw_pw2wan_log = logs / "epw_pw2wannier90.log"
        epw_interp_log = logs / "epw_interp.log"

        epw_scf_rc, epw_scf_dt = run_command(
            [str(qe_bin / "pw.x"), "-in", str(inputs["Si.epw.scf.in"])],
            cwd=work,
            log_path=epw_scf_log,
            timeout_s=timeout_s,
        )
        epw_scf_ok = epw_scf_rc == 0 and has_job_done(epw_scf_log)
        add_adv("epw_scf", "PASS" if epw_scf_ok else "FAIL", epw_scf_dt, "prefix=siepw")

        epw_nscf_ok = False
        if epw_scf_ok:
            epw_nscf_rc, epw_nscf_dt = run_command(
                [str(qe_bin / "pw.x"), "-in", str(inputs["Si.epw.nscf.in"])],
                cwd=work,
                log_path=epw_nscf_log,
                timeout_s=timeout_s,
            )
            epw_nscf_ok = epw_nscf_rc == 0 and has_job_done(epw_nscf_log)
            add_adv("epw_nscf", "PASS" if epw_nscf_ok else "FAIL", epw_nscf_dt, "8-point grid")
        else:
            add_adv("epw_nscf", "FAIL", 0.0, "skipped (epw_scf failed)")

        epw_w90_ok = False
        if epw_nscf_ok:
            epw_w90_rc, epw_w90_dt = run_command(
                [str(qe_bin / "wannier90.x"), "-pp", "siepw"],
                cwd=work,
                log_path=epw_w90pp_log,
                timeout_s=timeout_s,
            )
            epw_w90_ok = epw_w90_rc == 0 and (work / "siepw.nnkp").exists()
            add_adv("epw_wannier90_pp", "PASS" if epw_w90_ok else "FAIL", epw_w90_dt, "seed=siepw")
        else:
            add_adv("epw_wannier90_pp", "FAIL", 0.0, "skipped (epw_nscf failed)")

        epw_pw2wan_ok = False
        if epw_w90_ok:
            epw_pw2wan_rc, epw_pw2wan_dt = run_command(
                [str(qe_bin / "pw2wannier90.x"), "-in", str(inputs["Si.epw.pw2wan.in"])],
                cwd=work,
                log_path=epw_pw2wan_log,
                timeout_s=timeout_s,
            )
            epw_pw2wan_ok = epw_pw2wan_rc == 0 and has_job_done(epw_pw2wan_log)
            add_adv("epw_pw2wannier90", "PASS" if epw_pw2wan_ok else "FAIL", epw_pw2wan_dt, "AMN/MMN")
        else:
            add_adv("epw_pw2wannier90", "FAIL", 0.0, "skipped (epw_wannier90_pp failed)")

        if epw_pw2wan_ok:
            epw_interp_rc, epw_interp_dt = run_command(
                [str(qe_bin / "epw.x"), "-in", str(inputs["Si.epw.in"])],
                cwd=work,
                log_path=epw_interp_log,
                timeout_s=timeout_s,
            )
            epw_interp_ok = epw_interp_rc == 0 and has_epw_interpolation_marker(epw_interp_log)
            add_adv("epw_interp", "PASS" if epw_interp_ok else "FAIL", epw_interp_dt, "interpolation mode")
            metrics["epw_interpolation_marker"] = "YES" if epw_interp_ok else "NO"
        else:
            add_adv("epw_interp", "FAIL", 0.0, "skipped (epw_pw2wannier90 failed)")

        for epw_artifact in ["EPW.bib", "siepw.amn", "siepw.mmn", "siepw.eig", "siepw.wout"]:
            src = work / epw_artifact
            if src.exists():
                shutil.copy2(src, data / epw_artifact)

    write_tsv(
        paths["tables"] / "advanced_module_metrics.tsv",
        ["metric", "value"],
        [[key, value] for key, value in metrics.items()],
    )
    write_tsv(
        paths["tables"] / "advanced_module_cases.tsv",
        ["case", "status", "duration_s", "note"],
        advanced_rows,
    )
    plot_advanced_module_durations(advanced_rows, paths["plots"] / "advanced_module_durations.png")
    return metrics


def write_tsv(path: pathlib.Path, header: list[str], rows: Iterable[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)


def make_scf_variant(base_scf: pathlib.Path, *, prefix: str, outdir: str, dst: pathlib.Path) -> pathlib.Path:
    text = base_scf.read_text(encoding="utf-8")
    text = replace_prefix_and_outdir(text, prefix=prefix, outdir=outdir)
    text = replace_pseudo_dir(text)
    dst.write_text(text, encoding="utf-8")
    return dst


def run_wrapper(
    run_qe: pathlib.Path,
    qe_bin: pathlib.Path,
    exe_name: str,
    input_file: pathlib.Path,
    *,
    cwd: pathlib.Path,
    log_path: pathlib.Path,
    timeout_s: int,
    ranks: int,
) -> tuple[int, float]:
    env = os.environ.copy()
    env["QE_BIN_PATH"] = str(qe_bin)
    env["QE_RANKS"] = str(ranks)
    env["QE_BINDING"] = "--bind-to none"
    env["OMP_NUM_THREADS"] = "1"
    cmd = [str(run_qe), exe_name, "--", "-in", str(input_file)]
    rc, duration = run_command(cmd, cwd=cwd, log_path=log_path, env=env, timeout_s=timeout_s)
    if rc == 0:
        return rc, duration

    if has_mpi_socket_error(log_path):
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write("\n[validate_build] Wrapper MPI launch failed; retrying serial execution.\n")
        rc2, duration2 = run_command(
            [str(qe_bin / exe_name), "-in", str(input_file)],
            cwd=cwd,
            log_path=log_path,
            timeout_s=timeout_s,
            append=True,
        )
        return rc2, duration + duration2

    return rc, duration


def run_plot_script(script: pathlib.Path, base_dir: pathlib.Path, log_path: pathlib.Path) -> tuple[int, float]:
    mpl_cache = base_dir / ".mplconfig"
    mpl_cache.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.setdefault("MPLBACKEND", "Agg")
    env.setdefault("MPLCONFIGDIR", str(mpl_cache))
    cmd = [sys.executable, str(script), "--base", str(base_dir)]
    return run_command(cmd, cwd=ROOT, log_path=log_path, timeout_s=600, env=env)


def linkage_check(qe_bin: pathlib.Path, logs_dir: pathlib.Path) -> tuple[bool, str]:
    missing: list[str] = []
    for exe in sorted(qe_bin.glob("*.x")):
        proc = subprocess.run(["otool", "-L", str(exe)], capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            missing.append(f"{exe.name}: otool failed")
            continue
        for line in proc.stdout.splitlines()[1:]:
            if "not found" in line:
                missing.append(f"{exe.name}: {line.strip()}")
                break
    path = logs_dir / "linkage_check.log"
    lines = [f"Checked {len(list(qe_bin.glob('*.x')))} executables."]
    if missing:
        lines.append("Missing libraries:")
        lines.extend(missing)
    else:
        lines.append("No missing dynamic libraries detected.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return (not missing), path.name


def system_metadata() -> dict[str, str]:
    def safe_run(cmd: list[str]) -> str:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return proc.stdout.strip() if proc.returncode == 0 else "unavailable"

    return {
        "timestamp": dt.datetime.now().isoformat(timespec="seconds"),
        "python": sys.version.split()[0],
        "uname": safe_run(["uname", "-a"]),
        "sw_vers": safe_run(["sw_vers"]),
        "mpirun": safe_run(["mpirun", "--version"]).splitlines()[0] if safe_run(["mpirun", "--version"]) else "unavailable",
    }


def build_category_summary(cases: list[CaseResult]) -> dict[str, tuple[int, int]]:
    categories: dict[str, list[str]] = {
        "Core Workflow": [
            "pw_scf",
            "pw_bands",
            "bands_post",
            "pw_nscf",
            "dos",
            "projwfc",
            "pp_charge",
            "plot_bands",
            "plot_dos",
            "plot_pdos",
            "analyze_bandgap",
        ],
        "Phonon Chain": [
            "pw_scf_ph",
            "ph_gamma",
            "ph_grid",
            "q2r_ifc",
            "matdyn_gamma",
            "wrapper_ph",
        ],
        "Reproducibility": [c.case for c in cases if c.case.startswith("scf_rank_") or c.case.startswith("scf_repeat_")],
        "Wrapper/Linkage": [
            "linkage_qe_bins",
            "wrapper_pw",
        ],
        "Advanced Workflows": [
            "hp_scf_hubbard",
            "hp_num_pert",
            "neb_path_mini",
            "epw_scf",
            "epw_nscf",
            "epw_wannier90_pp",
            "epw_pw2wannier90",
            "epw_interp",
        ],
        "Optional Modules": [c.case for c in cases if c.case.startswith("module_")],
    }
    lookup = {c.case: c.status for c in cases}
    summary: dict[str, tuple[int, int]] = {}
    for category, names in categories.items():
        total = 0
        passed = 0
        for name in names:
            if name not in lookup:
                continue
            total += 1
            if lookup[name] == "PASS":
                passed += 1
        summary[category] = (passed, total)
    return summary


def plot_category_pass_fail(summary: dict[str, tuple[int, int]], out_path: pathlib.Path) -> None:
    categories = list(summary.keys())
    passed = [summary[c][0] for c in categories]
    failed = [summary[c][1] - summary[c][0] for c in categories]

    fig, ax = plt.subplots(figsize=(8, 4.5), dpi=170)
    y = np.arange(len(categories))
    ax.barh(y, passed, color="#2a9d8f", label="PASS")
    ax.barh(y, failed, left=passed, color="#e76f51", label="FAIL")
    for i, category in enumerate(categories):
        ax.text(
            summary[category][1] + 0.15,
            i,
            f"{summary[category][0]}/{summary[category][1]}",
            va="center",
            fontsize=9,
        )
    ax.set_yticks(y)
    ax.set_yticklabels(categories)
    ax.set_xlabel("Number of checks")
    ax.set_title("QE validation status by category")
    ax.legend(frameon=False, loc="lower right")
    ax.set_xlim(0, max((summary[c][1] for c in categories), default=1) + 2)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_rank_sweep(runs: list[ScfRun], out_path: pathlib.Path) -> None:
    runs = sorted(runs, key=lambda item: item.ranks)
    ranks = np.array([r.ranks for r in runs], dtype=float)
    energy = np.array([r.total_energy_ry for r in runs], dtype=float)
    fermi = np.array([r.fermi_ev for r in runs], dtype=float)
    runtime = np.array([r.duration_s for r in runs], dtype=float)
    energy_ref = np.median(energy)
    fermi_ref = np.median(fermi)

    fig, axes = plt.subplots(2, 1, figsize=(7, 6), dpi=170, sharex=True)
    axes[0].plot(ranks, runtime, marker="o", color="#264653")
    axes[0].set_ylabel("Wall time (s)")
    axes[0].set_title("SCF portability sweep across MPI ranks")
    axes[0].grid(alpha=0.25)

    axes[1].plot(ranks, (energy - energy_ref) * 1e6, marker="o", color="#e76f51", label="Energy delta (microRy)")
    axes[1].plot(ranks, (fermi - fermi_ref) * 1e3, marker="s", color="#2a9d8f", label="Fermi delta (meV)")
    axes[1].axhline(0.0, color="0.5", linestyle="--", linewidth=0.8)
    axes[1].set_xlabel("MPI ranks")
    axes[1].set_ylabel("Delta from median")
    axes[1].grid(alpha=0.25)
    axes[1].legend(frameon=False)

    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_repeatability(runs: list[ScfRun], out_path: pathlib.Path) -> None:
    x = np.arange(1, len(runs) + 1)
    energy = np.array([r.total_energy_ry for r in runs], dtype=float)
    fermi = np.array([r.fermi_ev for r in runs], dtype=float)
    e_mean = float(np.mean(energy))
    f_mean = float(np.mean(fermi))

    fig, axes = plt.subplots(2, 1, figsize=(7, 6), dpi=170, sharex=True)
    axes[0].plot(x, energy, marker="o", color="#1d3557")
    axes[0].axhline(e_mean, color="#457b9d", linestyle="--", linewidth=0.9, label="mean")
    axes[0].set_ylabel("Total energy (Ry)")
    axes[0].set_title("SCF repeatability (same machine, same input)")
    axes[0].grid(alpha=0.25)
    axes[0].legend(frameon=False)

    axes[1].plot(x, fermi, marker="o", color="#8d99ae")
    axes[1].axhline(f_mean, color="#457b9d", linestyle="--", linewidth=0.9, label="mean")
    axes[1].set_xlabel("Repeat index")
    axes[1].set_ylabel("Fermi level (eV)")
    axes[1].grid(alpha=0.25)
    axes[1].legend(frameon=False)

    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def plot_metric_deltas(metrics: list[tuple[str, float, float]], out_path: pathlib.Path) -> None:
    labels = [m[0] for m in metrics]
    deltas = []
    for name, ref, observed in metrics:
        delta = observed - ref
        if "energy" in name.lower():
            deltas.append(delta * 1e6)  # microRy
        else:
            deltas.append(delta * 1e3)  # meV

    fig, ax = plt.subplots(figsize=(8, 4), dpi=170)
    bars = ax.bar(np.arange(len(labels)), deltas, color="#577590")
    ax.axhline(0.0, color="0.45", linestyle="--", linewidth=0.8)
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(
        ["SCF E", "SCF Ef", "DOS Ef", "Indirect gap", "Direct gap"],
        rotation=15,
        ha="right",
    )
    ax.set_ylabel("Delta from reference (microRy for E, meV otherwise)")
    ax.set_title("Numerical drift vs reference metrics")
    for bar, value in zip(bars, deltas):
        ax.text(bar.get_x() + bar.get_width() / 2.0, value, f"{value:.3g}", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    fig.savefig(out_path)
    plt.close(fig)


def campaign(args: argparse.Namespace) -> int:
    qe_bin = detect_qe_bin(args.qe_bin)
    paths = prepare_dirs(args.out_dir.resolve())
    inputs = write_inputs(paths["input"])
    run_qe = ROOT / "scripts" / "run_qe.sh"

    cases: list[CaseResult] = []

    def add_case(name: str, status: str, duration_s: float, note: str) -> None:
        cases.append(CaseResult(case=name, status=status, duration_s=duration_s, note=note))

    # 1) Linkage health
    t0 = time.perf_counter()
    ok_linkage, linkage_note = linkage_check(qe_bin, paths["logs"])
    add_case("linkage_qe_bins", "PASS" if ok_linkage else "FAIL", time.perf_counter() - t0, linkage_note)

    # 2) Core workflow
    pipeline_steps = [
        ("pw_scf", "pw.x", "Si.scf.in", "pw_scf.log"),
        ("pw_bands", "pw.x", "Si.bands.in", "pw_bands.log"),
        ("bands_post", "bands.x", "Si.bands_post.in", "si_bands_post.txt"),
        ("pw_nscf", "pw.x", "Si.nscf.in", "pw_nscf.log"),
        ("dos", "dos.x", "Si.dos.in", "dos.log"),
        ("projwfc", "projwfc.x", "Si.projwfc.in", "projwfc.log"),
        ("pp_charge", "pp.x", "Si.pp.in", "pp_charge.log"),
        ("pw_scf_ph", "pw.x", "Si.scf_ph.in", "pw_scf_ph.log"),
        ("ph_gamma", "ph.x", "Si.ph.in", "ph_gamma.log"),
        ("ph_grid", "ph.x", "Si.ph_grid.in", "ph_grid.log"),
    ]

    pipeline_ok = True
    for case_name, exe_name, in_name, log_name in pipeline_steps:
        exe = qe_bin / exe_name
        log_path = paths["logs"] / log_name
        rc, duration = run_mpi_qe(
            exe,
            inputs[in_name],
            ranks=args.pipeline_ranks,
            cwd=paths["work"],
            log_path=log_path,
            timeout_s=args.timeout,
        )
        status = "PASS" if rc == 0 and has_job_done(log_path) else "FAIL"
        add_case(case_name, status, duration, f"ranks={args.pipeline_ranks}")
        if status == "FAIL":
            pipeline_ok = False

    # q2r and matdyn chain (serial invocation)
    for case_name, exe_name, in_name, log_name in [
        ("q2r_ifc", "q2r.x", "Si.q2r.in", "q2r.log"),
        ("matdyn_gamma", "matdyn.x", "Si.matdyn.in", "matdyn.log"),
    ]:
        exe = qe_bin / exe_name
        rc, duration = run_command(
            [str(exe)],
            cwd=paths["work"],
            log_path=paths["logs"] / log_name,
            timeout_s=args.timeout,
            stdin_text=inputs[in_name].read_text(encoding="utf-8"),
        )
        status = "PASS" if rc == 0 and has_job_done(paths["logs"] / log_name) else "FAIL"
        add_case(case_name, status, duration, "serial")
        if status == "FAIL":
            pipeline_ok = False

    # 3) Wrapper checks against installed QE bin path
    rc, duration = run_wrapper(
        run_qe,
        qe_bin,
        "pw.x",
        inputs["Si.scf.in"],
        cwd=paths["work"],
        log_path=paths["logs"] / "wrapper_pw.log",
        timeout_s=args.timeout,
        ranks=min(4, args.pipeline_ranks),
    )
    add_case("wrapper_pw", "PASS" if rc == 0 and has_job_done(paths["logs"] / "wrapper_pw.log") else "FAIL", duration, "run_qe.sh")

    rc, duration = run_wrapper(
        run_qe,
        qe_bin,
        "ph.x",
        inputs["Si.ph.in"],
        cwd=paths["work"],
        log_path=paths["logs"] / "wrapper_ph.log",
        timeout_s=args.timeout,
        ranks=min(4, args.pipeline_ranks),
    )
    add_case("wrapper_ph", "PASS" if rc == 0 and has_job_done(paths["logs"] / "wrapper_ph.log") else "FAIL", duration, "run_qe.sh")

    # 4) SCF rank sweep
    rank_sweep = [int(item.strip()) for item in args.rank_sweep.split(",") if item.strip()]
    rank_runs: list[ScfRun] = []
    for ranks in rank_sweep:
        variant = make_scf_variant(
            inputs["Si.scf.in"],
            prefix=f"silicon_r{ranks}",
            outdir=f"./tmp_r{ranks}",
            dst=paths["input"] / f"Si.scf.rank{ranks}.in",
        )
        log = paths["logs"] / f"scf_rank_{ranks}.log"
        rc, duration = run_mpi_qe(
            qe_bin / "pw.x",
            variant,
            ranks=ranks,
            cwd=paths["work"],
            log_path=log,
            timeout_s=args.timeout,
        )
        status = "PASS"
        note = "OK"
        total_energy = float("nan")
        fermi = float("nan")
        if rc != 0 or not has_job_done(log):
            status = "FAIL"
            note = "command failed"
        else:
            try:
                text = log.read_text(encoding="utf-8", errors="replace")
                total_energy = parse_total_energy(text)
                fermi = parse_fermi(text)
            except Exception as exc:  # pragma: no cover - defensive parsing
                status = "FAIL"
                note = f"parse failed: {exc}"
        add_case(f"scf_rank_{ranks}", status, duration, note)
        if status == "PASS":
            rank_runs.append(
                ScfRun(
                    label=f"rank_{ranks}",
                    ranks=ranks,
                    total_energy_ry=total_energy,
                    fermi_ev=fermi,
                    duration_s=duration,
                )
            )

    write_tsv(
        paths["tables"] / "scf_rank_sweep.tsv",
        ["label", "ranks", "total_energy_ry", "fermi_ev", "duration_s"],
        [
            [run.label, str(run.ranks), f"{run.total_energy_ry:.10f}", f"{run.fermi_ev:.6f}", f"{run.duration_s:.3f}"]
            for run in rank_runs
        ],
    )

    # 5) SCF repeatability (same ranks, same input)
    repeat_runs: list[ScfRun] = []
    repeat_rank = min(4, args.pipeline_ranks)
    for idx in range(1, args.repeat_count + 1):
        variant = make_scf_variant(
            inputs["Si.scf.in"],
            prefix=f"silicon_rep{idx}",
            outdir=f"./tmp_rep{idx}",
            dst=paths["input"] / f"Si.scf.repeat{idx}.in",
        )
        log = paths["logs"] / f"scf_repeat_{idx}.log"
        rc, duration = run_mpi_qe(
            qe_bin / "pw.x",
            variant,
            ranks=repeat_rank,
            cwd=paths["work"],
            log_path=log,
            timeout_s=args.timeout,
        )
        status = "PASS"
        note = "OK"
        total_energy = float("nan")
        fermi = float("nan")
        if rc != 0 or not has_job_done(log):
            status = "FAIL"
            note = "command failed"
        else:
            try:
                text = log.read_text(encoding="utf-8", errors="replace")
                total_energy = parse_total_energy(text)
                fermi = parse_fermi(text)
            except Exception as exc:  # pragma: no cover
                status = "FAIL"
                note = f"parse failed: {exc}"
        add_case(f"scf_repeat_{idx}", status, duration, note)
        if status == "PASS":
            repeat_runs.append(
                ScfRun(
                    label=f"repeat_{idx}",
                    ranks=repeat_rank,
                    total_energy_ry=total_energy,
                    fermi_ev=fermi,
                    duration_s=duration,
                )
            )

    write_tsv(
        paths["tables"] / "scf_repeatability.tsv",
        ["label", "ranks", "total_energy_ry", "fermi_ev", "duration_s"],
        [
            [run.label, str(run.ranks), f"{run.total_energy_ry:.10f}", f"{run.fermi_ev:.6f}", f"{run.duration_s:.3f}"]
            for run in repeat_runs
        ],
    )

    # 6) Module launch checks
    module_rows: list[list[str]] = []
    for module in MODULE_EXECUTABLES:
        exe = qe_bin / module
        log = paths["logs"] / f"module_{module}.log"
        if not exe.exists():
            add_case(f"module_{module[:-2]}_launch", "FAIL", 0.0, "missing executable")
            module_rows.append([module, "FAIL", "NA", "missing executable"])
            continue
        rc, duration = run_command(
            [str(exe)],
            cwd=paths["work"],
            log_path=log,
            timeout_s=30,
            stdin_text="\n",
        )
        text = log.read_text(encoding="utf-8", errors="replace")
        ok = ("Program" in text) and ("starts" in text)
        add_case(f"module_{module[:-2]}_launch", "PASS" if ok else "FAIL", duration, f"exit={rc}")
        module_rows.append([module, "PASS" if ok else "FAIL", str(rc), "launch banner detected" if ok else "no launch banner"])

    write_tsv(paths["tables"] / "module_launch_check.tsv", ["module", "status", "exit_code", "note"], module_rows)

    # 7) Deep mini-workflows for HP/NEB/EPW.
    advanced_metrics = run_advanced_workflows(
        qe_bin=qe_bin,
        inputs=inputs,
        paths=paths,
        timeout_s=args.timeout,
        add_case=add_case,
    )

    # 8) Gather primary outputs for analysis scripts
    output_files = [
        "silicon.bands.dat",
        "silicon.bands.dat.gnu",
        "silicon.bands.dat.rap",
        "silicon.dos",
        "silicon.pdos_tot",
        "silicon.pdos_atm#1(Si)_wfc#1(s)",
        "silicon.pdos_atm#1(Si)_wfc#2(p)",
        "silicon.pdos_atm#2(Si)_wfc#1(s)",
        "silicon.pdos_atm#2(Si)_wfc#2(p)",
        "silicon.rho",
        "silicon_rho.cube",
        "silicon_pdos.projwfc_up",
    ]
    for name in output_files:
        src = paths["work"] / name
        if src.exists():
            shutil.copy2(src, paths["data"] / name)

    # 9) Run plotting + band summary scripts if core workflow finished
    for case_name, script_name, log_name in [
        ("plot_bands", "plot_si_bands.py", "plot_bands.log"),
        ("plot_dos", "plot_si_dos.py", "plot_dos.log"),
        ("plot_pdos", "plot_si_pdos.py", "plot_pdos.log"),
        ("analyze_bandgap", "analyze_si_bandgap.py", "analyze.log"),
    ]:
        rc, duration = run_plot_script(COMMON_SCRIPTS / script_name, paths["root"], paths["logs"] / log_name)
        add_case(case_name, "PASS" if rc == 0 else "FAIL", duration, script_name)

    # 10) Numerical metrics table
    metrics_rows: list[tuple[str, float, float]] = []
    try:
        scf_text = (paths["logs"] / "pw_scf.log").read_text(encoding="utf-8", errors="replace")
        scf_energy = parse_total_energy(scf_text)
        scf_fermi = parse_fermi(scf_text)
        dos_fermi = parse_dos_fermi(paths["data"] / "silicon.dos")
        indirect_gap, direct_gap = compute_gaps(paths["data"] / "silicon.bands.dat.gnu", dos_fermi)
        observed = {
            "SCF total energy (Ry)": scf_energy,
            "SCF Fermi (eV)": scf_fermi,
            "DOS EFermi (eV)": dos_fermi,
            "Indirect gap (eV)": indirect_gap,
            "Direct gap (eV)": direct_gap,
        }
        for key, ref in REFERENCE_METRICS.items():
            metrics_rows.append((key, ref, observed[key]))

        write_tsv(
            paths["tables"] / "metrics_compare.tsv",
            ["metric", "reference", "observed", "delta(observed-reference)"],
            [[name, f"{ref:.10f}", f"{obs:.10f}", f"{(obs - ref):.10f}"] for name, ref, obs in metrics_rows],
        )
    except Exception as exc:  # pragma: no cover
        (paths["tables"] / "metrics_compare.tsv").write_text(
            f"metric\treference\tobserved\tdelta(observed-reference)\nERROR\tNA\tNA\t{exc}\n",
            encoding="utf-8",
        )

    # 11) Summary tables and plots
    write_tsv(
        paths["tables"] / "final_matrix.tsv",
        ["case", "status", "duration_s", "note"],
        [[c.case, c.status, f"{c.duration_s:.2f}", c.note] for c in cases],
    )

    category_summary = build_category_summary(cases)
    plot_category_pass_fail(category_summary, paths["plots"] / "category_pass_fail.png")
    if rank_runs:
        plot_rank_sweep(rank_runs, paths["plots"] / "scf_rank_sweep.png")
    if repeat_runs:
        plot_repeatability(repeat_runs, paths["plots"] / "scf_repeatability.png")
    if metrics_rows:
        plot_metric_deltas(list(metrics_rows), paths["plots"] / "metrics_delta.png")

    # 12) High-level report
    metadata = system_metadata()
    pass_count = sum(1 for c in cases if c.status == "PASS")
    fail_count = len(cases) - pass_count
    rank_energy_span = (
        max(r.total_energy_ry for r in rank_runs) - min(r.total_energy_ry for r in rank_runs)
        if rank_runs
        else float("nan")
    )
    rank_fermi_span = (
        max(r.fermi_ev for r in rank_runs) - min(r.fermi_ev for r in rank_runs)
        if rank_runs
        else float("nan")
    )
    rep_energy_std = statistics.pstdev([r.total_energy_ry for r in repeat_runs]) if len(repeat_runs) > 1 else float("nan")
    rep_fermi_std = statistics.pstdev([r.fermi_ev for r in repeat_runs]) if len(repeat_runs) > 1 else float("nan")

    report = [
        "# QE Build Validation Report",
        "",
        f"- Timestamp: {metadata['timestamp']}",
        f"- QE bin: `{qe_bin}`",
        f"- Output root: `{paths['root']}`",
        f"- System: `{metadata['uname']}`",
        f"- macOS: `{metadata['sw_vers']}`",
        f"- Python: `{metadata['python']}`",
        f"- MPI: `{metadata['mpirun']}`",
        "",
        "## Overall Status",
        "",
        f"- PASS: {pass_count}",
        f"- FAIL: {fail_count}",
        "",
        "## Reproducibility Highlights",
        "",
        f"- SCF rank sweep energy span: {rank_energy_span:.3e} Ry",
        f"- SCF rank sweep Fermi span: {rank_fermi_span:.3e} eV",
        f"- SCF repeatability sigma (energy): {rep_energy_std:.3e} Ry",
        f"- SCF repeatability sigma (Fermi): {rep_fermi_std:.3e} eV",
        "",
        "## Advanced Mini-Workflows",
        "",
        f"- HP determine_num_pert_only: {advanced_metrics['hp_determine_num_pert_only']}",
        f"- NEB activation energy (->): {advanced_metrics['neb_activation_energy_eV']} eV",
        f"- EPW interpolation marker found: {advanced_metrics['epw_interpolation_marker']}",
        "",
        "## Key Artifacts",
        "",
        "- Case matrix: `tables/final_matrix.tsv`",
        "- Rank sweep raw data: `tables/scf_rank_sweep.tsv`",
        "- Repeatability raw data: `tables/scf_repeatability.tsv`",
        "- Metrics comparison: `tables/metrics_compare.tsv`",
        "- Advanced module metrics: `tables/advanced_module_metrics.tsv`",
        "- Advanced module matrix: `tables/advanced_module_cases.tsv`",
        "- Module launch check: `tables/module_launch_check.tsv`",
        "- Category pass/fail plot: `plots/category_pass_fail.png`",
        "- Advanced module duration plot: `plots/advanced_module_durations.png`",
        "- NEB profile plot: `plots/neb_profile.png`",
        "- SCF portability sweep plot: `plots/scf_rank_sweep.png`",
        "- SCF repeatability plot: `plots/scf_repeatability.png`",
        "- Numerical drift plot: `plots/metrics_delta.png`",
        "- Physics plots: `plots/si_band_structure.png`, `plots/si_total_dos.png`, `plots/si_pdos.png`",
        "",
    ]
    (paths["root"] / "VALIDATION_REPORT.md").write_text("\n".join(report), encoding="utf-8")

    if not args.keep_work:
        shutil.rmtree(paths["work"], ignore_errors=True)

    return 0 if fail_count == 0 else 1


def main() -> int:
    args = parse_args()
    try:
        return campaign(args)
    except Exception as exc:  # pragma: no cover
        print(f"[validate_build] fatal error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
