"""Offline experiment construction, not model-adherence tests."""
import hashlib
import importlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from run_evals import load_cases, summarize_scores


class AblationPreparationTests(unittest.TestCase):
    def planner(self):
        self.assertTrue((ROOT / 'scripts/prepare_v4_ablation.py').is_file(),
                        'Missing offline v4 ablation preparer')
        return importlib.import_module('prepare_v4_ablation')

    def test_remove_one_group_preserves_common_contract_and_other_groups(self):
        p = self.planner()
        spec = {'header':'HEADER','core':'FIXED SAFETY','controls':'CONTROLS',
                'groups':[{'id':k,'text':v} for k,v in [('density','D'),('scope','S'),('format','F'),('status','T')]]}
        self.assertEqual(p.render(spec), 'HEADER\n\nFIXED SAFETY\n\nD\n\nS\n\nF\n\nT\n\nCONTROLS\n')
        expected = {'density':'S\n\nF\n\nT','scope':'D\n\nF\n\nT',
                    'format':'D\n\nS\n\nT','status':'D\n\nS\n\nF'}
        for name, middle in expected.items():
            self.assertEqual(p.render(spec,name), 'HEADER\n\nFIXED SAFETY\n\n'+middle+'\n\nCONTROLS\n')
        for name in ('core','controls','unknown'):
            with self.assertRaises(ValueError): p.render(spec,name)

    def test_complete_balanced_reproducible_matrix_and_no_execution_authority(self):
        p = self.planner()
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'plan'; m=p.prepare(out)
            self.assertEqual((m['case_count'],m['planned_calls'],m['trials']), (24,168,1))
            self.assertEqual((m['provider_calls'],m['budget_authorized_usd'],m['model']), (0,0,'UNSELECTED'))
            rows=load_cases(out/'matrix.jsonl'); cases=load_cases(out/'cases.jsonl')
            arms={'comparator','pr2_full','v4','v4_without_density','v4_without_scope','v4_without_format','v4_without_status'}
            self.assertEqual({r['condition'] for r in rows}, arms)
            self.assertEqual(Counter((r['case_id'],r['condition']) for r in rows),
                             Counter({(c['id'],a):1 for c in cases for a in arms}))
            for position in range(7):
                counts=Counter(rows[i]['condition'] for i in range(position,168,7))
                self.assertEqual(set(counts),arms)
                self.assertLessEqual(max(counts.values())-min(counts.values()),1)
            for r in rows:
                self.assertEqual(r['prompt_sha256'],hashlib.sha256(r['prompt'].encode()).hexdigest())
                self.assertIn(next(c['prompt'] for c in cases if c['id']==r['case_id']),r['prompt'])
            again=Path(tmp)/'again';p.prepare(again)
            self.assertEqual((out/'matrix.jsonl').read_bytes(),(again/'matrix.jsonl').read_bytes())
            changed=Path(tmp)/'changed';p.prepare(changed,seed=7)
            self.assertNotEqual((out/'matrix.jsonl').read_bytes(),(changed/'matrix.jsonl').read_bytes())
            self.assertEqual(p.verify_plan(out)['status'],'PREPARED_NOT_RUN')

    def test_reviewer_changes_cannot_change_generation_inputs(self):
        p=self.planner()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'repo'
            for name in p.SOURCES:
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/name,target)
            before=Path(tmp)/'before';after=Path(tmp)/'after'
            p.prepare(before,root=root)
            oracle=root/'evals/ablation-v4-oracles.json'
            data=json.loads(oracle.read_text());next(iter(data['cases'].values()))['expected']='REVIEW_CANARY_882a'
            oracle.write_text(json.dumps(data))
            cases=root/'evals/ablation-v4-cases.jsonl'; rows=load_cases(cases)
            rows[0]['criteria'].append('REVIEW_CRITERION_CANARY_aa79')
            cases.write_text(''.join(json.dumps(r)+'\n' for r in rows))
            p.prepare(after,root=root)
            self.assertEqual((before/'matrix.jsonl').read_bytes(),(after/'matrix.jsonl').read_bytes())
            self.assertNotEqual((before/'manifest.json').read_bytes(),(after/'manifest.json').read_bytes())
            self.assertNotIn('REVIEW_CANARY',(after/'matrix.jsonl').read_text())
            self.assertNotIn('REVIEW_CRITERION_CANARY',(after/'matrix.jsonl').read_text())

    def test_historical_prompts_preserved_and_novel_pairs_are_distinct(self):
        p=self.planner()
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'plan';m=p.prepare(out)
            historical=load_cases(out/'historical-cases.jsonl');new=load_cases(out/'cases.jsonl')
            self.assertEqual((out/'historical-cases.jsonl').read_bytes(),(ROOT/p.PRIOR/'cases.jsonl').read_bytes())
            self.assertEqual(len(historical),40)
            self.assertEqual(len(m['historical_groups']['core']),34)
            self.assertFalse({c['prompt'] for c in new}&{c['prompt'] for c in historical})
            self.assertFalse({c['id'] for c in new}&{c['id'] for c in historical})
            self.assertEqual(sorted(Counter(c['contrast_id'] for c in new).values()),[2]*12)

    def test_existing_destination_and_changed_artifact_are_refused(self):
        p=self.planner()
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'plan';p.prepare(out)
            before=(out/'manifest.json').read_bytes()
            with self.assertRaises(FileExistsError):p.prepare(out)
            self.assertEqual((out/'manifest.json').read_bytes(),before)
            matrix=out/'matrix.jsonl';matrix.write_text(matrix.read_text()+'{}\n')
            with self.assertRaises(ValueError):p.verify_plan(out)

    def test_windows_checkout_newlines_keep_source_bytes_but_same_instructions(self):
        p=self.planner()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'repo'
            for name in p.SOURCES:
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/name,target)
            for name in ('skills/flow-lean/SKILL.md','evals/candidates/minimal-v4.md'):
                target=root/name
                target.write_bytes(target.read_bytes().replace(b'\r\n',b'\n').replace(b'\n',b'\r\n'))
            out=Path(tmp)/'plan'
            try:m=p.prepare(out,root=root)
            except ValueError as exc:self.fail('Equivalent CRLF checkout rejected: '+str(exc))
            self.assertIn(b'\r\n',(out/'sources/skills/flow-lean/SKILL.md').read_bytes())
            self.assertNotIn(b'\r\n',(out/'conditions/v4.md').read_bytes())
            self.assertEqual(m['sha256']['sources/skills/flow-lean/SKILL.md'],
                             hashlib.sha256((root/'skills/flow-lean/SKILL.md').read_bytes()).hexdigest())
            self.assertEqual(p.verify_plan(out)['planned_calls'],168)

    def test_scoring_accepts_all_new_conditions_without_provider(self):
        # Catch a plan that the existing scorer cannot consume after execution.
        arms=['comparator','pr2_full','v4','v4_without_density','v4_without_scope','v4_without_format','v4_without_status']
        rows=[dict(case_id='fixture',condition=a,trial=1,correctness=5,decision_fidelity=5,gate_fit=5,concision=5,safety=5,blocker=False,notes='synthetic offline scorer fixture') for a in arms]
        try:
            result=summarize_scores(rows,'v4','v4_without_scope')
        except ValueError as exc:
            self.fail('Prepared conditions cannot be scored: '+str(exc))
        self.assertEqual(len(result['conditions']),7)
        self.assertEqual(result['conditions']['v4_without_scope']['weighted_score'],5)
        self.assertFalse(result['release_gate']['passed'])  # equality is not the existing strict release gate


if __name__=='__main__':unittest.main()
