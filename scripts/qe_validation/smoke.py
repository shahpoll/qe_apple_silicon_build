"""Reference-bound SCF smoke calculation with durable evidence."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys
from .core import Campaign, ROOT, ValidationError, executable, mpi_command, positive_int, pw_metrics, scalar_assertion, select_suite, sha256

def smoke(args) -> int:
    ranks = positive_int(args.ranks, 'ranks')
    suite = select_suite(args.qe_bin)
    ref_path = ROOT / 'profiles/silicon-smoke.json'
    reference = json.loads(ref_path.read_text())
    input_path = ROOT / reference['input']
    pp_path = ROOT / reference['pseudopotential']
    for path, expected in [(input_path, reference['input_sha256']), (pp_path, reference['pseudopotential_sha256'])]:
        if not path.is_file() or sha256(path) != expected:
            raise ValidationError('FIXTURE_IDENTITY', f'Fixture identity mismatch: {path}', 'ERROR')
    campaign = Campaign(args.out_dir, ['silicon_scf'], suite, 'silicon-smoke')
    try:
        text = input_path.read_text().replace("pseudo_dir='../cases/common/pp'", f"pseudo_dir='{pp_path.parent}'")
        def validate(log, work):
            metrics = pw_metrics(log, ranks=ranks, require_fermi=True)
            assertions = [scalar_assertion(k, metrics[k], v['value'], v['atol'], units=v['units']) for k,v in reference['metrics'].items()]
            return {'metrics': metrics, 'assertions': assertions}
        campaign.case('silicon_scf', mpi_command(executable(suite, 'pw.x'), ['-in', '{input}'], ranks, args.direct),
                      text=text, validator=validate, timeout=args.timeout, metadata={'reference_sha256': sha256(ref_path), 'reference_status':reference['reference_status'], 'requested_ranks':ranks})
    finally:
        result = campaign.finish()
    return result

def main(argv=None) -> int:
    p=argparse.ArgumentParser(description='Strict SCF smoke test; logs are retained outside the source tree')
    p.add_argument('--qe-bin', type=Path)
    p.add_argument('--ranks', type=int, default=2)
    p.add_argument('--direct', action='store_true', help='Explicit one-process diagnostic; requires --ranks 1')
    p.add_argument('--out-dir', type=Path)
    p.add_argument('--timeout', type=float, default=180)
    args=p.parse_args(argv)
    try:
        return smoke(args)
    except ValidationError as exc:
        print(json.dumps({'state':exc.state, 'reason':exc.reason, 'detail':str(exc)}), file=sys.stderr)
        return 2
