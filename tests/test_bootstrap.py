"""Exercise the actual curl bootstrap against local, checksum-pinned packages."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class BootstrapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package_tmp = tempfile.TemporaryDirectory(prefix='qe-package-test-')
        cls.package = Path(cls.package_tmp.name) / 'package'
        subprocess.run(
            [sys.executable, '-B', str(ROOT / 'scripts/package_release.py'),
             '--out-dir', str(cls.package)],
            check=True, capture_output=True, text=True,
        )
        cls.archive = cls.package / 'qe-manager.tar.gz'
        cls.digest = hashlib.sha256(cls.archive.read_bytes()).hexdigest()

    @classmethod
    def tearDownClass(cls):
        cls.package_tmp.cleanup()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='qe-bootstrap-')
        self.base = Path(self.tmp.name)
        self.prefix = self.base / 'manager with spaces μ'
        self.bin_dir = self.base / 'public bin μ'

    def tearDown(self):
        self.tmp.cleanup()

    def invoke(self, *args):
        env = dict(os.environ, QE_PYTHON=sys.executable)
        return subprocess.run(
            ['bash', str(ROOT / 'install.sh'), '--local-file',
             '--manager-prefix', str(self.prefix), '--bin-dir', str(self.bin_dir),
             *map(str, args)],
            cwd=self.base, env=env, capture_output=True, text=True, timeout=60,
        )

    def manifest(self, **changes):
        data = dict(schema=1, kind='qe-manager', version='local-test',
                    source_url=self.archive.as_uri(), source_sha256=self.digest)
        data.update(changes)
        path = self.base / 'manifest.json'
        path.write_text(json.dumps(data))
        return path

    def terminal(self):
        records = list((self.prefix / 'attempts').glob('*/result.json'))
        self.assertEqual(1, len(records))
        return json.loads(records[0].read_text())

    def test_manifest_install_and_installed_dispatch(self):
        result = self.invoke('--manifest-url', self.manifest().as_uri())
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual('PASS', self.terminal()['state'])
        command = self.bin_dir / 'qe-apple-silicon-build'
        help_result = subprocess.run([str(command), 'doctor', '--help'],
                                     capture_output=True, text=True)
        self.assertEqual(0, help_result.returncode, help_result.stderr)
        self.assertFalse(list((self.prefix / 'current').resolve().rglob('*.pyc')))

    def test_manifest_hash_mismatch_never_activates(self):
        result = self.invoke('--manifest-url', self.manifest(source_sha256='0' * 64).as_uri())
        self.assertEqual(1, result.returncode)
        self.assertIn('DOWNLOAD_HASH_MISMATCH', result.stderr)
        self.assertEqual('FAIL', self.terminal()['state'])
        self.assertFalse((self.prefix / 'current').exists())
        self.assertFalse((self.bin_dir / 'qe-apple-silicon-build').exists())

    def test_manifest_rejects_invalid_metadata(self):
        result = self.invoke('--manifest-url', self.manifest(source_sha256=None).as_uri())
        self.assertEqual(1, result.returncode)
        self.assertIn('MANAGER_MANIFEST_INVALID', result.stderr)
        self.assertFalse((self.prefix / 'current').exists())

    def test_explicit_archive_requires_checksum_pair(self):
        result = self.invoke('--source-url', self.archive.as_uri())
        self.assertEqual(2, result.returncode)
        self.assertIn('Supply both', result.stderr)
        self.assertFalse(self.prefix.exists())

    def test_explicit_archive_preserves_unrelated_command(self):
        self.bin_dir.mkdir()
        sentinel = self.bin_dir / 'qe-apple-silicon-build'
        sentinel.write_text('unrelated command\n')
        result = self.invoke('--source-url', self.archive.as_uri(),
                             '--source-sha256', self.digest)
        self.assertEqual(1, result.returncode)
        self.assertIn('PUBLIC_ENTRYPOINT_CONFLICT', result.stderr)
        self.assertEqual('unrelated command\n', sentinel.read_text())
        self.assertFalse((self.prefix / 'current').exists())


if __name__ == '__main__':
    unittest.main()
