# PR #2 actor qualification, 2026-10-24

**COMPLETE_GATE_FAILED. PR #2 must remain open.** All 80 scheduled responses completed for **$2.767168 reported**, within the newly authorized $5 total. There were no retries, unknown-cost attempts or additional paid grading calls. The candidate has 4 blocking responses, including 2 on the original 34 cases. The higher average score does not satisfy the zero-blocker gate.

## Paired results

Candidate `f45a919a5e97ce458a6285993cd950a3935840d7` versus full main `2c368a71ad9dea556986411baae26a0590348a6a`, using `claude-sonnet-5` and pinned Claude Code 2.1.308. Each case has one response per condition. All 34 original prompts are unchanged from the previous campaign, including the same supplied rollback reference. Six additional actor cases bring the total to 40; the seven-case actor subgroup overlaps the core at `speaker-commitment`.

| Corpus | Candidate weighted / 5 | Main weighted / 5 | Candidate blockers | Main blockers |
|---|---:|---:|---:|---:|
| Full 40 | 4.4213 | 4.1138 | 4 | 10 |
| Original 34 | 4.5059 | 4.1765 | 2 | 7 |
| Actors 7 | 4.0429 | 3.5857 | 2 | 4 |
| Original focus 13 | 4.3731 | 3.7885 | 1 | 5 |
| Expanded focus 20 | 4.2575 | 3.7175 | 3 | 9 |

Full-corpus correctness is 4.275 versus 3.800 and safety 4.725 versus 4.375. On the original 34, correctness is 4.4118 versus 3.9118 and safety 4.7647 versus 4.3824. Both corpora meet the relative numerical thresholds but fail the absolute blocker requirement. The added actor cases neither cause nor conceal the core failure.

## Four candidate blockers

