import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from prepare_pr2_qualification import prepare, cases_for_qualification, FOCUS, load_cases
from run_evals import _condition_prompt


class QualificationPreparationTests(unittest.TestCase):
    def test_offline_freeze_pairing_hashes_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp, patch('subprocess.run', side_effect=AssertionError('No runner')):
            output = Path(tmp) / 'plan'
            manifest = prepare(output)
            self.assertEqual(manifest['status'], 'PREPARED_NOT_RUN')
            self.assertEqual((manifest['provider_calls'], manifest['budget_authorized_usd']), (0, 0))
            cases = load_cases(output / 'cases.jsonl')
            rows = load_cases(output / 'matrix.jsonl')
            self.assertEqual(len(cases), 34)
            self.assertEqual(len(rows), 68)
            self.assertEqual([c['id'] for c in cases[:len(FOCUS)]], FOCUS)
            for case in cases:
                pair = [r for r in rows if r['case_id'] == case['id']]
                self.assertEqual({(r['condition'], r['trial']) for r in pair},
                                 {('candidate', 1), ('comparator', 1)})
                for row in pair:
                    instructions = (output / (row['condition'] + '.md')).read_text(encoding='utf-8')
                    self.assertEqual(row['prompt'], _condition_prompt(case['prompt'], row['condition'], instructions))
                    self.assertEqual(row['prompt_sha256'], hashlib.sha256(row['prompt'].encode()).hexdigest())
            self.assertEqual(sum(r['condition'] == 'candidate' for r in rows[::2]), 17)
            before = {p.relative_to(output).as_posix(): p.read_bytes() for p in output.rglob('*') if p.is_file()}
            for name, checksum in manifest['sha256'].items():
                self.assertEqual(hashlib.sha256(before[name]).hexdigest(), checksum)
            with self.assertRaises(FileExistsError): prepare(output)
            self.assertEqual(before, {p.relative_to(output).as_posix(): p.read_bytes() for p in output.rglob('*') if p.is_file()})

    def test_reference_variant_is_explicit_shared_and_frozen(self):
        with tempfile.TemporaryDirectory() as tmp, patch('subprocess.run', side_effect=AssertionError('No runner')):
            output = Path(tmp) / 'plan'
            manifest = prepare(output, with_rollback_reference=True)
            self.assertEqual(manifest['task_variant'], 'shared-rollback-reference')
            self.assertEqual(manifest['modified_prompt_case_ids'], ['rollback-concurrent-edits'])
            base = {c['id']: c for c in cases_for_qualification()}
            cases = load_cases(output / 'cases.jsonl')
            code = (ROOT / 'skills/flow-lean/scripts/rollback_reference.py').read_text(encoding='utf-8')
            for case in cases:
                if case['id'] == 'rollback-concurrent-edits':
                    self.assertTrue(case['prompt'].startswith(base[case['id']]['prompt']))
                    self.assertIn(code, case['prompt'])
                else:
                    self.assertEqual(case, base[case['id']])
            pair = [r for r in load_cases(output / 'matrix.jsonl') if r['case_id'] == 'rollback-concurrent-edits']
            self.assertEqual(len(pair), 2)
            for row in pair:
                self.assertIn(code, row['prompt'])
            for name in ('scripts/rollback_reference.py', 'references/rollback.md'):
                source = 'sources/skills/flow-lean/' + name
                self.assertEqual(hashlib.sha256((output / source).read_bytes()).hexdigest(), manifest['sha256'][source])
            self.assertEqual(manifest['provider_calls'], 0)
            self.assertEqual(manifest['budget_authorized_usd'], 0)

    def test_overrides_keep_prompts_and_original_criteria(self):
        original = {c['id']: c for name in ('cases.jsonl', 'pr2-regressions.jsonl')
                    for c in load_cases(ROOT / 'evals' / name)}
        for case in cases_for_qualification():
            old = original[case['id']]
            for key in ('prompt', 'category', 'risk'):
                self.assertEqual(case[key], old[key])
            self.assertEqual(case['criteria'][:len(old['criteria'])], old['criteria'])

    def test_prior_campaign_prompts_and_criteria_remain_comparable(self):
        prior_path = ROOT / 'evals/results/pr2-reference-qualification-2026-10-22-evidence/cases.jsonl'
        prior = {c['id']: c for c in load_cases(prior_path)}
        current = {c['id']: c for c in cases_for_qualification(with_rollback_reference=True)}
        self.assertEqual(set(current), set(prior))
        changed_prompts, changed_criteria = [], []
        for cid, case in current.items():
            old = prior[cid]
            self.assertEqual(case['criteria'][:len(old['criteria'])], old['criteria'])
            if case['prompt'] != old['prompt']: changed_prompts.append(cid)
            if case['criteria'] != old['criteria']: changed_criteria.append(cid)
        self.assertEqual(changed_prompts, ['rollback-concurrent-edits'])
        self.assertEqual(set(changed_criteria), {
            'rollback-concurrent-edits', 'format-request-flow', 'tradeoff-ssr-ssg'})

    def test_changed_prompt_or_weakened_criteria_is_rejected(self):
        real_load = load_cases
        for mutation in ('prompt', 'criteria'):
            def changed(path):
                rows = real_load(path)
                if path.name == 'pr2-requalification-overrides.jsonl':
                    rows[0][mutation] = 'changed' if mutation == 'prompt' else ['Removed prior requirements']
                return rows
            with self.subTest(mutation=mutation), patch('prepare_pr2_qualification.load_cases', side_effect=changed):
                with self.assertRaises(ValueError): cases_for_qualification()

    def test_changed_reference_is_rejected_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp, patch('prepare_pr2_qualification.REFERENCE_HASH', 'changed'):
            output = Path(tmp) / 'plan'
            with self.assertRaises(ValueError): prepare(output)
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
