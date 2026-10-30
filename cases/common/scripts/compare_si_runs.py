#!/usr/bin/env python3
import argparse,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from qe_validation.analysis import compare_runs
from qe_validation.core import ValidationError
if __name__=='__main__':
    p=argparse.ArgumentParser(description='Compare matching fresh datasets; no fitted normalization')
    p.add_argument('--manual',type=pathlib.Path,required=True);p.add_argument('--pwtk',type=pathlib.Path,required=True);p.add_argument('--out-dir',type=pathlib.Path)
    p.add_argument('--spectral-atol',type=float,default=1e-5);p.add_argument('--band-atol',type=float,default=1e-5);a=p.parse_args()
    try:raise SystemExit(compare_runs(a.manual,a.pwtk,a.out_dir,a.spectral_atol,a.band_atol))
    except ValidationError as e:print(str(e),file=sys.stderr);raise SystemExit(2)
