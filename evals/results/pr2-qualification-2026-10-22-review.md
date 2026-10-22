# PR #2 qualification review, 2026-10-22

**Do not merge.** Guillaume had already completed the requested 34-case,
two-condition, one-trial comparison in `6b4108e` before this review started.
Reconciliation confirms the prepared candidate, comparator and cases. No duplicate
generation was launched: **zero new provider calls and zero new provider spend**.

The original [report](pr2-qualification-2026-10-22.md), receipts, scores and blind
key remain unchanged. This is an unblinded review by the implementing assistant,
with offline execution of the generated rollback scripts. It is not an independent
human review or a new full numerical regrade.

## Evidence and cost

The [offline verifier](pr2-qualification-2026-10-22-verify.py) reconciles all 68
responses with 68 paired successful attempt receipts, their text and costs,
the 34 exact cases, prompt fingerprints, instruction text, runner configuration,
rubric/harness hashes, and the blind-grade mapping. Three corrupted copies were
rejected: a missing response, a changed receipt cost and changed instructions.

The receipt model is `claude-sonnet-5`, with Claude Code 2.1.308 on Windows.
Receipts advertise no tools or skills and contain no tool-use blocks. Built-in
plugins are listed; these checks do not establish the absence of every possible
host influence. The recorded working directories are fresh and the attempt
journal reports no directory writes. We verified submitted evidence, not the
remote machine itself.

The candidate plan hash differs from the public LF file because Windows checked
it out with CRLF. The exact normalized instructions in the run manifest match
`695c79f` (SHA-256 `41a480403ec59b5066c80b45310def38b65bc66ad386457f3798fefb4e3ee5c7`).
The comparator matches main `2c368a7`. Rubric and runner source hashes likewise
reconcile with CRLF. This is not candidate drift.

Generation receipts total **$2.245588**, below $5. The contributor describes this
as a list-price equivalent under subscription authentication, not a confirmed
cash charge. Costs of the contributor's grading subagents are not present in
the generation ledger. No claim about their total billed spend is made.

| Recorded measure | Main comparator | Candidate |
| --- | ---: | ---: |
| Responses | 34 | 34 |
| Original weighted score | 4.5603 | 4.5471 |
| Original rubric blockers | 3 | 2 |
| Generation cost reported | $1.067912 | $1.177676 |
| Output tokens reported | 19,480 | 17,508 |
| Cache-creation input tokens | 218,244 | 250,615 |
| Response words, whitespace split | 3,228 | 3,386 |
| Median response words, same method | 59.5 | 66 |

The original report's medians of 64 and 72 do not reproduce with this method;
its totals do. Candidate word count rises about 4.9%, while reported output
tokens fall about 10.1% and reported generation cost rises about 10.3%. These
measure different things; none establishes quality-preserving savings. One
trial and the fixed comparator-first order do not establish general superiority.
The original numerical gate fails on blockers and weighted score.

## Decisions on the disputed judgments

1. **`useEffect`: keep the blocker on both conditions.** The signature itself is
   fine, but the added empty-dependency claim omits the development Strict Mode
   setup/cleanup cycle. That exception was explicitly required before generation.
   [React's reference](https://react.dev/reference/react/useEffect#caveats) confirms
   it. Correct handling when the exception is supplied does not repair this miss.
2. **Hardcoded secret: keep both blockers.** Rotation comes first, correctly.
   The separate history-rewrite advice still omits inspection and coordination,
   which the frozen criterion explicitly requires. Rewriting also cannot erase
   other people's existing clones. [GitHub's guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)
   explains both constraints. Neither output proves that a leak or destructive
   rewrite actually occurred; these are unsafe proposed steps.
3. **`requested-detail`: retain the auditor's comparator blocker.** Its closing
   sentence makes staging/integration or representative data an alternative to
   production evidence. The prompt's central criterion explicitly rejects that
   inference. The candidate does require production-path evidence.
