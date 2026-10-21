# Evaluations

Real, API-backed comparison of flow-lean against a plain baseline, generic
"be concise" instructions, and each of its three source skills (caveman,
ponytail, i-have-adhd). Cases live in `cases.jsonl`, the scoring contract
lives in `rubric.md`. The harness itself (`scripts/run_evals.py`) is forked
from [ayghri/i-have-adhd](https://github.com/ayghri/i-have-adhd) (MIT),
credited in the script header. Flow Lean now adds provenance-bound resumes,
per-attempt accounting and isolated working directories.

This is different from `../EVAL.md`, which is a manual, self-graded
regression battery you paste into a fresh session after any `SKILL.md` edit.
This harness answers a different question: does flow-lean measurably beat
its inspirations and plain terseness, not just hold its own contract.

Run every command below from the repository root (`flow-lean/`), not from
inside `evals/`, `--cases` and `--runner-config` default to the right paths
under `evals/` on their own.

## Routing scenarios

The positive and negative routing corpus is bundled at
[`skills/flow-lean/evals/scenarios.json`](../skills/flow-lean/evals/scenarios.json).
`evals/scenarios.json` is a compatibility symlink to that one source. Named
invocations and controls are kept in [`explicit-controls.json`](explicit-controls.json)
for separate native-host checks; they are not implicit-routing training data.
[`routing-probes.json`](routing-probes.json) retains additional public phrasing
and boundary probes outside calibration; report misses rather than hiding them. Routing
checks measure skill selection; they do not prove response quality or native
plugin invocation.

## Latest source-update checks

The [2026-09-27 check report](results/concision-2026-09-27.md) records isolated
Claude installation, focused Claude/Codex response checks, local routing,
and the failed or incomplete checks. The
[2026-09-26 report](results/concision-2026-09-26.md) remains historical evidence.
Neither is a paired comparison or a benchmark release-gate pass.

## CI without model calls

The repository's "Owner-requested workflows only" Actions policy permits
`workflow_dispatch` by the owner. Push and pull-request events are not allowed
and previously produced `startup_failure` before any job ran. The workflow now
declares only the permitted manual trigger; the policy remains unchanged.

After pushing, the owner can select the branch in Actions, or run:

```bash
gh workflow run plugin-load-check.yml --repo FlorianBruniaux/flow-lean --ref YOUR_BRANCH
```

Replace `YOUR_BRANCH` with the branch to verify. Check the resulting run's
`headSha` against the intended commit before using its result. Pushes and PRs
alone do not start CI. The workflow runs offline harness tests on Linux and
Windows, validates the corpus, and installs/lists the plugin in an isolated
Claude configuration. It makes no model-generation calls and supplies no model
API credentials. Plugin loading does not establish model adherence.

## Fetch comparators

Comparator `SKILL.md` files are not vendored in this repo, they are fetched
fresh before each run so the comparison always uses the current published
version, not a stale copy:

```bash
./scripts/fetch_comparators.sh
```

Writes `evals/comparators/caveman.md`, `ponytail.md`, and `i-have-adhd.md`
(gitignored).

## Validate and plan

```bash
python3 scripts/run_evals.py validate
python3 scripts/run_evals.py plan --trials 1 --include-comparator
```

`plan` prints the expected call count before any money is spent. At 1 trial,
30 cases, 3 conditions: 90 planned calls, before retries.

## Run

Use a new output file for each runner/model/corpus/trial selection and comparator.
A manifest binds each condition to its actual instructions. Incompatible resumes
fail before generation rather than silently skipping cases. Historical result
files without this provenance remain readable by `score`, but cannot be resumed.

`--budget-usd` now applies to **all attempts and conditions in one output file**,
including failed calls. It is no longer a separate allowance for each condition.
Keep the same total budget in commands that share an output. The CLI stops at
the reported limit; the provider-side cap remains necessary, especially when a
runner does not enforce the budget flag.

For v3, use the [group comparison](GROUP-COMPARISON.md) and
[executable rollback checks](ROLLBACK-CHECKS.md). The separately authorized
seven-arm pilot stopped at its budget reserve after 118/175 responses.
It validates neither group removal nor quality-preserving savings.
The [v3.1 installation record](V3.1-ROUTING-INSTALL.md) covers the integrated
global variant and its local routing checks, not a public plugin release or
a new model comparison.

For the four-arm experiment, use the [minimal-core v2 protocol](MINIMAL-COMPARISON.md)
and its explicit candidate path. V1 is preserved. A local v2 pilot completed on
2026-10-17 within its $5 ceiling; correctness and safety defects prevent adoption.
The protocol records its scope and local evidence location.

```bash
# Sanity run first: baseline + candidate only, no comparator, cheap
python3 scripts/run_evals.py run \
  --runner claude --condition baseline \
  --trials 1 --budget-usd 5 \
  --output evals/results/sanity.jsonl

python3 scripts/run_evals.py run \
  --runner claude --condition candidate \
  --condition-skill skills/flow-lean/SKILL.md \
  --trials 1 --budget-usd 5 \
  --output evals/results/sanity.jsonl

# Then one full baseline + candidate + comparator run per comparator
for comparator in caveman ponytail i-have-adhd; do
  out="evals/results/vs-${comparator}.jsonl"
  python3 scripts/run_evals.py run \
    --runner claude --condition baseline \
    --trials 1 --budget-usd 5 --output "$out"
  python3 scripts/run_evals.py run \
    --runner claude --condition candidate \
    --condition-skill skills/flow-lean/SKILL.md \
    --trials 1 --budget-usd 5 --output "$out"
  python3 scripts/run_evals.py run \
    --runner claude --condition comparator \
    --condition-skill "evals/comparators/${comparator}.md" \
    --trials 1 --budget-usd 5 --output "$out"
done
```

Style instructions are injected from the supplied file. All conditions receive
the same task and explicit text-only environment framing, including baseline.
The baseline has no extra style instructions. The revised corpus asks for written
decisions, proposed code, or reports from supplied facts, not actual repository
operations. It cannot establish safe tool execution.

`--runner-config` defaults to `evals/runners.example.json`, no need to copy
it anywhere, the requested model lives there. Verify availability before spending, and use a
separate config per model. `version_command` observes the installed CLI version
without generating a response; a changed version invalidates resume. A declared
model label is not proof of the model actually served: retain provider metadata.

The example runner disables skills, built-in tools and MCP servers and requests
empty setting sources. Each attempt runs in a fresh temporary directory outside
this repository. This tests injected style instructions, not native skill loading.
The common prompt declares the lack of tools, repository and network access;
scenario paths do not refer to that temporary directory. Keep this harness
text-only. A tool-enabled evaluation requires a separate protocol and context.

The Claude example replaces the coding-agent system prompt with a neutral one.
The runner receives closed stdin, so launcher input cannot be appended to the
case prompt. Files or directories left in the temporary working directory mark
the attempt failed: its raw receipt, reported cost and top-level entry names
are journaled before retry or resume. A failed attempt never completes the case.
Unknown cost blocks metered continuation as for other failures.

This directory check detects leftovers, not writes later removed or reads and
writes outside that directory. Claude Code may still inject environment metadata.
The proposed Codex CLI runner retains shell access and locally discovered skills,
so it is not included as an isolated text baseline. Native Claude/Codex reference
loading remains a separate follow-up in issue #4; no new live model run validates
native isolation here. Historical runs must retain their original runner settings.
Inherited environment and host-managed instructions are not fully captured by
these controls; check the host before any public benchmark claim.

### Evidence and interruption recovery

Keep these three files together:

- `<output>.manifest.json`: corpus snapshot, instruction snapshots, hashes of the
  runner configuration, rubric and harness, selected cases/trials, observed CLI
  version when available, Python/platform, and creation-time Git revision.
- `<output>.attempts.jsonl`: durable start/finish events, raw stdout/stderr, status,
  usage, reported cost and elapsed time for every attempt.
- `<output>`: successful nonempty responses with run/condition fingerprints and
  an attempt ID. A missing response write is recovered from a finished success.

Instructions are read once per invocation. Case content and injected prompts
are fingerprinted from the snapshots actually used. Retry count and spending
allowance can change on resume; changing the experimental inputs requires a new
output. Keep local runner scripts and external configuration fixed as well: the
harness hashes configuration, not every transitive dependency or environment value.

A missing, invalid or interrupted cost stays `null`/`UNKNOWN`. Metered runs stop
before further calls, including on resume. `--allow-unmetered` permits continuation
only when you have a separate provider-side spending cap; the displayed subtotal
is then explicitly not the total. Retries consume the remaining shared budget.
The retry count is per invocation, so manually resuming can retry a failed case
again, within the cumulative spending allowance.

`<output>.lock` prevents concurrent writers. A killed process may leave this lock:
verify that its PID is no longer running before removing that lock alone. Do not
delete unfinished attempt events or costs to make a resume pass. Malformed JSONL
or inconsistent response evidence is rejected; preserve it for investigation.

Logs and snapshots can contain task content, provider output and errors. Use the
ignored `evals/local/` directory for private trials and inspect/redact evidence
before publishing. Existing committed results remain unchanged.

## Judge and score

`run_evals.py` only generates responses, it does not judge them. Judging is
a separate, deliberately human (or a carefully isolated LLM-judge you run
yourself) step: read `evals/results/vs-<comparator>.jsonl`, blind the
`condition` field before judging (relabel rows `A`/`B`/`C`, don't look at
which is which while scoring), and write one JSON object per response with
the fields `rubric.md` defines:

```json
{"case_id":"factual-git-log","trial":1,"condition":"candidate","correctness":5,"decision_fidelity":5,"gate_fit":5,"concision":5,"safety":5,"blocker":false,"notes":"Correct command, no preamble."}
```

Then apply the release gate:

```bash
python3 scripts/run_evals.py score evals/results/scores-vs-caveman.jsonl
```

For `no-invented-fact` cases, run the separate fact-audit pass described in
`rubric.md` before scoring, its `false` verdicts are a hard blocker
regardless of the weighted score.

Do not compare conditions produced with different cases, models, trial
counts, or rubrics. Commit `evals/results/` snapshots so numbers are
reproducible without re-spending.

The committed v0.2.0 result files used the former 13-case suite. They remain
historical evidence only. Run all three conditions again before publishing a
current-version comparison against the 30-case suite.
The text-only context and revised cases/criteria also invalidate direct score
comparisons with the local v1 pilot, even though the case IDs and count remain
unchanged. Retain old manifests as evidence; regenerate all conditions for v2.
