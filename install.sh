#!/usr/bin/env bash
# Download to a file with curl, inspect if desired, then run with bash.
# Package content is checked against the versioned release manifest before use.
set -euo pipefail
exec "${QE_PYTHON:-python3}" - "$@" <<'PY'
import argparse, datetime, hashlib, json, os, pathlib, shutil, subprocess, sys, tarfile, uuid
DEFAULT_MANIFEST = 'https://github.com/shahpoll/qe_apple_silicon_build/releases/download/v2.0.0-rc.1/manager.json'
p=argparse.ArgumentParser(description='Install the QE manager from a checksum-pinned curl archive; existing tools only')
p.add_argument('--manifest-url',help='Versioned manager manifest; defaults to the v2.0.0-rc.1 preview')
p.add_argument('--source-url',help='Explicit archive URL; requires --source-sha256')
p.add_argument('--source-sha256',help='Expected archive SHA256; requires --source-url')
p.add_argument('--manager-prefix',type=pathlib.Path,default=pathlib.Path.home()/'.local/share/qe-manager')
p.add_argument('--bin-dir',type=pathlib.Path,default=pathlib.Path.home()/'.local/bin')
p.add_argument('--local-file',action='store_true',help='Explicitly allow file:// package URL for local/offline installation')
a=p.parse_args()
if sys.version_info<(3,12) or not hasattr(tarfile,'data_filter'):p.error('Python 3.12+ is required; install it from https://www.python.org/downloads/macos/ or select QE_PYTHON')
if bool(a.source_url)!=bool(a.source_sha256):p.error('Supply both --source-url and --source-sha256, or neither to use the release manifest')
if a.manifest_url and a.source_url:p.error('Choose --manifest-url or the explicit archive/checksum pair')
def valid_digest(value):return isinstance(value,str) and len(value)==64 and all(x in '0123456789abcdef' for x in value)
def valid_url(value):return isinstance(value,str) and (value.startswith('https://') or (a.local_file and value.startswith('file://')))
if a.source_url and (not valid_url(a.source_url) or not valid_digest(a.source_sha256)):p.error('HTTPS and an expected lowercase SHA256 are required; file:// requires --local-file')
manifest_url=None if a.source_url else a.manifest_url or DEFAULT_MANIFEST
if manifest_url and not valid_url(manifest_url):p.error('Manifest requires HTTPS; file:// requires --local-file')
prefix=a.manager_prefix.expanduser().resolve();bin_dir=a.bin_dir.expanduser().resolve()
if prefix in (pathlib.Path('/'),pathlib.Path.home().resolve()):p.error('Select a dedicated manager prefix')
prefix.mkdir(parents=True,exist_ok=True)
attempt=prefix/'attempts'/('install-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S')+'-'+uuid.uuid4().hex[:8]);attempt.mkdir(parents=True)
record={'state':'RUNNING','manifest_url':manifest_url,'source_url':a.source_url,'expected_sha256':a.source_sha256,'prefix':str(prefix),'bin_dir':str(bin_dir)}
(attempt/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
try:
 protocol='=https,file' if a.local_file else '=https'
 def download(url,destination,label):
  command=['curl','--fail','--location','--show-error','--silent','--proto',protocol,'--proto-redir',protocol,'--tlsv1.2','--connect-timeout','20','--max-time','300',url,'--output',str(destination)]
  with (attempt/(label+'.stdout.log')).open('w') as out,(attempt/(label+'.stderr.log')).open('w') as err:
   proc=subprocess.run(command,stdout=out,stderr=err,timeout=330)
  if proc.returncode:raise RuntimeError('CURL_DOWNLOAD_FAILED: inspect '+str(attempt))
 if manifest_url:
  manifest_file=attempt/'manager.json';download(manifest_url,manifest_file,'manifest-curl')
  manifest=json.loads(manifest_file.read_text())
  if not isinstance(manifest,dict) or manifest.get('schema')!=1 or manifest.get('kind')!='qe-manager' or not valid_url(manifest.get('source_url')) or not valid_digest(manifest.get('source_sha256')):
   raise RuntimeError('MANAGER_MANIFEST_INVALID: archive URL and SHA256 are required')
  a.source_url=manifest['source_url'];a.source_sha256=manifest['source_sha256']
  record.update(source_url=a.source_url,expected_sha256=a.source_sha256,version=manifest.get('version'),manifest_sha256=hashlib.sha256(manifest_file.read_bytes()).hexdigest())
  (attempt/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
 archive=attempt/'manager.tar.gz'
 download(a.source_url,archive,'curl')
 actual=hashlib.sha256(archive.read_bytes()).hexdigest()
 if actual!=a.source_sha256:raise RuntimeError('DOWNLOAD_HASH_MISMATCH')
 release=prefix/'releases'/a.source_sha256
 if release.exists():raise RuntimeError('RELEASE_EXISTS: installed releases are immutable; inspect the retained previous attempt')
 extraction=attempt/'extracted';extraction.mkdir()
 with tarfile.open(archive) as tar:tar.extractall(extraction,filter='data')
 contents=list(extraction.iterdir())
 if len(contents)!=1 or not contents[0].is_dir():raise RuntimeError('ARCHIVE_LAYOUT')
 source=contents[0]
 cli=source/'bin/qe-apple-silicon-build'
 if not cli.is_file():raise RuntimeError('PACKAGE_ENTRYPOINT_MISSING')
 check=subprocess.run(['bash',str(cli),'smoke','--help'],capture_output=True,text=True,timeout=30)
 (attempt/'dispatch.stdout.log').write_text(check.stdout);(attempt/'dispatch.stderr.log').write_text(check.stderr)
 if check.returncode:raise RuntimeError('PACKAGE_DISPATCH_FAILED')
 lock=prefix/'.install-lock'
 try:lock.mkdir()
 except FileExistsError:raise RuntimeError('INSTALL_LOCKED: preserve and inspect concurrent/interrupted attempt')
 try:
  prefix.joinpath('releases').mkdir(exist_ok=True)
  if release.exists():raise RuntimeError('RELEASE_EXISTS')
  bin_dir.mkdir(parents=True,exist_ok=True)
  public=bin_dir/'qe-apple-silicon-build'
  if public.exists() or public.is_symlink():
   if not public.is_symlink() or not public.resolve().is_relative_to(prefix):raise RuntimeError('PUBLIC_ENTRYPOINT_CONFLICT: existing unrelated command preserved')
  shutil.move(str(source),release)
  current=prefix/'current'
  if current.exists() and not current.is_symlink():raise RuntimeError('ACTIVATION_CONFLICT')
  previous=str(current.resolve()) if current.is_symlink() else None
  temp=prefix/('.current-'+uuid.uuid4().hex);temp.symlink_to(release.relative_to(prefix));os.replace(temp,current)
  link=bin_dir/('.qe-manager-'+uuid.uuid4().hex);link.symlink_to(current/'bin/qe-apple-silicon-build');os.replace(link,public)
  record.update(state='PASS',release=str(release),previous=previous,archive_sha256=actual,command=str(public))
 finally:lock.rmdir()
except BaseException as e:
 record.update(state='FAIL',reason=str(e))
 print(str(e),file=sys.stderr)
finally:
 (attempt/'result.json').write_text(json.dumps(record,indent=2)+'\n')
 print('Evidence: '+str(attempt))
if record['state']=='PASS':
 print('Installed manager: '+record['command'])
 print('Next: add '+str(bin_dir)+' to PATH, then run qe-apple-silicon-build doctor --blas-library /path/to/libopenblas.dylib')
sys.exit(0 if record['state']=='PASS' else 1)
PY
