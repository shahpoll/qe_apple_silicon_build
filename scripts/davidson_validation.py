#!/usr/bin/env python3
"""CH4 Davidson response: converged residual and ten upstream transition energies."""
import argparse
import json
import sys
import hashlib
from pathlib import Path
import re
import shutil
from qe_validation.core import *
from qe_validation.upstream import species

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--qe-bin',type=Path);p.add_argument('--source',type=Path,required=True)
p.add_argument('--pseudo-cache',type=Path,required=True);p.add_argument('--out-dir',type=Path)
p.add_argument('--ranks',type=int,default=2);p.add_argument('--timeout',type=float,default=600)
a=p.parse_args();suite=select_suite(a.qe_bin);ranks=positive_int(a.ranks,'ranks')
c=Campaign(a.out_dir,['davidson_ground','davidson_response'],suite,'upstream-davidson-ch4')
try:
 ref=a.source.resolve()/'TDDFPT/examples/example08/reference'
 work=c.root/'work/ch4';work.mkdir();ppdir=work/'pseudo';ppdir.mkdir()
 expected_scf=(ref/'CH4.scf.out').read_text()
 md5={Path(name.strip()).name:digest for name,digest in re.findall(r'read from file:\s*\n([^\n]+)\s*\n\s*MD5 check sum:\s*([a-f0-9]{32})',expected_scf)}
 hashes={}
 for name in species((ref/'CH4.scf.in').read_text()):
  pp=a.pseudo_cache/name
  if not pp.is_file() or name not in md5 or hashlib.md5(pp.read_bytes()).hexdigest()!=md5[name]:
   raise ValidationError('PSEUDOPOTENTIAL_IDENTITY',name,'BLOCKED')
  shutil.copy2(pp,ppdir/name);hashes[name]=sha256(pp)
 def paths(text):
  text=re.sub(r"pseudo_dir\s*=\s*'[^']*'",f"pseudo_dir='{ppdir}'",text)
  return re.sub(r"outdir\s*=\s*'[^']*'",f"outdir='{work/'tmp'}'",text)
 energy=last_number(expected_scf,rf'^\s*!\s+total energy\s*=\s*({NUMBER})','ground reference')
 def ground(log,work):
  m=pw_metrics(log,ranks=ranks)
  return {'metrics':m,'assertions':[scalar_assertion('ground_energy',m['total_energy_ry'],energy,0.001,units='Ry/cell')]}
 r=c.case('davidson_ground',mpi_command(executable(suite,'pw.x'),['-in','{input}'],ranks),text=paths((ref/'CH4.scf.in').read_text()),cwd=work,validator=ground,timeout=a.timeout,metadata={'pseudopotentials':hashes,'reference_sha256':sha256(ref/'CH4.scf.out')})
 pattern=rf'The\s+\d+\s+-th eigen state\. The transition energy is:\s*({NUMBER})'
 expected=[finite(x) for x in re.findall(pattern,(ref/'CH4.tddfpt.out').read_text())]
 if len(expected)!=10:raise ValidationError('REFERENCE_COVERAGE','Ten transition energies required','ERROR')
 def response(log,work):
  completion(log)
  if observed_ranks(log)!=ranks:raise ValidationError('MPI_RANK_MISMATCH','Davidson actual rank count differs')
  residue=last_number(log,rf'Largest residue:\s*({NUMBER})','Davidson final residual')
  if residue>=1e-4:raise ValidationError('RESPONSE_NOT_CONVERGED','Davidson residual must be below the declared 1e-4 threshold')
  actual=[finite(x) for x in re.findall(pattern,log)]
  if len(actual)!=10:raise ValidationError('METRIC_COVERAGE','Ten transitions required','ERROR')
  return {'metrics':{'final_residual':residue,'transition_energies_ry':actual},'assertions':[scalar_assertion(f'transition[{i}]',x,y,0.001,units='Ry') for i,(x,y) in enumerate(zip(actual,expected))]}
 c.case('davidson_response',mpi_command(executable(suite,'turbo_davidson.x'),['-in','{input}'],ranks),text=paths((ref/'CH4.tddfpt.in').read_text()),cwd=work,validator=response,timeout=a.timeout,blocked='Ground state failed' if r['state']!='PASS' else None,metadata={'reference_sha256':sha256(ref/'CH4.tddfpt.out'),'transition_atol_ry':0.001,'rationale':'Fixed upstream CH4 example, ten energies, final residual below 1e-4; 1e-3 Ry regression budget. Model accuracy and convergence for other systems remain separate.'})
except ValidationError as error:
 print(json.dumps({'state':error.state,'reason':error.reason,'detail':str(error)}),file=sys.stderr)
 pending=next((name for name in c.expected if name not in c.records),None)
 if pending:
  def reject(log,work):raise error
  c.case(pending,None,validator=reject)
finally:rc=c.finish()
raise SystemExit(rc)
