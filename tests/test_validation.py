"""Adversarial regression tests; injected calculations never count as QE physics."""
import contextlib
import io
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from qe_validation import core

VALID = '''Program PWSCF v.7.5 starts
Parallel version (MPI), running on 2 processors
number of electrons = 8.00
! total energy = -2.283927198D+01 Ry
the Fermi energy is 6.4346 ev
convergence has been achieved in 5 iterations
JOB DONE.
'''


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='qe-regression-')
        self.base = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def rejected(self, reason, fn, *args, **kwargs):
        with self.assertRaises(core.ValidationError) as ctx:
            fn(*args, **kwargs)
        self.assertEqual(reason, ctx.exception.reason)

    def test_finite_fortran_and_nonfinite(self):
        self.assertEqual(12.5, core.finite('1.25d1'))
        for value in ['nan', 'inf', '-inf', '1e999']:
            self.rejected('METRIC_NONFINITE', core.finite, value)

    def test_valid_completed_reference(self):
        m=core.pw_metrics(VALID, ranks=2, require_fermi=True)
        self.assertAlmostEqual(-22.83927198,m['total_energy_ry'])
        self.assertEqual(8,m['electrons'])

    def test_missing_completion(self):
        self.rejected('COMPLETION_MISSING',core.pw_metrics,VALID.replace('JOB DONE.',''))

    def test_nonconvergence_and_good_numbers(self):
        self.rejected('CALCULATION_ERROR',core.pw_metrics,VALID.replace('convergence has been achieved','convergence NOT achieved'))

    def test_missing_scf_convergence(self):
        self.rejected('SCF_NOT_CONVERGED',core.pw_metrics,VALID.replace('convergence has been achieved','other text'))

    def test_fixed_occupation_no_fermi(self):
        text=VALID.replace('the Fermi energy is 6.4346 ev\n','')
        self.assertNotIn('fermi_ev',core.pw_metrics(text))
        self.rejected('METRIC_MISSING',core.pw_metrics,text,require_fermi=True)

    def test_actual_ranks_required(self):
        self.rejected('MPI_RANK_MISMATCH',core.pw_metrics,VALID,ranks=4)
        self.rejected('MPI_RANK_UNKNOWN',core.pw_metrics,VALID.replace('running on 2 processors','unknown ranks'),ranks=2)

    def test_final_energy_not_first(self):
        text=VALID.replace('! total energy', '! total energy = -20 Ry\n! total energy')
        self.assertAlmostEqual(-22.83927198,core.pw_metrics(text)['total_energy_ry'])

    def test_mixed_attempts(self):
        self.rejected('MIXED_ATTEMPTS',core.pw_metrics,VALID+VALID)

    def test_nscf_separate_contract(self):
        text=VALID.replace('! total energy = -2.283927198D+01 Ry\n','').replace('convergence has been achieved in 5 iterations\n','')
        self.assertNotIn('total_energy_ry',core.pw_metrics(text,calculation='nscf',ranks=2))

    def test_geometry_requires_algorithm_convergence(self):
        self.rejected('OPTIMIZATION_NOT_CONVERGED',core.pw_metrics,VALID,calculation='vc-relax')
        core.pw_metrics(VALID+'Wentzcovitch Damped Cell Dynamics Minimization:\n convergence achieved, Efinal= -2\n',calculation='vc-relax')
        core.pw_metrics(VALID+'End of BFGS Geometry Optimization',calculation='relax')

    def test_upstream_extract_scalar_and_table_formats(self):
        from qe_validation.upstream import extract_metrics
        extractor=self.base/'extract.sh';extractor.write_text('cat "$1"\n')
        data=self.base/'data';data.write_text('e1\n-1.25D+01\nn1\n5\n')
        self.assertEqual({'e1':[-12.5],'n1':[5]},extract_metrics(extractor,'data',self.base))
        data.write_text('jx1 jy1 jz1\n1 2 3\n4 5 6\n')
        self.assertEqual({'jx1':[1,4],'jy1':[2,5],'jz1':[3,6]},extract_metrics(extractor,'data',self.base))
        data.write_text('jx1 jy1\n1\n')
        self.rejected('METRIC_SHAPE',extract_metrics,extractor,'data',self.base)

    def test_reference_and_boundary(self):
        self.assertFalse(core.scalar_assertion('energy',-17.83927198,-22.83927198,0.001)['passed'])
        self.assertTrue(core.scalar_assertion('boundary',0.125,0,0.125)['passed'])
        self.assertFalse(core.scalar_assertion('outside',0.25,0,0.125)['passed'])
        self.assertTrue(core.scalar_assertion('zero',0,0,0)['passed'])

    def test_rank_coverage(self):
        for value in ['', '1,1', '0', '-1']:
            with self.assertRaises(core.ValidationError):core.parse_ranks(value)
        self.assertEqual([1,2,4],core.parse_ranks('1,2,4'))

    def test_safe_output_preserves_unrelated_file(self):
        sentinel=self.base/'sentinel'; sentinel.write_text('keep')
        self.rejected('OUTPUT_EXISTS',core.safe_new_directory,self.base)
        self.assertEqual('keep',sentinel.read_text())
        for path in [Path('/'),Path.home(),core.ROOT,core.ROOT/'validation_reports/new']:
            self.rejected('OUTPUT_PROTECTED',core.safe_new_directory,path)

    def test_symlink_boundary(self):
        link=self.base/'link'; link.symlink_to(self.base)
        self.rejected('OUTPUT_SYMLINK',core.safe_new_directory,link)

    def test_independent_scratch(self):
        one=core.safe_new_directory(self.base/'one')
        two=core.safe_new_directory(self.base/'two')
        (one/'file').write_text('one');(two/'file').write_text('two')
        self.assertEqual('one',(one/'file').read_text())

    def test_exact_selection_no_fallback(self):
        with mock.patch.dict(os.environ,{},clear=True):
            self.rejected('PATH_SELECTION',core.select_suite,self.base/'missing')
            suite=self.base/'suite';suite.mkdir()
            self.rejected('EXECUTABLE_MISSING',core.executable,suite,'ph.x')

    def test_conflicting_selectors(self):
        one=self.base/'one';two=self.base/'two';one.mkdir();two.mkdir()
        for path in [one/'pw.x',two/'pw.x']:
            path.write_text('#!/bin/sh\nexit 0\n');path.chmod(0o755)
        with mock.patch.dict(os.environ,{'QE_PW_BIN':str(two/'pw.x')},clear=True):
            self.rejected('PATH_CONFLICT',core.select_suite,one)

    def test_gap_analytic_and_band_coverage(self):
        self.assertEqual((1.0,2.0),core.gaps([[0,1],[2,3]],1.5))
        self.rejected('BAND_COVERAGE',core.gaps,[[0,1]],2)
        self.rejected('METRIC_NONFINITE',core.gaps,[[0,math.nan],[2,3]],1.5)

    def test_coordinate_grid_checked(self):
        self.rejected('GRID_MISMATCH',core.compare_arrays,[[0,1],[1,2]],[[0,1],[2,2]],atol=1)
        self.assertFalse(core.compare_arrays([[0,1]],[[0,2]],atol=0.1)['passed'])

    def test_finite_json(self):
        with self.assertRaises(ValueError):core.write_json(self.base/'result.json',{'x':math.nan})
        self.assertFalse((self.base/'result.json').exists())

    def campaign(self, expected):
        with contextlib.redirect_stdout(io.StringIO()):
            return core.Campaign(self.base/'campaign',expected)

    def test_wrong_values_fail_campaign_and_are_retained(self):
        c=self.campaign(['scf'])
        r=c.case('scf',[sys.executable,'-c',f'print({VALID!r})'],validator=lambda log,work:{'metrics':core.pw_metrics(log),'assertions':[core.scalar_assertion('wrong',5,0,0.001)]})
        self.assertEqual('FAIL',r['state']);self.assertEqual(['NUMERICAL_DISAGREEMENT'],r['reasons'])
        with contextlib.redirect_stdout(io.StringIO()):self.assertEqual(1,c.finish())
        self.assertTrue((c.root/'cases/scf/attempt-001/failure.json').exists())

    def test_missing_case_blocks_complete_success(self):
        c=self.campaign(['one','two']);c.case('one',None,validator=lambda *_:{})
        with contextlib.redirect_stdout(io.StringIO()):self.assertEqual(2,c.finish())
        self.assertEqual('BLOCKED',c.records['two']['state'])

    def test_parser_error_is_durable(self):
        c=self.campaign(['scf'])
        r=c.case('scf',[sys.executable,'-c','print("JOB DONE.")'],validator=lambda log,work:core.pw_metrics(log))
        self.assertEqual('FAIL',r['state'])
        self.assertIn('SCF_NOT_CONVERGED',r['reasons'])

    def test_process_failure_no_retry(self):
        c=self.campaign(['exit'])
        r=c.case('exit',[sys.executable,'-c','print("JOB DONE.");raise SystemExit(7)'])
        self.assertEqual(7,r['exit_code']);self.assertEqual('FAIL',r['state'])
        self.assertEqual(1,len(list((c.root/'cases/exit').glob('attempt-*'))))

    def test_timeout_terminates_children(self):
        c=self.campaign(['hang'])
        script='import subprocess,sys,time,pathlib; p=subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"]); pathlib.Path("child.pid").write_text(str(p.pid)); time.sleep(30)'
        r=c.case('hang',[sys.executable,'-c',script],timeout=0.5)
        self.assertEqual(['TIMEOUT'],r['reasons'])
        pid=int((c.root/'cases/hang/attempt-001/work/child.pid').read_text())
        # A dead child may briefly remain a zombie; it must not be running.
        proc=subprocess.run(['ps','-p',str(pid),'-o','stat='],capture_output=True,text=True)
        self.assertTrue(not proc.stdout.strip() or proc.stdout.strip().startswith('Z'))

    def test_exited_parent_cannot_leave_running_child(self):
        c=self.campaign(['parent'])
        script='import subprocess,sys,pathlib; p=subprocess.Popen([sys.executable,"-c","import time; time.sleep(30)"]); pathlib.Path("child.pid").write_text(str(p.pid))'
        r=c.case('parent',[sys.executable,'-c',script],timeout=5)
        self.assertEqual('PASS',r['state'])
        pid=int((c.root/'cases/parent/attempt-001/work/child.pid').read_text())
        proc=subprocess.run(['ps','-p',str(pid),'-o','stat='],capture_output=True,text=True)
        self.assertTrue(not proc.stdout.strip() or proc.stdout.strip().startswith('Z'))

    def test_parent_hash_mismatch_blocks(self):
        c=self.campaign(['post']);p=c.root/'work/parent';p.write_text('old');digest=core.sha256(p);p.write_text('new')
        r=c.case('post',None,parents={str(p):digest})
        self.assertEqual('BLOCKED',r['state']);self.assertEqual(['PARENT_HASH_MISMATCH'],r['reasons'])

    def test_empty_duplicate_inventory(self):
        for ids in [[],['one','one'],['../escape']]:
            self.rejected('CASE_INVENTORY',core.Campaign,self.base/'out',ids)

    def test_evidence_corruption_blocks_aggregate(self):
        c=self.campaign(['one'])
        c.case('one',[sys.executable,'-c','print("kept")'])
        (c.root/'cases/one/attempt-001/stdout.log').write_text('tampered')
        with contextlib.redirect_stdout(io.StringIO()):self.assertEqual(2,c.finish())
        self.assertEqual('ERROR',json.loads((c.root/'summary.json').read_text())['cases'][0]['state'])

    def test_version_and_severe_flags(self):
        self.rejected('OUTPUT_VERSION_UNSUPPORTED',core.completion,VALID.replace('v.7.5','v.9.0'))
        self.rejected('FLOATING_POINT_EXCEPTION',core.completion,VALID+'IEEE_INVALID_FLAG')
        core.completion('Program EPW v.6.0 starts\nJOB DONE.\n')

    def test_band_parent_rejected_for_dos(self):
        work=self.base/'work';path=work/'tmp/silicon.save';path.mkdir(parents=True)
        (path/'data-file-schema.xml').write_text('<root><input><control_variables><calculation>bands</calculation></control_variables></input></root>')
        self.rejected('PARENT_CALCULATION',core.saved_parent,work,'silicon','nscf')

    def test_archive_extraction_refuses_traversal(self):
        from qe_validation.install import extract_archive
        import tarfile
        archive=self.base/'bad.tar'
        with tarfile.open(archive,'w') as tar:
            item=tarfile.TarInfo('../sentinel');item.size=4;tar.addfile(item,io.BytesIO(b'evil'))
        with self.assertRaises(tarfile.FilterError):extract_archive(archive,self.base/'extract')
        self.assertFalse((self.base/'sentinel').exists())

    def test_download_pin_required(self):
        from qe_validation.install import verified_download
        self.rejected('DOWNLOAD_CHECKSUM_REQUIRED',verified_download,'https://example.invalid','bad',self.base/'output',self.base)

    def test_missing_dylib_is_detected(self):
        if sys.platform!='darwin':self.skipTest('Mach-O fixture requires macOS')
        from qe_validation.linkage import inspect_binary
        lib=self.base/'libprobe.dylib';exe=self.base/'probe.x'
        (self.base/'library.c').write_text('int value(void) { return 3; }')
        (self.base/'main.c').write_text('extern int value(void); int main(void){return value()!=3;}')
        subprocess.run(['clang','-dynamiclib',str(self.base/'library.c'),'-Wl,-install_name,'+str(lib),'-o',str(lib)],check=True,capture_output=True)
        subprocess.run(['clang',str(self.base/'main.c'),str(lib),'-o',str(exe)],check=True,capture_output=True)
        inspect_binary(exe)
        lib.unlink()
        self.rejected('DYLIB_UNRESOLVED',inspect_binary,exe)

if __name__=='__main__':
    unittest.main()
