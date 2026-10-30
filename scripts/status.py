#!/usr/bin/env python3
"""Inspect finalized and interrupted attempts without rewriting historical records."""
import argparse,json
from pathlib import Path
from qe_validation.core import sha256
p=argparse.ArgumentParser(description=__doc__);p.add_argument('run',type=Path);a=p.parse_args()
manifest=json.loads((a.run/'campaign.json').read_text())
expected=manifest['expected_cases']
if not expected or len(expected)!=len(set(expected)):
 raise SystemExit('CASE_INVENTORY: empty or duplicate expected case list')
summary=json.loads((a.run/'summary.json').read_text()) if (a.run/'summary.json').is_file() else None
summary_cases={r['case']:r for r in summary['cases']} if summary else {}
records=[]
for cid in manifest['expected_cases']:
 p=a.run/'cases'/cid/'case-result.json'
 if not p.is_file():records.append({'case':cid,'state':'INTERRUPTED_OR_NOT_RUN','reason':'No finalized case result'});continue
 r=json.loads(p.read_text());valid=True
 attempt=a.run/r['evidence']
 if not (attempt/'result.json').is_file() or json.loads((attempt/'result.json').read_text())!=r:valid=False
 if summary_cases.get(cid)!=r:valid=False
 for name,digest in r['artifacts'].items():
  f=a.run/r['evidence']/name
  if not f.is_file() or sha256(f)!=digest:valid=False
 records.append({'case':cid,'state':r['state'] if valid else 'EVIDENCE_INVALID','reasons':r['reasons']})
complete=all(r['state']=='PASS' for r in records) and summary is not None and summary['state']=='PASS' and len(summary['cases'])==len(expected)
print(json.dumps({'run':str(a.run),'cases':records,'complete':complete},indent=2))
raise SystemExit(0 if complete else 2)
