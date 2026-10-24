"""Offline evidence integrity, never an automatic semantic model judge."""
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import prepare_pr2_qualification as planner
from run_evals import load_cases

BLOCKERS = {'debug-spiral-missing-info', 'tradeoff-db-choice',
            'actor-reversed-draft', 'actor-ambiguous-approval'}
PRIOR = ROOT / 'evals/results/pr2-actor-qualification-2026-10-24-evidence/cases.jsonl'


class GuardrailPreparationTests(unittest.TestCase):
    def test_same_40_tasks_with_only_four_strengthened_criteria(self):
        prior = {c['id']: c for c in load_cases(PRIOR)}
        current = {c['id']: c for c in planner.cases_for_qualification(
            with_rollback_reference=True, with_actor_regressions=True)}
        self.assertEqual(set(current), set(prior))
        changed = set()
        for cid, old in prior.items():
            for key in ('prompt', 'category', 'risk'):
                self.assertEqual(current[cid][key], old[key], (cid, key))
            self.assertEqual(current[cid]['criteria'][:len(old['criteria'])], old['criteria'])
            if current[cid]['criteria'] != old['criteria']: changed.add(cid)
        self.assertEqual(changed, BLOCKERS)

    def test_review_groups_and_evidence_are_frozen_without_prompt_leakage(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / 'plan'
            manifest = planner.prepare(output, with_rollback_reference=True, with_actor_regressions=True)
            groups = manifest['groups']
            self.assertIn('previous_blockers', groups)
            self.assertEqual(set(groups['previous_blockers']), BLOCKERS)
            self.assertEqual(groups['data_isolation'], ['tradeoff-db-choice'])
            self.assertEqual(set(groups['diagnostic']), {'debug-spiral-missing-info',
                'debug-spiral-evidence-available', 'debug-unauthorized-flag',
                'debug-protected-evidence-supplied'})
            self.assertEqual((len(groups['core']), len(groups['actors'])), (34, 7))
            for name in ('evals/guardrail-review-fixtures.json', 'evals/PR2-GUARDRAIL-QUALIFICATION.md',
                         'tests/test_guardrail_preparation.py'):
                frozen = 'sources/' + name
                self.assertIn(frozen, manifest['sha256'])
                self.assertEqual((output / frozen).read_bytes(), (ROOT / name).read_bytes())
                self.assertEqual(hashlib.sha256((output / frozen).read_bytes()).hexdigest(), manifest['sha256'][frozen])
            fixtures = json.loads((output / 'sources/evals/guardrail-review-fixtures.json').read_text())
            prompts = [r['prompt'] for r in load_cases(output / 'matrix.jsonl')]
            for item in fixtures['cases'].values():
                for field in ('observed_response', 'passing_example', 'failure_reason'):
                    self.assertTrue(all(item[field] not in p for p in prompts), field)

    def test_failure_fixtures_are_exact_receipts_not_authored_model_outputs(self):
        path = ROOT / 'evals/guardrail-review-fixtures.json'
        self.assertTrue(path.is_file(), 'Missing reviewer fixtures for four observed failures')
        fixtures = json.loads(path.read_text())
        self.assertEqual(set(fixtures['cases']), BLOCKERS)
        cases = {c['id']: c for c in load_cases(PRIOR)}
        for cid, item in fixtures['cases'].items():
            source = ROOT / 'evals' / item['observed_source']
            self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), item['observed_source_sha256'])
            rows = [r for r in load_cases(source) if r['case_id'] == cid and r['condition'] == 'candidate']
            self.assertEqual(len(rows), 1)
            self.assertEqual(item['observed_response'], rows[0]['response'])
            self.assertIn(item['source_anchor'], cases[cid]['prompt'])
            self.assertNotEqual(item['passing_example'], item['observed_response'])
            self.assertTrue(item['failure_reason'])

    def test_changing_review_answers_changes_evidence_but_not_generation(self):
        # Catches accidental inclusion of reviewer material even after paraphrasing
        # a known passing example. Exercise real files and the actual preparer.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'repo'
            for name in planner.SOURCES + [planner.PRIOR]:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            with patch.object(planner, 'ROOT', root):
                before_dir, after_dir = Path(tmp) / 'before', Path(tmp) / 'after'
                before = planner.prepare(before_dir, with_rollback_reference=True, with_actor_regressions=True)
                oracle_names = ('evals/guardrail-review-fixtures.json', 'evals/actor-fidelity-oracles.json')
                for name in oracle_names:
                    path = root / name
                    data = json.loads(path.read_text())
                    for item in data['cases'].values():
                        item['passing_example'] = 'REVIEW_ONLY_CANARY_7e51'
                    path.write_text(json.dumps(data))
                after = planner.prepare(after_dir, with_rollback_reference=True, with_actor_regressions=True)
                for name in ('matrix.jsonl', 'cases.jsonl', 'candidate.md', 'comparator.md'):
                    self.assertEqual((before_dir / name).read_bytes(), (after_dir / name).read_bytes())
                self.assertNotIn('REVIEW_ONLY_CANARY_7e51', (after_dir / 'matrix.jsonl').read_text())
                for name in oracle_names:
                    self.assertNotEqual(before['sha256']['sources/' + name], after['sha256']['sources/' + name])


class DataIsolationCounterexamples(unittest.TestCase):
    """SQLite relational counterexample, NOT PostgreSQL/MongoDB or RLS validation."""
    def database(self, tenant_aware):
        db = sqlite3.connect(':memory:')
        self.addCleanup(db.close)
        db.execute('PRAGMA foreign_keys = ON')
        db.execute('CREATE TABLE parents (id INTEGER PRIMARY KEY, tenant TEXT NOT NULL, UNIQUE(tenant, id))')
        fk = ('FOREIGN KEY(tenant, parent_id) REFERENCES parents(tenant, id)' if tenant_aware
              else 'FOREIGN KEY(parent_id) REFERENCES parents(id)')
        db.execute('CREATE TABLE children (tenant TEXT NOT NULL, parent_id INTEGER NOT NULL, ' + fk + ')')
        db.execute("INSERT INTO parents VALUES (1, 'tenant-a')")
        return db

    def test_plain_foreign_key_accepts_cross_tenant_reference(self):
        db = self.database(False)
        db.execute("INSERT INTO children VALUES ('tenant-b', 1)")
        self.assertEqual(db.execute('SELECT children.tenant, parents.tenant FROM children JOIN parents ON parents.id = parent_id').fetchall(), [('tenant-b', 'tenant-a')])
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute("INSERT INTO children VALUES ('tenant-a', 999)")

    def test_tenant_aware_key_blocks_cross_tenant_reference_but_not_reads(self):
        db = self.database(True)
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute("INSERT INTO children VALUES ('tenant-b', 1)")
        with self.assertRaises(sqlite3.IntegrityError):
            db.execute("INSERT INTO children VALUES (NULL, 1)")
        db.execute("INSERT INTO children VALUES ('tenant-a', 1)")
        db.execute("INSERT INTO parents VALUES (2, 'tenant-b')")
        # Relationship integrity is not row access control: unrestricted reads still return both tenants.
        self.assertEqual(db.execute('SELECT tenant FROM parents ORDER BY id').fetchall(), [('tenant-a',), ('tenant-b',)])


if __name__ == '__main__':
    unittest.main()
