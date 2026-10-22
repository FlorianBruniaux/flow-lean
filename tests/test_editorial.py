"""Deterministic editorial checks: prose is flagged, code, quotes and schema output are not."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import editorial  # noqa: E402

TOKENS = editorial.banned_tokens()


class EditorialCheckTests(unittest.TestCase):
    def test_tokens_come_from_the_skill(self):
        self.assertIn("robust", TOKENS)
        self.assertIn("complexite", TOKENS)

    def test_prose_em_dash_and_banned_tokens_are_flagged(self):
        result = editorial.check("Une solution robuste — sans les défis habituels. Crucially, ok.", TOKENS)
        self.assertEqual(result["em_dashes"], 1)
        self.assertEqual(result["banned"], ["robuste", "defis", "crucially"])

    def test_code_and_quotes_are_exempt(self):
        text = (
            "Run this:\n\n```text\nrobust — seamless\n```\n\n"
            "Use `--mode=robust` here.\n"
            "> The docs say: a crucial — step.\n"
            'The error reads "pivotal — failure" verbatim, and «enjeux» too.\n'
        )
        self.assertEqual(editorial.check(text, TOKENS), {"exempt": None, "em_dashes": 0, "banned": []})

    def test_inflection_does_not_widen_to_other_words(self):
        self.assertEqual(editorial.check("La défiscalisation et le landscaping.", TOKENS)["banned"], [])

    def test_schema_output_is_exempt(self):
        self.assertEqual(editorial.check('{"note": "robust — output"}', TOKENS)["exempt"], "output-schema")
        self.assertEqual(editorial.check("robust", TOKENS, output_schema=True)["exempt"], "output-schema")

    def test_cli_reports_per_condition(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cases = root / "cases.jsonl"
            responses = root / "responses.jsonl"
            case = {"category": "style", "prompt": "p", "risk": "low", "criteria": ["c"]}
            cases.write_text("".join(json.dumps({"id": i, **case, **extra}) + "\n" for i, extra in
                                     (("a", {}), ("b", {"output_schema": True}))), encoding="utf-8")
            rows = [
                {"case_id": "a", "trial": 1, "condition": "baseline", "response": "x — y, robust"},
                {"case_id": "a", "trial": 1, "condition": "candidate", "response": "x, y"},
                {"case_id": "b", "trial": 1, "condition": "candidate", "response": "robust — raw"},
            ]
            responses.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
            completed = subprocess.run([sys.executable, str(ROOT / "scripts/run_evals.py"), "editorial",
                                        str(responses), "--cases", str(cases)], capture_output=True, encoding="utf-8")
            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(completed.stdout)
        self.assertEqual(report["conditions"]["baseline"]["with_em_dash"], 1)
        self.assertEqual(report["conditions"]["candidate"], {"responses": 2, "exempt": 1, "with_em_dash": 0,
                                                             "em_dashes": 0, "with_banned": 0})
        self.assertEqual([f["case_id"] for f in report["findings"]], ["a"])
        self.assertEqual(report["findings"][0]["banned"], ["robust"])


if __name__ == "__main__":
    unittest.main()
