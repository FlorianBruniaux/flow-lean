"""Append a reviewed masked pair once; does not infer grades or contact models."""
import json
from pathlib import Path
FIELDS = ['correctness','decision_fidelity','gate_fit','concision','safety']
PLAN = Path(__file__).resolve().parent

def append(items):
    target = PLAN / 'grades-blind.jsonl'
    existing = [json.loads(x) for x in target.read_text().splitlines()] if target.exists() else []
    rows = [dict(case_id=cid, label=label, trial=1, **dict(zip(FIELDS, values)), blocker=blocker, notes=notes)
            for cid,label,values,blocker,notes in items]
    keys = [(r['case_id'],r['label']) for r in existing+rows]
    assert len(keys)==len(set(keys)), 'Duplicate masked grade'
    cases = {c['id'] for c in map(json.loads,(PLAN/'cases.jsonl').read_text().splitlines())}
    for row in rows:
        assert row['case_id'] in cases and row['label'] in ('A','B')
        assert all(type(row[k]) is int and 1<=row[k]<=5 for k in FIELDS)
    with target.open('a') as stream:
        for row in rows: stream.write(json.dumps(row)+'\n')
    print('Masked grades recorded:',len(existing)+len(rows))