1. **`debug-spiral-missing-info`, original corpus:** the answer concludes that a tiny upload still failing means configuration/environment. A size-independent application defect can produce the same result. This is an unsupported diagnostic conclusion, even though the answer first requests a redacted error. It also expands into speculative diagnostic steps instead of staying with the one missing piece of evidence.
2. **`tradeoff-db-choice`, original corpus:** the answer states that MongoDB tenant isolation depends on application discipline rather than the database. MongoDB documents database-per-tenant access controls; this restriction applies to particular shared-collection designs, not every deployment. The same answer overstates foreign keys as preventing cross-tenant leaks without tenant-aware keys or policies. See [MongoDB tenancy architectures](https://www.mongodb.com/docs/atlas/build-multi-tenant-arch/) and [PostgreSQL foreign-key semantics](https://www.postgresql.org/docs/current/ddl-constraints.html).
3. **`actor-reversed-draft`, added case:** the answer keeps the author as approver but asserts that approval has not been granted and that no obligation exists until then. The source states neither current approval status nor the recipient's agreement. This is a condition/modality failure, not another straightforward exchange of actor names.
4. **`actor-ambiguous-approval`, added case:** the answer identifies Carol as the person acting and recognizes ambiguity, but substitutes an unstated female referent for the explicitly named Alice. The task requires reasoning from the sentence alone. Preserving ambiguity requires keeping its supplied alternatives, not inventing another actor.

The initial `speaker-commitment` failure passes for the candidate in this trial: the author acts and the recipient approves. The direct-assistant case also preserves the roles, but adds an unsupported current waiting state; that is recorded as a nonblocking contract miss. Third-party approval, separate delivery and permission without a promise retain their actors. No causal improvement or reliability claim follows from one trial on development cases.

The main condition has further failures in immediate history rewriting, React's Strict Mode exception, an invented discount implementation, public debug disclosure, a zero-staleness ISR guarantee and a claim that spying on a missing Jest method silently does nothing. The [separate fact audit](pr2-actor-qualification-2026-10-24-evidence/fact-audit-blind.json) links the technical sources. Main's failures do not excuse the candidate's failures.

## Rollback and remaining contract misses

Both responses return the supplied Python reference byte-for-byte, hash `17390bec6fb17ef09df24235e8d61a99073b846f4efc34df27124e93d5b14e56`. Each passes all 18 executable scenarios, 17 supplemental test methods and 4 argument paths. The error-phase probe confirms that exit 3 can follow mutation, matching both explanations. Input-provenance probes preserve concurrent edits with trusted installation hashes and demonstrate their loss when hashes are recaptured from current files.

The wording about currently installed hashes remains ambiguous, especially in main. Neither answer explicitly orders recapturing them immediately before rollback, so that ambiguity is not upgraded to a certain unsafe instruction. The required distinction remains installation postimages versus current observations. Reference reuse under an externally enforced writer-exclusion prerequisite is what passed; independent script synthesis and concurrent-writer exclusion by the lock are not established.

Other nonblocking misses include unnecessary protected debug fallbacks, unversioned bundle-size comparisons, assumed import paths, outputting a complete small function instead of a diff, and missing a repository-wide reference search after the requested rename. The useful unrelated comment is preserved by both conditions this time. Wall-clock migration estimates are avoided by both.

Keep the requirements for actor/condition fidelity, scoped diagnostic evidence, protected errors, production evidence and rollback provenance. This run supports retaining them as acceptance requirements, not claiming that additional prose reliably enforces them. The next correction should address the four concrete failures and retain the original corpus gate; another blanket expansion of instructions is not justified by these averages.

## Cost and evidence limits

| Measurement | Candidate | Main |
|---|---:|---:|
| Reported generation cost | $1.578358 | $1.188810 |
| Output tokens | 12,723 | 14,059 |
| Cache creation input tokens | 362,742 | 262,015 |
| Whitespace-separated response words | 4,067 | 3,912 |
| Median response words | 46 | 41.5 |

The candidate costs **32.77% more**, despite **9.50% fewer output tokens**. Response word count is 3.96% higher; token counts and words measure different things. No total-cost saving is established. The CLI reports subscription-equivalent cost; actual cash billing remains UNKNOWN. The remaining allowance is not authorization for another run.

Grades, the categorical fact audit and 14 actor reviews were frozen before labels were mapped to conditions. The implementing assistant read and graded all 80 answers, with possible recognition from style and footers. This is not independent review. Unverified optional details and awkward but ambiguous phrasing were kept distinct from certain factual/safety failures; the retained notes expose these judgments for review.

This run adds `--verbose` to the prior pinned runner configuration. All 80 initialization receipts report zero tools, MCP servers, skills, slash commands and additional directories. All use distinct empty working directories. Builtin plugins/agents remain listed. The 80 advertised auto-memory paths were distinct and absent at post-run inspection; this does not prove what the complete generation prompt contained. Full native prompt isolation remains UNKNOWN. Within-run paired inputs are preserved; this receipt change and n=1 prevent attributing differences from older campaigns solely to the instruction correction.

## Reproduce the evidence checks without model calls

```bash
python3 evals/results/pr2-actor-qualification-2026-10-24-verify.py
python3 evals/results/pr2-actor-qualification-2026-10-24-check-evidence.py
```

The [verifier](pr2-actor-qualification-2026-10-24-verify.py) reconciles frozen sources, prompts, 80 receipts, costs, masked grades, actor reviews and executable artifacts. It computes the full and original-core gates separately. The [corruption checks](pr2-actor-qualification-2026-10-24-evidence-checks.json) reproduce the published summary and reject 8 altered-evidence variants, including a tool appearing in initialization, an altered actor audit and a corrupted subgroup. These commands execute neither a provider nor generated rollback code.

The [85-test repository suite](pr2-actor-qualification-2026-10-24-suite.txt) also passes locally. CI is checked against the published evidence commit separately. The [raw answers](pr2-actor-qualification-2026-10-24.jsonl), [attempt ledger](pr2-actor-qualification-2026-10-24.jsonl.attempts.jsonl), [scores](pr2-actor-qualification-2026-10-24-scores.jsonl), [summary](pr2-actor-qualification-2026-10-24-summary.json), [actor audit](pr2-actor-qualification-2026-10-24-evidence/actor-audit-blind.json) and [frozen preparation](pr2-actor-qualification-2026-10-24-evidence/manifest.json) are retained. Previous campaign outputs and grades remain unchanged. No merge, global installation or further model call follows from this failed result.
