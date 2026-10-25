import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_rollback import check, SCENARIOS


def adapter(mutant="none"):
    return {"command": [sys.executable, str(ROOT / "tests/fixtures/rollback_program.py"),
                        "{root}", "{records}", "{backup}", "{original_sha256}",
                        "{config_sha256}", "{cache_sha256}", mutant],
            "source_files": [str(ROOT / "tests/fixtures/rollback_program.py")],
            "lock_kind": "directory", "lock_path": "{root}/.lock"}


class RollbackTests(unittest.TestCase):
    def test_actual_temporary_filename_is_checked(self):
        spec = adapter('overwrite_other_temp')
        spec['temporary_paths'] = ['{root}/restore.stage']
        result = check(spec, ('unrelated_temp',))
        self.assertEqual(result['status'], 'FAIL', result)
        self.assertFalse(result['results'][0]['checks']['unrelated_paths_preserved'])

    def test_known_alternate_temporary_filename_is_checked(self):
        result = check(adapter('overwrite_temp_underscore'), ('unrelated_temp',))
        self.assertEqual(result['status'], 'FAIL', result)
        self.assertFalse(result['results'][0]['checks']['unrelated_paths_preserved'])

    def test_temporary_probe_paths_cannot_escape_or_alias_inputs(self):
        for path in ('../outside', '{root}/config.md', '{root}/cache',
                     '{root}/cache/new.json', '{backup}', '{records}/prior-evidence.txt',
                     '{root}/.lock', '{root}/config.md/child'):
            with self.subTest(path=path):
                spec = adapter(); spec['temporary_paths'] = [path]
                with self.assertRaises(ValueError): check(spec, ('unrelated_temp',))

    def test_type_parent_and_unreceipted_restoration_conflicts(self):
        cases = ('config_directory', 'cache_directory', 'backup_directory',
                 'backup_symlink', 'cache_parent_symlink', 'already_restored')
        result = check(adapter(), cases)
        self.assertEqual(result['status'], 'PASS', result)
        for row in result['results']:
            self.assertTrue(row['checks']['refuses_before_mutation'])

    def test_following_parent_or_backup_symlinks_is_rejected(self):
        for mutant, scenario in (('follow_parent', 'cache_parent_symlink'),
                                 ('follow_backup', 'backup_symlink')):
            with self.subTest(mutant=mutant):
                result = check(adapter(mutant), (scenario,))
                self.assertEqual(result['status'], 'FAIL', result)
                self.assertFalse(result['results'][0]['checks']['refuses_before_mutation'])

    def test_conflict_preservation_includes_nested_files(self):
        result = check(adapter('alter_conflict_child'), ('cache_directory',))
        self.assertEqual(result['status'], 'FAIL', result)
        self.assertFalse(result['results'][0]['checks']['refuses_before_mutation'])

    def test_held_directory_lock_contents_are_preserved(self):
        result = check(adapter('alter_other_lock'), ('held_lock',))
        self.assertEqual(result['status'], 'FAIL', result)
        self.assertFalse(result['results'][0]['checks']['preserves_other_owners_lock'])

    def test_owned_temporary_file_must_be_cleaned(self):
        result = check(adapter('leak_temp'), ('normal',))
        self.assertEqual(result['status'], 'FAIL', result)
        self.assertFalse(result['results'][0]['checks']['no_unexpected_root_paths'])

    def test_positive_control_all_scenarios(self):
        result = check(adapter())
        self.assertEqual(result["status"], "PASS", result)
        self.assertEqual(len(result["results"]), len(SCENARIOS))

    def test_declared_nonzero_retained_directory_is_not_a_false_failure(self):
        spec = adapter('reported_retained_directory')
        self.assertEqual(check(spec, ('nonempty_cache',))['status'], 'FAIL')
        spec['success_codes'] = {'nonempty_cache': [0, 6]}
        self.assertEqual(check(spec, ('nonempty_cache',))['status'], 'PASS')
        spec = adapter('delete_nonempty'); spec['success_codes'] = {'nonempty_cache': [0, 6]}
        self.assertEqual(check(spec, ('nonempty_cache',))['status'], 'FAIL')

    def test_exclusive_file_lock_lifecycle(self):
        spec = adapter('file_lock'); spec['lock_kind'] = 'exclusive_file'
        self.assertEqual(check(spec)['status'], 'PASS')

    def test_mutants_are_rejected_on_behavior(self):
        mutations = [
            ("leak_lock", "normal", "releases_owned_lock"),
            ("leak_lock", "config_conflict", "releases_owned_lock"),
            ("partial_mutation", "config_conflict", "refuses_before_mutation"),
            ("partial_mutation", "cache_conflict", "refuses_before_mutation"),
            ("overwrite_temp", "unrelated_temp", "unrelated_paths_preserved"),
            ("remove_other_lock", "held_lock", "preserves_other_owners_lock"),
            ("noop", "normal", "restores_original_content"),
            ("empty_evidence", "normal", "new_nonempty_evidence_retained"),
            ("tamper_evidence", "normal", "prior_evidence_preserved"),
            ("delete_nonempty", "nonempty_cache", "unrelated_paths_preserved"),
            ("accept_missing", "missing_target", "refuses_before_mutation"),
        ]
        if os.name != "nt": mutations.append(("wrong_mode", "normal", "restores_original_mode"))
        for mutant, scenario, criterion in mutations:
            with self.subTest(mutant=mutant, scenario=scenario):
                result = check(adapter(mutant), (scenario,))
                self.assertEqual(result["status"], "FAIL")
                self.assertFalse(result["results"][0]["checks"][criterion])

    def test_timeout_and_missing_program_are_not_passes(self):
        for command in ([sys.executable, "-c", "import time; time.sleep(2)"],
                        ["/nonexistent-flow-lean-program"]):
            spec = adapter(); spec.update(command=command, timeout_seconds=0.05)
            result = check(spec, ("normal",))
            self.assertEqual(result["status"], "FAIL")
            self.assertIsNotNone(result["results"][0]["error"])

    def test_rejects_lock_escape_and_unknown_scenario(self):
        spec = adapter(); spec["lock_path"] = "../outside"
        with self.assertRaises(ValueError): check(spec, ("normal",))
        with self.assertRaises(ValueError): check(adapter(), ("typo",))

    def test_cli_requires_review_and_preserves_receipts(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp); spec = p / "adapter.json"; output = p / "report.json"
            spec.write_text(json.dumps(adapter("leak_lock")))
            command = [sys.executable, str(ROOT / "scripts/check_rollback.py"), str(spec),
                       "--output", str(output)]
            first = subprocess.run(command, capture_output=True)
            self.assertNotEqual(first.returncode, 0); self.assertFalse(output.exists())
            run = subprocess.run(command + ["--reviewed"], capture_output=True)
            self.assertEqual(run.returncode, 1)
            saved = output.read_bytes()
            self.assertEqual(json.loads(saved)["status"], "FAIL")
            self.assertNotEqual(subprocess.run(command + ["--reviewed"], capture_output=True).returncode, 0)
            self.assertEqual(output.read_bytes(), saved)


    @unittest.skipUnless(Path("/bin/bash").is_file(), "requires a local Bash")
    def test_repaired_v3_witness_and_argument_errors(self):
        source = ROOT / "tests/fixtures/rollback_v3_1.sh"
        spec = {
            "command": ["/bin/bash", str(source), "--root", "{root}",
                        "--verify-dir", "{records}", "--backup", "{backup}",
                        "--orig-checksum", "{original_sha256}",
                        "--installed-config-checksum", "{config_sha256}",
                        "--installed-cache-checksum", "{cache_sha256}",
                        "--lock-wait-seconds", "0"],
            "source_files": [str(source)], "lock_kind": "directory",
            "lock_path": "{root}/.rollback.lock",
            "success_codes": {"nonempty_cache": [0, 6]},
        }
        result = check(spec)
        self.assertEqual(result["status"], "PASS", result)
        for args in ([], ["--root"]):
            with self.subTest(args=args):
                run = subprocess.run(["/bin/bash", str(source), *args],
                                     capture_output=True, text=True)
                self.assertEqual(run.returncode, 1)
                self.assertIn("Missing", run.stderr)
                self.assertNotIn("bad substitution", run.stderr)
                self.assertNotIn("unbound variable", run.stderr)


if __name__ == "__main__": unittest.main()
