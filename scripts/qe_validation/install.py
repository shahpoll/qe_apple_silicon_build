"""Verified curl downloads, clean CMake builds, and qualified atomic activation."""
from __future__ import annotations
import argparse
import contextlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import uuid
from .core import Campaign, ROOT, ValidationError, executable, runtime_env, safe_new_directory, sha256, tree_manifest, utc, write_json
from .campaign import seed_spec, seed_validator
from .core import mpi_command
from .linkage import inspect_binary

PROGRAMS = {
    'core': ['pw.x','ph.x','bands.x','dos.x','projwfc.x','pp.x','q2r.x','matdyn.x'],
    'workstation': ['pw.x','ph.x','bands.x','dos.x','projwfc.x','pp.x','q2r.x','matdyn.x','cp.x','hp.x','neb.x','epw.x','pw2wannier90.x','wannier90.x','xspectra.x','all_currents.x','turbo_davidson.x','turbo_lanczos.x','turbo_eels.x','turbo_magnon.x','turbo_spectrum.x'],
}


def verified_download(url: str, digest: str, destination: Path, evidence: Path, *, local: bool = False) -> Path:
    if not digest or len(digest)!=64 or any(x not in '0123456789abcdef' for x in digest):
        raise ValidationError('DOWNLOAD_CHECKSUM_REQUIRED','Expected lowercase SHA256 is required','ERROR')
    if not url.startswith('https://') and not (local and url.startswith('file://')):
        raise ValidationError('DOWNLOAD_PROTOCOL','HTTPS required; file URLs require explicit local mode','ERROR')
    if destination.exists():
        if destination.is_file() and sha256(destination)==digest:return destination
        raise ValidationError('CACHE_HASH_MISMATCH',f'Existing cache does not match pin: {destination}','ERROR')
    partial=evidence/'download.partial'
    c=Campaign(evidence/'transfer',['curl'],profile='verified-download')
    def validate(log,work):
        if not partial.is_file() or sha256(partial)!=digest:
            raise ValidationError('DOWNLOAD_HASH_MISMATCH','Downloaded content differs from the frozen checksum')
        return {'metrics':{'sha256':digest,'bytes':partial.stat().st_size}}
    protocol='=https,file' if local else '=https'
    c.case('curl',['curl','--fail','--location','--show-error','--silent','--proto',protocol,'--proto-redir',protocol,'--tlsv1.2','--connect-timeout','20','--max-time','300',url,'--output',str(partial)],validator=validate,timeout=330)
    if c.finish()!=0:raise ValidationError('DOWNLOAD_FAILED',f'Failed verified download; evidence: {c.root}','BLOCKED')
    destination.parent.mkdir(parents=True,exist_ok=True)
    os.link(partial,destination)  # Exclusive; never replace an existing cache entry.
    return destination


def extract_archive(archive: Path, destination: Path) -> Path:
    if destination.exists():raise ValidationError('EXTRACT_EXISTS',str(destination),'ERROR')
    destination.mkdir()
    with tarfile.open(archive,'r:*') as tar:
        # Python's data filter blocks absolute paths, traversal, and escaping links.
        if not hasattr(tarfile,'data_filter'):
            raise ValidationError('PYTHON_UNSUPPORTED','Python with safe tarfile data_filter is required','BLOCKED')
        tar.extractall(destination,filter='data')
    children=list(destination.iterdir())
    if len(children)!=1 or not children[0].is_dir():
        raise ValidationError('ARCHIVE_LAYOUT','Archive must contain one root directory','ERROR')
    return children[0]


def preflight(backend: str, blas: str | None) -> dict:
    if platform.system()!='Darwin' or platform.machine()!='arm64':
        raise ValidationError('PLATFORM_UNSUPPORTED','This installer profile requires native arm64 macOS','BLOCKED')
    tools={name:shutil.which(name) for name in ['curl','git','cmake','mpif90','mpicc','mpirun','gfortran','clang','otool']}
    missing=[name for name,p in tools.items() if not p]
    if missing:raise ValidationError('PREREQUISITE_MISSING','Install existing-tool prerequisites: '+', '.join(missing),'BLOCKED')
    if backend=='openblas' and (not blas or not Path(blas).expanduser().is_file()):
        raise ValidationError('BLAS_PATH_REQUIRED','--blas-library must name an existing OpenBLAS dylib','BLOCKED')
    sdk=subprocess.run(['xcode-select','-p'],capture_output=True,text=True)
    if sdk.returncode:raise ValidationError('SDK_MISSING','Apple Command Line Tools are required','BLOCKED')
    versions={name:subprocess.run([path,'--version'],capture_output=True,text=True).stdout.splitlines()[:2] for name,path in tools.items() if name in ['cmake','gfortran','mpirun']}
    wrapper=subprocess.run([tools['mpif90'],'--showme'],capture_output=True,text=True)
    # MPI compiler aliases select language by argv[0]; resolving mpif90 to
    # opal_wrapper destroys that selection. Keep invocation and identity apart.
    return {'tools':{n:str(Path(p).absolute()) for n,p in tools.items()},'tool_realpaths':{n:str(Path(p).resolve()) for n,p in tools.items()},'versions':versions,'mpi_wrapper':wrapper.stdout.strip(),'sdk':sdk.stdout.strip(),'backend':backend,'blas_library':str(Path(blas).expanduser().resolve()) if blas else '-framework Accelerate','platform':platform.platform()}


