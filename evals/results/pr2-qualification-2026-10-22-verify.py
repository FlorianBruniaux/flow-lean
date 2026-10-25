"""Reconcile the submitted qualification evidence offline. No provider calls.

Run from any directory: python3 evals/results/pr2-qualification-2026-10-22-verify.py
The JSON report goes to stdout; existing evidence is never written.
"""
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from eval_runtime import digest
from run_evals import _condition_prompt, _parse_response, summarize_scores

PREFIX = ROOT / 'evals/results/pr2-qualification-2026-10-22'


def load(suffix):
    return json.loads(Path(str(PREFIX) + suffix).read_text(encoding='utf-8'))


def rows(suffix):
    return [json.loads(line) for line in Path(str(PREFIX) + suffix).read_text(
        encoding='utf-8').splitlines() if line.strip()]


def blob(revision, name):
    return subprocess.check_output(['git', 'show', revision + ':' + name], cwd=ROOT)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify():
    manifest, plan = load('.manifest.json'), load('-plan.json')
    cases = {}
    for name in ('evals/cases.jsonl', 'evals/pr2-regressions.jsonl'):
        for case in map(json.loads, blob('695c79f', name).decode().splitlines()):
            cases[case['id']] = case
    require(len(cases) == 34 and manifest['cases'] == list(cases.values()), 'Case mismatch')
    windows_cases = ''.join(json.dumps(case, ensure_ascii=False) + '\r\n' for case in cases.values()).encode()
    require(hashlib.sha256(windows_cases).hexdigest() == plan['sha256']['cases.jsonl'], 'Plan corpus hash mismatch')
    context = manifest['context']
    require(context['case_ids'] == sorted(cases) and context['trials'] == 1, 'Coverage context mismatch')
    require(context['cases_sha256'] == digest(list(cases.values())), 'Cases digest mismatch')
    require(manifest['run_fingerprint'] == digest(context), 'Context digest mismatch')
    require(manifest['git_revision_at_creation'] == '695c79f21152f3d7369668cfb64a470e15056c8f', 'Unexpected generator revision')
    require(set(manifest['conditions']) == {'candidate', 'comparator'}, 'Unexpected condition')
    hashes = {}
    for arm, revision in [('candidate', '695c79f'), ('comparator', '2c368a7')]:
        data = blob(revision, 'skills/flow-lean/SKILL.md')
        require(manifest['conditions'][arm]['instructions'] == data.decode(), 'Instruction mismatch')
        checkout = data.replace(b'\n', b'\r\n') if arm == 'candidate' else data
        require(hashlib.sha256(checkout).hexdigest() == plan['sha256'][arm + '.md'], 'Plan hash mismatch')
        hashes[arm] = hashlib.sha256(data).hexdigest()
        prompts = {c['id']: _condition_prompt(c['prompt'], arm, data.decode()) for c in cases.values()}
        require(manifest['conditions'][arm]['prompts_sha256'] == digest(prompts), 'Prompt mismatch')
    file_hashes = {}
    for name in ('evals/rubric.md', 'scripts/run_evals.py', 'scripts/eval_runtime.py'):
        checksum = hashlib.sha256(blob('695c79f', name).replace(b'\n', b'\r\n')).hexdigest()
        require(checksum == plan['sha256']['sources\\' + name.replace('/', '\\')], 'Windows source hash mismatch')
        file_hashes[name] = checksum
    require(context['rubric_sha256'] == file_hashes['evals/rubric.md'], 'Rubric mismatch')
    require(context['harness_sha256'] == digest({Path(k).name: v for k, v in file_hashes.items()
                                               if k.startswith('scripts/')}), 'Harness mismatch')
    runner = json.loads(blob('695c79f', 'evals/runners.example.json'))['claude']
    require(context['runner_sha256'] == digest(runner), 'Runner mismatch')
    starts, finishes = {}, {}
    receipt_models = set()
    for event in rows('.attempts.jsonl'):
        aid, kind = event['attempt_id'], event['event']
        require(event['run_fingerprint'] == manifest['run_fingerprint'], 'Attempt context mismatch')
        require(event['condition_fingerprint'] == digest(manifest['conditions'][event['condition']]), 'Attempt condition mismatch')
        if kind == 'started':
            require(aid not in starts, 'Duplicate start')
            starts[aid] = event
            continue
        require(kind == 'finished' and aid in starts and aid not in finishes, 'Unpaired event')
        require(event['status'] == 'success' and event['returncode'] == 0
                and event['cwd_entries'] == [] and event['error'] is None, 'Failed attempt')
        text, usage, cost = _parse_response(event['stdout'], 'claude-json')
        require(cost is not None and cost == event['cost_usd'] == event['result']['cost_usd'], 'Receipt cost mismatch')
        require(text == event['result']['response'] and usage == event['result']['usage'], 'Receipt output mismatch')
        raw = json.loads(event['stdout'])
        init = [r for r in raw if r.get('type') == 'system' and r.get('subtype') == 'init']
        require(len(init) == 1 and init[0]['tools'] == [] and init[0]['skills'] == [], 'Unexpected tools or skills')
        receipt_models.add(init[0]['model'])
        require(not any(part.get('type') == 'tool_use' for r in raw
                        for part in r.get('message', {}).get('content', [])), 'Observed tool call')
        finishes[aid] = event
    answers = rows('.jsonl')
    require(len(answers) == len(starts) == len(finishes) == 68, 'Incomplete campaign')
    focused = {c['id'] for c in map(json.loads, blob('695c79f', 'evals/pr2-regressions.jsonl').decode().splitlines())}
    require({(r['case_id'], r['condition']) for r in answers[:12]}
            == {(cid, arm) for cid in focused for arm in ('candidate', 'comparator')}, 'Focus-first order mismatch')
    require({(r['case_id'], r['trial'], r['condition']) for r in answers}
            == {(cid, 1, arm) for cid in cases for arm in ('candidate', 'comparator')}, 'Unpaired coverage')
    require(all(r == finishes[r['attempt_id']]['result'] for r in answers), 'Response/ledger mismatch')
    scores = rows('-scores.jsonl')
    key = load('-blind-key.json')['key']
    unblinded = [{**{k: v for k, v in row.items() if k != 'label'}, 'trial': 1,
                  'condition': key[row['case_id']][row['label']]} for row in rows('-grades-blind.jsonl')]
    ordered = lambda data: sorted(data, key=lambda r: (r['case_id'], r['condition']))
    require(ordered(unblinded) == ordered(scores), 'Blind grades/scores mismatch')
    summary = summarize_scores(scores, 'comparator', 'candidate')
    measured = {}
    for arm in ('comparator', 'candidate'):
        subset = [r for r in answers if r['condition'] == arm]
        measured[arm] = {'responses': len(subset), 'reported_cost_usd': round(sum(r['cost_usd'] for r in subset), 6),
                         'words_whitespace_split': sum(len(r['response'].split()) for r in subset),
                         'median_words_whitespace_split': statistics.median(len(r['response'].split()) for r in subset),
                         'output_tokens': sum(r['usage']['output_tokens'] for r in subset),
                         'cache_creation_input_tokens': sum(r['usage'].get('cache_creation_input_tokens', 0) for r in subset)}
    total = round(sum(r['cost_usd'] for r in answers), 6)
    require(total <= 5, 'Observed cost exceeds user ceiling')
    return {'status': 'EVIDENCE_RECONCILED_GATE_FAILED' if not summary['release_gate']['passed'] else 'EVIDENCE_RECONCILED',
            'new_provider_calls': 0, 'reported_generation_cost_usd': total,
            'receipt_models': sorted(receipt_models), 'instruction_hashes_lf': hashes,
            'windows_crlf_source_hashes_reconciled': True, 'metrics': measured, 'original_scores': summary,
            'scope': 'Offline consistency checks of contributor receipts, not provider billing confirmation or independent grading'}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
