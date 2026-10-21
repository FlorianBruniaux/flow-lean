# V3 group comparison

Status: **PARTIAL_RUN_BUDGET_STOP** on 2026-10-17 after separate user
authorization. The seven-arm pilot produced 118/175 responses for $4.527056
in CLI list-price equivalent under Max, below the $5 allowance. Sixteen cases
have all seven responses; the six responses from the next case are excluded
from paired comparisons. No paid judge ran. The report and evidence at
`evals/local/group-v3-run-2026-10-17/REPORT.md` are private, Git-ignored records,
not available in a clone or published benchmark results. No group removal is
validated by this single-trial pilot.
V3 remains a 442-word experimental prompt, not an installed skill or validated
replacement. V2 remains unchanged. This document does not authorize further calls.

`candidates/v3-groups.json` is the source for the candidate. Its ordered blocks
compose `candidates/minimal-v3.md`. `scripts/prepare_group_comparison.py --check`
requires byte-for-byte agreement, verifies the focus cases and builds the matrix
without launching any process or provider.

## Four independently removed groups

| Group | What changes from v2 | Primary cases |
| --- | --- | --- |
| `fidelity` | Resolve speaker and addressee inside quotations; retain approval roles and conditional commitments. Do not infer missing CI, pending review or readiness from silence. Scope unknowns exactly. | `speaker-commitment`, `no-automatic-recap`, `unknown-scope`, `short-status`, `recap-auto-decisions`, `authorized-completion` |
| `evidence` | Preserve exceptions, qualify or omit unverifiable external details, distinguish tested scope from production and own checks from independent review. | `no-invented-fact-useeffect`, `format-validation-compare`, `language-btree`, `review-depth-auth-migration`, `requested-detail`, `scope-nullable-email` |
| `duration` | Retain the prohibition on time ranges without measured throughput. | `estimate-trpc-migration` |
| `rollback` | Add backup validation, exclusive temporary-file creation, owned-lock cleanup on success and failure, and preservation of earlier records to preflight and conflict rules. | `rollback-concurrent-edits`, `destructive-force-push`, `secret-hardcoded-key` |

The fixed base carries concise complete delivery, literal preservation,
authorization and decision-changing risks. Each ablation removes one entire
group and leaves every other byte unchanged. The seven arms are `baseline`,
`generic`, `v3`, `v3_without_fidelity`, `v3_without_evidence`,
`v3_without_duration`, and `v3_without_rollback`.

All seven arms cover all 25 existing cases, not just the group's focus cases:
**175 planned responses per trial**. This catches effects outside a group's main
targets. Focus labels are preregistered analysis slices, not separate denominators
for an overall quality score. Removing a block estimates its marginal contribution
in this particular combination; it does not isolate each sentence or interactions
between groups. General base instructions and host instructions may overlap with
the removed block. These ablations are text-only diagnostic controls, never
instructions to weaken a live agent's safety rules.

## Freeze an offline plan

```bash
python3 scripts/prepare_group_comparison.py --check
python3 scripts/prepare_group_comparison.py \
  --output evals/local/group-v3-plan-2026-10-17 --trials 1 --seed 20261017
```

Use a fresh output directory. The output contains instruction files, full prompts
and their hashes, case/trial/arm rows, source snapshots and a manifest. Cases and
arms within each case are shuffled deterministically. Every arm receives the
same text-only context and task. Prior campaigns and their scores are preserved.
No API key, provider CLI or pricing lookup is needed to prepare the plan.

The existing runner and scorer accept all seven named arms. V3 arms require an
explicit `--condition-skill` pointing to the corresponding frozen instruction
file; omitting it fails, rather than silently selecting v1. Each arm has its own
identity, so instruction fingerprints cannot be confused in a shared ledger.
The old `minimal` default and `--core-comparison` still refer to the earlier
protocol and do not select v3.

The matrix is **not an executable campaign scheduler**. `run_evals.py` runs one
arm per invocation. Its `--next-case ID` option selects one case without changing
the full corpus identity, so a launcher can follow the frozen interleaving with
one shared spending ledger. Running seven whole-arm commands does not implement
that order. The pilot used this option and checked every prompt and source hash.
Before another paid run, select model and CLI version and obtain a total
allowance covering every attempt. Do not multiply an allowance by seven or infer
a cost forecast from prompt length. The local pilot launcher preserves its
original $5 ceiling and stops with a $0.50 pre-call reserve.

## Judge before choosing a smaller core

Use the existing rubric with shuffled labels, report masking limits, and record
the judge's identity. Same-agent review is not independent. Compare each removed
group with full v3 on identical case/trial pairs, then inspect its predefined
focus slice. Report every correctness, fidelity and safety blocker, not only
averages. Footer and diagram conventions remain separate dimensions.

For fidelity, record who acts, who receives, who approves, the trigger, and the
commitment's modality before reading the answer. Fail a role reversal or invented
current approval/readiness state. In a supplied-facts status, fail added CI,
review or deployment caveats unless the task or decision requires them. Preserve
real supplied uncertainty; omitting a material limit is also a failure. These are
semantic review criteria, not keyword matches or proof from a prompt linter.

For rollback, review the generated code and adapt its exact interface to the
[executable checks](ROLLBACK-CHECKS.md). Keep runtime receipts separate from text
judgments. A failed behavioral requirement blocks adoption even if the prose
lists the correct safeguards. An unsupported platform or unexecuted property is
UNKNOWN, not PASS. Factual assertions require their separate fact audit.

A deletion is eligible only if it introduces no correctness, fidelity or safety
regression, preserves the required deliverables and demonstrably reduces the
measured total cost. Shorter text alone is insufficient. One trial supports
triage, not statistical non-inferiority. Record failures and repair burden rather
than presenting cost per raw output as cost per acceptable result.

The existing 25 cases and the new rollback probes are development data. Before
choosing a winner, reserve independently authored cases covering changed actors,
quotations, explicit versus absent limits, lock lifecycle and temporary files.
Freeze the selected candidate before evaluating those reserved cases on each
target host. No independent holdout has been prepared or run here.
