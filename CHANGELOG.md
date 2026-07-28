# Changelog

All notable changes to flow-lean are documented here.

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
