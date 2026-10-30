#!/usr/bin/env python3
import argparse
from pathlib import Path
from qe_validation.analysis import compare_runs
p=argparse.ArgumentParser(description='Compare matching fresh datasets with fixed grid/physics/tolerance contracts')
p.add_argument('--manual',type=Path,required=True);p.add_argument('--pwtk',type=Path,required=True);p.add_argument('--out-dir',type=Path)
p.add_argument('--spectral-atol',type=float,default=1e-5);p.add_argument('--band-atol',type=float,default=1e-5);a=p.parse_args()
raise SystemExit(compare_runs(a.manual,a.pwtk,a.out_dir,a.spectral_atol,a.band_atol))
