# Concision update checks, 2026-09-26

The public skill was synchronized with the general concision improvements.
It contains no personal voice profile and requires no separate `msg` skill.
These are source-update checks, not a new benchmark or a release-gate pass.

## Structural checks

- Evaluation catalog: 22 valid cases, 66 planned calls for a three-condition,
  one-trial comparison. The comparison itself was not run.
- Markdown links and fences, JSON catalogs, plugin entry points, and the
  bundled routing-corpus link resolve successfully.
- Both host discovery configurations resolve the same candidate `SKILL.md`.
  The installed global skills were not changed.

## Response smoke tests

Raw responses, exact injected prompt, source hashes, and routing probes are in
[`concision-2026-09-26.json`](concision-2026-09-26.json).

Two fresh CLI processes generated 22 responses each, with the whole skill
injected into the prompt and tool use disabled. Each process handled a batch;
these were not 44 separate sessions or native plugin invocations. Codex used
its CLI default without a model override; an effective model identifier was
not captured. Claude reported `claude-opus-5-5`. No comparison is made between
the models or against the historical scores.

A first Claude batch retained a local output style in its initialization
metadata. Its 22 responses are retained as excluded evidence. The replacement
used empty setting sources, the default output style, and a neutral system
prompt; initialization reported no tools or skills. Its outer JSON code fence
was removed for parsing, without editing response text.

Same-agent inspection found the intended short status replies, prose for the
simple choice, and preservation of requested detail. It also found limits:

- Claude adds optional detail to several short requests.
- Its commitment explanation preserves the actor and condition but adds an
  interpretation about quick turnaround that the supplied facts do not require.
- Its request-flow diagram sends an error inside a branch and then falls
  through to another response outside that branch.
- Its production-verification explanation includes a staging/production
  ambiguity even though its last sentence states the boundary correctly.
- Its React explanation says an empty dependency array runs the effect only
  after the initial mount, omitting the extra development cycle documented
  for [Strict Mode](https://react.dev/reference/react/useEffect). This is a
  factual limitation, not a passing fact-audit result.

This is not a claim that all 44 responses passed every form and factual check.
No independent human grading or paired benchmark release gate was completed.

## Routing checks

The established natural-language corpus was bundled with the skill. Named
controls remain separate from implicit routing calibration. On both local
host configurations, the skill was eligible, the global F1 gate passed
(0.7605), and the 16 positive plus 4 negative in-corpus checks passed.

The nine additional probes returned 6 passes and 3 misses on each host:

- `Réduis les output tokens et va droit au but`
- `Be concise but keep the important caveat`
- `Use short prose by default, skip the duplicate summary`

These are known limits of the tested local BM25 catalog. They are not a test
of either host's native implicit skill selection, and were not added back to
calibration to make this run appear perfect. Named invocation is covered by
the manual checks in `evals/explicit-controls.json`, not by this result.
