#!/usr/bin/env python3
"""Freeze the v4 rule-removal experiment offline; never execute a provider."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import random
import re
import tempfile

from run_evals import ROOT, _condition_prompt, load_cases, validate_cases

PRIOR = Path('evals/results/pr2-guardrail-qualification-2026-10-24-evidence')
GROUPS = ('density', 'scope', 'format', 'status')
SOURCES = [
    'evals/candidates/v4-groups.json', 'evals/candidates/minimal-v4.md',
    'evals/ablation-v4-cases.jsonl', 'evals/ablation-v4-oracles.json',
    'evals/ABLATION-V4.md', 'evals/rubric.md', 'scripts/prepare_v4_ablation.py',
    'scripts/run_evals.py', 'scripts/eval_runtime.py', 'tests/test_v4_ablation.py',
    'scripts/check_routing.cjs', 'tests/test_routing_preview.py', '.gitattributes',
    'skills/flow-lean/SKILL.md', 'skills/flow-lean/evals/scenarios.json',
    'skills/flow-lean/references/rollback.md', 'skills/flow-lean/scripts/rollback_reference.py',
    *[str(PRIOR / name) for name in ('candidate.md','comparator.md','cases.jsonl','manifest.json')],
]
PINNED = {'pr2_full':'6f393a7eb7dbb7d99cd048257b7607cac4225a551526aba94c7de68098f21fe5',
          'comparator':'b592b638b5c43898463302b8816a1e5019821a373a74d9fa2c36daf8713b4bac'}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def render(spec, omit=None):
    if [g['id'] for g in spec['groups']] != list(GROUPS):
        raise ValueError('Expected four distinct ordered removable groups')
    if omit is not None and omit not in GROUPS:
        raise ValueError('Only optional groups can be removed')
    blocks = [spec['header'],spec['core'],*[g['text'] for g in spec['groups'] if g['id'] != omit],spec['controls']]
    if any(not isinstance(b,str) or not b.strip() for b in blocks):
        raise ValueError('Empty instruction block')
    return '\n\n'.join(b.strip() for b in blocks)+'\n'


def prepare(output, *, root=ROOT, seed=20261024):
    root, output = Path(root), Path(output)
    # Read all preimages before writing the inert plan. No provider is invoked.
    sources = {name:(root/name).read_bytes() for name in SOURCES}
    spec = json.loads(sources['evals/candidates/v4-groups.json'])
    candidate = render(spec)
    if candidate != sources['evals/candidates/minimal-v4.md'].decode('utf-8').replace('\r\n','\n'):
        raise ValueError('Rendered candidate differs from the canonical group source')
    arms = {name:sources[str(PRIOR/file)].decode('utf-8') for name,file in
            [('comparator','comparator.md'),('pr2_full','candidate.md')]}
    for name,checksum in PINNED.items():
        if sha(arms[name].encode()) != checksum:
            raise ValueError('Frozen comparator changed: '+name)
    if sources['skills/flow-lean/SKILL.md'].decode('utf-8').replace('\r\n','\n') != arms['pr2_full']:
        raise ValueError('Public candidate drifted from the tested PR revision')
    arms['v4'] = candidate
    arms.update({f'v4_without_{g}':render(spec,g) for g in GROUPS})
    cases = [json.loads(l) for l in sources['evals/ablation-v4-cases.jsonl'].decode().splitlines()]
    old = [json.loads(l) for l in sources[str(PRIOR/'cases.jsonl')].decode().splitlines()]
    errors = validate_cases(cases)
    if errors: raise ValueError('; '.join(errors))
    if len(cases)!=24 or len(old)!=40 or len({c['prompt'] for c in cases})!=24:
        raise ValueError('Expected 24 distinct new prompts and 40 historical cases')
    if {c['id'] for c in cases}&{c['id'] for c in old} or {c['prompt'] for c in cases}&{c['prompt'] for c in old}:
        raise ValueError('New cases duplicate historical IDs or prompts')
    if Counter(c['category'] for c in cases) != Counter(dict(density=4,scope=4,format=4,status=4,essential=8)):
        raise ValueError('Focus/safeguard coverage mismatch')
    contrasts = Counter(c['contrast_id'] for c in cases)
    if len(contrasts)!=12 or set(contrasts.values())!={2}:
        raise ValueError('Expected twelve contrast pairs')
    oracles = json.loads(sources['evals/ablation-v4-oracles.json'])
    if set(oracles['cases']) != {c['id'] for c in cases}:
        raise ValueError('Reviewer oracle coverage mismatch')
    for item in oracles['cases'].values():
        if not item.get('expected') or not item.get('blocking_counterexample'):
            raise ValueError('Incomplete reviewer oracle')
    rng = random.Random(seed)
    ordered = list(cases);rng.shuffle(ordered)
    order = list(arms);rng.shuffle(order)
    rows=[]
    for index, case in enumerate(ordered):
        offset=index%len(order)
        for arm in order[offset:]+order[:offset]:
            prompt=_condition_prompt(case['prompt'],arm,arms[arm])
            rows.append(dict(sequence=len(rows)+1,case_id=case['id'],trial=1,condition=arm,
                             prompt=prompt,prompt_sha256=sha(prompt.encode()),
                             instructions_sha256=sha(arms[arm].encode())))
    files = {'sources/'+name:data for name,data in sources.items()}
    files.update({f'conditions/{name}.md':text.encode() for name,text in arms.items()})
    files['cases.jsonl']=sources['evals/ablation-v4-cases.jsonl']
    files['historical-cases.jsonl']=sources[str(PRIOR/'cases.jsonl')]
    files['matrix.jsonl']=''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows).encode()
    files['skill/SKILL.md']=candidate.encode()
    for name in ('evals/scenarios.json','references/rollback.md','scripts/rollback_reference.py'):
        files['skill/'+name]=sources['skills/flow-lean/'+name]
    old_groups=json.loads(sources[str(PRIOR/'manifest.json')])['groups']
    manifest = dict(status='PREPARED_NOT_RUN',provider_calls=0,budget_authorized_usd=0,
        model='UNSELECTED',trials=1,case_count=24,planned_calls=168,seed=seed,
        reference_commit='2c368a71ad9dea556986411baae26a0590348a6a',
        pr2_full_commit='c0ec3cdfdec0143b436a59df5a3584cbd7a801a0',
        arms=list(arms),fixed_blocks=['header','core','controls'],
        comparisons=[dict(reference='v4',candidate='v4_without_'+g,focus_family=g) for g in GROUPS],
        groups={g:[c['id'] for c in cases if c['category']==g] for g in (*GROUPS,'essential')},
        historical_groups=old_groups,historical_confirmation_planned_calls=80,
        historical_confirmation_status='DEFERRED_UNSELECTED_UNAUTHORIZED',
        novelty='New authored prompts; not previously evaluated here, not an independent holdout.',
        instruction_sizes={a:dict(bytes=len(t.encode()),words_whitespace_split=len(t.split())) for a,t in arms.items()},
        sha256={name:sha(data) for name,data in files.items()})
    output.mkdir(parents=True,exist_ok=False)
    for name,data in files.items():
        target=output/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    (output/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    verify_plan(output)
    return manifest


def verify_plan(output):
    output=Path(output)
    m=json.loads((output/'manifest.json').read_text(encoding='utf-8'))
    for name,checksum in m['sha256'].items():
        path=(output/name).resolve()
        if output.resolve() not in path.parents or sha(path.read_bytes())!=checksum:
            raise ValueError('Plan artifact mismatch: '+name)
    if (m['status'],m['provider_calls'],m['budget_authorized_usd'],m['model']) != ('PREPARED_NOT_RUN',0,0,'UNSELECTED'):
        raise ValueError('An offline plan cannot grant execution authority')
    spec=json.loads((output/'sources/evals/candidates/v4-groups.json').read_text())
    for arm,omit in [('v4',None),*[(f'v4_without_{g}',g) for g in GROUPS]]:
        if (output/f'conditions/{arm}.md').read_text()!=render(spec,omit):
            raise ValueError('Ablation changed more than its declared group')
    for arm,checksum in PINNED.items():
        if sha((output/f'conditions/{arm}.md').read_bytes())!=checksum:
            raise ValueError('Comparator drift')
    rows=load_cases(output/'matrix.jsonl');cases=load_cases(output/'cases.jsonl')
    expected={(c['id'],a,1) for c in cases for a in m['arms']}
    if len(rows)!=168 or len(expected)!=168 or Counter((r['case_id'],r['condition'],r['trial']) for r in rows)!=Counter({k:1 for k in expected}):
        raise ValueError('Incomplete experiment matrix')
    for i,r in enumerate(rows,1):
        case=next(c for c in cases if c['id']==r['case_id'])
        instructions=(output/f"conditions/{r['condition']}.md").read_text()
        if r['sequence']!=i or r['prompt']!=_condition_prompt(case['prompt'],r['condition'],instructions) or r['prompt_sha256']!=sha(r['prompt'].encode()) or r['instructions_sha256']!=sha(instructions.encode()):
            raise ValueError('Generation prompt/provenance mismatch')
    package=output/'skill'
    if (package/'SKILL.md').read_text()!=render(spec):raise ValueError('Package differs from candidate')
    for doc in (package/'SKILL.md',package/'references/rollback.md'):
        for link in re.findall(r'\]\(([^)]+)\)',doc.read_text()):
            if '://' in link:continue
            target=(doc.parent/link).resolve()
            if package.resolve() not in target.parents or not target.is_file():
                raise ValueError('Missing or escaped skill resource')
    return m


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    action=parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--output',type=Path)
    action.add_argument('--verify',type=Path)
    action.add_argument('--check',action='store_true')
    parser.add_argument('--seed',type=int,default=20261024)
    args=parser.parse_args()
    if args.verify:m=verify_plan(args.verify)
    elif args.check:
        with tempfile.TemporaryDirectory() as temp:m=prepare(Path(temp)/'plan',seed=args.seed)
    else:m=prepare(args.output,seed=args.seed)
    print(json.dumps({k:m[k] for k in ('status','provider_calls','budget_authorized_usd','case_count','planned_calls','model')}))


if __name__=='__main__':main()
