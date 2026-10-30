"""Strict results, isolated attempts, bounded processes, and scientific parsers.

No plotting or third-party dependency is required to produce numerical verdicts.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import signal
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = 1
STATES = {'PASS', 'FAIL', 'ERROR', 'BLOCKED', 'SKIP', 'NOT_RUN'}
NUMBER = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eEdD][-+]?\d+)?|[-+]?(?:nan|inf(?:inity)?)'


class ValidationError(RuntimeError):
    def __init__(self, reason: str, message: str, state: str = 'FAIL'):
        super().__init__(message)
        self.reason, self.state = reason, state


def utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, value: object) -> None:
    """Atomic finite-only JSON; do not use this to rewrite old attempt records."""
    payload = json.dumps(value, indent=2, allow_nan=False) + '\n'
    tmp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    with tmp.open('x', encoding='utf-8') as f:
        f.write(payload)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def finite(value: object, name: str = 'metric') -> float:
    try:
        result = float(str(value).replace('D', 'E').replace('d', 'e'))
    except (ValueError, TypeError) as exc:
        raise ValidationError('METRIC_PARSE', f'{name}: invalid number {value!r}', 'ERROR') from exc
    if not math.isfinite(result):
        raise ValidationError('METRIC_NONFINITE', f'{name}: nonfinite value {value!r}')
    return result


def scalar_assertion(name: str, observed: float, reference: float, atol: float, rtol: float = 0.0, units: str = '') -> dict:
    observed, reference = finite(observed, name), finite(reference, name + ' reference')
    atol, rtol = finite(atol), finite(rtol)
    if atol < 0 or rtol < 0:
        raise ValidationError('CONFIG_TOLERANCE', 'Negative tolerance', 'ERROR')
    delta = observed - reference
    limit = atol + rtol * abs(reference)
    return dict(name=name, observed=observed, reference=reference, delta=delta,
                limit=limit, units=units, passed=abs(delta) <= limit)


def positive_int(value: object, name: str) -> int:
    try:
        n = int(value)
    except (ValueError, TypeError) as exc:
        raise ValidationError('CONFIG_INTEGER', f'{name} must be an integer', 'ERROR') from exc
    if n <= 0:
        raise ValidationError('CONFIG_INTEGER', f'{name} must be positive', 'ERROR')
    return n


def parse_ranks(value: str) -> list[int]:
    ranks = [positive_int(v.strip(), 'rank') for v in value.split(',') if v.strip()]
    if not ranks or len(ranks) != len(set(ranks)):
        raise ValidationError('COVERAGE_RANKS', 'Rank sweep must be nonempty and distinct', 'ERROR')
    return ranks


def runtime_env() -> dict[str, str]:
    env = os.environ.copy()
    for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'MKL_NUM_THREADS'):
        env[name] = '1'
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    return env


def select_suite(explicit: Path | str | None = None) -> Path:
    env_bin = os.environ.get('QE_BIN_PATH')
    env_pw = os.environ.get('QE_PW_BIN')
    candidate = Path(explicit).expanduser() if explicit is not None else Path(env_bin).expanduser() if env_bin else Path(env_pw).expanduser().parent if env_pw else None
    if candidate is None:
        path_pw = shutil.which('pw.x')
        candidates = [Path.home() / 'opt/qe-7.5/bin']
        if path_pw:
            candidates.append(Path(path_pw).resolve().parent)
        candidate = next((p for p in candidates if (p / 'pw.x').is_file()), None)
    if candidate is None or not candidate.is_dir():
        raise ValidationError('PATH_SELECTION', 'Select an existing QE suite with --qe-bin or QE_BIN_PATH', 'BLOCKED')
    candidate = candidate.resolve()
    if env_pw and Path(env_pw).expanduser().resolve() != (candidate / 'pw.x').resolve():
        raise ValidationError('PATH_CONFLICT', 'QE_PW_BIN conflicts with the selected suite', 'ERROR')
    if explicit is not None and env_bin and Path(env_bin).expanduser().resolve() != candidate:
        raise ValidationError('PATH_CONFLICT', 'QE_BIN_PATH conflicts with --qe-bin', 'ERROR')
    executable(candidate, 'pw.x')
    return candidate


def executable(suite: Path, name: str) -> Path:
    if Path(name).name != name:
        raise ValidationError('PATH_SELECTION', 'Executable must be a suite member name', 'ERROR')
    path = suite / name
    if not path.is_file() or not os.access(path, os.X_OK):
        raise ValidationError('EXECUTABLE_MISSING', f'Missing executable in selected suite: {path}', 'BLOCKED')
    return path.resolve()


def mpi_command(exe: Path, args: list[str], ranks: int, direct: bool = False, binding: list[str] | None = None) -> list[str]:
    ranks = positive_int(ranks, 'ranks')
    if direct:
        if ranks != 1:
            raise ValidationError('MPI_DIRECT_RANKS', 'Direct execution requires ranks=1', 'ERROR')
        return [str(exe), *args]
    launcher = os.environ.get('QE_MPI_LAUNCHER') or shutil.which('mpirun')
    if not launcher or not Path(launcher).is_file():
        raise ValidationError('MPI_LAUNCHER_MISSING', 'mpirun unavailable; select QE_MPI_LAUNCHER', 'BLOCKED')
    # No retry, binding speculation, or serial replacement.
    return [str(Path(launcher).resolve()), '-np', str(ranks), *(binding if binding is not None else ['--bind-to', 'none']), str(exe), *args]


def safe_new_directory(requested: Path | None, prefix: str = 'qe') -> Path:
    if requested is None:
        base = Path(os.environ.get('QE_RUNS_DIR', str(Path.home() / '.local/state/qe/runs'))).expanduser()
        requested = base / (prefix + '-' + dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S') + '-' + uuid.uuid4().hex[:8])
    original = requested.expanduser().absolute()
    if original.is_symlink():
        raise ValidationError('OUTPUT_SYMLINK', f'Refusing symlink output: {original}', 'ERROR')
    target = original.resolve()
    home = Path.home().resolve()
    if target in (Path('/'), home) or target in ROOT.parents or target == ROOT or target.is_relative_to(ROOT):
        raise ValidationError('OUTPUT_PROTECTED', f'Run output must be outside source/package trees: {target}', 'ERROR')
    if target.exists():
        raise ValidationError('OUTPUT_EXISTS', f'Output already exists; choose a new attempt directory: {target}', 'ERROR')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.mkdir(exist_ok=False)
    write_json(target / 'ownership.json', {'schema': SCHEMA, 'purpose': 'qe-run', 'path': str(target), 'created_utc': utc(), 'id': uuid.uuid4().hex})
    return target


def source_identity() -> dict:
    files = {}
    for folder in ('scripts', 'bin', 'inputs', 'profiles', 'fixtures/upstream-qe75', 'cases/common/scripts', 'cases/si/pwtk/scripts', 'cases/si/convergence'):
        for p in sorted((ROOT / folder).rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts and not p.is_symlink():
                files[str(p.relative_to(ROOT))] = sha256(p)
    for name in ('install.sh', 'CMakePresets.json', 'README.md'):
        if (ROOT/name).is_file():files[name]=sha256(ROOT/name)
    return {'files': files, 'sha256': hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()}


class Campaign:
    def __init__(self, out_dir: Path | None, expected: list[str], suite: Path | None = None, profile: str = 'custom'):
        if not expected or len(set(expected)) != len(expected) or any(not re.fullmatch(r'[A-Za-z0-9_.-]+', c) for c in expected):
            raise ValidationError('CASE_INVENTORY', 'Expected cases must be nonempty, distinct, and safe IDs', 'ERROR')
        self.root = safe_new_directory(out_dir)
        self.expected, self.suite, self.records = expected, suite, {}
        (self.root / 'cases').mkdir()
        (self.root / 'work').mkdir()
        identity=source_identity()
        for rel in identity['files']:
            target=self.root/'source'/rel
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(ROOT/rel,target)
        write_json(self.root / 'campaign.json', dict(schema=SCHEMA, expected_cases=expected, profile=profile,
                   created_utc=utc(), suite=str(suite) if suite else None, source=identity))
        write_json(self.root / 'environment.json', dict(platform=platform.platform(), machine=platform.machine(),
                   python=sys.version, threads={k: runtime_env()[k] for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS', 'MKL_NUM_THREADS')}))
        self.event('CAMPAIGN_STARTED')

    def event(self, kind: str, **fields: object) -> None:
        with (self.root / 'events.jsonl').open('a', encoding='utf-8') as f:
            f.write(json.dumps(dict(utc=utc(), kind=kind, **fields), allow_nan=False) + '\n')
            f.flush()
            os.fsync(f.fileno())

    def case(self, case_id: str, command: list[str] | None, *, text: str | None = None, validator=None,
             cwd: Path | None = None, stdin: str | None = None, timeout: float = 1800,
             parents: dict[str, str] | None = None, blocked: str | None = None, metadata: dict | None = None) -> dict:
        if case_id not in self.expected or case_id in self.records:
            raise ValidationError('CASE_INVENTORY', f'Unexpected/duplicate case: {case_id}', 'ERROR')
        case_dir = self.root / 'cases' / case_id
        case_dir.mkdir()
        attempt = case_dir / 'attempt-001'
        attempt.mkdir()
        (attempt / 'work').mkdir()
        work = cwd or attempt / 'work'
        if not work.resolve().is_relative_to(self.root):
            raise ValidationError('SCRATCH_BOUNDARY', 'Case work must belong to this campaign', 'ERROR')
        if text is not None:
            (attempt / 'input.in').write_text(text, encoding='utf-8')
            command = [str(x).replace('{input}', str(attempt / 'input.in')) for x in command or []]
        if stdin is not None:
            (attempt/'stdin.in').write_text(stdin,encoding='utf-8')
        manifest = dict(schema=SCHEMA, case=case_id, attempt='attempt-001', command=command,
                        cwd=str(work), parents=parents or {}, started_utc=utc(), timeout_s=timeout,
                        input_sha256=sha256(attempt / 'input.in') if text is not None else None,
                        stdin_sha256=sha256(attempt/'stdin.in') if stdin is not None else None,
                        metadata=metadata or {})
        if command:
            manifest['executables'] = {str(Path(x).resolve()): sha256(Path(x).resolve()) for x in command if Path(x).is_file() and os.access(x,os.X_OK)}
        write_json(attempt / 'manifest.json', manifest)
        self.event('CASE_STARTED', case=case_id, attempt='attempt-001')
        record = dict(schema=SCHEMA, case=case_id, state='ERROR', reasons=[], metrics={}, assertions=[],
                      attempt='attempt-001', evidence=str(attempt.relative_to(self.root)))
        started = time.monotonic()
        try:
            if blocked:
                raise ValidationError('PREREQUISITE_FAILED', blocked, 'BLOCKED')
            for path, digest in (parents or {}).items():
                p = Path(path)
                if not p.is_file() or sha256(p) != digest:
                    raise ValidationError('PARENT_HASH_MISMATCH', str(p), 'BLOCKED')
            if command:
                process = run_process(command, work, attempt, timeout, stdin)
                record.update(process)
                if process['reason']:
                    raise ValidationError(process['reason'], process['detail'], 'ERROR' if process['reason'] == 'TIMEOUT' else 'FAIL')
                log = (attempt / 'stdout.log').read_text(errors='replace') + '\n' + (attempt / 'stderr.log').read_text(errors='replace')
            else:
                log = ''
            if validator:
                data = validator(log, work) or {}
                record['metrics'] = data.get('metrics', {})
                record['assertions'] = data.get('assertions', [])
                # Force finite JSON validation before granting PASS.
                json.dumps(data, allow_nan=False)
                if any(not a['passed'] for a in record['assertions']):
                    raise ValidationError('NUMERICAL_DISAGREEMENT', 'Required numerical assertion failed')
            record['state'] = 'PASS'
        except ValidationError as exc:
            record.update(state=exc.state, reasons=[exc.reason], detail=str(exc))
        except (KeyboardInterrupt, SystemExit):
            record.update(state='ERROR', reasons=['INTERRUPTED'], detail='Execution interrupted')
            raise
        except Exception as exc:
            record.update(state='ERROR', reasons=['HARNESS_ERROR'], detail=repr(exc))
        finally:
            record.update(duration_s=time.monotonic()-started, finished_utc=utc())
            record['artifacts'] = {str(p.relative_to(attempt)): sha256(p) for p in attempt.iterdir() if p.is_file()}
            write_json(attempt / 'result.json', record)
            if record['state'] != 'PASS':
                write_json(attempt / 'failure.json', dict(record, next_action='Inspect preserved inputs/logs and typed reason before a new attempt; do not modify tolerances.'))
            write_json(case_dir / 'case-result.json', record)
            self.records[case_id] = record
            self.event('CASE_FINISHED', case=case_id, state=record['state'], reasons=record['reasons'])
        return record

    def finish(self) -> int:
        for case in self.expected:
            if case not in self.records:
                self.case(case, None, blocked='Campaign ended before this expected case ran')
        cases = []
        for cid in self.expected:
            record=self.records[cid]
            path=self.root/'cases'/cid/'case-result.json'
            try:
                if json.loads(path.read_text())!=record:
                    raise ValueError('Case record differs from the finalized attempt')
                attempt=self.root/record['evidence']
                for rel,digest in record['artifacts'].items():
                    file=attempt/rel
                    if not file.is_file() or sha256(file)!=digest:
                        raise ValueError('Evidence hash mismatch: '+rel)
            except Exception as exc:
                record=dict(record,state='ERROR',reasons=['EVIDENCE_INVALID'],detail=str(exc))
            cases.append(record)
        fail = any(c['state'] == 'FAIL' for c in cases)
        incomplete = any(c['state'] != 'PASS' for c in cases)
        state = 'FAIL' if fail else 'INCOMPLETE' if incomplete else 'PASS'
        counts = {s: sum(c['state'] == s for c in cases) for s in sorted(STATES)}
        summary = dict(schema=SCHEMA, state=state, expected_count=len(self.expected), counts=counts, cases=cases)
        write_json(self.root / 'summary.json', summary)
        lines = ['# QE validation report', '', f'State: **{state}**', '',
                 'This verdict covers the frozen cases below, on this exact configuration.', '',
                 '| Case | State | Reason |', '|---|---|---|']
        lines += [f"| {c['case']} | {c['state']} | {', '.join(c['reasons'])} |" for c in cases]
        (self.root / 'VALIDATION_REPORT.md').write_text('\n'.join(lines) + '\n')
        self.event('CAMPAIGN_FINISHED', state=state, counts=counts)
        print(json.dumps(dict(state=state, counts=counts, output=str(self.root)), indent=2))
        return 1 if fail else 2 if incomplete else 0


def run_process(command: list[str], cwd: Path, attempt: Path, timeout: float, stdin: str | None = None) -> dict:
    if timeout <= 0:
        raise ValidationError('CONFIG_TIMEOUT', 'Timeout must be positive', 'ERROR')
    proc = None
    reason, detail = None, ''
    try:
        with (attempt / 'stdout.log').open('w') as stdout, (attempt / 'stderr.log').open('w') as stderr:
            proc = subprocess.Popen(command, cwd=cwd, env=runtime_env(), stdin=subprocess.PIPE if stdin is not None else subprocess.DEVNULL,
                                    stdout=stdout, stderr=stderr, text=True, start_new_session=True)
            try:
                proc.communicate(input=stdin, timeout=timeout)
            except subprocess.TimeoutExpired:
                stop_process_group(proc)
                reason, detail = 'TIMEOUT', f'Exceeded {timeout} seconds; process group terminated'
            except BaseException:
                stop_process_group(proc)
                raise
        if proc.returncode and not reason:
            reason, detail = 'PROCESS_EXIT', f'Command exited {proc.returncode}; see stdout/stderr'
        stop_process_group(proc)
        return dict(exit_code=proc.returncode, reason=reason, detail=detail)
    except FileNotFoundError as exc:
        raise ValidationError('EXECUTABLE_MISSING', str(exc), 'BLOCKED') from exc


def stop_process_group(proc: subprocess.Popen) -> None:
    # Kill the group even if the launcher has exited but descendants remain.
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        proc.wait(timeout=3)
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    proc.wait()


def final_log(text: str) -> str:
    starts = list(re.finditer(r'^\s*Program\s+\S+\s+v\.', text, re.M))
    if len(starts) > 1:
        raise ValidationError('MIXED_ATTEMPTS', 'More than one QE program invocation in this attempt log')
    return text


def completion(text: str) -> None:
    final_log(text)
    version=re.search(r'^\s*Program\s+(\S+)\s+v\.([^\s]+)',text,re.M)
    supported={'EPW':{'6.0'}}  # EPW 6.0 is bundled in pinned QE 7.5.
    if version and version.group(2) not in supported.get(version.group(1),{'7.5'}):
        raise ValidationError('OUTPUT_VERSION_UNSUPPORTED','Runtime module version is outside the pinned QE 7.5 suite','ERROR')
    epw_complete=bool(version and version.group(1)=='EPW' and re.search(r'Total program execution\s+EPW\s*:\s*[\d.]+s CPU\s+[\d.]+s WALL',text))
    xspectra_complete='END JOB XSpectra' in text and '... End STEP 2 ...' in text
    if 'JOB DONE.' not in text and not epw_complete and not xspectra_complete:
        raise ValidationError('COMPLETION_MISSING', 'QE completion marker missing')
    if re.search(r'Error in routine|convergence NOT achieved|Maximum number of iterations reached|\bNaN\b|\bInfinity\b', text, re.I):
        raise ValidationError('CALCULATION_ERROR', 'Calculation error, nonconvergence, or nonfinite output')
    if re.search(r'IEEE_INVALID_FLAG|IEEE_DIVIDE_BY_ZERO|IEEE_OVERFLOW_FLAG',text):
        raise ValidationError('FLOATING_POINT_EXCEPTION','Severe floating-point flag requires diagnosis before qualification')


def observed_ranks(text: str) -> int:
    ranks = [int(x) for x in re.findall(r'running on\s+(\d+)\s+processors', text)]
    if not ranks and 'Serial version' in text:
        ranks = [1]
    if len(ranks) != 1:
        raise ValidationError('MPI_RANK_UNKNOWN', 'Exactly one actual rank count is required')
    return ranks[0]


def last_number(text: str, pattern: str, name: str, required: bool = True) -> float | None:
    matches = re.findall(pattern, text, re.M | re.I)
    if not matches:
        if required:
            raise ValidationError('METRIC_MISSING', f'{name} not found', 'ERROR')
        return None
    return finite(matches[-1], name)


def pw_metrics(text: str, *, calculation: str = 'scf', ranks: int | None = None, require_fermi: bool = False) -> dict:
    completion(text)
    if calculation in ('scf', 'relax', 'vc-relax', 'md') and 'convergence has been achieved' not in text:
        raise ValidationError('SCF_NOT_CONVERGED', 'Final SCF convergence evidence missing')
    # For iterative ionic runs, ensure the last SCF block converged.
    bfgs='End of BFGS Geometry Optimization' in text
    damped=bool(re.search(r'(?:Wentzcovitch )?Damped (?:Cell )?Dynamics Minimization:\s*convergence achieved, Efinal=',text,re.I))
    if calculation in ('relax', 'vc-relax') and not (bfgs or damped):
        raise ValidationError('OPTIMIZATION_NOT_CONVERGED', 'Explicit geometry convergence missing')
    metrics = {}
    if calculation != 'nscf' and calculation != 'bands':
        metrics['total_energy_ry'] = last_number(text, rf'^\s*!\s+total energy\s*=\s*({NUMBER})', 'total energy')
    fermi = last_number(text, rf'the Fermi energy is\s+({NUMBER})', 'Fermi energy', require_fermi)
    if fermi is not None:
        metrics['fermi_ev'] = fermi
    for key, pattern in [('electrons', rf'number of electrons\s*=\s*({NUMBER})'), ('total_force_ry_bohr', rf'Total force\s*=\s*({NUMBER})'), ('magnetization_muB', rf'total magnetization\s*=\s*({NUMBER})')]:
        value = last_number(text, pattern, key, False)
        if value is not None:
            metrics[key] = value
    if ranks is not None:
        actual = observed_ranks(text)
        metrics['observed_ranks'] = actual
        if actual != ranks:
            raise ValidationError('MPI_RANK_MISMATCH', f'Requested {ranks}, observed {actual}')
    return metrics


def read_table(path: Path) -> list[list[float]]:
    rows = []
    for line in path.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        rows.append([finite(x, str(path)) for x in line.split()])
    if not rows or len({len(r) for r in rows}) != 1:
        raise ValidationError('ARTIFACT_SHAPE', f'Empty/ragged table: {path}', 'ERROR')
    return rows


def read_bands(path: Path) -> tuple[list[float], list[list[float]]]:
    blocks = re.split(r'\n\s*\n', path.read_text().strip())
    bands, grids = [], []
    for block in blocks:
        rows = [[finite(x) for x in line.split()] for line in block.splitlines() if line.strip()]
        if any(len(r) != 2 for r in rows):
            raise ValidationError('ARTIFACT_SHAPE', 'Band rows must contain coordinate and energy', 'ERROR')
        grids.append([r[0] for r in rows]); bands.append([r[1] for r in rows])
    if not bands or not grids[0] or any(g != grids[0] for g in grids):
        raise ValidationError('GRID_MISMATCH', 'Inconsistent band coordinates', 'ERROR')
    return grids[0], bands


def gaps(bands: list[list[float]], fermi: float) -> tuple[float, float]:
    fermi = finite(fermi)
    if not bands or not bands[0] or len({len(b) for b in bands}) != 1:
        raise ValidationError('ARTIFACT_SHAPE', 'Inconsistent bands', 'ERROR')
    v, c = [], []
    for column in zip(*bands):
        column = [finite(x) for x in column]
        val, con = [x for x in column if x <= fermi], [x for x in column if x > fermi]
        if not val or not con:
            raise ValidationError('BAND_COVERAGE', 'Valence and empty conduction states required at every k point')
        v.append(max(val)); c.append(min(con))
    return finite(min(c)-max(v)), finite(min(ci-vi for ci, vi in zip(c, v)))


def compare_arrays(a: list[list[float]], b: list[list[float]], *, atol: float, grid_atol: float = 1e-10) -> dict:
    if len(a) != len(b) or not a or len({len(r) for r in a+b}) != 1:
        raise ValidationError('ARTIFACT_SHAPE', 'Comparison dimensions differ')
    if any(abs(finite(x[0])-finite(y[0])) > grid_atol for x,y in zip(a,b)):
        raise ValidationError('GRID_MISMATCH', 'Comparison coordinates differ')
    delta = max(abs(finite(x)-finite(y)) for rowa,rowb in zip(a,b) for x,y in zip(rowa[1:],rowb[1:]))
    return scalar_assertion('max_absolute_difference', delta, 0.0, atol)


def tree_manifest(path: Path) -> dict[str, str]:
    return {str(p.relative_to(path)): sha256(p) for p in sorted(path.rglob('*')) if p.is_file() and not p.is_symlink()}


def saved_parent(work: Path, prefix: str, expected_calculation: str | None = None) -> dict[str, str]:
    xml = work / 'tmp' / (prefix + '.save') / 'data-file-schema.xml'
    if not xml.is_file():
        raise ValidationError('PARENT_MISSING', str(xml), 'BLOCKED')
    if expected_calculation:
        import xml.etree.ElementTree as ET
        doc = ET.parse(xml)
        calc = doc.findtext('.//input/control_variables/calculation')
        if calc != expected_calculation:
            raise ValidationError('PARENT_CALCULATION', f'Expected {expected_calculation} parent, found {calc}', 'BLOCKED')
    return {str(xml): sha256(xml)}
