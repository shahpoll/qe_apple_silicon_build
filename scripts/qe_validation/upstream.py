"""Version-pinned upstream numerical cases with preserved raw and extracted data."""
from __future__ import annotations
import argparse
import ast
import configparser
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from .core import *

FAMILIES={
 'pw_scf':['scf.in','scf-gamma.in'], 'pw_uspp':['uspp.in'], 'pw_pawatom':['paw-atom.in'],
 'pw_metal':['metal.in'], 'pw_lsda':['lsda.in'], 'pw_noncolin':['noncolin.in'],
 'pw_spinorbit':['spinorbit.in'], 'pw_lda+U':['lda+U.in'], 'pw_hse':['hse-si111.in'],
 'pw_metaGGA':['metaGGA-1.in'], 'pw_vdw':['vdw-d2.in'], 'pw_relax':['relax.in'],
 'pw_vc-relax':['vc-relax1.in'], 'pw_cluster':['cluster1.in'], 'pw_dipole':['dipole.in'],
 'ph_base':['c.scf.in','c.phG.in','si.scf.in','si.phG.in','si.phX.in'],
 'ph_metal':['al.scf.fit.in','al.scf.in','al.elph.in','al.elph.notrans.in','q2r.in','matdyn.in.freq','matdyn.in.dos','lambda.in'],
 'cp_si':['si-vbc-lda-1.in','si-vbc-lda-2.in','si-vbc-lda-3.in'],
 'hp_insulator_us':['LiCoO2.scf.in','LiCoO2.hp.in'],
 'epw_base':['scf.in','ph.in','scf_epw.in','nscf_epw.in','epw1.in'],
 'tddfpt_CH4':['CH4.pw.in','CH4.tddfpt.in','CH4.tddfpt_pp.in'],
 'tddfpt_eels-si':['Si.pw.in','Si.tddfpt-eels.in','Si.tddfpt_pp_eels.in'],
 'tddfpt_magnons_fe':['Fe.pw.in','Fe.tddfpt-magnons.in','Fe.tddfpt_pp_magnons.in'],
 'QEHeat_h2o':['all_currents.in','all_currents_2pt.in'],
}

def species(text):
    found=[];active=False
    for line in text.splitlines():
        if re.match(r'\s*ATOMIC_SPECIES',line,re.I):active=True;continue
        if active:
            parts=line.split()
            if not parts or line.lstrip().startswith(('!','#')):continue
            if len(parts)>=3:
                try:float(parts[1])
                except ValueError:break
                found.append(parts[2].strip("'\""))
            else:break
    return found

