"""Display completed pairs without their arm names or cost metadata."""
import json
from pathlib import Path
import sys

plan = Path(__file__).resolve().parent
root = plan.parents[2]
cases = [json.loads(line) for line in (plan / 'cases.jsonl').read_text().splitlines()]
key = json.loads((plan / 'blind-key.json').read_text())['key']
responses = [json.loads(line) for line in (root / 'evals/results/pr2-reference-qualification-2026-10-22.jsonl').read_text().splitlines()]
by_id = {(r['case_id'], r['condition']): r['response'] for r in responses}
for case in cases[int(sys.argv[1]):int(sys.argv[2])]:
    cid = case['id']
    if not all((cid, arm) in by_id for arm in key[cid].values()):
        continue
    print('\nCASE:', cid)
    for label, arm in key[cid].items():
        print('\nLABEL:', label, '\n' + by_id[(cid, arm)])
