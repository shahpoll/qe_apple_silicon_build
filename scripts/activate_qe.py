#!/usr/bin/env python3
"""Activate or roll back only an identified, numerically qualified release."""
import argparse,json,sys
from pathlib import Path
from qe_validation.install import activate
from qe_validation.core import ValidationError
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--install-prefix',type=Path,required=True)
p.add_argument('--release',type=Path,required=True)
p.add_argument('--qualification',type=Path,required=True)
a=p.parse_args()
try:print(json.dumps(activate(a.install_prefix.resolve(),a.release.resolve(),a.qualification.resolve()),indent=2))
except ValidationError as e:print(json.dumps({'state':e.state,'reason':e.reason,'detail':str(e)}),file=sys.stderr);raise SystemExit(2)
