#!/usr/bin/env python3
"""Exact-suite execution with isolated evidence; no automatic retries."""
import argparse
import json
import os
from pathlib import Path
import shlex
import sys
from qe_validation.core import ValidationError, executable, mpi_command, observed_ranks, positive_int, select_suite, safe_new_directory, run_process, write_json, runtime_env

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('executable')
    p.add_argument('args', nargs=argparse.REMAINDER)
    a=p.parse_args()
    args=a.args[1:] if a.args[:1]==['--'] else a.args
    try:
        if os.environ.get('QE_CPUSET'):
            raise ValidationError('CPUSET_UNSUPPORTED','QE_CPUSET is unsupported on this macOS profile; select explicit MPI binding with QE_BINDING','ERROR')
        suite=select_suite()
        exe=executable(suite,a.executable)
        ranks=positive_int(os.environ.get('QE_RANKS','2'),'QE_RANKS')
        command=mpi_command(exe,args,ranks,binding=shlex.split(os.environ.get('QE_BINDING','--bind-to none')))
        evidence=safe_new_directory(None, 'wrapper')
        write_json(evidence/'manifest.json',{'argv':command,'cwd':str(Path.cwd()),'requested_ranks':ranks,'suite':str(suite),'threads':{k:runtime_env()[k] for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','VECLIB_MAXIMUM_THREADS']}})
        result=run_process(command,Path.cwd(),evidence,float(os.environ.get('QE_TIMEOUT','1800')))
        text=(evidence/'stdout.log').read_text(errors='replace')
        sys.stdout.write(text)
        sys.stderr.write((evidence/'stderr.log').read_text(errors='replace'))
        if not result['reason']:
            actual=observed_ranks(text)
            if actual!=ranks:
                raise ValidationError('MPI_RANK_MISMATCH',f'Requested {ranks}, observed {actual}')
        result['state']='PASS' if not result['reason'] else 'FAIL'
        result['scope']='Execution and actual MPI ranks only; use a numerical campaign for scientific qualification'
        write_json(evidence/'result.json',result)
        print(f'[run_qe] Evidence: {evidence}',file=sys.stderr)
        return 0 if result['state']=='PASS' else 1
    except ValidationError as exc:
        if 'evidence' in locals():
            write_json(evidence/'result.json',{'state':exc.state,'reason':exc.reason,'detail':str(exc)})
        print(json.dumps({'state':exc.state,'reason':exc.reason,'detail':str(exc)}),file=sys.stderr)
        return 2

if __name__=='__main__':
    raise SystemExit(main())
