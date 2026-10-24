# PR #2 reference-assisted qualification, 2026-10-22

**COMPLETE_GATE_FAILED. Do not merge or install this candidate.** All 68 scheduled responses completed for **$2.300146 reported** against the newly authorized $5 total cap, without retries or extra paid grading calls. The candidate scores **4.5662/5 versus 4.3103**, but has **3 blocking responses versus 5**. Better averages do not satisfy the preregistered zero-blocker rule.

## Frozen comparison and evidence limits

Candidate: `69bf59bbcf5774625fb4608211ba5dbb9a778660`, skill SHA-256 `78d453df4d73fdd15d3be758d4d1330511749fac121871cab24d210861e925d2`. Comparator: main `2c368a71ad9dea556986411baae26a0590348a6a`, full skill SHA-256 `b592b638b5c43898463302b8816a1e5019821a373a74d9fa2c36daf8713b4bac`.

Both conditions use `claude-sonnet-5`, Claude Code `2.1.308`, 34 cases and one trial per case. The frozen matrix runs 11 focus cases first, with the first condition alternating across pairs, 17 each. There are 68 starts, 68 successful finishes and 68 matching responses; receipts report only `claude-sonnet-5`. No costs are unknown. The costs are CLI-reported subscription list-price equivalents; billed cash is **UNKNOWN**.

This is the prepared **shared-rollback-reference** variant. Both arms receive the same Python program and contract in the rollback prompt. The other 33 prompts are unchanged. The original preparation manifest remains `PREPARED_NOT_RUN` with zero authorization: the separate execution authorization records this new campaign. No earlier receipts, scores or results were replaced.

The implementing Codex assistant graded the 68 masked outputs, then froze the grades and separate claim audit before revealing arm names. This is **not independent grading**. Wording and style can reveal condition identity. The development corpus and intervention were informed by previous failures; this is neither a holdout benchmark nor a causal test of individual rules. One trial does not estimate reliability or establish a general improvement.

The runner configured no tools, strict empty MCP, disabled slash commands and settings sources, a generic system prompt, and fresh temporary directories. Receipts report no server tool use or working-directory entries. They are single result objects without initialization events, so complete native isolation is not independently established.

## Results

| Measure | Main comparator | Candidate |
| --- | ---: | ---: |
| Responses | 34 | 34 |
| Correctness | 4.1765 | 4.4706 |
| Decision fidelity | 4.6765 | 4.9412 |
| Gate fit | 4.0882 | 4.4706 |
| Concision | 4.1176 | 4.0882 |
| Safety | 4.5294 | 4.8235 |
| Weighted score | 4.3103 | 4.5662 |
| Blocking responses | 5 | 3 |
| Reported cost | $1.016146 | $1.284000 |
| Output tokens | 12,321 | 11,890 |
| Cache-creation input tokens | 223,200 | 291,241 |
| Words, whitespace split, including code | 3,592 | 3,764 |
| Median words per response | 60.5 | 70 |

The candidate costs **26.36% more**, generates **3.50% fewer output tokens**, and uses **30.48% more cache-creation input tokens** on this campaign. This is not total token savings. Token and word counts measure different things; complete copied scripts contribute to these totals. No cost claim transfers to native sessions or other caching patterns.

The unchanged 33-case subset scores 4.5879 versus 4.3045, with 2 versus 5 blockers. The 11-case focus group scores 4.4955 versus 3.6273, with 1 versus 4 blockers. These are preregistered diagnostics, not substitute release gates. The full-corpus numeric thresholds pass; the zero-blocker and categorical fact checks fail.

## Three candidate blockers

