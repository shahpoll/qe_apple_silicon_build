#!/usr/bin/env python3
"""Re-extract a preserved upstream attempt after a parser correction, without rewriting it."""
import argparse,json,shutil
from pathlib import Path
from qe_validation.core import *
from qe_validation.upstream import extract_metrics
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--attempt',type=Path,required=True);p.add_argument('--source',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True)
a=p.parse_args()
m=json.loads((a.attempt/'manifest.json').read_text());metadata=m['metadata'];entry=metadata['upstream'];old_work=Path(m['cwd'])
reference=old_work/entry['benchmark'];log_path=a.attempt/'stdout.log';stderr=a.attempt/'stderr.log'
c=Campaign(a.out_dir,['reextract'],profile='preserved-upstream-reextraction')
try:
 def validate(log,work):
  if sha256(reference)!=metadata['benchmark_sha256']:raise ValidationError('REFERENCE_DRIFT','Reference changed','ERROR')
  raw=log_path.read_text(errors='replace')+'\n'+stderr.read_text(errors='replace')
  completion(raw)
  filename='result.out.inp='+entry['input']+('.args='+entry['arg'] if entry['arg'] else '')
  (work/filename).write_text(log_path.read_text(errors='replace'))
  bench=work/entry['benchmark'];shutil.copy2(reference,bench)
  script=a.source/'test-suite'/('extract-'+entry['program'].lower()+'.sh')
  expected=extract_metrics(script,bench.name,work);actual=extract_metrics(script,filename,work)
  assertions=[]
  for key,values in expected.items():
   if key not in actual or len(actual[key])!=len(values):raise ValidationError('METRIC_COVERAGE',key,'ERROR')
   atol,rtol=metadata['tolerances'][key]
   assertions += [scalar_assertion(key+f'[{i}]',x,y,atol,rtol) for i,(x,y) in enumerate(zip(actual[key],values))]
  return {'metrics':actual,'assertions':assertions}
 c.case('reextract',None,validator=validate,parents={str(log_path):sha256(log_path),str(stderr):sha256(stderr),str(reference):sha256(reference)},metadata={'original_attempt':str(a.attempt),'purpose':'Parser correction; original terminal record remains unchanged'})
finally:rc=c.finish()
raise SystemExit(rc)
