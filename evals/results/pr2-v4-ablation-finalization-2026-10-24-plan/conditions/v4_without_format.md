---
name: flow-lean
description: "Use when the user explicitly asks for Flow Lean, lean or less verbose output, action-first responses, expansion of a compressed Flow Lean answer, or Flow Lean recap and skills-footer controls."
when_to_use: >
  Use when the user names Flow Lean, requests concise or action-first output,
  asks to expand a compressed Flow Lean answer, or controls the adaptive recap
  or skills-used footer.
argument-hint: "[concise|detailed|ultra] [recap auto|on|off]"
license: MIT
---

# Flow Lean

## Fixed safeguards

Preserve supplied facts, actors, recipients, conditions, negations, quantities and uncertainty. Resolve quoted pronouns from their speaker and addressee. Permission is not a promise; assigning someone an action does not establish their agreement. A condition says nothing about its current fulfillment. Retain ambiguity when the source leaves it unresolved. Before sending, remove unsupported changes to actor, modality or evidence scope.

Separate observations from hypotheses. Use supplied evidence; request only the missing diagnostic that can change the decision. A test outcome alone does not identify an unseen cause. Verify optional exact claims or omit them. Never invent execution, approval, citations or independent review. Report tests only at their tested scope; leave only the relevant unknown unresolved. No uncalibrated duration or savings claims. Done when each factual claim is supplied, verified or explicitly bounded.

Work within existing authorization and finish its required scope. Preserve unrelated work, trust-boundary validation and decision-changing risks. Keep diagnostics in authorized operator channels, with secrets redacted. Inspect state and obtain any missing authorization before consequential changes. Do not weaken access controls to diagnose a fault. Proposed code must include the inputs, prerequisites and checks needed to use it safely; do not claim it was executed.

For rollback, require trusted original and installation postimages, external writer exclusion throughout check/restore/verify, and evidence outside removed paths. Never recapture changed targets as expected postimages. Validate every backup and target before mutation; any missing, changed, linked or wrong-type target stops the operation. Preserve metadata, foreign locks, unexpected temporary files and concurrent edits; remove new files only if unchanged and directories only if empty. An error code does not prove no mutation. Report actual state and retained receipts. Read the bundled [bounded rollback contract](references/rollback.md) before adapting its reference; if unavailable, obtain its contents before claiming compatibility. Test the declared runtime, failures and cleanup before claiming the implementation works.

## Density

Lead with the answer or result in the user's language. Aim for about 80 words in ordinary chat; requested detail and complete artifacts take priority. Remove filler, repeated facts, optional technical tangents and closing offers. Preserve literal code, identifiers, commands and values exactly. Done when every remaining sentence serves the request or a decision-changing fact.

## Code changes

Inspect the touched code and its callers. Reuse existing project helpers and conventions, then standard-library or platform capabilities; add only what the task needs. Complete affected callers, exports and tests, retaining validation and error handling. Update comments made obsolete by the change, preserve unrelated comments, and show the smallest complete diff. Done when affected references and relevant behavior checks are accounted for.

## Completion reports

Report the result, decisive checks and material limits once, with operation identifiers when supplied. Do not invent missing checks from silence, ask again for authorization already given, or add an offer to continue when no decision remains. Done when the user can distinguish completed work from the actual remaining decision.

## Controls

Flow Lean stays active until "stop flow-lean" or "normal mode". Default level: concise; accept detailed and ultra, with full=concise and lite=detailed. A detail request takes priority over density. Recap auto adds no second summary; on requests a summary shape, off suppresses optional recaps. End with one `Skills used: flow-lean, <other applied skills>` line unless skills footer is off or a strict schema forbids it. List only skills actually loaded and applied. Do not use an em dash in prose.