1. **Rollback error-state guarantee.** The supplied code is copied exactly and passes execution checks, but the answer asserts that exit 3 means no mutation happened. The retained [fault-injection probe](pr2-reference-qualification-2026-10-22-evidence/probe_exit_contract.py) changes lock ownership after the real replacement. The unchanged program restores `config.md`, deletes `cache/new.json`, retains the foreign lock, writes `validated/restored/verified/failed` receipts and returns 3. The implementation correctly refuses to claim completion; the surrounding explanation falsely guarantees an untouched state. [Probe results](pr2-reference-qualification-2026-10-22-evidence/exit-contract-probe.json).
2. **Redis expiration.** The candidate adds that stale data persists after TTL expiry without invalidation, despite showing a finite-TTL cache entry. Redis expiration removes the entry; the stated explanation is false for the shown cache flow. The comparator's indefinite-staleness claim has the same defect. Separate races or stale database reads would require different reasoning. [Redis key expiration](https://redis.io/docs/latest/develop/using-commands/keyspace/).
3. **Astro rendering.** The candidate treats Astro on-demand rendering as incremental static regeneration with retained CDN caching, an alternative to SSR. On-demand rendering is server rendering; adapter and cache configuration determine any regeneration/caching behavior. [Astro on-demand rendering](https://docs.astro.build/en/guides/on-demand-rendering/).

The comparator also blocks on unconditional history purge, the missing development Strict Mode exception, raw diagnostic disclosure in the missing-information case, and an environment-only debug gate on an internet-facing staging endpoint. A failing comparator does not excuse candidate defects. [GitHub history-removal guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository), [React effect reference](https://react.dev/reference/react/useEffect), [OWASP error handling](https://cheatsheetseries.owasp.org/cheatsheets/Error_Handling_Cheat_Sheet.html).

The categorical audit distinguishes false claims from unverified detail. Unversioned bundle sizes, speculative diagnoses and overbroad implementation advice are not silently treated as verified. Their grading rationale and nonblocking contract misses remain in the [frozen grades](pr2-reference-qualification-2026-10-22-evidence/grades-blind.jsonl) and [claim audit](pr2-reference-qualification-2026-10-22-evidence/fact-audit-blind.json).

## Rollback execution and local verification

Both outputs reproduce the supplied reference byte-for-byte: SHA-256 `934f4e5b08a1547876a42d7b39c6be3178fc408f15742192aa0573b0708833a0`. Each passes **18/18 scenarios**, **12 supplemental unittest methods**, and four argument/help paths on Python 3.9.6/POSIX. The supplemental methods include a repeat of the 18-scenario suite; these are overlapping checks, not 30 distinct scenarios.

Checks cover metadata, complete/failed receipts, nonempty directory preservation, owned lock cleanup, foreign lock contents, and I/O failures before replacement and after restoration before deletion. Generated scripts were inspected and executed unchanged. The added exit-contract probe is a diagnostic of the prose guarantee, not a newly invented acceptance threshold or a repair to either answer.

This validates use of the supplied reference, not independent rollback synthesis. It cannot be compared directly with the earlier unassisted 15/18 result as evidence of a prompt-only gain. The tests do not establish external writer exclusion, all I/O faults, crash recovery, ACL/xattr/atime preservation or Windows rollback. The injected lock change deliberately exercises defensive failure handling; it does not simulate enforced writer exclusion.

The repository's **74 offline tests pass** and the corpus validates. The campaign verifier reproduces the summary and rejects five corruptions even after their inventory entry is rehashed: missing response, altered receipt cost, altered instructions, changed frozen grade and failed supplemental rollback tests. [Verifier checks](pr2-reference-qualification-2026-10-22-evidence-checks.json).

The evaluated code SHA has [four successful CI jobs](https://github.com/FlorianBruniaux/flow-lean/actions/runs/39821444301): Linux Python 3.9/3.12, Windows harness and plugin loading. Windows skips POSIX rollback behavior. CI is an offline/source check, not approval of these generated responses.

## What this supports retaining

Keep the tested rollback resource and its explicit writer-exclusion, metadata and partial-failure boundaries. The experiment shows that both variants can reuse it successfully when supplied, but the candidate still overstates its exit contract. The next useful correction is to make failure-state interpretation explicit and test the explanation against actual exits, rather than add another generic promise of safety.

Keep the scope/reuse/comment-preservation rules: their focused editing examples retain the intended helper, remove obsolete comments and preserve unrelated ones. The rename response still searches too narrowly for non-call references. Keep coordinated history cleanup, the Strict Mode exception, scoped production evidence and correct remote-only Git ranges: the candidate handles those cases in this sample. This supports their relevance, not their individual causal effectiveness.

Protected diagnostics remain necessary, but the candidate still suggests a token-gated raw-response fallback in one case and an ambiguous return-more-detail configuration in another. These are contract misses, not proven unauthenticated disclosure in those candidate outputs. Do not present them as fully solved.

For Redis and Astro, the common failure is extra technical detail stated without adequate qualification. A general rule to preserve the requested answer and verify optional specifics is more testable than accumulating one product-specific exception per observed failure. A future qualification needs fresh cases and repeated trials to estimate reliability. No further provider calls are authorized by this report, and no global installation was changed.

## Reproduce the evidence checks without model calls

```bash
python3 evals/results/pr2-reference-qualification-2026-10-22-verify.py
python3 evals/results/pr2-reference-qualification-2026-10-22-check-evidence.py
```

These scripts inspect stored evidence and reject inconsistency; they do not run providers or generated programs. The raw [answers](pr2-reference-qualification-2026-10-22.jsonl), [receipt ledger](pr2-reference-qualification-2026-10-22.jsonl.attempts.jsonl), [scores](pr2-reference-qualification-2026-10-22-scores.jsonl), [summary](pr2-reference-qualification-2026-10-22-summary.json), and [artifact inventory](pr2-reference-qualification-2026-10-22-evidence/artifact-hashes.json) are retained. The evidence folder also contains the original execution controller and runner for provenance; do not run those as offline checks or reuse this spent authorization.
