"""Offline CLI regressions: a real subprocess stands in for the paid provider."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/run_evals.py"


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dir = Path(self.temp.name)
        self.output = self.dir / "responses.jsonl"
        self.state = self.dir / "calls.jsonl"
        self.script = self.dir / "provider.py"
        self.script.write_text('''import json, sys, os
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')
state, fixture = map(Path, sys.argv[1:3])
n = len(state.read_text().splitlines()) if state.exists() else 0
with state.open('a') as f:
    f.write(json.dumps({'cwd': os.getcwd(), 'args': sys.argv[3:]}) + '\\n')
rows = json.loads(fixture.read_text())
row = rows[min(n, len(rows)-1)]
print(row['stdout'])
sys.exit(row.get('exit', 0))
''', encoding="utf-8")
        self.fixture = self.dir / "fixture.json"
        self.configure_responses([self.response()])
        self.config = self.dir / "runners.json"
        self.runner = {"command": [sys.executable, str(self.script), str(self.state), str(self.fixture)],
                       "response_format": "claude-json", "budget_flag": "--budget",
                       "model": "fixture-model", "runner_version": "fixture-v1"}
        self.save_config()
        self.cases = self.dir / "cases.jsonl"
        self.cases.write_text(json.dumps({"id": "one", "category": "test", "prompt": "réponds",
                                         "risk": "low", "criteria": ["preserve meaning"]}) + "\n")
        self.skill = self.dir / "candidate.md"
        self.skill.write_text("Keep required facts.")

    def save_config(self):
        self.config.write_text(json.dumps({"fixture": self.runner}))

    @staticmethod
    def response(cost=0.1, text="Vérifié — réserve conservée", exit=0):
        return {"stdout": json.dumps({"result": text, "total_cost_usd": cost,
                                      "usage": {"input_tokens": 10, "output_tokens": 3}}, ensure_ascii=False), "exit": exit}

    def configure_responses(self, rows):
        self.fixture.write_text(json.dumps(rows), encoding="utf-8")

    def run_cli(self, *extra, condition="candidate"):
        return subprocess.run([sys.executable, str(CLI), "run", "--cases", str(self.cases),
                               "--runner-config", str(self.config), "--runner", "fixture",
                               "--condition", condition, "--condition-skill", str(self.skill),
                               "--trials", "1", "--budget-usd", "1", "--retries", "0",
                               "--output", str(self.output), *extra], capture_output=True, text=True)

    def rows(self, path):
        return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]

    def test_resume_skips_success_but_rejects_changed_skill(self):
        self.assertEqual(self.run_cli().returncode, 0)
        self.assertEqual(self.run_cli().returncode, 0)
        self.skill.write_text("Changed instructions.")
        changed = self.run_cli()
        self.assertNotEqual(changed.returncode, 0, "changed skill must not reuse old results")
        self.assertIn("provenance", changed.stderr.lower())
        self.assertEqual(len(self.rows(self.state)), 1)

    def test_interleaved_case_schedule_preserves_shared_provenance_and_budget(self):
        case = self.rows(self.cases)[0]
        other = {**case, 'id': 'two', 'prompt': 'second case'}
        self.cases.write_text(json.dumps(case) + '\n' + json.dumps(other) + '\n')
        self.assertEqual(self.run_cli('--next-case', 'two', condition='v3').returncode, 0)
        self.assertEqual(self.run_cli('--next-case', 'one', condition='v3_without_fidelity').returncode, 0)
        self.assertEqual(self.run_cli('--next-case', 'one', condition='v3').returncode, 0)
        rows = self.rows(self.output)
        self.assertEqual([(r['case_id'], r['condition']) for r in rows],
                         [('two', 'v3'), ('one', 'v3_without_fidelity'), ('one', 'v3')])
        self.assertEqual(len({r['run_fingerprint'] for r in rows}), 1)
        self.assertEqual(self.rows(self.state)[2]['args'][1], '0.8000')
        self.assertEqual(self.run_cli('--next-case', 'two', condition='v3').returncode, 0)
        self.assertEqual(len(self.rows(self.state)), 3)
        invalid = self.run_cli('--next-case', 'missing', condition='v3')
        self.assertNotEqual(invalid.returncode, 0)
        self.assertEqual(len(self.rows(self.state)), 3)

    def test_resume_rejects_changed_model_and_corpus(self):
        self.assertEqual(self.run_cli().returncode, 0)
        self.runner['model'] = 'other-model'
        self.save_config()
        self.assertNotEqual(self.run_cli().returncode, 0)
        self.runner['model'] = 'fixture-model'
        self.save_config()
        case = json.loads(self.cases.read_text())
        case['prompt'] = 'changed'
        self.cases.write_text(json.dumps(case))
        self.assertNotEqual(self.run_cli().returncode, 0)
        self.assertEqual(len(self.rows(self.state)), 1)

    def test_attempt_costs_reduce_retry_budget_and_survive_failure(self):
        self.configure_responses([self.response(0.2, exit=1), self.response(0.1)])
        result = self.run_cli('--retries', '1', '--budget-usd', '0.5')
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.rows(self.state)
        self.assertEqual(calls[1]['args'][1], '0.3000')
        ledger = self.rows(Path(str(self.output) + '.attempts.jsonl'))
        finished = [r for r in ledger if r['event'] == 'finished']
        self.assertEqual([r['cost_usd'] for r in finished], [0.2, 0.1])
        self.assertEqual([r['status'] for r in finished], ['failed', 'success'])
        self.assertEqual(len(self.rows(self.output)), 1)

    def test_unknown_cost_stops_before_retry_and_resume(self):
        self.configure_responses([self.response(None, exit=1), self.response()])
        self.assertNotEqual(self.run_cli('--retries', '1').returncode, 0)
        self.assertEqual(len(self.rows(self.state)), 1)
        self.assertNotEqual(self.run_cli().returncode, 0)
        self.assertEqual(len(self.rows(self.state)), 1)

    def test_empty_response_is_not_completed_and_unicode_is_exact(self):
        self.configure_responses([self.response(text=''), self.response()])
        self.assertNotEqual(self.run_cli().returncode, 0)
        self.assertEqual(self.run_cli().returncode, 0)
        self.assertEqual(self.rows(self.output)[0]['response'], 'Vérifié — réserve conservée')

    def test_isolated_working_directory_and_result_provenance(self):
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotEqual(self.rows(self.state)[0]['cwd'], str(ROOT))
        row = self.rows(self.output)[0]
        self.assertEqual(len(row['run_fingerprint']), 64)
        self.assertEqual(len(row['condition_fingerprint']), 64)
        self.assertTrue(Path(str(self.output) + '.manifest.json').exists())

    def test_legacy_results_cannot_be_silently_resumed(self):
        self.output.write_text(json.dumps({'case_id': 'one', 'trial': 1, 'condition': 'candidate',
                                          'runner': 'fixture', 'response': 'old'}) + '\n')
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.state.exists())

    def test_budget_is_shared_by_conditions(self):
        self.configure_responses([self.response(cost=0.5)])
        self.assertEqual(self.run_cli('--budget-usd', '0.5').returncode, 0)
        result = self.run_cli('--budget-usd', '0.5', condition='baseline')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(len(self.rows(self.state)), 1)

    def test_committed_success_recovers_without_provider_replay(self):
        self.assertEqual(self.run_cli().returncode, 0)
        self.output.write_text('')
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.rows(self.state)), 1)
        self.assertEqual(len(self.rows(self.output)), 1)

    def test_incomplete_attempt_blocks_metered_resume(self):
        self.assertEqual(self.run_cli().returncode, 0)
        ledger = Path(str(self.output) + '.attempts.jsonl')
        rows = self.rows(ledger)
        ledger.write_text(json.dumps(rows[0]) + '\n')
        self.output.write_text('')
        result = self.run_cli()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(self.rows(self.state)), 1)

    def test_claude_event_array_uses_last_result(self):
        self.configure_responses([{'stdout': json.dumps([{'type': 'system'},
            {'type': 'result', 'result': 'old', 'total_cost_usd': 0.1},
            {'type': 'result', 'result': 'final', 'total_cost_usd': 0.2}])}])
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.rows(self.output)[0]['response'], 'final')

    def test_locked_output_does_not_start_provider(self):
        Path(str(self.output) + '.lock').write_text('another process')
        self.assertNotEqual(self.run_cli().returncode, 0)
        self.assertFalse(self.state.exists())

    def test_manifest_preserves_preexisting_temporary_file(self):
        existing = Path(str(self.output) + '.manifest.json.tmp')
        existing.write_bytes(b'unrelated work\n')
        result = self.run_cli()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(existing.read_bytes(), b'unrelated work\n')

    def test_missing_result_event_retains_raw_failure_and_blocks_resume(self):
        raw = json.dumps([{'type': 'system', 'message': 'incomplete stream'}])
        self.configure_responses([{'stdout': raw}])
        self.assertNotEqual(self.run_cli().returncode, 0)
        ledger = self.rows(Path(str(self.output) + '.attempts.jsonl'))
        self.assertEqual(ledger[-1]['event'], 'finished')
        self.assertEqual(ledger[-1]['status'], 'failed')
        self.assertEqual(ledger[-1]['stdout'].strip(), raw)
        self.assertIsNone(ledger[-1]['cost_usd'])
        self.assertNotEqual(self.run_cli().returncode, 0)
        self.assertEqual(len(self.rows(self.state)), 1)

    def test_null_result_is_not_a_success_and_retains_cost(self):
        self.configure_responses([self.response(cost=0.2, text=None)])
        self.assertNotEqual(self.run_cli().returncode, 0)
        self.assertFalse(self.output.exists())
        ledger = self.rows(Path(str(self.output) + '.attempts.jsonl'))
        self.assertEqual(ledger[-1]['status'], 'failed')
        self.assertEqual(ledger[-1]['cost_usd'], 0.2)

    def test_invalid_budget_cannot_start_provider(self):
        for value in ('nan', 'inf', '-1', '26'):
            self.assertNotEqual(self.run_cli('--budget-usd', value).returncode, 0)
        self.assertFalse(self.state.exists())

    def test_allow_unmetered_keeps_unknown_cost_explicit(self):
        self.configure_responses([self.response(None)])
        result = self.run_cli('--allow-unmetered')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('total UNKNOWN', result.stdout)
        self.assertIsNone(self.rows(self.output)[0]['cost_usd'])

    def test_generic_and_minimal_use_distinct_instructions(self):
        # Omitting --condition-skill selects the bundled experimental fixtures.
        for condition in ('generic', 'minimal'):
            command = [sys.executable, str(CLI), 'run', '--cases', str(self.cases),
                       '--runner-config', str(self.config), '--runner', 'fixture',
                       '--condition', condition, '--trials', '1', '--budget-usd', '1',
                       '--output', str(self.output)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        rows = self.rows(self.output)
        self.assertNotEqual(rows[0]['condition_fingerprint'], rows[1]['condition_fingerprint'])
        calls = self.rows(self.state)
        self.assertTrue(all('<task>\nréponds\n</task>' in c['args'][-1] for c in calls))

    def test_core_plan_is_paired_and_makes_no_provider_calls(self):
        result = subprocess.run([sys.executable, str(CLI), 'plan', '--core-comparison',
                                 '--cases', str(self.cases), '--trials', '2'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual(len(rows), 8)
        for trial in (1, 2):
            self.assertEqual({r['condition'] for r in rows if r['trial'] == trial},
                             {'baseline', 'generic', 'minimal', 'candidate'})
        self.assertFalse(self.state.exists())

    def test_all_conditions_receive_same_text_only_context_and_task(self):
        # Removing the context from baseline (or any other arm) must fail.
        conditions = ('baseline', 'generic', 'minimal', 'candidate', 'comparator')
        for condition in conditions:
            result = self.run_cli(condition=condition)
            self.assertEqual(result.returncode, 0, result.stderr)
        prompts = [call['args'][-1] for call in self.rows(self.state)]
        contexts = []
        for condition, prompt in zip(conditions, prompts):
            self.assertTrue(prompt.startswith('<evaluation_context>\n'), condition)
            context, separator, remainder = prompt.partition('</evaluation_context>')
            self.assertTrue(separator, condition)
            self.assertIn('no tools, repository access, or network access', context)
            self.assertIn("not the runner's working directory", context)
            self.assertIn('<task>\nréponds\n</task>', remainder)
            self.assertEqual('<response_style>' in remainder, condition != 'baseline')
            contexts.append(context)
        self.assertEqual(len(set(contexts)), 1)

    def test_provider_error_with_zero_exit_is_not_a_success(self):
        self.configure_responses([{'stdout': json.dumps({'type': 'result', 'is_error': True,
                                   'result': 'budget reached', 'total_cost_usd': 0.2})}])
        self.assertNotEqual(self.run_cli().returncode, 0)
        self.assertFalse(self.output.exists())
        ledger = self.rows(Path(str(self.output) + '.attempts.jsonl'))
        self.assertEqual(ledger[-1]['cost_usd'], 0.2)

    def test_observed_runner_version_change_rejects_resume(self):
        version_file = self.dir / 'version.txt'
        version_file.write_text('v1')
        self.runner['version_command'] = [sys.executable, '-c',
            'import pathlib,sys; print(pathlib.Path(sys.argv[1]).read_text())', str(version_file)]
        self.save_config()
        self.assertEqual(self.run_cli().returncode, 0)
        version_file.write_text('v2')
        self.assertNotEqual(self.run_cli().returncode, 0)
        self.assertEqual(len(self.rows(self.state)), 1)

    def test_scoring_can_compare_minimal_to_current_candidate(self):
        scores = self.dir / 'scores.jsonl'
        rows = []
        for condition, correctness in [('candidate', 5), ('minimal', 3)]:
            rows.append({'case_id': 'one', 'trial': 1, 'condition': condition,
                         'correctness': correctness, 'decision_fidelity': 5, 'gate_fit': 5,
                         'concision': 5, 'safety': 5, 'blocker': False, 'notes': ''})
        scores.write_text(''.join(json.dumps(row)+'\n' for row in rows))
        result = subprocess.run([sys.executable, str(CLI), 'score', str(scores),
            '--reference-condition', 'candidate', '--candidate-condition', 'minimal'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertFalse(report['release_gate']['passed'])
        self.assertEqual(report['comparison'], {'reference': 'candidate', 'candidate': 'minimal'})

    def test_scoring_rejects_unpaired_minimal_results(self):
        scores = self.dir / 'scores.jsonl'
        rows = [{'case_id': case, 'trial': 1, 'condition': condition, 'correctness': 5,
                 'decision_fidelity': 5, 'gate_fit': 5, 'concision': 5, 'safety': 5,
                 'blocker': False, 'notes': ''} for case, condition in [('one','candidate'), ('two','minimal')]]
        scores.write_text(''.join(json.dumps(row)+'\n' for row in rows))
        result = subprocess.run([sys.executable, str(CLI), 'score', str(scores),
            '--reference-condition', 'candidate', '--candidate-condition', 'minimal'], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('same rows', result.stderr)


if __name__ == '__main__':
    unittest.main()
