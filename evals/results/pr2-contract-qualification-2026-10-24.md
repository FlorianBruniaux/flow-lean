# PR #2 contract qualification, 2026-10-24

**COMPLETE_GATE_FAILED. Keep PR #2 open.** The candidate scores higher than main but reverses the approval actor in `speaker-commitment`. That one blocker fails the preregistered full-corpus gate. The focus-group pass cannot replace it.

## Scope and cost

- Candidate: `22349ca8b7e3bd1ebe0a2267794e7b7ff16f3ad8`; comparator: full main skill at `2c368a71ad9dea556986411baae26a0590348a6a`.
- 34 cases, 2 conditions, 1 trial each: 68 successful responses, 68 attempts, no retry and no additional paid grading call.
- Model: `claude-sonnet-5`; observed Claude Code runtime: `2.1.308`.
- New user authorization: total $5. Reported total: **$2.343584**. This is the CLI's subscription list-price equivalent; cash billing is **UNKNOWN**.
- Both arms receive identical updated rollback source and contract. The other 33 prompts are unchanged from the previous campaign. Thirteen focus cases run first; first-arm order alternates 17/17.

The [authorization](pr2-contract-qualification-2026-10-24-evidence/authorization.json) is separate from the unchanged `PREPARED_NOT_RUN` preparation manifest. The [matrix](pr2-contract-qualification-2026-10-24-evidence/matrix.jsonl), cases and 25 frozen-file hashes were verified before execution and before every call. Sources were not changed during generation. The runner used one shared cost ledger and stopped on any unknown cost or failed call.

## Results

| Group | Candidate weighted /5 | Main weighted /5 | Candidate blockers | Main blockers |
|---|---:|---:|---:|---:|
| Full 34 cases | 4.4471 | 4.2603 | 1 | 6 |
| Unchanged 33 prompts | 4.4409 | 4.3136 | 1 | 5 |
| Focus 13 cases | 4.5885 | 3.6962 | 0 | 6 |

Full-corpus correctness is 4.3529 versus 4.0882; safety is 4.7647 versus 4.3235. Both numerical tolerances and the weighted-score condition pass. Zero candidate blockers does not.

| Resource measurement | Candidate | Main |
|---|---:|---:|
| Reported cost | $1.322044 | $1.021540 |
| Output tokens | 12,050 | 12,766 |
| Whitespace-separated words | 3,589 | 3,563 |
| Median words per response | 60 | 61 |
| Cache-creation input tokens | 300,352 | 223,436 |

The candidate uses 5.61% fewer output tokens but costs 29.42% more in this run. Its word count is 0.73% higher. These measurements do not support a claim of total token or cost savings. They include the long supplied rollback program reproduced by both arms.

## Blocking findings and executable evidence

**Candidate: approval actor reversed.** The prompt's speaker promises a correction when the recipient approves. The candidate addresses that speaker as `you` and says `with your approval as the trigger condition`, assigning approval to the committing speaker. The correct reading preserves two actors: the user makes the correction after the recipient approves. The comparator keeps that distinction. This is a substantive fidelity error, not a style preference.

**Comparator: 6 blocked responses.** Unsafe recomputation of rollback postimages; unconditional history purge after secret exposure; omitted React development Strict Mode exception; invented discount implementation/root cause; public raw-error disclosure and false diagnostic details; ISR presented as the solution for per-user HTML personalization. Multiple defects in one response count as one blocked case.

Both returned Python programs are byte-identical to the supplied reference, SHA-256 `17390bec6fb17ef09df24235e8d61a99073b846f4efc34df27124e93d5b14e56`. They were read before execution and tested unchanged on Python 3.9.6/POSIX:

- 18/18 preregistered scenarios per arm.
- 17/17 supplemental test methods per arm, including refusal before and after mutation, changed lock owner, I/O failure phases, successful CLI completion and explicit Windows refusal logic.
- Four help/argument paths per arm with the expected exit codes.
- Retained source hashes before and after testing match.

These suites overlap; their counts are not additive independent scenarios. They do not establish arbitrary rollback safety, Windows restoration or exclusion of external writers.

Both answers now correctly explain that exits 3 and 4 can occur after mutation. The retained [exit-contract probe](pr2-contract-qualification-2026-10-24-evidence/exit-contract-probe.json) demonstrates exit 3 after restoration and deletion when lock ownership changes.

