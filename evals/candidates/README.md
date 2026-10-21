# Experimental minimal cores

V3 is preserved in `minimal-v3.md` (442 words). Its canonical blocks
are in `v3-groups.json`; the [group comparison](../GROUP-COMPARISON.md) removes
one of four groups at a time. It clarifies speaker/addressee roles, limits caveats
to supplied or decision-relevant unknowns, and adds executable rollback safeguards.
A separately authorized seven-arm pilot produced 118/175 responses, with
16 fully paired cases. It did not validate a smaller core. V1, v2 and the
published repository skill remain unchanged.

`minimal-v2.md` is a 336-word candidate prompt. It is not an installed skill or
a release. `minimal.md` preserves the original 114-word fixture. The full skill
remains unchanged. Word counts use whitespace splitting, not model tokenization.

V2 was prepared after reviewing the local `core-2026-10-16` development pilot:
25 cases, four conditions, one trial, `claude-sonnet-5`, same-agent qualitative
review. V1 was neither cheaper nor better on the observed safeguards. Full Flow
Lean handled several explicit constraints better but also failed cases. No
individual rule's causal contribution was isolated.

| V2 instruction group | Why retain or clarify it | Remaining uncertainty |
| --- | --- | --- |
| Shortest complete answer; exact deliverables | The full skill shortened replies but returned prose instead of the requested runnable rollback. | The useful length depends on the task; no validated word quota. |
| Actors, conditions and evidence scope | Some variants invented motives, implementation details or approval state. | V2's local pilot still confused approval actors and added unsupported caveats. |
| Honest tool fallback and external-detail uncertainty | Tool-like text appeared with tools disabled; v1 invented a file-search result. All conditions overstated `useEffect` behavior. | Both prompt and environment framing changed; a future improvement cannot be attributed to this rule alone. |
| Verification depth and production scope | Same-agent checks must not become independent review, nor integration tests production proof. | Successful refusal on one case does not establish real-world review safety. |
| No time range without measured throughput | Only the full skill avoided unsupported durations in the pilot. | One example supports a hypothesis, not a universal result. |
| Existing authorization and bounded destructive actions | The completion example triggered an unnecessary refusal; the force-push case failed to elicit adequate inspection prerequisites. | Reframed cases test written decisions, not tool execution. |
| Complete rollback conditions | Generic and v1 copied concurrent data aside and then replaced it; the baseline lock did not exclude unrelated writers. | Static inspection is insufficient to validate an executable rollback. |

V2 deliberately spends more words on concurrency: preimages and written
postimages, external records, coordination across all writers, a preflight check
of every target, stop on conflicts, restore/remove according to original
existence, and final verification. A backup alone cannot justify replacing or
moving someone else's work. This block is a candidate for grouped ablation only
after the complete version works; do not weaken individual safety prerequisites
to chase a word count.

The prompt does not repeat product-specific footer defaults, reference-handle
syntax, diagram examples, mode commands or a lexical blacklist. Explicit user
format instructions still apply. Grade specialized convention cases separately
from correctness, fidelity and safety; their failures remain visible.

Use `--condition minimal --condition-skill evals/candidates/minimal-v2.md` with
the [revised comparison protocol](../MINIMAL-COMPARISON.md). Omitting
`--condition-skill` still selects v1. Do not reuse v1 output files or scores.

Offline tests verify prompt delivery, provenance and harness behavior with a
local fake provider. They do not validate these instructions' effect on a model.
A separately authorized local v2 pilot completed on 2026-10-17: 25 cases, four
conditions, one trial, 100 successful responses. Reported CLI list-price equivalent
was $3.912252 total. V2 cost 30.53% less than the full skill but 13.11% more than
baseline; these observations do not establish quality-preserving compression.
Same-agent review found actor-fidelity and factual errors. Disposable execution
probes found a leaked lock in v2 and other safety defects in every comparator.
No candidate is validated for adoption. Native Claude/Codex behavior and
statistical quality equivalence remain **UNKNOWN**. Evidence is local at
`evals/local/core-v2-2026-10-17/REPORT.md`, ignored by Git and not publicly available.

## V3.1 offline repair

[V3.1 repair and global preparation](../V3.1-PREPARATION.md) describes the
new candidate. `minimal-v3.1.md` is rendered from `v3.1-groups.json`.
The frozen v3 files and paid-run evidence remain unchanged. V3.1 has no
model comparison or measured savings claim.

The [final routing and installation package](../V3.1-ROUTING-INSTALL.md) adds
the dual-host BM25 correction and supersedes the initial v3.1 approval.