@contextlib.contextmanager
def activation_lock(prefix: Path):
    prefix.mkdir(parents=True,exist_ok=True)
    lock=prefix/'.activation-lock'
    try:lock.mkdir()
    except FileExistsError as exc:raise ValidationError('ACTIVATION_LOCKED',f'Another activation or retained interrupted lock exists: {lock}','BLOCKED') from exc
    write_json(lock/'owner.json',{'pid':os.getpid(),'utc':utc(),'token':uuid.uuid4().hex})
    try:yield
    finally:
        (lock/'owner.json').unlink()
        lock.rmdir()


def activate(prefix: Path, candidate: Path, qualification: Path) -> dict:
    record=json.loads(qualification.read_text())
    if record.get('state')!='PASS':raise ValidationError('ACTIVATION_UNQUALIFIED','Candidate qualification is not PASS','BLOCKED')
    if not candidate.resolve().is_relative_to((prefix/'releases').resolve()):
        raise ValidationError('ACTIVATION_BOUNDARY','Candidate must be a release under this prefix','ERROR')
    manifest=json.loads((candidate/'release.json').read_text())
    campaign_file=qualification.parent/'campaign.json'
    if not campaign_file.is_file():raise ValidationError('QUALIFICATION_IDENTITY','Qualification campaign manifest missing','BLOCKED')
    campaign=json.loads(campaign_file.read_text())
    if campaign.get('suite')!=str((candidate/'bin').resolve()):
        raise ValidationError('QUALIFICATION_IDENTITY','Qualification belongs to a different binary suite','BLOCKED')
    wanted='core' if manifest['profile']=='core' else 'comprehensive'
    if campaign.get('profile')!=wanted:
        raise ValidationError('QUALIFICATION_SCOPE',f'{manifest["profile"]} activation requires {wanted} numerical qualification, not build/seed checks','BLOCKED')
    expected=campaign['expected_cases']
    cases=record.get('cases',[])
    if len(cases)!=len(expected) or {r['case'] for r in cases}!=set(expected) or any(r['state']!='PASS' for r in cases):
        raise ValidationError('QUALIFICATION_COVERAGE','Missing, duplicated, or non-PASS qualification cases','BLOCKED')
    if wanted=='core':
        required={'upstream_seed','pw_scf','pw_bands','bands_post','pw_nscf','dos','projwfc','pp_charge','ph_gamma','ph_grid','q2r_ifc','matdyn_gamma','scf_rank_1','scf_rank_2','scf_rank_4','reference_and_peer_agreement'}
        if not required.issubset(expected) or len([x for x in expected if x.startswith('scf_repeat_')])<3:
            raise ValidationError('QUALIFICATION_COVERAGE','Core contract needs the entire workflow, three ranks, and three repeats','BLOCKED')
    for case in cases:
        attempt=qualification.parent/case['evidence']
        if not attempt.resolve().is_relative_to(qualification.parent.resolve()):
            raise ValidationError('QUALIFICATION_EVIDENCE_BOUNDARY',str(attempt),'BLOCKED')
        terminal=qualification.parent/'cases'/case['case']/'case-result.json'
        if json.loads(terminal.read_text())!=case or json.loads((attempt/'result.json').read_text())!=case:
            raise ValidationError('QUALIFICATION_RECORD_DRIFT','Summary differs from finalized case evidence','BLOCKED')
        if any(not item.get('passed') for item in case.get('assertions',[])):
            raise ValidationError('QUALIFICATION_ASSERTION_FAILED',case['case'],'BLOCKED')
        for rel,digest in case['artifacts'].items():
            file=attempt/rel
            if not file.is_file() or sha256(file)!=digest:raise ValidationError('QUALIFICATION_EVIDENCE_DRIFT',str(file),'BLOCKED')
        invocation=json.loads((attempt/'manifest.json').read_text())
        for path,digest in invocation.get('executables',{}).items():
            binary=Path(path)
            if binary.parent==(candidate/'bin').resolve() and digest!=manifest['binary_sha256'].get(binary.name):
                raise ValidationError('QUALIFICATION_BINARY_DRIFT',str(binary),'BLOCKED')
    for rel,digest in campaign['source']['files'].items():
        file=qualification.parent/'source'/rel
        if not file.is_file() or sha256(file)!=digest:
            raise ValidationError('QUALIFICATION_SOURCE_DRIFT',str(file),'BLOCKED')
    if wanted=='comprehensive':
        review=qualification.parent/'review.json'
        if not review.is_file() or not json.loads(review.read_text()).get('independent_review_accepted'):
            raise ValidationError('INDEPENDENT_REVIEW_REQUIRED','Comprehensive activation needs accepted independent code-and-evidence review','BLOCKED')
    for name,digest in manifest['binary_sha256'].items():
        if sha256(candidate/'bin'/name)!=digest:raise ValidationError('BINARY_DRIFT',name,'BLOCKED')
        actual=inspect_binary(candidate/'bin'/name)
        if name not in manifest.get('dependencies',{}):
            raise ValidationError('DEPENDENCY_MANIFEST_MISSING',name,'BLOCKED')
        closure={path:info['sha256'] for path,info in actual['closure'].items()}
        if closure!=manifest['dependencies'][name]:
            raise ValidationError('DEPENDENCY_DRIFT',f'{name}: dependency closure changed; requalification is required','BLOCKED')
    if manifest['toolchain']['platform']!=platform.platform():
        raise ValidationError('PLATFORM_DRIFT','macOS/architecture changed since qualification','BLOCKED')
    with activation_lock(prefix):
        current=prefix/'current'
        if current.exists() and not current.is_symlink():raise ValidationError('ACTIVATION_CONFLICT','current must be an owned symlink','ERROR')
        previous=str(current.resolve()) if current.is_symlink() else None
        temp=prefix/('.current-'+uuid.uuid4().hex)
        temp.symlink_to(candidate.relative_to(prefix))
        os.replace(temp,current)
        history={'state':'PASS','candidate':str(candidate),'previous':previous,'qualification':str(qualification),'qualification_sha256':sha256(qualification),'utc':utc()}
        with (prefix/'activation-history.jsonl').open('a') as f:f.write(json.dumps(history)+'\n');f.flush();os.fsync(f.fileno())
    return history


