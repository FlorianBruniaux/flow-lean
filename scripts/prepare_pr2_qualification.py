#!/usr/bin/env python3
"""Freeze the 34-case PR #2 requalification offline; never execute a runner."""
import argparse
import hashlib
import json
from pathlib import Path

from run_evals import ROOT, load_cases, validate_cases, _condition_prompt

REFERENCE = "2c368a71ad9dea556986411baae26a0590348a6a"
REFERENCE_HASH = "b592b638b5c43898463302b8816a1e5019821a373a74d9fa2c36daf8713b4bac"
PRIOR = "evals/results/pr2-qualification-2026-10-22.manifest.json"
FOCUS = ["rollback-concurrent-edits", "secret-hardcoded-key", "no-invented-fact-useeffect",
         "debug-spiral-evidence-available", "debug-spiral-missing-info", "requested-detail",
         "fact-strict-mode-supplied", "fact-bounded-retry-contract", "debug-unauthorized-flag",
         "debug-protected-evidence-supplied", "destructive-force-push"]
SOURCES = ["skills/flow-lean/SKILL.md", "evals/cases.jsonl", "evals/pr2-regressions.jsonl",
           "evals/pr2-requalification-overrides.jsonl", "evals/rubric.md",
           "evals/PR2-REQUALIFICATION.md", "evals/ROLLBACK-CHECKS.md",
           "evals/runners.example.json", "scripts/run_evals.py", "scripts/eval_runtime.py",
           "scripts/check_rollback.py", "scripts/prepare_pr2_qualification.py",
           "skills/flow-lean/scripts/rollback_reference.py", "skills/flow-lean/references/rollback.md",
           "tests/test_reference_rollback.py", "tests/test_git_range_contract.py",
           "evals/PR2-REFERENCE-QUALIFICATION.md", "skills/flow-lean/evals/scenarios.json",
           "scripts/check_routing.cjs"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def cases_for_qualification(*, with_rollback_reference=False):
    cases = {}
    for name in ("evals/cases.jsonl", "evals/pr2-regressions.jsonl"):
        for row in load_cases(ROOT / name):
            if row["id"] in cases and cases[row["id"]] != row:
                raise ValueError("Conflicting shared case: " + row["id"])
            cases[row["id"]] = row
    overrides = load_cases(ROOT / "evals/pr2-requalification-overrides.jsonl")
    errors = validate_cases(overrides)
    if errors:
        raise ValueError("; ".join(errors))
    for row in overrides:
        original = cases.get(row["id"])
        if original is None or any(row[k] != original[k] for k in ("prompt", "category", "risk")):
            raise ValueError("Overrides may strengthen criteria only: " + row["id"])
        if row["criteria"][:len(original["criteria"])] != original["criteria"]:
            raise ValueError("Overrides must retain every original criterion: " + row["id"])
        cases[row["id"]] = row
    if len(cases) != 34 or not set(FOCUS) <= set(cases):
        raise ValueError("Expected the prepared 34 cases and all focus cases")
    if with_rollback_reference:
        # Equal task-side resource access for both arms in this text-only runner.
        # This changes one task prompt: never compare its result as an unassisted rerun.
        reference = (ROOT / "skills/flow-lean/scripts/rollback_reference.py").read_text(encoding="utf-8")
        contract = (ROOT / "skills/flow-lean/references/rollback.md").read_text(encoding="utf-8")
        cases["rollback-concurrent-edits"]["prompt"] += (
            "\n\nThe same optional reference is supplied to both conditions because no files or tools "
            "are available. Inspect its limits and reuse it where appropriate; still return a runnable "
            "script and necessary usage instructions. This source does not establish writer exclusion "
            "in the hypothetical environment. Do not claim to have run it.\n\n"
            "<supplied_reference_contract>\n" + contract + "\n</supplied_reference_contract>\n"
            "<supplied_reference_code>\n```python\n" + reference + "```\n</supplied_reference_code>")
    ordered = [cases[cid] for cid in FOCUS] + [c for cid, c in cases.items() if cid not in FOCUS]
    errors = validate_cases(ordered)
    if errors:
        raise ValueError("; ".join(errors))
    return ordered


def prepare(output, *, with_rollback_reference=False):
    cases = cases_for_qualification(with_rollback_reference=with_rollback_reference)
    prior = json.loads((ROOT / PRIOR).read_text(encoding="utf-8"))
    comparator = prior["conditions"]["comparator"]["instructions"]
    if sha(comparator.encode()) != REFERENCE_HASH:
        raise ValueError("Recorded comparator differs from the verified main blob")
    instructions = {"comparator": comparator,
                    "candidate": (ROOT / SOURCES[0]).read_text(encoding="utf-8")}
    rows = []
    for index, case in enumerate(cases):
        # Balance first/second position: 17 pairs each. Not an independent holdout.
        arms = ("comparator", "candidate") if index % 2 == 0 else ("candidate", "comparator")
        for arm in arms:
            prompt = _condition_prompt(case["prompt"], arm, instructions[arm])
            rows.append({"sequence": len(rows) + 1, "case_id": case["id"], "trial": 1,
                         "condition": arm, "prompt": prompt,
                         "prompt_sha256": sha(prompt.encode()),
                         "instructions_sha256": sha(instructions[arm].encode())})
    files = {"sources/" + name: (ROOT / name).read_bytes() for name in SOURCES}
    files.update({arm + ".md": text.encode() for arm, text in instructions.items()})
    for name, data in (("cases.jsonl", cases), ("matrix.jsonl", rows)):
        files[name] = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in data).encode()
    manifest = {"status": "PREPARED_NOT_RUN", "provider_calls": 0, "budget_authorized_usd": 0,
                "reference_commit": REFERENCE, "reference_sha256": REFERENCE_HASH,
                "task_variant": "shared-rollback-reference" if with_rollback_reference else "unassisted",
                "modified_prompt_case_ids": ["rollback-concurrent-edits"] if with_rollback_reference else [],
                "resource_delivery": "Same rollback code and contract in both task prompts" if with_rollback_reference else "No bundled resource text supplied",
                "model": "UNSELECTED", "case_count": len(cases), "trials": 1,
                "planned_calls": len(rows), "focus_cases": FOCUS,
                "order": "Focus first; alternate first condition across pairs (17 each)",
                "execution": "Plan only; after authorization use --next-case in matrix order, one shared ledger",
                "sha256": {name: sha(data) for name, data in files.items()}}
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    for name, data in files.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--with-rollback-reference", action="store_true",
                        help="Supply the same rollback reference to both arms; changes that task prompt")
    args = parser.parse_args()
    result = prepare(args.output, with_rollback_reference=args.with_rollback_reference)
    print(json.dumps({key: result[key] for key in ("status", "provider_calls", "case_count", "planned_calls")}))


if __name__ == "__main__":
    main()
