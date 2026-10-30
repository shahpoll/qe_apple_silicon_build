#!/usr/bin/env python3
"""Check existing build prerequisites without installing or changing tools."""
import argparse
import os
from pathlib import Path
import shutil
import sys
from qe_validation.core import ValidationError
from qe_validation.install import preflight

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--backend',choices=['openblas','accelerate'],default='openblas')
    p.add_argument('--blas-library',default=os.environ.get('QE_BLAS_LIBRARY'))
    p.add_argument('--work-dir',type=Path,default=Path.home(),help='Planned build/run location; checks its volume without creating directories')
    a=p.parse_args()
    try:
        if sys.version_info<(3,12):raise ValidationError('PYTHON_UNSUPPORTED','Python 3.12+ is required','BLOCKED')
        info=preflight(a.backend,a.blas_library)
        volume=a.work_dir.expanduser().resolve()
        while not volume.exists():volume=volume.parent
        free=shutil.disk_usage(volume).free
        print('Quantum ESPRESSO build prerequisites')
        for name,path in info['tools'].items():print(f'  {name:<10} {path}')
        print('  BLAS       '+info['blas_library'])
        print(f'  Free space {free/1024**3:.1f} GiB on the volume containing {volume}')
        if free<8*1024**3:raise ValidationError('DISK_BUDGET','A clean build requires at least 8 GiB free on its output volume. Choose a volume with sufficient space.','BLOCKED')
        print('PASS: required tools are present. The clean build and numerical checks are the next steps.')
        return 0
    except ValidationError as error:
        print(f'{error.state}: {error.reason}: {error}',file=sys.stderr)
        print('Setup guide: https://github.com/shahpoll/qe_apple_silicon_build/blob/main/docs/INSTALL.md',file=sys.stderr)
        return 2

if __name__=='__main__':raise SystemExit(main())
