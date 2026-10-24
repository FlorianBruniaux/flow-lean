"""Exercise the documented ranges in a disposable diverged history; no remote writes."""
from pathlib import Path
import subprocess
import tempfile
import unittest


class GitRangeContractTests(unittest.TestCase):
    def test_remote_only_direction_and_recovery_ref(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            def git(*args):
                return subprocess.check_output(['git', *args], cwd=root, text=True, stderr=subprocess.PIPE).strip()
            git('init', '-b', 'main')
            git('config', 'user.name', 'Fixture'); git('config', 'user.email', 'fixture@example.invalid')
            git('config', 'commit.gpgsign', 'false'); git('config', 'core.hooksPath', str(root / 'no-hooks'))
            git('commit', '--allow-empty', '-m', 'base')
            git('checkout', '-b', 'remote-fixture')
            git('commit', '--allow-empty', '-m', 'remote-only')
            remote = git('rev-parse', 'HEAD')
            git('update-ref', 'refs/remotes/origin/main', remote)
            git('checkout', 'main'); git('commit', '--allow-empty', '-m', 'local-only')
            self.assertEqual(git('log', '--format=%s', 'main..origin/main'), 'remote-only')
            self.assertEqual(git('log', '--format=%s', 'origin/main..main'), 'local-only')
            git('branch', 'recovery/remote-main', remote)
            self.assertEqual(git('rev-parse', 'recovery/remote-main'), remote)
            self.assertNotEqual(git('rev-parse', 'main'), remote)


if __name__ == '__main__': unittest.main()
