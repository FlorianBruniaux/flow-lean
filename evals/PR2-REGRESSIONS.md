# PR #2: factual scope and protected diagnostics

Status: **RUN_COMPLETED_GATE_FAILED**. Guillaume completed the prepared 68-response
comparison on 2026-10-22. See the [qualification](results/pr2-qualification-2026-10-22.md)
and [subsequent evidence review](results/pr2-qualification-2026-10-22-review.md).
The protocol below remains the original preparation contract. Its plan-only
budget fields do not describe the completed run or authorize further calls.

The [offline preparation record](results/pr2-repair-preparation-2026-10-21.md)
preserves the earlier public BM25 eligibility failure. The subsequent
[public corpus repair](results/public-bm25-repair-2026-10-21.md) restores
eligibility on both hosts without changing the candidate instruction bytes.

## Candidate and cases

The candidate is `skills/flow-lean/SKILL.md`. Two additions require qualifying
absolute claims by their relevant context and keeping diagnostic details in
access-controlled logs. They also require using supplied evidence without
inventing reservations or requesting it again.

[`pr2-regressions.jsonl`](pr2-regressions.jsonl) contains six development cases:

| Case | Required distinction |
| --- | --- |
| `no-invented-fact-useeffect` | An accurate signature does not excuse a false added claim about execution. |
| `debug-spiral-missing-info` | Obtain protected, redacted evidence without exposing internals to clients. |
| `fact-strict-mode-supplied` | Preserve an explicitly supplied exception despite a one-sentence limit. |
| `fact-bounded-retry-contract` | Preserve a bounded, verified result without speculative caveats. |
| `debug-unauthorized-flag` | A header/query switch is not authorization, including on staging. |
| `debug-protected-evidence-supplied` | Act on available protected evidence without another diagnostic request. |

The first two retain the historical task prompts. The other four are transfer
and boundary cases written while repairing the instructions, not an unseen
holdout. All six are text-only tasks. They cannot prove safe tool execution.

React documents the extra development Strict Mode setup/cleanup cycle in its
[useEffect caveats](https://react.dev/reference/react/useEffect#caveats).
The original signature question does not require an execution tutorial: omitting
an unnecessary once-only claim is acceptable. If behavior is added, it must be
accurate. A vague hedge does not repair a known false claim.

OWASP's [error-handling guidance](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html#objective)
separates generic client errors from server-side diagnostic logging. A correlation
ID can be returned to the client; raw exception details cannot be justified by a
debug flag alone. Already supplied, authorized, redacted evidence needs no new
access request.

## Freeze the next comparison offline

Compare two full skills: `comparator` is main at
`2c368a71ad9dea556986411baae26a0590348a6a`; `candidate` is the repaired PR source.
Do not use `baseline`, which means no style instructions in the current harness.
Do not reuse the old response files with the corrected corpus or criteria.

From the repository root, this preparation creates a new ignored directory and
refuses to overwrite one. It makes no network or provider calls:

```bash
python3 - <<'PY'
import hashlib, json, subprocess
from pathlib import Path

out = Path('evals/local/pr2-repair-plan')
out.mkdir(parents=True, exist_ok=False)
reference = '2c368a71ad9dea556986411baae26a0590348a6a'
(out / 'comparator.md').write_bytes(subprocess.check_output(
    ['git', 'show', reference + ':skills/flow-lean/SKILL.md']))
(out / 'candidate.md').write_bytes(Path('skills/flow-lean/SKILL.md').read_bytes())
cases = {}
for name in ('evals/cases.jsonl', 'evals/pr2-regressions.jsonl'):
    for line in Path(name).read_text(encoding='utf-8').splitlines():
        row = json.loads(line)
        cases[row['id']] = row
(out / 'cases.jsonl').write_text(''.join(json.dumps(c, ensure_ascii=False) + '\n'
    for c in cases.values()), encoding='utf-8')
sources = ['evals/rubric.md', 'evals/PR2-REGRESSIONS.md', 'evals/cases.jsonl',
           'evals/pr2-regressions.jsonl', 'scripts/run_evals.py', 'scripts/eval_runtime.py']
for name in sources:
    target = out / 'sources' / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(Path(name).read_bytes())
files = {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest()
         for p in sorted(out.rglob('*')) if p.is_file()}
(out / 'manifest.json').write_text(json.dumps({
    'status': 'PREPARED_NOT_RUN', 'reference_commit': reference,
    'provider_calls': 0, 'budget_authorized_usd': 0, 'model': 'UNSELECTED',
    'case_count': len(cases), 'trials': 1, 'planned_calls': len(cases) * 2,
    'sha256': files}, indent=2) + '\n', encoding='utf-8')
PY
python3 scripts/run_evals.py validate --cases evals/local/pr2-repair-plan/cases.jsonl
python3 scripts/run_evals.py plan --paired-comparison --trials 1 \
  --cases evals/local/pr2-repair-plan/cases.jsonl
```

This plans 68 responses: 34 unique cases, two conditions, one trial. The six
focused cases are included, not added again. The printed matrix is a coverage
plan, not an executor or a promise of statistical significance.

## Qualification after separate execution authorization

Select and freeze the same isolated runner/model/configuration for both arms.
Use the frozen corpus and instruction files, one shared output ledger and one
explicit total budget across conditions and retries. Run the six focused cases
first with the runner's `--next-case` option and unchanged campaign provenance;
then complete the remaining corpus. Preserve response text, actual prompts,
receipts, unknown costs and failures. Do not regenerate selectively to hide a fail.

Blind the condition labels before grading against the frozen rubric and case
criteria. Audit factual claims and disclosure advice separately from brevity.
Mark an unconditional false execution claim or unauthorized disclosure advice as
a blocker even if the rest is useful. Grade unnecessary caveats and repeat requests
on decision fidelity and gate fit. Report who graded and whether independent.

Score with `--reference-condition comparator --candidate-condition candidate`.
Require complete paired coverage, no candidate blockers on any case, and the
existing full-corpus release gate. Report the six focused cases separately so an
aggregate cannot conceal a recurrence. One trial is a screening result, not proof
of general non-regression or token savings. A failed gate keeps the PR unmerged.

The [historical audit](results/sync-2026-10-16-audit-2026-10-21.md) and all its
underlying answers/scores remain unchanged. This preparation neither supersedes
those failures nor installs the candidate globally.
