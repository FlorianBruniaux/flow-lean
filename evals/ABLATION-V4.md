# Minimal v4: fixed safeguards and rule ablations

Status: **PREPARED_NOT_RUN**. Provider calls: 0. Authorized budget: $0. Model: UNSELECTED. This plan grants no execution, merge or global-installation authority.

## Candidate scope

The experimental source is `evals/candidates/v4-groups.json`; `minimal-v4.md` is its checked rendering. The public `skills/flow-lean/SKILL.md` and installed Claude/Codex skills remain unchanged. The preparer builds a disposable installable package from the rendered candidate plus the repository's unchanged routing corpus and bounded rollback resources. Routing checks use disposable dual-host projections and caches, never the live shared installation.

The fixed core preserves source actors, modality and evidence; consequential authorization; protected diagnostics; unrelated/concurrent work; and rollback preimages, trusted postimages, writer exclusion, refusal, receipts and verification. Compatibility controls and footer behavior are also identical across the five v4 conditions. These safeguards are not variables in this experiment. Static construction proves their retention, not model adherence.

Four removable modules cover density, code-change scope/reuse, presentation and completion-report conventions. They add preferences and workflow guidance around the fixed safety floor. Removing a module does not instruct the model to do the opposite: default behavior may already satisfy the same cases.

## Seven conditions and 24 new tasks

| Condition | Instructions |
|---|---|
| `comparator` | Frozen full main `2c368a7` |
| `pr2_full` | Frozen failed PR candidate `c0ec3cd` |
| `v4` | Fixed core, four modules and controls |
| `v4_without_density` | Only density removed |
| `v4_without_scope` | Only code-change guidance removed |
| `v4_without_format` | Only presentation guidance removed |
| `v4_without_status` | Only completion conventions removed |

`ablation-v4-cases.jsonl` contains 24 newly authored prompts in 12 contrast pairs: four tasks for each removable module and eight shared safeguard probes. Prompts supply the needed scenario facts; they request written deliverables, not unavailable tools. They distinguish brief/detailed output, exact prose/JSON, existing/absent helpers, obsolete/relevant comments, comparison/single choice, runtime/static relationships, completed/pending authorization, scoped/absent limitations, permission/promise, missing/decisive diagnostics, isolation capability/configuration and conflicting/partially completed rollback.

These are new prompts not used in the earlier model campaigns, but their author has seen the previous failures. They are development contrast cases, **not an independent holdout**. Similar behavioral motifs are deliberate. Exact duplicate IDs/prompts are rejected; this does not prove semantic novelty. Expectations and counterexamples are authored reviewer material in `ablation-v4-oracles.json`, not model outputs. Neither those answers nor grading criteria enter generation prompts.

All seven conditions receive each new case once: **168 planned calls**. Case order is seeded, and cyclic condition order balances each condition's position to within one occurrence. Each call must use a fresh session/cwd. The planner freezes the complete prompts, instruction/resource/source hashes, corpus, rubric, contrasts and original 40-case evidence. It neither selects a paid runner nor launches one. This larger matrix must not inherit a previous $5 allowance or assume it fits a future one.

## Analysis specified before execution

Compare v4 with both main and the failed full candidate. For each single-module removal, compare against intact v4 on all 24 tasks, its four targeted tasks, and the eight safeguard probes. Publish paired per-case differences, five rubric dimensions, weighted scores, every blocker and literal-claim audit, response words, actual usage tokens, total reported cost and cost completeness. Keep product-convention misses separate from safety/factual errors. Report all conditions, not only the best one.

A module is only a removal candidate if the ablation has no blockers, no additional blocking case, correctness/safety/decision-fidelity losses of at most 0.1 on both all-case and target-family averages, and a measurable cost or instruction-size reduction. A tie or mixed signal is inconclusive with one trial. These are exploratory screening rules, not proof of equivalence or an automatic release gate. Never trade a new actor, evidence, security or rollback failure for shorter output. Do not use the existing scorer's strictly-higher-score release verdict as the rule-removal decision; inspect the paired dimensions and focus subset.

Single-module effects are conditional on the other three modules remaining. They do not establish that several removals can be combined safely. Do not silently combine the apparent winners, change scoring after unmasking, or rerun failed cases until they pass. Freeze randomized-label grades and both factual/actor audits before revealing conditions; describe the reviewer's relationship to the implementation and possible style leakage.

After choosing and freezing a candidate, the original 40 prompts remain a separate confirmation phase against full main: 80 calls, requiring a new authorized scope/budget. Report the original 34 and all 40 separately with the unchanged zero-blocker and relative-score gates. This phase is not included in the 168-call matrix and has no selected winner or generated paid runner yet. Unchanged rollback code tests do not qualify changed usage instructions. Any executable answer requires the applicable behavior checks before release.

## Reproduce preparation without providers

```bash
python3 scripts/prepare_v4_ablation.py --check
python3 scripts/prepare_v4_ablation.py --output /tmp/new-flow-lean-v4-plan
python3 scripts/prepare_v4_ablation.py --verify /tmp/new-flow-lean-v4-plan
python3 -m unittest discover -s tests -v
```

The existing harness accepts the seven condition names using explicit condition-skill files. A future execution must bind the model, runtime, runner, shared budget and attempts ledger to the frozen matrix before any call; unknown cost or source drift stops it. Existing score commands accept the resulting labels. No runner configuration or execution command is created here.

The package at `PLAN/skill/` has the same metadata and scenarios as the public skill. Use the installed router with `scripts/check_routing.cjs ROUTER_ROOT NEW_REPORT PLAN/skill --preview-personal` to test both clients without installation. Word/byte reductions are deterministic source measurements, not tokenizer measurements, savings or quality results.

The preview mode copies each host's effective personal routing catalog into temporary directories and substitutes the candidate homonym there. This accommodates Claude's personal-before-project precedence; Codex still selects the project projection. Other skill metadata/corpora remain byte-identical in the mirror. Live catalogs, thresholds and caches are not modified. Passing preview routing is not proof that the candidate is installed or selected in a native session. The default checker still rejects a project candidate shadowed by a different personal skill.

Text comparison of working-tree instructions accepts LF/CRLF checkout representation. Frozen historical digests and every archived source byte remain exact; the source snapshots retain their original bytes. The rendered generation instructions use LF on both platforms.
