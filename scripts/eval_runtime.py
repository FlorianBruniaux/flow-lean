"""Provenance and append-only attempt accounting for the offline style harness."""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import subprocess
import tempfile
import time
import uuid
from contextlib import contextmanager
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     allow_nan=False).encode('utf-8')).hexdigest()


def file_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def append(path, row):
    with path.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps(row, ensure_ascii=False, allow_nan=False) + '\n')
        stream.flush()
        os.fsync(stream.fileno())


@contextmanager
def output_lock(path):
    lock = Path(str(path) + '.lock')
    try:
        stream = lock.open('x', encoding='utf-8')
    except FileExistsError as exc:
        raise ValueError(f'Output locked: {lock}. Check the owning process before removing a stale lock.') from exc
    try:
        with stream:
            stream.write(str(os.getpid()))
        yield
    finally:
        lock.unlink()


def write_manifest(path, manifest):
    fd, name = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(manifest, stream, indent=2, ensure_ascii=False, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def money(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value) if math.isfinite(value) and value >= 0 else None


def provider_failed(stdout, response_format):
    if response_format == 'claude-json':
        payload = json.loads(stdout)
        if isinstance(payload, list):
            payload = next((event for event in reversed(payload)
                            if event.get('type') == 'result'), None)
            if payload is None:
                raise ValueError('Claude event stream has no result event')
        return bool(payload.get('is_error'))
    if response_format == 'codex-jsonl':
        return any(json.loads(line).get('type') in ('turn.failed', 'error')
                   for line in stdout.splitlines() if line.strip())
    return False


def execute(args, cases, runner, instructions, prompts, parse_response, read_jsonl):
    if not math.isfinite(args.budget_usd) or not 0 < args.budget_usd <= 25:
        raise ValueError('--budget-usd must be finite, greater than 0 and no more than 25')
    if args.trials < 1 or args.retries < 0:
        raise ValueError('trials must be positive and retries non-negative')
    observed_version = 'UNKNOWN'
    if runner.get('version_command'):
        version = subprocess.run(runner['version_command'], capture_output=True, check=True,
                                 text=True, encoding='utf-8', timeout=15, cwd=ROOT)
        observed_version = version.stdout.strip()
        if not observed_version:
            raise ValueError('Runner version command returned no version')
    selected = sorted(args.case or [case['id'] for case in cases])
    context = {
        'schema_version': 1,
        'cases_sha256': digest(cases),
        'runner_name': args.runner,
        'runner_sha256': digest(runner),
        'declared_model': runner.get('model', 'UNKNOWN'),
        'declared_runner_version': runner.get('runner_version', 'UNKNOWN'),
        'observed_runner_version': observed_version,
        'rubric_sha256': file_digest(ROOT / 'evals/rubric.md'),
        'harness_sha256': digest({name: file_digest(ROOT / 'scripts' / name)
                                  for name in ('run_evals.py', 'eval_runtime.py')}),
        'trials': args.trials, 'case_ids': selected,
        'execution': 'fresh-temporary-directory-per-attempt',
        'python': platform.python_version(), 'platform': platform.system(),
    }
    fingerprint = digest(context)
    condition = {'instructions': instructions, 'prompts_sha256': digest(prompts)}
    condition_fingerprint = digest(condition)
    output = args.output.resolve()
    manifest_path = Path(str(output) + '.manifest.json')
    ledger_path = Path(str(output) + '.attempts.jsonl')
    output.parent.mkdir(parents=True, exist_ok=True)
    with output_lock(output):
        if manifest_path.exists():
            manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
            if manifest.get('context') != context or manifest.get('run_fingerprint') != fingerprint:
                raise ValueError('Run provenance changed; use a new output file.')
        else:
            if any(p.exists() and p.stat().st_size for p in (output, ledger_path)):
                raise ValueError('Missing provenance for existing evidence; use a new output file.')
            revision = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT,
                                      capture_output=True, text=True, encoding='utf-8', check=False)
            manifest = {'context': context, 'run_fingerprint': fingerprint,
                        'git_revision_at_creation': revision.stdout.strip() or 'UNKNOWN',
                        'cases': cases, 'conditions': {}}
        old_condition = manifest['conditions'].get(args.condition)
        if old_condition is not None and old_condition != condition:
            raise ValueError('Condition provenance changed; use a new output file.')
        manifest['conditions'][args.condition] = condition
        write_manifest(manifest_path, manifest)

        events = read_jsonl(ledger_path) if ledger_path.exists() else []
        starts, finishes = {}, {}
        for event in events:
            if event.get('run_fingerprint') != fingerprint:
                raise ValueError('Attempt provenance mismatch')
            kind, attempt_id = event.get('event'), event.get('attempt_id')
            if kind not in ('started', 'finished') or not isinstance(attempt_id, str):
                raise ValueError('Invalid attempt journal event')
            bucket = starts if kind == 'started' else finishes
            if attempt_id in bucket or (kind == 'finished' and attempt_id not in starts):
                raise ValueError('Duplicate or unpaired attempt journal event')
            bucket[attempt_id] = event
        known_cost = sum(money(row.get('cost_usd')) or 0 for row in finishes.values())
        unknown_cost = len(set(starts) - set(finishes)) + sum(
            money(row.get('cost_usd')) is None for row in finishes.values())
        if unknown_cost and not args.allow_unmetered:
            raise RuntimeError('UNKNOWN attempt cost: refusing further calls; external spending cap required for --allow-unmetered.')

        # The finished event is authoritative if a crash preceded the response write.
        successes = {aid: row['result'] for aid, row in finishes.items() if row.get('status') == 'success'}
        prior_rows = read_jsonl(output) if output.exists() else []
        seen = set()
        for row in prior_rows:
            aid = row.get('attempt_id')
            if aid in seen or row != successes.get(aid):
                raise ValueError('Response evidence does not match the attempt journal')
            seen.add(aid)
        for aid, row in successes.items():
            if aid not in seen:
                append(output, row)
        done = {(row['case_id'], row['trial'], row['condition']) for row in successes.values()}
        for trial in range(1, args.trials + 1):
            for case in cases:
                key = (case['id'], trial, args.condition)
                if case['id'] not in selected or key in done:
                    continue
                if args.next_case is not None and case['id'] != args.next_case:
                    continue
                for attempt in range(args.retries + 1):
                    remaining = args.budget_usd - known_cost
                    if remaining <= 1e-9:
                        print('Budget exhausted; stopping.')
                        return 2
                    invocation = list(runner['command'])
                    if runner.get('budget_flag'):
                        invocation.extend([runner['budget_flag'], f'{remaining:.4f}'])
                    invocation.append(prompts[case['id']])
                    identity = {'attempt_id': uuid.uuid4().hex, 'run_fingerprint': fingerprint,
                                'condition_fingerprint': condition_fingerprint, 'case_id': case['id'],
                                'trial': trial, 'condition': args.condition, 'runner': args.runner}
                    append(ledger_path, {**identity, 'event': 'started', 'timestamp': time.time()})
                    started = time.monotonic()
                    try:
                        with tempfile.TemporaryDirectory(prefix='flow-lean-eval-') as work:
                            completed = subprocess.run(invocation, check=False, capture_output=True,
                                                       cwd=work)
                    except OSError as exc:
                        append(ledger_path, {**identity, 'event': 'finished', 'status': 'failed',
                                            'cost_usd': None, 'error': str(exc), 'elapsed_seconds': time.monotonic()-started})
                        raise RuntimeError('Runner could not start; attempt recorded with UNKNOWN cost.') from exc
                    text, usage, cost, error = '', {}, None, None
                    # Decode explicitly; byte corruption is an error, never silent replacement in responses.
                    try:
                        stdout = completed.stdout.decode('utf-8')
                        text, usage, cost = parse_response(stdout, runner.get('response_format', 'text'))
                        cost = money(cost)
                        if not text:
                            error = 'Empty response'
                        if provider_failed(stdout, runner.get('response_format', 'text')):
                            error = 'Provider reported failure'
                    except (UnicodeError, ValueError, TypeError, AttributeError) as exc:
                        error = f'Invalid response: {exc}'
                    result = {**identity, 'response': text, 'usage': usage, 'cost_usd': cost}
                    status = 'success' if completed.returncode == 0 and not error else 'failed'
                    finished = {**identity, 'event': 'finished', 'status': status,
                                'returncode': completed.returncode, 'cost_usd': cost,
                                'usage': usage, 'elapsed_seconds': time.monotonic()-started,
                                'stdout': completed.stdout.decode('utf-8', errors='backslashreplace'),
                                'stderr': completed.stderr.decode('utf-8', errors='backslashreplace'),
                                'error': error, 'result': result}
                    append(ledger_path, finished)
                    known_cost += cost or 0
                    unknown_cost += cost is None
                    if status == 'success':
                        append(output, result)
                    if cost is None and not args.allow_unmetered:
                        raise RuntimeError('UNKNOWN attempt cost: refusing further calls; see attempt journal.')
                    if known_cost > args.budget_usd + 1e-9:
                        print('Provider-reported cost exceeded budget; stopping.')
                        return 2
                    if status == 'success':
                        break
                    if attempt == args.retries:
                        raise RuntimeError('Runner failed; inspect the attempt journal before resuming.')
                    time.sleep(min(2**attempt, 5))
        label = 'known subtotal; total UNKNOWN' if unknown_cost else 'reported total'
        print(f'Cost ({label}): ${known_cost:.4f}')
    return 0
