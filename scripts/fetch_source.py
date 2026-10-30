#!/usr/bin/env python3
"""Verified fetch into a new external destination; old source trees are retained."""
import argparse,json
from pathlib import Path
import sys
from qe_validation.core import ROOT,ValidationError,safe_new_directory
from qe_validation.install import verified_download,extract_archive
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('kind',choices=['qe-7.5','pwtk-3.2'])
p.add_argument('--destination',type=Path)
a=p.parse_args()
try:
 pins=json.loads((ROOT/'profiles/sources.json').read_text())
 pin=pins[a.kind]
 work=safe_new_directory(a.destination,'fetch-'+a.kind)
 archive=work/(a.kind+'.tar.gz')
 verified_download(pin['url'],pin['sha256'],archive,work/'work')
 source=extract_archive(archive,work/'extracted')
 print(source)
except ValidationError as e:print(json.dumps({'state':e.state,'reason':e.reason,'detail':str(e)}),file=sys.stderr);raise SystemExit(2)
