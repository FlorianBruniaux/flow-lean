#!/usr/bin/env python3
"""Validate, run, and score paired response-quality evaluations.

Forked from ayghri/i-have-adhd (https://github.com/ayghri/i-have-adhd),
scripts/run_evals.py, MIT License, Copyright (c) 2026 Ayoub Ghriss.
Flow Lean adds scoring weights, provenance-bound resumes, isolated execution,
and a durable per-attempt cost ledger.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from eval_runtime import execute


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "evals" / "cases.jsonl"
WEIGHTS = {
    "correctness": 0.30,
    "decision_fidelity": 0.25,
    "gate_fit": 0.20,
    "concision": 0.15,
    "safety": 0.10,
}
CONDITIONS = {"baseline", "candidate", "comparator", "generic", "minimal", "v3",
              "v3_without_fidelity", "v3_without_evidence", "v3_without_duration",
              "v3_without_rollback", "pr2_full", "v4", "v4_without_density",
              "v4_without_scope", "v4_without_format", "v4_without_status"}


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}: line {number}: {exc.msg}") from exc
        if not isinstance(row, dict):
            raise ValueError(f"{path}: line {number}: expected a JSON object")
        rows.append(row)
    return rows


def load_cases(path: Path = DEFAULT_CASES) -> list[dict[str, Any]]:
    return read_jsonl(path)


def validate_cases(cases: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    required = {"id", "category", "prompt", "risk", "criteria"}
    for index, case in enumerate(cases, start=1):
        missing = sorted(required - set(case))
        if missing:
            errors.append(f"Case {index}: missing fields: {', '.join(missing)}")
            continue
        case_id = case["id"]
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"Case {index}: id must be a non-empty string")
        elif case_id in seen:
            errors.append(f"Duplicate case id: {case_id}")
        else:
            seen.add(case_id)
        if case["risk"] not in {"low", "medium", "high"}:
            errors.append(f"Case {case_id}: risk must be low, medium, or high")
        if not isinstance(case["criteria"], list) or not case["criteria"]:
            errors.append(f"Case {case_id}: criteria must be a non-empty list")
    return errors


def _validate_score(row: dict[str, Any], index: int) -> None:
    required = {"case_id", "trial", "condition", *WEIGHTS, "blocker", "notes"}
    missing = sorted(required - set(row))
    if missing:
        raise ValueError(f"Score row {index}: missing fields: {', '.join(missing)}")
    if row["condition"] not in CONDITIONS:
        raise ValueError(f"Score row {index}: unsupported condition {row['condition']!r}")
    for metric in WEIGHTS:
        value = row[metric]
        if not isinstance(value, (int, float)) or not 1 <= value <= 5:
            raise ValueError(f"Score row {index}: {metric} must be between 1 and 5")
    if not isinstance(row["blocker"], bool):
        raise ValueError(f"Score row {index}: blocker must be boolean")


def _describe_rows(keys: list[tuple[str, Any]]) -> str:
    return ", ".join(f"{case_id}/trial {trial}" for case_id, trial in keys)


def _check_pairing(grouped: dict[str, list[dict[str, Any]]], reference: str = "baseline") -> None:
    """Conditions are only comparable when judged on identical rows."""
    coverage = {
        condition: Counter((row["case_id"], row["trial"]) for row in rows)
        for condition, rows in grouped.items()
    }
    for condition, counts in sorted(coverage.items()):
        repeated = sorted(key for key, count in counts.items() if count > 1)
        if repeated:
            raise ValueError(
                f"{condition}: duplicate score rows for {_describe_rows(repeated)}"
            )
    baseline = coverage[reference]
    for condition, counts in sorted(coverage.items()):
        if condition == reference or counts == baseline:
            continue
        details = []
        missing = sorted(set(baseline) - set(counts))
        if missing:
            details.append(f"missing {_describe_rows(missing)}")
        unmatched = sorted(set(counts) - set(baseline))
        if unmatched:
            details.append(f"unmatched {_describe_rows(unmatched)}")
        raise ValueError(
            f"{condition} was not judged on the same rows as {reference}: "
            + "; ".join(details)
        )


def summarize_scores(scores: list[dict[str, Any]], reference: str = "baseline",
                     candidate_name: str = "candidate") -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for index, row in enumerate(scores, start=1):
        _validate_score(row, index)
        grouped[row["condition"]].append(row)
    if reference == candidate_name or reference not in grouped or candidate_name not in grouped:
        raise ValueError("Scores must include two distinct selected comparison conditions")
    _check_pairing(grouped, reference)

    conditions: dict[str, dict[str, Any]] = {}
    for condition, rows in sorted(grouped.items()):
        metrics = {
            metric: sum(float(row[metric]) for row in rows) / len(rows)
            for metric in WEIGHTS
        }
        conditions[condition] = {
            "rows": len(rows),
            **metrics,
            "weighted_score": sum(metrics[metric] * weight for metric, weight in WEIGHTS.items()),
            "blocking_findings": sum(bool(row["blocker"]) for row in rows),
        }

    baseline = conditions[reference]
    candidate = conditions[candidate_name]
    reasons: list[str] = []
    if candidate["blocking_findings"]:
        reasons.append("Candidate has blocking safety or correctness findings.")
    if candidate["correctness"] < baseline["correctness"] - 0.1:
        reasons.append("Candidate correctness regressed by more than 0.1 points against the selected reference.")
    if candidate["safety"] < baseline["safety"] - 0.1:
        reasons.append("Candidate safety regressed by more than 0.1 points against the selected reference.")
    if candidate["weighted_score"] <= baseline["weighted_score"]:
        reasons.append("Candidate weighted score did not beat the selected reference.")

    return {
        "comparison": {"reference": reference, "candidate": candidate_name},
        "weights": WEIGHTS,
        "conditions": conditions,
        "release_gate": {"passed": not reasons, "reasons": reasons},
    }


def _condition_instructions(condition: str, skill_path: Path | None) -> str:
    if condition == "baseline":
        return ""
    if skill_path is None and condition in {"generic", "minimal"}:
        skill_path = ROOT / "evals" / "candidates" / f"{condition}.md"
    if skill_path is None:
        raise ValueError(f"--condition-skill is required for the {condition} condition")
    return skill_path.read_text(encoding="utf-8")


def _condition_prompt(task: str, condition: str, instructions: str) -> str:
    context = (
        "<evaluation_context>\n"
        "This is a text-only evaluation with no tools, repository access, or network access. "
        "Paths and operational facts belong to the task's scenario, not the runner's working directory. "
        "Requested code and commands are text deliverables, not actions to execute.\n"
        "</evaluation_context>\n\n"
    )
    style = "" if condition == "baseline" else (
        "Follow the response-style skill below while completing the task. "
        "Do not discuss or quote the skill.\n\n"
        f"<response_style>\n{instructions}\n</response_style>\n\n"
    )
    return f"{context}{style}<task>\n{task}\n</task>"


def _parse_response(output: str, response_format: str) -> tuple[str, dict[str, Any], float | None]:
    if response_format == "text":
        return output.strip(), {}, None
    if response_format == "claude-json":
        payload = json.loads(output)
        # Newer Claude Code CLIs emit an event array; the final "result" event holds the answer.
        if isinstance(payload, list):
            payload = next((e for e in reversed(payload) if e.get("type") == "result"), {})
        result = payload.get("result")
        return (
            result.strip() if isinstance(result, str) else "",
            payload.get("usage", {}) or {},
            payload.get("total_cost_usd"),
        )
    if response_format == "codex-jsonl":
        events = [json.loads(line) for line in output.splitlines() if line.strip()]
        text = ""
        usage: dict[str, Any] = {}
        for event in events:
            item = event.get("item", {})
            if event.get("type") == "item.completed" and item.get("type") == "agent_message":
                text = item.get("text", text)
            if event.get("type") == "turn.completed":
                usage = event.get("usage", usage)
        return str(text).strip(), usage, None
    raise ValueError(f"Unsupported response format: {response_format}")


def run_evaluations(args: argparse.Namespace) -> int:
    cases = load_cases(args.cases)
    errors = validate_cases(cases)
    if errors:
        raise ValueError("\n".join(errors))
    unknown = sorted(set(args.case or []) - {case["id"] for case in cases})
    if unknown:
        raise ValueError(f"--case matched no evaluation case: {', '.join(unknown)}")
    selected = set(args.case or [case["id"] for case in cases])
    if args.next_case is not None and args.next_case not in selected:
        raise ValueError("--next-case must belong to the selected campaign cases")
    config = json.loads(args.runner_config.read_text(encoding="utf-8"))
    runner = config[args.runner]
    response_format = runner.get("response_format", "text")
    if response_format != "claude-json" and not args.allow_unmetered:
        raise RuntimeError(
            f"The {response_format!r} response format never reports dollar cost; rerun with "
            "--allow-unmetered only when the provider has a separate hard spending cap."
        )
    instructions = _condition_instructions(args.condition, args.condition_skill)
    prompts = {case["id"]: _condition_prompt(case["prompt"], args.condition, instructions)
               for case in cases}
    return execute(args, cases, runner, instructions, prompts, _parse_response, read_jsonl)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate the case catalog")
    validate.add_argument("--cases", type=Path, default=DEFAULT_CASES)

    plan = subparsers.add_parser("plan", help="Print the paired run matrix as JSONL")
    plan.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    plan.add_argument("--trials", type=int, default=3)
    plans = plan.add_mutually_exclusive_group()
    plans.add_argument("--include-comparator", action="store_true")
    plans.add_argument("--paired-comparison", action="store_true",
                       help="Plan comparator and candidate only (two full skills)")
    plans.add_argument("--core-comparison", action="store_true",
                       help="Plan baseline, generic, minimal and current candidate")

    score = subparsers.add_parser("score", help="Aggregate manually judged score rows")
    score.add_argument("scores", type=Path)
    score.add_argument("--reference-condition", choices=sorted(CONDITIONS), default="baseline")
    score.add_argument("--candidate-condition", choices=sorted(CONDITIONS), default="candidate")

    run = subparsers.add_parser("run", help="Run one evaluation condition")
    run.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    run.add_argument("--runner-config", type=Path, default=ROOT / "evals" / "runners.example.json")
    run.add_argument("--runner", required=True)
    run.add_argument("--condition", choices=sorted(CONDITIONS), required=True)
    run.add_argument("--condition-skill", type=Path)
    run.add_argument("--case", action="append")
    run.add_argument("--next-case", help="Schedule one selected case without changing campaign provenance")
    run.add_argument("--trials", type=int, default=3)
    run.add_argument("--retries", type=int, default=2)
    run.add_argument("--budget-usd", type=float, default=25.0)
    run.add_argument("--allow-unmetered", action="store_true")
    run.add_argument("--output", type=Path, required=True)
    run.set_defaults(handler=run_evaluations)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if hasattr(args, "handler"):
        return args.handler(args)
    if args.command == "validate":
        errors = validate_cases(load_cases(args.cases))
        if errors:
            for error in errors:
                print(f"ERROR: {error}", file=sys.stderr)
            return 1
        print("Evaluation cases are valid.")
        return 0
    if args.command == "plan":
        cases = load_cases(args.cases)
        errors = validate_cases(cases)
        if errors:
            raise ValueError("\n".join(errors))
        if args.trials < 1:
            raise ValueError("trials must be positive")
        conditions = (["baseline", "generic", "minimal", "candidate"]
                      if args.core_comparison else ["baseline", "candidate"])
        if args.paired_comparison:
            conditions = ["comparator", "candidate"]
        if args.include_comparator:
            conditions.append("comparator")
        for trial in range(1, args.trials + 1):
            for case in cases:
                for condition in conditions:
                    print(json.dumps({"case_id": case["id"], "trial": trial, "condition": condition}))
        return 0
    if args.command == "score":
        print(json.dumps(summarize_scores(read_jsonl(args.scores), args.reference_condition, args.candidate_condition), indent=2))
        return 0
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
