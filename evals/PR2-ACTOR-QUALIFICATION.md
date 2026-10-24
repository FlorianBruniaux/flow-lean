# PR #2 actor-fidelity qualification preparation

**Preparation record; execution completed under a later authorization.** The [80-response campaign](results/pr2-actor-qualification-2026-10-24.md) cost $2.767168 reported and failed both the full and original-core gates. The frozen plan below had zero provider calls and zero authorized budget; it remains preserved unchanged. The preceding [34-case campaign](results/pr2-contract-qualification-2026-10-24.md) failed with one candidate blocker. The new instruction and evaluation material do not establish improved model adherence. No merge or global installation follows from this preparation.

## Change and cases

The canonical repository skill now distinguishes the source speaker, source addressee, action owner and approver before resolving pronouns. The quote's addressee is not automatically the user or assistant reading it. Preserve ability, permission, commitment, negation and current approval state; retain genuine ambiguity instead of inventing a role. The completion check maps each action and approval back to its source actor. This replaces the earlier closing reminder rather than duplicating it.

All 34 existing task prompts, including the shared rollback resource, remain unchanged from the 2026-10-24 campaign. Every earlier criterion remains in order. Only `speaker-commitment` receives additional explicit role criteria. Six [actor regressions](actor-fidelity.jsonl) extend the prepared campaign to 40 cases and 80 responses:

| Case | Distinction to preserve |
|---|---|
| `actor-reversed-draft` | Draft recipient acts; author approves, the inverse of the original case |
| `actor-third-party-fr` | Alice acts, Karim approves, Bob receives the quoted French message |
| `actor-direct-assistant` | The user acts; the assistant really is the explicitly addressed approver, without approving |
| `actor-separate-delivery` | Nora sends to Maya; Leo approves |
| `actor-permission-not-promise` | The user can review; only the recipient may approve; neither permission implies a promise |
| `actor-ambiguous-approval` | Carol acts; the sentence does not disambiguate Alice versus Carol as approver |

[Reviewer-only oracles](actor-fidelity-oracles.json) retain manually resolved roles, accepted examples and rejected counterexamples for these six cases and the original failure. The original rejected answer is copied unchanged from the recorded campaign. The other examples are authored fixtures, not model outputs. Oracles are frozen for review, never appended to model prompts. No keyword matcher or automatic semantic judge is introduced: identical pronouns can express different roles, and valid paraphrases need semantic review.

## Freeze and qualification gate

```bash
python3 scripts/prepare_pr2_qualification.py \
  --with-rollback-reference --with-actor-regressions \
  --output evals/local/pr2-actors-next
python3 scripts/run_evals.py validate --cases evals/local/pr2-actors-next/cases.jsonl
```

The explicit actor option adds six cases; omitting it keeps the 34-case preparation available. Neither command starts a runner. Both conditions receive the same 40 tasks, one trial each, against full main `2c368a71ad9dea556986411baae26a0590348a6a`. Twenty focus cases run first, including the original 13 and the seven actor cases. First-arm order alternates 20/20. No model/runtime is selected and no runner authorization is created.

A later execution requires a new explicit budget authorization. Freeze its model, runtime, runner, conditions, schedule and total budget before generation. Use a shared cost ledger including retries and any paid grading, stopping on unknown cost. Do not reuse a completed campaign's allowance or reinterpret a prepared plan as spending permission.

Report the full 40, unchanged 34 core prompts, seven actor cases, original 13 focus cases and rollback separately. The 34-case core and full 40 must each pass the existing numerical gate: correctness and safety no more than 0.1 below main and strictly higher weighted score. Require complete pairs, zero candidate rubric/fact blockers across all 40, and all applicable executable checks passing without UNKNOWN. Added cases cannot dilute a core failure. A focus-group pass cannot replace the full gate; a failing comparator never excuses a candidate blocker.

For the seven actor cases, read the response in its actual viewpoint and record who performs each action, who approves, what the trigger/modality is, and what approval state is asserted. Compare meaning with the oracle, not literal wording. Swapped actors, an assistant commitment substituted for the user's, permission converted into obligation, or invented certainty in the ambiguous case are blocking findings. Do not force an extra question when identifying the ambiguity answers the task.

Preserve masked grades and a separate factual audit before unmasking. Disclose same-agent judging and possible style leakage. Optional technical claims remain auditable. Test delivered rollback code unchanged, including all 18 scenarios, 17 supplemental methods, argument paths and explanatory failure phases. Keep the input-provenance counterexample available when auditing instructions to supply trusted installation postimages.

## Evidence limits

Offline tests verify preparation behavior: shared task delivery, balanced pairing, preserved prompts/criteria, oracle separation and source hashes. Authored positive/negative examples calibrate a reviewer; they do not prove that a model will distinguish those cases. The known development corpus is not a holdout, and n=1 does not establish reliability or causal improvement.

The previous CLI run introduced a project reference absent from the inputs. Its origin remains UNKNOWN. Before interpreting a future campaign as isolated, inspect native initialization evidence or use a separately reviewed direct API runner. Result-only receipts and empty working directories alone are insufficient. This preparation changes no runner and claims no isolation repair.
