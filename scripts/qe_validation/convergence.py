"""Observable-specific silicon convergence, with joint and stronger-reference checks."""
import argparse
import json
from pathlib import Path
import re
import sys
from .core import *

RY_TO_EV=13.605693122994

def scf_input(cutoff,rho,mesh):
    text=(ROOT/'inputs/Si.scf.in').read_text()
    text=text.replace("pseudo_dir='../cases/common/pp'",f"pseudo_dir='{ROOT/'cases/common/pp'}'")
    text=re.sub(r'ecutwfc=\s*[\d.]+',f'ecutwfc={cutoff}',text)
    text=re.sub(r'ecutrho=\s*[\d.]+',f'ecutrho={rho}',text)
    return re.sub(r'(K_POINTS automatic\s*\n)\s*8 8 8',rf'\g<1>{mesh} {mesh} {mesh}',text)

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--qe-bin',type=Path)
    p.add_argument('--out-dir',type=Path)
    p.add_argument('--ranks',type=int,default=2)
    p.add_argument('--energy-target-mev-atom',type=float,default=1.0)
    p.add_argument('--gap-target-mev',type=float,default=1.0)
    p.add_argument('--candidate',default='50,400,12',help='Explicit new production variant: ecutwfc,Ry; ecutrho,Ry; k mesh')
    p.add_argument('--timeout',type=float,default=600)
    a=p.parse_args(argv)
    try:
        suite=select_suite(a.qe_bin);ranks=positive_int(a.ranks,'ranks')
        energy_target=finite(a.energy_target_mev_atom);gap_target=finite(a.gap_target_mev)
        if energy_target<=0 or gap_target<=0:raise ValidationError('CONFIG_TOLERANCE','Targets must be positive','ERROR')
        candidate=[positive_int(x,'candidate setting') for x in a.candidate.split(',')]
        if len(candidate)!=3:raise ValidationError('CONFIG_SETTINGS','Candidate needs three values','ERROR')
        variants={**{f'cutoff_{w}':(w,8*w,12) for w in [30,40,50,60,80]},**{f'rho_{rho}':(60,rho,12) for rho in [240,320,480,640,800]},**{f'kmesh_{k}':(60,800,k) for k in [4,6,8,10,12,14,16]},'candidate_joint':tuple(candidate),'reference_joint':(80,800,16),'reference_repeat':(80,800,16)}
        expected=[f'{v}_{stage}' for v in variants for stage in ['scf','bands','post']]+['stronger_reference_checks','candidate_accuracy']
        c=Campaign(a.out_dir,expected,suite,'silicon-observable-convergence')
        write_json(c.root/'convergence-contract.json',{'variants':variants,'energy_target_mev_atom':energy_target,'gap_target_mev':gap_target,'candidate':candidate,'pw_ranks':ranks,'postprocess_ranks':1,'rationale':'Default 1 meV targets define this study; historical 30/240/8 settings remain a regression fixture, not silently changed. Managed one-rank postprocessing is the explicit supported layout.','gap_scope':'path-sampled Kohn-Sham eigenvalue gap','reference_gate_fraction':0.5})
        measured={}
        try:
            for name,(w,rho,k) in variants.items():
                work=c.root/'work'/name;work.mkdir()
                text=scf_input(w,rho,k)
                scf=c.case(name+'_scf',mpi_command(executable(suite,'pw.x'),['-in','{input}'],ranks),text=text,cwd=work,timeout=a.timeout,validator=lambda log,work: {'metrics':pw_metrics(log,ranks=ranks,require_fermi=True)},metadata={'settings':[w,rho,k]})
                bands=(ROOT/'inputs/Si.bands.in').read_text().replace("pseudo_dir='../cases/common/pp'",f"pseudo_dir='{ROOT/'cases/common/pp'}'")
                bands=re.sub(r'ecutwfc=\s*[\d.]+',f'ecutwfc={w}',bands)
                bands=re.sub(r'ecutrho=\s*[\d.]+',f'ecutrho={rho}',bands)
                b=c.case(name+'_bands',mpi_command(executable(suite,'pw.x'),['-in','{input}'],ranks),text=bands,cwd=work,timeout=a.timeout,validator=lambda log,work:{'metrics':pw_metrics(log,calculation='bands',ranks=ranks)},blocked='SCF failed' if scf['state']!='PASS' else None)
                def post(log,work,scf=scf):
                    completion(log)
                    if observed_ranks(log)!=1:raise ValidationError('MPI_RANK_MISMATCH','Convergence postprocessing requires one managed rank')
                    _,energies=read_bands(work/'silicon.bands.dat.gnu')
                    indirect,direct=gaps(energies,scf['metrics']['fermi_ev'])
                    return {'metrics':{'total_energy_ry':scf['metrics']['total_energy_ry'],'path_gap_ev':indirect,'direct_path_gap_ev':direct}}
                record=c.case(name+'_post',mpi_command(executable(suite,'bands.x'),['-in','{input}'],1),text=(ROOT/'inputs/Si.bands_post.in').read_text(),cwd=work,timeout=a.timeout,validator=post,blocked='Band calculation failed' if b['state']!='PASS' else None,metadata={'requested_ranks':1,'scope':'Explicit managed one-rank postprocessing; no retry or rank substitution'})
                if record['state']=='PASS':measured[name]=record['metrics']
            def accuracy(log,work, pairs, fraction):
                assertions=[];metrics={}
                for left,right in pairs:
                    x,y=measured[left],measured[right]
                    e=(x['total_energy_ry']-y['total_energy_ry'])*RY_TO_EV*1000/2
                    g=(x['path_gap_ev']-y['path_gap_ev'])*1000
                    metrics[left+'_vs_'+right]={'energy_difference_mev_atom':e,'gap_difference_mev':g}
                    assertions += [scalar_assertion(left+' energy difference',e,0,energy_target*fraction,units='meV/atom'),scalar_assertion(left+' gap difference',g,0,gap_target*fraction,units='meV')]
                return {'metrics':metrics,'assertions':assertions}
            complete=len(measured)==len(variants)
            stronger=c.case('stronger_reference_checks',None,validator=lambda l,w:accuracy(l,w,[('cutoff_60','cutoff_80'),('rho_640','rho_800'),('kmesh_14','kmesh_16'),('reference_repeat','reference_joint')],0.5),blocked='One or more scan calculations failed' if not complete else None)
            c.case('candidate_accuracy',None,validator=lambda l,w:accuracy(l,w,[('candidate_joint','reference_joint')],1.0),blocked='Stronger reference not established' if stronger['state']!='PASS' else None)
            write_json(c.root/'convergence-results.json',{'contract_sha256':sha256(c.root/'convergence-contract.json'),'measurements':measured})
        finally:rc=c.finish()
        return rc
    except ValidationError as e:print(json.dumps({'state':e.state,'reason':e.reason,'detail':str(e)}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
