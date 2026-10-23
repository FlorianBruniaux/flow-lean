# PR #2 contract qualification preparation, 2026-10-23

Status: **PREPARED_NOT_RUN**. Zero provider calls and zero authorized budget. The [last completed campaign](results/pr2-reference-qualification-2026-10-22.md) remains failed with 3 candidate blockers. These source corrections and offline tests do not establish that future model answers will comply. No merge or global installation is authorized by this preparation.

## Candidate changes

The rollback CLI now warns that exit 3 can follow target mutations and directs the caller to retained evidence. The code and usage contract distinguish preflight refusal, final verification failure, changed-lock cleanup and I/O failure. Exit numbers remain compatible: 0 completion, 2 argument error, 3 refusal, 4 I/O failure. Neither 3 nor 4 locates the mutation phase. No automatic retry, transaction or crash-recovery guarantee is introduced.

The general factual-detail rule now requires a necessary added claim to follow the stated mechanism and configuration, including its state transitions. A product feature name does not establish adjacent functionality or deployment guarantees. Unsupported optional examples are omitted; necessary uncertain details retain their precise dependency. This addresses both the Redis TTL explanation and Astro rendering/caching conflation without adding separate product rules to the skill. The evaluation criteria name these observed failures explicitly.

Primary references checked on 2026-10-23: [Redis expiry](https://redis.io/docs/latest/commands/expire/) removes an expired entry; [Astro on-demand rendering](https://docs.astro.build/en/guides/on-demand-rendering/) is server rendering, with adapter-specific configuration. An expiry bound on one entry is not a universal freshness guarantee for the whole application. On-demand rendering does not forbid caching; it does not establish it by itself.

## Freeze the next paired campaign

```bash
python3 scripts/prepare_pr2_qualification.py \
  --with-rollback-reference \
  --output evals/local/pr2-contract-20261023
python3 scripts/run_evals.py validate --cases evals/local/pr2-contract-20261023/cases.jsonl
```

Keep the same 34 case IDs and full main comparator `2c368a7`, one trial per arm, 68 planned responses. Thirteen focus cases run first, including the two factual-detail cases. The first arm still alternates 17/17. All 33 non-rollback prompts are unchanged; only the shared rollback code/contract changes. Both arms receive exactly that same updated resource. All prior criteria are retained in order, with additions for the three blockers. Frozen hashes cover the full matrix, cases, instructions, resource code, contracts and tests.

The resource change makes this a new assisted rollback variant. Do not compare its rollback result with earlier assisted or unassisted results as if the prompt were unchanged, or attribute an improvement to the candidate instructions alone. Report the whole 34-case corpus, unchanged 33-case subset, 13-case focus group and rollback separately. The focus group differs from the prior 11-case group. This is a known development corpus, not a holdout.

Select and freeze model, runtime and runner only after a new explicit execution authorization. Use one shared budget ledger covering all generation, retries and any paid grading. Unknown cost stops execution. This preparation does not reuse the previous $5 authorization and must not contact a model. CLI result receipts without initialization events do not prove complete native isolation.

## Verification and grading

1. Grade all responses with masked conditions and the unchanged rubric. Preserve grades before unmasking, disclose same-agent judging and identity leakage, and perform a separate categorical fact audit. No candidate blocker can be averaged away. Unsupported optional claims remain auditable even when outside the requested core answer.
2. For rollback, inspect and extract the unchanged delivered program. Execute all 18 scenarios and its real CLI argument, success and error paths. Run the supplemental reference tests against the delivered program only if its interface and scope match; otherwise adapt the test invocation transparently. Never repair the answer before testing or assume copied source proves correct prose.
3. Test refusal both before mutation and after restoration at final verification and lock cleanup. Also inject I/O failure before replacement and after restoration before deletion. Assert exit code, target contents, cache existence, retained evidence, no `complete` receipt on failure, and preservation of foreign lock state. A refusal may happen after both targets changed. Test actual behavior and explanatory claims together.
4. For cache explanations, trace hit, miss and expiry under the stated configuration. Do not require write invalidation for expiration to work, or infer global freshness from TTL alone. For rendering advice, distinguish server rendering, regeneration and configured cache behavior; neither a feature name nor a framework comparison supplies missing settings. Correct concise answers may omit optional examples entirely.

The release gate remains: complete pairs; zero candidate rubric or fact blockers; all applicable executable checks passing with no UNKNOWN; correctness and safety each no more than 0.1 below main; strictly higher weighted score. A failing comparator does not excuse a candidate blocker. No gate, corpus or score is changed after results are seen.

## Offline evidence and limits

The new CLI tests exercise observed state, not an inferred meaning of an error number. Red tests first reproduced missing post-mutation warnings; green tests include preflight refusal, verification refusal, changed owner, I/O before/after restoration and successful completion. Existing metadata, unrelated content, lock and argument checks remain. POSIX checks do not establish Windows rollback or exclusion of external writers.

The planner test compares the new inputs to the preserved previous campaign, requiring identical 34 IDs, 33 unchanged prompts and preservation of every earlier criterion. This tests preparation integrity; it does not grade model answers. BM25 checks use disposable Claude Code/Codex projections with isolated caches. They do not update or qualify the global installation.

Guillaume's proposed split and relative merge criterion are separate decisions. This preparation keeps the current scope and absolute gate requested by the active task; one trial cannot establish that model errors are independent of a prompt change. Splitting code for offline validation can be considered without retrospectively declaring the failed response campaign successful.
