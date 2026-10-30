#!/usr/bin/env python3
"""Independent energy/force and isotropic energy/stress consistency checks."""
import argparse
import json
from pathlib import Path
import re
import sys
from qe_validation.core import *
from qe_validation.convergence import scf_input

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--qe-bin',type=Path);p.add_argument('--out-dir',type=Path);p.add_argument('--ranks',type=int,default=2)
    a=p.parse_args();suite=select_suite(a.qe_bin);ranks=positive_int(a.ranks,'ranks')
    variants={'base':(0,0),**{f'displacement_{h}_{sign}':(sign*h,0) for h in [0.002,0.001] for sign in [-1,1]},**{f'strain_{h}_{sign}':(0,sign*h) for h in [0.001,0.0005] for sign in [-1,1]}}
    c=Campaign(a.out_dir,list(variants)+['force_consistency','stress_consistency'],suite,'finite-difference-physical-consistency')
    write_json(c.root/'physical-contract.json',{'variant_parameters':variants,'units':{'displacement':'Bohr','strain':'dimensionless isotropic lattice strain'},'force_atol_ry_bohr':1e-5,'pressure_atol_kbar':1.0,'cutoffs_ry':[80,800],'mesh':[12,12,12],'geometry':'FCC Si with second atom displaced by 0.01 alat in Cartesian x, creating a nonzero force','scope':'Derivative consistency for this numerical model; not agreement with experiment'})
    results={}
    try:
        for name,(dx,strain) in variants.items():
            text=scf_input(80,800,12)
            text=text.replace("calculation='scf'","calculation='scf', tprnfor=.true., tstress=.true.")
            alat=10.26*(1+strain)
            text=text.replace('celldm(1)=10.26',f'celldm(1)={alat:.12f}')
            text=text.replace('conv_thr=1.0d-8','conv_thr=1.0d-11')
            text=text.replace('ATOMIC_POSITIONS crystal\n Si 0.00 0.00 0.00\n Si 0.25 0.25 0.25',f'ATOMIC_POSITIONS alat\n Si 0.00 0.00 0.00\n Si {-0.24+dx/alat:.14f} 0.25 0.25')
            def validate(log,work):
                m=pw_metrics(log,ranks=ranks)
                m['force_x_ry_bohr']=last_number(log,rf'atom\s+2\s+type\s+1\s+force\s*=\s*({NUMBER})','atom-2 x force')
                m['pressure_kbar']=last_number(log,rf'total\s+stress.*?P=\s*({NUMBER})','pressure')
                return {'metrics':m}
            r=c.case(name,mpi_command(executable(suite,'pw.x'),['-in','{input}'],ranks),text=text,validator=validate,timeout=300,metadata={'displacement_bohr':dx,'isotropic_strain':strain})
            if r['state']=='PASS':results[name]=r['metrics']
        def forces(log,work):
            analytic=results['base']['force_x_ry_bohr'];fd=[]
            for h in [0.002,0.001]:
                fd.append(-(results[f'displacement_{h}_1']['total_energy_ry']-results[f'displacement_{h}_-1']['total_energy_ry'])/(2*h))
            if abs(analytic)<1e-4:raise ValidationError('TRIVIAL_FORCE_FIXTURE','Nontrivial displaced-atom force required')
            return {'metrics':{'analytic_ry_bohr':analytic,'finite_differences_ry_bohr':fd},'assertions':[scalar_assertion('force_derivative_'+str(i),v,analytic,1e-5,units='Ry/Bohr') for i,v in enumerate(fd)]+[scalar_assertion('force_step_refinement',fd[0],fd[1],1e-5,units='Ry/Bohr')]}
        def stresses(log,work):
            analytic=results['base']['pressure_kbar'];fd=[]
            volume=10.26**3/4
            for h in [0.001,0.0005]:
                diff=results[f'strain_{h}_1']['total_energy_ry']-results[f'strain_{h}_-1']['total_energy_ry']
                dvolume=volume*((1+h)**3-(1-h)**3)
                fd.append(-diff/dvolume*147105.078482)
            return {'metrics':{'analytic_kbar':analytic,'finite_differences_kbar':fd},'assertions':[scalar_assertion('pressure_derivative_'+str(i),v,analytic,1.0,units='kbar') for i,v in enumerate(fd)]+[scalar_assertion('pressure_step_refinement',fd[0],fd[1],1.0,units='kbar')]}
        complete=len(results)==len(variants)
        c.case('force_consistency',None,validator=forces,blocked='A finite-difference calculation failed' if not complete else None)
        c.case('stress_consistency',None,validator=stresses,blocked='A finite-difference calculation failed' if not complete else None)
    finally:rc=c.finish()
    return rc

if __name__=='__main__':raise SystemExit(main())
