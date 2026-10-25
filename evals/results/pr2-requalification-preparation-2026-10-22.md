# PR #2 rollback repair and offline preparation

**PREPARED_NOT_RUN.** The repository candidate and evaluation checks are repaired;
new model adherence is unverified. No provider calls or paid grading were made.
The failed 68-response campaign and its original scores remain byte-identical.

The [new protocol](../PR2-REQUALIFICATION.md) retains 34 task prompts and plans one
trial for each full-skill condition, 68 responses. Three case overrides strengthen
criteria without changing tasks or removing earlier requirements. Ten focus cases
run first, and first-arm position alternates across pairs. The plan has zero
authorized budget and requires separate execution authorization.

## What changed

The rollback instructions now require all-target validation before mutation,
refusal on missing/type/link substitutions, exclusive temporary creation,
metadata restoration and cleanup of owned resources. Original-looking state
without a matching receipt is insufficient evidence of a completed rollback.

Diagnostic instructions distinguish observed test output from hypotheses about
unseen implementation, and reject the inference that a small successful request
rules out a code bug. Raw errors stay in an authorized operator channel. Secret
remediation requires inspection and coordination before history rewriting. The
factual-scope rule now gives an omission example; it does not hardcode the answer
to the React case. These prompt changes still need response qualification.

## Executed offline checks

- **60 unit tests pass locally**, including 12 new tests for preservation checks
  and frozen-plan integrity. Negative controls cover actual temporary filenames,
  nested conflict data, other owners' lock contents, link following and leaked
  temporary files. The new rollback tests failed before the checker changes.
- **18 rollback scenarios pass** for the controlled Python program and repaired
  Bash witness. The Bash witness additionally refuses a symlinked backup and
  cache parent. These witnesses are test fixtures, not newly generated answers
  or production rollback implementations. Bash argument-error tests pass locally.
- **BM25 passes for both hosts**, eligibility and 22/22 hook probes per host,
  using the full installed catalogs with disposable projections and caches. The
  same canonical skill bytes are discovered by Claude Code and Codex. Global
  installation files are untouched; native model loading was not exercised.
- The planner freezes sources and actual prompts, rejects a changed comparator
  or weakened criteria, and refuses an existing output directory. All frozen
  source hashes match the working tree. Catalog validation passes.
- The previous qualification verifier still reconciles all 68 historical receipts.

The [machine-readable preparation record](pr2-requalification-preparation-2026-10-22.json)
contains the source/plan hashes, routing calibration and historical replay verdicts.
Full disposable replay receipts and the frozen plan remain under `evals/local/`.
Regenerate a new plan with `scripts/prepare_pr2_qualification.py`; it invokes no
subprocess or provider. Reproduce routing with `scripts/check_routing.cjs` and an
installed compatible router. Its catalog-dependent metrics are development
evidence, not a holdout or proof of response quality.

## Historical replay and merge boundary

The two previously reviewed generated rollback programs were replayed unchanged
with the expanded checker, using each program's actual temporary filename.
Source hashes were checked against the previous receipts before execution and
remained unchanged afterward. The old candidate passes 9/18 scenarios and the
old comparator 11/18. Both still destroy unrelated temporary content; the old
candidate also mutates when the expected cache postimage is absent or a directory.
These are retrospective development checks, separate from original numerical scores.

The previous commit `409f65d` has a successful
[three-job CI run](https://github.com/FlorianBruniaux/flow-lean/actions/runs/39797968147).
That result predates this repair; the new commit requires its own CI. Neither
that CI nor the local checks clear the failed model-quality gate. Keep PR #2
open until a separately authorized campaign passes the unchanged release gate,
the strengthened criteria and execution checks for its generated rollback.

The checks do not establish writer exclusion under a live race, crash recovery,
all path substitutions, ACL/ownership restoration or every I/O-failure path.
The checker is not a sandbox. No release, global installation, merge or measured
token-saving claim is included in this preparation.
