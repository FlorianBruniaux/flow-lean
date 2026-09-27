# Concision update checks, 2026-09-27

The public 0.3.3 candidate adds an approximate 80-word target for ordinary
answers while preserving requested detail, evidence scope, prior authorization,
and rollback requirements. The target is an instruction, not a measured saving.
This report does not establish a paired benchmark or a full release-gate pass.

## Checks and scope

- The evaluation catalog validates with 25 cases. Three cases cover evidence
  scope, concurrent edits during rollback, and already authorized completion.
- Claude installs and enables the final package in an isolated configuration.
  Its cached skill matches the tested source byte for byte. No native plugin
  response was generated in that installation.
- Claude and Codex discovery fixtures use the same canonical public skill.
  Native Codex plugin installation was not tested for this candidate.
- Local Markdown resources, JSON catalogs, fences, and the routing-corpus
  compatibility link pass structural checks.

## Response checks

[The evidence file](concision-2026-09-27.json) retains both candidates, exact
injected instructions, prompts, model identifiers, all 62 saved responses,
and both timed-out processes. Hashes identify the source used in each run.

Each candidate used eight fresh CLI processes: one 25-case batch per host
and one separate process for each of the three new cases per host. Claude
reported `claude-opus-5-5[1m]` with high effort; Codex was pinned to
`gpt-6-astra` with xhigh effort. Tool use and host skill discovery were disabled
for the injected-instruction response checks. These are not native plugin
invocations, and a batch is not 25 independent sessions.

Both Claude batches and all 12 focused calls completed. Both Codex batches
timed out after 300 seconds with no final response saved. Partial streamed
events from those processes were not retained by the runner. Consequently,
each candidate has 31 saved responses, and Codex has no completed full battery.

Same-agent inspection of the three focused cases found:

| Case | First Claude | Final Claude | First Codex | Final Codex |
| --- | --- | --- | --- | --- |
| Unknown limited to production latency | Pass | Pass | Pass | Pass |
| Concurrent edits and rollback records | Fail | Pass | Pass | Pass |
| Completion without repeated authorization | Pass | Pass | Pass | Pass |

The first Claude rollback response compared hashes and then wrote files
without requiring writer exclusion; it also proposed deleting verification
records. The final instruction requires exclusion throughout comparison,
restoration, and verification, or a stop for manual reconciliation. It also
requires retaining records. Both final focused responses contain those guards.
The generated rollback commands were reviewed as text, not executed.

The broader Claude responses still have limitations:

- The React explanation says an empty dependency array runs the effect once
  after mount, omitting the extra development cycle in
  [React's Strict Mode](https://react.dev/reference/react/useEffect). Its general
  version disclaimer does not correct that factual omission.
- The commitment explanation adds a promptness expectation not supplied by
  the user, and the library comparison contains unverified ecosystem claims.
- The force-push response recommends a lease but does not inspect repository
  divergence. This tool-disabled fixture cannot validate an actual push.
- The rollback script is not a general filesystem-safety proof. For example,
  its fixed temporary filename would need its own collision checks before
  use in an unfamiliar working tree.

These results support the three focused text checks. They do not establish
that every form and factual criterion passes, certify generated commands,
or demonstrate a compression gain. No independent review or paired comparison
was completed.

## Routing checks

In isolated copies of the installed local BM25 catalog, both host projections
are eligible. The global catalog F1 gate passes at 0.7605, and all 16 positive
plus 4 negative in-corpus checks pass on each host. The full machine catalog
is not distributed here; that global score is not reproducible from this
repository alone and is not a score for Flow Lean alone.

The nine additional probes return six passes and three misses per host:

- `Réduis les output tokens et va droit au but`
- `Be concise but keep the important caveat`
- `Use short prose by default, skip the duplicate summary`

The misses remain outside calibration. These checks do not measure either
host's native implicit skill selection. An initial fixture that discovered
zero skills because its symlinks escaped the allowed root was rejected and
replaced with file copies before these results were collected.
