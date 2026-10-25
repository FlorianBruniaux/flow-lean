# PR #2 repair preparation, 2026-10-21

The source now guards contextual exceptions in absolute claims and keeps error
diagnostics in protected logs. Six focused development cases and a 34-case
paired comparison are prepared. **New model responses: NOT RUN.** No paid calls,
global installation, version bump or new quality/token-saving claim.

Candidate skill SHA-256:
`41a480403ec59b5066c80b45310def38b65bc66ad386457f3798fefb4e3ee5c7`.

## Offline checks

- 48 executable tests pass. The new paired-plan tests failed before adding the
  option and pass afterward. The scoring regression confirms that an explicit
  blocker prevents release despite a higher aggregate score.
- The 30 main cases, six focused cases and 34 unique combined cases validate.
  The two shared cases must remain identical; the test suite checks this.
- The documented preparation was executed: 68 planned responses, two full-skill
  arms, one trial, zero provider calls. The reference is main at
  `2c368a71ad9dea556986411baae26a0590348a6a`, not the no-instructions baseline.
- Skill structure/frontmatter validates. The skill has no local Markdown resource
  links to resolve. All pre-existing result files remain byte-identical to
  `e35ba7f4766059978fe7b0f81df1dec327478501`.

These checks exercise the harness and preparation, not model adherence. The
synthetic scoring fixture is not a new model judgment. Use the
[qualification protocol](../PR2-REGRESSIONS.md) before claiming the two historical
response blockers are resolved.

## Existing public routing limitation

In a disposable project, one frozen candidate copy at
`.agents/skills/flow-lean` and a Claude projection at `.claude/skills/flow-lean`
resolve to the same bytes. Both are isolated test paths, not installed project
or global configuration. The installed router discovers this candidate among
the full user catalogs (123 Claude skills, 164 Codex skills), with temporary
caches. The initial external symlink fixture was rejected by discovery and is
excluded from the candidate evidence.

The public corpus has 16 positives and four negatives. Both host builds pass the
global quality gate but exclude Flow Lean from BM25 eligibility. None of the
five public positive probes select it; the four negatives and `Vas-y` correctly
do not select it. Repeating calibration with the exact main skill and the same
corpus yields identical thresholds and exclusion. This is an existing public
corpus problem, not a regression introduced by the eight instruction lines.

The separate installed v3.1 variant is not this public candidate. Its earlier
routing qualification cannot be borrowed for this PR. No global indexes were
rebuilt, and no native Claude/Codex model sessions were started.

The [machine-readable record](pr2-repair-preparation-2026-10-21.json) preserves
both candidate and main control calibration results, including all probe misses.
Public BM25 eligibility still needs a separate correction; no implicit-routing
readiness or explicit-only exception is claimed here.
