"""Preparation integrity, not a semantic grader or proof of model adherence."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import prepare_pr2_qualification as planner
from run_evals import load_cases, _condition_prompt


class ActorFidelityPreparationTests(unittest.TestCase):
    def test_extended_preparation_cannot_start_processes_or_network(self):
        with tempfile.TemporaryDirectory() as tmp, \
                patch('subprocess.Popen', side_effect=AssertionError('No runner')), \
                patch('socket.socket.connect', side_effect=AssertionError('No network')):
            output = Path(tmp) / 'plan'
            manifest = planner.prepare(output, with_rollback_reference=True, with_actor_regressions=True)
            self.assertEqual(len(load_cases(output / 'matrix.jsonl')), 80)
            self.assertEqual((manifest['provider_calls'], manifest['budget_authorized_usd']), (0, 0))

    def test_extension_preserves_all_prior_tasks_and_criteria(self):
        prior = {c['id']: c for c in load_cases(
            ROOT / 'evals/results/pr2-contract-qualification-2026-10-24-evidence/cases.jsonl')}
        extended = {c['id']: c for c in planner.cases_for_qualification(
            with_rollback_reference=True, with_actor_regressions=True)}
        self.assertEqual(len(set(extended) - set(prior)), 6)
        for cid, old in prior.items():
            with self.subTest(case=cid):
                for key in ('prompt', 'category', 'risk'):
                    self.assertEqual(extended[cid][key], old[key])
                self.assertEqual(extended[cid]['criteria'][:len(old['criteria'])], old['criteria'])

    def test_invalid_actor_catalog_fails_before_writing(self):
        real_load = load_cases
        for mutation in ('duplicate', 'shadow', 'missing'):
            def changed(path):
                rows = real_load(path)
                if path.name == 'actor-fidelity.jsonl':
                    if mutation == 'duplicate': rows[1]['id'] = rows[0]['id']
                    elif mutation == 'shadow': rows[0]['id'] = 'speaker-commitment'
                    else: rows.pop()
                return rows
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp, \
                    patch('prepare_pr2_qualification.load_cases', side_effect=changed):
                output = Path(tmp) / 'plan'
                with self.assertRaises(ValueError):
                    planner.prepare(output, with_actor_regressions=True)
                self.assertFalse(output.exists())

    def test_review_fixtures_cover_tasks_and_preserve_observed_failure(self):
        cases = {c['id']: c for c in planner.cases_for_qualification(with_actor_regressions=True)}
        actor_ids = {c['id'] for c in load_cases(ROOT / 'evals/actor-fidelity.jsonl')}
        oracles = json.loads((ROOT / 'evals/actor-fidelity-oracles.json').read_text(encoding='utf-8'))['cases']
        self.assertEqual(set(oracles), actor_ids | {'speaker-commitment'})
        for cid, oracle in oracles.items():
            with self.subTest(case=cid):
                self.assertIn(oracle['source_anchor'], cases[cid]['prompt'])
                self.assertNotEqual(oracle['passing_example'], oracle['failing_example'])
                self.assertTrue(oracle['failure_reason'])
                self.assertEqual(set(oracle['role_map']),
                    {'action_actor', 'approval_actor', 'modality', 'approval_state'})
        historical = oracles['speaker-commitment']
        rows = load_cases(ROOT / 'evals' / historical['observed_failure_source'])
        observed = [r for r in rows if r['case_id'] == 'speaker-commitment' and r['condition'] == 'candidate']
        self.assertEqual(len(observed), 1)
        self.assertEqual(historical['failing_example'], observed[0]['response'])

    def test_cli_extension_freezes_40_pairs_without_disclosing_review_oracles(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'plan'
            result = subprocess.run([
                sys.executable, str(ROOT / 'scripts/prepare_pr2_qualification.py'),
                '--output', str(output), '--with-rollback-reference',
                '--with-actor-regressions'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads((output / 'manifest.json').read_text())
            self.assertEqual((manifest['provider_calls'], manifest['budget_authorized_usd']), (0, 0))
            self.assertEqual((manifest['case_count'], manifest['planned_calls']), (40, 80))
            self.assertEqual(manifest['model'], 'UNSELECTED')
            cases, rows = (load_cases(output / name) for name in ('cases.jsonl', 'matrix.jsonl'))
            self.assertEqual(len(rows), 80)
            self.assertEqual(len({c['id'] for c in cases}), 40)
            self.assertEqual(sum(r['condition'] == 'candidate' for r in rows[::2]), 20)
            groups = manifest['groups']
            self.assertEqual([len(groups[g]) for g in ('core', 'actors', 'focus')], [34, 7, 20])
            self.assertEqual(set(groups['core']) & set(groups['actors']), {'speaker-commitment'})
            self.assertEqual(set(groups['core']) | set(groups['actors']), {c['id'] for c in cases})
            by_id = {c['id']: c for c in cases}
            for row in rows:
                instructions = (output / (row['condition'] + '.md')).read_text()
                self.assertEqual(row['prompt'], _condition_prompt(by_id[row['case_id']]['prompt'], row['condition'], instructions))
                self.assertNotIn('passing_example', row['prompt'])
                self.assertNotIn('role_map', row['prompt'])
            for name in ('evals/actor-fidelity.jsonl', 'evals/actor-fidelity-oracles.json',
                         'tests/test_actor_fidelity.py', 'evals/PR2-ACTOR-QUALIFICATION.md'):
                frozen = 'sources/' + name
                self.assertEqual(hashlib.sha256((output / frozen).read_bytes()).hexdigest(), manifest['sha256'][frozen])


if __name__ == '__main__':
    unittest.main()
