# Minimal-core comparison protocol

Status: a local v2 pilot completed on 2026-10-17: 25 cases across four conditions,
one trial each, 100 successful responses, $3.912252 CLI list-price equivalent
under a $5 total ceiling. Same-agent review found correctness and safety defects;
no quality-equivalence or release-gate pass is established. Local evidence is in
`evals/local/core-v2-2026-10-17/REPORT.md` (ignored by Git, not public evidence).
These fixtures are experimental prompt inputs, not installed skills.
`skills/flow-lean/SKILL.md` remains the published contract. No further paid calls
are authorized by preparing this revision.

| Condition | Instructions | Purpose |
| --- | --- | --- |
| `baseline` | Common text-only context, no style instructions | Measure the host's response under the same task conditions |
| `generic` | `candidates/generic.md` | Control for a simple concision request |
| `minimal` | Explicit `--condition-skill evals/candidates/minimal-v2.md` | Test the revised core and explicit safeguards |
| `candidate` | `skills/flow-lean/SKILL.md` | Current full skill |

The v1 file `candidates/minimal.md` remains unchanged and is still the CLI default
for `minimal`. Select v2 explicitly; its instruction snapshot and fingerprint
distinguish it from v1. See the [candidate rationale](candidates/README.md).

The minimal fixtures deliberately omit specialized defaults such as the skills
footer, explicit recap modes, diagram examples and the lexical blacklist. The
existing corpus includes specialized cases: report these failures separately,
not as noise to remove after seeing results. This is not a drop-in replacement
or a native routing experiment. The same fixture can be injected by either host;
only the Claude runner example is provided. A Codex runner needs separately
verified isolation and an external spending cap when dollar usage is unavailable.

## Text-only corpus revision

Every condition, including baseline and comparators, now receives the same
`evaluation_context`: no tools, repository or network access; supplied paths and
facts describe the scenario; requested code and commands are text deliverables.
This context is included in the actual prompt and its fingerprint. It declares
the environment without supplying answers or safety criteria. The harness is
for text-only comparisons; a future tool-enabled evaluation needs its own context
and fixtures, not this runner framing.

Five cases were reframed while retaining all 25 IDs:

| Case | Revision and boundary |
| --- | --- |
| `destructive-force-push` | Shared-branch decision exercise with unknown remote history; requires a written response and prerequisites, not a push. |
| `scope-nullable-email` | Supplies the PostgreSQL schema and requests proposed SQL; no hidden files to discover. |
| `recap-off-actions` | Supplies package, version, artifact and local-check facts; requests three written next steps. |
| `rollback-concurrent-edits` | Requires a runnable script, declares available backup/hash inputs, and grades the executable deliverable separately from concurrency safeguards. |
| `authorized-completion` | Explicitly requests a fictional final-message example; no confusion with actual operations in the runner directory. |

Four other cases have stronger judge criteria without changing their task:
`secret-hardcoded-key` checks unsafe history-cleanup advice;
`no-invented-fact-useeffect` checks exceptions to absolute behavior claims;
`speaker-commitment` checks invented current approval state and immediacy;
`requested-detail` checks the difference between integration tests and production
evidence. The React case intentionally has no supplied reference: it evaluates
knowledge calibration under no lookup access, and permits explicit uncertainty.
The judge verifies claims separately. It does not measure retrieval ability.

These are development-set repairs informed by observed failures, not new holdout
cases. Do not compare v2 scores directly with the old pilot: even unchanged task
text now receives different environment framing, and criteria have changed.
Historical manifests, responses and scores remain frozen. A future comparison
must regenerate every condition using the same revised corpus and rubric.

## Before paid calls

Run offline checks and inspect the full matrix:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/run_evals.py validate
python3 scripts/run_evals.py plan --core-comparison --trials 3
```

The current corpus has 30 cases. Four conditions and three trials give **360
planned calls**, before failures/retries. One trial gives 120 calls and is useful
for a pilot, not for a general savings claim. No estimated dollar savings are
inferred from prompt length.

Choose the model, CLI version, total spending allowance, trial count and rubric
before generation. Use a fixed configuration, and record whether sessions/cache
are cold or warm when observable. Otherwise label cache state `UNKNOWN`. Keep
provider token categories separate; do not add a nested reasoning-token field
to output tokens without checking whether it is already included.

The 30 public cases are a development suite. Reserve separate, independently
written cases before tuning a winner. Do not label the existing suite a holdout.
Freeze the selected winner before running that reserved set on each target host.

## Run a pilot

These commands invoke the provider and may consume paid credits or subscription
quota. The completed local pilot used frozen source copies and a rotated condition
order. These examples do not authorize another run. The example allowance is
**$5 total for the shared output**, not $5 per
condition, and may stop the campaign before completion.

```bash
mkdir -p evals/local
python3 scripts/run_evals.py plan --core-comparison --trials 1 > evals/local/core-v2-plan.jsonl

python3 scripts/run_evals.py run --runner claude --condition baseline \
  --trials 1 --budget-usd 5 --output evals/local/core-v2.jsonl
python3 scripts/run_evals.py run --runner claude --condition generic \
  --trials 1 --budget-usd 5 --output evals/local/core-v2.jsonl
python3 scripts/run_evals.py run --runner claude --condition minimal \
  --condition-skill evals/candidates/minimal-v2.md \
  --trials 1 --budget-usd 5 --output evals/local/core-v2.jsonl
python3 scripts/run_evals.py run --runner claude --condition candidate \
  --condition-skill skills/flow-lean/SKILL.md \
  --trials 1 --budget-usd 5 --output evals/local/core-v2.jsonl
```

Use a new filename if the skill, model, runner, corpus, rubric, selected cases,
trial count or harness changes. Repeat campaigns with a preselected shuffled or
rotated condition order and record it to expose order/cache effects. The runner
executes one condition at a time; the printed matrix is not an interleaving scheduler.
Incomplete campaigns cannot be treated as paired comparisons.

## Judge and decide

Use the existing rubric and fact-audit. Hide condition names, fingerprints and
instruction text from the judge. Randomize labels; if using a model for pairwise
judging, reverse response order and report disagreements. Judge correctness,
fidelity and safety before concision; an omitted condition cannot be compensated
by fewer words. Preserve the judge identity/version, prompt and raw judgments
alongside the generation manifest. The runner does not call or validate a judge.

Create score rows with the actual condition names after unblinding. Compare the
minimal fixture directly to the full skill:

```bash
python3 scripts/run_evals.py score evals/local/core-v2-scores.jsonl \
  --reference-condition candidate --candidate-condition minimal
```

Also compare each contender with `baseline` and `generic` by changing these
options. All conditions present in a score file must cover identical case/trial
pairs, without duplicates. Historical score files remain supported.

Publish correctness, decision fidelity, safety and blockers per case/category,
alongside output tokens, input/cache usage, reported cost including failed
attempts and latency. Missing usage is unknown, not zero. Report outliers and
variation across trials, not just a mean. The legacy weighted-score gate is an
advisory check; it does not establish statistical non-inferiority or authorize a
release. A cheaper response with a critical omission is rejected.

Only then test removing one block at a time from the full skill. Preserve the
rest, assign a new output, and keep the same evaluation protocol. Choose retained
rules from observed behavior and validate on reserved cases before publication.

This first comparison is single-turn. It cannot establish full-session savings,
native reference loading, or reduced clarification/repair turns. Those require a
separate multi-turn campaign after selecting candidates.
