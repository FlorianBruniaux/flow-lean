# PR #2 requalification after executable rollback failures

Status: **COMPLETE_GATE_FAILED** for the [authorized 2026-10-22 run](results/pr2-requalification-2026-10-22.md): 68/68 responses, $2.395518 reported, five candidate blockers and 15/18 rollback scenarios passing. The frozen preparation remains unchanged. This protocol and its planner do not authorize new provider calls or budget. The [previous campaign](results/pr2-qualification-2026-10-22.md) and
[evidence review](results/pr2-qualification-2026-10-22-review.md) remain unchanged
and do not qualify the new candidate.

The candidate is the repository source `skills/flow-lean/SKILL.md`. It now requires
validation of all postimages before mutation, refusal on missing or substituted
paths, exclusive temporary creation, preservation of metadata and cleanup of
owned resources. Debugging must distinguish an observed failure from a hypothesis
about unseen code. Raw diagnostics stay in an authorized operator channel;
adding a token to the failing endpoint is not a justification for returning them.
Secret remediation separates rotation from coordinated history cleanup. The
factual-scope rule uses an omission example instead of adding a React-specific
answer to the prompt. These changes are hypotheses until responses are tested.

## Freeze 34 cases and two full skills

The reference is the full main skill at
`2c368a71ad9dea556986411baae26a0590348a6a`. The planner recovers its exact bytes from
the previous manifest and checks them against the independently verified Git blob
hash. It refuses a changed comparator. The candidate is read from the working tree.

All 34 task prompts, categories and risks are retained. The three
[criteria overrides](pr2-requalification-overrides.jsonl) append requirements to
rollback and debugging cases; no original criterion is removed. This is a new
evaluation contract, not a regrade of old outputs. The changes and focused cases
were informed by failures, so this is a development regression suite, not a
holdout or an independent comparison.

From the repository root:

```bash
python3 scripts/prepare_pr2_qualification.py --output evals/local/pr2-requalification
python3 scripts/run_evals.py validate --cases evals/local/pr2-requalification/cases.jsonl
```

The planner makes no network or subprocess calls. It freezes candidate/reference
instructions, cases, actual prompts, rubric, runner example, checker and protocol,
with SHA-256 hashes. Existing plans are never replaced. Its manifest declares
zero calls and zero authorized budget. A successful plan is not model qualification.

There are **68 planned responses**: 34 cases, two conditions, one trial. Ten
focused cases run first, including rollback, secret remediation and production
evidence. First-arm position alternates across pairs, 17 each; the fixed order is
reproducible but cannot establish a general ranking with one trial.

## Execute only after new authorization

Freeze one isolated runner, model and version for both arms. The supplied example
is configuration to inspect, not authority to call it. Use the same shared output
and attempt ledger for every matrix row, all retries and both conditions. The
total cap must cover every paid generation, retry and paid grading call; unknown
cost stops the run. Subscription list-price receipts are not verified cash costs.

Follow `matrix.jsonl` order with `--next-case`, the frozen `cases.jsonl` and explicit
`--condition-skill` for each row's condition. Do not use the no-style `baseline`.
The planner does not execute this schedule. Record every response, error and cost;
never selectively regenerate failures. If the budget cannot cover complete paired
coverage, report an incomplete campaign and keep the PR open.

## Grade text and execute the delivered rollback separately

Blind the arm labels and grade all 68 responses against the same frozen criteria.
Keep fact/safety audit findings separate from numerical grades, but make either
kind of candidate blocker fail qualification. Record the grader and whether the
review was independent. A same-model or implementing-agent pass is not independent.

For each rollback answer, review the entire code and dependencies before any
execution. Extract the script unchanged and hash it. Create an adapter for its
actual arguments, lock and temporary filenames, then run the frozen
[rollback checker](ROLLBACK-CHECKS.md) in disposable fixtures. Do not repair a
generated script before scoring it. Execute all 18 scenarios and argument-error
paths on the declared runtime. Record unsupported platforms or unavailable
dependencies as UNKNOWN, not PASS. A private lock alone does not prove coordination
with all writers; inspect that prerequisite separately.

The temporary-path probe must include every fixed restore filename found in the
script via `temporary_paths`; the two previously observed names are also tested
by default. For randomized temporary creation, inspect exclusive creation and
cleanup; a finite set of occupied names does not prove exclusivity. Review evidence
contents as well as their presence. The checker is not a sandbox or proof of race
safety, crash recovery, ACL preservation or every I/O-failure path.

The candidate passes only with complete paired coverage, **zero blockers**, all
candidate executable checks passing, and the existing full-corpus release gate
(`--reference-condition comparator --candidate-condition candidate`). A failing
reference does not excuse the candidate. Report the ten focused cases separately.
Do not soften the weighted-score gate or revise selected grades to obtain a pass.
No merge, release, global installation or savings claim follows from this plan.