4. **Authenticated debug fallback: contract miss, not proven unauthenticated
   disclosure.** A credential gate is not equivalent to an unauthenticated boolean
   flag; no exploit or actual authorization bypass was demonstrated. Still, the
   raw-error fallback departs from this candidate's protected-log/generic-response
   contract and [OWASP guidance](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html#objective).
   Keep the original non-blocking score rather than inventing a broader automatic
   blocker after seeing the answer. A proper operator diagnostic channel can be
   authorized; this prompt did not require creating one.

The candidate's bounded retry statement is also less problematic than the
grader implies: one send with retries disabled reasonably supports no retry in
that test. Its added wording may be redundant, but is not necessarily a factual
error. This reinforces why the tiny aggregate difference is not the decisive
reason to withhold merging. Numerical grades are preserved, not selectively
adjusted until one arm wins.

## Additional executable findings

Both rollback programs were read in full, extracted unchanged from their response
code fences, and executed only against disposable fixtures with the existing
`scripts/check_rollback.py`. No application files were supplied. The local runtime
is recorded in the [review JSON](pr2-qualification-2026-10-22-review.json); this
is not Windows or Python 3.8 runtime qualification, nor a live writer-race test.

| Existing checker scenario | Comparator | Candidate |
| --- | --- | --- |
| Normal / nonempty cache | Fails original POSIX mode restoration | Same |
| Missing expected `cache/new.json` | Refuses | Restores config and reports completion |
| Config/cache content conflicts, missing config, invalid/missing backup, held lock | Pass | Pass |
| Config/cache symlink substitution | Mutates instead of refusing | Same |
| Preexisting `config.md.rollback.tmp` | Destroys unrelated file | Preserves this filename, but uses a different one |

The standard checker yields **7/12 passing scenarios for the comparator, 6/12
for the candidate**. An additional probe places unrelated content at each
program's actual restore temporary filename: `config.md.rollback.tmp` and
`config.md.rollback_tmp`. **Both programs consume that unrelated file and return
success.** These are additional blocking preservation defects, beyond the old
rubric flags. Source hashes match before and after execution.

The candidate's prose claim that any changed postimage causes a stop is therefore
not established by its script. Its missing-file branch only checks a mismatch
when the file still exists. Both fixed temporary paths use truncating writes.
These findings justify rejecting the executable deliverables independently of
the supplemental POSIX-mode checks. The new replay is reported separately; it
is not presented as a test performed by the contributor's original grader.

The response review also found unsupported diagnosis: both versions assert an
internal `basePrice` implementation from a failing assertion alone in
`debug-spiral-evidence-available`. The candidate's missing-information answer
also says a successful tiny upload excludes a code bug, which it does not.
Its protected-diagnostic improvement should not earn full correctness for those
unproven deductions. No new full 68-row score is claimed here.

## What this supports

Keep the protected-diagnostics direction as a candidate rule: it prevents direct
stack disclosure in the original missing-log case in this run. Its authenticated
fallback boundary still needs work. Do not claim the factual-scope addition is
validated: the original failure remains. Code-reuse and comment-preservation
answers retain the intended behavior, while the evidence-first debugging rule
still produces speculative diagnoses.

Before another paid comparison, repair the rollback deliverable and narrow
debugging to supported hypotheses; test the factual addition separately instead
of appending more generic warnings or repeatedly rerunning unchanged prompts.
No source-rule change, rerun, merge, release or global installation is part of
this review. The submitted campaign is sufficient to reject this candidate;
the newly authorized $5 allowance has not been spent.

Reproduce reconciliation without model calls:

```bash
python3 evals/results/pr2-qualification-2026-10-22-verify.py
```

For rollback replay, extract the first Python fence of the corresponding
`rollback-concurrent-edits` response without edits, review it, and use the argv
and lock templates in the review JSON with `scripts/check_rollback.py`.
`<extracted-script>` denotes that local reviewed file. The extra temporary-path
probe uses its recorded basename with unrelated content before invoking the
same command. Generated programs require review: the checker is not a sandbox.
