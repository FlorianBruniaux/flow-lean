# PR #2 contract corrections prepared, 2026-10-23

**PREPARED_NOT_RUN: zero provider calls, zero authorized budget.** The three observed failure classes have source corrections and stronger verification. The [last model campaign](pr2-reference-qualification-2026-10-22.md) still fails; no new answer quality or token saving is claimed. No merge or global installation occurred.

## Changes and evidence

| Finding | Change | Offline evidence |
| --- | --- | --- |
| Refusal incorrectly explained as no mutation | CLI refusal message, source docstring, bundled contract and skill distinguish preflight from verification/cleanup after mutation | CLI tests assert exit 3 with unchanged targets before restoration, and exit 3 with restored/deleted targets after verification or lock-owner failure |
| Finite-TTL cache described as stale after expiry | General instruction requires checking the stated state transition; evaluation criteria distinguish pre-expiry staleness from expiry/miss | All prior criteria retained; 33 non-rollback prompts remain identical; no new model response generated |
| Astro on-demand conflated with regeneration/caching | General instruction disallows inferring adjacent functionality or deployment guarantees from a feature name; criteria require the distinction | Primary documentation checked, criteria and source frozen; no Astro deployment or model behavior tested |

The source remains `skills/flow-lean/SKILL.md`; branch-specific rollback guidance stays in its bundled reference. The script keeps exit-code compatibility. Its refusal error now directs callers to the retained evidence and warns that targets may already have changed. The core restoration algorithm and its writer-exclusion prerequisite are unchanged.

The new tests also compare exit 4 before and after restoration, assert no success receipt on failure, preserve foreign lock ownership and earlier evidence, and check CLI success only after verified state and lock release. Five additional behavior tests bring the rollback suite to **17 methods**, including the existing **18-scenario checker**. These counts overlap.

## Validation

The complete local suite passes **80 tests** on Python 3.9.6/POSIX. The first full run had one `OSError: Directory not empty: '.git'` during cleanup of the disposable Git-range fixture. A subsequent complete run passes with the final source. The cleanup cause is not established; both logs are retained rather than replacing the initial result. The focused rollback tests and standalone 18 scenarios pass.

The skill metadata validator passes, and all three local resource links resolve inside the skill. The canonical skill and resources match disposable Claude Code and Codex projections byte-for-byte. Both router builds mark Flow Lean eligible, pass the global quality gate and pass **22/22 probes**, with global F1 **0.7213438735**. Projection layout is `.agents/skills/flow-lean` with `.claude/skills/flow-lean` resolving to that same fixture source; the fixture and caches are removed after the check. No live shared skill, hook or router index was changed.

The [latest historical campaign verifier](pr2-reference-qualification-2026-10-22-verify.py) and its five evidence-corruption checks still pass. Previous generated outputs, scripts, scores, claims and receipts remain unchanged.

## Prepared campaign

The [protocol](../PR2-CONTRACT-QUALIFICATION.md) and [frozen plan](pr2-contract-preparation-2026-10-23-plan/manifest.json) retain 34 paired cases, one trial and 68 planned responses. The comparator is full main `2c368a71ad9dea556986411baae26a0590348a6a`. Thirteen focus cases now run first; first-arm position remains balanced 17/17.

Twenty-five frozen files cover sources, instructions, cases, matrix and their hashes. Both arms receive the same updated rollback code/contract. The 33 other prompts are unchanged. Earlier criteria remain in order; only the three observed blocker cases receive additions. The planner regression test enforces these relationships against the retained previous campaign.

The plan selects no runner or model and grants no spend. A new explicit authorization is required before any generation or paid grading. Keep the absolute zero-blocker gate, full numeric gate and executable checks; retain the 33-case and 13-case subset reports as diagnostics. The changed shared resource prevents treating the rollback result as the same prompt as the previous campaign. This remains a development corpus, not an independent holdout.

Guillaume proposed separating sync, rollback and routing and changing the merge criterion. Those proposals remain separate decisions; they do not retrospectively qualify a failed campaign. This change follows the active request to correct the three failures and prepare the next qualification.

## Retained artifacts

- [Check summary](pr2-contract-preparation-2026-10-23-checks.json), [initial full-suite log](pr2-contract-preparation-2026-10-23-initial-suite.txt), [passing full-suite log](pr2-contract-preparation-2026-10-23-suite.txt), [rollback methods](pr2-contract-preparation-2026-10-23-rollback-tests.txt).
- [Rollback scenario traces](pr2-contract-preparation-2026-10-23-rollback.json) and [Claude/Codex routing evidence](pr2-contract-preparation-2026-10-23-routing.json).
- [Frozen cases](pr2-contract-preparation-2026-10-23-plan/cases.jsonl) and [paired matrix](pr2-contract-preparation-2026-10-23-plan/matrix.jsonl).

Relevant primary references: [Redis expiration](https://redis.io/docs/latest/commands/expire/) and [Astro on-demand rendering](https://docs.astro.build/en/guides/on-demand-rendering/), checked on 2026-10-23. They support the evaluation distinctions, not a claim that the revised skill has already produced correct answers.
