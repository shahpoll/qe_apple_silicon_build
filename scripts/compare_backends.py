#!/usr/bin/env python3
"""Compare frozen, successful core campaigns without fitting or changing references."""
import argparse,json
from pathlib import Path
from qe_validation.core import *
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--left',type=Path,required=True);p.add_argument('--right',type=Path,required=True);p.add_argument('--out-dir',type=Path,required=True);a=p.parse_args()
left=json.loads((a.left/'summary.json').read_text());right=json.loads((a.right/'summary.json').read_text())
c=Campaign(a.out_dir,['cross_backend'],profile='cross-backend-core-reference')
try:
 def compare(log,work):
  if left['state']!='PASS' or right['state']!='PASS':raise ValidationError('PREREQUISITE_FAILED','Both campaigns must be complete PASS','BLOCKED')
  l={r['case']:r for r in left['cases']};r={r['case']:r for r in right['cases']}
  if set(l)!=set(r):raise ValidationError('COVERAGE_MISMATCH','Backend case inventories differ','ERROR')
  assertions=[]
  budgets={'total_energy_ry':1e-7,'fermi_ev':1e-4,'integrated_charge_electrons':1e-5,'dos_fermi_ev':1e-4}
  for name in l:
   for key,budget in budgets.items():
    if key in l[name]['metrics']:
     assertions.append(scalar_assertion(name+'.'+key,r[name]['metrics'][key],l[name]['metrics'][key],budget))
   if 'frequencies_cm1' in l[name]['metrics']:
    x=l[name]['metrics']['frequencies_cm1'];y=r[name]['metrics']['frequencies_cm1']
    if len(x)!=len(y):raise ValidationError('ARTIFACT_SHAPE','Phonon dimensions differ','ERROR')
    assertions.extend(scalar_assertion(name+f'.mode[{i}]',v,u,0.01,units='cm^-1') for i,(u,v) in enumerate(zip(x,y)))
  if not assertions:raise ValidationError('METRIC_COVERAGE','No comparable numerical measurements','ERROR')
  return {'assertions':assertions,'metrics':{'compared_observables':len(assertions),'scope':'Same declared core fixtures on two build/backend configurations; independent upstream references remain separate'}}
 c.case('cross_backend',None,validator=compare,parents={str(a.left/'summary.json'):sha256(a.left/'summary.json'),str(a.right/'summary.json'):sha256(a.right/'summary.json')})
finally:rc=c.finish()
raise SystemExit(rc)
