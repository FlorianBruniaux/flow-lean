# PR #2 actor-fidelity preparation, 2026-10-24

**PREPARED_NOT_RUN. Zero model calls and zero spending in this preparation.** The repository instruction now distinguishes who writes a quoted commitment, who receives it, who acts and who approves. The last [completed qualification](pr2-contract-qualification-2026-10-24.md) still has one candidate blocker; this source correction does not establish that a model will follow it. PR #2 remains unqualified.

## Correction and regression coverage

The observed answer assigned approval to the committing author while explaining a draft whose recipient must approve. The new rule resolves pronouns in the quote and in the assistant's answer separately. It preserves ability, permission, commitment, negation and ambiguity, without inventing approval or a new obligation. It replaces the earlier generic actor reminder.

The [frozen plan](pr2-actor-preparation-2026-10-24-plan/manifest.json) contains the same 34 task prompts and 6 added actor regressions: reversed roles, a French third-party approver, an explicitly addressed assistant, a separate delivery recipient, permission without a promise, and an ambiguous approver. All previous criteria remain; only `speaker-commitment` receives additional criteria. Seven reviewer-only role maps include accepted and rejected examples. Only the original failure is a recorded model answer; the other examples are authored test fixtures. They never enter generation prompts.

The [protocol](../PR2-ACTOR-QUALIFICATION.md) prepares 40 cases, 2 conditions and 1 trial: 80 responses, with 20 focus cases first and balanced first-arm order. Both arms receive identical tasks and the unchanged rollback resource. The full 40 and original 34 must pass separately; all 40 require zero candidate blockers. Added actor cases cannot dilute a core failure. Model and runtime remain unselected, with no execution budget authorized.

## Offline evidence

- [85 repository tests pass](pr2-actor-preparation-2026-10-24-tests.txt), including 5 actor-preparation methods. They exercise the real planner, reject duplicate/shadowed/missing actor cases, preserve prior prompts and criteria, check reviewer-fixture provenance and prevent subprocess/network use during preparation. These are preparation tests, not semantic model-adherence tests.
- The new CLI extension first failed because the actor option did not exist; the [red test](pr2-actor-preparation-2026-10-24-red-test.txt) is retained. The implemented extension now freezes 40 cases and 80 paired inputs without exposing review answers.
- All 29 frozen file hashes match. The base and extended corpora validate; the skill's required frontmatter fields validate. The [check summary](pr2-actor-preparation-2026-10-24-checks.json) records this scope.
- [Dual-host routing](pr2-actor-preparation-2026-10-24-routing.json) passes eligibility and 22/22 probes for Claude Code and Codex in disposable projections. Global calibration F1 is 0.7167, above the 0.70 gate. Catalogs differ from earlier runs, so this is not a measured routing improvement. No global files are installed or changed.
- The previous campaign's [offline verification](pr2-actor-preparation-2026-10-24-prior-verification.json) reproduces its failed gate. Its [corruption checks](pr2-actor-preparation-2026-10-24-prior-corruption-checks.json) reproduce the summary and reject all 5 altered evidence variants. Earlier outputs, scores and source snapshots are unchanged.

The rollback implementation and contract remain unchanged. Existing executable repository tests still pass; no generated model script was rerun by the historical evidence verifier. CI is checked separately against the published commit, not inferred from this local suite.

No new quality score or token-saving claim follows from these checks. The development cases are not a holdout. The previous native runner's unexplained project reference remains an isolation uncertainty; this preparation neither changes the runner nor resolves that uncertainty. A later model run needs a fresh authorization and must report that limit unless native initialization evidence or a separately reviewed runner resolves it.
