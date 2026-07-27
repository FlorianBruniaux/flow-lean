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

Three layers, one rule underneath all of them: every token earns its place. A
token earns its place only if it carries an action, a step, a decision-changing
risk, or a proof.

- **Solution altitude (ponytail)**: before writing code, run a ladder from "does
  this need to exist" down to "the minimum code that works". Deliberate
  shortcuts get a `# ponytail: <ceiling>, <upgrade path>` marker. Non-trivial
  logic ships with one runnable check.
- **Form (adhd)**: first line is doable now, no preamble. Multi-step work is
  numbered. Tradeoffs lead with the verdict, then the why.
- **Density (caveman)**: zero preamble, zero recap, zero hedging, zero praise.
  Cut every sentence that carries no decision, keep every one that does.

## The rules

Compression is not applied uniformly. A gate keyed on task type overrides the
intensity level:

| Task | Safe compression |
|------|------------------|
| Factual, lookup, debug diagnosis | 40-60%, `ultra` OK |
| Explanation, teaching, walkthrough | 10-30% |
| Tradeoff, recommendation, design decision | 0-15%, verdict first |

Compression auto-suspends for destructive actions, security/auth/secrets, and
any tradeoff where a wrong read costs real money or time.

Three intensity levels:

| Level | Behavior |
|-------|----------|
| `lite` | Form + density, light connective prose |
| `full` (default) | All three layers, tight, complete sentences |
| `ultra` | Symbols, near-telegraphic, factual/debug only, never on decisions |

Switch with `/flow-lean lite|full|ultra`. Full rules live in
[`skills/flow-lean/SKILL.md`](skills/flow-lean/SKILL.md).

## Credits

flow-lean fuses three disciplines from three existing Claude Code skills:

- [caveman](https://github.com/JuliusBrussee/caveman): zero-fat density
- [ponytail](https://github.com/DietrichGebert/ponytail): minimal solution ladder
- [i-have-adhd](https://github.com/ayghri/i-have-adhd): action-first structure

## License

MIT, see [LICENSE](LICENSE).
