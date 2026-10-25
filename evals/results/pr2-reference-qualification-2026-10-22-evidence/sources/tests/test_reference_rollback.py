"""Behavior checks for the shipped, bounded POSIX reference, without providers."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'skills/flow-lean/scripts/rollback_reference.py'
sys.path.insert(0, str(ROOT / 'scripts'))
from check_rollback import check, digest, ORIGINAL, INSTALLED, CACHE, tree_snapshot
spec = importlib.util.spec_from_file_location('rollback_reference', SOURCE)
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)


def adapter():
    return {'command': [sys.executable, str(SOURCE), '--root', '{root}', '--records', '{records}',
                        '--backup', '{backup}', '--original-sha256', '{original_sha256}',
                        '--config-sha256', '{config_sha256}', '--cache-sha256', '{cache_sha256}',
                        '--writers-stopped'],
            'source_files': [str(SOURCE)], 'lock_kind': 'directory',
            'lock_path': '{root}/.rollback.lock'}


@unittest.skipUnless(os.name == 'posix', 'Reference explicitly requires POSIX metadata semantics')
class ReferenceRollbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name).resolve()
        self.root = self.base / 'root'; self.root.mkdir()
        (self.root / 'cache').mkdir()
        self.config = self.root / 'config.md'; self.config.write_bytes(INSTALLED)
        self.new = self.root / 'cache/new.json'; self.new.write_bytes(CACHE)
        self.backup = self.base / 'original'; self.backup.write_bytes(ORIGINAL)
        self.backup.chmod(0o640)
        os.utime(self.backup, ns=(1500000000000000000, 1500000000000000000))
        self.records = self.base / 'records'; self.records.mkdir()
        self.prior = self.records / 'prior'; self.prior.write_text('prior evidence')
        self.kwargs = dict(root=self.root, records=self.records, backup=self.backup,
                           original_sha256=digest(ORIGINAL), config_sha256=digest(INSTALLED),
                           cache_sha256=digest(CACHE), writers_stopped=True)

    def events(self):
        return [json.loads(line) for p in self.records.glob('rollback-*.jsonl')
                for line in p.read_text().splitlines()]

    def test_all_18_executable_scenarios(self):
        result = check(adapter())
        self.assertEqual(result['status'], 'PASS', result)
        self.assertEqual(len(result['results']), 18)

    def test_success_preserves_metadata_receipt_and_backup(self):
        before = self.backup.stat()
        result = reference.rollback(**self.kwargs)
        self.assertEqual(result['status'], 'complete')
        self.assertEqual(self.config.read_bytes(), ORIGINAL)
        after = self.config.stat()
        for name in ('st_mode', 'st_uid', 'st_gid', 'st_mtime_ns'):
            self.assertEqual(getattr(before, name), getattr(after, name), name)
        self.assertEqual(self.backup.read_bytes(), ORIGINAL)
        self.assertEqual(self.prior.read_text(), 'prior evidence')
        self.assertFalse((self.root / '.rollback.lock').exists())
        self.assertEqual([e['stage'] for e in self.events()], ['validated', 'restored', 'verified', 'complete'])
        self.assertEqual(self.events()[0]['postimages']['config']['sha256'], digest(INSTALLED))
        self.assertEqual(self.events()[-2]['config']['sha256'], digest(ORIGINAL))
        self.assertFalse(self.events()[-2]['cache_directory_retained'])
        # Idempotency is deliberately refused, not inferred from original-looking content.
        with self.assertRaises(reference.Refusal): reference.rollback(**self.kwargs)
        self.assertFalse((self.root / '.rollback.lock').exists())

    def test_nonempty_cache_preserves_nested_and_link_entries(self):
        nested = self.root / 'cache/other'; nested.mkdir()
        (nested / 'data').write_text('concurrent work')
        (nested / 'link').symlink_to(self.backup)
        before = tree_snapshot(nested)
        self.assertEqual(reference.rollback(**self.kwargs)['status'], 'complete')
        self.assertEqual(tree_snapshot(nested), before)
        self.assertTrue(self.events()[-2]['cache_directory_retained'])
        self.assertFalse(self.new.exists())

    def test_writer_ack_required_before_any_write(self):
        self.kwargs['writers_stopped'] = False
        before = tree_snapshot(self.base)
        with self.assertRaises(reference.Refusal): reference.rollback(**self.kwargs)
        self.assertEqual(tree_snapshot(self.base), before)

    def test_hardlinks_and_symlinked_root_or_records_are_refused(self):
        for target in ('backup', 'root', 'records', 'config'):
            with self.subTest(target=target):
                if target == 'backup':
                    os.link(self.backup, self.base / 'alias')
                elif target == 'config':
                    os.link(self.config, self.base / 'alias')
                else:
                    alias = self.base / 'alias'; alias.symlink_to(self.kwargs[target], target_is_directory=True)
                    self.kwargs[target] = alias
                before = tree_snapshot(self.base)
                with self.assertRaises(reference.Refusal): reference.rollback(**self.kwargs)
                self.assertEqual(tree_snapshot(self.base), before)
                (self.base / 'alias').unlink()
                self.kwargs['root'], self.kwargs['records'] = self.root, self.records

    def test_records_and_backup_inside_root_are_rejected(self):
        for field, value in [('records', self.root / 'cache'), ('backup', self.new)]:
            with self.subTest(field=field):
                args = {**self.kwargs, field: value}
                before = tree_snapshot(self.base)
                with self.assertRaises(reference.Refusal): reference.rollback(**args)
                self.assertEqual(tree_snapshot(self.base), before)

    def test_io_failure_before_replace_preserves_targets_and_cleans_owned_paths(self):
        for op in ('replace', 'fchmod', 'fsync'):
            with self.subTest(operation=op):
                before = tree_snapshot(self.root)
                with patch.object(reference.os, op, side_effect=OSError('injected ' + op)):
                    with self.assertRaises(OSError): reference.rollback(**self.kwargs)
                self.assertEqual(tree_snapshot(self.root), before)
                self.assertEqual(self.backup.read_bytes(), ORIGINAL)
                self.assertEqual(self.prior.read_text(), 'prior evidence')

    def test_failure_after_restore_is_not_success_and_preserves_evidence(self):
        real_unlink = Path.unlink
        def fail_target(path, *args, **kwargs):
            if path == self.new: raise OSError('injected cache deletion failure')
            return real_unlink(path, *args, **kwargs)
        with patch.object(Path, 'unlink', fail_target):
            with self.assertRaises(OSError): reference.rollback(**self.kwargs)
        self.assertEqual(self.config.read_bytes(), ORIGINAL)
        self.assertEqual(self.new.read_bytes(), CACHE)
        self.assertFalse((self.root / '.rollback.lock').exists())
        self.assertEqual(self.events()[-1]['stage'], 'failed')
        self.assertNotIn('complete', [e['stage'] for e in self.events()])
        self.assertEqual(self.backup.read_bytes(), ORIGINAL)

    def test_foreign_lock_contents_are_never_deleted(self):
        lock = self.root / '.rollback.lock'
        real_replace = reference.os.replace
        def changed_lock(*args):
            (lock / 'foreign').write_text('keep')
            return real_replace(*args)
        with patch.object(reference.os, 'replace', side_effect=changed_lock):
            with self.assertRaises(reference.Refusal): reference.rollback(**self.kwargs)
        self.assertEqual((lock / 'foreign').read_text(), 'keep')
        self.assertNotIn('complete', [e['stage'] for e in self.events()])

    def test_modified_lock_owner_is_preserved(self):
        owner = self.root / '.rollback.lock/owner.json'
        real_replace = reference.os.replace
        def changed_owner(*args):
            owner.write_text('different owner')
            return real_replace(*args)
        with patch.object(reference.os, 'replace', side_effect=changed_owner):
            with self.assertRaises(reference.Refusal): reference.rollback(**self.kwargs)
        self.assertEqual(owner.read_text(), 'different owner')
        self.assertNotIn('complete', [e['stage'] for e in self.events()])

    def test_cli_argument_errors_are_clean_and_inert(self):
        for args in ([], ['--root'], ['--help'], ['--bogus']):
            run = subprocess.run([sys.executable, str(SOURCE), *args], capture_output=True, text=True)
            self.assertEqual(run.returncode, 0 if args == ['--help'] else 2)
            self.assertNotIn('Traceback', run.stderr)
        before = tree_snapshot(self.base)
        values = {'root': str(self.root), 'records': str(self.records), 'backup': str(self.backup),
                  'original_sha256': digest(ORIGINAL), 'config_sha256': digest(INSTALLED), 'cache_sha256': digest(CACHE)}
        command = [p.format_map(values) for p in adapter()['command']]
        run = subprocess.run(command[:-1], capture_output=True, text=True)
        self.assertEqual(run.returncode, 3)
        self.assertEqual(tree_snapshot(self.base), before)


class ReferencePortabilityTests(unittest.TestCase):
    def test_windows_is_explicitly_refused_before_filesystem_access(self):
        with patch.object(reference.os, 'name', 'nt'):
            with self.assertRaisesRegex(reference.Refusal, 'requires POSIX'):
                reference.rollback(root='unused', records='unused', backup='unused',
                                   original_sha256='unused', config_sha256='unused',
                                   cache_sha256='unused', writers_stopped=True)


if __name__ == '__main__': unittest.main()
