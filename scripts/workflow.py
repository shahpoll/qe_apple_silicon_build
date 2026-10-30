#!/usr/bin/env python3
"""Fresh canonical silicon workflow through manual QE or PWTK."""
import argparse
import json
from pathlib import Path
import sys
from qe_validation.core import Campaign, ValidationError, select_suite, positive_int
from qe_validation.campaign import core_workflow

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--qe-bin',type=Path)
    p.add_argument('--out-dir',type=Path)
    p.add_argument('--ranks',type=int,default=2)
    p.add_argument('--timeout',type=float,default=600)
    p.add_argument('--engine',choices=['manual','pwtk'],default='manual')
    p.add_argument('--pwtk',type=Path)
    p.add_argument('--tclsh',default='tclsh')
    a=p.parse_args()
    try:
        suite=select_suite(a.qe_bin);ranks=positive_int(a.ranks,'ranks')
        expected=['pw_scf','pw_bands','bands_post','pw_nscf','dos','projwfc','pp_charge','pw_scf_ph','ph_gamma','ph_grid','q2r_ifc','matdyn_gamma']
        c=Campaign(a.out_dir,expected,suite,'silicon-'+a.engine)
        try:core_workflow(c,suite,ranks,a.timeout,engine=a.engine,pwtk=a.pwtk,tclsh=a.tclsh)
        finally:rc=c.finish()
        return rc
    except ValidationError as e:
        print(json.dumps({'state':e.state,'reason':e.reason,'detail':str(e)}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
