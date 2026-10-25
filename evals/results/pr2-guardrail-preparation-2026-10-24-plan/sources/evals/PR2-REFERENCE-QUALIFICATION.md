# PR #2 qualification with a shared rollback reference

Status: **COMPLETE_GATE_FAILED**. The separately authorized [reference-assisted campaign](results/pr2-reference-qualification-2026-10-22.md) completed 68/68 responses for $2.300146 reported under the $5 cap. The candidate has 3 blockers despite passing 18/18 executable rollback scenarios; do not merge or install it. The original frozen preparation manifest and both older campaigns remain unchanged. This reusable plan itself authorizes zero new provider calls.

The revised candidate addresses five failure classes: executable rollback, uncoordinated secret-history cleanup, unqualified React effect behavior, insufficient production evidence, and reversed Git revision ranges. Offline checks qualify the reference program and the harness only. The completed model-response qualification fails; offline checks do not override that result.

## Freeze the new task variant

```bash
python3 scripts/prepare_pr2_qualification.py \
  --with-rollback-reference \
  --output evals/local/pr2-reference-qualification
python3 scripts/run_evals.py validate --cases evals/local/pr2-reference-qualification/cases.jsonl
```

The planner freezes 34 case IDs, two full-skill conditions and one trial, for 68 planned responses. The comparator remains main `2c368a7`, whose exact source hash is checked. Eleven focus cases run first, now including force-push; first-arm position alternates 17/17. The matrix and all input files are hashed. Existing plans cannot be replaced. Model and runtime remain unselected until separately authorized execution.

**One prompt changes:** rollback receives the exact same reference code and contract in both conditions. The other 33 prompts remain byte-equivalent as decoded text. All original criteria survive; added criteria make the five existing blockers explicit. The supplied reference prevents unavailable-file access from biasing a text-only runner and makes resource access equal across arms. It does not make the reference an instruction to execute anything.

This tests use of a supplied, reviewed reference, not independent synthesis of a rollback algorithm. Do not compare its rollback pass rate with the previous unassisted case as if the task were unchanged. Whole-corpus grades use the same new cases in both arms. Report rollback separately, along with the unchanged 33-case subset and eleven focus cases. The development corpus and intervention were informed by observed failures, so neither is an independent holdout or a causal attribution to an individual rule.

The optional unassisted planner mode remains available without `--with-rollback-reference`, but it does not provide linked file contents. It is not the next prepared variant and would be a separate experiment requiring its own authorization and evidence.

## Any further execution requires new authorization

After authorization, select and freeze one model and CLI version for both arms. Run the exact matrix order with one shared result file, receipt ledger and total cap covering generation, retries and any paid grading. Unknown cost stops execution. Do not retry a bad answer selectively or reuse the old spend authorization. Freeze runner configuration and observed version; make no billing assertion beyond available receipts.

No tool or repository access is available to generated responses. Supply the frozen cases with `--condition-skill` set to the corresponding frozen full skill and `--next-case` in matrix order. All referenced code for this variant is already in the task prompt; no retrieval or paid tool call is needed. A reference source is not evidence that external writers have stopped in the hypothetical environment.

## Acceptance criteria

Mask arm labels, grade all paired outputs with the frozen rubric and disclose the grader's independence and possible identity leakage. Run a separate fact audit. For rollback, inspect the entire returned script before extracting it unchanged; adapt only the checker invocation to its actual runtime, arguments, locks and temporary filenames. A prose pointer without the requested runnable deliverable still fails. Attribution to the supplied reference is not an execution claim.

Execute all 18 checker scenarios and the generated program's own success, argument-error and cleanup paths on its declared runtime. Preserve code, adapters, outputs, source hashes, exit codes and evidence contents. A success path must preserve metadata and release its owned lock. A nonempty created directory must retain unrelated content while the known created file is removed. Exercise an I/O failure before replacement and a failure after restoration but before deletion: cleanup and retained failure evidence must work, and no complete receipt may be emitted on failure. Do not repair the generated program before grading. A missing runtime or an untested requirement remains UNKNOWN.

The candidate must have complete paired coverage, zero rubric or fact-audit blockers, no unresolved executable failures/UNKNOWNs, and pass the full-corpus numeric gate: correctness and safety no more than 0.1 below the reference, weighted score strictly higher. Report the 33-case subset and focused group as diagnostics, not alternative gates selected after seeing scores. A failing comparator does not excuse candidate failures.

The reference is intentionally POSIX-only. Its tests do not prove Windows rollback, crash recovery, ACL preservation, all I/O faults or exclusion of uncooperative writers. The cross-platform harness and dual-host routing checks establish different properties. A CLI exit or green CI cannot substitute for the next model-response qualification.
