# Changelog

All notable changes to flow-lean are documented here.

## [0.3.0] - 2026-09-07

### Added

- Adaptive recap selection with `recap=auto|on|off`; the recap becomes the
  primary answer shape instead of repeating a prose answer.
- Stable handles (`F1`, `D1`, `R1`, and related prefixes) for multi-item
  decisions that need precise follow-up.
- Optional `Skills used: ...` footer with session-level `on`, `off`, and
  `status` controls.
- Review-depth boundary inspired by Liza's adversarial-pairing protocol:
  compression changes the reported output, not verification depth; independent
  review is recommended only when it could change the decision and is never
  started without user request or approval.
- Codex installation instructions and BM25 routing scenarios alongside the
  existing Claude Code plugin distribution.
- Four regression cases for recap selection, footer control, review depth, and
  false claims of independent review.

### Changed

- Default level is now named `concise`; `full` remains a compatibility alias.
- `detailed` replaces `lite` as the primary name; `lite` remains an alias.
- Action-first and density rules now preserve required context, evidence, and
  decision-changing risk while removing optional history and duplicate recaps.
- Historical benchmark scores are explicitly scoped to the v0.2.0 13-case
  suite. The current suite has 17 cases and requires a fresh run before new
  comparison claims.
- The evaluation rubric now checks recap/footer controls, preserved verification
  depth, and truthful reviewer provenance.

### Fixed

- Removed an unsupported README claim about an Anthropic 100-word experiment.
- Corrected the README's SSR/SSG blog example and scoped compression figures to
  the historical v0.2.0 runs.
- Clarified that a same-agent self-check is not an independent or adversarial
  review.

## [0.2.0] - 2026-07-28

### Added

- Real, API-backed eval harness (`evals/`), forked from
  [i-have-adhd](https://github.com/ayghri/i-have-adhd)'s own eval script.
  Blind A/B/C judges flow-lean against a plain baseline and against caveman,
  ponytail, and i-have-adhd on 13 shared cases. Run it with
  `evals/README.md`, raw responses and judged scores are in
  `evals/results/`, including the runs that failed, not just the ones that
  looked good.
- `SKILL.md`: a rule to point to existing depth (a file, an earlier message,
  existing docs) in one line instead of re-deriving or compressing it into
  the response. One idea kept out of a wider ecosystem scan of similar
  skills, the rest didn't fit flow-lean's scope.
- README: real, verified weighted scores from the eval harness, replacing
  the abstract pointer to the manual battery only.

### Fixed

- `SKILL.md` auto-suspend now also covers *offering* to run a destructive or
  irreversible action, not just running one. The eval caught candidate
  offering to execute a live Supabase migration on a guessed target where
  the plain baseline correctly declined and asked first.
- `SKILL.md` honesty rule: an unverifiable external detail (a library's
  exact type signature, an argument) must be hedged or skipped, never
  compressed into a confident-looking guess. The first fix attempt (forcing
  byte-exact precision on type signatures) made the failure worse on
  re-test, it pushed the model toward a more specific, more wrong answer.
  Reverted and replaced with an explicit hedge-under-uncertainty rule.

## [0.1.0] - 2026-07-27

### Added

- Initial public release: `SKILL.md`, plugin manifest, README, `EVAL.md`
  (manual regression battery), MIT license.
