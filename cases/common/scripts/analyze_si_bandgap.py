#!/usr/bin/env python3
import argparse,json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from qe_validation.analysis import band_summary
from qe_validation.core import ValidationError,write_json

def main(base=None):
    result=band_summary(base)
    write_json(base/'band-summary.json',result)
    print(json.dumps(result,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base',type=pathlib.Path,required=True);a=p.parse_args()
    try:main(a.base)
    except ValidationError as e:print(str(e),file=sys.stderr);raise SystemExit(2)
