<div align="center">

# flow-lean

Lean output mode for Claude Code: minimal solution, action-first structure, zero-fat density.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

## Before / After

<table>
<tr>
<th>Without flow-lean</th>
<th>With flow-lean</th>
</tr>
<tr>
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
</table>

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

flow-lean fuses the three under one rule instead of three overlapping ones.
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

## Credits

flow-lean fuses three disciplines from three existing Claude Code skills:

- [caveman](https://github.com/JuliusBrussee/caveman): zero-fat density
- [ponytail](https://github.com/DietrichGebert/ponytail): minimal solution ladder
- [i-have-adhd](https://github.com/ayghri/i-have-adhd): action-first structure

## License

MIT, see [LICENSE](LICENSE).
