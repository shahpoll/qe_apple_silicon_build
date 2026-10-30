"""Frozen silicon core workflow and rank/repeat checks with explicit claim scope."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from .core import *
from .inputs import write_inputs
from .linkage import inspect_binary


def seed_spec() -> tuple[str, dict]:
    spec=json.loads((ROOT/'profiles/upstream-seed.json').read_text())
    base=ROOT/Path(spec['input']).parent
    for name,digest in spec['hashes'].items():
        if sha256(base/name)!=digest:
            raise ValidationError('FIXTURE_IDENTITY',f'Upstream fixture changed: {name}','ERROR')
    text=(ROOT/spec['input']).read_text().replace('&control',f"&control\n pseudo_dir='{base}', outdir='./tmp', prefix='seed',")
    return text,spec


def seed_validator(spec, ranks):
    def validate(log,work):
        metrics=pw_metrics(log,ranks=ranks)
        assertions=[scalar_assertion(k,metrics[k],v['value'],v['atol'],v.get('rtol',0),v['units']) for k,v in spec['metrics'].items()]
        return {'metrics':metrics,'assertions':assertions}
    return validate


def cube_electrons(path: Path) -> float:
    lines=path.read_text().splitlines()
    nat=abs(int(lines[2].split()[0]))
    axes=[[finite(x) for x in lines[i].split()[1:4]] for i in range(3,6)]
    dimensions=[int(lines[i].split()[0]) for i in range(3,6)]
    if any(n<=0 for n in dimensions):
        raise ValidationError('CUBE_UNITS','Positive Bohr grid dimensions required')
    a,b,c=axes
    volume=abs(a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]))
    values=[finite(x) for line in lines[6+nat:] for x in line.split()]
    if len(values)!=math.prod(dimensions):
        raise ValidationError('ARTIFACT_SHAPE','Cube grid/data dimensions differ')
    return math.fsum(values)*volume


def core_workflow(campaign: Campaign, suite: Path, ranks: int, timeout: float, *, prefix: str = 'silicon', engine: str = 'manual', pwtk: Path | None = None, tclsh: str | None = None) -> dict:
    contract=json.loads((ROOT/'profiles/silicon-workflow.json').read_text())
    for rel,digest in contract['files'].items():
        if sha256(ROOT/rel)!=digest:
            raise ValidationError('FIXTURE_IDENTITY','Canonical workflow changed without a new case contract: '+rel,'ERROR')
    work=campaign.root/'work'/prefix;work.mkdir()
    inp=campaign.root/'inputs';inp.mkdir(exist_ok=True)
    inputs=write_inputs(inp)
    ids=['pw_scf','pw_bands','bands_post','pw_nscf','dos','projwfc','pp_charge','pw_scf_ph','ph_gamma','ph_grid','q2r_ifc','matdyn_gamma']
    dependencies={'pw_bands':['pw_scf'],'bands_post':['pw_bands'],'pw_nscf':['pw_scf'],'dos':['pw_nscf'], 'projwfc':['pw_nscf'],'pp_charge':['pw_nscf'],'ph_gamma':['pw_scf_ph'],'ph_grid':['pw_scf_ph'],'q2r_ifc':['ph_grid'],'matdyn_gamma':['q2r_ifc']}
    descriptors=[('pw_scf','pw.x','Si.scf.in','scf'),('pw_bands','pw.x','Si.bands.in','bands'),('bands_post','bands.x','Si.bands_post.in',None),('pw_nscf','pw.x','Si.nscf.in','nscf'),('dos','dos.x','Si.dos.in',None),('projwfc','projwfc.x','Si.projwfc.in',None),('pp_charge','pp.x','Si.pp.in',None),('pw_scf_ph','pw.x','Si.scf_ph.in','scf'),('ph_gamma','ph.x','Si.ph.in',None),('ph_grid','ph.x','Si.ph_grid.in',None),('q2r_ifc','q2r.x','Si.q2r.in',None),('matdyn_gamma','matdyn.x','Si.matdyn.in',None)]
    history={}
    spec=json.loads((ROOT/'profiles/silicon-smoke.json').read_text())
    for cid,name,input_name,calc in descriptors:
        failed=[x for x in dependencies.get(cid,[]) if history[x]['state']!='PASS']
        parents={}
        error=None
        try:
            if not failed and cid in ('pw_bands','pw_nscf'):
                parents=saved_parent(work,'silicon')
            if not failed and cid in ('dos','projwfc','pp_charge'):
                parents=saved_parent(work,'silicon','nscf')
                doc=ET.parse(next(iter(parents)))
                if int(doc.findtext('.//output/band_structure/nbnd'))!=36:
                    raise ValidationError('BAND_COVERAGE','NSCF parent must have 36 bands','BLOCKED')
        except ValidationError as exc:error=str(exc)
        def validate(log,work,cid=cid,calc=calc):
            metrics={};assertions=[]
            if calc:
                metrics=pw_metrics(log,calculation=calc,ranks=ranks,require_fermi=cid=='pw_scf')
                if cid=='pw_scf':
                    assertions=[scalar_assertion(k,metrics[k],v['value'],v['atol'],units=v['units']) for k,v in spec['metrics'].items()]
            else:
                completion(log)
                expected_ranks=ranks if cid in ('ph_gamma','ph_grid') else 1
                if cid in ('bands_post','dos','projwfc','ph_gamma','ph_grid') and observed_ranks(log)!=expected_ranks:
                    raise ValidationError('MPI_RANK_MISMATCH','Postprocessor used wrong ranks')
            if cid=='bands_post':
                grid,bands=read_bands(work/'silicon.bands.dat.gnu')
                metrics.update(bands=len(bands),kpoints=len(grid))
            if cid=='dos':
                rows=read_table(work/'silicon.dos')
                if any(b[0]<=a[0] for a,b in zip(rows,rows[1:])):raise ValidationError('GRID_MISMATCH','DOS energy grid not increasing')
                fermi=last_number((work/'silicon.dos').read_text(),rf'EFermi\s*=\s*({NUMBER})','DOS EFermi')
                metrics.update(dos_rows=len(rows),dos_fermi_ev=fermi)
                assertions.append(scalar_assertion('dos_fermi',fermi,6.2130,0.005,units='eV'))
            if cid=='projwfc':
                rows=read_table(work/'silicon.pdos_tot')
                metrics['pdos_rows']=len(rows)
            if cid=='pp_charge':
                metrics['integrated_charge_electrons']=cube_electrons(work/'silicon_rho.cube')
                assertions.append(scalar_assertion('integrated_charge_electrons',metrics['integrated_charge_electrons'],8,0.005,units='electrons/cell'))
            if cid.startswith('ph_'):
                frequencies=[finite(x) for x in re.findall(r'freq\s*\(\s*\d+\)\s*=.*?=\s*('+NUMBER+r')\s*\[cm-1\]',log)]
                if not frequencies:raise ValidationError('METRIC_MISSING','Phonon frequencies missing','ERROR')
                metrics['frequencies_cm1']=frequencies
                metrics['coverage']='finite requested mode output; upstream reference family supplies numerical regression'
            if cid=='q2r_ifc' and not (work/'silicon.fc').is_file():raise ValidationError('ARTIFACT_MISSING','Force constants absent','ERROR')
            if cid=='matdyn_gamma':
                file=work/'silicon.freq'
                if not file.is_file():raise ValidationError('ARTIFACT_MISSING','matdyn frequencies absent','ERROR')
                vals=[finite(x) for x in re.findall(NUMBER,file.read_text())]
                if not vals:raise ValidationError('ARTIFACT_SHAPE','Empty matdyn frequencies','ERROR')
                metrics['frequency_artifact_sha256']=sha256(file)
            return {'metrics':metrics,'assertions':assertions}
        try:
            exe=executable(suite,name)
            serial=name not in ('pw.x','ph.x')
            text=inputs[input_name].read_text()
            # Use a managed one-rank MPI launch for single-process stages.
            # On this device MPI singleton initialization itself sets the
            # overflow flag; the isolated no-arithmetic probe documents it.
            command=mpi_command(exe,['-in','{input}'],1 if serial else ranks)
            validator=validate
            if engine=='pwtk' and cid in ('pw_scf','pw_bands','bands_post','pw_nscf','dos','projwfc'):
                if not pwtk or not pwtk.is_file() or not tclsh:
                    raise ValidationError('PWTK_MISSING','Select --pwtk and --tclsh','BLOCKED')
                # Generate both engines from the exact same canonical QE input.
                loader,runner={'pw.x':('pwi::load_fromPWI','runPW'),'bands.x':('bi::load_fromBI','runBANDS'),'dos.x':('di::load_fromDI','runDOS'),'projwfc.x':('pri::load_fromPRI','runPROJWFC')}[name]
                quote=lambda s:'"'+str(s).replace('\\','\\\\').replace('"','\\"').replace('$','\\$').replace('[','\\[').replace(']','\\]')+'"'
                input_path=campaign.root/'cases'/cid/'attempt-001/input.in'
                launcher=command[0]
                script=work/(cid+'.pwtk')
                script.write_text(f'::pwtk::bin_dir {quote(suite)}\n::pwtk::prefix {quote(launcher)} -np {1 if serial else ranks} --bind-to none\n::pwtk::{loader} {quote(input_path)}\n::pwtk::{runner} {cid}\n')
                command=[str(tclsh),str(pwtk),str(script)]
                def pwtk_validate(log,work,validate=validate,cid=cid):
                    raw=work/(cid+'.out')
                    if not raw.is_file():raise ValidationError('ARTIFACT_MISSING','PWTK did not produce the declared QE output','ERROR')
                    if re.search(r'IEEE_INVALID_FLAG|IEEE_DIVIDE_BY_ZERO|IEEE_OVERFLOW_FLAG',log):
                        raise ValidationError('FLOATING_POINT_EXCEPTION','Severe floating-point flag in PWTK launcher output')
                    return validate(raw.read_text(errors='replace'),work)
                validator=pwtk_validate
            history[cid]=campaign.case(cid,command,text=text,cwd=work,validator=validator,timeout=timeout,parents=parents,blocked='Failed prerequisites: '+','.join(failed) if failed else error, metadata={'requested_ranks':1 if serial else ranks,'input_origin':input_name,'engine':engine,'qe_executable':str(exe),'qe_executable_sha256':sha256(exe)})
        except ValidationError as exc:
            history[cid]=campaign.case(cid,None,blocked=str(exc))
    artifacts=tree_manifest(work)
    write_json(campaign.root/'workflow-artifacts.json',{'work':str(work),'artifacts':artifacts,'history':{k:v['state'] for k,v in history.items()},'ancestry':'SCF -> bands -> bands post; SCF -> uniform NSCF -> DOS/PDOS'})
    if all(v['state']=='PASS' for v in history.values()):
        data=campaign.root/'data';data.mkdir()
        for file in work.iterdir():
            if file.is_file() and file.name.startswith('silicon.') and file.suffix not in ('.xml',):
                shutil.copy2(file,data/file.name)
        shutil.copy2(work/'silicon_rho.cube',data/'silicon_rho.cube')
        logs=campaign.root/'logs';logs.mkdir()
        band_log=work/'bands_post.out' if engine=='pwtk' else campaign.root/'cases/bands_post/attempt-001/stdout.log'
        shutil.copy2(band_log,logs/'si_bands_post.txt')
        write_json(campaign.root/'dataset.json',{'schema':1,'state':'PASS','engine':engine,'artifacts':tree_manifest(data),'settings':{'scf_mesh':[8,8,8],'nscf_mesh':[12,12,12],'nbnd':36,'ecutwfc_ry':30,'ecutrho_ry':240,'dos_degauss_ry':0.001470,'pdos_degauss_ry':0.02,'pseudopotential_sha256':sha256(ROOT/'cases/common/pp/Si.pbe-n-rrkjus_psl.1.0.0.UPF')},'case_evidence':{k:v['evidence'] for k,v in history.items()},'sampling':'high-symmetry-path bands; uniform NSCF DOS/PDOS'})
    return history


def campaign(args) -> int:
    suite=select_suite(args.qe_bin)
    ranks=parse_ranks(args.rank_sweep)
    if args.profile=='core' and not {1,2,4}.issubset(ranks):
        raise ValidationError('COVERAGE_RANKS','Core qualification requires distinct actual ranks 1, 2, and 4','ERROR')
    if args.repeat_count<3:raise ValidationError('COVERAGE_REPEATS','At least three independent repetitions are required','ERROR')
    pipeline=positive_int(args.pipeline_ranks,'pipeline ranks')
    expected=['linkage','upstream_seed']
    expected += ['pw_scf','pw_bands','bands_post','pw_nscf','dos','projwfc','pp_charge','pw_scf_ph','ph_gamma','ph_grid','q2r_ifc','matdyn_gamma'] if args.profile=='core' else []
    expected += [f'scf_rank_{r}' for r in ranks]+[f'scf_repeat_{i}' for i in range(args.repeat_count)]+['reference_and_peer_agreement']
    c=Campaign(args.out_dir,expected,suite,args.profile)
    try:
        required=['pw.x']+(['ph.x','bands.x','dos.x','projwfc.x','pp.x','q2r.x','matdyn.x'] if args.profile=='core' else [])
        def linkage(log,work):
            manifest={name:inspect_binary(executable(suite,name)) for name in required}
            write_json(work/'suite-manifest.json',manifest)
            return {'metrics':{'executables_inspected':len(manifest),'scope':'dependency resolution; calculation cases perform actual loader/numerical tests'}}
        c.case('linkage',None,validator=linkage)
        text,spec=seed_spec()
        c.case('upstream_seed',mpi_command(executable(suite,'pw.x'),['-in','{input}'],pipeline),text=text,validator=seed_validator(spec,pipeline),timeout=args.timeout,metadata={'reference':spec})
        if args.profile=='core':core_workflow(c,suite,pipeline,args.timeout)
        smoke=json.loads((ROOT/'profiles/silicon-smoke.json').read_text())
        pp=ROOT/smoke['pseudopotential']
        inp=ROOT/smoke['input']
        if sha256(inp)!=smoke['input_sha256'] or sha256(pp)!=smoke['pseudopotential_sha256']:
            raise ValidationError('FIXTURE_IDENTITY','Silicon reproducibility input/UPF changed','ERROR')
        text=inp.read_text().replace("pseudo_dir='../cases/common/pp'",f"pseudo_dir='{pp.parent}'")
        cases=[]
        for cid,r in [(f'scf_rank_{r}',r) for r in ranks]+[(f'scf_repeat_{i}',pipeline) for i in range(args.repeat_count)]:
            def validate(log,work,r=r):
                m=pw_metrics(log,ranks=r,require_fermi=True)
                return {'metrics':m,'assertions':[scalar_assertion(k,m[k],v['value'],v['atol'],units=v['units']) for k,v in smoke['metrics'].items()]}
            cases.append(c.case(cid,mpi_command(executable(suite,'pw.x'),['-in','{input}'],r),text=text,validator=validate,timeout=args.timeout,metadata={'requested_ranks':r,'reference_sha256':sha256(ROOT/'profiles/silicon-smoke.json')}))
        def agreement(log,work):
            assertions=[];metrics={}
            for key,limit in smoke['peer_limits'].items():
                vals=[r['metrics'][key] for r in cases]
                span=max(vals)-min(vals);metrics[key+'_span']=span
                assertions.append(scalar_assertion(key+'_span',span,0,limit))
            return {'metrics':metrics,'assertions':assertions}
        c.case('reference_and_peer_agreement',None,validator=agreement,blocked='A required rank/repeat case failed' if any(r['state']!='PASS' for r in cases) else None)
    finally:
        result=c.finish()
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description='Strict reference/rank/repeat and silicon core validation; advanced modules use explicit upstream contracts')
    p.add_argument('--qe-bin',type=Path)
    p.add_argument('--out-dir',type=Path)
    p.add_argument('--profile',choices=['smoke','core'],default='core')
    p.add_argument('--rank-sweep',default='1,2,4')
    p.add_argument('--pipeline-ranks',type=int,default=2)
    p.add_argument('--repeat-count',type=int,default=3)
    p.add_argument('--timeout',type=float,default=600)
    p.add_argument('--keep-work',action='store_true',help='Compatibility flag: all work/evidence is always retained')
    args=p.parse_args(argv)
    try:return campaign(args)
    except ValidationError as exc:
        print(json.dumps({'state':exc.state,'reason':exc.reason,'detail':str(exc)}),file=sys.stderr);return 2
    except Exception as exc:
        print(json.dumps({'state':'ERROR','reason':'HARNESS_ERROR','detail':repr(exc)}),file=sys.stderr);return 2
