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

## Routing scenarios

The positive and negative routing corpus is bundled at
[`skills/flow-lean/evals/scenarios.json`](../skills/flow-lean/evals/scenarios.json).
`evals/scenarios.json` is a compatibility symlink to that one source. Named
invocations and controls are kept in [`explicit-controls.json`](explicit-controls.json)
for separate native-host checks; they are not implicit-routing training data.
[`routing-probes.json`](routing-probes.json) retains additional public phrasing
and boundary probes outside calibration; report misses rather than hiding them. Routing
checks measure skill selection; they do not prove response quality or native
plugin invocation.

## Latest source-update checks

The [2026-09-27 check report](results/concision-2026-09-27.md) records isolated
Claude installation, focused Claude/Codex response checks, local routing,
and the failed or incomplete checks. The
[2026-09-26 report](results/concision-2026-09-26.md) remains historical evidence.
Neither is a paired comparison or a benchmark release-gate pass.

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
22 cases, 3 conditions: 66 calls per full run.

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

`runners.example.json` defines two Claude runners. Don't compare results
across them.

- `claude` is for text-only response-style evaluations, which is what this
  harness measures. It runs from a fresh empty temporary directory
  (`"cwd": "empty"`). `--tools ""` removes built-in tools, and
  `--strict-mcp-config` removes MCP servers, including claude.ai connectors
  such as mail or chat. `--system-prompt` replaces the coding-agent prompt.
  The run aborts if a call writes into that directory.
- `claude-native` runs from the repository root with read tools available.
  Use it only for tests that are meant to read files, such as skill or
  reference loading.

- `codex` runs `codex exec` from a fresh empty temporary directory with a
  read-only sandbox. It ignores `config.toml` and execpolicy rules, and turns
  off plugins, apps, hooks and web search. It reports no dollar cost, so pass
  `--allow-unmetered`.

Both Claude runners pass `--setting-sources ""`, so locally installed skills,
flow-lean included, cannot leak into the `baseline` condition.

**Known limit:** Claude Code still injects its environment context (working
directory, git flag, OS and date) into the `claude` runner. The `codex`
runner still lists skills from `~/.codex/skills`, `~/.agents/skills` and the
bundled system skills, and keeps its shell tool, which can read outside the
empty directory. Before a Codex `baseline` run, check that no flow-lean or
source skill (caveman, ponytail, i-have-adhd) is installed there. Fully
isolated text runs need a direct API runner.

Before this change, the `claude` runner ran from the repository with read
tools and MCP servers available. Its results, including every committed one
up to v0.3.3, are not directly comparable with runs made with the new
`claude` runner.

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

The committed v0.2.0 result files used the former 13-case suite. They remain
historical evidence only. Run all three conditions again before publishing a
current-version comparison against the 25-case suite.
