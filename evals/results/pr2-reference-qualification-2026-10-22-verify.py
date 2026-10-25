"""Verify this campaign offline, without executing generated code or providers."""
import hashlib
import json
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[2]
PREFIX = ROOT / 'evals/results/pr2-reference-qualification-2026-10-22'
EVIDENCE = Path(str(PREFIX) + '-evidence')
sys.path.insert(0, str(EVIDENCE / 'sources/scripts'))
from eval_runtime import digest
from run_evals import _condition_prompt, _parse_response, summarize_scores


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def rows(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify():
    inventory = load(EVIDENCE / 'artifact-hashes.json')
    for name, checksum in inventory.items():
        require(sha(PREFIX.parent / name) == checksum, 'Published artifact changed: ' + name)
    plan = load(EVIDENCE / 'manifest.json')
    for name, checksum in plan['sha256'].items():
        require(sha(EVIDENCE / name) == checksum, 'Frozen file mismatch: ' + name)
    auth = load(EVIDENCE / 'authorization.json')
    require(auth['budget_total_usd'] == 5 and auth['generation_retries'] == 0, 'Authorization mismatch')
    require(sha(EVIDENCE / 'runner.json') == auth['runner_sha256'], 'Runner file mismatch')
    manifest = load(Path(str(PREFIX) + '.jsonl.manifest.json'))
    cases = rows(EVIDENCE / 'cases.jsonl')
    context = manifest['context']
    require(manifest['git_revision_at_creation'] == auth['candidate_commit'], 'Generator revision mismatch')
    require(manifest['cases'] == cases and len(cases) == 34, 'Corpus mismatch')
    require(context['case_ids'] == sorted(c['id'] for c in cases) and context['trials'] == 1, 'Context coverage mismatch')
    require(context['cases_sha256'] == digest(cases), 'Corpus digest mismatch')
    require(manifest['run_fingerprint'] == digest(context), 'Context fingerprint mismatch')
    require(context['runner_sha256'] == digest(load(EVIDENCE / 'runner.json')['claude']), 'Runner digest mismatch')
    require(context['rubric_sha256'] == sha(EVIDENCE / 'sources/evals/rubric.md'), 'Rubric mismatch')
    require(context['harness_sha256'] == digest({n: sha(EVIDENCE / 'sources/scripts' / n)
            for n in ('run_evals.py', 'eval_runtime.py')}), 'Harness mismatch')
    require(context['declared_model'] == auth['model'] == 'claude-sonnet-5', 'Model configuration mismatch')
    require(context['observed_runner_version'] == '2.1.308 (Claude Code)', 'Version mismatch')
    require(set(manifest['conditions']) == {'candidate', 'comparator'}, 'Condition mismatch')
    for arm in manifest['conditions']:
        instructions = (EVIDENCE / (arm + '.md')).read_text()
        require(manifest['conditions'][arm]['instructions'] == instructions, 'Instructions mismatch')
        prompts = {c['id']: _condition_prompt(c['prompt'], arm, instructions) for c in cases}
        require(manifest['conditions'][arm]['prompts_sha256'] == digest(prompts), 'Prompts mismatch')
    answers = rows(Path(str(PREFIX) + '.jsonl'))
    matrix = rows(EVIDENCE / 'matrix.jsonl')
    require([(r['case_id'], r['condition']) for r in answers] ==
            [(r['case_id'], r['condition']) for r in matrix], 'Scheduled order mismatch')
    expected = {(c['id'], arm, 1) for c in cases for arm in ('candidate', 'comparator')}
    require(len(answers) == 68 and {(r['case_id'], r['condition'], r['trial']) for r in answers} == expected, 'Incomplete coverage')
    starts, finishes, models = {}, {}, set()
    for event in rows(Path(str(PREFIX) + '.jsonl.attempts.jsonl')):
        aid = event['attempt_id']
        require(event['run_fingerprint'] == manifest['run_fingerprint'], 'Attempt fingerprint mismatch')
        require(event['condition_fingerprint'] == digest(manifest['conditions'][event['condition']]), 'Condition fingerprint mismatch')
        if event['event'] == 'started':
            require(aid not in starts, 'Duplicate start')
            starts[aid] = event
            continue
        require(event['event'] == 'finished' and aid in starts and aid not in finishes, 'Unpaired attempt')
        for key in ('case_id', 'condition', 'trial', 'runner'):
            require(event[key] == starts[aid][key] == event['result'][key], 'Attempt identity mismatch')
        require(event['status'] == 'success' and event['returncode'] == 0 and event['error'] is None, 'Failed attempt')
        require(event['cwd_entries'] == [], 'Working directory writes')
        text, usage, cost = _parse_response(event['stdout'], 'claude-json')
        require(cost is not None and cost == event['cost_usd'] == event['result']['cost_usd'], 'Receipt cost mismatch')
        require(text == event['result']['response'] and usage == event['result']['usage'], 'Receipt response mismatch')
        raw = json.loads(event['stdout'])
        require(isinstance(raw, dict), 'Unexpected receipt shape')
        models.update(raw.get('modelUsage', {}).keys())
        require(not any(usage.get('server_tool_use', {}).values()), 'Reported server tool use')
        finishes[aid] = event
    require(len(starts) == len(finishes) == 68, 'Unexpected attempt count')
    require(models == {auth['model']}, 'Observed model mismatch')
    require(all(r == finishes[r['attempt_id']]['result'] for r in answers), 'Response/receipt mismatch')
    scores = rows(Path(str(PREFIX) + '-scores.jsonl'))
    grades = rows(EVIDENCE / 'grades-blind.jsonl')
    require(sha(EVIDENCE / 'grades-blind.jsonl') == load(EVIDENCE / 'grading-freeze.json')['sha256'], 'Frozen grades changed')
    fact_audit = load(EVIDENCE / 'fact-audit-blind.json')
    require(sha(EVIDENCE / 'fact-audit-blind.json') == load(EVIDENCE / 'grading-freeze.json')['fact_audit_sha256'], 'Frozen fact audit changed')
    key = load(EVIDENCE / 'blind-key.json')['key']
    require(scores == [{**r, 'condition': key[r['case_id']][r['label']]} for r in grades], 'Grade mapping mismatch')
    require(len(scores) == 68 and {(r['case_id'], r['condition'], r['trial']) for r in scores} == expected, 'Grade coverage mismatch')
    measured, rollback = {}, {}
    for arm in ('comparator', 'candidate'):
        subset = [r for r in answers if r['condition'] == arm]
        measured[arm] = {'responses': len(subset), 'reported_cost_usd': round(sum(r['cost_usd'] for r in subset), 6),
            'words_whitespace_split': sum(len(r['response'].split()) for r in subset),
            'median_words_whitespace_split': statistics.median(len(r['response'].split()) for r in subset),
            'output_tokens': sum(r['usage']['output_tokens'] for r in subset),
            'cache_creation_input_tokens': sum(r['usage'].get('cache_creation_input_tokens', 0) for r in subset)}
        label = next(k for k, v in key['rollback-concurrent-edits'].items() if v == arm)
        report = load(EVIDENCE / ('rollback-' + label + '-report.json'))
        require(report['source_hashes'] == report['source_hashes_after'], 'Generated script changed during tests')
        script = next((EVIDENCE / Path(name).name) for name in report['source_hashes'])
        require(sha(script) in report['source_hashes'].values(), 'Extracted script changed')
        answer = next(r['response'] for r in subset if r['case_id'] == 'rollback-concurrent-edits')
        import re
        code = re.search(r'```(?:python|bash)\n(.*?)```', answer, re.S).group(1)
        require(script.read_text() == code, 'Script differs from delivered code')
        require(len(report['results']) == 18, 'Rollback coverage mismatch')
        require(report['matches_supplied_reference'] is True, 'Reference reuse mismatch')
        require(sha(script) == sha(EVIDENCE / 'sources/skills/flow-lean/scripts/rollback_reference.py'), 'Reference code mismatch')
        supplemental = report['supplemental_tests']
        require(supplemental['count'] == 12 and supplemental['success'] is True, 'Supplemental rollback checks failed')
        require(len(report['argument_errors']) == 4, 'Argument-error coverage missing')
        require(all(r['returncode'] == (0 if r['args'] == ['--help'] else 2) for r in report['argument_errors']), 'Argument-error result mismatch')
        rollback[arm] = {'supplemental_tests': 12, 'supplemental_success': True, 'argument_paths': 4, 'passed': sum(r['status'] == 'PASS' for r in report['results']), 'total': 18,
            'failed': [r['scenario'] for r in report['results'] if r['status'] != 'PASS'],
            'status': report['status'], 'label': label}
    total = round(sum(r['cost_usd'] for r in answers), 6)
    require(total <= auth['budget_total_usd'], 'Budget exceeded')
    full = summarize_scores(scores, 'comparator', 'candidate')
    fact_blockers = [{**r, 'condition': key[r['case_id']][r['label']]} for r in fact_audit['claims'] if r['blocker']]
    for finding in fact_blockers:
        require(any(s['case_id'] == finding['case_id'] and s['label'] == finding['label'] and s['blocker'] for s in scores), 'Fact blocker omitted from scores')
    probe = load(EVIDENCE / 'exit-contract-probe.json')
    require(len(probe['results']) == 2, 'Exit contract probe coverage missing')
    for r in probe['results']:
        require(r['source_sha256'] == sha(EVIDENCE / ('rollback-' + r['label'] + '.py')), 'Exit probe source mismatch')
        require(r['exit_code'] == 3 and r['after']['config'] != r['before']['config'] and not r['after']['cache_file_exists'], 'Exit probe counterexample mismatch')
        require(r['receipt_stages'] == ['validated', 'restored', 'verified', 'failed'], 'Exit probe evidence mismatch')
    gate = dict(full['release_gate'])
    gate['reasons'] = list(gate['reasons'])
    if any(r['condition'] == 'candidate' for r in fact_blockers):
        gate['reasons'].append('Candidate has categorical fact/safety blockers.')
    if rollback['candidate']['passed'] != 18 or rollback['candidate']['status'] != 'PASS':
        gate['reasons'].append('Candidate has unresolved executable failures.')
    gate['passed'] = not gate['reasons']
    return {'status': 'COMPLETE_GATE_PASSED' if gate['passed'] else 'COMPLETE_GATE_FAILED', 'qualification_gate': gate, 'provider_calls': 68, 'extra_paid_grading_calls': 0,
        'reported_generation_cost_usd': total, 'billed_cash': 'UNKNOWN',
        'configured_model': context['declared_model'], 'model_usage_keys': sorted(models),
        'observed_runner_version': context['observed_runner_version'],
        'receipt_limit': 'Single result objects, no init events; tool isolation configured, not independently established.',
        'metrics': measured, 'full_scores': full,
        'unchanged_33_scores': summarize_scores([r for r in scores if r['case_id'] != 'rollback-concurrent-edits'], 'comparator', 'candidate'),
        'fact_blockers': fact_blockers,
        'focus_scores': summarize_scores([r for r in scores if r['case_id'] in plan['focus_cases']], 'comparator', 'candidate'),
        'rollback': rollback,
        'scope': 'Offline consistency verification; no model calls or generated-script execution; grading is non-independent.'}


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
