import json
import hashlib
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from prepare_group_comparison import SPEC, V3, build, render, sha
from run_evals import CONDITIONS, load_cases, _condition_prompt, _condition_instructions, summarize_scores


class GroupComparisonTests(unittest.TestCase):
    def setUp(self):
        self.spec = json.loads(SPEC.read_text())
        self.cases = load_cases()

    def test_exact_single_group_removal_and_tracked_candidate(self):
        instructions, _ = build(self.spec, self.cases)
        self.assertEqual(V3.read_text(), render(self.spec))
        for group in self.spec["groups"]:
            arm = "v3_without_" + group["id"]
            self.assertIn(arm, CONDITIONS)
            self.assertEqual(instructions[arm], render(self.spec).replace("\n\n" + group["text"], ""))

    def test_balanced_pairing_actual_prompt_hashes_and_determinism(self):
        with patch("subprocess.run", side_effect=AssertionError("Planner must not start a process")):
            instructions, rows = build(self.spec, self.cases, trials=2)
        self.assertEqual(len(rows), len(self.cases) * 7 * 2)
        self.assertEqual(rows, build(self.spec, self.cases, trials=2)[1])
        self.assertNotEqual(rows, build(self.spec, self.cases, trials=2, seed=3)[1])
        for trial in (1, 2):
            for case in self.cases:
                paired = [r for r in rows if r["case_id"] == case["id"] and r["trial"] == trial]
                self.assertEqual({r["condition"] for r in paired}, set(instructions))
                self.assertEqual(len(paired), 7)
                for row in paired:
                    self.assertEqual(row["prompt"], _condition_prompt(case["prompt"], row["condition"], instructions[row["condition"]]))
                    self.assertEqual(row["prompt_sha256"], sha(row["prompt"]))

    def test_invalid_focus_and_trial_count(self):
        self.spec["groups"][0]["cases"].append("nonexistent")
        with self.assertRaises(ValueError): build(self.spec, self.cases)
        for trials in (0, -1, True):
            with self.assertRaises(ValueError): build(self.spec, self.cases, trials=trials)

    def test_scoring_accepts_new_named_arms(self):
        rows = [{"case_id": "one", "trial": 1, "condition": arm, "correctness": 5,
                 "decision_fidelity": 5, "gate_fit": 5, "concision": 5, "safety": 5,
                 "blocker": False, "notes": "fixture"} for arm in ("v3", "v3_without_fidelity")]
        summary = summarize_scores(rows, "v3", "v3_without_fidelity")
        self.assertEqual(set(summary["conditions"]), {"v3", "v3_without_fidelity"})

    def test_new_arms_require_explicit_instructions(self):
        for arm in CONDITIONS:
            if arm.startswith("v3"):
                with self.assertRaises(ValueError): _condition_instructions(arm, None)

    def test_cli_freezes_sources_and_refuses_to_replace_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "plan"
            command = [sys.executable, str(ROOT / "scripts/prepare_group_comparison.py"),
                       "--output", str(output)]
            run = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            manifest = json.loads((output / "manifest.json").read_text())
            matrix = (output / "matrix.jsonl").read_text()
            self.assertEqual(manifest["provider_calls"], 0)
            self.assertEqual(manifest["budget_authorized_usd"], 0)
            self.assertEqual(manifest["matrix_sha256"], hashlib.sha256((output / "matrix.jsonl").read_bytes()).hexdigest())
            self.assertEqual(len(matrix.splitlines()), len(self.cases) * 7)
            for path, fingerprint in manifest["source_hashes"].items():
                self.assertEqual(hashlib.sha256((output / "sources" / path).read_bytes()).hexdigest(), fingerprint)
            self.assertNotEqual(subprocess.run(command, capture_output=True).returncode, 0)
            self.assertEqual((output / "matrix.jsonl").read_text(), matrix)


if __name__ == "__main__": unittest.main()
