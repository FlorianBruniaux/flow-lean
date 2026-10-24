# Public BM25 corpus repair, 2026-10-21

Flow Lean is eligible on Claude Code and Codex with the repaired public corpus.
All 22 development hook probes pass on each host. These are routing results,
not a new response-quality evaluation. No paid calls or global installation.

## Change

The former corpus mixed generic conversation summaries with Flow Lean intent,
while treating requests for detail as negative. It had few boundaries against
message writing, handoffs, configuration audits and other neighboring skills.

The new corpus adapts the already tracked v3.1 routing candidate, with three
additional positive formulations covering concise mode, output-token reduction
and short prose, and two negative boundaries for token accounting and file
compression. It contains 18 positives and 23 negatives. Named detail, recap and
footer controls remain valid intent; generic document or message tasks do not.

Only the routing corpus changes skill behavior in this patch. `SKILL.md` remains
byte-identical to `b0de50e792884531e699657046b897bd8cd1f32f`, SHA-256
`41a480403ec59b5066c80b45310def38b65bc66ad386457f3798fefb4e3ee5c7`.
The prepared 34-case response comparison therefore remains applicable.

## Executed checks

[`scripts/check_routing.cjs`](../../scripts/check_routing.cjs) builds indexes and
executes the actual installed `bm25-suggest.js` in fresh processes. A temporary
project contains one candidate copy under `.agents/skills/flow-lean` and a Claude
projection under `.claude/skills/flow-lean`; both resolve to the same bytes.
The checker rejects a build that discovers the installed skill instead of the
candidate. User catalogs remain present, with 123 Claude skills and 164 Codex
skills. Caches and projections are temporary; global files are not written.

| Check, per host | Original corpus control | Repaired corpus |
| --- | ---: | ---: |
| Flow Lean eligible | No | Yes |
| Global quality gate | Pass | Pass |
| Real hook probes | 12/22 | 22/22 |
| Flow Lean cross-skill F1 | 0.4211 | 0.9444 |

The control uses the exact skill and corpus from `b0de50e`. The same checker
exits 1 for that control and 0 for the repair. It also refuses to overwrite an
existing report; its original bytes were verified unchanged after that rejection.
The repository's 48 offline tests pass.

The 22 probes combine the nine public regression phrases, ten prior v3.1
development probes and three controls: `Vas-y`, `stop flow-lean` and the native
invocation (`/flow-lean concise` on Claude, `$flow-lean concise` on Codex).
The controls receive no duplicate Flow Lean BM25 hint. This does not test native
command execution or mode persistence. All five formerly missed public positive
phrases now select Flow Lean.

## Evidence limits

Calibration is not perfect: Flow Lean retains one false positive and one false
negative in the cross-skill evaluation (17 true positives, 23 true negatives).
The full catalog global F1 is 0.7410, above the installed router's 0.70 gate;
that aggregate includes errors from other skills. Neither number is a production
accuracy estimate. Eligibility depends on the router version and competing corpus.

The probes informed this repair and are explicitly labeled development
regressions. They are not an unseen or independently authored holdout. No model
responses were generated, no response-quality improvement or token savings were
measured, and the PR's response-quality gate remains pending.

The [machine-readable record](public-bm25-repair-2026-10-21.json) includes the
control summaries, all final probe results, source hashes, Node version and
router source hashes. The prior failure reports remain unchanged. Reproduce
with the command in the [evaluation README](../README.md#routing-scenarios),
using an existing compatible router and a new report path.