def build(args) -> int:
    toolchain=preflight(args.backend,args.blas_library)
    jobs=int(args.jobs)
    if jobs<1 or jobs>min(8,os.cpu_count() or 1):raise ValidationError('BUILD_JOBS','Use a positive job count within the CPU count and the eight-job limit','ERROR')
    profile=args.profile
    if args.activate and profile!='core':
        raise ValidationError('QUALIFICATION_SCOPE','Automatic activation supports only --profile core; comprehensive workstation qualification and independent review remain required','BLOCKED')
    expected=['verified_source','configure','build','suite_manifest','upstream_qualification']
    c=Campaign(args.out_dir,expected,profile='build-'+profile)
    prefix=args.install_prefix.expanduser().resolve()
    if prefix in (Path('/'),Path.home(),ROOT) or prefix.is_relative_to(ROOT):raise ValidationError('INSTALL_PROTECTED','Install outside source and existing unversioned suites','ERROR')
    release=prefix/'releases'/('qe-7.5-'+args.backend+'-'+uuid.uuid4().hex[:10])
    release.mkdir(parents=True,exist_ok=False)
    write_json(c.root/'candidate.json',{'path':str(release),'profile':profile,'activation':'INACTIVE'})
    write_json(c.root/'toolchain.json',toolchain)
    try:
        free=shutil.disk_usage(c.root).free
        write_json(c.root/'resources.json',{'free_bytes':free,'required_free_bytes':8*1024**3,'build_jobs':jobs,'logical_cpus':os.cpu_count(),'scope':'Conservative build disk admission; runtime memory needs remain calculation dependent'})
        if free<8*1024**3:raise ValidationError('DISK_BUDGET','At least 8 GiB free is required before a clean build','BLOCKED')
        pin=json.loads((ROOT/'profiles/sources.json').read_text())['qe-7.5']
        archive=args.archive.expanduser().resolve() if args.archive else c.root/'qe-7.5.tar.gz'
        def source_check(log,work):
            if args.archive:
                if not archive.is_file() or sha256(archive)!=pin['sha256']:raise ValidationError('SOURCE_HASH_MISMATCH','Provided source archive differs from pin')
            else:verified_download(pin['url'],pin['sha256'],archive,c.root/'work')
            return {'metrics':{'source_sha256':pin['sha256']}}
        r=c.case('verified_source',None,validator=source_check)
        if r['state']!='PASS':return c.finish()
        src=extract_archive(archive,c.root/'work/source')
        bld=c.root/'work/build'
        blas=str(Path(args.blas_library).expanduser().resolve()) if args.backend=='openblas' else '-framework Accelerate'
        # All modules are built by the default CMake target; no overlay of old bin/.
        command=['cmake','-S',str(src),'-B',str(bld),'-DCMAKE_BUILD_TYPE=Release',
                 '-DCMAKE_C_COMPILER='+toolchain['tools']['mpicc'],'-DCMAKE_Fortran_COMPILER='+toolchain['tools']['mpif90'],
                 '-DQE_ENABLE_MPI=ON','-DQE_ENABLE_OPENMP=OFF','-DQE_ENABLE_FOX=OFF','-DQE_ENABLE_TEST=OFF',
                 '-DBLAS_LIBRARIES='+blas,'-DLAPACK_LIBRARIES='+blas,'-DCMAKE_INSTALL_PREFIX='+str(release)]
        r=c.case('configure',command,timeout=600)
        r=c.case('build',['cmake','--build',str(bld),'--parallel',str(jobs)],timeout=args.build_timeout,blocked='Configure failed' if r['state']!='PASS' else None)
        def suite_check(log,work):
            bin_dir=bld/'bin'
            manifest={}
            available=sorted(p.name for p in bin_dir.glob('*.x') if p.is_file())
            missing=set(PROGRAMS[profile])-set(available)
            if missing:raise ValidationError('BUILD_MODULE_MISSING',','.join(sorted(missing)),'BLOCKED')
            for name in available:
                exe=executable(bin_dir,name)
                shutil.copy2(exe,release/'bin'/name)
                manifest[name]={'sha256':sha256(release/'bin'/name),'linkage':inspect_binary(release/'bin'/name)}
            submodules={}
            for path in (src/'external').iterdir():
                if (path/'.git').exists():
                    proc=subprocess.run(['git','-C',str(path),'rev-parse','HEAD'],capture_output=True,text=True,check=True)
                    submodules[path.name]=proc.stdout.strip()
            write_json(release/'release.json',{'schema':1,'source':pin,'toolchain':toolchain,'submodules':submodules,'profile':profile,'required_programs':PROGRAMS[profile],'dependencies':{n:{path:info['sha256'] for path,info in v['linkage']['closure'].items()} for n,v in manifest.items()},'binary_sha256':{n:v['sha256'] for n,v in manifest.items()},'created_utc':utc(),'qualification_scope':'build completeness and upstream seed; broader capabilities require their explicit numerical records'})
            write_json(work/'suite.json',manifest)
            return {'metrics':{'programs':len(manifest)}}
        (release/'bin').mkdir()
        r=c.case('suite_manifest',None,validator=suite_check,blocked='Build failed' if r['state']!='PASS' else None)
        text,spec=seed_spec()
        if r['state']=='PASS':command=mpi_command(executable(release/'bin','pw.x'),['-in','{input}'],2)
        else:command=None
        c.case('upstream_qualification',command,text=text,validator=seed_validator(spec,2),timeout=180,blocked='Suite incomplete' if r['state']!='PASS' else None)
    finally:
        result=c.finish()
    if result==0 and args.activate:
        from .campaign import main as qualify
        result=qualify(['--qe-bin',str(release/'bin'),'--profile','core','--out-dir',str(c.root/'qualification')])
        if result==0:write_json(c.root/'activation.json',activate(prefix,release,c.root/'qualification/summary.json'))
        else:print('Candidate retained inactive: numerical qualification failed; '+str(release))
    else:print('Candidate retained inactive: '+str(release))
    return result


def main(argv=None):
    p=argparse.ArgumentParser(description='Curl/source installer using existing tools; never invokes Homebrew')
    p.add_argument('--qe-tag',choices=['qe-7.5'],default='qe-7.5')
    p.add_argument('--install-prefix',type=Path,default=Path.home()/'.local/share/qe')
    p.add_argument('--archive',type=Path,help='Already downloaded archive; must match the frozen checksum')
    p.add_argument('--out-dir',type=Path)
    p.add_argument('--backend',choices=['openblas','accelerate'],default='openblas')
    p.add_argument('--blas-library',default=os.environ.get('QE_BLAS_LIBRARY'))
    p.add_argument('--jobs',type=int,default=2)
    p.add_argument('--profile',choices=list(PROGRAMS),default='workstation')
    p.add_argument('--build-timeout',type=float,default=3600)
    p.add_argument('--activate',action='store_true',help='Activate only after this explicitly selected qualification profile passes')
    args=p.parse_args(argv)
    try:return build(args)
    except ValidationError as exc:
        print(json.dumps({'state':exc.state,'reason':exc.reason,'detail':str(exc)}),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