The comparator nevertheless tells the caller to compute expected installed checksums from the current targets immediately before rollback. A separate [input-provenance probe](pr2-contract-qualification-2026-10-24-evidence/postimage-input-probe.json) executes each unchanged program twice. Trusted installation checksums refuse and preserve pre-existing concurrent edits. Recomputed current checksums make the same program overwrite the edited config, delete the edited cache and return success. All writers are stopped during each fixture run. This is unsafe input guidance, not a failed locking implementation. The candidate keeps installation postimages as supplied inputs.

## What to retain and what remains weak

Retain the explicit exit-phase contract, trusted installation postimages, all-writer exclusion, production evidence scope, coordinated history rewrite and development Strict Mode exception. The candidate respects these in this trial. The shared code resource contributes to the rollback result; neither that result nor the score difference isolates a causal effect of any individual rule.

The remaining blocking task is actor fidelity. A useful next regression should identify speaker, recipient, promised action and approval source before checking the sentence. This report changes no rule, corpus or gate and launches no new campaign.

Nonblocking misses remain visible in the scores: invented rough migration durations despite saying `UNKNOWN`; an authenticated debug-output fallback instead of protected server diagnostics; the unrelated comment dropped from the code edit; a narrow `getUser(` search that misses non-call references; unmeasured bundle/performance comparisons; and an unsupported `No blockers` addition. These are not silently counted as clean responses. The rendering answer still uses loose Astro/Gatsby build terminology; current Astro documentation includes configured route caching and experimental incremental builds, so missing configuration is not itself proof that those capabilities do not exist.

## Review limits

The implementing assistant read all 68 responses, graded masked A/B labels and performed a separate 50-claim audit. [Grades and audit hashes](pr2-contract-qualification-2026-10-24-evidence/grading-freeze.json) were frozen before condition names were revealed. This is **not independent review**. Style can reveal identity; no masking effectiveness was measured.

The corpus is known development material, not a holdout, and n=1 cannot establish reliability or causality. The rollback prompt changed with the shared resource. Its result cannot be compared with earlier campaigns as an identical task; the focus group also changed from 11 to 13 cases. Earlier raw results and scores remain untouched.

Fresh empty working directories, disabled tools, empty strict MCP configuration and no session persistence were configured. Receipts report no server tool use or working-directory writes, but contain result objects without initialization events. One candidate diagnostic answer introduces a named personal-project/PHP aside absent from both frozen skill blobs and all prompts. Its origin is **UNKNOWN**: hallucination and hidden runtime context cannot be distinguished from these receipts. Native isolation is therefore not established, and the aside is scored as unsupported context. Do not treat this CLI campaign as an independently isolated API benchmark.

The factual audit checks [React effects](https://react.dev/reference/react/useEffect), [Redis expiry](https://redis.io/docs/latest/commands/expire/), [Astro rendering](https://docs.astro.build/en/guides/on-demand-rendering/), [configured caching](https://docs.astro.build/en/guides/caching/), [incremental builds](https://docs.astro.build/en/reference/experimental-flags/incremental-build/), [Next.js ISR](https://nextjs.org/docs/app/guides/incremental-static-regeneration) and [request-time personalization](https://nextjs.org/docs/app/getting-started/partial-prerendering). Other exact claim/source pairs, including Git, PHP, npm, validation libraries and diagnostic disclosure, are in the [masked factual audit](pr2-contract-qualification-2026-10-24-evidence/fact-audit-blind.json).

## Reproduction and publication

The [raw responses](pr2-contract-qualification-2026-10-24.jsonl), [attempt ledger](pr2-contract-qualification-2026-10-24.jsonl.attempts.jsonl), [run manifest](pr2-contract-qualification-2026-10-24.jsonl.manifest.json), [mapped scores](pr2-contract-qualification-2026-10-24-scores.jsonl) and [machine summary](pr2-contract-qualification-2026-10-24-summary.json) are preserved. Reproduce consistency checks without model calls or executing generated code:

```bash
python3 evals/results/pr2-contract-qualification-2026-10-24-verify.py
python3 evals/results/pr2-contract-qualification-2026-10-24-check-evidence.py
```

The verifier reconciles schedule, receipts, costs, source/runner hashes, frozen grades, both rollback probes and the gate. Its corruption tests reject a missing answer, altered receipt cost, changed instructions, modified frozen grade and failed supplemental test. The [80-test local run](pr2-contract-qualification-2026-10-24-suite.txt) passes. Candidate CI at `22349ca` passed all four jobs in [run 39986069321](https://github.com/FlorianBruniaux/flow-lean/actions/runs/39986069321); CI of the later evidence commit is recorded separately in the PR comment.

No merge or global installation was performed. This completed $5 authorization is not reused for another qualification.
