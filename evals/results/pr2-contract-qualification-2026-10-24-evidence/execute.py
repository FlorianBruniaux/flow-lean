import hashlib
import json
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[3]
plan = Path(__file__).resolve().parent
manifest = json.loads((plan / 'manifest.json').read_text())
authorization = json.loads((plan / 'authorization.json').read_text())
output = root / 'evals/results/pr2-contract-qualification-2026-10-24.jsonl'
ledger = Path(str(output) + '.attempts.jsonl')
assert authorization['budget_total_usd'] == 5
assert hashlib.sha256((plan / 'runner.json').read_bytes()).hexdigest() == authorization['runner_sha256']
rows = [json.loads(line) for line in (plan / 'matrix.jsonl').read_text().splitlines()]
assert len(rows) == 68
for row in rows:
    for name, checksum in manifest['sha256'].items():
        assert hashlib.sha256((plan / name).read_bytes()).hexdigest() == checksum, name
        if name.startswith('sources/'):
            assert hashlib.sha256((root / name[8:]).read_bytes()).hexdigest() == checksum, name
    command = [sys.executable, str(root / 'scripts/run_evals.py'), 'run',
               '--cases', str(plan / 'cases.jsonl'), '--runner-config', str(plan / 'runner.json'),
               '--runner', 'claude', '--condition', row['condition'],
               '--condition-skill', str(plan / (row['condition'] + '.md')),
               '--next-case', row['case_id'], '--trials', '1', '--retries', '0',
               '--budget-usd', '5', '--output', str(output)]
    print(json.dumps({'starting': row['sequence'], 'case': row['case_id'], 'arm': row['condition']}), flush=True)
    result = subprocess.run(command, cwd=root, capture_output=True, text=True)
    events = [json.loads(line) for line in ledger.read_text().splitlines()] if ledger.exists() else []
    finished = [event for event in events if event['event'] == 'finished']
    known = sum(event['cost_usd'] or 0 for event in finished)
    unknown = any(event['cost_usd'] is None for event in finished)
    print(json.dumps({'completed': row['sequence'], 'returncode': result.returncode,
                      'cost_usd': known, 'unknown_cost': unknown}), flush=True)
    if result.returncode or unknown or known > 5:
        print(result.stdout, result.stderr, flush=True)
        raise SystemExit(1)
print('COMPLETE: 68 scheduled responses', flush=True)
