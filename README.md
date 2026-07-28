<div align="center">

# flow-lean

Lean output mode for Claude Code: minimal solution, action-first structure, zero-fat density.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

<a href="#examples">Examples</a> ·
<a href="#install">Install</a> ·
<a href="#what-it-does">What it does</a> ·
<a href="#why">Why</a> ·
<a href="#eval">Eval</a>

</div>

## Examples

**By task type.** Compression scales with what's being asked, not blindly with
the level:

<table>
<tr>
<th>Situation</th>
<th>Without flow-lean</th>
<th>With flow-lean</th>
</tr>
<tr>
<td valign="top">Implement a feature</td>
<td valign="top">

Great question! There are a few different ways
you could approach this. Let me walk you through
the options before we decide together.

</td>
<td valign="top">

Run `pnpm add zod`, then wrap the input at
`src/schema.ts:12`. Proof: `pnpm test schema`.
One risk: the existing `parse()` throws on null,
handle it or the API 500s. Rest is mechanical.

</td>
</tr>
<tr>
<td valign="top">Tradeoff: SSR or SSG for a high-traffic blog</td>
<td valign="top">

Both have tradeoffs worth considering. SSR gives
fresher content on every request but costs more
server load. SSG is faster and cheaper to host but
content can go stale between builds. It depends on
your specific needs and traffic patterns.

</td>
<td valign="top">

Use SSR, not SSG. A high-traffic blog changes often
enough that stale SSG pages cost more in lost
engagement than the extra server load costs in
infrastructure. Cache the SSR output at the edge to
close most of the performance gap.

</td>
</tr>
<tr>
<td valign="top">Factual lookup, <code>/flow-lean ultra</code></td>
<td valign="top">

To find the last commit that changed a file, you
can use the git log command with a path filter,
which will show you the commit history for that
specific file.

</td>
<td valign="top">

`git log -1 --format=%H -- src/auth.ts`

</td>
</tr>
</table>

**By level.** The task-type gate above always wins, but at the same task type
the level still sets the default density. Same prompt ("what's the difference
between debounce and throttle") at each level:

| Level | Response |
|-------|----------|
| `lite` | Debounce waits until input stops for a set delay, then fires once, useful for a search box you don't want to query on every keystroke. Throttle fires at a fixed interval no matter how often the event repeats, useful for a scroll handler you want running steadily. |
| `full` | Debounce delays until input stops for N ms, then fires once. Throttle fires at a fixed interval regardless of event frequency. Debounce for a search box, wait for typing to stop. Throttle for a scroll handler, run steadily. |
| `ultra` | Not shown here. Explanation tasks cap at `full`/`lite` under the task-type gate, `ultra` is reserved for factual and debug lookups, see the git example above. |

## Install

```
claude plugin marketplace add FlorianBruniaux/flow-lean
claude plugin install flow-lean@flow-lean
```

## What it does

Three fused disciplines, one rule underneath: every token earns its place.

- **ponytail**: minimal solution, ladder from "skip it" down to "the minimum code that works"
- **adhd**: action-first, command or verdict in line one, numbered steps
- **caveman**: zero-fat density, cut every sentence that carries no decision

Compression scales with task type (factual and debug compress hard, tradeoffs
barely move) and intensity level (`lite` / `full` / `ultra`, switch with
`/flow-lean lite|full|ultra`). Suspends automatically on destructive actions,
security, and high-stakes tradeoffs.

Full mechanics: [`skills/flow-lean/SKILL.md`](skills/flow-lean/SKILL.md).

## Why

Three existing skills already push toward less verbose output, each covering a
third of the problem. Caveman, the most widely used of the three, compresses
prose (zero preamble, symbols over words, code and commands kept byte-exact)
but does not touch what gets built or how it is structured. Ponytail decides
what to code (YAGNI, stdlib before a library, one line before ten) but not the
form. i-have-adhd decides the form (action-first, numbered steps, proof by
command) but not the density. Stacked together they step on each other, and two
of adhd's own rules are actively harmful: estimating in minutes, and stripping
tangents in a way that can hide a real risk.

flow-lean fuses the three under one rule instead of three overlapping ones:

```
ponytail            adhd             caveman
(what to code)    (the form)      (the density)
      \                |                /
       \_______________|_______________/
                        |
                        v
               +------------------+
               |     flow-lean    |   one rule:
               +------------------+   every token earns its place
                        |
          ______________|______________
         /               |              \
        v                v                v
   never ultra      compression      size in effort,
   a decision        OFF on risk       not minutes
```

Where it goes further than any of the source skills:

- It never compresses a decision. A tradeoff or recommendation gets its verdict
  in sentence one, then stays close to full prose. Compress a tradeoff too hard
  and only the reasoning for the rejected option survives, so the reader infers
  the opposite of the recommendation. Anthropic tested a uniform 100-word cap on
  its own models, measured a 3% accuracy drop, and reverted it after a week.
  "Just be terse" is a measured mistake, not a style choice.
- It drops compression entirely on destructive actions, security and secrets,
  or a tradeoff with real money on the line, full clear prose there instead.
- It sizes work in effort or steps, never in minutes, a confident "15 min" from
  a model is a guess dressed up as a fact.

Measured net compression on mixed work lands around 20-30%, not the 50-75%
Caveman's own README cites, those bigger figures hold for verbose prose or
explanation, not general use.

## Eval

[`EVAL.md`](EVAL.md) is a 13-case regression battery, form (density, gate,
auto-suspend) and fact (no invented specifics) graded apart. Run it in a fresh
session after any change to `SKILL.md` to catch regressions before they ship.

[`evals/`](evals/) is a separate, real API-backed harness (forked from
[i-have-adhd](https://github.com/ayghri/i-have-adhd)'s own eval script) that
blind-judges flow-lean against a plain baseline and against each of the three
source skills, same 13 cases, weighted rubric in
[`evals/rubric.md`](evals/rubric.md):

| vs | baseline | flow-lean | comparator |
|---|---:|---:|---:|
| plain baseline | 4.32 | **4.52** | n/a |
| caveman | 4.24 | **4.62** | 3.98 |
| ponytail | 4.28 | **4.80** | 4.57 |
| i-have-adhd | 4.12 | **4.85** | 4.21 |

flow-lean wins the weighted score in every run, driven mostly by
decision-fidelity and concision, the two dimensions none of the three source
skills individually target. This is a single trial per case (n=1, Claude
Sonnet 5), not a proof: re-running the same comparison during development
moved the weighted score by 0.2-0.3 points on an unchanged skill, and one run
surfaced a real regression (compression dropping a safety detail) that got
fixed and re-verified, see commit history in `evals/results/` for the full,
uncherry-picked trail including the runs that failed. Raw responses and judged
scores: [`evals/results/`](evals/results/).

## Credits

flow-lean fuses three disciplines from three existing Claude Code skills:

- [caveman](https://github.com/JuliusBrussee/caveman): zero-fat density
- [ponytail](https://github.com/DietrichGebert/ponytail): minimal solution ladder
- [i-have-adhd](https://github.com/ayghri/i-have-adhd): action-first structure

## License

MIT, see [LICENSE](LICENSE).
