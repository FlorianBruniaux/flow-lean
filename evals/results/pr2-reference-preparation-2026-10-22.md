# PR #2 reference rollback and next qualification preparation

**PREPARED_NOT_RUN. Zero provider calls and no authorized model budget.** The five failure classes have corresponding source corrections and a new qualification contract. This does not demonstrate that newly generated answers comply; PR #2 stays open. The [previous failed campaign](pr2-requalification-2026-10-22.md) and its evidence remain unchanged.

| Failure | Correction | Offline evidence or remaining limit |
| --- | --- | --- |
| Broken generated rollback | Ship a bounded Python reference and load it only for matching rollback tasks | All 18 scenarios pass; additional tests cover metadata, lock ownership, argument errors and selected I/O failures |
| Uncoordinated history purge | Separate urgent credential rotation from a conditional history rewrite after inspection and coordination | Stronger frozen criteria; model adherence untested |
| Unqualified `useEffect([])` claim | Answer the requested signature/argument without an unsolicited execution claim; retain development Strict Mode if discussing execution | Explicit source rule; model adherence untested |
| Tests treated as production resolution | Require the relevant observed production behavior, tied to version and bounded scope | Integration/load tests and deployed SHA explicitly insufficient; model adherence untested |
| Inverted force-push range | Remote-only is `main..origin/main`; preserve inspected remote tip before a separately justified rewrite | Disposable divergent-history test verifies both directions and the remote recovery ref |

The Git and React rules follow their primary references: [Git revision ranges](https://git-scm.com/docs/gitrevisions#_dotted_range_notations), [React effect caveats](https://react.dev/reference/react/useEffect#caveats). Secret remediation follows [GitHub's history-cleanup guidance](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository). These explicit examples target known development failures; they are not unseen evaluation evidence.

## Reference program and limits

The canonical source is [skills/flow-lean/scripts/rollback_reference.py](../../skills/flow-lean/scripts/rollback_reference.py), with its [scope and usage contract](../../skills/flow-lean/references/rollback.md). It is Python 3.9+ and POSIX only. The runtime here was Python 3.9.6 on macOS. Windows is explicitly refused before filesystem access; the CI matrix also exercises Python 3.9 and 3.12 on Linux, with the cross-platform harness on Windows.

The program validates the backup and both installed postimages before any target mutation. It uses an exclusive temporary, restores original content/mode/UID/GID/mtime, removes only the known created file, retains a populated cache directory, writes staged evidence outside the root, and reports completion only after verification and owned-lock cleanup. It never recursively clears the cache or removes an existing lock. Changed lock-owner contents or unexpected contents are retained for reconciliation.

The [18-scenario report](pr2-reference-preparation-2026-10-22-rollback.json) includes actual exit codes, before/after snapshots and unchanged source hashes. Supplemental tests inject failure before replacement and after restoration but before cache deletion. A later failure can leave a partially restored tree: the program reports failure, retains the backup and evidence, cleans owned resources where safe, and does not retry automatically. Tests also verify nonempty nested-directory/link preservation, malformed arguments, physical-path restrictions and the requirement to acknowledge externally stopped writers.

No private lock can prove exclusion of uncooperative writers. `--writers-stopped` is an explicit caller prerequisite, not an enforcement mechanism. This is not a crash-recovery system or atomic multi-file transaction. ACLs, extended attributes, birth time, access time, hardlink identity, every I/O fault and Windows rollback are outside the supported scope. Missing or original-looking targets are refused; receipt-based idempotent replay is intentionally not implemented.

## Routing and dual-host resource discovery

Before this change and with the revised skill, the current complete catalog missed one of 22 probes on both hosts: a French request for shorter prose without a table or recap. The previous-skill control reproduces that miss, so it is not attributed to the new rollback prose. One non-verbatim positive example repairs that boundary. The [before/control/after evidence](pr2-reference-preparation-2026-10-22-routing.json) is preserved.

Both Claude Code and Codex now pass 22/22 probes, and Flow Lean is eligible with the global gate passing. Global F1 changes from 0.7282 to 0.7213, above the configured 0.70 gate; this is not a claim that overall catalog quality improved. The repaired skill's cross-skill calibration still has one false positive and one false negative. The reported probe pass is a development regression result, not perfect routing or a holdout score.

The check copies the canonical skill into disposable `.agents/skills/flow-lean` and projects `.claude/skills/flow-lean` to the same bytes. It now verifies the bundled reference code and documentation as well as `SKILL.md` and the corpus. Both catalogs and isolated indexes are rebuilt. No live global instructions, skills, hooks or indexes were modified; native model loading is not established by routing.

## Frozen next experiment

The [protocol](../PR2-REFERENCE-QUALIFICATION.md) prepares 34 cases, two full-skill conditions and one trial: 68 planned responses, eleven focus cases first and alternating first-arm position. The [plan manifest](pr2-reference-preparation-2026-10-22-plan.json) records exact source/matrix hashes and zero authorized budget. The local frozen plan is `evals/local/pr2-reference-20261022`; it can be reproduced from the committed source with the documented planner command and a new output directory.

The rollback task alone now contains the identical reference source and contract in both arms. This avoids asking a text-only model to read inaccessible files and provides equal resource access. The other 33 task prompts are preserved, and no original criterion is removed. Report the assisted rollback separately from both the previous unassisted case and the unchanged 33-case subset. This tests reference use, not independent algorithm synthesis; it does not identify the effect of an individual skill rule.

The full-corpus gate remains zero blockers, all executable requirements passed, correctness/safety within 0.1 of the comparator or better, and a strictly higher weighted score. Separate factual verification and declared-runtime tests remain mandatory. A successful reference test cannot stand in for testing the actual unchanged script returned by a model. A new authorization is required before generation or paid grading.

Local validation: 74 offline unit tests pass; the corpus and all local skill links validate; both routing probes pass. This is an implementing-assistant check, not independent review. CI state is reported on the PR against the exact pushed SHA.
