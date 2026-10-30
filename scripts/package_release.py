#!/usr/bin/env python3
"""Build a portable manager archive and checksum files without publishing it."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tarfile

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = (
    'bin', 'scripts/qe_validation', 'profiles', 'fixtures/upstream-qe75',
    'cases/common/scripts',
)
FILES = (
    'scripts/install_qe.py', 'scripts/doctor.py', 'scripts/smoke_test.py',
    'scripts/validate_build.py', 'scripts/workflow.py',
    'scripts/upstream_validation.py', 'scripts/compare_runs.py',
    'scripts/physical_checks.py', 'scripts/example_validation.py',
    'scripts/davidson_validation.py', 'scripts/compare_backends.py',
    'scripts/review_case.py', 'scripts/activate_qe.py', 'scripts/status.py',
    'scripts/fetch_source.py', 'scripts/run_qe.py', 'scripts/run_qe.sh',
    'scripts/qe_manager.sh', 'scripts/ci_migration_check.sh',
    'scripts/setup/bootstrap.sh', 'scripts/setup/fetch_qe.sh',
    'scripts/setup/fetch_pwtk.sh', 'inputs/Si.scf.in', 'inputs/Si.bands.in',
    'inputs/Si.bands_post.in', 'inputs/Si.nscf.in', 'inputs/Si.dos.in',
    'inputs/Si.projwfc.in',
    'cases/common/pp/Si.pbe-n-rrkjus_psl.1.0.0.UPF',
    'cases/si/convergence/run_convergence.py', 'docs/INSTALL.md',
    'docs/VALIDATION.md', 'docs/README.md', 'docs/Workflow_Basics.md',
    'docs/PP.md', 'docs/Command_Reference.md', 'docs/Troubleshooting.md',
    'docs/Release_Checklist.md', 'install.sh', 'CMakePresets.json',
    'CONTRIBUTING.md', 'CHANGELOG.md', 'README.md', 'LICENSE',
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out-dir', type=Path, required=True)
    p.add_argument('--release-tag', default='v2.0.0-rc.1')
    p.add_argument('--repository', default='shahpoll/qe_apple_silicon_build')
    a = p.parse_args()
    if not re.fullmatch(r'v[0-9][A-Za-z0-9._-]*', a.release_tag):
        p.error('Use a version tag such as v2.0.0-rc.1')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', a.repository):
        p.error('Repository must have owner/name form')
    a.out_dir.mkdir(parents=True, exist_ok=False)
    archive = a.out_dir / 'qe-manager.tar.gz'
    members = set(FILES)
    for folder in FOLDERS:
        members.update(str(path.relative_to(ROOT))
                       for path in (ROOT / folder).rglob('*')
                       if path.is_file() and '__pycache__' not in path.parts)
    with tarfile.open(archive, 'w:gz') as tar:
        for name in sorted(members):
            tar.add(ROOT / name, arcname='qe-manager/' + name, recursive=False)
    shutil.copy2(ROOT / 'install.sh', a.out_dir / 'install.sh')
    url = f'https://github.com/{a.repository}/releases/download/{a.release_tag}'
    manifest = {
        'schema': 1, 'kind': 'qe-manager', 'version': a.release_tag,
        'source_url': url + '/qe-manager.tar.gz',
        'source_sha256': sha256(archive),
        'scope': 'Manager preview; QE is separately built and qualified',
    }
    (a.out_dir / 'manager.json').write_text(json.dumps(manifest, indent=2) + '\n')
    assets = ('install.sh', 'manager.json', 'qe-manager.tar.gz')
    (a.out_dir / 'SHA256SUMS').write_text(''.join(
        sha256(a.out_dir / name) + '  ' + name + '\n' for name in assets))
    (a.out_dir / 'release.json').write_text(json.dumps({
        'archive': str(archive), 'sha256': manifest['source_sha256'],
        'publication': 'NOT_PUBLISHED', 'version': a.release_tag,
        'scope': manifest['scope'],
        'files': {name: sha256(ROOT / name) for name in sorted(members)},
    }, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
