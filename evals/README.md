# Evaluations

Real, API-backed comparison of flow-lean against a plain baseline, generic
"be concise" instructions, and each of its three source skills (caveman,
ponytail, i-have-adhd). Cases live in `cases.jsonl`, the scoring contract
lives in `rubric.md`. The harness itself (`scripts/run_evals.py`) is forked
from [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) (MIT),
credited in the script header. Only the scoring weights changed.

This is different from `../EVAL.md`, which is a manual, self-graded
regression battery you paste into a fresh session after any `SKILL.md` edit.
This harness answers a different question: does flow-lean measurably beat
its inspirations and plain terseness, not just hold its own contract.

Run every command below from the repository root (`flow-lean/`), not from
inside `evals/`, `--cases` and `--runner-config` default to the right paths
under `evals/` on their own.

## Fetch comparators

Comparator `SKILL.md` files are not vendored in this repo, they are fetched
fresh before each run so the comparison always uses the current published
version, not a stale copy:

```bash
./scripts/fetch_comparators.sh
```

Writes `evals/comparators/caveman.md`, `ponytail.md`, and `i-have-adhd.md`
(gitignored).

## Validate and plan

```bash
python3 scripts/run_evals.py validate
python3 scripts/run_evals.py plan --trials 1 --include-comparator
```

`plan` prints the expected call count before any money is spent. At 1 trial,
13 cases, 3 conditions: 39 calls per full run.

## Run

Each run of `baseline` + `candidate` + `comparator` must land in its own
output file. The resumability key is `(case_id, trial, condition, runner)`,
it does not know which skill file backed a `comparator` run, so writing two
different comparators into the same file makes the second one skip every
case as "already done". Three comparators means three full runs, three files.

```bash
# Sanity run first: baseline + candidate only, no comparator, cheap
python3 scripts/run_evals.py run \
  --runner claude --condition baseline \
  --trials 1 --budget-usd 5 \
  --output evals/results/sanity.jsonl

python3 scripts/run_evals.py run \
  --runner claude --condition candidate \
  --condition-skill skills/flow-lean/SKILL.md \
  --trials 1 --budget-usd 5 \
  --output evals/results/sanity.jsonl

# Then one full baseline + candidate + comparator run per comparator
for comparator in caveman ponytail i-have-adhd; do
  out="evals/results/vs-${comparator}.jsonl"
  python3 scripts/run_evals.py run \
    --runner claude --condition baseline \
    --trials 1 --budget-usd 5 --output "$out"
  python3 scripts/run_evals.py run \
    --runner claude --condition candidate \
    --condition-skill skills/flow-lean/SKILL.md \
    --trials 1 --budget-usd 5 --output "$out"
  python3 scripts/run_evals.py run \
    --runner claude --condition comparator \
    --condition-skill "evals/comparators/${comparator}.md" \
    --trials 1 --budget-usd 5 --output "$out"
done
```

Candidate and comparator instructions are injected from the supplied skill
file, task prompts stay identical across all three conditions in a given run.

`--runner-config` defaults to `evals/runners.example.json`, no need to copy
it anywhere, the model pin (`claude-sonnet-5` per this session) lives there.
Record the exact pinned model with any published result.

`--setting-sources ""` (baked into the `claude` runner command in
`runners.example.json`) isolates every call from this machine's own Claude
Code config. Without it, any locally installed skill, including flow-lean
itself, leaks into the `baseline` condition and measures the skill against
itself.

Runs are resumable: rerun the same command after a provider failure and
completed `(case_id, trial, condition, runner)` rows are skipped, no need to
track progress by hand.

## Judge and score

`run_evals.py` only generates responses, it does not judge them. Judging is
a separate, deliberately human (or a carefully isolated LLM-judge you run
yourself) step: read `evals/results/vs-<comparator>.jsonl`, blind the
`condition` field before judging (relabel rows `A`/`B`/`C`, don't look at
which is which while scoring), and write one JSON object per response with
the fields `rubric.md` defines:

```json
{"case_id":"factual-git-log","trial":1,"condition":"candidate","correctness":5,"decision_fidelity":5,"gate_fit":5,"concision":5,"safety":5,"blocker":false,"notes":"Correct command, no preamble."}
```

Then apply the release gate:

```bash
python3 scripts/run_evals.py score evals/results/scores-vs-caveman.jsonl
```

For `no-invented-fact` cases, run the separate fact-audit pass described in
`rubric.md` before scoring, its `false` verdicts are a hard blocker
regardless of the weighted score.

Do not compare conditions produced with different cases, models, trial
counts, or rubrics. Commit `evals/results/` snapshots so numbers are
reproducible without re-spending.
