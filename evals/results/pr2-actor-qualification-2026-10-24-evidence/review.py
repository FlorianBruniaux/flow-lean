"""Display completed pairs without their arm names or cost metadata."""
import hashlib
import re
import json
from pathlib import Path
import sys

plan = Path(__file__).resolve().parent
root = plan.parents[2]
cases = [json.loads(line) for line in (plan / 'cases.jsonl').read_text().splitlines()]
key = json.loads((plan / 'blind-key.json').read_text())['key']
responses = [json.loads(line) for line in (root / 'evals/results/pr2-actor-qualification-2026-10-24.jsonl').read_text().splitlines()]
by_id = {(r['case_id'], r['condition']): r['response'] for r in responses}
for case in cases[int(sys.argv[1]):int(sys.argv[2])]:
    cid = case['id']
    if not all((cid, arm) in by_id for arm in key[cid].values()):
        continue
    print('\nCASE:', cid)
    print('TASK:', case['prompt'].split('\n\nThe same optional reference')[0])
    print('CRITERIA:', json.dumps(case['criteria']))
    for label, arm in key[cid].items():
        answer = by_id[(cid, arm)]
        if cid == 'rollback-concurrent-edits':
            reference = (plan / 'sources/skills/flow-lean/scripts/rollback_reference.py').read_bytes()
            for match in re.finditer(r'```python\n(.*?)```', answer, re.S):
                code = match.group(1).encode()
                if code == reference:
                    answer = answer.replace(match.group(0), '[Exact supplied reference code, fully inspected separately. SHA256: ' + hashlib.sha256(code).hexdigest() + ']')
        print('\nLABEL:', label, '\n' + answer)
