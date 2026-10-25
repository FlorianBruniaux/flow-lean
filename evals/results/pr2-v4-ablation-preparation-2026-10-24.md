# PR #2: minimal v4 and ablation preparation, 2026-10-24

**PREPARED_NOT_RUN.** A shorter experimental candidate and seven-condition comparison are ready. No provider/model calls, spending, merge or global installation were performed. The public PR skill remains byte-identical to the last tested candidate; its failed qualification is not superseded by these offline checks.

## What changed

The canonical experimental source is [v4-groups.json](../candidates/v4-groups.json), with a checked [minimal-v4 rendering](../candidates/minimal-v4.md). The [packaged skill](pr2-v4-ablation-preparation-2026-10-24-final-plan/skill/SKILL.md) provides navigable resource links and the same metadata, routing scenarios and bounded rollback resources as the public skill. Resource paths in the standalone rendering are package-relative.

The current PR skill has 3,929 whitespace-separated words and 25,698 UTF-8 bytes. V4 has **691 words and 4,861 bytes**, an **82.41% word reduction** against that PR revision. The fixed core plus metadata/controls accounts for 461 words; four removable modules supply the remainder. The older minimal-v3.1 has 625 words without the same bundled controls and four-module experiment, so v4 is not claimed to be shorter than that older artifact. These are source sizes, not tokenization, provider cost or quality measurements.

| Condition | Words | Bytes |
|---|---:|---:|
| `comparator` | 2577 | 16736 |
| `pr2_full` | 3929 | 25698 |
| `v4` | 691 | 4861 |
| `v4_without_density` | 634 | 4470 |
| `v4_without_scope` | 626 | 4399 |
| `v4_without_format` | 636 | 4497 |
| `v4_without_status` | 638 | 4508 |

All five v4 variants retain the same safety/evidence/actor/authorization/rollback core and controls. The four removals affect density, code-change scope/reuse, presentation and completion-report conventions. The current failed PR candidate and full main remain frozen controls. The preparer rejects unsupported removals and source drift; the scorer now accepts the new condition names without changing score weights or release gates.

## New contrast cases and interpretation

The [24 cases](../ablation-v4-cases.jsonl) form 12 contrast pairs, with four cases for each optional module and eight safeguard cases. Supplied facts make the tasks answerable without tools. [Reviewer-only expectations](../ablation-v4-oracles.json) include authored counterexamples; they are not model responses. Mutating those expectations and criteria changes the evidence hashes without changing the generated prompts.

The plan schedules **168 responses**, one per new case/condition, with deterministic case order and balanced condition positions. It selects no model and authorizes **$0**. No executable paid runner is generated. The 40 previous prompts are retained byte-for-byte as a separate, deferred confirmation phase, with the original 34 explicitly grouped. That phase would compare the selected candidate with main in 80 calls; it is not selected or authorized yet.

These new cases were authored with knowledge of prior failures. They are not an independent holdout, even though they have not been used in the previous model campaigns. Single-module removal measures an effect conditional on the other modules staying present; it cannot justify combining several removals. The [protocol](../ABLATION-V4.md) requires per-case differences, focused subsets, all blockers and cost completeness. One trial supports exploration, not an equivalence or reliability claim. Safety, fidelity and evidence errors cannot be averaged away by brevity.

## Offline checks and portability

**100 repository tests pass.** Eight new tests cover actual construction behavior: exact single-module removal, pairing and order, reviewer leakage, historical preservation, destination/integrity refusal, scorer compatibility, CRLF handling and non-mutating routing previews. Their initial failing runs are retained. They do not test whether a model obeys the prose.

The first routing attempt correctly failed discovery because the installed router now gives Claude's personal Flow Lean homonym precedence over the project candidate. A new `--preview-personal` option copies effective routing metadata/corpora into disposable catalogs and substitutes only Flow Lean there. The test checks both hosts and confirms the source catalog is unchanged; no global file, hook, threshold or cache is written.

The preview covers 125 active Claude skills and 166 active Codex skills. Both pass eligibility, the configured global gate and **22/22 probes**. Global calibration F1 is 0.71673 in each catalog; this is router calibration, not model quality. Candidate resources are derived from the same source and verified by hashes. The native skill packager's structure check passes, as do local resource resolution and the router's metadata parser. The separate system quick validator could not run because that Python lacks PyYAML; its validation is not claimed.

The first frozen plan remains under `-plan/`. The **final plan** adds the tested routing-preview source, its test, updated protocol and `.gitattributes` to the frozen inputs. Both plans produce the same 168 model prompts. Source snapshots retain exact bytes; only semantic working-tree comparisons tolerate LF/CRLF, so Windows checkout conversion does not masquerade as instruction drift. Historical raw digests remain strict.

Evidence:

- [Final manifest](pr2-v4-ablation-preparation-2026-10-24-final-plan/manifest.json)
- [Routing preview](pr2-v4-ablation-routing-2026-10-24.json)
- [Full test log](pr2-v4-ablation-preparation-2026-10-24-tests.log)
- [Initial preparation failures](pr2-v4-ablation-preparation-2026-10-24-red.log), [CRLF regression](pr2-v4-ablation-preparation-2026-10-24-crlf-red.log), [routing-preview regression](pr2-v4-ablation-preparation-2026-10-24-routing-red.log)

The PR's next comment records CI against the published commit. No routing or test result here establishes native activation, response quality, financial savings or readiness to merge. The previous qualification remains failed: 10 candidate blockers on 40 cases, including eight on the original 34.
