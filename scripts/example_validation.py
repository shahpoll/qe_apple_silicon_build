#!/usr/bin/env python3
"""Version-matched converged NEB and XSpectra numerical example checks."""
import argparse
import json
from pathlib import Path
import re
import shutil
from qe_validation.core import *

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--qe-bin',type=Path);p.add_argument('--source',type=Path,required=True);p.add_argument('--out-dir',type=Path)
p.add_argument('--ranks',type=int,default=2);p.add_argument('--timeout',type=float,default=1200)
a=p.parse_args();suite=select_suite(a.qe_bin);ranks=positive_int(a.ranks,'ranks')
c=Campaign(a.out_dir,['neb_reference','xspectra_scf','xspectra_response'],suite,'upstream-neb-xspectra')
try:
 source=a.source.resolve()
 work=c.root/'work/neb';work.mkdir()
 script=source/'NEB/examples/example01/run_example';ref=source/'NEB/examples/example01/reference/H2+H.out'
 text=re.search(r'cat > H2\+H.in << EOF\n(.*?)\nEOF',script.read_text(),re.S).group(1)
 pp=source/'pseudo/HUSPBE.RRKJ3'
 text=text.replace('$TMP_DIR',str(work/'tmp')).replace('$PSEUDO_DIR',str(pp.parent))
 barrier=last_number(ref.read_text(),r'activation energy \(\-\>\)\s*=\s*('+NUMBER+r')','reference barrier')
 def neb(log,work):
  completion(log)
  if 'neb: convergence achieved' not in log:raise ValidationError('NEB_NOT_CONVERGED','Path convergence was not achieved')
  value=last_number(log,r'activation energy \(\-\>\)\s*=\s*('+NUMBER+r')','activation barrier')
  data=read_table(work/'H2+H.dat')
  if len(data)!=7:raise ValidationError('NEB_PROFILE_SHAPE','Seven-image profile required')
  return {'metrics':{'barrier_ev':value,'images':len(data),'path_threshold_eva':0.1},'assertions':[scalar_assertion('barrier_ev',value,barrier,0.02,units='eV')]}
 c.case('neb_reference',mpi_command(executable(suite,'neb.x'),['-inp','{input}'],ranks),text=text,cwd=work,validator=neb,timeout=a.timeout,metadata={'reference_sha256':sha256(ref),'input_source_sha256':sha256(script),'pseudopotential_sha256':sha256(pp),'rationale':'Independent upstream seven-image H2+H example, explicit 0.1 eV/Angstrom convergence; 0.02 eV regression barrier budget; no universal barrier accuracy claim'})
 work=c.root/'work/xspectra';work.mkdir()
 refdir=source/'XSpectra/examples/reference';ppdir=source/'XSpectra/examples/pseudo'
 shutil.copy2(refdir/'C.wfc',work/'C.wfc')
 def paths(text):
  text=re.sub(r"pseudo_dir\s*=\s*'[^']*'",f"pseudo_dir='{ppdir}'",text)
  return re.sub(r"outdir\s*=\s*'[^']*'",f"outdir='{work/'tmp'}'",text)
 ref_energy=last_number((refdir/'diamond.scf.out').read_text(),rf'^\s*!\s+total energy\s*=\s*({NUMBER})','reference XS ground energy')
 def scf(log,work):
  m=pw_metrics(log,ranks=ranks)
  return {'metrics':m,'assertions':[scalar_assertion('ground_energy_ry',m['total_energy_ry'],ref_energy,8e-4,1e-4,units='Ry/cell')]}
 result=c.case('xspectra_scf',mpi_command(executable(suite,'pw.x'),['-in','{input}'],ranks),text=paths((refdir/'diamond.scf.in').read_text()),cwd=work,validator=scf,timeout=a.timeout,metadata={'reference_sha256':sha256(refdir/'diamond.scf.out'),'input_sha256':sha256(refdir/'diamond.scf.in'),'pseudo_sha256':sha256(ppdir/'C_PBE_TM_2pj.UPF')})
 def xspectra(log,work):
  completion(log)
  observed=read_table(work/'xanes.dat');expected=read_table(refdir/'diamond.xspectra.dat')
  assertion=compare_arrays(observed,expected,atol=0.002,grid_atol=1e-7)
  return {'metrics':{'spectrum_rows':len(observed),'scope':'Fixed absorber, polarization, broadening and raw energy grid; no fitted shift or scale'},'assertions':[assertion]}
 c.case('xspectra_response',mpi_command(executable(suite,'xspectra.x'),['-in','{input}'],ranks),text=paths((refdir/'diamond.xspectra.in').read_text()),cwd=work,validator=xspectra,timeout=a.timeout,blocked='Ground state failed' if result['state']!='PASS' else None,metadata={'reference_sha256':sha256(refdir/'diamond.xspectra.dat'),'input_sha256':sha256(refdir/'diamond.xspectra.in'),'core_wavefunction_sha256':sha256(work/'C.wfc'),'absolute_spectrum_budget':0.002,'rationale':'Fixed upstream spectrum regression; convergence/model adequacy for another absorber remains a separate study'})
finally:rc=c.finish()
raise SystemExit(rc)
