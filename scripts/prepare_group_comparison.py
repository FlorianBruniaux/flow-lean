#!/usr/bin/env python3
"""Build a frozen group-ablation matrix offline. Does not run providers."""
import argparse
import hashlib
import json
from pathlib import Path
import random

from run_evals import ROOT, _condition_prompt, load_cases, validate_cases

SPEC = ROOT / "evals/candidates/v3-groups.json"
V3 = ROOT / "evals/candidates/minimal-v3.md"


def sha(data):
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def render(spec, omit=None):
    return "\n\n".join([spec["base"], *(g["text"] for g in spec["groups"] if g["id"] != omit)]) + "\n"


def build(spec, cases, trials=1, seed=20261017):
    if isinstance(trials, bool) or not isinstance(trials, int) or trials < 1:
        raise ValueError("trials must be a positive integer")
    errors = validate_cases(cases)
    if errors: raise ValueError("; ".join(errors))
    ids = {case["id"] for case in cases}
    groups = [group["id"] for group in spec["groups"]]
    if groups != ["fidelity", "evidence", "duration", "rollback"]:
        raise ValueError("Expected the four ordered v3 groups")
    if not spec["base"].strip() or any(not g["text"].strip() for g in spec["groups"]):
        raise ValueError("Empty instruction block")
    for group in spec["groups"]:
        if not group["cases"] or not set(group["cases"]) <= ids:
            raise ValueError(f"Unknown or missing focus cases for {group['id']}")
    instructions = {"baseline": "", "generic": (ROOT / "evals/candidates/generic.md").read_text(),
                    "v3": render(spec)}
    instructions.update({f"v3_without_{name}": render(spec, name) for name in groups})
    rng = random.Random(seed)
    rows = []
    for trial in range(1, trials + 1):
        ordered_cases = list(cases); rng.shuffle(ordered_cases)
        for case in ordered_cases:
            arms = list(instructions); rng.shuffle(arms)
            for arm in arms:
                prompt = _condition_prompt(case["prompt"], arm, instructions[arm])
                rows.append({"sequence": len(rows) + 1, "case_id": case["id"], "trial": trial,
                             "condition": arm, "instructions_sha256": sha(instructions[arm]),
                             "prompt_sha256": sha(prompt), "prompt": prompt})
    return instructions, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true", help="Validate tracked v3 text without writing")
    parser.add_argument("--trials", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20261017)
    args = parser.parse_args()
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    instructions, rows = build(spec, load_cases(), args.trials, args.seed)
    if not V3.exists() or V3.read_text(encoding="utf-8") != instructions["v3"]:
        parser.error("minimal-v3.md differs from v3-groups.json; regenerate and review before planning")
    if args.check:
        print(json.dumps({"status": "PASS", "arms": len(instructions), "planned_calls": len(rows),
                          "provider_calls": 0, "v3_words": len(instructions["v3"].split())}))
        return 0
    if args.output is None: parser.error("--output or --check is required")
    if args.output.exists(): parser.error("Use a new output directory; prior plans are immutable")
    args.output.mkdir(parents=True)
    snapshots = {}
    sources = [SPEC, V3, ROOT / "evals/cases.jsonl", ROOT / "evals/rubric.md",
               ROOT / "evals/GROUP-COMPARISON.md", ROOT / "evals/ROLLBACK-CHECKS.md",
               ROOT / "evals/candidates/generic.md", Path(__file__).resolve(),
               ROOT / "scripts/run_evals.py", ROOT / "scripts/eval_runtime.py",
               ROOT / "scripts/check_rollback.py"]
    for source in sources:
        relative = source.relative_to(ROOT)
        data = source.read_bytes()
        target = args.output / "sources" / relative
        target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(data)
        snapshots[str(relative)] = hashlib.sha256(data).hexdigest()
    prompts = args.output / "instructions"; prompts.mkdir()
    for arm, text in instructions.items(): (prompts / f"{arm}.md").write_bytes(text.encode("utf-8"))
    matrix = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    (args.output / "matrix.jsonl").write_bytes(matrix.encode("utf-8"))
    manifest = {"status": "PREPARED_NOT_RUN", "provider_calls": 0, "budget_authorized_usd": 0,
                "model": "UNSELECTED", "trials": args.trials, "seed": args.seed,
                "planned_calls": len(rows), "arms": list(instructions), "groups": spec["groups"],
                "matrix_sha256": sha(matrix), "source_hashes": snapshots,
                "pairing": "All arms share every case/trial; shuffled within each case",
                "execution": "Plan only; run_evals runs one arm per invocation and does not execute this order"}
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "planned_calls": len(rows), "provider_calls": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
