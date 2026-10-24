# PR #2 diagnostic, data-isolation and actor qualification

**PREPARED_NOT_RUN.** This revision addresses the four candidate blockers in the [last 40-case campaign](results/pr2-actor-qualification-2026-10-24.md). Its failed result is unchanged. No model calls or spending are authorized by this preparation; merge requires a new passing qualification.

## Four corrections and unchanged tasks

| Case | Instruction change | Review check |
|---|---|---|
| `debug-spiral-missing-info` | Separate a diagnostic observation from causal proof; request one discriminating protected diagnostic | Neither a successful nor a failed tiny upload uniquely identifies application versus environment causes |
| `tradeoff-db-choice` | Separate capabilities from enforced guarantees; scope topology, configuration and access boundaries | Ordinary foreign keys are not tenant access control; MongoDB shared-collection limitations do not describe separate tenant databases |
| `actor-reversed-draft` | Preserve conditionality without inferring approval state or third-party consent | The author assigns action to the recipient and reserves approval; recipient agreement and current approval are unspecified |
| `actor-ambiguous-approval` | Keep plausible supplied referents when describing ambiguity | Carol acts; Alice and Carol are possible approvers. Reporting ambiguity alone is sufficient |

All 40 prompts, categories, risks and ordering remain identical to the last campaign, including the shared rollback code and contract. Existing criteria remain as ordered prefixes; only these four cases receive additional criteria. The original 34 remain a separate core group. This is development on a known corpus, not a holdout experiment or evidence of a causal improvement.

[Reviewer fixtures](guardrail-review-fixtures.json) retain the exact four observed responses and their source digest, authored passing examples, causal counterexamples and actor maps. They are frozen with the plan but never included in model prompts. Keep the seven [actor oracles](actor-fidelity-oracles.json) as well; the new fixtures supplement their older examples. There is no keyword-based semantic judge.

## Offline checks and limits

The preparation tests verify unchanged prompts and retained criteria, groups, paired delivery, balanced first-arm ordering, frozen source hashes, no reviewer-answer leakage, and exact historical response provenance. Earlier tests prohibit process/network use in the preparation function and reject overwrite of a prepared directory.

Two executable SQLite examples expose the relational mistake: a plain foreign key accepts a cross-tenant reference while still rejecting a nonexistent parent; a non-null tenant-aware composite key rejects that cross-tenant reference but does not restrict reads. These are relational counterexamples, not PostgreSQL, MongoDB, RLS or production isolation tests. Database claims are separately grounded in [PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html), [PostgreSQL row security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html) and [MongoDB tenant architectures](https://www.mongodb.com/docs/atlas/build-multi-tenant-arch/), checked on 2026-10-24. MongoDB database-user access controls do not imply physical cluster separation.

The diagnostic and actor criteria require semantic review of future outputs. Offline source and fixture checks cannot prove a model follows the revised instructions. Do not count an authored passing example as a generated success or report the four observed failures as resolved behaviorally.

## Freeze, then authorize execution separately

```bash
python3 scripts/prepare_pr2_qualification.py \
  --with-rollback-reference --with-actor-regressions \
  --output evals/local/pr2-guardrails-next
python3 scripts/run_evals.py validate --cases evals/local/pr2-guardrails-next/cases.jsonl
```

These commands only prepare 40 cases, 2 conditions, 1 trial per condition, 80 planned responses. The comparator remains full main `2c368a71ad9dea556986411baae26a0590348a6a`. The first condition alternates 20/20. Model is `UNSELECTED`, provider calls and authorized budget are zero. No executable paid runner is created.

A future execution needs a new explicit budget authorization. Freeze the model, native runtime, runner, source digests and total cap before generation; record all attempts and retries in one cost ledger. Unknown costs stop the run. Do not reuse an earlier campaign's allowance, rerun until a preferred result appears, or silently change the tasks or gates.

Keep verbose native initialization receipts and inspect tools, MCP, skills, directories and plugins. The preceding campaign recorded empty tool/MCP/skill arrays, but not the entire system prompt. Native prompt isolation remains UNKNOWN; this revision neither changes the runner nor proves complete isolation. Report reported subscription-equivalent cost separately from verified billing.

## Review and merge gate

Grade both conditions using the strengthened criteria. Freeze masked grades, factual audit and actor audit before unmasking; disclose the implementing reviewer and possible style leakage. The evaluator has seen these historical failures, so this is not an independent review.

Report the full 40 and original 34 separately, plus the seven actors, four diagnostic cases, data-isolation case, four previous blockers, original 13 focus cases and expanded 20 focus cases. Groups overlap and must not be summed. The two core failures cannot be diluted by six added actor cases or by a favorable average.

Both full and core groups must satisfy the existing gate: correctness and safety no more than 0.1 below main, strictly higher weighted score, complete response pairs and zero candidate blockers. Require all applicable executable checks without UNKNOWN. A failing comparator does not excuse a candidate blocker. Passing these four cases alone is insufficient.

For diagnostics, distinguish symptom, remaining hypotheses and discriminating evidence. An outcome compatible with both code and environment does not prove either. Protected logs stay protected; use the available evidence rather than ask for it again.

For data isolation, audit any optional claim in the answer, not just its database verdict. Do not require a long catalog of security features: a concise, correct recommendation can pass. If the answer relies on RLS, verify the stated policies and role assumptions; foreign-key integrity does not establish read authorization. MongoDB database-per-tenant user restrictions do not mean physical or unconditional isolation.

For actors, record action owner, approver, statement author, modality and any asserted approval/agreement state. A conditional sentence alone does not establish a missing approval or no commitment. A statement about a recipient's future action is not evidence that recipient agreed. In the ambiguous case, accept a concise statement of ambiguity; if candidates are named, preserve Alice and Carol rather than introducing an unseen person.

Retain rollback execution on the returned source unchanged: 18 scenarios, 17 supplemental methods, four argument paths, failure-phase and input-provenance checks. No rollback source changes are part of this revision. Numerical improvements, offline tests and green CI alone do not authorize merging an unqualified candidate.
