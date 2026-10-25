# PR finalization, 24 October 2026

PR #8 is merged as `1e5f932598d73a9fc38901e81213d2f149759d61` after 56 local tests and all three CI jobs passed at `a52f7813ed5d164294cf346ea7b200fc032fb175`.

https://github.com/FlorianBruniaux/flow-lean/actions/runs/40102665733

The PR #2 integration passes 113 offline tests on local Python 3.9. The new archive smoke test runs the frozen editorial CLI from a temporary directory, without the live checkout or PYTHONPATH. It first failed with a missing editorial module; that module and its tests now join the frozen sources. The Git range fixture initially failed twice during cleanup. Personal Git configuration exposed a trace2 daemon integration; isolating the fixture from global/system configuration and event tracing removed the failure. No global configuration was changed.

The integrated plan is [pr2-v4-ablation-finalization-2026-10-24-plan](pr2-v4-ablation-finalization-2026-10-24-plan/manifest.json). Its manifest SHA256 is `6aa0107c29db0d5d9cd973f77c8a0fde9844375f5e22d070e7074fb9e374d21a`. All 168 generation prompts are byte-identical to the previous final plan. Previous plans remain intact and their verifier passes. Status remains `PREPARED_NOT_RUN`, model `UNSELECTED`, provider calls 0, authorized budget $0.

## Editorial report on existing responses

[Recorded counts](pr2-editorial-finalization-2026-10-24.json) cover all 80 existing responses, with the same current public-skill vocabulary across conditions. Candidate: 2/40 responses contain a prose em dash; comparator: 0/40. Neither condition contains a matched banned token outside exemptions. The two excerpts were inspected: `rollback-concurrent-edits` uses the dash in explanatory prose after its code block; `tradeoff-db-choice` uses it between clauses. These advisory findings do not change archived grades, fact audits or release gates. No model was called.

| Input or output | SHA256 |
| --- | --- |
| `evals/results/pr2-guardrail-qualification-2026-10-24.jsonl` | `94a11437e939b865c25113d5a66461d61886fb9bd96c2a90b3455c35accd95e8` |
| `evals/results/pr2-guardrail-qualification-2026-10-24-evidence/cases.jsonl` | `ab25552be3926956471bb921feb5d282efbb450476cb9df8b2be193f07d9cbd6` |
| `scripts/editorial.py` | `418a620d3c8af8790726cd8b00808050e1a1709c0dd0a6a44ba337a08c8754d4` |
| `skills/flow-lean/SKILL.md` | `6f393a7eb7dbb7d99cd048257b7607cac4225a551526aba94c7de68098f21fe5` |
| `evals/results/pr2-editorial-finalization-2026-10-24.json` | `1a3804fa733a70ae6924b4f9aaff58e14403d58cdb348591917a66d6bff052a7` |

## Remaining work

- #9: select and qualify v4 through the prepared 24-case, seven-condition screen; any paid execution needs a newly authorized model and total budget. A later selected-candidate/main confirmation has 40 cases per condition and must report the original 34 separately.
- #2: do not merge while its last real qualification has 10 candidate blockers (8 on the original 34). The 691-word v4 remains experimental and is not installed globally.
- #4: after supported rule selection, assess reference extraction with native simple-question-then-rollback and missing/unreadable-reference traces on both Claude Code and Codex. Preserve core stop conditions and footer/schema exceptions. Structural preview checks are not native model-loading evidence.

No new model calls, global installation, or claim of response-quality improvement accompanies this integration. CI for this new commit must be checked separately from the PR #8 run above.