def extract_metrics(script: Path, filename: str, cwd: Path) -> dict[str,list[float]]:
    proc=subprocess.run(['bash',str(script),filename],cwd=cwd,capture_output=True,text=True,timeout=30)
    if proc.returncode:raise ValidationError('UPSTREAM_EXTRACT_FAILED',proc.stderr,'ERROR')
    values={};key=None;headers=None
    for line in proc.stdout.splitlines():
        line=line.strip()
        if not line:continue
        parts=line.split()
        if len(parts)>1 and all(re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*',x) for x in parts):
            headers=parts
            for key_name in headers:values.setdefault(key_name,[])
        elif headers:
            if len(parts)!=len(headers):raise ValidationError('METRIC_SHAPE','Upstream table header/data columns differ','ERROR')
            for key_name,value in zip(headers,parts):values[key_name].append(finite(value,key_name))
        elif re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*',line):key=line;values.setdefault(key,[])
        elif key:values[key].extend(finite(x,key) for x in parts)
    values={k:v for k,v in values.items() if v}
    if not values:raise ValidationError('METRICS_EMPTY','Upstream extractor produced no numerical values','ERROR')
    return values

def program_name(program: str,arg: str,input_name: str) -> str:
    code=int(arg) if arg else 1
    if program=='PW':return 'pw.x'
    if program=='CP':return 'cp.x'
    if program=='PH':return {1:'pw.x',2:'ph.x',3:'q2r.x',4:'matdyn.x',5:'lambda.x',8:'matdyn.x',9:'dynmat.x',11:'ph.x'}[code]
    if program=='HP':return 'pw.x' if code in (1,2) else 'hp.x'
    if program=='EPW':return {0:'pw.x',1:'pw.x',2:'ph.x',3:'epw.x',4:'q2r.x'}[code]
    if program=='TDDFPT':return {1:'pw.x',2:'turbo_lanczos.x',3:'turbo_spectrum.x',4:'turbo_spectrum.x',5:'turbo_eels.x',6:'turbo_magnon.x',7:'turbo_spectrum.x'}[code]
    if program=='ALL_CURRENTS' or program.startswith('QEHeat_'):return 'all_currents.x'
    raise ValidationError('UPSTREAM_PROGRAM_UNSUPPORTED',program,'BLOCKED')

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--qe-bin',type=Path)
    p.add_argument('--source',type=Path,required=True,help='Authenticated QE 7.5 source directory')
    p.add_argument('--out-dir',type=Path)
    p.add_argument('--families',default=','.join(FAMILIES))
    p.add_argument('--pseudo-cache',type=Path,required=True)
    p.add_argument('--ranks',type=int,default=2)
    p.add_argument('--epw-pools',type=int,default=1,help='Explicit EPW pool layout; a different pool count is a distinct execution variant')
    p.add_argument('--timeout',type=float,default=600)
    a=p.parse_args(argv)
    try:
        suite=select_suite(a.qe_bin);ranks=positive_int(a.ranks,'ranks')
        source=a.source.resolve();test=source/'test-suite'
        conf=configparser.ConfigParser(interpolation=None);conf.read(test/'jobconfig')
        user=configparser.ConfigParser(interpolation=None);user.read(test/'userconfig.tmp')
        families=a.families.split(',')
        if not families or len(set(families))!=len(families) or any(f not in FAMILIES for f in families):raise ValidationError('PROFILE_FAMILIES','Select distinct supported families','ERROR')
        catalog=[]
        for family in families:
            section=family+'/'
            if section not in conf and family in conf:section=family
            # Families omitted from jobconfig use the upstream userconfig
            # program default ('*.in', ''), rather than a nonexistent section.
            defaults={'pw':'PW','ph':'PH','cp':'CP','hp':'HP','epw':'EPW','tddfpt':'TDDFPT','QEHeat':'ALL_CURRENTS'}
            program=conf[section]['program'] if section in conf else defaults[family.split('_')[0]]
            ordered=ast.literal_eval(conf[section]['inputs_args']) if section in conf and 'inputs_args' in conf[section] else [(name,'') for name in FAMILIES[family]]
            lookup={name:arg for name,arg in ordered}
            for name in FAMILIES[family]:
                arg=lookup.get(name,'')
                if name not in lookup:raise ValidationError('UPSTREAM_INPUT_UNDECLARED',family+'/'+name,'ERROR')
                benchmark='benchmark.out.git.inp='+name+('.args='+arg if arg else '')
                if not (test/family/benchmark).is_file() and (test/family/Path(name).with_suffix('.ref')).is_file():
                    benchmark=str(Path(name).with_suffix('.ref'))
                cid=re.sub(r'[^A-Za-z0-9_.-]','_',family+'__'+name)
                catalog.append(dict(case=cid,family=family,input=name,arg=arg,program=program,executable=program_name(program,arg,name),benchmark=benchmark))
                if program=='EPW' and arg=='2':
                    catalog.append(dict(case=cid+'_preprocess',family=family,input='pp.in',arg='',program='PREPROCESS',executable='python',benchmark=None))
        c=Campaign(a.out_dir,[v['case'] for v in catalog],suite,'upstream-selected-families')
        write_json(c.root/'catalog.json',{'source':str(source),'jobconfig_sha256':sha256(test/'jobconfig'),'tolerance_sha256':sha256(test/'userconfig.tmp'),'epw_pools':positive_int(a.epw_pools,'EPW pools'),'cases':catalog,'scope':'Finite selected upstream numerical regressions; production-model adequacy is separate'})
        file_index={}
        md5_index={}
        for path in source.rglob('*'):
            if path.is_file() and path.suffix.lower() in ('.upf','.bhs'):
                file_index.setdefault(path.name,[]).append(path)
                md5_index.setdefault(hashlib.md5(path.read_bytes()).hexdigest(),[]).append(path)
        cache=a.pseudo_cache.resolve();cache.mkdir(parents=True,exist_ok=True)
        history={};workspaces={}
        try:
            for entry in catalog:
                family=entry['family'];cid=entry['case'];name=entry['input'];prog=entry['program'];exe_name=entry['executable']
                if family not in workspaces:
                    work=c.root/'work'/family
                    shutil.copytree(test/family,work)
                    workspaces[family]=work
                work=workspaces[family];inp=work/name;benchmark=work/entry['benchmark'] if entry['benchmark'] else None
                if prog=='PREPROCESS':
                    def prepared(log,work):
                        artifacts=tree_manifest(work/'save')
                        if not artifacts:raise ValidationError('EPW_PARENT_MISSING','Phonon preprocessing produced no saved data','ERROR')
                        return {'metrics':{'saved_files':len(artifacts),'artifacts':artifacts}}
                    result=c.case(cid,[sys.executable,str(source/'EPW/bin/pp.py')],cwd=work,stdin=inp.read_text(),validator=prepared,timeout=60,blocked='Earlier EPW stage failed' if any(v!='PASS' for v in history.get(family,[])) else None)
                    history.setdefault(family,[]).append(result['state'])
                    continue
                blocked=None
                if prog=='PH' and exe_name=='pw.x':history[family]=[]
                if family.startswith(('ph_','hp_','epw_','tddfpt_','cp_')) and any(v!='PASS' for v in history.get(family,[])):
                    blocked='Earlier stage in this upstream family failed'
                try:
                    if not benchmark.is_file():raise ValidationError('REFERENCE_MISSING',str(benchmark),'BLOCKED')
                    text=inp.read_text()
                    reference=benchmark.read_text(errors='replace')
                    required_md5=dict((Path(path.strip()).name,digest) for path,digest in re.findall(r'read from file:\s*\n([^\n]+)\s*\n\s*MD5 check sum:\s*([a-f0-9]{32})',reference))
                    ppdir=work/'pseudopotentials';ppdir.mkdir(exist_ok=True)
                    hashes={}
                    for pp in species(text):
                        wanted=required_md5.get(pp)
                        available=file_index.get(pp,[])+md5_index.get(wanted,[])+([cache/pp] if (cache/pp).is_file() else [])
                        chosen=next((x for x in available if not wanted or hashlib.md5(x.read_bytes()).hexdigest()==wanted),None)
                        if chosen is None:raise ValidationError('PSEUDOPOTENTIAL_IDENTITY',f'Exact reference UPF unavailable: {pp}; wanted MD5 {wanted or "unrecorded"}','BLOCKED')
                        if not (ppdir/pp).exists():shutil.copy2(chosen,ppdir/pp)
                        hashes[pp]=sha256(ppdir/pp)
                    if species(text):
                        if re.search(r'pseudo_dir\s*=',text,re.I):text=re.sub(r"pseudo_dir\s*=\s*(['\"]).*?\1",f"pseudo_dir='{ppdir}'",text,flags=re.I)
                        else:text=re.sub(r'(&control\b)',rf"\g<1>\n pseudo_dir='{ppdir}',",text,flags=re.I)
                    extractor=test/Path(user[prog]['extract_program']).name
                    expected=extract_metrics(extractor,entry['benchmark'],work)
                    declared=ast.literal_eval(user[prog]['tolerance'])
                    if declared and not isinstance(declared[0],(tuple,list)):
                        declared=[declared]
                    tolerance={v[2]:(v[0] or 0.0,v[1] or 0.0) for v in declared if len(v)==3}
                    defaults=[v for v in declared if len(v)==2]
                    if defaults:
                        for key in expected:tolerance.setdefault(key,(defaults[0][0] or 0.0,defaults[0][1] or 0.0))
                    # An integer step-count contract is exact; the upstream
                    # extractor emits it but userconfig omits a named limit.
                    if prog=='TDDFPT':tolerance['nblanczos']=(0.0,0.0)
                    if prog=='PH':tolerance['qpoint']=tolerance['qpt']
                    def validate(log,work,entry=entry,extractor=extractor,expected=expected,tolerance=tolerance):
                        completion(log)
                        if observed_ranks(log)!=ranks:raise ValidationError('MPI_RANK_MISMATCH','Upstream case actual ranks differ')
                        if entry['executable']=='pw.x':
                            calc=re.search(r"calculation\s*=\s*['\"]([^'\"]+)",text,re.I)
                            calc=calc.group(1) if calc else 'scf'
                            pw_metrics(log,calculation=calc,ranks=ranks)
                        artifact=c.root/'cases'/entry['case']/'attempt-001/stdout.log'
                        metric_input=work/('result.out.inp='+entry['input']+('.args='+entry['arg'] if entry['arg'] else ''))
                        shutil.copy2(artifact,metric_input)
                        if entry['executable']=='hp.x':
                            files=list(work.glob('*.Hubbard_parameters.dat'))
                            if len(files)!=1:raise ValidationError('HP_RESPONSE_MISSING','Actual Hubbard response result missing')
                            shutil.copy2(files[0],metric_input)
                        elif entry['executable']=='turbo_spectrum.x':
                            files=list(work.glob('*.plot_eps.dat' if 'eels' in entry['input'] else '*.plot_chi.dat'))
                            if len(files)!=1:raise ValidationError('SPECTRUM_MISSING','Unique response spectrum missing')
                            shutil.copy2(files[0],metric_input)
                            shutil.copy2(files[0],artifact.parent/'response-spectrum.dat')
                        elif entry['executable']=='matdyn.x' and entry['arg']=='8':shutil.copy2(work/'matdyn.modes',metric_input)
                        actual=extract_metrics(extractor,metric_input.name,work)
                        assertions=[]
                        for key,values in expected.items():
                            if key not in actual or len(actual[key])!=len(values):raise ValidationError('METRIC_COVERAGE',f'{key}: missing/mismatched reference dimensions','ERROR')
                            if key not in tolerance:raise ValidationError('TOLERANCE_MISSING',key,'ERROR')
                            atol,rtol=tolerance[key]
                            assertions.extend(scalar_assertion(key+f'[{i}]',x,y,atol,rtol) for i,(x,y) in enumerate(zip(actual[key],values)))
                        return {'metrics':actual,'assertions':assertions}
                    command=mpi_command(executable(suite,exe_name),['-in','{input}'],ranks)
                    if exe_name=='epw.x':command=mpi_command(executable(suite,exe_name),['-npool',str(a.epw_pools),'-in','{input}'],ranks)
                    result=c.case(cid,command,text=text,cwd=work,validator=validate,timeout=a.timeout,blocked=blocked,metadata={'upstream':entry,'input_origin_sha256':sha256(inp),'benchmark_sha256':sha256(benchmark),'pseudopotentials':hashes,'tolerances':tolerance})
                except ValidationError as exc:
                    def reject(log,work,error=exc):raise error
                    result=c.case(cid,None,validator=reject)
                history.setdefault(family,[]).append(result['state'])
        finally:rc=c.finish()
        return rc
    except ValidationError as exc:print(json.dumps({'state':exc.state,'reason':exc.reason,'detail':str(exc)}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
